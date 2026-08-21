from __future__ import annotations

import hashlib
import json
import math
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_shadow_modal import shadow_image


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"

BANDS: tuple[tuple[str, int, int, str], ...] = (
    ("section2", 33, 48, "fresh-section2-reference-free-cache.json"),
    ("section3", 49, 64, "fresh-section3-reference-free-cache.json"),
    ("section4", 65, 80, "fresh-section4-reference-free-cache.json"),
    ("section5", 81, 96, "fresh-section5-reference-free-cache.json"),
    ("reserve", 97, 113, "reserve-97-113-reference-free-cache.json"),
)

SECTION5_BASE = CAL / "fresh-section5-base027-frozen-events.json"
RESERVE_BASE = CAL / "reserve-97-113-base027-frozen-events.json"
RESERVE_CANDIDATE = CAL / "reserve-97-113-contextual-prune-frozen-events.json"

SECTION5_MEASURES = set(range(81, 97))
TARGET_MEASURES = set(range(97, 114))
CONTEXT_MEASURES = set(range(81, 114))

app = modal.App("dadrock-v143-surviving-band-provenance")

# Keep this diagnostic isolated from production. The base image contains the
# frozen V143 runtime/model inputs; add only historical reference-free carriers
# and pre-grading frozen prediction artifacts needed for replay comparison.
provenance_image = shadow_image.add_local_python_source(
    "v143_contextual_prune_shadow_modal"
)
for filename in (
    "fresh-section2-reference-free-cache.json",
    "fresh-section3-reference-free-cache.json",
    "fresh-section4-reference-free-cache.json",
    "reserve-97-113-reference-free-cache.json",
    "fresh-section5-base027-frozen-events.json",
    "reserve-97-113-base027-frozen-events.json",
    "reserve-97-113-contextual-prune-frozen-events.json",
):
    provenance_image = provenance_image.add_local_file(
        CAL / filename,
        f"/public/training/v143-musical-reconstruction-calibration/{filename}",
    )


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        return ".audio"
    return suffix


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Missing required artifact: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _research_normalize_audio(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        str(source),
        "-map",
        "0:a:0",
        "-vn",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-c:a",
        "pcm_s16le",
        str(destination),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            "Historical V143 research normalization failed:\n"
            + (result.stderr or result.stdout or "unknown ffmpeg error")[-4000:]
        )
    if not destination.exists() or destination.stat().st_size <= 0:
        raise RuntimeError("Historical V143 research normalization produced no audio")
    return destination


def _build_shadow_stems(
    normalized: Path,
    output_dir: Path,
) -> tuple[dict[str, Any], Path, Path]:
    from v143_deterministic_separator import build_deterministic_v143_stems

    stems = build_deterministic_v143_stems(normalized, output_dir)
    direct = Path(str(stems.get("directGuitar") or ""))
    cascade = Path(str(stems.get("cascadeGuitar") or ""))
    for label, path in (("direct", direct), ("cascade", cascade)):
        if not path.exists() or path.stat().st_size <= 0:
            raise RuntimeError(f"Provenance {label} guitar view is missing: {path}")
    if stems.get("deterministic") is not True:
        raise RuntimeError("Provenance separator is not marked deterministic")
    if stems.get("referenceFree") is not True:
        raise RuntimeError("Provenance separator is not marked reference-free")
    return stems, direct, cascade


