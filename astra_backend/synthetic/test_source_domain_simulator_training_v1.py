import json
from pathlib import Path

import numpy as np
import pytest
import torch

from synthetic.source_domain_simulator_training_v1 import (
    evaluate_gate, validate_launch, validate_datasets, run_experiment, git_blob_sha,
)
from synthetic.s11_pilot_v1 import initialize_model, module_sha, paired_batches, weighted_loss

def metric(f1=.8,rec=.8,prec=.8,state=.6,joint=.5,fp=.05):
    return {
      "pitchOnset":{"truePositive":8,"falsePositive":2,"falseNegative":2,
                    "precision":prec,"recall":rec,"f1":f1},
      "pitchOnsetOffset":{"f1":.7},
      "admission":{"stateAdmissionFraction":state,"jointAdmissionFraction":joint},
      "negativeOnlyFalsePositiveEvents":1,
      "negativeOnlySeconds":20.0,
      "negativeOnlyFalsePositiveEventsPerSecond":fp,
    }

def pair(chf1=.05,chrec=.08,chprec=0.0,ordf1=0.0,ordprec=0.0,ords=0.0,ordj=0.0):
    co=metric()
    io=metric(f1=.8+ordf1,prec=.8+ordprec,state=.6+ords,joint=.5+ordj)
    cq=metric(f1=.70,rec=.70)
    iq=metric(f1=.70+chf1,rec=.70+chrec,prec=.8+chprec)
    return {
      "control":{"fit":{"optimizerSteps":500},"ordinary":co,"challenge":cq},
      "intervention":{"fit":{"optimizerSteps":500},"ordinary":io,"challenge":iq},
      "ordinaryDelta":{"onsetF1":ordf1,"onsetRecall":0.0,"onsetPrecision":ordprec,
                       "stateAdmission":ords,"jointAdmission":ordj},
      "challengeDelta":{"onsetF1":chf1,"onsetRecall":chrec,"onsetPrecision":chprec,
                        "stateAdmission":0.0,"jointAdmission":0.0},
      "ordinaryNonChordFamilyF1Loss":{"isolated":max(0.0,-ordf1)},
      "pairIdentity":{"initializationIdentical":True,"batchIndicesIdentical":True},
    }

def test_gate_exact_frozen_boundaries_pass():
    g=evaluate_gate([pair(),pair(),pair()])
    assert g["gatePassed"] is True
    assert all(g["criteria"].values())

@pytest.mark.parametrize("kwargs",[
    {"chf1":0.0},
    {"chrec":0.0},
    {"chprec":-0.050001},
    {"ordf1":-0.030001},
    {"ordprec":-0.030001},
    {"ords":-0.030001},
    {"ordj":-0.040001},
])
def test_gate_rejects_boundary_violations(kwargs):
    ps=[pair(),pair(),pair()]
    ps[0]=pair(**kwargs)
    assert evaluate_gate(ps)["gatePassed"] is False

def test_gate_requires_exactly_three_pairs():
    with pytest.raises(ValueError):
        evaluate_gate([pair(),pair()])

def test_pair_initialization_and_batches_are_exact_without_optimizer():
    m1=initialize_model(20260927,960)
    m2=initialize_model(20260927,960)
    assert module_sha(m1)==module_sha(m2)

    n=2; t=4
    state=np.full((n,6,t),-1,dtype=np.int64)
    onset=np.zeros((n,6,t),dtype=np.int64)
    onset[:,0,1]=1; state[:,0,1]=0; state[:,0,2]=0
    split=np.array(["train","train"])
    neg=np.array([True,False])
    b1,s1=paired_batches(state,onset,split,neg,20260927)
    b2,s2=paired_batches(state,onset,split,neg,20260927)
    assert s1==s2
    assert np.array_equal(b1,b2)

def test_weighted_loss_gradient_path_is_finite_no_optimizer_step():
    m=initialize_model(20260927,960)
    x=torch.zeros((2,960),dtype=torch.float32)
    sl,ol=m(x)
    st=torch.full((2,6),-1,dtype=torch.long); st[0,0]=0
    ot=torch.zeros((2,6),dtype=torch.long); ot[0,0]=1
    loss=weighted_loss(sl,ol,st,ot)
    loss.backward()
    assert torch.isfinite(loss)
    assert all(p.grad is None or torch.isfinite(p.grad).all() for p in m.parameters())

