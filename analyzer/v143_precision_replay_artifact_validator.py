from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

EXPECTED_POLICY = "envelope-balanced-secondary-v2"
EXPECTED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EVIDENCE_FIELDS = ("attack", "early", "sustain", "body", "continuity", "score")
VIEW_FIELDS = ("attack", "early", "sustain")
ATTACK_TRANSIENT_RATIO_FLOOR = 0.70
ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR = 0.60
LOCAL_STRENGTH_MARGIN = 0.20
LOCAL_RADIUS_STEPS = 2
POSITIVE_ATTACK_FLOOR = 0.0
POSITIVE_BODY_FLOOR = -0.25


class ReplayArtifactValidationError(ValueError):
    pass


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ReplayArtifactValidationError(f"{label} is not numeric") from exc
    if not math.isfinite(number):
        raise ReplayArtifactValidationError(f"{label} is not finite")
    return number


def _int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise ReplayArtifactValidationError(f"{label} is boolean, not integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ReplayArtifactValidationError(f"{label} is not integer-like") from exc


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayArtifactValidationError(message)


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _key_record(value: Mapping[str, Any], label: str) -> tuple[int, int]:
    return (_int(value.get("measure"), f"{label}.measure"), _int(value.get("step"), f"{label}.step"))


def _candidate_values(item: Mapping[str, Any], label: str) -> dict[str, float]:
    values = {field: _finite(item.get(field), f"{label}.{field}") for field in EVIDENCE_FIELDS}
    views: dict[str, dict[str, float]] = {}
    for view_name in ("viewA", "viewB"):
        raw_view = item.get(view_name)
        _require(isinstance(raw_view, Mapping), f"{label}.{view_name} is not a mapping")
        views[view_name] = {
            field: _finite(raw_view.get(field), f"{label}.{view_name}.{field}")
            for field in VIEW_FIELDS
        }

    expected_attack = min(views["viewA"]["attack"], views["viewB"]["attack"])
    expected_early = min(views["viewA"]["early"], views["viewB"]["early"])
    expected_sustain = min(views["viewA"]["sustain"], views["viewB"]["sustain"])
    _require(math.isclose(values["attack"], expected_attack, rel_tol=0.0, abs_tol=1e-12), f"{label} attack does not match two-view minimum")
    _require(math.isclose(values["early"], expected_early, rel_tol=0.0, abs_tol=1e-12), f"{label} early does not match two-view minimum")
    _require(math.isclose(values["sustain"], expected_sustain, rel_tol=0.0, abs_tol=1e-12), f"{label} sustain does not match two-view minimum")
    _require(math.isclose(values["body"], max(values["early"], values["sustain"]), rel_tol=0.0, abs_tol=1e-12), f"{label} body is not max(early,sustain)")
    _require(math.isclose(values["continuity"], min(values["early"], values["sustain"]), rel_tol=0.0, abs_tol=1e-12), f"{label} continuity is not min(early,sustain)")
    expected_score = values["attack"] + 0.65 * values["body"] + 0.15 * values["continuity"]
    _require(math.isclose(values["score"], expected_score, rel_tol=0.0, abs_tol=1e-10), f"{label} score formula mismatch")
    return values


def _validate_attack_record(
    attack: Mapping[str, Any],
    *,
    label: str,
    require_retained: bool | None,
) -> tuple[tuple[int, int], set[int], set[int], int | None]:
    key = _key_record(attack, label)
    grid_time = _finite(attack.get("gridTime"), f"{label}.gridTime")
    onset_time = _finite(attack.get("onsetTime"), f"{label}.onsetTime")
    precision_strength = _finite(attack.get("precisionStrength"), f"{label}.precisionStrength")
    grid_error = _finite(attack.get("precisionGridErrorSeconds"), f"{label}.precisionGridErrorSeconds")
    _finite(attack.get("candidateStrength"), f"{label}.candidateStrength")
    stem_support = _int(attack.get("stemSupportMax"), f"{label}.stemSupportMax")
    sweep_support = _int(attack.get("sweepSupportMax"), f"{label}.sweepSupportMax")
    detection_count = _int(attack.get("detectionCountSum"), f"{label}.detectionCountSum")
    _require(grid_error >= 0.0, f"{label}.precisionGridErrorSeconds is negative")
    _require(math.isclose(grid_error, abs(onset_time - grid_time), rel_tol=0.0, abs_tol=1e-10), f"{label} grid error does not match onset/grid time")
    _require(isinstance(attack.get("retained"), bool), f"{label}.retained is not boolean")
    _require(isinstance(attack.get("failSafe"), bool), f"{label}.failSafe is not boolean")
    retained = attack.get("retained") is True
    if require_retained is not None:
        _require(retained is require_retained, f"{label}.retained flag mismatch")
    if attack.get("failSafe") is True:
        _require(retained, f"{label} marks a pruned attack as fail-safe")

    candidate_midis_raw = attack.get("candidateMidis") or []
    candidates = attack.get("candidates") or []
    _require(isinstance(candidate_midis_raw, Sequence) and not isinstance(candidate_midis_raw, (str, bytes, bytearray)), f"{label}.candidateMidis is not a sequence")
    _require(isinstance(candidates, Sequence) and not isinstance(candidates, (str, bytes, bytearray)), f"{label}.candidates is not a sequence")

    candidate_midis = [_int(value, f"{label}.candidateMidi") for value in candidate_midis_raw]
    candidate_records: list[int] = []
    selected: set[int] = set()
    primaries: list[int] = []
    strongest_score = -99.0
    for index, item in enumerate(candidates):
        _require(isinstance(item, Mapping), f"{label}.candidates[{index}] is not a mapping")
        midi = _int(item.get("midi"), f"{label}.candidates[{index}].midi")
        candidate_records.append(midi)
        values = _candidate_values(item, f"{label}.MIDI{midi}")
        strongest_score = max(strongest_score, values["score"])
        _require(isinstance(item.get("selected"), bool), f"{label}.MIDI{midi}.selected is not boolean")
        _require(isinstance(item.get("primary"), bool), f"{label}.MIDI{midi}.primary is not boolean")
        if item.get("selected") is True:
            selected.add(midi)
        if item.get("primary") is True:
            primaries.append(midi)

    _require(candidate_midis == candidate_records, f"{label} candidate identity/order mismatch")
    _require(len(candidate_records) == len(set(candidate_records)), f"{label} contains duplicate MIDI")
    expected_strength = (
        strongest_score
        + 0.10 * min(4, max(0, sweep_support))
        + 0.03 * min(16, max(0, detection_count))
        - 2.0 * grid_error
    )
    _require(math.isclose(precision_strength, expected_strength, rel_tol=0.0, abs_tol=1e-10), f"{label} precisionStrength cannot be recomputed from persisted source evidence")
    _require(stem_support == int(stem_support), f"{label}.stemSupportMax invalid")

    if retained:
        _require(len(candidate_records) > 0, f"{label} retained attack has no pitch hypotheses")
        _require(len(primaries) == 1, f"{label} retained attack must contain exactly one primary")
        _require(primaries[0] in selected, f"{label} retained primary is not selected")
        _require(selected, f"{label} retained attack has no selected pitch")
    else:
        _require(not selected, f"{label} pruned attack contains a selected pitch")
        _require(not primaries, f"{label} pruned attack contains a primary")

    return key, set(candidate_records), selected, (primaries[0] if primaries else None)


def _candidate_map(attack: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    return {int(item["midi"]): item for item in (attack.get("candidates") or [])}


def _best_candidate(attack: Mapping[str, Any]) -> Mapping[str, Any] | None:
    candidates = _candidate_map(attack)
    if not candidates:
        return None
    midi = max(candidates, key=lambda value: (float(candidates[value]["score"]), float(candidates[value]["attack"]), -int(value)))
    return candidates[midi]


def _transient_ratio(attack: Mapping[str, Any]) -> float:
    item = _best_candidate(attack)
    if item is None:
        return 0.0
    return float(max(0.0, float(item["attack"])) / max(1e-6, float(item["body"])))


def _attack_is_precise(
    key: tuple[int, int],
    attack: Mapping[str, Any],
    eligible: Mapping[tuple[int, int], Mapping[str, Any]],
) -> bool:
    item = _best_candidate(attack)
    if item is None:
        return False
    if float(item["attack"]) <= POSITIVE_ATTACK_FLOOR or float(item["body"]) <= POSITIVE_BODY_FLOOR:
        return False
    ratio = _transient_ratio(attack)
    if ratio >= ATTACK_TRANSIENT_RATIO_FLOOR:
        return True
    if ratio < ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR:
        return False
    strength = float(attack["precisionStrength"])
    neighbors = [
        float(other["precisionStrength"])
        for other_key, other in eligible.items()
        if other_key != key and other_key[0] == key[0] and abs(int(other_key[1]) - int(key[1])) <= LOCAL_RADIUS_STEPS
    ]
    if not neighbors:
        return True
    return strength >= max(neighbors) + LOCAL_STRENGTH_MARGIN


def _recompute_attack_policy(
    eligible: Mapping[tuple[int, int], Mapping[str, Any]],
    target_measures: set[int],
) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    scoped = {key: attack for key, attack in eligible.items() if key[0] in target_measures}
    retained = {key for key, attack in scoped.items() if _attack_is_precise(key, attack, scoped)}
    fail_safe: set[tuple[int, int]] = set()
    for measure in sorted(target_measures):
        measure_inputs = sorted(key for key in scoped if key[0] == measure)
        if not measure_inputs or any(key in retained for key in measure_inputs):
            continue
        winner = max(measure_inputs, key=lambda key: (_transient_ratio(scoped[key]), float(scoped[key]["precisionStrength"]), -int(key[1])))
        retained.add(winner)
        fail_safe.add(winner)
    for key in list(retained):
        if not (scoped[key].get("candidateMidis") or []):
            retained.remove(key)
            fail_safe.discard(key)
    retained_measures = {measure for measure, _step in retained}
    for measure in sorted(target_measures - retained_measures):
        candidates = [key for key in scoped if key[0] == measure and (scoped[key].get("candidateMidis") or [])]
        _require(bool(candidates), f"no pitched eligible attack can preserve measure {measure}")
        winner = max(candidates, key=lambda key: (_transient_ratio(scoped[key]), float(scoped[key]["precisionStrength"]), -int(key[1])))
        retained.add(winner)
        fail_safe.add(winner)
    return retained, fail_safe


def validate_product(product: Mapping[str, Any]) -> dict[str, Any]:
    candidate = product.get("candidate") or {}
    replay = product.get("precisionReplayEvidence") or {}
    precision = product.get("precisionDiagnostics") or {}
    diagnostics = product.get("candidateDiagnostics") or {}
    assembly = product.get("assembly") or {}
    timing = product.get("timing") or {}
    events = product.get("events") or []

    _require(isinstance(candidate, Mapping), "candidate metadata missing")
    _require(isinstance(replay, Mapping), "precisionReplayEvidence missing")
    _require(isinstance(precision, Mapping), "precisionDiagnostics missing")
    _require(isinstance(diagnostics, Mapping), "candidateDiagnostics missing")
    _require(isinstance(assembly, Mapping), "assembly metadata missing")
    _require(isinstance(timing, Mapping), "timing metadata missing")
    _require(isinstance(events, Sequence) and not isinstance(events, (str, bytes, bytearray)), "events must be a sequence")

    _require(candidate.get("approvedFixture") is True, "candidate is not approved fixture")
    _require(candidate.get("sourceSha256") == EXPECTED_AUDIO_SHA256, "approved fixture SHA mismatch")
    _require(candidate.get("professionalReferenceUsed") is False, "candidate indicates professional reference use")
    _require(candidate.get("runtimeLabelsRequired") is False, "candidate requires runtime labels")
    _require(candidate.get("productionModified") is False, "candidate indicates production mutation")

    _require(replay.get("schemaVersion") == 2, "unexpected replay schemaVersion")
    _require(replay.get("policy") == EXPECTED_POLICY, "unexpected replay policy")
    _require(replay.get("replayCompleteness") == "retained-pitch-plus-eligible-attack-source-universe", "unexpected replay completeness mode")
    _require(replay.get("fixedRetainedAttackPitchReplayReady") is True, "fixed retained-attack replay is not ready")
    _require(replay.get("attackPolicyReplayReady") is True, "attack-policy replay is not ready")
    _require(replay.get("sourceViewEvidenceReady") is True, "per-view source replay is not ready")
    _require(replay.get("precisionStrengthRecomputeReady") is True, "precision-strength replay is not ready")
    _require(replay.get("referenceFree") is True, "replay is not reference-free")
    _require(replay.get("professionalReferenceUsed") is False, "replay indicates professional reference use")
    _require(replay.get("runtimeLabelsRequired") is False, "replay requires runtime labels")
    _require(replay.get("productionModified") is False, "replay indicates production mutation")
    _require(replay.get("candidateAddsUnobservedAttack") is False, "replay says attack was invented")
    _require(replay.get("candidateAddsUnobservedPitch") is False, "replay says pitch was invented")

    input_key_records = replay.get("inputAttackKeys") or []
    missing_key_records = replay.get("carrierMissingInputAttackKeys") or []
    eligible_attacks = replay.get("eligibleAttacks") or []
    retained_attacks = replay.get("attacks") or []
    for name, value in (("inputAttackKeys", input_key_records), ("carrierMissingInputAttackKeys", missing_key_records), ("eligibleAttacks", eligible_attacks), ("attacks", retained_attacks)):
        _require(isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)), f"replay.{name} must be a sequence")

    input_keys_list = [_key_record(item, f"inputAttackKeys[{index}]") for index, item in enumerate(input_key_records)]
    missing_keys_list = [_key_record(item, f"carrierMissingInputAttackKeys[{index}]") for index, item in enumerate(missing_key_records)]
    _require(len(input_keys_list) == len(set(input_keys_list)), "duplicate input attack key")
    _require(len(missing_keys_list) == len(set(missing_keys_list)), "duplicate carrier-missing input key")
    _require(input_keys_list == sorted(input_keys_list), "input attack keys are not canonical-sorted")
    _require(missing_keys_list == sorted(missing_keys_list), "carrier-missing input keys are not canonical-sorted")

    eligible_by_key: dict[tuple[int, int], Mapping[str, Any]] = {}
    eligible_candidate_count = 0
    eligible_selected_count = 0
    stored_fail_safe: set[tuple[int, int]] = set()
    eligible_key_order: list[tuple[int, int]] = []
    for index, attack in enumerate(eligible_attacks):
        _require(isinstance(attack, Mapping), f"eligibleAttacks[{index}] is not a mapping")
        key, candidates, selected, _primary = _validate_attack_record(attack, label=f"eligibleAttacks[{index}]", require_retained=None)
        _require(key not in eligible_by_key, f"duplicate eligible replay attack {key}")
        eligible_by_key[key] = attack
        eligible_key_order.append(key)
        eligible_candidate_count += len(candidates)
        eligible_selected_count += len(selected)
        if attack.get("failSafe") is True:
            stored_fail_safe.add(key)

    retained_by_key: dict[tuple[int, int], Mapping[str, Any]] = {}
    retained_candidates: dict[tuple[int, int], set[int]] = {}
    retained_selected: dict[tuple[int, int], set[int]] = {}
    retained_candidate_count = 0
    retained_selected_count = 0
    retained_key_order: list[tuple[int, int]] = []
    for index, attack in enumerate(retained_attacks):
        _require(isinstance(attack, Mapping), f"attacks[{index}] is not a mapping")
        key, candidates, selected, _primary = _validate_attack_record(attack, label=f"attacks[{index}]", require_retained=True)
        _require(key not in retained_by_key, f"duplicate retained replay attack {key}")
        retained_by_key[key] = attack
        retained_candidates[key] = candidates
        retained_selected[key] = selected
        retained_key_order.append(key)
        retained_candidate_count += len(candidates)
        retained_selected_count += len(selected)

    eligible_keys = set(eligible_by_key)
    retained_keys = set(retained_by_key)
    input_keys = set(input_keys_list)
    missing_keys = set(missing_keys_list)
    _require(eligible_keys.isdisjoint(missing_keys), "eligible and carrier-missing attack keys overlap")
    _require(input_keys == eligible_keys | missing_keys, "input attack universe does not reconcile with eligible+missing keys")
    _require(retained_keys.issubset(eligible_keys), "retained attack is absent from eligible source universe")
    _require(eligible_key_order == sorted(eligible_keys), "eligible attacks are not canonical-sorted")
    _require(retained_key_order == sorted(retained_keys), "retained attacks are not canonical-sorted")
    for key in retained_keys:
        _require(dict(retained_by_key[key]) == dict(eligible_by_key[key]), f"retained attack {key} differs from eligible source record")
    for key, attack in eligible_by_key.items():
        _require((attack.get("retained") is True) == (key in retained_keys), f"eligible retained flag disagrees at {key}")

    _require(len(input_keys) == _int(replay.get("inputAttackCount"), "replay.inputAttackCount"), "replay input attack count mismatch")
    _require(len(eligible_keys) == _int(replay.get("eligibleAttackCount"), "replay.eligibleAttackCount"), "replay eligible attack count mismatch")
    _require(len(retained_keys) == _int(replay.get("retainedAttackCount"), "replay.retainedAttackCount"), "replay retained attack count mismatch")
    _require(len(input_keys - retained_keys) == _int(replay.get("prunedAttackCount"), "replay.prunedAttackCount"), "replay pruned attack count mismatch")
    _require(eligible_candidate_count == _int(replay.get("eligiblePitchHypothesisCount"), "replay.eligiblePitchHypothesisCount"), "eligible pitch hypothesis count mismatch")
    _require(retained_candidate_count == _int(replay.get("originalPitchHypothesisCount"), "replay.originalPitchHypothesisCount"), "retained original pitch count mismatch")
    _require(retained_candidate_count == _int(replay.get("retainedOriginalPitchHypothesisCount"), "replay.retainedOriginalPitchHypothesisCount"), "retainedOriginalPitchHypothesisCount mismatch")

    _require(_int(precision.get("inputAttackCount"), "precision.inputAttackCount") == len(input_keys), "precision/replay input attack count mismatch")
    _require(_int(precision.get("retainedAttackCount"), "precision.retainedAttackCount") == len(retained_keys), "precision/replay retained attack count mismatch")
    _require(_int(precision.get("prunedAttackCount"), "precision.prunedAttackCount") == len(input_keys - retained_keys), "precision/replay pruned attack count mismatch")
    _require(_int(precision.get("failSafeAttackCount"), "precision.failSafeAttackCount") == len(stored_fail_safe), "precision/replay fail-safe count mismatch")
    _require(_int(precision.get("originalPitchHypothesisCount"), "precision.originalPitchHypothesisCount") == retained_candidate_count, "precision/replay original pitch count mismatch")
    _require(_int(precision.get("retainedPitchHypothesisCount"), "precision.retainedPitchHypothesisCount") == retained_selected_count, "precision/replay selected pitch count mismatch")
    _require(eligible_selected_count == retained_selected_count, "pruned eligible attacks unexpectedly contribute selected pitches")

    measure_start = _int(timing.get("measureStart"), "timing.measureStart")
    measure_end = _int(timing.get("measureEnd"), "timing.measureEnd")
    _require(measure_start <= measure_end, "timing measure range is inverted")
    target_measures = set(range(measure_start, measure_end + 1))
    _require(all(key[0] in target_measures for key in eligible_keys), "eligible attack lies outside audio-derived measure range")
    recomputed_retained, recomputed_fail_safe = _recompute_attack_policy(eligible_by_key, target_measures)
    _require(recomputed_retained == retained_keys, "baseline attack replay does not reproduce retained attack identity")
    _require(recomputed_fail_safe == stored_fail_safe, "baseline attack replay does not reproduce fail-safe identity")

    event_keys: set[tuple[int, int]] = set()
    for index, event in enumerate(events):
        _require(isinstance(event, Mapping), f"event[{index}] is not a mapping")
        key = _key_record(event, f"event[{index}]")
        midi = _int(event.get("midi"), f"event[{index}].midi")
        _require(key in retained_candidates, f"render emitted attack absent from retained replay: {key}")
        _require(midi in retained_candidates[key], f"render emitted unobserved pitch {midi} at {key}")
        _require(midi in retained_selected[key], f"render emitted replay-unselected pitch {midi} at {key}")
        event_keys.add(key)

    _require(event_keys == retained_keys, "render/replay retained attack identity mismatch")
    _require(len(events) == _int(product.get("noteCount"), "product.noteCount"), "noteCount does not match events length")
    _require(len(retained_keys) == _int(product.get("selectedCount"), "product.selectedCount"), "selectedCount does not match retained replay attacks")
    _require(len(retained_keys) == _int(assembly.get("selectedAttackCount"), "assembly.selectedAttackCount"), "assembly selected attack count mismatch")
    _require(len(events) == _int(assembly.get("renderNoteCount"), "assembly.renderNoteCount"), "assembly render note count mismatch")

    supported_pitch_count = _int(diagnostics.get("supportedPitchCount"), "candidateDiagnostics.supportedPitchCount")
    rendered_pitch_count = _int(diagnostics.get("renderedPitchCount"), "candidateDiagnostics.renderedPitchCount")
    rendered_note_count = _int(diagnostics.get("renderedNoteCount"), "candidateDiagnostics.renderedNoteCount")
    dropped_pitch_count = _int(diagnostics.get("voicingDroppedPitchCount"), "candidateDiagnostics.voicingDroppedPitchCount")
    _require(diagnostics.get("everyCorrectedAttackRendered") is True, "candidate did not render every retained attack")
    _require(supported_pitch_count == retained_selected_count, "candidate supported pitch count does not match replay selected total")
    _require(rendered_pitch_count == len(events), "candidate rendered pitch count mismatch")
    _require(rendered_note_count == len(events), "candidate rendered note count mismatch")
    _require(dropped_pitch_count == retained_selected_count - len(events), "candidate voicing drop accounting mismatch")
    _require(dropped_pitch_count >= 0, "candidate voicing drop count is negative")

    replay_measures = {measure for measure, _step in retained_keys}
    _require(replay_measures == target_measures, "retained replay does not cover exact audio-derived measure range")
    _require(len(target_measures) == _int(product.get("audioDerivedMeasureCount"), "product.audioDerivedMeasureCount"), "audioDerivedMeasureCount mismatch")

    return {
        "schemaVersion": 2,
        "classification": "v143-precision-replay-artifact-exact-binding",
        "passed": True,
        "policy": EXPECTED_POLICY,
        "inputAttackCount": len(input_keys),
        "eligibleAttackCount": len(eligible_keys),
        "carrierMissingInputAttackCount": len(missing_keys),
        "retainedAttackCount": len(retained_keys),
        "prunedAttackCount": len(input_keys - retained_keys),
        "failSafeAttackCount": len(stored_fail_safe),
        "eligiblePitchHypothesisCount": eligible_candidate_count,
        "originalPitchHypothesisCount": retained_candidate_count,
        "storedSelectedPitchCount": retained_selected_count,
        "renderedPitchCount": len(events),
        "voicingDroppedPitchCount": dropped_pitch_count,
        "measureStart": measure_start,
        "measureEnd": measure_end,
        "baselineAttackReplayMatches": True,
        "sourceViewEvidenceMatches": True,
        "precisionStrengthRecomputeMatches": True,
        "fixedRetainedAttackPitchReplayReady": True,
        "attackPolicyReplayReady": True,
        "replayEvidenceSha256": _canonical_sha256(replay),
        "eventsSha256": _canonical_sha256(events),
        "referenceFree": True,
        "newInferenceUsed": False,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def _candidate(midi: int, attack: float, early: float, sustain: float, *, selected: bool, primary: bool) -> dict[str, Any]:
    body = max(early, sustain)
    continuity = min(early, sustain)
    return {
        "midi": midi,
        "attack": attack,
        "early": early,
        "sustain": sustain,
        "body": body,
        "continuity": continuity,
        "score": attack + 0.65 * body + 0.15 * continuity,
        "viewA": {"attack": attack, "early": early, "sustain": sustain},
        "viewB": {"attack": attack, "early": early, "sustain": sustain},
        "selected": selected,
        "primary": primary,
    }


def _attack_record(measure: int, step: int, candidates: list[dict[str, Any]], *, retained: bool, fail_safe: bool) -> dict[str, Any]:
    grid_time = float(measure)
    onset_time = grid_time + 0.01 * (step + 1)
    grid_error = abs(onset_time - grid_time)
    sweep_support = 0
    detection_count = 0
    strongest_score = max((float(item["score"]) for item in candidates), default=-99.0)
    precision_strength = strongest_score + 0.10 * min(4, sweep_support) + 0.03 * min(16, detection_count) - 2.0 * grid_error
    return {
        "measure": measure,
        "step": step,
        "gridTime": grid_time,
        "onsetTime": onset_time,
        "precisionStrength": precision_strength,
        "precisionGridErrorSeconds": grid_error,
        "candidateStrength": 0.0,
        "stemSupportMax": 0,
        "sweepSupportMax": sweep_support,
        "detectionCountSum": detection_count,
        "retained": retained,
        "failSafe": fail_safe,
        "candidateMidis": [int(item["midi"]) for item in candidates],
        "candidates": candidates,
    }


def _self_test_product() -> dict[str, Any]:
    strong = _attack_record(1, 0, [_candidate(60, 1.0, 0.8, 0.6, selected=True, primary=True), _candidate(64, 0.9, 0.7, 0.5, selected=True, primary=False)], retained=True, fail_safe=False)
    weak_pruned = _attack_record(1, 1, [_candidate(62, 0.3, 0.8, 0.7, selected=False, primary=False)], retained=False, fail_safe=False)
    weak_fail_safe = _attack_record(2, 0, [_candidate(65, 0.25, 0.8, 0.7, selected=True, primary=True)], retained=True, fail_safe=True)
    retained = [strong, weak_fail_safe]
    eligible = [strong, weak_pruned, weak_fail_safe]
    return {
        "candidate": {"approvedFixture": True, "sourceSha256": EXPECTED_AUDIO_SHA256, "professionalReferenceUsed": False, "runtimeLabelsRequired": False, "productionModified": False},
        "precisionReplayEvidence": {
            "schemaVersion": 2,
            "policy": EXPECTED_POLICY,
            "replayCompleteness": "retained-pitch-plus-eligible-attack-source-universe",
            "inputAttackCount": 3,
            "eligibleAttackCount": 3,
            "retainedAttackCount": 2,
            "prunedAttackCount": 1,
            "originalPitchHypothesisCount": 3,
            "retainedOriginalPitchHypothesisCount": 3,
            "eligiblePitchHypothesisCount": 4,
            "inputAttackKeys": [{"measure": 1, "step": 0}, {"measure": 1, "step": 1}, {"measure": 2, "step": 0}],
            "carrierMissingInputAttackKeys": [],
            "attacks": retained,
            "eligibleAttacks": eligible,
            "fixedRetainedAttackPitchReplayReady": True,
            "attackPolicyReplayReady": True,
            "sourceViewEvidenceReady": True,
            "precisionStrengthRecomputeReady": True,
            "candidateAddsUnobservedAttack": False,
            "candidateAddsUnobservedPitch": False,
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        },
        "precisionDiagnostics": {"inputAttackCount": 3, "retainedAttackCount": 2, "prunedAttackCount": 1, "failSafeAttackCount": 1, "originalPitchHypothesisCount": 3, "retainedPitchHypothesisCount": 3},
        "candidateDiagnostics": {"supportedPitchCount": 3, "renderedPitchCount": 2, "renderedNoteCount": 2, "voicingDroppedPitchCount": 1, "everyCorrectedAttackRendered": True},
        "assembly": {"selectedAttackCount": 2, "renderNoteCount": 2},
        "timing": {"measureStart": 1, "measureEnd": 2},
        "events": [{"measure": 1, "step": 0, "midi": 60}, {"measure": 2, "step": 0, "midi": 65}],
        "noteCount": 2,
        "selectedCount": 2,
        "audioDerivedMeasureCount": 2,
    }


def _self_test() -> None:
    from v143_contextual_prune_precision_shadow import (
        ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR as ACTUAL_ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR,
        ATTACK_TRANSIENT_RATIO_FLOOR as ACTUAL_ATTACK_TRANSIENT_RATIO_FLOOR,
        LOCAL_RADIUS_STEPS as ACTUAL_LOCAL_RADIUS_STEPS,
        LOCAL_STRENGTH_MARGIN as ACTUAL_LOCAL_STRENGTH_MARGIN,
        POSITIVE_ATTACK_FLOOR as ACTUAL_POSITIVE_ATTACK_FLOOR,
        POSITIVE_BODY_FLOOR as ACTUAL_POSITIVE_BODY_FLOOR,
    )

    assert ATTACK_TRANSIENT_RATIO_FLOOR == ACTUAL_ATTACK_TRANSIENT_RATIO_FLOOR
    assert ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR == ACTUAL_ATTACK_TRANSIENT_RATIO_EXCEPTION_FLOOR
    assert LOCAL_STRENGTH_MARGIN == ACTUAL_LOCAL_STRENGTH_MARGIN
    assert LOCAL_RADIUS_STEPS == ACTUAL_LOCAL_RADIUS_STEPS
    assert POSITIVE_ATTACK_FLOOR == ACTUAL_POSITIVE_ATTACK_FLOOR
    assert POSITIVE_BODY_FLOOR == ACTUAL_POSITIVE_BODY_FLOOR

    product = _self_test_product()
    report = validate_product(product)
    assert report["passed"] is True
    assert report["baselineAttackReplayMatches"] is True
    assert report["sourceViewEvidenceMatches"] is True
    assert report["precisionStrengthRecomputeMatches"] is True
    assert report["eligibleAttackCount"] == 3
    assert report["retainedAttackCount"] == 2
    assert report["failSafeAttackCount"] == 1
    assert report["eligiblePitchHypothesisCount"] == 4
    assert report["originalPitchHypothesisCount"] == 3
    assert report["storedSelectedPitchCount"] == 3
    assert report["renderedPitchCount"] == 2
    assert report["voicingDroppedPitchCount"] == 1

    broken_pitch = json.loads(json.dumps(product))
    broken_pitch["events"][0]["midi"] = 67
    try:
        validate_product(broken_pitch)
    except ReplayArtifactValidationError:
        pass
    else:
        raise AssertionError("validator failed to reject an invented rendered pitch")

    broken_attack = json.loads(json.dumps(product))
    broken_attack["precisionReplayEvidence"]["eligibleAttacks"][1]["retained"] = True
    broken_attack["precisionReplayEvidence"]["eligibleAttacks"][1]["candidates"][0]["selected"] = True
    broken_attack["precisionReplayEvidence"]["eligibleAttacks"][1]["candidates"][0]["primary"] = True
    try:
        validate_product(broken_attack)
    except ReplayArtifactValidationError:
        pass
    else:
        raise AssertionError("validator failed to reject a corrupted retained-attack baseline")

    broken_view = json.loads(json.dumps(product))
    broken_view["precisionReplayEvidence"]["eligibleAttacks"][0]["candidates"][0]["viewA"]["attack"] += 0.1
    try:
        validate_product(broken_view)
    except ReplayArtifactValidationError:
        pass
    else:
        raise AssertionError("validator failed to reject corrupted per-view source evidence")

    print("PASS v143 precision replay schema2 source-complete exact-binding self-test")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return
    if not args.input or not args.output:
        raise SystemExit("--input and --output are required unless --self-test is used")
    product = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = validate_product(product)
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
