from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
SEARCH_DIR = ROOT / "validation" / "v144_rhythm_calibration"
MODAL_DIR = ROOT / "modal"
for entry in (HOLDOUT_DIR, SEARCH_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
import score_rhythm_holdout as scorer  # noqa: E402
from analyze_singleton_baseline_fit_residuals import (  # noqa: E402
    BASELINE_EVENT_COUNT,
    BASELINE_EVENT_SHA256,
    BASELINE_MEASURE_COUNT,
    BASELINE_NAME,
    _validate_manifest,
    reconstruct_selected_baseline,
)
from analyze_split_baseline import split_name  # noqa: E402
from score_selected_conjunction_candidate import score_full_candidate  # noqa: E402
from search_single_signature_prunes import load_json, stage_score_for_events  # noqa: E402
from v144_rhythm_context_split_policy import ContextSplitConfig  # noqa: E402
from v144_rhythm_measure_set_guard import measure_set_evidence  # noqa: E402
from v144_rhythm_shared_dyad_surplus_prune_policy import (  # noqa: E402
    DEFAULT_MAX_CANDIDATES,
    DEFAULT_MIN_CORRECTION_SUPPORT,
    apply_shared_dyad_surplus_prune_rule,
    onset_matches_shared_dyad_surplus_prune_rule,
    rank_fit_shared_dyad_surplus_prune_rules,
)
from v144_rhythm_staged_selector import gate_locked_candidate, lock_fit_candidate  # noqa: E402

REPORT_SCHEMA_VERSION = 14427
BASELINE_LABEL = "accepted-v144-baseline"
_ALLOWED_CONTEXT_PREFIXES = (
    "measurePhase::",
    "section16::",
    "stepParity::",
    "stepQuarter::",
    "measurePhaseStep::",
)


def _validate_fixed_search_parameters(
    minimum_correction_support: int,
    maximum_candidates: int,
) -> None:
    if int(minimum_correction_support) != DEFAULT_MIN_CORRECTION_SUPPORT:
        raise ValueError("family #14 minimum correction support is preregistered at exactly 3")
    if int(maximum_candidates) != DEFAULT_MAX_CANDIDATES:
        raise ValueError("family #14 maximum candidate count is preregistered at exactly 256")


def _normalize_note_identity(string_index: int, pitch_class: int) -> tuple[int, int]:
    string_value = int(string_index)
    pitch_value = int(pitch_class)
    if not 0 <= string_value <= 5:
        raise ValueError("family #14 source string outside [0,5]")
    if not 0 <= pitch_value <= 11:
        raise ValueError("family #14 source pitch class outside [0,11]")
    return string_value, pitch_value


def _normalize_rule(
    context_signature_value: str,
    first_string_index: int,
    first_pitch_class: int,
    second_string_index: int,
    second_pitch_class: int,
    prune_string_index: int,
    prune_pitch_class: int,
) -> tuple[str, tuple[tuple[int, int], tuple[int, int]], tuple[int, int]]:
    context_value = str(context_signature_value)
    if not context_value.startswith(_ALLOWED_CONTEXT_PREFIXES):
        raise ValueError("family #14 rule requires one structural onset context signature")
    identities = tuple(
        sorted(
            (
                _normalize_note_identity(first_string_index, first_pitch_class),
                _normalize_note_identity(second_string_index, second_pitch_class),
            )
        )
    )
    if identities[0] == identities[1]:
        raise ValueError("family #14 rule requires two distinguishable source identities")
    prune_identity = _normalize_note_identity(prune_string_index, prune_pitch_class)
    if sum(1 for identity in identities if identity == prune_identity) != 1:
        raise ValueError("family #14 prune identity must uniquely name one dyad member")
    return context_value, identities, prune_identity  # type: ignore[return-value]


def candidate_name(
    context_signature_value: str,
    first_string_index: int,
    first_pitch_class: int,
    second_string_index: int,
    second_pitch_class: int,
    prune_string_index: int,
    prune_pitch_class: int,
) -> str:
    context_value, identities, prune_identity = _normalize_rule(
        context_signature_value,
        first_string_index,
        first_pitch_class,
        second_string_index,
        second_pitch_class,
        prune_string_index,
        prune_pitch_class,
    )
    token = (
        f"{context_value}\n"
        f"note0::{identities[0][0]}::{identities[0][1]}\n"
        f"note1::{identities[1][0]}::{identities[1][1]}\n"
        f"prune::{prune_identity[0]}::{prune_identity[1]}"
    )
    return "shared-dyad-surplus-prune-" + hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]


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


