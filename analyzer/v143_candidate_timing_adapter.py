from __future__ import annotations

import math
from bisect import bisect_left
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Callable, Iterable, Sequence


GUITAR_MIDI_MIN = 40
GUITAR_MIDI_MAX = 88
MAX_GRID_ERROR_SECONDS = 0.10
MINIMUM_NOTE_LENGTH_MS = 20.0
MINIMUM_FREQUENCY_HZ = 80.0
MAXIMUM_FREQUENCY_HZ = 1400.0

# Historical read-only profiling tested all four thresholds. Production only needs
# the widest run to establish a high-recall candidate universe; V143 performs the
# downstream rhythm/sustain selection.
HISTORICAL_WIDE_RECALL_SWEEPS = (
    ("o030_f020", 0.30, 0.20),
    ("o025_f015", 0.25, 0.15),
    ("o020_f012", 0.20, 0.12),
    ("o015_f010", 0.15, 0.10),
)
PRODUCTION_SWEEPS = (HISTORICAL_WIDE_RECALL_SWEEPS[-1],)

Predictor = Callable[..., Any]


@dataclass(frozen=True)
class TimingSlot:
    global_step: int
    measure: int
    step: int
    time_seconds: float


def _finite_float(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def validate_beat_times(beat_times: Iterable[float]) -> list[float]:
    beats = [_finite_float(value, "beat time") for value in beat_times]
    if len(beats) < 2:
        raise ValueError("At least two beat times are required")
    if beats[0] < 0.0:
        raise ValueError("Beat times cannot be negative")
    for left, right in zip(beats[:-1], beats[1:]):
        if right <= left:
            raise ValueError("Beat times must be strictly increasing")
    return beats


def build_subdivision_grid(
    beat_times: Iterable[float],
    *,
    beats_per_measure: int = 4,
    subdivisions_per_beat: int = 4,
    measure_start: int = 1,
    first_beat_in_measure: int = 0,
) -> list[TimingSlot]:
    """
    Convert reference-free beat times into the within-measure grid V143 expects.

    `first_beat_in_measure` makes bar phase explicit instead of silently assuming
    that every uploaded file starts on a downbeat. With the defaults, 4/4 audio
    is represented as sixteen steps per measure.
    """
    beats = validate_beat_times(beat_times)
    beats_per_measure = int(beats_per_measure)
    subdivisions_per_beat = int(subdivisions_per_beat)
    measure_start = int(measure_start)
    first_beat_in_measure = int(first_beat_in_measure)

    if beats_per_measure <= 0 or subdivisions_per_beat <= 0:
        raise ValueError("Meter and subdivision counts must be positive")
    if measure_start < 0:
        raise ValueError("measure_start cannot be negative")
    if not 0 <= first_beat_in_measure < beats_per_measure:
        raise ValueError("first_beat_in_measure is outside the requested meter")

    intervals = [right - left for left, right in zip(beats[:-1], beats[1:])]
    tail_interval = float(median(intervals[-min(4, len(intervals)) :]))
    steps_per_measure = beats_per_measure * subdivisions_per_beat

    slots: list[TimingSlot] = []
    for beat_index, beat_time in enumerate(beats):
        interval = intervals[beat_index] if beat_index < len(intervals) else tail_interval
        absolute_beat = first_beat_in_measure + beat_index
        measure = measure_start + absolute_beat // beats_per_measure
        beat_in_measure = absolute_beat % beats_per_measure

        for subdivision in range(subdivisions_per_beat):
            step = beat_in_measure * subdivisions_per_beat + subdivision
            t = beat_time + interval * subdivision / float(subdivisions_per_beat)
            slots.append(
                TimingSlot(
                    global_step=len(slots),
                    measure=int(measure),
                    step=int(step),
                    time_seconds=float(t),
                )
            )

    if any(slot.step < 0 or slot.step >= steps_per_measure for slot in slots):
        raise RuntimeError("Generated timing grid contains an invalid within-measure step")
    if any(b.time_seconds <= a.time_seconds for a, b in zip(slots[:-1], slots[1:])):
        raise RuntimeError("Generated timing grid is not strictly increasing")
    return slots


def parse_note_event(event: Any) -> tuple[float, float, int, float] | None:
    """Parse the Basic Pitch event shapes used by the historical profilers."""
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
        amp_f = float(amplitude or 0.0)
    except (TypeError, ValueError):
        return None
    if not all(math.isfinite(v) for v in (start_f, end_f, amp_f)):
        return None
    return start_f, end_f, pitch_i, amp_f


def nearest_timing_slot(
    onset_time: float,
    slots: Sequence[TimingSlot],
    *,
    max_grid_error_seconds: float = MAX_GRID_ERROR_SECONDS,
) -> tuple[TimingSlot, float] | None:
    if not slots:
        return None
    onset_time = _finite_float(onset_time, "onset_time")
    max_grid_error_seconds = _finite_float(
        max_grid_error_seconds,
        "max_grid_error_seconds",
    )
    if max_grid_error_seconds < 0.0:
        raise ValueError("max_grid_error_seconds cannot be negative")

    times = [slot.time_seconds for slot in slots]
    index = bisect_left(times, onset_time)
    candidates: list[TimingSlot] = []
    if index < len(slots):
        candidates.append(slots[index])
    if index > 0:
        candidates.append(slots[index - 1])
    if not candidates:
        return None

    best = min(
        candidates,
        key=lambda slot: (abs(slot.time_seconds - onset_time), slot.global_step),
    )
    error = abs(best.time_seconds - onset_time)
    if error > max_grid_error_seconds:
        return None
    return best, float(error)


def _load_basic_pitch_predictor() -> Predictor:
    try:
        from basic_pitch.inference import predict
    except ImportError as exc:
        raise RuntimeError("basic-pitch is required for production candidate detection") from exc
    return predict


def note_events_from_predict(
    stem_path: str | Path,
    *,
    predictor: Predictor | None = None,
    onset_threshold: float = 0.15,
    frame_threshold: float = 0.10,
) -> list[Any]:
    predict_fn = predictor or _load_basic_pitch_predictor()
    result = predict_fn(
        str(stem_path),
        onset_threshold=float(onset_threshold),
        frame_threshold=float(frame_threshold),
        minimum_note_length=MINIMUM_NOTE_LENGTH_MS,
        minimum_frequency=MINIMUM_FREQUENCY_HZ,
        maximum_frequency=MAXIMUM_FREQUENCY_HZ,
    )
    if not isinstance(result, tuple) or len(result) < 3:
        raise RuntimeError(f"Unexpected Basic Pitch return shape for {stem_path}")
    return list(result[2] or [])


def _hypothesis_quality(row: dict[str, Any]) -> tuple[float, float, float, float]:
    return (
        float(row["sourceCount"]),
        float(row["maxAmplitude"]),
        -float(row["minGridError"]),
        float(row["maxDuration"]),
    )


def candidate_slots_from_event_groups(
    event_groups: Iterable[tuple[str, Iterable[Any]]],
    timing_slots: Sequence[TimingSlot],
    *,
    max_grid_error_seconds: float = MAX_GRID_ERROR_SECONDS,
    guitar_midi_min: int = GUITAR_MIDI_MIN,
    guitar_midi_max: int = GUITAR_MIDI_MAX,
) -> list[dict[str, Any]]:
    """
    Map Basic Pitch note events to unique rhythmic slots.

    Historical V143 training collapsed pitch hypotheses to unique (measure, step)
    slots before extracting rhythm/sustain audio patches. Production does the same
    while retaining pitch hypotheses as metadata for the later note stage.
    """
    if not timing_slots:
        raise ValueError("No timing slots supplied")

    by_slot: dict[tuple[int, int], dict[str, Any]] = {}
    for source_name, raw_events in event_groups:
        source_name = str(source_name)
        for raw in raw_events:
            parsed = parse_note_event(raw)
            if parsed is None:
                continue
            start, end, pitch, amplitude = parsed
            if pitch < int(guitar_midi_min) or pitch > int(guitar_midi_max):
                continue
            nearest = nearest_timing_slot(
                start,
                timing_slots,
                max_grid_error_seconds=max_grid_error_seconds,
            )
            if nearest is None:
                continue
            slot, grid_error = nearest
            duration = max(0.0, end - start)
            key = (slot.measure, slot.step)
            aggregate = by_slot.setdefault(
                key,
                {
                    "slot": slot,
                    "events": [],
                },
            )
            aggregate["events"].append(
                {
                    "midi": int(pitch),
                    "amplitude": float(amplitude),
                    "gridError": float(grid_error),
                    "duration": float(duration),
                    "onsetTime": float(start),
                    "offsetTime": float(end),
                    "source": source_name,
                }
            )

    rows: list[dict[str, Any]] = []
    for (_measure, _step), aggregate in sorted(
        by_slot.items(),
        key=lambda item: item[1]["slot"].global_step,
    ):
        slot: TimingSlot = aggregate["slot"]
        events: list[dict[str, Any]] = aggregate["events"]
        by_pitch: dict[int, list[dict[str, Any]]] = {}
        for event in events:
            by_pitch.setdefault(int(event["midi"]), []).append(event)

        hypotheses: list[dict[str, Any]] = []
        for pitch, pitch_events in sorted(by_pitch.items()):
            source_names = sorted({str(event["source"]) for event in pitch_events})
            best_event = max(
                pitch_events,
                key=lambda event: (
                    float(event["amplitude"]),
                    -float(event["gridError"]),
                    float(event["duration"]),
                    -float(event["onsetTime"]),
                ),
            )
            hypotheses.append(
                {
                    "midi": int(pitch),
                    "sourceCount": len(source_names),
                    "sources": source_names,
                    "eventCount": len(pitch_events),
                    "maxAmplitude": max(float(event["amplitude"]) for event in pitch_events),
                    "meanAmplitude": sum(float(event["amplitude"]) for event in pitch_events) / len(pitch_events),
                    "minGridError": min(float(event["gridError"]) for event in pitch_events),
                    "maxDuration": max(float(event["duration"]) for event in pitch_events),
                    "bestOnsetTime": float(best_event["onsetTime"]),
                    "bestOffsetTime": float(best_event["offsetTime"]),
                }
            )

        dominant = max(
            hypotheses,
            key=lambda row: (_hypothesis_quality(row), -int(row["midi"])),
        )
        row = {
            "measure": int(slot.measure),
            "step": int(slot.step),
            # V143 patch extraction must be centered on the quantized grid time,
            # not on the raw Basic Pitch onset estimate.
            "time_seconds": float(slot.time_seconds),
            "gridGlobalStep": int(slot.global_step),
            "candidatePitchCount": len(hypotheses),
            "sourceCount": len({str(event["source"]) for event in events}),
            "eventCount": len(events),
            "dominantMidi": int(dominant["midi"]),
            "pitchHypotheses": hypotheses,
        }
        rows.append(row)

    if not rows:
        raise ValueError("Basic Pitch produced no candidates within the timing grid")
    return rows


def detect_candidate_slots(
    stem_paths: Sequence[str | Path],
    beat_times: Iterable[float],
    *,
    predictor: Predictor | None = None,
    sweeps: Sequence[tuple[str, float, float]] = PRODUCTION_SWEEPS,
    beats_per_measure: int = 4,
    subdivisions_per_beat: int = 4,
    measure_start: int = 1,
    first_beat_in_measure: int = 0,
    max_grid_error_seconds: float = MAX_GRID_ERROR_SECONDS,
) -> list[dict[str, Any]]:
    if not stem_paths:
        raise ValueError("At least one production stem path is required")
    if not sweeps:
        raise ValueError("At least one Basic Pitch sweep is required")

    grid = build_subdivision_grid(
        beat_times,
        beats_per_measure=beats_per_measure,
        subdivisions_per_beat=subdivisions_per_beat,
        measure_start=measure_start,
        first_beat_in_measure=first_beat_in_measure,
    )

    event_groups: list[tuple[str, list[Any]]] = []
    predict_fn = predictor or _load_basic_pitch_predictor()
    for stem_index, stem_path in enumerate(stem_paths):
        stem = Path(stem_path)
        for sweep_name, onset_threshold, frame_threshold in sweeps:
            events = note_events_from_predict(
                stem,
                predictor=predict_fn,
                onset_threshold=float(onset_threshold),
                frame_threshold=float(frame_threshold),
            )
            event_groups.append(
                (f"stem{stem_index}:{stem.name}:{sweep_name}", events)
            )

    return candidate_slots_from_event_groups(
        event_groups,
        grid,
        max_grid_error_seconds=max_grid_error_seconds,
    )


__all__ = [
    "GUITAR_MIDI_MIN",
    "GUITAR_MIDI_MAX",
    "MAX_GRID_ERROR_SECONDS",
    "HISTORICAL_WIDE_RECALL_SWEEPS",
    "PRODUCTION_SWEEPS",
    "TimingSlot",
    "validate_beat_times",
    "build_subdivision_grid",
    "parse_note_event",
    "nearest_timing_slot",
    "note_events_from_predict",
    "candidate_slots_from_event_groups",
    "detect_candidate_slots",
]
