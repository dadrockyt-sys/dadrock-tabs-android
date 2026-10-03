"""Reference-blind real-song guitar/bass pair diagnostic V1.

Uses only already-separated BS-Roformer stem audio plus YAMNet and signal metrics.
No professional tabs, timing map, or note scorer is read.
No audio is changed.

Fixed prospective windows:
- 8.0 s analysis window
- 4.0 s hop

The classifier thresholds are inherited from the frozen synthetic pair classifier
where applicable; this diagnostic reports evidence rather than applying cleanup.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, stft
import tensorflow_hub as hub

TARGET_SR = 16000
WINDOW_SECONDS = 8.0
HOP_SECONDS = 4.0
SILENT_ENERGY_MAX = 1e-9
SUBSTANTIAL_EVIDENCE_MIN = 0.05
SAME_CLASS_MARGIN_MIN = 0.005
PAIR_ENERGY_GAP_MAX_DB = 6.0

GUITAR_LABELS = {
    "Guitar","Electric guitar","Acoustic guitar","Steel guitar, slide guitar",
    "Tapping (guitar technique)","Strum"
}
BASS_LABELS = {"Bass guitar"}

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20), b""):
            h.update(c)
    return h.hexdigest()

def load(path):
    return sf.read(path, always_2d=True, dtype="float32")

def class_names(model):
    p=model.class_map_path().numpy().decode("utf-8")
    with open(p, newline="", encoding="utf-8") as f:
        return [r["display_name"] for r in csv.DictReader(f)]

def mono16(x, fs):
    mono=np.mean(x, axis=1)
    if fs != TARGET_SR:
        g=gcd(fs, TARGET_SR)
        mono=resample_poly(mono, TARGET_SR//g, fs//g).astype(np.float32)
    return mono.astype(np.float32)

def evidence(model, names, x, fs):
    scores,_,_=model(mono16(x,fs))
    arr=scores.numpy()
    idx={n:i for i,n in enumerate(names)}
    gi=[idx[n] for n in GUITAR_LABELS]
    bi=[idx[n] for n in BASS_LABELS]
    return {
        "guitar": float(np.max(np.mean(arr[:,gi], axis=0))),
        "bass": float(np.max(np.mean(arr[:,bi], axis=0))),
    }

def winner(ev):
    if ev["guitar"] > ev["bass"]:
        return "guitar", ev["guitar"]-ev["bass"]
    if ev["bass"] > ev["guitar"]:
        return "bass", ev["bass"]-ev["guitar"]
    return "tie", 0.0

def energy(x):
    return float(np.mean(np.asarray(x,dtype=np.float64)**2))

def zero_lag_corr(a,b):
    a=np.mean(np.asarray(a,dtype=np.float64),axis=1)
    b=np.mean(np.asarray(b,dtype=np.float64),axis=1)
    n=min(len(a),len(b))
    if n < 8: return 0.0
    a=a[:n]-np.mean(a[:n]); b=b[:n]-np.mean(b[:n])
    den=float(np.linalg.norm(a)*np.linalg.norm(b))
    return float(np.dot(a,b)/den) if den>1e-20 else 0.0

def spectral_overlap(a,b,fs):
    def pwr(x):
        chans=[]
        for ch in range(x.shape[1]):
            _,_,z=stft(x[:,ch],fs=fs,nperseg=2048,noverlap=1536,boundary="zeros",padded=True)
            chans.append(np.abs(z).astype(np.float64)**2)
        return np.mean(np.stack(chans,axis=0),axis=0)
    pa=pwr(a); pb=pwr(b)
    shared=float(np.sum(np.minimum(pa,pb)))
    ea=float(np.sum(pa)); eb=float(np.sum(pb))
    return {
        "guitarSharedFraction": shared/(ea+1e-20),
        "bassSharedFraction": shared/(eb+1e-20),
        "symmetricSharedFraction": 0.5*(shared/(ea+1e-20)+shared/(eb+1e-20)),
    }

def classify(gev,bev,ge,be):
    gw,gm=winner(gev); bw,bm=winner(bev)
    gap=abs(10*np.log10((ge+1e-20)/(be+1e-20)))
    if ge <= SILENT_ENERGY_MAX or be <= SILENT_ENERGY_MAX:
        state="missing_or_silent_member"
    elif gw=="guitar" and bw=="bass":
        state="complementary_pair"
    elif gw==bw and gw in {"guitar","bass"}:
        strong=(
            max(gev["guitar"],gev["bass"]) >= SUBSTANTIAL_EVIDENCE_MIN and
            max(bev["guitar"],bev["bass"]) >= SUBSTANTIAL_EVIDENCE_MIN and
            gm >= SAME_CLASS_MARGIN_MIN and bm >= SAME_CLASS_MARGIN_MIN and
            gap <= PAIR_ENERGY_GAP_MAX_DB
        )
        state=f"duplicate_{gw}_candidate" if strong else "ambiguous_pair"
    else:
        state="ambiguous_pair"
    return {
        "state":state,"guitarWinner":gw,"bassWinner":bw,
        "guitarMargin":gm,"bassMargin":bm,"energyGapDb":float(gap)
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--guitar-wav",required=True)
    ap.add_argument("--bass-wav",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--hub-url",default="https://tfhub.dev/google/yamnet/1")
    a=ap.parse_args()

    guitar,fs=load(a.guitar_wav)
    bass,fsb=load(a.bass_wav)
    if fs != fsb: raise RuntimeError("sample-rate mismatch")
    n=min(len(guitar),len(bass)); guitar=guitar[:n]; bass=bass[:n]

    yam=hub.load(a.hub_url); names=class_names(yam)
    w=max(1,int(round(WINDOW_SECONDS*fs))); hop=max(1,int(round(HOP_SECONDS*fs)))

    rows=[]
    starts=list(range(0,max(1,n),hop))
    for start in starts:
        end=min(n,start+w)
        if end-start < int(2.0*fs):
            continue
        g=guitar[start:end]; b=bass[start:end]
        gev=evidence(yam,names,g,fs); bev=evidence(yam,names,b,fs)
        ge=energy(g); be=energy(b)
        cls=classify(gev,bev,ge,be)
        ov=spectral_overlap(g,b,fs)
        rows.append({
            "startSeconds":start/fs,
            "endSeconds":end/fs,
            "guitarEnergy":ge,
            "bassEnergy":be,
            "guitarStemEvidence":gev,
            "bassStemEvidence":bev,
            **cls,
            "zeroLagCorrelation":zero_lag_corr(g,b),
            **ov,
        })

    counts={}
    for r in rows: counts[r["state"]]=counts.get(r["state"],0)+1
    duplicate=[r for r in rows if r["state"].startswith("duplicate_")]
    global_gev=evidence(yam,names,guitar,fs)
    global_bev=evidence(yam,names,bass,fs)

    out={
      "schemaVersion":1,
      "kind":"gomyway-real-guitar-bass-pair-diagnostic-v1",
      "referenceBlind":True,
      "professionalReferenceRead":False,
      "audioModified":False,
      "guitarStemSha256":sha(a.guitar_wav),
      "bassStemSha256":sha(a.bass_wav),
      "sampleRate":fs,
      "durationSeconds":n/fs,
      "windowSeconds":WINDOW_SECONDS,
      "hopSeconds":HOP_SECONDS,
      "classifierThresholds":{
        "silentEnergyMax":SILENT_ENERGY_MAX,
        "substantialEvidenceMin":SUBSTANTIAL_EVIDENCE_MIN,
        "sameClassMarginMin":SAME_CLASS_MARGIN_MIN,
        "pairEnergyGapMaxDb":PAIR_ENERGY_GAP_MAX_DB,
      },
      "global":{
        "guitarStemEvidence":global_gev,
        "bassStemEvidence":global_bev,
        "guitarEnergy":energy(guitar),
        "bassEnergy":energy(bass),
        "zeroLagCorrelation":zero_lag_corr(guitar,bass),
        **spectral_overlap(guitar,bass,fs),
      },
      "windowCount":len(rows),
      "stateCounts":counts,
      "duplicateCandidateWindowCount":len(duplicate),
      "windows":rows,
      "interpretationBoundary":"Diagnostic only; no suppression, reassignment, threshold search, or professional-reference scoring."
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"windowCount":len(rows),"stateCounts":counts,"global":out["global"]},indent=2))

if __name__=="__main__": main()
