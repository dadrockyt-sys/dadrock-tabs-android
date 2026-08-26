from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from canonical import canonical_events, sha256_json  # type: ignore  # noqa: E402
from v144_rhythm_conjunction_prune_policy import (  # noqa: E402
    DEFAULT_MAX_CANDIDATES,
    DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
    apply_conjunction_prune,
    rank_fit_conjunctions,
)
from v144_rhythm_context_split_policy import ContextSplitConfig  # noqa: E402
from v144_rhythm_staged_selector import (  # noqa: E402
    gate_locked_candidate,
    lock_fit_candidate,
)

# Reuse the already-gated scoring/split helpers; importing this module does not execute
# its CLI and does not add any validation/canary inputs to conjunction construction.
from search_single_signature_prunes import (  # noqa: E402
    candidate_safety,
    load_json,
    make_candidate,
    score_notes,
    stage_score_for_events,
    subset,
    unmatched_generated_fit_rows,
)
import score_rhythm_holdout as scorer  # type: ignore  # noqa: E402


def candidate_name(signatures: list[str]) -> str:
    token = "\n".join(sorted(signatures)).encode("utf-8")
    return "prune-conjunction-" + hashlib.sha256(token).hexdigest()[:16]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fit-only V144 search over deterministic two-signature context prunes."
    )
    parser.add_argument("render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
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
    if len(events) != 1209:
        raise ValueError(f"expected immutable V5 baseline stream with 1209 events, got {len(events)}")

    reference = scorer.validate_reference(load_json(args.gold_reference))
    reference_notes, _, _ = scorer.flatten_reference(reference)
    generated_notes, _ = scorer.flatten_generated(events)

    generated_fit = subset(generated_notes, "fit", config)
    reference_fit = subset(reference_notes, "fit", config)
    fit_unmatched_generated = unmatched_generated_fit_rows(generated_fit, reference_fit)

    # This is the complete candidate-construction interface. It accepts only fit rows.
    ranked_rules = rank_fit_conjunctions(
        fit_unmatched_generated,
        generated_fit,
        minimum_false_positive_support=args.minimum_false_positive_support,
        maximum_candidates=args.maximum_candidates,
    )

    baseline_fit = score_notes(generated_fit, reference_fit)
    candidates: list[dict[str, Any]] = [
        make_candidate("no-prune", "baseline", baseline_fit)
    ]
    metadata: dict[str, dict[str, Any]] = {}

    for rule in ranked_rules:
        signatures = [str(value) for value in rule["signatures"]]
        name = candidate_name(signatures)
        if name in metadata:
            raise ValueError(f"conjunction candidate-name collision: {name}")
        pruned_events = apply_conjunction_prune(events, signatures)
        fit_score = stage_score_for_events(pruned_events, reference_notes, "fit", config)
        candidates.append(
            make_candidate(
                name,
                "conjunction::" + " && ".join(signatures),
                fit_score,
            )
        )
        metadata[name] = {
            **rule,
            "removedTotalEventCount": len(events) - len(pruned_events),
            "remainingEventCount": len(pruned_events),
            "candidateEventSha256": sha256_json(pruned_events),
        }

    fit_lock = lock_fit_candidate(candidates, config=config, baseline_name="no-prune")
    locked_name = str(fit_lock["locked"])
    locked_rule = metadata.get(locked_name)
    locked_signatures = None if locked_rule is None else list(locked_rule["signatures"])
    locked_events = (
        events
        if locked_signatures is None
        else apply_conjunction_prune(events, locked_signatures)
    )

    # Validation/canary scoring occurs only after fit has irreversibly locked one rule.
    validation_gate = None
    canary_gate = None
    stopped_at = "fit"
    selected = "no-prune"
    selected_reason = "fit-no-qualified-candidate"

    if locked_name != "no-prune":
        baseline = candidates[0]
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
                selected_reason = "locked-candidate-passed-validation-and-canary"
                stopped_at = "complete"

    args.locked_events.parent.mkdir(parents=True, exist_ok=True)
    args.locked_events.write_text(
        json.dumps(
            {
                "schemaVersion": 14402,
                "instrument": "rhythm",
                "source": "immutable-v5-read-only-baseline",
                "lockedCandidate": locked_name,
                "lockedSignatures": locked_signatures,
                "runtimeReferenceInputUsed": False,
                "renderEvents": locked_events,
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )

    report = {
        "schemaVersion": 14402,
        "classification": "v144-rhythm-fit-only-conjunction-prune-search",
        "evaluationRole": "gold-calibration-fit-lock-then-gates",
        "mayClaimUnseenGeneralization": False,
        "candidateConstruction": {
            "sourceLabels": "fit-only-gross-unmatched-generated-notes",
            "runtimeRuleInputs": "reference-free-context-signature-conjunction-only",
            "candidateRuleShape": "two-signature-conjunction-prune",
            "minimumFalsePositiveSupport": int(args.minimum_false_positive_support),
            "maximumCandidates": int(args.maximum_candidates),
            "candidateCount": len(candidates) - 1,
            "fitUnmatchedGeneratedNoteCount": len(fit_unmatched_generated),
            "validationLabelsUsedForCandidateConstructionOrRanking": False,
            "canaryLabelsUsedForCandidateConstructionOrRanking": False,
            "previousSingleSignatureValidationResultUsedForConstructionOrRanking": False,
        },
        "baseline": {
            "name": "no-prune",
            "fit": baseline_fit,
            "eventCount": len(events),
            "eventSha256": sha256_json(events),
        },
        "fitLock": fit_lock,
        "candidateMetadata": metadata,
        "locked": {
            "name": locked_name,
            "signatures": locked_signatures,
            "eventCount": len(locked_events),
            "eventSha256": sha256_json(locked_events),
        },
        "validation": validation_gate,
        "canary": canary_gate,
        "selected": selected,
        "selectedReason": selected_reason,
        "stoppedAt": stopped_at,
        "promotionAllowed": selected != "no-prune",
        "alternateAfterGateFailureAllowed": False,
        "safety": {
            **candidate_safety(),
            "lockedCandidatePdfFidelityReproofRequired": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
