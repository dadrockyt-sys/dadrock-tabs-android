from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-renderable-rhythm-event-source-audit-v1.json"

EVENT_LIST_KEYS = {
    "events",
    "rhythmEvents",
    "renderEvents",
    "motifStabilizedEvents",
    "fingeringNormalizedEvents",
    "noteEvents",
    "candidateEvents",
    "approvedEvents",
}


def measure_number(item: dict[str, Any]) -> int | None:
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


def has_renderable_pitch(item: dict[str, Any]) -> bool:
    string_value = item.get("stringIndex", item.get("string"))
    fret_value = item.get("fret")
    if string_value is not None and fret_value is not None:
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


def has_timing(item: dict[str, Any]) -> bool:
    return any(
        item.get(key) is not None
        for key in (
            "start",
            "startTime",
            "position",
            "positionInMeasure",
            "quantizedStep",
            "step",
        )
    )


def walk(value: Any, path: str = "$", inherited_measure: int | None = None):
    if isinstance(value, dict):
        current_measure = measure_number(value)
        if current_measure is None:
            current_measure = inherited_measure

        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in EVENT_LIST_KEYS and isinstance(child, list):
                yield child_path, child, current_measure
            yield from walk(child, child_path, current_measure)

    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]", inherited_measure)


def analyze_file(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, OSError):
        return []

    records: list[dict[str, Any]] = []
    for json_path, rows, inherited_measure in walk(payload):
        dict_rows = [row for row in rows if isinstance(row, dict)]
        if not dict_rows:
            continue

        renderable = [row for row in dict_rows if has_renderable_pitch(row)]
        timed = [row for row in renderable if has_timing(row)]
        measures = sorted(
            {
                number
                for row in dict_rows
                for number in [measure_number(row) or inherited_measure]
                if number is not None
            }
        )

        if not renderable:
            continue

        records.append(
            {
                "file": str(path.relative_to(REPO_ROOT)),
                "jsonPath": json_path,
                "eventCount": len(dict_rows),
                "renderableEventCount": len(renderable),
                "timedRenderableEventCount": len(timed),
                "measureCount": len(measures),
                "minimumMeasure": min(measures) if measures else None,
                "maximumMeasure": max(measures) if measures else None,
                "coversFullSong": measures == list(range(1, 114)),
                "sampleKeys": sorted({key for row in renderable[:20] for key in row.keys()}),
            }
        )
    return records


def main() -> None:
    records: list[dict[str, Any]] = []
    files_examined = 0

    for path in sorted(PUBLIC_DIR.rglob("*.json")):
        if path == OUTPUT_PATH:
            continue
        files_examined += 1
        records.extend(analyze_file(path))

    records.sort(
        key=lambda item: (
            item["coversFullSong"],
            item["measureCount"],
            item["timedRenderableEventCount"],
            item["renderableEventCount"],
        ),
        reverse=True,
    )

    selected = records[0] if records else None
    full_song_candidates = [item for item in records if item["coversFullSong"]]
    key_counts = Counter(
        key
        for item in records
        for key in item.get("sampleKeys", [])
    )

    report = {
        "schemaVersion": 1,
        "auditType": "renderable-rhythm-event-source",
        "filesExamined": files_examined,
        "candidateLists": len(records),
        "fullSongCandidates": len(full_song_candidates),
        "selectedCandidate": selected,
        "candidates": records[:100],
        "commonEventKeys": key_counts.most_common(30),
        "readyForRealTabRendererBinding": bool(
            selected
            and selected["renderableEventCount"] > 0
            and selected["timedRenderableEventCount"] > 0
            and selected["measureCount"] > 0
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Renderable rhythm-event source audit V1 complete")
    print("Files examined:", report["filesExamined"])
    print("Candidate event lists:", report["candidateLists"])
    print("Full-song candidates:", report["fullSongCandidates"])
    print("Selected candidate:", selected["file"] if selected else None)
    print("Selected JSON path:", selected["jsonPath"] if selected else None)
    print("Renderable events:", selected["renderableEventCount"] if selected else 0)
    print("Timed renderable events:", selected["timedRenderableEventCount"] if selected else 0)
    print("Measure coverage:", selected["measureCount"] if selected else 0)
    print("Ready for real tab renderer binding:", report["readyForRealTabRendererBinding"])
    print()
    print("Top candidates:")
    for item in records[:10]:
        print(
            " ",
            item["file"],
            item["jsonPath"],
            f"events={item['renderableEventCount']}",
            f"timed={item['timedRenderableEventCount']}",
            f"measures={item['measureCount']}",
            f"fullSong={item['coversFullSong']}",
        )
    print()
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
