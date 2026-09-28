#!/usr/bin/env python3
"""Model-free S12 transform/target validity diagnostics for S13 preimplementation review."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

from synthetic.s0_pilot_v1 import context5
from synthetic.s12_pilot_v1 import soften_features

BINS = 192

def _features(frames: int) -> np.ndarray:
    return np.zeros((frames, BINS), dtype=np.float32)

def _onset(frames: int) -> np.ndarray:
    return np.zeros((6, frames), dtype=np.int64)

def validated_soften(features, onset, blend):
    x = np.asarray(features)
    y = np.asarray(onset)
    if x.ndim != 2 or x.shape[1] != BINS:
        raise ValueError("features must be frames x 192")
    if y.ndim != 2 or y.shape[0] != 6 or y.shape[1] != x.shape[0]:
        raise ValueError("onset must be 6 x frames and align with features")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("nonfinite input")
    before = np.array(x, copy=True)
    out = soften_features(x, y, blend)
    if not np.array_equal(x, before):
        raise RuntimeError("soften_features mutated its input")
    return out

def _context_bins(features, frame, bins=(0,1)):
    ctx = context5(np.asarray(features, dtype=np.float32)[None, ...])[0, frame]
    result = {}
    for rel, block in zip((-2,-1,0,1,2), range(5)):
        start = block * BINS
        result[str(rel)] = [float(ctx[start+b]) for b in bins]
    return result

def build_review_evidence():
    cases = {}

    # Isolated new pitch: onset identity is visibly attenuated and next frame is recursively altered.
    x=_features(5); y=_onset(5)
    x[1,0]=1.0; x[2,0]=1.0; x[3,0]=1.0; y[0,1]=1
    z=validated_soften(x,y,0.70)
    cases["isolated_new_pitch"]={
        "blend":0.70,
        "before":[float(x[i,0]) for i in range(4)],
        "after":[float(z[i,0]) for i in range(4)],
        "targetOnsetFrames":[1],
        "contextAtOnsetBefore":_context_bins(x,1,(0,)),
        "contextAtOnsetAfter":_context_bins(z,1,(0,)),
    }

    # Repeated same pitch: existing energy is pulled toward the preceding state rather than erased.
    x=_features(5); y=_onset(5)
    x[:,0]=[0.8,1.0,1.0,0.9,0.8]; y[0,1]=1
    z=validated_soften(x,y,0.70)
    cases["repeated_same_pitch"]={
        "before":[float(v) for v in x[:,0]],
        "after":[float(v) for v in z[:,0]],
        "targetOnsetFrames":[1],
    }

    # Attack on one string while another spectral component is changing: all bins are blended.
    x=_features(5); y=_onset(5)
    x[:,0]=[0.9,0.8,0.6,0.5,0.4]  # unrelated sustained/decaying component
    x[2:,1]=1.0                    # new attack component
    y[1,2]=1
    z=validated_soften(x,y,0.70)
    cases["attack_over_sustain"]={
        "sustainBinBefore":[float(v) for v in x[:,0]],
        "sustainBinAfter":[float(v) for v in z[:,0]],
        "attackBinBefore":[float(v) for v in x[:,1]],
        "attackBinAfter":[float(v) for v in z[:,1]],
        "targetOnsetFrames":[2],
    }

    # Adjacent onsets: second onset sees data already changed by first onset.
    x=_features(5); y=_onset(5)
    x[:,0]=[0.0,1.0,0.2,1.0,1.0]; y[0,1]=1; y[1,2]=1
    z=validated_soften(x,y,0.50)
    cases["adjacent_onsets"]={
        "before":[float(v) for v in x[:,0]],
        "after":[float(v) for v in z[:,0]],
        "targetOnsetFrames":[1,2],
        "note":"frame 2 is first changed as onset+1 of frame 1, then changed again as its own onset",
    }

    # Boundaries: frame zero onset is ignored; final frame has no following-frame update.
    x=_features(4); y=_onset(4)
    x[:,0]=[1.0,0.0,0.0,1.0]; y[0,0]=1; y[0,3]=1
    z=validated_soften(x,y,0.50)
    cases["boundaries"]={
        "before":[float(v) for v in x[:,0]],
        "after":[float(v) for v in z[:,0]],
        "targetOnsetFrames":[0,3],
        "frameZeroIgnored":bool(z[0,0]==x[0,0]),
    }

    return {
        "schema":"astra-s13-preimplementation-review-evidence-v1",
        "modelRun":False,
        "optimizerSteps":0,
        "p1Accessed":False,
        "p2Accessed":False,
        "p3Opened":False,
        "cases":cases,
    }

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a=ap.parse_args()
    evidence=build_review_evidence()
    Path(a.out).write_text(json.dumps(evidence, indent=2, sort_keys=True)+"\n")
    print(json.dumps(evidence, sort_keys=True))

if __name__=="__main__":
    main()
