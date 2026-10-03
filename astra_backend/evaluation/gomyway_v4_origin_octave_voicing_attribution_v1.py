"""Octave/voicing attribution diagnostic for frozen Go My Way V4-origin note evidence.

Measures error structure only. Does not mutate predictions or timing.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

EXPECTED_SCORER_SHA256={
 "rhythm":"d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555",
 "lead":"8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be",
 "bass":"39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1",
}
ONSET_TOL=0.05

def sha256_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def load_ref(role,path):
    if sha256_file(path)!=EXPECTED_SCORER_SHA256[role]:
        raise RuntimeError(f"{role} reference hash mismatch")
    return json.loads(Path(path).read_text())

def excluded(ref):
    p=ref.get("normalizationPolicy",{})
    out=set(int(x) for x in p.get("excludedSourceMeasures",[]))
    if p.get("measure88Excluded") is True: out.add(88)
    return out

def target_rows(role,ref,timing):
    bm={int(r["measureNumber"]):r for r in timing["measureBoundaries"]}
    ex=excluded(ref); out=[]
    for i,n in enumerate(ref["notes"]):
        m=int(n["measure"])
        if m in ex: continue
        b=bm[m]; step=float(n["step"])
        start=float(b["startSeconds"])+(step/16.0)*float(b["durationSeconds"])
        out.append({"id":f"{role}:{i}","midi":int(n["midi"]),"start":start,"measure":m,"step":step})
    return out,ex

def measure_for_time(t,timing):
    for r in timing["measureBoundaries"]:
        if float(r["startSeconds"])<=t<float(r["endSeconds"]): return int(r["measureNumber"])
    return None

def filter_preds(preds,timing,ex):
    first=float(timing["measureBoundaries"][0]["startSeconds"])
    last=float(timing["measureBoundaries"][-1]["endSeconds"])
    out=[]
    for p in preds:
        t=float(p["start"])
        if not(first<=t<last): continue
        m=measure_for_time(t,timing)
        if m is None or m in ex: continue
        q=dict(p); q["measure"]=m; out.append(q)
    return out

def onset_match(preds,targets):
    cand=[]
    for pi,p in enumerate(preds):
        ps=float(p["start"])
        for ti,t in enumerate(targets):
            d=abs(ps-float(t["start"]))
            if d<=ONSET_TOL: cand.append((d,pi,ti))
    cand.sort(key=lambda x:(x[0],x[1],x[2]))
    up=set();ut=set();rows=[]
    for d,pi,ti in cand:
        if pi in up or ti in ut: continue
        up.add(pi);ut.add(ti)
        p=preds[pi];t=targets[ti]
        delta=int(p["midi"])-int(t["midi"])
        rows.append({
          "predictionMidi":int(p["midi"]),"targetMidi":int(t["midi"]),
          "midiDelta":delta,"predictionStart":float(p["start"]),
          "targetStart":float(t["start"]),"onsetErrorSeconds":float(d),
          "measure":int(t["measure"]),"step":float(t["step"])
        })
    return rows

def role_summary(rows,target_count):
    wrong=[r for r in rows if r["midiDelta"]!=0]
    octv=[r for r in wrong if abs(r["midiDelta"]) in (12,24,36)]
    pitch_class=[r for r in wrong if r["midiDelta"]%12==0]
    exact=sum(r["midiDelta"]==0 for r in rows)
    hist={}
    for r in wrong:
        d=str(r["midiDelta"]); hist[d]=hist.get(d,0)+1
    interval_class={}
    for r in wrong:
        ic=abs(r["midiDelta"])%12
        k=str(ic); interval_class[k]=interval_class.get(k,0)+1
    return {
      "targetCount":target_count,
      "onsetMatchedCount":len(rows),
      "exactMidiCount":exact,
      "wrongMidiCount":len(wrong),
      "pitchClassCorrectButWrongOctaveCount":len(pitch_class),
      "pitchClassCorrectButWrongOctaveRateOfWrong":len(pitch_class)/len(wrong) if wrong else None,
      "recoverableBySingleOctavePlusMinus12Count":sum(abs(r["midiDelta"])==12 for r in wrong),
      "recoverableByAnyOctaveMultipleCount":len(octv),
      "singleOctaveRecoveryUpperBoundExactMidiCount":exact+sum(abs(r["midiDelta"])==12 for r in wrong),
      "singleOctaveRecoveryUpperBoundRateAmongOnsetMatched":(exact+sum(abs(r["midiDelta"])==12 for r in wrong))/len(rows) if rows else None,
      "midiDeltaHistogramWrongOnly":dict(sorted(hist.items(),key=lambda kv:int(kv[0]))),
      "intervalClassHistogramWrongOnly":dict(sorted(interval_class.items(),key=lambda kv:int(kv[0]))),
      "topAbsoluteIntervals":[
        {"semitones":k,"count":v}
        for k,v in sorted(
          ((n,sum(abs(r["midiDelta"])==n for r in wrong)) for n in sorted(set(abs(r["midiDelta"]) for r in wrong))),
          key=lambda x:(-x[1],x[0])
        )[:12]
      ],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--note-evidence",required=True);ap.add_argument("--timing-map",required=True)
    ap.add_argument("--rhythm-reference",required=True);ap.add_argument("--lead-reference",required=True);ap.add_argument("--bass-reference",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    ev=json.loads(Path(a.note_evidence).read_text())
    timing=json.loads(Path(a.timing_map).read_text())
    if ev["timingMap"]["sha256"]!=sha256_file(a.timing_map): raise RuntimeError("timing binding mismatch")
    source={"rhythm":"guitar","lead":"guitar","bass":"bass"}
    roles={}
    for role in ("rhythm","lead","bass"):
        ref=load_ref(role,getattr(a,f"{role}_reference"))
        targ,ex=target_rows(role,ref,timing)
        preds=filter_preds(ev["predictions"][source[role]],timing,ex)
        rows=onset_match(preds,targ)
        roles[role]={"summary":role_summary(rows,len(targ)),"matches":rows}
    out={
      "schemaVersion":1,
      "kind":"gomyway-v4-origin-octave-voicing-attribution-v1",
      "noteEvidenceSha256":sha256_file(a.note_evidence),
      "timingMapSha256":sha256_file(a.timing_map),
      "onsetToleranceSeconds":ONSET_TOL,
      "predictionMutation":False,
      "roles":roles,
      "interpretationBoundary":"Attribution/upper-bound diagnostic only; no corrections applied."
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({r:roles[r]["summary"] for r in roles},indent=2))

if __name__=="__main__":main()
