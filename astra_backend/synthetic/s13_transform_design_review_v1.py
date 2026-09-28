#!/usr/bin/env python3
"""Model-free review of one prospective onset-robustness transform for S13."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

BINS=192
DEFAULT_RETAIN_FRACTION=0.5

def onset_frames(onset):
    y=np.asarray(onset)
    if y.ndim!=2 or y.shape[0]!=6:
        raise ValueError("onset must be 6 x frames")
    return sorted(int(i) for i in np.flatnonzero(np.any(y>0,axis=0)) if int(i)>0)

def compress_positive_onset_increments(features,onset,retain_fraction=DEFAULT_RETAIN_FRACTION):
    """
    At labeled onset frames only, compress positive frame-to-frame CQT increments.
    Non-rising bins are bit-preserved. Each frame is computed from the immutable
    source array, so adjacent onsets cannot recursively contaminate one another.
    """
    x=np.asarray(features,dtype=np.float32)
    y=np.asarray(onset)
    if x.ndim!=2 or x.shape[1]!=BINS:
        raise ValueError("features must be frames x 192")
    if y.ndim!=2 or y.shape!=(6,x.shape[0]):
        raise ValueError("onset must be 6 x frames and align with features")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("nonfinite input")
    if np.any(x<0.0) or np.any(x>1.0):
        raise ValueError("features outside frozen [0,1] range")
    r=float(retain_fraction)
    if not (0.0<r<=1.0):
        raise ValueError("retain_fraction must be in (0,1]")
    src=np.array(x,copy=True)
    out=np.array(x,copy=True)
    for f in onset_frames(y):
        prev=src[f-1]
        cur=src[f]
        positive=np.maximum(cur-prev,0.0)
        out[f]=cur-(1.0-r)*positive
    if not np.isfinite(out).all():
        raise RuntimeError("nonfinite output")
    return out

def _features(frames):
    return np.zeros((frames,BINS),dtype=np.float32)

def _onset(frames):
    return np.zeros((6,frames),dtype=np.int64)

def build_review_evidence():
    cases={}

    x=_features(5); y=_onset(5)
    x[:,0]=[0,1,1,1,1]; y[0,1]=1
    z=compress_positive_onset_increments(x,y,0.5)
    cases["isolated_new_pitch"]={"before":x[:,0].tolist(),"after":z[:,0].tolist(),"onsets":[1]}

    x=_features(5); y=_onset(5)
    x[:,0]=[0.8,1.0,1.0,0.9,0.8]; y[0,1]=1
    z=compress_positive_onset_increments(x,y,0.5)
    cases["repeated_same_pitch"]={"before":x[:,0].tolist(),"after":z[:,0].tolist(),"onsets":[1]}

    x=_features(5); y=_onset(5)
    x[:,0]=[0.9,0.8,0.6,0.5,0.4]
    x[2:,1]=1.0
    y[1,2]=1
    z=compress_positive_onset_increments(x,y,0.5)
    cases["attack_over_sustain"]={
        "sustainBefore":x[:,0].tolist(),"sustainAfter":z[:,0].tolist(),
        "attackBefore":x[:,1].tolist(),"attackAfter":z[:,1].tolist(),"onsets":[2],
    }

    x=_features(5); y=_onset(5)
    x[:,0]=[0.0,1.0,0.2,1.0,1.0]; y[0,1]=1; y[1,2]=1
    z=compress_positive_onset_increments(x,y,0.5)
    cases["adjacent_onsets"]={"before":x[:,0].tolist(),"after":z[:,0].tolist(),"onsets":[1,2]}

    x=_features(4); y=_onset(4)
    x[:,0]=[1.0,0.0,0.0,1.0]; y[0,0]=1; y[0,3]=1
    z=compress_positive_onset_increments(x,y,0.5)
    cases["boundaries"]={"before":x[:,0].tolist(),"after":z[:,0].tolist(),"onsets":[0,3]}

    x=_features(4); y=_onset(4)
    x[:,0]=[0.1,0.7,0.7,0.7]
    x[:,1]=[0.2,0.5,0.5,0.5]  # unrelated rising energy at same acoustic frame
    y[0,1]=1
    z=compress_positive_onset_increments(x,y,0.5)
    cases["simultaneous_unattributed_rise"]={
        "beforeBin0":x[:,0].tolist(),"afterBin0":z[:,0].tolist(),
        "beforeBin1":x[:,1].tolist(),"afterBin1":z[:,1].tolist(),
        "limitation":"transform is representation-local, not string-source-separating",
    }

    return {
        "schema":"astra-s13-transform-design-review-v1",
        "transform":"positive-onset-increment-compression",
        "retainFractionDemonstration":0.5,
        "properties":{
            "usesImmutableSource":True,
            "changesOnlyLabeledOnsetFrames":True,
            "changesOnlyPositiveIncrements":True,
            "nonRisingBinsPreserved":True,
            "followingFrameMutation":False,
            "adjacentOnsetRecursion":False,
            "stringSourceSelective":False,
        },
        "modelRun":False,"optimizerSteps":0,
        "p1Accessed":False,"p2Accessed":False,"p3Opened":False,
        "cases":cases,
    }

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    e=build_review_evidence()
    Path(a.out).write_text(json.dumps(e,indent=2,sort_keys=True)+"\n")
    print(json.dumps(e,sort_keys=True))

if __name__=="__main__":
    main()
