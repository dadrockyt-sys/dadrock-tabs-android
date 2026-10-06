"""Reference-note-blind V4-origin 16th-grid quantizer for frozen Basic Pitch guitar events.

Uses only:
- frozen Basic Pitch guitar note evidence
- frozen V4-origin measure boundaries

Does not read rhythm/lead note references.
Does not add/drop/change MIDI notes.
Every in-range onset is snapped to the nearest 1/16 grid point.
Duration is preserved by shifting end by the same delta.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def grid_points(timing):
    pts=[]
    bounds=timing["measureBoundaries"]
    for b in bounds:
        m=int(b["measureNumber"])
        start=float(b["startSeconds"]); dur=float(b["durationSeconds"])
        for step in range(16):
            pts.append((start+(step/16.0)*dur,m,step))
    if bounds:
        b=bounds[-1]
        pts.append((float(b["endSeconds"]),int(b["measureNumber"])+1,0))
    pts.sort()
    return pts

def nearest_grid(t,pts):
    # Full scan is deterministic and tiny (~1800 points).
    return min(pts,key=lambda x:(abs(x[0]-t),x[0],x[1],x[2]))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--note-evidence",required=True)
    ap.add_argument("--timing-map",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    ev=json.loads(Path(a.note_evidence).read_text())
    timing=json.loads(Path(a.timing_map).read_text())
    preds=ev["predictions"]["guitar"]
    pts=grid_points(timing)
    lo=float(timing["measureBoundaries"][0]["startSeconds"])
    hi=float(timing["measureBoundaries"][-1]["endSeconds"])

    out_preds=[];moves=[]
    for p in preds:
        q=dict(p)
        t=float(p["start"])
        if lo <= t <= hi:
            gt,m,step=nearest_grid(t,pts)
            delta=gt-t
            q["originalStart"]=t
            q["start"]=float(gt)
            if "end" in q:
                q["end"]=float(q["end"])+delta
            q["quantizedMeasure"]=m
            q["quantizedStep16"]=step
            q["quantizationDeltaSeconds"]=float(delta)
            moves.append(abs(delta))
        else:
            q["quantizationDeltaSeconds"]=0.0
        out_preds.append(q)

    moved=sum(1 for x in moves if x>1e-12)
    s=sorted(moves)
    def pct(p):
        if not s:return 0.0
        idx=min(len(s)-1,max(0,int(math.ceil(p*len(s))-1)))
        return float(s[idx])
    out={
      "schemaVersion":1,
      "kind":"gomyway-v4-origin-guitar-grid-quantization-v1",
      "referenceNoteBlind":True,
      "professionalRhythmLeadReferenceRead":False,
      "noteEvidenceSha256":sha(a.note_evidence),
      "timingMapSha256":sha(a.timing_map),
      "grid":"nearest 1/16 position in frozen V4-origin measure map",
      "pitchMutation":False,
      "noteAddition":False,
      "noteDeletion":False,
      "inputCount":len(preds),
      "outputCount":len(out_preds),
      "movement":{
        "inRange":len(moves),
        "moved":moved,
        "meanAbsSeconds":float(sum(moves)/len(moves)) if moves else 0.0,
        "medianAbsSeconds":pct(0.5),
        "p90AbsSeconds":pct(0.9),
        "maxAbsSeconds":float(max(moves)) if moves else 0.0
      },
      "predictions":{"guitar":out_preds},
      "interpretationBoundary":"Post-hoc Go My Way research timing map is frozen. No professional note reference is read during candidate construction; no tunable snap threshold exists."
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"inputCount":len(preds),"outputCount":len(out_preds),"movement":out["movement"]},sort_keys=True))

if __name__=="__main__":main()
