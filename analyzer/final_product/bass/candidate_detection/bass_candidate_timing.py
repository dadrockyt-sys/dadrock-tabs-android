from __future__ import annotations

import math
from pathlib import Path
from statistics import median
from typing import Any, Callable, Iterable, Sequence

from final_product.bass.hz_features.bass_frequency_profile import (
    STANDARD_BASS_STRINGS,
    playable_fundamental_hz_bounds,
    playable_midi_bounds,
)
from final_product.shared.timing_grid import (
    DEFAULT_MAX_GRID_ERROR_SECONDS,
    TimingSlot,
    build_subdivision_grid,
    nearest_timing_slot,
)


BASS_MIDI_MIN, BASS_MIDI_MAX = playable_midi_bounds()
BASS_MIN_FREQUENCY_HZ, BASS_MAX_FREQUENCY_HZ = playable_fundamental_hz_bounds()
BASIC_PITCH_ONSET_THRESHOLD = 0.15
BASIC_PITCH_FRAME_THRESHOLD = 0.10
BASIC_PITCH_MINIMUM_NOTE_LENGTH_MS = 30.0
REQUIRED_CONSENSUS_VIEWS = 2
MAX_ACCEPTED_EVENTS = 5000

Predictor = Callable[..., Any]


def parse_note_event(event: Any) -> tuple[float, float, int, float] | None:
    """Parse Basic Pitch note events without assuming a particular tuple shape."""
    if isinstance(event, dict):
        start = event.get("start_time", event.get("start", event.get("startTime")))
        end = event.get("end_time", event.get("end", event.get("endTime", start)))
        pitch = event.get("pitch_midi", event.get("midi", event.get("pitch")))
        amplitude = event.get(
            "amplitude",
            event.get("confidence", event.get("velocity", 0.0)),
        )
    elif isinstance(event, (list, tuple)) and len(event) >= 3:
        start, end, pitch = event[0], event[1], event[2]
        amplitude = event[3] if len(event) >= 4 else 0.0
    else:
        return None

    try:
        start_f = float(start)
        end_f = float(end)
        pitch_i = int(round(float(pitch)))
        amplitude_f = float(amplitude or 0.0)
    except (TypeError, ValueError):
        return None
    if not all(math.isfinite(value) for value in (start_f, end_f, amplitude_f)):
        return None
    if start_f < 0.0 or end_f < start_f:
        return None
    return start_f, end_f, pitch_i, amplitude_f


def _load_basic_pitch_predictor() -> Predictor:
    try:
        from basic_pitch.inference import predict
    except ImportError as exc:
        raise RuntimeError("basic-pitch is required for Bass candidate detection") from exc
    return predict


def note_events_from_stem(
    stem_path: str | Path,
    *,
    predictor: Predictor | None = None,
    onset_threshold: float = BASIC_PITCH_ONSET_THRESHOLD,
    frame_threshold: float = BASIC_PITCH_FRAME_THRESHOLD,
) -> list[Any]:
    stem = Path(stem_path)
    if not stem.is_file() or stem.stat().st_size <= 0:
        raise FileNotFoundError(stem)

    predict_fn = predictor or _load_basic_pitch_predictor()
    result = predict_fn(
        str(stem),
        onset_threshold=float(onset_threshold),
        frame_threshold=float(frame_threshold),
        minimum_note_length=BASIC_PITCH_MINIMUM_NOTE_LENGTH_MS,
        minimum_frequency=float(BASS_MIN_FREQUENCY_HZ),
        maximum_frequency=float(BASS_MAX_FREQUENCY_HZ),
    )
    if not isinstance(result, tuple) or len(result) < 3:
        raise RuntimeError(f"Unexpected Basic Pitch return shape for {stem}")
    return list(result[2] or [])


def playable_positions(midi: int) -> list[dict[str, int | str]]:
    value = int(midi)
    positions: list[dict[str, int | str]] = []
    for string_index, (label, open_midi) in enumerate(STANDARD_BASS_STRINGS):
        fret = value - int(open_midi)
        if 0 <= fret <= 24:
            positions.append(
                {
                    "stringIndex": int(string_index),
                    "stringLabel": str(label),
                    "fret": int(fret),
                    "midi": value,
                }
            )
    return positions


