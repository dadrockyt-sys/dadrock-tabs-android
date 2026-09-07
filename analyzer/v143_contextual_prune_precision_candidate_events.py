from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from v143_contextual_prune_candidate_events import (
    CorrectedCandidateAssembly,
    _best_rows_by_slot,
    _pitch_evidence,
)
from v143_contextual_prune_precision_shadow import (
    HARMONIC_INTERVAL_WEIGHTS,
    POSITIVE_ATTACK_FLOOR,
    POSITIVE_BODY_FLOOR,
    PrecisionShadowResult,
)
from v143_precision_polyphony_boundary import resolve_precision_polyphony
from v143_reference_free_rhythm_pipeline import ReferenceFreeRhythmResult
from v143_reference_free_timing import ReferenceFreeTimingEstimate
from v143_rhythm_event_assembly import RhythmEventAssemblyResult


EventKey = tuple[int, int]


def _assert_preservation_only_decision(
    *,
    precision_midis: Sequence[int],
    selected_midis: Sequence[int],
    decision: Any,
) -> None:
    """Reject any helper decision that widens precision-v2 musical authority."""
    precision_set = {int(value) for value in precision_midis}
    selected_set = {int(value) for value in selected_midis}
    candidate_set = {int(value) for value in decision.candidate_midis}
    recovered_set = {int(value) for value in decision.recovered_midis}
    dropped_set = {int(value) for value in decision.dropped_midis}

    if candidate_set != precision_set:
        raise RuntimeError(
            "Polyphony helper changed the precision-v2 candidate pitch set"
        )
    if not selected_set.issubset(precision_set):
        raise RuntimeError(
            "Polyphony helper selected a precision-v2-pruned pitch"
        )
    if recovered_set:
        raise RuntimeError(
            "Polyphony helper reported recovery under preservation-only policy"
        )
    if dropped_set != precision_set.difference(selected_set):
        raise RuntimeError(
            "Polyphony helper reported inconsistent precision-v2 drops"
        )


def _voicing_with_explicit_primary(
    row: Mapping[str, Any],
    precision_midis: Sequence[int],
    observed_midis: Sequence[int],
    primary_midi: int,
):
    precision = tuple(sorted({int(value) for value in precision_midis}))
    observed = tuple(sorted({int(value) for value in observed_midis}))
    primary = int(primary_midi)
    if primary not in set(precision):
        raise RuntimeError(
            "Precision primary is absent from retained precision pitch set"
        )
    if not set(precision).issubset(set(observed)):
        raise RuntimeError(
            "Precision pitch set is not a subset of observed pitch evidence"
        )

    evidence = {midi: _pitch_evidence(row, midi) for midi in observed}
    decision = resolve_precision_polyphony(
        primary_midi=primary,
        precision_midis=precision,
        observed_midis=observed,
        evidence=evidence,
        positive_attack_floor=POSITIVE_ATTACK_FLOOR,
        positive_body_floor=POSITIVE_BODY_FLOOR,
        harmonic_intervals=tuple(HARMONIC_INTERVAL_WEIGHTS),
    )
    selected_midis = list(decision.selected_midis)
    _assert_preservation_only_decision(
        precision_midis=precision,
        selected_midis=selected_midis,
        decision=decision,
    )
    return (
        selected_midis,
        decision.voicing,
        evidence,
        decision,
    )


