from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
SELECTION_PATH = PUBLIC / "gomyway-rhythm-next-novel-training-anchors-v1.json"
VARIANT_REVIEW_PATH = PUBLIC / "gomyway-rhythm-measure-101-placement-variant-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-next-novel-training-anchors-review-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-next-novel-training-anchors-review-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_CANDIDATE_POOL_COUNT = 72
EXPECTED_SHORTLIST = [36, 51, 60, 73, 82, 91, 99, 101, 113]
KNOWN_VARIANT_MEASURE = 101
NEXT_CHRONOLOGICAL_TRAINING_ANCHOR = 36
QUEUED_AFTER_NEXT = [51, 60, 73, 82, 91, 99, 101, 113]


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


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    selection = load(SELECTION_PATH)
    variant_review = load(VARIANT_REVIEW_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if selection.get("passed") is not True:
        raise RuntimeError("Novel training-anchor selection V1 is not green.")
    if selection.get("readyForNovelTrainingAnchorReview") is not True:
        raise RuntimeError("Selection is not ready for novel training-anchor review.")
    if selection.get("selectionClaimedAsTrainingTruth") is not False:
        raise RuntimeError("Selection unexpectedly claims training truth.")
    if selection.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Selection unexpectedly allows threshold relaxation.")
    if selection.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Selection unexpectedly allows automatic application.")
    if selection.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Selection did not preserve protected source hash.")

    if selection.get("candidatePoolCount") != EXPECTED_CANDIDATE_POOL_COUNT:
        raise RuntimeError(
            f"Expected candidate pool {EXPECTED_CANDIDATE_POOL_COUNT}, found {selection.get('candidatePoolCount')}."
        )
    if selection.get("selectedAnchorCandidateMeasures") != EXPECTED_SHORTLIST:
        raise RuntimeError(
            f"Expected shortlist {EXPECTED_SHORTLIST}, found {selection.get('selectedAnchorCandidateMeasures')}."
        )
    if selection.get("selectedAnchorCandidateCount") != len(EXPECTED_SHORTLIST):
        raise RuntimeError("Unexpected shortlist count.")

    selected_rows = selection.get("selectedAnchorCandidates")
    if not isinstance(selected_rows, list):
        raise RuntimeError("Selected anchor candidate rows missing.")
    selected_by_measure = {
        int(row["measureNumber"]): row
        for row in selected_rows
        if isinstance(row, dict) and "measureNumber" in row
    }
    if sorted(selected_by_measure) != EXPECTED_SHORTLIST:
        raise RuntimeError("Selected anchor candidate rows do not match shortlist.")

    if variant_review.get("passed") is not True:
        raise RuntimeError("Measure 101 placement-variant review V1 is not green.")
    if variant_review.get("eligibleAsNewTrainingAnchor") is not True:
        raise RuntimeError("Measure 101 is no longer eligible as a new training anchor.")
    if selected_by_measure[KNOWN_VARIANT_MEASURE].get("knownPlacementVariant") is not True:
        raise RuntimeError("Measure 101 lost its known-placement-variant tag.")

    # Formal review decision: accept the nine-measure coverage shortlist as a
    # training-review queue, but preserve the section-by-section workflow by
    # advancing only the earliest novel measure (36) into full anchor training.
    # The remaining eight stay queued and untrained.
    next_row = selected_by_measure[NEXT_CHRONOLOGICAL_TRAINING_ANCHOR]
    queue_rows = [selected_by_measure[measure] for measure in QUEUED_AFTER_NEXT]

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and int(next_row["measureNumber"]) == NEXT_CHRONOLOGICAL_TRAINING_ANCHOR
        and [int(row["measureNumber"]) for row in queue_rows] == QUEUED_AFTER_NEXT
    )

    recommended = (
        "train-gomyway-rhythm-novel-anchor-36-v1"
        if passed
        else "review-gomyway-rhythm-next-novel-training-anchors-v1"
    )

    output = {
        "schemaVersion": 1,
        "reviewType": "read-only-novel-rhythm-training-anchor-shortlist-review",
        "passed": passed,
        "candidatePoolCount": EXPECTED_CANDIDATE_POOL_COUNT,
        "reviewedShortlistMeasures": EXPECTED_SHORTLIST,
        "shortlistAcceptedAsCoverageQueue": True,
        "nextChronologicalTrainingAnchor": NEXT_CHRONOLOGICAL_TRAINING_ANCHOR,
        "nextTrainingAnchorEvidence": next_row,
        "queuedTrainingAnchorMeasures": QUEUED_AFTER_NEXT,
        "queuedTrainingAnchorEvidence": queue_rows,
        "knownPlacementVariantMeasure": KNOWN_VARIANT_MEASURE,
        "knownPlacementVariantPreserved": True,
        "sectionBySectionTrainingOrderPreserved": True,
        "trainingTruthClaimed": False,
        "classificationClaimed": False,
        "rhythmTransferClaimed": False,
        "chordTransferClaimed": False,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "thresholdRelaxationAllowed": False,
        "automaticApplyAllowed": False,
        "readOnlyReview": True,
        "readyForNovelAnchor36Training": passed,
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
        "reviewedShortlistMeasures": EXPECTED_SHORTLIST,
        "nextChronologicalTrainingAnchor": NEXT_CHRONOLOGICAL_TRAINING_ANCHOR,
        "queuedTrainingAnchorMeasures": QUEUED_AFTER_NEXT,
        "knownPlacementVariantMeasure": KNOWN_VARIANT_MEASURE,
        "trainingTruthClaimed": False,
        "automaticApplyAllowed": False,
        "readyForNovelAnchor36Training": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM NEXT NOVEL TRAINING ANCHORS REVIEW V1 COMPLETE")
    print("Passed:", passed)
    print("Candidate pool count:", EXPECTED_CANDIDATE_POOL_COUNT)
    print("Reviewed shortlist:", EXPECTED_SHORTLIST)
    print("Shortlist accepted as coverage queue: True")
    print("Next chronological training anchor:", NEXT_CHRONOLOGICAL_TRAINING_ANCHOR)
    print("Queued after next:", QUEUED_AFTER_NEXT)
    print("Measure 101 known placement variant preserved: True")
    print("Section-by-section training order preserved: True")
    print("Training truth claimed: False")
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
    print("Ready for novel anchor 36 training:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
