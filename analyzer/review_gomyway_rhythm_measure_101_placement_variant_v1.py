from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
DIAGNOSTIC_PATH = PUBLIC / "gomyway-rhythm-measure-101-placement-diagnostic-v1.json"
CLOSURE_PATH = PUBLIC / "gomyway-rhythm-whole-song-generalization-closure-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-measure-101-placement-variant-review-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-measure-101-placement-variant-review-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
TARGET_MEASURE = 101
EXPECTED_ANCHOR = 24
EXPECTED_TARGET_STEPS = [3, 4, 5, 7, 8, 10, 11, 12, 15]
EXPECTED_ANCHOR_STEPS = [0, 1, 2, 3, 5, 7, 11, 12, 15]
EXPECTED_SHARED_STEPS = [3, 5, 7, 11, 12, 15]
EXPECTED_TARGET_ONLY = [4, 8, 10]
EXPECTED_ANCHOR_ONLY = [0, 1, 2]
EXPECTED_RHYTHM_CLOSED = [37, 70, 80, 88, 93, 94]
EXPECTED_CHORD_CLOSED = [37, 88]


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
    diagnostic = load(DIAGNOSTIC_PATH)
    closure = load(CLOSURE_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if closure.get("passed") is not True:
        raise RuntimeError("Whole-song generalization closure review V1 is not green.")
    if closure.get("wholeSongGeneralizationMilestoneClosedReadOnly") is not True:
        raise RuntimeError("Whole-song generalization milestone is not closed read-only.")
    if closure.get("rhythmStructureClosedMeasures") != EXPECTED_RHYTHM_CLOSED:
        raise RuntimeError("Closed rhythm-structure set changed unexpectedly.")
    if closure.get("chordShapeClosedMeasures") != EXPECTED_CHORD_CLOSED:
        raise RuntimeError("Closed chord-shape set changed unexpectedly.")
    if closure.get("heldOutMeasures") != [TARGET_MEASURE]:
        raise RuntimeError("Held-out measure set changed unexpectedly.")

    if diagnostic.get("passed") is not True:
        raise RuntimeError("Measure 101 placement diagnostic V1 is not green.")
    if diagnostic.get("measureNumber") != TARGET_MEASURE:
        raise RuntimeError("Placement diagnostic target measure changed unexpectedly.")
    if diagnostic.get("anchorMeasure") != EXPECTED_ANCHOR:
        raise RuntimeError("Placement diagnostic anchor changed unexpectedly.")
    if diagnostic.get("diagnosis") != "density-and-chord-like-but-rhythm-placement-variant":
        raise RuntimeError(f"Unexpected placement diagnosis: {diagnostic.get('diagnosis')!r}")
    if diagnostic.get("likelyConsistentGlobalStepShift") is not False:
        raise RuntimeError("Measure 101 unexpectedly looks like a consistent global shift.")
    if diagnostic.get("likelySparsePlacementVariant") is not True:
        raise RuntimeError("Measure 101 is not marked as a sparse placement variant.")
    if diagnostic.get("targetOccupiedSteps") != EXPECTED_TARGET_STEPS:
        raise RuntimeError("Measure 101 occupied-step set changed unexpectedly.")
    if diagnostic.get("anchorOccupiedSteps") != EXPECTED_ANCHOR_STEPS:
        raise RuntimeError("Anchor 24 occupied-step set changed unexpectedly.")
    if diagnostic.get("sharedOccupiedSteps") != EXPECTED_SHARED_STEPS:
        raise RuntimeError("Shared occupied-step set changed unexpectedly.")
    if diagnostic.get("targetOnlyOccupiedSteps") != EXPECTED_TARGET_ONLY:
        raise RuntimeError("Target-only occupied-step set changed unexpectedly.")
    if diagnostic.get("anchorOnlyOccupiedSteps") != EXPECTED_ANCHOR_ONLY:
        raise RuntimeError("Anchor-only occupied-step set changed unexpectedly.")
    if float(diagnostic.get("occupiedStepJaccard", -1)) != 0.5:
        raise RuntimeError("Expected occupied-step Jaccard 0.5 for measure 101.")

    best_shift = diagnostic.get("bestIntegerShift")
    if not isinstance(best_shift, dict):
        raise RuntimeError("Placement diagnostic bestIntegerShift missing.")
    if int(best_shift.get("shift", 999)) != 0:
        raise RuntimeError("Expected best integer shift 0 for measure 101.")
    if float(best_shift.get("jaccard", -1)) != 0.5:
        raise RuntimeError("Expected best-shift Jaccard to remain 0.5.")

    if diagnostic.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Placement diagnostic unexpectedly allows threshold relaxation.")
    if diagnostic.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Placement diagnostic unexpectedly allows automatic application.")
    if diagnostic.get("rhythmTransferClaimed") is not False:
        raise RuntimeError("Placement diagnostic unexpectedly claims rhythm transfer.")
    if diagnostic.get("chordTransferClaimed") is not False:
        raise RuntimeError("Placement diagnostic unexpectedly claims chord transfer.")
    if diagnostic.get("timingTransferClaimed") is not False:
        raise RuntimeError("Placement diagnostic unexpectedly claims timing transfer.")
    if diagnostic.get("techniqueTransferClaimed") is not False:
        raise RuntimeError("Placement diagnostic unexpectedly claims technique transfer.")
    if diagnostic.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Placement diagnostic did not preserve protected source hash.")

    # Formal review decision: preserve measure 101 as a distinct rhythm-placement
    # variant related to anchor 24 by density/chord evidence, but do not promote it
    # into the closed rhythm-transfer set and do not relax the occupied-step gate.
    variant_relationship_preserved = True
    rhythm_transfer_closed = False
    eligible_as_new_training_anchor = True

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(source_unchanged and variant_relationship_preserved and eligible_as_new_training_anchor)

    recommended = (
        "select-gomyway-rhythm-next-novel-training-anchors-v1"
        if passed
        else "review-gomyway-rhythm-measure-101-placement-variant-v1"
    )

    output = {
        "schemaVersion": 1,
        "reviewType": "read-only-held-out-rhythm-placement-variant-review",
        "passed": passed,
        "measureNumber": TARGET_MEASURE,
        "anchorMeasure": EXPECTED_ANCHOR,
        "diagnosis": diagnostic.get("diagnosis"),
        "occupiedStepJaccard": diagnostic.get("occupiedStepJaccard"),
        "targetOccupiedSteps": EXPECTED_TARGET_STEPS,
        "anchorOccupiedSteps": EXPECTED_ANCHOR_STEPS,
        "sharedOccupiedSteps": EXPECTED_SHARED_STEPS,
        "targetOnlyOccupiedSteps": EXPECTED_TARGET_ONLY,
        "anchorOnlyOccupiedSteps": EXPECTED_ANCHOR_ONLY,
        "bestIntegerShift": best_shift,
        "variantRelationshipPreservedReadOnly": variant_relationship_preserved,
        "rhythmTransferClosedForMeasure101": rhythm_transfer_closed,
        "measure101RemainsHeldOutFromTransferredRhythmSet": True,
        "eligibleAsNewTrainingAnchor": eligible_as_new_training_anchor,
        "thresholdRelaxationAllowed": False,
        "classificationClaimed": False,
        "rhythmTransferClaimed": False,
        "chordTransferClaimed": False,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "automaticApplyAllowed": False,
        "readOnlyReview": True,
        "readyForNovelTrainingAnchorSelection": passed,
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
        "measureNumber": TARGET_MEASURE,
        "anchorMeasure": EXPECTED_ANCHOR,
        "variantRelationshipPreservedReadOnly": variant_relationship_preserved,
        "measure101RemainsHeldOutFromTransferredRhythmSet": True,
        "eligibleAsNewTrainingAnchor": eligible_as_new_training_anchor,
        "thresholdRelaxationAllowed": False,
        "automaticApplyAllowed": False,
        "readyForNovelTrainingAnchorSelection": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM MEASURE 101 PLACEMENT VARIANT REVIEW V1 COMPLETE")
    print("Passed:", passed)
    print("Measure:", TARGET_MEASURE, "anchor:", EXPECTED_ANCHOR)
    print("Diagnosis:", diagnostic.get("diagnosis"))
    print("Variant relationship preserved read-only:", variant_relationship_preserved)
    print("Rhythm transfer closed for measure 101:", rhythm_transfer_closed)
    print("Measure 101 remains held out from transferred rhythm set: True")
    print("Eligible as new training anchor:", eligible_as_new_training_anchor)
    print("Threshold relaxation allowed: False")
    print("Classification claimed: False")
    print("Rhythm transfer claimed: False")
    print("Chord transfer claimed: False")
    print("Timing transfer claimed: False")
    print("Technique transfer claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for novel training anchor selection:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
