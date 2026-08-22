import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

EVIDENCE_PATH = PUBLIC / "gomyway-jimmy-paige-protected-section-evidence-comparison.json"
PREFLIGHT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-section-comparison-preflight.json"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-section-value-extraction.json"

REFERENCE_CANDIDATES = [
    PUBLIC / "gomyway-professional-rhythm-reference-v2.json",
    PUBLIC / "gomyway-professional-rhythm-reference.json",
]

SECTION_PLAN = [
    ("Intro", 1, 16),
    ("Verse 1", 17, 32),
    ("Chorus 1", 33, 38),
    ("Riff 1", 39, 46),
    ("Verse 2", 47, 62),
    ("Chorus 2", 63, 69),
    ("Bridge", 70, 77),
    ("Solo Backing", 78, 94),
    ("Return Riff and Out-Chorus", 95, 113),
]

SIGNAL_KEYS = {
    "pitch": ("pitch", "midi", "fret", "string", "voicing"),
    "timing": ("time", "phase", "beat", "tempo", "offset", "alignment"),
    "attack": ("attack", "onset", "strum"),
    "duration": ("duration", "sustain", "release", "tie"),
    "technique": ("bend", "vibrato", "mute", "slide", "pick", "technique"),
}

MEASURE_KEYS = {
    "measure",
    "measurenumber",
    "measure_number",
    "bar",
    "barnumber",
    "bar_number",
}
START_KEYS = {"startmeasure", "start_measure", "measurestart", "measure_start"}
END_KEYS = {"endmeasure", "end_measure", "measureend", "measure_end"}
RANGE_KEYS = {"measurerange", "measure_range", "barrange", "bar_range"}
SEQUENTIAL_LIST_KEYS = {"measures", "bars", "measuredata", "measure_data"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def as_measure(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 113:
        return value
    if isinstance(value, str) and value.strip().isdigit():
        number = int(value.strip())
        if 1 <= number <= 113:
            return number
    return None


def scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def explicit_measure(item: dict[str, Any]) -> int | None:
    for key, child in item.items():
        if str(key).lower() in MEASURE_KEYS:
            candidate = as_measure(child)
            if candidate is not None:
                return candidate
    return None


def measure_range(item: dict[str, Any]) -> tuple[int, int] | None:
    start = None
    end = None

    for key, child in item.items():
        lowered = str(key).lower()
        if lowered in START_KEYS:
            start = as_measure(child)
        elif lowered in END_KEYS:
            end = as_measure(child)
        elif lowered in RANGE_KEYS:
            if isinstance(child, (list, tuple)) and len(child) >= 2:
                start = as_measure(child[0])
                end = as_measure(child[1])
            elif isinstance(child, str):
                normalized = child.replace("–", "-").replace("—", "-")
                parts = [part.strip() for part in normalized.split("-")]
                if len(parts) == 2:
                    start = as_measure(parts[0])
                    end = as_measure(parts[1])

    if start is not None and end is not None and start <= end:
        return start, end
    return None


def collect_measure_values(value: Any) -> dict[int, dict[str, list[dict[str, Any]]]]:
    collected = {
        measure: {signal: [] for signal in SIGNAL_KEYS}
        for measure in range(1, 114)
    }

    def record(item: dict[str, Any], measure: int, path: str) -> None:
        for key, child in item.items():
            lowered = str(key).lower()
            for signal, tokens in SIGNAL_KEYS.items():
                if any(token in lowered for token in tokens):
                    if scalar(child):
                        collected[measure][signal].append(
                            {"path": f"{path}.{key}", "value": child}
                        )
                    elif isinstance(child, list):
                        for index, list_value in enumerate(child):
                            if scalar(list_value):
                                collected[measure][signal].append(
                                    {
                                        "path": f"{path}.{key}[{index}]",
                                        "value": list_value,
                                    }
                                )

    def walk(
        item: Any,
        inherited_measure: int | None = None,
        inherited_range: tuple[int, int] | None = None,
        path: str = "root",
    ) -> None:
        if isinstance(item, dict):
            current_measure = explicit_measure(item) or inherited_measure
            current_range = measure_range(item) or inherited_range

            if current_measure is not None:
                record(item, current_measure, path)

            for key, child in item.items():
                lowered = str(key).lower()

                # Support maps such as {"17": {...}, "18": {...}}.
                numeric_key_measure = as_measure(key)
                if numeric_key_measure is not None and isinstance(child, (dict, list)):
                    walk(
                        child,
                        numeric_key_measure,
                        (numeric_key_measure, numeric_key_measure),
                        f"{path}.{key}",
                    )
                    continue

                # Support ranged sections whose measure rows omit measureNumber.
                if (
                    lowered in SEQUENTIAL_LIST_KEYS
                    and isinstance(child, list)
                    and current_range is not None
                ):
                    start, end = current_range
                    expected_count = end - start + 1
                    for index, list_value in enumerate(child):
                        assigned = start + index if index < expected_count else None
                        walk(
                            list_value,
                            assigned,
                            current_range,
                            f"{path}.{key}[{index}]",
                        )
                    continue

                walk(child, current_measure, current_range, f"{path}.{key}")

        elif isinstance(item, list):
            for index, child in enumerate(item):
                assigned = inherited_measure
                if inherited_range is not None:
                    start, end = inherited_range
                    candidate = start + index
                    if candidate <= end:
                        assigned = candidate
                walk(child, assigned, inherited_range, f"{path}[{index}]")

    walk(value)
    return collected


def merge_measure_values(
    destination: dict[int, dict[str, list[dict[str, Any]]]],
    source: dict[int, dict[str, list[dict[str, Any]]]],
    source_path: str,
) -> None:
    for measure, signal_map in source.items():
        for signal, rows in signal_map.items():
            for row in rows:
                destination[measure][signal].append({"source": source_path, **row})


def section_summary(
    measure_values: dict[int, dict[str, list[dict[str, Any]]]],
    name: str,
    start: int,
    end: int,
) -> dict[str, Any]:
    signal_counts = {
        signal: sum(len(measure_values[m][signal]) for m in range(start, end + 1))
        for signal in SIGNAL_KEYS
    }
    measures_with_any_values = [
        measure
        for measure in range(start, end + 1)
        if any(measure_values[measure][signal] for signal in SIGNAL_KEYS)
    ]
    signals_present = {signal: count > 0 for signal, count in signal_counts.items()}
    ready = all(signals_present.values()) and len(measures_with_any_values) > 0

    return {
        "name": name,
        "startMeasure": start,
        "endMeasure": end,
        "measureCount": end - start + 1,
        "measuresWithExtractedValues": measures_with_any_values,
        "measuresWithExtractedValueCount": len(measures_with_any_values),
        "signalValueCounts": signal_counts,
        "signalsPresent": signals_present,
        "readyForProtectedValueAlignment": ready,
    }


def main() -> None:
    if not EVIDENCE_PATH.exists():
        raise FileNotFoundError(
            f"Missing evidence comparison: {EVIDENCE_PATH.relative_to(ROOT)}"
        )
    if not PREFLIGHT_PATH.exists():
        raise FileNotFoundError(
            f"Missing comparison preflight: {PREFLIGHT_PATH.relative_to(ROOT)}"
        )

    evidence = load_json(EVIDENCE_PATH)
    preflight = load_json(PREFLIGHT_PATH)

    if evidence.get("protectedSectionEvidenceComparisonPassed") is not True:
        raise RuntimeError("Protected section evidence comparison has not passed")
    if evidence.get("readyForProtectedSectionValueExtraction") is not True:
        raise RuntimeError("Protected section value extraction gate is not open")
    if preflight.get("protectedSectionComparisonPreflightPassed") is not True:
        raise RuntimeError("Protected section comparison preflight has not passed")

    reference_path = next((path for path in REFERENCE_CANDIDATES if path.exists()), None)
    if reference_path is None:
        raise FileNotFoundError("No professional rhythm reference JSON found")

    reference_payload = load_json(reference_path)
    reference_values = collect_measure_values(reference_payload)

    candidate_paths = [
        PUBLIC / row["path"].split("public/", 1)[-1]
        for row in preflight.get("candidateReports", [])
        if row.get("readable") is True and row.get("path")
    ]

    candidate_values = {
        measure: {signal: [] for signal in SIGNAL_KEYS}
        for measure in range(1, 114)
    }
    readable_candidate_count = 0

    for path in candidate_paths:
        if not path.exists() or path in {
            EVIDENCE_PATH,
            PREFLIGHT_PATH,
            OUTPUT_PATH,
            reference_path,
        }:
            continue
        try:
            payload = load_json(path)
        except Exception:
            continue
        readable_candidate_count += 1
        merge_measure_values(
            candidate_values,
            collect_measure_values(payload),
            str(path.relative_to(ROOT)),
        )

    reference_sections = [
        section_summary(reference_values, name, start, end)
        for name, start, end in SECTION_PLAN
    ]
    candidate_sections = [
        section_summary(candidate_values, name, start, end)
        for name, start, end in SECTION_PLAN
    ]

    section_rows = []
    for reference_section, candidate_section in zip(reference_sections, candidate_sections):
        section_ready = (
            reference_section["readyForProtectedValueAlignment"]
            and candidate_section["readyForProtectedValueAlignment"]
        )
        section_rows.append(
            {
                "name": reference_section["name"],
                "startMeasure": reference_section["startMeasure"],
                "endMeasure": reference_section["endMeasure"],
                "professionalReference": reference_section,
                "candidate": candidate_section,
                "readyForProtectedValueAlignment": section_ready,
            }
        )

    sections_ready = sum(
        1 for section in section_rows if section["readyForProtectedValueAlignment"]
    )
    extraction_passed = sections_ready == len(SECTION_PLAN)

    output = {
        "extractionName": "Jimmy Page protected section musical value extraction",
        "extractionVersion": 2,
        "professionalReference": str(reference_path.relative_to(ROOT)),
        "professionalReferenceSha256": sha256_file(reference_path),
        "referenceTraversal": {
            "explicitMeasureFields": True,
            "numericMeasureMapKeys": True,
            "measureRanges": True,
            "sequentialRangedLists": True,
        },
        "candidateArtifactsRead": readable_candidate_count,
        "sections": section_rows,
        "sectionsReadyForProtectedValueAlignment": sections_ready,
        "sectionCount": len(section_rows),
        "protectedSectionValueExtractionPassed": extraction_passed,
        "musicalValueAgreementConfirmed": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForProtectedSectionValueAlignment": extraction_passed,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Protected section musical value extraction complete")
    print("Reference traversal: explicit fields + numeric keys + ranges + sequential lists")
    print(f"Candidate artifacts read: {readable_candidate_count}")
    for section in section_rows:
        reference_counts = section["professionalReference"]["signalValueCounts"]
        candidate_counts = section["candidate"]["signalValueCounts"]
        print(
            f"{section['name']}: measures {section['startMeasure']}-{section['endMeasure']} "
            f"reference-values={sum(reference_counts.values())} "
            f"candidate-values={sum(candidate_counts.values())} "
            f"ready={section['readyForProtectedValueAlignment']}"
        )
    print(f"Sections ready for protected value alignment: {sections_ready}/9")
    print(f"Protected section value extraction passed: {extraction_passed}")
    print("Musical value agreement confirmed: False")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Ready for protected section value alignment: {extraction_passed}")
    print("Ready for production: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not extraction_passed:
        raise RuntimeError("Protected section musical value extraction did not pass")


if __name__ == "__main__":
    main()
