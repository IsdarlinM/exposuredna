import json
from exposuredna.core import ExposureEngine

def test_passive_source_adapters_create_typed_entities(tmp_path):
    ws=tmp_path/'ws';ws.mkdir();(ws/'workspace.json').write_text('{}');engine=ExposureEngine(ws)
    oauth=tmp_path/'oauth.json';oauth.write_text(json.dumps({'issuer':'https://login.example.com','audience':'api'}));assert engine.collect_adapter(oauth,'oauth')>=1
    asn=tmp_path/'asn.json';asn.write_text(json.dumps({'origin':'AS64500'}));assert engine.collect_adapter(asn,'asn')==1
    entities=engine.store.load()['entities'];assert any(x['dimension']=='IDENTITY_DNA' for x in entities);assert any(x['value']=='AS64500' for x in entities)

def test_unknown_adapter_fails_closed(tmp_path):
    ws=tmp_path/'ws';ws.mkdir();(ws/'workspace.json').write_text('{}');p=tmp_path/'x.txt';p.write_text('data')
    try:ExposureEngine(ws).collect_adapter(p,'mass-scan')
    except ValueError as exc:assert 'unsupported passive adapter' in str(exc)
    else:raise AssertionError('unknown adapter must fail closed')
