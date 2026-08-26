from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
MODAL_DIR = ROOT / "modal"
for entry in (HOLDOUT_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
import score_rhythm_holdout as scorer  # noqa: E402
from v144_rhythm_context_split_policy import ContextSplitConfig  # noqa: E402
from v144_rhythm_measure_set_guard import measure_set_evidence  # noqa: E402
from v144_rhythm_onset_dyad_pitch_policy import (  # noqa: E402
    DEFAULT_MAX_ABS_SEMITONE_SHIFT,
    DEFAULT_MAX_CANDIDATES,
    DEFAULT_MIN_CORRECTION_SUPPORT,
    apply_onset_dyad_pitch_rule,
    onset_matches_dyad_rule,
    rank_fit_onset_dyad_pitch_rules,
)
from v144_rhythm_pitch_position_shift_policy import apply_pitch_position_rule  # noqa: E402
from v144_rhythm_pitch_shift_policy import (  # noqa: E402
    OPEN_MIDI_BY_STRING_INDEX,
    apply_pitch_shift_rule,
)
from v144_rhythm_staged_selector import gate_locked_candidate, lock_fit_candidate  # noqa: E402
from v144_rhythm_triple_conjunction_policy import apply_triple_prune  # noqa: E402
from search_single_signature_prunes import (  # noqa: E402
    load_json,
    score_notes,
    stage_score_for_events,
    subset,
)
from score_selected_conjunction_candidate import score_full_candidate  # noqa: E402

SOURCE_EVENT_COUNT = 1209
SOURCE_EVENT_SHA256 = "7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1"
HISTORICAL_TRIPLE_SIGNATURES = ["register::high", "section16::1", "stepParity::0"]
HISTORICAL_TRIPLE_EVENT_COUNT = 1144
HISTORICAL_TRIPLE_EVENT_SHA256 = "68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3"
PITCH_BASELINE_SIGNATURES = ["pitchClass::4", "stepQuarter::0"]
PITCH_BASELINE_SHIFT = -2
PITCH_BASELINE_EVENT_SHA256 = "b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6"
ACCEPTED_BASELINE_NAME = "pitch-position-shift-54a6e8d3aa91c422"
ACCEPTED_POSITION_SIGNATURES = ["pitchClass::11", "stepParity::0"]
ACCEPTED_POSITION_PITCH_SHIFT = -2
ACCEPTED_POSITION_STRING_SHIFT = 1
ACCEPTED_EVENT_COUNT = 1144
ACCEPTED_EVENT_SHA256 = "5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d"
ACCEPTED_GENERATED_MEASURE_COUNT = 113


def _normalized_note_rules(note_rules: Sequence[Mapping[str, Any]]) -> tuple[tuple[int, int, int], ...]:
    if len(note_rules) != 2:
        raise ValueError("atomic dyad candidate requires exactly two note rules")
    normalized = tuple(
        sorted(
            (
                int(rule["stringIndex"]),
                int(rule["sourcePitchClass"]),
                int(rule["semitoneShift"]),
            )
            for rule in note_rules
        )
    )
    if normalized[0][0] == normalized[1][0]:
        raise ValueError("atomic dyad candidate requires two distinct strings")
    if any(not 0 <= pitch_class <= 11 for _, pitch_class, _ in normalized):
        raise ValueError("atomic dyad source pitch class outside [0,11]")
    if any(shift == 0 for _, _, shift in normalized):
        raise ValueError("atomic dyad candidate requires two non-zero shifts")
    return normalized


def candidate_name(context_signature_value: str, note_rules: Sequence[Mapping[str, Any]]) -> str:
    normalized = _normalized_note_rules(note_rules)
    token = str(context_signature_value) + "\n" + "\n".join(
        f"string::{string_index}|pitchClass::{pitch_class}|shift::{shift}"
        for string_index, pitch_class, shift in normalized
    )
    return "onset-dyad-pitch-" + hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]