def removed_event_count(
    baseline_events: Sequence[Mapping[str, Any]],
    candidate_events: Sequence[Mapping[str, Any]],
    *,
    expected_context_signature: str | None = None,
    expected_first_string_index: int | None = None,
    expected_first_pitch_class: int | None = None,
    expected_second_string_index: int | None = None,
    expected_second_pitch_class: int | None = None,
    expected_prune_string_index: int | None = None,
    expected_prune_pitch_class: int | None = None,
) -> int:
    """Prove a candidate is exactly a reference-free family #14 one-member dyad prune."""
    expected_values = (
        expected_context_signature,
        expected_first_string_index,
        expected_first_pitch_class,
        expected_second_string_index,
        expected_second_pitch_class,
        expected_prune_string_index,
        expected_prune_pitch_class,
    )
    supplied = [value is not None for value in expected_values]
    if any(supplied) and not all(supplied):
        raise ValueError("all expected family #14 rule fields must be supplied together")
    if len(candidate_events) > len(baseline_events):
        raise ValueError("family #14 candidate added events")

    baseline = [dict(row) for row in baseline_events]
    candidate = [dict(row) for row in candidate_events]
    baseline_indices = [int(row["eventIndex"]) for row in baseline]
    candidate_indices = [int(row["eventIndex"]) for row in candidate]
    candidate_set = set(candidate_indices)
    if candidate_indices != [value for value in baseline_indices if value in candidate_set]:
        raise ValueError("family #14 candidate changed survivor ordering or duplicated event indices")
    if len(candidate_indices) != len(candidate_set):
        raise ValueError("family #14 candidate duplicated survivor event indices")

    baseline_by_index = {int(row["eventIndex"]): row for row in baseline}
    if len(baseline_by_index) != len(baseline):
        raise ValueError("baseline event indices are not unique")
    for row in candidate:
        index = int(row["eventIndex"])
        if index not in baseline_by_index or row != baseline_by_index[index]:
            raise ValueError("family #14 candidate modified a surviving event")

    removed = len(baseline) - len(candidate)
    if removed > 0 and not all(supplied):
        raise ValueError("family #14 deletion proof requires the complete locked rule")

    if all(supplied):
        context_value, identities, prune_identity = _normalize_rule(
            str(expected_context_signature),
            int(expected_first_string_index),
            int(expected_first_pitch_class),
            int(expected_second_string_index),
            int(expected_second_pitch_class),
            int(expected_prune_string_index),
            int(expected_prune_pitch_class),
        )
        expected_candidate = apply_shared_dyad_surplus_prune_rule(
            baseline,
            context_value,
            identities[0][0],
            identities[0][1],
            identities[1][0],
            identities[1][1],
            prune_identity[0],
            prune_identity[1],
        )
        if candidate != expected_candidate:
            raise ValueError("family #14 candidate does not equal locked reference-free rule output")

        baseline_by_onset: dict[tuple[int, int], list[dict[str, Any]]] = {}
        candidate_by_onset: dict[tuple[int, int], list[dict[str, Any]]] = {}
        for row in baseline:
            baseline_by_onset.setdefault((int(row["measure"]), int(row["step"])), []).append(row)
        for row in candidate:
            candidate_by_onset.setdefault((int(row["measure"]), int(row["step"])), []).append(row)

        removed_onsets: set[tuple[int, int]] = set()
        for index in baseline_indices:
            if index in candidate_set:
                continue
            row = baseline_by_index[index]
            onset = (int(row["measure"]), int(row["step"]))
            onset_events = baseline_by_onset[onset]
            if len(onset_events) != 2:
                raise ValueError("family #14 removed a member of a non-dyad onset")
            if not onset_matches_shared_dyad_surplus_prune_rule(
                onset_events,
                context_value,
                identities[0][0],
                identities[0][1],
                identities[1][0],
                identities[1][1],
                prune_identity[0],
                prune_identity[1],
            ):
                raise ValueError("family #14 removed an onset outside the locked rule")
            row_identity = (int(row["stringIndex"]), int(row["midi"]) % 12)
            if row_identity != prune_identity:
                raise ValueError("family #14 removed the survivor instead of the locked prune member")
            remaining = candidate_by_onset.get(onset, [])
            if len(remaining) != 1:
                raise ValueError("family #14 changed onset did not remain an exact singleton")
            removed_onsets.add(onset)
        if removed != len(removed_onsets):
            raise ValueError("family #14 must remove exactly one event per changed dyad onset")
    return removed


