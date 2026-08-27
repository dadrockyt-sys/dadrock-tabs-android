"""CPU-only V147 Phase-B generated pitch-to-V145 integration adapter.

This module is intentionally reference-free and audio-free. It applies the
already-frozen V147 pitch hypothesis decision to cloned generated Rhythm events
and sends those clones through the untouched V145 CPU decoder.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from modal.v145_rhythm_decoder import (
    DEFAULT_MAX_FRET,
    DEFAULT_MAX_FRET_SPAN,
    DEFAULT_MAX_SHIFT_STEPS,
    DEFAULT_MAX_STATES,
    STANDARD_TUNING,
    DecodeResult,
    decode_nearest_timing_path,
    normalize_rhythm_events,
)
from modal.v147_pitch_hypothesis import choose_pitch_hypothesis


@dataclass(frozen=True)
class GeneratedIntegrationResult:
    corrected_events: tuple[dict[str, Any], ...]
    decisions: tuple[dict[str, Any], ...]
    normalized_evidence_count: int
    decode_result: DecodeResult


def apply_generated_pitch_hypotheses(
    events: Sequence[Mapping[str, object]],
    evidence_by_source_index: Mapping[int, Mapping[int, Mapping[str, Any]]] | Any,
) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...], int]:
    """Clone generated events and apply frozen V147 decisions by source index.

    Caller-owned event mappings are never mutated. A canonical ``midi`` field is
    added only when V147 selects an alternate pitch, making the corrected pitch
    the first pitch key consumed by the untouched V145 normalizer.
    """

    cloned_events = [dict(event) for event in events]
    normalized = normalize_rhythm_events(events)
    decisions: list[dict[str, Any]] = []

    evidence_mapping = evidence_by_source_index if isinstance(evidence_by_source_index, Mapping) else {}

    for event in normalized:
        evidence = evidence_mapping.get(event.source_index)
        decision = choose_pitch_hypothesis(event.midi, evidence)
        public_decision = {"sourceIndex": event.source_index, **decision}
        decisions.append(public_decision)

        if decision["changed"]:
            cloned_events[event.source_index]["midi"] = int(decision["selectedMidi"])

    decisions.sort(key=lambda row: int(row["sourceIndex"]))
    return tuple(cloned_events), tuple(decisions), len(normalized)


def decode_generated_pitch_hypotheses(
    events: Sequence[Mapping[str, object]],
    evidence_by_source_index: Mapping[int, Mapping[int, Mapping[str, Any]]] | Any,
    grid_quantum_seconds: float,
    *,
    max_shift_steps: int = DEFAULT_MAX_SHIFT_STEPS,
    tuning: Sequence[int] = STANDARD_TUNING,
    max_fret: int = DEFAULT_MAX_FRET,
    max_fret_span: int = DEFAULT_MAX_FRET_SPAN,
    max_states: int = DEFAULT_MAX_STATES,
) -> GeneratedIntegrationResult:
    """Apply V147 to generated events, then decode with untouched V145 logic."""

    corrected_events, decisions, normalized_count = apply_generated_pitch_hypotheses(
        events,
        evidence_by_source_index,
    )
    decode_result = decode_nearest_timing_path(
        corrected_events,
        grid_quantum_seconds,
        max_shift_steps=max_shift_steps,
        tuning=tuning,
        max_fret=max_fret,
        max_fret_span=max_fret_span,
        max_states=max_states,
    )
    return GeneratedIntegrationResult(
        corrected_events=corrected_events,
        decisions=decisions,
        normalized_evidence_count=normalized_count,
        decode_result=decode_result,
    )


def selected_midi_by_source_index(result: GeneratedIntegrationResult) -> dict[int, int]:
    """Return the pitch V145 was intended to consume for each normalized source."""

    selected: dict[int, int] = {}
    for decision in result.decisions:
        source_index = int(decision["sourceIndex"])
        selected[source_index] = int(decision["selectedMidi"])
    return selected


def position_identity_violations(
    result: GeneratedIntegrationResult,
    *,
    tuning: Sequence[int] = STANDARD_TUNING,
    max_fret: int = DEFAULT_MAX_FRET,
) -> int:
    """Count decoded notes whose MIDI/string/fret identity violates Phase-B rules."""

    selected = selected_midi_by_source_index(result)
    violations = 0

    if len(tuning) != 6:
        return len(result.decode_result.decoded_notes)

    for note in result.decode_result.decoded_notes:
        expected_midi = selected.get(note.source_index)
        if expected_midi is None or note.midi != expected_midi:
            violations += 1
            continue
        if not 1 <= note.string <= 6 or not 0 <= note.fret <= max_fret:
            violations += 1
            continue
        tuning_index = 6 - note.string
        if tuning[tuning_index] + note.fret != note.midi:
            violations += 1
            continue
        if not 40 <= note.midi <= 88:
            violations += 1

    return violations


def integration_result_to_dict(result: GeneratedIntegrationResult) -> dict[str, Any]:
    """Return a stable JSON-compatible representation for generated proofs."""

    return {
        "correctedEvents": [dict(event) for event in result.corrected_events],
        "decisions": [dict(decision) for decision in result.decisions],
        "normalizedEvidenceCount": result.normalized_evidence_count,
        "decodeResult": {
            "decodedNotes": [
                {
                    "sourceIndex": note.source_index,
                    "midi": note.midi,
                    "rawOnset": note.raw_onset,
                    "onset": note.onset,
                    "duration": note.duration,
                    "confidence": note.confidence,
                    "timingCost": note.timing_cost,
                    "string": note.string,
                    "fret": note.fret,
                }
                for note in result.decode_result.decoded_notes
            ],
            "undecodedOnsets": list(result.decode_result.undecoded_onsets),
            "evidenceCount": result.decode_result.evidence_count,
            "decodedEvidenceCount": result.decode_result.decoded_evidence_count,
        },
    }
