#!/usr/bin/env python3
"""Astra Architecture Research A1: decoupled state/onset encoders.

New architecture project version. The only architectural change from S11 is
replacing one shared Linear(960,128)+ReLU encoder with two disjoint encoders,
one for state and one for onset.
"""
from __future__ import annotations

import argparse, hashlib, json, math, os, time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from synthetic.s0_pilot_v1 import NUM_STRINGS, NUM_CLASSES
from synthetic.s11_pilot_v1 import (
    RUN_SEEDS, paired_batches, batch_sha, fit, evaluate, weighted_loss
)

SCHEMA="astra-architecture-research-a1-result-v1"
EXPECTED_FILE_SHA256={
    "control":"16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894",
    "intervention":"a17a16daeb8d698e325dc6820f18d5eda2fec75d9beebe2a9605a678124dc26b",
    "challenge":"368032e81722a4ca97bf2ec81b432b90ef2fc982cac20c8bd543d34f514d9bce",
    "comparator":"5b5b9be61196d6e40abb2182f5dd0cff4b21f7c9fe927592324bc20df471f36d",
}
MAX_MODELS=3
MAX_STEPS_PER_MODEL=500
MAX_TOTAL_STEPS=1500
MAX_FIT_EVAL_SECONDS=2700.0
SEEDS=(20260927,20260928,20260929)


class A1Model(nn.Module):
    def __init__(self,input_dim=960):
        super().__init__()
        self.state_encoder=nn.Sequential(nn.Linear(input_dim,128),nn.ReLU())
        self.onset_encoder=nn.Sequential(nn.Linear(input_dim,128),nn.ReLU())
        self.state_head=nn.Sequential(
            nn.Linear(128,128),
            nn.ReLU(),
            nn.Linear(128,NUM_STRINGS*NUM_CLASSES),
        )
        self.onset_head=nn.Linear(128,NUM_STRINGS)

    def forward(self,x):
        hs=self.state_encoder(x)
        ho=self.onset_encoder(x)
        return self.state_head(hs),self.onset_head(ho)


def _set_seed(seed):
    import random
    random.seed(int(seed))
    np.random.seed(int(seed))
    torch.manual_seed(int(seed))
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))


def initialize_a1(run_seed,input_dim=960):
    # Keep the frozen S11 seed namespace. Architecture differs, but seed identity
    # and batch-plan identity remain paired.
    _set_seed(int(run_seed)+11001)
    return A1Model(input_dim)


def module_sha(model):
    h=hashlib.sha256()
    for n,t in sorted(model.state_dict().items()):
        h.update(n.encode()); h.update(b"\0")
        h.update(np.ascontiguousarray(t.detach().cpu().numpy()).tobytes())
    return h.hexdigest()


def file_sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def parameter_count(model):
    return int(sum(p.numel() for p in model.parameters()))


