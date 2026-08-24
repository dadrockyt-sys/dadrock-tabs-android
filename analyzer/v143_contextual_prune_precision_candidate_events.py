from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from v143_contextual_prune_candidate_events import (
    CorrectedCandidateAssembly,
    _best_rows_by_slot,
    _pitch_evidence,
)
from v143_contextual_prune_precision_shadow import PrecisionShadowResult
from v143_reference_free_rhythm_pipeline import ReferenceFreeRhythmResult
from v143_reference_free_timing import ReferenceFreeTimingEstimate
from v143_rhythm_event_assembly import RhythmEventAssemblyResult
from v143_rhythm_guitar_note_mapper import resolve_joint_chord_voicing


MAX_GUITAR_STRINGS = 6
EventKey = tuple[int, int]


def _voicing_with_explicit_primary(
    row: Mapping[str, Any],
    supported_midis: Sequence[int],
    primary_midi: int,
) -> tuple[list[int], dict[int, dict[str, Any]], dict[int, dict[str, float]]]:
    supported = tuple(sorted({int(value) for value in supported_midis}))
    primary = int(primary_midi)
    if primary not in set(supported):
        raise RuntimeError("Precision primary is absent from supported pitch set")

    evidence = {midi: _pitch_evidence(row, midi) for midi in supported}
    others = sorted(
        (midi for midi in supported if midi != primary),
        key=lambda midi: (
            -evidence[midi]["score"],
            -evidence[midi]["attack"],
            -evidence[midi]["body"],
            int(midi),
        ),
    )

    # The primary selected by the precision stage is immutable here. Legal
    # secondary tones are admitted only if the entire set remains playable.
    selected = [primary]
    voicing = resolve_joint_chord_voicing(selected)
    if voicing is None:
        raise RuntimeError(f"Precision primary MIDI {primary} has no legal guitar position")

    for midi in others:
        if len(selected) >= MAX_GUITAR_STRINGS:
            break
        trial = selected + [int(midi)]
        trial_voicing = resolve_joint_chord_voicing(trial)
        if trial_voicing is None:
            continue
        selected = trial
        voicing = trial_voicing

    return selected, voicing, evidence


