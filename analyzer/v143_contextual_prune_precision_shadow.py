from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from v143_contextual_prune_shadow_correction import ShadowCorrectionResult


SPECTRUM_MIDI_MIN = 28
SPECTRUM_MIDI_MAX = 112
ATTACK_TRANSIENT_RATIO_FLOOR = 0.70
ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR = 0.60
LOCAL_STRENGTH_MARGIN = 0.20
LOCAL_RADIUS_STEPS = 2
POSITIVE_ATTACK_FLOOR = 0.0
POSITIVE_BODY_FLOOR = -0.25
FUNDAMENTAL_MIN_RAW_RATIO = 0.55
SECONDARY_RAW_RATIO = 0.80
HARMONIC_SECONDARY_RAW_RATIO = 0.92
HARMONIC_INTERVAL_WEIGHTS = {
    12: 0.35,
    19: 0.25,
    24: 0.20,
    28: 0.12,
    31: 0.10,
    36: 0.08,
}

EventKey = tuple[int, int]


@dataclass(frozen=True)
class PrecisionShadowResult:
    input_events: frozenset[EventKey]
    retained_events: frozenset[EventKey]
    pruned_events: frozenset[EventKey]
    original_pitch_sets: dict[EventKey, tuple[int, ...]]
    pitch_sets: dict[EventKey, tuple[int, ...]]
    primary_midis: dict[EventKey, int]
    fail_safe_events: frozenset[EventKey]
    fundamental_promotions: int
    suppressed_pitch_count: int

    def diagnostics(self) -> dict[str, Any]:
        before_pitches = sum(len(value) for value in self.original_pitch_sets.values())
        after_pitches = sum(len(value) for value in self.pitch_sets.values())
        primary_complete = (
            set(self.primary_midis) == set(self.retained_events)
            and all(
                int(primary) in set(self.pitch_sets.get(key, ()))
                for key, primary in self.primary_midis.items()
            )
        )
        return {
            "inputAttackCount": len(self.input_events),
            "retainedAttackCount": len(self.retained_events),
            "prunedAttackCount": len(self.pruned_events),
            "failSafeAttackCount": len(self.fail_safe_events),
            "originalPitchHypothesisCount": int(before_pitches),
            "retainedPitchHypothesisCount": int(after_pitches),
            "explicitPrimaryMidiCount": len(self.primary_midis),
            "explicitPrimaryMidiComplete": bool(primary_complete),
            "suppressedPitchCount": int(self.suppressed_pitch_count),
            "fundamentalPromotionCount": int(self.fundamental_promotions),
            "attackTransientRatioFloor": ATTACK_TRANSIENT_RATIO_FLOOR,
            "attackTransientRatioExceptionFloor": ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR,
            "secondaryRawRatio": SECONDARY_RAW_RATIO,
            "harmonicSecondaryRawRatio": HARMONIC_SECONDARY_RAW_RATIO,
            "candidateAddsUnobservedAttack": False,
            "candidateRelocatesEvents": False,
            "candidateAddsUnobservedPitch": False,
            "emptyMeasureFailSafeEnabled": True,
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
    if not isinstance(vector, Sequence) or isinstance(vector, (str, bytes, bytearray)):
        return -99.0
    if index < 0 or index >= len(vector):
        return -99.0
    return _finite(vector[index])


def _candidate_midis(row: Mapping[str, Any]) -> tuple[int, ...]:
    values: set[int] = set()
    for raw in row.get("candidateMidis") or ():
        try:
            midi = int(raw)
        except (TypeError, ValueError):
            continue
        if SPECTRUM_MIDI_MIN <= midi <= SPECTRUM_MIDI_MAX:
            values.add(midi)
    return tuple(sorted(values))


def _pitch_evidence(row: Mapping[str, Any], midi: int) -> dict[str, float]:
    view_a = row.get("viewA") if isinstance(row.get("viewA"), Mapping) else {}
    view_b = row.get("viewB") if isinstance(row.get("viewB"), Mapping) else {}
    attack = min(_vector_value(view_a.get("attackMax"), midi), _vector_value(view_b.get("attackMax"), midi))
    early = min(_vector_value(view_a.get("earlyMean"), midi), _vector_value(view_b.get("earlyMean"), midi))
    sustain = min(_vector_value(view_a.get("sustainMean"), midi), _vector_value(view_b.get("sustainMean"), midi))
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


def _grid_by_measure(grid: Mapping[EventKey, float]) -> dict[int, list[tuple[int, float]]]:
    output: dict[int, list[tuple[int, float]]] = {}
    for raw_key, raw_time in grid.items():
        try:
            measure, step = int(raw_key[0]), int(raw_key[1])
            time_value = float(raw_time)
        except (TypeError, ValueError, IndexError):
            continue
        if math.isfinite(time_value):
            output.setdefault(measure, []).append((step, time_value))
    for values in output.values():
        values.sort(key=lambda item: item[0])
    return output


def _best_rows_by_slot(
    rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
) -> dict[EventKey, dict[str, Any]]:
    grid_rows = _grid_by_measure(grid)
    best: dict[EventKey, dict[str, Any]] = {}
    for raw in rows:
        try:
            measure = int(raw["measure"])
            onset = float(raw["onsetTime"])
        except (KeyError, TypeError, ValueError):
            continue
        slots = grid_rows.get(measure) or ()
        if not slots:
            continue
        step, slot_time = min(slots, key=lambda item: (abs(onset - item[1]), item[0]))
        key = (measure, int(step))
        grid_error = abs(onset - slot_time)
        evidence = [_pitch_evidence(raw, midi) for midi in _candidate_midis(raw)]
        strongest = max((item["score"] for item in evidence), default=-99.0)
        strength = (
            strongest
            + 0.10 * min(4, max(0, int(raw.get("sweepSupportMax") or 0)))
            + 0.03 * min(16, max(0, int(raw.get("detectionCountSum") or 0)))
            - 2.0 * grid_error
        )
        current = best.get(key)
        if current is None or strength > float(current.get("_precisionStrength") or -99.0):
            row = dict(raw)
            row["_precisionStrength"] = float(strength)
            row["_precisionGridErrorSeconds"] = float(grid_error)
            best[key] = row
    return best


def _best_evidence(row: Mapping[str, Any]) -> tuple[int | None, dict[str, float] | None]:
    values = [(midi, _pitch_evidence(row, midi)) for midi in _candidate_midis(row)]
    if not values:
        return None, None
    return max(values, key=lambda item: (item[1]["score"], item[1]["attack"], -item[0]))


def _transient_ratio(evidence: Mapping[str, float] | None) -> float:
    if not evidence:
        return 0.0
    attack = max(0.0, float(evidence.get("attack") or 0.0))
    body = max(1e-6, float(evidence.get("body") or 0.0))
    return float(attack / body)


def _locally_prominent(
    key: EventKey,
    rows_by_slot: Mapping[EventKey, Mapping[str, Any]],
    eligible: set[EventKey],
) -> bool:
    row = rows_by_slot.get(key)
    if row is None:
        return False
    strength = float(row.get("_precisionStrength") or -99.0)
    neighbors = [
        float(other_row.get("_precisionStrength") or -99.0)
        for other_key, other_row in rows_by_slot.items()
        if other_key in eligible
        and other_key != key
        and other_key[0] == key[0]
        and abs(int(other_key[1]) - int(key[1])) <= LOCAL_RADIUS_STEPS
    ]
    if not neighbors:
        return True
    return strength >= max(neighbors) + LOCAL_STRENGTH_MARGIN


def _attack_is_precise(
    key: EventKey,
    row: Mapping[str, Any],
    rows_by_slot: Mapping[EventKey, Mapping[str, Any]],
    eligible: set[EventKey],
) -> bool:
    _midi, evidence = _best_evidence(row)
    if evidence is None:
        return False
    if evidence["attack"] <= POSITIVE_ATTACK_FLOOR or evidence["body"] <= POSITIVE_BODY_FLOOR:
        return False
    ratio = _transient_ratio(evidence)
    if ratio >= ATTACK_TRANSIENT_RATIO_FLOOR:
        return True
    return (
        ratio >= ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR
        and _locally_prominent(key, rows_by_slot, eligible)
    )


def _harmonic_family_score(
    midi: int,
    evidence: Mapping[int, Mapping[str, float]],
) -> float:
    base = evidence[midi]
    score = float(base["score"])
    for interval, weight in HARMONIC_INTERVAL_WEIGHTS.items():
        upper = evidence.get(int(midi) + int(interval))
        if upper is None:
            continue
        if upper["attack"] <= POSITIVE_ATTACK_FLOOR or upper["body"] <= POSITIVE_BODY_FLOOR:
            continue
        score += float(weight) * max(0.0, min(float(base["score"]), float(upper["score"])))
    return float(score)


def _precision_pitch_set(row: Mapping[str, Any]) -> tuple[tuple[int, ...], bool, int]:
    original = _candidate_midis(row)
    if not original:
        raise ValueError("Precision pitch selection requires an observed candidate pitch")
    evidence = {midi: _pitch_evidence(row, midi) for midi in original}
    positive = {
        midi: item
        for midi, item in evidence.items()
        if item["attack"] > POSITIVE_ATTACK_FLOOR and item["body"] > POSITIVE_BODY_FLOOR
    }
    if not positive:
        strongest = max(
            original,
            key=lambda midi: (evidence[midi]["score"], evidence[midi]["attack"], -midi),
        )
        return original, False, int(strongest)

    strongest_raw_midi = max(
        positive,
        key=lambda midi: (positive[midi]["score"], positive[midi]["attack"], -midi),
    )
    strongest_raw = positive[strongest_raw_midi]
    strongest_score = max(1e-6, float(strongest_raw["score"]))
    family_scores = {midi: _harmonic_family_score(midi, positive) for midi in positive}
    primary = max(
        family_scores,
        key=lambda midi: (family_scores[midi], positive[midi]["attack"], -midi),
    )

    # A lower fundamental may replace a stronger overtone only when the lower
    # candidate is itself physically present at substantial strength. This is a
    # general harmonic-family correction, not a song/key/chord rule.
    if float(positive[primary]["score"]) < FUNDAMENTAL_MIN_RAW_RATIO * strongest_score:
        primary = strongest_raw_midi

    kept = {int(primary)}
    for midi, item in sorted(
        positive.items(),
        key=lambda pair: (pair[1]["score"], pair[1]["attack"], -pair[0]),
        reverse=True,
    ):
        if midi == primary:
            continue
        is_harmonic_above_primary = int(midi) - int(primary) in HARMONIC_INTERVAL_WEIGHTS
        ratio_floor = HARMONIC_SECONDARY_RAW_RATIO if is_harmonic_above_primary else SECONDARY_RAW_RATIO
        if float(item["score"]) < ratio_floor * strongest_score:
            continue
        if float(item["attack"]) < ratio_floor * max(1e-6, float(strongest_raw["attack"])):
            continue
        if float(item["body"]) < ratio_floor * max(1e-6, float(strongest_raw["body"])):
            continue
        kept.add(int(midi))

    promoted = int(primary) != int(strongest_raw_midi)
    return tuple(sorted(kept)), promoted, int(primary)


def apply_reference_free_precision_shadow(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    correction: ShadowCorrectionResult,
    target_measures: Iterable[int],
) -> PrecisionShadowResult:
    """Prune attack/harmonic inflation using only physical two-view evidence.

    This stage is intentionally post-correction and research-only. It may remove
    corrected attacks, but it cannot add or relocate an attack. A retained pitch
    must already exist in the physical carrier row. Attack precision is based on
    transient-vs-body evidence plus a narrow local-prominence exception. Pitch
    precision ranks observed lower candidates with physically supported upper
    harmonic families, then requires strong independent evidence for additional
    chord tones. The selected primary pitch is explicitly preserved so a later
    guitar-voicing adapter cannot silently replace a promoted fundamental with a
    stronger overtone. No key, chord name, song section, reference label, or target
    event count is accepted by the function.
    """
    if not isinstance(correction, ShadowCorrectionResult):
        raise TypeError("correction must be ShadowCorrectionResult")
    input_events = set(correction.corrected_events)
    if not input_events:
        raise ValueError("correction contains no events")
    targets = {int(value) for value in target_measures}
    if not targets:
        raise ValueError("target_measures cannot be empty")

    rows_by_slot = _best_rows_by_slot(carrier_rows, grid)
    eligible = {key for key in input_events if key in rows_by_slot and key[0] in targets}
    retained = {
        key
        for key in eligible
        if _attack_is_precise(key, rows_by_slot[key], rows_by_slot, eligible)
    }

    fail_safe: set[EventKey] = set()
    for measure in sorted(targets):
        measure_inputs = sorted(key for key in eligible if key[0] == measure)
        if not measure_inputs or any(key in retained for key in measure_inputs):
            continue
        winner = max(
            measure_inputs,
            key=lambda key: (
                _transient_ratio(_best_evidence(rows_by_slot[key])[1]),
                float(rows_by_slot[key].get("_precisionStrength") or -99.0),
                -int(key[1]),
            ),
        )
        retained.add(winner)
        fail_safe.add(winner)

    original_pitch_sets: dict[EventKey, tuple[int, ...]] = {}
    pitch_sets: dict[EventKey, tuple[int, ...]] = {}
    primary_midis: dict[EventKey, int] = {}
    promoted_count = 0
    suppressed = 0
    for key in sorted(retained):
        row = rows_by_slot[key]
        original = _candidate_midis(row)
        if not original:
            retained.remove(key)
            fail_safe.discard(key)
            continue
        selected, promoted, primary = _precision_pitch_set(row)
        if not selected:
            selected = original
        if int(primary) not in set(selected):
            raise RuntimeError(f"Precision primary escaped retained pitch set at {key}")
        original_pitch_sets[key] = original
        pitch_sets[key] = selected
        primary_midis[key] = int(primary)
        promoted_count += int(promoted)
        suppressed += max(0, len(original) - len(selected))

    retained_measures = {measure for measure, _step in retained}
    missing = targets - retained_measures
    if missing:
        for measure in sorted(missing):
            candidates = [key for key in eligible if key[0] == measure and _candidate_midis(rows_by_slot[key])]
            if not candidates:
                raise RuntimeError(f"No observed pitched corrected event can preserve measure {measure}")
            winner = max(
                candidates,
                key=lambda key: (
                    _transient_ratio(_best_evidence(rows_by_slot[key])[1]),
                    float(rows_by_slot[key].get("_precisionStrength") or -99.0),
                    -int(key[1]),
                ),
            )
            retained.add(winner)
            fail_safe.add(winner)
            original = _candidate_midis(rows_by_slot[winner])
            selected, promoted, primary = _precision_pitch_set(rows_by_slot[winner])
            selected = selected or original
            if int(primary) not in set(selected):
                raise RuntimeError(f"Precision fail-safe primary escaped pitch set at {winner}")
            original_pitch_sets[winner] = original
            pitch_sets[winner] = selected
            primary_midis[winner] = int(primary)
            promoted_count += int(promoted)
            suppressed += max(0, len(original) - len(selected))

    pruned = input_events - retained
    if not retained.issubset(input_events):
        raise RuntimeError("Precision shadow added an attack")
    if set(primary_midis) != set(retained):
        raise RuntimeError("Precision shadow did not preserve one explicit primary per retained attack")
    for key, selected in pitch_sets.items():
        observed = set(_candidate_midis(rows_by_slot[key]))
        if not set(selected).issubset(observed):
            raise RuntimeError(f"Precision shadow invented pitch at {key}")
        if int(primary_midis[key]) not in set(selected):
            raise RuntimeError(f"Precision primary is not retained at {key}")

    return PrecisionShadowResult(
        input_events=frozenset(input_events),
        retained_events=frozenset(retained),
        pruned_events=frozenset(pruned),
        original_pitch_sets=original_pitch_sets,
        pitch_sets=pitch_sets,
        primary_midis=primary_midis,
        fail_safe_events=frozenset(fail_safe),
        fundamental_promotions=int(promoted_count),
        suppressed_pitch_count=int(suppressed),
    )


__all__ = [
    "ATTACK_TRANSIENT_RATIO_FLOOR",
    "ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR",
    "SECONDARY_RAW_RATIO",
    "HARMONIC_SECONDARY_RAW_RATIO",
    "HARMONIC_INTERVAL_WEIGHTS",
    "PrecisionShadowResult",
    "apply_reference_free_precision_shadow",
]
