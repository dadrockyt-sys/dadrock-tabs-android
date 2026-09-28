#!/usr/bin/env python3
"""Bounded synthetic-only Astra S0 diversity pilot.

No corpus media, P1/P2/P3, pretrained weights, threshold search, external audio
assets, or production mutation. Generates repo-owned procedural plucked-string
audio, extracts the frozen CQT, and compares exactly two fixed models.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time

import numpy as np
from scipy.signal import lfilter, resample_poly
import torch
from torch import nn
import torch.nn.functional as F

from tabcnn_runtime.preprocessing import (
    SAMPLE_RATE_HZ, HOP_LENGTH_SAMPLES, CQT_BINS, extract_cqt_features, rms_normalize,
)
from evaluation.event_decoder_v2 import (
    NUM_STRINGS, NUM_FRETS, NUM_CLASSES, SILENCE_CLASS,
    STATE_ACTIVE_THRESHOLD, ONSET_THRESHOLD, decode_event_list_v2,
)
from evaluation.evaluation_protocol_v2 import EvalPitchEvent, score_pitch_events_v2

SCHEMA="astra-synthetic-data-diversity-s0-pilot-v1"
ROOT_SEED=20260927
INTERNAL_SR=44100
OUTPUT_SR=22050
CLIP_SECONDS=2.0
BASES_PER_FAMILY=14
VARIANTS_PER_BASE=3
FAMILIES=("isolated","scales","chords","repeated","legato","palmmute","mixed")
EXAMPLES=BASES_PER_FAMILY*VARIANTS_PER_BASE*len(FAMILIES)
AUDIO_SECONDS=EXAMPLES*CLIP_SECONDS
MAX_EXAMPLES=3000
MAX_AUDIO_SECONDS=6000.0
MAX_DATASET_BYTES=350*1024*1024
MAX_RENDER_SECONDS=1200.0
MAX_STEPS=500
MAX_MODELS=2
MAX_FIT_EVAL_SECONDS=3600.0
BATCH_SIZE=128
LEARNING_RATE=0.003
STATE_ACTIVE_WEIGHT=1.5
ONSET_POS_WEIGHT=8.0
ONSET_LOSS_WEIGHT=4.0
OPEN_MIDI=(40,45,50,55,59,64)

if EXAMPLES > MAX_EXAMPLES or AUDIO_SECONDS > MAX_AUDIO_SECONDS:
    raise RuntimeError("frozen S0 dataset exceeds design ceiling")


def _sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def _seed(*parts):
    raw="|".join(str(x) for x in parts).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8],"big") & 0x7fffffff


def split_for_base(base_index):
    if not 0 <= int(base_index) < BASES_PER_FAMILY:
        raise ValueError("base index out of range")
    if base_index < 10: return "train"
    if base_index < 12: return "validation"
    return "test"


def _event(string,fret,start,end,*,attack=True,palm=False,soft=False):
    return {
        "string":int(string),"fret":int(fret),"start":float(start),"end":float(end),
        "attack":bool(attack),"palm":bool(palm),"soft":bool(soft),
    }


def build_template(family, base_index):
    if family not in FAMILIES: raise ValueError("unknown family")
    rng=np.random.RandomState(_seed(ROOT_SEED,"template",family,base_index))
    rows=[]
    negative_only=False
    has_negative_structure=family in ("legato","palmmute","mixed")
    if family=="isolated":
        s=int(rng.randint(0,6)); fret=int(rng.randint(0,16))
        rows=[_event(s,fret,.32,1.35)]
    elif family=="scales":
        base=int(rng.randint(0,9))
        for j in range(4):
            s=(j+int(rng.randint(0,2)))%6
            fret=min(18,base+j)
            st=.22+j*.36
            rows.append(_event(s,fret,st,st+.27))
    elif family=="chords":
        strings=sorted(rng.choice(np.arange(6),size=3,replace=False).tolist())
        for st in (.32,1.08):
            for s in strings:
                rows.append(_event(s,int(rng.randint(0,10)),st,st+.48))
    elif family=="repeated":
        s=int(rng.randint(0,6)); fret=int(rng.randint(0,15))
        for st in (.28,.68,1.08,1.48):
            rows.append(_event(s,fret,st,min(1.88,st+.31)))
    elif family=="legato":
        s=int(rng.randint(0,6)); a=int(rng.randint(1,10)); b=min(18,a+int(rng.randint(1,4)))
        rows=[_event(s,a,.28,.78),_event(s,b,.78,1.52,attack=False,soft=True)]
    elif family=="palmmute":
        s=int(rng.randint(0,6)); fret=int(rng.randint(0,12))
        for st in (.28,.62,.96,1.30,1.64):
            rows.append(_event(s,fret,st,min(1.90,st+.16),palm=True))
    elif family=="mixed":
        negative_only=(base_index % 2)==0
        if not negative_only:
            s=int(rng.randint(0,6)); fret=int(rng.randint(0,14))
            rows=[_event(s,fret,.36,1.22)]
    return {
        "family":family,"baseIndex":int(base_index),
        "templateId":f"{family}:{base_index:02d}",
        "split":split_for_base(base_index),
        "segments":rows,"negativeOnly":negative_only,
        "hasNegativeStructure":has_negative_structure,
    }


def _plucked_component(freq,duration,sr,rng,*,damping,pick_position,brightness,transient,soft):
    n=max(1,int(round(duration*sr)))
    t=np.arange(n,dtype=np.float64)/sr
    wave=np.zeros(n,dtype=np.float64)
    phase0=rng.uniform(0,2*np.pi)
    for h in range(1,7):
        pick=max(.08,abs(math.sin(math.pi*h*pick_position)))
        amp=(brightness**(h-1))*pick/(h**1.15)
        decay=np.exp(-(damping*(.78+.20*h))*t)
        wave += amp*np.sin(2*np.pi*freq*h*t+phase0/h)*decay
    tau=.045 if soft else .0025
    envelope=(1-np.exp(-t/max(tau,1e-5)))
    wave*=envelope
    if transient and not soft:
        burst=rng.normal(0,1,n)*np.exp(-t/.008)
        wave += .16*burst
    return wave


def render_waveform(template, variant):
    trng=np.random.RandomState(_seed(ROOT_SEED,"timbre",template["templateId"],variant))
    n=int(round(CLIP_SECONDS*INTERNAL_SR))
    audio=np.zeros(n,dtype=np.float64)
    damping=float(trng.uniform(.75,1.75))
    pick=float(trng.uniform(.12,.42))
    brightness=float(trng.uniform(.66,.88))
    body_a=float(trng.uniform(.82,.94))
    for row in template["segments"]:
        start=int(round(row["start"]*INTERNAL_SR))
        end=int(round(row["end"]*INTERNAL_SR))
        if end<=start or start>=n: continue
        end=min(n,end)
        pitch=OPEN_MIDI[row["string"]]+row["fret"]
        freq=440.0*(2.0**((pitch-69)/12.0))
        d=damping*(4.5 if row["palm"] else 1.0)*(1.0+.04*row["string"])
        comp=_plucked_component(
            freq,(end-start)/INTERNAL_SR,INTERNAL_SR,trng,
            damping=d,pick_position=pick,brightness=brightness,
            transient=row["attack"],soft=row["soft"],
        )
        audio[start:end]+=comp[:end-start]
    if template["hasNegativeStructure"]:
        center=int(round((1.70+.03*(variant-1))*INTERNAL_SR))
        width=max(8,int(.018*INTERNAL_SR))
        lo=max(0,center-width//2); hi=min(n,lo+width)
        burst=trng.normal(0,1,hi-lo)*np.hanning(hi-lo)
        audio[lo:hi]+=0.12*burst
        audio += trng.normal(0,1,n)*float(trng.uniform(.0005,.0020))
    else:
        audio += trng.normal(0,1,n)*0.00025
    audio=lfilter([1.0-body_a],[1.0,-body_a],audio)
    peak=float(np.max(np.abs(audio)))
    if peak>0: audio=.78*audio/peak
    out=resample_poly(audio,1,2).astype(np.float32)
    want=int(round(CLIP_SECONDS*OUTPUT_SR))
    if len(out)<want: out=np.pad(out,(0,want-len(out)))
    elif len(out)>want: out=out[:want]
    if not np.isfinite(out).all(): raise RuntimeError("nonfinite rendered audio")
    return out


def targets_for_template(template,frames):
    state=np.full((NUM_STRINGS,frames),-1,dtype=np.int16)
    onset=np.zeros((NUM_STRINGS,frames),dtype=np.int16)
    refs=[]
    hop=HOP_LENGTH_SAMPLES/SAMPLE_RATE_HZ
    for i,row in enumerate(template["segments"]):
        s=row["string"]; fret=row["fret"]
        lo=max(0,min(frames-1,int(round(row["start"]/hop))))
        hi=max(lo+1,min(frames,int(round(row["end"]/hop))))
        state[s,lo:hi]=fret
        if row["attack"]:
            onset[s,lo]=1
            pitch=OPEN_MIDI[s]+fret
            refs.append({
                "id":f"{template['templateId']}:{i}",
                "pitch":pitch,"start":lo*hop,"end":hi*hop,
                "string":s,"fret":fret,
            })
    return state,onset,refs


def generate_dataset(out_path,receipt_path):
    started=time.monotonic()
    features=[]; states=[]; onsets=[]
    families=[]; splits=[]; template_ids=[]; negative_only=[]; negative_struct=[]; refs_json=[]
    frame_count=None
    for fi,family in enumerate(FAMILIES):
        for bi in range(BASES_PER_FAMILY):
            template=build_template(family,bi)
            for variant in range(VARIANTS_PER_BASE):
                audio=render_waveform(template,variant)
                feat=extract_cqt_features(rms_normalize(audio)).squeeze(0).T.astype(np.float32,copy=False)
                if feat.ndim!=2 or feat.shape[1]!=CQT_BINS or not np.isfinite(feat).all():
                    raise RuntimeError("invalid frozen CQT features")
                if frame_count is None: frame_count=feat.shape[0]
                if feat.shape[0]!=frame_count: raise RuntimeError("inconsistent feature frame count")
                state,onset,refs=targets_for_template(template,frame_count)
                features.append(feat); states.append(state); onsets.append(onset)
                families.append(family); splits.append(template["split"]); template_ids.append(template["templateId"])
                negative_only.append(template["negativeOnly"]); negative_struct.append(template["hasNegativeStructure"])
                refs_json.append(json.dumps(refs,separators=(",",":"),sort_keys=True))
    elapsed=time.monotonic()-started
    x=np.stack(features); y_state=np.stack(states); y_onset=np.stack(onsets)
    np.savez_compressed(
        out_path,features=x,state=y_state,onset=y_onset,
        family=np.asarray(families),split=np.asarray(splits),template_id=np.asarray(template_ids),
        negative_only=np.asarray(negative_only,dtype=np.bool_),
        has_negative_structure=np.asarray(negative_struct,dtype=np.bool_),
        refs_json=np.asarray(refs_json),
    )
    size=Path(out_path).stat().st_size
    counts={k:int(np.sum(np.asarray(splits)==k)) for k in ("train","validation","test")}
    template_split={}
    for tid,sp in zip(template_ids,splits):
        old=template_split.setdefault(tid,sp)
        if old!=sp: raise RuntimeError("template-relative split leakage")
    receipt={
        "schema":"astra-s0-synthetic-render-receipt-v1",
        "seed":ROOT_SEED,"generator":"repo-owned analytic short-digital-waveguide/Karplus-Strong-family surrogate",
        "externalAudioAssets":False,"examples":len(features),"audioSeconds":len(features)*CLIP_SECONDS,
        "clipSeconds":CLIP_SECONDS,"internalSampleRate":INTERNAL_SR,"trainingSampleRate":OUTPUT_SR,
        "frameCount":frame_count,"featureBins":CQT_BINS,"splitCounts":counts,
        "uniqueTemplateCount":len(template_split),"variantsPerTemplate":VARIANTS_PER_BASE,
        "negativeStructureFraction":float(np.mean(negative_struct)),
        "negativeOnlyCount":int(np.sum(negative_only)),
        "persistedDatasetBytes":size,"renderSeconds":elapsed,
        "ceilings":{"examples":MAX_EXAMPLES,"audioSeconds":MAX_AUDIO_SECONDS,
                    "bytes":MAX_DATASET_BYTES,"renderSeconds":MAX_RENDER_SECONDS},
        "withinCeilings":bool(len(features)<=MAX_EXAMPLES and len(features)*CLIP_SECONDS<=MAX_AUDIO_SECONDS
                              and size<=MAX_DATASET_BYTES and elapsed<=MAX_RENDER_SECONDS),
        "datasetSha256":_sha256(out_path),
        "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False,"customerDeliveryEligible":False},
    }
    Path(receipt_path).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    if not receipt["withinCeilings"]: raise RuntimeError("synthetic render ceiling exceeded")
    print("S0_RENDER="+json.dumps(receipt,sort_keys=True))


def context5(features):
    x=np.asarray(features)
    if x.ndim!=3 or x.shape[2]!=CQT_BINS: raise ValueError("features must be N x T x 192")
    p=np.pad(x,((0,0),(2,2),(0,0)),mode="edge")
    return np.concatenate([p[:,i:i+x.shape[1],:] for i in range(5)],axis=2)


class FrameModel(nn.Module):
    def __init__(self,input_dim):
        super().__init__()
        self.encoder=nn.Sequential(nn.Linear(input_dim,128),nn.ReLU())
        self.state_head=nn.Linear(128,NUM_STRINGS*NUM_CLASSES)
        self.onset_head=nn.Linear(128,NUM_STRINGS)
    def forward(self,x):
        h=self.encoder(x)
        return self.state_head(h),self.onset_head(h)


def _loss(state_logits,onset_logits,state_target,onset_target):
    target=state_target.clone()
    target[target==-1]=SILENCE_CLASS
    raw=F.cross_entropy(state_logits.reshape(-1,NUM_CLASSES),target.reshape(-1),reduction="none")
    raw=raw.reshape(-1,NUM_STRINGS)
    w=torch.ones_like(raw); w[target!=SILENCE_CLASS]=STATE_ACTIVE_WEIGHT
    state_loss=(raw*w).sum()/w.sum()
    onset_loss=F.binary_cross_entropy_with_logits(
        onset_logits,onset_target.float(),
        pos_weight=torch.tensor(ONSET_POS_WEIGHT,dtype=onset_logits.dtype),
    )
    return state_loss+ONSET_LOSS_WEIGHT*onset_loss


def _set_determinism(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))


def fit_model(features,state,onset,train_mask,input_context,deadline):
    xin=context5(features) if input_context==5 else features
    train=np.flatnonzero(np.repeat(train_mask,features.shape[1]))
    xf=xin.reshape(-1,xin.shape[2])
    sf=state.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    of=onset.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    _set_determinism(ROOT_SEED+input_context)
    model=FrameModel(xin.shape[2])
    opt=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)
    rng=np.random.RandomState(ROOT_SEED+100+input_context)
    steps=0; started=time.monotonic(); stop="requested_steps_reached"
    while steps<MAX_STEPS:
        if time.monotonic()>=deadline:
            stop="fit_eval_time_ceiling"; break
        idx=rng.choice(train,size=BATCH_SIZE,replace=True)
        xb=torch.from_numpy(xf[idx]).float()
        sb=torch.from_numpy(sf[idx]).long()
        ob=torch.from_numpy(of[idx]).long()
        opt.zero_grad(set_to_none=True)
        sl,ol=model(xb)
        loss=_loss(sl,ol,sb,ob)
        if not torch.isfinite(loss): raise RuntimeError("nonfinite loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise RuntimeError("nonfinite gradient")
        opt.step(); steps+=1
    return model,{"optimizerSteps":steps,"requestedSteps":MAX_STEPS,
                  "elapsedSeconds":time.monotonic()-started,"stopReason":stop}


def _pred_pitch_events(decoded):
    out=[]
    for e in decoded:
        pitch=OPEN_MIDI[int(e.string)]+int(e.fret)
        out.append(EvalPitchEvent(
            str(e.id),pitch,float(e.start),float(e.end),float(e.start),float(e.end),
            False,False,True,True,
        ))
    return out


def _ref_pitch_events(rows):
    return [EvalPitchEvent(
        str(r["id"]),int(r["pitch"]),float(r["start"]),float(r["end"]),
        float(r["start"]),float(r["end"]),False,False,True,True,
    ) for r in rows]


def _sum_metric(rows,key):
    tp=sum(r[key]["truePositive"] for r in rows); fp=sum(r[key]["falsePositive"] for r in rows); fn=sum(r[key]["falseNegative"] for r in rows)
    p=tp/(tp+fp) if tp+fp else (1.0 if tp+fn==0 else 0.0)
    rec=tp/(tp+fn) if tp+fn else 1.0
    f1=2*p*rec/(p+rec) if p+rec else 0.0
    return {"truePositive":tp,"falsePositive":fp,"falseNegative":fn,"precision":p,"recall":rec,"f1":f1}


def evaluate_model(model,features,state,onset,family,split,negative_only,refs_json,input_context):
    xin=context5(features) if input_context==5 else features
    test_indices=np.flatnonzero(split=="test")
    per=[]; negative_preds=0; negative_seconds=0.0
    repeated_ref=0; repeated_tp=0
    model.eval()
    with torch.no_grad():
        for i in test_indices:
            x=torch.from_numpy(xin[i]).float()
            sl,ol=model(x)
            decoded=decode_event_list_v2(sl,ol,hop_seconds=HOP_LENGTH_SAMPLES/SAMPLE_RATE_HZ,
                                         state_active_threshold=STATE_ACTIVE_THRESHOLD,onset_threshold=ONSET_THRESHOLD,
                                         id_prefix=f"s0:{int(i)}")
            preds=_pred_pitch_events(decoded)
            refs_data=json.loads(str(refs_json[i])); refs=_ref_pitch_events(refs_data)
            score=score_pitch_events_v2(preds,refs)
            row={"index":int(i),"family":str(family[i]),"pitchOnset":score["pitchOnset"],
                 "pitchOnsetOffset":score["pitchOnsetOffset"],"predictionCountRaw":len(decoded)}
            per.append(row)
            if bool(negative_only[i]):
                negative_preds+=len(decoded); negative_seconds+=CLIP_SECONDS
            bypitch={}
            for r in refs:
                bypitch.setdefault(r.pitch,[]).append(r)
            repeated=[x for group in bypitch.values() for x in sorted(group,key=lambda z:z.start)[1:]]
            if repeated:
                rr=score_pitch_events_v2(preds,repeated)["pitchOnset"]
                repeated_ref+=len(repeated); repeated_tp+=rr["truePositive"]
    onset_agg=_sum_metric(per,"pitchOnset")
    offset_agg=_sum_metric(per,"pitchOnsetOffset")
    fam={}
    for f in FAMILIES:
        rows=[r for r in per if r["family"]==f]
        fam[f]=_sum_metric(rows,"pitchOnset")
    neg_rate=negative_preds/negative_seconds if negative_seconds else None
    rep_rec=repeated_tp/repeated_ref if repeated_ref else None
    return {"pitchOnset":onset_agg,"pitchOnsetOffset":offset_agg,
            "familyPitchOnset":fam,"repeatedReferenceCount":repeated_ref,
            "repeatedAttackRecall":rep_rec,"negativeOnlySeconds":negative_seconds,
            "negativeOnlyFalsePositiveEvents":negative_preds,"negativeOnlyFalsePositiveEventsPerSecond":neg_rate,
            "testExampleCount":len(test_indices)}


def run_pilot(dataset_path,out_path,candidate_path,comparator_path):
    started=time.monotonic(); deadline=started+MAX_FIT_EVAL_SECONDS
    d=np.load(dataset_path,allow_pickle=False)
    x=d["features"].astype(np.float32,copy=False); state=d["state"]; onset=d["onset"]
    family=d["family"]; split=d["split"]; negative_only=d["negative_only"]; refs=d["refs_json"]
    if len(x)!=EXAMPLES: raise RuntimeError("unexpected synthetic example count")
    if not np.isfinite(x).all(): raise RuntimeError("nonfinite dataset features")
    train=(split=="train")
    if MAX_MODELS!=2: raise RuntimeError("model ceiling invariant failed")
    comparator,cf=fit_model(x,state,onset,train,1,deadline)
    cm=evaluate_model(comparator,x,state,onset,family,split,negative_only,refs,1)
    candidate,kf=fit_model(x,state,onset,train,5,deadline)
    km=evaluate_model(candidate,x,state,onset,family,split,negative_only,refs,5)

    synthetic_gate={
        "pitchOnsetPrecisionAtLeast0_90":km["pitchOnset"]["precision"]>=.90,
        "pitchOnsetRecallAtLeast0_90":km["pitchOnset"]["recall"]>=.90,
        "pitchOnsetF1AtLeast0_90":km["pitchOnset"]["f1"]>=.90,
        "pitchOnsetOffsetF1AtLeast0_80":km["pitchOnsetOffset"]["f1"]>=.80,
        "repeatedAttackRecallAtLeast0_85":km["repeatedAttackRecall"] is not None and km["repeatedAttackRecall"]>=.85,
        "negativeFalsePositiveRateAtMost0_10PerSecond":km["negativeOnlyFalsePositiveEventsPerSecond"] is not None and km["negativeOnlyFalsePositiveEventsPerSecond"]<=.10,
        "eachSupportedFamilyOnsetF1AtLeast0_80":all(v["f1"]>=.80 for v in km["familyPitchOnset"].values()),
        "finiteAndBounded":bool(np.isfinite(x).all() and cf["optimizerSteps"]<=MAX_STEPS and kf["optimizerSteps"]<=MAX_STEPS),
    }
    delta_f1=km["pitchOnset"]["f1"]-cm["pitchOnset"]["f1"]
    delta_rep=(km["repeatedAttackRecall"] or 0)-(cm["repeatedAttackRecall"] or 0)
    precision_loss=cm["pitchOnset"]["precision"]-km["pitchOnset"]["precision"]
    comparator_gate=(delta_f1>=.03) or (delta_rep>=.10 and precision_loss<=.02)
    overall=all(synthetic_gate.values()) and comparator_gate and cf["optimizerSteps"]==MAX_STEPS and kf["optimizerSteps"]==MAX_STEPS
    receipt={
        "schema":SCHEMA,"seed":ROOT_SEED,
        "dataset":{"sha256":_sha256(dataset_path),"examples":len(x),"audioSeconds":AUDIO_SECONDS,
                   "persistedBytes":Path(dataset_path).stat().st_size,
                   "splitCounts":{s:int(np.sum(split==s)) for s in ("train","validation","test")}},
        "models":{
            "comparator":{"name":"per-frame-192x128","inputContextFrames":1,"fit":cf,"test":cm},
            "candidate":{"name":"five-frame-960x128","inputContextFrames":5,"fit":kf,"test":km},
        },
        "thresholds":{"stateActive":STATE_ACTIVE_THRESHOLD,"onset":ONSET_THRESHOLD,"thresholdSearch":False,"thresholdRetuning":False},
        "syntheticGate":synthetic_gate,
        "candidateVsComparator":{"onsetF1Delta":delta_f1,"repeatedAttackRecallDelta":delta_rep,
                                 "candidatePrecisionLossVsComparator":precision_loss,"passed":bool(comparator_gate)},
        "pilotAdvancementGatePassed":bool(overall),
        "execution":{"modelCount":2,"optimizerStepsTotal":cf["optimizerSteps"]+kf["optimizerSteps"],
                     "fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0},
        "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False,"externalAudioAssets":False,
                  "productionMutation":False,"customerDeliveryEligible":False},
        "meaning":"Synthetic-only bounded engineering hypothesis test. Passing does not establish real-guitar transfer, unseen-performer generalization, or product readiness.",
    }
    Path(out_path).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"kind":"comparator","stateDict":comparator.state_dict(),"optimizerSteps":cf["optimizerSteps"]},comparator_path)
    torch.save({"schema":SCHEMA,"kind":"candidate","stateDict":candidate.state_dict(),"optimizerSteps":kf["optimizerSteps"]},candidate_path)
    if receipt["execution"]["fitEvalSeconds"]>MAX_FIT_EVAL_SECONDS+5:
        raise RuntimeError("fit/eval time ceiling exceeded")
    print("S0_RESULT="+json.dumps(receipt,sort_keys=True))


def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    g=sub.add_parser("generate"); g.add_argument("--out",required=True); g.add_argument("--receipt",required=True)
    r=sub.add_parser("run"); r.add_argument("--dataset",required=True); r.add_argument("--out",required=True)
    r.add_argument("--candidate",required=True); r.add_argument("--comparator",required=True)
    args=ap.parse_args()
    if args.cmd=="generate": generate_dataset(args.out,args.receipt)
    else: run_pilot(args.dataset,args.out,args.candidate,args.comparator)

if __name__=="__main__": main()