def validate_inputs(control_path,intervention_path,challenge_path,comparator_path):
    paths={
      "control":Path(control_path),"intervention":Path(intervention_path),
      "challenge":Path(challenge_path),"comparator":Path(comparator_path),
    }
    for k,p in paths.items():
        got=file_sha256(p)
        if got!=EXPECTED_FILE_SHA256[k]:
            raise RuntimeError(f"A1 frozen input hash mismatch: {k}: {got}")

    c=np.load(paths["control"],allow_pickle=False)
    i=np.load(paths["intervention"],allow_pickle=False)
    q=np.load(paths["challenge"],allow_pickle=False)
    comp=json.loads(paths["comparator"].read_text())

    if len(c["features"])!=294 or len(i["features"])!=294:
        raise RuntimeError("A1 control/intervention row count mismatch")
    if len(q["features"])!=84 or not np.all(q["split"]=="test"):
        raise RuntimeError("A1 V3 challenge identity mismatch")
    if set(c.files)!=set(i.files):
        raise RuntimeError("A1 control/intervention key mismatch")
    for k in c.files:
        if k!="features" and not np.array_equal(c[k],i[k]):
            raise RuntimeError("A1 control/intervention non-feature mismatch: "+k)
    train=c["split"]=="train"
    heldout=~train
    if int(np.sum(train))!=210:
        raise RuntimeError("A1 train row count mismatch")
    if not np.array_equal(c["features"][heldout],i["features"][heldout]):
        raise RuntimeError("A1 intervention heldout changed")
    if np.array_equal(c["features"][train],i["features"][train]):
        raise RuntimeError("A1 intervention train features unexpectedly identical")

    if comp.get("schema")!="astra-source-domain-v3-synthetic-training-v1":
        raise RuntimeError("A1 comparator must be full frozen V3 result")
    pairs=comp.get("pairs",[])
    if len(pairs)!=3:
        raise RuntimeError("A1 comparator must contain three seed pairs")
    by_seed={int(p["runSeed"]):p for p in pairs}
    if tuple(sorted(by_seed))!=tuple(sorted(SEEDS)):
        raise RuntimeError("A1 comparator seed set mismatch")

    batch_rows=[]
    for seed in SEEDS:
        batches,_=paired_batches(i["state"],i["onset"],i["split"],i["has_negative_structure"],seed)
        bh=batch_sha(batches)
        frozen=str(by_seed[seed]["batchPlanSha256"])
        if bh!=frozen:
            raise RuntimeError(f"A1 batch hash mismatch seed {seed}")
        batch_rows.append({"seed":seed,"batchPlanSha256":bh})

    return {
      "controlRows":294,"interventionRows":294,"challengeRows":84,
      "trainRows":210,"batchPlans":batch_rows,
      "fileSha256":{k:file_sha256(p) for k,p in paths.items()},
      "identityPassed":True,
    }


def _metric_delta(a,b):
    return {
      "onsetF1":float(a["pitchOnset"]["f1"]-b["pitchOnset"]["f1"]),
      "onsetRecall":float(a["pitchOnset"]["recall"]-b["pitchOnset"]["recall"]),
      "onsetPrecision":float(a["pitchOnset"]["precision"]-b["pitchOnset"]["precision"]),
      "stateAdmission":float(a["admission"]["stateAdmissionFraction"]-b["admission"]["stateAdmissionFraction"]),
      "jointAdmission":float(a["admission"]["jointAdmissionFraction"]-b["admission"]["jointAdmissionFraction"]),
    }


def _summary(vals):
    a=np.asarray(vals,dtype=float)
    if a.size==0 or not np.isfinite(a).all():
        raise RuntimeError("A1 nonfinite summary")
    return {
      "mean":float(a.mean()),"median":float(np.median(a)),
      "minimum":float(a.min()),"maximum":float(a.max()),
      "positiveCount":int(np.sum(a>0)),
    }


