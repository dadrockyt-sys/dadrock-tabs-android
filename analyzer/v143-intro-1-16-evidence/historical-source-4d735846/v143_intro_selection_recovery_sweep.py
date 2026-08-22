from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-analysis-cache.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-selection-recovery-sweep.json"
)

INTRO_FIRST_MEASURE = 1
INTRO_LAST_MEASURE = 16
Q_VALUES = tuple(round(0.20 + 0.05 * i, 2) for i in range(17))


def _int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _location(row: dict[str, Any]) -> tuple[int, int]:
    return (
        int(row.get("measure", row.get("measureNumber", 0)) or 0),
        int(row.get("step", row.get("quantizedStep", 0)) or 0),
    )


def _hypothesis_midis(row: dict[str, Any]) -> set[int]:
    values: set[int] = set()
    for hypothesis in row.get("pitchHypotheses", []) or []:
        if isinstance(hypothesis, dict):
            midi = _int(hypothesis.get("midi"))
            if midi is not None:
                values.add(midi)
    dominant = _int(row.get("dominantMidi"))
    if dominant is not None:
        values.add(dominant)
    return values


def _reference_events(reference: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for measure in reference.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if not INTRO_FIRST_MEASURE <= number <= INTRO_LAST_MEASURE:
            continue
        for raw in measure.get("events", []) or []:
            if not isinstance(raw, dict):
                continue
            event = dict(raw)
            event["measureNumber"] = number
            out.append(event)
    return out


def _percent(n: int, d: int) -> float:
    return round(100.0 * n / d, 3) if d else 100.0


def _f1(precision: float, recall: float) -> float:
    if precision + recall <= 0.0:
        return 0.0
    return round(2.0 * precision * recall / (precision + recall), 3)


def evaluate(rows: list[dict[str, Any]], refs: list[dict[str, Any]], q: float) -> dict[str, Any]:
    ranked = sorted(
        rows,
        key=lambda row: (float(row.get("v143Score") or 0.0), -int(row.get("step") or 0)),
        reverse=True,
    )
    k = max(1, min(len(ranked), int(round(float(q) * len(ranked)))))
    selected = ranked[:k]
    by_loc = {_location(row): row for row in selected}

    reference_locations = {
        (int(ref["measureNumber"]), int(ref.get("step") or 0))
        for ref in refs
    }
    selected_locations = set(by_loc)
    location_hits = len(reference_locations & selected_locations)
    location_precision = _percent(location_hits, len(selected_locations))
    location_recall = _percent(location_hits, len(reference_locations))

    reference_pitch_pairs = {
        (
            int(ref["measureNumber"]),
            int(ref.get("step") or 0),
            int(_int(ref.get("midiPitch")) or -999),
        )
        for ref in refs
        if _int(ref.get("midiPitch")) is not None
    }
    candidate_pitch_pairs: set[tuple[int, int, int]] = set()
    for row in selected:
        measure, step = _location(row)
        for midi in _hypothesis_midis(row):
            candidate_pitch_pairs.add((measure, step, midi))

    pitch_hits = len(reference_pitch_pairs & candidate_pitch_pairs)
    pitch_precision = _percent(pitch_hits, len(candidate_pitch_pairs))
    pitch_recall = _percent(pitch_hits, len(reference_pitch_pairs))

    near_pitch_hits = 0
    for measure, step, midi in reference_pitch_pairs:
        found = False
        for delta in (-2, -1, 0, 1, 2):
            row = by_loc.get((measure, step + delta))
            if row is not None and midi in _hypothesis_midis(row):
                found = True
                break
        if found:
            near_pitch_hits += 1

    near_pitch_recall = _percent(near_pitch_hits, len(reference_pitch_pairs))
    location_f1 = _f1(location_precision, location_recall)
    pitch_f1 = _f1(pitch_precision, pitch_recall)

    # This is a development diagnostic, not a production gate. It rewards both
    # attack-location quality and pitch-pair quality without reading reference
    # data inside the analyzer itself.
    objective = round(0.50 * location_f1 + 0.50 * pitch_f1, 3)

    return {
        "q": float(q),
        "selectedSlotCount": len(selected),
        "locationPrecisionPercent": location_precision,
        "locationRecallPercent": location_recall,
        "locationF1Percent": location_f1,
        "pitchHypothesisPrecisionPercent": pitch_precision,
        "pitchHypothesisRecallPercent": pitch_recall,
        "pitchHypothesisF1Percent": pitch_f1,
        "pitchRecallWithinPlusMinus2StepsPercent": near_pitch_recall,
        "objectivePercent": objective,
    }


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(
            "Missing intro analysis cache. Run: modal run analyzer/v143_intro_capture_analysis_cache.py"
        )
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Professional reference missing: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())
    rows = [dict(row) for row in (cache.get("analysis", {}).get("introRows") or [])]
    refs = _reference_events(reference)
    if not rows:
        raise RuntimeError("Intro cache contains no V143 rows")

    results = [evaluate(rows, refs, q) for q in Q_VALUES]
    best = max(
        results,
        key=lambda row: (
            float(row["objectivePercent"]),
            float(row["pitchHypothesisRecallPercent"]),
            float(row["locationRecallPercent"]),
            -float(row["q"]),
        ),
    )

    report = {
        "sweepVersion": 1,
        "scope": "professional-measures-1-16",
        "rowCount": len(rows),
        "referenceEventCount": len(refs),
        "results": results,
        "bestDevelopmentRow": best,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedByOfflineSweep": True,
        "productionModified": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("=== V143 INTRO ATTACK-SELECTION RECOVERY SWEEP ===")
    print("rows:", len(rows))
    print("referenceEvents:", len(refs))
    print()
    print(" q    slots   locP   locR   locF1   pitchP  pitchR  pitchF1  near±2R  objective")
    for row in results:
        print(
            f"{row['q']:>4.2f}  {row['selectedSlotCount']:>5}  "
            f"{row['locationPrecisionPercent']:>5.1f}  {row['locationRecallPercent']:>5.1f}  "
            f"{row['locationF1Percent']:>6.1f}  {row['pitchHypothesisPrecisionPercent']:>6.1f}  "
            f"{row['pitchHypothesisRecallPercent']:>6.1f}  {row['pitchHypothesisF1Percent']:>7.1f}  "
            f"{row['pitchRecallWithinPlusMinus2StepsPercent']:>7.1f}  {row['objectivePercent']:>8.1f}"
        )
    print()
    print("BEST DEVELOPMENT ROW:")
    for key, value in best.items():
        print(f"{key}: {value}")
    print("Professional reference used by analyzer: False")
    print("Production modified: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
