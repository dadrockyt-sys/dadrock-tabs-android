from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

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
from v144_rhythm_pitch_shift_policy import (  # noqa: E402
    DEFAULT_MAX_ABS_SEMITONE_SHIFT,
    DEFAULT_MAX_CANDIDATES,
    DEFAULT_MIN_CORRECTION_SUPPORT,
    apply_pitch_shift_rule,
    rank_fit_pitch_shift_rules,
)
from v144_rhythm_staged_selector import (  # noqa: E402
    gate_locked_candidate,
    lock_fit_candidate,
)
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
ACCEPTED_BASELINE_NAME = "prune-triple-67348efe50436fc5"
ACCEPTED_BASELINE_SIGNATURES = ["register::high", "section16::1", "stepParity::0"]
ACCEPTED_EVENT_COUNT = 1144
ACCEPTED_EVENT_SHA256 = "68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3"
ACCEPTED_GENERATED_MEASURE_COUNT = 113


def candidate_name(signatures: list[str], semitone_shift: int) -> str:
    token = (
        "\n".join(sorted(str(value) for value in signatures))
        + f"\nshift::{int(semitone_shift)}"
    ).encode("utf-8")
    return "pitch-shift-" + hashlib.sha256(token).hexdigest()[:16]


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


def changed_event_count(
    baseline_events: list[Mapping[str, Any]], candidate_events: list[Mapping[str, Any]]
) -> int:
    """Count pitch shifts while proving every non-pitch event field stayed identical."""
    if len(baseline_events) != len(candidate_events):
        raise ValueError("pitch-shift candidate changed event count")

    changed = 0
    for baseline, candidate in zip(baseline_events, candidate_events):
        if int(baseline["eventIndex"]) != int(candidate["eventIndex"]):
            raise ValueError("pitch-shift candidate changed event ordering")

        baseline_non_pitch = {
            key: value for key, value in baseline.items() if key not in {"midi", "fret"}
        }
        candidate_non_pitch = {
            key: value for key, value in candidate.items() if key not in {"midi", "fret"}
        }
        if baseline_non_pitch != candidate_non_pitch:
            raise ValueError("pitch-shift candidate changed non-pitch event metadata")

        midi_delta = int(candidate["midi"]) - int(baseline["midi"])
        fret_delta = int(candidate["fret"]) - int(baseline["fret"])
        if midi_delta != fret_delta:
            raise ValueError("pitch-shift candidate changed midi/fret inconsistently")
        if midi_delta != 0:
            changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fit-only contextual same-string pitch-shift search from the accepted "
            "V144 1144-event Rhythm baseline."
        )
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
    parser.add_argument(
        "--maximum-candidates",
        type=int,
        default=DEFAULT_MAX_CANDIDATES,
    )
    parser.add_argument(
        "--maximum-abs-semitone-shift",
        type=int,
        default=DEFAULT_MAX_ABS_SEMITONE_SHIFT,
    )
    args = parser.parse_args()

    config = ContextSplitConfig.from_mapping(load_json(args.config))
    manifest = load_json(args.accepted_manifest)
    if manifest.get("classification") != "v144-rhythm-selected-calibration-baseline":
        raise ValueError("accepted V144 manifest classification changed")
    if manifest.get("name") != ACCEPTED_BASELINE_NAME:
        raise ValueError("accepted V144 baseline name changed")
    if (manifest.get("transform") or {}).get("signatures") != ACCEPTED_BASELINE_SIGNATURES:
        raise ValueError("accepted V144 baseline signatures changed")
    selected_manifest = manifest.get("selectedCandidate") or {}
    if int(selected_manifest.get("eventCount") or 0) != ACCEPTED_EVENT_COUNT:
        raise ValueError("accepted V144 baseline event count changed")
    if selected_manifest.get("eventSha256") != ACCEPTED_EVENT_SHA256:
        raise ValueError("accepted V144 baseline SHA changed")
    if (manifest.get("promotionScope") or {}).get("calibrationBaseline") is not True:
        raise ValueError("accepted V144 manifest is not a calibration baseline")

    v5_stream = load_json(args.v5_render_stream)
    v5_events = canonical_events(v5_stream.get("events") or [])
    if len(v5_events) != SOURCE_EVENT_COUNT or sha256_json(v5_events) != SOURCE_EVENT_SHA256:
        raise ValueError("immutable V5 event identity changed")

    baseline_events = canonical_events(
        apply_triple_prune(v5_events, ACCEPTED_BASELINE_SIGNATURES)
    )
    if len(baseline_events) != ACCEPTED_EVENT_COUNT:
        raise ValueError("accepted baseline reconstruction event count changed")
    if sha256_json(baseline_events) != ACCEPTED_EVENT_SHA256:
        raise ValueError("accepted baseline reconstruction SHA changed")
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

    ranked_rules = rank_fit_pitch_shift_rules(
        generated_fit_events,
        reference_fit,
        minimum_correction_support=args.minimum_correction_support,
        maximum_candidates=args.maximum_candidates,
        maximum_abs_semitone_shift=args.maximum_abs_semitone_shift,
    )

    baseline_fit = score_notes(generated_fit_notes, reference_fit)
    baseline = make_candidate(
        "accepted-v144-baseline",
        "accepted-v144-triple-baseline",
        baseline_fit,
        measure_preserved=True,
        event_count_preserved=True,
    )
    candidates: list[dict[str, Any]] = [baseline]
    metadata: dict[str, dict[str, Any]] = {}

    for rule in ranked_rules:
        signatures = [str(value) for value in rule["signatures"]]
        semitone_shift = int(rule["semitoneShift"])
        name = candidate_name(signatures, semitone_shift)
        if name in metadata:
            raise ValueError(f"pitch-shift candidate-name collision: {name}")

        candidate_events = canonical_events(
            apply_pitch_shift_rule(
                baseline_events,
                signatures,
                semitone_shift,
                maximum_abs_semitone_shift=args.maximum_abs_semitone_shift,
            )
        )
        event_count_preserved = len(candidate_events) == ACCEPTED_EVENT_COUNT
        if not event_count_preserved:
            raise ValueError(f"pitch-shift candidate {name} changed event count")
        measure_evidence = measure_set_evidence(baseline_events, candidate_events)
        if not measure_evidence["baselineGeneratedMeasureSetPreserved"]:
            raise ValueError(f"pitch-shift candidate {name} changed generated measure set")
        if measure_evidence["candidateGeneratedMeasureCount"] != ACCEPTED_GENERATED_MEASURE_COUNT:
            raise ValueError(f"pitch-shift candidate {name} changed generated measure count")

        changed_count = changed_event_count(baseline_events, candidate_events)
        if changed_count <= 0:
            continue
        fit_score = stage_score_for_events(candidate_events, reference_notes, "fit", config)
        candidates.append(
            make_candidate(
                name,
                "contextual-same-string-pitch-shift::"
                + " && ".join(signatures)
                + f" => {semitone_shift:+d}",
                fit_score,
                measure_preserved=True,
                event_count_preserved=True,
            )
        )
        metadata[name] = {
            **rule,
            "changedEventCount": changed_count,
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

    fit_lock = lock_fit_candidate(
        candidates,
        config=config,
        baseline_name="accepted-v144-baseline",
    )
    locked_name = str(fit_lock["locked"])
    locked_rule = metadata.get(locked_name)
    locked_signatures = None if locked_rule is None else list(locked_rule["signatures"])
    locked_shift = None if locked_rule is None else int(locked_rule["semitoneShift"])
    locked_events = (
        baseline_events
        if locked_rule is None
        else canonical_events(
            apply_pitch_shift_rule(
                baseline_events,
                locked_signatures or [],
                int(locked_shift),
                maximum_abs_semitone_shift=args.maximum_abs_semitone_shift,
            )
        )
    )
    if len(locked_events) != ACCEPTED_EVENT_COUNT:
        raise ValueError("selector locked a pitch-shift candidate with changed event count")
    locked_measure_evidence = measure_set_evidence(baseline_events, locked_events)
    if not locked_measure_evidence["baselineGeneratedMeasureSetPreserved"]:
        raise ValueError("selector locked a candidate that violates accepted-baseline measure preservation")
    locked_changed_count = changed_event_count(baseline_events, locked_events)

    validation_gate = None
    canary_gate = None
    full_calibration = None
    stopped_at = "fit"
    selected = "accepted-v144-baseline"
    selected_reason = "fit-no-qualified-pitch-shift-candidate"

    if locked_name != "accepted-v144-baseline":
        locked = next(candidate for candidate in candidates if candidate["name"] == locked_name)
        baseline["validation"] = stage_score_for_events(
            baseline_events, reference_notes, "validation", config
        )
        locked["validation"] = stage_score_for_events(
            locked_events, reference_notes, "validation", config
        )
        validation_gate = gate_locked_candidate(
            baseline,
            locked,
            stage="validation",
            config=config,
        )
        stopped_at = "validation"
        selected_reason = "locked-pitch-shift-candidate-failed-validation"

        if validation_gate["passed"]:
            baseline["canary"] = stage_score_for_events(
                baseline_events, reference_notes, "canary", config
            )
            locked["canary"] = stage_score_for_events(
                locked_events, reference_notes, "canary", config
            )
            canary_gate = gate_locked_candidate(
                baseline,
                locked,
                stage="canary",
                config=config,
            )
            stopped_at = "canary"
            selected_reason = "locked-pitch-shift-candidate-failed-canary"

            if canary_gate["passed"]:
                selected = locked_name
                selected_reason = "locked-pitch-shift-candidate-passed-split-gates-pending-full-invariant"
                stopped_at = "full-calibration"
                selected_full = score_full_candidate(locked_events, reference)
                accepted_full = manifest.get("fullGoldCalibration") or {}
                baseline_metrics = accepted_full.get("gatedMetrics") or {}
                baseline_critical = int(accepted_full.get("criticalMismatchCount") or 0)
                gated_deltas = {
                    metric_name: float(selected_full["gatedMetrics"][metric_name])
                    - float(baseline_metrics[metric_name])
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
                        "criticalMismatchDelta": int(selected_full["criticalMismatchCount"])
                        - baseline_critical,
                    },
                    "pdfEventFidelity": None,
                    "invariantPassed": None,
                }

    args.locked_events.parent.mkdir(parents=True, exist_ok=True)
    args.locked_events.write_text(
        json.dumps(
            {
                "schemaVersion": 14410,
                "instrument": "rhythm",
                "source": "accepted-v144-calibration-baseline",
                "sourceEventSha256": ACCEPTED_EVENT_SHA256,
                "lockedCandidate": locked_name,
                "lockedSignatures": locked_signatures,
                "lockedSemitoneShift": locked_shift,
                "runtimeReferenceInputUsed": False,
                "baselineEventCountPreserved": len(locked_events) == ACCEPTED_EVENT_COUNT,
                "baselineGeneratedMeasureSetPreserved": locked_measure_evidence[
                    "baselineGeneratedMeasureSetPreserved"
                ],
                "renderEvents": locked_events,
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )

    report = {
        "schemaVersion": 14410,
        "classification": "v144-rhythm-fit-only-contextual-pitch-shift-search",
        "evaluationRole": "accepted-v144-baseline-contextual-pitch-correction-gold-calibration",
        "mayClaimUnseenGeneralization": False,
        "candidateConstruction": {
            "sourceBaselineName": ACCEPTED_BASELINE_NAME,
            "sourceBaselineEventCount": ACCEPTED_EVENT_COUNT,
            "sourceBaselineEventSha256": ACCEPTED_EVENT_SHA256,
            "sourceLabels": "accepted-baseline-fit-only-same-onset-generated-reference-substitutions",
            "runtimeRuleInputs": "reference-free-source-pitch-class-plus-structural-context-and-fixed-shift-only",
            "candidateRuleShape": "same-string-contextual-pitch-shift",
            "pairingPolicy": "exact-pitch-removal-then-minimum-absolute-midi-distance-deterministic",
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
            "nonPitchEventMetadataPreservationRequired": True,
            "generatedMeasureSetPreservationRequired": True,
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
            "signatures": locked_signatures,
            "semitoneShift": locked_shift,
            "eventCount": len(locked_events),
            "eventSha256": sha256_json(locked_events),
            "changedEventCount": locked_changed_count,
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
        "safety": safety_payload(
            measure_preserved=True,
            event_count_preserved=True,
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
