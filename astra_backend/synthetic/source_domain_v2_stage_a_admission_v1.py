#!/usr/bin/env python3
"""Stage-A model-free acoustic admission for source-domain joint-coverage V2.

Uses the frozen V2 parameter manifest and existing V1 waveform equations.
No full dataset preparation, model loading, inference, optimizer, thresholds,
or P1/P2/P3 access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np

from synthetic.s0_pilot_v1 import (
    CLIP_SECONDS, OUTPUT_SR, OPEN_MIDI, build_template, render_waveform, targets_for_template,
)
from synthetic.s9_pilot_v1 import intervention_chord_template, render_waveform_with_timbre_key
from synthetic.source_domain_joint_coverage_manifest_v2 import (
    FAMILIES, AXES, EXPECTED_CONTROL_SHA256, _sha256_file,
)
from synthetic.source_domain_simulator_diversity_v1 import (
    render_source_domain, _hash_array, _features, _fundamental_cents,
    _rise_time, _first_difference_energy, _cqt_flux,
)

SCHEMA="astra-source-domain-v2-stage-a-acoustic-admission-v1"
EXPECTED_MANIFEST_CONTENT_SHA256="2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469"
TRAIN_POSITIONS=(0,29)
CHALLENGE_POSITIONS=(0,5)
MAX_WAVEFORM_RENDERS=112
MAX_AUDIO_SECONDS=224.0
MAX_WALL_SECONDS=20*60.0
MAX_PERSISTED_BYTES=150*1024*1024


def _file_sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()


def _manifest_payload_sha(manifest):
    x=dict(manifest)
    x.pop("manifestContentSha256",None)
    payload=json.dumps(x,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _override_from_manifest(row):
    out={axis:float(row[axis]) for axis in AXES}
    out["nonlinearActive"]=bool(row["nonlinearActive"])
    out["humActive"]=bool(row["humActive"])
    # humCombinedRmsRelative is intentionally NOT overridden: it is not one of
    # the frozen V2 joint-plan axes and therefore retains the deterministic V1
    # source-parameter substream. Frequency is meaningful only when hum is on.
    if row["humActive"]:
        out["humFundamentalHz"]=int(row["humFundamentalHz"])
    return out


def _row_context(control,row_index,chord_train_rows):
    i=int(row_index)
    family=str(control["family"][i])
    split=str(control["split"][i])
    tid=str(control["template_id"][i])

    chord_slot={int(r):slot for slot,r in enumerate(chord_train_rows.tolist())}.get(i)
    if chord_slot is not None:
        template=intervention_chord_template(chord_slot)
        variant=chord_slot%3
        expected_control_tid=f"chords:{chord_slot//3:02d}"
        control_audio=render_waveform_with_timbre_key(template,expected_control_tid,variant)
        return template,variant,control_audio,{"historicalS9TrainChord":True,"slot":int(chord_slot)}

    # Frozen S0 ordering stores each template's three variants contiguously.
    same=np.flatnonzero((control["family"]==family)&(control["template_id"]==tid))
    prior=same[same<=i]
    variant=len(prior)-1
    if not 0<=variant<=2:
        raise RuntimeError(f"unable to derive variant row {i}")
    if ":" not in tid:
        raise RuntimeError(f"unexpected template id row {i}: {tid}")
    base=int(tid.rsplit(":",1)[1])
    template=build_template(family,base)
    control_audio=render_waveform(template,variant)
    return template,variant,control_audio,{"historicalS9TrainChord":False}


def _selected_rows(manifest):
    selected=[]
    for family in FAMILIES:
        train=sorted([r for r in manifest["trainRows"] if r["family"]==family],key=lambda r:r["rowIndex"])
        challenge=sorted([r for r in manifest["primaryChallengeRows"] if r["family"]==family],key=lambda r:r["rowIndex"])
        if len(train)!=30 or len(challenge)!=6:
            raise RuntimeError("unexpected family manifest counts")
        for pos in TRAIN_POSITIONS:
            selected.append((family,"train",pos,train[pos]))
        for pos in CHALLENGE_POSITIONS:
            selected.append((family,"challenge",pos,challenge[pos]))
    if len(selected)!=28:
        raise RuntimeError("Stage A must select exactly 28 V2 rows")
    return selected


def _labels_identity(control,i,template,frames,historical_s9):
    state,onset,refs=targets_for_template(template,frames)
    if not np.array_equal(state,control["state"][i]):
        return False,False,False
    if not np.array_equal(onset,control["onset"][i]):
        return True,False,False
    ref_json=json.dumps(refs,separators=(",",":"),sort_keys=True)
    stored=str(control["refs_json"][i])
    if historical_s9:
        refs_ok=(len(stored)<len(ref_json) and ref_json.startswith(stored))
    else:
        refs_ok=(stored==ref_json)
    return True,True,bool(refs_ok)


def _row_metrics(audio,features,template,meta):
    attacked=[e for e in meta["events"] if e["attack"]]
    nonattack_transients=[e for e in meta["events"] if (not e["attack"]) and e["transientApplied"]]
    events=[]
    cents=[]
    rises=[]
    diffs=[]
    fluxes=[]
    for e in attacked:
        freq=440.0*(2.0**((int(e["pitch"])-69)/12.0))
        stable_start=min(float(e["end"])-.04,float(e["start"])+.10)
        stable_end=min(float(e["end"]),stable_start+.12)
        cent=_fundamental_cents(audio,freq,stable_start,stable_end)
        rise=_rise_time(audio,float(e["start"]))
        diff=_first_difference_energy(audio,float(e["start"]))
        frame=int(round(float(e["start"])/(512/22050)))
        flux=_cqt_flux(features,frame)
        events.append({
            "eventIndex":int(e["index"]),
            "fundamentalCents":cent,
            "riseSeconds":rise,
            "firstDifferenceEnergy":diff,
            "cqtPositiveFlux":flux,
        })
        if cent is not None: cents.append(abs(float(cent)))
        if rise is not None: rises.append(float(rise))
        diffs.append(float(diff)); fluxes.append(float(flux))
    return {
        "attackedEvents":events,
        "unlabeledTransientCount":len(nonattack_transients),
        "maxAbsoluteFundamentalCents":max(cents) if cents else None,
        "medianRiseSeconds":float(np.median(rises)) if rises else None,
        "medianFirstDifferenceEnergy":float(np.median(diffs)) if diffs else None,
        "medianPreparedCqtPositiveFlux":float(np.median(fluxes)) if fluxes else None,
    }


def run_stage_a(control_path,manifest_path,out_path):
    started=time.monotonic()
    if _sha256_file(control_path)!=EXPECTED_CONTROL_SHA256:
        raise RuntimeError("frozen S9 control hash mismatch")
    manifest=json.loads(Path(manifest_path).read_text())
    if manifest.get("schema")!="astra-source-domain-joint-coverage-manifest-v2":
        raise RuntimeError("wrong V2 manifest schema")
    content_sha=_manifest_payload_sha(manifest)
    if content_sha!=EXPECTED_MANIFEST_CONTENT_SHA256 or manifest.get("manifestContentSha256")!=EXPECTED_MANIFEST_CONTENT_SHA256:
        raise RuntimeError("frozen V2 manifest content hash mismatch")

    c=np.load(control_path,allow_pickle=False)
    if len(c["features"])!=294:
        raise RuntimeError("unexpected frozen control size")
    chord_train=np.flatnonzero((c["family"]=="chords")&(c["split"]=="train"))
    if len(chord_train)!=30:
        raise RuntimeError("unexpected frozen S9 chord training count")

    rows=[]
    renders=0
    max_cents=[]
    all_finite=True
    all_peak=True
    all_deterministic=True
    all_state=True
    all_onset=True
    all_refs=True
    all_no_unlabeled=True
    all_positive_cqt_changed=True

    for family,kind,local_position,mrow in _selected_rows(manifest):
        i=int(mrow["rowIndex"])
        if str(c["family"][i])!=family:
            raise RuntimeError("manifest/control family mismatch")
        expected_split="train" if kind=="train" else "test"
        if str(c["split"][i])!=expected_split:
            raise RuntimeError("manifest/control split mismatch")

        template,variant,control_audio,ctx=_row_context(c,i,chord_train)
        override=_override_from_manifest(mrow)

        v2a,meta=render_source_domain(
            template,variant,profile="intervention",override=override,return_metadata=True
        )
        v2b=render_source_domain(
            template,variant,profile="intervention",override=override,return_metadata=False
        )
        renders += 3  # clean control + V2 + deterministic V2 rerender

        deterministic=bool(np.array_equal(v2a,v2b))
        all_deterministic &= deterministic

        control_feat=_features(control_audio)
        v2_feat=_features(v2a)
        if control_feat.shape!=v2_feat.shape:
            raise RuntimeError("Stage A frontend shape mismatch")
        finite=bool(np.isfinite(control_audio).all() and np.isfinite(v2a).all()
                    and np.isfinite(control_feat).all() and np.isfinite(v2_feat).all())
        all_finite &= finite

        state_ok,onset_ok,refs_ok=_labels_identity(
            c,i,template,len(v2_feat),bool(ctx["historicalS9TrainChord"])
        )
        all_state &= state_ok; all_onset &= onset_ok; all_refs &= refs_ok

        rm=_row_metrics(v2a,v2_feat,template,meta)
        no_unlabeled=rm["unlabeledTransientCount"]==0
        all_no_unlabeled &= no_unlabeled
        if rm["maxAbsoluteFundamentalCents"] is not None:
            max_cents.append(float(rm["maxAbsoluteFundamentalCents"]))

        peak=float(np.max(np.abs(v2a)))
        peak_ok=peak<.999
        all_peak &= peak_ok

        positive=any(bool(x["attack"]) for x in template["segments"])
        cqt_changed=bool(not np.array_equal(control_feat,v2_feat))
        if positive:
            all_positive_cqt_changed &= cqt_changed

        displacement=float(np.mean(np.abs(v2_feat.astype(np.float64)-control_feat.astype(np.float64))))
        rows.append({
            "family":family,"kind":kind,"localPosition":int(local_position),"rowIndex":i,
            "templateIdStored":str(c["template_id"][i]),"variant":int(variant),
            "historicalS9TrainChord":bool(ctx["historicalS9TrainChord"]),
            "manifestStrata":dict(mrow["strata"]),
            "manifestParameters":{k:mrow[k] for k in list(AXES)+["nonlinearActive","humActive","humFundamentalHz"]},
            "controlWaveformSha256":_hash_array(control_audio),
            "v2WaveformSha256":_hash_array(v2a),
            "v2RerenderSha256":_hash_array(v2b),
            "deterministicRerender":deterministic,
            "controlCqtSha256":_hash_array(control_feat),
            "v2CqtSha256":_hash_array(v2_feat),
            "cqtChanged":cqt_changed,
            "finite":finite,
            "peak":peak,
            "rms":float(np.sqrt(np.mean(v2a.astype(np.float64)**2))),
            "spectralCentroid":_spectral_centroid(v2a),
            "preparedCqtRowDisplacement":displacement,
            "stateIdentity":bool(state_ok),"onsetIdentity":bool(onset_ok),"referenceIdentity":bool(refs_ok),
            **rm,
        })

    elapsed=time.monotonic()-started
    audio_seconds=renders*CLIP_SECONDS
    max_abs_cents=max(max_cents) if max_cents else None
    criteria={
        "deterministicRerenderIdentity":bool(all_deterministic),
        "stateIdentity":bool(all_state),
        "onsetIdentity":bool(all_onset),
        "referenceIdentity":bool(all_refs),
        "finiteAudioAndFeatures":bool(all_finite),
        "peakUnder0_999":bool(all_peak),
        "fundamentalWithin15Cents":bool(max_abs_cents is not None and max_abs_cents<=15.0),
        "noUnlabeledTransientInjection":bool(all_no_unlabeled),
        "cqtChangedEveryPositiveSelectedRow":bool(all_positive_cqt_changed),
        "manifestBindingExact":True,
        "selectedRowsExact":len(rows)==28,
        "renderCeiling":renders<=MAX_WAVEFORM_RENDERS,
        "audioSecondsCeiling":audio_seconds<=MAX_AUDIO_SECONDS,
        "wallTimeCeiling":elapsed<=MAX_WALL_SECONDS,
    }
    result={
        "schema":SCHEMA,
        "status":"passed" if all(criteria.values()) else "failed",
        "manifestContentSha256":content_sha,
        "controlFileSha256":EXPECTED_CONTROL_SHA256,
        "selection":{
            "families":list(FAMILIES),
            "trainLocalPositions":list(TRAIN_POSITIONS),
            "challengeLocalPositions":list(CHALLENGE_POSITIONS),
            "selectedV2Rows":28,
        },
        "rows":rows,
        "summary":{
            "maximumAbsoluteFundamentalErrorCents":max_abs_cents,
            "criteria":criteria,
            "stageAPassed":all(criteria.values()),
        },
        "execution":{
            "waveformRenders":renders,
            "audioSeconds":audio_seconds,
            "elapsedSeconds":elapsed,
            "modelLoads":0,"modelInference":False,"optimizerSteps":0,
            "thresholdSearch":False,"thresholdRetuning":False,"automaticRetry":False,
            "p1Accessed":False,"p2Accessed":False,"p3Opened":False,
            "paidComputeDollars":0,"productionMutation":False,
        },
        "ceilings":{
            "waveformRendersMax":MAX_WAVEFORM_RENDERS,
            "audioSecondsMax":MAX_AUDIO_SECONDS,
            "wallSecondsMax":MAX_WALL_SECONDS,
            "persistedBytesMax":MAX_PERSISTED_BYTES,
        }
    }
    Path(out_path).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if Path(out_path).stat().st_size>MAX_PERSISTED_BYTES:
        raise RuntimeError("Stage A persisted-byte ceiling exceeded")
    print("SOURCE_DOMAIN_V2_STAGE_A="+json.dumps({
        "status":result["status"],"criteria":criteria,
        "maximumAbsoluteFundamentalErrorCents":max_abs_cents,
        "execution":result["execution"],
    },sort_keys=True))
    if not result["summary"]["stageAPassed"]:
        raise SystemExit("V2 Stage A acoustic admission failed")
    return result


def _spectral_centroid(audio):
    x=np.asarray(audio,dtype=np.float64)
    if not len(x): return 0.0
    mag=np.abs(np.fft.rfft(x*np.hanning(len(x))))
    freq=np.fft.rfftfreq(len(x),1.0/OUTPUT_SR)
    den=float(np.sum(mag))
    return 0.0 if den<=0 else float(np.sum(freq*mag)/den)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--control",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    out=Path(a.out)
    if out.exists():
        raise RuntimeError("refusing existing Stage A output")
    run_stage_a(a.control,a.manifest,a.out)


if __name__=="__main__":
    main()
