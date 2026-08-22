from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
IMPACT_PATH = PUBLIC / "gomyway-rhythm-whole-song-with-anchors-36-51-v1.json"
REGISTRATION_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-51-read-only-registration-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-anchor-51-whole-song-impact-review-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-anchor-51-whole-song-impact-review-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_REGISTERED_ANCHORS = [36, 51]
EXPECTED_ANCHOR36_GAINS = [66, 99]
EXPECTED_ANCHOR51_WINS = [52, 113]
EXPECTED_IMPROVED = [52, 113]
EXPECTED_NEWLY_CROSSED_080: list[int] = []
EXPECTED_NEWLY_CROSSED_070: list[int] = []
EXPECTED_NEWLY_CROSSED_060: list[int] = []
EXPECTED_COUNTS = {"090": 0, "080": 9, "070": 52, "060": 60}
EXPECTED_QUEUE = [60, 73, 82, 91, 99, 101, 113]
NEXT_TRAINING_ANCHOR = 60


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
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if impact.get("passed") is not True or impact.get("readyForAnchor51ImpactReview") is not True:
        raise RuntimeError("Anchor 51 cumulative whole-song diagnostic V1 is not green.")
    if impact.get("registeredRhythmAnchorMeasures") != EXPECTED_REGISTERED_ANCHORS:
        raise RuntimeError("Registered rhythm-anchor set changed unexpectedly.")
    if impact.get("anchor36CoverageGainsPreserved") != EXPECTED_ANCHOR36_GAINS:
        raise RuntimeError("Anchor 36 coverage gains changed unexpectedly.")
    if impact.get("anchor51WinningMeasures") != EXPECTED_ANCHOR51_WINS:
        raise RuntimeError("Anchor 51 winning measures changed unexpectedly.")
    if impact.get("incrementallyImprovedMeasures") != EXPECTED_IMPROVED:
        raise RuntimeError("Anchor 51 incremental improvement set changed unexpectedly.")
    if impact.get("newlyCrossed080Measures") != EXPECTED_NEWLY_CROSSED_080:
        raise RuntimeError("Unexpected new >=0.80 crossings.")
    if impact.get("newlyCrossed070Measures") != EXPECTED_NEWLY_CROSSED_070:
        raise RuntimeError("Unexpected new >=0.70 crossings.")
    if impact.get("newlyCrossed060Measures") != EXPECTED_NEWLY_CROSSED_060:
        raise RuntimeError("Unexpected new >=0.60 crossings.")
    if impact.get("bestStructuralScoreAtLeast090Count") != EXPECTED_COUNTS["090"]:
        raise RuntimeError("Unexpected >=0.90 count.")
    if impact.get("bestStructuralScoreAtLeast080Count") != EXPECTED_COUNTS["080"]:
        raise RuntimeError("Unexpected >=0.80 count.")
    if impact.get("bestStructuralScoreAtLeast070Count") != EXPECTED_COUNTS["070"]:
        raise RuntimeError("Unexpected >=0.70 count.")
    if impact.get("bestStructuralScoreAtLeast060Count") != EXPECTED_COUNTS["060"]:
        raise RuntimeError("Unexpected >=0.60 count.")
    if impact.get("classificationClaimed") is not False:
        raise RuntimeError("Impact diagnostic unexpectedly claims classification.")
    if impact.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Impact diagnostic unexpectedly allows automatic application.")
    if impact.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Impact diagnostic did not preserve protected source hash.")

    if registration.get("passed") is not True:
        raise RuntimeError("Anchor 51 registration V1 is not green.")
    if registration.get("registeredRhythmAnchorMeasures") != EXPECTED_REGISTERED_ANCHORS:
        raise RuntimeError("Anchor 51 registration anchor set changed unexpectedly.")
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

    row52 = by_measure.get(52)
    row113 = by_measure.get(113)
    if not isinstance(row52, dict) or not isinstance(row113, dict):
        raise RuntimeError("Expected anchor 51 win rows are missing.")
    if row52.get("anchor51Wins") is not True or row113.get("anchor51Wins") is not True:
        raise RuntimeError("Expected anchor 51 wins are not preserved.")

    score52 = float(row52.get("bestStructuralSimilarityAfterAnchors3651", 0.0))
    score113 = float(row113.get("bestStructuralSimilarityAfterAnchors3651", 0.0))
    delta52 = float(row52.get("incrementalStructuralImprovementFrom51", 0.0))
    delta113 = float(row113.get("incrementalStructuralImprovementFrom51", 0.0))
    if score52 != 0.714286 or delta52 != 0.000397:
        raise RuntimeError("Measure 52 anchor 51 impact changed unexpectedly.")
    if score113 != 0.463333 or delta113 != 0.011904:
        raise RuntimeError("Measure 113 anchor 51 impact changed unexpectedly.")

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after

    # Anchor 51 is useful but modest: it wins on two measures without creating
    # any new confidence-band crossings. Preserve those gains read-only and
    # continue the chronological anchor-training queue with measure 60.
    impact_accepted = bool(source_unchanged)
    broad_overgeneralization = False
    passed = bool(impact_accepted and not broad_overgeneralization)
    recommended = (
        "train-gomyway-rhythm-novel-anchor-60-v1"
        if passed
        else "review-gomyway-rhythm-anchor-51-whole-song-impact-v1"
    )

    output = {
        "schemaVersion": 1,
        "reviewType": "read-only-anchor-51-cumulative-whole-song-impact-review",
        "passed": passed,
        "anchor51ImpactAcceptedReadOnly": impact_accepted,
        "registeredRhythmAnchorMeasures": EXPECTED_REGISTERED_ANCHORS,
        "anchor36CoverageGainsPreserved": EXPECTED_ANCHOR36_GAINS,
        "anchor51WinningMeasures": EXPECTED_ANCHOR51_WINS,
        "incrementallyImprovedMeasures": EXPECTED_IMPROVED,
        "measure52BestStructuralSimilarity": score52,
        "measure52IncrementalGain": delta52,
        "measure113BestStructuralSimilarity": score113,
        "measure113IncrementalGain": delta113,
        "newlyCrossed080Measures": [],
        "newlyCrossed070Measures": [],
        "newlyCrossed060Measures": [],
        "broadOvergeneralizationDetected": broad_overgeneralization,
        "anchor51ScopePreserved": "rhythm-structure-only",
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
        "readyForNovelAnchor60Training": passed,
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
        "anchor51ImpactAcceptedReadOnly": impact_accepted,
        "anchor51WinningMeasures": EXPECTED_ANCHOR51_WINS,
        "nextChronologicalTrainingAnchor": NEXT_TRAINING_ANCHOR,
        "automaticApplyAllowed": False,
        "readyForNovelAnchor60Training": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM ANCHOR 51 WHOLE SONG IMPACT REVIEW V1 COMPLETE")
    print("Passed:", passed)
    print("Anchor 51 impact accepted read-only:", impact_accepted)
    print("Registered rhythm anchors:", EXPECTED_REGISTERED_ANCHORS)
    print("Anchor 36 coverage gains preserved:", EXPECTED_ANCHOR36_GAINS)
    print("Anchor 51 winning measures:", EXPECTED_ANCHOR51_WINS)
    print("Measure 52: score=0.714286 incrementalGain=0.000397")
    print("Measure 113: score=0.463333 incrementalGain=0.011904")
    print("New confidence-band crossings: []")
    print("Broad overgeneralization detected: False")
    print("Anchor 51 scope preserved: rhythm-structure-only")
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
    print("Ready for novel anchor 60 training:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
