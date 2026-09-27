#!/usr/bin/env python3
"""Synthetic-only harness primitives for the temporal-context controlled intervention."""
from __future__ import annotations
import torch
from torch import nn

BASE_FEATURE_DIM=192
CONTEXT_FEATURE_DIM=576
HIDDEN_DIM=128
NUM_STRINGS=6
NUM_CLASSES=21

def temporal_triplet(x: torch.Tensor) -> torch.Tensor:
    if x.ndim != 3 or x.shape[-1] != BASE_FEATURE_DIM:
        raise ValueError("expected B x T x 192")
    prev=torch.cat([x[:,0:1,:],x[:,:-1,:]],dim=1)
    nxt=torch.cat([x[:,1:,:],x[:,-1:,:]],dim=1)
    return torch.cat([prev,x,nxt],dim=-1)

def repeated_current(x: torch.Tensor) -> torch.Tensor:
    if x.ndim != 3 or x.shape[-1] != BASE_FEATURE_DIM:
        raise ValueError("expected B x T x 192")
    return torch.cat([x,x,x],dim=-1)

class ControlledContextModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder=nn.Sequential(nn.Linear(CONTEXT_FEATURE_DIM,HIDDEN_DIM),nn.ReLU())
        self.state_head=nn.Linear(HIDDEN_DIM,NUM_STRINGS*NUM_CLASSES)
        self.onset_head=nn.Linear(HIDDEN_DIM,NUM_STRINGS)
    def forward(self,x):
        if x.ndim!=3 or x.shape[-1]!=CONTEXT_FEATURE_DIM:
            raise ValueError("expected B x T x 576")
        h=self.encoder(x)
        return {"state":self.state_head(h),"onset":self.onset_head(h)}

def clone_identical_pair(seed:int=20260927):
    torch.manual_seed(seed)
    base=ControlledContextModel()
    a=ControlledContextModel(); b=ControlledContextModel()
    a.load_state_dict(base.state_dict()); b.load_state_dict(base.state_dict())
    return a,b
