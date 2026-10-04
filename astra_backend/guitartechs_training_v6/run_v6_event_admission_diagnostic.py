#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import torch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))

from guitartechs_real_training import real_training as base
from guitartechs_training_v6.model import NUM_CLASSES,NUM_FRETS,NUM_PITCHES,NUM_STRINGS,SILENCE_CLASS,TemporalTabCNNV6
from guitartechs_training_v6.objective_decoder import (
    EVENT_START_CONFIDENCE,ACTIVITY_CONTINUE_CONFIDENCE,STATE_START_CONFIDENCE,
    STATE_CONTINUE_CONFIDENCE,STATE_START_VS_SILENCE_RATIO,STATE_CONTINUE_VS_SILENCE_RATIO,
    GAP_FRAMES,MIN_RUN_FRAMES,_merge_short_gaps,_prune,decode_v6
)

CANDIDATE="astra_guitartechs_tabcnn_v6_learned_event_admission"
RUN_ID=37167968302
BINS=100

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for ch in iter(lambda:f.read(1024*1024),b""): h.update(ch)
    return h.hexdigest()

def content_name(c): return "PalmMute" if c=="techniques" else c

def load_model(path,expected_sha,fold,source_root):
    if sha(path)!=expected_sha: raise RuntimeError(f"model sha mismatch {fold}")
    p=torch.load(path,map_location="cpu")
    if p.get("candidateId")!=CANDIDATE or p.get("fold")!=fold: raise RuntimeError("model identity mismatch")
    m=TemporalTabCNNV6(source_root); m.load_state_dict(p["stateDict"])
    if base.state_sha256(m)!=p.get("stateSha256"): raise RuntimeError("state sha mismatch")
    return m

def infer(m,feat,chunk=512):
    pad=np.pad(feat,((0,0),(base.HALF_CONTEXT,base.HALF_CONTEXT)))
    windows=np.lib.stride_tricks.sliding_window_view(pad,base.FRAME_CONTEXT,axis=1).transpose(1,0,2)
    T=feat.shape[1]
    state=np.empty((T,NUM_STRINGS,NUM_CLASSES),np.float32)
    event=np.empty((T,NUM_STRINGS),np.float32)
    activity=np.empty((T,NUM_STRINGS),np.float32)
    onset=np.empty((T,NUM_STRINGS),np.float32)
    pitch=np.empty((T,NUM_PITCHES),np.float32)
    hidden=None;m.eval()
    with torch.no_grad():
        for lo in range(0,T,chunk):
            hi=min(T,lo+chunk); w=np.ascontiguousarray(windows[lo:hi])[None,:,None,:,:]
            o=m(torch.from_numpy(w),hidden); hidden=o["hidden"].detach()
            state[lo:hi]=torch.softmax(o["tablature"].reshape(1,hi-lo,NUM_STRINGS,NUM_CLASSES),-1)[0].cpu().numpy()
            event[lo:hi]=torch.sigmoid(o["event"])[0].cpu().numpy()
            activity[lo:hi]=torch.sigmoid(o["activity"])[0].cpu().numpy()
            onset[lo:hi]=torch.sigmoid(o["onset"])[0].cpu().numpy()
            pitch[lo:hi]=torch.sigmoid(o["pitch"])[0].cpu().numpy()
    return state,event,activity,onset,pitch

def ref_onsets(ref):
    x=ref.T; valid=x!=base.MASK; active=valid&(x>=0)
    onset=np.zeros_like(valid,bool)
    if len(x)>1:
        ok=valid[1:]&valid[:-1]
        onset[1:]=ok&active[1:]&((~active[:-1])|(x[1:]!=x[:-1]))
    return x,valid,active,onset

def hist_add(h,scores,pos):
    idx=np.minimum(BINS-1,np.floor(np.clip(scores,0,1)*BINS).astype(int))
    if np.any(pos): h["pos"]+=np.bincount(idx[pos],minlength=BINS)
    if np.any(~pos): h["neg"]+=np.bincount(idx[~pos],minlength=BINS)

