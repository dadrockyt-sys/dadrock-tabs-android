#!/usr/bin/env python3
"""Final model-free source-domain V3 challenge coverage admission."""
from __future__ import annotations

import argparse, hashlib, json, math, time
from pathlib import Path
import numpy as np

from synthetic.source_domain_joint_coverage_manifest_v2 import (
    FAMILIES, AXES, EXPECTED_CONTROL_SHA256, _sha256_file, _map,
)
from synthetic.source_domain_simulator_diversity_v1 import (
    render_source_domain, _features, _rise_time, _first_difference_energy,
    _cqt_flux, _hash_array,
)
from synthetic.source_domain_v2_stage_a_admission_v1 import (
    _override_from_manifest, _spectral_centroid,
)
from synthetic.source_domain_v2_stage_b_preparation_v1 import (
    _template_variant, _label_identity,
)

SCHEMA="astra-source-domain-joint-coverage-v3-final-result-v1"
ROOT="astra-source-domain-joint-v3"
EXPECTED_STAGE_B_RESULT_SHA256="d1f4ee0580ca98094fb12adabf76f437e6e3769c85b1fbc7f741205c9a3b13d2"
EXPECTED_INTERVENTION_SHA256="a17a16daeb8d698e325dc6820f18d5eda2fec75d9beebe2a9605a678124dc26b"
MAX_RENDERS=200
MAX_AUDIO_SECONDS=400.0
MAX_WALL_SECONDS=30*60.0
MAX_PERSISTED_BYTES=250*1024*1024
DESCRIPTORS=(
    "waveformRms",
    "spectralCentroid",
    "rmsNormalizedFirstDifferenceEnergy",
    "preparedCqtPositiveFlux",
    "preparedCqtRowDisplacement",
)

def _file_sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def _seed(*parts):
    raw="|".join(map(str,parts)).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8],"big") & 0x7fffffff

def _perm(n,family,axis):
    return np.random.RandomState(_seed(ROOT,"challenge",family,axis)).permutation(n)

def _challenge_rows_for_family(source_indices,family):
    source_indices=sorted(map(int,source_indices))
    if len(source_indices)!=6: raise RuntimeError("expected six source test rows per family")
    slots=[]
    for row in source_indices:
        for rep in (0,1):
            slots.append({"sourceRowIndex":row,"replicate":rep})
    if len(slots)!=12: raise RuntimeError("V3 slot count mismatch")
    for axis in AXES:
        p=_perm(12,family,axis)
        for pos,k in enumerate(p):
            slots[pos][axis]=float(_map(axis,(int(k)+0.5)/12.0))
            slots[pos].setdefault("strata",{})[axis]=int(k)
    nl=np.zeros(12,dtype=bool); nl[_perm(12,family,"nonlinearActive")[:6]]=True
    hum=np.zeros(12,dtype=bool); hum[_perm(12,family,"humActive")[:4]]=True
    active=np.flatnonzero(hum)
    order=_perm(len(active),family,"humFundamentalHz")
    active=active[order]
    freq=np.zeros(12,dtype=int)
    freq[active[:2]]=50; freq[active[2:]]=60
    for i,s in enumerate(slots):
        s["family"]=family
        s["kind"]="v3-primary-challenge"
        s["nonlinearActive"]=bool(nl[i])
        s["humActive"]=bool(hum[i])
        s["humFundamentalHz"]=int(freq[i]) if hum[i] else None
        s["slot"]=i
    return slots

def build_challenge_manifest(control):
    rows=[]
    for fam in FAMILIES:
        ids=np.flatnonzero((control["family"]==fam)&(control["split"]=="test"))
        rows.extend(_challenge_rows_for_family(ids,fam))
    if len(rows)!=84: raise RuntimeError("V3 challenge manifest row count mismatch")
    for fam in FAMILIES:
        rr=[r for r in rows if r["family"]==fam]
        if len(rr)!=12: raise RuntimeError("family V3 challenge count mismatch")
        for axis in AXES:
            if sorted(r["strata"][axis] for r in rr)!=list(range(12)):
                raise RuntimeError("V3 marginal stratum mismatch")
        if sum(r["nonlinearActive"] for r in rr)!=6: raise RuntimeError("V3 nonlinear count")
        hh=[r for r in rr if r["humActive"]]
        if len(hh)!=4 or sum(r["humFundamentalHz"]==50 for r in hh)!=2 or sum(r["humFundamentalHz"]==60 for r in hh)!=2:
            raise RuntimeError("V3 hum categorical count")
    return rows

def _override(row):
    # Same clip-level override contract as V2.
    return _override_from_manifest(row)

