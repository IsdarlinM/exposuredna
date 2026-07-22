import json
from sric.workspace import Workspace
from exposuredna.core import ExposureEngine
from exposuredna.models import Entity,Dimension,Relationship

def test_coverage_resolution_diversity_compare_and_decision(tmp_path):
    e=ExposureEngine(Workspace.create(tmp_path,'ws').root);e.set_organization('Org A')
    e.add_entity(Entity(entity_id='a',entity_type='domain',value='api.old.test',dimension=Dimension.API,source='ct',evidence_ids=['E1'],metadata={'oauth_issuer':'https://id.test','source_groups':['ct','dns']}))
    e.add_entity(Entity(entity_id='b',entity_type='domain',value='api.new.test',dimension=Dimension.API,source='sdk',evidence_ids=['E2'],metadata={'oauth_issuer':'https://id.test','source_groups':['sdk']}))
    cov=e.dimension_coverage()[Dimension.API.value];assert cov['coverage']==1.0 and cov['meaning'].startswith('evidence')
    c=e.correlate()[0];assert c.confidence>0.2 and any('source diversity' in x for x in c.supporting)
    assert e.decide_resolution(c.candidate_id,'KEEP_INFERRED','needs more evidence')['decision']=='KEEP_INFERRED'
    other=tmp_path/'other.json';other.write_text(json.dumps({'entities':[Entity(entity_id='c',entity_type='domain',value='other.test',dimension=Dimension.API,source='repo',metadata={'oauth_issuer':'https://id.test'}).model_dump(mode='json')]}),encoding='utf-8')
    cmp=e.compare_dataset(other);assert cmp['ownership_established'] is False and cmp['shared_signals']

def test_lineage_and_cross_project_correlation(tmp_path):
    e=ExposureEngine(Workspace.create(tmp_path,'ws').root)
    e.add_entity(Entity(entity_id='brand',entity_type='brand',value='Brand A',dimension=Dimension.HISTORICAL,source='public',evidence_ids=['E1']))
    e.add_entity(Entity(entity_id='company',entity_type='organization',value='Company B',dimension=Dimension.HISTORICAL,source='public',evidence_ids=['E2']))
    e.add_relationship(Relationship(relationship_id='r',source_entity_id='brand',target_entity_id='company',relationship_type='acquired_by',confidence=0.8,evidence_ids=['E3']))
    assert e.organization_lineage()[0]['relationship_type']=='acquired_by'
    inp=tmp_path/'fossil.json';inp.write_text(json.dumps({'format':'fossilscope','candidates':[{'value':'old.api','status':'HYPOTHESIS','evidence_ids':['E4']}]}))
    assert e.cross_project_correlate([inp])[0]['status']=='HYPOTHESIS'
