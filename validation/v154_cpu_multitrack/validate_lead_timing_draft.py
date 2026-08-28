#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'research/v154-professional-references/lead-professional-reference-machine-readable.json'
TIM=ROOT/'research/v154-professional-references/lead-source-local-attack-timing-draft.json'
EXPECTED_SRC_SHA='122e0f6b2fa63fb2ea701e9cefe897dd4337fd08de0792e11579f4933804b716'
EXPECTED_TIM_SHA='32107c2b09ec3d2322fa141c550a98569ea1b1a4c8e5ed92c6db062596e2df15'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)==EXPECTED_SRC_SHA,(sha(SRC),EXPECTED_SRC_SHA)
assert sha(TIM)==EXPECTED_TIM_SHA,(sha(TIM),EXPECTED_TIM_SHA)
s=json.loads(SRC.read_text()); t=json.loads(TIM.read_text())
assert t['policy']['candidateRead'] is False and t['policy']['scoringPerformed'] is False
ms=s['measures']; sb=t['stepsByMeasure']
assert len(ms)==113 and set(sb)=={str(i) for i in range(1,114)}
mismatch=[]
source_events=pitched=dead=cont=0
for mo in ms:
 m=mo['measure']; ev=mo['events']; st=sb[str(m)]
 source_events+=len(ev)
 pitched+=sum(e.get('kind')=='note' for e in ev)
 dead+=sum(e.get('kind')=='deadNote' for e in ev)
 cont+=sum(bool(e.get('continuationOnly')) for e in ev)
 if len(ev)!=len(st): mismatch.append({'measure':m,'events':len(ev),'steps':len(st),'eventKinds':[e.get('kind') for e in ev],'visualOrders':[e.get('visualOrder') for e in ev]})
print(json.dumps({'sourceEvents':source_events,'pitched':pitched,'dead':dead,'continuationOnly':cont,'timingEntries':sum(len(v) for v in sb.values()),'mismatches':mismatch,'candidateRead':False,'scoringPerformed':False},indent=2))
if mismatch: raise SystemExit(2)
assert source_events==487 and pitched==476 and dead==11 and cont==23
