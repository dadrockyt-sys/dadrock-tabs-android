"""Guitar-only timing/coordinate diagnostic against revalidated V3 map.

Inference remains frozen. Diagnostics are post-inference only and do not mutate timing.
"""
from __future__ import annotations
import argparse, json, tempfile
from pathlib import Path
import numpy as np

from evaluate_gomyway_full_song_professional_v2 import (
    EXPECTED_BP_SHA256, BASIC_PITCH_VERSION, sha256_file, load_audio,
    validate_reference, scorer_targets, filter_predictions, measure_for_time
)
from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from evaluate_s0_transcription_failure_attribution_v1 import run_probe
from pretrained_note_front_end_v1 import basic_pitch_model_identity

BEAT_SHIFTS=range(-8,9)

def nearest_same_midi(preds,targets):
    by={}
    for t in targets: by.setdefault(int(t["midi"]),[]).append(float(t["start"]))
    for k in by: by[k]=np.asarray(sorted(by[k]),float)
    rows=[]
    for p in preds:
        arr=by.get(int(p["midi"]))
        if arr is None or not len(arr): continue
        x=float(p["start"]); j=int(np.searchsorted(arr,x))
        cand=[]
        if j<len(arr): cand.append(arr[j])
        if j>0: cand.append(arr[j-1])
        if not cand: continue
        y=min(cand,key=lambda z:abs(z-x))
        rows.append({"predictionStart":x,"midi":int(p["midi"]),"signedErrorSeconds":x-y,"absoluteErrorSeconds":abs(x-y)})
    return rows

def segments(rows,duration):
    if not rows:return {}
    out={}
    for name,lo,hi in (("early",0,1/3),("middle",1/3,2/3),("late",2/3,1)):
        rr=[r for r in rows if lo*duration <= r["predictionStart"] < hi*duration]
        if rr:
            e=np.asarray([r["signedErrorSeconds"] for r in rr]); a=np.abs(e)
            out[name]={"count":len(rr),"meanSignedErrorSeconds":float(e.mean()),"medianAbsoluteErrorSeconds":float(np.median(a))}
    return out

def shifted_targets(targets,beat_shift,timing):
    rows=[]
    boundaries=timing["measureBoundaries"]
    # Build quarter-beat timeline from measure boundaries and meter.
    beats=[]
    for m in boundaries:
        n=int(m["meter"]["numerator"]); st=float(m["startSeconds"]); en=float(m["endSeconds"]); dur=(en-st)/n
        for b in range(n): beats.append(st+b*dur)
    beats=np.asarray(beats,float)
    # Estimate target beat index from target time and shift by integer beats.
    out=[]
    for t in targets:
        x=float(t["start"])
        j=int(np.argmin(np.abs(beats-x)))
        k=j+beat_shift
        if 0<=k<len(beats):
            delta=float(beats[k]-beats[j])
            q=dict(t); q["start"]=x+delta; out.append(q)
    return out

def simple_match(preds,targets,tol=.05):
    c=[]
    for pi,p in enumerate(preds):
        for ti,t in enumerate(targets):
            if int(p["midi"])!=int(t["midi"]): continue
            d=abs(float(p["start"])-float(t["start"]))
            if d<=tol:c.append((d,pi,ti))
    c.sort(); up=set(); ut=set(); n=0
    for d,pi,ti in c:
        if pi in up or ti in ut:continue
        up.add(pi);ut.add(ti);n+=1
    return n

def per_measure_hits(preds,targets,timing):
    out=[]
    for m in range(1,114):
        pp=[p for p in preds if measure_for_time(float(p["start"]),timing)==m]
        tt=[t for t in targets if int(t["measure"])==m]
        tp=simple_match(pp,tt)
        out.append({"measure":m,"predictionCount":len(pp),"targetCount":len(tt),"tp":tp})
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audio-source",required=True);ap.add_argument("--audio-wav",required=True)
    ap.add_argument("--timing-map",required=True);ap.add_argument("--rhythm-reference",required=True);ap.add_argument("--lead-reference",required=True)
    ap.add_argument("--model",required=True);ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    bp=basic_pitch_model_identity()
    if bp["packageVersion"]!=BASIC_PITCH_VERSION or bp["modelSha256"]!=EXPECTED_BP_SHA256: raise RuntimeError("Basic Pitch identity mismatch")
    timing=json.loads(Path(a.timing_map).read_text())
    refs={r:validate_reference(r,Path(getattr(a,f"{r}_reference"))) for r in ("rhythm","lead")}
    targets={}; excluded={}
    for r in ("rhythm","lead"): targets[r],excluded[r]=scorer_targets(r,refs[r],timing)
    audio,fs=load_audio(Path(a.audio_wav))
    stems=BsRoformer6StemOnnxAdapter(Path(a.model)).separate_array(audio,fs)
    with tempfile.TemporaryDirectory(prefix="astra_guitar_diag_") as td:
        guitar=run_probe(stems["guitar"],fs,Path(td)/"guitar.wav","guitar")
    result={"kind":"gomyway-guitar-timing-coordinate-diagnostic-v1",
            "timingMapSha256":sha256_file(Path(a.timing_map)),
            "predictionCount":len(guitar),"roles":{}}
    dur=len(audio)/float(fs)
    for role in ("rhythm","lead"):
        pp=filter_predictions(guitar,timing,excluded[role])
        near=nearest_same_midi(pp,targets[role])
        shifts=[]
        for s in BEAT_SHIFTS:
            st=shifted_targets(targets[role],s,timing)
            shifts.append({"beatShift":s,"tpAt50ms":simple_match(pp,st)})
        result["roles"][role]={
          "filteredPredictionCount":len(pp),"targetCount":len(targets[role]),
          "nearestExactMidi":{
            "count":len(near),
            "medianAbsoluteErrorSeconds":float(np.median([r["absoluteErrorSeconds"] for r in near])) if near else None,
            "meanAbsoluteErrorSeconds":float(np.mean([r["absoluteErrorSeconds"] for r in near])) if near else None,
            "segments":segments(near,dur)
          },
          "integerBeatShiftDiagnostics":shifts,
          "perMeasure":per_measure_hits(pp,targets[role],timing)
        }
    Path(a.output_json).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({
      r:{
        "nearest":result["roles"][r]["nearestExactMidi"],
        "bestBeatShift":max(result["roles"][r]["integerBeatShiftDiagnostics"],key=lambda x:x["tpAt50ms"])
      } for r in ("rhythm","lead")
    },indent=2))

if __name__=="__main__":main()
