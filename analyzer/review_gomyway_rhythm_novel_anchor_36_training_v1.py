from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
TRAINING_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-36-training-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-36-training-review-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-36-training-review-v1-manifest.json"

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
    training = load(TRAINING_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if training.get("passed") is not True:
        raise RuntimeError("Novel anchor 36 training V1 is not green.")
    if training.get("measureNumber") != TARGET_MEASURE:
        raise RuntimeError("Novel anchor training target changed unexpectedly.")
    if training.get("readyForNovelAnchor36TrainingReview") is not True:
        raise RuntimeError("Training artifact is not ready for review.")
    if training.get("anchorTrainingClaimedAsTruth") is not False:
        raise RuntimeError("Training artifact unexpectedly claims training truth.")
    if training.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Training artifact unexpectedly allows threshold relaxation.")
    if training.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Training artifact unexpectedly allows automatic application.")
    if training.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Training artifact did not preserve protected source hash.")
    if training.get("queuedTrainingAnchorMeasures") != QUEUED_AFTER:
        raise RuntimeError("Queued training-anchor order changed unexpectedly.")

    rhythm = training.get("rhythmEvidence")
    chord = training.get("chordShapeEvidence")
    timing = training.get("timingEvidence")
    technique = training.get("techniqueEvidence")
    if not all(isinstance(item, dict) for item in (rhythm, chord, timing, technique)):
        raise RuntimeError("One or more training evidence domains are missing.")

    if rhythm.get("supported") is not True:
        raise RuntimeError("Measure 36 rhythm evidence is not supported.")
    if rhythm.get("occupiedSteps") != EXPECTED_OCCUPIED_STEPS:
        raise RuntimeError("Measure 36 occupied-step pattern changed unexpectedly.")
    if rhythm.get("stepMultiplicities") != EXPECTED_MULTIPLICITIES:
        raise RuntimeError("Measure 36 step multiplicities changed unexpectedly.")
    if int(rhythm.get("unquantizedEventCount", -1)) != 0:
        raise RuntimeError("Measure 36 contains unexpected unquantized events.")

    if chord.get("observationAvailable") is not False:
        raise RuntimeError("Measure 36 unexpectedly has chord-shape evidence.")
    if chord.get("multiNoteSteps") != []:
        raise RuntimeError("Measure 36 unexpectedly contains multi-note steps.")
    if timing.get("observationAvailable") is not False:
        raise RuntimeError("Measure 36 unexpectedly has timing evidence.")
    if technique.get("observationAvailable") is not False:
        raise RuntimeError("Measure 36 unexpectedly has technique evidence.")
    if int(technique.get("explicitTechniqueEventCount", -1)) != 0:
        raise RuntimeError("Measure 36 unexpectedly contains explicit technique events.")

    rhythm_pattern_accepted = True
    chord_domain_closed_unsupported = True
    timing_domain_closed_unsupported = True
    technique_domain_closed_unsupported = True

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and rhythm_pattern_accepted
        and chord_domain_closed_unsupported
        and timing_domain_closed_unsupported
        and technique_domain_closed_unsupported
    )

    recommended = (
        "register-gomyway-rhythm-novel-anchor-36-read-only-v1"
        if passed
        else "review-gomyway-rhythm-novel-anchor-36-training-v1"
    )

    output = {
        "schemaVersion": 1,
        "reviewType": "read-only-novel-rhythm-anchor-training-review",
        "passed": passed,
        "measureNumber": TARGET_MEASURE,
        "rhythmPatternAcceptedAsTrainingEvidence": rhythm_pattern_accepted,
        "occupiedSteps": EXPECTED_OCCUPIED_STEPS,
        "stepMultiplicities": EXPECTED_MULTIPLICITIES,
        "chordShapeDomainClosedUnsupported": chord_domain_closed_unsupported,
        "timingDomainClosedUnsupported": timing_domain_closed_unsupported,
        "techniqueDomainClosedUnsupported": technique_domain_closed_unsupported,
        "queuedTrainingAnchorMeasures": QUEUED_AFTER,
        "anchorRegisteredAsLearnedTruth": False,
        "classificationClaimed": False,
        "rhythmTransferClaimed": False,
        "chordTransferClaimed": False,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "thresholdRelaxationAllowed": False,
        "automaticApplyAllowed": False,
        "readOnlyReview": True,
        "readyForNovelAnchor36ReadOnlyRegistration": passed,
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
        "rhythmPatternAcceptedAsTrainingEvidence": rhythm_pattern_accepted,
        "chordShapeDomainClosedUnsupported": chord_domain_closed_unsupported,
        "timingDomainClosedUnsupported": timing_domain_closed_unsupported,
        "techniqueDomainClosedUnsupported": technique_domain_closed_unsupported,
        "anchorRegisteredAsLearnedTruth": False,
        "automaticApplyAllowed": False,
        "readyForNovelAnchor36ReadOnlyRegistration": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM NOVEL ANCHOR 36 TRAINING REVIEW V1 COMPLETE")
    print("Passed:", passed)
    print("Measure:", TARGET_MEASURE)
    print("Rhythm pattern accepted as training evidence:", rhythm_pattern_accepted)
    print("Occupied steps:", EXPECTED_OCCUPIED_STEPS)
    print("Step multiplicities:", EXPECTED_MULTIPLICITIES)
    print("Chord-shape domain closed unsupported:", chord_domain_closed_unsupported)
    print("Timing domain closed unsupported:", timing_domain_closed_unsupported)
    print("Technique domain closed unsupported:", technique_domain_closed_unsupported)
    print("Anchor registered as learned truth: False")
    print("Threshold relaxation allowed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for novel anchor 36 read-only registration:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
