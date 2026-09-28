import json
from pathlib import Path
import numpy as np
import pytest
import torch

from synthetic.s13_pilot_v1 import (
    RETAIN_FRACTION, transformed_training_rows, build_datasets, evaluate_gate,
    validate_launch, validate_dataset_hashes, run_experiment
)
from synthetic.s11_pilot_v1 import initialize_model, module_sha, paired_batches, weighted_loss
from synthetic.s13_transform_design_review_v1 import BINS

def tiny_dataset(path):
    n=14; t=5
    family=np.array(["isolated"]*7+["chords"]*7)
    split=np.array(["train"]*4+["validation"]+["test"]*2+["train"]*4+["validation"]+["test"]*2)
    features=np.zeros((n,t,BINS),dtype=np.float32)
    state=np.full((n,6,t),-1,dtype=np.int64)
    onset=np.zeros((n,6,t),dtype=np.int64)
    for i in range(n):
        features[i,1:,i%BINS]=1
        onset[i,0,1]=1
        state[i,0,1:]=0
    arrays=dict(features=features,state=state,onset=onset,family=family,split=split,
                negative_only=np.zeros(n,dtype=bool),has_negative_structure=np.zeros(n,dtype=bool),
                refs_json=np.array(["[]"]*n),template_id=np.array([f"x{i}" for i in range(n)]))
    np.savez_compressed(path,**arrays)

def test_family_balanced_subset_is_deterministic_and_half():
    family=np.array(["a"]*6+["b"]*5); split=np.array(["train"]*11)
    a,pa=transformed_training_rows(family,split)
    b,pb=transformed_training_rows(family,split)
    assert np.array_equal(a,b) and pa==pb
    assert pa["a"]["transformedRows"]==3
    assert pa["b"]["transformedRows"]==2

def test_dataset_builder_preserves_nonfeatures_and_scopes(tmp_path):
    c=tmp_path/"c.npz"; tiny_dataset(c)
    i=tmp_path/"i.npz"; q=tmp_path/"q.npz"; r=tmp_path/"receipt.json"
    receipt=build_datasets(c,i,q,r,expected_examples=14)
    cd=np.load(c,allow_pickle=False); id_=np.load(i,allow_pickle=False); qd=np.load(q,allow_pickle=False)
    for k in cd.files:
        if k!="features":
            assert np.array_equal(cd[k],id_[k]) and np.array_equal(cd[k],qd[k])
    assert np.array_equal(cd["features"][cd["split"]!="train"],id_["features"][id_["split"]!="train"])
    assert np.array_equal(cd["features"][cd["split"]!="test"],qd["features"][qd["split"]!="test"])
    assert receipt["guards"]["modelRun"] is False and receipt["guards"]["optimizerSteps"]==0

def test_pair_initialization_and_batches_are_exact():
    m1=initialize_model(20260927,960); m2=initialize_model(20260927,960)
    assert module_sha(m1)==module_sha(m2)
    n=2; t=4
    s=np.full((n,6,t),-1,dtype=np.int64); o=np.zeros((n,6,t),dtype=np.int64)
    # positive onset + active non-onset on both clips; inactive frames split across
    # negative-structure and ordinary clips so all four frozen strata are present.
    o[:,0,1]=1; s[:,0,1]=0; s[:,0,2]=0
    split=np.array(["train","train"]); neg=np.array([True,False])
    b1,strata1=paired_batches(s,o,split,neg,20260927)
    b2,strata2=paired_batches(s,o,split,neg,20260927)
    assert strata1==strata2
    assert np.array_equal(b1,b2)

def test_weighted_loss_gradient_path_is_finite_and_unchanged():
    m=initialize_model(20260927,960)
    x=torch.zeros((2,960),dtype=torch.float32)
    sl,ol=m(x)
    st=torch.full((2,6),-1,dtype=torch.long); st[0,0]=0
    ot=torch.zeros((2,6),dtype=torch.long); ot[0,0]=1
    loss=weighted_loss(sl,ol,st,ot)
    loss.backward()
    assert torch.isfinite(loss)
    assert all(p.grad is None or torch.isfinite(p.grad).all() for p in m.parameters())

def metric(f1=.8,rec=.8,prec=.8,state=.6,joint=.5,fp=.05):
    return {
      "pitchOnset":{"truePositive":8,"falsePositive":2,"falseNegative":2,"precision":prec,"recall":rec,"f1":f1},
      "pitchOnsetOffset":{"f1":.7},
      "admission":{"stateAdmissionFraction":state,"jointAdmissionFraction":joint},
      "negativeOnlyFalsePositiveEvents":1,"negativeOnlySeconds":20.0,
      "negativeOnlyFalsePositiveEventsPerSecond":fp,
    }

