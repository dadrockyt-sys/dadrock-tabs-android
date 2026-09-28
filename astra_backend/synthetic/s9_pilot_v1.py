#!/usr/bin/env python3
"""Astra S9 synthetic-only chord-voicing-diversity experiment.

Only the 30 training chord voicing assignments differ. Control uses the frozen
10 voicings x 3 variants. Intervention uses 30 unique deterministic voicings,
one per paired control chord slot, while reusing each slot's exact original
timbre RNG key. Validation/test and all non-chord arrays are bit-identical.
"""
from __future__ import annotations

import argparse, hashlib, json, math, time
from pathlib import Path

import numpy as np
from scipy.signal import lfilter, resample_poly
import torch

from synthetic.s0_pilot_v1 import (
    ROOT_SEED, INTERNAL_SR, OUTPUT_SR, CLIP_SECONDS, OPEN_MIDI,
    EXAMPLES, AUDIO_SECONDS, HOP_LENGTH_SAMPLES, SAMPLE_RATE_HZ,
    CQT_BINS, _seed, _event, _plucked_component, build_template,
    targets_for_template, extract_cqt_features, rms_normalize,
)
from synthetic.s1_pilot_v1 import build_sampling_strata
from synthetic.s2_pilot_v1 import array_content_sha256, dataset_array_hashes
from synthetic.s6_pilot_v1 import initialize_arm, module_sha, fit_arm, evaluate_arm, precompute_batches, batch_plan_sha256

SCHEMA="astra-synthetic-data-diversity-s9-pilot-v1"
MAX_TOTAL_STEPS=1000
CHORD_FAMILY="chords"
TRAIN_CHORD_CLIPS=30
CONTROL_UNIQUE_VOICINGS=10
INTERVENTION_UNIQUE_VOICINGS=30


def chord_signature(template):
    seg=template["segments"]
    if len(seg)!=6:
        raise RuntimeError("S9 chord template must contain six events")
    strings=tuple(int(x["string"]) for x in seg[:3])
    frets=tuple(int(x["fret"]) for x in seg)
    return strings+frets


