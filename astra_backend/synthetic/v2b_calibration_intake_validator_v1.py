#!/usr/bin/env python3
from __future__ import annotations
import json, math
from pathlib import Path

REQ_COVERAGE={
  "clean-capture","distorted-or-overdriven-capture","single-note",
  "repeated-attacks","legato-bend-slide","chordal-polyphonic"
}
class V2BValidationError(ValueError): pass

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)): raise V2BValidationError(name)
    v=float(v)
    if not math.isfinite(v): raise V2BValidationError(name)
    return v

def validate_v2b(x):
    if x.get("schema")!="astra-v2b-calibration-development-intake-v1":
        raise V2BValidationError("schema")
    ind=x.get("independence") or {}
    for k in ("noV1_1Overlap","noV1_1NearDuplicates","noP1Overlap","noP2Overlap","noP3Overlap","noPreviouslyModelInspectedAudio"):
        if ind.get(k) is not True: raise V2BValidationError("independence:"+k)
    if not isinstance(ind.get("declaration"),str) or not ind["declaration"].strip():
        raise V2BValidationError("independence declaration")

    clips=x.get("clips")
    if not isinstance(clips,list) or len(clips)<16: raise V2BValidationError("clip count")

    pos=[c for c in clips if c.get("kind")=="positive"]
    neg=[c for c in clips if c.get("kind")=="negative-only"]
    if len(pos)<12 or len(neg)<4: raise V2BValidationError("class counts")

    ids=set(); possec=negsec=0.0; creators=set(); coverage=set()
    for c in clips:
        cid=c.get("id")
        if not isinstance(cid,str) or not cid or cid in ids: raise V2BValidationError("id")
        ids.add(cid)
        sha=c.get("sha256")
        if not isinstance(sha,str) or len(sha)!=64: raise V2BValidationError("sha")
        d=_num(c.get("durationSeconds"),cid+":duration")
        if d<4 or d>10: raise V2BValidationError(cid+":duration-range")
        creator=c.get("creatorOrCaptureChain")
        if not isinstance(creator,str) or not creator.strip(): raise V2BValidationError(cid+":creator")
        creators.add(creator.strip())
        tags=c.get("coverage",[])
        if not isinstance(tags,list): raise V2BValidationError(cid+":coverage")
        coverage.update(tags)
        if c.get("kind")=="positive":
            possec+=d
            anns=c.get("annotations")
            if not isinstance(anns,list) or not anns: raise V2BValidationError(cid+":annotations")
        else:
            negsec+=d
            if c.get("annotations") not in ([],None): raise V2BValidationError(cid+":negative-annotations")

    if possec<60 or negsec<20: raise V2BValidationError("duration minima")
    if len(creators)<2: raise V2BValidationError("creator diversity")
    if not REQ_COVERAGE.issubset(coverage): raise V2BValidationError("coverage")

    if x.get("annotationsFrozenBeforeInference") is not True: raise V2BValidationError("annotations freeze")
    if x.get("modelInferenceCount")!=0 or x.get("optimizerSteps")!=0: raise V2BValidationError("pre-inference execution")
    for k in ("p1Accessed","p2Accessed","p3Accessed","v1_1AccessedForTuning"):
        if x.get(k) is not False: raise V2BValidationError(k)
    return True

def validate_file(path):
    return validate_v2b(json.loads(Path(path).read_text()))
