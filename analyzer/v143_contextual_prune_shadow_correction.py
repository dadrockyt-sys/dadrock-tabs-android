from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import median
from typing import Any, Iterable, Mapping, Sequence


SPECTRUM_MIDI_MIN = 28
SPECTRUM_MIDI_MAX = 112
STRICT_MIN_STEM_SUPPORT = 2
STRICT_MIN_SWEEP_SUPPORT = 3
STRICT_MIN_DETECTION_COUNT = 4
ATTACK_CONSENSUS_FLOOR = 0.0
BODY_CONSENSUS_FLOOR = -0.25
SECONDARY_SCORE_MARGIN = 1.35
SECONDARY_ATTACK_MARGIN = 1.00
SECONDARY_BODY_MARGIN = 1.00
MIN_RESCUE_STEP_SEPARATION = 2
LOCAL_RESCUE_RADIUS_STEPS = 2

EventKey = tuple[int, int]


@dataclass(frozen=True)
class ShadowCorrectionResult:
    base_events: frozenset[EventKey]
    corrected_events: frozenset[EventKey]
    rescued_events: frozenset[EventKey]
    original_pitch_sets: dict[EventKey, tuple[int, ...]]
    pitch_sets: dict[EventKey, tuple[int, ...]]
    suppressed_pitch_count: int
    observed_slot_count: int
    strict_slot_count: int

    @property
    def added_event_count(self) -> int:
        return len(self.rescued_events)

    @property
    def changed(self) -> bool:
        return bool(self.rescued_events or self.suppressed_pitch_count)

    def diagnostics(self) -> dict[str, Any]:
        return {
            "baseEventCount": len(self.base_events),
            "correctedEventCount": len(self.corrected_events),
            "rescuedEventCount": len(self.rescued_events),
            "suppressedPitchCount": int(self.suppressed_pitch_count),
            "observedSlotCount": int(self.observed_slot_count),
            "strictSlotCount": int(self.strict_slot_count),
            "baseEventsPreserved": self.base_events.issubset(self.corrected_events),
            "rescuesAreObservedSlots": True,
            "localPeakRescueEnabled": True,
            "emptyMeasureFailSafeEnabled": True,
            "candidateRelocatesEvents": False,
            "referenceFree": True,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


def _finite(value: Any, default: float = -99.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _vector_value(vector: Any, midi: int) -> float:
    index = int(midi) - SPECTRUM_MIDI_MIN
    if not isinstance(vector, Sequence) or isinstance(vector, (str, bytes)):
        return -99.0
    if index < 0 or index >= len(vector):
        return -99.0
    return _finite(vector[index])


def _pitch_evidence(row: Mapping[str, Any], midi: int) -> dict[str, float]:
    view_a = row.get("viewA") if isinstance(row.get("viewA"), Mapping) else {}
    view_b = row.get("viewB") if isinstance(row.get("viewB"), Mapping) else {}

    attack_a = _vector_value(view_a.get("attackMax"), midi)
    attack_b = _vector_value(view_b.get("attackMax"), midi)
    early_a = _vector_value(view_a.get("earlyMean"), midi)
    early_b = _vector_value(view_b.get("earlyMean"), midi)
    sustain_a = _vector_value(view_a.get("sustainMean"), midi)
    sustain_b = _vector_value(view_b.get("sustainMean"), midi)

    attack = min(attack_a, attack_b)
    early = min(early_a, early_b)
    sustain = min(sustain_a, sustain_b)
    body = max(early, sustain)
    continuity = min(early, sustain)
    score = attack + 0.65 * body + 0.15 * continuity

    return {
        "attack": float(attack),
        "early": float(early),
        "sustain": float(sustain),
        "body": float(body),
        "continuity": float(continuity),
        "score": float(score),
    }


def _candidate_midis(row: Mapping[str, Any]) -> tuple[int, ...]:
    values: list[int] = []
    for raw in row.get("candidateMidis") or ():
        try:
            midi = int(raw)
        except (TypeError, ValueError):
            continue
        if SPECTRUM_MIDI_MIN <= midi <= SPECTRUM_MIDI_MAX:
            values.append(midi)
    return tuple(sorted(set(values)))


def _row_pitch_evidence(row: Mapping[str, Any]) -> dict[int, dict[str, float]]:
    return {midi: _pitch_evidence(row, midi) for midi in _candidate_midis(row)}


def _strict_attack_row(row: Mapping[str, Any]) -> bool:
    if int(row.get("stemSupportMax") or 0) < STRICT_MIN_STEM_SUPPORT:
        return False
    if int(row.get("sweepSupportMax") or 0) < STRICT_MIN_SWEEP_SUPPORT:
        return False
    if int(row.get("detectionCountSum") or 0) < STRICT_MIN_DETECTION_COUNT:
        return False
    evidence = _row_pitch_evidence(row)
    if not evidence:
        return False
    best = max(evidence.values(), key=lambda item: item["score"])
    return (
        best["attack"] > ATTACK_CONSENSUS_FLOOR
        and best["body"] > BODY_CONSENSUS_FLOOR
    )


def _grid_by_measure(grid: Mapping[EventKey, float]) -> dict[int, list[tuple[int, float]]]:
    out: dict[int, list[tuple[int, float]]] = {}
    for raw_key, raw_time in grid.items():
        try:
            measure, step = int(raw_key[0]), int(raw_key[1])
            time_value = float(raw_time)
        except (TypeError, ValueError, IndexError):
            continue
        if not math.isfinite(time_value):
            continue
        out.setdefault(measure, []).append((step, time_value))
    for values in out.values():
        values.sort(key=lambda item: item[0])
    return out


def _nearest_slot_for_row(
    row: Mapping[str, Any],
    grid_rows: Mapping[int, list[tuple[int, float]]],
) -> tuple[EventKey, float] | None:
    try:
        measure = int(row["measure"])
        onset = float(row["onsetTime"])
    except (KeyError, TypeError, ValueError):
        return None
    values = grid_rows.get(measure) or ()
    if not values:
        return None
    step, time_value = min(values, key=lambda item: (abs(onset - item[1]), item[0]))
    return (measure, int(step)), abs(onset - time_value)


def _row_strength(row: Mapping[str, Any], grid_error: float) -> float:
    evidence = _row_pitch_evidence(row)
    best_pitch = max((item["score"] for item in evidence.values()), default=-99.0)
    sweep_support = min(4, max(0, int(row.get("sweepSupportMax") or 0)))
    detection_count = min(16, max(0, int(row.get("detectionCountSum") or 0)))
    return float(best_pitch + 0.10 * sweep_support + 0.03 * detection_count - 2.0 * grid_error)


def _best_rows_by_slot(
    rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
) -> dict[EventKey, dict[str, Any]]:
    grid_rows = _grid_by_measure(grid)
    best: dict[EventKey, dict[str, Any]] = {}
    for raw in rows:
        row = dict(raw)
        nearest = _nearest_slot_for_row(row, grid_rows)
        if nearest is None:
            continue
        key, grid_error = nearest
        row["_shadowGridErrorSeconds"] = float(grid_error)
        row["_shadowEvidenceStrength"] = _row_strength(row, grid_error)
        current = best.get(key)
        if current is None or float(row["_shadowEvidenceStrength"]) > float(
            current["_shadowEvidenceStrength"]
        ):
            best[key] = row
    return best


def _steps_too_close(step: int, occupied_steps: Iterable[int]) -> bool:
    return any(
        abs(int(step) - int(other)) < MIN_RESCUE_STEP_SEPARATION
        for other in occupied_steps
    )


def _rescue_strict_local_peaks(
    base_events: set[EventKey],
    rows_by_slot: Mapping[EventKey, Mapping[str, Any]],
    target_measures: set[int],
) -> set[EventKey]:
    """Add only locally dominant, cross-view-confirmed physical onset slots.

    This replaces the old empty-measure-only rescue. It remains deliberately
    label-free: a rescue must already exist in the physical carrier, pass strict
    stem/sweep/CQT consensus, be at least the median strict evidence strength in
    its own measure, be a local strength maximum, and remain separated from an
    already-selected attack. Completely empty measures retain one conservative
    strict fail-safe so a global rank cutoff cannot erase an otherwise observed
    measure.
    """
    occupied_by_measure: dict[int, set[int]] = {}
    for measure, step in base_events:
        occupied_by_measure.setdefault(int(measure), set()).add(int(step))

    strict_by_measure: dict[int, list[tuple[EventKey, Mapping[str, Any]]]] = {}
    for key, row in rows_by_slot.items():
        if key[0] not in target_measures or key in base_events:
            continue
        if not _strict_attack_row(row):
            continue
        strict_by_measure.setdefault(key[0], []).append((key, row))

    rescued: set[EventKey] = set()
    for measure in sorted(target_measures):
        candidates = list(strict_by_measure.get(measure) or ())
        if not candidates:
            continue

        strengths = [float(row.get("_shadowEvidenceStrength") or -99.0) for _, row in candidates]
        local_floor = float(median(strengths))
        ordered = sorted(
            candidates,
            key=lambda item: (
                -float(item[1].get("_shadowEvidenceStrength") or -99.0),
                int(item[0][1]),
            ),
        )

        occupied = set(occupied_by_measure.get(measure) or ())
        measure_rescues: set[EventKey] = set()
        for key, row in ordered:
            step = int(key[1])
            strength = float(row.get("_shadowEvidenceStrength") or -99.0)
            if strength < local_floor:
                continue
            if _steps_too_close(step, occupied):
                continue

            neighborhood = [
                (other_key, other_row)
                for other_key, other_row in candidates
                if abs(int(other_key[1]) - step) <= LOCAL_RESCUE_RADIUS_STEPS
            ]
            neighborhood_winner = min(
                neighborhood,
                key=lambda item: (
                    -float(item[1].get("_shadowEvidenceStrength") or -99.0),
                    int(item[0][1]),
                ),
            )
            if neighborhood_winner[0] != key:
                continue

            measure_rescues.add(key)
            occupied.add(step)

        # A completely empty base measure is protected from global-cutoff erasure.
        # The fallback is still a strict physical row and never invents a slot.
        if not occupied_by_measure.get(measure) and not measure_rescues:
            key, _row = ordered[0]
            measure_rescues.add(key)

        rescued.update(measure_rescues)

    return rescued


def _supported_pitch_set(row: Mapping[str, Any]) -> tuple[int, ...]:
    original = _candidate_midis(row)
    evidence = _row_pitch_evidence(row)
    if not evidence:
        return ()
    ranked = sorted(
        evidence.items(),
        key=lambda item: (item[1]["score"], item[1]["attack"], -item[0]),
        reverse=True,
    )
    best_midi, best = ranked[0]

    # Suppression must be evidence-positive, not merely relative. If even the
    # strongest candidate fails the independent two-view attack/body floors,
    # preserve the observed candidate set unchanged rather than collapsing an
    # uncertain chord to an arbitrary single pitch. This keeps the shadow
    # correction conservative whenever the physical evidence is inconclusive.
    if (
        best["attack"] <= ATTACK_CONSENSUS_FLOOR
        or best["body"] <= BODY_CONSENSUS_FLOOR
    ):
        return original

    kept = {best_midi}
    for midi, item in ranked[1:]:
        if item["attack"] <= ATTACK_CONSENSUS_FLOOR:
            continue
        if item["body"] <= BODY_CONSENSUS_FLOOR:
            continue
        if item["score"] < best["score"] - SECONDARY_SCORE_MARGIN:
            continue
        if item["attack"] < best["attack"] - SECONDARY_ATTACK_MARGIN:
            continue
        if item["body"] < best["body"] - SECONDARY_BODY_MARGIN:
            continue
        kept.add(midi)

    return tuple(sorted(kept))


def apply_reference_free_shadow_correction(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    base_events: Iterable[EventKey],
    target_measures: Iterable[int],
) -> ShadowCorrectionResult:
    """Conservative isolated correction driven only by physical audio evidence.

    Existing events are preserved. Additional events may only come from strict
    cross-view physical onset rows that are locally dominant in their measure;
    completely empty measures retain a one-event strict fail-safe. Secondary
    pitch hypotheses are suppressed only when the locally strongest candidate
    itself has positive two-view attack/body support, and retained pitches must
    remain close to that strongest candidate across attack/body windows. If the
    strongest candidate is not independently supported, the original observed
    pitch set is preserved unchanged. No event is relocated and no label input is
    accepted by this function.
    """
    base = {(int(measure), int(step)) for measure, step in base_events}
    targets = {int(value) for value in target_measures}
    if not targets:
        raise ValueError("target_measures cannot be empty")
    rows_by_slot = _best_rows_by_slot(carrier_rows, grid)
    rescued = _rescue_strict_local_peaks(base, rows_by_slot, targets)
    corrected = set(base) | rescued

    original_pitch_sets: dict[EventKey, tuple[int, ...]] = {}
    pitch_sets: dict[EventKey, tuple[int, ...]] = {}
    suppressed = 0
    for key in sorted(corrected):
        row = rows_by_slot.get(key)
        if row is None:
            continue
        original = _candidate_midis(row)
        if original:
            original_pitch_sets[key] = original
        supported = _supported_pitch_set(row)
        if not supported and original:
            supported = original
        if supported:
            pitch_sets[key] = supported
            suppressed += max(0, len(original) - len(supported))

    strict_slots = sum(1 for row in rows_by_slot.values() if _strict_attack_row(row))
    result = ShadowCorrectionResult(
        base_events=frozenset(base),
        corrected_events=frozenset(corrected),
        rescued_events=frozenset(rescued),
        original_pitch_sets=original_pitch_sets,
        pitch_sets=pitch_sets,
        suppressed_pitch_count=int(suppressed),
        observed_slot_count=len(rows_by_slot),
        strict_slot_count=int(strict_slots),
    )
    if not result.base_events.issubset(result.corrected_events):
        raise RuntimeError("Shadow correction removed an existing event")
    if not result.rescued_events.issubset(set(rows_by_slot)):
        raise RuntimeError("Shadow correction invented an unobserved event slot")
    return result


__all__ = [
    "SPECTRUM_MIDI_MIN",
    "SPECTRUM_MIDI_MAX",
    "STRICT_MIN_STEM_SUPPORT",
    "STRICT_MIN_SWEEP_SUPPORT",
    "STRICT_MIN_DETECTION_COUNT",
    "MIN_RESCUE_STEP_SEPARATION",
    "LOCAL_RESCUE_RADIUS_STEPS",
    "ShadowCorrectionResult",
    "apply_reference_free_shadow_correction",
]
