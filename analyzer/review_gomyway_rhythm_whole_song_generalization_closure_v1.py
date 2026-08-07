from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
RHYTHM_REVIEW_PATH = PUBLIC / "gomyway-rhythm-structure-transfer-proof-review-v1.json"
CHORD_REVIEW_PATH = PUBLIC / "gomyway-chord-shape-transfer-proof-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-whole-song-generalization-closure-review-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-whole-song-generalization-closure-review-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_RHYTHM_CLOSED = [37, 70, 80, 88, 93, 94]
EXPECTED_CHORD_CLOSED = [37, 88]
EXPECTED_HELD_OUT = [101]


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
    rhythm_review = load(RHYTHM_REVIEW_PATH)
    chord_review = load(CHORD_REVIEW_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )

    if rhythm_review.get("passed") is not True:
        raise RuntimeError("Rhythm-structure transfer proof review V1 is not green.")
    if rhythm_review.get("rhythmStructureTransferClosedReadOnly") is not True:
        raise RuntimeError("Rhythm-structure subset is not closed read-only.")
    if rhythm_review.get("rhythmStructureClosedMeasures") != EXPECTED_RHYTHM_CLOSED:
        raise RuntimeError("Rhythm-structure closed set changed unexpectedly.")
    if rhythm_review.get("heldOutMeasures") != EXPECTED_HELD_OUT:
        raise RuntimeError("Rhythm review held-out set changed unexpectedly.")
    if rhythm_review.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Rhythm review unexpectedly allows automatic application.")
    if rhythm_review.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Rhythm review unexpectedly allows threshold relaxation.")

    if chord_review.get("passed") is not True:
        raise RuntimeError("Chord-shape transfer proof review V1 is not green.")
    if chord_review.get("chordShapeTransferClosedReadOnly") is not True:
        raise RuntimeError("Chord-shape subset is not closed read-only.")
    if chord_review.get("chordShapeClosedMeasures") != EXPECTED_CHORD_CLOSED:
        raise RuntimeError("Chord-shape closed set changed unexpectedly.")
    if chord_review.get("heldOutMeasures") != EXPECTED_HELD_OUT:
        raise RuntimeError("Chord review held-out set changed unexpectedly.")
    if chord_review.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Chord review unexpectedly allows automatic application.")
    if chord_review.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Chord review unexpectedly allows threshold relaxation.")

    timing_claimed = bool(
        rhythm_review.get("timingTransferClaimed")
        or chord_review.get("timingTransferClaimed")
    )
    technique_claimed = bool(
        rhythm_review.get("techniqueTransferClaimed")
        or chord_review.get("techniqueTransferClaimed")
    )
    classification_claimed = bool(
        rhythm_review.get("classificationClaimed")
        or chord_review.get("classificationClaimed")
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after

    passed = bool(
        source_unchanged
        and not timing_claimed
        and not technique_claimed
        and not classification_claimed
    )

    # The first learned-generalization milestone is closed read-only. The next
    # evidence-driven action is to diagnose the single held-out measure 101
    # rather than loosen thresholds or auto-expand classifications.
    recommended = (
        "diagnose-gomyway-rhythm-measure-101-placement-v1"
        if passed
        else "review-gomyway-rhythm-whole-song-generalization-closure-v1"
    )

    output = {
        "schemaVersion": 1,
        "reviewType": "read-only-whole-song-rhythm-generalization-closure-review",
        "passed": passed,
        "rhythmStructureClosedReadOnly": True,
        "rhythmStructureClosedCount": len(EXPECTED_RHYTHM_CLOSED),
        "rhythmStructureClosedMeasures": EXPECTED_RHYTHM_CLOSED,
        "chordShapeClosedReadOnly": True,
        "chordShapeClosedCount": len(EXPECTED_CHORD_CLOSED),
        "chordShapeClosedMeasures": EXPECTED_CHORD_CLOSED,
        "heldOutMeasures": EXPECTED_HELD_OUT,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "thresholdRelaxationAllowed": False,
        "wholeSongGeneralizationMilestoneClosedReadOnly": passed,
        "readyForHeldOutMeasureDiagnosis": passed,
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
        "rhythmStructureClosedCount": len(EXPECTED_RHYTHM_CLOSED),
        "chordShapeClosedCount": len(EXPECTED_CHORD_CLOSED),
        "heldOutMeasures": EXPECTED_HELD_OUT,
        "automaticApplyAllowed": False,
        "thresholdRelaxationAllowed": False,
        "wholeSongGeneralizationMilestoneClosedReadOnly": passed,
        "readyForHeldOutMeasureDiagnosis": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM WHOLE SONG GENERALIZATION CLOSURE REVIEW V1 COMPLETE")
    print("Passed:", passed)
    print("Rhythm-structure closed read-only:", len(EXPECTED_RHYTHM_CLOSED), EXPECTED_RHYTHM_CLOSED)
    print("Chord-shape closed read-only:", len(EXPECTED_CHORD_CLOSED), EXPECTED_CHORD_CLOSED)
    print("Held out:", EXPECTED_HELD_OUT)
    print("Timing transfer claimed: False")
    print("Technique transfer claimed: False")
    print("Classification claimed: False")
    print("Automatic apply allowed: False")
    print("Threshold relaxation allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Whole-song generalization milestone closed read-only:", passed)
    print("Ready for held-out measure diagnosis:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
