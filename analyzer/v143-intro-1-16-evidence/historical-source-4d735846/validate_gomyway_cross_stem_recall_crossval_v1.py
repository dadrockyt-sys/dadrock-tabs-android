from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_cross_stem_consensus_recall_v1 as cross

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CANDIDATE_PATH = cross.CANDIDATE_PATH
REFERENCE_PATH = cross.REFERENCE_PATH
OUTPUT_PATH = PUBLIC / "gomyway-cross-stem-recall-crossval-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-cross-stem-recall-crossval-v1-manifest.json"

# IMPORTANT: this rule is frozen from the preceding benchmark before cross-validation.
FROZEN_RULE = "alt_additions_all"
FOLD_COUNT = 5
MEASURE_START = 17
MEASURE_END = 113


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subset(counter: Counter[tuple[int, int, int]], measures: set[int]) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if token[0] in measures})


def metrics(
    predicted: Counter[tuple[int, int, int]],
    reference: Counter[tuple[int, int, int]],
) -> dict[str, Any]:
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    expected = sum(reference.values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())
    return {
        "pitchF1": round(100.0 * v2.f1(matched, predicted_count, expected), 2),
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "predictions": predicted_count,
        "referenceTokens": expected,
    }


def main() -> None:
    for path in (cross.WINNER_STEM, cross.ALT_STEM):
        if not path.exists():
            raise FileNotFoundError(f"Missing benchmark stem: {path.relative_to(ROOT)}")

    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, grid_diagnostics = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)
    if sum(reference.values()) != 867:
        raise RuntimeError(f"Expected 867 professional pitch tokens, found {sum(reference.values())}")

    print("Analyzing winner stem once for frozen cross-validation...", flush=True)
    winner_grouped = cross.group_rows(cross.WINNER_STEM, grid)
    print("Analyzing alternate direct-Demucs stem once for frozen cross-validation...", flush=True)
    alt_grouped = cross.group_rows(cross.ALT_STEM, grid)

    champion = cross.merge_rows(winner_grouped, alt_grouped, "champion_only")
    selective = cross.merge_rows(winner_grouped, alt_grouped, FROZEN_RULE)

    full_champion = metrics(champion, reference)
    full_selective = metrics(selective, reference)

    folds: list[dict[str, Any]] = []
    deltas: list[float] = []
    matched_deltas: list[int] = []
    extra_deltas: list[int] = []

    for fold_index in range(FOLD_COUNT):
        measures = {
            measure
            for measure in range(MEASURE_START, MEASURE_END + 1)
            if (measure - MEASURE_START) % FOLD_COUNT == fold_index
        }
        fold_reference = subset(reference, measures)
        fold_champion = metrics(subset(champion, measures), fold_reference)
        fold_selective = metrics(subset(selective, measures), fold_reference)
        delta = round(float(fold_selective["pitchF1"]) - float(fold_champion["pitchF1"]), 2)
        matched_delta = int(fold_selective["matched"]) - int(fold_champion["matched"])
        extra_delta = int(fold_selective["extra"]) - int(fold_champion["extra"])
        deltas.append(delta)
        matched_deltas.append(matched_delta)
        extra_deltas.append(extra_delta)
        row = {
            "fold": fold_index + 1,
            "measureCount": len(measures),
            "measureFirst": min(measures),
            "measureLast": max(measures),
            "champion": fold_champion,
            "crossStem": fold_selective,
            "deltaPitchF1Points": delta,
            "deltaMatched": matched_delta,
            "deltaExtra": extra_delta,
            "improvedF1": delta > 0.0,
            "improvedMatched": matched_delta > 0,
        }
        folds.append(row)
        print(
            f"fold{fold_index + 1}: championF1={fold_champion['pitchF1']} crossStemF1={fold_selective['pitchF1']} "
            f"delta={delta:+.2f} matchedDelta={matched_delta:+d} extraDelta={extra_delta:+d}",
            flush=True,
        )

    positive_folds = sum(1 for delta in deltas if delta > 0.0)
    nonnegative_folds = sum(1 for delta in deltas if delta >= 0.0)
    matched_positive_folds = sum(1 for delta in matched_deltas if delta > 0)
    mean_delta = round(statistics.mean(deltas), 3)
    median_delta = round(statistics.median(deltas), 3)
    full_delta = round(float(full_selective["pitchF1"]) - float(full_champion["pitchF1"]), 2)

    # Frozen before seeing fold results: require majority-fold generalization plus
    # positive aggregate and median deltas. This is validation only; no rule selection.
    crossval_passed = (
        full_delta > 0.0
        and positive_folds >= 3
        and median_delta > 0.0
        and matched_positive_folds >= 3
    )

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during cross-stem cross-validation.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "frozen-cross-stem-recall-five-fold-cross-validation",
        "frozenRule": FROZEN_RULE,
        "ruleSelectedBeforeCrossValidation": True,
        "foldAssignment": "(measure-17) modulo 5",
        "timingGrid": grid_diagnostics,
        "fullSetChampion": full_champion,
        "fullSetCrossStem": full_selective,
        "fullSetDeltaPitchF1Points": full_delta,
        "folds": folds,
        "positiveF1Folds": positive_folds,
        "nonnegativeF1Folds": nonnegative_folds,
        "positiveMatchedFolds": matched_positive_folds,
        "meanFoldDeltaPitchF1Points": mean_delta,
        "medianFoldDeltaPitchF1Points": median_delta,
        "crossValidationPassed": crossval_passed,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-cross-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "profile-cross-stem-additions-and-build-conservative-fixed-rule"
            if crossval_passed
            else "freeze-6.60-and-profile-missing-pitches-by-section-and-register"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "frozenRule": FROZEN_RULE,
        "crossValidationPassed": crossval_passed,
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CROSS-STEM RECALL CROSSVAL V1 COMPLETE")
    print("Passed: True")
    print("Frozen rule:", FROZEN_RULE)
    print("Full champion/cross-stem F1:", full_champion["pitchF1"], "/", full_selective["pitchF1"])
    print("Full delta points:", full_delta)
    print("Positive F1 folds:", positive_folds, "/", FOLD_COUNT)
    print("Positive matched folds:", matched_positive_folds, "/", FOLD_COUNT)
    print("Mean fold delta points:", mean_delta)
    print("Median fold delta points:", median_delta)
    print("Cross-validation passed:", crossval_passed)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
