"""Freeze note events from the pinned HCQT+Mel guitar-specific AMT model.

Runs on an audio file and emits frame-transition note onsets from per-string tablature.
No professional reference is read.
"""
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import sys
import numpy as np

from v143_specialized_guitar_amt_probe import (
    load_audio, extract_features, load_model, infer, probabilities,
    TUNING_LOW_TO_HIGH, SILENCE_CLASS, SR, HOP, sha256
)

def events_from_frames(classes, confidence, activity, times):
    events=[]
    prev=[SILENCE_CLASS]*6
    for frame in range(classes.shape[0]):
        for s in range(6):
            fret=int(classes[frame,s])
            if fret!=SILENCE_CLASS and fret!=prev[s]:
                midi=int(TUNING_LOW_TO_HIGH[s]+fret)
                events.append({
                    "id":f"s{s}:f{frame}:m{midi}",
                    "start":float(times[frame]),
                    "midi":midi,
                    "stringLowToHigh":s,
                    "fret":fret,
                    "classProbability":float(confidence[frame,s]),
                    "stringActivityProbability":float(activity[frame,s]),
                })
            prev[s]=fret
    return events

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audio",required=True,type=Path)
    ap.add_argument("--upstream-code",required=True,type=Path)
    ap.add_argument("--config",required=True,type=Path)
    ap.add_argument("--checkpoint",required=True,type=Path)
    ap.add_argument("--device",default="cpu")
    ap.add_argument("--output-json",required=True,type=Path)
    ap.add_argument("--label",required=True)
    a=ap.parse_args()

    audio=load_audio(a.audio)
    hcqt,mel,times=extract_features(audio)
    model=load_model(a.upstream_code,a.config,a.checkpoint,a.device)
    raw=infer(model,hcqt,mel,a.device)
    classes,conf,mp,activity,hp=probabilities(raw)
    events=events_from_frames(classes,conf,activity,times)

    out={
      "schemaVersion":1,
      "kind":"gomyway-specialized-guitar-amt-frozen-events-v1",
      "referenceBlind":True,
      "professionalReferenceRead":False,
      "input":{"label":a.label,"path":str(a.audio),"sha256":sha256(a.audio)},
      "model":{"configSha256":sha256(a.config),"checkpointSha256":sha256(a.checkpoint)},
      "featureContract":{"sampleRate":SR,"hopLength":HOP,"frameCount":len(times)},
      "predictionCount":len(events),
      "events":events,
      "interpretationBoundary":"Generic guitar note events from frozen per-string frame transitions; no rhythm/lead role assignment."
    }
    a.output_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"label":a.label,"predictionCount":len(events),
                      "inputSha256":out["input"]["sha256"],
                      "checkpointSha256":out["model"]["checkpointSha256"]},indent=2))

if __name__=="__main__":main()