def _first_mismatch(
    expected: Any,
    actual: Any,
    path: str = "$",
) -> dict[str, Any] | None:
    # This is the already-established diagnostic tolerance. It is deliberately
    # not widened here.
    if isinstance(expected, bool) or isinstance(actual, bool):
        return None if expected == actual else {
            "path": path,
            "expected": expected,
            "actual": actual,
        }
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        left = float(expected)
        right = float(actual)
        if math.isfinite(left) and math.isfinite(right) and math.isclose(
            left,
            right,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            return None
        return None if left == right else {
            "path": path,
            "expected": expected,
            "actual": actual,
        }
    if type(expected) is not type(actual):
        return {
            "path": path,
            "expectedType": type(expected).__name__,
            "actualType": type(actual).__name__,
            "expected": expected,
            "actual": actual,
        }
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            return {
                "path": path,
                "missingKeys": sorted(set(expected) - set(actual)),
                "extraKeys": sorted(set(actual) - set(expected)),
            }
        for key in expected:
            mismatch = _first_mismatch(expected[key], actual[key], f"{path}.{key}")
            if mismatch is not None:
                return mismatch
        return None
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return {
                "path": path,
                "expectedLength": len(expected),
                "actualLength": len(actual),
            }
        for index, (left, right) in enumerate(zip(expected, actual)):
            mismatch = _first_mismatch(left, right, f"{path}[{index}]")
            if mismatch is not None:
                return mismatch
        return None
    return None if expected == actual else {
        "path": path,
        "expected": expected,
        "actual": actual,
    }


def _normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Historical band captures restart this ordering-only identifier. The frozen
    # scorers do not consume it, so compare all scoring semantics without it.
    normalized: list[dict[str, Any]] = []
    for raw in rows:
        row = dict(raw)
        row.pop("onsetGroupId", None)
        normalized.append(row)
    return normalized


def _timing_payload(timing: Any) -> dict[str, Any]:
    return {
        "tempoBpm": float(timing.tempo_bpm),
        "firstBeatInMeasure": int(timing.first_beat_in_measure),
        "downbeatIndexMod4": int(timing.downbeat_index_mod4),
        "beatConfidence": float(timing.beat_confidence),
        "barConfidence": float(timing.bar_confidence),
    }


def _expected_semantics(
    cache: dict[str, Any],
    start: int,
    end: int,
) -> dict[str, Any]:
    if cache.get("referenceFree") is not True:
        raise RuntimeError(f"Historical {start}-{end} cache lost referenceFree=true")
    if cache.get("professionalReferenceUsedByAnalyzer") is not False:
        raise RuntimeError(
            f"Historical {start}-{end} cache unexpectedly used professional reference"
        )
    section = dict(cache.get("section") or {})
    if int(section.get("startMeasure", -1)) != start or int(
        section.get("endMeasure", -1)
    ) != end:
        raise RuntimeError(f"Unexpected historical cache section: {section}")

    return {
        "timing": dict(cache.get("timing") or {}),
        "grid": [dict(row) for row in cache.get("grid", []) or []],
        "rows": _normalize_rows([dict(row) for row in cache.get("rows", []) or []]),
        "targetSampleRate": int(cache.get("targetSampleRate", -1)),
        "hopLength": int(cache.get("hopLength", -1)),
        "binsPerOctave": int(cache.get("binsPerOctave", -1)),
        "spectrumMidiMin": int(cache.get("spectrumMidiMin", -1)),
        "spectrumMidiMax": int(cache.get("spectrumMidiMax", -1)),
        "guitarMidiMin": int(cache.get("guitarMidiMin", -1)),
        "guitarMidiMax": int(cache.get("guitarMidiMax", -1)),
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
    }


def _generated_semantics(carrier: Any) -> dict[str, Any]:
    return {
        "timing": _timing_payload(carrier.timing),
        "grid": [dict(row) for row in carrier.grid_rows],
        "rows": _normalize_rows([dict(row) for row in carrier.rows]),
        "targetSampleRate": 22050,
        "hopLength": 128,
        "binsPerOctave": 36,
        "spectrumMidiMin": 28,
        "spectrumMidiMax": 112,
        "guitarMidiMin": 40,
        "guitarMidiMax": 88,
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
    }


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


def _band_result(
    label: str,
    cache: dict[str, Any],
    carrier: Any,
    start: int,
    end: int,
) -> dict[str, Any]:
    expected = _expected_semantics(cache, start, end)
    generated = _generated_semantics(carrier)
    semantic_mismatch = _first_mismatch(expected, generated)

    expected_capture = _capture_diagnostics_from_cache(cache)
    generated_capture = _capture_diagnostics_from_carrier(carrier)
    capture_mismatch = _first_mismatch(expected_capture, generated_capture)

    semantic_passed = semantic_mismatch is None
    capture_passed = capture_mismatch is None and expected_capture == generated_capture
    return {
        "label": label,
        "measures": f"{start}-{end}",
        "comparisonScope": "original-boundary scoring semantics plus exact capture diagnostics",
        "expectedSemanticSha256": _canonical_sha256(expected),
        "generatedSemanticSha256": _canonical_sha256(generated),
        "exactSemanticReplayPassed": expected == generated,
        "toleranceSemanticReplayPassed": semantic_passed,
        "semanticFirstMismatch": semantic_mismatch,
        "captureDiagnosticsReplayPassed": capture_passed,
        "captureDiagnosticsFirstMismatch": capture_mismatch,
        "provenanceReplayPassed": semantic_passed and capture_passed,
        "expected": {
            "gridCount": len(expected["grid"]),
            "rowCount": len(expected["rows"]),
            **expected_capture,
        },
        "generated": {
            "gridCount": len(generated["grid"]),
            "rowCount": len(generated["rows"]),
            **generated_capture,
        },
    }


def _freeze_cache_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (tuple, list)):
        return tuple(_freeze_cache_value(item) for item in value)
    if isinstance(value, dict):
        return tuple(
            sorted((str(key), _freeze_cache_value(item)) for key, item in value.items())
        )
    return repr(value)


