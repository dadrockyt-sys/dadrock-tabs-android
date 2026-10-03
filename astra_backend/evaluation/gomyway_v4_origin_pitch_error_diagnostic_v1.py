"""Pitch-error diagnostic from frozen Go My Way V4-origin note evidence.

Post-inference diagnostic only:
- reads frozen raw predictions
- onset-matches without MIDI first
- measures MIDI error distribution
- does not mutate or retune predictions
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

EXPECTED_SCORER_SHA256 = {
    "rhythm": "d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555",
    "bass": "39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1",
    "lead": "8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be",
}

def sha256_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def validate_reference(role,path):
    actual=sha256_file(path)
    if actual != EXPECTED_SCORER_SHA256[role]:
        raise RuntimeError(f"{role} scorer SHA mismatch: {actual}")
    d=json.loads(Path(path).read_text())
    if int(d.get("counts",{}).get("measures",-1)) != 113:
        raise RuntimeError(f"{role} scorer measure count mismatch")
    return d

def excluded_measures(ref):
    p=ref.get("normalizationPolicy",{})
    out=set(int(x) for x in p.get("excludedSourceMeasures",[]))
    if p.get("measure88Excluded") is True:
        out.add(88)
    return out

def boundaries_map(timing):
    rows={int(r["measureNumber"]):r for r in timing["measureBoundaries"]}
    if set(rows) != set(range(1,114)):
        raise RuntimeError("timing map must cover measures 1..113")
    return rows

def scorer_targets(role,ref,timing):
    bounds=boundaries_map(timing)
    excluded=excluded_measures(ref)
    targets=[]
    for i,note in enumerate(ref.get("notes",[])):
        m=int(note["measure"])
        if m in excluded:
            raise RuntimeError(f"{role} scorer unexpectedly contains excluded measure {m}")
        step=float(note["step"])
        b=bounds[m]
        start=float(b["startSeconds"])+(step/16.0)*float(b["durationSeconds"])
        targets.append({"id":f"{role}:{i}:m{m}:s{step}","role":role,"midi":int(note["midi"]),
                        "start":start,"measure":m,"step":step})
    targets.sort(key=lambda x:(x["start"],x["midi"],x["id"]))
    return targets,excluded

def measure_for_time(t,timing):
    for row in timing["measureBoundaries"]:
        if float(row["startSeconds"]) <= t < float(row["endSeconds"]):
            return int(row["measureNumber"])
    return None

def filter_predictions(predictions,timing,excluded):
    first=float(timing["measureBoundaries"][0]["startSeconds"])
    last=float(timing["measureBoundaries"][-1]["endSeconds"])
    out=[]
    for p in predictions:
        t=float(p["start"])
        if t < first or t >= last:
            continue
        m=measure_for_time(t,timing)
        if m is None or m in excluded:
            continue
        q=dict(p); q["measure"]=m; out.append(q)
    return out

ONSET_TOL=0.05

def match_onset_only(preds, targets, tol=ONSET_TOL):
    candidates=[]
    for pi,p in enumerate(preds):
        ps=float(p["start"])
        for ti,t in enumerate(targets):
            d=abs(ps-float(t["start"]))
            if d<=tol:
                candidates.append((d,pi,ti))
    candidates.sort(key=lambda x:(x[0],x[1],x[2]))
    up=set(); ut=set(); rows=[]
    for d,pi,ti in candidates:
        if pi in up or ti in ut: continue
        up.add(pi); ut.add(ti)
        p=preds[pi]; t=targets[ti]
        delta=int(p["midi"])-int(t["midi"])
        rows.append({
          "predictionId":p["id"],"targetId":t["id"],
          "predictionStart":float(p["start"]),"targetStart":float(t["start"]),
          "onsetErrorSeconds":float(d),
          "predictionMidi":int(p["midi"]),"targetMidi":int(t["midi"]),
          "midiDelta":delta,"measure":int(t["measure"]),"step":float(t["step"])
        })
    return rows

def summarize(rows, target_count, pred_count):
    deltas=np.asarray([r["midiDelta"] for r in rows],int) if rows else np.asarray([],int)
    exact=int(np.sum(deltas==0)) if len(deltas) else 0
    buckets={
      "exact": exact,
      "plusMinus1":int(np.sum(np.abs(deltas)==1)) if len(deltas) else 0,
      "plusMinus2":int(np.sum(np.abs(deltas)==2)) if len(deltas) else 0,
      "plusMinus3to5":int(np.sum((np.abs(deltas)>=3)&(np.abs(deltas)<=5))) if len(deltas) else 0,
      "octavePlusMinus12":int(np.sum(np.abs(deltas)==12)) if len(deltas) else 0,
      "other":int(np.sum(~(
        (deltas==0)|(np.abs(deltas)==1)|(np.abs(deltas)==2)|
        ((np.abs(deltas)>=3)&(np.abs(deltas)<=5))|(np.abs(deltas)==12)
      ))) if len(deltas) else 0
    }
    hist={}
    for d in sorted(set(int(x) for x in deltas)):
        hist[str(d)]=int(np.sum(deltas==d))
    absd=np.abs(deltas) if len(deltas) else np.asarray([],int)
    return {
      "predictionCount":pred_count,
      "targetCount":target_count,
      "onsetMatchedCount":len(rows),
      "onsetMatchedTargetRecall":len(rows)/target_count if target_count else None,
      "exactMidiAmongOnsetMatched":exact,
      "exactMidiRateAmongOnsetMatched":exact/len(rows) if rows else None,
      "medianAbsoluteMidiErrorSemitones":float(np.median(absd)) if len(absd) else None,
      "meanAbsoluteMidiErrorSemitones":float(np.mean(absd)) if len(absd) else None,
      "buckets":buckets,
      "midiDeltaHistogram":hist
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--note-evidence",required=True)
    ap.add_argument("--timing-map",required=True)
    ap.add_argument("--rhythm-reference",required=True)
    ap.add_argument("--lead-reference",required=True)
    ap.add_argument("--bass-reference",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()

    evidence=json.loads(Path(a.note_evidence).read_text())
    timing=json.loads(Path(a.timing_map).read_text())
    if evidence["timingMap"]["sha256"] != sha256_file(Path(a.timing_map)):
        raise RuntimeError("timing map hash mismatch")

    refs={r:validate_reference(r,Path(getattr(a,f"{r}_reference"))) for r in ("rhythm","lead","bass")}
    targets={}; excluded={}
    for r in ("rhythm","lead","bass"):
        targets[r],excluded[r]=scorer_targets(r,refs[r],timing)

    source={"rhythm":"guitar","lead":"guitar","bass":"bass"}
    roles={}
    for role in ("rhythm","lead","bass"):
        preds=filter_predictions(evidence["predictions"][source[role]],timing,excluded[role])
        rows=match_onset_only(preds,targets[role])
        roles[role]={
          "summary":summarize(rows,len(targets[role]),len(preds)),
          "matches":rows
        }

    out={
      "schemaVersion":1,
      "kind":"gomyway-v4-origin-pitch-error-diagnostic-v1",
      "noteEvidenceSha256":sha256_file(Path(a.note_evidence)),
      "timingMapSha256":sha256_file(Path(a.timing_map)),
      "onsetToleranceSeconds":ONSET_TOL,
      "predictionMutation":False,
      "roles":roles,
      "interpretationBoundary":"Onset-first diagnostic only. No candidate is altered or promoted."
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({r:roles[r]["summary"] for r in roles},indent=2))

if __name__=="__main__":main()