def pair(chdf1=.05,chdrec=.08,ordf1=0,ordprec=0,ords=0,ordj=0):
    co=metric(); io=metric(f1=.8+ordf1,prec=.8+ordprec,state=.6+ords,joint=.5+ordj)
    cq=metric(f1=.7,rec=.7); iq=metric(f1=.7+chdf1,rec=.7+chdrec)
    return {"control":{"fit":{"optimizerSteps":500},"ordinary":co,"challenge":cq},
            "intervention":{"fit":{"optimizerSteps":500},"ordinary":io,"challenge":iq},
            "ordinaryDelta":{"onsetF1":ordf1,"onsetRecall":0,"onsetPrecision":ordprec,"stateAdmission":ords,"jointAdmission":ordj},
            "challengeDelta":{"onsetF1":chdf1,"onsetRecall":chdrec,"onsetPrecision":0,"stateAdmission":0,"jointAdmission":0},
            "ordinaryNonChordFamilyF1Loss":{"isolated":0.0},"pairIdentity":{"initializationIdentical":True,"batchIndicesIdentical":True}}

def test_gate_exact_boundaries_pass():
    g=evaluate_gate([pair(),pair(),pair()])
    assert g["gatePassed"] is True

@pytest.mark.parametrize("kwargs",[
    {"chdf1":0.0},{"chdrec":0.0},{"ordf1":-0.030001},{"ordprec":-0.030001},{"ords":-0.030001},{"ordj":-0.040001}
])
def test_gate_rejects_boundary_violations(kwargs):
    ps=[pair(),pair(),pair()]
    ps[0]=pair(**kwargs)
    assert evaluate_gate(ps)["gatePassed"] is False

def test_run_refuses_existing_output(tmp_path):
    out=tmp_path/"exists.json"; out.write_text("x")
    with pytest.raises(RuntimeError,match="existing output"):
        run_experiment("none","none","none",out)

def test_launch_rejects_unarmed_reused_attempt_and_wrong_branch(tmp_path,monkeypatch):
    root=tmp_path
    (root/"docs/astra").mkdir(parents=True)
    spec=root/"docs/astra/SYNTHETIC_S13_SPEC_V1.json"; spec.write_text("{}")
    src=root/"source.py"; src.write_text("x")
    scope=root/"scope.json"
    scope.write_text(json.dumps({"schema":"astra-synthetic-s13-run-scope-v1",
        "sourcePaths":{"x":"source.py"},"sourceGitBlobs":{"x":"bad"}}))
    launch=root/"launch.json"; history=root/"history.json"
    history.write_text(json.dumps({"schema":"astra-synthetic-s13-execution-history-v1","consumedLaunchIdentities":[]}))
    launch.write_text(json.dumps({"schema":"astra-synthetic-s13-launch-v1","status":"disabled",
      "launchIdentity":"x","scopeGitBlob":"x","specGitBlob":"x"}))
    with pytest.raises(RuntimeError,match="not armed"):
        validate_launch(root,launch,history,scope)
    launch.write_text(json.dumps({"schema":"astra-synthetic-s13-launch-v1","status":"armed",
      "launchIdentity":"x","scopeGitBlob":"x","specGitBlob":"x"}))
    history.write_text(json.dumps({"schema":"astra-synthetic-s13-execution-history-v1","consumedLaunchIdentities":["x"]}))
    with pytest.raises(RuntimeError,match="already consumed"):
        validate_launch(root,launch,history,scope)
    history.write_text(json.dumps({"schema":"astra-synthetic-s13-execution-history-v1","consumedLaunchIdentities":[]}))
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT","2")
    with pytest.raises(RuntimeError,match="attempt"):
        validate_launch(root,launch,history,scope)

def test_retain_fraction_is_frozen():
    assert RETAIN_FRACTION==0.50


def test_dataset_hash_validation_fails_closed(tmp_path):
    c=tmp_path/"c.npz"; tiny_dataset(c)
    i=tmp_path/"i.npz"; q=tmp_path/"q.npz"; r=tmp_path/"receipt.json"
    receipt=build_datasets(c,i,q,r,expected_examples=14)
    with pytest.raises(RuntimeError,match="missing"):
        validate_dataset_hashes({},c,i,q)
    scope={"datasetArrayHashes":receipt["arrayHashes"]}
    assert validate_dataset_hashes(scope,c,i,q) is True
    bad=json.loads(json.dumps(scope))
    bad["datasetArrayHashes"]["intervention"]["features"]="0"*64
    with pytest.raises(RuntimeError,match="intervention"):
        validate_dataset_hashes(bad,c,i,q)
