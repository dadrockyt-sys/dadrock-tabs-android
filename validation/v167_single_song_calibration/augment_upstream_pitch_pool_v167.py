#!/usr/bin/env python3
"""Augment the reference-blind V167 near-miss pool with upstream pitch evidence.

Adds two evidence-only pools without changing any generated event:
- Guitar: all MIDI 40..88 six-frame harmonic-template candidates at independent
  onset peaks, including pitches not active in Basic Pitch.
- Bass: all MIDI 28..67 harmonic+pYIN candidates at retained-onset and merged-
  proposal sites, including onset sites that lacked a stable-state proposal.

No scorer/reference is accepted as input. This runs before the evidence pool is
frozen and is intended for later whole-rule calibration sweeps only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import instrument_v166_nearmiss_v167 as observer
from run_instrument_v166_nearmiss_v167 import load_v166_module_with_event_logic

EPS = 1e-12


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def guitar_pool(module, guitar_path: Path, pool: dict[str, Any]) -> dict[str, Any]:
    import librosa

    y = module.load_mono(guitar_path)
    env = module.onset_env(y)
    rms = module.rms_env(y)
    cqt, freqs = module.harmonic_cqt(y, module.GUITAR_RANGE[0], module.GUITAR_RANGE[1])
    raw = list((pool.get("guitar") or {}).get("rawBasicPitch") or [])

    independent = np.asarray(
        librosa.onset.onset_detect(
            onset_envelope=env,
            sr=module.SR,
            hop_length=module.HOP,
            backtrack=False,
            units="frames",
        ),
        dtype=int,
    )
    independent = np.asarray(module.collapse_onsets(independent, 0.040), dtype=int)
    peak_frames = sorted({int(module.local_peak(env, int(frame), 3)[0]) for frame in independent})
    rows: list[dict[str, Any]] = []

    for peak_frame in peak_frames:
        seconds = float(librosa.frames_to_time(peak_frame, sr=module.SR, hop_length=module.HOP))
        scores, fundamentals = module.three_frame_template(
            cqt, freqs, peak_frame, module.GUITAR_RANGE[0], module.GUITAR_RANGE[1]
        )
        med_fund = float(np.median(fundamentals))
        onset = module.onset_evidence(
            env,
            peak_frame,
            radius=module.GUITAR_REATTACK_RADIUS_FRAMES,
            positive_q=module.GUITAR_RECOVERY_POSITIVE_QUANTILE,
        )
        activity = float(
            module.support_unit(
                float(rms[int(np.clip(peak_frame, 0, len(rms) - 1))]),
                rms,
            )
        )
        active_parents = [
            row
            for row in raw
            if float(row["startSeconds"]) - EPS <= seconds <= float(row["endSeconds"]) + EPS
        ]
        active_by_midi: dict[int, list[float]] = {}
        for parent in active_parents:
            active_by_midi.setdefault(int(parent["midi"]), []).append(float(parent.get("confidence", 0.0)))

        for midi in range(module.GUITAR_RANGE[0], module.GUITAR_RANGE[1] + 1):
            offset = midi - module.GUITAR_RANGE[0]
            parent_conf = active_by_midi.get(midi, [])
            rows.append(
                {
                    "siteFrame": peak_frame,
                    "siteSeconds": seconds,
                    "midi": midi,
                    "templateScore": float(scores[offset]),
                    "templateRank": float(module.template_rank(scores, offset)),
                    "fundamentalMeanMagnitude": float(fundamentals[offset]),
                    "fundamentalPresent": bool(fundamentals[offset] > med_fund),
                    "onsetSupport": float(onset["normalizedSupport"]),
                    "onsetEvidence": observer.native(onset),
                    "activitySupport": activity,
                    "basicPitchActiveAtSite": bool(parent_conf),
                    "basicPitchActiveParentCount": len(parent_conf),
                    "basicPitchMaxParentConfidence": max(parent_conf) if parent_conf else None,
                    "source": "v166_six_frame_standalone_harmonic_observation",
                }
            )

    return {
        "schema": "dadrock.tabs.v167.guitar-standalone-harmonic-pool.v1",
        "siteCount": len(peak_frames),
        "midiRange": [module.GUITAR_RANGE[0], module.GUITAR_RANGE[1]],
        "candidateCount": len(rows),
        "includesPitchesNotActiveInBasicPitch": True,
        "candidates": rows,
    }


def bass_pool(module, bass_path: Path, pool: dict[str, Any]) -> dict[str, Any]:
    import librosa

    y = module.load_mono(bass_path)
    env = module.onset_env(y)
    rms = module.rms_env(y)
    harmonic, _ = librosa.effects.hpss(y)
    f0, _flag, voiced_prob = librosa.pyin(
        harmonic,
        fmin=librosa.midi_to_hz(module.BASS_RANGE[0]),
        fmax=librosa.midi_to_hz(module.BASS_RANGE[1]),
        sr=module.SR,
        frame_length=2048,
        hop_length=256,
    )
    pyin_midi = librosa.hz_to_midi(np.asarray(f0, dtype=float))
    voiced_prob = np.asarray(voiced_prob, dtype=float)
    cqt, freqs = module.harmonic_cqt(y, module.BASS_RANGE[0], module.BASS_RANGE[1])
    half_frames = max(1, int(round((0.120 / 2.0) * module.SR / module.HOP)))

    bass = pool.get("bass") or {}
    retained = [int(x) for x in bass.get("retainedOnsets") or []]
    proposals = list(bass.get("mergedProposals") or [])
    admitted_states = [
        row
        for row in (bass.get("stateDecisions") or [])
        if row.get("decision") == "ADMITTED"
    ]
    states = [
        {
            "midi": int(row["midi"]),
            "startFrame": int(row["startFrame"]),
            "endFrameExclusive": int(row["endFrameExclusive"]),
            "frameCount": int(row["frameCount"]),
            "medianVoicedProbability": float(row["medianVoicedProbability"]),
        }
        for row in admitted_states
    ]

    site_map: dict[int, dict[str, Any]] = {}
    for frame in retained:
        site_map.setdefault(frame, {"retainedOnset": False, "mergedProposalKinds": []})["retainedOnset"] = True
    for proposal in proposals:
        frame = int(proposal["frame"])
        site = site_map.setdefault(frame, {"retainedOnset": False, "mergedProposalKinds": []})
        site["mergedProposalKinds"].append(str(proposal["kind"]))

    rows: list[dict[str, Any]] = []
    site_summaries: list[dict[str, Any]] = []
    for original_frame in sorted(site_map):
        site_info = site_map[original_frame]
        refined_frame, refine_meta = module.refine_onset_frame(env, original_frame, 8)
        lo = max(0, refined_frame - half_frames)
        hi = min(cqt.shape[1], refined_frame + half_frames + 1)
        frames = list(range(lo, hi)) or [refined_frame]
        hscores, fundamentals = module.template_scores(
            cqt, freqs, frames, module.BASS_RANGE[0], module.BASS_RANGE[1]
        )
        harmonic_z = module.z_across_candidates(hscores)
        p_lo, p_hi = max(0, lo), min(len(pyin_midi), hi)
        finite = np.isfinite(pyin_midi[p_lo:p_hi])
        if np.any(finite):
            pm = float(np.median(pyin_midi[p_lo:p_hi][finite]))
            vp = float(np.nanmedian(voiced_prob[p_lo:p_hi][finite]))
            vp = 0.0 if not math.isfinite(vp) else float(np.clip(vp, 0.0, 1.0))
            midi_values = np.arange(module.BASS_RANGE[0], module.BASS_RANGE[1] + 1, dtype=float)
            proximity = np.exp(-0.5 * ((midi_values - pm) / 0.75) ** 2)
            combined = harmonic_z + 0.75 * vp * proximity
        else:
            pm, vp = None, 0.0
            proximity = np.zeros_like(harmonic_z)
            combined = harmonic_z
        med_fund = float(np.median(fundamentals))
        onset_support, onset_prov = observer.local_admission_support(module, env, refined_frame)
        activity = float(
            module.support_unit(
                float(rms[int(np.clip(refined_frame, 0, len(rms) - 1))]),
                rms,
            )
        )
        nearby_state = module.state_for_frame(states, original_frame)
        seconds = float(librosa.frames_to_time(refined_frame, sr=module.SR, hop_length=module.HOP))
        site_summaries.append(
            {
                "originalFrame": original_frame,
                "refinedFrame": int(refined_frame),
                "seconds": seconds,
                "retainedOnset": bool(site_info["retainedOnset"]),
                "mergedProposalKinds": sorted(site_info["mergedProposalKinds"]),
                "hadNearbyStableState": nearby_state is not None,
                "nearbyStableStateMidi": int(nearby_state["midi"]) if nearby_state is not None else None,
                "medianPyinMidi": pm,
                "medianPyinVoicedProbability": vp,
                "onsetSupport": float(onset_support),
                "activitySupport": activity,
                "onsetRefinement": observer.native(refine_meta),
                "onsetNormalization": observer.native(onset_prov),
            }
        )
        for midi in range(module.BASS_RANGE[0], module.BASS_RANGE[1] + 1):
            offset = midi - module.BASS_RANGE[0]
            rows.append(
                {
                    "originalFrame": original_frame,
                    "refinedFrame": int(refined_frame),
                    "seconds": seconds,
                    "midi": midi,
                    "retainedOnset": bool(site_info["retainedOnset"]),
                    "mergedProposalKinds": sorted(site_info["mergedProposalKinds"]),
                    "hadNearbyStableState": nearby_state is not None,
                    "nearbyStableStateMidi": int(nearby_state["midi"]) if nearby_state is not None else None,
                    "harmonicTemplateScore": float(hscores[offset]),
                    "harmonicZScore": float(harmonic_z[offset]),
                    "fundamentalMeanMagnitude": float(fundamentals[offset]),
                    "fundamentalPresent": bool(fundamentals[offset] > med_fund),
                    "medianPyinMidi": pm,
                    "medianPyinVoicedProbability": vp,
                    "pyinProximity": float(proximity[offset]),
                    "combinedPitchScore": float(combined[offset]),
                    "templateRank": float(module.template_rank(combined, offset)),
                    "onsetSupport": float(onset_support),
                    "activitySupport": activity,
                    "source": "v166_pre_admission_bass_pitch_observation",
                }
            )

    return {
        "schema": "dadrock.tabs.v167.bass-upstream-pitch-pool.v1",
        "siteCount": len(site_summaries),
        "midiRange": [module.BASS_RANGE[0], module.BASS_RANGE[1]],
        "candidateCount": len(rows),
        "siteSummaries": site_summaries,
        "candidates": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--guitar", type=Path, required=True)
    ap.add_argument("--bass", type=Path, required=True)
    ap.add_argument("--v166-transcriber", type=Path, required=True)
    args = ap.parse_args()
    for path in (args.pool, args.guitar, args.bass, args.v166_transcriber):
        if not path.is_file():
            raise RuntimeError(f"missing upstream-pool input: {path}")

    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    policy = pool.get("policy") or {}
    if policy.get("referenceRead") is not False or policy.get("scorerRead") is not False:
        raise RuntimeError("near-miss pool is not reference-blind")
    if policy.get("thresholdTuningPerformed") is not False:
        raise RuntimeError("near-miss pool was already tuned")

    module = load_v166_module_with_event_logic(args.v166_transcriber)
    guitar = guitar_pool(module, args.guitar, pool)
    bass = bass_pool(module, args.bass, pool)
    pool["upstreamPitchPools"] = {"guitarStandaloneHarmonic": guitar, "bassPreAdmission": bass}
    pool["policy"]["standaloneHarmonicPitchDiscoveryObserved"] = True
    pool["policy"]["referenceReadDuringUpstreamPitchObservation"] = False
    pool["policy"]["scorerReadDuringUpstreamPitchObservation"] = False
    pool["policy"]["generatedEventsChangedByUpstreamPitchObservation"] = False
    pool["upstreamPitchPoolInputSha256"] = {
        "guitarStem": sha256_file(args.guitar),
        "bassStem": sha256_file(args.bass),
    }
    args.pool.write_text(json.dumps(observer.native(pool), indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "guitarSites": guitar["siteCount"],
        "guitarCandidates": guitar["candidateCount"],
        "bassSites": bass["siteCount"],
        "bassCandidates": bass["candidateCount"],
        "referenceRead": False,
        "scorerRead": False,
        "generatedEventsChanged": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
