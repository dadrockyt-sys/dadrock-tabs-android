#!/usr/bin/env python3
"""Model-free Stage-B full preparation and family coverage admission for V2."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from synthetic.s0_pilot_v1 import CLIP_SECONDS, build_template, targets_for_template
from synthetic.s9_pilot_v1 import intervention_chord_template
from synthetic.s2_pilot_v1 import dataset_array_hashes
from synthetic.s13_pilot_v1 import file_sha256
from synthetic.source_domain_joint_coverage_manifest_v2 import (
    FAMILIES, AXES, EXPECTED_CONTROL_SHA256, _sha256_file,
)
from synthetic.source_domain_simulator_diversity_v1 import (
    render_source_domain, _features, _rise_time, _first_difference_energy,
    _cqt_flux, _hash_array,
)
from synthetic.source_domain_v2_stage_a_admission_v1 import (
    EXPECTED_MANIFEST_CONTENT_SHA256, _manifest_payload_sha,
    _override_from_manifest, _spectral_centroid,
)

SCHEMA="astra-source-domain-v2-stage-b-preparation-result-v1"
EXPECTED_EXAMPLES=294
MAX_RENDERS=900
MAX_AUDIO_SECONDS=1800.0
MAX_WALL_SECONDS=45*60.0
MAX_PERSISTED_BYTES=500*1024*1024
DESCRIPTORS=(
    "waveformRms",
    "spectralCentroid",
    "firstDifferenceEnergy",
    "preparedCqtPositiveFlux",
    "preparedCqtRowDisplacement",
)


def _template_variant(control,row_index,chord_train_rows):
    i=int(row_index)
    family=str(control["family"][i]); tid=str(control["template_id"][i])
    chord_map={int(r):slot for slot,r in enumerate(chord_train_rows.tolist())}
    if i in chord_map:
        slot=int(chord_map[i])
        return intervention_chord_template(slot),slot%3,True

    if ":" not in tid:
        raise RuntimeError(f"unexpected template id row {i}: {tid}")
    base=int(tid.rsplit(":",1)[1])
    same=np.flatnonzero((control["family"]==family)&(control["template_id"]==tid))
    prior=same[same<=i]
    variant=len(prior)-1
    if not 0<=variant<=2:
        raise RuntimeError(f"unable to derive variant row {i}")
    return build_template(family,base),int(variant),False


def _label_identity(control,i,template,frames,historical):
    state,onset,refs=targets_for_template(template,frames)
    if not np.array_equal(state,control["state"][i]): return False,False,False
    if not np.array_equal(onset,control["onset"][i]): return True,False,False
    ref_json=json.dumps(refs,separators=(",",":"),sort_keys=True)
    stored=str(control["refs_json"][i])
    refs_ok=(len(stored)<len(ref_json) and ref_json.startswith(stored)) if historical else (stored==ref_json)
    return True,True,bool(refs_ok)


def _row_descriptor(audio,feat,control_feat,template):
    attacked=[r for r in template["segments"] if bool(r["attack"])]
    diffs=[]; flux=[]; rises=[]
    hop=512/22050
    for row in attacked:
        st=float(row["start"])
        diffs.append(_first_difference_energy(audio,st))
        frame=int(round(st/hop))
        flux.append(_cqt_flux(feat,frame))
        rt=_rise_time(audio,st)
        if rt is not None: rises.append(float(rt))
    return {
        "waveformRms":float(np.sqrt(np.mean(np.asarray(audio,dtype=np.float64)**2))),
        "spectralCentroid":float(_spectral_centroid(audio)),
        "firstDifferenceEnergy":float(np.median(diffs)) if diffs else 0.0,
        "preparedCqtPositiveFlux":float(np.median(flux)) if flux else 0.0,
        "preparedCqtRowDisplacement":float(np.mean(np.abs(feat.astype(np.float64)-control_feat.astype(np.float64)))),
        "riseTimeSeconds":float(np.median(rises)) if rises else None,
    }


def _render_pass(control,manifest):
    ia={k:np.array(control[k],copy=True) for k in control.files}
    qa={k:np.array(control[k],copy=True) for k in control.files}
    chord_train=np.flatnonzero((control["family"]=="chords")&(control["split"]=="train"))
    if len(chord_train)!=30: raise RuntimeError("expected 30 S9 chord train rows")

    train_map={int(r["rowIndex"]):r for r in manifest["trainRows"]}
    challenge_map={int(r["rowIndex"]):r for r in manifest["primaryChallengeRows"]}
    if len(train_map)!=210 or len(challenge_map)!=42:
        raise RuntimeError("manifest row count mismatch")

    train_records=[]; challenge_records=[]; waveform_hashes={}
    state_ok=onset_ok=refs_ok=True
    changed_train=[]; changed_challenge=[]
    renders=0

    for i,mrow in sorted(train_map.items()):
        if str(control["split"][i])!="train": raise RuntimeError("train manifest split mismatch")
        template,variant,historical=_template_variant(control,i,chord_train)
        override=_override_from_manifest(mrow)
        audio=render_source_domain(template,variant,profile="intervention",override=override)
        renders+=1
        feat=_features(audio)
        if feat.shape!=control["features"][i].shape or not np.isfinite(feat).all():
            raise RuntimeError("invalid V2 train feature")
        so,oo,ro=_label_identity(control,i,template,len(feat),historical)
        state_ok&=so; onset_ok&=oo; refs_ok&=ro
        ia["features"][i]=feat
        if np.array_equal(feat,control["features"][i]):
            raise RuntimeError(f"V2 training row unchanged unexpectedly: {i}")
        changed_train.append(i)
        rec={"rowIndex":i,"family":str(control["family"][i]),"split":"train",
             "variant":variant,"historicalS9TrainChord":historical,
             "waveformSha256":_hash_array(audio),
             **_row_descriptor(audio,feat,control["features"][i],template)}
        train_records.append(rec); waveform_hashes[f"train:{i}"]=rec["waveformSha256"]

    for i,mrow in sorted(challenge_map.items()):
        if str(control["split"][i])!="test": raise RuntimeError("challenge manifest split mismatch")
        template,variant,historical=_template_variant(control,i,chord_train)
        if historical: raise RuntimeError("test challenge must not be historical S9 train chord")
        override=_override_from_manifest(mrow)
        audio=render_source_domain(template,variant,profile="intervention",override=override)
        renders+=1
        feat=_features(audio)
        if feat.shape!=control["features"][i].shape or not np.isfinite(feat).all():
            raise RuntimeError("invalid V2 challenge feature")
        so,oo,ro=_label_identity(control,i,template,len(feat),False)
        state_ok&=so; onset_ok&=oo; refs_ok&=ro
        qa["features"][i]=feat
        if np.array_equal(feat,control["features"][i]):
            raise RuntimeError(f"V2 challenge row unchanged unexpectedly: {i}")
        changed_challenge.append(i)
        rec={"rowIndex":i,"family":str(control["family"][i]),"split":"test",
             "variant":variant,"historicalS9TrainChord":False,
             "waveformSha256":_hash_array(audio),
             **_row_descriptor(audio,feat,control["features"][i],template)}
        challenge_records.append(rec); waveform_hashes[f"challenge:{i}"]=rec["waveformSha256"]

    train_rows=np.flatnonzero(control["split"]=="train").tolist()
    test_rows=np.flatnonzero(control["split"]=="test").tolist()
    if changed_train!=train_rows: raise RuntimeError("changed intervention rows not exactly train")
    if changed_challenge!=test_rows: raise RuntimeError("changed challenge rows not exactly test")

    heldout=np.flatnonzero(control["split"]!="train")
    non_test=np.flatnonzero(control["split"]!="test")
    if not np.array_equal(ia["features"][heldout],control["features"][heldout]):
        raise RuntimeError("intervention heldout identity failed")
    if not np.array_equal(qa["features"][non_test],control["features"][non_test]):
        raise RuntimeError("challenge train/validation identity failed")

    for k in control.files:
        if k=="features": continue
        if not np.array_equal(ia[k],control[k]) or not np.array_equal(qa[k],control[k]):
            raise RuntimeError("non-feature identity failed: "+k)

    return {
        "intervention":ia,"challenge":qa,
        "trainRecords":train_records,"challengeRecords":challenge_records,
        "waveformHashes":waveform_hashes,
        "renders":renders,
        "identity":{"state":state_ok,"onset":onset_ok,"refs":refs_ok},
    }


def _coverage(train_records,challenge_records):
    checks=[]; byfam={}
    for fam in FAMILIES:
        tr=[r for r in train_records if r["family"]==fam]
        ch=[r for r in challenge_records if r["family"]==fam]
        if len(tr)!=30 or len(ch)!=6: raise RuntimeError("family coverage row count mismatch")
        fam_checks=[]
        for d in DESCRIPTORS:
            tv=np.asarray([float(r[d]) for r in tr],dtype=float)
            cv=np.asarray([float(r[d]) for r in ch],dtype=float)
            lo,hi=np.quantile(tv,[.05,.95],interpolation="linear")
            med=float(np.median(cv))
            passed=bool(float(lo)<=med<=float(hi))
            row={"family":fam,"descriptor":d,"trainP05":float(lo),"trainP95":float(hi),
                 "challengeMedian":med,"passed":passed}
            checks.append(row); fam_checks.append(row)
        byfam[fam]=fam_checks
    passed=sum(1 for x in checks if x["passed"])
    return {"checks":checks,"byFamily":byfam,"passed":passed,"total":len(checks),"required":35,"admissionPassed":passed==35}


def run_stage_b(control_path,manifest_path,out_dir):
    started=time.monotonic()
    out=Path(out_dir)
    if out.exists(): raise RuntimeError("refusing existing Stage B output")
    out.mkdir(parents=True)

    if _sha256_file(control_path)!=EXPECTED_CONTROL_SHA256:
        raise RuntimeError("frozen control hash mismatch")
    manifest=json.loads(Path(manifest_path).read_text())
    if _manifest_payload_sha(manifest)!=EXPECTED_MANIFEST_CONTENT_SHA256 or manifest.get("manifestContentSha256")!=EXPECTED_MANIFEST_CONTENT_SHA256:
        raise RuntimeError("frozen manifest hash mismatch")

    control=np.load(control_path,allow_pickle=False)
    if len(control["features"])!=EXPECTED_EXAMPLES: raise RuntimeError("unexpected control size")

    first=_render_pass(control,manifest)
    second=_render_pass(control,manifest)
    renders=first["renders"]+second["renders"]
    if renders!=504: raise RuntimeError("unexpected Stage B render count")
    if first["waveformHashes"]!=second["waveformHashes"]:
        raise RuntimeError("deterministic waveform hash repeat failed")

    for arm in ("intervention","challenge"):
        if not np.array_equal(first[arm]["features"],second[arm]["features"]):
            raise RuntimeError("deterministic feature repeat failed: "+arm)

    intervention_path=out/"v2-intervention.npz"
    challenge_path=out/"v2-primary-challenge.npz"
    np.savez_compressed(intervention_path,**first["intervention"])
    np.savez_compressed(challenge_path,**first["challenge"])

    i=np.load(intervention_path,allow_pickle=False)
    q=np.load(challenge_path,allow_pickle=False)
    coverage=_coverage(first["trainRecords"],first["challengeRecords"])
    audio_seconds=renders*CLIP_SECONDS
    elapsed=time.monotonic()-started
    persisted=Path(intervention_path).stat().st_size+Path(challenge_path).stat().st_size

    criteria={
        "interventionChangedRowsExactlyTrain":True,
        "challengeChangedRowsExactlyTest":True,
        "interventionValidationTestFeaturesBitIdentical":True,
        "challengeTrainValidationFeaturesBitIdentical":True,
        "allNonFeatureArraysBitIdentical":True,
        "reconstructedStateIdentity":bool(first["identity"]["state"]),
        "reconstructedOnsetIdentity":bool(first["identity"]["onset"]),
        "referenceIdentityIncludingHistoricalPrefixes":bool(first["identity"]["refs"]),
        "deterministicRepeatFeatureHashes":True,
        "deterministicRepeatWaveformHashes":True,
        "coverage35of35":bool(coverage["admissionPassed"]),
        "renderCeiling":renders<=MAX_RENDERS,
        "audioSecondsCeiling":audio_seconds<=MAX_AUDIO_SECONDS,
        "wallTimeCeiling":elapsed<=MAX_WALL_SECONDS,
        "persistedBytesCeiling":persisted<=MAX_PERSISTED_BYTES,
    }
    result={
        "schema":SCHEMA,
        "status":"passed" if all(criteria.values()) else "failed",
        "manifestContentSha256":EXPECTED_MANIFEST_CONTENT_SHA256,
        "controlFileSha256":EXPECTED_CONTROL_SHA256,
        "datasetFileSha256":{
            "control":file_sha256(control_path),
            "intervention":file_sha256(intervention_path),
            "challenge":file_sha256(challenge_path),
        },
        "arrayHashes":{
            "control":dataset_array_hashes(control),
            "intervention":dataset_array_hashes(i),
            "challenge":dataset_array_hashes(q),
        },
        "coverage":coverage,
        "criteria":criteria,
        "trainRecords":first["trainRecords"],
        "challengeRecords":first["challengeRecords"],
        "execution":{
            "renderOperations":renders,"audioSeconds":audio_seconds,"elapsedSeconds":elapsed,
            "persistedBytes":persisted,"modelLoads":0,"modelInference":False,
            "optimizerSteps":0,"thresholdSearch":False,"thresholdRetuning":False,
            "automaticRetry":False,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,
            "paidComputeDollars":0,"productionMutation":False,
        },
        "ceilings":{
            "renderOperationsMax":MAX_RENDERS,"audioSecondsMax":MAX_AUDIO_SECONDS,
            "wallSecondsMax":MAX_WALL_SECONDS,"persistedBytesMax":MAX_PERSISTED_BYTES,
        },
        "oldV1Challenge":{"gateEligible":False,"rerendered":False},
    }
    result_path=out/"stage-b-result.json"
    result_path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SOURCE_DOMAIN_V2_STAGE_B="+json.dumps({
        "status":result["status"],"coverage":{k:coverage[k] for k in ("passed","total","required","admissionPassed")},
        "criteria":criteria,"execution":result["execution"]
    },sort_keys=True))
    if not all(criteria.values()):
        raise SystemExit("V2 Stage B admission failed")
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--control",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--out-dir",required=True)
    a=ap.parse_args()
    run_stage_b(a.control,a.manifest,a.out_dir)


if __name__=="__main__":
    main()