def hist_finish(h):
    pos=h["pos"].astype(float);neg=h["neg"].astype(float)
    pt,nt=pos.sum(),neg.sum();tp=np.cumsum(pos[::-1]);fp=np.cumsum(neg[::-1])
    tpr=tp/pt if pt else np.zeros_like(tp);fpr=fp/nt if nt else np.zeros_like(fp)
    return {"positiveCount":int(pt),"negativeCount":int(nt),"approxAUROC100Bins":float(np.trapz(tpr,fpr)) if pt and nt else None}

def decode_ablation(state,event,activity,use_event,use_state):
    T=state.shape[0];out=np.full((T,NUM_STRINGS),-1,np.int16)
    for s in range(NUM_STRINGS):
        cur=-1
        for t in range(T):
            row=state[t,s];sil=float(row[SILENCE_CLASS]);best=int(np.argmax(row[:NUM_FRETS]));bp=float(row[best])
            gates=[]
            if use_event:gates.append(event[t,s]>=EVENT_START_CONFIDENCE)
            if use_state:gates.append(bp>=STATE_START_CONFIDENCE and bp>=sil*STATE_START_VS_SILENCE_RATIO)
            can=all(gates) if gates else True
            if cur>=0:
                if can and best!=cur:
                    cur=best;out[t,s]=cur;continue
                keep=float(row[cur])
                if activity[t,s]>=ACTIVITY_CONTINUE_CONFIDENCE and keep>=STATE_CONTINUE_CONFIDENCE and keep>=sil*STATE_CONTINUE_VS_SILENCE_RATIO:
                    out[t,s]=cur;continue
                cur=-1
            if can: cur=best;out[t,s]=cur
        out[:,s]=_prune(_merge_short_gaps(out[:,s],GAP_FRAMES),MIN_RUN_FRAMES)
    return out

def aggregate(caps):
    per=defaultdict(list)
    for c in caps: per[c["performance"]].append(c)
    rows=[]
    fields=("precision","recall","f1","completeness","frameAccuracy","abstentionRate")
    for key,views in sorted(per.items()):
        r={"performance":key,"category":views[0]["category"]}
        for f in fields:r[f]=float(np.mean([v[f] for v in views]))
        rows.append(r)
    out={f:float(np.mean([r[f] for r in rows])) for f in fields}
    out["contentF1"]={}
    for cat in ("chords","scales","singlenotes","techniques"):
        vals=[r["f1"] for r in rows if r["category"]==cat]
        out["contentF1"][content_name(cat)]=float(np.mean(vals)) if vals else 0.0
    out["performanceCount"]=len(rows);out["captureCount"]=len(caps)
    return out

def assert_metrics(a,e,tol=1e-12):
    for f in ("precision","recall","f1","completeness","frameAccuracy","abstentionRate"):
        if abs(float(a[f])-float(e[f]))>tol: raise RuntimeError(f"metric mismatch {f}: {a[f]} != {e[f]}")

