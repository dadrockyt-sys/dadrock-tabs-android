from __future__ import annotations
import torch
import torch.nn.functional as F

ONSET_POS_WEIGHT=8.0

def spread_onset_targets(onset):
    """Frozen O1/O3 +/-1 frame soft target: center=1, adjacent=.5."""
    if onset.ndim != 3:
        raise ValueError('expected N x strings x frames onset tensor')
    out=onset.to(torch.float32).clone()
    left=torch.zeros_like(out); right=torch.zeros_like(out)
    left[:,:,1:]=onset[:,:,:-1].to(torch.float32)*0.5
    right[:,:,:-1]=onset[:,:,1:].to(torch.float32)*0.5
    return torch.maximum(out,torch.maximum(left,right))

def bce_onset_loss(logits,target):
    return F.binary_cross_entropy_with_logits(
        logits,target.to(logits.dtype),
        pos_weight=torch.tensor(ONSET_POS_WEIGHT,dtype=logits.dtype,device=logits.device)
    )

def focal_onset_loss(logits,target):
    """Frozen gamma=2, alpha+=.75, alpha-=.25 focal loss; supports soft target O3."""
    y=target.to(logits.dtype)
    p=torch.sigmoid(logits)
    ce=F.binary_cross_entropy_with_logits(logits,y,reduction='none')
    pt=y*p+(1-y)*(1-p)
    alpha=y*0.75+(1-y)*0.25
    return (alpha*((1-pt)**2.0)*ce).mean()

def onset_loss(logits,target,arm):
    if arm in ('O0','O1'):
        return bce_onset_loss(logits,target)
    if arm in ('O2','O3'):
        return focal_onset_loss(logits,target)
    raise ValueError(arm)
