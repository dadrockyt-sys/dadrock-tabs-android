from __future__ import annotations

import hashlib
import json
import math
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_section3_drift_attribution_modal import (
    BASE_FEATURE_NAMES,
    SECTION3_CACHE,
    _approx_unmatched_rows,
    _build_shadow_stems,
    _compact_boundary,
    _first_delta_key,
    _freeze_cache_value,
    _grid_from_rows,
    _load_json,
    _max_delta_key,
    _prune_boundary,
    _rank_shift,
    _research_normalize_audio,
    _row_summary,
    _rows_by_measure,
    _safe_suffix,
    _sequence_feature_names,
    _top_contributions,
    _top_deltas,
    attribution_image,
)


app = modal.App("dadrock-v143-contextual-prune-section3-drift-attribution-v2")

# The v2 diagnostic deliberately imports the v1 module for its already-audited
# label-free helpers, while correcting only the attribution assumption that every
# score-drift focus cell is base-active. Mount v1 explicitly for remote startup.
attribution_image_v2 = attribution_image.add_local_python_source(
    "v143_contextual_prune_section3_drift_attribution_modal"
)


@app.function(image=attribution_image_v2, gpu="L4", timeout=1800, memory=12288)
def diagnose_section3_drift_v2(
    source_audio: bytes,
    suffix: str = ".audio",
) -> dict[str, Any]:
    """Attribute Section-3 score drift without assuming every focus key is base-active.

    Base and sequence scores exist for all grid cells with evidence. The frozen
    contextual selector, however, only builds contextual features and keep
    probabilities for base-active events. Therefore an inactive cell can be the
    largest base/sequence score drift while legitimately having no contextual
    keep-probability attribution. This diagnostic records that state explicitly.
    """
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

    with tempfile.TemporaryDirectory(prefix="v143-section3-drift-v2-") as temp_dir:
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
            cache_key = (
                str(Path(audio_path).resolve()),
                _freeze_cache_value(args),
                _freeze_cache_value(kwargs),
            )
            if cache_key in prediction_cache:
                cache_hits += 1
                return (None, None, prediction_cache[cache_key])
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
            prediction_cache[cache_key] = note_events
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

        base_std = np.asarray(base_model["featureStd"], dtype=np.float64)
        base_weights = np.asarray(base_model["weights"], dtype=np.float64)

        sequence_std = np.asarray(sequence_model["featureStd"], dtype=np.float64)
        sequence_basis = np.asarray(sequence_model["pcaBasis"], dtype=np.float64)
        sequence_weights = np.asarray(sequence_model["ridgeWeights"], dtype=np.float64)
        sequence_raw_standardized_weights = sequence_basis @ sequence_weights[1:]

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

            context_applicable = (
                key in historical_context_features
                and key in fresh_context_features
                and key in historical.keep_probabilities
                and key in fresh.keep_probabilities
            )
            if context_applicable:
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
                hist_probability = float(historical.keep_probabilities[key])
                fresh_probability = float(fresh.keep_probabilities[key])
                hist_logit = math.log(
                    max(hist_probability, 1e-15)
                    / max(1.0 - hist_probability, 1e-15)
                )
                fresh_logit = math.log(
                    max(fresh_probability, 1e-15)
                    / max(1.0 - fresh_probability, 1e-15)
                )
                contextual_payload: dict[str, Any] = {
                    "applicable": True,
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
                }
            else:
                contextual_payload = {
                    "applicable": False,
                    "reason": (
                        "not-base-active; frozen contextual runtime only builds "
                        "features and keep probabilities for base-active events"
                    ),
                    "historicalProbability": None,
                    "freshProbability": None,
                    "probabilityDelta": None,
                    "historicalLogit": None,
                    "freshLogit": None,
                    "logitDelta": None,
                    "reconstructedLogitDeltaFromFeatures": None,
                    "topFeatureContributions": [],
                }

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
                    "contextualKeep": contextual_payload,
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
            "schemaVersion": 2,
            "gate": "v143-contextual-prune-section3-drift-attribution-v2",
            "executionStrategy": "layer-aware-attribution-inactive-grid-cells-have-no-contextual-keep-layer",
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
    result = diagnose_section3_drift_v2.remote(
        source.read_bytes(),
        source.suffix,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
