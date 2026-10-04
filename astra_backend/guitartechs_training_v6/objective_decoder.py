from __future__ import annotations

import math
from collections import Counter

import numpy as np
import torch
import torch.nn.functional as F

from .model import NUM_CLASSES,NUM_FRETS,NUM_PITCHES,NUM_STRINGS,OPEN_MIDI,SILENCE_CLASS

MASK=-100
STATE_ACTIVE_WEIGHT=1.15
ONSET_POS_WEIGHT=2.0
ACTIVITY_POS_WEIGHT=1.2
PITCH_POS_WEIGHT=3.0
EVENT_POS_WEIGHT=2.0

# Frozen explicit multitask weights. No learned task weighting.
STATE_LOSS_WEIGHT=1.0
ONSET_LOSS_WEIGHT=0.35
ACTIVITY_LOSS_WEIGHT=0.35
PITCH_LOSS_WEIGHT=0.25
EVENT_LOSS_WEIGHT=0.75
CONTENT_WEIGHT_MIN=0.75
CONTENT_WEIGHT_MAX=1.50
PRIMARY_CONTENT=("chords","scales","singlenotes","PalmMute")

EVENT_START_CONFIDENCE=0.50
ACTIVITY_CONTINUE_CONFIDENCE=0.45
STATE_START_CONFIDENCE=0.30
STATE_CONTINUE_CONFIDENCE=0.20
STATE_START_VS_SILENCE_RATIO=0.70
STATE_CONTINUE_VS_SILENCE_RATIO=0.60
GAP_FRAMES=2
MIN_RUN_FRAMES=2

def bounded_content_weights(category_counts: dict[str,int]) -> dict[str,float]:
    if set(category_counts)!=set(PRIMARY_CONTENT):
        raise ValueError("all four primary content classes are required")
    if any((not isinstance(v,int)) or v<=0 for v in category_counts.values()):
        raise ValueError("content counts must be positive integers")
    mean_count=sum(category_counts.values())/len(PRIMARY_CONTENT)
    raw={name:math.sqrt(mean_count/category_counts[name]) for name in PRIMARY_CONTENT}
    clipped={name:min(CONTENT_WEIGHT_MAX,max(CONTENT_WEIGHT_MIN,raw[name])) for name in PRIMARY_CONTENT}
    weighted_mean=sum(clipped[name]*category_counts[name] for name in PRIMARY_CONTENT)/sum(category_counts.values())
    return {name:min(CONTENT_WEIGHT_MAX,max(CONTENT_WEIGHT_MIN,clipped[name]/weighted_mean)) for name in PRIMARY_CONTENT}

def normalized_targets(labels):
    target=labels.transpose(1,2).contiguous().clone()
    target[target==-1]=SILENCE_CLASS
    invalid=(target!=MASK)&((target<0)|(target>=NUM_CLASSES))
    if torch.any(invalid): raise ValueError("invalid class")
    return target

def targets(labels):
    state=normalized_targets(labels)
    valid=state!=MASK
    active=valid&(state!=SILENCE_CLASS)
    onset=torch.zeros_like(active,dtype=torch.float32)
    onset_valid=torch.zeros_like(valid)
    if state.shape[1]>1:
        pv=valid[:,:-1,:]; nv=valid[:,1:,:]
        onset_valid[:,1:,:]=pv&nv
        pa=active[:,:-1,:]; na=active[:,1:,:]
        changed=state[:,1:,:]!=state[:,:-1,:]
        onset[:,1:,:]=(na & (~pa|changed)).float()
    event=onset.clone()
    activity=active.float()
    pitch=torch.zeros((state.shape[0],state.shape[1],NUM_PITCHES),dtype=torch.float32,device=state.device)
    pitch_valid=valid.all(dim=-1)
    for s in range(NUM_STRINGS):
        fret=state[:,:,s]
        mask=(fret>=0)&(fret<NUM_FRETS)&pitch_valid
        if torch.any(mask):
            midi=OPEN_MIDI[s]+fret[mask]
            rows=mask.nonzero(as_tuple=False)
            pitch[rows[:,0],rows[:,1],(midi-40).long()]=1.0
    return dict(state=state,valid=valid,active=active,onset=onset,onset_valid=onset_valid,
                event=event,activity=activity,pitch=pitch,pitch_valid=pitch_valid)

def mbce(logits,target,valid,pos):
    if not torch.any(valid): return logits.new_tensor(0.0)
    raw=F.binary_cross_entropy_with_logits(logits,target.to(logits.dtype),
        pos_weight=torch.tensor(pos,device=logits.device,dtype=logits.dtype),reduction="none")
    return raw[valid].mean()

