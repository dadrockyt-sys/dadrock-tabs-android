#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, time
from pathlib import Path
import numpy as np

from synthetic.s11_pilot_v1 import (
    RUN_SEEDS, initialize_model, paired_batches, fit, evaluate, module_sha, batch_sha,
)

SCHEMA="astra-synthetic-onset-envelope-s12-pilot-v1"
BLEND_MIN=0.25
BLEND_MAX=0.75
CHALLENGE_BLEND=0.70
ROOT_SEED=20260927
MAX_TOTAL_STEPS=3000

def _seed(*parts):
    import hashlib
    raw="|".join(str(x) for x in parts).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8],"big") & 0x7fffffff

def onset_frames(onset):
    x=np.asarray(onset)
    if x.ndim!=2: raise ValueError("onset array must be strings x frames")
    return sorted(int(i) for i in np.flatnonzero(np.any(x>0,axis=0)) if int(i)>0)

def soften_features(features,onset,blend):
    x=np.asarray(features,dtype=np.float32).copy()
    if x.ndim!=2: raise ValueError("features must be frames x bins")
    if not (0.0<=float(blend)<=1.0): raise ValueError("blend out of range")
    for f in onset_frames(onset):
        prev=x[f-1].copy()
        x[f]=(1.0-blend)*x[f]+blend*prev
        if f+1<len(x):
            x[f+1]=(1.0-blend)*x[f+1]+blend*x[f]
    np.clip(x,0.0,1.0,out=x)
    if not np.isfinite(x).all(): raise RuntimeError("nonfinite softened features")
    return x

