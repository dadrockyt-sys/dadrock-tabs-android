#!/usr/bin/env python3
"""Polyphony-safe Stage-A V2 acoustic admission.

Preserves the frozen Stage-A selection/gates. Only simultaneous attacked-event
pitch measurement uses an event-isolated diagnostic shadow render.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
from scipy.signal import lfilter, resample_poly

from synthetic.s0_pilot_v1 import CLIP_SECONDS, INTERNAL_SR, OUTPUT_SR, OPEN_MIDI
from synthetic.source_domain_joint_coverage_manifest_v2 import FAMILIES, AXES, EXPECTED_CONTROL_SHA256, _sha256_file
from synthetic.source_domain_simulator_diversity_v1 import (
    FINAL_PEAK, source_parameters, _note_params, _component, _apply_color, _rng,
    render_source_domain, _hash_array, _features, _fundamental_cents,
    _rise_time, _first_difference_energy, _cqt_flux,
)
from synthetic.source_domain_v2_stage_a_admission_v1 import (
    EXPECTED_MANIFEST_CONTENT_SHA256, TRAIN_POSITIONS, CHALLENGE_POSITIONS,
    MAX_WAVEFORM_RENDERS, MAX_AUDIO_SECONDS, MAX_WALL_SECONDS, MAX_PERSISTED_BYTES,
    _manifest_payload_sha, _override_from_manifest, _row_context, _selected_rows,
    _labels_identity, _spectral_centroid,
)

SCHEMA="astra-source-domain-v2-stage-a-polyphony-safe-result-v2"
SIMULTANEOUS_EPS_SECONDS=1e-6


def _simultaneous_attacked_indices(template):
    attacked=[i for i,r in enumerate(template["segments"]) if bool(r["attack"])]
    out=set()
    for i in attacked:
        si=float(template["segments"][i]["start"])
        if any(j!=i and abs(float(template["segments"][j]["start"])-si)<=SIMULTANEOUS_EPS_SECONDS for j in attacked):
            out.add(i)
    return out


def render_event_shadow(template,variant,event_index,override):
    """Render one original event in isolation while preserving original RNG keys."""
    event_index=int(event_index)
    if not 0<=event_index<len(template["segments"]):
        raise ValueError("event index out of range")
    row=template["segments"][event_index]
    params=dict(source_parameters(template["templateId"],variant))
    params.update(dict(override))

    n=int(round(CLIP_SECONDS*INTERNAL_SR))
    audio=np.zeros(n,dtype=np.float64)
    start=int(round(float(row["start"])*INTERNAL_SR))
    end=min(n,int(round(float(row["end"])*INTERNAL_SR)))
    if end<=start or start>=n:
        raise RuntimeError("shadow event has invalid bounds")

    note=_note_params(template["templateId"],variant,event_index,None)
    pitch=OPEN_MIDI[int(row["string"])]+int(row["fret"])
    freq=440.0*(2.0**((pitch-69)/12.0))
    d=1.15*float(params["dampingMultiplier"])*float(note["dampingMultiplier"])
    d*=4.5 if bool(row["palm"]) else 1.0
    d*=1.0+0.04*int(row["string"])
    rise=float(np.clip(float(params["attackBaseRiseSeconds"])*float(note["riseMultiplier"]),.001,.060))

    erng=_rng(template["templateId"],variant,"component",event_index)
    comp=_component(
        freq,(end-start)/INTERNAL_SR,INTERNAL_SR,erng,
        damping=d,
        pick_position=float(params["pickPosition"]),
        brightness=float(params["brightness"]),
        attack_rise=rise,
        transient=bool(row["attack"]),
        transient_gain=float(params["transientNoiseGain"]) if bool(row["attack"]) else 0.0,
        transient_decay=float(params["transientDecaySeconds"]),
        soft=bool(row["soft"]),
    )
    audio[start:end]+=float(note["amplitudeMultiplier"])*comp[:end-start]

    audio=_apply_color(audio,INTERNAL_SR,params)
    rms=float(np.sqrt(np.mean(audio**2)))
    nrng=_rng(template["templateId"],variant,"noise-final")
    if rms>0:
        noise_rms=float(params["broadbandNoiseRmsRelative"])*rms
        audio += nrng.normal(0,noise_rms,n)
        if bool(params["humActive"]) and float(params["humCombinedRmsRelative"])>0:
            t=np.arange(n,dtype=np.float64)/INTERNAL_SR
            f=float(params["humFundamentalHz"])
            h=np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*2*f*t)+.25*np.sin(2*np.pi*3*f*t)
            hr=float(np.sqrt(np.mean(h*h)))
            audio += h*(float(params["humCombinedRmsRelative"])*rms/max(hr,1e-12))

    body_a=.88
    audio=lfilter([1.0-body_a],[1.0,-body_a],audio)
    peak=float(np.max(np.abs(audio)))
    if peak>0:
        audio=FINAL_PEAK*audio/peak
    out=resample_poly(audio,1,2).astype(np.float32)
    want=int(round(CLIP_SECONDS*OUTPUT_SR))
    out=np.pad(out,(0,max(0,want-len(out))))[:want]
    final_peak=float(np.max(np.abs(out)))
    if final_peak>FINAL_PEAK:
        out=(out*(FINAL_PEAK/final_peak)).astype(np.float32,copy=False)
    if not np.isfinite(out).all() or float(np.max(np.abs(out)))>=.999:
        raise RuntimeError("invalid shadow output")
    return out


def _event_pitch_metrics(full_audio,features,template,meta,variant,override):
    simultaneous=_simultaneous_attacked_indices(template)
    events=[]
    gate_cents=[]
    mixed_cents=[]
    shadow_renders=0
    unlabeled_transients=[e for e in meta["events"] if (not e["attack"]) and e["transientApplied"]]

    for e in [x for x in meta["events"] if x["attack"]]:
        idx=int(e["index"])
        freq=440.0*(2.0**((int(e["pitch"])-69)/12.0))
        stable_start=min(float(e["end"])-.04,float(e["start"])+.10)
        stable_end=min(float(e["end"]),stable_start+.12)
        mixed=_fundamental_cents(full_audio,freq,stable_start,stable_end)
        if mixed is not None:
            mixed_cents.append(abs(float(mixed)))

        measurement_audio=full_audio
        mode="mixed-row"
        if idx in simultaneous:
            measurement_audio=render_event_shadow(template,variant,idx,override)
            shadow_renders+=1
            mode="event-shadow"

        gate=_fundamental_cents(measurement_audio,freq,stable_start,stable_end)
        if gate is not None:
            gate_cents.append(abs(float(gate)))

        rise=_rise_time(full_audio,float(e["start"]))
        diff=_first_difference_energy(full_audio,float(e["start"]))
        frame=int(round(float(e["start"])/(512/22050)))
        flux=_cqt_flux(features,frame)
        events.append({
            "eventIndex":idx,
            "simultaneous":idx in simultaneous,
            "pitchMeasurementMode":mode,
            "gateFundamentalCents":gate,
            "mixedRowFundamentalCentsDiagnostic":mixed,
            "riseSeconds":rise,
            "firstDifferenceEnergy":diff,
            "cqtPositiveFlux":flux,
        })

    return {
        "attackedEvents":events,
        "unlabeledTransientCount":len(unlabeled_transients),
        "maxAbsoluteGateFundamentalCents":max(gate_cents) if gate_cents else None,
        "maxAbsoluteMixedDiagnosticCents":max(mixed_cents) if mixed_cents else None,
        "shadowRenders":shadow_renders,
    }


def run_stage_a_v2(control_path,manifest_path,out_path):
    started=time.monotonic()
    if _sha256_file(control_path)!=EXPECTED_CONTROL_SHA256:
        raise RuntimeError("frozen control hash mismatch")
    manifest=json.loads(Path(manifest_path).read_text())
    content_sha=_manifest_payload_sha(manifest)
    if content_sha!=EXPECTED_MANIFEST_CONTENT_SHA256 or manifest.get("manifestContentSha256")!=EXPECTED_MANIFEST_CONTENT_SHA256:
        raise RuntimeError("frozen manifest hash mismatch")

    c=np.load(control_path,allow_pickle=False)
    chord_train=np.flatnonzero((c["family"]=="chords")&(c["split"]=="train"))
    rows=[]
    renders=0
    gate_cents=[]
    mixed_cents=[]
    simultaneous_events=0
    all_flags={k:True for k in (
        "deterministicRerenderIdentity","stateIdentity","onsetIdentity","referenceIdentity",
        "finiteAudioAndFeatures","peakUnder0_999","noUnlabeledTransientInjection",
        "cqtChangedEveryPositiveSelectedRow"
    )}

    for family,kind,local_position,mrow in _selected_rows(manifest):
        i=int(mrow["rowIndex"])
        expected_split="train" if kind=="train" else "test"
        if str(c["family"][i])!=family or str(c["split"][i])!=expected_split:
            raise RuntimeError("manifest/control row mismatch")

        template,variant,control_audio,ctx=_row_context(c,i,chord_train)
        override=_override_from_manifest(mrow)
        v2a,meta=render_source_domain(template,variant,profile="intervention",override=override,return_metadata=True)
        v2b=render_source_domain(template,variant,profile="intervention",override=override)
        renders+=3

        deterministic=bool(np.array_equal(v2a,v2b))
        all_flags["deterministicRerenderIdentity"] &= deterministic
        cf=_features(control_audio); vf=_features(v2a)
        finite=bool(np.isfinite(control_audio).all() and np.isfinite(v2a).all() and np.isfinite(cf).all() and np.isfinite(vf).all())
        all_flags["finiteAudioAndFeatures"] &= finite
        state_ok,onset_ok,refs_ok=_labels_identity(c,i,template,len(vf),bool(ctx["historicalS9TrainChord"]))
        all_flags["stateIdentity"] &= state_ok
        all_flags["onsetIdentity"] &= onset_ok
        all_flags["referenceIdentity"] &= refs_ok

        pm=_event_pitch_metrics(v2a,vf,template,meta,variant,override)
        renders+=int(pm["shadowRenders"])
        simultaneous_events+=int(pm["shadowRenders"])
        all_flags["noUnlabeledTransientInjection"] &= pm["unlabeledTransientCount"]==0
        if pm["maxAbsoluteGateFundamentalCents"] is not None:
            gate_cents.append(float(pm["maxAbsoluteGateFundamentalCents"]))
        if pm["maxAbsoluteMixedDiagnosticCents"] is not None:
            mixed_cents.append(float(pm["maxAbsoluteMixedDiagnosticCents"]))

        peak=float(np.max(np.abs(v2a)))
        all_flags["peakUnder0_999"] &= peak<.999
        positive=any(bool(x["attack"]) for x in template["segments"])
        cqt_changed=bool(not np.array_equal(cf,vf))
        if positive:
            all_flags["cqtChangedEveryPositiveSelectedRow"] &= cqt_changed

        rows.append({
            "family":family,"kind":kind,"localPosition":int(local_position),"rowIndex":i,
            "templateIdStored":str(c["template_id"][i]),"variant":int(variant),
            "historicalS9TrainChord":bool(ctx["historicalS9TrainChord"]),
            "manifestParameters":{k:mrow[k] for k in list(AXES)+["nonlinearActive","humActive","humFundamentalHz"]},
            "controlWaveformSha256":_hash_array(control_audio),
            "v2WaveformSha256":_hash_array(v2a),
            "v2RerenderSha256":_hash_array(v2b),
            "controlCqtSha256":_hash_array(cf),
            "v2CqtSha256":_hash_array(vf),
            "cqtChanged":cqt_changed,
            "peak":peak,
            "rms":float(np.sqrt(np.mean(v2a.astype(np.float64)**2))),
            "spectralCentroid":_spectral_centroid(v2a),
            "preparedCqtRowDisplacement":float(np.mean(np.abs(vf.astype(np.float64)-cf.astype(np.float64)))),
            "stateIdentity":bool(state_ok),"onsetIdentity":bool(onset_ok),"referenceIdentity":bool(refs_ok),
            **pm,
        })

    elapsed=time.monotonic()-started
    audio_seconds=renders*CLIP_SECONDS
    max_gate=max(gate_cents) if gate_cents else None
    criteria=dict(all_flags)
    criteria.update({
        "fundamentalWithin15Cents":bool(max_gate is not None and max_gate<=15.0),
        "manifestBindingExact":True,
        "selectedRowsExact":len(rows)==28,
        "simultaneousShadowRenderCountExact":simultaneous_events==24,
        "renderCeiling":renders<=MAX_WAVEFORM_RENDERS,
        "audioSecondsCeiling":audio_seconds<=MAX_AUDIO_SECONDS,
        "wallTimeCeiling":elapsed<=MAX_WALL_SECONDS,
    })
    passed=all(criteria.values())
    result={
        "schema":SCHEMA,
        "status":"passed" if passed else "failed",
        "manifestContentSha256":content_sha,
        "controlFileSha256":EXPECTED_CONTROL_SHA256,
        "selection":{
            "families":list(FAMILIES),
            "trainLocalPositions":list(TRAIN_POSITIONS),
            "challengeLocalPositions":list(CHALLENGE_POSITIONS),
            "selectedV2Rows":28,
        },
        "measurement":{
            "simultaneousDefinitionMicroseconds":1,
            "simultaneousPitchMode":"event-isolated-shadow",
            "nonSimultaneousPitchMode":"mixed-row-original",
            "pitchToleranceCents":15,
            "shadowRenderCount":simultaneous_events,
            "maximumAbsoluteGateFundamentalErrorCents":max_gate,
            "maximumAbsoluteMixedRowDiagnosticErrorCents":max(mixed_cents) if mixed_cents else None,
        },
        "rows":rows,
        "summary":{"criteria":criteria,"stageAV2Passed":passed},
        "execution":{
            "waveformRenders":renders,"audioSeconds":audio_seconds,"elapsedSeconds":elapsed,
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
        raise RuntimeError("persisted byte ceiling exceeded")
    print("SOURCE_DOMAIN_V2_STAGE_A_POLYPHONY_SAFE="+json.dumps({
        "status":result["status"],"criteria":criteria,"measurement":result["measurement"],"execution":result["execution"]
    },sort_keys=True))
    if not passed:
        raise SystemExit("polyphony-safe Stage A V2 admission failed")
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--control",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    if Path(a.out).exists():
        raise RuntimeError("refusing existing output")
    run_stage_a_v2(a.control,a.manifest,a.out)


if __name__=="__main__":
    main()