def _choose_position(
    midi: int,
    previous: dict[str, Any] | None,
) -> dict[str, int | str]:
    positions = playable_positions(midi)
    if not positions:
        raise ValueError(f"MIDI {midi} has no playable Standard Bass position")

    if previous is None:
        return min(
            positions,
            key=lambda row: (int(row["fret"]), int(row["stringIndex"])),
        )

    previous_fret = int(previous["fret"])
    previous_string = int(previous["stringIndex"])

    def movement_cost(row: dict[str, int | str]) -> tuple[float, int, int]:
        fret = int(row["fret"])
        string_index = int(row["stringIndex"])
        cost = (
            abs(fret - previous_fret)
            + 2.0 * abs(string_index - previous_string)
            + 0.05 * fret
        )
        return float(cost), fret, string_index

    return min(positions, key=movement_cost)


def _duration_steps(duration_seconds: float, slots: Sequence[TimingSlot]) -> int:
    if len(slots) < 2:
        return 1
    step_intervals = [
        right.time_seconds - left.time_seconds
        for left, right in zip(slots[:-1], slots[1:])
        if right.time_seconds > left.time_seconds
    ]
    if not step_intervals:
        return 1
    typical_step = float(median(step_intervals))
    if typical_step <= 0.0:
        return 1
    return max(1, min(16, int(round(float(duration_seconds) / typical_step))))


def candidate_events_from_event_groups(
    event_groups: Iterable[tuple[str, Iterable[Any]]],
    timing_slots: Sequence[TimingSlot],
    *,
    required_consensus_views: int = REQUIRED_CONSENSUS_VIEWS,
    max_grid_error_seconds: float = DEFAULT_MAX_GRID_ERROR_SECONDS,
) -> dict[str, Any]:
    """Create one cross-view Bass note candidate per authenticated timing slot."""
    if not timing_slots:
        raise ValueError("No authenticated timing slots supplied")
    required_consensus_views = int(required_consensus_views)
    if required_consensus_views < 2:
        raise ValueError("Professional Bass candidates require at least two views")

    by_slot_pitch: dict[tuple[int, int, int], list[dict[str, Any]]] = {}
    source_raw_counts: dict[str, int] = {}
    source_in_range_counts: dict[str, int] = {}
    source_grid_aligned_counts: dict[str, int] = {}

    for source_name, raw_events in event_groups:
        source = str(source_name)
        events = list(raw_events)
        source_raw_counts[source] = len(events)
        source_in_range_counts[source] = 0
        source_grid_aligned_counts[source] = 0

        for raw in events:
            parsed = parse_note_event(raw)
            if parsed is None:
                continue
            start, end, pitch, amplitude = parsed
            if pitch < BASS_MIDI_MIN or pitch > BASS_MIDI_MAX:
                continue
            source_in_range_counts[source] += 1

            nearest = nearest_timing_slot(
                start,
                timing_slots,
                max_grid_error_seconds=max_grid_error_seconds,
            )
            if nearest is None:
                continue
            source_grid_aligned_counts[source] += 1
            slot, grid_error = nearest
            key = (int(slot.measure), int(slot.step), int(pitch))
            by_slot_pitch.setdefault(key, []).append(
                {
                    "source": source,
                    "midi": int(pitch),
                    "amplitude": float(amplitude),
                    "gridErrorSeconds": float(grid_error),
                    "onsetTimeSeconds": float(start),
                    "offsetTimeSeconds": float(end),
                    "durationSeconds": float(max(0.0, end - start)),
                    "globalStep": int(slot.global_step),
                    "gridTimeSeconds": float(slot.time_seconds),
                }
            )

    consensus_by_slot: dict[tuple[int, int], list[dict[str, Any]]] = {}
    rejected_without_consensus = 0
    for (measure, step, pitch), events in by_slot_pitch.items():
        sources = sorted({str(event["source"]) for event in events})
        if len(sources) < required_consensus_views:
            rejected_without_consensus += 1
            continue

        best = max(
            events,
            key=lambda event: (
                float(event["amplitude"]),
                -float(event["gridErrorSeconds"]),
                float(event["durationSeconds"]),
                -float(event["onsetTimeSeconds"]),
            ),
        )
        hypothesis = {
            "measure": int(measure),
            "step": int(step),
            "globalStep": int(best["globalStep"]),
            "timeSeconds": float(best["gridTimeSeconds"]),
            "midi": int(pitch),
            "sourceCount": len(sources),
            "sources": sources,
            "eventCount": len(events),
            "maxAmplitude": max(float(event["amplitude"]) for event in events),
            "meanAmplitude": sum(float(event["amplitude"]) for event in events)
            / len(events),
            "minGridErrorSeconds": min(
                float(event["gridErrorSeconds"]) for event in events
            ),
            "durationSeconds": max(
                float(event["durationSeconds"]) for event in events
            ),
        }
        consensus_by_slot.setdefault((measure, step), []).append(hypothesis)

    selected: list[dict[str, Any]] = []
    for (_measure, _step), hypotheses in sorted(
        consensus_by_slot.items(),
        key=lambda item: min(int(row["globalStep"]) for row in item[1]),
    ):
        winner = max(
            hypotheses,
            key=lambda row: (
                int(row["sourceCount"]),
                float(row["maxAmplitude"]),
                -float(row["minGridErrorSeconds"]),
                float(row["durationSeconds"]),
                -int(row["midi"]),
            ),
        )
        selected.append(dict(winner))
        if len(selected) >= MAX_ACCEPTED_EVENTS:
            break

    if not selected:
        raise ValueError("No cross-view Bass candidates survived timing authentication")

    previous_position: dict[str, Any] | None = None
    accepted_events: list[dict[str, Any]] = []
    for row in selected:
        position = _choose_position(int(row["midi"]), previous_position)
        event = {
            "measure": int(row["measure"]),
            "step": int(row["step"]),
            "timeSeconds": float(row["timeSeconds"]),
            "midi": int(row["midi"]),
            "stringIndex": int(position["stringIndex"]),
            "stringLabel": str(position["stringLabel"]),
            "fret": int(position["fret"]),
            "durationSeconds": float(row["durationSeconds"]),
            "durationSteps": _duration_steps(
                float(row["durationSeconds"]),
                timing_slots,
            ),
            "sourceCount": int(row["sourceCount"]),
            "sources": list(row["sources"]),
            "candidateEventCount": int(row["eventCount"]),
            "candidateMaxAmplitude": float(row["maxAmplitude"]),
            "candidateMeanAmplitude": float(row["meanAmplitude"]),
            "gridErrorSeconds": float(row["minGridErrorSeconds"]),
            "techniques": [],
        }
        accepted_events.append(event)
        previous_position = event

    return {
        "events": accepted_events,
        "diagnostics": {
            "sourceRawEventCounts": source_raw_counts,
            "sourceInBassRangeCounts": source_in_range_counts,
            "sourceGridAlignedCounts": source_grid_aligned_counts,
            "slotPitchHypothesisCount": len(by_slot_pitch),
            "rejectedSlotPitchHypothesesWithoutConsensus": rejected_without_consensus,
            "consensusSlotCount": len(consensus_by_slot),
            "acceptedEventCount": len(accepted_events),
            "requiredConsensusViews": required_consensus_views,
            "maximumGridErrorSeconds": float(max_grid_error_seconds),
            "bassMidiMinimum": BASS_MIDI_MIN,
            "bassMidiMaximum": BASS_MIDI_MAX,
            "bassMinimumFrequencyHz": float(BASS_MIN_FREQUENCY_HZ),
            "bassMaximumFrequencyHz": float(BASS_MAX_FREQUENCY_HZ),
        },
    }


