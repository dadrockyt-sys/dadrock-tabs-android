#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path

import numpy as np
import torch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
sys.path.insert(0,str(HERE.parent/"tabcnn_runtime"))

from guitartechs_real_training.real_training import decode_audio, state_sha256
from tabcnn_runtime.preprocessing import extract_cqt_features, rms_normalize, SAMPLE_RATE_HZ, HOP_LENGTH_SAMPLES
from guitartechs_training_v7.model import NUM_CLASSES, NUM_STRINGS, OPEN_MIDI, TemporalTabCNNV7
from guitartechs_training_v8.decoder import decode_v8_hybrid

CANDIDATE_ID="astra_guitartechs_v8_v4_hysteresis_event_rank_backshift"
MODEL_ID="astra_guitartechs_tabcnn_v7_ranked_event_transition"
STRING_NAMES=("E","A","D","G","B","e")

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def load_model(path, expected_sha, expected_fold, source_root):
    if sha256_file(path)!=expected_sha:
        raise RuntimeError("frozen model file SHA mismatch")
    payload=torch.load(path,map_location="cpu")
    if payload.get("candidateId")!=MODEL_ID or payload.get("fold")!=expected_fold:
        raise RuntimeError("frozen model identity mismatch")
    model=TemporalTabCNNV7(source_root)
    model.load_state_dict(payload["stateDict"])
    if state_sha256(model)!=payload.get("stateSha256"):
        raise RuntimeError("frozen model state SHA mismatch")
    return model,payload

def infer(model,feat,chunk=512):
    half=4;context=9
    pad=np.pad(feat,((0,0),(half,half)))
    windows=np.lib.stride_tricks.sliding_window_view(pad,context,axis=1).transpose(1,0,2)
    T=feat.shape[1]
    state=np.empty((T,NUM_STRINGS,NUM_CLASSES),np.float32)
    event=np.empty((T,NUM_STRINGS),np.float32)
    hidden=None
    model.eval()
    with torch.no_grad():
        for lo in range(0,T,chunk):
            hi=min(T,lo+chunk)
            x=np.ascontiguousarray(windows[lo:hi])[None,:,None,:,:]
            out=model(torch.from_numpy(x),hidden)
            hidden=out["hidden"].detach()
            state[lo:hi]=torch.softmax(
                out["tablature"].reshape(1,hi-lo,NUM_STRINGS,NUM_CLASSES),dim=-1
            )[0].cpu().numpy().astype(np.float32)
            event[lo:hi]=out["event"][0].cpu().numpy().astype(np.float32)
    return state,event

def runs(states):
    T,S=states.shape
    for s in range(S):
        i=0
        while i<T:
            fret=int(states[i,s]);j=i+1
            while j<T and int(states[j,s])==fret:j+=1
            if fret>=0:
                yield s,i,j,fret
            i=j

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--guitar-wav",required=True)
    ap.add_argument("--model",required=True)
    ap.add_argument("--expected-model-sha",required=True)
    ap.add_argument("--fold",required=True)
    ap.add_argument("--source-root",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()

    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(4)
    wav=decode_audio(a.guitar_wav)
    feat=extract_cqt_features(rms_normalize(wav)).squeeze(0).astype(np.float32,copy=False)
    model,payload=load_model(a.model,a.expected_model_sha,a.fold,a.source_root)
    state,event=infer(model,feat)
    decoded=decode_v8_hybrid(state,event)

    frame_seconds=HOP_LENGTH_SAMPLES/SAMPLE_RATE_HZ
    events=[]
    for s,i,j,fret in runs(decoded):
        events.append({
            "stringIndex":s,
            "string":STRING_NAMES[s],
            "fret":fret,
            "midi":int(OPEN_MIDI[s]+fret),
            "start":float(i*frame_seconds),
            "end":float(j*frame_seconds),
            "duration":float((j-i)*frame_seconds),
            "startFrame":i,
            "endFrameExclusive":j
        })
    events.sort(key=lambda x:(x["start"],x["midi"],x["stringIndex"]))

    out={
      "schema":"astra-gomyway-v8-frozen-candidate-v1",
      "candidateId":CANDIDATE_ID,
      "fold":a.fold,
      "input":{
        "label":"bs-roformer-guitar-stem",
        "wavSha256":sha256_file(a.guitar_wav),
        "sampleRateHz":SAMPLE_RATE_HZ,
        "hopLengthSamples":HOP_LENGTH_SAMPLES,
        "featureFrames":int(feat.shape[1])
      },
      "model":{
        "fileSha256":a.expected_model_sha,
        "stateSha256":payload["stateSha256"],
        "selectedEpoch":int(payload["epoch"])
      },
      "decoder":{
        "kind":"V8 frozen V4 hysteresis plus event-rank backshift",
        "referenceBlind":True,
        "thresholdRetuned":False
      },
      "events":events,
      "eventCount":len(events),
      "guards":{
        "professionalReferenceRead":False,
        "timingMapRead":False,
        "optimizerStepsExecuted":0,
        "modelWeightsModified":False
      }
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"fold":a.fold,"eventCount":len(events),"output":a.output_json},sort_keys=True))

if __name__=="__main__":
    main()
