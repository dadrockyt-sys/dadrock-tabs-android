from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from v143_contextual_prune_precision_shadow import (
    HARMONIC_INTERVAL_WEIGHTS,
    POSITIVE_ATTACK_FLOOR,
    POSITIVE_BODY_FLOOR,
    EventKey,
    PrecisionShadowResult,
    _best_rows_by_slot,
    _candidate_midis,
    _pitch_evidence,
)


@dataclass(frozen=True)
class PromotedHarmonicGuardDiagnostics:
    inspected_attack_count: int
    promoted_primary_count: int
    harmonic_strongest_above_promoted_primary_count: int
    suppressed_strongest_harmonic_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": 1,
            "guard": "v143-reference-free-promoted-fundamental-strongest-harmonic",
            "inspectedAttackCount": int(self.inspected_attack_count),
            "promotedPrimaryCount": int(self.promoted_primary_count),
            "harmonicStrongestAbovePromotedPrimaryCount": int(
                self.harmonic_strongest_above_promoted_primary_count
            ),
            "suppressedStrongestHarmonicCount": int(self.suppressed_strongest_harmonic_count),
            "attackIdentityChanged": False,
            "primaryMidiChanged": False,
            "addsUnobservedAttack": False,
            "addsUnobservedPitch": False,
            "relocatesAttack": False,
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


def _strongest_positive_raw_midi(row: Mapping[str, Any]) -> int | None:
    evidence = {
        midi: _pitch_evidence(row, midi)
        for midi in _candidate_midis(row)
    }
    positive = {
        midi: item
        for midi, item in evidence.items()
        if item["attack"] > POSITIVE_ATTACK_FLOOR
        and item["body"] > POSITIVE_BODY_FLOOR
    }
    if not positive:
        return None
    return int(
        max(
            positive,
            key=lambda midi: (
                positive[midi]["score"],
                positive[midi]["attack"],
                -int(midi),
            ),
        )
    )


def apply_reference_free_promoted_harmonic_guard(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    precision: PrecisionShadowResult,
) -> tuple[PrecisionShadowResult, PromotedHarmonicGuardDiagnostics]:
    """Remove only the strongest upper harmonic that a promotion reinterpreted.

    The precision stage may deliberately replace its strongest raw pitch with a
    lower physically observed candidate when upper harmonic-family evidence makes
    the lower candidate the more plausible fundamental. Before this guard, that
    same strongest upper pitch was then automatically retained as a secondary
    because its relative score/attack/body ratios are 1.0 by definition. That is
    internally contradictory: one decision interprets the strongest upper as an
    overtone supporting a lower fundamental while the next renders it as an
    independent chord note.

    This guard is intentionally minimal. It changes no attack, grid position,
    primary, non-harmonic secondary, or weaker harmonic secondary. It only removes
    the exact strongest raw pitch when (a) the primary was promoted away from it,
    (b) the strongest raw is an upper harmonic-family interval from that promoted
    primary, and (c) it survived into the selected pitch set.
    """
    if not isinstance(precision, PrecisionShadowResult):
        raise TypeError("precision must be PrecisionShadowResult")

    rows_by_slot = _best_rows_by_slot(carrier_rows, grid)
    guarded_sets: dict[EventKey, tuple[int, ...]] = {
        key: tuple(int(value) for value in values)
        for key, values in precision.pitch_sets.items()
    }

    promoted_count = 0
    harmonic_strongest_count = 0
    suppressed_count = 0

    for key in sorted(precision.retained_events):
        row = rows_by_slot.get(key)
        if row is None:
            raise RuntimeError(f"Promoted-harmonic guard has no carrier row for {key}")
        if key not in guarded_sets or key not in precision.primary_midis:
            raise RuntimeError(f"Promoted-harmonic guard missing precision identity for {key}")

        primary = int(precision.primary_midis[key])
        strongest_raw = _strongest_positive_raw_midi(row)
        if strongest_raw is None or strongest_raw == primary:
            continue

        promoted_count += 1
        interval = int(strongest_raw) - int(primary)
        if interval not in HARMONIC_INTERVAL_WEIGHTS:
            continue
        harmonic_strongest_count += 1

        selected = set(guarded_sets[key])
        if strongest_raw not in selected:
            continue
        selected.remove(strongest_raw)
        if primary not in selected:
            raise RuntimeError(f"Promoted-harmonic guard removed primary at {key}")
        if not selected:
            raise RuntimeError(f"Promoted-harmonic guard emptied pitch set at {key}")
        guarded_sets[key] = tuple(sorted(selected))
        suppressed_count += 1

    guarded = replace(
        precision,
        pitch_sets=guarded_sets,
        suppressed_pitch_count=int(precision.suppressed_pitch_count) + int(suppressed_count),
    )

    if guarded.retained_events != precision.retained_events:
        raise RuntimeError("Promoted-harmonic guard changed attack identity")
    if guarded.primary_midis != precision.primary_midis:
        raise RuntimeError("Promoted-harmonic guard changed primary MIDI")
    for key, values in guarded.pitch_sets.items():
        before = set(precision.pitch_sets[key])
        after = set(values)
        if not after.issubset(before):
            raise RuntimeError(f"Promoted-harmonic guard invented pitch at {key}")
        if int(guarded.primary_midis[key]) not in after:
            raise RuntimeError(f"Promoted-harmonic guard lost primary at {key}")

    diagnostics = PromotedHarmonicGuardDiagnostics(
        inspected_attack_count=len(precision.retained_events),
        promoted_primary_count=promoted_count,
        harmonic_strongest_above_promoted_primary_count=harmonic_strongest_count,
        suppressed_strongest_harmonic_count=suppressed_count,
    )
    return guarded, diagnostics


__all__ = [
    "PromotedHarmonicGuardDiagnostics",
    "apply_reference_free_promoted_harmonic_guard",
]
