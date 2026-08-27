"""Reference-free support for the frozen V147 Phase-C artifact protocol.

This module deliberately does *not* decode audio. It provides only pre-audio
identity/materialization helpers, frozen frame selection, delegation to the
already-frozen V147 CQT evidence/decision code, and fixed-timing guitar-position
assignment.
"""

from __future__ import annotations

import hashlib
import math
import sys
from itertools import product
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MODAL_DIR = ROOT / "modal"
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
for entry in (MODAL_DIR, HOLDOUT_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
from v144_rhythm_pitch_position_shift_policy import apply_pitch_position_rule  # noqa: E402
from v144_rhythm_pitch_shift_policy import apply_pitch_shift_rule  # noqa: E402
from v144_rhythm_singleton_onset_replacement_policy import (  # noqa: E402
    apply_singleton_onset_replacement_rule,
)
from v144_rhythm_triple_conjunction_policy import apply_triple_prune  # noqa: E402

from modal.v145_rhythm_decoder import enumerate_guitar_positions  # noqa: E402
from modal.v147_pitch_hypothesis import choose_pitch_hypothesis_from_cqt  # noqa: E402


EXPECTED_RAW_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_V5_EVENT_COUNT = 1209
EXPECTED_V5_EVENT_SHA256 = "7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1"
EXPECTED_TRIPLE_EVENT_SHA256 = "68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3"
EXPECTED_PITCH_SHIFT_EVENT_SHA256 = "b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6"
EXPECTED_PITCH_POSITION_EVENT_SHA256 = "5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d"
EXPECTED_ACCEPTED_EVENT_COUNT = 1144
EXPECTED_ACCEPTED_EVENT_SHA256 = "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881"
EXPECTED_MEASURE_COUNT = 113

TRIPLE_SIGNATURES = ("register::high", "section16::1", "stepParity::0")
PITCH_SHIFT_SIGNATURES = ("pitchClass::4", "stepQuarter::0")
PITCH_SHIFT_SEMITONES = -2
PITCH_POSITION_SIGNATURES = ("pitchClass::11", "stepParity::0")
PITCH_POSITION_SEMITONES = -2
PITCH_POSITION_STRING_SHIFT = 1
SINGLETON_CONTEXT = "stepParity::0"
SINGLETON_SOURCE_STRING_INDEX = 0
SINGLETON_SOURCE_PITCH_CLASS = 4
SINGLETON_TARGET_STRING_INDEX = 3
SINGLETON_SEMITONES = -12

TEMPO_BPM = 129.19921875
STEPS_PER_BEAT = 4
STEPS_PER_MEASURE = 16
FRAME_START_OFFSET_SECONDS = 0.020
FRAME_MAX_SPAN_SECONDS = 0.180
FRAME_MIN_SPAN_SECONDS = 0.060
FRAME_DURATION_FRACTION = 0.75
FRAME_NEXT_ONSET_GUARD_SECONDS = 0.020
MIN_USABLE_FRAMES = 3

MIN_V147_MIDI = 40
MAX_V147_MIDI = 88
MAX_FRET = 24
OPEN_MIDI_BY_STRING_INDEX = {0: 64, 1: 59, 2: 55, 3: 50, 4: 45, 5: 40}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_sha256(payload: bytes, expected_sha256: str) -> str:
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("payload must be bytes-like")
    expected = str(expected_sha256).strip().lower()
    if len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
        raise ValueError("expected_sha256 must be a 64-character lowercase hexadecimal digest")
    actual = sha256_bytes(bytes(payload))
    if actual != expected:
        raise ValueError(f"SHA-256 mismatch: expected {expected}, got {actual}")
    return actual


def verify_raw_audio_identity(audio_bytes: bytes) -> str:
    """Verify exact historical audio bytes without decoding or inspecting waveform data."""
    return verify_sha256(audio_bytes, EXPECTED_RAW_AUDIO_SHA256)


def _assert_event_stage(
    events: Sequence[Mapping[str, Any]],
    *,
    expected_count: int,
    expected_sha256: str,
    label: str,
) -> list[dict[str, Any]]:
    canonical = canonical_events(events)
    actual_sha = sha256_json(canonical)
    if len(canonical) != expected_count or actual_sha != expected_sha256:
        raise ValueError(
            f"{label} identity mismatch count={len(canonical)} sha={actual_sha} "
            f"expected_count={expected_count} expected_sha={expected_sha256}"
        )
    return [dict(row) for row in canonical]


def materialize_accepted_family(
    v5_render_stream_or_events: Mapping[str, Any] | Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Replay only the already-selected reference-free transforms for family #10."""
    if isinstance(v5_render_stream_or_events, Mapping):
        source = v5_render_stream_or_events.get("events")
    else:
        source = v5_render_stream_or_events
    if not isinstance(source, Sequence) or isinstance(source, (str, bytes, bytearray)):
        raise ValueError("V5 source must contain an event sequence")

    events = _assert_event_stage(
        source,
        expected_count=EXPECTED_V5_EVENT_COUNT,
        expected_sha256=EXPECTED_V5_EVENT_SHA256,
        label="V5 source",
    )

    events = apply_triple_prune(events, TRIPLE_SIGNATURES)
    events = _assert_event_stage(
        events,
        expected_count=EXPECTED_ACCEPTED_EVENT_COUNT,
        expected_sha256=EXPECTED_TRIPLE_EVENT_SHA256,
        label="selected triple prune",
    )

    events = apply_pitch_shift_rule(
        events,
        PITCH_SHIFT_SIGNATURES,
        PITCH_SHIFT_SEMITONES,
    )
    events = _assert_event_stage(
        events,
        expected_count=EXPECTED_ACCEPTED_EVENT_COUNT,
        expected_sha256=EXPECTED_PITCH_SHIFT_EVENT_SHA256,
        label="selected pitch shift",
    )

    events = apply_pitch_position_rule(
        events,
        PITCH_POSITION_SIGNATURES,
        PITCH_POSITION_SEMITONES,
        PITCH_POSITION_STRING_SHIFT,
    )
    events = _assert_event_stage(
        events,
        expected_count=EXPECTED_ACCEPTED_EVENT_COUNT,
        expected_sha256=EXPECTED_PITCH_POSITION_EVENT_SHA256,
        label="selected pitch-position shift",
    )

    events = apply_singleton_onset_replacement_rule(
        events,
        SINGLETON_CONTEXT,
        SINGLETON_SOURCE_STRING_INDEX,
        SINGLETON_SOURCE_PITCH_CLASS,
        SINGLETON_TARGET_STRING_INDEX,
        SINGLETON_SEMITONES,
    )
    events = _assert_event_stage(
        events,
        expected_count=EXPECTED_ACCEPTED_EVENT_COUNT,
        expected_sha256=EXPECTED_ACCEPTED_EVENT_SHA256,
        label="accepted family #10",
    )

    measures = {int(row["measure"]) for row in events}
    if len(measures) != EXPECTED_MEASURE_COUNT or measures != set(range(1, EXPECTED_MEASURE_COUNT + 1)):
        raise ValueError("accepted family generated measure set changed")
    return events


def event_onset_seconds(event: Mapping[str, Any]) -> float:
    measure = int(event["measure"])
    step = int(event["step"])
    if measure < 1 or step < 0 or step >= STEPS_PER_MEASURE:
        raise ValueError("event measure/step is outside the frozen 4/4 grid")
    absolute_step = (measure - 1) * STEPS_PER_MEASURE + step
    return float(absolute_step) * (60.0 / TEMPO_BPM) / float(STEPS_PER_BEAT)


def event_frame_window(
    event: Mapping[str, Any],
    *,
    next_onset_seconds: float | None = None,
) -> tuple[float, float]:
    onset = event_onset_seconds(event)
    try:
        duration = float(event.get("durationSeconds", 0.0))
    except (TypeError, ValueError):
        duration = 0.0
    if not math.isfinite(duration) or duration < 0.0:
        duration = 0.0
    span = min(
        FRAME_MAX_SPAN_SECONDS,
        max(FRAME_MIN_SPAN_SECONDS, duration * FRAME_DURATION_FRACTION),
    )
    start = onset + FRAME_START_OFFSET_SECONDS
    end = onset + span
    if next_onset_seconds is not None:
        next_value = float(next_onset_seconds)
        if math.isfinite(next_value):
            end = min(end, next_value - FRAME_NEXT_ONSET_GUARD_SECONDS)
    return (float(start), float(end))


def select_frame_indices(
    frame_times: Sequence[float],
    event: Mapping[str, Any],
    *,
    next_onset_seconds: float | None = None,
) -> tuple[int, ...]:
    start, end = event_frame_window(event, next_onset_seconds=next_onset_seconds)
    if end < start:
        return tuple()
    selected: list[int] = []
    for index, raw_time in enumerate(frame_times):
        try:
            time_value = float(raw_time)
        except (TypeError, ValueError):
            return tuple()
        if not math.isfinite(time_value):
            return tuple()
        if start <= time_value <= end:
            selected.append(index)
    return tuple(selected)


def decide_event_from_prepared_cqt(
    event: Mapping[str, Any],
    cqt_magnitude: Any,
    midi_bins: Any,
    frame_times: Sequence[float],
    *,
    next_onset_seconds: float | None = None,
) -> dict[str, Any]:
    """Select frozen Phase-C frames then delegate all evidence math to V147."""
    original_midi = int(event["midi"])
    frames = select_frame_indices(
        frame_times,
        event,
        next_onset_seconds=next_onset_seconds,
    )
    if len(frames) < MIN_USABLE_FRAMES:
        return {
            "originalMidi": original_midi,
            "selectedMidi": original_midi,
            "changed": False,
            "semitoneDelta": 0,
            "reason": "insufficient-frames",
            "candidates": [],
            "frameIndices": list(frames),
        }
    decision = dict(
        choose_pitch_hypothesis_from_cqt(
            original_midi,
            cqt_magnitude,
            midi_bins,
            frames,
        )
    )
    decision["frameIndices"] = list(frames)
    return decision


def _validate_fixed_event_position(event: Mapping[str, Any]) -> tuple[int, int, int]:
    string_index = int(event["stringIndex"])
    fret = int(event["fret"])
    midi = int(event["midi"])
    if string_index not in OPEN_MIDI_BY_STRING_INDEX:
        raise ValueError("invalid accepted stringIndex")
    if fret < 0:
        raise ValueError("invalid accepted fret")
    if OPEN_MIDI_BY_STRING_INDEX[string_index] + fret != midi:
        raise ValueError("accepted event pitch-position identity mismatch")
    return string_index, fret, midi


def _assignment_key(
    fixed_rows: Sequence[Mapping[str, Any]],
    changed_rows: Sequence[tuple[Mapping[str, Any], int]],
    positions: Sequence[Any],
) -> tuple[Any, ...]:
    frets = [int(row["fret"]) for row in fixed_rows] + [int(position.fret) for position in positions]
    span = max(frets) - min(frets) if frets else 0
    anchor = sum(frets) / len(frets) if frets else 0.0
    local_cost = span * 0.25 + anchor * 0.01
    movement = sum(
        abs(int(position.fret) - int(row["fret"]))
        for (row, _), position in zip(changed_rows, positions)
    )
    identity = tuple(
        (int(selected_midi), int(position.string), int(position.fret))
        for (_, selected_midi), position in zip(changed_rows, positions)
    )
    return (float(local_cost), int(span), float(anchor), int(movement), identity)


def apply_fixed_time_pitch_decisions(
    accepted_events: Sequence[Mapping[str, Any]],
    selected_midi_by_event_index: Mapping[int, int],
) -> dict[str, Any]:
    """Apply ±1 decisions without changing accepted timing or unchanged event positions."""
    source = [dict(row) for row in accepted_events]
    output = [dict(row) for row in accepted_events]
    by_onset: dict[tuple[int, int], list[int]] = {}
    for index, row in enumerate(source):
        by_onset.setdefault((int(row["measure"]), int(row["step"])), []).append(index)

    changed_event_count = 0
    fail_closed_groups = 0

    for onset in sorted(by_onset):
        indices = by_onset[onset]
        changed_rows: list[tuple[Mapping[str, Any], int, int]] = []
        fixed_rows: list[Mapping[str, Any]] = []
        invalid_group = False

        for list_index in indices:
            row = source[list_index]
            event_index = int(row["eventIndex"])
            original_midi = int(row["midi"])
            selected_midi = int(selected_midi_by_event_index.get(event_index, original_midi))
            if selected_midi == original_midi:
                _validate_fixed_event_position(row)
                fixed_rows.append(row)
                continue
            if (
                abs(selected_midi - original_midi) != 1
                or selected_midi < MIN_V147_MIDI
                or selected_midi > MAX_V147_MIDI
            ):
                invalid_group = True
                break
            changed_rows.append((row, selected_midi, list_index))

        if invalid_group or not changed_rows:
            if invalid_group:
                fail_closed_groups += 1
            continue

        fixed_strings: set[int] = set()
        duplicate_fixed_string = False
        for row in fixed_rows:
            string_number = int(row["stringIndex"]) + 1
            if string_number in fixed_strings:
                duplicate_fixed_string = True
                break
            fixed_strings.add(string_number)
        if duplicate_fixed_string:
            fail_closed_groups += 1
            continue

        position_options: list[tuple[Any, ...]] = []
        for row, selected_midi, _ in changed_rows:
            options = tuple(
                position
                for position in enumerate_guitar_positions(selected_midi, max_fret=MAX_FRET)
                if int(position.string) not in fixed_strings
            )
            if not options:
                invalid_group = True
                break
            position_options.append(options)
        if invalid_group:
            fail_closed_groups += 1
            continue

        valid_assignments: list[tuple[Any, ...]] = []
        for positions in product(*position_options):
            strings = [int(position.string) for position in positions]
            if len(strings) != len(set(strings)):
                continue
            valid_assignments.append(tuple(positions))
        if not valid_assignments:
            fail_closed_groups += 1
            continue

        rows_for_key = [(row, selected) for row, selected, _ in changed_rows]
        best = min(
            valid_assignments,
            key=lambda positions: _assignment_key(fixed_rows, rows_for_key, positions),
        )
        for (row, selected_midi, list_index), position in zip(changed_rows, best):
            output[list_index]["midi"] = int(selected_midi)
            output[list_index]["stringIndex"] = int(position.string) - 1
            output[list_index]["fret"] = int(position.fret)
            changed_event_count += 1

    return {
        "events": output,
        "changedEventCount": changed_event_count,
        "onsetGroupFailClosedCount": fail_closed_groups,
    }


def timing_and_metadata_violations(
    before: Sequence[Mapping[str, Any]],
    after: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return all forbidden mutations; only midi/stringIndex/fret may differ."""
    if len(before) != len(after):
        return [{"reason": "event-count-changed", "before": len(before), "after": len(after)}]
    allowed = {"midi", "stringIndex", "fret"}
    violations: list[dict[str, Any]] = []
    for index, (left, right) in enumerate(zip(before, after)):
        changed_keys = {
            key
            for key in set(left) | set(right)
            if left.get(key) != right.get(key)
        }
        forbidden = sorted(changed_keys - allowed)
        if forbidden:
            violations.append({"eventIndex": index, "forbiddenFields": forbidden})
    return violations


__all__ = [
    "EXPECTED_ACCEPTED_EVENT_COUNT",
    "EXPECTED_ACCEPTED_EVENT_SHA256",
    "EXPECTED_RAW_AUDIO_SHA256",
    "apply_fixed_time_pitch_decisions",
    "decide_event_from_prepared_cqt",
    "event_frame_window",
    "event_onset_seconds",
    "materialize_accepted_family",
    "select_frame_indices",
    "sha256_bytes",
    "timing_and_metadata_violations",
    "verify_raw_audio_identity",
    "verify_sha256",
]
