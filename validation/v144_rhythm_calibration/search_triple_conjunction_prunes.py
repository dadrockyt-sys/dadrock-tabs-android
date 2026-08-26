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
from v144_rhythm_staged_selector import (  # noqa: E402
    gate_locked_candidate,
    lock_fit_candidate,
)
from v144_rhythm_triple_conjunction_policy import (  # noqa: E402
    DEFAULT_MAX_CANDIDATES,
    DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
    apply_triple_prune,
    rank_fit_triples,
)
from search_single_signature_prunes import (  # noqa: E402
    load_json,
    score_notes,
    stage_score_for_events,
    subset,
    unmatched_generated_fit_rows,
)
from score_selected_conjunction_candidate import score_full_candidate  # noqa: E402

BASELINE_EVENT_SHA256 = "7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1"
EXPECTED_BASELINE_EVENT_COUNT = 1209


def candidate_name(signatures: list[str]) -> str:
    token = "\n".join(sorted(signatures)).encode("utf-8")
    return "prune-triple-" + hashlib.sha256(token).hexdigest()[:16]


def safety_payload(*, measure_preserved: bool) -> dict[str, Any]:
    return {
        "v5Modified": False,
        "productionModified": False,
        "mainModified": False,
        "runtimeReferenceInputUsed": False,
        "modalGpuInvoked": False,
        "deterministic": True,
        "baselineGeneratedMeasureSetPreserved": bool(measure_preserved),
    }


