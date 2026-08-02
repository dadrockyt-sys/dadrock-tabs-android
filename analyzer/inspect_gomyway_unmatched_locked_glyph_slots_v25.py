import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-locked-shared-time-column-model-v24.json"
FALLBACK_INPUT_PATH = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
OUTPUT_PATH = PUBLIC / "gomyway-unmatched-locked-glyph-slots-v25.json"


def get_slots(data: dict[str, Any]) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for row in data.get("rows", []):
        page = int(row.get("pageNumber", 0))
        row_index = int(row.get("rowIndex", 0))
        measure_entries = row.get("measureEventSlots") or row.get("measuresOutput") or []
        for measure_entry in measure_entries:
            measure = int(measure_entry.get("measure", 0))
            event_slots = measure_entry.get("eventSlots") or measure_entry.get("slots") or []
            for slot in event_slots:
                copied = dict(slot)
                copied["pageNumber"] = page
                copied["rowIndex"] = row_index
                copied["measure"] = int(copied.get("measure", measure))
                slots.append(copied)
    return slots


def assigned_component(slot: dict[str, Any]) -> Any:
    for key in (
        "assignedComponentIndex",
        "sharedColumnAssignedComponentIndex",
        "nearestComponentIndex",
        "componentIndex",
    ):
        value = slot.get(key)
        if value is not None:
            return value
    return None


def normalized_string(slot: dict[str, Any]) -> Any:
    return slot.get("normalizedStringHighEToLowE", slot.get("string"))


def main() -> None:
    source_path = INPUT_PATH if INPUT_PATH.exists() else FALLBACK_INPUT_PATH
    if not source_path.exists():
        raise RuntimeError("Missing v24 and v23 glyph assignment outputs")

    source = json.loads(source_path.read_text(encoding="utf-8"))
    slots = get_slots(source)
    if len(slots) != 144:
        raise RuntimeError(f"Expected 144 locked event slots, found {len(slots)}")

    unmatched = [slot for slot in slots if assigned_component(slot) is None]
    matched = [slot for slot in slots if assigned_component(slot) is not None]

    fret_counts = Counter(str(slot.get("fret")) for slot in unmatched)
    string_counts = Counter(str(normalized_string(slot)) for slot in unmatched)
    measure_counts = Counter(int(slot["measure"]) for slot in unmatched)
    technique_counts: Counter[str] = Counter()
    for slot in unmatched:
        technique = slot.get("technique") or {}
        if isinstance(technique, dict) and technique:
            for key, value in technique.items():
                if value not in (None, False, "", 0):
                    technique_counts[str(key)] += 1
        else:
            technique_counts["none"] += 1

    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for slot in unmatched:
        by_measure[int(slot["measure"])].append(
            {
                "pageNumber": slot.get("pageNumber"),
                "rowIndex": slot.get("rowIndex"),
                "measure": int(slot["measure"]),
                "stringHighEToLowE": normalized_string(slot),
                "fret": slot.get("fret"),
                "time": slot.get("time"),
                "expectedX": slot.get("expectedX"),
                "technique": slot.get("technique") or {},
            }
        )

    likely_multi_digit = sum(
        count for fret, count in fret_counts.items()
        if fret.lstrip("-").isdigit() and len(fret.lstrip("-")) >= 2
    )
    likely_open = fret_counts.get("0", 0)
    likely_technique = sum(
        count for name, count in technique_counts.items() if name != "none"
    )

    output = {
        "diagnosticName": "Gomyway unmatched locked glyph slot inspection v25",
        "referenceType": "locked-professional-unmatched-glyph-diagnostic",
        "input": str(source_path.relative_to(ROOT)),
        "eventSlotsObserved": len(slots),
        "matchedEventSlots": len(matched),
        "unmatchedEventSlots": len(unmatched),
        "unmatchedFretCounts": dict(sorted(fret_counts.items())),
        "unmatchedStringCounts": dict(sorted(string_counts.items())),
        "unmatchedMeasureCounts": {
            str(key): value for key, value in sorted(measure_counts.items())
        },
        "unmatchedTechniqueCounts": dict(sorted(technique_counts.items())),
        "likelyMultiDigitFretSlots": likely_multi_digit,
        "likelyOpenStringSlots": likely_open,
        "slotsWithTechniqueMetadata": likely_technique,
        "unmatchedByMeasure": {
            str(key): value for key, value in sorted(by_measure.items())
        },
        "diagnosticComplete": len(slots) == 144,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "select-targeted-component-recovery-strategy-v26",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Unmatched locked glyph slot inspection v25 complete")
    print(f"Input: {source_path.relative_to(ROOT)}")
    print(f"Event slots observed: {len(slots)}")
    print(f"Matched event slots: {len(matched)}")
    print(f"Unmatched event slots: {len(unmatched)}")
    print(f"Unmatched fret counts: {dict(sorted(fret_counts.items()))}")
    print(f"Unmatched string counts: {dict(sorted(string_counts.items()))}")
    print(f"Measures with unmatched slots: {sorted(measure_counts)}")
    print(f"Likely multi-digit fret slots: {likely_multi_digit}")
    print(f"Likely open-string slots: {likely_open}")
    print(f"Slots with technique metadata: {likely_technique}")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
