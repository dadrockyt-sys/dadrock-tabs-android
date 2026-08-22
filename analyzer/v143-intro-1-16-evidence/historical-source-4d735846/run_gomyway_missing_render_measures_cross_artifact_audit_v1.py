from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-missing-render-measures-cross-artifact-audit-v1.json"
TARGET_MEASURES = {106, 113}


def get_measure(item: dict[str, Any]) -> int | None:
    for key in ("measureNumber", "measure", "barNumber", "bar"):
        value = item.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                pass
    return None


def looks_renderable(item: dict[str, Any]) -> bool:
    if item.get("fret") is not None and (
        item.get("stringIndex") is not None or item.get("string") is not None
    ):
        return True
    notes = item.get("notes")
    if isinstance(notes, list):
        return any(
            isinstance(note, dict)
            and note.get("fret") is not None
            and (note.get("stringIndex") is not None or note.get("string") is not None)
            for note in notes
        )
    return False


def looks_musical(item: dict[str, Any]) -> bool:
    keys = {
        "fret", "stringIndex", "string", "notes", "pitch", "midi", "midiPitch",
        "duration", "durationSteps", "step", "quantizedStep", "start", "startTime",
        "position", "positionInMeasure", "techniques", "tie", "sustain", "rest",
        "chord", "chordSymbol", "label", "patternId", "eventStatus", "reviewStatus",
    }
    return any(key in item for key in keys)


def compact(item: dict[str, Any]) -> dict[str, Any]:
    preferred = (
        "measureNumber", "measure", "step", "quantizedStep", "start", "startTime",
        "position", "positionInMeasure", "duration", "durationSteps", "stringIndex",
        "string", "fret", "pitch", "midi", "midiPitch", "notes", "techniques",
        "tie", "sustain", "rest", "chord", "chordSymbol", "label", "patternId",
        "classification", "eventStatus", "reviewStatus", "humanApproved", "sourceResolved",
        "confidence",
    )
    result = {key: item[key] for key in preferred if key in item}
    if not result:
        result = {key: value for key, value in list(item.items())[:20]}
    return result


def walk(value: Any, json_path: str = "$"):
    if isinstance(value, dict):
        measure = get_measure(value)
        if measure in TARGET_MEASURES and looks_musical(value):
            yield measure, json_path, value
        for key, child in value.items():
            yield from walk(child, f"{json_path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{json_path}[{index}]")


def main() -> None:
    findings: dict[int, list[dict[str, Any]]] = {106: [], 113: []}
    files_examined = 0

    for path in sorted(PUBLIC_DIR.rglob("*.json")):
        if path == OUTPUT_PATH:
            continue
        files_examined += 1
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue

        for measure, json_path, item in walk(payload):
            findings[measure].append(
                {
                    "file": str(path.relative_to(REPO_ROOT)),
                    "jsonPath": json_path,
                    "renderable": looks_renderable(item),
                    "data": compact(item),
                }
            )

    for measure in TARGET_MEASURES:
        findings[measure].sort(
            key=lambda row: (row["renderable"], row["file"], row["jsonPath"]),
            reverse=True,
        )

    renderable_counts = {
        str(measure): sum(1 for row in findings[measure] if row["renderable"])
        for measure in sorted(TARGET_MEASURES)
    }

    report = {
        "schemaVersion": 1,
        "auditType": "missing-render-measures-cross-artifact",
        "targetMeasures": sorted(TARGET_MEASURES),
        "filesExamined": files_examined,
        "findingCounts": {
            str(measure): len(findings[measure]) for measure in sorted(TARGET_MEASURES)
        },
        "renderableFindingCounts": renderable_counts,
        "findings": {str(measure): findings[measure] for measure in sorted(TARGET_MEASURES)},
        "readyForTargetedReconciliation": all(
            renderable_counts[str(measure)] > 0 for measure in TARGET_MEASURES
        ),
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Missing render measures cross-artifact audit V1 complete")
    print("Files examined:", files_examined)
    for measure in sorted(TARGET_MEASURES):
        print()
        print(f"MEASURE {measure}")
        print("Findings:", len(findings[measure]))
        print("Renderable findings:", renderable_counts[str(measure)])
        for row in findings[measure][:12]:
            print(
                " ",
                row["file"],
                row["jsonPath"],
                f"renderable={row['renderable']}",
                row["data"],
            )

    print()
    print("Ready for targeted reconciliation:", report["readyForTargetedReconciliation"])
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
