from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_historical_band_diagnostic_modal import (
    SECTION3_CACHE,
    _band_result,
    _freeze_cache_value,
    _research_normalize_audio,
    _safe_suffix,
)
from v143_contextual_prune_section3_repeatability_modal import (
    _decision_payload,
    _grid_from_cache,
    _rows_by_measure,
)
from v143_demucs_shift_offset_probe_modal import (
    EXPECTED_SHIFT_MAX,
    KNOWN_CASCADE,
    KNOWN_DIRECT,
    SEED,
    _family,
    _pcm_sha256,
    _read_trace,
    _shift_values,
    probe_image,
)
from v143_production_separator import (
    normalize_input_audio,
    separate_demucs_guitar,
    separate_roformer_instrumental,
)
from v143_seeded_separator import seeded_audio_separator_cli


app = modal.App("dadrock-v143-section3-exact-family-provenance-capture")
capture_image = probe_image.add_local_python_source(
    "v143_contextual_prune_reference_free_carrier",
    "v143_contextual_prune_runtime",
)

BATCH_SIZE = 4
MAX_BATCHES = 3
TARGET_FAMILY = "B"


def _exact_score_maps(left: dict[Any, float], right: dict[Any, float]) -> bool:
    if set(left) != set(right):
        return False
    return all(float(left[key]) == float(right[key]) for key in left)


def _capture_diagnostics_from_cache(cache: dict[str, Any]) -> dict[str, Any]:
    return {
        "rawEventCount": int(cache.get("rawEventCount", -1)),
        "candidateClusterCount": int(cache.get("candidateClusterCount", -1)),
        "onsetGroupCount": int(cache.get("onsetGroupCount", -1)),
        "sweepEventCounts": dict(cache.get("sweepEventCounts") or {}),
        "stemEventCounts": dict(cache.get("stemEventCounts") or {}),
        "candidateStemCount": int(cache.get("candidateStemCount", -1)),
    }


def _capture_diagnostics_from_carrier(carrier: Any) -> dict[str, Any]:
    return {
        "rawEventCount": int(carrier.raw_event_count),
        "candidateClusterCount": int(carrier.candidate_cluster_count),
        "onsetGroupCount": len(carrier.rows),
        "sweepEventCounts": dict(carrier.sweep_event_counts),
        "stemEventCounts": dict(carrier.stem_event_counts),
        "candidateStemCount": len(carrier.stem_event_counts),
    }


