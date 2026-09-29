#!/usr/bin/env python3
"""Frozen V5 target-structure objective helpers.

Same 6x21 state logits and onset logits as the S9/S6-style model.  This module
changes only the state objective / diagnostic aggregation.  It does not load
models, audio, V1.1, P1/P2/P3, or mutate decoder thresholds.
"""
from __future__ import annotations
import torch
import torch.nn.functional as F

NUM_STRINGS=6
NUM_FRETS=20
NUM_CLASSES=21
SILENCE_CLASS=20
OPEN_MIDI=(40,45,50,55,59,64)
STATE_ACTIVE_WEIGHT=9.0
EPS=1e-8

def exact_state_loss(state_logits,state_target):
    target=state_target.clone()
    target[target==-1]=SILENCE_CLASS
    raw=F.cross_entropy(
        state_logits.reshape(-1,NUM_CLASSES),
        target.reshape(-1),
        reduction="none",
    ).reshape(-1,NUM_STRINGS)
    weights=torch.ones_like(raw)
    weights[target!=SILENCE_CLASS]=STATE_ACTIVE_WEIGHT
    return (raw*weights).sum()/weights.sum()

def _pitch_geometry(device):
    min_pitch=40
    max_pitch=max(OPEN_MIDI)+NUM_FRETS-1
    pcount=max_pitch-min_pitch+1
    pos_pitch=[]
    for s,open_midi in enumerate(OPEN_MIDI):
        for fret in range(NUM_FRETS):
            pos_pitch.append(open_midi+fret-min_pitch)
    pos_pitch=torch.tensor(pos_pitch,dtype=torch.long,device=device)
    compat=F.one_hot(pos_pitch,num_classes=pcount).T.to(torch.float32)
    return min_pitch,pcount,pos_pitch,compat

def pitch_equivalent_state_loss(state_logits,state_target):
    """Noisy-OR pitch coverage plus unsupported-state suppression.

    Coverage rewards assigning state probability to any physical string/fret
    position for each active target MIDI pitch. Suppression requires each
    string's probability mass to remain on silence or positions whose pitch is
    active in the target frame.
    """
    probs=torch.softmax(
        state_logits.reshape(-1,NUM_STRINGS,NUM_CLASSES),dim=-1
    )
    active_probs=probs[:,:,:NUM_FRETS]
    bsz=probs.shape[0]
    device=probs.device
    min_pitch,pcount,pos_pitch,compat=_pitch_geometry(device)
    compat=compat.to(probs.dtype)

    open_t=torch.tensor(OPEN_MIDI,dtype=torch.long,device=device)
    active=(state_target>=0)&(state_target<NUM_FRETS)
    fret=torch.clamp(state_target,min=0,max=NUM_FRETS-1)
    pitch_idx=(open_t.view(1,-1)+fret-min_pitch).long()
    target_mask=torch.zeros((bsz,pcount),dtype=probs.dtype,device=device)
    target_mask.scatter_add_(1,pitch_idx,active.to(probs.dtype))
    target_mask=torch.clamp(target_mask,0,1)

    flat=active_probs.reshape(bsz,-1)
    log_miss=torch.log(torch.clamp(1.0-flat,min=EPS)) @ compat.T
    cover=1.0-torch.exp(log_miss)
    coverage=(-torch.log(torch.clamp(cover,min=EPS,max=1.0))*target_mask).sum()

    allowed_flat=target_mask[:,pos_pitch]
    allowed_active=(
        flat*allowed_flat
    ).reshape(bsz,NUM_STRINGS,NUM_FRETS).sum(dim=-1)
    allowed_total=torch.clamp(
        probs[:,:,SILENCE_CLASS]+allowed_active,min=EPS,max=1.0
    )
    suppression=(-torch.log(allowed_total)).sum()

    denom=STATE_ACTIVE_WEIGHT*target_mask.sum()+float(NUM_STRINGS*bsz)
    return (
        STATE_ACTIVE_WEIGHT*coverage+suppression
    )/torch.clamp(denom,min=1.0)

def mixed_state_loss(state_logits,state_target):
    return 0.5*exact_state_loss(
        state_logits,state_target
    )+0.5*pitch_equivalent_state_loss(state_logits,state_target)

def compatible_state_probability(state_probabilities,midi_pitch):
    """Bounded noisy-OR over all physical positions representing midi_pitch."""
    if state_probabilities.shape[-2:]!=(NUM_STRINGS,NUM_CLASSES):
        raise ValueError("expected ... x 6 x 21 probabilities")
    positions=[
        (s,midi_pitch-open_midi)
        for s,open_midi in enumerate(OPEN_MIDI)
        if 0<=midi_pitch-open_midi<NUM_FRETS
    ]
    if not positions:
        raise ValueError("pitch outside representable guitar range")
    miss=torch.ones(
        state_probabilities.shape[:-2],
        dtype=state_probabilities.dtype,
        device=state_probabilities.device,
    )
    for s,fret in positions:
        miss=miss*(1.0-state_probabilities[...,s,fret])
    return 1.0-miss

def compatible_onset_probability(onset_probabilities,midi_pitch):
    positions=[
        s for s,open_midi in enumerate(OPEN_MIDI)
        if 0<=midi_pitch-open_midi<NUM_FRETS
    ]
    if not positions:
        raise ValueError("pitch outside representable guitar range")
    return onset_probabilities[...,positions].amax(dim=-1)