def _extract_events(payload: Any, allowed: set[int]) -> set[tuple[int, int]]:
    found: set[tuple[int, int]] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if "measure" in value and ("step" in value or "quantizedStep" in value):
                try:
                    measure = int(value["measure"])
                    step = int(value.get("step", value.get("quantizedStep")))
                    if measure in allowed and 0 <= step < 16:
                        found.add((measure, step))
                except (TypeError, ValueError):
                    pass
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(payload)
    return found


def _merge_generated_reserve_context(
    section5_carrier: Any,
    reserve_carrier: Any,
) -> tuple[
    dict[int, list[dict[str, Any]]],
    dict[tuple[int, int], float],
    dict[str, Any],
]:
    """Recreate the historical 81-113 reserve context from two band carriers.

    This deliberately does not build an 81-113 carrier. Section 5 and reserve
    retain their original CQT boundaries and are merged only after construction,
    matching the sealed reserve prediction path.
    """
    rows_by_measure: dict[int, list[dict[str, Any]]] = {}
    grid: dict[tuple[int, int], float] = {}
    group_offset = 0

    for carrier in (section5_carrier, reserve_carrier):
        for raw in carrier.rows:
            if not isinstance(raw, dict):
                continue
            measure = int(raw.get("measure") or raw.get("nearestMeasure") or 0)
            if measure not in CONTEXT_MEASURES:
                continue
            row = dict(raw)
            row["measure"] = measure
            if row.get("onsetGroupId") is not None:
                row["onsetGroupId"] = int(row.get("onsetGroupId") or 0) + group_offset
            rows_by_measure.setdefault(measure, []).append(row)

        for raw in carrier.grid_rows:
            if not isinstance(raw, dict):
                continue
            measure = int(raw.get("measure") or 0)
            step = int(raw.get("step") or 0)
            if measure not in CONTEXT_MEASURES or not 0 <= step < 16:
                continue
            key = (measure, step)
            time_seconds = float(raw.get("timeSeconds") or 0.0)
            if key in grid and abs(grid[key] - time_seconds) > 1e-6:
                raise RuntimeError(
                    f"Conflicting generated reserve-context grid time for {key}: "
                    f"{grid[key]} vs {time_seconds}"
                )
            grid[key] = time_seconds

        group_offset += 1_000_000

    for values in rows_by_measure.values():
        values.sort(
            key=lambda row: (
                float(row.get("onsetTime") or 0.0),
                int(row.get("onsetGroupId") or 0),
            )
        )

    missing_complete = [
        (measure, step)
        for measure in range(81, 113)
        for step in range(16)
        if (measure, step) not in grid
    ]
    final_steps = sorted(step for measure, step in grid if measure == 113)
    expected_final_steps = list(range(8))
    expected_grid_count = (32 * 16) + len(expected_final_steps)
    missing_row_measures = sorted(CONTEXT_MEASURES - set(rows_by_measure))

    partial_tail_passed = (
        not missing_complete
        and final_steps == expected_final_steps
        and len(grid) == expected_grid_count
        and not missing_row_measures
    )
    diagnostics = {
        "contextMeasures": "81-113",
        "construction": "merge independently-built 81-96 and 97-113 carriers",
        "completeGridMissing": missing_complete[:12],
        "measure113Steps": final_steps,
        "expectedMeasure113Steps": expected_final_steps,
        "gridCount": len(grid),
        "expectedGridCount": expected_grid_count,
        "missingRowMeasures": missing_row_measures,
        "partialTailInvariantPassed": partial_tail_passed,
    }
    if not partial_tail_passed:
        raise RuntimeError(
            "Generated 81-113 reserve-context partial-tail invariant failed: "
            + json.dumps(diagnostics, sort_keys=True)
        )

    return rows_by_measure, grid, diagnostics


