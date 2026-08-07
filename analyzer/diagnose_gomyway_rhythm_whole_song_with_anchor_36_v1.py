from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
BASELINE_PATH = PUBLIC / "gomyway-rhythm-whole-song-learned-similarity-diagnostic-v1.json"
REGISTRATION_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-36-read-only-registration-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-whole-song-with-anchor-36-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-whole-song-with-anchor-36-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
FIRST_MEASURE = 1
LAST_MEASURE = 113
NEW_ANCHOR = 36
TARGET_START = 37
EXPECTED_TARGET_COUNT = 77
EXPECTED_OCCUPIED_STEPS = [0, 3, 5, 10, 14, 15]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def measure_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def jaccard(a: set[int], b: set[int]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 1.0


def ratio_similarity(a: int, b: int) -> float:
    if a == 0 and b == 0:
        return 1.0
    if a <= 0 or b <= 0:
        return 0.0
    return min(a, b) / max(a, b)


def build_profiles(events: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    grouped: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for event in events:
        measure = measure_of(event)
        step = step_of(event)
        if measure is None or step is None or not FIRST_MEASURE <= measure <= LAST_MEASURE:
            continue
        grouped[measure][step].append(event)

    profiles: dict[int, dict[str, Any]] = {}
    for measure in range(FIRST_MEASURE, LAST_MEASURE + 1):
        step_map = grouped.get(measure, {})
        occupied = set(step_map)
        multiplicity = {step: len(rows) for step, rows in step_map.items()}
        profiles[measure] = {
            "occupiedSteps": occupied,
            "multiplicityByStep": multiplicity,
            "sourceEventRows": sum(len(rows) for rows in step_map.values()),
        }
    return profiles


def compare_rhythm(a: dict[str, Any], b: dict[str, Any]) -> dict[str, float]:
    steps_a: set[int] = a["occupiedSteps"]
    steps_b: set[int] = b["occupiedSteps"]
    occupied = jaccard(steps_a, steps_b)
    shared = steps_a & steps_b
    if shared:
        multiplicity_scores = []
        for step in shared:
            ma = int(a["multiplicityByStep"].get(step, 0))
            mb = int(b["multiplicityByStep"].get(step, 0))
            multiplicity_scores.append(1.0 - min(1.0, abs(ma - mb) / max(1, ma, mb)))
        multiplicity = sum(multiplicity_scores) / len(multiplicity_scores)
    else:
        multiplicity = 0.0
    density = ratio_similarity(int(a["sourceEventRows"]), int(b["sourceEventRows"]))
    structural = occupied * 0.50 + multiplicity * 0.30 + density * 0.20
    return {
        "occupiedStepJaccard": round(occupied, 6),
        "sharedStepMultiplicitySimilarity": round(multiplicity, 6),
        "rowDensitySimilarity": round(density, 6),
        "rhythmStructuralSimilarityScore": round(structural, 6),
    }


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    baseline = load(BASELINE_PATH)
    registration = load(REGISTRATION_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}.")
    if baseline.get("passed") is not True:
        raise RuntimeError("Baseline whole-song similarity diagnostic V1 is not green.")
    if registration.get("passed") is not True:
        raise RuntimeError("Anchor 36 registration V1 is not green.")
    if registration.get("anchor36RegisteredReadOnly") is not True:
        raise RuntimeError("Anchor 36 is not registered read-only.")
    if registration.get("registrationScope") != "rhythm-structure-only":
        raise RuntimeError("Anchor 36 registration scope changed unexpectedly.")
    if registration.get("occupiedSteps") != EXPECTED_OCCUPIED_STEPS:
        raise RuntimeError("Anchor 36 occupied-step pattern changed unexpectedly.")
    if registration.get("eligibleAsSimilarityAnchor") is not True:
        raise RuntimeError("Anchor 36 is not eligible as a similarity anchor.")
    if any(registration.get(key) is not False for key in (
        "chordKnowledgeRegistered", "timingKnowledgeRegistered", "techniqueKnowledgeRegistered"
    )):
        raise RuntimeError("Anchor 36 unexpectedly contains non-rhythm knowledge.")
    if registration.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Anchor 36 registration unexpectedly allows automatic application.")
    if registration.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Anchor 36 registration did not preserve protected source hash.")

    profiles = build_profiles(events)
    if sorted(profiles[NEW_ANCHOR]["occupiedSteps"]) != EXPECTED_OCCUPIED_STEPS:
        raise RuntimeError("Protected source profile for measure 36 no longer matches registration.")

    baseline_rows = baseline.get("rows")
    if not isinstance(baseline_rows, list):
        raise RuntimeError("Baseline diagnostic rows missing.")
    baseline_by_measure = {
        int(row["measureNumber"]): row
        for row in baseline_rows
        if isinstance(row, dict) and "measureNumber" in row
    }

    rows: list[dict[str, Any]] = []
    won_by_anchor36: list[int] = []
    improved_measures: list[int] = []
    improved_to_080: list[int] = []
    improved_to_070: list[int] = []
    improved_to_060: list[int] = []

    for measure in range(TARGET_START, LAST_MEASURE + 1):
        prior = baseline_by_measure.get(measure)
        if prior is None:
            raise RuntimeError(f"Missing baseline row for measure {measure}.")

        old_anchor = int(prior["bestAnchorMeasure"])
        old_score = float(prior["bestStructuralSimilarityScore"])
        anchor36 = compare_rhythm(profiles[measure], profiles[NEW_ANCHOR])
        anchor36_score = float(anchor36["rhythmStructuralSimilarityScore"])

        # Anchor 36 is rhythm-only, so it may replace the old winner only on
        # rhythm-structural evidence. We never infer chord/timing/technique here.
        wins = anchor36_score > old_score
        best_anchor = NEW_ANCHOR if wins else old_anchor
        best_score = anchor36_score if wins else old_score
        delta = round(best_score - old_score, 6)

        if wins:
            won_by_anchor36.append(measure)
        if delta > 0:
            improved_measures.append(measure)
        if old_score < 0.80 <= best_score:
            improved_to_080.append(measure)
        if old_score < 0.70 <= best_score:
            improved_to_070.append(measure)
        if old_score < 0.60 <= best_score:
            improved_to_060.append(measure)

        rows.append({
            "measureNumber": measure,
            "baselineBestAnchorMeasure": old_anchor,
            "baselineBestStructuralSimilarityScore": old_score,
            "anchor36RhythmComparison": anchor36,
            "anchor36Wins": wins,
            "bestAnchorAfterAnchor36": best_anchor,
            "bestStructuralSimilarityAfterAnchor36": round(best_score, 6),
            "structuralImprovement": delta,
            "classificationClaimed": False,
            "automaticApplyAllowed": False,
        })

    new_scores = [float(row["bestStructuralSimilarityAfterAnchor36"]) for row in rows]
    counts = {
        "atLeast090": sum(score >= 0.90 for score in new_scores),
        "atLeast080": sum(score >= 0.80 for score in new_scores),
        "atLeast070": sum(score >= 0.70 for score in new_scores),
        "atLeast060": sum(score >= 0.60 for score in new_scores),
    }

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(source_unchanged and len(rows) == EXPECTED_TARGET_COUNT)

    recommended = (
        "review-gomyway-rhythm-anchor-36-whole-song-impact-v1"
        if passed
        else "diagnose-gomyway-rhythm-whole-song-with-anchor-36-v1"
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-whole-song-rhythm-similarity-with-anchor-36",
        "passed": passed,
        "targetMeasureRange": [TARGET_START, LAST_MEASURE],
        "targetMeasureCount": len(rows),
        "registeredAnchorMeasure": NEW_ANCHOR,
        "registeredAnchorScope": "rhythm-structure-only",
        "anchor36WinCount": len(won_by_anchor36),
        "anchor36WinningMeasures": won_by_anchor36,
        "structurallyImprovedMeasureCount": len(improved_measures),
        "structurallyImprovedMeasures": improved_measures,
        "newBestStructuralScoreAtLeast090Count": counts["atLeast090"],
        "newBestStructuralScoreAtLeast080Count": counts["atLeast080"],
        "newBestStructuralScoreAtLeast070Count": counts["atLeast070"],
        "newBestStructuralScoreAtLeast060Count": counts["atLeast060"],
        "newlyCrossed080Measures": improved_to_080,
        "newlyCrossed070Measures": improved_to_070,
        "newlyCrossed060Measures": improved_to_060,
        "rows": rows,
        "classificationClaimed": False,
        "rhythmTransferClaimed": False,
        "chordTransferClaimed": False,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "thresholdRelaxationAllowed": False,
        "automaticApplyAllowed": False,
        "readOnlyDiagnostic": True,
        "readyForAnchor36ImpactReview": passed,
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
        "targetMeasureCount": len(rows),
        "anchor36WinCount": len(won_by_anchor36),
        "anchor36WinningMeasures": won_by_anchor36,
        "newBestStructuralScoreAtLeast080Count": counts["atLeast080"],
        "newBestStructuralScoreAtLeast070Count": counts["atLeast070"],
        "newBestStructuralScoreAtLeast060Count": counts["atLeast060"],
        "readyForAnchor36ImpactReview": passed,
        "recommendedNextAction": recommended,
        "automaticApplyAllowed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM WHOLE SONG WITH ANCHOR 36 V1 COMPLETE")
    print("Passed:", passed)
    print("Target measures scanned:", len(rows))
    print("Anchor 36 wins:", len(won_by_anchor36), won_by_anchor36)
    print("Structurally improved measures:", len(improved_measures), improved_measures)
    print("Best structural similarity >= 0.90:", counts["atLeast090"])
    print("Best structural similarity >= 0.80:", counts["atLeast080"])
    print("Best structural similarity >= 0.70:", counts["atLeast070"])
    print("Best structural similarity >= 0.60:", counts["atLeast060"])
    print("Newly crossed 0.80:", improved_to_080)
    print("Newly crossed 0.70:", improved_to_070)
    print("Newly crossed 0.60:", improved_to_060)
    for row in rows:
        if row["anchor36Wins"]:
            comparison = row["anchor36RhythmComparison"]
            print(
                f"measure={row['measureNumber']} oldAnchor={row['baselineBestAnchorMeasure']} "
                f"old={row['baselineBestStructuralSimilarityScore']} anchor36={comparison['rhythmStructuralSimilarityScore']} "
                f"occupied={comparison['occupiedStepJaccard']} multiplicity={comparison['sharedStepMultiplicitySimilarity']} "
                f"density={comparison['rowDensitySimilarity']} delta={row['structuralImprovement']}"
            )
    print("Classification claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for anchor 36 impact review:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
