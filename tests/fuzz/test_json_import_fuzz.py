from pathlib import Path
import random
from sric.workspace import Workspace
from exposuredna.core import ExposureEngine

def test_malformed_json_fuzz_smoke(tmp_path:Path)->None:
    ws=Workspace.create(tmp_path,"w"); engine=ExposureEngine(ws.root); rng=random.Random(1337)
    for i in range(40):
        path=tmp_path/f"fuzz-{i}.json"; path.write_bytes(bytes(rng.randrange(0,256) for _ in range(rng.randrange(1,80))))
        try: engine.import_json(path)
        except (UnicodeDecodeError,ValueError,TypeError,KeyError): pass
