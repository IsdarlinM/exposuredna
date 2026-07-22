from pathlib import Path
from sric.workspace import Workspace
from exposuredna.core import ExposureEngine
from exposuredna.models import Dimension,Entity

def test_entity_resolution_never_confirms_ownership(tmp_path:Path)->None:
    e=ExposureEngine(Workspace.create(tmp_path,"w").root)
    e.add_entity(Entity(entity_id="a",entity_type="domain",value="a.test",dimension=Dimension.INFRASTRUCTURE,source="ct",metadata={"oauth_issuer":"id.test"},evidence_ids=["E1"]))
    e.add_entity(Entity(entity_id="b",entity_type="domain",value="b.test",dimension=Dimension.API,source="sdk",metadata={"oauth_issuer":"id.test"},evidence_ids=["E2"]))
    c=e.correlate()[0]; assert c.status.value=="INFERRED"; assert c.confidence<1.0; assert c.supporting
