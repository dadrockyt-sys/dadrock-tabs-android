from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
VALIDATION_PATH = PUBLIC / "gomyway-rhythm-provisional-rule-transfer-evidence-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-provisional-rule-transfer-evidence-review-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-provisional-rule-transfer-evidence-review-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_PROVED = [37, 70, 80, 88, 93, 94]
EXPECTED_HELD_OUT = [101]
EXPECTED_RHYTHM_SUPPORTED = [37, 70, 80, 88, 93, 94]
EXPECTED_CHORD_SUPPORTED = [37, 88]
EXPECTED_CHORD_UNSUPPORTED = [70, 80, 93, 94]


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
    validation = load(VALIDATION_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if validation.get("passed") is not True:
        raise RuntimeError("Provisional rule-transfer evidence validation V1 is not green.")
    if validation.get("readyForRuleTransferEvidenceReview") is not True:
        raise RuntimeError("Validation is not ready for rule-transfer evidence review.")
    if validation.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Validation unexpectedly allows automatic application.")
    if validation.get("ruleTransferClaimed") is not False:
        raise RuntimeError("Validation unexpectedly claims rule transfer.")
    if validation.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Validation did not preserve protected source hash.")

    proved = validation.get("provedRelationshipMeasures")
    held_out = validation.get("heldOutMeasures")
    rhythm_supported = validation.get("rhythmStructureEvidenceSupportedMeasures")
    rhythm_unsupported = validation.get("rhythmStructureEvidenceUnsupportedMeasures")
    chord_supported = validation.get("chordShapeEvidenceSupportedMeasures")
    chord_unsupported = validation.get("chordShapeEvidenceUnsupportedMeasures")
    timing_count = validation.get("timingTransferEvidenceSupportedCount")
    technique_count = validation.get("techniqueTransferEvidenceSupportedCount")

    if proved != EXPECTED_PROVED:
        raise RuntimeError(f"Expected proved measures {EXPECTED_PROVED}, found {proved}.")
    if held_out != EXPECTED_HELD_OUT:
        raise RuntimeError(f"Expected held-out measures {EXPECTED_HELD_OUT}, found {held_out}.")
    if rhythm_supported != EXPECTED_RHYTHM_SUPPORTED:
        raise RuntimeError(
            f"Expected rhythm-supported measures {EXPECTED_RHYTHM_SUPPORTED}, found {rhythm_supported}."
        )
    if rhythm_unsupported != []:
        raise RuntimeError(f"Expected no rhythm-unsupported measures, found {rhythm_unsupported}.")
    if chord_supported != EXPECTED_CHORD_SUPPORTED:
        raise RuntimeError(
            f"Expected chord-supported measures {EXPECTED_CHORD_SUPPORTED}, found {chord_supported}."
        )
    if chord_unsupported != EXPECTED_CHORD_UNSUPPORTED:
        raise RuntimeError(
            f"Expected chord-unsupported measures {EXPECTED_CHORD_UNSUPPORTED}, found {chord_unsupported}."
        )
    if timing_count != 0:
        raise RuntimeError(f"Expected zero timing-transfer evidence, found {timing_count}.")
    if technique_count != 0:
        raise RuntimeError(f"Expected zero technique-transfer evidence, found {technique_count}.")

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after

    rhythm_subset_ready = bool(source_unchanged and rhythm_supported == EXPECTED_RHYTHM_SUPPORTED)
    chord_subset_ready = bool(source_unchanged and chord_supported == EXPECTED_CHORD_SUPPORTED)
    timing_subset_ready = False
    technique_subset_ready = False

    passed = bool(
        source_unchanged
        and rhythm_subset_ready
        and chord_subset_ready
        and timing_count == 0
        and technique_count == 0
    )

    recommended = (
        "prove-gomyway-rhythm-structure-transfer-v1"
        if passed
        else "review-gomyway-rhythm-provisional-rule-transfer-evidence-v1"
    )

    output = {
        "schemaVersion": 1,
        "reviewType": "read-only-provisional-domain-rule-transfer-evidence-review",
        "passed": passed,
        "provedRelationshipMeasures": EXPECTED_PROVED,
        "heldOutMeasures": EXPECTED_HELD_OUT,
        "rhythmStructureSubset": {
            "candidateCount": len(EXPECTED_RHYTHM_SUPPORTED),
            "candidateMeasures": EXPECTED_RHYTHM_SUPPORTED,
            "readyForProof": rhythm_subset_ready,
        },
        "chordShapeSubset": {
            "candidateCount": len(EXPECTED_CHORD_SUPPORTED),
            "candidateMeasures": EXPECTED_CHORD_SUPPORTED,
            "unsupportedMeasures": EXPECTED_CHORD_UNSUPPORTED,
            "readyForProof": chord_subset_ready,
        },
        "timingTransferSubset": {
            "candidateCount": 0,
            "candidateMeasures": [],
            "readyForProof": timing_subset_ready,
            "reason": "no-explicit-timing-transfer-evidence",
        },
        "techniqueTransferSubset": {
            "candidateCount": 0,
            "candidateMeasures": [],
            "readyForProof": technique_subset_ready,
            "reason": "no-explicit-technique-transfer-evidence",
        },
        "measure101HeldOut": True,
        "measure101Reason": "occupied-step-structure-below-generalization-proof-floor",
        "thresholdRelaxationAllowed": False,
        "classificationClaimed": False,
        "ruleTransferClaimed": False,
        "automaticApplyAllowed": False,
        "readOnlyReview": True,
        "readyForRhythmStructureTransferProof": bool(passed and rhythm_subset_ready),
        "readyForChordShapeTransferProof": bool(passed and chord_subset_ready),
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
        "rhythmStructureCandidateCount": len(EXPECTED_RHYTHM_SUPPORTED),
        "chordShapeCandidateCount": len(EXPECTED_CHORD_SUPPORTED),
        "timingTransferCandidateCount": 0,
        "techniqueTransferCandidateCount": 0,
        "measure101HeldOut": True,
        "thresholdRelaxationAllowed": False,
        "classificationClaimed": False,
        "ruleTransferClaimed": False,
        "automaticApplyAllowed": False,
        "readyForRhythmStructureTransferProof": bool(passed and rhythm_subset_ready),
        "readyForChordShapeTransferProof": bool(passed and chord_subset_ready),
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM PROVISIONAL RULE-TRANSFER EVIDENCE REVIEW V1 COMPLETE")
    print("Passed:", passed)
    print("Rhythm-structure subset:", len(EXPECTED_RHYTHM_SUPPORTED), EXPECTED_RHYTHM_SUPPORTED)
    print("Chord-shape subset:", len(EXPECTED_CHORD_SUPPORTED), EXPECTED_CHORD_SUPPORTED)
    print("Chord-shape unsupported:", len(EXPECTED_CHORD_UNSUPPORTED), EXPECTED_CHORD_UNSUPPORTED)
    print("Timing-transfer subset: 0 []")
    print("Technique-transfer subset: 0 []")
    print("Measure 101 held out: True")
    print("Threshold relaxation allowed: False")
    print("Classification claimed: False")
    print("Rule transfer claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for rhythm-structure transfer proof:", bool(passed and rhythm_subset_ready))
    print("Ready for chord-shape transfer proof:", bool(passed and chord_subset_ready))
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