def evaluate_gate(rows):
    arch_ord={k:_summary([r["vsFrozenIntervention"]["ordinary"][k] for r in rows])
              for k in ("onsetF1","onsetRecall","onsetPrecision","stateAdmission","jointAdmission")}
    arch_ch={k:_summary([r["vsFrozenIntervention"]["challenge"][k] for r in rows])
             for k in ("onsetF1","onsetRecall","onsetPrecision","stateAdmission","jointAdmission")}
    abs_ord={k:_summary([r["vsFrozenControl"]["ordinary"][k] for r in rows])
             for k in ("onsetF1","onsetRecall","onsetPrecision","stateAdmission","jointAdmission")}
    abs_ch={k:_summary([r["vsFrozenControl"]["challenge"][k] for r in rows])
            for k in ("onsetF1","onsetRecall","onsetPrecision","stateAdmission","jointAdmission")}

    required=[]
    for r in rows:
        for domain in ("ordinary","challenge"):
            m=r["a1"][domain]
            required += [
              m["pitchOnset"]["precision"],m["pitchOnset"]["recall"],m["pitchOnset"]["f1"],
              m["admission"]["stateAdmissionFraction"],m["admission"]["jointAdmissionFraction"],
              m["negativeOnlyFalsePositiveEventsPerSecond"],
            ]
    finite=all(x is not None and math.isfinite(float(x)) for x in required)

    criteria={
      "ordinaryStateGainVsS11InterventionPositive3of3":arch_ord["stateAdmission"]["positiveCount"]==3,
      "meanOrdinaryStateGainVsS11InterventionAtLeast0_04":arch_ord["stateAdmission"]["mean"]>=.04,
      "ordinaryJointGainVsS11InterventionPositive3of3":arch_ord["jointAdmission"]["positiveCount"]==3,
      "meanOrdinaryJointGainVsS11InterventionAtLeast0_04":arch_ord["jointAdmission"]["mean"]>=.04,
      "noChallengeF1LossVsS11InterventionOver0_03":all(r["vsFrozenIntervention"]["challenge"]["onsetF1"]>=-.03 for r in rows),
      "noChallengeRecallLossVsS11InterventionOver0_03":all(r["vsFrozenIntervention"]["challenge"]["onsetRecall"]>=-.03 for r in rows),
      "noOrdinaryF1LossVsS11InterventionOver0_03":all(r["vsFrozenIntervention"]["ordinary"]["onsetF1"]>=-.03 for r in rows),
      "noOrdinaryPrecisionLossVsS11InterventionOver0_03":all(r["vsFrozenIntervention"]["ordinary"]["onsetPrecision"]>=-.03 for r in rows),
      "a1ChallengeNegativeFpAtMost0_10EverySeed":all(r["a1"]["challenge"]["negativeOnlyFalsePositiveEventsPerSecond"]<=.10 for r in rows),
      "a1OrdinaryNegativeFpAtMost0_10EverySeed":all(r["a1"]["ordinary"]["negativeOnlyFalsePositiveEventsPerSecond"]<=.10 for r in rows),
      "ordinaryStateLossVsS11ControlAtMost0_03EverySeed":all(r["vsFrozenControl"]["ordinary"]["stateAdmission"]>=-.03 for r in rows),
      "ordinaryJointLossVsS11ControlAtMost0_04EverySeed":all(r["vsFrozenControl"]["ordinary"]["jointAdmission"]>=-.04 for r in rows),
      "challengeF1GainVsS11ControlPositive3of3":abs_ch["onsetF1"]["positiveCount"]==3,
      "meanChallengeF1GainVsS11ControlAtLeast0_05":abs_ch["onsetF1"]["mean"]>=.05,
      "challengeRecallGainVsS11ControlPositive3of3":abs_ch["onsetRecall"]["positiveCount"]==3,
      "allRequiredMetricsFinite":finite,
      "threeModels500Steps":all(r["fit"]["optimizerSteps"]==500 for r in rows),
      "fixedThresholdsNoSearch":True,
      "exactFrozenBatchPlans":all(r["batchPlanMatchesFrozen"] for r in rows),
      "noAutomaticRetry":True,
    }
    return {
      "architectureEffectOrdinary":arch_ord,
      "architectureEffectChallenge":arch_ch,
      "absoluteVsFrozenControlOrdinary":abs_ord,
      "absoluteVsFrozenControlChallenge":abs_ch,
      "criteria":criteria,
      "gatePassed":all(criteria.values()),
    }


