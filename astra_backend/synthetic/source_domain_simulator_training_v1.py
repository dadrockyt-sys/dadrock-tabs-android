#!/usr/bin/env python3
"""Fail-closed synthetic source-domain training package V1.

All admission/verification helpers are model-free. The run entry point is disabled
unless an exact armed launch and unconsumed durable execution ledger are supplied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np

from synthetic.s2_pilot_v1 import dataset_array_hashes
from synthetic.s11_pilot_v1 import (
    RUN_SEEDS, initialize_model, module_sha, paired_batches, batch_sha,
    fit, evaluate,
)

SCHEMA="astra-source-domain-simulator-training-v1"
LAUNCH_SCHEMA="astra-source-domain-simulator-training-launch-v1"
HISTORY_SCHEMA="astra-source-domain-simulator-training-execution-history-v1"
SCOPE_SCHEMA="astra-source-domain-simulator-training-run-scope-v1"
MAX_MODELS=6
MAX_STEPS_PER_MODEL=500
MAX_TOTAL_STEPS=3000
MAX_FIT_EVAL_SECONDS=5400.0

EXPECTED_FEATURE_HASHES={
    "control":"b172b7cdcc0df5bc3b47b54a8dd116992f9552383babe0dc4cde5eecdac3a749",
    "intervention":"a8b5c5c590c82c152f302260430b3d6e4a3c9d5ee378d683bd8091f8f220501a",
    "challenge":"c786d846b2651872b621afa16d69a179965ffc0190a164d2e5e4ca89e0842640",
}
EXPECTED_FILE_SHA256={
    "control":"16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894",
    "intervention":"b46fa80121c43705708bfe786715456be535f6e39d31835b2fa611629024e94e",
    "challenge":"0d40ab89291f4c19cf44bddb3c1c2adb4926ce3363eeb67f45770940ae03a010",
}

def git_blob_sha(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def file_sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def _refuse_existing(path):
    p=Path(path)
    if p.exists():
        raise RuntimeError("refusing existing output path: "+str(p))

def validate_datasets(control_path,intervention_path,challenge_path,expected=None):
    paths={"control":Path(control_path),"intervention":Path(intervention_path),"challenge":Path(challenge_path)}
    expected=expected or {"featureHashes":EXPECTED_FEATURE_HASHES,"fileSha256":EXPECTED_FILE_SHA256}
    loaded={k:np.load(v,allow_pickle=False) for k,v in paths.items()}
    c,i,q=loaded["control"],loaded["intervention"],loaded["challenge"]
    if len(c["features"])!=294 or len(i["features"])!=294 or len(q["features"])!=294:
        raise RuntimeError("unexpected source-domain dataset size")
    if set(c.files)!=set(i.files) or set(c.files)!=set(q.files):
        raise RuntimeError("dataset key mismatch")
    for k in c.files:
        if k!="features" and (not np.array_equal(c[k],i[k]) or not np.array_equal(c[k],q[k])):
            raise RuntimeError("non-feature identity mismatch: "+k)
    train=(c["split"]=="train"); test=(c["split"]=="test")
    heldout=~train; non_test=~test
    if int(np.sum(train))!=210 or int(np.sum(test))!=42:
        raise RuntimeError("frozen split counts changed")
    if not np.array_equal(c["features"][heldout],i["features"][heldout]):
        raise RuntimeError("intervention validation/test features changed")
    if not np.array_equal(c["features"][non_test],q["features"][non_test]):
        raise RuntimeError("challenge train/validation features changed")
    if np.array_equal(c["features"][train],i["features"][train]):
        raise RuntimeError("intervention training features unexpectedly identical")
    if np.array_equal(c["features"][test],q["features"][test]):
        raise RuntimeError("challenge test features unexpectedly identical")
    for name,d in loaded.items():
        ah=dataset_array_hashes(d)
        if ah["features"]!=expected["featureHashes"][name]:
            raise RuntimeError("feature hash mismatch: "+name)
        if file_sha256(paths[name])!=expected["fileSha256"][name]:
            raise RuntimeError("dataset file hash mismatch: "+name)
    # Preserve historical S9 fixed-width training chord strings across every arm.
    chord_train=(c["family"]=="chords")&train
    if int(np.sum(chord_train))!=30:
        raise RuntimeError("historical S9 chord-row count changed")
    if not all(str(x).startswith("s9-chords:") for x in c["template_id"][chord_train].tolist()):
        raise RuntimeError("historical S9 chord template identifiers changed")
    if not all(len(str(x))==625 for x in c["refs_json"][chord_train].tolist()):
        raise RuntimeError("historical S9 chord reference truncation identity changed")
    return {
      "examples":294,"trainRows":210,"testRows":42,
      "historicalS9TruncatedTrainingChordRows":30,
      "featureHashes":{n:dataset_array_hashes(d)["features"] for n,d in loaded.items()},
      "fileSha256":{n:file_sha256(paths[n]) for n in paths},
      "identityPassed":True,
    }

def delta(a,b):
    return {
      "onsetF1":float(a["pitchOnset"]["f1"]-b["pitchOnset"]["f1"]),
      "onsetRecall":float(a["pitchOnset"]["recall"]-b["pitchOnset"]["recall"]),
      "onsetPrecision":float(a["pitchOnset"]["precision"]-b["pitchOnset"]["precision"]),
      "onsetOffsetF1":float(a["pitchOnsetOffset"]["f1"]-b["pitchOnsetOffset"]["f1"]),
      "stateAdmission":float(a["admission"]["stateAdmissionFraction"]-b["admission"]["stateAdmissionFraction"]),
      "jointAdmission":float(a["admission"]["jointAdmissionFraction"]-b["admission"]["jointAdmissionFraction"]),
    }

def summarize(values):
    a=np.asarray(values,dtype=float)
    if a.size==0 or not np.isfinite(a).all():
        raise RuntimeError("empty/nonfinite summary")
    return {"mean":float(a.mean()),"median":float(np.median(a)),
            "minimum":float(a.min()),"maximum":float(a.max()),
            "positiveCount":int(np.sum(a>0))}

def evaluate_gate(pairs):
    if len(pairs)!=3:
        raise ValueError("source-domain gate requires exactly three seed pairs")
    challenge={k:summarize([p["challengeDelta"][k] for p in pairs])
               for k in ("onsetF1","onsetRecall","onsetPrecision","stateAdmission","jointAdmission")}
    ordinary={k:summarize([p["ordinaryDelta"][k] for p in pairs])
              for k in ("onsetF1","onsetRecall","onsetPrecision","stateAdmission","jointAdmission")}
    fams={}
    common=set.intersection(*[set(p["ordinaryNonChordFamilyF1Loss"]) for p in pairs])
    for fam in sorted(common):
        losses=[float(p["ordinaryNonChordFamilyF1Loss"][fam]) for p in pairs]
        fams[fam]={"losses":losses,"lossOver0_15Count":int(sum(x>.15 for x in losses))}
    required=[]
    for p in pairs:
        for arm in ("control","intervention"):
            for domain in ("ordinary","challenge"):
                m=p[arm][domain]
                required += [
                    m["pitchOnset"]["truePositive"],m["pitchOnset"]["falsePositive"],m["pitchOnset"]["falseNegative"],
                    m["pitchOnset"]["precision"],m["pitchOnset"]["recall"],m["pitchOnset"]["f1"],
                    m["pitchOnsetOffset"]["f1"],m["admission"]["stateAdmissionFraction"],
                    m["admission"]["jointAdmissionFraction"],m["negativeOnlyFalsePositiveEvents"],
                    m["negativeOnlySeconds"],m["negativeOnlyFalsePositiveEventsPerSecond"],
                ]
    finite=all(x is not None and math.isfinite(float(x)) for x in required)
    criteria={
      "challengeOnsetF1GainPositive3of3":challenge["onsetF1"]["positiveCount"]==3,
      "challengeOnsetRecallGainPositive3of3":challenge["onsetRecall"]["positiveCount"]==3,
      "meanChallengeOnsetF1GainAtLeast0_05":challenge["onsetF1"]["mean"]>=.05,
      "meanChallengeOnsetRecallGainAtLeast0_08":challenge["onsetRecall"]["mean"]>=.08,
      "noChallengePrecisionLossOver0_05":all(p["challengeDelta"]["onsetPrecision"]>=-.05 for p in pairs),
      "challengeNegativeOnlyFpAtMost0_10EverySeed":all(
          p["intervention"]["challenge"]["negativeOnlyFalsePositiveEventsPerSecond"]<=.10 for p in pairs),
      "noOrdinaryOnsetF1LossOver0_03":all(p["ordinaryDelta"]["onsetF1"]>=-.03 for p in pairs),
      "noOrdinaryPrecisionLossOver0_03":all(p["ordinaryDelta"]["onsetPrecision"]>=-.03 for p in pairs),
      "noOrdinaryStateAdmissionLossOver0_03":all(p["ordinaryDelta"]["stateAdmission"]>=-.03 for p in pairs),
      "noOrdinaryJointAdmissionLossOver0_04":all(p["ordinaryDelta"]["jointAdmission"]>=-.04 for p in pairs),
      "ordinaryNegativeOnlyFpAtMost0_10EverySeed":all(
          p["intervention"]["ordinary"]["negativeOnlyFalsePositiveEventsPerSecond"]<=.10 for p in pairs),
      "ordinaryNonChordFamilyLossOver0_15InAtMostOneSeed":all(v["lossOver0_15Count"]<=1 for v in fams.values()),
      "allRequiredMetricsFinite":finite,
      "allSix500Steps":all(
          p["control"]["fit"]["optimizerSteps"]==500 and p["intervention"]["fit"]["optimizerSteps"]==500 for p in pairs),
      "pairedInitializationAndBatches":all(all(p["pairIdentity"].values()) for p in pairs),
    }
    return {"challengeDeltaSummary":challenge,"ordinaryDeltaSummary":ordinary,
            "ordinaryNonChordFamilyStability":fams,"criteria":criteria,
            "gatePassed":all(criteria.values())}

def validate_launch(root,launch_path,history_path,scope_path):
    launch=json.loads(Path(launch_path).read_text())
    history=json.loads(Path(history_path).read_text())
    scope=json.loads(Path(scope_path).read_text())
    if launch.get("schema")!=LAUNCH_SCHEMA or launch.get("status")!="armed":
        raise RuntimeError("source-domain launch is not armed")
    if history.get("schema")!=HISTORY_SCHEMA:
        raise RuntimeError("execution history schema mismatch")
    if scope.get("schema")!=SCOPE_SCHEMA:
        raise RuntimeError("run scope schema mismatch")
    launch_id=str(launch.get("launchIdentity",""))
    if not launch_id:
        raise RuntimeError("missing launch identity")
    if launch_id in set(map(str,history.get("consumedLaunchIdentities",[]))):
        raise RuntimeError("launch identity already consumed")
    if int(os.environ.get("GITHUB_RUN_ATTEMPT","1"))!=1:
        raise RuntimeError("GitHub run attempt must equal 1")
    if os.environ.get("GITHUB_REF_NAME") not in (None,"","astra-work"):
        raise RuntimeError("wrong branch")
    if launch.get("scopeGitBlob")!=git_blob_sha(scope_path):
        raise RuntimeError("scope pin mismatch")
    if launch.get("specGitBlob")!=git_blob_sha(root/"docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_SPEC_V1.json"):
        raise RuntimeError("training spec pin mismatch")
    if scope.get("designGitBlob")!=git_blob_sha(root/"docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_DESIGN_V1.md"):
        raise RuntimeError("training design pin mismatch")
    if scope.get("specGitBlob")!=git_blob_sha(root/"docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_SPEC_V1.json"):
        raise RuntimeError("scope training spec pin mismatch")
    if scope.get("historyGitBlob")!=git_blob_sha(history_path):
        raise RuntimeError("history pin mismatch")
    for key,rel in scope["sourcePaths"].items():
        if scope["sourceGitBlobs"].get(key)!=git_blob_sha(root/rel):
            raise RuntimeError("source pin mismatch: "+key)
    ex=launch.get("execution",{})
    required={"maxModels":6,"optimizerStepsPerModel":500,"maxTotalOptimizerSteps":3000,
              "stateThreshold":.5,"onsetThreshold":.5,"thresholdSearch":False,
              "thresholdRetuning":False,"automaticRetry":False,"paidComputeDollars":0,
              "p1Access":False,"p2Access":False,"p3Access":False}
    if any(ex.get(k)!=v for k,v in required.items()):
        raise RuntimeError("launch execution ceiling mismatch")
    return launch,history,scope

def run_experiment(control_path,intervention_path,challenge_path,out_path):
    _refuse_existing(out_path)
    started=time.monotonic(); deadline=started+MAX_FIT_EVAL_SECONDS
    c=np.load(control_path,allow_pickle=False)
    i=np.load(intervention_path,allow_pickle=False)
    q=np.load(challenge_path,allow_pickle=False)
    pairs=[]
    for seed in RUN_SEEDS:
        cb,cs=paired_batches(c["state"],c["onset"],c["split"],c["has_negative_structure"],seed)
        ib,is_=paired_batches(i["state"],i["onset"],i["split"],i["has_negative_structure"],seed)
        if cs!=is_ or not np.array_equal(cb,ib):
            raise RuntimeError("paired batch mismatch")
        cm=initialize_model(seed,960); im=initialize_model(seed,960)
        if module_sha(cm)!=module_sha(im):
            raise RuntimeError("paired initialization mismatch")
        cfit=fit(cm,c["features"].astype(np.float32,copy=False),c["state"],c["onset"],cb,deadline)
        ifit=fit(im,i["features"].astype(np.float32,copy=False),i["state"],i["onset"],ib,deadline)
        co=evaluate(cm,c,"test")
        io=evaluate(im,c,"test")  # ordinary clean/control test for both models
        cq=evaluate(cm,q,"test")
        iq=evaluate(im,q,"test")
        pairs.append({
          "runSeed":int(seed),
          "modelInitSha256":module_sha(initialize_model(seed,960)),
          "batchPlanSha256":batch_sha(cb),
          "control":{"fit":cfit,"ordinary":co,"challenge":cq},
          "intervention":{"fit":ifit,"ordinary":io,"challenge":iq},
          "ordinaryDelta":delta(io,co),
          "challengeDelta":delta(iq,cq),
          "ordinaryNonChordFamilyF1Loss":{
              fam:float(co["familyPitchOnset"][fam]["f1"]-io["familyPitchOnset"][fam]["f1"])
              for fam in co["familyPitchOnset"] if fam!="chords"
          },
          "pairIdentity":{"initializationIdentical":True,"batchIndicesIdentical":True},
        })
    gate=evaluate_gate(pairs)
    execution={"modelCount":6,
      "optimizerStepsTotal":sum(p["control"]["fit"]["optimizerSteps"]+p["intervention"]["fit"]["optimizerSteps"] for p in pairs),
      "fitEvalSeconds":float(time.monotonic()-started),"automaticRetry":False,"paidComputeDollars":0}
    identity={
      "fixedDatasetHashesVerified":True,
      "nonFeatureArraysBitIdentical":True,
      "interventionValidationTestFeaturesBitIdentical":True,
      "challengeTrainValidationFeaturesBitIdentical":True,
      "interventionChangedRowsExactlyTrain":True,
      "challengeChangedRowsExactlyTest":True,
      "historicalS9TrainingChordStringsPreserved":True,
      "fixedThresholdsNoSearch":True,
      "exactSixModelsAnd3000Steps":execution["modelCount"]==MAX_MODELS and execution["optimizerStepsTotal"]==MAX_TOTAL_STEPS,
      "noAutomaticRetry":True,
    }
    criteria={**gate["criteria"],**identity}
    result={
      "schema":SCHEMA,"runSeeds":list(RUN_SEEDS),"pairs":pairs,
      "challengeDeltaSummary":gate["challengeDeltaSummary"],
      "ordinaryDeltaSummary":gate["ordinaryDeltaSummary"],
      "ordinaryNonChordFamilyStability":gate["ordinaryNonChordFamilyStability"],
      "criteria":criteria,
      "sourceDomainGatePassed":bool(all(criteria.values())),
      "fixed":{"stateThreshold":.5,"onsetThreshold":.5,"thresholdSearch":False,"thresholdRetuning":False},
      "execution":execution,
      "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False,
                "codespacesUsed":False,"vercelUsed":False,"productionMutation":False},
      "historicalS9StringStorage":{"trainingChordRows":30,"preservedUnchanged":True},
    }
    if execution["optimizerStepsTotal"]!=MAX_TOTAL_STEPS:
        raise RuntimeError("optimizer-step total mismatch")
    Path(out_path).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    v=sub.add_parser("verify-datasets")
    v.add_argument("--control",required=True); v.add_argument("--intervention",required=True); v.add_argument("--challenge",required=True)
    r=sub.add_parser("run")
    r.add_argument("--control",required=True); r.add_argument("--intervention",required=True); r.add_argument("--challenge",required=True)
    r.add_argument("--out",required=True); r.add_argument("--launch",required=True); r.add_argument("--history",required=True); r.add_argument("--scope",required=True)
    a=ap.parse_args()
    if a.cmd=="verify-datasets":
        print("SOURCE_DOMAIN_DATASET_VERIFY="+json.dumps(validate_datasets(a.control,a.intervention,a.challenge),sort_keys=True))
    else:
        root=Path(__file__).resolve().parents[2]
        validate_launch(root,a.launch,a.history,a.scope)
        validate_datasets(a.control,a.intervention,a.challenge)
        run_experiment(a.control,a.intervention,a.challenge,a.out)

if __name__=="__main__":
    main()
