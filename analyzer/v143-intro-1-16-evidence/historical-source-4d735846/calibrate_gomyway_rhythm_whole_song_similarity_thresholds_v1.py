from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
DIAGNOSTIC_PATH = PUBLIC / "gomyway-rhythm-whole-song-learned-similarity-diagnostic-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-whole-song-similarity-threshold-calibration-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-whole-song-similarity-threshold-calibration-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_UNTRAINED_MEASURE_COUNT = 78

STRUCTURAL_THRESHOLDS = (0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60)
MARGIN_THRESHOLDS = (0.05, 0.03, 0.02, 0.01, 0.00)
MUSICAL_FLOORS = (0.75, 0.70, 0.65, 0.60, 0.00)


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


def number(row: dict[str, Any], key: str) -> float:
    value = row.get(key)
    if isinstance(value, bool):
        raise RuntimeError(f"Unexpected boolean for {key}")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {value!r}") from exc


def integer(row: dict[str, Any], key: str) -> int:
    value = row.get(key)
    if isinstance(value, bool):
        raise RuntimeError(f"Unexpected boolean for {key}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {value!r}") from exc


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {
            "min": 0.0,
            "p10": 0.0,
            "p25": 0.0,
            "median": 0.0,
            "p75": 0.0,
            "p90": 0.0,
            "max": 0.0,
        }
    return {
        "min": round(min(values), 6),
        "p10": round(percentile(values, 0.10), 6),
        "p25": round(percentile(values, 0.25), 6),
        "median": round(percentile(values, 0.50), 6),
        "p75": round(percentile(values, 0.75), 6),
        "p90": round(percentile(values, 0.90), 6),
        "max": round(max(values), 6),
    }


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    diagnostic = load(DIAGNOSTIC_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if diagnostic.get("passed") is not True:
        raise RuntimeError("Whole-song learned-similarity diagnostic V1 is not green.")
    if diagnostic.get("readyForSimilarityThresholdCalibration") is not True:
        raise RuntimeError("Similarity diagnostic is not ready for threshold calibration.")
    if diagnostic.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Diagnostic unexpectedly allows automatic application.")
    if diagnostic.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Diagnostic did not preserve the protected source hash.")

    rows = diagnostic.get("rows")
    if not isinstance(rows, list) or len(rows) != EXPECTED_UNTRAINED_MEASURE_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_UNTRAINED_MEASURE_COUNT} diagnostic rows, "
            f"found {len(rows) if isinstance(rows, list) else 'non-list'}."
        )

    normalized: list[dict[str, Any]] = []
    for raw in rows:
        if not isinstance(raw, dict):
            raise RuntimeError("Diagnostic row is not an object.")
        normalized.append(
            {
                "measureNumber": integer(raw, "measureNumber"),
                "bestAnchorMeasure": integer(raw, "bestAnchorMeasure"),
                "structural": number(raw, "bestStructuralSimilarityScore"),
                "musical": number(raw, "bestMusicalSimilarityScore"),
                "margin": number(raw, "bestVsRunnerUpMargin"),
            }
        )

    structural_values = [row["structural"] for row in normalized]
    musical_values = [row["musical"] for row in normalized]
    margin_values = [row["margin"] for row in normalized]

    structural_counts = {
        f"ge_{threshold:.2f}": sum(row["structural"] >= threshold for row in normalized)
        for threshold in STRUCTURAL_THRESHOLDS
    }
    margin_counts = {
        f"ge_{threshold:.2f}": sum(row["margin"] >= threshold for row in normalized)
        for threshold in MARGIN_THRESHOLDS
    }

    grid: list[dict[str, Any]] = []
    for structural_threshold in STRUCTURAL_THRESHOLDS:
        for margin_threshold in MARGIN_THRESHOLDS:
            for musical_floor in MUSICAL_FLOORS:
                selected = [
                    row
                    for row in normalized
                    if row["structural"] >= structural_threshold
                    and row["margin"] >= margin_threshold
                    and row["musical"] >= musical_floor
                ]
                grid.append(
                    {
                        "structuralThreshold": structural_threshold,
                        "marginThreshold": margin_threshold,
                        "musicalFloor": musical_floor,
                        "candidateCount": len(selected),
                        "candidateMeasures": [row["measureNumber"] for row in selected],
                    }
                )

    # Calibration bands are evidence-reporting labels only. They do not classify,
    # mutate, project, promote, or apply anything to source events.
    conservative = [
        row
        for row in normalized
        if row["structural"] >= 0.85
        and row["margin"] >= 0.03
        and row["musical"] >= 0.70
    ]
    exploratory = [
        row
        for row in normalized
        if row["structural"] >= 0.80
        and row["margin"] >= 0.02
        and row["musical"] >= 0.65
    ]
    broad = [
        row
        for row in normalized
        if row["structural"] >= 0.75
        and row["margin"] >= 0.01
        and row["musical"] >= 0.60
    ]

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and len(normalized) == EXPECTED_UNTRAINED_MEASURE_COUNT
        and all(36 <= row["measureNumber"] <= 113 for row in normalized)
    )

    recommended = (
        "review-gomyway-rhythm-whole-song-similarity-calibration-v1"
        if passed
        else "calibrate-gomyway-rhythm-whole-song-similarity-thresholds-v1"
    )

    output = {
        "schemaVersion": 1,
        "calibrationType": "read-only-whole-song-rhythm-similarity-threshold-calibration",
        "passed": passed,
        "untrainedMeasureCount": len(normalized),
        "structuralDistribution": summarize(structural_values),
        "musicalDistribution": summarize(musical_values),
        "marginDistribution": summarize(margin_values),
        "structuralThresholdCounts": structural_counts,
        "marginThresholdCounts": margin_counts,
        "thresholdGrid": grid,
        "evidenceBands": {
            "conservative": {
                "structuralThreshold": 0.85,
                "marginThreshold": 0.03,
                "musicalFloor": 0.70,
                "candidateCount": len(conservative),
                "candidateMeasures": [row["measureNumber"] for row in conservative],
            },
            "exploratory": {
                "structuralThreshold": 0.80,
                "marginThreshold": 0.02,
                "musicalFloor": 0.65,
                "candidateCount": len(exploratory),
                "candidateMeasures": [row["measureNumber"] for row in exploratory],
            },
            "broad": {
                "structuralThreshold": 0.75,
                "marginThreshold": 0.01,
                "musicalFloor": 0.60,
                "candidateCount": len(broad),
                "candidateMeasures": [row["measureNumber"] for row in broad],
            },
        },
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "readOnlyCalibration": True,
        "readyForCalibrationReview": passed,
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
        "untrainedMeasureCount": len(normalized),
        "conservativeCandidateCount": len(conservative),
        "exploratoryCandidateCount": len(exploratory),
        "broadCandidateCount": len(broad),
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "readyForCalibrationReview": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM WHOLE SONG SIMILARITY THRESHOLD CALIBRATION V1 COMPLETE")
    print("Passed:", passed)
    print("Untrained measures calibrated:", len(normalized))
    print("Structural score distribution:", summarize(structural_values))
    print("Musical score distribution:", summarize(musical_values))
    print("Best-vs-runner-up margin distribution:", summarize(margin_values))
    print("Structural threshold counts:")
    for threshold in STRUCTURAL_THRESHOLDS:
        print(f"  >= {threshold:.2f}: {structural_counts[f'ge_{threshold:.2f}']}")
    print("Evidence bands (read-only):")
    print(
        "  conservative structural>=0.85 margin>=0.03 musical>=0.70:",
        len(conservative),
        [row["measureNumber"] for row in conservative],
    )
    print(
        "  exploratory structural>=0.80 margin>=0.02 musical>=0.65:",
        len(exploratory),
        [row["measureNumber"] for row in exploratory],
    )
    print(
        "  broad structural>=0.75 margin>=0.01 musical>=0.60:",
        len(broad),
        [row["measureNumber"] for row in broad],
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
    print("Ready for calibration review:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
