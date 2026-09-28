#!/usr/bin/env python3
"""Final Astra source-domain V3 synthetic training experiment.

Training/evaluation semantics are frozen from source_domain_simulator_training_v1.
Only the admitted data inputs change:
- control: frozen S9
- intervention training: frozen V2 Stage-B intervention
- challenge: frozen standalone 84-row V3 primary challenge
"""
from __future__ import annotations

import argparse, hashlib, json, math, os, time
from pathlib import Path

import numpy as np

from synthetic.s2_pilot_v1 import dataset_array_hashes
from synthetic.s11_pilot_v1 import (
    RUN_SEEDS, initialize_model, module_sha, paired_batches, batch_sha,
    fit, evaluate,
)
from synthetic.source_domain_simulator_training_v1 import delta, evaluate_gate

SCHEMA="astra-source-domain-v3-synthetic-training-v1"
EXPECTED={
 "control":"16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894",
 "intervention":"a17a16daeb8d698e325dc6820f18d5eda2fec75d9beebe2a9605a678124dc26b",
 "challenge":"368032e81722a4ca97bf2ec81b432b90ef2fc982cac20c8bd543d34f514d9bce",
}
SEEDS=(20260927,20260928,20260929)
MAX_MODELS=6
MAX_STEPS_PER_MODEL=500
MAX_TOTAL_STEPS=3000
MAX_FIT_EVAL_SECONDS=5400.0


def file_sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def validate_inputs(control_path,intervention_path,challenge_path):
    paths={"control":Path(control_path),"intervention":Path(intervention_path),"challenge":Path(challenge_path)}
    for k,p in paths.items():
        if file_sha256(p)!=EXPECTED[k]:
            raise RuntimeError("V3 training file hash mismatch: "+k)

    c=np.load(paths["control"],allow_pickle=False)
    i=np.load(paths["intervention"],allow_pickle=False)
    q=np.load(paths["challenge"],allow_pickle=False)

    if len(c["features"])!=294 or len(i["features"])!=294:
        raise RuntimeError("control/intervention row count mismatch")
    if len(q["features"])!=84:
        raise RuntimeError("V3 challenge must contain exactly 84 rows")

    # Control/intervention identity: only train features may differ.
    if set(c.files)!=set(i.files):
        raise RuntimeError("control/intervention key mismatch")
    for k in c.files:
        if k!="features" and not np.array_equal(c[k],i[k]):
            raise RuntimeError("control/intervention non-feature mismatch: "+k)
    train=(c["split"]=="train")
    test=(c["split"]=="test")
    heldout=~train
    if int(np.sum(train))!=210 or int(np.sum(test))!=42:
        raise RuntimeError("frozen control split counts changed")
    if not np.array_equal(c["features"][heldout],i["features"][heldout]):
        raise RuntimeError("V2 intervention heldout changed")
    if np.array_equal(c["features"][train],i["features"][train]):
        raise RuntimeError("V2 intervention training features unexpectedly identical")

    # Historical S9 fixed-width bookkeeping must remain frozen.
    chord_train=(c["family"]=="chords")&train
    if int(np.sum(chord_train))!=30:
        raise RuntimeError("historical S9 chord-row count changed")
    if not all(str(x).startswith("s9-chords:") for x in c["template_id"][chord_train].tolist()):
        raise RuntimeError("historical S9 chord template strings changed")
    if not all(len(str(x))==625 for x in c["refs_json"][chord_train].tolist()):
        raise RuntimeError("historical S9 chord refs changed")

    # Standalone V3 challenge identity.
    required={"features","state","onset","family","split","template_id","negative_only",
              "has_negative_structure","refs_json","source_row_index","challenge_replicate"}
    if not required.issubset(set(q.files)):
        raise RuntimeError("V3 challenge missing required arrays")
    if not np.isfinite(q["features"]).all():
        raise RuntimeError("nonfinite V3 challenge features")
    if not np.all(q["split"]=="test"):
        raise RuntimeError("V3 challenge must be test-only")
    fam_counts={f:int(np.sum(q["family"]==f)) for f in sorted(set(map(str,q["family"].tolist())))}
    expected_fams={"chords","isolated","legato","mixed","palmmute","repeated","scales"}
    if set(fam_counts)!=expected_fams or any(v!=12 for v in fam_counts.values()):
        raise RuntimeError("V3 challenge family counts changed")
    src=np.asarray(q["source_row_index"],dtype=int)
    if len(src)!=84 or not np.all(test[src]):
        raise RuntimeError("V3 challenge source rows are not frozen control test rows")
    reps=np.asarray(q["challenge_replicate"],dtype=int)
    if set(reps.tolist())!={0,1}:
        raise RuntimeError("V3 challenge replicate identities changed")
    for f in expected_fams:
        ids=np.flatnonzero(c["family"]==f)
        source_test=set(np.flatnonzero((c["family"]==f)&test).tolist())
        got=q["source_row_index"][q["family"]==f].astype(int).tolist()
        if set(got)!=source_test or any(got.count(x)!=2 for x in source_test):
            raise RuntimeError("V3 challenge source-row replication mismatch: "+f)

    return {
      "controlRows":294,"interventionRows":294,"challengeRows":84,
      "trainRows":210,"ordinaryTestRows":42,"challengeRowsPerFamily":fam_counts,
      "fileSha256":{k:file_sha256(v) for k,v in paths.items()},
      "controlFeatureHash":dataset_array_hashes(c)["features"],
      "interventionFeatureHash":dataset_array_hashes(i)["features"],
      "challengeFeatureHash":dataset_array_hashes(q)["features"],
      "identityPassed":True,
    }


