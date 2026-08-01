import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-professional-value-reference-inventory.json"

MEASURE_KEYS = {
    "measure",
    "measurenumber",
    "measure_number",
    "bar",
    "barnumber",
    "bar_number",
}


def as_measure(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 113:
        return value
    if isinstance(value, str) and value.strip().isdigit():
        number = int(value.strip())
        if 1 <= number <= 113:
            return number
    return None


def explicit_measure(item: dict[str, Any]) -> int | None:
    for key, child in item.items():
        if str(key).lower() in MEASURE_KEYS:
            measure = as_measure(child)
            if measure is not None:
                return measure
    return None


def inspect_payload(payload: Any) -> dict[str, Any]:
    explicit_measures: set[int] = set()
    indexed_measure_arrays: list[dict[str, Any]] = []
    event_rows = 0
    musical_fields = 0

    musical_tokens = (
        "pitch",
        "midi",
        "fret",
        "string",
        "positioninmeasure",
        "duration",
        "technique",
        "attack",
        "onset",
        "timing",
    )

    def walk(item: Any, path: str = "root") -> None:
        nonlocal event_rows, musical_fields

        if isinstance(item, dict):
            measure = explicit_measure(item)
            if measure is not None:
                explicit_measures.add(measure)

            if isinstance(item.get("events"), list):
                event_rows += len(item["events"])

            for key, child in item.items():
                lowered = str(key).lower()
                if any(token in lowered for token in musical_tokens):
                    musical_fields += 1

                if lowered in {"measures", "bars"} and isinstance(child, list):
                    indexed_measure_arrays.append(
                        {
                            "path": f"{path}.{key}",
                            "rowCount": len(child),
                            "authoritativeIndexCoverage": [1, min(len(child), 113)],
                        }
                    )

                walk(child, f"{path}.{key}")

        elif isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, f"{path}[{index}]")

    walk(payload)

    largest_array = max(
        (row["rowCount"] for row in indexed_measure_arrays),
        default=0,
    )
    inferred_coverage = set(explicit_measures)
    if largest_array:
        inferred_coverage.update(range(1, min(largest_array, 113) + 1))

    return {
        "explicitMeasures": sorted(explicit_measures),
        "explicitMeasureCount": len(explicit_measures),
        "indexedMeasureArrays": indexed_measure_arrays,
        "largestIndexedMeasureArray": largest_array,
        "inferredMeasureCoverage": sorted(inferred_coverage),
        "inferredMeasureCoverageCount": len(inferred_coverage),
        "eventRowCount": event_rows,
        "musicalFieldCount": musical_fields,
        "hasFull113MeasureCoverage": len(inferred_coverage) == 113,
        "appearsMusicallyUseful": event_rows > 0 and musical_fields > 0,
    }


def main() -> None:
    paths = sorted(
        path
        for path in PUBLIC.glob("*.json")
        if any(
            token in path.name.lower()
            for token in ("professional", "reference", "rhythm", "timing")
        )
        and path != OUTPUT_PATH
    )

    reports = []
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as error:
            reports.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "readable": False,
                    "error": str(error),
                }
            )
            continue

        reports.append(
            {
                "path": str(path.relative_to(ROOT)),
                "readable": True,
                **inspect_payload(payload),
            }
        )

    full_song_candidates = [
        row["path"]
        for row in reports
        if row.get("readable") is True
        and row.get("hasFull113MeasureCoverage") is True
        and row.get("appearsMusicallyUseful") is True
    ]

    output = {
        "inventoryName": "Jimmy Page professional musical-value reference inventory",
        "filesInspected": len(reports),
        "reports": reports,
        "fullSongProfessionalValueCandidates": full_song_candidates,
        "fullSongProfessionalValueCandidateCount": len(full_song_candidates),
        "readyForProtected113MeasureValueExtraction": len(full_song_candidates) > 0,
        "sourceFilesChanged": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Professional musical-value reference inventory complete")
    print(f"Files inspected: {len(reports)}")
    for row in reports:
        if row.get("readable") is not True:
            print(f"UNREADABLE {row['path']}: {row.get('error')}")
            continue
        print(
            f"{row['path']}: "
            f"coverage={row['inferredMeasureCoverageCount']}/113 "
            f"largest-array={row['largestIndexedMeasureArray']} "
            f"events={row['eventRowCount']} "
            f"musical-fields={row['musicalFieldCount']} "
            f"full-song={row['hasFull113MeasureCoverage']}"
        )

    print(
        "Full-song professional value candidates: "
        f"{len(full_song_candidates)}"
    )
    for path in full_song_candidates:
        print(f"  {path}")
    print(
        "Ready for protected 113-measure value extraction: "
        f"{len(full_song_candidates) > 0}"
    )
    print("No source files changed. Production remains disabled.")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