def detect_bass_candidate_events(
    stem_paths: Sequence[str | Path],
    beat_times: Iterable[float],
    *,
    first_beat_in_measure: int,
    predictor: Predictor | None = None,
) -> dict[str, Any]:
    if len(stem_paths) < REQUIRED_CONSENSUS_VIEWS:
        raise ValueError("Bass candidate detection requires direct and cascade stems")

    timing_slots = build_subdivision_grid(
        beat_times,
        beats_per_measure=4,
        subdivisions_per_beat=4,
        measure_start=1,
        first_beat_in_measure=int(first_beat_in_measure),
    )

    predict_fn = predictor or _load_basic_pitch_predictor()
    event_groups: list[tuple[str, list[Any]]] = []
    for index, stem_path in enumerate(stem_paths):
        source_name = "direct" if index == 0 else "cascade" if index == 1 else f"view{index}"
        event_groups.append(
            (
                source_name,
                note_events_from_stem(stem_path, predictor=predict_fn),
            )
        )

    return candidate_events_from_event_groups(
        event_groups,
        timing_slots,
        required_consensus_views=REQUIRED_CONSENSUS_VIEWS,
        max_grid_error_seconds=DEFAULT_MAX_GRID_ERROR_SECONDS,
    )


__all__ = [
    "BASS_MIDI_MIN",
    "BASS_MIDI_MAX",
    "BASS_MIN_FREQUENCY_HZ",
    "BASS_MAX_FREQUENCY_HZ",
    "BASIC_PITCH_ONSET_THRESHOLD",
    "BASIC_PITCH_FRAME_THRESHOLD",
    "REQUIRED_CONSENSUS_VIEWS",
    "parse_note_event",
    "note_events_from_stem",
    "playable_positions",
    "candidate_events_from_event_groups",
    "detect_bass_candidate_events",
]
