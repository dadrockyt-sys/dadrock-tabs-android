#!/usr/bin/env python3
from __future__ import annotations
import json
import torch
from paired_view import FROZEN_CONFIG, paired_tensor_views, symmetric_kl_consistency

CONSISTENCY_WEIGHT = 0.10

def main():
    assert CONSISTENCY_WEIGHT == 0.10
    assert FROZEN_CONFIG.gain_db_max_abs == 3.0
    assert FROZEN_CONFIG.noise_snr_db_min == 30.0
    assert FROZEN_CONFIG.noise_snr_db_max == 50.0
    assert FROZEN_CONFIG.tilt_db_per_octave_max_abs == 1.5
    assert FROZEN_CONFIG.mask_span_frames_max == 4
    assert FROZEN_CONFIG.mask_span_count_max == 2
    x=torch.arange(1*32*1*192*9,dtype=torch.float32).reshape(1,32,1,192,9)/10000.0
    a,b=paired_tensor_views(x,20260921)
    a2,b2=paired_tensor_views(x,20260921)
    assert torch.equal(a,a2) and torch.equal(b,b2)
    assert a.shape == x.shape and b.shape == x.shape
    assert torch.isfinite(a).all() and torch.isfinite(b).all()
    la=torch.randn(1,32,6,21,generator=torch.Generator().manual_seed(1),requires_grad=True)
    lb=torch.randn(1,32,6,21,generator=torch.Generator().manual_seed(2),requires_grad=True)
    c=symmetric_kl_consistency(la,lb)
    total=0.5*(la.square().mean()+lb.square().mean())+CONSISTENCY_WEIGHT*c
    total.backward()
    assert torch.isfinite(total)
    assert la.grad is not None and torch.isfinite(la.grad).all()
    assert lb.grad is not None and torch.isfinite(lb.grad).all()
    print(json.dumps({"status":"PASS","optimizerSteps":0,"realMediaAccessed":False,"consistencyWeight":CONSISTENCY_WEIGHT},sort_keys=True))

if __name__=="__main__":
    main()
