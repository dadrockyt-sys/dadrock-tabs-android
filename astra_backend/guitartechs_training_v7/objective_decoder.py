from __future__ import annotations

import math
import numpy as np
import torch
import torch.nn.functional as F

from .model import NUM_CLASSES,NUM_FRETS,NUM_PITCHES,NUM_STRINGS,OPEN_MIDI,SILENCE_CLASS

MASK=-100
ACTIVE_WEIGHT=1.30
CONTINUITY_LAMBDA=0.10
IDENTITY_LAMBDA=0.25
IDENTITY_MARGIN=0.15
EVENT_RANK_MARGIN=0.50
EVENT_RANK_RADIUS=2

STATE_WEIGHT=1.0
ACTIVITY_WEIGHT=0.25
PITCH_WEIGHT=0.20
EVENT_RANK_WEIGHT=0.60

CONTENT_WEIGHT_MIN=0.75
CONTENT_WEIGHT_MAX=1.50
PRIMARY_CONTENT=("chords","scales","singlenotes","PalmMute")
GAP_FRAMES=2
MIN_RUN_FRAMES=2

def bounded_content_weights(counts):
    if set(counts)!=set(PRIMARY_CONTENT): raise ValueError("all four content classes required")
    mean=sum(counts.values())/4
    raw={k:math.sqrt(mean/counts[k]) for k in PRIMARY_CONTENT}
    clip={k:min(CONTENT_WEIGHT_MAX,max(CONTENT_WEIGHT_MIN,raw[k])) for k in PRIMARY_CONTENT}
    wm=sum(clip[k]*counts[k] for k in PRIMARY_CONTENT)/sum(counts.values())
    return {k:min(CONTENT_WEIGHT_MAX,max(CONTENT_WEIGHT_MIN,clip[k]/wm)) for k in PRIMARY_CONTENT}

def normalized_targets(labels):
    t=labels.transpose(1,2).contiguous().clone()
    t[t==-1]=SILENCE_CLASS
    bad=(t!=MASK)&((t<0)|(t>=NUM_CLASSES))
    if torch.any(bad): raise ValueError("bad target")
    return t

def target_views(labels):
    state=normalized_targets(labels); valid=state!=MASK; active=valid&(state!=SILENCE_CLASS)
    event=torch.zeros_like(active,dtype=torch.bool); event_valid=torch.zeros_like(valid)
    if state.shape[1]>1:
        ok=valid[:,1:]&valid[:,:-1]
        event_valid[:,1:]=ok
        event[:,1:]=ok&active[:,1:]&((~active[:,:-1])|(state[:,1:]!=state[:,:-1]))
    activity=active.float()
    pitch=torch.zeros((state.shape[0],state.shape[1],NUM_PITCHES),dtype=torch.float32,device=state.device)
    frame_valid=valid.all(-1)
    for s in range(NUM_STRINGS):
        fret=state[:,:,s]; m=(fret>=0)&(fret<NUM_FRETS)&frame_valid
        if torch.any(m):
            rows=m.nonzero(as_tuple=False); midi=OPEN_MIDI[s]+fret[m]
            pitch[rows[:,0],rows[:,1],(midi-40).long()]=1.0
    return state,valid,active,event,event_valid,activity,pitch,frame_valid

def continuity_loss(probs,target):
    stable=(target[:,1:]!=MASK)&(target[:,:-1]!=MASK)&(target[:,1:]==target[:,:-1])
    if not torch.any(stable): return probs.new_tensor(0.)
    d=(probs[:,1:]-probs[:,:-1]).pow(2).mean(-1)
    return d[stable].mean()

def identity_loss(probs,target):
    losses=[]
    B,T,S=target.shape
    for b in range(B):
      for t in range(T):
       for s in range(S):
        fret=int(target[b,t,s])
        if fret in (MASK,SILENCE_CLASS) or not 0<=fret<NUM_FRETS: continue
        pitch=OPEN_MIDI[s]+fret; correct=probs[b,t,s,fret]
        for ss in range(NUM_STRINGS):
          if ss==s: continue
          af=pitch-OPEN_MIDI[ss]
          if 0<=af<NUM_FRETS:
            alt_target=int(target[b,t,ss])
            if alt_target==MASK or alt_target==af: continue
            losses.append(F.relu(IDENTITY_MARGIN+probs[b,t,ss,af]-correct))
    return torch.stack(losses).mean() if losses else probs.new_tensor(0.)

