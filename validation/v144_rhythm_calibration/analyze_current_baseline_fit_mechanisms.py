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
from v144_rhythm_pitch_position_shift_policy import apply_pitch_position_rule  # noqa: E402
from v144_rhythm_pitch_shift_policy import apply_pitch_shift_rule  # noqa: E402
from v144_rhythm_triple_conjunction_policy import apply_triple_prune  # noqa: E402
from analyze_split_baseline import score_subset, split_name  # noqa: E402

SOURCE_EVENT_COUNT = 1209
SOURCE_EVENT_SHA256 = "7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1"
TRIPLE_SIGNATURES = ["register::high", "section16::1", "stepParity::0"]
TRIPLE_EVENT_COUNT = 1144
TRIPLE_EVENT_SHA256 = "68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3"
PITCH_BASELINE_SIGNATURES = ["pitchClass::4", "stepQuarter::0"]
PITCH_BASELINE_SHIFT = -2
PITCH_BASELINE_EVENT_SHA256 = "b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6"
BASELINE_NAME = "pitch-position-shift-54a6e8d3aa91c422"
BASELINE_SIGNATURES = ["pitchClass::11", "stepParity::0"]
BASELINE_SEMITONE_SHIFT = -2
BASELINE_STRING_SHIFT = 1
BASELINE_EVENT_COUNT = 1144
BASELINE_EVENT_SHA256 = "5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d"
BASELINE_MEASURE_COUNT = 113


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