def build_precision_candidate_assembly(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    precision: PrecisionShadowResult,
    timing: ReferenceFreeTimingEstimate,
) -> CorrectedCandidateAssembly:
    """Render retained precision attacks with preservation-only legal voicing.

    Precision-v2 keeps sole authority over attack identity, explicit primary, and
    retained pitch membership. This adapter may drop a retained secondary only
    when the full retained pitch set cannot be voiced legally on the six-string
    instrument. Observed pitches that precision-v2 pruned remain diagnostic
    evidence only and can never be re-admitted by feasibility or positivity.

    This adapter cannot add or relocate attacks, invent pitches, change the primary,
    consult a professional reference, or authorize a precision-pruned pitch through
    a legacy recovery marker.
    """
    if not isinstance(precision, PrecisionShadowResult):
        raise TypeError("precision must be PrecisionShadowResult")
    if not isinstance(timing, ReferenceFreeTimingEstimate):
        raise TypeError("timing must be ReferenceFreeTimingEstimate")
    if set(precision.primary_midis) != set(precision.retained_events):
        raise RuntimeError(
            "Precision result does not contain one primary per retained attack"
        )

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
            raise RuntimeError(
                f"Precision attack has no physical carrier row: {key}"
            )
        precision_supported = tuple(
            int(value) for value in precision.pitch_sets.get(key, ())
        )
        observed = tuple(
            int(value) for value in precision.original_pitch_sets.get(key, ())
        )
        primary = int(precision.primary_midis[key])
        if not precision_supported:
            raise RuntimeError(
                f"Precision attack has no retained pitch set: {key}"
            )
        if not observed:
            raise RuntimeError(
                f"Precision attack has no original observed pitch set: {key}"
            )
        if primary not in set(precision_supported):
            raise RuntimeError(f"Precision primary is not retained at {key}")

        selected_midis, voicing, evidence, decision = (
            _voicing_with_explicit_primary(
                row,
                precision_supported,
                observed,
                primary,
            )
        )
        if primary not in set(selected_midis):
            raise RuntimeError(
                f"Legal voicing dropped precision primary at {key}"
            )

        precision_set = set(precision_supported)
        selected_set = set(selected_midis)
        candidate_set = set(decision.candidate_midis)
        _assert_preservation_only_decision(
            precision_midis=precision_supported,
            selected_midis=selected_midis,
            decision=decision,
        )

        supported_pitch_count += len(candidate_set)
        rendered_pitch_count += len(selected_set)
        grid_time = float(grid[key])
        physical_onset = float(row.get("onsetTime") or grid_time)

        pitch_hypotheses = []
        for midi in observed:
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
                    "detectionCount": int(
                        row.get("detectionCountSum") or 0
                    ),
                    "precisionPrimary": int(midi) == primary,
                    "precisionRetained": int(midi) in precision_set,
                    # Legacy recovery-shaped fields are retained only for schema
                    # compatibility. They are never selection authority.
                    "feasibilityRecoveryEligible": False,
                    "feasibilityRecovered": False,
                    "rendered": int(midi) in selected_set,
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
            "v143Score": float(
                row.get("_candidateStrength")
                or row.get("_precisionStrength")
                or 0.0
            ),
            "v143Rank": int(rank),
            "v143Selected": True,
            "candidateMode": (
                "contextual-prune-reference-free-precision-"
                "primary-preserved-feasibility-polyphony"
            ),
            "polyphonyBoundary": {
                "version": 2,
                "precisionPitchCount": len(precision_set),
                "observedPitchCount": len(set(observed)),
                "candidatePitchCount": len(candidate_set),
                "renderedPitchCount": len(selected_set),
                "recoveredPitchCount": 0,
                "droppedCandidatePitchCount": len(
                    decision.dropped_midis
                ),
                "protectedPromotedHarmonicMidi": (
                    int(decision.protected_harmonic_midi)
                    if decision.protected_harmonic_midi is not None
                    else None
                ),
                "primaryMidiChanged": False,
                "attackIdentityChanged": False,
                "addsUnobservedPitch": False,
                "recoveryPermitted": False,
                "referenceFree": True,
                "professionalReferenceUsed": False,
                "runtimeLabelsRequired": False,
            },
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
            if int(midi) not in precision_set:
                raise RuntimeError(
                    "Precision candidate adapter attempted to render a "
                    f"precision-v2-pruned pitch at {key}"
                )
            position = voicing[int(midi)]
            event = deepcopy(source_row)
            event["midi"] = int(midi)
            event["stringIndex"] = int(position["stringIndex"])
            event["stringName"] = str(position["stringName"])
            event["fret"] = int(position["fret"])
            event["rhythmTechniques"] = []
            event["noteMapping"] = {
                "version": 6,
                "mode": (
                    "reference-free-precision-primary-preserved-"
                    "feasibility-polyphony-joint-voicing"
                ),
                "tuning": "standard",
                "jointChordVoicingResolved": True,
                "sourceAttackMidi": primary,
                "chordNoteIndex": int(note_index),
                "chordNoteCount": len(ordered_midis),
                "primaryTechniqueNote": int(midi) == primary,
                "precisionPrimaryPreserved": True,
                "precisionPitchRetained": True,
                # Legacy compatibility field; never selection authority.
                "feasibilityRecoveredSecondary": False,
                "observedPitchOnly": True,
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

    emitted_keys = {
        (int(event["measure"]), int(event["step"]))
        for event in events
    }
    if emitted_keys != set(corrected_keys):
        raise RuntimeError(
            "Precision candidate adapter changed attack identity"
        )
    for event in events:
        key = (int(event["measure"]), int(event["step"]))
        original = set(precision.original_pitch_sets[key])
        precision_set = set(precision.pitch_sets[key])
        midi = int(event["midi"])
        if midi not in original:
            raise RuntimeError(
                "Precision candidate adapter invented unobserved pitch "
                f"at {key}"
            )
        if midi not in precision_set:
            raise RuntimeError(
                "Precision candidate adapter emitted precision-v2-pruned "
                f"pitch at {key}"
            )
        if int(event["dominantMidi"]) != int(
            precision.primary_midis[key]
        ):
            raise RuntimeError(
                f"Precision candidate adapter changed primary at {key}"
            )
        if bool(
            event.get("noteMapping", {}).get(
                "feasibilityRecoveredSecondary"
            )
        ):
            raise RuntimeError(
                "Precision candidate adapter emitted a recovery marker under "
                f"preservation-only policy at {key}"
            )

    return CorrectedCandidateAssembly(
        source=source,
        assembly=assembly,
        corrected_attack_count=len(corrected_keys),
        rendered_note_count=len(events),
        supported_pitch_count=int(supported_pitch_count),
        rendered_pitch_count=int(rendered_pitch_count),
        voicing_dropped_pitch_count=int(
            supported_pitch_count - rendered_pitch_count
        ),
    )


__all__ = ["build_precision_candidate_assembly"]
