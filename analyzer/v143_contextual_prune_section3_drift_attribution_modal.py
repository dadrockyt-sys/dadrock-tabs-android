from __future__ import annotations

import hashlib
import json
import math
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_historical_band_diagnostic_modal import (
    SECTION3_CACHE,
    _build_shadow_stems,
    _freeze_cache_value,
    _research_normalize_audio,
    _safe_suffix,
    diagnostic_image,
)


app = modal.App("dadrock-v143-contextual-prune-section3-drift-attribution")
attribution_image = diagnostic_image.add_local_python_source(
    "v143_contextual_prune_historical_band_diagnostic_modal"
)

BASE_FEATURE_NAMES = (
    "evidencePresent",
    "residualNormalized",
    "absoluteResidualNormalized",
    "secondNearestResidualNormalized",
    "nearbyRowCountScaled",
    "candidateCountNormalized",
    "sourceClusterCountNormalized",
    "nearestStemSupportNormalized",
    "nearestSweepSupportNormalized",
    "nearestDetectionCountNormalized",
    "windowStemSupportMaxNormalized",
    "windowSweepSupportMaxNormalized",
    "windowDetectionCountSumNormalized",
    "attackMax.mean",
    "attackMax.std",
    "attackMax.top1",
    "attackMax.top1MinusTop2",
    "attackMax.normViewA",
    "attackMax.normViewB",
    "attackMax.viewCorrelation",
    "earlyMean.mean",
    "earlyMean.std",
    "earlyMean.top1",
    "earlyMean.top1MinusTop2",
    "earlyMean.normViewA",
    "earlyMean.normViewB",
    "earlyMean.viewCorrelation",
    "sustainMean.mean",
    "sustainMean.std",
    "sustainMean.top1",
    "sustainMean.top1MinusTop2",
    "sustainMean.normViewA",
    "sustainMean.normViewB",
    "sustainMean.viewCorrelation",
    "stepSin",
    "stepCos",
)