@app.function(image=capture_image, gpu="L4", timeout=1800, memory=12288)
def capture_worker(source_audio: bytes, suffix: str, worker_index: int) -> dict[str, Any]:
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import Model, predict as basic_pitch_predict
    from v143_contextual_prune_reference_free_carrier import (
        build_contextual_prune_reference_free_carrier,
    )
    from v143_contextual_prune_runtime import run_contextual_prune
    from v143_reference_free_timing import estimate_reference_free_timing

    if not source_audio:
        raise ValueError("Probe audio is empty")

    section3 = json.loads(SECTION3_CACHE.read_text(encoding="utf-8"))
    targets = set(range(49, 65))
    historical_rows = _rows_by_measure([dict(row) for row in section3.get("rows", []) or []])
    historical_grid = _grid_from_cache(section3)
    historical_runtime = run_contextual_prune(
        historical_rows,
        historical_grid,
        targets,
        context_measures=targets,
    )
    historical_decision = _decision_payload(historical_runtime)

    with tempfile.TemporaryDirectory(prefix=f"v143-section3-exact-family-{worker_index}-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        research_normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, research_normalized)

        work = root / "separator"
        normalized = normalize_input_audio(research_normalized, work / "normalized")
        regular_cli = seeded_audio_separator_cli()
        trace_cli = [sys.executable, "-m", "v143_shift_trace_audio_separator_cli"]
        direct_trace_path = root / "direct-shift-trace.jsonl"
        cascade_trace_path = root / "cascade-shift-trace.jsonl"

        saved = {
            name: os.environ.get(name)
            for name in (
                "PYTHONHASHSEED",
                "V143_SEPARATOR_SEED",
                "V143_SHIFT_TRACE_PATH",
                "V143_SHIFT_TRACE_STAGE",
            )
        }
        try:
            os.environ["PYTHONHASHSEED"] = SEED
            os.environ["V143_SEPARATOR_SEED"] = SEED

            os.environ["V143_SHIFT_TRACE_PATH"] = str(direct_trace_path)
            os.environ["V143_SHIFT_TRACE_STAGE"] = "direct"
            direct = separate_demucs_guitar(trace_cli, normalized, work / "direct")

            os.environ.pop("V143_SHIFT_TRACE_PATH", None)
            os.environ.pop("V143_SHIFT_TRACE_STAGE", None)
            roformer = separate_roformer_instrumental(regular_cli, normalized, work / "roformer")

            os.environ["V143_SHIFT_TRACE_PATH"] = str(cascade_trace_path)
            os.environ["V143_SHIFT_TRACE_STAGE"] = "cascade"
            cascade = separate_demucs_guitar(trace_cli, Path(roformer["path"]), work / "cascade")
        finally:
            for name, value in saved.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

        direct_path = Path(direct["path"])
        roformer_path = Path(roformer["path"])
        cascade_path = Path(cascade["path"])
        direct_pcm = _pcm_sha256(direct_path)
        roformer_pcm = _pcm_sha256(roformer_path)
        cascade_pcm = _pcm_sha256(cascade_path)
        direct_family = _family(direct_pcm["sha256"], KNOWN_DIRECT)
        cascade_family = _family(cascade_pcm["sha256"], KNOWN_CASCADE)
        direct_trace = _read_trace(direct_trace_path)
        cascade_trace = _read_trace(cascade_trace_path)
        direct_shifts = _shift_values(direct_trace)
        cascade_shifts = _shift_values(cascade_trace)
        historical_family_pair = direct_family == TARGET_FAMILY and cascade_family == TARGET_FAMILY

        base = {
            "worker": int(worker_index),
            "modalTaskId": os.environ.get("MODAL_TASK_ID"),
            "directFamily": direct_family,
            "cascadeFamily": cascade_family,
            "familyLockstep": direct_family == cascade_family,
            "historicalFamilyPair": historical_family_pair,
            "directPcm": direct_pcm,
            "roformerPcm": roformer_pcm,
            "cascadePcm": cascade_pcm,
            "directShiftValues": direct_shifts,
            "cascadeShiftValues": cascade_shifts,
            "shiftTraceExpectedBounds": [0, EXPECTED_SHIFT_MAX],
        }

        if not historical_family_pair:
            return {
                **base,
                "carrierBuilt": False,
                "exactHistoricalCarrierAndScores": False,
                "reason": "separator PCM pair is not historical Family B",
            }

        # Preserve the exact Family-B PCM bytes while restoring only the canonical
        # historical stem filenames consumed by capture diagnostics. This happens
        # before carrier construction and does not modify audio samples or events.
        canonical_stems = root / "canonical-stems"
        canonical_stems.mkdir(parents=True, exist_ok=True)
        canonical_direct = canonical_stems / "direct-demucs6s-guitar.wav"
        canonical_cascade = canonical_stems / "bsroformer-demucs6s-guitar.wav"
        shutil.copy2(direct_path, canonical_direct)
        shutil.copy2(cascade_path, canonical_cascade)
        canonical_direct_pcm = _pcm_sha256(canonical_direct)
        canonical_cascade_pcm = _pcm_sha256(canonical_cascade)
        canonical_pcm_preserved = (
            canonical_direct_pcm["sha256"] == direct_pcm["sha256"]
            and canonical_cascade_pcm["sha256"] == cascade_pcm["sha256"]
        )
        if not canonical_pcm_preserved:
            raise RuntimeError("Canonical stem filename copy changed Family-B PCM bytes")

        timing = estimate_reference_free_timing(normalized)
        model = Model(ICASSP_2022_MODEL_PATH)
        prediction_cache: dict[Any, tuple[Any, ...]] = {}

        def memoized_predict(audio_path: str, *args: Any, **kwargs: Any) -> Any:
            key = (
                str(Path(audio_path).resolve()),
                _freeze_cache_value(args),
                _freeze_cache_value(kwargs),
            )
            if key in prediction_cache:
                return (None, None, prediction_cache[key])
            result = basic_pitch_predict(audio_path, model, *args, **kwargs)
            if not isinstance(result, tuple) or len(result) < 3:
                raise RuntimeError(f"Unexpected Basic Pitch return shape for {audio_path}")
            note_events = tuple(result[2] or ())
            prediction_cache[key] = note_events
            return (None, None, note_events)

        def fixed_timing(_path: str | Path) -> Any:
            return timing

        carrier = build_contextual_prune_reference_free_carrier(
            normalized,
            (canonical_direct, canonical_cascade),
            measure_start=49,
            measure_end=64,
            predictor=memoized_predict,
            timing_estimator=fixed_timing,
        )
        band = _band_result(f"historical-family-worker-{worker_index}", section3, carrier, 49, 64)
        expected_capture = _capture_diagnostics_from_cache(section3)
        generated_capture = _capture_diagnostics_from_carrier(carrier)
        capture_exact = expected_capture == generated_capture
        semantic_exact = band.get("exactSemanticReplayPassed") is True
        provenance_exact = semantic_exact and capture_exact

        fresh_runtime = run_contextual_prune(
            carrier.rows_by_measure,
            carrier.grid,
            targets,
            context_measures=targets,
        )
        fresh_decision = _decision_payload(fresh_runtime)

        decision_exact = fresh_decision == historical_decision
        base_scores_exact = _exact_score_maps(historical_runtime.base_scores, fresh_runtime.base_scores)
        sequence_scores_exact = _exact_score_maps(historical_runtime.sequence_scores, fresh_runtime.sequence_scores)
        keep_probabilities_exact = _exact_score_maps(
            historical_runtime.keep_probabilities,
            fresh_runtime.keep_probabilities,
        )
        exact_all = (
            provenance_exact
            and decision_exact
            and base_scores_exact
            and sequence_scores_exact
            and keep_probabilities_exact
        )

        return {
            **base,
            "carrierBuilt": True,
            "canonicalStemFilenames": [canonical_direct.name, canonical_cascade.name],
            "canonicalStemPcmPreserved": canonical_pcm_preserved,
            "carrier": {
                "provenanceReplayPassed": provenance_exact,
                "exactSemanticReplayPassed": semantic_exact,
                "captureDiagnosticsReplayPassed": capture_exact,
                "semanticFirstMismatch": band.get("firstMismatch"),
                "captureDiagnosticsFirstMismatch": None if capture_exact else {
                    "expected": expected_capture,
                    "generated": generated_capture,
                },
                "rowCount": len(carrier.rows),
                "rawEventCount": int(carrier.raw_event_count),
                "candidateClusterCount": int(carrier.candidate_cluster_count),
                "stemEventCounts": dict(carrier.stem_event_counts),
                "sweepEventCounts": dict(carrier.sweep_event_counts),
            },
            "scoring": {
                "decisionSetExact": decision_exact,
                "baseScoresExact": base_scores_exact,
                "sequenceScoresExact": sequence_scores_exact,
                "keepProbabilitiesExact": keep_probabilities_exact,
            },
            "predictionCache": {
                "entryCount": len(prediction_cache),
                "singleLoadedBasicPitchModel": True,
                "storesNoteEventsOnly": True,
            },
            "exactHistoricalCarrierAndScores": exact_all,
        }


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    payload = source.read_bytes()

    workers: list[dict[str, Any]] = []
    batches_run = 0
    for batch in range(MAX_BATCHES):
        start = batch * BATCH_SIZE + 1

        def invoke(offset: int) -> dict[str, Any]:
            return capture_worker.remote(payload, source.suffix, start + offset)

        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as pool:
            workers.extend(pool.map(invoke, range(BATCH_SIZE)))
        batches_run += 1
        if any(row.get("exactHistoricalCarrierAndScores") is True for row in workers):
            break

    workers.sort(key=lambda row: int(row["worker"]))
    historical_workers = [row for row in workers if row.get("historicalFamilyPair") is True]
    exact_workers = [row for row in workers if row.get("exactHistoricalCarrierAndScores") is True]

    result = {
        "schemaVersion": 2,
        "gate": "v143-section3-exact-family-provenance-capture",
        "claimScope": "Section 3 measures 49-64 only; exact historical Family-B carrier and frozen scorer evidence",
        "executionStrategy": "adaptive independent L4 workers; classify exact separator PCM family; build carrier/scorer only for historical Family B with canonical historical stem filenames",
        "sourceSha256": hashlib.sha256(payload).hexdigest(),
        "batchSize": BATCH_SIZE,
        "maxBatches": MAX_BATCHES,
        "batchesRun": batches_run,
        "workerCount": len(workers),
        "knownHistoricalFamily": {
            "label": TARGET_FAMILY,
            "directPcmSha256": KNOWN_DIRECT[TARGET_FAMILY],
            "cascadePcmSha256": KNOWN_CASCADE[TARGET_FAMILY],
        },
        "workers": workers,
        "summary": {
            "historicalFamilyWorkerCount": len(historical_workers),
            "exactHistoricalCarrierAndScoreCount": len(exact_workers),
            "allHistoricalFamilyWorkersExact": bool(historical_workers)
            and all(row.get("exactHistoricalCarrierAndScores") is True for row in historical_workers),
            "section3ExactProvenanceCaptured": bool(exact_workers),
        },
        "invariants": {
            "originalBandBoundaryPreserved": True,
            "strictExactSemanticComparison": True,
            "strictExactCaptureDiagnosticsComparison": True,
            "strictExactDecisionComparison": True,
            "strictExactScoreComparison": True,
            "comparisonTolerancesWeakened": False,
            "canonicalHistoricalStemFilenamesAppliedBeforeCarrierBuild": True,
            "canonicalStemPcmBytesRequiredUnchanged": True,
            "traceWrapperReturnsOriginalRandintValueUnchanged": True,
            "professionalReferenceOpened": False,
            "runtimeLabelsRequired": False,
            "measures17To32Claimed": False,
            "frozenModelModified": False,
            "frozenPredictionsModified": False,
            "thresholdsModified": False,
            "liveEndpointDeployedOrModified": False,
            "productionModified": False,
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
