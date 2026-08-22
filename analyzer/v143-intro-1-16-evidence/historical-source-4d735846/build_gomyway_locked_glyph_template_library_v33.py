import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ASSIGNMENT_PATH = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
LOCALIZATION_PATH = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
SIGNATURE_PATH = PUBLIC / "gomyway-locked-template-technique-signatures-v32.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-glyph-template-library-v33.json"
TEMPLATE_DIR = PUBLIC / "gomyway-locked-glyph-template-library-v33"
REQUIRED_FRETS = ["0", "2", "3"]
MAX_TEMPLATES_PER_FRET = 24
MIN_TEMPLATES_PER_FRET = 8


def normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): normalize_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    return value


def technique_signature(slot: dict[str, Any]) -> str:
    technique = slot.get("technique")
    normalized = normalize_value(technique if isinstance(technique, dict) else {"value": technique})
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"))


def fret_key(slot: dict[str, Any]) -> str:
    value = slot.get("fret")
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return str(value)


def all_assignment_slots(data: dict[str, Any]) -> list[dict[str, Any]]:
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


def main() -> None:
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless") from exc

    for path in (ASSIGNMENT_PATH, LOCALIZATION_PATH, SIGNATURE_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    assignment = json.loads(ASSIGNMENT_PATH.read_text(encoding="utf-8"))
    localization = json.loads(LOCALIZATION_PATH.read_text(encoding="utf-8"))
    signature_audit = json.loads(SIGNATURE_PATH.read_text(encoding="utf-8"))

    if int(assignment.get("componentCollisionSlots", -1)) != 0:
        raise RuntimeError("V23 assignment contains component collisions")
    if not bool(signature_audit.get("techniqueMetadataIsGlobalOrDefault", False)):
        raise RuntimeError("V32 did not approve technique-neutral templates")
    if signature_audit.get("requiredFretClasses") != REQUIRED_FRETS:
        raise RuntimeError(
            f"Unexpected required frets: {signature_audit.get('requiredFretClasses')}"
        )

    dominant_signature = json.dumps(
        normalize_value(signature_audit.get("dominantTechniqueSignature")),
        sort_keys=True,
        separators=(",", ":"),
    )

    row_lookup: dict[tuple[int, int], dict[str, Any]] = {}
    component_lookup: dict[tuple[int, int, int], dict[str, Any]] = {}
    for row in localization.get("rows", []):
        page = int(row["pageNumber"])
        row_index = int(row["rowIndex"])
        row_lookup[(page, row_index)] = row
        for component in row.get("compactStringLocalComponents", []):
            index = int(component["componentIndex"])
            component_lookup[(page, row_index, index)] = component

    candidates_by_fret: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for slot in all_assignment_slots(assignment):
        if not bool(slot.get("strictCandidate", False)):
            continue
        component_index = slot.get("assignedComponentIndex")
        if component_index is None:
            continue
        if technique_signature(slot) != dominant_signature:
            continue
        fret = fret_key(slot)
        if fret not in REQUIRED_FRETS:
            continue
        page = int(slot["pageNumber"])
        row_index = int(slot["rowIndex"])
        component = component_lookup.get((page, row_index, int(component_index)))
        row = row_lookup.get((page, row_index))
        if component is None or row is None:
            continue
        candidate = {
            **slot,
            "component": component,
            "sourceCrop": row["sourceCrop"],
        }
        candidates_by_fret[fret].append(candidate)

    for fret in REQUIRED_FRETS:
        candidates_by_fret[fret].sort(
            key=lambda item: (
                float(item.get("distancePixels") or 9999),
                abs(float(item["component"].get("width", 0)) - 10.0),
                abs(float(item["component"].get("height", 0)) - 14.0),
                int(item.get("measure", 0)),
            )
        )

    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    library: dict[str, list[dict[str, Any]]] = {}
    template_counts: Counter[str] = Counter()
    source_measures: dict[str, set[int]] = defaultdict(set)
    source_strings: dict[str, set[int]] = defaultdict(set)

    print("Technique-neutral locked glyph template library v33 starting", flush=True)

    for fret in REQUIRED_FRETS:
        entries: list[dict[str, Any]] = []
        seen_components: set[tuple[int, int, int]] = set()
        for candidate in candidates_by_fret[fret]:
            if len(entries) >= MAX_TEMPLATES_PER_FRET:
                break
            page = int(candidate["pageNumber"])
            row_index = int(candidate["rowIndex"])
            component_index = int(candidate["assignedComponentIndex"])
            key = (page, row_index, component_index)
            if key in seen_components:
                continue
            seen_components.add(key)

            component = candidate["component"]
            crop_path = ROOT / candidate["sourceCrop"]
            gray = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
            if gray is None:
                raise RuntimeError(f"Unable to read crop: {crop_path.relative_to(ROOT)}")

            x = int(component.get("x", component.get("left", 0)))
            y = int(component.get("y", component.get("top", 0)))
            width = int(component.get("width", 0))
            height = int(component.get("height", 0))
            if width <= 0 or height <= 0:
                continue

            pad_x = max(3, round(width * 0.45))
            pad_y = max(3, round(height * 0.35))
            x0 = max(0, x - pad_x)
            y0 = max(0, y - pad_y)
            x1 = min(gray.shape[1], x + width + pad_x)
            y1 = min(gray.shape[0], y + height + pad_y)
            patch = gray[y0:y1, x0:x1]
            if patch.size == 0:
                continue

            normalized = cv2.resize(patch, (32, 32), interpolation=cv2.INTER_AREA)
            template_name = f"fret-{fret}-template-{len(entries) + 1:02d}.png"
            template_path = TEMPLATE_DIR / template_name
            cv2.imwrite(str(template_path), normalized)

            string_number = int(candidate.get("normalizedStringHighEToLowE") or 0)
            measure = int(candidate.get("measure") or 0)
            entry = {
                "templateId": f"fret-{fret}-{len(entries) + 1:02d}",
                "fret": int(fret),
                "pageNumber": page,
                "rowIndex": row_index,
                "measure": measure,
                "stringHighEToLowE": string_number,
                "componentIndex": component_index,
                "distancePixels": candidate.get("distancePixels"),
                "sourceCrop": candidate["sourceCrop"],
                "sourceBoundingBox": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                },
                "templateImage": str(template_path.relative_to(ROOT)),
                "normalizedSize": [32, 32],
                "strictCandidate": True,
                "collisionFree": True,
                "dominantTechniqueSignature": True,
                "humanValidated": False,
            }
            entries.append(entry)
            template_counts[fret] += 1
            source_measures[fret].add(measure)
            source_strings[fret].add(string_number)

        library[fret] = entries
        print(
            f"Fret {fret}: templates={len(entries)}, "
            f"measures={len(source_measures[fret])}, strings={len(source_strings[fret])}",
            flush=True,
        )

    missing_frets = [
        fret for fret in REQUIRED_FRETS
        if template_counts[fret] < MIN_TEMPLATES_PER_FRET
    ]
    images_built = all(
        (ROOT / entry["templateImage"]).exists()
        for entries in library.values()
        for entry in entries
    )
    template_library_built = not missing_frets and images_built

    output = {
        "diagnosticName": "Gomyway technique-neutral locked glyph template library v33",
        "referenceType": "locked-professional-rhythm-tab-glyph-template-library",
        "sourceAssignment": str(ASSIGNMENT_PATH.relative_to(ROOT)),
        "sourceLocalization": str(LOCALIZATION_PATH.relative_to(ROOT)),
        "sourceTechniqueSignatureAudit": str(SIGNATURE_PATH.relative_to(ROOT)),
        "requiredFretClasses": REQUIRED_FRETS,
        "minimumTemplatesPerFret": MIN_TEMPLATES_PER_FRET,
        "maximumTemplatesPerFret": MAX_TEMPLATES_PER_FRET,
        "templateCountsByFret": dict(template_counts),
        "sourceMeasureCountsByFret": {
            fret: len(source_measures[fret]) for fret in REQUIRED_FRETS
        },
        "sourceStringCountsByFret": {
            fret: len(source_strings[fret]) for fret in REQUIRED_FRETS
        },
        "missingTemplateFretClasses": missing_frets,
        "allTemplateImagesBuilt": images_built,
        "templateLibraryBuilt": template_library_built,
        "templatesRequireHumanVisualValidation": True,
        "unresolvedTechniqueConnectedEventsExcluded": 6,
        "templates": library,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "human-review-locked-glyph-template-contact-sheets-v34"
            if template_library_built
            else "expand-template-library-for-missing-fret-classes-v34"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Technique-neutral locked glyph template library v33 complete")
    print(f"Required fret classes: {REQUIRED_FRETS}")
    print(f"Template counts by fret: {dict(template_counts)}")
    print(f"Missing template fret classes: {missing_frets}")
    print(f"All template images built: {images_built}")
    print(f"Template library built: {template_library_built}")
    print("Templates require human visual validation: True")
    print("Unresolved technique-connected events excluded: 6")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Template images: {TEMPLATE_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
