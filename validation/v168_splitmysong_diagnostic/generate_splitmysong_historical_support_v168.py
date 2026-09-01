#!/usr/bin/env python3
"""One-shot reference-blind SplitMySong generator using exact persisted V166 shared support.

This is the implementation of the separately frozen historical-shared-support
neighborhood preregistration. It never regenerates historical Demucs stems. After
one Basic Pitch observation on the private SplitMySong Guitar, it fails closed
unless every actual V166 pre-grid event timing option (nearest-1/nearest/nearest+1)
is backed by an exact historical sharedSupport row already persisted in the frozen
V166 candidate. No reference/scorer path is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

import generate_splitmysong_candidate_v168 as frozen_core
import historical_shared_support_v168 as historical

BRANCH = "v143-contextual-prune-lobo"
FROZEN_CORE_BLOB = "95972fb9b1f9c1bf4872e2c945025b4aa69a312c"
HISTORICAL_HELPER_BLOB = "c9b5cc1bc4076be77780d64f73d53f2a7083f94f"
PREREG_BLOB = "f34661e2d67f9f1c541b80ac01af2c6ea82e2159"
V166_CANDIDATE_BLOB = "c36a4d1e14ca66235b51a866ad3908322834efff"
V166_TIMEBASE_BLOB = "abebae25801b7ddeb5b933977c4f4a918f7bf9ef"
PREREG_PATH = "debug/v168-splitmysong-diagnostic/historical-shared-support-neighborhood-preregistration.json"
HELPER_PATH = "validation/v168_splitmysong_diagnostic/historical_shared_support_v168.py"
CORE_PATH = "validation/v168_splitmysong_diagnostic/generate_splitmysong_candidate_v168.py"
V166_CANDIDATE_PATH = "debug/v166-cpu-autonomous/generated.json"
V166_TIMEBASE_PATH = "debug/v166-cpu-autonomous/timebase.json"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.chmod(path, 0o600)


def verify_new_path(repo: Path) -> dict[str, str]:
    pins = {
        CORE_PATH: FROZEN_CORE_BLOB,
        HELPER_PATH: HISTORICAL_HELPER_BLOB,
        PREREG_PATH: PREREG_BLOB,
        V166_CANDIDATE_PATH: V166_CANDIDATE_BLOB,
        V166_TIMEBASE_PATH: V166_TIMEBASE_BLOB,
    }
    observed: dict[str, str] = {}
    for rel, expected in pins.items():
        path = repo / rel
        if not path.is_file():
            raise RuntimeError(f"missing frozen historical-support input: {rel}")
        blob = git_blob_sha(path)
        observed[rel] = blob
        if blob != expected:
            raise RuntimeError(f"frozen Git blob mismatch for {rel}: {blob} != {expected}")
    prereg = json.loads((repo / PREREG_PATH).read_text(encoding="utf-8"))
    if prereg.get("status") != "PREREGISTERED_BEFORE_SPLITMYSONG_PITCH_INFERENCE_OR_NEIGHBORHOOD_RESULT":
        raise RuntimeError("historical-support preregistration state invalid")
    safety = prereg.get("safety") or {}
    if not (
        safety.get("splitMySongPitchInferenceInvokedAtPreregistration") is False
        and safety.get("splitMySongCandidateGeneratedAtPreregistration") is False
        and safety.get("referenceRead") is False
        and safety.get("scorerRead") is False
    ):
        raise RuntimeError("historical-support preregistration safety boundary invalid")
    return observed


def observe_splitmysong_guitar(repo: Path, normalized_guitar: Path):
    from basic_pitch import ICASSP_2022_MODEL_PATH
    import basic_pitch.inference as bp_inference

    model_path = Path(ICASSP_2022_MODEL_PATH)
    frozen_core.require_file_sha(
        model_path, frozen_core.BASIC_PITCH_MODEL_SHA256, "Basic Pitch model"
    )
    runner, augment, phase, step_apply, state_builder = frozen_core.import_pipeline_modules(repo)
    v166_path = repo / "validation/v166_cpu_autonomous/transcribe_v166.py"
    module = runner.load_v166_module_with_event_logic(v166_path)

    original_predict = bp_inference.predict
    cache: dict[str, Any] = {}
    counters = {"wrapperCalls": 0, "actualInferenceCalls": 0}

    def cached_predict(*args, **kwargs):
        counters["wrapperCalls"] += 1
        if "result" not in cache:
            cache["result"] = original_predict(*args, **kwargs)
            counters["actualInferenceCalls"] += 1
        return cache["result"]

    bp_inference.predict = cached_predict
    try:
        pregrid_events, v166_meta, guitar_env = module.guitar_events(normalized_guitar)
    finally:
        bp_inference.predict = original_predict

    if counters["actualInferenceCalls"] != 1:
        raise AssertionError(f"expected exactly one Basic Pitch inference, got {counters}")
    notes = cache["result"][2]
    raw_basic_pitch = frozen_core.raw_basic_pitch_from_notes(
        notes, module.GUITAR_RANGE[0], module.GUITAR_RANGE[1]
    )
    if len(raw_basic_pitch) != int(v166_meta["basicPitchRawEventCount"]):
        raise AssertionError("cached Basic Pitch raw note count disagrees with V166 front-end")
    modules = {
        "runner": runner,
        "augment": augment,
        "phase": phase,
        "step_apply": step_apply,
        "state_builder": state_builder,
        "v166": module,
    }
    return pregrid_events, v166_meta, guitar_env, raw_basic_pitch, counters, modules


def neighborhood_gate(
    events: list[dict[str, Any]],
    lattice: list[float],
    support_table: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    if len(lattice) < 2:
        raise RuntimeError("frozen V166 lattice too short")
    first_half = 0.5 * float(lattice[1] - lattice[0])
    required: set[int] = set()
    pregrid_excluded = 0
    eligible_events = 0
    event_neighborhoods: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        event_time = float(event["startSeconds"])
        if event_time < float(lattice[0]) - first_half:
            pregrid_excluded += 1
            continue
        eligible_events += 1
        nearest, options = historical.option_steps_for_event(event_time, lattice)
        required.update(options)
        event_neighborhoods.append(
            {
                "eventIndex": index,
                "eventTimeSeconds": event_time,
                "midi": int(event["midi"]),
                "nearestStep": nearest,
                "candidateSteps": options,
            }
        )
    covered = sorted(step for step in required if step in support_table)
    missing = sorted(step for step in required if step not in support_table)
    return {
        "status": "PASS" if not missing else "FAIL_CLOSED_NO_CANDIDATE",
        "preGridEventCount": len(events),
        "preGridExcludedCount": pregrid_excluded,
        "eligibleEventCount": eligible_events,
        "requiredUniqueStepCount": len(required),
        "coveredRequiredStepCount": len(covered),
        "missingRequiredStepCount": len(missing),
        "requiredCoveragePercent": 100.0 if not required else 100.0 * len(covered) / len(required),
        "missingRequiredSteps": missing,
        "requiredSteps": sorted(required),
        "eventNeighborhoods": event_neighborhoods,
        "historicalTableCoveredStepCount": len(support_table),
        "historicalTableLatticeStepCount": len(lattice),
        "noInterpolation": True,
        "noExtrapolation": True,
        "freshDemucsUsed": False,
        "referenceRead": False,
        "scorerRead": False,
    }


def map_events_with_historical_support(
    module,
    events: list[dict[str, Any]],
    lattice: list[float],
    instrument_env: np.ndarray,
    support_table: dict[int, dict[str, Any]],
    stream: str,
) -> tuple[list[dict[str, Any]], int, int]:
    gate = neighborhood_gate(events, lattice, support_table)
    if gate["status"] != "PASS":
        raise RuntimeError("historical shared-support neighborhood coverage is incomplete")

    mapped: dict[tuple[int, int], dict[str, Any]] = {}
    pregrid = corrected = 0
    first_half = 0.5 * float(lattice[1] - lattice[0])
    for row in events:
        event_time = float(row["startSeconds"])
        if event_time < float(lattice[0]) - first_half:
            pregrid += 1
            continue
        nearest, options = historical.option_steps_for_event(event_time, lattice)
        candidate_rows: list[dict[str, Any]] = []
        for step in options:
            shared = support_table.get(step)
            if shared is None:
                raise RuntimeError(f"required historical shared support missing at step {step}")
            if step == 0:
                nominal_sub = float(lattice[1] - lattice[0])
            elif step == len(lattice) - 1:
                nominal_sub = float(lattice[-1] - lattice[-2])
            else:
                nominal_sub = 0.5 * float(lattice[step + 1] - lattice[step - 1])
            beat_index, beat_start, beat_end = module._candidate_beat_bounds(lattice, step)
            if beat_index != int(shared["normalizationBeatIndex"]):
                raise RuntimeError(f"historical beat provenance mismatch at step {step}")
            inst_frame = module.seconds_to_nearest_frame(
                float(lattice[step]), len(instrument_env)
            )
            inst_support, inst_prov = module.beat_support_unit(
                float(instrument_env[inst_frame]), instrument_env, beat_start, beat_end
            )
            score = module.event_step_score(
                event_time,
                float(lattice[step]),
                nominal_sub,
                inst_support,
                float(shared["sharedSupport"]),
            )
            candidate_rows.append(
                {
                    "step": int(step),
                    "score": float(score),
                    "instrumentSupport": float(inst_support),
                    "sharedSupport": float(shared["sharedSupport"]),
                    "time": float(lattice[step]),
                    "normalizationBeatIndex": int(beat_index),
                    "instrumentNormalizationLoFrame": int(inst_prov["loFrame"]),
                    "instrumentNormalizationHiFrame": int(inst_prov["hiFrame"]),
                    "sharedNormalizationLoFrame": int(shared["sharedNormalizationLoFrame"]),
                    "sharedNormalizationHiFrame": int(shared["sharedNormalizationHiFrame"]),
                }
            )
        winner = historical.select_from_rows(nearest, candidate_rows)
        selected_step = int(winner["step"])
        corrected += int(selected_step != nearest)
        selection = {
            "nearestStep": int(nearest),
            "winner": dict(winner),
            "candidates": candidate_rows,
            "sharedSupportSource": "frozen_v166_persisted_stepSelection",
        }
        item = dict(row)
        item.update(
            {
                "absoluteGridStep": selected_step,
                "measure": selected_step // frozen_core.STEPS_PER_MEASURE + 1,
                "step": selected_step % frozen_core.STEPS_PER_MEASURE,
                "stream": stream,
                "nearestLatticeStep": int(nearest),
                "selectedLatticeTimeSeconds": float(lattice[selected_step]),
                "gridCorrectionSteps": int(selected_step - nearest),
                "stepSelection": selection,
            }
        )
        key = (selected_step, int(item["midi"]))
        old = mapped.get(key)
        if old is None:
            mapped[key] = item
        else:
            new_evidence = float(item.get("admissionScore", item.get("recoveryScore", 0.0)))
            old_evidence = float(old.get("admissionScore", old.get("recoveryScore", 0.0)))
            new_conf = float(item.get("confidence", item.get("medianPyinVoicedProbability", 0.0)))
            old_conf = float(old.get("confidence", old.get("medianPyinVoicedProbability", 0.0)))
            if (-new_evidence, -new_conf, int(item["midi"])) < (
                -old_evidence,
                -old_conf,
                int(old["midi"]),
            ):
                mapped[key] = item
    rows = list(mapped.values())
    rows = module.cap_guitar_polyphony(rows) if stream == "combinedGuitar" else module.cap_bass_grid(rows)
    return rows, pregrid, corrected


def downstream_i005(
    repo: Path,
    normalized_guitar: Path,
    mapped_guitar: list[dict[str, Any]],
    raw_basic_pitch: list[dict[str, Any]],
    lattice: list[float],
    modules: dict[str, Any],
):
    module = modules["v166"]
    augment = modules["augment"]
    phase = modules["phase"]
    step_apply = modules["step_apply"]
    state_builder = modules["state_builder"]

    i001_guitar = [phase.shift_event(row, -12) for row in mapped_guitar]
    rule_code = repo / "validation/v167_single_song_calibration/step_rule_sweep_v167.py"
    rule_module = step_apply.load_rule_module(rule_code)
    i002_guitar, i002_summary = step_apply.transform_stream(
        i001_guitar, "combinedGuitar", "max_score_x_shared", rule_module
    )
    pool_seed = {"guitar": {"rawBasicPitch": raw_basic_pitch}}
    standalone_pool = augment.guitar_pool(module, normalized_guitar, pool_seed)
    rows = list(standalone_pool["candidates"])
    config = state_builder.full_config(
        "gss-active-only",
        inactive_enabled=False,
        inactive_ratio_min=None,
        inactive_interval_policy=None,
    )
    final_guitar, i005_summary = state_builder.build_guitar(
        i002_guitar, rows, config, lattice
    )
    coords = [
        (int(row["absoluteGridStep"]), int(row["midi"])) for row in final_guitar
    ]
    if len(coords) != len(set(coords)):
        raise AssertionError("final Guitar candidate contains duplicate step/MIDI coordinates")
    per_step: dict[int, int] = {}
    for absolute, _midi in coords:
        if absolute < 0:
            raise AssertionError("negative final Guitar grid step")
        per_step[absolute] = per_step.get(absolute, 0) + 1
    if max(per_step.values(), default=0) > 6:
        raise AssertionError("final Guitar candidate exceeds frozen polyphony cap")
    return final_guitar, i001_guitar, i002_guitar, i002_summary, standalone_pool, config, i005_summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--normalized-guitar", type=Path, required=True)
    ap.add_argument("--arm-receipt", type=Path, required=True)
    ap.add_argument("--environment-receipt", type=Path, required=True)
    ap.add_argument("--ffmpeg-receipt", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    repo = args.repo_root.resolve()
    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o700)

    attempt_marker = out_dir / "splitmysong-historical-support-attempt.marker"
    observation_path = out_dir / "splitmysong-basic-pitch-observation.json"
    gate_path = out_dir / "splitmysong-historical-support-neighborhood-gate.json"
    candidate_path = out_dir / "splitmysong-i005-candidate.json"
    receipt_path = out_dir / "splitmysong-generation-receipt.json"
    freeze_path = out_dir / "splitmysong-candidate-freeze.json"
    for path in (
        attempt_marker,
        observation_path,
        gate_path,
        candidate_path,
        receipt_path,
        freeze_path,
    ):
        if path.exists():
            raise RuntimeError(f"one-shot output/marker already exists; rerun forbidden: {path}")

    frozen_core.require_file_sha(
        args.source, frozen_core.PRIVATE_SOURCE_SHA256, "private SplitMySong source"
    )
    frozen_core.require_file_sha(
        args.normalized_guitar,
        frozen_core.NORMALIZED_GUITAR_SHA256,
        "normalized SplitMySong Guitar",
    )
    frozen_core.require_file_sha(
        args.arm_receipt, frozen_core.ARM_RECEIPT_SHA256, "ARM preflight receipt"
    )
    frozen_core.require_file_sha(
        args.environment_receipt,
        frozen_core.ENV_RECEIPT_SHA256,
        "CPU environment receipt",
    )
    frozen_core.require_file_sha(
        args.ffmpeg_receipt,
        frozen_core.FFMPEG_RECEIPT_SHA256,
        "FFmpeg normalizer receipt",
    )
    repo_blobs = frozen_core.verify_repo(repo)
    repo_blobs.update(verify_new_path(repo))
    runtime = frozen_core.verify_runtime()
    _candidate, lattice, support_table, support_report = historical.load_and_validate(repo)

    attempt_marker.write_text(
        "ONE_SHOT_REFERENCE_BLIND_BASIC_PITCH_OBSERVATION_STARTED\n",
        encoding="utf-8",
    )
    os.chmod(attempt_marker, 0o600)

    (
        pregrid_events,
        v166_meta,
        guitar_env,
        raw_basic_pitch,
        inference_counters,
        modules,
    ) = observe_splitmysong_guitar(repo, args.normalized_guitar)

    observation = {
        "schema": "dadrock.tabs.v168.splitmysong-basic-pitch-observation.v1",
        "status": "REFERENCE_BLIND_ONE_SHOT_OBSERVATION_FROZEN",
        "sourceSha256": frozen_core.PRIVATE_SOURCE_SHA256,
        "normalizedGuitarSha256": frozen_core.NORMALIZED_GUITAR_SHA256,
        "basicPitchModelSha256": frozen_core.BASIC_PITCH_MODEL_SHA256,
        "basicPitchInference": inference_counters,
        "rawBasicPitch": raw_basic_pitch,
        "v166PreGridEvents": pregrid_events,
        "v166Metadata": v166_meta,
        "referenceRead": False,
        "scorerRead": False,
        "gpuCudaUsed": False,
        "modalUsed": False,
    }
    write_json(observation_path, observation)
    observation_sha = frozen_core.sha256_file(observation_path)

    gate = neighborhood_gate(pregrid_events, lattice, support_table)
    gate.update(
        {
            "schema": "dadrock.tabs.v168.splitmysong-historical-shared-support-neighborhood-gate.v1",
            "preregistrationGitBlob": PREREG_BLOB,
            "historicalSupportHelperGitBlob": HISTORICAL_HELPER_BLOB,
            "basicPitchObservationSha256": observation_sha,
            "historicalSupportTableReport": support_report,
            "pitchInferenceInvoked": True,
            "basicPitchActualInferenceCalls": int(inference_counters["actualInferenceCalls"]),
            "candidateGenerated": False,
            "referenceFacingScoreCalls": 0,
        }
    )
    write_json(gate_path, gate)
    gate_sha = frozen_core.sha256_file(gate_path)

    if gate["status"] != "PASS":
        print(
            json.dumps(
                {
                    "status": gate["status"],
                    "basicPitchObservationSha256": observation_sha,
                    "neighborhoodGateSha256": gate_sha,
                    "requiredUniqueStepCount": gate["requiredUniqueStepCount"],
                    "missingRequiredStepCount": gate["missingRequiredStepCount"],
                    "missingRequiredSteps": gate["missingRequiredSteps"],
                    "candidateGenerated": False,
                    "referenceRead": False,
                    "scorerRead": False,
                },
                sort_keys=True,
            )
        )
        return 2

    mapped_guitar, pre_grid, evidence_corrections = map_events_with_historical_support(
        modules["v166"],
        pregrid_events,
        lattice,
        guitar_env,
        support_table,
        "combinedGuitar",
    )
    (
        final_guitar,
        i001_guitar,
        i002_guitar,
        i002_summary,
        standalone_pool,
        config,
        i005_summary,
    ) = downstream_i005(
        repo,
        args.normalized_guitar,
        mapped_guitar,
        raw_basic_pitch,
        lattice,
        modules,
    )

    candidate = {
        "schema": "dadrock.tabs.v168.splitmysong-ayggmw-diagnostic-candidate.v2-historical-support",
        "version": "V168_SPLITMYSONG_DIAGNOSTIC",
        "status": "REFERENCE_BLIND_CANDIDATE_FROZEN_PENDING_LEGACY_SCORE",
        "diagnosticOnly": True,
        "song": {
            "artist": "Lenny Kravitz",
            "title": "Are You Gonna Go My Way",
            "alignmentStartOffsetSeconds": 0.0,
            "timeStretchApplied": False,
        },
        "streams": {"combinedGuitar": final_guitar},
        "pipeline": {
            "changedAudioInput": "guitar_audio_only",
            "historicalTimebasePreserved": True,
            "historicalSharedSupportPreservedAtEveryConsultedTimingOption": True,
            "historicalSharedSupportSource": V166_CANDIDATE_PATH,
            "historicalDemucsStemBytesRegenerated": False,
            "historicalSharedSupportNeighborhoodGateSha256": gate_sha,
            "v166RawBasicPitchCount": int(v166_meta["basicPitchRawEventCount"]),
            "v166MappedGuitarCount": len(mapped_guitar),
            "v167I001EquivalentGuitarCount": len(i001_guitar),
            "v167I002EquivalentGuitarCount": len(i002_guitar),
            "v167I002RuleSummary": i002_summary,
            "upstreamPitchPoolSiteCount": int(standalone_pool["siteCount"]),
            "upstreamPitchPoolCandidateCount": int(standalone_pool["candidateCount"]),
            "i005Config": config,
            "i005Summary": i005_summary,
            "finalGuitarCount": len(final_guitar),
            "preGridExcludedAtV166": int(pre_grid),
            "evidenceStepCorrectionsAtV166": int(evidence_corrections),
            "basicPitchInference": inference_counters,
        },
        "safety": {
            "referenceRead": False,
            "scorerRead": False,
            "referenceFacingScoreCalls": 0,
            "professionalReferencePathsOpened": 0,
            "referenceGuidedFiltering": False,
            "thresholdTuningPerformed": False,
            "humanCorrection": False,
            "pitchInferenceInvoked": True,
            "candidateGenerated": True,
            "gpuCudaUsed": False,
            "modalUsed": False,
            "mainOrProductionModified": False,
        },
    }
    write_json(candidate_path, candidate)
    candidate_sha = frozen_core.sha256_file(candidate_path)

    receipt = {
        "schema": "dadrock.tabs.v168.splitmysong-ayggmw-diagnostic-generation-receipt.v2-historical-support",
        "status": "REFERENCE_BLIND_CANDIDATE_GENERATED_AND_HASH_FROZEN",
        "candidateSha256": candidate_sha,
        "basicPitchObservationSha256": observation_sha,
        "historicalSharedSupportNeighborhoodGateSha256": gate_sha,
        "inputIdentities": {
            "privateSplitMySongSourceSha256": frozen_core.PRIVATE_SOURCE_SHA256,
            "normalizedSplitMySongGuitarSha256": frozen_core.NORMALIZED_GUITAR_SHA256,
            "armReceiptSha256": frozen_core.ARM_RECEIPT_SHA256,
            "environmentReceiptSha256": frozen_core.ENV_RECEIPT_SHA256,
            "ffmpegReceiptSha256": frozen_core.FFMPEG_RECEIPT_SHA256,
            "v166CandidateSha256": historical.V166_CANDIDATE_SHA256,
            "v166TimebaseSha256": historical.V166_TIMEBASE_SHA256,
        },
        "repositoryGitBlobs": repo_blobs,
        "runtime": runtime,
        "generation": {
            "v166Metadata": v166_meta,
            "basicPitchRawCount": len(raw_basic_pitch),
            "mappedGuitarCount": len(mapped_guitar),
            "i001Count": len(i001_guitar),
            "i002Count": len(i002_guitar),
            "finalGuitarCount": len(final_guitar),
            "i002Summary": i002_summary,
            "i005Summary": i005_summary,
            "basicPitchInference": inference_counters,
        },
        "safety": {
            "referenceRead": False,
            "scorerRead": False,
            "referenceFacingScoreCalls": 0,
            "professionalReferencePathsOpened": 0,
            "referenceGuidedFiltering": False,
            "thresholdTuningPerformed": False,
            "humanCorrection": False,
            "candidateGenerated": True,
            "pitchInferenceInvoked": True,
            "basicPitchActualInferenceCalls": int(inference_counters["actualInferenceCalls"]),
            "gpuCudaUsed": False,
            "modalUsed": False,
            "mainOrProductionModified": False,
        },
    }
    write_json(receipt_path, receipt)
    receipt_sha = frozen_core.sha256_file(receipt_path)

    freeze = {
        "schema": "dadrock.tabs.v168.splitmysong-ayggmw-diagnostic-candidate-freeze.v2-historical-support",
        "status": "FROZEN_BEFORE_ANY_LEGACY_REFERENCE_OR_SCORER_ACCESS",
        "candidateSha256": candidate_sha,
        "generationReceiptSha256": receipt_sha,
        "basicPitchObservationSha256": observation_sha,
        "historicalSharedSupportNeighborhoodGateSha256": gate_sha,
        "referenceRead": False,
        "scorerRead": False,
        "referenceFacingScoreCalls": 0,
    }
    write_json(freeze_path, freeze)
    freeze_sha = frozen_core.sha256_file(freeze_path)

    print(
        json.dumps(
            {
                "status": freeze["status"],
                "candidateSha256": candidate_sha,
                "generationReceiptSha256": receipt_sha,
                "candidateFreezeSha256": freeze_sha,
                "basicPitchObservationSha256": observation_sha,
                "historicalSharedSupportNeighborhoodGateSha256": gate_sha,
                "requiredUniqueStepCount": gate["requiredUniqueStepCount"],
                "requiredCoveragePercent": gate["requiredCoveragePercent"],
                "finalGuitarCount": len(final_guitar),
                "i005Summary": i005_summary,
                "basicPitchActualInferenceCalls": inference_counters["actualInferenceCalls"],
                "referenceRead": False,
                "scorerRead": False,
                "referenceFacingScoreCalls": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