def _descriptor(audio,feat,control_feat,template):
    attacked=[r for r in template["segments"] if bool(r["attack"])]
    diffs=[]; fluxes=[]; rises=[]
    hop=512/22050
    for row in attacked:
        st=float(row["start"])
        diffs.append(float(_first_difference_energy(audio,st)))
        fluxes.append(float(_cqt_flux(feat,int(round(st/hop)))))
        rt=_rise_time(audio,st)
        if rt is not None: rises.append(float(rt))
    rms=float(np.sqrt(np.mean(np.asarray(audio,dtype=np.float64)**2)))
    raw=float(np.median(diffs)) if diffs else 0.0
    norm=(raw/(rms*rms)) if rms>0 else 0.0
    return {
        "waveformRms":rms,
        "spectralCentroid":float(_spectral_centroid(audio)),
        "rawFirstDifferenceEnergy":raw,
        "rmsNormalizedFirstDifferenceEnergy":float(norm),
        "preparedCqtPositiveFlux":float(np.median(fluxes)) if fluxes else 0.0,
        "preparedCqtRowDisplacement":float(np.mean(np.abs(feat.astype(np.float64)-control_feat.astype(np.float64)))),
        "riseTimeSeconds":float(np.median(rises)) if rises else None,
    }

def _render_pass(control,manifest_rows):
    chord_train=np.flatnonzero((control["family"]=="chords")&(control["split"]=="train"))
    records=[]; feats=[]; states=[]; onsets=[]; families=[]; splits=[]; tids=[]; neg=[]; negstruct=[]; refs=[]; source_rows=[]; reps=[]
    waveform_hashes=[]
    for mrow in manifest_rows:
        i=int(mrow["sourceRowIndex"])
        if str(control["split"][i])!="test" or str(control["family"][i])!=mrow["family"]:
            raise RuntimeError("V3 source row identity mismatch")
        template,variant,historical=_template_variant(control,i,chord_train)
        if historical: raise RuntimeError("V3 challenge cannot use historical train chord")
        audio=render_source_domain(template,variant,profile="intervention",override=_override(mrow))
        feat=_features(audio)
        if feat.shape!=control["features"][i].shape or not np.isfinite(feat).all():
            raise RuntimeError("invalid V3 challenge features")
        so,oo,ro=_label_identity(control,i,template,len(feat),False)
        if not (so and oo and ro): raise RuntimeError("V3 label/reference identity failed")
        if any(bool(x["attack"]) for x in template["segments"]) and np.array_equal(feat,control["features"][i]):
            raise RuntimeError("V3 positive challenge feature unchanged")
        rec={
            "family":mrow["family"],"sourceRowIndex":i,"replicate":int(mrow["replicate"]),"slot":int(mrow["slot"]),
            "variant":int(variant),"waveformSha256":_hash_array(audio),"featureSha256":_hash_array(feat),
            "manifestParameters":{k:mrow[k] for k in list(AXES)+["nonlinearActive","humActive","humFundamentalHz"]},
            **_descriptor(audio,feat,control["features"][i],template),
        }
        records.append(rec); waveform_hashes.append(rec["waveformSha256"])
        feats.append(feat); states.append(control["state"][i]); onsets.append(control["onset"][i])
        families.append(control["family"][i]); splits.append("test"); tids.append(control["template_id"][i])
        neg.append(control["negative_only"][i]); negstruct.append(control["has_negative_structure"][i]); refs.append(control["refs_json"][i])
        source_rows.append(i); reps.append(int(mrow["replicate"]))
    arrays={
      "features":np.stack(feats),
      "state":np.stack(states),
      "onset":np.stack(onsets),
      "family":np.asarray(families),
      "split":np.asarray(splits),
      "template_id":np.asarray(tids),
      "negative_only":np.asarray(neg,dtype=np.bool_),
      "has_negative_structure":np.asarray(negstruct,dtype=np.bool_),
      "refs_json":np.asarray(refs),
      "source_row_index":np.asarray(source_rows,dtype=np.int32),
      "challenge_replicate":np.asarray(reps,dtype=np.int8),
    }
    return records,arrays,waveform_hashes

def _training_records(stage_b):
    rows=stage_b.get("trainRecords",[])
    if len(rows)!=210: raise RuntimeError("frozen Stage-B train record count mismatch")
    out=[]
    for r in rows:
        x=dict(r)
        rms=float(x["waveformRms"]); raw=float(x["firstDifferenceEnergy"])
        x["rmsNormalizedFirstDifferenceEnergy"]=raw/(rms*rms) if rms>0 else 0.0
        out.append(x)
    return out

def _coverage(training,challenge):
    checks=[]
    for fam in FAMILIES:
        tr=[r for r in training if r["family"]==fam]
        ch=[r for r in challenge if r["family"]==fam]
        if len(tr)!=30 or len(ch)!=12: raise RuntimeError("V3 coverage family count mismatch")
        for d in DESCRIPTORS:
            tv=np.asarray([float(r[d]) for r in tr])
            cv=np.asarray([float(r[d]) for r in ch])
            lo,hi=np.quantile(tv,[.05,.95],method="linear")
            med=float(np.median(cv))
            checks.append({"family":fam,"descriptor":d,"trainP05":float(lo),"trainP95":float(hi),
                           "challengeMedian":med,"passed":bool(float(lo)<=med<=float(hi))})
    passed=sum(x["passed"] for x in checks)
    return {"checks":checks,"passed":int(passed),"total":35,"required":35,"admissionPassed":passed==35}