def pitch_bce(logits,target,valid):
    if not torch.any(valid): return logits.new_tensor(0.0)
    pw=torch.full((NUM_PITCHES,),PITCH_POS_WEIGHT,device=logits.device,dtype=logits.dtype)
    raw=F.binary_cross_entropy_with_logits(logits,target.to(logits.dtype),pos_weight=pw,reduction="none")
    return raw[valid].mean()

def v6_sequence_loss(outputs,labels,*,content_weight:float=1.0):
    req={"tablature","onset","activity","pitch","event"}
    if not (CONTENT_WEIGHT_MIN <= content_weight <= CONTENT_WEIGHT_MAX): raise ValueError("content_weight outside frozen bounds")
    if not req.issubset(outputs): raise ValueError("missing V6 heads")
    t=targets(labels)
    batch,frames,strings=t["state"].shape
    x=outputs["tablature"].reshape(batch,frames,NUM_STRINGS,NUM_CLASSES)
    flat=F.cross_entropy(x.reshape(-1,NUM_CLASSES),t["state"].reshape(-1),ignore_index=MASK,reduction="none").reshape(batch,frames,NUM_STRINGS)
    weight=torch.ones_like(flat); weight[t["active"]]=STATE_ACTIVE_WEIGHT; weight*=t["valid"]
    state=(flat*weight).sum()/weight.sum().clamp(min=1.0)
    onset=mbce(outputs["onset"],t["onset"],t["onset_valid"],ONSET_POS_WEIGHT)
    activity=mbce(outputs["activity"],t["activity"],t["valid"],ACTIVITY_POS_WEIGHT)
    event=mbce(outputs["event"],t["event"],t["onset_valid"],EVENT_POS_WEIGHT)
    pitch=pitch_bce(outputs["pitch"],t["pitch"],t["pitch_valid"])
    total=content_weight*(STATE_LOSS_WEIGHT*state + ONSET_LOSS_WEIGHT*onset + ACTIVITY_LOSS_WEIGHT*activity +
           PITCH_LOSS_WEIGHT*pitch + EVENT_LOSS_WEIGHT*event)
    return total,{"state":state,"onset":onset,"activity":activity,"pitch":pitch,"event":event}

def _runs(x):
    out=[];i=0
    while i<len(x):
        v=int(x[i]);j=i+1
        while j<len(x) and int(x[j])==v:j+=1
        out.append((i,j,v));i=j
    return out

def _merge_short_gaps(states,max_gap):
    out=states.copy();changed=True
    while changed:
        changed=False
        runs=_runs(out)
        for i in range(1,len(runs)-1):
            a,b,v=runs[i]
            if v==-1 and b-a<=max_gap and runs[i-1][2]>=0 and runs[i-1][2]==runs[i+1][2]:
                out[a:b]=runs[i-1][2];changed=True;break
    return out

def _prune(states,min_run):
    out=states.copy()
    for a,b,v in _runs(out):
        if v>=0 and b-a<min_run: out[a:b]=-1
    return out

def decode_v6(state_prob,event_prob,activity_prob,
              event_start_confidence=EVENT_START_CONFIDENCE,
              activity_continue_confidence=ACTIVITY_CONTINUE_CONFIDENCE,
              state_start_confidence=STATE_START_CONFIDENCE,
              state_continue_confidence=STATE_CONTINUE_CONFIDENCE):
    state=np.asarray(state_prob,float); event=np.asarray(event_prob,float); activity=np.asarray(activity_prob,float)
    if state.ndim!=3 or state.shape[1:]!=(NUM_STRINGS,NUM_CLASSES): raise ValueError("bad state shape")
    if event.shape!=state.shape[:2] or activity.shape!=state.shape[:2]: raise ValueError("bad auxiliary shape")
    out=np.full((state.shape[0],NUM_STRINGS),-1,dtype=np.int16)
    for s in range(NUM_STRINGS):
        cur=-1
        for t in range(state.shape[0]):
            row=state[t,s];sil=float(row[SILENCE_CLASS]);best=int(np.argmax(row[:NUM_FRETS]));bp=float(row[best])
            can_start=(event[t,s]>=event_start_confidence and bp>=state_start_confidence and bp>=sil*STATE_START_VS_SILENCE_RATIO)
            if cur>=0:
                if can_start and best!=cur:
                    cur=best;out[t,s]=cur;continue
                keep=float(row[cur])
                if activity[t,s]>=activity_continue_confidence and keep>=state_continue_confidence and keep>=sil*STATE_CONTINUE_VS_SILENCE_RATIO:
                    out[t,s]=cur;continue
                cur=-1
            if can_start: cur=best;out[t,s]=cur
        out[:,s]=_prune(_merge_short_gaps(out[:,s],GAP_FRAMES),MIN_RUN_FRAMES)
    return out

def count_active_runs(states):
    arr=np.asarray(states)
    return sum(1 for s in range(NUM_STRINGS) for _,_,v in _runs(arr[:,s]) if v>=0)
