#!/usr/bin/env python3
"""Source-isolating pitch diagnostic for Astra V2 Stage-A.

Model-free diagnostic only. It preserves the exact selected V2 rows, event indices,
clip-level manifest parameters, per-note substreams and post chain, while rendering
one attacked musical event per probe to remove simultaneous-note FFT competition.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from scipy.signal import lfilter, resample_poly

from synthetic.s0_pilot_v1 import INTERNAL_SR, OUTPUT_SR, CLIP_SECONDS, OPEN_MIDI
from synthetic.source_domain_joint_coverage_manifest_v2 import EXPECTED_CONTROL_SHA256
from synthetic.source_domain_simulator_diversity_v1 import (
    FINAL_PEAK, _apply_color, _component, _fundamental_cents, _hash_array,
    _note_params, _rng, source_parameters,
)
from synthetic.source_domain_v2_stage_a_admission_v1 import (
    EXPECTED_MANIFEST_CONTENT_SHA256, _manifest_payload_sha, _override_from_manifest,
    _row_context, _selected_rows,
)

SCHEMA="astra-source-domain-v2-source-isolating-pitch-result-v1"
MAX_RENDERS=172
MAX_AUDIO_SECONDS=344.0
MAX_WALL_SECONDS=20*60.0
MAX_PERSISTED_BYTES=100*1024*1024


def _sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()


def _render_isolated(template,variant,event_index,override):
    params=dict(source_parameters(template["templateId"],variant))
    params.update(override)
    row=template["segments"][event_index]
    if not bool(row["attack"]):
        raise RuntimeError("isolated pitch probe must target attacked event")

    n=int(round(CLIP_SECONDS*INTERNAL_SR))
    audio=np.zeros(n,dtype=np.float64)
    start=int(round(float(row["start"])*INTERNAL_SR))
    end=min(n,int(round(float(row["end"])*INTERNAL_SR)))
    if end<=start or start>=n:
        raise RuntimeError("invalid isolated event bounds")

    pitch=OPEN_MIDI[int(row["string"])]+int(row["fret"])
    freq=440.0*(2.0**((pitch-69)/12.0))
    note=_note_params(template["templateId"],variant,event_index,None)
    base_damping=1.15*float(params["dampingMultiplier"])
    damping=base_damping*float(note["dampingMultiplier"])*(4.5 if row["palm"] else 1.0)*(1.0+.04*int(row["string"]))
    rise=float(np.clip(float(params["attackBaseRiseSeconds"])*float(note["riseMultiplier"]),.001,.060))
    erng=_rng(template["templateId"],variant,"component",event_index)
    comp=_component(
        freq,(end-start)/INTERNAL_SR,INTERNAL_SR,erng,
        damping=damping,
        pick_position=float(params["pickPosition"]),
        brightness=float(params["brightness"]),
        attack_rise=rise,
        transient=True,
        transient_gain=float(params["transientNoiseGain"]),
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
        if params["humActive"] and params["humCombinedRmsRelative"]>0:
            t=np.arange(n,dtype=np.float64)/INTERNAL_SR
            f=float(params["humFundamentalHz"])
            hum=np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*2*f*t)+.25*np.sin(2*np.pi*3*f*t)
            hr=float(np.sqrt(np.mean(hum*hum)))
            audio += hum*(float(params["humCombinedRmsRelative"])*rms/max(hr,1e-12))

    audio=lfilter([.12],[1.0,-.88],audio)
    peak=float(np.max(np.abs(audio)))
    if peak>0:
        audio=FINAL_PEAK*audio/peak
    out=resample_poly(audio,1,2).astype(np.float32)
    want=int(round(CLIP_SECONDS*OUTPUT_SR))
    out=np.pad(out,(0,max(0,want-len(out))))[:want]
    if not np.isfinite(out).all():
        raise RuntimeError("nonfinite isolated probe")
    final_peak=float(np.max(np.abs(out)))
    if final_peak>FINAL_PEAK:
        out=(out*(FINAL_PEAK/final_peak)).astype(np.float32,copy=False)
    if float(np.max(np.abs(out)))>=.999:
        raise RuntimeError("isolated probe clipping guard")
    return out,{
        "pitch":int(pitch),"frequencyHz":float(freq),
        "start":float(row["start"]),"end":float(row["end"]),
        "eventIndex":int(event_index),"riseSeconds":rise,
        "params":params,
    }


def run(control_path,manifest_path,stage_a_result_path,out_path):
    started=time.monotonic()
    if _sha256_file(control_path)!=EXPECTED_CONTROL_SHA256:
        raise RuntimeError("control hash mismatch")
    manifest=json.loads(Path(manifest_path).read_text())
    if _manifest_payload_sha(manifest)!=EXPECTED_MANIFEST_CONTENT_SHA256:
        raise RuntimeError("manifest content mismatch")
    if manifest.get("manifestContentSha256")!=EXPECTED_MANIFEST_CONTENT_SHA256:
        raise RuntimeError("embedded manifest hash mismatch")

    frozen=json.loads(Path(stage_a_result_path).read_text())
    if frozen.get("schema")!="astra-source-domain-v2-stage-a-acoustic-admission-v1":
        raise RuntimeError("wrong frozen Stage-A artifact")
    if frozen["manifestContentSha256"]!=EXPECTED_MANIFEST_CONTENT_SHA256:
        raise RuntimeError("Stage-A artifact manifest mismatch")

    control=np.load(control_path,allow_pickle=False)
    chord_train=np.flatnonzero((control["family"]=="chords")&(control["split"]=="train"))
    frozen_rows={(int(r["rowIndex"]),int(e["eventIndex"])):e
                 for r in frozen["rows"] for e in r["attackedEvents"]}

    rows=[]
    renders=0
    measurable_original=0
    measurable_isolated=0
    missing_original_measurable=0
    outside=[]
    all_deterministic=True
    all_finite=True
    all_peak=True

    for family,kind,local_position,mrow in _selected_rows(manifest):
        row_index=int(mrow["rowIndex"])
        template,variant,_,ctx=_row_context(control,row_index,chord_train)
        override=_override_from_manifest(mrow)
        for event_index,event in enumerate(template["segments"]):
            if not bool(event["attack"]):
                continue
            probe1,meta=_render_isolated(template,variant,event_index,override)
            probe2,_=_render_isolated(template,variant,event_index,override)
            renders += 2
            deterministic=bool(np.array_equal(probe1,probe2))
            finite=bool(np.isfinite(probe1).all())
            peak=float(np.max(np.abs(probe1)))
            peak_ok=peak<.999
            all_deterministic &= deterministic
            all_finite &= finite
            all_peak &= peak_ok

            stable_start=min(meta["end"]-.04,meta["start"]+.10)
            stable_end=min(meta["end"],stable_start+.12)
            cents=_fundamental_cents(probe1,meta["frequencyHz"],stable_start,stable_end)
            if cents is not None:
                measurable_isolated += 1
            prior=frozen_rows.get((row_index,event_index))
            prior_cents=None if prior is None else prior.get("fundamentalCents")
            if prior_cents is not None:
                measurable_original += 1
                if cents is None:
                    missing_original_measurable += 1
            if cents is not None and abs(float(cents))>15.0:
                outside.append({
                    "family":family,"kind":kind,"rowIndex":row_index,
                    "eventIndex":event_index,"pitch":meta["pitch"],
                    "isolatedCents":float(cents),"originalMixedCents":prior_cents,
                })
            rows.append({
                "family":family,"kind":kind,"localPosition":int(local_position),
                "rowIndex":row_index,"eventIndex":int(event_index),
                "pitch":meta["pitch"],"variant":int(variant),
                "historicalS9TrainChord":bool(ctx["historicalS9TrainChord"]),
                "waveformSha256":_hash_array(probe1),
                "rerenderSha256":_hash_array(probe2),
                "deterministic":deterministic,"finite":finite,"peak":peak,
                "isolatedFundamentalCents":cents,
                "originalMixedFundamentalCents":prior_cents,
                "absoluteMeasurementChangeCents":None if cents is None or prior_cents is None else abs(float(cents)-float(prior_cents)),
            })

    elapsed=time.monotonic()-started
    audio_seconds=renders*CLIP_SECONDS
    criteria={
        "deterministicRerender":bool(all_deterministic),
        "finiteAndPeakBounded":bool(all_finite and all_peak),
        "exactSelectedRows":len(_selected_rows(manifest))==28,
        "allOriginalMeasurableEventsRetained":bool(measurable_original==86 and missing_original_measurable==0),
        "allIsolatedMeasurableWithin15Cents":bool(measurable_isolated>=measurable_original and len(outside)==0),
        "renderCeiling":renders<=MAX_RENDERS,
        "audioSecondsCeiling":audio_seconds<=MAX_AUDIO_SECONDS,
        "wallTimeCeiling":elapsed<=MAX_WALL_SECONDS,
    }
    result={
        "schema":SCHEMA,
        "status":"passed" if all(criteria.values()) else "failed",
        "frozenManifestContentSha256":EXPECTED_MANIFEST_CONTENT_SHA256,
        "frozenControlSha256":EXPECTED_CONTROL_SHA256,
        "rows":rows,
        "summary":{
            "attackedProbeEvents":len(rows),
            "originalMeasurableEvents":measurable_original,
            "isolatedMeasurableEvents":measurable_isolated,
            "missingOriginalMeasurableEvents":missing_original_measurable,
            "outside15Cents":outside,
            "maxAbsoluteIsolatedCents":max([abs(float(r["isolatedFundamentalCents"])) for r in rows if r["isolatedFundamentalCents"] is not None],default=None),
            "criteria":criteria,
            "admissionPassed":all(criteria.values()),
        },
        "execution":{
            "waveformRenders":renders,"audioSeconds":audio_seconds,"elapsedSeconds":elapsed,
            "modelLoads":0,"modelInference":False,"optimizerSteps":0,
            "thresholdWork":False,"automaticRetry":False,
            "p1Accessed":False,"p2Accessed":False,"p3Opened":False,
            "paidComputeDollars":0,"productionMutation":False,
        }
    }
    Path(out_path).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if Path(out_path).stat().st_size>MAX_PERSISTED_BYTES:
        raise RuntimeError("persisted-byte ceiling exceeded")
    print("SOURCE_ISOLATING_PITCH="+json.dumps({
        "status":result["status"],"summary":result["summary"],"execution":result["execution"]
    },sort_keys=True))
    if not result["summary"]["admissionPassed"]:
        raise SystemExit("source-isolating pitch diagnostic failed")
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--control",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--stage-a-result",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    if Path(a.out).exists():
        raise RuntimeError("refusing existing output")
    run(a.control,a.manifest,a.stage_a_result,a.out)


if __name__=="__main__":
    main()