def test_run_refuses_existing_output_before_dataset_or_optimizer_access(tmp_path):
    out=tmp_path/"result.json"; out.write_text("occupied")
    with pytest.raises(RuntimeError,match="existing output"):
        run_experiment("missing","missing","missing",out)

def _launch_fixture(tmp_path):
    root=tmp_path
    (root/"docs/astra").mkdir(parents=True)
    design=root/"docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_DESIGN_V1.md"
    spec=root/"docs/astra/SOURCE_DOMAIN_SIMULATOR_TRAINING_SPEC_V1.json"
    history=root/"history.json"; scope=root/"scope.json"; launch=root/"launch.json"; src=root/"source.py"
    design.write_text("design"); spec.write_text("{}"); src.write_text("source")
    history.write_text(json.dumps({
      "schema":"astra-source-domain-simulator-training-execution-history-v1",
      "consumedLaunchIdentities":[]
    }))
    scope_obj={
      "schema":"astra-source-domain-simulator-training-run-scope-v1",
      "designGitBlob":git_blob_sha(design),
      "specGitBlob":git_blob_sha(spec),
      "historyGitBlob":git_blob_sha(history),
      "sourcePaths":{"runner":"source.py"},
      "sourceGitBlobs":{"runner":git_blob_sha(src)}
    }
    scope.write_text(json.dumps(scope_obj))
    execution={"maxModels":6,"optimizerStepsPerModel":500,"maxTotalOptimizerSteps":3000,
      "stateThreshold":.5,"onsetThreshold":.5,"thresholdSearch":False,
      "thresholdRetuning":False,"automaticRetry":False,"paidComputeDollars":0,
      "p1Access":False,"p2Access":False,"p3Access":False}
    launch.write_text(json.dumps({
      "schema":"astra-source-domain-simulator-training-launch-v1","status":"armed",
      "launchIdentity":"unit-launch","scopeGitBlob":git_blob_sha(scope),
      "specGitBlob":git_blob_sha(spec),"execution":execution
    }))
    return root,launch,history,scope

def test_launch_validation_accepts_exact_frozen_fixture(tmp_path,monkeypatch):
    root,launch,history,scope=_launch_fixture(tmp_path)
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT","1")
    monkeypatch.setenv("GITHUB_REF_NAME","astra-work")
    a,_,_=validate_launch(root,launch,history,scope)
    assert a["launchIdentity"]=="unit-launch"

def test_launch_rejects_unarmed_reused_attempt_wrong_branch_and_ceiling(tmp_path,monkeypatch):
    root,launch,history,scope=_launch_fixture(tmp_path)
    x=json.loads(launch.read_text()); x["status"]="disabled"; launch.write_text(json.dumps(x))
    with pytest.raises(RuntimeError,match="not armed"):
        validate_launch(root,launch,history,scope)

    root,launch,history,scope=_launch_fixture(tmp_path/"reuse")
    h=json.loads(history.read_text()); h["consumedLaunchIdentities"]=["unit-launch"]; history.write_text(json.dumps(h))
    # Refresh scope history pin and launch scope pin so rejection is specifically reuse.
    s=json.loads(scope.read_text()); s["historyGitBlob"]=git_blob_sha(history); scope.write_text(json.dumps(s))
    l=json.loads(launch.read_text()); l["scopeGitBlob"]=git_blob_sha(scope); launch.write_text(json.dumps(l))
    with pytest.raises(RuntimeError,match="already consumed"):
        validate_launch(root,launch,history,scope)

    root,launch,history,scope=_launch_fixture(tmp_path/"attempt")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT","2")
    with pytest.raises(RuntimeError,match="attempt"):
        validate_launch(root,launch,history,scope)

    root,launch,history,scope=_launch_fixture(tmp_path/"branch")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT","1"); monkeypatch.setenv("GITHUB_REF_NAME","main")
    with pytest.raises(RuntimeError,match="wrong branch"):
        validate_launch(root,launch,history,scope)

    root,launch,history,scope=_launch_fixture(tmp_path/"ceiling")
    monkeypatch.setenv("GITHUB_REF_NAME","astra-work")
    l=json.loads(launch.read_text()); l["execution"]["maxModels"]=7; launch.write_text(json.dumps(l))
    with pytest.raises(RuntimeError,match="ceiling"):
        validate_launch(root,launch,history,scope)

def test_dataset_validator_rejects_missing_files():
    with pytest.raises(Exception):
        validate_datasets("no-control.npz","no-intervention.npz","no-challenge.npz")
