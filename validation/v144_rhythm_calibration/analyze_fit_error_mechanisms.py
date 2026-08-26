from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
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
from v144_rhythm_triple_conjunction_policy import apply_triple_prune  # noqa: E402
from analyze_split_baseline import score_subset, split_name  # noqa: E402

SOURCE_EVENT_COUNT = 1209
SOURCE_EVENT_SHA256 = "7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1"
BASELINE_NAME = "prune-triple-67348efe50436fc5"
BASELINE_SIGNATURES = ["register::high", "section16::1", "stepParity::0"]
BASELINE_EVENT_COUNT = 1144
BASELINE_EVENT_SHA256 = "68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def f1_from_matched(matched: int, generated: int, reference: int) -> float:
    if generated + reference == 0:
        return 1.0
    return 2.0 * float(matched) / float(generated + reference)


def same_onset_pitch_mechanisms(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    generated_by_onset: dict[tuple[int, int], Counter[int]] = defaultdict(Counter)
    reference_by_onset: dict[tuple[int, int], Counter[int]] = defaultdict(Counter)
    for row in generated_notes:
        generated_by_onset[(int(row["measure"]), int(row["step"]))][int(row["midi"])] += 1
    for row in reference_notes:
        reference_by_onset[(int(row["measure"]), int(row["step"]))][int(row["midi"])] += 1

    exact = 0
    wrong_pitch_slots = 0
    extra_generated_slots = 0
    missing_reference_slots = 0
    for onset in sorted(set(generated_by_onset) | set(reference_by_onset)):
        generated = generated_by_onset[onset]
        reference = reference_by_onset[onset]
        shared = generated & reference
        exact_here = sum(shared.values())
        exact += exact_here
        generated_remaining = sum(generated.values()) - exact_here
        reference_remaining = sum(reference.values()) - exact_here
        substitutions = min(generated_remaining, reference_remaining)
        wrong_pitch_slots += substitutions
        extra_generated_slots += generated_remaining - substitutions
        missing_reference_slots += reference_remaining - substitutions

    return {
        "exactOnsetExactPitchNotes": exact,
        "sameOnsetWrongPitchSubstitutionSlots": wrong_pitch_slots,
        "sameOnsetExtraGeneratedSlotsAfterSubstitution": extra_generated_slots,
        "sameOnsetMissingReferenceSlotsAfterSubstitution": missing_reference_slots,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fit-only mechanism diagnostic for the accepted V144 1144-event Rhythm baseline. "
            "This does not construct, rank, select, or promote a candidate."
        )
    )
    parser.add_argument("v5_render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("accepted_manifest", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    manifest = load_json(args.accepted_manifest)
    if manifest.get("classification") != "v144-rhythm-selected-calibration-baseline":
        raise ValueError("accepted V144 manifest classification changed")
    if manifest.get("name") != BASELINE_NAME:
        raise ValueError("accepted V144 baseline name changed")
    if (manifest.get("transform") or {}).get("signatures") != BASELINE_SIGNATURES:
        raise ValueError("accepted V144 baseline signatures changed")
    selected = manifest.get("selectedCandidate") or {}
    if int(selected.get("eventCount") or 0) != BASELINE_EVENT_COUNT:
        raise ValueError("accepted V144 baseline event count changed")
    if selected.get("eventSha256") != BASELINE_EVENT_SHA256:
        raise ValueError("accepted V144 baseline event SHA changed")
    if (manifest.get("promotionScope") or {}).get("calibrationBaseline") is not True:
        raise ValueError("accepted V144 manifest is not a calibration baseline")

    v5_stream = load_json(args.v5_render_stream)
    source_events = canonical_events(v5_stream.get("events") or [])
    if len(source_events) != SOURCE_EVENT_COUNT:
        raise ValueError("immutable V5 event count changed")
    if sha256_json(source_events) != SOURCE_EVENT_SHA256:
        raise ValueError("immutable V5 event SHA changed")

    baseline_events = apply_triple_prune(source_events, BASELINE_SIGNATURES)
    if len(baseline_events) != BASELINE_EVENT_COUNT:
        raise ValueError("accepted baseline reconstruction event count changed")
    if sha256_json(baseline_events) != BASELINE_EVENT_SHA256:
        raise ValueError("accepted baseline reconstruction SHA changed")
    measure_evidence = measure_set_evidence(baseline_events, baseline_events)
    if measure_evidence["baselineGeneratedMeasureSetPreserved"] is not True:
        raise ValueError("accepted baseline failed self measure preservation")
    if measure_evidence["baselineGeneratedMeasureCount"] != 113:
        raise ValueError("accepted baseline must retain 113 generated measures")

    config = ContextSplitConfig.from_mapping(load_json(args.config))
    reference = scorer.validate_reference(load_json(args.gold_reference))
    reference_notes, _, _ = scorer.flatten_reference(reference)
    generated_notes, _ = scorer.flatten_generated(baseline_events)

    fit_generated = [row for row in generated_notes if split_name(row, config) == "fit"]
    fit_reference = [row for row in reference_notes if split_name(row, config) == "fit"]
    fit_score = score_subset(fit_generated, fit_reference)

    pitch_content = scorer.multiset_match(
        ((row["measure"], row["midi"]) for row in fit_generated),
        ((row["measure"], row["midi"]) for row in fit_reference),
    )
    tight_pitch_pairs = scorer.greedy_match(
        fit_generated,
        fit_reference,
        lambda generated, ref: generated["midi"] == ref["midi"],
        scorer.STEP_TOLERANCE,
    )
    gross_pitch_pairs = scorer.greedy_match(
        fit_generated,
        fit_reference,
        lambda generated, ref: generated["midi"] == ref["midi"],
        scorer.GROSS_STEP_TOLERANCE,
    )
    position_pairs = scorer.greedy_match(
        fit_generated,
        fit_reference,
        lambda generated, ref: (
            generated["midi"] == ref["midi"]
            and generated["stringIndex"] == ref["stringIndex"]
            and generated["fret"] == ref["fret"]
        ),
        scorer.STEP_TOLERANCE,
    )
    onset = same_onset_pitch_mechanisms(fit_generated, fit_reference)

    generated_count = len(fit_generated)
    reference_count = len(fit_reference)
    pitch_matched = int(pitch_content["matched"])
    tight_matched = len(tight_pitch_pairs)
    gross_matched = len(gross_pitch_pairs)
    position_matched = len(position_pairs)

    pruning_pitch_generated = pitch_matched
    pruning_gross_generated = gross_matched
    report = {
        "schemaVersion": 14409,
        "classification": "v144-rhythm-accepted-baseline-fit-error-mechanisms",
        "evaluationRole": "gold-calibration-fit-only-mechanism-diagnostic",
        "mayClaimUnseenGeneralization": False,
        "candidateConstructionPerformed": False,
        "candidateRankingPerformed": False,
        "candidateSelectionPerformed": False,
        "baseline": {
            "name": BASELINE_NAME,
            "eventCount": BASELINE_EVENT_COUNT,
            "eventSha256": BASELINE_EVENT_SHA256,
            "generatedMeasureCount": 113,
            "baselineGeneratedMeasureSetPreserved": True,
        },
        "fit": {
            "generatedNoteCount": generated_count,
            "referenceNoteCount": reference_count,
            "score": fit_score,
            "pitchContentMatchedNotes": pitch_matched,
            "tightPitchTimingMatchedNotes": tight_matched,
            "grossPitchTimingMatchedNotes": gross_matched,
            "exactStringFretTimingMatchedNotes": position_matched,
        },
        "mechanisms": {
            **onset,
            "sameMeasurePitchMatchesDisplacedFromExactOnset": max(
                0, pitch_matched - onset["exactOnsetExactPitchNotes"]
            ),
            "samePitchTimingMatchesRecoveredOnlyByGrossTwoStepTolerance": max(
                0, gross_matched - tight_matched
            ),
            "sameMeasurePitchMatchesStillOutsideGrossTwoStepToleranceOrCompeting": max(
                0, pitch_matched - gross_matched
            ),
            "correctPitchTimingButWrongStringFret": max(0, tight_matched - position_matched),
            "grossUnmatchedGeneratedNotes": generated_count - gross_matched,
            "grossUnmatchedReferenceNotes": reference_count - gross_matched,
            "pitchContentFalsePositiveNotes": generated_count - pitch_matched,
            "pitchContentFalseNegativeNotes": reference_count - pitch_matched,
        },
        "fitOnlyOracles": {
            "interpretation": (
                "Diagnostic ceilings only. They use fit labels and may not be implemented as runtime rules, "
                "used to change fixed selector thresholds, or represented as generalization evidence."
            ),
            "perfectPitchFalsePositiveDeletion": {
                "deletedGeneratedNotes": generated_count - pitch_matched,
                "remainingGeneratedNotes": pruning_pitch_generated,
                "matchedNotesHeldConstant": pitch_matched,
                "pitchContentF1Ceiling": f1_from_matched(
                    pitch_matched, pruning_pitch_generated, reference_count
                ),
            },
            "perfectGrossUnmatchedDeletion": {
                "deletedGeneratedNotes": generated_count - gross_matched,
                "remainingGeneratedNotes": pruning_gross_generated,
                "matchedNotesHeldConstant": gross_matched,
                "grossPitchTimingF1Ceiling": f1_from_matched(
                    gross_matched, pruning_gross_generated, reference_count
                ),
            },
            "perfectCountPreservingPitchCorrection": {
                "maximumMatchedNotesIgnoringRuntimeFeasibility": min(
                    generated_count, reference_count
                ),
                "pitchContentF1Ceiling": f1_from_matched(
                    min(generated_count, reference_count), generated_count, reference_count
                ),
            },
        },
        "constructionBoundary": {
            "fitLabelsUsedForThisDiagnostic": True,
            "validationLabelsUsedForThisDiagnostic": False,
            "canaryLabelsUsedForThisDiagnostic": False,
            "historicalConsumedFamilyOutcomesUsedToComputeMechanisms": False,
            "runtimeReferenceInputAllowed": False,
            "fixedSelectorThresholdsMayBeChangedFromThisDiagnostic": False,
            "consumedFamilyRunnerUpSelectionAllowed": False,
            "nextFamilyMustBeMateriallyNewAndPreRegistered": True,
        },
        "safety": {
            "v5Modified": False,
            "mainModified": False,
            "productionModified": False,
            "runtimeReferenceInputUsed": False,
            "modalGpuInvoked": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