def build(control_path,intervention_out,challenge_out,receipt_out):
    d=np.load(control_path,allow_pickle=False)
    ia={k:np.array(d[k],copy=True) for k in d.files}
    qa={k:np.array(d[k],copy=True) for k in d.files}
    if len(d["features"])!=294: raise RuntimeError("unexpected S12 control size")
    profiles=[]; train_n=0; test_n=0
    for i in range(len(d["features"])):
        split=str(d["split"][i])
        if split=="train":
            rng=np.random.RandomState(_seed(ROOT_SEED,"s12-blend",i))
            blend=float(rng.uniform(BLEND_MIN,BLEND_MAX))
            ia["features"][i]=soften_features(d["features"][i],d["onset"][i],blend)
            profiles.append({"rowIndex":int(i),"blend":blend})
            train_n+=1
        elif split=="test":
            qa["features"][i]=soften_features(d["features"][i],d["onset"][i],CHALLENGE_BLEND)
            test_n+=1
    for k in d.files:
        if k!="features":
            if not np.array_equal(d[k],ia[k]) or not np.array_equal(d[k],qa[k]):
                raise RuntimeError("non-feature arrays changed: "+k)
    heldout=d["split"]!="train"
    non_test=d["split"]!="test"
    if not np.array_equal(d["features"][heldout],ia["features"][heldout]):
        raise RuntimeError("intervention heldout changed")
    if not np.array_equal(d["features"][non_test],qa["features"][non_test]):
        raise RuntimeError("challenge non-test changed")
    np.savez_compressed(intervention_out,**ia)
    np.savez_compressed(challenge_out,**qa)
    receipt={
      "schema":"astra-s12-dataset-receipt-v1",
      "controlExamples":int(len(d["features"])),
      "trainingRowsTransformed":int(train_n),
      "challengeTestRowsTransformed":int(test_n),
      "blendRange":[BLEND_MIN,BLEND_MAX],
      "challengeBlend":CHALLENGE_BLEND,
      "labelsAndReferencesBitIdentical":True,
      "ordinaryHeldoutFeaturesBitIdentical":True,
      "challengeNonTestFeaturesBitIdentical":True,
      "profiles":profiles,
      "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False,"externalAudioAssets":False}
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
    return {"mean":float(a.mean()),"median":float(np.median(a)),"minimum":float(a.min()),
            "positiveCount":int(np.sum(a>0))}

def run(control_path,intervention_path,challenge_path,out_path):
    started=time.monotonic(); deadline=started+5400.0
    c=np.load(control_path,allow_pickle=False)
    i=np.load(intervention_path,allow_pickle=False)
    q=np.load(challenge_path,allow_pickle=False)
    if any(len(x["features"])!=294 for x in (c,i,q)): raise RuntimeError("dataset size mismatch")
    for k in c.files:
        if k!="features" and (not np.array_equal(c[k],i[k]) or not np.array_equal(c[k],q[k])):
            raise RuntimeError("identity mismatch "+k)
    if not np.array_equal(c["features"][c["split"]!="train"],i["features"][i["split"]!="train"]):
        raise RuntimeError("ordinary heldout mismatch")

    pairs=[]
    for seed in RUN_SEEDS:
        cb,cs=paired_batches(c["state"],c["onset"],c["split"],c["has_negative_structure"],seed)
        ib,is_=paired_batches(i["state"],i["onset"],i["split"],i["has_negative_structure"],seed)
        if cs!=is_ or not np.array_equal(cb,ib): raise RuntimeError("paired batch mismatch")
        cm=initialize_model(seed,960); im=initialize_model(seed,960)
        if module_sha(cm)!=module_sha(im): raise RuntimeError("paired initialization mismatch")
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
          "pairIdentity":{"initializationIdentical":True,"batchIndicesIdentical":True}
        })

    keys=("onsetF1","onsetRecall","onsetPrecision","onsetOffsetF1","stateAdmission","jointAdmission")
    chal={k:summarize([p["challengeDelta"][k] for p in pairs]) for k in keys}
    ordinary={k:summarize([p["ordinaryDelta"][k] for p in pairs]) for k in keys}
    fams={}
    for fam in pairs[0]["ordinaryNonChordFamilyF1Loss"]:
        losses=[p["ordinaryNonChordFamilyF1Loss"][fam] for p in pairs]
        fams[fam]={"lossOver0_15Count":int(sum(x>.15 for x in losses)),"losses":losses}
    criteria={
      "challengeOnsetF1GainPositive3of3":chal["onsetF1"]["positiveCount"]==3,
      "challengeOnsetRecallGainPositive3of3":chal["onsetRecall"]["positiveCount"]==3,
      "meanChallengeOnsetF1GainAtLeast0_05":chal["onsetF1"]["mean"]>=.05,
      "meanChallengeOnsetRecallGainAtLeast0_08":chal["onsetRecall"]["mean"]>=.08,
      "noOrdinaryOnsetF1LossOver0_03":all(p["ordinaryDelta"]["onsetF1"]>=-.03 for p in pairs),
      "noOrdinaryStateAdmissionLossOver0_03":all(p["ordinaryDelta"]["stateAdmission"]>=-.03 for p in pairs),
      "noOrdinaryJointAdmissionLossOver0_04":all(p["ordinaryDelta"]["jointAdmission"]>=-.04 for p in pairs),
      "noChallengePrecisionLossOver0_05":all(p["challengeDelta"]["onsetPrecision"]>=-.05 for p in pairs),
      "challengeNegativeOnlyFpAtMost0_10EverySeed":all(p["intervention"]["challenge"]["negativeOnlyFalsePositiveEventsPerSecond"]<=.10 for p in pairs),
      "ordinaryNonChordFamilyLossOver0_15InAtMostOneSeed":all(v["lossOver0_15Count"]<=1 for v in fams.values()),
      "allSix500StepsFinitePairedFixedThresholds":(
        all(p["control"]["fit"]["optimizerSteps"]==500 and p["intervention"]["fit"]["optimizerSteps"]==500 for p in pairs)
        and all(all(p["pairIdentity"].values()) for p in pairs)
        and all(math.isfinite(v["mean"]) for v in list(chal.values())+list(ordinary.values()))
      )
    }
    result={
      "schema":SCHEMA,"runSeeds":list(RUN_SEEDS),
      "fixed":{"blendRange":[BLEND_MIN,BLEND_MAX],"challengeBlend":CHALLENGE_BLEND,
               "stateThreshold":0.5,"onsetThreshold":0.5,"thresholdSearch":False,"thresholdRetuning":False},
      "pairs":pairs,"challengeDeltaSummary":chal,"ordinaryDeltaSummary":ordinary,
      "ordinaryNonChordFamilyStability":fams,"criteria":criteria,"s12GatePassed":all(criteria.values()),
      "execution":{"modelCount":6,"optimizerStepsTotal":sum(p["control"]["fit"]["optimizerSteps"]+p["intervention"]["fit"]["optimizerSteps"] for p in pairs),
                   "fitEvalSeconds":float(time.monotonic()-started),"automaticRetry":False,"thresholdSearch":False,"paidComputeDollars":0},
      "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False,"codespacesUsed":False,"vercelUsed":False,"productionMutation":False},
      "meaning":"Synthetic-only paired robustness test of training CQT onset-transition diversity under a prospectively frozen soft-onset challenge."
    }
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS: raise RuntimeError("optimizer ceiling")
    Path(out_path).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("S12_RESULT="+json.dumps(result,sort_keys=True))

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    b=sub.add_parser("build")
    b.add_argument("--control-dataset",required=True); b.add_argument("--intervention-out",required=True)
    b.add_argument("--challenge-out",required=True); b.add_argument("--receipt-out",required=True)
    r=sub.add_parser("run")
    r.add_argument("--control-dataset",required=True); r.add_argument("--intervention-dataset",required=True)
    r.add_argument("--challenge-dataset",required=True); r.add_argument("--out",required=True)
    a=ap.parse_args()
    if a.cmd=="build": print("S12_DATASET="+json.dumps(build(a.control_dataset,a.intervention_out,a.challenge_out,a.receipt_out),sort_keys=True))
    else: run(a.control_dataset,a.intervention_dataset,a.challenge_dataset,a.out)

if __name__=="__main__": main()
