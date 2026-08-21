from __future__ import annotations

import hashlib
import json
import math
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_historical_band_diagnostic_modal import (
    SECTION2_CACHE,
    SECTION3_CACHE,
    _build_shadow_stems,
    _freeze_cache_value,
    _research_normalize_audio,
    _safe_suffix,
    diagnostic_image,
)


app = modal.App("dadrock-v143-contextual-prune-downstream-equivalence")

# This module imports the historical carrier diagnostic at remote-container
# startup. Mount that module explicitly; its image already mounts the shared
# shadow module and frozen V143 runtime dependencies.
downstream_image = diagnostic_image.add_local_python_source(
    "v143_contextual_prune_historical_band_diagnostic_modal"
)


NUMERIC_REL_TOL = 1e-12
NUMERIC_ABS_TOL = 1e-12


def _rows_by_measure(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for raw in rows:
        row = dict(raw)
        measure = int(row["measure"])
        out.setdefault(measure, []).append(row)
    for values in out.values():
        values.sort(
            key=lambda row: (
                float(row.get("onsetTime") or 0.0),
                int(row.get("onsetGroupId") or 0),
            )
        )
    return out


def _grid_from_rows(rows: list[dict[str, Any]]) -> dict[tuple[int, int], float]:
    out: dict[tuple[int, int], float] = {}
    for raw in rows:
        key = (int(raw["measure"]), int(raw["step"]))
        value = float(raw["timeSeconds"])
        if key in out and not math.isclose(out[key], value, rel_tol=0.0, abs_tol=1e-12):
            raise RuntimeError(f"Conflicting historical grid time for {key}")
        out[key] = value
    return out


def _event_rows(events: Any) -> list[dict[str, int]]:
    return [
        {"measure": int(measure), "step": int(step)}
        for measure, step in sorted(events)
    ]


def _event_set_comparison(expected: Any, generated: Any) -> dict[str, Any]:
    left = set(expected)
    right = set(generated)
    expected_only = sorted(left - right)
    generated_only = sorted(right - left)
    return {
        "exact": left == right,
        "expectedCount": len(left),
        "generatedCount": len(right),
        "expectedOnlyCount": len(expected_only),
        "generatedOnlyCount": len(generated_only),
        "expectedOnly": _event_rows(expected_only[:24]),
        "generatedOnly": _event_rows(generated_only[:24]),
    }


def _float_map_comparison(
    expected: dict[tuple[int, int], float],
    generated: dict[tuple[int, int], float],
) -> dict[str, Any]:
    expected_keys = set(expected)
    generated_keys = set(generated)
    shared = sorted(expected_keys & generated_keys)
    max_abs_delta = 0.0
    max_delta_key: tuple[int, int] | None = None
    first_mismatch: dict[str, Any] | None = None

    for key in shared:
        left = float(expected[key])
        right = float(generated[key])
        delta = abs(left - right)
        if delta > max_abs_delta:
            max_abs_delta = delta
            max_delta_key = key
        if first_mismatch is None and not math.isclose(
            left,
            right,
            rel_tol=NUMERIC_REL_TOL,
            abs_tol=NUMERIC_ABS_TOL,
        ):
            first_mismatch = {
                "measure": int(key[0]),
                "step": int(key[1]),
                "expected": left,
                "generated": right,
                "absoluteDelta": delta,
            }

    expected_only = sorted(expected_keys - generated_keys)
    generated_only = sorted(generated_keys - expected_keys)
    key_set_exact = expected_keys == generated_keys
    tolerance_passed = key_set_exact and first_mismatch is None
    return {
        "keySetExact": key_set_exact,
        "expectedKeyCount": len(expected_keys),
        "generatedKeyCount": len(generated_keys),
        "expectedOnly": _event_rows(expected_only[:24]),
        "generatedOnly": _event_rows(generated_only[:24]),
        "maxAbsDelta": float(max_abs_delta),
        "maxDeltaAt": (
            None
            if max_delta_key is None
            else {"measure": int(max_delta_key[0]), "step": int(max_delta_key[1])}
        ),
        "tolerancePassed": tolerance_passed,
        "firstMismatch": first_mismatch,
        "relTolerance": NUMERIC_REL_TOL,
        "absTolerance": NUMERIC_ABS_TOL,
    }


def _bool_map_comparison(
    expected: dict[tuple[int, int], bool],
    generated: dict[tuple[int, int], bool],
) -> dict[str, Any]:
    expected_keys = set(expected)
    generated_keys = set(generated)
    shared = sorted(expected_keys & generated_keys)
    first_mismatch: dict[str, Any] | None = None
    mismatch_count = 0
    for key in shared:
        left = bool(expected[key])
        right = bool(generated[key])
        if left != right:
            mismatch_count += 1
            if first_mismatch is None:
                first_mismatch = {
                    "measure": int(key[0]),
                    "step": int(key[1]),
                    "expected": left,
                    "generated": right,
                }
    expected_only = sorted(expected_keys - generated_keys)
    generated_only = sorted(generated_keys - expected_keys)
    key_set_exact = expected_keys == generated_keys
    return {
        "exact": key_set_exact and mismatch_count == 0,
        "keySetExact": key_set_exact,
        "mismatchCount": mismatch_count,
        "expectedOnly": _event_rows(expected_only[:24]),
        "generatedOnly": _event_rows(generated_only[:24]),
        "firstMismatch": first_mismatch,
    }


def _run_downstream_pair(
    label: str,
    cache: dict[str, Any],
    carrier: Any,
    start: int,
    end: int,
) -> dict[str, Any]:
    from v143_contextual_prune_runtime import run_contextual_prune

    targets = set(range(int(start), int(end) + 1))
    historical_rows = _rows_by_measure(
        [dict(row) for row in cache.get("rows", []) or []]
    )
    historical_grid = _grid_from_rows(
        [dict(row) for row in cache.get("grid", []) or []]
    )

    historical = run_contextual_prune(
        historical_rows,
        historical_grid,
        targets,
        context_measures=targets,
    )
    fresh = run_contextual_prune(
        carrier.rows_by_measure,
        carrier.grid,
        targets,
        context_measures=targets,
    )

    base_events = _event_set_comparison(historical.base_events, fresh.base_events)
    candidate_events = _event_set_comparison(
        historical.candidate_events,
        fresh.candidate_events,
    )
    pruned_events = _event_set_comparison(
        historical.pruned_events,
        fresh.pruned_events,
    )
    base_scores = _float_map_comparison(historical.base_scores, fresh.base_scores)
    sequence_scores = _float_map_comparison(
        historical.sequence_scores,
        fresh.sequence_scores,
    )
    sequence_evidence = _bool_map_comparison(
        historical.sequence_evidence,
        fresh.sequence_evidence,
    )
    keep_probabilities = _float_map_comparison(
        historical.keep_probabilities,
        fresh.keep_probabilities,
    )

    decision_equivalent = (
        base_events["exact"] is True
        and candidate_events["exact"] is True
        and pruned_events["exact"] is True
    )
    scoring_equivalent = (
        base_scores["tolerancePassed"] is True
        and sequence_scores["tolerancePassed"] is True
        and sequence_evidence["exact"] is True
        and keep_probabilities["tolerancePassed"] is True
    )

    return {
        "label": label,
        "measures": f"{start}-{end}",
        "comparisonScope": "frozen-contextual-prune-downstream-output",
        "historicalDiagnostics": historical.diagnostics(),
        "freshDiagnostics": fresh.diagnostics(),
        "baseEvents": base_events,
        "candidateEvents": candidate_events,
        "prunedEvents": pruned_events,
        "baseScores": base_scores,
        "sequenceScores": sequence_scores,
        "sequenceEvidence": sequence_evidence,
        "keepProbabilities": keep_probabilities,
        "downstreamDecisionEquivalent": decision_equivalent,
        "downstreamScoringEquivalentWithinTolerance": scoring_equivalent,
        "fullyEquivalentWithinTolerance": decision_equivalent and scoring_equivalent,
    }


@app.function(image=downstream_image, gpu="L4", timeout=1800, memory=12288)
def diagnose_downstream_equivalence(
    source_audio: bytes,
    suffix: str = ".audio",
) -> dict[str, Any]:
    """Compare historical and freshly rebuilt carriers through the frozen scorer.

    This is a label-blind, reference-free research gate. It does not modify the
    frozen model, frozen predictions, live endpoint, or production output.
    """
    if not source_audio:
        raise ValueError("Diagnostic audio is empty")
    if len(source_audio) > 50 * 1024 * 1024:
        raise ValueError("Diagnostic audio cannot exceed 50 MB")

    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import Model, predict as basic_pitch_predict
    from v143_contextual_prune_reference_free_carrier import (
        build_contextual_prune_reference_free_carrier,
    )
    from v143_reference_free_timing import estimate_reference_free_timing

    section2 = json.loads(SECTION2_CACHE.read_text(encoding="utf-8"))
    section3 = json.loads(SECTION3_CACHE.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="v143-downstream-equivalence-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, normalized)
        stems, direct, cascade = _build_shadow_stems(normalized, root / "stems")

        timing = estimate_reference_free_timing(normalized)
        basic_pitch_model = Model(ICASSP_2022_MODEL_PATH)
        prediction_cache: dict[Any, tuple[Any, ...]] = {}
        cache_hits = 0
        cache_misses = 0

        def memoized_predict(audio_path: str, *args: Any, **kwargs: Any) -> Any:
            nonlocal cache_hits, cache_misses
            key = (
                str(Path(audio_path).resolve()),
                _freeze_cache_value(args),
                _freeze_cache_value(kwargs),
            )
            if key in prediction_cache:
                cache_hits += 1
                return (None, None, prediction_cache[key])
            result = basic_pitch_predict(
                audio_path,
                basic_pitch_model,
                *args,
                **kwargs,
            )
            if not isinstance(result, tuple) or len(result) < 3:
                raise RuntimeError(
                    f"Unexpected Basic Pitch return shape for {audio_path}"
                )
            note_events = tuple(result[2] or ())
            prediction_cache[key] = note_events
            cache_misses += 1
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

        section2_result = _run_downstream_pair(
            "section2",
            section2,
            carrier2,
            33,
            48,
        )
        section3_result = _run_downstream_pair(
            "section3",
            section3,
            carrier3,
            49,
            64,
        )

        return {
            "schemaVersion": 1,
            "gate": "v143-contextual-prune-downstream-equivalence-diagnostic",
            "executionStrategy": "historical-vs-fresh-carrier-through-frozen-contextual-runtime",
            "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
            "section2": section2_result,
            "section3": section3_result,
            "allHistoricalBandsDecisionEquivalent": (
                section2_result["downstreamDecisionEquivalent"] is True
                and section3_result["downstreamDecisionEquivalent"] is True
            ),
            "allHistoricalBandsFullyEquivalentWithinTolerance": (
                section2_result["fullyEquivalentWithinTolerance"] is True
                and section3_result["fullyEquivalentWithinTolerance"] is True
            ),
            "predictionCache": {
                "entryCount": len(prediction_cache),
                "misses": int(cache_misses),
                "hits": int(cache_hits),
                "expectedUniquePredictions": 8,
                "reusedForSecondBand": cache_hits >= 8,
                "storesNoteEventsOnly": True,
                "singleLoadedBasicPitchModel": True,
            },
            "separator": {
                "deterministic": stems.get("deterministic") is True,
                "referenceFree": stems.get("referenceFree") is True,
                "settings": dict(stems.get("settings") or {}),
                "models": dict(stems.get("models") or {}),
            },
            "invariants": {
                "professionalReferenceOpened": False,
                "runtimeLabelsRequired": False,
                "frozenModelModified": False,
                "frozenPredictionsModified": False,
                "liveEndpointDeployedOrModified": False,
                "productionModified": False,
            },
        }


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    result = diagnose_downstream_equivalence.remote(
        source.read_bytes(),
        source.suffix,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
