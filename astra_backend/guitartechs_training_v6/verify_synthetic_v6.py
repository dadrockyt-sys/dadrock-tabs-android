#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,random,tempfile
from pathlib import Path
import numpy as np, torch
from guitartechs_training_v2 import train_v2 as base
from guitartechs_training_v6.model import TemporalTabCNNV6,NUM_CLASSES,NUM_PITCHES,NUM_STRINGS
from guitartechs_training_v6.objective_decoder import v6_sequence_loss,decode_v6,count_active_runs

SEED=20261003

def setup():
    random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True);torch.set_num_threads(4)

def batch():
    feat=np.random.RandomState(SEED).normal(0,1,size=(192,260)).astype(np.float32)
    windows=base.sequence_windows(feat,20,220)
    x=torch.from_numpy(windows[None,:,None,:,:])
    labels=np.random.RandomState(SEED+1).randint(0,NUM_CLASSES,size=(1,NUM_STRINGS,200),dtype=np.int64)
    return x,torch.from_numpy(labels)

def new(root):
    m=TemporalTabCNNV6(root); return m,torch.optim.Adadelta(m.parameters(),lr=1.0)

def check_shapes(root):
    setup();m,_=new(root);x,y=batch();o=m(x)
    assert o["tablature"].shape==(1,200,NUM_STRINGS*NUM_CLASSES)
    assert o["onset"].shape==(1,200,NUM_STRINGS)
    assert o["activity"].shape==(1,200,NUM_STRINGS)
    assert o["event"].shape==(1,200,NUM_STRINGS)
    assert o["pitch"].shape==(1,200,NUM_PITCHES)
    loss,parts=v6_sequence_loss(o,y); assert torch.isfinite(loss)
    loss.backward()
    for name in ("onset_head","activity_head","pitch_head","event_head","state_head"):
        mod=getattr(m,name); grads=[p.grad for p in mod.parameters() if p.requires_grad]
        assert grads and all(g is not None and torch.all(torch.isfinite(g)) for g in grads)
    assert all(torch.isfinite(v) for v in parts.values())
    print("V6_SHAPES_GRADIENTS_PASS")

def check_temporal(root):
    setup();m,_=new(root);m.eval();x,_=batch();a=x[:,:6].clone();b=a.clone();b[:,0]+=0.25
    with torch.no_grad(): oa=m(a)["event"];ob=m(b)["event"]
    assert torch.max(torch.abs(oa[:,1]-ob[:,1])).item()>1e-10
    print("V6_TEMPORAL_CONTEXT_PASS")

def check_decoder():
    state=np.zeros((8,NUM_STRINGS,NUM_CLASSES));state[...,20]=1.0
    event=np.zeros((8,NUM_STRINGS));act=np.zeros((8,NUM_STRINGS))
    for t in range(2,7):
        state[t,0,:]=0;state[t,0,20]=0.1;state[t,0,4]=0.9;act[t,0]=0.9
    assert count_active_runs(decode_v6(state,event,act))==0
    event[2,0]=0.9
    d=decode_v6(state,event,act)
    assert np.all(d[2:7,0]==4) and count_active_runs(d)==1
    print("V6_EVENT_ADMISSION_DECODER_PASS")

def nested(a,b):
    if torch.is_tensor(a): return torch.equal(a,b)
    if isinstance(a,np.ndarray): return np.array_equal(a,b)
    if isinstance(a,dict): return a.keys()==b.keys() and all(nested(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)): return len(a)==len(b) and all(nested(x,y) for x,y in zip(a,b))
    return a==b

def rng(): return {"py":random.getstate(),"np":np.random.get_state(),"torch":torch.get_rng_state().clone()}
def restore(r): random.setstate(r["py"]);np.random.set_state(r["np"]);torch.set_rng_state(r["torch"])
def clone(sd): return {k:v.detach().cpu().clone() for k,v in sd.items()}

def check_resume(root):
    x,y=batch()
    def step(m,o):
        o.zero_grad(set_to_none=True);loss,_=v6_sequence_loss(m(x),y);loss.backward();o.step()
    setup();a,ao=new(root)
    for _ in range(4):step(a,ao)
    am=clone(a.state_dict());aos=copy.deepcopy(ao.state_dict());ar=rng()
    setup();b,bo=new(root)
    for _ in range(2):step(b,bo)
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"v6.pt";torch.save({"m":clone(b.state_dict()),"o":bo.state_dict(),"r":rng()},p)
        setup();c,co=new(root);z=torch.load(p,map_location="cpu");c.load_state_dict(z["m"]);co.load_state_dict(z["o"]);restore(z["r"])
        for _ in range(2):step(c,co)
    assert nested(am,c.state_dict()) and nested(aos,co.state_dict()) and nested(ar,rng())
    print("V6_RESUME_DETERMINISM_PASS")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source-root",required=True);a=ap.parse_args()
    check_shapes(a.source_root);check_temporal(a.source_root);check_decoder();check_resume(a.source_root)
    print("V6_SYNTHETIC_VERIFICATION_PASS")
if __name__=="__main__":main()
