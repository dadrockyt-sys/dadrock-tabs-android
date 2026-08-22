from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
DIAGNOSTIC_PATH = PUBLIC / "gomyway-rhythm-whole-song-learned-similarity-diagnostic-v1.json"
VARIANT_REVIEW_PATH = PUBLIC / "gomyway-rhythm-measure-101-placement-variant-review-v1.json"
CLOSURE_PATH = PUBLIC / "gomyway-rhythm-whole-song-generalization-closure-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-next-novel-training-anchors-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-next-novel-training-anchors-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
UNTRAINED_START = 36
UNTRAINED_END = 113
EXPECTED_UNTRAINED_COUNT = 78
KNOWN_VARIANT_MEASURE = 101
EXPECTED_RHYTHM_CLOSED = [37, 70, 80, 88, 93, 94]
EXPECTED_CHORD_CLOSED = [37, 88]
TARGET_BIN_COUNT = 8


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def number(row: dict[str, Any], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {row.get(key)!r}") from exc


def integer(row: dict[str, Any], key: str) -> int:
    try:
        return int(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {row.get(key)!r}") from exc


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    diagnostic = load(DIAGNOSTIC_PATH)
    variant_review = load(VARIANT_REVIEW_PATH)
    closure = load(CLOSURE_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if diagnostic.get("passed") is not True:
        raise RuntimeError("Whole-song learned-similarity diagnostic V1 is not green.")
    if closure.get("passed") is not True:
        raise RuntimeError("Whole-song generalization closure review V1 is not green.")
    if closure.get("wholeSongGeneralizationMilestoneClosedReadOnly") is not True:
        raise RuntimeError("Whole-song generalization milestone is not closed read-only.")
    if closure.get("rhythmStructureClosedMeasures") != EXPECTED_RHYTHM_CLOSED:
        raise RuntimeError("Closed rhythm-structure set changed unexpectedly.")
    if closure.get("chordShapeClosedMeasures") != EXPECTED_CHORD_CLOSED:
        raise RuntimeError("Closed chord-shape set changed unexpectedly.")
    if variant_review.get("passed") is not True:
        raise RuntimeError("Measure 101 placement-variant review V1 is not green.")
    if variant_review.get("eligibleAsNewTrainingAnchor") is not True:
        raise RuntimeError("Measure 101 is not eligible as a new training anchor.")
    if variant_review.get("readyForNovelTrainingAnchorSelection") is not True:
        raise RuntimeError("Variant review is not ready for novel training anchor selection.")
    if variant_review.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Variant review unexpectedly allows threshold relaxation.")
    if variant_review.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Variant review unexpectedly allows automatic application.")

    raw_rows = diagnostic.get("rows")
    if not isinstance(raw_rows, list) or len(raw_rows) != EXPECTED_UNTRAINED_COUNT:
        raise RuntimeError("Similarity diagnostic does not contain exactly 78 untrained rows.")

    closed = set(EXPECTED_RHYTHM_CLOSED)
    candidates: list[dict[str, Any]] = []
    for raw in raw_rows:
        if not isinstance(raw, dict):
            continue
        measure = integer(raw, "measureNumber")
        if not (UNTRAINED_START <= measure <= UNTRAINED_END):
            continue
        if measure in closed:
            continue

        structural = number(raw, "bestStructuralSimilarityScore")
        musical = number(raw, "bestMusicalSimilarityScore")
        margin = number(raw, "bestVsRunnerUpMargin")
        comparison = raw.get("bestComparison")
        if not isinstance(comparison, dict):
            raise RuntimeError(f"bestComparison missing for measure {measure}.")

        # High score means the measure contributes vocabulary not already well-covered
        # by anchors 1-35. This is only an anchor-review priority score.
        novelty = max(0.0, 1.0 - structural)
        placement_novelty = max(0.0, 1.0 - float(comparison.get("occupiedStepJaccard", 0.0)))
        multiplicity_novelty = max(
            0.0, 1.0 - float(comparison.get("sharedStepMultiplicitySimilarity", 0.0))
        )
        novelty_score = round(
            0.55 * novelty + 0.30 * placement_novelty + 0.15 * multiplicity_novelty,
            6,
        )

        candidates.append(
            {
                "measureNumber": measure,
                "bestLearnedAnchorMeasure": integer(raw, "bestAnchorMeasure"),
                "structuralSimilarity": structural,
                "musicalSimilarity": musical,
                "bestVsRunnerUpMargin": margin,
                "occupiedStepJaccard": float(comparison.get("occupiedStepJaccard", 0.0)),
                "multiplicitySimilarity": float(
                    comparison.get("sharedStepMultiplicitySimilarity", 0.0)
                ),
                "noveltyPriorityScore": novelty_score,
                "knownPlacementVariant": measure == KNOWN_VARIANT_MEASURE,
            }
        )

    candidates.sort(key=lambda row: row["measureNumber"])
    if not candidates:
        raise RuntimeError("No novel anchor candidates available.")

    # Chronological coverage: divide measures 36-113 into eight nearly equal bins.
    width = (UNTRAINED_END - UNTRAINED_START + 1) / TARGET_BIN_COUNT
    bins: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    for index in range(TARGET_BIN_COUNT):
        start = int(UNTRAINED_START + index * width)
        end = (
            UNTRAINED_END
            if index == TARGET_BIN_COUNT - 1
            else int(UNTRAINED_START + (index + 1) * width) - 1
        )
        rows = [row for row in candidates if start <= row["measureNumber"] <= end]
        if not rows:
            bins.append({"bin": index + 1, "startMeasure": start, "endMeasure": end, "selected": None})
            continue
        chosen = max(
            rows,
            key=lambda row: (
                row["noveltyPriorityScore"],
                row["knownPlacementVariant"],
                -row["structuralSimilarity"],
                -row["measureNumber"],
            ),
        )
        selected.append(chosen)
        bins.append(
            {
                "bin": index + 1,
                "startMeasure": start,
                "endMeasure": end,
                "selected": chosen,
            }
        )

    # Measure 101 has already earned explicit new-anchor eligibility; retain it even
    # if another measure wins its chronological bin.
    if KNOWN_VARIANT_MEASURE not in {row["measureNumber"] for row in selected}:
        measure101 = next(
            (row for row in candidates if row["measureNumber"] == KNOWN_VARIANT_MEASURE),
            None,
        )
        if measure101 is None:
            raise RuntimeError("Measure 101 missing from novel candidate pool.")
        selected.append(measure101)

    selected.sort(key=lambda row: row["measureNumber"])
    selected_measures = [row["measureNumber"] for row in selected]

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and KNOWN_VARIANT_MEASURE in selected_measures
        and len(selected_measures) >= TARGET_BIN_COUNT
        and len(selected_measures) == len(set(selected_measures))
    )

    recommended = (
        "review-gomyway-rhythm-next-novel-training-anchors-v1"
        if passed
        else "select-gomyway-rhythm-next-novel-training-anchors-v1"
    )

    output = {
        "schemaVersion": 1,
        "selectionType": "read-only-chronological-novel-rhythm-training-anchor-shortlist",
        "passed": passed,
        "untrainedMeasureRange": [UNTRAINED_START, UNTRAINED_END],
        "candidatePoolCount": len(candidates),
        "closedRhythmMeasuresExcluded": EXPECTED_RHYTHM_CLOSED,
        "knownPlacementVariantMeasure": KNOWN_VARIANT_MEASURE,
        "targetChronologicalBinCount": TARGET_BIN_COUNT,
        "chronologicalBins": bins,
        "selectedAnchorCandidateCount": len(selected),
        "selectedAnchorCandidateMeasures": selected_measures,
        "selectedAnchorCandidates": selected,
        "selectionClaimedAsTrainingTruth": False,
        "classificationClaimed": False,
        "rhythmTransferClaimed": False,
        "chordTransferClaimed": False,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "thresholdRelaxationAllowed": False,
        "automaticApplyAllowed": False,
        "readOnlySelection": True,
        "readyForNovelTrainingAnchorReview": passed,
        "recommendedNextAction": recommended,
        "protectedSourceEventCount": len(events),
        "protectedSourceHashBefore": source_hash_before,
        "protectedSourceHashAfter": source_hash_after,
        "protectedSourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "candidatePoolCount": len(candidates),
        "selectedAnchorCandidateCount": len(selected),
        "selectedAnchorCandidateMeasures": selected_measures,
        "knownPlacementVariantMeasure": KNOWN_VARIANT_MEASURE,
        "selectionClaimedAsTrainingTruth": False,
        "automaticApplyAllowed": False,
        "readyForNovelTrainingAnchorReview": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM NEXT NOVEL TRAINING ANCHORS V1 COMPLETE")
    print("Passed:", passed)
    print("Candidate pool count:", len(candidates))
    print("Chronological bins:", TARGET_BIN_COUNT)
    print("Selected anchor candidate count:", len(selected))
    print("Selected anchor candidate measures:", selected_measures)
    for row in selected:
        print(
            f"measure={row['measureNumber']} bestAnchor={row['bestLearnedAnchorMeasure']} "
            f"structural={row['structuralSimilarity']} occupied={row['occupiedStepJaccard']} "
            f"multiplicity={row['multiplicitySimilarity']} novelty={row['noveltyPriorityScore']} "
            f"knownVariant={row['knownPlacementVariant']}"
        )
    print("Selection claimed as training truth: False")
    print("Threshold relaxation allowed: False")
    print("Classification claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for novel training anchor review:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
