#!/usr/bin/env python3
from __future__ import annotations
import argparse,random
import numpy as np,torch
from guitartechs_training_v2 import train_v2 as base
from guitartechs_training_v7.model import TemporalTabCNNV7,NUM_CLASSES,NUM_STRINGS
from guitartechs_training_v7.objective_decoder import v7_sequence_loss,decode_ranked_events,count_active_runs,local_event_maxima

SEED=20261004
def setup():
 random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.use_deterministic_algorithms(True);torch.set_num_threads(4)

def batch():
 feat=np.random.RandomState(SEED).normal(0,1,(192,260)).astype(np.float32)
 x=torch.from_numpy(base.sequence_windows(feat,20,220)[None,:,None,:,:])
 y=torch.from_numpy(np.random.RandomState(SEED+1).randint(0,NUM_CLASSES,(1,NUM_STRINGS,200),dtype=np.int64))
 return x,y

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source-root",required=True);a=ap.parse_args();setup()
 m=TemporalTabCNNV7(a.source_root);x,y=batch();o=m(x);loss,parts=v7_sequence_loss(o,y)
 assert torch.isfinite(loss);loss.backward()
 for name in ("state_head","activity_head","pitch_head","event_head"):
  grads=[p.grad for p in getattr(m,name).parameters() if p.requires_grad]
  assert grads and all(g is not None and torch.all(torch.isfinite(g)) for g in grads)
 assert all(torch.isfinite(v) for v in parts.values())
 print("V7_FINITE_GRADIENTS_PASS")

 # Decoder must be invariant to affine event-score calibration.
 T=10
 state=np.zeros((T,NUM_STRINGS,NUM_CLASSES),float);state[...,20]=1.
 for t in range(2,7):state[t,0,:]=0;state[t,0,4]=0.8;state[t,0,20]=0.2
 ev=np.zeros((T,NUM_STRINGS),float);ev[2,0]=2.;ev[6,0]=1.
 d1=decode_ranked_events(state,ev);d2=decode_ranked_events(state,ev*7.0+13.0)
 assert np.array_equal(d1,d2)
 assert count_active_runs(d1)==1 and np.all(d1[2:7,0]==4)
 print("V7_CALIBRATION_INVARIANCE_PASS")

 # Local ranking, not absolute magnitude, decides the event.
 lo=np.array([[0.1],[0.2],[0.9],[0.3],[0.1]])
 hi=lo*100+1000
 assert np.array_equal(local_event_maxima(lo),local_event_maxima(hi))
 print("V7_LOCAL_RANKING_PASS")
 print("V7_SYNTHETIC_VERIFICATION_PASS")
if __name__=="__main__":main()