def no_optimizer_pairing_check(control_path,intervention_path):
    c=np.load(control_path,allow_pickle=False); i=np.load(intervention_path,allow_pickle=False)
    rows=[]
    for seed in SEEDS:
        cb,cs=paired_batches(c["state"],c["onset"],c["split"],c["has_negative_structure"],seed)
        ib,is_=paired_batches(i["state"],i["onset"],i["split"],i["has_negative_structure"],seed)
        if cs!=is_ or not np.array_equal(cb,ib):
            raise RuntimeError("paired batch mismatch")
        cm=initialize_model(seed,960); im=initialize_model(seed,960)
        if module_sha(cm)!=module_sha(im):
            raise RuntimeError("paired initialization mismatch")
        rows.append({"seed":seed,"modelInitSha256":module_sha(cm),"batchPlanSha256":batch_sha(cb)})
    if len({r["modelInitSha256"] for r in rows})!=3 or len({r["batchPlanSha256"] for r in rows})!=3:
        raise RuntimeError("distinct seed identity failure")
    return rows


def run_experiment(control_path,intervention_path,challenge_path,out_path):
    out=Path(out_path)
    if out.exists(): raise RuntimeError("refusing existing output path")
    validate_inputs(control_path,intervention_path,challenge_path)
    started=time.monotonic(); deadline=started+MAX_FIT_EVAL_SECONDS
    c=np.load(control_path,allow_pickle=False)
    i=np.load(intervention_path,allow_pickle=False)
    q=np.load(challenge_path,allow_pickle=False)
    pairs=[]

    for seed in SEEDS:
        cb,cs=paired_batches(c["state"],c["onset"],c["split"],c["has_negative_structure"],seed)
        ib,is_=paired_batches(i["state"],i["onset"],i["split"],i["has_negative_structure"],seed)
        if cs!=is_ or not np.array_equal(cb,ib):
            raise RuntimeError("paired V3 batch mismatch")
        cm=initialize_model(seed,960); im=initialize_model(seed,960)
        if module_sha(cm)!=module_sha(im):
            raise RuntimeError("paired V3 initialization mismatch")

        cfit=fit(cm,c["features"].astype(np.float32,copy=False),c["state"],c["onset"],cb,deadline)
        ifit=fit(im,i["features"].astype(np.float32,copy=False),i["state"],i["onset"],ib,deadline)
        if cfit["optimizerSteps"]!=500 or ifit["optimizerSteps"]!=500:
            raise RuntimeError("V3 training did not complete 500 steps")

        co=evaluate(cm,c,"test")
        io=evaluate(im,c,"test")
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
    optimizer_total=sum(p["control"]["fit"]["optimizerSteps"]+p["intervention"]["fit"]["optimizerSteps"] for p in pairs)
    elapsed=float(time.monotonic()-started)
    if optimizer_total!=3000 or elapsed>MAX_FIT_EVAL_SECONDS:
        raise RuntimeError("V3 execution ceiling failure")

    identity={
      "exactFrozenDatasetHashesVerified":True,
      "controlInterventionNonFeatureArraysBitIdentical":True,
      "interventionValidationTestFeaturesBitIdentical":True,
      "interventionChangedRowsExactlyTrain":True,
      "v3ChallengeExactly84Rows":True,
      "v3ChallengeExactly12RowsPerFamily":True,
      "v3ChallengeSourceRowsOnlyFrozenControlTest":True,
      "historicalS9TrainingChordStringsPreserved":True,
      "fixedThresholdsNoSearch":True,
      "exactSixModelsAnd3000Steps":True,
      "noAutomaticRetry":True,
    }
    criteria={**gate["criteria"],**identity}
    result={
      "schema":SCHEMA,
      "runSeeds":list(SEEDS),
      "pairs":pairs,
      "challengeDeltaSummary":gate["challengeDeltaSummary"],
      "ordinaryDeltaSummary":gate["ordinaryDeltaSummary"],
      "ordinaryNonChordFamilyStability":gate["ordinaryNonChordFamilyStability"],
      "criteria":criteria,
      "v3SyntheticTrainingGatePassed":bool(all(criteria.values())),
      "fixed":{"stateThreshold":0.5,"onsetThreshold":0.5,"thresholdSearch":False,"thresholdRetuning":False},
      "datasetIdentity":validate_inputs(control_path,intervention_path,challenge_path),
      "execution":{
        "modelCount":6,"optimizerStepsPerModel":500,"optimizerStepsTotal":optimizer_total,
        "fitEvalSeconds":elapsed,"automaticRetry":False,"paidComputeDollars":0,
        "p1Accessed":False,"p2Accessed":False,"p3Opened":False,
        "codespacesUsed":False,"vercelUsed":False,"productionMutation":False,
      },
      "meaning":"Final three-seed paired synthetic source-domain robustness test using V2 admitted training support and independently admitted V3 challenge."
    }
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SOURCE_DOMAIN_V3_TRAINING="+json.dumps({
      "gatePassed":result["v3SyntheticTrainingGatePassed"],
      "challengeDeltaSummary":result["challengeDeltaSummary"],
      "ordinaryDeltaSummary":result["ordinaryDeltaSummary"],
      "execution":result["execution"]
    },sort_keys=True))
    return result


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    v=sub.add_parser("verify")
    v.add_argument("--control",required=True); v.add_argument("--intervention",required=True); v.add_argument("--challenge",required=True)
    p=sub.add_parser("pairing-check")
    p.add_argument("--control",required=True); p.add_argument("--intervention",required=True)
    r=sub.add_parser("run")
    r.add_argument("--control",required=True); r.add_argument("--intervention",required=True); r.add_argument("--challenge",required=True); r.add_argument("--out",required=True)
    a=ap.parse_args()
    if a.cmd=="verify":
        print("V3_TRAINING_VERIFY="+json.dumps(validate_inputs(a.control,a.intervention,a.challenge),sort_keys=True))
    elif a.cmd=="pairing-check":
        print("V3_PAIRING_VERIFY="+json.dumps(no_optimizer_pairing_check(a.control,a.intervention),sort_keys=True))
    else:
        if int(os.environ.get("GITHUB_RUN_ATTEMPT","1"))!=1:
            raise RuntimeError("V3 training requires GitHub run attempt 1")
        run_experiment(a.control,a.intervention,a.challenge,a.out)

if __name__=="__main__":
    main()