if len(BASE_FEATURE_NAMES) != 36:
    raise RuntimeError("Base feature-name width changed")


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
        out[key] = float(raw["timeSeconds"])
    return out


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _top_deltas(
    expected: dict[tuple[int, int], float],
    generated: dict[tuple[int, int], float],
    limit: int = 12,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in sorted(set(expected) & set(generated)):
        left = float(expected[key])
        right = float(generated[key])
        rows.append(
            {
                "measure": int(key[0]),
                "step": int(key[1]),
                "expected": left,
                "generated": right,
                "delta": right - left,
                "absoluteDelta": abs(right - left),
            }
        )
    rows.sort(key=lambda row: (-float(row["absoluteDelta"]), row["measure"], row["step"]))
    return rows[: int(limit)]


def _first_delta_key(
    expected: dict[tuple[int, int], float],
    generated: dict[tuple[int, int], float],
) -> tuple[int, int] | None:
    for key in sorted(set(expected) & set(generated)):
        if not math.isclose(
            float(expected[key]),
            float(generated[key]),
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            return key
    return None


def _max_delta_key(
    expected: dict[tuple[int, int], float],
    generated: dict[tuple[int, int], float],
) -> tuple[int, int] | None:
    shared = set(expected) & set(generated)
    if not shared:
        return None
    return max(
        shared,
        key=lambda key: (
            abs(float(generated[key]) - float(expected[key])),
            -int(key[0]),
            -int(key[1]),
        ),
    )


def _row_summary(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    keys = (
        "measure",
        "onsetGroupId",
        "onsetTime",
        "candidateCount",
        "sourceClusterCount",
        "stemSupportMax",
        "sweepSupportMax",
        "detectionCountSum",
    )
    return {key: row.get(key) for key in keys if key in row}


def _top_contributions(
    names: list[str] | tuple[str, ...],
    historical: Any,
    fresh: Any,
    contribution_delta: Any,
    limit: int = 10,
) -> list[dict[str, Any]]:
    rows = [
        {
            "feature": str(name),
            "historical": float(left),
            "fresh": float(right),
            "rawDelta": float(right - left),
            "scoreContributionDelta": float(contrib),
            "absoluteContributionDelta": abs(float(contrib)),
        }
        for name, left, right, contrib in zip(
            names,
            historical,
            fresh,
            contribution_delta,
        )
    ]
    rows.sort(
        key=lambda row: (
            -float(row["absoluteContributionDelta"]),
            str(row["feature"]),
        )
    )
    return rows[: int(limit)]


def _sequence_feature_names() -> tuple[str, ...]:
    from v143_intro_sequence_event_model import WINDOWS_MS

    names: list[str] = []
    for window_ms in WINDOWS_MS:
        names.extend(
            f"window{int(window_ms)}ms.{name}"
            for name in BASE_FEATURE_NAMES
        )

    names.extend(
        (
            "currentBaseScore",
            "currentBaseMargin",
            "currentBaseEvidence",
        )
    )

    for delta in (-3, -2, -1, 0, 1, 2, 3):
        names.extend(
            (
                f"localStep{delta:+d}.baseScore",
                f"localStep{delta:+d}.evidence",
            )
        )
    names.extend(
        (
            "localMeanBaseScore",
            "localStdBaseScore",
            "localMaxBaseScore",
            "localMinBaseScore",
            "localAboveThresholdFraction",
            "localEvidenceFraction",
            "peerSameStepMean",
            "peerSameStepStd",
            "peerSameStepMax",
            "peerSameStepMedian",
            "peerSameStepAboveThresholdFraction",
            "phase2SameStepMean",
            "phase2SameStepMax",
            "phase2SameStepMedian",
            "phase2SameStepAboveThresholdFraction",
            "phase4SameStepMean",
            "phase4SameStepMax",
            "phase4SameStepMedian",
            "phase4SameStepAboveThresholdFraction",
        )
    )
    for delta in (-2, -1, 1, 2):
        names.extend(
            (
                f"measure{delta:+d}.sameStepBaseScore",
                f"measure{delta:+d}.sameStepEvidence",
            )
        )
    return tuple(names)


def _prune_boundary(result: Any) -> dict[str, Any]:
    probs = dict(result.keep_probabilities)
    pruned = set(result.pruned_events)
    kept = set(result.candidate_events)
    pruned_values = [float(probs[key]) for key in pruned]
    kept_values = [float(probs[key]) for key in kept]
    ordered = sorted(probs, key=lambda key: (float(probs[key]), key))
    ranks = {key: index for index, key in enumerate(ordered)}
    return {
        "prunedCount": len(pruned),
        "keptCount": len(kept),
        "highestPrunedProbability": max(pruned_values) if pruned_values else None,
        "lowestKeptProbability": min(kept_values) if kept_values else None,
        "boundaryGap": (
            None
            if not pruned_values or not kept_values
            else min(kept_values) - max(pruned_values)
        ),
        "ranks": ranks,
    }


def _rank_shift(
    historical_boundary: dict[str, Any],
    fresh_boundary: dict[str, Any],
) -> dict[str, Any]:
    left = historical_boundary["ranks"]
    right = fresh_boundary["ranks"]
    shared = set(left) & set(right)
    if not shared:
        return {"maxAbsoluteRankShift": 0, "at": None}
    key = max(
        shared,
        key=lambda value: (
            abs(int(right[value]) - int(left[value])),
            -int(value[0]),
            -int(value[1]),
        ),
    )
    return {
        "maxAbsoluteRankShift": abs(int(right[key]) - int(left[key])),
        "at": {
            "measure": int(key[0]),
            "step": int(key[1]),
            "historicalRank": int(left[key]),
            "freshRank": int(right[key]),
        },
    }


def _compact_boundary(boundary: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in boundary.items() if key != "ranks"}


def _approx_unmatched_rows(
    historical_rows: dict[int, list[dict[str, Any]]],
    fresh_rows: dict[int, list[dict[str, Any]]],
    tolerance_seconds: float = 0.002,
) -> dict[str, Any]:
    changed: list[dict[str, Any]] = []
    for measure in range(49, 65):
        left = list(historical_rows.get(measure, []))
        right = list(fresh_rows.get(measure, []))
        used: set[int] = set()
        unmatched_historical: list[dict[str, Any]] = []
        max_matched_delta = 0.0
        for row in left:
            onset = float(row.get("onsetTime") or 0.0)
            candidates = [
                (abs(float(other.get("onsetTime") or 0.0) - onset), index)
                for index, other in enumerate(right)
                if index not in used
            ]
            if not candidates:
                unmatched_historical.append(row)
                continue
            delta, index = min(candidates)
            if delta <= float(tolerance_seconds):
                used.add(index)
                max_matched_delta = max(max_matched_delta, float(delta))
            else:
                unmatched_historical.append(row)
        unmatched_fresh = [
            row for index, row in enumerate(right) if index not in used
        ]
        if (
            len(left) != len(right)
            or unmatched_historical
            or unmatched_fresh
        ):
            changed.append(
                {
                    "measure": measure,
                    "historicalRowCount": len(left),
                    "freshRowCount": len(right),
                    "rowCountDelta": len(right) - len(left),
                    "maxMatchedOnsetDeltaSeconds": max_matched_delta,
                    "approxUnmatchedHistorical": [
                        _row_summary(row) for row in unmatched_historical[:8]
                    ],
                    "approxUnmatchedFresh": [
                        _row_summary(row) for row in unmatched_fresh[:8]
                    ],
                }
            )
    return {
        "matchToleranceSeconds": float(tolerance_seconds),
        "changedMeasures": changed,
        "totalHistoricalRows": sum(len(v) for v in historical_rows.values()),
        "totalFreshRows": sum(len(v) for v in fresh_rows.values()),
    }


@app.function(image=attribution_image, gpu="L4", timeout=1800, memory=12288)
def diagnose_section3_drift(
    source_audio: bytes,
    suffix: str = ".audio",
) -> dict[str, Any]:
    if not source_audio:
        raise ValueError("Diagnostic audio is empty")
    if len(source_audio) > 50 * 1024 * 1024:
        raise ValueError("Diagnostic audio cannot exceed 50 MB")

    import numpy as np
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import Model, predict as basic_pitch_predict
    import v143_correlation_safe_fixed_count_reranker_freeze as freeze
    import v143_intro_sequence_event_model as sequence
    from v143_contextual_prune_reference_free_carrier import (
        build_contextual_prune_reference_free_carrier,
    )
    from v143_contextual_prune_runtime import (
        CONTEXTUAL_MODEL_PATH,
        FEATURE_NAMES as CONTEXTUAL_FEATURE_NAMES,
        _build_features,
        run_contextual_prune,
    )
    from v143_intro_learned_grid_event_selector import _grid_feature
    from v143_reference_free_timing import estimate_reference_free_timing

    section3 = _load_json(SECTION3_CACHE)
    targets = set(range(49, 65))

    with tempfile.TemporaryDirectory(prefix="v143-section3-drift-") as temp_dir:
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

        carrier = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=49,
            measure_end=64,
            predictor=memoized_predict,
            timing_estimator=fixed_timing,
        )

        historical_rows = _rows_by_measure(
            [dict(row) for row in section3.get("rows", []) or []]
        )
        historical_grid = _grid_from_rows(
            [dict(row) for row in section3.get("grid", []) or []]
        )
        fresh_rows = carrier.rows_by_measure
        fresh_grid = carrier.grid

        historical = run_contextual_prune(
            historical_rows,
            historical_grid,
            targets,
            context_measures=targets,
        )
        fresh = run_contextual_prune(
            fresh_rows,
            fresh_grid,
            targets,
            context_measures=targets,
        )

        decision_exact = (
            historical.base_events == fresh.base_events
            and historical.candidate_events == fresh.candidate_events
            and historical.pruned_events == fresh.pruned_events
        )
        if not decision_exact:
            raise RuntimeError(
                "Section-3 drift attribution expected the already-proven decision-equivalent result"
            )

        base_model = _load_json(freeze.BASE_MODEL_PATH)
        sequence_model = _load_json(freeze.SEQUENCE_MODEL_PATH)
        contextual_model = _load_json(CONTEXTUAL_MODEL_PATH)

        historical_base_scores, historical_base_evidence = freeze._score_measures(
            historical_rows,
            historical_grid,
            targets,
            base_model,
        )
        fresh_base_scores, fresh_base_evidence = freeze._score_measures(
            fresh_rows,
            fresh_grid,
            targets,
            base_model,
        )

        sequence_feature_base_threshold = float(
            _load_json(freeze.FROZEN_SEQUENCE_17_96_PATH)[
                "historicalSequenceFeatureBaseThreshold"
            ]
        )
        historical_sequence_ds = sequence._dataset(
            historical_rows,
            historical_grid,
            {},
            targets,
            targets,
            historical_base_scores,
            historical_base_evidence,
            sequence_feature_base_threshold,
        )
        fresh_sequence_ds = sequence._dataset(
            fresh_rows,
            fresh_grid,
            {},
            targets,
            targets,
            fresh_base_scores,
            fresh_base_evidence,
            sequence_feature_base_threshold,
        )
        if historical_sequence_ds["keys"] != fresh_sequence_ds["keys"]:
            raise RuntimeError("Section-3 sequence feature key order changed")

        historical_sequence_x = freeze._neutralize_sequence_grid_columns(
            historical_sequence_ds["X"],
            base_model,
            sequence_model,
        )
        fresh_sequence_x = freeze._neutralize_sequence_grid_columns(
            fresh_sequence_ds["X"],
            base_model,
            sequence_model,
        )
        sequence_names = _sequence_feature_names()
        if historical_sequence_x.shape[1] != len(sequence_names):
            raise RuntimeError(
                f"Sequence feature-name width mismatch: "
                f"{historical_sequence_x.shape[1]} vs {len(sequence_names)}"
            )
        sequence_key_to_index = {
            key: index
            for index, key in enumerate(historical_sequence_ds["keys"])
        }

        historical_context_features = _build_features(
            set(historical.base_events),
            historical.base_scores,
            historical.sequence_scores,
            historical.sequence_evidence,
        )
        fresh_context_features = _build_features(
            set(fresh.base_events),
            fresh.base_scores,
            fresh.sequence_scores,
            fresh.sequence_evidence,
        )

        base_mean = np.asarray(base_model["featureMean"], dtype=np.float64)
        base_std = np.asarray(base_model["featureStd"], dtype=np.float64)
        base_weights = np.asarray(base_model["weights"], dtype=np.float64)

        sequence_mean = np.asarray(sequence_model["featureMean"], dtype=np.float64)
        sequence_std = np.asarray(sequence_model["featureStd"], dtype=np.float64)
        sequence_basis = np.asarray(sequence_model["pcaBasis"], dtype=np.float64)
        sequence_weights = np.asarray(sequence_model["ridgeWeights"], dtype=np.float64)
        sequence_raw_standardized_weights = (
            sequence_basis @ sequence_weights[1:]
        )

        contextual_mean = np.asarray(
            contextual_model["featureMean"],
            dtype=np.float64,
        )
        contextual_std = np.asarray(
            contextual_model["featureStd"],
            dtype=np.float64,
        )
        contextual_weights = np.asarray(
            contextual_model["weights"],
            dtype=np.float64,
        )

        top_base = _top_deltas(
            historical.base_scores,
            fresh.base_scores,
            12,
        )
        top_sequence = _top_deltas(
            historical.sequence_scores,
            fresh.sequence_scores,
            12,
        )
        top_keep = _top_deltas(
            historical.keep_probabilities,
            fresh.keep_probabilities,
            12,
        )

        focus: list[tuple[int, int]] = []
        for left, right in (
            (historical.base_scores, fresh.base_scores),
            (historical.sequence_scores, fresh.sequence_scores),
            (historical.keep_probabilities, fresh.keep_probabilities),
        ):
            for key in (_max_delta_key(left, right), _first_delta_key(left, right)):
                if key is not None and key not in focus:
                    focus.append(key)

        attribution: list[dict[str, Any]] = []
        base_window_ms = int(base_model["windowMs"])

        for key in focus:
            hist_target = float(historical_grid[key])
            fresh_target = float(fresh_grid[key])
            hist_base_feature, hist_nearest = _grid_feature(
                historical_rows,
                int(key[0]),
                int(key[1]),
                hist_target,
                base_window_ms,
            )
            fresh_base_feature, fresh_nearest = _grid_feature(
                fresh_rows,
                int(key[0]),
                int(key[1]),
                fresh_target,
                base_window_ms,
            )
            base_contrib = (
                (fresh_base_feature - hist_base_feature)
                / base_std
                * base_weights[1:]
            )

            seq_index = sequence_key_to_index[key]
            hist_seq_feature = np.asarray(
                historical_sequence_x[seq_index],
                dtype=np.float64,
            )
            fresh_seq_feature = np.asarray(
                fresh_sequence_x[seq_index],
                dtype=np.float64,
            )
            sequence_contrib = (
                (fresh_seq_feature - hist_seq_feature)
                / sequence_std
                * sequence_raw_standardized_weights
            )

            hist_context = np.asarray(
                historical_context_features[key],
                dtype=np.float64,
            )
            fresh_context = np.asarray(
                fresh_context_features[key],
                dtype=np.float64,
            )
            context_logit_contrib = (
                (fresh_context - hist_context)
                / contextual_std
                * contextual_weights[1:]
            )

            hist_probability = float(historical.keep_probabilities.get(key, 0.0))
            fresh_probability = float(fresh.keep_probabilities.get(key, 0.0))
            hist_logit = math.log(
                max(hist_probability, 1e-15)
                / max(1.0 - hist_probability, 1e-15)
            )
            fresh_logit = math.log(
                max(fresh_probability, 1e-15)
                / max(1.0 - fresh_probability, 1e-15)
            )

            attribution.append(
                {
                    "measure": int(key[0]),
                    "step": int(key[1]),
                    "historicalGridTime": hist_target,
                    "freshGridTime": fresh_target,
                    "gridTimeDelta": fresh_target - hist_target,
                    "historicalNearestBaseRow": _row_summary(hist_nearest),
                    "freshNearestBaseRow": _row_summary(fresh_nearest),
                    "baseScore": {
                        "historical": float(historical.base_scores[key]),
                        "fresh": float(fresh.base_scores[key]),
                        "delta": float(
                            fresh.base_scores[key]
                            - historical.base_scores[key]
                        ),
                        "reconstructedDeltaFromFeatures": float(
                            np.sum(base_contrib)
                        ),
                        "topFeatureContributions": _top_contributions(
                            BASE_FEATURE_NAMES,
                            hist_base_feature,
                            fresh_base_feature,
                            base_contrib,
                            10,
                        ),
                    },
                    "sequenceScore": {
                        "historical": float(historical.sequence_scores[key]),
                        "fresh": float(fresh.sequence_scores[key]),
                        "delta": float(
                            fresh.sequence_scores[key]
                            - historical.sequence_scores[key]
                        ),
                        "reconstructedDeltaFromFeatures": float(
                            np.sum(sequence_contrib)
                        ),
                        "topFeatureContributions": _top_contributions(
                            sequence_names,
                            hist_seq_feature,
                            fresh_seq_feature,
                            sequence_contrib,
                            12,
                        ),
                    },
                    "contextualKeep": {
                        "historicalProbability": hist_probability,
                        "freshProbability": fresh_probability,
                        "probabilityDelta": fresh_probability - hist_probability,
                        "historicalLogit": hist_logit,
                        "freshLogit": fresh_logit,
                        "logitDelta": fresh_logit - hist_logit,
                        "reconstructedLogitDeltaFromFeatures": float(
                            np.sum(context_logit_contrib)
                        ),
                        "topFeatureContributions": _top_contributions(
                            CONTEXTUAL_FEATURE_NAMES,
                            hist_context,
                            fresh_context,
                            context_logit_contrib,
                            10,
                        ),
                    },
                    "decision": {
                        "baseActiveHistorical": key in historical.base_events,
                        "baseActiveFresh": key in fresh.base_events,
                        "keptHistorical": key in historical.candidate_events,
                        "keptFresh": key in fresh.candidate_events,
                        "prunedHistorical": key in historical.pruned_events,
                        "prunedFresh": key in fresh.pruned_events,
                    },
                }
            )

        historical_boundary = _prune_boundary(historical)
        fresh_boundary = _prune_boundary(fresh)

        expected_stem_counts = dict(section3.get("stemEventCounts") or {})
        generated_stem_counts = dict(carrier.stem_event_counts)
        stem_deltas = {
            key: int(generated_stem_counts.get(key, 0))
            - int(expected_stem_counts.get(key, 0))
            for key in sorted(set(expected_stem_counts) | set(generated_stem_counts))
        }

        return {
            "schemaVersion": 1,
            "gate": "v143-contextual-prune-section3-drift-attribution",
            "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
            "section": {"startMeasure": 49, "endMeasure": 64},
            "carrierDelta": {
                "historicalRawEventCount": int(section3.get("rawEventCount", -1)),
                "freshRawEventCount": int(carrier.raw_event_count),
                "rawEventDelta": int(carrier.raw_event_count)
                - int(section3.get("rawEventCount", -1)),
                "historicalCandidateClusterCount": int(
                    section3.get("candidateClusterCount", -1)
                ),
                "freshCandidateClusterCount": int(carrier.candidate_cluster_count),
                "candidateClusterDelta": int(carrier.candidate_cluster_count)
                - int(section3.get("candidateClusterCount", -1)),
                "historicalRowCount": len(section3.get("rows", []) or []),
                "freshRowCount": len(carrier.rows),
                "rowCountDelta": len(carrier.rows)
                - len(section3.get("rows", []) or []),
                "stemEventCountDeltas": stem_deltas,
                "rowLocalization": _approx_unmatched_rows(
                    historical_rows,
                    fresh_rows,
                ),
            },
            "scoreDeltas": {
                "base": top_base,
                "sequence": top_sequence,
                "keepProbability": top_keep,
            },
            "focusAttribution": attribution,
            "pruneBoundary": {
                "historical": _compact_boundary(historical_boundary),
                "fresh": _compact_boundary(fresh_boundary),
                "rankShift": _rank_shift(
                    historical_boundary,
                    fresh_boundary,
                ),
                "decisionSetExact": decision_exact,
            },
            "predictionCache": {
                "entryCount": len(prediction_cache),
                "misses": int(cache_misses),
                "hits": int(cache_hits),
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
                "thresholdsModified": False,
                "liveEndpointDeployedOrModified": False,
                "productionModified": False,
            },
        }


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    result = diagnose_section3_drift.remote(
        source.read_bytes(),
        source.suffix,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
