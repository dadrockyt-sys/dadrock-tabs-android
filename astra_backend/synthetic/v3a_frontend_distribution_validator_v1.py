#!/usr/bin/env python3
from __future__ import annotations
import json, math
from pathlib import Path

class V3AValidationError(ValueError): pass

def _finite(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)): raise V3AValidationError(name)
    x=float(v)
    if not math.isfinite(x): raise V3AValidationError(name)
    return x

def validate(data):
    if data.get("schema")!="astra-v3a-frontend-distribution-audit-result-v1":
        raise V3AValidationError("schema")
    for side in ("synthetic","real"):
        x=data.get(side)
        if not isinstance(x,dict): raise V3AValidationError(side)
        s=x.get("summary",{})
        if s.get("frames",0)<=0: raise V3AValidationError(side+":frames")
        for k in ("mean","std","median","mad","floorOccupancy"):
            a=s.get(k)
            if not isinstance(a,list) or len(a)!=192: raise V3AValidationError(side+":"+k)
            for i,v in enumerate(a): _finite(v,f"{side}:{k}:{i}")
    d=data.get("distances",{})
    for k in ("standardizedMeanDifference","wassersteinPerBin","rangeOverlapPerBin"):
        a=d.get(k)
        if not isinstance(a,list) or len(a)!=192: raise V3AValidationError(k)
        for i,v in enumerate(a): _finite(v,f"{k}:{i}")
    for k in ("medianAbsoluteSmd","fractionAbsSmdAtLeast1","fractionAbsSmdAtLeast2","wassersteinMedian","wassersteinP95","rangeOverlapMedian"):
        _finite(d.get(k),k)
    e=data.get("execution",{})
    if e.get("modelInferenceCount")!=0 or e.get("optimizerSteps")!=0 or e.get("thresholdSearch") is not False or e.get("frontendChanged") is not False:
        raise V3AValidationError("execution")
    g=data.get("guards",{})
    for k in ("v1_1Used","p1Accessed","p2Accessed","p3Accessed","a2Opened"):
        if g.get(k) is not False: raise V3AValidationError(k)
    return True

def validate_file(path):
    return validate(json.loads(Path(path).read_text()))
