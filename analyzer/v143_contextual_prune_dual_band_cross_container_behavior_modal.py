from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_historical_band_diagnostic_modal import (
    SECTION2_CACHE,
    SECTION3_CACHE,
    _band_result,
    _build_shadow_stems,
    _canonical_sha256,
    _freeze_cache_value,
    _generated_semantics,
    _research_normalize_audio,
    _safe_suffix,
    _sha256,
    diagnostic_image,
)
from v143_contextual_prune_section3_repeatability_modal import (
    _decision_payload,
    _grid_from_cache,
    _max_float_delta,
    _pcm_sha256,
    _rows_by_measure,
)


app = modal.App("dadrock-v143-dual-band-cross-container-behavior")
worker_image = diagnostic_image.add_local_python_source(
    "v143_contextual_prune_historical_band_diagnostic_modal",
    "v143_contextual_prune_section3_repeatability_modal",
)
WORKER_COUNT = 3


def _historical_runtime(cache: dict[str, Any], start: int, end: int) -> tuple[Any, dict[str, Any]]:
    from v143_contextual_prune_runtime import run_contextual_prune

    targets = set(range(start, end + 1))
    rows = _rows_by_measure([dict(row) for row in cache.get("rows", []) or []])
    grid = _grid_from_cache(cache)
    runtime = run_contextual_prune(rows, grid, targets, context_measures=targets)
    return runtime, _decision_payload(runtime)


def _evaluate_band(
    label: str,
    cache: dict[str, Any],
    carrier: Any,
    start: int,
    end: int,
    historical_runtime: Any,
    historical_decision: dict[str, Any],
) -> dict[str, Any]:
    from v143_contextual_prune_runtime import run_contextual_prune

    targets = set(range(start, end + 1))
    band = _band_result(label, cache, carrier, start, end)
    fresh_runtime = run_contextual_prune(
        carrier.rows_by_measure,
        carrier.grid,
        targets,
        context_measures=targets,
    )
    fresh_decision = _decision_payload(fresh_runtime)
    return {
        "carrier": {
            "semanticSha256": _canonical_sha256(_generated_semantics(carrier)),
            "exactHistoricalReplay": band["exactSemanticReplayPassed"],
            "toleranceHistoricalReplay": band["toleranceSemanticReplayPassed"],
            "firstMismatch": band["firstMismatch"],
            "rawEventCount": int(carrier.raw_event_count),
            "candidateClusterCount": int(carrier.candidate_cluster_count),
            "rowCount": len(carrier.rows),
            "stemEventCounts": dict(carrier.stem_event_counts),
            "sweepEventCounts": dict(carrier.sweep_event_counts),
        },
        "downstream": {
            "historicalDecisionSha256": _canonical_sha256(historical_decision),
            "decisionSha256": _canonical_sha256(fresh_decision),
            "decisionSetExactToHistorical": fresh_decision == historical_decision,
            "baseScoreDelta": _max_float_delta(
                historical_runtime.base_scores,
                fresh_runtime.base_scores,
            ),
            "sequenceScoreDelta": _max_float_delta(
                historical_runtime.sequence_scores,
                fresh_runtime.sequence_scores,
            ),
            "keepProbabilityDelta": _max_float_delta(
                historical_runtime.keep_probabilities,
                fresh_runtime.keep_probabilities,
            ),
        },
    }


