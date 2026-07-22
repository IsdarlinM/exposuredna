from pathlib import Path
from fastapi.testclient import TestClient
from sric.workspace import Workspace
from exposuredna.api import create_app

def test_api(tmp_path:Path)->None:
    ws=Workspace.create(tmp_path,"w"); c=TestClient(create_app(ws.root)); root=c.get("/"); assert root.status_code==200; assert "script-src 'self'" in root.headers["content-security-policy"]
    js=c.get("/assets/app.js"); assert js.status_code==200 and "fetch(" in js.text; assert c.get("/api/dna").json()=={}
