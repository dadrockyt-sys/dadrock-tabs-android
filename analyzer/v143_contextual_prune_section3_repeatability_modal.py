from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_historical_band_diagnostic_modal import (
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


app = modal.App("dadrock-v143-contextual-prune-section3-repeatability")
repeatability_image = diagnostic_image.add_local_python_source(
    "v143_contextual_prune_historical_band_diagnostic_modal"
)

REPEAT_COUNT = 3


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


def _grid_from_cache(cache: dict[str, Any]) -> dict[tuple[int, int], float]:
    return {
        (int(row["measure"]), int(row["step"])): float(row["timeSeconds"])
        for row in cache.get("grid", []) or []
    }


def _event_rows(events: Any) -> list[dict[str, int]]:
    return [
        {"measure": int(measure), "step": int(step)}
        for measure, step in sorted(events)
    ]


def _decision_payload(result: Any) -> dict[str, Any]:
    return {
        "baseEvents": _event_rows(result.base_events),
        "candidateEvents": _event_rows(result.candidate_events),
        "prunedEvents": _event_rows(result.pruned_events),
    }


def _max_float_delta(
    expected: dict[tuple[int, int], float],
    generated: dict[tuple[int, int], float],
) -> dict[str, Any]:
    shared = sorted(set(expected) & set(generated))
    if not shared:
        return {"maxAbsDelta": 0.0, "at": None, "keySetExact": set(expected) == set(generated)}
    key = max(
        shared,
        key=lambda item: (
            abs(float(generated[item]) - float(expected[item])),
            -int(item[0]),
            -int(item[1]),
        ),
    )
    return {
        "maxAbsDelta": abs(float(generated[key]) - float(expected[key])),
        "at": {"measure": int(key[0]), "step": int(key[1])},
        "keySetExact": set(expected) == set(generated),
    }


def _pcm_sha256(path: Path) -> dict[str, Any]:
    import soundfile as sf

    audio, sample_rate = sf.read(str(path), dtype="int16", always_2d=True)
    return {
        "sha256": hashlib.sha256(audio.tobytes()).hexdigest(),
        "sampleRate": int(sample_rate),
        "frames": int(audio.shape[0]),
        "channels": int(audio.shape[1]),
    }


def _all_equal(values: list[Any]) -> bool:
    return len(set(values)) <= 1


@app.function(image=repeatability_image, gpu="L4", timeout=1800, memory=12288)
def diagnose_section3_repeatability(
    source_audio: bytes,
    suffix: str = ".audio",
) -> dict[str, Any]:
    """Repeat Section 3 from independent separator outputs and localize variability.

    The same normalized source and the same reference-free timing estimate are reused
    deliberately. Each repetition independently rebuilds both guitar stems and runs
    fresh Basic Pitch inference. Historical labels/reference are never opened.
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
    from v143_contextual_prune_runtime import run_contextual_prune
    from v143_reference_free_timing import estimate_reference_free_timing

    section3 = json.loads(SECTION3_CACHE.read_text(encoding="utf-8"))
    targets = set(range(49, 65))
    historical_rows = _rows_by_measure(
        [dict(row) for row in section3.get("rows", []) or []]
    )
    historical_grid = _grid_from_cache(section3)
    historical_runtime = run_contextual_prune(
        historical_rows,
        historical_grid,
        targets,
        context_measures=targets,
    )
    historical_decision = _decision_payload(historical_runtime)
    historical_decision_sha = _canonical_sha256(historical_decision)

    with tempfile.TemporaryDirectory(prefix="v143-section3-repeatability-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, normalized)

        timing = estimate_reference_free_timing(normalized)
        basic_pitch_model = Model(ICASSP_2022_MODEL_PATH)
        repeats: list[dict[str, Any]] = []

        for repeat_index in range(1, REPEAT_COUNT + 1):
            stems, direct, cascade = _build_shadow_stems(
                normalized,
                root / f"stems-repeat-{repeat_index}",
            )
            prediction_cache: dict[Any, tuple[Any, ...]] = {}
            misses = 0
            hits = 0

            def memoized_predict(audio_path: str, *args: Any, **kwargs: Any) -> Any:
                nonlocal misses, hits
                key = (
                    str(Path(audio_path).resolve()),
                    _freeze_cache_value(args),
                    _freeze_cache_value(kwargs),
                )
                if key in prediction_cache:
                    hits += 1
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
                misses += 1
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
            band = _band_result(
                f"section3-repeat-{repeat_index}",
                section3,
                carrier,
                49,
                64,
            )
            fresh_runtime = run_contextual_prune(
                carrier.rows_by_measure,
                carrier.grid,
                targets,
                context_measures=targets,
            )
            fresh_decision = _decision_payload(fresh_runtime)

            repeats.append(
                {
                    "repeat": repeat_index,
                    "separator": {
                        "deterministicFlag": stems.get("deterministic") is True,
                        "referenceFree": stems.get("referenceFree") is True,
                        "directFileSha256": _sha256(direct),
                        "cascadeFileSha256": _sha256(cascade),
                        "directPcm": _pcm_sha256(direct),
                        "cascadePcm": _pcm_sha256(cascade),
                    },
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
                    "predictionCache": {
                        "entryCount": len(prediction_cache),
                        "misses": misses,
                        "hits": hits,
                        "singleLoadedBasicPitchModel": True,
                        "storesNoteEventsOnly": True,
                    },
                }
            )

        direct_pcm_hashes = [row["separator"]["directPcm"]["sha256"] for row in repeats]
        cascade_pcm_hashes = [row["separator"]["cascadePcm"]["sha256"] for row in repeats]
        carrier_hashes = [row["carrier"]["semanticSha256"] for row in repeats]
        decision_hashes = [row["downstream"]["decisionSha256"] for row in repeats]

        direct_repeatable = _all_equal(direct_pcm_hashes)
        cascade_repeatable = _all_equal(cascade_pcm_hashes)
        carrier_repeatable = _all_equal(carrier_hashes)
        decisions_repeatable = _all_equal(decision_hashes)

        if not direct_repeatable or not cascade_repeatable:
            classification = "separator-output-varies-across-independent-rebuilds"
        elif not carrier_repeatable:
            classification = "post-separator-carrier-or-basic-pitch-varies"
        elif not decisions_repeatable:
            classification = "downstream-runtime-varies-with-identical-carrier"
        else:
            classification = "repeatable-within-this-three-run-modal-job"

        return {
            "schemaVersion": 1,
            "gate": "v143-contextual-prune-section3-repeatability",
            "executionStrategy": "three-independent-separator-and-basic-pitch-rebuilds-shared-normalized-audio-and-timing",
            "repeatCount": REPEAT_COUNT,
            "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
            "researchNormalizedSha256": _sha256(normalized),
            "historicalCacheSha256": _sha256(SECTION3_CACHE),
            "historicalDecisionSha256": historical_decision_sha,
            "repeats": repeats,
            "repeatability": {
                "directStemPcmExactAcrossRepeats": direct_repeatable,
                "cascadeStemPcmExactAcrossRepeats": cascade_repeatable,
                "carrierSemanticExactAcrossRepeats": carrier_repeatable,
                "downstreamDecisionExactAcrossRepeats": decisions_repeatable,
                "historicalCarrierExactReplayCount": sum(
                    row["carrier"]["exactHistoricalReplay"] is True for row in repeats
                ),
                "historicalDecisionExactCount": sum(
                    row["downstream"]["decisionSetExactToHistorical"] is True
                    for row in repeats
                ),
                "classification": classification,
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
    result = diagnose_section3_repeatability.remote(
        source.read_bytes(),
        source.suffix,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
