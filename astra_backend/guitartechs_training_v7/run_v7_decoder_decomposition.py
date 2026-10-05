#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np, torch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from guitartechs_real_training import real_training as base
from guitartechs_training_v7.model import NUM_CLASSES,NUM_STRINGS,TemporalTabCNNV7
from guitartechs_training_v7.objective_decoder import decode_ranked_events
from guitartechs_training_v4.objective_decoder import decode_with_hysteresis

CANDIDATE="astra_guitartechs_tabcnn_v7_ranked_event_transition"

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1024*1024),b""):h.update(c)
 return h.hexdigest()

def load_model(path,expected,fold,root):
 if sha(path)!=expected:raise RuntimeError("model sha mismatch")
 p=torch.load(path,map_location="cpu")
 if p.get("candidateId")!=CANDIDATE or p.get("fold")!=fold:raise RuntimeError("identity mismatch")
 m=TemporalTabCNNV7(root);m.load_state_dict(p["stateDict"])
 if base.state_sha256(m)!=p["stateSha256"]:raise RuntimeError("state hash mismatch")
 return m

def infer(m,feat,chunk=512):
 pad=np.pad(feat,((0,0),(base.HALF_CONTEXT,base.HALF_CONTEXT)))
 w=np.lib.stride_tricks.sliding_window_view(pad,base.FRAME_CONTEXT,axis=1).transpose(1,0,2)
 T=feat.shape[1]
 state=np.empty((T,NUM_STRINGS,NUM_CLASSES),np.float32)
 event=np.empty((T,NUM_STRINGS),np.float32)
 hidden=None;m.eval()
 with torch.no_grad():
  for lo in range(0,T,chunk):
   hi=min(T,lo+chunk);x=np.ascontiguousarray(w[lo:hi])[None,:,None,:,:]
   o=m(torch.from_numpy(x),hidden);hidden=o["hidden"].detach()
   state[lo:hi]=torch.softmax(o["tablature"].reshape(1,hi-lo,NUM_STRINGS,NUM_CLASSES),-1)[0].cpu().numpy()
   event[lo:hi]=o["event"][0].cpu().numpy()
 return state,event

def state_relative(state):
 best=np.argmax(state,axis=-1).astype(np.int16)
 best[best==20]=-1
 return best

def aggregate(caps):
 per=defaultdict(list)
 for c in caps:per[c["performance"]].append(c)
 rows=[];fields=("precision","recall","f1","completeness","frameAccuracy","abstentionRate")
 for key,v in sorted(per.items()):
  r={"performance":key,"category":v[0]["category"]}
  for f in fields:r[f]=float(np.mean([x[f] for x in v]))
  rows.append(r)
 out={f:float(np.mean([x[f] for x in rows])) for f in fields}
 out["performanceCount"]=len(rows);out["captureCount"]=len(caps)
 return out

def ref_onsets(ref):
 x=ref.T;valid=x!=base.MASK;active=valid&(x>=0);on=np.zeros_like(valid,bool)
 if len(x)>1:
  ok=valid[1:]&valid[:-1]
  on[1:]=ok&active[1:]&((~active[:-1])|(x[1:]!=x[:-1]))
 return x,on

def rank_stats(event,ref):
 rs,on=ref_onsets(ref);vals=[];ranks=[]
 T,S=event.shape
 for t,s in np.argwhere(on):
  lo=max(0,t-2);hi=min(T,t+3);win=event[lo:hi,s]
  vals.append(float(event[t,s]))
  ranks.append(1+int(np.sum(win>event[t,s])))
 return vals,ranks

def diagnose(rows,m,perf):
 buckets={k:[] for k in ("ranked","stateRelative","v4Hysteresis")}
 ranks=[];scores=[]
 for row in [r for r in rows if r["performer"]==perf]:
  feat=np.load(row["_features"],mmap_mode="r");ref=np.load(row["_labels"],mmap_mode="r")
  state,event=infer(m,feat)
  preds={"ranked":decode_ranked_events(state,event),"stateRelative":state_relative(state),"v4Hysteresis":decode_with_hysteresis(state)}
  meta={"performance":row["performer"]+"|"+row["category"]+"|"+row["performanceKey"],"category":row["category"]}
  for k,p in preds.items():
   mm=base.capture_metrics(p,ref);mm.update(meta);buckets[k].append(mm)
  v,rk=rank_stats(event,ref);scores.extend(v);ranks.extend(rk)
 return {
  "decoders":{k:aggregate(v) for k,v in buckets.items()},
  "trueEventLocalRank":{"count":len(ranks),"rank1Rate":float(np.mean(np.array(ranks)==1)) if ranks else 0.0,"meanRank":float(np.mean(ranks)) if ranks else None}
 }

def main():
 p=argparse.ArgumentParser()
 for n in ("source-root","manifest","data-dir","p1-model","p2-model","out"):p.add_argument("--"+n,required=True)
 a=p.parse_args();torch.use_deterministic_algorithms(True);torch.set_num_threads(4)
 rows=base.load_manifest(a.manifest,a.data_dir)
 if len(rows)!=256:raise RuntimeError("expected 256")
 p1=load_model(a.p1_model,"072fb49ac8112d65df2d11a0110535d675cafc4b9c04631fd2d0a9eeafcd0763","p1-train-p2-validate",a.source_root)
 p2=load_model(a.p2_model,"566a4f2d7e4d97e0b93ffe1662b921d8e0e75066540a8a5f1e683f5a6498d596","p2-train-p1-validate",a.source_root)
 out={"schema":"astra-guitar-techs-v7-decoder-decomposition-v1","folds":{
  "p1-train-p2-validate":diagnose(rows,p1,"P2"),
  "p2-train-p1-validate":diagnose(rows,p2,"P1")},
  "guards":{"optimizerStepsExecuted":0,"thresholdsRetuned":False,"p3Opened":False,"protectedSongUsed":False}}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("V7_DECODER_DECOMPOSITION_PASS")
 print(json.dumps(out["folds"],sort_keys=True))
if __name__=="__main__":main()
