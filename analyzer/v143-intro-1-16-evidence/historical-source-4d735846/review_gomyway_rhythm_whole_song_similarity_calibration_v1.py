from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
DIAGNOSTIC_PATH = PUBLIC / "gomyway-rhythm-whole-song-learned-similarity-diagnostic-v1.json"
CALIBRATION_PATH = PUBLIC / "gomyway-rhythm-whole-song-similarity-threshold-calibration-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-whole-song-similarity-calibration-review-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-whole-song-similarity-calibration-review-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_UNTRAINED_MEASURE_COUNT = 78


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


def require_number(row: dict[str, Any], key: str) -> float:
    value = row.get(key)
    if isinstance(value, bool):
        raise RuntimeError(f"Unexpected boolean for {key}")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {value!r}") from exc


def require_int(row: dict[str, Any], key: str) -> int:
    value = row.get(key)
    if isinstance(value, bool):
        raise RuntimeError(f"Unexpected boolean for {key}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {value!r}") from exc


def band_measures(calibration: dict[str, Any], name: str) -> list[int]:
    evidence = calibration.get("evidenceBands")
    if not isinstance(evidence, dict):
        raise RuntimeError("Calibration evidenceBands missing.")
    band = evidence.get(name)
    if not isinstance(band, dict):
        raise RuntimeError(f"Calibration band missing: {name}")
    measures = band.get("candidateMeasures")
    if not isinstance(measures, list):
        raise RuntimeError(f"Calibration band candidateMeasures missing: {name}")
    return [int(value) for value in measures]


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    diagnostic = load(DIAGNOSTIC_PATH)
    calibration = load(CALIBRATION_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if diagnostic.get("passed") is not True:
        raise RuntimeError("Similarity diagnostic V1 is not green.")
    if calibration.get("passed") is not True:
        raise RuntimeError("Similarity threshold calibration V1 is not green.")
    if calibration.get("readyForCalibrationReview") is not True:
        raise RuntimeError("Calibration is not ready for review.")
    if calibration.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Calibration unexpectedly allows automatic application.")
    if calibration.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Calibration did not preserve protected source hash.")

    raw_rows = diagnostic.get("rows")
    if not isinstance(raw_rows, list) or len(raw_rows) != EXPECTED_UNTRAINED_MEASURE_COUNT:
        raise RuntimeError("Diagnostic does not contain exactly 78 untrained-measure rows.")

    rows: dict[int, dict[str, Any]] = {}
    for raw in raw_rows:
        if not isinstance(raw, dict):
            raise RuntimeError("Diagnostic row is not an object.")
        measure = require_int(raw, "measureNumber")
        rows[measure] = {
            "measureNumber": measure,
            "anchorMeasure": require_int(raw, "bestAnchorMeasure"),
            "runnerUpAnchorMeasure": require_int(raw, "runnerUpAnchorMeasure"),
            "structural": require_number(raw, "bestStructuralSimilarityScore"),
            "musical": require_number(raw, "bestMusicalSimilarityScore"),
            "margin": require_number(raw, "bestVsRunnerUpMargin"),
        }

    conservative = band_measures(calibration, "conservative")
    exploratory = band_measures(calibration, "exploratory")
    broad = band_measures(calibration, "broad")

    if not set(conservative) <= set(exploratory):
        raise RuntimeError("Conservative band is not nested inside exploratory band.")
    if not set(exploratory) <= set(broad):
        raise RuntimeError("Exploratory band is not nested inside broad band.")

    def details(measures: list[int]) -> list[dict[str, Any]]:
        return [rows[measure] for measure in measures]

    conservative_rows = details(conservative)
    exploratory_rows = details(exploratory)
    broad_rows = details(broad)

    anchor_counts = {
        "conservative": dict(sorted(Counter(row["anchorMeasure"] for row in conservative_rows).items())),
        "exploratory": dict(sorted(Counter(row["anchorMeasure"] for row in exploratory_rows).items())),
        "broad": dict(sorted(Counter(row["anchorMeasure"] for row in broad_rows).items())),
    }

    # Review-only provisional gate. This exactly mirrors the exploratory calibration
    # band and does not classify, project, mutate, or promote any source event.
    provisional_gate = {
        "structuralThreshold": 0.80,
        "marginThreshold": 0.02,
        "musicalFloor": 0.65,
    }
    provisional_rows = [
        row
        for row in rows.values()
        if row["structural"] >= provisional_gate["structuralThreshold"]
        and row["margin"] >= provisional_gate["marginThreshold"]
        and row["musical"] >= provisional_gate["musicalFloor"]
    ]
    provisional_rows.sort(key=lambda row: row["measureNumber"])

    ambiguous_high_structure = [
        row
        for row in rows.values()
        if row["structural"] >= 0.80 and row["margin"] < 0.02
    ]
    ambiguous_high_structure.sort(key=lambda row: row["measureNumber"])

    runner_up_close = [
        row
        for row in rows.values()
        if row["margin"] < 0.01
    ]
    runner_up_close.sort(key=lambda row: row["measureNumber"])

    anchor_to_measures: dict[int, list[int]] = defaultdict(list)
    for row in provisional_rows:
        anchor_to_measures[row["anchorMeasure"]].append(row["measureNumber"])

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and len(rows) == EXPECTED_UNTRAINED_MEASURE_COUNT
        and [row["measureNumber"] for row in provisional_rows] == exploratory
    )

    recommended = (
        "prove-gomyway-rhythm-whole-song-provisional-generalization-v1"
        if passed and provisional_rows
        else "review-gomyway-rhythm-whole-song-similarity-calibration-v1"
    )

    output = {
        "schemaVersion": 1,
        "reviewType": "read-only-whole-song-rhythm-similarity-calibration-review",
        "passed": passed,
        "untrainedMeasureCount": len(rows),
        "evidenceBandCounts": {
            "conservative": len(conservative_rows),
            "exploratory": len(exploratory_rows),
            "broad": len(broad_rows),
        },
        "conservativeMeasures": conservative,
        "exploratoryMeasures": exploratory,
        "broadMeasures": broad,
        "anchorCountsByBand": anchor_counts,
        "provisionalGeneralizationGate": provisional_gate,
        "provisionalCandidateCount": len(provisional_rows),
        "provisionalCandidateMeasures": [row["measureNumber"] for row in provisional_rows],
        "provisionalCandidateDetails": provisional_rows,
        "provisionalAnchorToMeasures": {
            str(anchor): measures for anchor, measures in sorted(anchor_to_measures.items())
        },
        "highStructuralButAmbiguousCount": len(ambiguous_high_structure),
        "highStructuralButAmbiguousMeasures": [
            row["measureNumber"] for row in ambiguous_high_structure
        ],
        "runnerUpMarginBelow001Count": len(runner_up_close),
        "runnerUpMarginBelow001Measures": [row["measureNumber"] for row in runner_up_close],
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "readOnlyReview": True,
        "readyForProvisionalGeneralizationProof": bool(passed and provisional_rows),
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
        "provisionalCandidateCount": len(provisional_rows),
        "provisionalCandidateMeasures": [row["measureNumber"] for row in provisional_rows],
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "readyForProvisionalGeneralizationProof": bool(passed and provisional_rows),
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM WHOLE SONG SIMILARITY CALIBRATION REVIEW V1 COMPLETE")
    print("Passed:", passed)
    print("Untrained measures reviewed:", len(rows))
    print("Evidence band counts:")
    print("  conservative:", len(conservative_rows), conservative)
    print("  exploratory:", len(exploratory_rows), exploratory)
    print("  broad:", len(broad_rows), broad)
    print("Provisional generalization gate:", provisional_gate)
    print("Provisional candidate count:", len(provisional_rows))
    print("Provisional candidate measures:", [row["measureNumber"] for row in provisional_rows])
    print("Provisional anchors:", dict(sorted(anchor_to_measures.items())))
    print("High structural but ambiguous:", len(ambiguous_high_structure), [row["measureNumber"] for row in ambiguous_high_structure])
    print("Runner-up margin < 0.01:", len(runner_up_close))
    print("Classification claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for provisional generalization proof:", bool(passed and provisional_rows))
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
