import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ASSIGNMENT_PATH = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
UNMATCHED_PATH = PUBLIC / "gomyway-unmatched-locked-glyph-slots-v25.json"
OFFSET_PATH = PUBLIC / "gomyway-open-string-x-offset-hypothesis-v30.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-template-coverage-audit-v31.json"


def all_slots(data: dict[str, Any]) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for row in data.get("rows", []):
        page = int(row.get("pageNumber", 0))
        row_index = int(row.get("rowIndex", 0))
        for measure_entry in row.get("measureEventSlots", []):
            measure = int(measure_entry.get("measure", 0))
            for slot in measure_entry.get("eventSlots", []):
                copied = dict(slot)
                copied["pageNumber"] = page
                copied["rowIndex"] = row_index
                copied["measure"] = int(copied.get("measure", measure))
                slots.append(copied)
    return slots


def fret_key(slot: dict[str, Any]) -> str:
    value = slot.get("fret")
    if isinstance(value, bool) or value is None:
        return "unknown"
    try:
        number = int(value)
        return str(number)
    except (TypeError, ValueError):
        return str(value)


def has_technique(slot: dict[str, Any]) -> bool:
    technique = slot.get("technique") or {}
    if isinstance(technique, dict):
        return any(value not in (None, False, "", 0, [], {}) for value in technique.values())
    return bool(technique)


def main() -> None:
    for path in (ASSIGNMENT_PATH, UNMATCHED_PATH, OFFSET_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    assignment = json.loads(ASSIGNMENT_PATH.read_text(encoding="utf-8"))
    unmatched = json.loads(UNMATCHED_PATH.read_text(encoding="utf-8"))
    offset = json.loads(OFFSET_PATH.read_text(encoding="utf-8"))

    slots = all_slots(assignment)
    if len(slots) != 144:
        raise RuntimeError(f"Expected 144 locked event slots, found {len(slots)}")
    if int(unmatched.get("unmatchedEventSlots", -1)) != 6:
        raise RuntimeError("V25 did not isolate exactly six unresolved events")
    if bool(offset.get("globalOffsetHypothesisPassed", True)):
        raise RuntimeError("V30 unexpectedly accepted a global offset")

    total_by_fret: Counter[str] = Counter()
    matched_by_fret: Counter[str] = Counter()
    strict_by_fret: Counter[str] = Counter()
    strict_clean_by_fret: Counter[str] = Counter()
    strict_technique_by_fret: Counter[str] = Counter()
    strict_examples: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for slot in slots:
        fret = fret_key(slot)
        total_by_fret[fret] += 1
        matched = slot.get("assignedComponentIndex") is not None
        strict = bool(slot.get("strictCandidate", False))
        if matched:
            matched_by_fret[fret] += 1
        if strict:
            strict_by_fret[fret] += 1
            if has_technique(slot):
                strict_technique_by_fret[fret] += 1
            else:
                strict_clean_by_fret[fret] += 1
            if len(strict_examples[fret]) < 12:
                strict_examples[fret].append(
                    {
                        "pageNumber": slot.get("pageNumber"),
                        "rowIndex": slot.get("rowIndex"),
                        "measure": slot.get("measure"),
                        "stringHighEToLowE": slot.get("normalizedStringHighEToLowE"),
                        "fret": slot.get("fret"),
                        "componentIndex": slot.get("assignedComponentIndex"),
                        "distancePixels": slot.get("distancePixels"),
                        "width": slot.get("assignedWidth"),
                        "height": slot.get("assignedHeight"),
                        "area": slot.get("assignedArea"),
                        "techniqueExcluded": has_technique(slot),
                    }
                )

    required_frets = sorted(total_by_fret, key=lambda item: (item == "unknown", int(item) if item.lstrip("-").isdigit() else 999, item))
    clean_minimum = 3
    coverage_by_fret = {
        fret: {
            "totalLockedEvents": total_by_fret[fret],
            "matchedEvents": matched_by_fret[fret],
            "strictCandidates": strict_by_fret[fret],
            "strictCleanCandidates": strict_clean_by_fret[fret],
            "strictTechniqueCandidates": strict_technique_by_fret[fret],
            "minimumCleanTemplatesRequired": clean_minimum,
            "cleanTemplateCoveragePassed": strict_clean_by_fret[fret] >= clean_minimum,
            "examples": strict_examples[fret],
        }
        for fret in required_frets
    }

    missing_template_frets = [
        fret for fret in required_frets
        if strict_clean_by_fret[fret] < clean_minimum
    ]
    unresolved_measures = sorted(
        int(value) for value in unmatched.get("unmatchedByMeasure", {}).keys()
    )
    unresolved_only_technique_open_strings = (
        unmatched.get("unmatchedFretCounts") == {"0": 6}
        and unmatched.get("unmatchedStringCounts") == {"6": 6}
        and int(unmatched.get("slotsWithTechniqueMetadata", 0)) == 6
    )
    template_coverage_passed = (
        not missing_template_frets
        and unresolved_only_technique_open_strings
        and int(assignment.get("componentCollisionSlots", -1)) == 0
    )

    output = {
        "diagnosticName": "Gomyway locked glyph template coverage audit v31",
        "referenceType": "locked-professional-template-eligibility-audit",
        "sourceAssignment": str(ASSIGNMENT_PATH.relative_to(ROOT)),
        "sourceUnmatchedInspection": str(UNMATCHED_PATH.relative_to(ROOT)),
        "sourceOffsetHypothesis": str(OFFSET_PATH.relative_to(ROOT)),
        "lockedEventSlotsObserved": len(slots),
        "requiredFretClasses": required_frets,
        "coverageByFret": coverage_by_fret,
        "minimumCleanTemplatesPerFret": clean_minimum,
        "missingTemplateFretClasses": missing_template_frets,
        "unresolvedEventSlotsExcludedFromTemplates": int(unmatched.get("unmatchedEventSlots", 0)),
        "unresolvedMeasuresExcludedFromTemplates": unresolved_measures,
        "unresolvedOnlyTechniqueOpenStrings": unresolved_only_technique_open_strings,
        "componentCollisionSlots": int(assignment.get("componentCollisionSlots", -1)),
        "templateCoveragePassed": template_coverage_passed,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "build-clean-locked-glyph-template-library-v32"
            if template_coverage_passed
            else "expand-clean-template-evidence-for-missing-fret-classes-v32"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked glyph template coverage audit v31 complete")
    print(f"Locked event slots observed: {len(slots)}")
    print(f"Required fret classes: {required_frets}")
    for fret in required_frets:
        item = coverage_by_fret[fret]
        print(
            f"Fret {fret}: total={item['totalLockedEvents']}, "
            f"matched={item['matchedEvents']}, strict={item['strictCandidates']}, "
            f"strictClean={item['strictCleanCandidates']}, "
            f"coveragePassed={item['cleanTemplateCoveragePassed']}"
        )
    print(f"Missing template fret classes: {missing_template_frets}")
    print(f"Unresolved event slots excluded from templates: {output['unresolvedEventSlotsExcludedFromTemplates']}")
    print(f"Unresolved measures excluded from templates: {unresolved_measures}")
    print(f"Unresolved only technique open strings: {unresolved_only_technique_open_strings}")
    print(f"Component collision slots: {output['componentCollisionSlots']}")
    print(f"Template coverage passed: {template_coverage_passed}")
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