def make_candidate(
    name: str,
    policy: str,
    fit: Mapping[str, Any],
    *,
    measure_preserved: bool,
) -> dict[str, Any]:
    return {
        "name": name,
        "policy": policy,
        "fit": dict(fit),
        "holdout": None,
        "safety": safety_payload(measure_preserved=measure_preserved),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fit-only V144 search over measure-safe three-signature context prunes."
    )
    parser.add_argument("render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("baseline_report", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("locked_events", type=Path)
    parser.add_argument(
        "--minimum-false-positive-support",
        type=int,
        default=DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
    )
    parser.add_argument(
        "--maximum-candidates", type=int, default=DEFAULT_MAX_CANDIDATES
    )
    args = parser.parse_args()

    config = ContextSplitConfig.from_mapping(load_json(args.config))
    stream = load_json(args.render_stream)
    events = canonical_events(stream.get("events") or [])
    if len(events) != EXPECTED_BASELINE_EVENT_COUNT:
        raise ValueError(f"expected {EXPECTED_BASELINE_EVENT_COUNT} baseline events, got {len(events)}")
    if sha256_json(events) != BASELINE_EVENT_SHA256:
        raise ValueError("immutable V5 canonical event identity changed")

    baseline_measure_evidence = measure_set_evidence(events, events)
    if not baseline_measure_evidence["baselineGeneratedMeasureSetPreserved"]:
        raise ValueError("baseline measure set failed self-preservation")
    if baseline_measure_evidence["baselineGeneratedMeasureCount"] != 113:
        raise ValueError("immutable V5 baseline must span exactly 113 generated measures")

    reference = scorer.validate_reference(load_json(args.gold_reference))
    reference_notes, _, _ = scorer.flatten_reference(reference)
    generated_notes, _ = scorer.flatten_generated(events)
    generated_fit = subset(generated_notes, "fit", config)
    reference_fit = subset(reference_notes, "fit", config)
    fit_unmatched_generated = unmatched_generated_fit_rows(generated_fit, reference_fit)

    ranked_rules = rank_fit_triples(
        fit_unmatched_generated,
        generated_fit,
        minimum_false_positive_support=args.minimum_false_positive_support,
        maximum_candidates=args.maximum_candidates,
    )

    baseline_fit = score_notes(generated_fit, reference_fit)
    baseline = make_candidate(
        "no-prune", "baseline", baseline_fit, measure_preserved=True
    )
    candidates: list[dict[str, Any]] = [baseline]
    metadata: dict[str, dict[str, Any]] = {}

    for rule in ranked_rules:
        signatures = [str(value) for value in rule["signatures"]]
        name = candidate_name(signatures)
        if name in metadata:
            raise ValueError(f"triple candidate-name collision: {name}")
        pruned_events = apply_triple_prune(events, signatures)
        measure_evidence = measure_set_evidence(events, pruned_events)
        fit_score = stage_score_for_events(pruned_events, reference_notes, "fit", config)
        candidates.append(
            make_candidate(
                name,
                "triple-conjunction::" + " && ".join(signatures),
                fit_score,
                measure_preserved=bool(
                    measure_evidence["baselineGeneratedMeasureSetPreserved"]
                ),
            )
        )
        metadata[name] = {
            **rule,
            "removedTotalEventCount": len(events) - len(pruned_events),
            "remainingEventCount": len(pruned_events),
            "candidateEventSha256": sha256_json(pruned_events),
            "measureSet": {
                "baselineGeneratedMeasureCount": measure_evidence[
                    "baselineGeneratedMeasureCount"
                ],
                "candidateGeneratedMeasureCount": measure_evidence[
                    "candidateGeneratedMeasureCount"
                ],
                "missingBaselineGeneratedMeasures": measure_evidence[
                    "missingBaselineGeneratedMeasures"
                ],
                "extraCandidateGeneratedMeasures": measure_evidence[
                    "extraCandidateGeneratedMeasures"
                ],
                "baselineGeneratedMeasureSetPreserved": measure_evidence[
                    "baselineGeneratedMeasureSetPreserved"
                ],
                "professionalReferenceUsed": False,
            },
        }

    fit_lock = lock_fit_candidate(candidates, config=config, baseline_name="no-prune")
    locked_name = str(fit_lock["locked"])
    locked_rule = metadata.get(locked_name)
    locked_signatures = None if locked_rule is None else list(locked_rule["signatures"])
    locked_events = (
        events
        if locked_signatures is None
        else apply_triple_prune(events, locked_signatures)
    )
    locked_measure_evidence = measure_set_evidence(events, locked_events)
    if not locked_measure_evidence["baselineGeneratedMeasureSetPreserved"]:
        raise ValueError("selector locked a candidate that violates measure-set preservation")

    validation_gate = None
    canary_gate = None
    full_calibration = None
    stopped_at = "fit"
    selected = "no-prune"
    selected_reason = "fit-no-qualified-candidate"

    if locked_name != "no-prune":
        locked = next(candidate for candidate in candidates if candidate["name"] == locked_name)
        baseline["validation"] = stage_score_for_events(
            events, reference_notes, "validation", config
        )
        locked["validation"] = stage_score_for_events(
            locked_events, reference_notes, "validation", config
        )
        validation_gate = gate_locked_candidate(
            baseline, locked, stage="validation", config=config
        )
        stopped_at = "validation"
        selected_reason = "locked-candidate-failed-validation"

        if validation_gate["passed"]:
            baseline["canary"] = stage_score_for_events(
                events, reference_notes, "canary", config
            )
            locked["canary"] = stage_score_for_events(
                locked_events, reference_notes, "canary", config
            )
            canary_gate = gate_locked_candidate(
                baseline, locked, stage="canary", config=config
            )
            stopped_at = "canary"
            selected_reason = "locked-candidate-failed-canary"

            if canary_gate["passed"]:
                selected = locked_name
                selected_reason = "locked-candidate-passed-split-gates-pending-full-invariant"
                stopped_at = "full-calibration"
                selected_full = score_full_candidate(locked_events, reference)
                baseline_report = load_json(args.baseline_report)
                baseline_metrics = (baseline_report.get("baseline") or {}).get(
                    "gatedMetrics"
                ) or {}
                baseline_critical = int(
                    (baseline_report.get("baseline") or {}).get("criticalMismatchCount")
                    or 0
                )
                gated_deltas = {
                    name: float(selected_full["gatedMetrics"][name])
                    - float(baseline_metrics[name])
                    for name in (
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
                        "gatedMetricDeltas": gated_deltas,
                        "criticalMismatchDelta": int(
                            selected_full["criticalMismatchCount"]
                        )
                        - baseline_critical,
                    },
                    "pdfEventFidelity": None,
                    "invariantPassed": None,
                }

    args.locked_events.parent.mkdir(parents=True, exist_ok=True)
    args.locked_events.write_text(
        json.dumps(
            {
                "schemaVersion": 14405,
                "instrument": "rhythm",
                "source": "immutable-v5-read-only-baseline",
                "lockedCandidate": locked_name,
                "lockedSignatures": locked_signatures,
                "runtimeReferenceInputUsed": False,
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
        "schemaVersion": 14405,
        "classification": "v144-rhythm-fit-only-measure-safe-triple-conjunction-search",
        "evaluationRole": "gold-calibration-fit-lock-then-gates-then-full-invariant",
        "mayClaimUnseenGeneralization": False,
        "candidateConstruction": {
            "sourceLabels": "fit-only-gross-unmatched-generated-notes",
            "runtimeRuleInputs": "reference-free-context-signature-triple-only",
            "candidateRuleShape": "three-signature-conjunction-prune",
            "minimumFalsePositiveSupport": int(args.minimum_false_positive_support),
            "maximumCandidates": int(args.maximum_candidates),
            "candidateCount": len(candidates) - 1,
            "fitUnmatchedGeneratedNoteCount": len(fit_unmatched_generated),
            "validationLabelsUsedForCandidateConstructionOrRanking": False,
            "canaryLabelsUsedForCandidateConstructionOrRanking": False,
            "historicalValidationOrFullInvariantResultsUsedForConstructionOrRanking": False,
            "measureSetGuardUsesProfessionalReference": False,
        },
        "baseline": {
            "name": "no-prune",
            "fit": baseline_fit,
            "eventCount": len(events),
            "eventSha256": sha256_json(events),
            "generatedMeasureCount": 113,
        },
        "fitLock": fit_lock,
        "candidateMetadata": metadata,
        "locked": {
            "name": locked_name,
            "signatures": locked_signatures,
            "eventCount": len(locked_events),
            "eventSha256": sha256_json(locked_events),
            "measureSet": {
                "baselineGeneratedMeasureCount": locked_measure_evidence[
                    "baselineGeneratedMeasureCount"
                ],
                "candidateGeneratedMeasureCount": locked_measure_evidence[
                    "candidateGeneratedMeasureCount"
                ],
                "missingBaselineGeneratedMeasures": locked_measure_evidence[
                    "missingBaselineGeneratedMeasures"
                ],
                "extraCandidateGeneratedMeasures": locked_measure_evidence[
                    "extraCandidateGeneratedMeasures"
                ],
                "baselineGeneratedMeasureSetPreserved": locked_measure_evidence[
                    "baselineGeneratedMeasureSetPreserved"
                ],
                "professionalReferenceUsed": False,
            },
        },
        "validation": validation_gate,
        "canary": canary_gate,
        "fullCalibration": full_calibration,
        "selected": selected,
        "selectedReason": selected_reason,
        "stoppedAt": stopped_at,
        "splitPromotionAllowed": selected != "no-prune",
        "calibrationPromotionAllowed": False,
        "alternateAfterGateFailureAllowed": False,
        "safety": safety_payload(measure_preserved=True),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