def _fit_rows(
    baseline_events: Sequence[Mapping[str, Any]],
    reference: Mapping[str, Any],
    config: ContextSplitConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    generated_notes, _ = scorer.flatten_generated(baseline_events)
    reference_notes, _, _ = scorer.flatten_reference(reference)
    fit_generated = [dict(row) for row in generated_notes if split_name(row, config) == "fit"]
    fit_reference = [dict(row) for row in reference_notes if split_name(row, config) == "fit"]
    return fit_generated, fit_reference


def main() -> int:
    parser = argparse.ArgumentParser(
        description="FIT-only family #14 atomic shared dyad-to-singleton surplus-note prune search."
    )
    parser.add_argument("v5_render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("accepted_manifest", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("locked_events", type=Path)
    parser.add_argument(
        "--minimum-correction-support",
        type=int,
        default=DEFAULT_MIN_CORRECTION_SUPPORT,
    )
    parser.add_argument("--maximum-candidates", type=int, default=DEFAULT_MAX_CANDIDATES)
    args = parser.parse_args()
    _validate_fixed_search_parameters(args.minimum_correction_support, args.maximum_candidates)

    config = ContextSplitConfig.from_mapping(load_json(args.config))
    manifest = load_json(args.accepted_manifest)
    _validate_manifest(manifest)

    v5_payload = load_json(args.v5_render_stream)
    source_events = canonical_events(v5_payload.get("events") or [])
    baseline_events = reconstruct_selected_baseline(source_events)
    if len(baseline_events) != BASELINE_EVENT_COUNT or sha256_json(baseline_events) != BASELINE_EVENT_SHA256:
        raise ValueError("accepted family #10 baseline identity changed")
    if len({int(row["measure"]) for row in baseline_events}) != BASELINE_MEASURE_COUNT:
        raise ValueError("accepted family #10 measure count changed")

    # Gold labels are opened only after accepted baseline identity is reconstructed.
    reference = scorer.validate_reference(load_json(args.gold_reference))
    fit_generated, fit_reference = _fit_rows(baseline_events, reference, config)
    ranked_rules = rank_fit_shared_dyad_surplus_prune_rules(
        fit_generated,
        fit_reference,
        minimum_correction_support=args.minimum_correction_support,
        maximum_candidates=args.maximum_candidates,
    )

    reference_notes = scorer.flatten_reference(reference)[0]
    baseline_fit = stage_score_for_events(baseline_events, reference_notes, "fit", config)
    baseline = make_candidate(
        BASELINE_LABEL,
        "accepted-family-ten-singleton-baseline",
        baseline_fit,
        measure_preserved=True,
        event_count_preserved=True,
    )
    candidates: list[dict[str, Any]] = [baseline]
    metadata: dict[str, dict[str, Any]] = {}

    for rule in ranked_rules:
        context_value = str(rule["contextSignature"])
        first_string = int(rule["firstSourceStringIndex"])
        first_pitch = int(rule["firstSourcePitchClass"])
        second_string = int(rule["secondSourceStringIndex"])
        second_pitch = int(rule["secondSourcePitchClass"])
        prune_string = int(rule["pruneSourceStringIndex"])
        prune_pitch = int(rule["pruneSourcePitchClass"])
        name = candidate_name(
            context_value,
            first_string,
            first_pitch,
            second_string,
            second_pitch,
            prune_string,
            prune_pitch,
        )
        candidate_events = apply_shared_dyad_surplus_prune_rule(
            baseline_events,
            context_value,
            first_string,
            first_pitch,
            second_string,
            second_pitch,
            prune_string,
            prune_pitch,
        )
        if len(candidate_events) >= len(baseline_events):
            continue
        measure_evidence = measure_set_evidence(baseline_events, candidate_events)
        if not measure_evidence["baselineGeneratedMeasureSetPreserved"]:
            continue
        if int(measure_evidence["candidateGeneratedMeasureCount"]) != BASELINE_MEASURE_COUNT:
            continue
        removed_count = removed_event_count(
            baseline_events,
            candidate_events,
            expected_context_signature=context_value,
            expected_first_string_index=first_string,
            expected_first_pitch_class=first_pitch,
            expected_second_string_index=second_string,
            expected_second_pitch_class=second_pitch,
            expected_prune_string_index=prune_string,
            expected_prune_pitch_class=prune_pitch,
        )
        if removed_count <= 0:
            continue

        fit_score = stage_score_for_events(candidate_events, reference_notes, "fit", config)
        candidates.append(
            make_candidate(
                name,
                "atomic-shared-dyad-surplus-note-prune::"
                + context_value
                + f" | dyad ({first_string},{first_pitch}) ({second_string},{second_pitch})"
                + f" | prune ({prune_string},{prune_pitch})",
                fit_score,
                measure_preserved=True,
                event_count_preserved=False,
            )
        )
        metadata[name] = {
            **rule,
            "removedEventCount": removed_count,
            "removedOnsetCount": removed_count,
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

    fit_lock = lock_fit_candidate(candidates, config=config, baseline_name=BASELINE_LABEL)
    locked_name = str(fit_lock["locked"])
    locked_rule = metadata.get(locked_name)
    locked_context = None if locked_rule is None else str(locked_rule["contextSignature"])
    locked_first_string = None if locked_rule is None else int(locked_rule["firstSourceStringIndex"])
    locked_first_pitch = None if locked_rule is None else int(locked_rule["firstSourcePitchClass"])
    locked_second_string = None if locked_rule is None else int(locked_rule["secondSourceStringIndex"])
    locked_second_pitch = None if locked_rule is None else int(locked_rule["secondSourcePitchClass"])
    locked_prune_string = None if locked_rule is None else int(locked_rule["pruneSourceStringIndex"])
    locked_prune_pitch = None if locked_rule is None else int(locked_rule["pruneSourcePitchClass"])
    locked_events = baseline_events if locked_rule is None else apply_shared_dyad_surplus_prune_rule(
        baseline_events,
        locked_context or "",
        int(locked_first_string),
        int(locked_first_pitch),
        int(locked_second_string),
        int(locked_second_pitch),
        int(locked_prune_string),
        int(locked_prune_pitch),
    )
    locked_measure_evidence = measure_set_evidence(baseline_events, locked_events)
    if not locked_measure_evidence["baselineGeneratedMeasureSetPreserved"]:
        raise ValueError("selector locked family #14 candidate violating measure preservation")
    if int(locked_measure_evidence["candidateGeneratedMeasureCount"]) != BASELINE_MEASURE_COUNT:
        raise ValueError("selector locked family #14 candidate changed generated measure count")
    locked_removed_count = 0 if locked_rule is None else removed_event_count(
        baseline_events,
        locked_events,
        expected_context_signature=locked_context,
        expected_first_string_index=locked_first_string,
        expected_first_pitch_class=locked_first_pitch,
        expected_second_string_index=locked_second_string,
        expected_second_pitch_class=locked_second_pitch,
        expected_prune_string_index=locked_prune_string,
        expected_prune_pitch_class=locked_prune_pitch,
    )

    validation_gate = None
    canary_gate = None
    full_calibration = None
    stopped_at = "fit"
    selected = BASELINE_LABEL
    selected_reason = "fit-no-qualified-atomic-shared-dyad-surplus-prune-candidate"

    if locked_name != BASELINE_LABEL:
        locked = next(candidate for candidate in candidates if candidate["name"] == locked_name)
        baseline["validation"] = stage_score_for_events(baseline_events, reference_notes, "validation", config)
        locked["validation"] = stage_score_for_events(locked_events, reference_notes, "validation", config)
        validation_gate = gate_locked_candidate(baseline, locked, stage="validation", config=config)
        stopped_at = "validation"
        selected_reason = "locked-atomic-shared-dyad-surplus-prune-candidate-failed-validation"
        if validation_gate["passed"]:
            baseline["canary"] = stage_score_for_events(baseline_events, reference_notes, "canary", config)
            locked["canary"] = stage_score_for_events(locked_events, reference_notes, "canary", config)
            canary_gate = gate_locked_candidate(baseline, locked, stage="canary", config=config)
            stopped_at = "canary"
            selected_reason = "locked-atomic-shared-dyad-surplus-prune-candidate-failed-canary"
            if canary_gate["passed"]:
                selected = locked_name
                selected_reason = "locked-atomic-shared-dyad-surplus-prune-candidate-passed-split-gates-pending-full-invariant"
                stopped_at = "full-calibration"
                selected_full = score_full_candidate(locked_events, reference)
                accepted_full = manifest.get("fullGoldCalibration") or {}
                baseline_metrics = accepted_full.get("gatedMetrics") or {}
                baseline_critical = int(accepted_full.get("criticalMismatchCount") or 0)
                metric_names = (
                    "pitchContentF1",
                    "pitchTimingTolerantF1",
                    "stringFretTimingTolerantF1",
                    "chordPitchSetTolerantF1",
                    "exactVoicingTolerantF1",
                    "measureCoverageRecall",
                )
                gated_deltas = {
                    metric_name: float(selected_full["gatedMetrics"][metric_name]) - float(baseline_metrics[metric_name])
                    for metric_name in metric_names
                }
                full_calibration = {
                    "score": selected_full,
                    "baselineComparison": {
                        "baselineName": BASELINE_NAME,
                        "baselineEventSha256": BASELINE_EVENT_SHA256,
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
                "schemaVersion": REPORT_SCHEMA_VERSION,
                "instrument": "rhythm",
                "source": "accepted-v144-singleton-calibration-baseline",
                "sourceEventSha256": BASELINE_EVENT_SHA256,
                "lockedCandidate": locked_name,
                "lockedContextSignature": locked_context,
                "lockedFirstSourceStringIndex": locked_first_string,
                "lockedFirstSourcePitchClass": locked_first_pitch,
                "lockedSecondSourceStringIndex": locked_second_string,
                "lockedSecondSourcePitchClass": locked_second_pitch,
                "lockedPruneSourceStringIndex": locked_prune_string,
                "lockedPruneSourcePitchClass": locked_prune_pitch,
                "runtimeReferenceInputUsed": False,
                "baselineGeneratedMeasureSetPreserved": locked_measure_evidence["baselineGeneratedMeasureSetPreserved"],
                "renderEvents": locked_events,
            },
            separators=(",", ":"),
        ) + "\n",
        encoding="utf-8",
    )

    report = {
        "schemaVersion": REPORT_SCHEMA_VERSION,
        "classification": "v144-rhythm-fit-only-atomic-shared-dyad-surplus-note-prune-search",
        "evaluationRole": "accepted-singleton-baseline-atomic-shared-dyad-to-singleton-surplus-note-prune-gold-calibration",
        "mayClaimUnseenGeneralization": False,
        "candidateConstruction": {
            "sourceBaselineName": BASELINE_NAME,
            "sourceBaselineEventCount": BASELINE_EVENT_COUNT,
            "sourceBaselineEventSha256": BASELINE_EVENT_SHA256,
            "sourceLabels": "accepted-baseline-fit-only-shared-exact-g2-r1-onsets-with-one-exact-midi-survivor",
            "runtimeRuleInputs": "reference-free-exact-two-note-generated-onset-plus-one-structural-context-two-sorted-source-string-pitch-class-identities-and-one-unique-prune-identity-only",
            "candidateRuleShape": "atomic-shared-dyad-to-singleton-surplus-note-prune",
            "minimumCorrectionSupport": int(args.minimum_correction_support),
            "maximumCandidates": int(args.maximum_candidates),
            "rankedRuleCount": len(ranked_rules),
            "evaluatedCandidateCount": len(candidates) - 1,
            "fitGeneratedNoteCount": len(fit_generated),
            "fitReferenceNoteCount": len(fit_reference),
            "validationLabelsUsedForCandidateConstructionOrRanking": False,
            "canaryLabelsUsedForCandidateConstructionOrRanking": False,
            "historicalConsumedFamilyResultsUsedForConstructionOrRanking": False,
            "measureSetGuardUsesProfessionalReference": False,
            "eventCountPreservationRequired": False,
            "generatedMeasureSetPreservationRequired": True,
            "exactlyTwoGeneratedNotesOnsetRequired": True,
            "exactlyOneReferenceNoteOnsetRequiredForConstruction": True,
            "exactlyOneGeneratedExactMidiSurvivorRequiredForConstruction": True,
            "atomicSingleMemberDeletionRequired": True,
            "removedEventsPerChangedOnset": 1,
            "sharedOnsetPreservedAsSingleton": True,
            "linkedOrReferencedEventsEligible": False,
            "measureErasingOnsetsEligible": False,
            "survivorMutationAllowed": False,
        },
        "baseline": {
            "name": BASELINE_LABEL,
            "fit": baseline_fit,
            "eventCount": len(baseline_events),
            "eventSha256": sha256_json(baseline_events),
            "generatedMeasureCount": BASELINE_MEASURE_COUNT,
        },
        "fitLock": fit_lock,
        "candidateMetadata": metadata,
        "locked": {
            "name": locked_name,
            "contextSignature": locked_context,
            "firstSourceStringIndex": locked_first_string,
            "firstSourcePitchClass": locked_first_pitch,
            "secondSourceStringIndex": locked_second_string,
            "secondSourcePitchClass": locked_second_pitch,
            "pruneSourceStringIndex": locked_prune_string,
            "pruneSourcePitchClass": locked_prune_pitch,
            "eventCount": len(locked_events),
            "eventSha256": sha256_json(locked_events),
            "removedEventCount": locked_removed_count,
            "removedOnsetCount": locked_removed_count,
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
        "splitPromotionAllowed": selected != BASELINE_LABEL,
        "calibrationPromotionAllowed": False,
        "alternateAfterGateFailureAllowed": False,
        "safety": safety_payload(
            measure_preserved=locked_measure_evidence["baselineGeneratedMeasureSetPreserved"],
            event_count_preserved=len(locked_events) == BASELINE_EVENT_COUNT,
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