def build_precision_candidate_assembly(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    precision: PrecisionShadowResult,
    timing: ReferenceFreeTimingEstimate,
) -> CorrectedCandidateAssembly:
    """Render retained precision attacks while preserving their chosen primary.

    The precision stage has already selected an observed pitch set and one
    explicit primary/fundamental for every retained attack. This adapter only
    resolves a legal guitar voicing. It cannot re-rank the primary, add pitches,
    add attacks, or relocate attacks.
    """
    if not isinstance(precision, PrecisionShadowResult):
        raise TypeError("precision must be PrecisionShadowResult")
    if not isinstance(timing, ReferenceFreeTimingEstimate):
        raise TypeError("timing must be ReferenceFreeTimingEstimate")
    if set(precision.primary_midis) != set(precision.retained_events):
        raise RuntimeError("Precision result does not contain one primary per retained attack")

    rows_by_slot = _best_rows_by_slot(carrier_rows, grid)
    corrected_keys = sorted(precision.retained_events)
    if not corrected_keys:
        raise RuntimeError("Precision candidate contains no attacks")

    source_rows: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    supported_pitch_count = 0
    rendered_pitch_count = 0

    for rank, key in enumerate(corrected_keys, start=1):
        row = rows_by_slot.get(key)
        if row is None:
            raise RuntimeError(f"Precision attack has no physical carrier row: {key}")
        supported = tuple(int(value) for value in precision.pitch_sets.get(key, ()))
        primary = int(precision.primary_midis[key])
        if not supported:
            raise RuntimeError(f"Precision attack has no supported pitch set: {key}")
        if primary not in set(supported):
            raise RuntimeError(f"Precision primary is not retained at {key}")
        supported_pitch_count += len(supported)

        selected_midis, voicing, evidence = _voicing_with_explicit_primary(
            row,
            supported,
            primary,
        )
        if primary not in set(selected_midis):
            raise RuntimeError(f"Legal voicing dropped precision primary at {key}")
        rendered_pitch_count += len(selected_midis)
        grid_time = float(grid[key])
        physical_onset = float(row.get("onsetTime") or grid_time)

        pitch_hypotheses = []
        for midi in supported:
            item = evidence[int(midi)]
            pitch_hypotheses.append(
                {
                    "midi": int(midi),
                    "physicalAttack": float(item["attack"]),
                    "physicalBody": float(item["body"]),
                    "physicalContinuity": float(item["continuity"]),
                    "physicalScore": float(item["score"]),
                    "stemSupport": int(row.get("stemSupportMax") or 0),
                    "sweepSupport": int(row.get("sweepSupportMax") or 0),
                    "detectionCount": int(row.get("detectionCountSum") or 0),
                    "precisionPrimary": int(midi) == primary,
                    "source": "reference-free-two-view-cqt-consensus",
                }
            )

        source_row = {
            "measure": int(key[0]),
            "step": int(key[1]),
            "timeSeconds": grid_time,
            "onsetTime": physical_onset,
            "dominantMidi": primary,
            "pitchHypotheses": deepcopy(pitch_hypotheses),
            "v143Score": float(row.get("_candidateStrength") or row.get("_precisionStrength") or 0.0),
            "v143Rank": int(rank),
            "v143Selected": True,
            "candidateMode": "contextual-prune-reference-free-precision-primary-preserved",
        }
        source_rows.append(source_row)

        ordered_midis = sorted(
            selected_midis,
            key=lambda midi: (
                int(voicing[int(midi)]["stringIndex"]),
                int(midi),
            ),
        )
        for note_index, midi in enumerate(ordered_midis):
            position = voicing[int(midi)]
            event = deepcopy(source_row)
            event["midi"] = int(midi)
            event["stringIndex"] = int(position["stringIndex"])
            event["stringName"] = str(position["stringName"])
            event["fret"] = int(position["fret"])
            event["rhythmTechniques"] = []
            event["noteMapping"] = {
                "version": 4,
                "mode": "reference-free-precision-primary-preserved-joint-voicing",
                "tuning": "standard",
                "jointChordVoicingResolved": True,
                "sourceAttackMidi": primary,
                "chordNoteIndex": int(note_index),
                "chordNoteCount": len(ordered_midis),
                "primaryTechniqueNote": int(midi) == primary,
                "precisionPrimaryPreserved": True,
                "professionalReferenceUsed": False,
                "runtimeLabelsRequired": False,
            }
            events.append(event)

    source = ReferenceFreeRhythmResult(
        timing=timing,
        candidates=tuple(deepcopy(row) for row in source_rows),
        rows=tuple(deepcopy(row) for row in source_rows),
    )
    assembly = RhythmEventAssemblyResult(
        source=source,
        events=tuple(deepcopy(event) for event in events),
    )

    emitted_keys = {(int(event["measure"]), int(event["step"])) for event in events}
    if emitted_keys != set(corrected_keys):
        raise RuntimeError("Precision candidate adapter changed attack identity")
    for event in events:
        key = (int(event["measure"]), int(event["step"]))
        if int(event["midi"]) not in set(precision.pitch_sets[key]):
            raise RuntimeError(f"Precision candidate adapter invented pitch at {key}")
        if int(event["dominantMidi"]) != int(precision.primary_midis[key]):
            raise RuntimeError(f"Precision candidate adapter changed primary at {key}")

    return CorrectedCandidateAssembly(
        source=source,
        assembly=assembly,
        corrected_attack_count=len(corrected_keys),
        rendered_note_count=len(events),
        supported_pitch_count=int(supported_pitch_count),
        rendered_pitch_count=int(rendered_pitch_count),
        voicing_dropped_pitch_count=int(supported_pitch_count - rendered_pitch_count),
    )


__all__ = ["build_precision_candidate_assembly"]
