from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
DIAGNOSTIC_PATH = PUBLIC / "gomyway-rhythm-whole-song-learned-similarity-diagnostic-v1.json"
CLOSURE_PATH = PUBLIC / "gomyway-rhythm-whole-song-generalization-closure-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-measure-101-placement-diagnostic-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-measure-101-placement-diagnostic-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
TARGET_MEASURE = 101
EXPECTED_ANCHOR = 24
EXPECTED_RHYTHM_CLOSED = [37, 70, 80, 88, 93, 94]
EXPECTED_CHORD_CLOSED = [37, 88]


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


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def measure_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def require_number(row: dict[str, Any], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {row.get(key)!r}") from exc


def require_int(row: dict[str, Any], key: str) -> int:
    try:
        return int(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {row.get(key)!r}") from exc


def occupied_steps(events: list[dict[str, Any]], measure: int) -> list[int]:
    steps = {
        step
        for event in events
        if measure_of(event) == measure
        for step in [step_of(event)]
        if step is not None
    }
    return sorted(steps)


def best_integer_shift(target: list[int], anchor: list[int], max_abs_shift: int = 4) -> dict[str, Any]:
    target_set = set(target)
    best: dict[str, Any] | None = None
    for shift in range(-max_abs_shift, max_abs_shift + 1):
        shifted = {step + shift for step in anchor}
        overlap = len(target_set & shifted)
        union = len(target_set | shifted)
        jaccard = overlap / union if union else 1.0
        candidate = {
            "shift": shift,
            "overlapCount": overlap,
            "jaccard": round(jaccard, 6),
            "shiftedAnchorSteps": sorted(shifted),
        }
        if best is None or (candidate["jaccard"], candidate["overlapCount"], -abs(shift)) > (
            best["jaccard"], best["overlapCount"], -abs(best["shift"])
        ):
            best = candidate
    assert best is not None
    return best


def nearest_step_deltas(target: list[int], anchor: list[int]) -> list[dict[str, int]]:
    result: list[dict[str, int]] = []
    if not anchor:
        return result
    for step in target:
        nearest = min(anchor, key=lambda value: (abs(value - step), value))
        result.append({"targetStep": step, "nearestAnchorStep": nearest, "delta": step - nearest})
    return result


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    diagnostic = load(DIAGNOSTIC_PATH)
    closure = load(CLOSURE_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}.")
    if diagnostic.get("passed") is not True:
        raise RuntimeError("Whole-song learned-similarity diagnostic V1 is not green.")
    if closure.get("passed") is not True:
        raise RuntimeError("Whole-song generalization closure review V1 is not green.")
    if closure.get("wholeSongGeneralizationMilestoneClosedReadOnly") is not True:
        raise RuntimeError("Whole-song generalization milestone is not formally closed read-only.")
    if closure.get("readyForHeldOutMeasureDiagnosis") is not True:
        raise RuntimeError("Closure review is not ready for held-out measure diagnosis.")
    if closure.get("rhythmStructureClosedMeasures") != EXPECTED_RHYTHM_CLOSED:
        raise RuntimeError("Closed rhythm-structure set changed unexpectedly.")
    if closure.get("chordShapeClosedMeasures") != EXPECTED_CHORD_CLOSED:
        raise RuntimeError("Closed chord-shape set changed unexpectedly.")
    if closure.get("heldOutMeasures") != [TARGET_MEASURE]:
        raise RuntimeError(f"Expected held-out measure [{TARGET_MEASURE}], found {closure.get('heldOutMeasures')}.")
    if closure.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Closure unexpectedly allows threshold relaxation.")
    if closure.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Closure unexpectedly allows automatic application.")
    if closure.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Closure did not preserve protected source hash.")

    raw_rows = diagnostic.get("rows")
    if not isinstance(raw_rows, list):
        raise RuntimeError("Similarity diagnostic rows missing.")
    target_row = next(
        (row for row in raw_rows if isinstance(row, dict) and require_int(row, "measureNumber") == TARGET_MEASURE),
        None,
    )
    if target_row is None:
        raise RuntimeError(f"Similarity row for measure {TARGET_MEASURE} missing.")

    anchor = require_int(target_row, "bestAnchorMeasure")
    if anchor != EXPECTED_ANCHOR:
        raise RuntimeError(f"Expected measure {TARGET_MEASURE} anchor {EXPECTED_ANCHOR}, found {anchor}.")

    target_steps = occupied_steps(events, TARGET_MEASURE)
    anchor_steps = occupied_steps(events, EXPECTED_ANCHOR)
    target_set = set(target_steps)
    anchor_set = set(anchor_steps)
    shared = sorted(target_set & anchor_set)
    target_only = sorted(target_set - anchor_set)
    anchor_only = sorted(anchor_set - target_set)
    raw_union = target_set | anchor_set
    raw_jaccard = len(shared) / len(raw_union) if raw_union else 1.0

    best_shift = best_integer_shift(target_steps, anchor_steps)
    deltas = nearest_step_deltas(target_steps, anchor_steps)
    delta_histogram: dict[str, int] = {}
    for item in deltas:
        key = str(item["delta"])
        delta_histogram[key] = delta_histogram.get(key, 0) + 1

    comparison = target_row.get("bestComparison")
    if not isinstance(comparison, dict):
        raise RuntimeError("Measure 101 bestComparison missing.")

    structural = require_number(target_row, "bestStructuralSimilarityScore")
    musical = require_number(target_row, "bestMusicalSimilarityScore")
    margin = require_number(target_row, "bestVsRunnerUpMargin")
    occupied = require_number(comparison, "occupiedStepJaccard")
    multiplicity = require_number(comparison, "sharedStepMultiplicitySimilarity")
    row_density = require_number(comparison, "rowDensitySimilarity")
    note_density = require_number(comparison, "noteDensitySimilarity")
    pitch_class = require_number(comparison, "sharedStepPitchClassSimilarity")

    likely_global_shift = bool(best_shift["shift"] != 0 and best_shift["jaccard"] >= 0.60)
    likely_sparse_placement_variant = bool(
        not likely_global_shift
        and raw_jaccard < 0.60
        and multiplicity >= 0.75
        and row_density >= 0.90
        and note_density >= 0.85
    )

    if likely_global_shift:
        diagnosis = "possible-consistent-step-shift-relative-to-anchor"
        recommended = "prove-gomyway-rhythm-measure-101-shift-normalized-placement-v1"
    elif likely_sparse_placement_variant:
        diagnosis = "density-and-chord-like-but-rhythm-placement-variant"
        recommended = "review-gomyway-rhythm-measure-101-placement-variant-v1"
    else:
        diagnosis = "insufficient-placement-equivalence-evidence"
        recommended = "retain-gomyway-rhythm-measure-101-held-out-v1"

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and occupied == round(raw_jaccard, 6)
        and anchor == EXPECTED_ANCHOR
        and bool(target_steps)
        and bool(anchor_steps)
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-held-out-rhythm-placement-diagnostic",
        "passed": passed,
        "measureNumber": TARGET_MEASURE,
        "anchorMeasure": EXPECTED_ANCHOR,
        "structuralSimilarityScore": structural,
        "musicalSimilarityScore": musical,
        "bestVsRunnerUpMargin": margin,
        "occupiedStepJaccard": occupied,
        "sharedStepMultiplicitySimilarity": multiplicity,
        "rowDensitySimilarity": row_density,
        "noteDensitySimilarity": note_density,
        "sharedStepPitchClassSimilarity": pitch_class,
        "targetOccupiedSteps": target_steps,
        "anchorOccupiedSteps": anchor_steps,
        "sharedOccupiedSteps": shared,
        "targetOnlyOccupiedSteps": target_only,
        "anchorOnlyOccupiedSteps": anchor_only,
        "bestIntegerShift": best_shift,
        "nearestAnchorStepDeltas": deltas,
        "nearestAnchorStepDeltaHistogram": delta_histogram,
        "likelyConsistentGlobalStepShift": likely_global_shift,
        "likelySparsePlacementVariant": likely_sparse_placement_variant,
        "diagnosis": diagnosis,
        "thresholdRelaxationAllowed": False,
        "classificationClaimed": False,
        "rhythmTransferClaimed": False,
        "chordTransferClaimed": False,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "automaticApplyAllowed": False,
        "readOnlyDiagnostic": True,
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
        "anchorMeasure": EXPECTED_ANCHOR,
        "occupiedStepJaccard": occupied,
        "bestIntegerShift": best_shift,
        "diagnosis": diagnosis,
        "thresholdRelaxationAllowed": False,
        "automaticApplyAllowed": False,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM MEASURE 101 PLACEMENT DIAGNOSTIC V1 COMPLETE")
    print("Passed:", passed)
    print("Measure:", TARGET_MEASURE, "anchor:", EXPECTED_ANCHOR)
    print("Target occupied steps:", target_steps)
    print("Anchor occupied steps:", anchor_steps)
    print("Shared occupied steps:", shared)
    print("Target-only occupied steps:", target_only)
    print("Anchor-only occupied steps:", anchor_only)
    print("Raw occupied-step Jaccard:", round(raw_jaccard, 6))
    print("Best integer shift:", best_shift)
    print("Nearest-step delta histogram:", delta_histogram)
    print("Likely consistent global step shift:", likely_global_shift)
    print("Likely sparse placement variant:", likely_sparse_placement_variant)
    print("Diagnosis:", diagnosis)
    print("Threshold relaxation allowed: False")
    print("Classification claimed: False")
    print("Rhythm transfer claimed: False")
    print("Chord transfer claimed: False")
    print("Timing transfer claimed: False")
    print("Technique transfer claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
