"""Bounded H1 loss-normalization pilot core; copied execution semantics from frozen V9."""
import hashlib
import json
import math
import time
from collections import defaultdict
import numpy as np
import torch
from guitartechs_training_v9 import train_v9_resumable as v9
from guitartechs_training_v9.paired_view import paired_tensor_views,symmetric_kl_consistency
from guitartechs_training_v7.objective_decoder import v7_sequence_loss
from guitartechs_training_v9.post_v9_output_admission_audit_v1 import infer_raw,summarize_capture,aggregate
from guitartechs_real_training import real_training as metric_base

EPOCHS=20
SEED=20260921
KL_WEIGHT=0.10
CWEIGHTS={"stateCE":1.0,"continuity":.10,"identityMargin":.25,"activity":.25,"pitch":.20,"eventRank":.60}
GROUPS=("conv","acoustic","temporal","routing","state_head")
FOLDS=(
 ("p1-train-p2-validate","P1","P2",41,120,40,"933c5faedafa4b3ddfb37e0ad87cef639294a99ff29acd6d581f622ed64a966e"),
 ("p2-train-p1-validate","P2","P1",40,136,41,"56b275d79426f5dd14641c0f3ffd802491734dd4f2ec9110a75616b861588a01"),
)


def losses(outputs_a,outputs_b,labels,content_weight,normalized):
    a,parts_a=v7_sequence_loss(outputs_a,labels,content_weight=content_weight)
    b,parts_b=v7_sequence_loss(outputs_b,labels,content_weight=content_weight)
    sup=(a+b)*.5
    bs,t=outputs_a["tablature"].shape[:2]
    assert bs==1 and t==200
    left=outputs_a["tablature"].reshape(bs,t,6,21)
    right=outputs_b["tablature"].reshape(bs,t,6,21)
    raw=symmetric_kl_consistency(left,right)
    weighted=KL_WEIGHT*raw/(1200 if normalized else 1)
    return sup,raw,weighted,{k:.5*(parts_a[k]+parts_b[k]) for k in CWEIGHTS}


def probe(model,sup,weighted):
    named=list(model.named_parameters())
    pars=tuple(p for _,p in named)
    g1=torch.autograd.grad(sup,pars,retain_graph=True,allow_unused=True)
    g2=torch.autograd.grad(weighted,pars,retain_graph=True,allow_unused=True)
    out={}
    for group in GROUPS:
        s=k=0.0
        for (name,_), a,b in zip(named,g1,g2):
            if name.startswith(group+"."):
                if a is not None: s+=float(a.detach().double().square().sum())
                if b is not None: k+=float(b.detach().double().square().sum())
        a,b=math.sqrt(s),math.sqrt(k)
        out[group]={"supervisedGradientL2":a,"weightedKLGradientL2":b,
                    "klToSupervisedRatio":b/a if a else None}
    return out


