from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
MODAL_DIR = ROOT / "modal"
for entry in (HOLDOUT_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import score_rhythm_holdout as scorer  # noqa: E402
from canonical import canonical_events, sha256_json  # noqa: E402
from v144_rhythm_context_split_policy import (  # noqa: E402
    ContextSplitConfig,
    context_signature,
    split_for_location,
)
from v144_rhythm_staged_selector import (  # noqa: E402
    gate_locked_candidate,
    lock_fit_candidate,
)

STAGES = ("fit", "validation", "canary")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def split_name(row: Mapping[str, Any], config: ContextSplitConfig) -> str:
    return split_for_location(
        int(row["measure"]),
        int(row["step"]),
        seed=config.split_seed,
        fit_percent=config.fit_percent,
        validation_percent=config.validation_percent,
    )


def subset(rows: Sequence[Mapping[str, Any]], stage: str, config: ContextSplitConfig):
    return [row for row in rows if split_name(row, config) == stage]


def metric_for_pairs(pairs, generated, reference):
    return scorer.metric_for_pairs(pairs, generated, reference)


def score_notes(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    pitch_content = scorer.multiset_match(
        ((row["measure"], row["midi"]) for row in generated_notes),
        ((row["measure"], row["midi"]) for row in reference_notes),
    )
    pitch_pairs = scorer.greedy_match(
        generated_notes,
        reference_notes,
        lambda generated, ref: generated["midi"] == ref["midi"],
        scorer.STEP_TOLERANCE,
    )
    position_pairs = scorer.greedy_match(
        generated_notes,
        reference_notes,
        lambda generated, ref: (
            generated["midi"] == ref["midi"]
            and generated["stringIndex"] == ref["stringIndex"]
            and generated["fret"] == ref["fret"]
        ),
        scorer.STEP_TOLERANCE,
    )
    gross_pairs = scorer.greedy_match(
        generated_notes,
        reference_notes,
        lambda generated, ref: generated["midi"] == ref["midi"],
        scorer.GROSS_STEP_TOLERANCE,
    )
    generated_onsets = scorer.onset_groups(generated_notes)
    reference_onsets = scorer.onset_groups(reference_notes)
    pitchset_pairs = scorer.greedy_match(
        generated_onsets,
        reference_onsets,
        lambda generated, ref: generated["pitchSet"] == ref["pitchSet"],
        scorer.STEP_TOLERANCE,
    )
    voicing_pairs = scorer.greedy_match(
        generated_onsets,
        reference_onsets,
        lambda generated, ref: generated["voicing"] == ref["voicing"],
        scorer.STEP_TOLERANCE,
    )
    pitch_timing = metric_for_pairs(pitch_pairs, generated_notes, reference_notes)
    position_timing = metric_for_pairs(position_pairs, generated_notes, reference_notes)
    pitchset = metric_for_pairs(pitchset_pairs, generated_onsets, reference_onsets)
    voicing = metric_for_pairs(voicing_pairs, generated_onsets, reference_onsets)
    critical = (
        len(generated_notes) - len(gross_pairs)
        + len(reference_notes) - len(gross_pairs)
    )
    return {
        "gatedMetrics": {
            "pitchContentF1": float(pitch_content["f1"]),
            "pitchTimingTolerantF1": float(pitch_timing["f1"]),
            "stringFretTimingTolerantF1": float(position_timing["f1"]),
            "chordPitchSetTolerantF1": float(pitchset["f1"]),
            "exactVoicingTolerantF1": float(voicing["f1"]),
            # Search candidates are canonical renderer events. The locked stream is
            # independently re-proven with verify_pdf_event_fidelity.py before any
            # result can be treated as promotion evidence.
            "pdfEventFidelity": 1.0,
        },
        "criticalMismatchCount": int(critical),
        "counts": {
            "generatedNotes": len(generated_notes),
            "referenceNotes": len(reference_notes),
            "grossMatchedNotes": len(gross_pairs),
        },
    }


def unmatched_generated_fit_rows(
    generated_fit: Sequence[Mapping[str, Any]],
    reference_fit: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    pairs = scorer.greedy_match(
        generated_fit,
        reference_fit,
        lambda generated, ref: generated["midi"] == ref["midi"],
        scorer.GROSS_STEP_TOLERANCE,
    )
    matched_generated = {generated_index for generated_index, _ in pairs}
    return [
        row for index, row in enumerate(generated_fit)
        if index not in matched_generated
    ]


def candidate_name(signature: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", signature).strip("-").lower()
    return f"prune-{slug}"


def apply_signature_prune(
    events: Sequence[Mapping[str, Any]], signature: str
) -> list[dict[str, Any]]:
    """Runtime-safe rule: prune using only candidate event context, never reference data."""
    kept: list[dict[str, Any]] = []
    for event in canonical_events(events):
        if signature in context_signature(event):
            continue
        kept.append(event)
    return kept


def candidate_safety() -> dict[str, Any]:
    return {
        "v5Modified": False,
        "productionModified": False,
        "mainModified": False,
        "runtimeReferenceInputUsed": False,
        "modalGpuInvoked": False,
        "deterministic": True,
    }


def make_candidate(name: str, policy: str, fit: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "policy": policy,
        "fit": fit,
        "holdout": None,
        "safety": candidate_safety(),
    }


def stage_score_for_events(
    events: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
    stage: str,
    config: ContextSplitConfig,
) -> dict[str, Any]:
    notes, _ = scorer.flatten_generated(events)
    return score_notes(subset(notes, stage, config), subset(reference_notes, stage, config))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fit-only V144 search over single reference-free context-signature prunes."
    )
    parser.add_argument("render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("locked_events", type=Path)
    parser.add_argument("--maximum-candidates", type=int, default=96)
    args = parser.parse_args()

    config = ContextSplitConfig.from_mapping(load_json(args.config))
    stream = load_json(args.render_stream)
    events = canonical_events(stream.get("events") or [])
    if len(events) != 1209:
        raise ValueError(f"expected immutable V5 baseline stream with 1209 events, got {len(events)}")
    reference = scorer.validate_reference(load_json(args.gold_reference))
    reference_notes, _, _ = scorer.flatten_reference(reference)
    generated_notes, _ = scorer.flatten_generated(events)

    # Candidate construction is FIT ONLY. Non-fit reference rows are not consumed by
    # candidate generation, scoring, or ranking below.
    generated_fit = subset(generated_notes, "fit", config)
    reference_fit = subset(reference_notes, "fit", config)
    fit_unmatched_generated = unmatched_generated_fit_rows(generated_fit, reference_fit)

    support: Counter[str] = Counter()
    for row in fit_unmatched_generated:
        support.update(context_signature(row))
    ranked_signatures = sorted(support, key=lambda signature: (-support[signature], signature))
    ranked_signatures = ranked_signatures[: max(1, int(args.maximum_candidates))]

    baseline_fit = score_notes(generated_fit, reference_fit)
    candidates: list[dict[str, Any]] = [make_candidate("no-prune", "baseline", baseline_fit)]
    candidate_metadata: dict[str, dict[str, Any]] = {}

    for signature in ranked_signatures:
        pruned_events = apply_signature_prune(events, signature)
        fit_score = stage_score_for_events(pruned_events, reference_notes, "fit", config)
        name = candidate_name(signature)
        candidates.append(make_candidate(name, f"single-signature::{signature}", fit_score))
        candidate_metadata[name] = {
            "signature": signature,
            "fitFalsePositiveSupport": int(support[signature]),
            "removedTotalEventCount": len(events) - len(pruned_events),
            "remainingEventCount": len(pruned_events),
            "candidateEventSha256": sha256_json(pruned_events),
        }

    fit_lock = lock_fit_candidate(candidates, config=config, baseline_name="no-prune")
    locked_name = str(fit_lock["locked"])
    locked_signature = candidate_metadata.get(locked_name, {}).get("signature")
    locked_events = (
        events if locked_name == "no-prune"
        else apply_signature_prune(events, str(locked_signature))
    )

    # Later stages are intentionally absent until the fit lock exists. If fit chooses
    # no-prune, validation/canary are never scored at all.
    validation_gate = None
    canary_gate = None
    stopped_at = "fit"
    selected = "no-prune"
    selected_reason = "fit-no-qualified-candidate"

    if locked_name != "no-prune":
        baseline = candidates[0]
        locked = next(candidate for candidate in candidates if candidate["name"] == locked_name)

        baseline["validation"] = stage_score_for_events(events, reference_notes, "validation", config)
        locked["validation"] = stage_score_for_events(locked_events, reference_notes, "validation", config)
        validation_gate = gate_locked_candidate(
            baseline, locked, stage="validation", config=config
        )
        stopped_at = "validation"
        selected_reason = "locked-candidate-failed-validation"

        if validation_gate["passed"]:
            baseline["canary"] = stage_score_for_events(events, reference_notes, "canary", config)
            locked["canary"] = stage_score_for_events(locked_events, reference_notes, "canary", config)
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
                "schemaVersion": 14401,
                "instrument": "rhythm",
                "source": "immutable-v5-read-only-baseline",
                "lockedCandidate": locked_name,
                "lockedSignature": locked_signature,
                "runtimeReferenceInputUsed": False,
                "renderEvents": locked_events,
            },
            separators=(",", ":"),
        ) + "\n",
        encoding="utf-8",
    )

    report = {
        "schemaVersion": 14401,
        "classification": "v144-rhythm-fit-only-single-signature-prune-search",
        "evaluationRole": "gold-calibration-fit-lock-then-gates",
        "mayClaimUnseenGeneralization": False,
        "candidateConstruction": {
            "sourceLabels": "fit-only-gross-unmatched-generated-notes",
            "runtimeRuleInputs": "reference-free-context-signature-only",
            "candidateRuleShape": "single-signature-prune",
            "candidateCount": len(candidates) - 1,
            "fitUnmatchedGeneratedNoteCount": len(fit_unmatched_generated),
            "validationLabelsUsedForCandidateConstructionOrRanking": False,
            "canaryLabelsUsedForCandidateConstructionOrRanking": False,
        },
        "baseline": {
            "name": "no-prune",
            "fit": baseline_fit,
            "eventCount": len(events),
            "eventSha256": sha256_json(events),
        },
        "fitLock": fit_lock,
        "candidateMetadata": candidate_metadata,
        "locked": {
            "name": locked_name,
            "signature": locked_signature,
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
            "v5Modified": False,
            "productionModified": False,
            "mainModified": False,
            "runtimeReferenceInputUsed": False,
            "modalGpuInvoked": False,
            "lockedCandidatePdfFidelityReproofRequired": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