def event_rank_loss(logits,event,event_valid):
    # Each true event must outrank neighboring valid non-events on the same string.
    losses=[]
    B,T,S=event.shape
    for b in range(B):
      for s in range(S):
        for t in torch.nonzero(event[b,:,s],as_tuple=False).flatten().tolist():
          lo=max(0,t-EVENT_RANK_RADIUS);hi=min(T,t+EVENT_RANK_RADIUS+1)
          neg=event_valid[b,lo:hi,s] & (~event[b,lo:hi,s])
          if torch.any(neg):
            pos=logits[b,t,s]
            losses.append(F.relu(EVENT_RANK_MARGIN-pos+logits[b,lo:hi,s][neg]).mean())
    return torch.stack(losses).mean() if losses else logits.new_tensor(0.)

def v7_sequence_loss(outputs,labels,*,content_weight=1.0):
    state,valid,active,event,event_valid,activity,pitch,pitch_valid=target_views(labels)
    B,T,S=state.shape
    logits=outputs["tablature"].reshape(B,T,S,NUM_CLASSES)
    flat=F.cross_entropy(logits.reshape(-1,NUM_CLASSES),state.reshape(-1),ignore_index=MASK,reduction="none").reshape(B,T,S)
    w=torch.ones_like(flat);w[active]=ACTIVE_WEIGHT;w*=valid
    ce=(flat*w).sum()/w.sum().clamp(min=1.)
    probs=torch.softmax(logits,-1)
    cont=continuity_loss(probs,state);ident=identity_loss(probs,state)
    act=F.binary_cross_entropy_with_logits(outputs["activity"][valid],activity[valid]) if torch.any(valid) else ce.new_tensor(0.)
    p=F.binary_cross_entropy_with_logits(outputs["pitch"][pitch_valid],pitch[pitch_valid]) if torch.any(pitch_valid) else ce.new_tensor(0.)
    rank=event_rank_loss(outputs["event"],event,event_valid)
    total=content_weight*(STATE_WEIGHT*(ce+CONTINUITY_LAMBDA*cont+IDENTITY_LAMBDA*ident)+ACTIVITY_WEIGHT*act+PITCH_WEIGHT*p+EVENT_RANK_WEIGHT*rank)
    return total,{"stateCE":ce,"continuity":cont,"identityMargin":ident,"activity":act,"pitch":p,"eventRank":rank}

def _runs(x):
    out=[];i=0
    while i<len(x):
        v=int(x[i]);j=i+1
        while j<len(x) and int(x[j])==v:j+=1
        out.append((i,j,v));i=j
    return out

def _merge(x,max_gap):
    out=x.copy();changed=True
    while changed:
      changed=False;r=_runs(out)
      for i in range(1,len(r)-1):
        a,b,v=r[i]
        if v==-1 and b-a<=max_gap and r[i-1][2]>=0 and r[i-1][2]==r[i+1][2]:
          out[a:b]=r[i-1][2];changed=True;break
    return out

def _prune(x,min_run):
    out=x.copy()
    for a,b,v in _runs(out):
        if v>=0 and b-a<min_run: out[a:b]=-1
    return out

def local_event_maxima(scores):
    scores=np.asarray(scores,float)
    out=np.zeros_like(scores,dtype=bool)
    T,S=scores.shape
    for s in range(S):
      for t in range(T):
        lo=max(0,t-EVENT_RANK_RADIUS);hi=min(T,t+EVENT_RANK_RADIUS+1)
        # deterministic tie-break: earliest maximum in window
        win=scores[lo:hi,s];m=np.max(win)
        if scores[t,s]==m and (lo+int(np.argmax(win)))==t: out[t,s]=True
    return out

def decode_ranked_events(state_prob,event_score):
    state=np.asarray(state_prob,float);event=np.asarray(event_score,float)
    if state.ndim!=3 or state.shape[1:]!=(NUM_STRINGS,NUM_CLASSES):raise ValueError("bad state")
    if event.shape!=state.shape[:2]:raise ValueError("bad event")
    maxima=local_event_maxima(event)
    T=state.shape[0];out=np.full((T,NUM_STRINGS),-1,np.int16)
    for s in range(NUM_STRINGS):
      cur=-1
      for t in range(T):
        row=state[t,s];best=int(np.argmax(row)) # purely relative state decision
        active=best!=SILENCE_CLASS
        start=maxima[t,s] and active
        if cur>=0:
          if start and best!=cur:
            cur=best;out[t,s]=cur;continue
          if active and best==cur:
            out[t,s]=cur;continue
          cur=-1
        if start:
          cur=best;out[t,s]=cur
      out[:,s]=_prune(_merge(out[:,s],GAP_FRAMES),MIN_RUN_FRAMES)
    return out

def count_active_runs(states):
    return sum(1 for s in range(NUM_STRINGS) for _,_,v in _runs(np.asarray(states)[:,s]) if v>=0)
