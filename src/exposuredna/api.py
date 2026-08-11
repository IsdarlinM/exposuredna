from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import ResearchNotebook
from sric.workspace import Workspace

from . import __version__
from .core import ExposureEngine

HTML = """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Exposure DNA</title><style>:root{color-scheme:dark}*{box-sizing:border-box}body{font-family:system-ui,-apple-system,sans-serif;margin:0;background:#0d1117;color:#f0f6fc}header{padding:14px 18px;border-bottom:1px solid #30363d;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;background:#11161d}.brand{display:flex;align-items:center;gap:12px}.brand span,.muted{color:#8b949e}.nav{display:flex;gap:7px;overflow:auto}.nav a{white-space:nowrap;text-decoration:none;color:#dbe5ee;border:1px solid #3b4652;border-radius:999px;padding:7px 10px;font-size:12px}.nav a.primary{background:#17314a;border-color:#406f98;color:#e4f2ff}main{padding:20px;display:grid;gap:14px;max-width:1500px;margin:auto}.callout{border:1px solid #355a78;background:#101c27;border-radius:12px;padding:14px}.callout a{color:#9ed4ff;font-weight:700}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:18px}.row{padding:10px 0;border-bottom:1px solid #30363d;word-break:break-word}@media(max-width:650px){header{align-items:flex-start}.brand{width:100%;justify-content:space-between}.nav{width:100%}main{padding:12px}.grid{grid-template-columns:1fr}}</style></head><body><header><div class='brand'><b>Exposure DNA</b><span>imr :: v__VERSION__</span></div><nav class='nav' aria-label='Exposure DNA Web navigation'><a href='/'>Dashboard</a><a class='primary' href='/workbench'>Security Console</a><a href='/docs'>API</a></nav><span id='jobs' class='muted'>Jobs: idle</span></header><main><section class='callout'><strong>Guided operations:</strong> use the <a href='/workbench'>Security Console</a> to configure Exposure DNA capabilities through typed controls without memorizing commands or flags. Correlation never proves ownership by similarity alone.</section><div class='grid'><section class='card'><h3>DNA coverage</h3><div id='dna'></div></section><section class='card'><h3>Knowledge graph</h3><div id='graph'></div></section><section class='card'><h3>Resolution queue</h3><div id='queue'></div></section><section class='card'><h3>Organization lineage</h3><div id='lineage'></div></section></div></main><script src='/assets/app.js'></script></body></html>"""

JS = """const e=s=>String(s).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));const r=x=>`<div class='row'>${e(JSON.stringify(x))}</div>`;async function load(){const[d,g,q,l]=await Promise.all(['/api/dna','/api/graph','/api/resolution-queue','/api/lineage'].map(u=>fetch(u).then(x=>x.json())));dna.innerHTML=Object.entries(d).map(([k,v])=>r({dimension:k,...v})).join('')||'<span class=muted>No DNA entities.</span>';graph.innerHTML=`<b>${g.entities.length}</b> entities · <b>${g.relationships.length}</b> relationships`;queue.innerHTML=q.map(r).join('')||'<span class=muted>No unresolved candidates.</span>';lineage.innerHTML=l.map(r).join('')||'<span class=muted>No lineage relationships.</span>'}try{const s=new EventSource('/api/jobs/events');s.addEventListener('job',x=>{const j=JSON.parse(x.data);jobs.textContent='Job: '+(j.event_type||'event')});s.onerror=()=>{jobs.textContent='Jobs: reconnecting'}}catch(_){}load().catch(()=>{})"""


def create_app(workspace: Path) -> FastAPI:
    workspace = Workspace.initialize(workspace).root
    app = FastAPI(title="Exposure DNA Local API", version=__version__, redoc_url=None)
    engine = ExposureEngine(workspace)
    graph_store = TemporalGraph(workspace)
    jobs = JobEngine(workspace)
    lineage_store = EvidenceLineage(workspace)
    notebook = ResearchNotebook(workspace)

    @app.middleware("http")
    async def hdr(req: Any, call_next: Any) -> Any:
        response = await call_next(req)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'unsafe-inline'; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/", response_class=HTMLResponse)
    async def root() -> str:
        return HTML.replace("__VERSION__", __version__)

    @app.get("/assets/app.js")
    async def js() -> Response:
        return Response(JS, media_type="application/javascript")

    @app.get("/api/graph")
    async def graph() -> dict[str, Any]:
        return engine.graph()

    @app.get("/api/dna")
    async def dna() -> dict[str, Any]:
        return engine.dimension_coverage()

    @app.get("/api/resolution-queue")
    async def queue() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in engine.correlate()]

    @app.get("/api/lineage")
    async def lineage() -> list[dict[str, Any]]:
        return engine.organization_lineage()

    @app.get("/api/external-correlations")
    async def external() -> list[dict[str, Any]]:
        return list(engine.store.load().get("external_correlations", []))

    @app.get("/api/search")
    async def search(q: str, limit: int = 50) -> list[dict[str, Any]]:
        return graph_store.search(q, max(1, min(limit, 500)))

    @app.get("/api/jobs")
    async def list_jobs() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in jobs.list()]

    @app.get("/api/jobs/events")
    async def events(cursor: int = 0, once: bool = False) -> StreamingResponse:
        async def stream() -> Any:
            current = max(0, cursor)
            while True:
                evs = jobs.all_events(current)
                for ev in evs:
                    yield f"id: {current}\nevent: job\ndata: {json.dumps(ev.model_dump(mode='json'), default=str)}\n\n"
                    current += 1
                if once:
                    if not evs:
                        yield "event: heartbeat\ndata: {}\n\n"
                    break
                await asyncio.sleep(1)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )

    @app.get("/api/notebook")
    async def notebook_entries() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in notebook.list()]

    @app.get("/api/evidence-lineage/{artifact_id:path}")
    async def evidence_lineage(artifact_id: str) -> dict[str, Any]:
        try:
            return lineage_store.explain(artifact_id)
        except KeyError:
            return {"artifact_id": artifact_id, "status": "UNKNOWN", "message": "No lineage record found."}

    return app