def signature_sha(signatures):
    raw=json.dumps([list(x) for x in signatures],separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


def intervention_chord_template(slot):
    """Create one unique deterministic 3-string/two-attack voicing for a slot."""
    if not 0 <= int(slot) < TRAIN_CHORD_CLIPS:
        raise ValueError("S9 chord slot out of range")
    # Fail-closed deterministic rejection sampling in the vanishingly unlikely
    # event a generated signature collides with an earlier slot.
    used=set()
    for prior in range(slot+1):
        chosen=None
        for attempt in range(100):
            rng=np.random.RandomState(_seed(ROOT_SEED,"s9-chord-voicing",prior,attempt))
            strings=sorted(rng.choice(np.arange(6),size=3,replace=False).tolist())
            frets=[int(rng.randint(0,10)) for _ in range(6)]
            sig=tuple(strings+frets)
            if sig not in used:
                chosen=(strings,frets,sig)
                break
        if chosen is None:
            raise RuntimeError("unable to construct unique S9 chord signature")
        used.add(chosen[2])
    strings,frets,sig=chosen
    rows=[]
    k=0
    for st in (.32,1.08):
        for s in strings:
            rows.append(_event(s,frets[k],st,st+.48))
            k+=1
    return {
      "family":"chords",
      "baseIndex":int(slot),
      "templateId":f"s9-chords:{slot:02d}",
      "split":"train",
      "segments":rows,
      "negativeOnly":False,
      "hasNegativeStructure":False,
    }


def render_waveform_with_timbre_key(template, control_template_id, variant):
    """Render target voicing while using the paired control slot's exact timbre RNG key."""
    trng=np.random.RandomState(_seed(ROOT_SEED,"timbre",control_template_id,variant))
    n=int(round(CLIP_SECONDS*INTERNAL_SR))
    audio=np.zeros(n,dtype=np.float64)
    damping=float(trng.uniform(.75,1.75))
    pick=float(trng.uniform(.12,.42))
    brightness=float(trng.uniform(.66,.88))
    body_a=float(trng.uniform(.82,.94))
    for row in template["segments"]:
        start=int(round(row["start"]*INTERNAL_SR))
        end=int(round(row["end"]*INTERNAL_SR))
        if end<=start or start>=n: continue
        end=min(n,end)
        pitch=OPEN_MIDI[row["string"]]+row["fret"]
        freq=440.0*(2.0**((pitch-69)/12.0))
        d=damping*(4.5 if row["palm"] else 1.0)*(1.0+.04*row["string"])
        comp=_plucked_component(
            freq,(end-start)/INTERNAL_SR,INTERNAL_SR,trng,
            damping=d,pick_position=pick,brightness=brightness,
            transient=row["attack"],soft=row["soft"],
        )
        audio[start:end]+=comp[:end-start]
    audio += trng.normal(0,1,n)*0.00025
    audio=lfilter([1.0-body_a],[1.0,-body_a],audio)
    peak=float(np.max(np.abs(audio)))
    if peak>0: audio=.78*audio/peak
    out=resample_poly(audio,1,2).astype(np.float32)
    want=int(round(CLIP_SECONDS*OUTPUT_SR))
    if len(out)<want: out=np.pad(out,(0,want-len(out)))
    elif len(out)>want: out=out[:want]
    if not np.isfinite(out).all(): raise RuntimeError("nonfinite S9 audio")
    return out


def _array_sha(x):
    return array_content_sha256(np.asarray(x))


def build_intervention_dataset(control_npz, intervention_out, receipt_out):
    started=time.monotonic()
    d=np.load(control_npz,allow_pickle=False)
    arrays={k:np.array(d[k],copy=True) for k in d.files}
    if len(arrays["features"])!=EXAMPLES or float(AUDIO_SECONDS)!=588.0:
        raise RuntimeError("unexpected S9 control corpus")

    family=arrays["family"]; split=arrays["split"]; tids=arrays["template_id"]
    chord_train=np.flatnonzero((family==CHORD_FAMILY)&(split=="train"))
    if len(chord_train)!=TRAIN_CHORD_CLIPS:
        raise RuntimeError("control must contain exactly 30 train chord clips")

    control_signatures=[]
    for base in range(10):
        sig=chord_signature(build_template("chords",base))
        control_signatures.append(sig)
    if len(set(control_signatures))!=CONTROL_UNIQUE_VOICINGS:
        raise RuntimeError("control chord signature uniqueness mismatch")

    intervention_templates=[intervention_chord_template(i) for i in range(TRAIN_CHORD_CLIPS)]
    intervention_signatures=[chord_signature(t) for t in intervention_templates]
    if len(set(intervention_signatures))!=INTERVENTION_UNIQUE_VOICINGS:
        raise RuntimeError("intervention chord signatures are not all unique")

    pairing=[]
    for slot,row_idx in enumerate(chord_train.tolist()):
        control_tid=str(tids[row_idx])
        if not control_tid.startswith("chords:"):
            raise RuntimeError("unexpected control chord template id")
        # Frozen control ordering is base 0..9, variant 0..2.
        base=slot//3
        variant=slot%3
        expected_tid=f"chords:{base:02d}"
        if control_tid!=expected_tid:
            raise RuntimeError("unexpected chord slot order")
        template=intervention_templates[slot]
        audio=render_waveform_with_timbre_key(template,expected_tid,variant)
        feat=extract_cqt_features(rms_normalize(audio)).squeeze(0).T.astype(np.float32,copy=False)
        if feat.shape!=arrays["features"][row_idx].shape or not np.isfinite(feat).all():
            raise RuntimeError("invalid S9 replacement feature shape")
        state,onset,refs=targets_for_template(template,feat.shape[0])
        arrays["features"][row_idx]=feat
        arrays["state"][row_idx]=state
        arrays["onset"][row_idx]=onset
        arrays["template_id"][row_idx]=template["templateId"]
        arrays["refs_json"][row_idx]=json.dumps(refs,separators=(",",":"),sort_keys=True)
        pairing.append({
          "slot":slot,"rowIndex":row_idx,"controlTemplateId":expected_tid,
          "variant":variant,"timbreRngSeed":int(_seed(ROOT_SEED,"timbre",expected_tid,variant)),
          "interventionTemplateId":template["templateId"],"signature":list(intervention_signatures[slot]),
        })

    # Identity guards: only train chord rows may differ.
    unchanged=np.ones(len(family),dtype=bool)
    unchanged[chord_train]=False
    for k in ("features","state","onset","refs_json","family","split","negative_only","has_negative_structure"):
        if not np.array_equal(np.asarray(d[k])[unchanged],arrays[k][unchanged]):
            raise RuntimeError("non-chord/heldout data changed: "+k)

    heldout=(split!="train")
    for k in ("features","state","onset","refs_json","family","split"):
        if not np.array_equal(np.asarray(d[k])[heldout],arrays[k][heldout]):
            raise RuntimeError("validation/test data changed: "+k)

    cstrata=build_sampling_strata(d["state"],d["onset"],d["split"],d["has_negative_structure"])
    istrata=build_sampling_strata(arrays["state"],arrays["onset"],arrays["split"],arrays["has_negative_structure"])
    for k in cstrata:
        if not np.array_equal(cstrata[k],istrata[k]):
            raise RuntimeError("S9 sampler stratum membership changed: "+k)

    np.savez_compressed(intervention_out,**arrays)
    receipt={
      "schema":"astra-s9-intervention-dataset-receipt-v1",
      "controlExamples":int(len(family)),"interventionExamples":int(len(family)),
      "audioSecondsPerArm":float(AUDIO_SECONDS),
      "trainChordClipsPerArm":TRAIN_CHORD_CLIPS,
      "controlUniqueTrainChordVoicings":len(set(control_signatures)),
      "interventionUniqueTrainChordVoicings":len(set(intervention_signatures)),
      "controlSignatureSha256":signature_sha(control_signatures),
      "interventionSignatureSha256":signature_sha(intervention_signatures),
      "pairedTimbreVariantCounts":{str(v):sum(1 for x in pairing if x["variant"]==v) for v in (0,1,2)},
      "pairing":pairing,
      "validationTestBitIdentical":True,
      "nonChordBitIdentical":True,
      "samplerStrataIdentical":True,
      "replacementChordClipsRendered":TRAIN_CHORD_CLIPS,
      "renderSeconds":float(time.monotonic()-started),
      "externalAudioAssets":False,
      "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False,"codespacesUsed":False,"vercelUsed":False},
    }
    Path(receipt_out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    return receipt


def run(control_dataset,intervention_dataset,out,control_model,intervention_model,identity_out):
    started=time.monotonic(); deadline=started+3600.0
    c=np.load(control_dataset,allow_pickle=False)
    i=np.load(intervention_dataset,allow_pickle=False)
    if len(c["features"])!=294 or len(i["features"])!=294:
        raise RuntimeError("S9 dataset size mismatch")

    # Reconfirm frozen identity conditions before optimization.
    unchanged=~((c["family"]=="chords")&(c["split"]=="train"))
    heldout=(c["split"]!="train")
    for k in ("features","state","onset","refs_json","family","split","negative_only","has_negative_structure"):
        if not np.array_equal(c[k][unchanged],i[k][unchanged]):
            raise RuntimeError("S9 unchanged subset mismatch: "+k)
    for k in ("features","state","onset","refs_json"):
        if not np.array_equal(c[k][heldout],i[k][heldout]):
            raise RuntimeError("S9 heldout mismatch: "+k)

    cbatches,cstrata=precompute_batches(c["state"],c["onset"],c["split"],c["has_negative_structure"])
    ibatches,istrata=precompute_batches(i["state"],i["onset"],i["split"],i["has_negative_structure"])
    if not np.array_equal(cbatches,ibatches):
        raise RuntimeError("S9 paired batch indices differ")
    if cstrata!=istrata:
        raise RuntimeError("S9 stratum sizes differ")

    # Exact initialization and pre-update logits.
    xf=context5(c["features"].astype(np.float32,copy=False)).reshape(-1,960)
    idx=cbatches[0]
    mc=initialize_arm(960,True); mi=initialize_arm(960,True)
    if module_sha(mc)!=module_sha(mi): raise RuntimeError("S9 initialization mismatch")
    xb=torch.from_numpy(xf[idx]).float()
    with torch.no_grad():
        cs,co=mc(xb); is_,io=mi(xb)
    if not torch.equal(cs,is_) or not torch.equal(co,io):
        raise RuntimeError("S9 pre-update logits differ")

    control,cf=fit_arm(c["features"].astype(np.float32,copy=False),c["state"],c["onset"],cbatches,nonlinear=True,deadline=deadline)
    intervention,wf=fit_arm(i["features"].astype(np.float32,copy=False),i["state"],i["onset"],ibatches,nonlinear=True,deadline=deadline)

    ctest=evaluate_arm(control,c,"test"); wtest=evaluate_arm(intervention,i,"test")
    cval=evaluate_arm(control,c,"validation"); wval=evaluate_arm(intervention,i,"validation")

    chord_c=ctest["familyPitchOnset"]["chords"]; chord_w=wtest["familyPitchOnset"]["chords"]
    chord_f1_gain=chord_w["f1"]-chord_c["f1"]
    chord_recall_gain=chord_w["recall"]-chord_c["recall"]
    state_gain=wtest["admission"]["stateAdmissionFraction"]-ctest["admission"]["stateAdmissionFraction"]
    joint_gain=wtest["admission"]["jointAdmissionFraction"]-ctest["admission"]["jointAdmissionFraction"]
    recall_gain=wtest["pitchOnset"]["recall"]-ctest["pitchOnset"]["recall"]
    f1_gain=wtest["pitchOnset"]["f1"]-ctest["pitchOnset"]["f1"]
    offset_decline=ctest["pitchOnsetOffset"]["f1"]-wtest["pitchOnsetOffset"]["f1"]
    non_chord_losses={f:ctest["familyPitchOnset"][f]["f1"]-wtest["familyPitchOnset"][f]["f1"] for f in ctest["familyPitchOnset"] if f!="chords"}

    criteria={
      "chordOnsetF1GainAtLeast0_15":chord_f1_gain>=.15,
      "chordRecallGainAtLeast0_15":chord_recall_gain>=.15,
      "stateAdmissionGainAtLeast0_05":state_gain>=.05,
      "jointAdmissionGainAtLeast0_04":joint_gain>=.04,
      "overallOnsetRecallGainAtLeast0_03":recall_gain>=.03,
      "overallOnsetF1GainAtLeast0_025":f1_gain>=.025,
      "absoluteChordF1AtLeast0_45":chord_w["f1"]>=.45,
      "absoluteStateAdmissionAtLeast0_42":wtest["admission"]["stateAdmissionFraction"]>=.42,
      "absoluteOnsetRecallAtLeast0_65":wtest["pitchOnset"]["recall"]>=.65,
      "absoluteOnsetF1AtLeast0_74":wtest["pitchOnset"]["f1"]>=.74,
      "repeatedRecallAtLeast0_55":wtest["repeatedAttackRecall"] is not None and wtest["repeatedAttackRecall"]>=.55,
      "onsetPrecisionAtLeast0_82":wtest["pitchOnset"]["precision"]>=.82,
      "onsetOffsetDeclineAtMost0_03":offset_decline<=.03,
      "negativeOnlyFalsePositiveRateAtMost0_10PerSecond":wtest["negativeOnlyFalsePositiveEventsPerSecond"] is not None and wtest["negativeOnlyFalsePositiveEventsPerSecond"]<=.10,
      "noNonChordFamilyF1LossOver0_15":all(v<=.15 for v in non_chord_losses.values()),
      "finiteBoth500StepsExactInitBatchAndDataIdentity":(
        cf["optimizerSteps"]==500 and wf["optimizerSteps"]==500
        and module_sha(initialize_arm(960,True))==module_sha(initialize_arm(960,True))
        and np.array_equal(cbatches,ibatches)
        and all(math.isfinite(float(v)) for v in (chord_f1_gain,chord_recall_gain,state_gain,joint_gain,recall_gain,f1_gain))
      ),
    }

    identity={
      "schema":"astra-s9-identity-v1",
      "controlArrayContentSha256":dataset_array_hashes(c),
      "interventionArrayContentSha256":dataset_array_hashes(i),
      "batchPlanSha256":batch_plan_sha256(cbatches),
      "batchIndicesIdentical":True,
      "validationTestBitIdentical":True,
      "nonChordBitIdentical":True,
      "preUpdateModelInitializationIdentical":True,
      "preUpdateStateLogitsIdentical":True,
      "preUpdateOnsetLogitsIdentical":True,
    }
    Path(identity_out).write_text(json.dumps(identity,indent=2,sort_keys=True)+"\n")

    result={
      "schema":SCHEMA,"seed":ROOT_SEED,
      "fixed":{"architecture":"S6 nonlinear replacement state head","sampler":"uniform 32/32/32/32 onset-aware",
               "stateActiveWeight":9.0,"onsetPositiveWeight":8.0,"onsetLossWeight":4.0,"learningRate":0.003,
               "stateThreshold":0.5,"onsetThreshold":0.5,"thresholdSearch":False,"thresholdRetuning":False},
      "identity":identity,
      "control10Voicings":{"fit":cf,"validation":cval,"test":ctest},
      "intervention30Voicings":{"fit":wf,"validation":wval,"test":wtest},
      "comparison":{"chordOnsetF1Gain":chord_f1_gain,"chordRecallGain":chord_recall_gain,
                    "stateAdmissionGain":state_gain,"jointAdmissionGain":joint_gain,
                    "onsetRecallGain":recall_gain,"onsetF1Gain":f1_gain,
                    "onsetOffsetF1Decline":offset_decline,"nonChordFamilyF1LossVsControl":non_chord_losses},
      "criteria":criteria,"s9GatePassed":all(criteria.values()),
      "execution":{"modelCount":2,"optimizerStepsTotal":cf["optimizerSteps"]+wf["optimizerSteps"],
                   "fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0},
      "guards":{"externalAudioAssets":False,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,
                "codespacesUsed":False,"vercelUsed":False,"productionMutation":False},
      "meaning":"Synthetic-only controlled chord-voicing-diversity experiment."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"10-voicing-control","stateDict":control.state_dict(),"optimizerSteps":cf["optimizerSteps"]},control_model)
    torch.save({"schema":SCHEMA,"arm":"30-voicing-intervention","stateDict":intervention.state_dict(),"optimizerSteps":wf["optimizerSteps"]},intervention_model)
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS: raise RuntimeError("S9 optimizer ceiling")
    print("S9_RESULT="+json.dumps(result,sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("build-intervention")
    p.add_argument("--control-dataset",required=True); p.add_argument("--out",required=True); p.add_argument("--receipt",required=True)
    q=sub.add_parser("run")
    q.add_argument("--control-dataset",required=True); q.add_argument("--intervention-dataset",required=True); q.add_argument("--out",required=True)
    q.add_argument("--identity-out",required=True); q.add_argument("--control-model",required=True); q.add_argument("--intervention-model",required=True)
    a=ap.parse_args()
    if a.cmd=="build-intervention":
        r=build_intervention_dataset(a.control_dataset,a.out,a.receipt)
        print("S9_DATASET="+json.dumps(r,sort_keys=True))
    else:
        run(a.control_dataset,a.intervention_dataset,a.out,a.control_model,a.intervention_model,a.identity_out)

if __name__=="__main__": main()
