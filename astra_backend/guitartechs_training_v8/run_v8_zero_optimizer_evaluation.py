#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np, torch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from guitartechs_real_training import real_training as base
from guitartechs_training_v7.model import NUM_CLASSES,NUM_STRINGS,TemporalTabCNNV7
from guitartechs_training_v8.decoder import decode_v8_hybrid

CANDIDATE="astra_guitartechs_tabcnn_v7_ranked_event_transition"

def load(path,fold,root):
 p=torch.load(path,map_location="cpu")
 if p.get("candidateId")!=CANDIDATE or p.get("fold")!=fold:raise RuntimeError("identity")
 m=TemporalTabCNNV7(root);m.load_state_dict(p["stateDict"]);return m

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
 return decode_v8_hybrid(state,event)

def aggregate(caps):
 per=defaultdict(list)
 for c in caps:per[c["performance"]].append(c)
 rows=[];fields=("precision","recall","f1","completeness","frameAccuracy","abstentionRate")
 for k,v in sorted(per.items()):
  r={"performance":k,"category":v[0]["category"]}
  for f in fields:r[f]=float(np.mean([x[f] for x in v]))
  rows.append(r)
 out={f:float(np.mean([x[f] for x in rows])) for f in fields}
 out["performanceCount"]=len(rows);out["captureCount"]=len(caps)
 return out

def eval_fold(rows,m,perf):
 caps=[]
 for row in [r for r in rows if r["performer"]==perf]:
  feat=np.load(row["_features"],mmap_mode="r");ref=np.load(row["_labels"],mmap_mode="r")
  pred=infer(m,feat)
  mm=base.capture_metrics(pred,ref);mm.update({"performance":row["performer"]+"|"+row["category"]+"|"+row["performanceKey"],"category":row["category"]})
  caps.append(mm)
 return aggregate(caps)

def main():
 p=argparse.ArgumentParser()
 for n in ("source-root","manifest","data-dir","p1-model","p2-model","out"):p.add_argument("--"+n,required=True)
 a=p.parse_args();torch.use_deterministic_algorithms(True);torch.set_num_threads(4)
 rows=base.load_manifest(a.manifest,a.data_dir)
 if len(rows)!=256:raise RuntimeError("expected 256")
 p1=load(a.p1_model,"p1-train-p2-validate",a.source_root)
 p2=load(a.p2_model,"p2-train-p1-validate",a.source_root)
 folds={"p1-train-p2-validate":eval_fold(rows,p1,"P2"),"p2-train-p1-validate":eval_fold(rows,p2,"P1")}
 macro_f1=sum(x["f1"] for x in folds.values())/2
 macro_c=sum(x["completeness"] for x in folds.values())/2
 out={"schema":"astra-guitar-techs-v8-zero-optimizer-evaluation-v1","folds":folds,"aggregate":{"macroF1":macro_f1,"macroCompleteness":macro_c},"guards":{"optimizerStepsExecuted":0,"modelWeightsModified":False,"thresholdsRetuned":False,"p3Opened":False,"protectedSongUsed":False}}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("V8_ZERO_OPTIMIZER_EVALUATION_PASS")
 print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