@app.function(image=worker_image, gpu="L4", timeout=1800, memory=12288)
def behavior_worker(source_audio: bytes, suffix: str, worker_index: int) -> dict[str, Any]:
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import Model, predict as basic_pitch_predict
    from v143_contextual_prune_reference_free_carrier import (
        build_contextual_prune_reference_free_carrier,
    )
    from v143_reference_free_timing import estimate_reference_free_timing

    if not source_audio:
        raise ValueError("Diagnostic audio is empty")

    section2 = json.loads(SECTION2_CACHE.read_text(encoding="utf-8"))
    section3 = json.loads(SECTION3_CACHE.read_text(encoding="utf-8"))
    hist2_runtime, hist2_decision = _historical_runtime(section2, 33, 48)
    hist3_runtime, hist3_decision = _historical_runtime(section3, 49, 64)

    with tempfile.TemporaryDirectory(prefix=f"v143-dual-band-worker-{worker_index}-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, normalized)

        stems, direct, cascade = _build_shadow_stems(normalized, root / "stems")
        timing = estimate_reference_free_timing(normalized)
        model = Model(ICASSP_2022_MODEL_PATH)
        prediction_cache: dict[Any, tuple[Any, ...]] = {}
        hits = 0
        misses = 0

        def memoized_predict(audio_path: str, *args: Any, **kwargs: Any) -> Any:
            nonlocal hits, misses
            key = (
                str(Path(audio_path).resolve()),
                _freeze_cache_value(args),
                _freeze_cache_value(kwargs),
            )
            if key in prediction_cache:
                hits += 1
                return (None, None, prediction_cache[key])
            result = basic_pitch_predict(audio_path, model, *args, **kwargs)
            if not isinstance(result, tuple) or len(result) < 3:
                raise RuntimeError(f"Unexpected Basic Pitch return shape for {audio_path}")
            note_events = tuple(result[2] or ())
            prediction_cache[key] = note_events
            misses += 1
            return (None, None, note_events)

        def fixed_timing(_path: str | Path) -> Any:
            return timing

        carrier2 = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=33,
            measure_end=48,
            predictor=memoized_predict,
            timing_estimator=fixed_timing,
        )
        carrier3 = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=49,
            measure_end=64,
            predictor=memoized_predict,
            timing_estimator=fixed_timing,
        )

        return {
            "worker": int(worker_index),
            "runtimeIdentity": {"modalTaskId": os.environ.get("MODAL_TASK_ID")},
            "normalizedSha256": _sha256(normalized),
            "separator": {
                "deterministicFlag": stems.get("deterministic") is True,
                "referenceFree": stems.get("referenceFree") is True,
                "directFileSha256": _sha256(direct),
                "cascadeFileSha256": _sha256(cascade),
                "directPcm": _pcm_sha256(direct),
                "cascadePcm": _pcm_sha256(cascade),
            },
            "section2": _evaluate_band(
                f"dual-worker-{worker_index}-section2",
                section2,
                carrier2,
                33,
                48,
                hist2_runtime,
                hist2_decision,
            ),
            "section3": _evaluate_band(
                f"dual-worker-{worker_index}-section3",
                section3,
                carrier3,
                49,
                64,
                hist3_runtime,
                hist3_decision,
            ),
            "predictionCache": {
                "entryCount": len(prediction_cache),
                "misses": int(misses),
                "hits": int(hits),
                "expectedUniquePredictions": 8,
                "singleLoadedBasicPitchModel": True,
                "storesNoteEventsOnly": True,
            },
        }


def _section_summary(workers: list[dict[str, Any]], key: str) -> dict[str, Any]:
    carrier_hashes = [row[key]["carrier"]["semanticSha256"] for row in workers]
    decision_hashes = [row[key]["downstream"]["decisionSha256"] for row in workers]
    return {
        "carrierSemanticExactAcrossWorkers": len(set(carrier_hashes)) == 1,
        "downstreamDecisionExactAcrossWorkers": len(set(decision_hashes)) == 1,
        "historicalCarrierExactReplayCount": sum(
            row[key]["carrier"]["exactHistoricalReplay"] is True for row in workers
        ),
        "historicalDecisionExactCount": sum(
            row[key]["downstream"]["decisionSetExactToHistorical"] is True
            for row in workers
        ),
    }


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    payload = source.read_bytes()

    def invoke(index: int) -> dict[str, Any]:
        return behavior_worker.remote(payload, source.suffix, index)

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKER_COUNT) as pool:
        workers = list(pool.map(invoke, range(1, WORKER_COUNT + 1)))
    workers.sort(key=lambda row: int(row["worker"]))

    direct_hashes = [row["separator"]["directPcm"]["sha256"] for row in workers]
    cascade_hashes = [row["separator"]["cascadePcm"]["sha256"] for row in workers]
    section2 = _section_summary(workers, "section2")
    section3 = _section_summary(workers, "section3")

    result = {
        "schemaVersion": 1,
        "gate": "v143-contextual-prune-dual-band-cross-container-behavior",
        "executionStrategy": "three-independent-l4-workers-one-separation-per-worker-two-exact-band-carriers-frozen-runtime",
        "workerCount": WORKER_COUNT,
        "sourceSha256": hashlib.sha256(payload).hexdigest(),
        "workers": workers,
        "separatorRepeatability": {
            "directStemPcmExactAcrossWorkers": len(set(direct_hashes)) == 1,
            "cascadeStemPcmExactAcrossWorkers": len(set(cascade_hashes)) == 1,
        },
        "section2": section2,
        "section3": section3,
        "allHistoricalDecisionsExact": (
            section2["historicalDecisionExactCount"] == WORKER_COUNT
            and section3["historicalDecisionExactCount"] == WORKER_COUNT
        ),
        "invariants": {
            "professionalReferenceOpened": False,
            "runtimeLabelsRequired": False,
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
