# ruff: noqa: F401
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Optional
import typer
from sric.workspace import Workspace
from sric.evidence import EvidenceStore
from sric.models import Provenance, ProvenanceType
from sric.plugins import PluginRegistry
from sric.scope import ScopeEngine, ScopePolicy
from sric.updater import perform_update
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import NotebookEntry, ResearchNotebook
from . import __version__
from .api import create_app
from .core import ExposureEngine
from .models import Dimension, Entity, Relationship
from .cli import app, rd, wp

@app.command()
def add(workspace: str, entity_id: str, entity_type: str, value: str, dimension: Dimension, source: str, evidence: list[str] = typer.Option([], "--evidence"), metadata_json: str = "{}", root: Path = typer.Option(rd(), "--root")) -> None:
    ExposureEngine(wp(workspace, root)).add_entity(Entity(entity_id=entity_id,entity_type=entity_type,value=value,dimension=dimension,source=source,evidence_ids=evidence,metadata=json.loads(metadata_json))); typer.echo(entity_id)

@app.command("relationship")
def relationship_cmd(workspace: str, relationship_id: str, source_entity_id: str, target_entity_id: str, relationship_type: str, confidence: float, evidence: list[str] = typer.Option([], "--evidence"), counter: list[str] = typer.Option([], "--counter-evidence"), root: Path = typer.Option(rd(), "--root")) -> None:
    ExposureEngine(wp(workspace,root)).add_relationship(Relationship(relationship_id=relationship_id,source_entity_id=source_entity_id,target_entity_id=target_entity_id,relationship_type=relationship_type,confidence=confidence,evidence_ids=evidence,counter_evidence=counter)); typer.echo(relationship_id)

@app.command("import")
def import_cmd(workspace:str,path:Path,root:Path=typer.Option(rd(),"--root"))->None: typer.echo(json.dumps(ExposureEngine(wp(workspace,root)).import_json(path),indent=2))

@app.command()
def collect(workspace:str|None=None,adapter:str|None=None,path:Path|None=None,root:Path=typer.Option(rd(),"--root"))->None:
    if workspace is None and adapter is None and path is None: typer.echo("PASSIVE mode: no unbounded external collection. Adapters = ct,dns,repo,package,oauth,analytics,asn,openapi,mobile; supply WORKSPACE ADAPTER PATH to ingest an explicit local export."); return
    if not workspace or not adapter or path is None: raise typer.BadParameter("WORKSPACE, ADAPTER and PATH must be supplied together")
    typer.echo(json.dumps({"mode":"PASSIVE","adapter":adapter,"imported":ExposureEngine(wp(workspace,root)).collect_adapter(path,adapter)},indent=2))

@app.command()
def entities(workspace:str,root:Path=typer.Option(rd(),"--root"))->None: typer.echo(json.dumps(ExposureEngine(wp(workspace,root)).store.load()["entities"],indent=2))
@app.command()
def correlate(workspace:str,root:Path=typer.Option(rd(),"--root"))->None: typer.echo(json.dumps([x.model_dump(mode="json") for x in ExposureEngine(wp(workspace,root)).correlate()],indent=2))
@app.command()
def graph(workspace:str,root:Path=typer.Option(rd(),"--root"))->None: typer.echo(json.dumps(ExposureEngine(wp(workspace,root)).graph(),indent=2))
@app.command()
def timeline(workspace:str,root:Path=typer.Option(rd(),"--root"))->None: typer.echo(json.dumps(ExposureEngine(wp(workspace,root)).timeline(),indent=2))
@app.command()
def explain(workspace:str,candidate_id:str,root:Path=typer.Option(rd(),"--root"))->None:
    try:c=ExposureEngine(wp(workspace,root)).explain(candidate_id)
    except KeyError:raise typer.Exit(2)
    typer.echo(c.model_dump_json(indent=2))
@app.command("coverage")
def coverage_command(workspace:str,root:Path=typer.Option(rd(),"--root"))->None: typer.echo(json.dumps(ExposureEngine(wp(workspace,root)).dimension_coverage(),indent=2))
@app.command("lineage")
def lineage_command(workspace:str,root:Path=typer.Option(rd(),"--root"))->None: typer.echo(json.dumps(ExposureEngine(wp(workspace,root)).organization_lineage(),indent=2))
@app.command("compare-org")
def compare_org_command(workspace:str,other:Path=typer.Argument(...,exists=True,dir_okay=False),root:Path=typer.Option(rd(),"--root"))->None: typer.echo(json.dumps(ExposureEngine(wp(workspace,root)).compare_dataset(other),indent=2))
@app.command("resolve")
def resolve_command(workspace:str,candidate_id:str,decision:str,note:str=typer.Option(...,"--note"),root:Path=typer.Option(rd(),"--root"))->None:
    try:payload=ExposureEngine(wp(workspace,root)).decide_resolution(candidate_id,decision,note)
    except (KeyError,ValueError) as exc:typer.echo(str(exc),err=True);raise typer.Exit(2)
    typer.echo(json.dumps(payload,indent=2))
@app.command("cross-correlate")
def cross_correlate_command(workspace:str,inputs:list[Path]=typer.Argument(...,exists=True,dir_okay=False),root:Path=typer.Option(rd(),"--root"))->None: typer.echo(json.dumps(ExposureEngine(wp(workspace,root)).cross_project_correlate(inputs),indent=2))
@app.command("export")
def export_cmd(workspace:str,output:Path,root:Path=typer.Option(rd(),"--root"))->None: output.write_text(json.dumps(ExposureEngine(wp(workspace,root)).export(),indent=2),encoding="utf-8");typer.echo(str(output))
@app.command()
def report(workspace:str,output:Path,root:Path=typer.Option(rd(),"--root"))->None:
    e=ExposureEngine(wp(workspace,root));d=e.graph();q=e.correlate();output.write_text("# Exposure DNA Report\n\n## Organization\n"+str(d.get("organization"))+"\n\n## DNA dimensions\n```json\n"+json.dumps(e.dimensions(),indent=2)+"\n```\n\n## Entity resolution queue\n```json\n"+json.dumps([x.model_dump(mode="json") for x in q],indent=2)+"\n```\n\nAll inferred relationships require evidence review; similarity alone never proves ownership.\n",encoding="utf-8");typer.echo(str(output))
@app.command()
def demo(workspace:str="demo",root:Path=typer.Option(rd(),"--root"))->None:
    path=wp(workspace,root)
    if not path.exists():root.mkdir(parents=True,exist_ok=True);ws=Workspace.create(root,workspace);ExposureEngine(ws.root).set_organization("Example Corp")
    e=ExposureEngine(path);e.add_entity(Entity(entity_id="e1",entity_type="domain",value="api.oldbrand.test",dimension=Dimension.INFRASTRUCTURE,source="ct",evidence_ids=["E1"],metadata={"oauth_issuer":"https://id.example.test","sdk_family":"example-sdk","certificate_org":"OldBrand"}));e.add_entity(Entity(entity_id="e2",entity_type="domain",value="api.example.test",dimension=Dimension.API,source="sdk",evidence_ids=["E2"],metadata={"oauth_issuer":"https://id.example.test","sdk_family":"example-sdk","certificate_org":"Example Corp"}));typer.echo(json.dumps([x.model_dump(mode="json") for x in e.correlate()],indent=2))
