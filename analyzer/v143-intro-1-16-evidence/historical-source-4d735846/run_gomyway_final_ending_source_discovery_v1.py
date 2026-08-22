from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-final-ending-source-discovery-v1.json"

ENDING_START = 111
ENDING_END = 113
MAX_FILE_BYTES = 40_000_000

MEASURE_KEYS = (
    "measureNumber",
    "measure",
    "barNumber",
    "bar",
)
STEP_KEYS = (
    "candidateStep",
    "quantizedStep",
    "step",
    "sixteenthStep",
)
EVENT_HINT_KEYS = {
    "start",
    "end",
    "duration",
    "position",
    "positionInMeasure",
    "midiPitch",
    "midi",
    "pitch",
    "stringIndex",
    "string",
    "fret",
    "notes",
    "classification",
    "confidence",
}


def integer_value(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            number = float(value)
        except ValueError:
            return None
        if number.is_integer():
            return int(number)
    return None


def measure_from_record(record: dict[str, Any]) -> int | None:
    for key in MEASURE_KEYS:
        if key in record:
            value = integer_value(record.get(key))
            if value is not None:
                return value
    return None


def compact_record(record: dict[str, Any], path: str) -> dict[str, Any]:
    keep = set(MEASURE_KEYS) | set(STEP_KEYS) | EVENT_HINT_KEYS | {
        "section",
        "label",
        "eventIndex",
        "sourceEventIndex",
        "readOnly",
        "humanValidated",
        "sourceDerived",
    }
    compact = {
        key: value
        for key, value in record.items()
        if key in keep and isinstance(value, (str, int, float, bool, type(None), list))
    }
    compact["jsonPath"] = path
    return compact


def walk(node: Any, path: str = "$") -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(node, dict):
        measure = measure_from_record(node)
        if measure is not None and ENDING_START <= measure <= ENDING_END:
            yield path, node
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")


def main() -> None:
    file_reports: list[dict[str, Any]] = []
    total_records = 0
    measures_seen: Counter[int] = Counter()
    parse_errors: list[dict[str, str]] = []

    for path in sorted(PUBLIC_DIR.glob("gomyway*.json")):
        if path == OUTPUT_PATH or path.stat().st_size > MAX_FILE_BYTES:
            continue

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # diagnostic-only inventory
            parse_errors.append({
                "file": str(path.relative_to(REPO_ROOT)),
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue

        matches: list[dict[str, Any]] = []
        path_counts: Counter[str] = Counter()
        measure_counts: Counter[int] = Counter()

        for json_path, record in walk(payload):
            measure = measure_from_record(record)
            if measure is None:
                continue
            matches.append(compact_record(record, json_path))
            measure_counts[measure] += 1
            measures_seen[measure] += 1
            path_root = json_path.split("[")[0]
            path_counts[path_root] += 1

        if matches:
            total_records += len(matches)
            file_reports.append({
                "file": str(path.relative_to(REPO_ROOT)),
                "recordCount": len(matches),
                "measureCounts": {
                    str(key): value for key, value in sorted(measure_counts.items())
                },
                "topJsonPaths": [
                    {"path": key, "count": value}
                    for key, value in path_counts.most_common(8)
                ],
                "sampleRecords": matches[:20],
            })

    report = {
        "schemaVersion": 1,
        "auditType": "final-ending-source-discovery",
        "measureRange": [ENDING_START, ENDING_END],
        "filesWithEndingRecords": len(file_reports),
        "endingRecordCount": total_records,
        "measureRecordCounts": {
            str(key): value for key, value in sorted(measures_seen.items())
        },
        "fileReports": file_reports,
        "parseErrors": parse_errors,
        "interpretation": (
            "The chorus ranking contains no measures 111-113, so zero ranking rows do not "
            "prove a silent ending. This read-only discovery pass inventories every gomyway JSON "
            "source containing explicit records for measures 111-113 before selecting the correct "
            "rhythm-event source for a final-ending candidate audit."
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Final-ending source discovery V1 complete")
    print("Measure range:", report["measureRange"])
    print("Files with ending records:", report["filesWithEndingRecords"])
    print("Ending records:", report["endingRecordCount"])
    print("Measure record counts:", report["measureRecordCounts"])
    print()

    for item in file_reports:
        print(
            item["file"],
            "records=", item["recordCount"],
            "measures=", item["measureCounts"],
        )
        for root in item["topJsonPaths"][:3]:
            print("  ", root["path"], "count=", root["count"])

    print()
    print("Automatic promotion allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
