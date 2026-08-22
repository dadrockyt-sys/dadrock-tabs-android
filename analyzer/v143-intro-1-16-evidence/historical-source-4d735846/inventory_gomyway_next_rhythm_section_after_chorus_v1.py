from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
CLOSURE_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-closure-proof-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-next-rhythm-section-after-chorus-inventory-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-next-rhythm-section-after-chorus-inventory-v1-manifest.json"

FIRST_MEASURE = 36
LOOKAHEAD_MEASURES = 16


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def measure_number(row: dict[str, Any]) -> int | None:
    for key in ("measureNumber", "measure"):
        value = row.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
    return None


def quantized_step(row: dict[str, Any]) -> int | None:
    value = row.get("quantizedStep")
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def section_label(row: dict[str, Any]) -> str | None:
    for key in ("sectionLabel", "sectionName", "section"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    closure = load(CLOSURE_PATH)
    rows = source_rows(source)

    if len(rows) != 949:
        raise RuntimeError(f"Protected source must contain exactly 949 events, found {len(rows)}.")
    if closure.get("passed") is not True:
        raise RuntimeError("Chorus 33-35 technique closure proof is not green.")
    if closure.get("chorusMeasures3335ClosedReadOnly") is not True:
        raise RuntimeError("Chorus measures 33-35 are not closed read-only.")
    if closure.get("readyForNextRhythmSectionInventory") is not True:
        raise RuntimeError("Closure proof did not authorize next-section inventory.")

    max_measure = FIRST_MEASURE + LOOKAHEAD_MEASURES - 1
    window_rows = [
        row for row in rows
        if (m := measure_number(row)) is not None and FIRST_MEASURE <= m <= max_measure
    ]

    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in window_rows:
        m = measure_number(row)
        if m is not None:
            by_measure[m].append(row)

    inventory_rows: list[dict[str, Any]] = []
    observed_measures = sorted(by_measure)
    for measure in observed_measures:
        measure_rows = by_measure[measure]
        step_groups: dict[int, int] = defaultdict(int)
        labels: set[str] = set()
        for row in measure_rows:
            step = quantized_step(row)
            if step is not None:
                step_groups[step] += 1
            label = section_label(row)
            if label:
                labels.add(label)

        occupied_steps = sorted(step_groups)
        chord_attacks = sum(1 for count in step_groups.values() if count >= 2)
        max_multiplicity = max(step_groups.values(), default=0)
        inventory_rows.append({
            "measureNumber": measure,
            "eventCount": len(measure_rows),
            "occupiedQuantizedStepCount": len(occupied_steps),
            "occupiedQuantizedSteps": occupied_steps,
            "simultaneousAttackGroups": chord_attacks,
            "maxAttackMultiplicity": max_multiplicity,
            "sectionLabelsObserved": sorted(labels),
        })

    contiguous_from_36: list[int] = []
    expected = FIRST_MEASURE
    for measure in observed_measures:
        if measure != expected:
            break
        contiguous_from_36.append(measure)
        expected += 1

    label_votes: dict[str, int] = defaultdict(int)
    for row in inventory_rows:
        for label in row["sectionLabelsObserved"]:
            label_votes[label] += 1

    dominant_label = None
    if label_votes:
        dominant_label = max(sorted(label_votes), key=lambda label: label_votes[label])

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    inventory_available = bool(window_rows and contiguous_from_36)
    passed = bool(source_unchanged and inventory_available)

    recommended = (
        "diagnose-gomyway-next-rhythm-section-boundary-after-chorus-v1"
        if passed
        else "diagnose-gomyway-next-rhythm-section-inventory-failure-v1"
    )

    output = {
        "schemaVersion": 1,
        "inventoryType": "read-only-next-rhythm-section-after-chorus",
        "passed": passed,
        "firstMeasureAfterClosedChorus": FIRST_MEASURE,
        "lookaheadMeasureCount": LOOKAHEAD_MEASURES,
        "lookaheadLastMeasure": max_measure,
        "windowEventCount": len(window_rows),
        "observedMeasureCount": len(observed_measures),
        "observedMeasures": observed_measures,
        "contiguousMeasuresFrom36": contiguous_from_36,
        "dominantExistingSectionLabel": dominant_label,
        "sectionLabelVotes": dict(sorted(label_votes.items())),
        "rows": inventory_rows,
        "sectionBoundaryClaimed": False,
        "readyForNextRhythmSectionBoundaryDiagnostic": passed,
        "recommendedNextAction": recommended,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
        "protectedSourceEventCount": 949,
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
        "windowEventCount": len(window_rows),
        "observedMeasureCount": len(observed_measures),
        "dominantExistingSectionLabel": dominant_label,
        "sectionBoundaryClaimed": False,
        "readyForNextRhythmSectionBoundaryDiagnostic": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY NEXT RHYTHM SECTION AFTER CHORUS INVENTORY V1 COMPLETE")
    print("Passed:", passed)
    print("First measure after closed chorus:", FIRST_MEASURE)
    print("Lookahead measures:", LOOKAHEAD_MEASURES)
    print("Window events:", len(window_rows))
    print("Observed measures:", observed_measures)
    print("Contiguous measures from 36:", contiguous_from_36)
    print("Dominant existing section label:", dominant_label)
    for row in inventory_rows:
        print(
            f"measure={row['measureNumber']} "
            f"events={row['eventCount']} "
            f"occupiedSteps={row['occupiedQuantizedStepCount']} "
            f"chordGroups={row['simultaneousAttackGroups']} "
            f"maxMultiplicity={row['maxAttackMultiplicity']} "
            f"labels={row['sectionLabelsObserved']}"
        )
    print("Section boundary claimed: False")
    print("Ready for next rhythm section boundary diagnostic:", passed)
    print("Recommended next action:", recommended)
    print("Professional reference used as training label only: True")
    print("Professional notes copied into protected source: False")
    print("Protected source event count: 949")
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
