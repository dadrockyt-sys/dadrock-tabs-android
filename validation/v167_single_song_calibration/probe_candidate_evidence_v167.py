#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

EVENT_HINTS={"midi","measure","step","absoluteGridStep","confidence","score","rank","onset","time"}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--candidate',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    if a.output.exists(): raise RuntimeError(f'output exists: {a.output}')
    root=json.loads(a.candidate.read_text())
    path_types=Counter(); list_sizes=[]; object_keysets=Counter(); numeric_fields=defaultdict(list); eventish=[]
    def walk(v:Any,path:str):
        path_types[(path,type(v).__name__)]+=1
        if isinstance(v,dict):
            ks=tuple(sorted(v.keys())); object_keysets[ks]+=1
            overlap=sorted(set(v.keys()) & EVENT_HINTS)
            if len(overlap)>=2:
                eventish.append({"path":path,"keys":sorted(v.keys())[:80],"hintKeys":overlap})
            for k,x in v.items():
                if isinstance(x,(int,float)) and not isinstance(x,bool):
                    numeric_fields[k].append(float(x))
                walk(x,f'{path}.{k}' if path else k)
        elif isinstance(v,list):
            list_sizes.append({"path":path,"size":len(v)})
            for i,x in enumerate(v[:2000]): walk(x,f'{path}[]')
    walk(root,'')
    numeric_summary={}
    for k,vals in numeric_fields.items():
        if len(vals)>=2:
            numeric_summary[k]={"count":len(vals),"min":min(vals),"max":max(vals),"mean":sum(vals)/len(vals)}
    top_keysets=[{"count":c,"keys":list(k)} for k,c in object_keysets.most_common(50)]
    report={
      "schema":"dadrock.tabs.v167.candidate-evidence-probe.v1","version":"V167",
      "topLevelKeys":sorted(root.keys()),
      "largestLists":sorted(list_sizes,key=lambda r:(-r['size'],r['path']))[:100],
      "topObjectKeysets":top_keysets,
      "numericFieldSummary":dict(sorted(numeric_summary.items())),
      "eventishObjectSamples":eventish[:250],
      "policy":{"referenceRead":False,"candidateModified":False}
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({"topLevelKeys":report['topLevelKeys'],"largestLists":report['largestLists'][:25],"numericFields":list(report['numericFieldSummary'])},indent=2))
if __name__=='__main__': main()
