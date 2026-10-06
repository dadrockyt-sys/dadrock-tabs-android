#!/usr/bin/env python3
"""Freeze Basic Pitch baseline candidates on sealed GuitarSet players 00/01/03.

Audio-only candidate generation. No JAMS/reference path is accepted.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

EVAL_PLAYERS=("00","01","03")
DEV_PLAYERS=("02","04","05")
EXPECTED_TRACKS=180
EXPECTED_MODEL_SHA256="3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"
BASIC_PITCH_CONFIG={
  "version":"0.4.0","onsetThreshold":0.5,"frameThreshold":0.3,
  "minimumNoteLengthMs":127.70,"minimumFrequency":None,"maximumFrequency":None,
  "multiplePitchBends":False,"melodiaTrick":True,"midiTempo":120.0,
}

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def stem_from_audio(path:Path)->str:
    if not path.name.endswith("_mic.wav"): raise RuntimeError(f"unexpected audio filename {path.name}")
    return path.name[:-8]

def normalize(note_events:list[tuple[Any,...]])->list[dict[str,Any]]:
    out=[]
    for row in note_events:
        start,end,pitch,amp=row[:4]
        out.append({"start":float(start),"end":float(end),"pitch":int(pitch),"amplitude":float(amp)})
    out.sort(key=lambda x:(x["start"],x["end"],x["pitch"],x["amplitude"]))
    for i,row in enumerate(out): row["eventId"]=i
    return out

def discover(root:Path):
    rows=[]
    for p in sorted(root.glob("*.wav")):
        stem=stem_from_audio(p); player=stem[:2]
        if player in DEV_PLAYERS: raise RuntimeError(f"development audio present in sealed workspace: {p.name}")
        if player not in EVAL_PLAYERS: raise RuntimeError(f"unexpected player: {p.name}")
        rows.append((player,stem,p))
    if len(rows)!=EXPECTED_TRACKS: raise RuntimeError(f"expected {EXPECTED_TRACKS} tracks, got {len(rows)}")
    counts={x:sum(r[0]==x for r in rows) for x in EVAL_PLAYERS}
    if counts!={"00":60,"01":60,"03":60}: raise RuntimeError(f"player counts mismatch {counts}")
    if len({r[1] for r in rows})!=EXPECTED_TRACKS: raise RuntimeError("duplicate track stems")
    return rows

def self_test():
    fake=[(0.2,0.5,64,0.7,None),(0.1,0.3,60,0.5,None)]
    n=normalize(fake)
    assert [x["pitch"] for x in n]==[60,64]
    assert [x["eventId"] for x in n]==[0,1]
    return {"status":"GUITARSET_MISSING_EVENT_BASELINE_V1_SELF_TEST_PASS","referenceRead":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audio-root",type=Path)
    ap.add_argument("--output-dir",type=Path)
    ap.add_argument("--self-test",action="store_true")
    a=ap.parse_args()
    if a.self_test:
        print(json.dumps(self_test(),sort_keys=True)); return 0
    if a.audio_root is None or a.output_dir is None: raise SystemExit("--audio-root and --output-dir required")
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import Model,predict
    model_path=Path(ICASSP_2022_MODEL_PATH)
    model_sha=sha256_file(model_path)
    if model_sha!=EXPECTED_MODEL_SHA256: raise RuntimeError(f"Basic Pitch model SHA mismatch {model_sha}")
    model=Model(model_path)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    receipts=[]; total=0
    for player,stem,audio_path in discover(a.audio_root):
        _,_,events=predict(
            audio_path,model_or_model_path=model,
            onset_threshold=0.5,frame_threshold=0.3,minimum_note_length=127.70,
            minimum_frequency=None,maximum_frequency=None,multiple_pitch_bends=False,
            melodia_trick=True,midi_tempo=120.0,
        )
        baseline=normalize(events)
        payload={
          "schema":"astra-guitarset-missing-event-baseline-v1",
          "dataset":"GuitarSet","datasetVersion":"1.1.0",
          "player":player,"trackStem":stem,
          "sourceAudioFile":audio_path.name,"sourceAudioSha256":sha256_file(audio_path),
          "basicPitch":{**BASIC_PITCH_CONFIG,"modelSha256":model_sha},
          "events":baseline,"eventCount":len(baseline),
          "referenceRead":False,"jamsNoteEventsRead":0,
          "predictionMutation":False,"thresholdSearch":False,
        }
        out=a.output_dir/f"{stem}.json"
        out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        rec={"file":out.name,"sha256":sha256_file(out),"player":player,"trackStem":stem,"eventCount":len(baseline)}
        receipts.append(rec); total+=len(baseline)
        print(json.dumps({"frozen":rec},sort_keys=True),flush=True)
    manifest={
      "schema":"astra-guitarset-missing-event-baseline-v1-freeze-manifest",
      "players":list(EVAL_PLAYERS),"formerSealedHoldoutConsumedByThisDiagnostic":True,
      "candidateFileCount":len(receipts),"totalEventCount":total,
      "basicPitch":{**BASIC_PITCH_CONFIG,"modelSha256":model_sha},
      "files":sorted(receipts,key=lambda x:(x["player"],x["trackStem"])),
      "referenceRead":False,"jamsNoteEventsRead":0,
      "predictionMutation":False,"thresholdSearch":False,
    }
    mp=a.output_dir/"candidate-freeze-manifest.json"
    mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"GUITARSET_MISSING_EVENT_BASELINE_V1_FROZEN","manifestSha256":sha256_file(mp),"candidateFileCount":len(receipts),"totalEventCount":total},indent=2,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
