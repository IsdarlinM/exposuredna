from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from typing import Any
from .models import Entity, Relationship, ResolutionCandidate
from .store import JsonStore
from sric.graph import GraphEdge, GraphNode, TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage, LineageRecord

MAX_IMPORT_BYTES = 10 * 1024 * 1024

def _load_json_file(path: Path) -> Any:
    if not path.is_file() or path.is_symlink(): raise ValueError("import path must be a regular non-symlink file")
    if path.stat().st_size > MAX_IMPORT_BYTES: raise ValueError(f"import exceeds {MAX_IMPORT_BYTES} byte limit")
    return __import__("json").loads(path.read_text(encoding="utf-8"))

def _upsert(items: list[dict[str, Any]], key: str, value: dict[str, Any]) -> None:
    for i, x in enumerate(items):
        if x.get(key) == value.get(key): items[i] = value; return
    items.append(value)

class ExposureEngine:
    def __init__(self, workspace: Path) -> None:
        self.workspace=workspace; self.store=JsonStore(workspace); self.graph_store=TemporalGraph(workspace); self.jobs=JobEngine(workspace); self.lineage=EvidenceLineage(workspace)
    def set_organization(self,name:str)->None:
        d=self.store.load(); d["organization"]=name; self.store.save(d)
    def add_entity(self,e:Entity)->None:
        d=self.store.load(); _upsert(d["entities"],"entity_id",e.model_dump(mode="json")); self.store.save(d)
        self.graph_store.upsert_node(GraphNode(node_id=f"exposure:{e.entity_id}",node_type=e.entity_type,label=e.value,source=e.source,first_seen=e.first_seen,last_seen=e.last_seen,observed_at=e.observed_at,evidence_ids=e.evidence_ids,metadata={"dimension":e.dimension.value,**e.metadata}))
        self._lineage_once(LineageRecord(artifact_id=f"exposure:{e.entity_id}",artifact_type="organization_entity",status="OBSERVED",source=e.source,method="entity_ingest",evidence_ids=e.evidence_ids))
    def add_relationship(self,r:Relationship)->None:
        d=self.store.load(); ids={x["entity_id"] for x in d["entities"]}
        if r.source_entity_id not in ids or r.target_entity_id not in ids: raise ValueError("relationship references unknown entity")
        _upsert(d["relationships"],"relationship_id",r.model_dump(mode="json")); self.store.save(d)
        self.graph_store.upsert_edge(GraphEdge(edge_id=f"exposure-rel:{r.relationship_id}",source_node_id=f"exposure:{r.source_entity_id}",target_node_id=f"exposure:{r.target_entity_id}",edge_type=r.relationship_type,confidence=r.confidence,evidence_ids=r.evidence_ids,counter_evidence_ids=[],discovery_method="explicit_or_reviewed_relationship",metadata={"status":r.status.value,"temporal_validity":r.temporal_validity,"counter_evidence":r.counter_evidence,"reasoning":r.reasoning}))
    def import_json(self,path:Path)->dict[str,int]:
        p=_load_json_file(path); ne=nr=0
        if p.get("organization"): self.set_organization(str(p["organization"]))
        for x in p.get("entities",[]): self.add_entity(Entity.model_validate(x)); ne+=1
        for x in p.get("relationships",[]): self.add_relationship(Relationship.model_validate(x)); nr+=1
        return {"entities":ne,"relationships":nr}
    def collect_adapter(self,path:Path,adapter:str)->int:
        from .collectors import collect_passive
        entities=collect_passive(path,adapter)
        for entity in entities:self.add_entity(entity)
        return len(entities)
    def graph(self)->dict[str,Any]: return self.store.load()
    def dimensions(self)->dict[str,int]:
        out:dict[str,int]=defaultdict(int)
        for e in self.store.load()["entities"]: out[e["dimension"]]+=1
        return dict(sorted(out.items()))
    def timeline(self)->list[dict[str,Any]]:
        out: list[dict[str, Any]]=[]
        for x in self.store.load()["entities"]:
            e=Entity.model_validate(x); out.append({"entity_id":e.entity_id,"value":e.value,"dimension":e.dimension.value,"first_seen":e.first_seen.isoformat() if e.first_seen else None,"last_seen":e.last_seen.isoformat() if e.last_seen else None,"observed_at":e.observed_at.isoformat(),"source":e.source})
        return sorted(out,key=lambda x:x["observed_at"])
    def correlate(self)->list[ResolutionCandidate]:
        d=self.store.load(); entities=[Entity.model_validate(x) for x in d["entities"]]; out: list[ResolutionCandidate]=[]
        for i,a in enumerate(entities):
            for b in entities[i+1:]:
                supporting=[]; against=[]; evidence=sorted(set(a.evidence_ids+b.evidence_ids)); score=0.0
                for k in sorted(set(a.metadata).intersection(b.metadata)):
                    if k.lower() in {"oauth_issuer","analytics_id","sdk_family","certificate_fingerprint","asn","repository_org"} and a.metadata[k]==b.metadata[k]: supporting.append(f"shared {k}: {a.metadata[k]}"); score+=0.22
                if a.value.split(".")[-2:]==b.value.split(".")[-2:] and "." in a.value and "." in b.value: supporting.append("shared registrable-domain suffix heuristic"); score+=0.12
                groups=set(str(x) for x in a.metadata.get("source_groups",[a.source])).union(str(x) for x in b.metadata.get("source_groups",[b.source]))
                if a.source==b.source or len(groups)<=1: against.append("Evidence originates from the same source family and is not independent."); score-=0.08
                elif len(groups)>=3: supporting.append(f"source diversity: {len(groups)} independent source groups"); score+=0.12
                if a.metadata.get("certificate_org") and b.metadata.get("certificate_org") and a.metadata.get("certificate_org")!=b.metadata.get("certificate_org"): against.append("Certificate organization metadata differs."); score-=0.15
                if score>=0.18: out.append(ResolutionCandidate(candidate_id=f"ER-{len(out)+1:04d}",entity_a=a.entity_id,entity_b=b.entity_id,confidence=max(0.05,min(0.95,round(score,4))),supporting=supporting,against=against,evidence_ids=evidence))
        d["resolution_queue"]=[x.model_dump(mode="json") for x in out]; self.store.save(d); return out
    def _lineage_once(self,record:LineageRecord)->None:
        try:self.lineage.explain(record.artifact_id)
        except KeyError:self.lineage.append(record)
    def dimension_coverage(self)->dict[str,dict[str,Any]]:
        entities=[Entity.model_validate(x) for x in self.store.load()["entities"]]; out={}
        for dim in sorted({e.dimension.value for e in entities}):
            items=[e for e in entities if e.dimension.value==dim]; with_evidence=sum(1 for e in items if e.evidence_ids); multi=sum(1 for e in items if len(set(str(x) for x in e.metadata.get("source_groups",[e.source])))>=2)
            out[dim]={"entities":len(items),"with_evidence":with_evidence,"multi_source_entities":multi,"coverage":round(with_evidence/len(items),4) if items else 0.0,"meaning":"evidence completeness, not security risk"}
        return out
    def organization_lineage(self)->list[dict[str,Any]]:
        allowed={"acquired_by","subsidiary_of","former_brand_of","rebranded_to","merged_into"}; rels=[Relationship.model_validate(x) for x in self.store.load()["relationships"]]
        return [{"source_entity_id":r.source_entity_id,"target_entity_id":r.target_entity_id,"relationship_type":r.relationship_type,"confidence":r.confidence,"status":r.status.value,"temporal_validity":r.temporal_validity,"evidence_ids":r.evidence_ids,"counter_evidence":r.counter_evidence} for r in rels if r.relationship_type.lower() in allowed]
    def compare_dataset(self,other:Path)->dict[str,Any]:
        payload=_load_json_file(other)
        if not isinstance(payload,dict):raise ValueError("comparison dataset must be a JSON object")
        ours=[Entity.model_validate(x) for x in self.store.load()["entities"]]; theirs=[Entity.model_validate(x) for x in payload.get("entities",[])]; shared=sorted({e.value for e in ours}.intersection(e.value for e in theirs)); signals=[]
        for a in ours:
            for b in theirs:
                for key in {"oauth_issuer","sdk_family","analytics_id","certificate_fingerprint","repository_org"}:
                    if a.metadata.get(key) and a.metadata.get(key)==b.metadata.get(key): signals.append({"signal":key,"value":a.metadata[key],"entity_a":a.entity_id,"entity_b":b.entity_id})
        return {"shared_values":shared,"shared_signals":signals,"status":"INFERRED" if shared or signals else "UNKNOWN","ownership_established":False,"note":"Similarity/correlation never establishes ownership by itself."}
    def decide_resolution(self,candidate_id:str,decision:str,note:str)->dict[str,Any]:
        decision=decision.upper()
        if decision not in {"CONFIRMED_RELATIONSHIP","REJECTED","KEEP_INFERRED"}:raise ValueError("unsupported resolution decision")
        candidate=self.explain(candidate_id); d=self.store.load(); item={"candidate_id":candidate_id,"decision":decision,"note":note,"entity_a":candidate.entity_a,"entity_b":candidate.entity_b,"evidence_ids":candidate.evidence_ids}; d["resolution_decisions"]=[x for x in d["resolution_decisions"] if x.get("candidate_id")!=candidate_id]+[item]; self.store.save(d); return item
    def cross_project_correlate(self,inputs:list[Path])->list[dict[str,Any]]:
        results=[]
        for path in inputs:
            payload=_load_json_file(path)
            if not isinstance(payload,dict):continue
            source=str(payload.get("format") or path.stem)
            for key,kind in (("candidates","candidate"),("findings","finding"),("relationships","relationship")):
                for item in payload.get(key,[]):
                    if isinstance(item,dict): results.append({"source":source,"kind":kind,"status":item.get("status","INFERRED" if kind=="relationship" else "UNKNOWN"),"value":item.get("value") or item.get("title") or item.get("relationship_type"),"evidence_ids":item.get("evidence_ids",[])})
        d=self.store.load(); d["external_correlations"]=results; self.store.save(d); return results
    def explain(self,candidate_id:str)->ResolutionCandidate:
        for x in self.store.load()["resolution_queue"]:
            if x["candidate_id"]==candidate_id:return ResolutionCandidate.model_validate(x)
        raise KeyError(candidate_id)
    def export(self)->dict[str,Any]: return {"format":"sric.organization-security-knowledge-graph","version":"0.2",**self.store.load()}