def train_arm(rows,fold,arm,source_root,control_sha,before_step=None,on_step=None):
    if arm not in ("original_batchmean","per_position_normalized"):
        raise ValueError("unregistered arm")
    v9._setup_determinism()
    model,opt=v9._new_model_and_optimizer(source_root)
    initial=v9.base.state_sha256(model)
    bykey={r["key"]:r for r in rows}
    weights=v9._training_content_weights(rows)
    groups=len({(r["performer"],r["category"],r["performanceKey"]) for r in rows})
    assert groups in (40,41)
    history=[]
    first_grad=None
    steps=0
    start=time.monotonic()
    for epoch in range(EPOCHS):
        plan=v9.build_epoch_plan(rows,epoch=epoch)
        if len(plan)!=groups: raise RuntimeError("training plan group drift")
        batches=v9.batch_epoch_plan(plan,batch_size=32)
        if len(batches)!=2: raise RuntimeError('H1_EXPECTED_TWO_BATCHES_PER_EPOCH')
        stats=defaultdict(list)
        model.train()
        for batch in batches:
            opt.zero_grad(set_to_none=True)
            for item in batch:
                x,y=v9.base._sequence_tensors(bykey,item)
                w=weights[v9._content_name(bykey[item["captureKey"]]["category"])]
                salt=json.dumps({"epoch":epoch,"item":item},sort_keys=True).encode()
                seed=int(hashlib.sha256(salt).hexdigest()[:16],16)
                aa,bb=paired_tensor_views(x,seed)
                oa,ob=model(aa),model(bb)
                sup,raw,cons,parts=losses(oa,ob,y,w,arm=="per_position_normalized")
                loss=sup+cons
                if not torch.isfinite(loss): raise RuntimeError("nonfinite H1 pilot loss")
                if first_grad is None: first_grad=probe(model,sup,cons)
                (loss/len(batch)).backward()
                for k,t in (("supervised",sup),("rawBatchmeanKL",raw),
                            ("weightedKL",cons),("total",loss)):
                    stats[k].append(float(t.detach()))
                for k,p in parts.items():
                    stats["component_"+k].append(float(p.detach()))
            if before_step is not None: before_step()
            opt.step()
            steps+=1
            if on_step is not None: on_step(fold,arm,epoch+1,steps)
        row={"epoch":epoch+1,"steps":steps,"means":{
            k:float(np.mean(vals)) for k,vals in sorted(stats.items())}}
        if not all(math.isfinite(v) for v in row["means"].values()):
            raise RuntimeError("nonfinite telemetry")
        history.append(row)
        if epoch+1 in (1,5,10,15,20):
            print("H1_EPOCH="+json.dumps({"fold":fold,"arm":arm,**row},sort_keys=True),flush=True)
    if steps!=40: raise RuntimeError("not exact 40 optimizer steps")
    digest=v9.base.state_sha256(model)
    if arm=="original_batchmean" and digest!=control_sha:
        raise RuntimeError("ORIGINAL_EPOCH20_SHA_REPRODUCTION_FAILED")
    return model,{
        "arm":arm,"epoch20Sha256":digest,"initialStateSha256":initial,
        "matchesFrozenOriginalEpoch20":digest==control_sha,
        "steps":steps,"epochs":EPOCHS,"wallSeconds":float(time.monotonic()-start),
        "trainingWeights":weights,"firstMicrobatchGradients":first_grad,"epochTelemetry":history}


def evaluate(model,rows,expected_captures,expected_performances):
    caps=[]
    model.eval()
    for row in rows:
        feature=np.load(row["_features"],mmap_mode="r",allow_pickle=False)
        ref=np.load(row["_labels"],mmap_mode="r",allow_pickle=False)
        state,event=infer_raw(model,feature)
        predicted,info=summarize_capture(state,event,ref)
        met=metric_base.capture_metrics(predicted,ref)
        if not all(k in met and math.isfinite(float(met[k])) for k in
                   ('precision','recall','f1','completeness','frameAccuracy','abstentionRate')):
            raise RuntimeError('H1_NONFINITE_OR_MISSING_CAPTURE_METRICS')
        if any(not isinstance(info.get(k),int) or info[k]<0 for k in
               ('predictedEvents','referenceEvents','truePositiveEvents','activeRunsAfterPrune')):
            raise RuntimeError('H1_INVALID_EVENT_COUNTER_SCHEMA')
        if info['truePositiveEvents']>min(info['predictedEvents'],info['referenceEvents']):
            raise RuntimeError('H1_IMPOSSIBLE_EVENT_COUNTS')
        caps.append({"_performance":row["performer"]+"|"+row["category"]+"|"+row["performanceKey"],
                     "_category":row["category"],"metrics":met,"audit":info})
    summary=aggregate(caps)
    if summary["captureCount"]!=expected_captures or summary["performanceCount"]!=expected_performances:
        raise RuntimeError("validation capture/performance count drift")
    if not all(k in summary and math.isfinite(float(summary[k])) for k in
               ('precision','recall','f1','completeness','frameAccuracy','abstentionRate')):
        raise RuntimeError('H1_NONFINITE_OR_MISSING_MACRO_METRICS')
    fields=("predictedEvents","referenceEvents","truePositiveEvents","stateArgmaxActivePositions",
            "activeRunsBeforeGapMerge","activeRunsAfterPrune","strongStartCandidates",
            "confirmedStartCandidates","acceptedStrongStarts","acceptedConfirmedStarts")
    return {"metrics":summary,"totals":{k:sum(c["audit"][k] for c in caps) for k in fields}}