def safety_payload(*, measure_preserved: bool, event_count_preserved: bool) -> dict[str, Any]:
    return {
        "v5Modified": False,
        "productionModified": False,
        "mainModified": False,
        "runtimeReferenceInputUsed": False,
        "modalGpuInvoked": False,
        "deterministic": True,
        "baselineGeneratedMeasureSetPreserved": bool(measure_preserved),
        "baselineEventCountPreserved": bool(event_count_preserved),
    }


def make_candidate(
    name: str,
    policy: str,
    fit: Mapping[str, Any],
    *,
    measure_preserved: bool,
    event_count_preserved: bool,
) -> dict[str, Any]:
    return {
        "name": name,
        "policy": policy,
        "fit": dict(fit),
        "holdout": None,
        "safety": safety_payload(
            measure_preserved=measure_preserved,
            event_count_preserved=event_count_preserved,
        ),
    }


def _validate_position(event: Mapping[str, Any]) -> tuple[int, int, int]:
    string_index = int(event["stringIndex"])
    fret = int(event["fret"])
    midi = int(event["midi"])
    if string_index not in OPEN_MIDI_BY_STRING_INDEX:
        raise ValueError("atomic dyad candidate has invalid string index")
    if not 0 <= fret <= 36:
        raise ValueError("atomic dyad candidate has invalid fret")
    if OPEN_MIDI_BY_STRING_INDEX[string_index] + fret != midi:
        raise ValueError("atomic dyad candidate violates tuning-derived pitch/fret identity")
    return string_index, fret, midi


def changed_event_count(
    baseline_events: Sequence[Mapping[str, Any]],
    candidate_events: Sequence[Mapping[str, Any]],
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
    expected_context_signature: str | None = None,
    expected_note_rules: Sequence[Mapping[str, Any]] | None = None,
) -> int:
    """Count changed events while proving atomic two-event dyad invariants."""
    maximum = int(maximum_abs_semitone_shift)
    if maximum < 1 or maximum > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")
    if (expected_context_signature is None) != (expected_note_rules is None):
        raise ValueError("expected context and note rules must be supplied together")
    normalized_expected = None
    if expected_note_rules is not None:
        normalized_expected = _normalized_note_rules(expected_note_rules)
        if any(abs(shift) > maximum for _, _, shift in normalized_expected):
            raise ValueError("expected dyad shift exceeds preregistered bound")

    if len(baseline_events) != len(candidate_events):
        raise ValueError("atomic dyad candidate changed event count")

    changed_by_onset: dict[tuple[int, int], list[int]] = defaultdict(list)
    baseline_by_onset: dict[tuple[int, int], list[Mapping[str, Any]]] = defaultdict(list)
    mutable_fields = {"midi", "fret"}

    for index, (baseline, candidate) in enumerate(zip(baseline_events, candidate_events)):
        if int(baseline["eventIndex"]) != int(candidate["eventIndex"]):
            raise ValueError("atomic dyad candidate changed event ordering")
        baseline_static = {key: value for key, value in baseline.items() if key not in mutable_fields}
        candidate_static = {key: value for key, value in candidate.items() if key not in mutable_fields}
        if baseline_static != candidate_static:
            raise ValueError("atomic dyad candidate changed protected non-pitch metadata")

        base_string, _, base_midi = _validate_position(baseline)
        cand_string, _, cand_midi = _validate_position(candidate)
        if base_string != cand_string:
            raise ValueError("atomic dyad candidate changed string position")
        midi_delta = cand_midi - base_midi
        fret_delta = int(candidate["fret"]) - int(baseline["fret"])
        if midi_delta != fret_delta:
            raise ValueError("atomic dyad candidate changed midi/fret inconsistently")
        if abs(midi_delta) > maximum:
            raise ValueError("atomic dyad candidate exceeded semitone bound")

        onset = (int(baseline["measure"]), int(baseline["step"]))
        baseline_by_onset[onset].append(baseline)
        if midi_delta != 0:
            changed_by_onset[onset].append(index)

    changed = 0
    for onset, indices in sorted(changed_by_onset.items()):
        if len(indices) != 2:
            raise ValueError("atomic dyad candidate changed only part of a two-note onset")
        baseline_onset = baseline_by_onset[onset]
        if len(baseline_onset) != 2:
            raise ValueError("atomic dyad candidate changed an onset that was not exactly two notes")

        changed_rows = [(baseline_events[index], candidate_events[index]) for index in indices]
        changed_strings = tuple(sorted(int(baseline["stringIndex"]) for baseline, _ in changed_rows))
        if len(set(changed_strings)) != 2:
            raise ValueError("atomic dyad changed events must occupy two distinct strings")

        if normalized_expected is not None:
            if not onset_matches_dyad_rule(
                baseline_onset,
                str(expected_context_signature),
                expected_note_rules or [],
                maximum_abs_semitone_shift=maximum,
            ):
                raise ValueError("atomic dyad candidate changed an onset outside the locked rule")
            expected_by_string = {
                string_index: (pitch_class, shift)
                for string_index, pitch_class, shift in normalized_expected
            }
            if changed_strings != tuple(sorted(expected_by_string)):
                raise ValueError("atomic dyad candidate changed non-locked strings")
            for baseline, candidate in changed_rows:
                string_index = int(baseline["stringIndex"])
                pitch_class, shift = expected_by_string[string_index]
                if int(baseline["midi"]) % 12 != pitch_class:
                    raise ValueError("atomic dyad candidate used a non-locked source pitch class")
                if int(candidate["midi"]) - int(baseline["midi"]) != shift:
                    raise ValueError("atomic dyad candidate used a non-locked semitone delta")
        changed += 2
    return changed


