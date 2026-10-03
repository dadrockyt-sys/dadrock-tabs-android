"""Reference-blind Basic Pitch activation recovery V2 with contour corroboration.

V1 proved that broad onset+frame admission recovers true notes but collapses
precision. V2 keeps the same frozen onset/frame thresholds and adds a structural,
reference-blind requirement from Basic Pitch's own 3-bins-per-semitone contour
output.

No professional references are read. No threshold search is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

MIDI_OFFSET = 21
ONSET_THRESHOLD = 0.5
FRAME_THRESHOLD = 0.3
MIN_NOTE_MS = 127.70
CONTOUR_BINS_PER_SEMITONE = 3
ANNOTATIONS_BASE_FREQUENCY_HZ = 27.5

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20), b""):
            h.update(c)
    return h.hexdigest()

def onset_local_max(a, i):
    lo=max(0,i-1); hi=min(len(a),i+2)
    return a[i] >= np.max(a[lo:hi])

def contour_group_score(contour_row, pitch_index):
    lo=pitch_index*CONTOUR_BINS_PER_SEMITONE
    hi=lo+CONTOUR_BINS_PER_SEMITONE
    return float(np.max(contour_row[lo:hi]))

def contour_corroborated(contour_row, pitch_index):
    own=contour_group_score(contour_row,pitch_index)
    neighbors=[]
    if pitch_index>0:
        neighbors.append(contour_group_score(contour_row,pitch_index-1))
    if pitch_index<87:
        neighbors.append(contour_group_score(contour_row,pitch_index+1))
    return own >= max(neighbors) if neighbors else True

def dedup(existing, proposed, tol):
    out=[dict(p) for p in existing]
    for q in proposed:
        dup=False
        for p in out:
            if int(p["midi"])==int(q["midi"]) and abs(float(p["start"])-float(q["start"]))<=tol:
                dup=True
                break
        if not dup:
            out.append(q)
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
    contour=np.asarray(z["contour"],dtype=float)
    if note.shape!=onset.shape or note.ndim!=2 or note.shape[1]!=88:
        raise RuntimeError(f"unexpected note/onset shapes: {note.shape}, {onset.shape}")
    if contour.ndim!=2 or contour.shape[0]!=note.shape[0] or contour.shape[1]!=264:
        raise RuntimeError(f"unexpected contour shape: {contour.shape}")

    duration=float(meta["audioDurationSeconds"])
    frame_dt=duration/max(1,note.shape[0]-1)
    min_sep=max(1,int(round((MIN_NOTE_MS/1000.0)/frame_dt)))
    dedup_tol=(MIN_NOTE_MS/1000.0)/2.0

    raw=0
    contour_ok=0
    proposals=[]
    for pitch in range(88):
        last=-10**9
        for i in range(note.shape[0]):
            if onset[i,pitch] < ONSET_THRESHOLD or note[i,pitch] < FRAME_THRESHOLD:
                continue
            if not onset_local_max(onset[:,pitch],i):
                continue
            raw += 1
            if not contour_corroborated(contour[i],pitch):
                continue
            contour_ok += 1
            if i-last < min_sep:
                continue
            proposals.append({
                "midi":int(pitch+MIDI_OFFSET),
                "start":float(i*frame_dt),
                "source":"rawActivationContourRecoveryV2",
                "onsetActivation":float(onset[i,pitch]),
                "frameActivation":float(note[i,pitch]),
                "contourActivation":contour_group_score(contour[i],pitch),
            })
            last=i

    combined=dedup(base,proposals,dedup_tol)
    out={
      "schemaVersion":1,
      "kind":"gomyway-reference-blind-basic-pitch-activation-recovery-v2",
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
        "contourBinsPerSemitone":CONTOUR_BINS_PER_SEMITONE,
        "annotationsBaseFrequencyHz":ANNOTATIONS_BASE_FREQUENCY_HZ,
        "contourRule":"candidate semitone contour max must be >= adjacent semitone contour maxima at the same frame",
        "frameDurationSeconds":frame_dt,
        "minimumSeparationFrames":min_sep,
        "dedupToleranceSeconds":dedup_tol,
      },
      "predictionCounts":{
        "frozenThresholdedInput":len(base),
        "rawOnsetFramePeaks":raw,
        "contourCorroboratedPeaks":contour_ok,
        "recoveryProposalsAfterSeparation":len(proposals),
        "recoveredAdded":len(combined)-len(base),
        "combinedCandidate":len(combined),
      },
      "predictions":{"guitar":combined},
      "interpretationBoundary":"Reference-blind contour-corroborated recovery only; frozen Basic Pitch thresholds unchanged."
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out["predictionCounts"],indent=2))

if __name__=="__main__":
    main()
