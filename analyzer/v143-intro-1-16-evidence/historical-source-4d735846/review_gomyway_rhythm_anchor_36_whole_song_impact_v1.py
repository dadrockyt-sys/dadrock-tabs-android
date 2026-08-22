from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
IMPACT_PATH = PUBLIC / "gomyway-rhythm-whole-song-with-anchor-36-v1.json"
REGISTRATION_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-36-read-only-registration-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-anchor-36-whole-song-impact-review-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-anchor-36-whole-song-impact-review-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_ANCHOR_WINS = [66, 99]
EXPECTED_IMPROVED = [66, 99]
EXPECTED_NEWLY_CROSSED_080: list[int] = []
EXPECTED_NEWLY_CROSSED_070 = [66]
EXPECTED_NEWLY_CROSSED_060 = [99]
EXPECTED_COUNTS = {"090": 0, "080": 10, "070": 67, "060": 75}
EXPECTED_QUEUE = [51, 60, 73, 82, 91, 99, 101, 113]
NEXT_TRAINING_ANCHOR = 51


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
    impact = load(IMPACT_PATH)
    registration = load(REGISTRATION_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}.")
    if impact.get("passed") is not True or impact.get("readyForAnchor36ImpactReview") is not True:
        raise RuntimeError("Anchor 36 whole-song impact diagnostic V1 is not green.")
    if impact.get("registeredAnchorMeasure") != 36:
        raise RuntimeError("Registered anchor measure changed unexpectedly.")
    if impact.get("registeredAnchorScope") != "rhythm-structure-only":
        raise RuntimeError("Anchor 36 impact scope changed unexpectedly.")
    if impact.get("anchor36WinningMeasures") != EXPECTED_ANCHOR_WINS:
        raise RuntimeError("Anchor 36 winning measures changed unexpectedly.")
    if impact.get("structurallyImprovedMeasures") != EXPECTED_IMPROVED:
        raise RuntimeError("Anchor 36 improved-measure set changed unexpectedly.")
    if impact.get("newlyCrossed080Measures") != EXPECTED_NEWLY_CROSSED_080:
        raise RuntimeError("Unexpected new >=0.80 crossings.")
    if impact.get("newlyCrossed070Measures") != EXPECTED_NEWLY_CROSSED_070:
        raise RuntimeError("Unexpected new >=0.70 crossings.")
    if impact.get("newlyCrossed060Measures") != EXPECTED_NEWLY_CROSSED_060:
        raise RuntimeError("Unexpected new >=0.60 crossings.")
    if impact.get("newBestStructuralScoreAtLeast090Count") != EXPECTED_COUNTS["090"]:
        raise RuntimeError("Unexpected >=0.90 count.")
    if impact.get("newBestStructuralScoreAtLeast080Count") != EXPECTED_COUNTS["080"]:
        raise RuntimeError("Unexpected >=0.80 count.")
    if impact.get("newBestStructuralScoreAtLeast070Count") != EXPECTED_COUNTS["070"]:
        raise RuntimeError("Unexpected >=0.70 count.")
    if impact.get("newBestStructuralScoreAtLeast060Count") != EXPECTED_COUNTS["060"]:
        raise RuntimeError("Unexpected >=0.60 count.")
    if impact.get("classificationClaimed") is not False:
        raise RuntimeError("Impact diagnostic unexpectedly claims classification.")
    if impact.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Impact diagnostic unexpectedly allows automatic application.")
    if impact.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Impact diagnostic did not preserve protected source hash.")

    if registration.get("passed") is not True:
        raise RuntimeError("Anchor 36 registration V1 is not green.")
    if registration.get("queuedTrainingAnchorMeasures") != EXPECTED_QUEUE:
        raise RuntimeError("Queued training-anchor order changed unexpectedly.")

    rows = impact.get("rows")
    if not isinstance(rows, list):
        raise RuntimeError("Impact rows missing.")
    by_measure = {
        int(row["measureNumber"]): row
        for row in rows
        if isinstance(row, dict) and "measureNumber" in row
    }
    for measure in EXPECTED_ANCHOR_WINS:
        row = by_measure.get(measure)
        if not isinstance(row, dict) or row.get("anchor36Wins") is not True:
            raise RuntimeError(f"Anchor 36 win row missing for measure {measure}.")

    row66 = by_measure[66]
    row99 = by_measure[99]
    if float(row66.get("bestStructuralSimilarityAfterAnchor36", 0.0)) != 0.75:
        raise RuntimeError("Measure 66 expected best structural score 0.75.")
    if float(row99.get("bestStructuralSimilarityAfterAnchor36", 0.0)) != 0.65:
        raise RuntimeError("Measure 99 expected best structural score 0.65.")

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after

    # Review decision: anchor 36 is useful but remains rhythm-only. Preserve the
    # two coverage gains read-only and continue section-by-section with anchor 51.
    impact_accepted = bool(source_unchanged)
    passed = impact_accepted
    recommended = (
        "train-gomyway-rhythm-novel-anchor-51-v1"
        if passed
        else "review-gomyway-rhythm-anchor-36-whole-song-impact-v1"
    )

    output = {
        "schemaVersion": 1,
        "reviewType": "read-only-anchor-36-whole-song-impact-review",
        "passed": passed,
        "anchor36ImpactAcceptedReadOnly": impact_accepted,
        "anchor36WinningMeasures": EXPECTED_ANCHOR_WINS,
        "structurallyImprovedMeasures": EXPECTED_IMPROVED,
        "measure66AcceptedAsAnchor36CoverageGain": True,
        "measure66BestStructuralSimilarity": 0.75,
        "measure66NewlyCrossed070": True,
        "measure99AcceptedAsAnchor36CoverageGain": True,
        "measure99BestStructuralSimilarity": 0.65,
        "measure99NewlyCrossed060": True,
        "newlyCrossed080Measures": [],
        "broadOvergeneralizationDetected": False,
        "anchor36ScopePreserved": "rhythm-structure-only",
        "queuedTrainingAnchorMeasures": EXPECTED_QUEUE,
        "nextChronologicalTrainingAnchor": NEXT_TRAINING_ANCHOR,
        "classificationClaimed": False,
        "rhythmTransferClaimed": False,
        "chordTransferClaimed": False,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "thresholdRelaxationAllowed": False,
        "automaticApplyAllowed": False,
        "readOnlyReview": True,
        "readyForNovelAnchor51Training": passed,
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
        "anchor36ImpactAcceptedReadOnly": impact_accepted,
        "anchor36WinningMeasures": EXPECTED_ANCHOR_WINS,
        "nextChronologicalTrainingAnchor": NEXT_TRAINING_ANCHOR,
        "automaticApplyAllowed": False,
        "readyForNovelAnchor51Training": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM ANCHOR 36 WHOLE SONG IMPACT REVIEW V1 COMPLETE")
    print("Passed:", passed)
    print("Anchor 36 impact accepted read-only:", impact_accepted)
    print("Anchor 36 winning measures:", EXPECTED_ANCHOR_WINS)
    print("Measure 66 coverage gain: 0.75 newly crossed >=0.70")
    print("Measure 99 coverage gain: 0.65 newly crossed >=0.60")
    print("Newly crossed >=0.80: []")
    print("Broad overgeneralization detected: False")
    print("Anchor 36 scope preserved: rhythm-structure-only")
    print("Next chronological training anchor:", NEXT_TRAINING_ANCHOR)
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
    print("Ready for novel anchor 51 training:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
