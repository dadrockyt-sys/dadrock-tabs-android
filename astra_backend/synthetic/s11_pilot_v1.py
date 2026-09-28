#!/usr/bin/env python3
"""Astra S11 multi-seed robustness confirmation for S9 chord diversity."""
from __future__ import annotations
import argparse, hashlib, json, math, os, random, time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from synthetic.s0_pilot_v1 import (
    ROOT_SEED, MAX_STEPS, NUM_STRINGS, NUM_CLASSES, SILENCE_CLASS,
    STATE_ACTIVE_THRESHOLD, ONSET_THRESHOLD, LEARNING_RATE,
    context5, evaluate_model,
)
from synthetic.s1_pilot_v1 import build_sampling_strata
from synthetic.s2_pilot_v1 import dataset_array_hashes, state_admission_diagnostics, array_content_sha256
from synthetic.s3_pilot_v1 import repeated_reference_diagnostics

SCHEMA="astra-synthetic-data-diversity-s11-pilot-v1"
RUN_SEEDS=(20260927,20260928,20260929)
STATE_ACTIVE_WEIGHT=9.0
ONSET_POS_WEIGHT=8.0
ONSET_LOSS_WEIGHT=4.0
MAX_TOTAL_STEPS=3000

class S11Model(nn.Module):
    def __init__(self,input_dim):
        super().__init__()
        self.encoder=nn.Sequential(nn.Linear(input_dim,128),nn.ReLU())
        self.state_head=nn.Sequential(
            nn.Linear(128,128),
            nn.ReLU(),
            nn.Linear(128,NUM_STRINGS*NUM_CLASSES),
        )
        self.onset_head=nn.Linear(128,NUM_STRINGS)

    def forward(self,x):
        h=self.encoder(x)
        return self.state_head(h),self.onset_head(h)

def _set_seed(seed):
    random.seed(int(seed))
    np.random.seed(int(seed))
    torch.manual_seed(int(seed))
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))

def module_sha(model):
    h=hashlib.sha256()
    for n,t in sorted(model.state_dict().items()):
        h.update(n.encode()); h.update(b"\0")
        h.update(np.ascontiguousarray(t.detach().cpu().numpy()).tobytes())
    return h.hexdigest()

def initialize_model(run_seed,input_dim):
    _set_seed(run_seed+11001)
    return S11Model(input_dim)

def paired_batches(state,onset,split,negative_structure,run_seed):
    strata=build_sampling_strata(state,onset,split,negative_structure)
    rng=np.random.RandomState(run_seed+7001)
    batches=[]
    for _ in range(MAX_STEPS):
        chunks=[
            rng.choice(strata["positiveOnset"],32,replace=True),
            rng.choice(strata["activeNonOnset"],32,replace=True),
            rng.choice(strata["negativeStructureInactive"],32,replace=True),
            rng.choice(strata["otherInactive"],32,replace=True),
        ]
        idx=np.concatenate(chunks)
        batches.append(idx[rng.permutation(len(idx))].astype(np.int64,copy=False))
    return np.stack(batches),{k:int(len(v)) for k,v in strata.items()}

def batch_sha(x):
    return array_content_sha256(np.asarray(x,dtype=np.int64))

def weighted_loss(state_logits,onset_logits,state_target,onset_target):
    target=state_target.clone()
    target[target==-1]=SILENCE_CLASS
    raw=F.cross_entropy(
        state_logits.reshape(-1,NUM_CLASSES),
        target.reshape(-1),
        reduction="none",
    ).reshape(-1,NUM_STRINGS)
    weights=torch.ones_like(raw)
    weights[target!=SILENCE_CLASS]=STATE_ACTIVE_WEIGHT
    state_loss=(raw*weights).sum()/weights.sum()
    onset_loss=F.binary_cross_entropy_with_logits(
        onset_logits,onset_target.float(),
        pos_weight=torch.tensor(ONSET_POS_WEIGHT,dtype=onset_logits.dtype),
    )
    return state_loss+ONSET_LOSS_WEIGHT*onset_loss

