from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
TRAINING_REVIEW_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-36-training-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-36-read-only-registration-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-36-read-only-registration-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
TARGET_MEASURE = 36
EXPECTED_OCCUPIED_STEPS = [0, 3, 5, 10, 14, 15]
EXPECTED_MULTIPLICITIES = {"0": 1, "3": 1, "5": 1, "10": 1, "14": 1, "15": 1}
QUEUED_AFTER = [51, 60, 73, 82, 91, 99, 101, 113]


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
    review = load(TRAINING_REVIEW_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if review.get("passed") is not True:
        raise RuntimeError("Novel anchor 36 training review V1 is not green.")
    if review.get("measureNumber") != TARGET_MEASURE:
        raise RuntimeError("Novel anchor review target changed unexpectedly.")
    if review.get("readyForNovelAnchor36ReadOnlyRegistration") is not True:
        raise RuntimeError("Training review is not ready for read-only registration.")
    if review.get("rhythmPatternAcceptedAsTrainingEvidence") is not True:
        raise RuntimeError("Measure 36 rhythm pattern was not accepted as training evidence.")
    if review.get("occupiedSteps") != EXPECTED_OCCUPIED_STEPS:
        raise RuntimeError("Measure 36 occupied-step pattern changed unexpectedly.")
    if review.get("stepMultiplicities") != EXPECTED_MULTIPLICITIES:
        raise RuntimeError("Measure 36 multiplicity pattern changed unexpectedly.")
    if review.get("chordShapeDomainClosedUnsupported") is not True:
        raise RuntimeError("Measure 36 chord domain is not formally closed unsupported.")
    if review.get("timingDomainClosedUnsupported") is not True:
        raise RuntimeError("Measure 36 timing domain is not formally closed unsupported.")
    if review.get("techniqueDomainClosedUnsupported") is not True:
        raise RuntimeError("Measure 36 technique domain is not formally closed unsupported.")
    if review.get("anchorRegisteredAsLearnedTruth") is not False:
        raise RuntimeError("Review unexpectedly pre-registered the anchor as learned truth.")
    if review.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Review unexpectedly allows threshold relaxation.")
    if review.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Review unexpectedly allows automatic application.")
    if review.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Review did not preserve protected source hash.")
    if review.get("queuedTrainingAnchorMeasures") != QUEUED_AFTER:
        raise RuntimeError("Queued training-anchor order changed unexpectedly.")

    # Read-only registration means measure 36 is now eligible to participate as a
    # learned RHYTHM anchor in future diagnostics. It does not register chord,
    # timing, or technique knowledge, and it never mutates protected source data.
    learned_domains = {
        "rhythmStructure": True,
        "chordShape": False,
        "timing": False,
        "technique": False,
    }
    registration = {
        "measureNumber": TARGET_MEASURE,
        "registrationScope": "rhythm-structure-only",
        "occupiedSteps": EXPECTED_OCCUPIED_STEPS,
        "stepMultiplicities": EXPECTED_MULTIPLICITIES,
        "learnedDomains": learned_domains,
        "sourceOfTruth": "read-only-reviewed-training-evidence",
        "eligibleAsSimilarityAnchor": True,
        "eligibleForChordTransfer": False,
        "eligibleForTimingTransfer": False,
        "eligibleForTechniqueTransfer": False,
    }

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    registered = bool(source_unchanged)
    passed = bool(
        registered
        and registration["eligibleAsSimilarityAnchor"]
        and learned_domains["rhythmStructure"]
        and not learned_domains["chordShape"]
        and not learned_domains["timing"]
        and not learned_domains["technique"]
    )

    recommended = (
        "diagnose-gomyway-rhythm-whole-song-with-anchor-36-v1"
        if passed
        else "register-gomyway-rhythm-novel-anchor-36-read-only-v1"
    )

    output = {
        "schemaVersion": 1,
        "registrationType": "read-only-reviewed-novel-rhythm-anchor-registration",
        "passed": passed,
        "anchorRegistration": registration,
        "anchor36RegisteredReadOnly": registered,
        "registeredRhythmAnchorMeasures": [TARGET_MEASURE],
        "queuedTrainingAnchorMeasures": QUEUED_AFTER,
        "registrationChangesProtectedSource": False,
        "classificationClaimed": False,
        "rhythmTransferClaimed": False,
        "chordTransferClaimed": False,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "thresholdRelaxationAllowed": False,
        "automaticApplyAllowed": False,
        "readOnlyRegistration": True,
        "readyForWholeSongSimilarityWithAnchor36": passed,
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
        "registrationScope": "rhythm-structure-only",
        "occupiedSteps": EXPECTED_OCCUPIED_STEPS,
        "anchor36RegisteredReadOnly": registered,
        "eligibleAsSimilarityAnchor": registration["eligibleAsSimilarityAnchor"],
        "queuedTrainingAnchorMeasures": QUEUED_AFTER,
        "automaticApplyAllowed": False,
        "readyForWholeSongSimilarityWithAnchor36": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM NOVEL ANCHOR 36 READ-ONLY REGISTRATION V1 COMPLETE")
    print("Passed:", passed)
    print("Measure:", TARGET_MEASURE)
    print("Anchor 36 registered read-only:", registered)
    print("Registration scope: rhythm-structure-only")
    print("Occupied steps:", EXPECTED_OCCUPIED_STEPS)
    print("Step multiplicities:", EXPECTED_MULTIPLICITIES)
    print("Eligible as similarity anchor: True")
    print("Chord knowledge registered: False")
    print("Timing knowledge registered: False")
    print("Technique knowledge registered: False")
    print("Queued training anchors:", QUEUED_AFTER)
    print("Threshold relaxation allowed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for whole-song similarity with anchor 36:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
