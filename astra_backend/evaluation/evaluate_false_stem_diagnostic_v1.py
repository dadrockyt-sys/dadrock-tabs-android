"""False-stem diagnostic V1 for frozen S0 mixtures.

Purpose:
- detect cases where BS-Roformer emits a substantial guitar/bass stem even though
  the target is absent;
- compare YAMNet evidence on the claimed stem vs the strongest competing stem;
- evaluate hypothetical reassignment non-destructively;
- do not alter production audio or tune thresholds after observing results.
"""
from __future__ import annotations
import argparse, csv, json
from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import tensorflow_hub as hub

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from stem_bleed_diagnostics_v1 import DiagnosticConfig, diagnose_stems

TARGET_SR=16000
GUITAR_LABELS={"Guitar","Electric guitar","Acoustic guitar","Steel guitar, slide guitar","Tapping (guitar technique)","Strum"}
BASS_LABELS={"Bass guitar"}

def load(path):
    return sf.read(path,always_2d=True,dtype="float32")

def truth_presence(directory):
    present=set()
    for p in directory.glob("*.wav"):
        if p.name.endswith("_mix.wav"):
            continue
        present.add(p.stem.split("_",1)[1])
    return present

def class_names(model):
    p=model.class_map_path().numpy().decode("utf-8")
    with open(p,newline="",encoding="utf-8") as f:
        return [r["display_name"] for r in csv.DictReader(f)]

def mono16(x,fs):
    mono=np.mean(x,axis=1)
    if fs!=TARGET_SR:
        g=gcd(fs,TARGET_SR)
        mono=resample_poly(mono,TARGET_SR//g,fs//g).astype(np.float32)
    return mono.astype(np.float32)

def evidence(model,names,x,fs):
    scores,_,_=model(mono16(x,fs))
    arr=scores.numpy()
    idx={n:i for i,n in enumerate(names)}
    gi=[idx[n] for n in GUITAR_LABELS]
    bi=[idx[n] for n in BASS_LABELS]
    return {
        "guitar":float(np.max(np.mean(arr[:,gi],axis=0))),
        "bass":float(np.max(np.mean(arr[:,bi],axis=0))),
    }

def energy(x):
    return float(np.mean(np.asarray(x,dtype=np.float64)**2))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--s0-root",required=True)
    ap.add_argument("--model",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--hub-url",default="https://tfhub.dev/google/yamnet/1")
    args=ap.parse_args()

    sep=BsRoformer6StemOnnxAdapter(Path(args.model))
    yam=hub.load(args.hub_url)
    names=class_names(yam)
    diag_cfg=DiagnosticConfig()
    rows=[]

    for directory in sorted(Path(args.s0_root).glob("S0M*")):
        mix_files=list(directory.glob("*_mix.wav"))
        if len(mix_files)!=1:
            continue
        mix,fs=load(mix_files[0])
        raw=sep.separate_array(mix,fs)
        diagnostics=diagnose_stems(mix,raw,fs,diag_cfg)
        present=truth_presence(directory)
        stem_evidence={name:evidence(yam,names,wav,fs) for name,wav in raw.items()}
        stem_energy={name:energy(wav) for name,wav in raw.items()}

        for claimed in ("guitar","bass"):
            absent=claimed not in present
            other_claim="bass" if claimed=="guitar" else "guitar"
            strongest=max(
                (k for k in raw if k!=claimed),
                key=lambda k: diagnostics[claimed]["perCompetitor"][k]["overlapPressure"]
            )
            claimed_ev=stem_evidence[claimed]
            strongest_ev=stem_evidence[strongest]
            row={
                "mixture":directory.name,
                "claimedStem":claimed,
                "targetActuallyAbsent":absent,
                "claimedStemEnergy":stem_energy[claimed],
                "claimedEvidence":claimed_ev,
                "stringWinner":"guitar" if claimed_ev["guitar"]>=claimed_ev["bass"] else "bass",
                "stringMargin":abs(claimed_ev["guitar"]-claimed_ev["bass"]),
                "interferencePressure":diagnostics[claimed]["interferencePressure"],
                "competitorDominanceFraction":diagnostics[claimed]["competitorDominanceFraction"],
                "strongestOverlapCompetitor":strongest,
                "strongestCompetitorEvidence":strongest_ev,
                "strongestCompetitorEnergy":stem_energy[strongest],
                "claimedVsCompetitorEnergyDb":float(
                    10*np.log10((stem_energy[claimed]+1e-20)/(stem_energy[strongest]+1e-20))
                ),
                "hypotheticalReassignment": {
                    "destination":strongest,
                    "sourceEnergyMoved":stem_energy[claimed],
                    "wouldPreserveMixtureEnergyExactly":True
                }
            }
            rows.append(row)

    absent=[r for r in rows if r["targetActuallyAbsent"]]
    result={
        "schemaVersion":1,
        "kind":"s0-false-stem-diagnostic-v1",
        "modelSha256":FP16_SHA256,
        "mixtureCount":len(set(r["mixture"] for r in rows)),
        "claimCount":len(rows),
        "absentClaimCount":len(absent),
        "results":rows,
        "interpretationBoundary":"Diagnostic only. No reassignment or suppression is applied."
    }
    Path(args.output_json).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
