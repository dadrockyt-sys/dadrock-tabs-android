#!/usr/bin/env python3
"""Astra S13 frozen positive-increment robustness package.

Preparation/admission logic is model-free. The training entry point exists but is
fail-closed unless an exact frozen launch file is present and armed.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, time
from pathlib import Path
import numpy as np
import torch

from synthetic.s0_pilot_v1 import generate_dataset, context5
from synthetic.s9_pilot_v1 import build_intervention_dataset
from synthetic.s11_pilot_v1 import (
    RUN_SEEDS, initialize_model, module_sha, paired_batches, batch_sha,
    fit, evaluate,
)
from synthetic.s2_pilot_v1 import dataset_array_hashes, array_content_sha256
from synthetic.s13_transform_design_review_v1 import compress_positive_onset_increments

SCHEMA="astra-synthetic-s13-positive-increment-v1"
RETAIN_FRACTION=0.50
MAX_MODELS=6
MAX_STEPS_PER_MODEL=500
MAX_TOTAL_STEPS=3000
MAX_FIT_EVAL_SECONDS=5400.0
LAUNCH_SCHEMA="astra-synthetic-s13-launch-v1"
HISTORY_SCHEMA="astra-synthetic-s13-execution-history-v1"

def git_blob_sha(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def file_sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def rank_key(row_index):
    raw=f"astra-s13-soft-subset-v1|{int(row_index)}".encode()
    return hashlib.sha256(raw).hexdigest()

def transformed_training_rows(family,split):
    family=np.asarray(family); split=np.asarray(split)
    chosen=[]
    per_family={}
    for fam in sorted(set(str(x) for x in family.tolist())):
        rows=np.flatnonzero((family==fam)&(split=="train")).tolist()
        ranked=sorted(rows,key=lambda i:(rank_key(i),int(i)))
        take=len(rows)//2
        selected=ranked[:take]
        chosen.extend(selected)
        per_family[fam]={
            "trainRows":len(rows),
            "transformedRows":take,
            "rowIndices":[int(i) for i in selected],
            "rankKeys":[rank_key(i) for i in selected],
        }
    return np.asarray(sorted(chosen),dtype=np.int64),per_family

def _validate_common_arrays(c,a,b):
    if set(c.files)!=set(a.files) or set(c.files)!=set(b.files):
        raise RuntimeError("dataset key mismatch")
    for k in c.files:
        if k=="features": continue
        if not np.array_equal(c[k],a[k]) or not np.array_equal(c[k],b[k]):
            raise RuntimeError("non-feature identity mismatch: "+k)

def build_datasets(control_path,intervention_out,challenge_out,receipt_out,expected_examples=294):
    c=np.load(control_path,allow_pickle=False)
    if len(c["features"])!=int(expected_examples):
        raise RuntimeError("unexpected S13 control size")
    ia={k:np.array(c[k],copy=True) for k in c.files}
    qa={k:np.array(c[k],copy=True) for k in c.files}
    rows,per_family=transformed_training_rows(c["family"],c["split"])

    for i in rows.tolist():
        ia["features"][i]=compress_positive_onset_increments(
            c["features"][i],c["onset"][i],RETAIN_FRACTION
        )
    test_rows=np.flatnonzero(c["split"]=="test")
    for i in test_rows.tolist():
        qa["features"][i]=compress_positive_onset_increments(
            c["features"][i],c["onset"][i],RETAIN_FRACTION
        )

    heldout=(c["split"]!="train")
    non_test=(c["split"]!="test")
    if not np.array_equal(c["features"][heldout],ia["features"][heldout]):
        raise RuntimeError("intervention validation/test changed")
    if not np.array_equal(c["features"][non_test],qa["features"][non_test]):
        raise RuntimeError("challenge train/validation changed")

    # Exact transform admission on every changed row.
    selected=set(int(x) for x in rows.tolist())
    for i in range(len(c["features"])):
        if i in selected:
            expected=compress_positive_onset_increments(c["features"][i],c["onset"][i],RETAIN_FRACTION)
            if not np.array_equal(expected,ia["features"][i]):
                raise RuntimeError("intervention formula mismatch")
        elif not np.array_equal(c["features"][i],ia["features"][i]):
            raise RuntimeError("unselected intervention row changed")

    for i in test_rows.tolist():
        expected=compress_positive_onset_increments(c["features"][i],c["onset"][i],RETAIN_FRACTION)
        if not np.array_equal(expected,qa["features"][i]):
            raise RuntimeError("challenge formula mismatch")

    np.savez_compressed(intervention_out,**ia)
    np.savez_compressed(challenge_out,**qa)
    i=np.load(intervention_out,allow_pickle=False)
    q=np.load(challenge_out,allow_pickle=False)
    _validate_common_arrays(c,i,q)

    receipt={
        "schema":"astra-s13-dataset-receipt-v1",
        "retainFraction":RETAIN_FRACTION,
        "controlExamples":int(len(c["features"])),
        "transformedTrainingRows":int(len(rows)),
        "challengeTestRows":int(len(test_rows)),
        "familySelection":per_family,
        "arrayHashes":{
            "control":dataset_array_hashes(c),
            "intervention":dataset_array_hashes(i),
            "challenge":dataset_array_hashes(q),
        },
        "datasetFileSha256":{
            "control":file_sha256(control_path),
            "intervention":file_sha256(intervention_out),
            "challenge":file_sha256(challenge_out),
        },
        "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False,"modelRun":False,"optimizerSteps":0},
    }
    Path(receipt_out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    return receipt

def delta(a,b):
    return {
      "onsetF1":a["pitchOnset"]["f1"]-b["pitchOnset"]["f1"],
      "onsetRecall":a["pitchOnset"]["recall"]-b["pitchOnset"]["recall"],
      "onsetPrecision":a["pitchOnset"]["precision"]-b["pitchOnset"]["precision"],
      "onsetOffsetF1":a["pitchOnsetOffset"]["f1"]-b["pitchOnsetOffset"]["f1"],
      "stateAdmission":a["admission"]["stateAdmissionFraction"]-b["admission"]["stateAdmissionFraction"],
      "jointAdmission":a["admission"]["jointAdmissionFraction"]-b["admission"]["jointAdmissionFraction"],
    }

def summarize(vals):
    a=np.asarray(vals,dtype=float)
    if a.size==0 or not np.isfinite(a).all():
        raise RuntimeError("nonfinite/empty summary")
    return {"mean":float(a.mean()),"median":float(np.median(a)),"minimum":float(a.min()),
            "maximum":float(a.max()),"positiveCount":int(np.sum(a>0))}

def evaluate_gate(pairs):
    if len(pairs)!=3:
        raise ValueError("S13 gate requires exactly three seed pairs")
    challenge={k:summarize([p["challengeDelta"][k] for p in pairs])
               for k in ("onsetF1","onsetRecall","onsetPrecision","stateAdmission","jointAdmission")}
    ordinary={k:summarize([p["ordinaryDelta"][k] for p in pairs])
              for k in ("onsetF1","onsetRecall","onsetPrecision","stateAdmission","jointAdmission")}
    fams={}
    families=set.intersection(*[set(p["ordinaryNonChordFamilyF1Loss"].keys()) for p in pairs])
    for fam in sorted(families):
        losses=[float(p["ordinaryNonChordFamilyF1Loss"][fam]) for p in pairs]
        fams[fam]={"losses":losses,"lossOver0_15Count":sum(x>0.15 for x in losses)}
    required_numbers=[]
    for p in pairs:
        for domain in ("control","intervention"):
            for split in ("ordinary","challenge"):
                m=p[domain][split]
                required_numbers += [
                    m["pitchOnset"]["truePositive"],m["pitchOnset"]["falsePositive"],m["pitchOnset"]["falseNegative"],
                    m["pitchOnset"]["precision"],m["pitchOnset"]["recall"],m["pitchOnset"]["f1"],
                    m["pitchOnsetOffset"]["f1"],m["admission"]["stateAdmissionFraction"],
                    m["admission"]["jointAdmissionFraction"],m["negativeOnlyFalsePositiveEvents"],
                    m["negativeOnlySeconds"],m["negativeOnlyFalsePositiveEventsPerSecond"],
                ]
    all_finite=all(v is not None and math.isfinite(float(v)) for v in required_numbers)
    criteria={
      "challengeOnsetF1GainPositive3of3":challenge["onsetF1"]["positiveCount"]==3,
      "challengeOnsetRecallGainPositive3of3":challenge["onsetRecall"]["positiveCount"]==3,
      "meanChallengeOnsetF1GainAtLeast0_05":challenge["onsetF1"]["mean"]>=0.05,
      "meanChallengeOnsetRecallGainAtLeast0_08":challenge["onsetRecall"]["mean"]>=0.08,
      "noChallengePrecisionLossOver0_05":all(p["challengeDelta"]["onsetPrecision"]>=-0.05 for p in pairs),
      "challengeNegativeOnlyFpAtMost0_10EverySeed":all(p["intervention"]["challenge"]["negativeOnlyFalsePositiveEventsPerSecond"]<=0.10 for p in pairs),
      "noOrdinaryOnsetF1LossOver0_03":all(p["ordinaryDelta"]["onsetF1"]>=-0.03 for p in pairs),
      "noOrdinaryPrecisionLossOver0_03":all(p["ordinaryDelta"]["onsetPrecision"]>=-0.03 for p in pairs),
      "noOrdinaryStateAdmissionLossOver0_03":all(p["ordinaryDelta"]["stateAdmission"]>=-0.03 for p in pairs),
      "noOrdinaryJointAdmissionLossOver0_04":all(p["ordinaryDelta"]["jointAdmission"]>=-0.04 for p in pairs),
      "ordinaryNegativeOnlyFpAtMost0_10EverySeed":all(p["intervention"]["ordinary"]["negativeOnlyFalsePositiveEventsPerSecond"]<=0.10 for p in pairs),
      "ordinaryNonChordFamilyLossOver0_15InAtMostOneSeed":all(v["lossOver0_15Count"]<=1 for v in fams.values()),
      "allRequiredMetricsFinite":all_finite,
      "allSix500Steps":all(p["control"]["fit"]["optimizerSteps"]==500 and p["intervention"]["fit"]["optimizerSteps"]==500 for p in pairs),
      "pairedInitializationAndBatches":all(all(p["pairIdentity"].values()) for p in pairs),
    }
    return {"challengeDeltaSummary":challenge,"ordinaryDeltaSummary":ordinary,
            "ordinaryNonChordFamilyStability":fams,"criteria":criteria,
            "gatePassed":all(criteria.values())}

def _refuse_existing(path):
    p=Path(path)
    if p.exists():
        raise RuntimeError("refusing existing output path: "+str(p))

def validate_scope(root, scope_path, history_path):
    history=json.loads(Path(history_path).read_text())
    scope=json.loads(Path(scope_path).read_text())
    spec_path=root/"docs/astra/SYNTHETIC_S13_SPEC_V1.json"
    design_path=root/"docs/astra/SYNTHETIC_S13_DESIGN_V1.md"
    spec=json.loads(spec_path.read_text())
    if history.get("schema")!=HISTORY_SCHEMA:
        raise RuntimeError("execution history schema mismatch")
    if scope.get("schema")!="astra-synthetic-s13-run-scope-v1":
        raise RuntimeError("scope schema mismatch")
    if scope.get("specGitBlob")!=git_blob_sha(spec_path):
        raise RuntimeError("scope spec pin mismatch")
    if scope.get("designGitBlob")!=git_blob_sha(design_path):
        raise RuntimeError("design pin mismatch")
    if scope.get("historyGitBlob")!=git_blob_sha(history_path):
        raise RuntimeError("history pin mismatch")
    for key,rel in scope.get("sourcePaths",{}).items():
        actual=git_blob_sha(root/rel)
        if scope.get("sourceGitBlobs",{}).get(key)!=actual:
            raise RuntimeError("source pin mismatch: "+key)
    fixed=scope.get("fixed",{})
    expected={
      "retainFraction":0.50,"stateThreshold":0.50,"onsetThreshold":0.50,
      "thresholdSearch":False,"thresholdRetuning":False,
      "runSeeds":[20260927,20260928,20260929],
      "maxModels":6,"optimizerStepsPerModel":500,"maxTotalOptimizerSteps":3000,
      "maxFitEvalMinutes":90,"automaticRetry":False,"paidComputeDollars":0,
      "p1Access":False,"p2Access":False,"p3Access":False,
    }
    for k,v in expected.items():
        if fixed.get(k)!=v:
            raise RuntimeError("scope fixed value mismatch: "+k)
    if spec.get("intervention",{}).get("retainFraction")!=0.5:
        raise RuntimeError("spec retain fraction mismatch")
    tr=spec.get("training",{})
    if tr.get("seeds")!=[20260927,20260928,20260929] or tr.get("optimizerStepsPerModel")!=500 or tr.get("maxModels")!=6 or tr.get("maxTotalOptimizerSteps")!=3000:
        raise RuntimeError("spec training ceiling mismatch")
    dec=spec.get("decoder",{})
    if dec.get("stateThreshold")!=0.5 or dec.get("onsetThreshold")!=0.5 or dec.get("thresholdSearch") or dec.get("thresholdRetuning"):
        raise RuntimeError("spec decoder/threshold mismatch")
    return history,scope

def validate_launch(root, launch_path, history_path, scope_path):
    launch=json.loads(Path(launch_path).read_text())
    history,scope=validate_scope(root,scope_path,history_path)
    if launch.get("schema")!=LAUNCH_SCHEMA or launch.get("status")!="armed":
        raise RuntimeError("S13 launch is not armed")
    launch_id=str(launch.get("launchIdentity",""))
    if not launch_id:
        raise RuntimeError("missing launch identity")
    used=set(str(x) for x in history.get("consumedLaunchIdentities",[]))
    if launch_id in used:
        raise RuntimeError("launch identity already consumed")
    attempt=int(os.environ.get("GITHUB_RUN_ATTEMPT","1"))
    if attempt!=1:
        raise RuntimeError("GitHub run attempt must equal 1")
    if os.environ.get("GITHUB_REF_NAME") not in (None,"","astra-work"):
        raise RuntimeError("wrong branch")
    if launch.get("scopeGitBlob")!=git_blob_sha(scope_path):
        raise RuntimeError("scope pin mismatch")
    if launch.get("specGitBlob")!=git_blob_sha(root/"docs/astra/SYNTHETIC_S13_SPEC_V1.json"):
        raise RuntimeError("spec pin mismatch")
    return launch,history,scope

def validate_dataset_hashes(scope, control_path, intervention_path, challenge_path):
    expected=scope.get("datasetArrayHashes")
    if not isinstance(expected,dict):
        raise RuntimeError("frozen dataset array hashes missing from scope")
    for name,path in (("control",control_path),("intervention",intervention_path),("challenge",challenge_path)):
        d=np.load(path,allow_pickle=False)
        actual=dataset_array_hashes(d)
        if actual!=expected.get(name):
            raise RuntimeError("dataset array hash mismatch: "+name)
    return True

def run_experiment(control_path,intervention_path,challenge_path,out_path):
    _refuse_existing(out_path)
    started=time.monotonic(); deadline=started+MAX_FIT_EVAL_SECONDS
    c=np.load(control_path,allow_pickle=False)
    i=np.load(intervention_path,allow_pickle=False)
    q=np.load(challenge_path,allow_pickle=False)
    _validate_common_arrays(c,i,q)
    if not np.array_equal(c["features"][c["split"]!="train"],i["features"][i["split"]!="train"]):
        raise RuntimeError("ordinary heldout mismatch")
    if not np.array_equal(c["features"][c["split"]!="test"],q["features"][q["split"]!="test"]):
        raise RuntimeError("challenge train/validation mismatch")

    expected_rows,_=transformed_training_rows(c["family"],c["split"])
    selected=set(expected_rows.tolist())
    for idx in range(len(c["features"])):
        if idx in selected:
            exp=compress_positive_onset_increments(c["features"][idx],c["onset"][idx],RETAIN_FRACTION)
            if not np.array_equal(exp,i["features"][idx]): raise RuntimeError("intervention transform mismatch")
        elif not np.array_equal(c["features"][idx],i["features"][idx]):
            raise RuntimeError("unexpected intervention feature change")
    test_rows=np.flatnonzero(c["split"]=="test")
    for idx in test_rows.tolist():
        exp=compress_positive_onset_increments(c["features"][idx],c["onset"][idx],RETAIN_FRACTION)
        if not np.array_equal(exp,q["features"][idx]):
            raise RuntimeError("challenge transform mismatch")

    pairs=[]
    for seed in RUN_SEEDS:
        cb,cs=paired_batches(c["state"],c["onset"],c["split"],c["has_negative_structure"],seed)
        ib,is_=paired_batches(i["state"],i["onset"],i["split"],i["has_negative_structure"],seed)
        if cs!=is_ or not np.array_equal(cb,ib):
            raise RuntimeError("paired batch mismatch")
        cm=initialize_model(seed,960); im=initialize_model(seed,960)
        if module_sha(cm)!=module_sha(im):
            raise RuntimeError("paired initialization mismatch")
        cf=fit(cm,c["features"].astype(np.float32,copy=False),c["state"],c["onset"],cb,deadline)
        inf=fit(im,i["features"].astype(np.float32,copy=False),i["state"],i["onset"],ib,deadline)
        co=evaluate(cm,c,"test"); io=evaluate(im,i,"test")
        cq=evaluate(cm,q,"test"); iq=evaluate(im,q,"test")
        pairs.append({
          "runSeed":int(seed),"modelInitSha256":module_sha(initialize_model(seed,960)),
          "batchPlanSha256":batch_sha(cb),
          "control":{"fit":cf,"ordinary":co,"challenge":cq},
          "intervention":{"fit":inf,"ordinary":io,"challenge":iq},
          "ordinaryDelta":delta(io,co),"challengeDelta":delta(iq,cq),
          "ordinaryNonChordFamilyF1Loss":{
            fam:co["familyPitchOnset"][fam]["f1"]-io["familyPitchOnset"][fam]["f1"]
            for fam in co["familyPitchOnset"] if fam!="chords"
          },
          "pairIdentity":{"initializationIdentical":True,"batchIndicesIdentical":True},
        })
    gate=evaluate_gate(pairs)
    execution={"modelCount":6,
               "optimizerStepsTotal":sum(p["control"]["fit"]["optimizerSteps"]+p["intervention"]["fit"]["optimizerSteps"] for p in pairs),
               "fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0}
    identity_criteria={
      "nonFeatureArraysBitIdentical":True,
      "interventionValidationTestFeaturesBitIdentical":True,
      "challengeTrainValidationFeaturesBitIdentical":True,
      "transformedRowSetMatchesFrozenRule":True,
      "transformFormulaAndNonRisingPreservationVerified":True,
      "fixedThresholdsNoSearch":True,
      "exactSixModelsAnd3000Steps":execution["modelCount"]==MAX_MODELS and execution["optimizerStepsTotal"]==MAX_TOTAL_STEPS,
      "noAutomaticRetry":execution["automaticRetry"] is False,
    }
    all_criteria={**gate["criteria"],**identity_criteria}
    result={
      "schema":SCHEMA,"runSeeds":list(RUN_SEEDS),"pairs":pairs,
      "challengeDeltaSummary":gate["challengeDeltaSummary"],
      "ordinaryDeltaSummary":gate["ordinaryDeltaSummary"],
      "ordinaryNonChordFamilyStability":gate["ordinaryNonChordFamilyStability"],
      "criteria":all_criteria,
      "fixed":{"retainFraction":RETAIN_FRACTION,"stateThreshold":0.5,"onsetThreshold":0.5,
               "thresholdSearch":False,"thresholdRetuning":False},
      "execution":execution,
      "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False,"codespacesUsed":False,
                "vercelUsed":False,"productionMutation":False},
      "s13GatePassed":bool(all(all_criteria.values())),
    }
    if result["execution"]["modelCount"]!=MAX_MODELS or result["execution"]["optimizerStepsTotal"]!=MAX_TOTAL_STEPS:
        raise RuntimeError("execution ceiling/receipt mismatch")
    Path(out_path).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

def prepare_only(out_dir):
    out=Path(out_dir)
    _refuse_existing(out)
    out.mkdir(parents=True)
    work=out/"datasets"; work.mkdir()
    s0=work/"s0-control.npz"
    s9=work/"s9-control.npz"
    intervention=work/"s13-intervention.npz"
    challenge=work/"s13-challenge.npz"
    generate_dataset(s0,out/"s0-render-receipt.json")
    build_intervention_dataset(s0,s9,out/"s9-diverse-receipt.json")
    receipt=build_datasets(s9,intervention,challenge,out/"s13-dataset-receipt.json")
    summary={
      "schema":"astra-s13-preparation-verification-v1",
      "modelRun":False,"optimizerSteps":0,
      "datasetReceipt":receipt,
      "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False},
    }
    (out/"preparation-summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("S13_PREPARATION="+json.dumps(summary,sort_keys=True))
    return summary

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("prepare-only"); p.add_argument("--out-dir",required=True)
    v=sub.add_parser("verify-scope"); v.add_argument("--scope",required=True); v.add_argument("--history",required=True)
    r=sub.add_parser("run")
    r.add_argument("--control-dataset",required=True); r.add_argument("--intervention-dataset",required=True)
    r.add_argument("--challenge-dataset",required=True); r.add_argument("--out",required=True)
    r.add_argument("--launch",required=True); r.add_argument("--history",required=True); r.add_argument("--scope",required=True)
    a=ap.parse_args()
    root=Path(__file__).resolve().parents[2]
    if a.cmd=="prepare-only":
        prepare_only(a.out_dir)
    elif a.cmd=="verify-scope":
        validate_scope(root,a.scope,a.history)
        print("S13_SCOPE_OK")
    else:
        _launch,_history,scope=validate_launch(root,a.launch,a.history,a.scope)
        validate_dataset_hashes(scope,a.control_dataset,a.intervention_dataset,a.challenge_dataset)
        run_experiment(a.control_dataset,a.intervention_dataset,a.challenge_dataset,a.out)

if __name__=="__main__":
    main()
