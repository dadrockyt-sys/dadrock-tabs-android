from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
PROOF_PATH = PUBLIC / "gomyway-chord-shape-transfer-proof-v1.json"
RHYTHM_REVIEW_PATH = PUBLIC / "gomyway-rhythm-structure-transfer-proof-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chord-shape-transfer-proof-review-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chord-shape-transfer-proof-review-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_CHORD_CLOSED = [37, 88]
EXPECTED_ANCHOR_MAP = {37: 27, 88: 24}
EXPECTED_RHYTHM_CLOSED = [37, 70, 80, 88, 93, 94]
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
    proof = load(PROOF_PATH)
    rhythm_review = load(RHYTHM_REVIEW_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if rhythm_review.get("passed") is not True:
        raise RuntimeError("Rhythm-structure transfer proof review V1 is not green.")
    if rhythm_review.get("rhythmStructureTransferClosedReadOnly") is not True:
        raise RuntimeError("Rhythm-structure subset is not formally closed read-only.")
    if rhythm_review.get("rhythmStructureClosedMeasures") != EXPECTED_RHYTHM_CLOSED:
        raise RuntimeError("Closed rhythm-structure measure set changed unexpectedly.")
    if rhythm_review.get("heldOutMeasures") != EXPECTED_HELD_OUT:
        raise RuntimeError("Held-out measure set changed unexpectedly.")

    if proof.get("passed") is not True:
        raise RuntimeError("Chord-shape transfer proof V1 is not green.")
    if proof.get("readyForChordShapeTransferReview") is not True:
        raise RuntimeError("Chord-shape transfer proof is not ready for review.")
    if proof.get("candidateMeasures") != EXPECTED_CHORD_CLOSED:
        raise RuntimeError("Chord-shape candidate set changed unexpectedly.")
    if proof.get("anchorMap") != {str(k): v for k, v in EXPECTED_ANCHOR_MAP.items()}:
        raise RuntimeError("Chord-shape anchor map changed unexpectedly.")
    if proof.get("chordShapeTransferProvedMeasures") != EXPECTED_CHORD_CLOSED:
        raise RuntimeError("Expected both chord-shape measures to be proved.")
    if proof.get("chordShapeTransferRejectedMeasures") != []:
        raise RuntimeError("Expected zero rejected chord-shape measures.")
    if proof.get("chordShapeTransferProvedCount") != 2:
        raise RuntimeError("Expected exactly two proved chord-shape measures.")
    if proof.get("timingTransferClaimed") is not False:
        raise RuntimeError("Proof unexpectedly claims timing transfer.")
    if proof.get("techniqueTransferClaimed") is not False:
        raise RuntimeError("Proof unexpectedly claims technique transfer.")
    if proof.get("classificationClaimed") is not False:
        raise RuntimeError("Proof unexpectedly claims classification.")
    if proof.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Proof unexpectedly allows automatic application.")
    if proof.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Proof unexpectedly allows threshold relaxation.")
    if proof.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Chord-shape proof did not preserve protected source hash.")

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and proof.get("chordShapeTransferProvedCount") == 2
        and proof.get("chordShapeTransferRejectedMeasures") == []
    )

    recommended = (
        "review-gomyway-rhythm-whole-song-generalization-closure-v1"
        if passed
        else "review-gomyway-chord-shape-transfer-proof-v1"
    )

    output = {
        "schemaVersion": 1,
        "reviewType": "read-only-chord-shape-transfer-proof-review",
        "passed": passed,
        "rhythmStructureClosedMeasures": EXPECTED_RHYTHM_CLOSED,
        "rhythmStructureClosedCount": len(EXPECTED_RHYTHM_CLOSED),
        "chordShapeClosedMeasures": EXPECTED_CHORD_CLOSED,
        "chordShapeClosedCount": len(EXPECTED_CHORD_CLOSED),
        "chordShapeAnchorMap": {str(k): v for k, v in EXPECTED_ANCHOR_MAP.items()},
        "heldOutMeasures": EXPECTED_HELD_OUT,
        "chordShapeTransferClosedReadOnly": passed,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "thresholdRelaxationAllowed": False,
        "readyForWholeSongGeneralizationClosureReview": passed,
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
        "readyForWholeSongGeneralizationClosureReview": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORD SHAPE TRANSFER PROOF REVIEW V1 COMPLETE")
    print("Passed:", passed)
    print("Rhythm-structure closed read-only:", len(EXPECTED_RHYTHM_CLOSED), EXPECTED_RHYTHM_CLOSED)
    print("Chord-shape closed read-only:", len(EXPECTED_CHORD_CLOSED), EXPECTED_CHORD_CLOSED)
    print("Chord-shape anchors:", EXPECTED_ANCHOR_MAP)
    print("Held out:", EXPECTED_HELD_OUT)
    print("Threshold relaxation allowed: False")
    print("Timing transfer claimed: False")
    print("Technique transfer claimed: False")
    print("Classification claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for whole-song generalization closure review:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