def _score_map_from_historical_reserve(
    payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for raw in payload.get("events", []) or []:
        if not isinstance(raw, dict):
            continue
        measure = int(raw.get("measure") or 0)
        step = int(raw.get("quantizedStep", raw.get("step", -1)))
        if measure not in TARGET_MEASURES or not 0 <= step < 16:
            continue
        result[f"{measure}:{step}"] = {
            "baseScore": float(raw.get("baseScore") or 0.0),
            "sequenceScore": float(raw.get("sequenceScore") or 0.0),
            "sequenceEvidence": bool(raw.get("sequenceEvidence", False)),
            "contextualKeepProbability": float(
                raw.get("contextualKeepProbability") or 0.0
            ),
        }
    return result


def _score_map_from_runtime(result: Any) -> dict[str, dict[str, Any]]:
    return {
        f"{measure}:{step}": {
            "baseScore": float(result.base_scores.get((measure, step), 0.0)),
            "sequenceScore": float(result.sequence_scores.get((measure, step), 0.0)),
            "sequenceEvidence": bool(
                result.sequence_evidence.get((measure, step), False)
            ),
            "contextualKeepProbability": float(
                result.keep_probabilities.get((measure, step), 0.0)
            ),
        }
        for measure, step in sorted(result.base_events)
    }


def _section5_score_map(payload: dict[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    for raw in payload.get("events", []) or []:
        if not isinstance(raw, dict):
            continue
        measure = int(raw.get("measure") or 0)
        step = int(raw.get("step", raw.get("quantizedStep", -1)))
        if measure in SECTION5_MEASURES and 0 <= step < 16:
            result[f"{measure}:{step}"] = float(
                raw.get("score", raw.get("baseScore", 0.0)) or 0.0
            )
    return result


def _reserve_scoring_replay(section5_carrier: Any, reserve_carrier: Any) -> dict[str, Any]:
    from v143_contextual_prune_runtime import run_contextual_prune

    historical_section5 = _load_json(SECTION5_BASE)
    historical_base = _load_json(RESERVE_BASE)
    historical_candidate = _load_json(RESERVE_CANDIDATE)

    if historical_section5.get("referenceUsedForPrediction") is not False:
        raise RuntimeError("Historical Section-5 base predictions used reference labels")
    for label, payload in (
        ("reserve base", historical_base),
        ("reserve candidate", historical_candidate),
    ):
        if payload.get("professionalReferenceUsedForPrediction") is not False:
            raise RuntimeError(f"Historical {label} unexpectedly used professional reference")
        if payload.get("predictionFrozenBeforeReserveGrading") is not True:
            raise RuntimeError(f"Historical {label} was not frozen before reserve grading")

    rows_by_measure, grid, context_diagnostics = _merge_generated_reserve_context(
        section5_carrier,
        reserve_carrier,
    )

    # This first replay is an explicit invariant in the original sealed reserve
    # prediction: Section-5 base events must still replay inside 81-113 context.
    replayed_section5 = run_contextual_prune(
        rows_by_measure,
        grid,
        SECTION5_MEASURES,
        context_measures=CONTEXT_MEASURES,
    )
    replayed_reserve = run_contextual_prune(
        rows_by_measure,
        grid,
        TARGET_MEASURES,
        context_measures=CONTEXT_MEASURES,
    )

    expected_section5_events = _extract_events(
        historical_section5,
        SECTION5_MEASURES,
    )
    generated_section5_events = set(replayed_section5.base_events)
    section5_missing = sorted(expected_section5_events - generated_section5_events)
    section5_added = sorted(generated_section5_events - expected_section5_events)

    expected_section5_scores = _section5_score_map(historical_section5)
    generated_section5_scores = {
        f"{measure}:{step}": float(
            replayed_section5.base_scores.get((measure, step), 0.0)
        )
        for measure, step in sorted(replayed_section5.base_events)
    }
    section5_score_mismatch = _first_mismatch(
        expected_section5_scores,
        generated_section5_scores,
    )

    expected_base_events = _extract_events(historical_base, TARGET_MEASURES)
    generated_base_events = set(replayed_reserve.base_events)
    expected_candidate_events = _extract_events(
        historical_candidate,
        TARGET_MEASURES,
    )
    generated_candidate_events = set(replayed_reserve.candidate_events)

    expected_reserve_scores = _score_map_from_historical_reserve(historical_base)
    generated_reserve_scores = _score_map_from_runtime(replayed_reserve)
    reserve_score_mismatch = _first_mismatch(
        expected_reserve_scores,
        generated_reserve_scores,
    )

    section5_base_passed = generated_section5_events == expected_section5_events
    section5_score_passed = section5_score_mismatch is None
    reserve_base_passed = generated_base_events == expected_base_events
    reserve_candidate_passed = generated_candidate_events == expected_candidate_events
    reserve_score_passed = reserve_score_mismatch is None

    return {
        "context": context_diagnostics,
        "section5BaseReplayPassed": section5_base_passed,
        "section5BaseScoreReplayPassed": section5_score_passed,
        "section5ExpectedBaseEventCount": len(expected_section5_events),
        "section5GeneratedBaseEventCount": len(generated_section5_events),
        "section5MissingBaseEvents": section5_missing[:24],
        "section5UnexpectedBaseEvents": section5_added[:24],
        "section5ScoreFirstMismatch": section5_score_mismatch,
        "reserveBaseReplayPassed": reserve_base_passed,
        "reserveCandidateReplayPassed": reserve_candidate_passed,
        "reserveScoreReplayPassed": reserve_score_passed,
        "reserveExpectedBaseEventCount": len(expected_base_events),
        "reserveGeneratedBaseEventCount": len(generated_base_events),
        "reserveExpectedCandidateEventCount": len(expected_candidate_events),
        "reserveGeneratedCandidateEventCount": len(generated_candidate_events),
        "reserveMissingBaseEvents": sorted(expected_base_events - generated_base_events)[:24],
        "reserveUnexpectedBaseEvents": sorted(generated_base_events - expected_base_events)[:24],
        "reserveMissingCandidateEvents": sorted(
            expected_candidate_events - generated_candidate_events
        )[:24],
        "reserveUnexpectedCandidateEvents": sorted(
            generated_candidate_events - expected_candidate_events
        )[:24],
        "reserveScoreFirstMismatch": reserve_score_mismatch,
        "reserveScoringReplayPassed": (
            context_diagnostics["partialTailInvariantPassed"] is True
            and section5_base_passed
            and section5_score_passed
            and reserve_base_passed
            and reserve_candidate_passed
            and reserve_score_passed
        ),
    }


@app.function(image=provenance_image, gpu="L4", timeout=2400, memory=12288)
def diagnose_surviving_band_provenance(
    source_audio: bytes,
    suffix: str = ".audio",
) -> dict[str, Any]:
    """Authoritative surviving-band V143 provenance diagnostic.

    Each historical carrier is constructed independently at its original band
    boundary. Expensive full-stem Basic Pitch inference and timing are shared,
    but no carrier is built as a monolithic 33-113 range and sliced. The reserve
    scorer receives the historical merged 81-113 context only after separate
    81-96 and 97-113 carrier construction.
    """
    if not source_audio:
        raise ValueError("source_audio is empty")
    if len(source_audio) > 50 * 1024 * 1024:
        raise ValueError("Provenance audio cannot exceed 50 MB")

    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import Model, predict as basic_pitch_predict
    from v143_contextual_prune_reference_free_carrier import (
        build_contextual_prune_reference_free_carrier,
    )
    from v143_reference_free_timing import estimate_reference_free_timing

    historical_caches = {
        label: _load_json(CAL / filename)
        for label, _start, _end, filename in BANDS
    }

    with tempfile.TemporaryDirectory(prefix="v143-surviving-provenance-") as temp_dir:
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

        carriers: dict[str, Any] = {}
        band_results: dict[str, Any] = {}
        for label, start, end, _filename in BANDS:
            # Critical provenance rule: build at the original historical band
            # boundary. Never build a larger carrier and slice it.
            carrier = build_contextual_prune_reference_free_carrier(
                normalized,
                (direct, cascade),
                measure_start=start,
                measure_end=end,
                predictor=memoized_predict,
                timing_estimator=fixed_timing,
            )
            carriers[label] = carrier
            band_results[label] = _band_result(
                label,
                historical_caches[label],
                carrier,
                start,
                end,
            )

        reserve_scoring = _reserve_scoring_replay(
            carriers["section5"],
            carriers["reserve"],
        )

        all_carriers_passed = all(
            result.get("provenanceReplayPassed") is True
            for result in band_results.values()
        )
        all_passed = (
            all_carriers_passed
            and reserve_scoring.get("reserveScoringReplayPassed") is True
        )

        return {
            "schemaVersion": 1,
            "gate": "v143-contextual-prune-surviving-band-provenance",
            "claimScope": "surviving historical carriers 33-113; measures 17-32 explicitly excluded",
            "executionStrategy": "five original-boundary carriers; shared full-stem inference; merged 81-113 reserve scoring context",
            "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
            "researchNormalizedSha256": _sha256(normalized),
            "historicalCacheSha256": {
                label: _sha256(CAL / filename)
                for label, _start, _end, filename in BANDS
            },
            "bands": band_results,
            "reserveScoring": reserve_scoring,
            "predictionCache": {
                "entryCount": len(prediction_cache),
                "misses": int(cache_misses),
                "hits": int(cache_hits),
                "expectedUniquePredictions": 8,
                "storesNoteEventsOnly": True,
                "singleLoadedBasicPitchModel": True,
            },
            "allCarrierProvenancePassed": all_carriers_passed,
            "allSurvivingBandsProvenancePassed": all_passed,
            "separator": {
                "deterministic": stems.get("deterministic") is True,
                "referenceFree": stems.get("referenceFree") is True,
                "settings": dict(stems.get("settings") or {}),
                "models": dict(stems.get("models") or {}),
            },
            "invariants": {
                "originalBandBoundariesPreserved": True,
                "monolithicCarrierUsed": False,
                "measures17To32Claimed": False,
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
    result = diagnose_surviving_band_provenance.remote(
        source.read_bytes(),
        source.suffix,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