def reconstruct_accepted_baseline(v5_events: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    historical = canonical_events(apply_triple_prune(v5_events, HISTORICAL_TRIPLE_SIGNATURES))
    if len(historical) != HISTORICAL_TRIPLE_EVENT_COUNT or sha256_json(historical) != HISTORICAL_TRIPLE_EVENT_SHA256:
        raise ValueError("historical triple baseline reconstruction changed")

    pitch_baseline = canonical_events(
        apply_pitch_shift_rule(
            historical,
            PITCH_BASELINE_SIGNATURES,
            PITCH_BASELINE_SHIFT,
            maximum_abs_semitone_shift=DEFAULT_MAX_ABS_SEMITONE_SHIFT,
        )
    )
    if len(pitch_baseline) != ACCEPTED_EVENT_COUNT or sha256_json(pitch_baseline) != PITCH_BASELINE_EVENT_SHA256:
        raise ValueError("historical pitch baseline reconstruction changed")

    accepted = canonical_events(
        apply_pitch_position_rule(
            pitch_baseline,
            ACCEPTED_POSITION_SIGNATURES,
            ACCEPTED_POSITION_PITCH_SHIFT,
            ACCEPTED_POSITION_STRING_SHIFT,
            maximum_abs_semitone_shift=DEFAULT_MAX_ABS_SEMITONE_SHIFT,
            maximum_abs_string_shift=1,
        )
    )
    if len(accepted) != ACCEPTED_EVENT_COUNT or sha256_json(accepted) != ACCEPTED_EVENT_SHA256:
        raise ValueError("accepted pitch-position baseline reconstruction changed")
    return accepted


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fit-only atomic exact-two-note onset dyad pitch rewrite search from locked V144 Rhythm baseline."
    )
    parser.add_argument("v5_render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("accepted_manifest", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("locked_events", type=Path)
    parser.add_argument("--minimum-correction-support", type=int, default=DEFAULT_MIN_CORRECTION_SUPPORT)
    parser.add_argument("--maximum-candidates", type=int, default=DEFAULT_MAX_CANDIDATES)
    parser.add_argument("--maximum-abs-semitone-shift", type=int, default=DEFAULT_MAX_ABS_SEMITONE_SHIFT)
    args = parser.parse_args()

    config = ContextSplitConfig.from_mapping(load_json(args.config))
    manifest = load_json(args.accepted_manifest)
    if manifest.get("classification") != "v144-rhythm-selected-calibration-baseline":
        raise ValueError("accepted V144 manifest classification changed")
    if manifest.get("name") != ACCEPTED_BASELINE_NAME:
        raise ValueError("accepted current V144 baseline name changed")
    transform = manifest.get("transform") or {}
    if transform.get("type") != "contextual-joint-pitch-adjacent-string-position-shift":
        raise ValueError("accepted V144 baseline transform type changed")
    if transform.get("signatures") != ACCEPTED_POSITION_SIGNATURES:
        raise ValueError("accepted V144 baseline signatures changed")
    if int(transform.get("semitoneShift") or 0) != ACCEPTED_POSITION_PITCH_SHIFT:
        raise ValueError("accepted V144 baseline pitch shift changed")
    if int(transform.get("stringShift") or 0) != ACCEPTED_POSITION_STRING_SHIFT:
        raise ValueError("accepted V144 baseline string shift changed")
    selected_manifest = manifest.get("selectedCandidate") or {}
    if int(selected_manifest.get("eventCount") or 0) != ACCEPTED_EVENT_COUNT:
        raise ValueError("accepted V144 baseline event count changed")
    if selected_manifest.get("eventSha256") != ACCEPTED_EVENT_SHA256:
        raise ValueError("accepted V144 baseline SHA changed")
    if (manifest.get("promotionScope") or {}).get("calibrationBaseline") is not True:
        raise ValueError("accepted V144 manifest is not a calibration baseline")
    if (manifest.get("promotionScope") or {}).get("productionPromotionAllowed") is not False:
        raise ValueError("accepted V144 manifest unexpectedly allows Production promotion")

    v5_stream = load_json(args.v5_render_stream)
    v5_events = canonical_events(v5_stream.get("events") or [])
    if len(v5_events) != SOURCE_EVENT_COUNT or sha256_json(v5_events) != SOURCE_EVENT_SHA256:
        raise ValueError("immutable V5 event identity changed")
    baseline_events = reconstruct_accepted_baseline(v5_events)
    baseline_self = measure_set_evidence(baseline_events, baseline_events)
    if baseline_self["baselineGeneratedMeasureSetPreserved"] is not True:
        raise ValueError("accepted baseline failed self-preservation")
    if baseline_self["baselineGeneratedMeasureCount"] != ACCEPTED_GENERATED_MEASURE_COUNT:
        raise ValueError("accepted baseline must span exactly 113 generated measures")

    reference = scorer.validate_reference(load_json(args.gold_reference))
    reference_notes, _, _ = scorer.flatten_reference(reference)
    generated_notes, _ = scorer.flatten_generated(baseline_events)
    generated_fit_notes = subset(generated_notes, "fit", config)
    generated_fit_events = subset(baseline_events, "fit", config)
    reference_fit = subset(reference_notes, "fit", config)
    if len(generated_fit_events) != len(generated_fit_notes):
        raise ValueError("canonical fit-event and flattened fit-note counts diverged")

    ranked_rules = rank_fit_onset_dyad_pitch_rules(
        generated_fit_events,
        reference_fit,
        minimum_correction_support=args.minimum_correction_support,
        maximum_candidates=args.maximum_candidates,
        maximum_abs_semitone_shift=args.maximum_abs_semitone_shift,
    )

    baseline_fit = score_notes(generated_fit_notes, reference_fit)
    baseline = make_candidate(
        "accepted-v144-baseline",
        "accepted-v144-pitch-position-baseline",
        baseline_fit,
        measure_preserved=True,
        event_count_preserved=True,
    )
    candidates: list[dict[str, Any]] = [baseline]
    metadata: dict[str, dict[str, Any]] = {}

    for rule in ranked_rules:
        context_value = str(rule["contextSignature"])
        note_rules = [dict(value) for value in rule["noteRules"]]
        name = candidate_name(context_value, note_rules)
        if name in metadata:
            raise ValueError(f"atomic dyad candidate-name collision: {name}")
        candidate_events = canonical_events(
            apply_onset_dyad_pitch_rule(
                baseline_events,
                context_value,
                note_rules,
                maximum_abs_semitone_shift=args.maximum_abs_semitone_shift,
            )
        )
        if len(candidate_events) != ACCEPTED_EVENT_COUNT:
            raise ValueError(f"atomic dyad candidate {name} changed event count")
        measure_evidence = measure_set_evidence(baseline_events, candidate_events)
        if not measure_evidence["baselineGeneratedMeasureSetPreserved"]:
            raise ValueError(f"atomic dyad candidate {name} changed generated measure set")
        if measure_evidence["candidateGeneratedMeasureCount"] != ACCEPTED_GENERATED_MEASURE_COUNT:
            raise ValueError(f"atomic dyad candidate {name} changed generated measure count")
        changed_count = changed_event_count(
            baseline_events,
            candidate_events,
            maximum_abs_semitone_shift=args.maximum_abs_semitone_shift,
            expected_context_signature=context_value,
            expected_note_rules=note_rules,
        )
        if changed_count <= 0 or changed_count % 2 != 0:
            continue
        fit_score = stage_score_for_events(candidate_events, reference_notes, "fit", config)
        policy_text = "atomic-onset-dyad-pitch::" + context_value + " => " + ", ".join(
            f"string {int(note['stringIndex'])} pc {int(note['sourcePitchClass'])} pitch {int(note['semitoneShift']):+d}"
            for note in note_rules
        )
        candidates.append(
            make_candidate(
                name,
                policy_text,
                fit_score,
                measure_preserved=True,
                event_count_preserved=True,
            )
        )
        metadata[name] = {
            **rule,
            "changedEventCount": changed_count,
            "changedOnsetCount": changed_count // 2,
            "remainingEventCount": len(candidate_events),
            "candidateEventSha256": sha256_json(candidate_events),
            "measureSet": {
                "baselineGeneratedMeasureCount": measure_evidence["baselineGeneratedMeasureCount"],
                "candidateGeneratedMeasureCount": measure_evidence["candidateGeneratedMeasureCount"],
                "missingBaselineGeneratedMeasures": measure_evidence["missingBaselineGeneratedMeasures"],
                "extraCandidateGeneratedMeasures": measure_evidence["extraCandidateGeneratedMeasures"],
                "baselineGeneratedMeasureSetPreserved": measure_evidence["baselineGeneratedMeasureSetPreserved"],
                "professionalReferenceUsed": False,
            },
        }

    fit_lock = lock_fit_candidate(candidates, config=config, baseline_name="accepted-v144-baseline")
    locked_name = str(fit_lock["locked"])
    locked_rule = metadata.get(locked_name)
    locked_context = None if locked_rule is None else str(locked_rule["contextSignature"])
    locked_note_rules = None if locked_rule is None else [dict(value) for value in locked_rule["noteRules"]]
    locked_events = baseline_events if locked_rule is None else canonical_events(
        apply_onset_dyad_pitch_rule(
            baseline_events,
            locked_context or "",
            locked_note_rules or [],
            maximum_abs_semitone_shift=args.maximum_abs_semitone_shift,
        )
    )
    if len(locked_events) != ACCEPTED_EVENT_COUNT:
        raise ValueError("selector locked atomic dyad candidate with changed event count")
    locked_measure_evidence = measure_set_evidence(baseline_events, locked_events)
    if not locked_measure_evidence["baselineGeneratedMeasureSetPreserved"]:
        raise ValueError("selector locked atomic dyad candidate violating measure preservation")
    locked_changed_count = 0 if locked_rule is None else changed_event_count(
        baseline_events,
        locked_events,
        maximum_abs_semitone_shift=args.maximum_abs_semitone_shift,
        expected_context_signature=locked_context,
        expected_note_rules=locked_note_rules,
    )

    validation_gate = None
    canary_gate = None
    full_calibration = None
    stopped_at = "fit"
    selected = "accepted-v144-baseline"
    selected_reason = "fit-no-qualified-atomic-onset-dyad-candidate"

    if locked_name != "accepted-v144-baseline":
        locked = next(candidate for candidate in candidates if candidate["name"] == locked_name)
        baseline["validation"] = stage_score_for_events(baseline_events, reference_notes, "validation", config)
        locked["validation"] = stage_score_for_events(locked_events, reference_notes, "validation", config)
        validation_gate = gate_locked_candidate(baseline, locked, stage="validation", config=config)
        stopped_at = "validation"
        selected_reason = "locked-atomic-onset-dyad-candidate-failed-validation"
        if validation_gate["passed"]:
            baseline["canary"] = stage_score_for_events(baseline_events, reference_notes, "canary", config)
            locked["canary"] = stage_score_for_events(locked_events, reference_notes, "canary", config)
            canary_gate = gate_locked_candidate(baseline, locked, stage="canary", config=config)
            stopped_at = "canary"
            selected_reason = "locked-atomic-onset-dyad-candidate-failed-canary"
            if canary_gate["passed"]:
                selected = locked_name
                selected_reason = "locked-atomic-onset-dyad-candidate-passed-split-gates-pending-full-invariant"
                stopped_at = "full-calibration"
                selected_full = score_full_candidate(locked_events, reference)
                accepted_full = manifest.get("fullGoldCalibration") or {}
                baseline_metrics = accepted_full.get("gatedMetrics") or {}
                baseline_critical = int(accepted_full.get("criticalMismatchCount") or 0)
                gated_deltas = {
                    metric_name: float(selected_full["gatedMetrics"][metric_name]) - float(baseline_metrics[metric_name])
                    for metric_name in (
                        "pitchContentF1",
                        "pitchTimingTolerantF1",
                        "stringFretTimingTolerantF1",
                        "chordPitchSetTolerantF1",
                        "exactVoicingTolerantF1",
                        "measureCoverageRecall",
                    )
                }
                full_calibration = {
                    "score": selected_full,
                    "baselineComparison": {
                        "baselineName": ACCEPTED_BASELINE_NAME,
                        "baselineEventSha256": ACCEPTED_EVENT_SHA256,
                        "gatedMetricDeltas": gated_deltas,
                        "criticalMismatchDelta": int(selected_full["criticalMismatchCount"]) - baseline_critical,
                    },
                    "pdfEventFidelity": None,
                    "invariantPassed": None,
                }

    args.locked_events.parent.mkdir(parents=True, exist_ok=True)
    args.locked_events.write_text(
        json.dumps(
            {
                "schemaVersion": 14418,
                "instrument": "rhythm",
                "source": "accepted-v144-pitch-position-calibration-baseline",
                "sourceEventSha256": ACCEPTED_EVENT_SHA256,
                "lockedCandidate": locked_name,
                "lockedContextSignature": locked_context,
                "lockedNoteRules": locked_note_rules,
                "runtimeReferenceInputUsed": False,
                "baselineEventCountPreserved": len(locked_events) == ACCEPTED_EVENT_COUNT,
                "baselineGeneratedMeasureSetPreserved": locked_measure_evidence["baselineGeneratedMeasureSetPreserved"],
                "renderEvents": locked_events,
            },
            separators=(",", ":"),
        ) + "\n",
        encoding="utf-8",
    )

    report = {
        "schemaVersion": 14418,
        "classification": "v144-rhythm-fit-only-atomic-onset-dyad-pitch-search",
        "evaluationRole": "accepted-v144-baseline-atomic-two-note-onset-dyad-pitch-correction-gold-calibration",
        "mayClaimUnseenGeneralization": False,
        "candidateConstruction": {
            "sourceBaselineName": ACCEPTED_BASELINE_NAME,
            "sourceBaselineEventCount": ACCEPTED_EVENT_COUNT,
            "sourceBaselineEventSha256": ACCEPTED_EVENT_SHA256,
            "sourceLabels": "accepted-baseline-fit-only-exact-two-note-onset-same-string-reference-pairs",
            "runtimeRuleInputs": "reference-free-exact-two-note-generated-onset-plus-structural-context-and-fixed-same-string-note-shifts-only",
            "candidateRuleShape": "atomic-exact-two-note-onset-same-string-dyad-pitch-rewrite",
            "pairingPolicy": "exact-two-note-generated-and-reference-onsets-same-two-distinct-strings-both-nonzero-tuning-derived-targets",
            "minimumCorrectionSupport": int(args.minimum_correction_support),
            "maximumCandidates": int(args.maximum_candidates),
            "maximumAbsSemitoneShift": int(args.maximum_abs_semitone_shift),
            "rankedRuleCount": len(ranked_rules),
            "evaluatedCandidateCount": len(candidates) - 1,
            "fitGeneratedNoteCount": len(generated_fit_notes),
            "fitGeneratedCanonicalEventCount": len(generated_fit_events),
            "fitReferenceNoteCount": len(reference_fit),
            "canonicalGeneratedEventsUsedForConstructionAndEligibility": True,
            "validationLabelsUsedForCandidateConstructionOrRanking": False,
            "canaryLabelsUsedForCandidateConstructionOrRanking": False,
            "historicalConsumedFamilyResultsUsedForConstructionOrRanking": False,
            "measureSetGuardUsesProfessionalReference": False,
            "eventCountPreservationRequired": True,
            "generatedMeasureSetPreservationRequired": True,
            "exactlyTwoNoteOnsetRequired": True,
            "sameTwoDistinctStringsRequired": True,
            "atomicTwoEventChangeRequired": True,
            "bothSemitoneShiftsNonZeroRequired": True,
            "timingPreservationRequired": True,
            "stringPreservationRequired": True,
            "durationAndOtherMetadataPreservationRequired": True,
            "tuningDerivedFretRequired": True,
            "linkedPitchTechniqueEventsEligible": False,
        },
        "baseline": {
            "name": "accepted-v144-baseline",
            "fit": baseline_fit,
            "eventCount": len(baseline_events),
            "eventSha256": sha256_json(baseline_events),
            "generatedMeasureCount": ACCEPTED_GENERATED_MEASURE_COUNT,
        },
        "fitLock": fit_lock,
        "candidateMetadata": metadata,
        "locked": {
            "name": locked_name,
            "contextSignature": locked_context,
            "noteRules": locked_note_rules,
            "eventCount": len(locked_events),
            "eventSha256": sha256_json(locked_events),
            "changedEventCount": locked_changed_count,
            "changedOnsetCount": locked_changed_count // 2,
            "measureSet": {
                "baselineGeneratedMeasureCount": locked_measure_evidence["baselineGeneratedMeasureCount"],
                "candidateGeneratedMeasureCount": locked_measure_evidence["candidateGeneratedMeasureCount"],
                "missingBaselineGeneratedMeasures": locked_measure_evidence["missingBaselineGeneratedMeasures"],
                "extraCandidateGeneratedMeasures": locked_measure_evidence["extraCandidateGeneratedMeasures"],
                "baselineGeneratedMeasureSetPreserved": locked_measure_evidence["baselineGeneratedMeasureSetPreserved"],
                "professionalReferenceUsed": False,
            },
        },
        "validation": validation_gate,
        "canary": canary_gate,
        "fullCalibration": full_calibration,
        "selected": selected,
        "selectedReason": selected_reason,
        "stoppedAt": stopped_at,
        "splitPromotionAllowed": selected != "accepted-v144-baseline",
        "calibrationPromotionAllowed": False,
        "alternateAfterGateFailureAllowed": False,
        "safety": safety_payload(measure_preserved=True, event_count_preserved=True),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