def run(control_path,stage_b_result_path,intervention_path,out_dir):
    started=time.monotonic()
    out=Path(out_dir)
    if out.exists(): raise RuntimeError("refusing existing V3 output")
    out.mkdir(parents=True)
    if _sha256_file(control_path)!=EXPECTED_CONTROL_SHA256: raise RuntimeError("control hash mismatch")
    if _file_sha256(stage_b_result_path)!=EXPECTED_STAGE_B_RESULT_SHA256: raise RuntimeError("Stage-B result hash mismatch")
    if _file_sha256(intervention_path)!=EXPECTED_INTERVENTION_SHA256: raise RuntimeError("V2 intervention hash mismatch")
    control=np.load(control_path,allow_pickle=False)
    stage_b=json.loads(Path(stage_b_result_path).read_text())
    training=_training_records(stage_b)
    manifest=build_challenge_manifest(control)
    manifest_payload=json.dumps(manifest,sort_keys=True,separators=(",",":")).encode()
    manifest_sha=hashlib.sha256(manifest_payload).hexdigest()

    rec1,arr1,wav1=_render_pass(control,manifest)
    rec2,arr2,wav2=_render_pass(control,manifest)
    renders=168
    if wav1!=wav2: raise RuntimeError("V3 waveform determinism failed")
    if not np.array_equal(arr1["features"],arr2["features"]): raise RuntimeError("V3 feature determinism failed")
    # Descriptors excluding incidental JSON key ordering must be exact.
    if rec1!=rec2: raise RuntimeError("V3 descriptor determinism failed")

    coverage=_coverage(training,rec1)
    dataset_path=out/"v3-primary-challenge.npz"
    np.savez_compressed(dataset_path,**arr1)
    manifest_path=out/"v3-challenge-manifest.json"
    manifest_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")

    elapsed=time.monotonic()-started
    persisted=dataset_path.stat().st_size+manifest_path.stat().st_size
    audio_seconds=renders*2.0
    criteria={
      "challengeRowCount84":len(rec1)==84,
      "challengeRowsPerFamily12":all(sum(r["family"]==f for r in rec1)==12 for f in FAMILIES),
      "deterministicWaveforms":True,
      "deterministicFeatures":True,
      "deterministicDescriptors":True,
      "coverage35of35":coverage["admissionPassed"],
      "renderCeiling":renders<=MAX_RENDERS,
      "audioSecondsCeiling":audio_seconds<=MAX_AUDIO_SECONDS,
      "wallTimeCeiling":elapsed<=MAX_WALL_SECONDS,
      "persistedBytesCeiling":persisted<=MAX_PERSISTED_BYTES,
    }
    result={
      "schema":SCHEMA,
      "status":"passed" if all(criteria.values()) else "failed",
      "controlSha256":EXPECTED_CONTROL_SHA256,
      "frozenStageBResultSha256":EXPECTED_STAGE_B_RESULT_SHA256,
      "frozenV2InterventionSha256":EXPECTED_INTERVENTION_SHA256,
      "challengeManifestSha256":manifest_sha,
      "challengeDatasetSha256":_file_sha256(dataset_path),
      "coverage":coverage,
      "criteria":criteria,
      "challengeRecords":rec1,
      "execution":{
        "renderOperations":renders,"audioSeconds":audio_seconds,"elapsedSeconds":elapsed,
        "persistedBytes":persisted,"modelLoads":0,"modelInference":False,"optimizerSteps":0,
        "thresholdSearch":False,"thresholdRetuning":False,"automaticRetry":False,
        "p1Accessed":False,"p2Accessed":False,"p3Opened":False,
        "paidComputeDollars":0,"productionMutation":False,
      },
      "stopIfFailed":"no-further-source-domain-coverage-redesign",
    }
    result_path=out/"v3-result.json"
    result_path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SOURCE_DOMAIN_V3_FINAL="+json.dumps({
      "status":result["status"],"coverage":{k:coverage[k] for k in ("passed","total","required","admissionPassed")},
      "criteria":criteria,"execution":result["execution"]
    },sort_keys=True))
    if not all(criteria.values()): raise SystemExit("V3 final coverage admission failed")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--control",required=True)
    ap.add_argument("--stage-b-result",required=True)
    ap.add_argument("--intervention",required=True)
    ap.add_argument("--out-dir",required=True)
    a=ap.parse_args()
    run(a.control,a.stage_b_result,a.intervention,a.out_dir)

if __name__=="__main__": main()