def run(control_path,intervention_path,challenge_path,comparator_path,out_path):
    out=Path(out_path)
    if out.exists(): raise RuntimeError("refusing existing A1 output")
    identity=validate_inputs(control_path,intervention_path,challenge_path,comparator_path)

    c=np.load(control_path,allow_pickle=False)
    i=np.load(intervention_path,allow_pickle=False)
    q=np.load(challenge_path,allow_pickle=False)
    comp=json.loads(Path(comparator_path).read_text())
    frozen={int(p["runSeed"]):p for p in comp["pairs"]}

    started=time.monotonic(); deadline=started+MAX_FIT_EVAL_SECONDS
    rows=[]
    for seed in SEEDS:
        batches,_=paired_batches(i["state"],i["onset"],i["split"],i["has_negative_structure"],seed)
        bh=batch_sha(batches)
        if bh!=frozen[seed]["batchPlanSha256"]:
            raise RuntimeError("A1 runtime batch hash mismatch")

        model=initialize_a1(seed,960)
        fit_result=fit(
          model,i["features"].astype(np.float32,copy=False),
          i["state"],i["onset"],batches,deadline
        )
        if fit_result["optimizerSteps"]!=500:
            raise RuntimeError("A1 did not finish 500 optimizer steps")

        ordinary=evaluate(model,c,"test")
        challenge=evaluate(model,q,"test")

        fint=frozen[seed]["intervention"]
        fctl=frozen[seed]["control"]
        rows.append({
          "seed":int(seed),
          "modelInitSha256":module_sha(initialize_a1(seed,960)),
          "parameterCount":parameter_count(model),
          "batchPlanSha256":bh,
          "batchPlanMatchesFrozen":True,
          "fit":fit_result,
          "a1":{"ordinary":ordinary,"challenge":challenge},
          "vsFrozenIntervention":{
            "ordinary":_metric_delta(ordinary,fint["ordinary"]),
            "challenge":_metric_delta(challenge,fint["challenge"]),
          },
          "vsFrozenControl":{
            "ordinary":_metric_delta(ordinary,fctl["ordinary"]),
            "challenge":_metric_delta(challenge,fctl["challenge"]),
          },
        })

    gate=evaluate_gate(rows)
    elapsed=float(time.monotonic()-started)
    total_steps=sum(r["fit"]["optimizerSteps"] for r in rows)
    if total_steps!=1500 or elapsed>MAX_FIT_EVAL_SECONDS:
        raise RuntimeError("A1 execution ceiling exceeded")

    result={
      "schema":SCHEMA,
      "status":"passed" if gate["gatePassed"] else "failed",
      "architecture":{
        "name":"A1-decoupled-state-onset-encoders",
        "inputDim":960,
        "stateEncoder":[960,128],
        "onsetEncoder":[960,128],
        "stateHead":[128,128,126],
        "onsetHead":[128,6],
        "onlyDeliberateChange":"shared S11 encoder replaced by two disjoint encoders",
        "parameterCount":parameter_count(initialize_a1(SEEDS[0],960)),
      },
      "identity":identity,
      "rows":rows,
      "gate":gate,
      "fixed":{
        "seeds":list(SEEDS),"stepsPerModel":500,
        "stateThreshold":0.5,"onsetThreshold":0.5,
        "thresholdSearch":False,"thresholdRetuning":False,
        "lossWeights":{"stateActive":9.0,"onsetPositive":8.0,"onsetMultiplier":4.0},
        "sampler":"onset-aware-32-32-32-32","learningRate":0.003,"batchSize":128,
      },
      "execution":{
        "modelCount":3,"optimizerStepsTotal":total_steps,
        "fitEvalSeconds":elapsed,"automaticRetry":False,
        "p1Accessed":False,"p2Accessed":False,"p3Opened":False,
        "paidComputeDollars":0,"codespacesUsed":False,"vercelUsed":False,
        "productionMutation":False,
      },
      "nextAction":"freeze-and-stop-before-real-data-or-further-architecture" if gate["gatePassed"] else "freeze-a1-failure-no-automatic-a2",
    }
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("ARCHITECTURE_A1="+json.dumps({
      "status":result["status"],
      "gatePassed":gate["gatePassed"],
      "architectureEffectOrdinary":gate["architectureEffectOrdinary"],
      "architectureEffectChallenge":gate["architectureEffectChallenge"],
      "execution":result["execution"]
    },sort_keys=True))
    return result


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    v=sub.add_parser("verify")
    v.add_argument("--control",required=True); v.add_argument("--intervention",required=True)
    v.add_argument("--challenge",required=True); v.add_argument("--comparator",required=True)
    r=sub.add_parser("run")
    r.add_argument("--control",required=True); r.add_argument("--intervention",required=True)
    r.add_argument("--challenge",required=True); r.add_argument("--comparator",required=True)
    r.add_argument("--out",required=True)
    a=ap.parse_args()
    if a.cmd=="verify":
        print("A1_VERIFY="+json.dumps(validate_inputs(a.control,a.intervention,a.challenge,a.comparator),sort_keys=True))
    else:
        if int(os.environ.get("GITHUB_RUN_ATTEMPT","1"))!=1:
            raise RuntimeError("A1 requires GitHub run attempt 1")
        run(a.control,a.intervention,a.challenge,a.comparator,a.out)

if __name__=="__main__":
    main()