def fit(model,features,state,onset,batches,deadline):
    xf=context5(features).reshape(-1,960)
    sf=state.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    of=onset.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    opt=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)
    started=time.monotonic(); steps=0; stop="requested_steps_reached"
    for step in range(MAX_STEPS):
        if time.monotonic()>=deadline:
            stop="fit_eval_time_ceiling"; break
        idx=batches[step]
        xb=torch.from_numpy(xf[idx]).float()
        sb=torch.from_numpy(sf[idx]).long()
        ob=torch.from_numpy(of[idx]).long()
        opt.zero_grad(set_to_none=True)
        sl,ol=model(xb)
        loss=weighted_loss(sl,ol,sb,ob)
        if not torch.isfinite(loss): raise RuntimeError("nonfinite S11 loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise RuntimeError("nonfinite S11 gradient")
        opt.step(); steps+=1
    return {"optimizerSteps":steps,"requestedSteps":MAX_STEPS,"elapsedSeconds":time.monotonic()-started,"stopReason":stop}

def evaluate(model,d,split_name):
    features=d["features"].astype(np.float32,copy=False)
    base=evaluate_model(
        model,features,d["state"],d["onset"],d["family"],
        np.where(d["split"]==split_name,"test","other"),
        d["negative_only"],d["refs_json"],5
    )
    base["admission"]=state_admission_diagnostics(model,features,d["state"],d["onset"],d["split"],split_name)
    base["repeatedReferenceOnset"]=repeated_reference_diagnostics(model,features,d["state"],d["onset"],d["split"],split_name)
    return base

def run_pair(control,intervention,run_seed,deadline):
    cb,cstrata=paired_batches(control["state"],control["onset"],control["split"],control["has_negative_structure"],run_seed)
    ib,istrata=paired_batches(intervention["state"],intervention["onset"],intervention["split"],intervention["has_negative_structure"],run_seed)
    if cstrata!=istrata or not np.array_equal(cb,ib):
        raise RuntimeError("paired S11 batches differ")

    cf=context5(control["features"].astype(np.float32,copy=False)).reshape(-1,960)
    cmodel=initialize_model(run_seed,960)
    imodel=initialize_model(run_seed,960)
    if module_sha(cmodel)!=module_sha(imodel):
        raise RuntimeError("paired S11 initialization differs")
    x=torch.from_numpy(cf[cb[0]]).float()
    with torch.no_grad():
        cs,co=cmodel(x); is_,io=imodel(x)
    if not torch.equal(cs,is_) or not torch.equal(co,io):
        raise RuntimeError("paired S11 pre-update logits differ")

    cfit=fit(cmodel,control["features"].astype(np.float32,copy=False),control["state"],control["onset"],cb,deadline)
    ifit=fit(imodel,intervention["features"].astype(np.float32,copy=False),intervention["state"],intervention["onset"],ib,deadline)

    ct=evaluate(cmodel,control,"test")
    it=evaluate(imodel,intervention,"test")
    return {
      "runSeed":run_seed,
      "modelInitSha256":module_sha(initialize_model(run_seed,960)),
      "batchPlanSha256":batch_sha(cb),
      "control":{"fit":cfit,"test":ct},
      "intervention":{"fit":ifit,"test":it},
      "delta":{
        "chordF1":it["familyPitchOnset"]["chords"]["f1"]-ct["familyPitchOnset"]["chords"]["f1"],
        "chordRecall":it["familyPitchOnset"]["chords"]["recall"]-ct["familyPitchOnset"]["chords"]["recall"],
        "onsetF1":it["pitchOnset"]["f1"]-ct["pitchOnset"]["f1"],
        "onsetRecall":it["pitchOnset"]["recall"]-ct["pitchOnset"]["recall"],
        "precision":it["pitchOnset"]["precision"]-ct["pitchOnset"]["precision"],
        "jointAdmission":it["admission"]["jointAdmissionFraction"]-ct["admission"]["jointAdmissionFraction"],
        "stateAdmission":it["admission"]["stateAdmissionFraction"]-ct["admission"]["stateAdmissionFraction"],
      },
      "nonChordFamilyF1Loss":{
        f:ct["familyPitchOnset"][f]["f1"]-it["familyPitchOnset"][f]["f1"]
        for f in ct["familyPitchOnset"] if f!="chords"
      },
      "pairIdentity":{"initializationIdentical":True,"batchIndicesIdentical":True,"preUpdateLogitsIdentical":True},
    }

def summarize(vals):
    a=np.asarray(vals,dtype=float)
    return {"mean":float(a.mean()),"median":float(np.median(a)),"minimum":float(a.min()),"positiveCount":int(np.sum(a>0))}

def run(control_path,intervention_path,out):
    started=time.monotonic(); deadline=started+5400.0
    c=np.load(control_path,allow_pickle=False); i=np.load(intervention_path,allow_pickle=False)

    unchanged=~((c["family"]=="chords")&(c["split"]=="train"))
    heldout=(c["split"]!="train")
    for k in ("features","state","onset","refs_json","family","split","negative_only","has_negative_structure"):
        if not np.array_equal(c[k][unchanged],i[k][unchanged]):
            raise RuntimeError("S11 unchanged subset mismatch: "+k)
    for k in ("features","state","onset","refs_json"):
        if not np.array_equal(c[k][heldout],i[k][heldout]):
            raise RuntimeError("S11 heldout mismatch: "+k)

    pairs=[run_pair(c,i,s,deadline) for s in RUN_SEEDS]
    if len({p["modelInitSha256"] for p in pairs})!=3:
        raise RuntimeError("S11 run seeds did not produce distinct model initializations")
    if len({p["batchPlanSha256"] for p in pairs})!=3:
        raise RuntimeError("S11 run seeds did not produce distinct batch plans")

    summaries={k:summarize([p["delta"][k] for p in pairs]) for k in ("chordF1","chordRecall","onsetF1","onsetRecall","jointAdmission","stateAdmission","precision")}
    nonchord={}
    for fam in pairs[0]["nonChordFamilyF1Loss"]:
        losses=[p["nonChordFamilyF1Loss"][fam] for p in pairs]
        nonchord[fam]={"lossOver0_15Count":int(sum(x>.15 for x in losses)),"losses":losses}

    criteria={
      "chordF1GainPositive3of3":summaries["chordF1"]["positiveCount"]==3,
      "chordRecallGainPositive3of3":summaries["chordRecall"]["positiveCount"]==3,
      "onsetF1GainPositive3of3":summaries["onsetF1"]["positiveCount"]==3,
      "onsetRecallGainPositive3of3":summaries["onsetRecall"]["positiveCount"]==3,
      "meanChordF1GainAtLeast0_10":summaries["chordF1"]["mean"]>=.10,
      "meanChordRecallGainAtLeast0_12":summaries["chordRecall"]["mean"]>=.12,
      "meanOnsetF1GainAtLeast0_04":summaries["onsetF1"]["mean"]>=.04,
      "meanOnsetRecallGainAtLeast0_06":summaries["onsetRecall"]["mean"]>=.06,
      "meanJointAdmissionGainAtLeast0_03":summaries["jointAdmission"]["mean"]>=.03,
      "noSeedPrecisionLossOver0_05":all(p["delta"]["precision"]>=-.05 for p in pairs),
      "negativeOnlyFpAtMost0_10EverySeed":all(p["intervention"]["test"]["negativeOnlyFalsePositiveEventsPerSecond"]<=.10 for p in pairs),
      "nonChordFamilyLossOver0_15InAtMostOneSeed":all(v["lossOver0_15Count"]<=1 for v in nonchord.values()),
      "allSix500StepsFinitePairedFixedThresholds":(
        all(p["control"]["fit"]["optimizerSteps"]==500 and p["intervention"]["fit"]["optimizerSteps"]==500 for p in pairs)
        and all(all(p["pairIdentity"].values()) for p in pairs)
        and all(math.isfinite(float(v["mean"])) for v in summaries.values())
      ),
    }

    result={
      "schema":SCHEMA,
      "datasetRootSeed":ROOT_SEED,
      "runSeeds":list(RUN_SEEDS),
      "datasetIdentity":{"control":dataset_array_hashes(c),"intervention":dataset_array_hashes(i),"heldoutBitIdentical":True,"nonChordBitIdentical":True},
      "pairs":pairs,
      "pairedDeltaSummary":summaries,
      "nonChordFamilyStability":nonchord,
      "criteria":criteria,
      "s11GatePassed":all(criteria.values()),
      "execution":{"modelCount":6,"optimizerStepsTotal":sum(p["control"]["fit"]["optimizerSteps"]+p["intervention"]["fit"]["optimizerSteps"] for p in pairs),
                   "fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"thresholdSearch":False,"paidComputeDollars":0},
      "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False,"codespacesUsed":False,"vercelUsed":False,"productionMutation":False},
      "meaning":"Three-seed paired synthetic robustness confirmation of S9 chord-voicing diversity effect."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS: raise RuntimeError("S11 optimizer ceiling")
    print("S11_RESULT="+json.dumps(result,sort_keys=True))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--control-dataset",required=True); ap.add_argument("--intervention-dataset",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(); run(a.control_dataset,a.intervention_dataset,a.out)

if __name__=="__main__": main()