def diagnose(rows,m,performer,expected):
    caps_full=[];caps_noevent=[];caps_eventonly=[];gate={"referenceOnsets":0,"eventPass":0,"statePass":0,"eventStatePass":0,"identityCorrect":0}
    eh={"pos":np.zeros(BINS,np.int64),"neg":np.zeros(BINS,np.int64)}
    oh={"pos":np.zeros(BINS,np.int64),"neg":np.zeros(BINS,np.int64)}
    ah={"pos":np.zeros(BINS,np.int64),"neg":np.zeros(BINS,np.int64)}
    for row in [r for r in rows if r["performer"]==performer]:
        feat=np.load(row["_features"],mmap_mode="r");ref=np.load(row["_labels"],mmap_mode="r")
        state,event,activity,onset,pitch=infer(m,feat)
        preds={"full":decode_v6(state,event,activity),"noEvent":decode_ablation(state,event,activity,False,True),"eventOnly":decode_ablation(state,event,activity,True,False)}
        meta={"performance":row["performer"]+"|"+row["category"]+"|"+row["performanceKey"],"category":row["category"]}
        for name,target in (("full",caps_full),("noEvent",caps_noevent),("eventOnly",caps_eventonly)):
            mm=base.capture_metrics(preds[name],ref);mm.update(meta);target.append(mm)
        rs,valid,active,ons=ref_onsets(ref)
        hist_add(eh,event[valid],ons[valid]);hist_add(oh,onset[valid],ons[valid]);hist_add(ah,activity[valid],active[valid])
        for t,s in np.argwhere(ons):
            fret=int(rs[t,s]);rowp=state[t,s];sil=float(rowp[SILENCE_CLASS]);best=int(np.argmax(rowp[:NUM_FRETS]));bp=float(rowp[best])
            ep=event[t,s]>=EVENT_START_CONFIDENCE
            sp=bp>=STATE_START_CONFIDENCE and bp>=sil*STATE_START_VS_SILENCE_RATIO
            gate["referenceOnsets"]+=1;gate["eventPass"]+=int(ep);gate["statePass"]+=int(sp);gate["eventStatePass"]+=int(ep and sp);gate["identityCorrect"]+=int(best==fret)
    full=aggregate(caps_full);assert_metrics(full,expected)
    n=gate["referenceOnsets"]
    gate.update({k+"Rate":v/n for k,v in list(gate.items()) if k!="referenceOnsets"})
    return {"frozenMetricReproduction":{"passed":True,"metrics":full},"headDiscrimination":{"event":hist_finish(eh),"onset":hist_finish(oh),"activity":hist_finish(ah)},"trueOnsetGate":gate,"ablations":{"full":full,"stateOnlyStart":aggregate(caps_noevent),"eventOnlyStart":aggregate(caps_eventonly)}}

def main():
    p=argparse.ArgumentParser()
    for n in ("source-root","manifest","data-dir","p1-model","p1-result","p2-model","p2-result","out"):p.add_argument("--"+n,required=True)
    a=p.parse_args();torch.use_deterministic_algorithms(True);torch.set_num_threads(4)
    rows=base.load_manifest(a.manifest,a.data_dir)
    if len(rows)!=256:raise RuntimeError("expected 256 captures")
    specs=[
      ("p1-train-p2-validate","P2",a.p1_model,a.p1_result,"14cdacbd6b5bc282bc6bf3fb55e9b43b3781c740a27a6ca470d7ea2a4605dfcb","3a3603a744f74cf34af022513cd46fc941684adb605b40c2917017a39b67c6b0"),
      ("p2-train-p1-validate","P1",a.p2_model,a.p2_result,"e3b72e30934ee334bd2dd131f4b1c8faae2179d98b42a5ec2effc0fc7962ed11","4cd24c1a98f5aa44e81c62a094f0e59a3b5515675b673e1e0a33b06523d7618e")
    ]
    folds={}
    for fold,perf,mp,rp,rsha,msha in specs:
        if sha(rp)!=rsha:raise RuntimeError("result sha mismatch")
        tr=json.load(open(rp))
        if tr["fold"]!=fold or tr["candidateId"]!=CANDIDATE:raise RuntimeError("receipt identity mismatch")
        m=load_model(mp,msha,fold,a.source_root)
        folds[fold]=diagnose(rows,m,perf,tr["fullValidationMetrics"])
    out={"schema":"astra-guitar-techs-v6-event-admission-diagnostic-v1","sourceRunId":RUN_ID,"candidateId":CANDIDATE,"folds":folds,
         "guards":{"optimizerStepsExecuted":0,"modelWeightsModified":False,"thresholdsRetuned":False,"p3Opened":False,"protectedSongUsed":False,"mainOrProductionModified":False}}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V6_EVENT_ADMISSION_DIAGNOSTIC_PASS")
    print(json.dumps(folds,sort_keys=True))
if __name__=="__main__":main()
