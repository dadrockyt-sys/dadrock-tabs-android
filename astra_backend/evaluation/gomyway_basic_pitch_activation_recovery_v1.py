"""Reference-blind raw-activation recovery decoder V1 for Go My Way guitar.

Purpose:
- start from the frozen Basic Pitch thresholded guitar note evidence;
- add only activation-supported onset/pitch candidates from the frozen raw tensors;
- reuse the already-frozen Basic Pitch thresholds and minimum-note-length scale;
- do not read professional rhythm/lead references;
- do not assign rhythm/lead roles.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

MIDI_OFFSET = 21
ONSET_THRESHOLD = 0.5
FRAME_THRESHOLD = 0.3
MIN_NOTE_MS = 127.70

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def local_max(a, i):
    lo=max(0,i-1); hi=min(len(a),i+2)
    return a[i] >= np.max(a[lo:hi])

def dedup(existing, added, tol):
    out=[dict(p) for p in existing]
    for q in added:
        duplicate=False
        for p in out:
            if int(p["midi"])==int(q["midi"]) and abs(float(p["start"])-float(q["start"]))<=tol:
                duplicate=True; break
        if not duplicate: out.append(q)
    out.sort(key=lambda x:(float(x["start"]),int(x["midi"])))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--activations-npz",required=True)
    ap.add_argument("--activations-meta",required=True)
    ap.add_argument("--note-evidence",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()

    meta=json.loads(Path(a.activations_meta).read_text())
    if sha(a.activations_npz)!=meta["npzSha256"]:
        raise RuntimeError("activation NPZ hash mismatch")

    ev=json.loads(Path(a.note_evidence).read_text())
    base=ev["predictions"]["guitar"]

    z=np.load(a.activations_npz)
    note=np.asarray(z["note"],dtype=float)
    onset=np.asarray(z["onset"],dtype=float)
    if note.shape!=onset.shape or note.ndim!=2 or note.shape[1]!=88:
        raise RuntimeError(f"unexpected activation shapes: {note.shape}, {onset.shape}")

    duration=float(meta["audioDurationSeconds"])
    frame_dt=duration/max(1,note.shape[0]-1)
    min_sep=max(1,int(round((MIN_NOTE_MS/1000.0)/frame_dt)))
    tol=(MIN_NOTE_MS/1000.0)/2.0

    candidates=[]
    for pitch in range(note.shape[1]):
        last=-10**9
        for i in range(note.shape[0]):
            if onset[i,pitch] < ONSET_THRESHOLD or note[i,pitch] < FRAME_THRESHOLD:
                continue
            if not local_max(onset[:,pitch],i):
                continue
            if i-last < min_sep:
                continue
            t=i*frame_dt
            candidates.append({
                "midi": int(pitch+MIDI_OFFSET),
                "start": float(t),
                "source": "rawActivationRecoveryV1",
                "onsetActivation": float(onset[i,pitch]),
                "frameActivation": float(note[i,pitch]),
            })
            last=i

    combined=dedup(base,candidates,tol)
    recovered=len(combined)-len(base)
    out={
      "schemaVersion":1,
      "kind":"gomyway-reference-blind-basic-pitch-activation-recovery-v1",
      "referenceBlind":True,
      "professionalReferenceRead":False,
      "thresholdSearch":False,
      "roleAssignment":False,
      "activationNpZSha256":sha(a.activations_npz),
      "activationMetaSha256":sha(a.activations_meta),
      "noteEvidenceSha256":sha(a.note_evidence),
      "parameters":{
        "onsetThreshold":ONSET_THRESHOLD,
        "frameThreshold":FRAME_THRESHOLD,
        "minimumNoteLengthMs":MIN_NOTE_MS,
        "frameDurationSeconds":frame_dt,
        "minimumSeparationFrames":min_sep,
        "dedupToleranceSeconds":tol,
      },
      "predictionCounts":{
        "frozenThresholdedInput":len(base),
        "rawActivationProposals":len(candidates),
        "recoveredAdded":recovered,
        "combinedCandidate":len(combined),
      },
      "predictions":{"guitar":combined},
      "interpretationBoundary":"Reference-blind structural recovery using only frozen Basic Pitch defaults; no threshold tuning or role splitting."
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out["predictionCounts"],indent=2))

if __name__=="__main__": main()
