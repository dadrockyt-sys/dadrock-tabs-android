"""Evaluate recognizer-gated cleanup on frozen S0 mixtures."""
from __future__ import annotations
import argparse, csv, json
from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import tensorflow_hub as hub

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from stem_bleed_cleanup_v1 import CleanupConfig, si_sdr, suppress_cross_stem_bleed
from stem_bleed_diagnostics_v1 import DiagnosticConfig, diagnose_stems
from recognizer_gate_v1 import RecognizerGateConfig, decide

TARGET_SR=16000
GUITAR_LABELS={"Guitar","Electric guitar","Acoustic guitar","Steel guitar, slide guitar","Tapping (guitar technique)","Strum"}
BASS_LABELS={"Bass guitar"}

def load(path):
    return sf.read(path,always_2d=True,dtype="float32")

def truth_stems(directory):
    out={}
    for p in sorted(directory.glob("*.wav")):
        if p.name.endswith("_mix.wav"):
            continue
        out[p.stem.split("_",1)[1]]=load(p)
    return out

def collapse_truth(truth,target,length):
    exact=[v[0][:length] for k,v in truth.items() if k==target]
    if exact:
        return np.sum(np.stack(exact),axis=0).astype(np.float32)
    sample=next(iter(truth.values()))[0]
    return np.zeros_like(sample[:length],dtype=np.float32)

def yamnet_names(model):
    path=model.class_map_path().numpy().decode("utf-8")
    with open(path,newline="",encoding="utf-8") as f:
        return [row["display_name"] for row in csv.DictReader(f)]

def mono16(x,fs):
    mono=np.mean(x,axis=1)
    if fs!=TARGET_SR:
        g=gcd(fs,TARGET_SR)
        mono=resample_poly(mono,TARGET_SR//g,fs//g).astype(np.float32)
    return mono.astype(np.float32)

def score(model,names,x,fs):
    scores,_,_=model(mono16(x,fs))
    arr=scores.numpy()
    idx={n:i for i,n in enumerate(names)}
    gi=[idx[n] for n in GUITAR_LABELS]
    bi=[idx[n] for n in BASS_LABELS]
    return float(np.max(np.mean(arr[:,gi],axis=0))), float(np.max(np.mean(arr[:,bi],axis=0)))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--s0-root",required=True)
    ap.add_argument("--model",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--hub-url",default="https://tfhub.dev/google/yamnet/1")
    args=ap.parse_args()

    sep=BsRoformer6StemOnnxAdapter(Path(args.model))
    yam=hub.load(args.hub_url)
    names=yamnet_names(yam)
    gate_cfg=RecognizerGateConfig()
    cleanup_cfg=CleanupConfig(floor_gain=gate_cfg.cleanup_floor_gain,competition=gate_cfg.cleanup_competition)
    diag_cfg=DiagnosticConfig()
    rows=[]

    for directory in sorted(Path(args.s0_root).glob("S0M*")):
        mixes=list(directory.glob("*_mix.wav"))
        if len(mixes)!=1:
            continue
        mix,fs=load(mixes[0])
        truth=truth_stems(directory)
        raw=sep.separate_array(mix,fs)
        diagnostics=diagnose_stems(mix,raw,fs,diag_cfg)
        cleaned,_=suppress_cross_stem_bleed(raw,fs,cleanup_cfg)
        gated=dict(raw)
        decisions={}

        for target in ("guitar","bass"):
            gs,bs=score(yam,names,raw[target],fs)
            decision=decide(target,gs,bs,diagnostics[target],gate_cfg)
            decisions[target]={"guitarEvidence":gs,"bassEvidence":bs,**decision}
            if decision["applyCleanup"]:
                gated[target]=cleaned[target]

        row={"id":directory.name,"decisions":decisions,"stems":{}}
        length=len(mix)
        for target in ("guitar","bass"):
            ref=collapse_truth(truth,target,length)
            present=float(np.sum(ref.astype(np.float64)**2)) >= 1e-12
            if present:
                raw_score=si_sdr(ref,raw[target])
                gated_score=si_sdr(ref,gated[target])
                row["stems"][target]={"targetPresent":True,"rawSiSdrDb":raw_score,"gatedSiSdrDb":gated_score,"improvementDb":gated_score-raw_score}
            else:
                row["stems"][target]={"targetPresent":False,"rawEnergy":float(np.mean(raw[target]**2)),"gatedEnergy":float(np.mean(gated[target]**2))}
        rows.append(row)

    improvements=[]
    applied=0
    for row in rows:
        for target in ("guitar","bass"):
            if row["decisions"][target]["applyCleanup"]:
                applied+=1
            if row["stems"][target].get("targetPresent"):
                improvements.append(row["stems"][target]["improvementDb"])

    result={
        "schemaVersion":1,
        "kind":"s0-recognizer-gated-cleanup-v1",
        "modelSha256":FP16_SHA256,
        "gateConfig":gate_cfg.to_dict(),
        "cleanupConfig":cleanup_cfg.to_dict(),
        "mixtureCount":len(rows),
        "cleanupAppliedCount":applied,
        "meanTargetImprovementDb":float(np.mean(improvements)),
        "minimumTargetImprovementDb":float(np.min(improvements)),
        "maximumTargetImprovementDb":float(np.max(improvements)),
        "results":rows,
        "interpretationBoundary":"S0 synthetic mixtures only."
    }
    Path(args.output_json).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