def reconstruct_current_baseline(source_events: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    triple_events = canonical_events(apply_triple_prune(source_events, TRIPLE_SIGNATURES))
    if len(triple_events) != TRIPLE_EVENT_COUNT:
        raise ValueError("historical triple reconstruction event count changed")
    if sha256_json(triple_events) != TRIPLE_EVENT_SHA256:
        raise ValueError("historical triple reconstruction SHA changed")

    pitch_events = canonical_events(
        apply_pitch_shift_rule(
            triple_events,
            PITCH_BASELINE_SIGNATURES,
            PITCH_BASELINE_SHIFT,
        )
    )
    if len(pitch_events) != BASELINE_EVENT_COUNT:
        raise ValueError("previous pitch baseline reconstruction event count changed")
    if sha256_json(pitch_events) != PITCH_BASELINE_EVENT_SHA256:
        raise ValueError("previous pitch baseline reconstruction SHA changed")

    baseline_events = canonical_events(
        apply_pitch_position_rule(
            pitch_events,
            BASELINE_SIGNATURES,
            BASELINE_SEMITONE_SHIFT,
            BASELINE_STRING_SHIFT,
        )
    )
    if len(baseline_events) != BASELINE_EVENT_COUNT:
        raise ValueError("current accepted baseline reconstruction event count changed")
    if sha256_json(baseline_events) != BASELINE_EVENT_SHA256:
        raise ValueError("current accepted baseline reconstruction SHA changed")
    return baseline_events


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fit-only mechanism diagnostic for the current accepted V144 Rhythm pitch-position baseline. "
            "It reconstructs the accepted transform chain but does not construct, rank, select, "
            "validate, canary, or promote any candidate."
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
        raise ValueError("current accepted V144 manifest classification changed")
    if manifest.get("name") != BASELINE_NAME:
        raise ValueError("current accepted V144 baseline name changed")
    transform = manifest.get("transform") or {}
    if transform.get("type") != "contextual-joint-pitch-adjacent-string-position-shift":
        raise ValueError("current accepted V144 transform type changed")
    if transform.get("signatures") != BASELINE_SIGNATURES:
        raise ValueError("current accepted V144 pitch-position signatures changed")
    if int(transform.get("semitoneShift") or 0) != BASELINE_SEMITONE_SHIFT:
        raise ValueError("current accepted V144 semitone shift changed")
    if int(transform.get("stringShift") or 0) != BASELINE_STRING_SHIFT:
        raise ValueError("current accepted V144 string shift changed")
    selected = manifest.get("selectedCandidate") or {}
    if int(selected.get("eventCount") or 0) != BASELINE_EVENT_COUNT:
        raise ValueError("current accepted V144 event count changed")
    if selected.get("eventSha256") != BASELINE_EVENT_SHA256:
        raise ValueError("current accepted V144 event SHA changed")
    if int(selected.get("generatedMeasureCount") or 0) != BASELINE_MEASURE_COUNT:
        raise ValueError("current accepted V144 generated measure count changed")
    promotion = manifest.get("promotionScope") or {}
    if promotion.get("calibrationBaseline") is not True:
        raise ValueError("current accepted V144 manifest is not a calibration baseline")
    if promotion.get("productionPromotionAllowed") is not False:
        raise ValueError("current accepted V144 manifest unexpectedly allows Production promotion")

    v5_stream = load_json(args.v5_render_stream)
    source_events = canonical_events(v5_stream.get("events") or [])
    if len(source_events) != SOURCE_EVENT_COUNT:
        raise ValueError("immutable V5 event count changed")
    if sha256_json(source_events) != SOURCE_EVENT_SHA256:
        raise ValueError("immutable V5 event SHA changed")

    baseline_events = reconstruct_current_baseline(source_events)
    measure_evidence = measure_set_evidence(baseline_events, baseline_events)
    if measure_evidence["baselineGeneratedMeasureSetPreserved"] is not True:
        raise ValueError("current accepted baseline failed self measure preservation")
    if measure_evidence["baselineGeneratedMeasureCount"] != BASELINE_MEASURE_COUNT:
        raise ValueError("current accepted baseline must retain 113 generated measures")

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

    report = {
        "schemaVersion": 14415,
        "classification": "v144-rhythm-current-baseline-fit-error-mechanisms",
        "evaluationRole": "gold-calibration-fit-only-current-baseline-mechanism-diagnostic",
        "mayClaimUnseenGeneralization": False,
        "candidateConstructionPerformed": False,
        "candidateRankingPerformed": False,
        "candidateSelectionPerformed": False,
        "validationLabelsUsedForDiagnostic": False,
        "canaryLabelsUsedForDiagnostic": False,
        "baseline": {
            "name": BASELINE_NAME,
            "eventCount": BASELINE_EVENT_COUNT,
            "eventSha256": BASELINE_EVENT_SHA256,
            "generatedMeasureCount": BASELINE_MEASURE_COUNT,
            "baselineGeneratedMeasureSetPreserved": True,
            "reconstructionChain": [
                {
                    "type": "triple-conjunction-prune",
                    "signatures": TRIPLE_SIGNATURES,
                    "outputEventSha256": TRIPLE_EVENT_SHA256,
                },
                {
                    "type": "same-string-contextual-pitch-shift",
                    "signatures": PITCH_BASELINE_SIGNATURES,
                    "semitoneShift": PITCH_BASELINE_SHIFT,
                    "outputEventSha256": PITCH_BASELINE_EVENT_SHA256,
                },
                {
                    "type": "contextual-joint-pitch-adjacent-string-position-shift",
                    "signatures": BASELINE_SIGNATURES,
                    "semitoneShift": BASELINE_SEMITONE_SHIFT,
                    "stringShift": BASELINE_STRING_SHIFT,
                    "outputEventSha256": BASELINE_EVENT_SHA256,
                },
            ],
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
            "sameMeasurePitchMatchesDisplacedFromExactOnset": max(0, pitch_matched - onset["exactOnsetExactPitchNotes"]),
            "samePitchTimingMatchesRecoveredOnlyByGrossTwoStepTolerance": max(0, gross_matched - tight_matched),
            "sameMeasurePitchMatchesStillOutsideGrossTwoStepToleranceOrCompeting": max(0, pitch_matched - gross_matched),
            "correctPitchTimingButWrongStringFret": max(0, tight_matched - position_matched),
            "grossUnmatchedGeneratedNotes": generated_count - gross_matched,
            "grossUnmatchedReferenceNotes": reference_count - gross_matched,
            "pitchContentFalsePositiveNotes": generated_count - pitch_matched,
            "pitchContentFalseNegativeNotes": reference_count - pitch_matched,
        },
        "fitOnlyOracles": {
            "interpretation": (
                "Diagnostic ceilings only. They use current-baseline fit labels and may not be implemented "
                "as runtime rules, used to change fixed selector thresholds, or represented as generalization evidence."
            ),
            "perfectPitchFalsePositiveDeletion": {
                "pitchContentF1Ceiling": f1_from_matched(pitch_matched, pitch_matched, reference_count),
            },
            "perfectCountPreservingPitchCorrection": {
                "pitchContentF1Ceiling": f1_from_matched(min(generated_count, reference_count), generated_count, reference_count),
            },
            "perfectTimingAlignmentOfExistingPitchContentMatches": {
                "matchedNotesHeldConstant": pitch_matched,
                "pitchTimingF1Ceiling": f1_from_matched(pitch_matched, generated_count, reference_count),
            },
            "perfectStringFretRemapOfCurrentTightPitchMatches": {
                "matchedNotesHeldConstant": tight_matched,
                "stringFretTimingF1Ceiling": f1_from_matched(tight_matched, generated_count, reference_count),
            },
        },
        "nextFamilyShapeSignals": {
            "timingOpportunityExistingPitchMatches": max(0, pitch_matched - tight_matched),
            "positionOpportunityWithinTightPitchMatches": max(0, tight_matched - position_matched),
            "sameOnsetPitchSubstitutionOpportunity": onset["sameOnsetWrongPitchSubstitutionSlots"],
            "diagnosticOnly": True,
        },
        "constructionBoundary": {
            "currentBaselineFitLabelsMayInformNextFamilyShape": True,
            "validationLabelsMayInformNextFamilyShape": False,
            "canaryLabelsMayInformNextFamilyShape": False,
            "consumedFamiliesMayBeReplayedOrRetuned": False,
            "runtimeReferenceInputAllowed": False,
            "fixedSelectorThresholdsMayBeChangedFromThisDiagnostic": False,
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
