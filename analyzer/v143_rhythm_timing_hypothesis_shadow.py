from __future__ import annotations

import math
from statistics import mean, median, pstdev
from typing import Any, Mapping, Sequence


BEATS_PER_MEASURE = 4
MIN_PHASE_BEATS = 8
STRICT_MIN_STEM_SUPPORT = 2
STRICT_MIN_SWEEP_SUPPORT = 3
STRICT_MIN_DETECTION_COUNT = 4
GRID_AMBIGUITY_MARGIN_SECONDS = 0.020

EventKey = tuple[int, int]


def _finite(value: Any, fallback: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return number if math.isfinite(number) else float(fallback)


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = max(0.0, min(1.0, float(fraction))) * (len(ordered) - 1)
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    alpha = position - lo
    return ordered[lo] * (1.0 - alpha) + ordered[hi] * alpha


def _strict_row(row: Mapping[str, Any]) -> bool:
    return (
        int(row.get("stemSupportMax") or 0) >= STRICT_MIN_STEM_SUPPORT
        and int(row.get("sweepSupportMax") or 0) >= STRICT_MIN_SWEEP_SUPPORT
        and int(row.get("detectionCountSum") or 0) >= STRICT_MIN_DETECTION_COUNT
    )


def score_four_way_bar_phase(
    beat_accents: Sequence[float],
    *,
    current_downbeat_index_mod4: int | None = None,
) -> dict[str, Any]:
    """Expose all four label-free accent hypotheses without changing bar phase."""
    accents = [_finite(value, float("nan")) for value in beat_accents]
    accents = [value for value in accents if math.isfinite(value)]
    if len(accents) < MIN_PHASE_BEATS:
        raise ValueError(
            f"At least {MIN_PHASE_BEATS} beat accents are required, got {len(accents)}"
        )

    candidates: list[dict[str, Any]] = []
    for downbeat_phase in range(BEATS_PER_MEASURE):
        downbeats = [
            value
            for index, value in enumerate(accents)
            if index % BEATS_PER_MEASURE == downbeat_phase
        ]
        others = [
            value
            for index, value in enumerate(accents)
            if index % BEATS_PER_MEASURE != downbeat_phase
        ]
        if len(downbeats) < 2 or len(others) < 2:
            raise ValueError("Insufficient beat accents for four-way phase scoring")
        downbeat_mean = float(mean(downbeats))
        other_mean = float(mean(others))
        candidates.append(
            {
                "downbeatIndexMod4": int(downbeat_phase),
                "firstBeatInMeasure": int((-downbeat_phase) % BEATS_PER_MEASURE),
                "downbeatMeanAccent": downbeat_mean,
                "otherBeatMeanAccent": other_mean,
                "accentContrast": float(downbeat_mean - other_mean),
                "downbeatSampleCount": len(downbeats),
                "otherBeatSampleCount": len(others),
            }
        )

    ranked = sorted(
        candidates,
        key=lambda item: (-float(item["accentContrast"]), int(item["downbeatIndexMod4"])),
    )
    winner = ranked[0]
    runner_up = ranked[1]
    spread = max(float(pstdev(accents)), 1.0e-9)
    separation = max(
        0.0,
        float(winner["accentContrast"]) - float(runner_up["accentContrast"]),
    )
    confidence = max(0.0, min(1.0, separation / spread))

    current = None if current_downbeat_index_mod4 is None else int(current_downbeat_index_mod4) % 4
    return {
        "beatCount": len(accents),
        "candidates": candidates,
        "winnerDownbeatIndexMod4": int(winner["downbeatIndexMod4"]),
        "winnerFirstBeatInMeasure": int(winner["firstBeatInMeasure"]),
        "winnerAccentContrast": float(winner["accentContrast"]),
        "runnerUpAccentContrast": float(runner_up["accentContrast"]),
        "winnerSeparation": float(separation),
        "accentSpread": float(spread),
        "confidence": float(confidence),
        "currentDownbeatIndexMod4": current,
        "currentWinnerMatches": (
            None if current is None else int(winner["downbeatIndexMod4"]) == current
        ),
        "phaseSelectedOrChanged": False,
    }


def extract_reference_free_beat_accents(
    normalized_audio_path: str,
    beat_times: Sequence[float],
) -> list[float]:
    """Reconstruct the production timing accent signal at already-tracked beats."""
    try:
        import numpy as np
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError("numpy and soundfile are required for beat-accent extraction") from exc

    from v143_reference_free_timing import (
        TIMING_SAMPLE_RATE,
        _finite_audio,
        _normalized_onset_envelope,
        _resample_audio,
    )

    samples, sample_rate = sf.read(str(normalized_audio_path), always_2d=False)
    mono = _finite_audio(samples)
    analysis_audio = _resample_audio(mono, int(sample_rate), TIMING_SAMPLE_RATE)
    onset, low_energy, frame_times = _normalized_onset_envelope(
        analysis_audio,
        TIMING_SAMPLE_RATE,
    )

    accents: list[float] = []
    for raw_time in beat_times:
        beat_time = _finite(raw_time, float("nan"))
        if not math.isfinite(beat_time):
            continue
        position = int(np.searchsorted(frame_times, beat_time))
        options = [
            index
            for index in (position - 1, position)
            if 0 <= index < len(frame_times)
        ]
        if not options:
            continue
        frame_index = min(
            options,
            key=lambda index: abs(float(frame_times[index]) - beat_time),
        )
        accents.append(
            float(onset[frame_index] + 0.25 * low_energy[frame_index])
        )
    return accents


def summarize_grid_ambiguity(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
) -> dict[str, Any]:
    """Measure nearest-vs-runner-up slot margins without moving any onset."""
    by_measure: dict[int, list[tuple[int, float]]] = {}
    for raw_key, raw_time in grid.items():
        try:
            measure = int(raw_key[0])
            step = int(raw_key[1])
            time_value = float(raw_time)
        except (TypeError, ValueError, IndexError):
            continue
        if math.isfinite(time_value):
            by_measure.setdefault(measure, []).append((step, time_value))
    for options in by_measure.values():
        options.sort(key=lambda item: item[0])

    rows: list[dict[str, Any]] = []
    strict_margins: list[float] = []
    all_margins: list[float] = []
    for row in carrier_rows:
        try:
            measure = int(row["measure"])
            onset = float(row["onsetTime"])
        except (KeyError, TypeError, ValueError):
            continue
        if not math.isfinite(onset):
            continue
        options = by_measure.get(measure) or []
        if len(options) < 2:
            continue
        distances = sorted(
            (
                abs(onset - time_value),
                int(step),
                float(time_value),
            )
            for step, time_value in options
        )
        nearest = distances[0]
        runner_up = distances[1]
        margin = max(0.0, float(runner_up[0] - nearest[0]))
        strict = _strict_row(row)
        all_margins.append(margin)
        if strict:
            strict_margins.append(margin)
        rows.append(
            {
                "measure": measure,
                "nearestStep": int(nearest[1]),
                "nearestAbsoluteResidualSeconds": float(nearest[0]),
                "runnerUpStep": int(runner_up[1]),
                "runnerUpAbsoluteResidualSeconds": float(runner_up[0]),
                "nearestRunnerUpMarginSeconds": margin,
                "ambiguousWithin20ms": margin <= GRID_AMBIGUITY_MARGIN_SECONDS,
                "strictPhysicalSupport": strict,
            }
        )

    strict_count = len(strict_margins)
    all_count = len(all_margins)
    return {
        "rowCount": len(rows),
        "strictRowCount": strict_count,
        "ambiguityMarginSeconds": GRID_AMBIGUITY_MARGIN_SECONDS,
        "allRows": {
            "ambiguousCount": sum(
                margin <= GRID_AMBIGUITY_MARGIN_SECONDS for margin in all_margins
            ),
            "ambiguousFraction": (
                sum(margin <= GRID_AMBIGUITY_MARGIN_SECONDS for margin in all_margins)
                / all_count
                if all_count
                else 0.0
            ),
            "marginP10Seconds": _percentile(all_margins, 0.10),
            "marginP50Seconds": _percentile(all_margins, 0.50),
        },
        "strictRows": {
            "ambiguousCount": sum(
                margin <= GRID_AMBIGUITY_MARGIN_SECONDS for margin in strict_margins
            ),
            "ambiguousFraction": (
                sum(margin <= GRID_AMBIGUITY_MARGIN_SECONDS for margin in strict_margins)
                / strict_count
                if strict_count
                else 0.0
            ),
            "marginP10Seconds": _percentile(strict_margins, 0.10),
            "marginP50Seconds": _percentile(strict_margins, 0.50),
            "marginMedianSeconds": float(median(strict_margins)) if strict_margins else 0.0,
        },
        "mostAmbiguousStrictRows": [
            item
            for item in sorted(
                (item for item in rows if item["strictPhysicalSupport"]),
                key=lambda item: (
                    float(item["nearestRunnerUpMarginSeconds"]),
                    int(item["measure"]),
                    int(item["nearestStep"]),
                ),
            )[:20]
        ],
    }


def summarize_timing_hypothesis_shadow(
    beat_accents: Sequence[float],
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    *,
    current_downbeat_index_mod4: int,
) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "mode": "v143-reference-free-timing-hypothesis-shadow",
        "barPhaseEvidence": score_four_way_bar_phase(
            beat_accents,
            current_downbeat_index_mod4=current_downbeat_index_mod4,
        ),
        "gridAmbiguity": summarize_grid_ambiguity(carrier_rows, grid),
        "invariants": {
            "tempoChanged": False,
            "barPhaseChanged": False,
            "attackTimingChanged": False,
            "candidateSelectionChanged": False,
            "pitchChanged": False,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        },
    }


__all__ = [
    "BEATS_PER_MEASURE",
    "MIN_PHASE_BEATS",
    "GRID_AMBIGUITY_MARGIN_SECONDS",
    "score_four_way_bar_phase",
    "extract_reference_free_beat_accents",
    "summarize_grid_ambiguity",
    "summarize_timing_hypothesis_shadow",
]
