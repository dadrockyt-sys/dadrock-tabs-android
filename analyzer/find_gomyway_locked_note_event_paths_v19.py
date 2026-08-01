import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT = PUBLIC / "gomyway-locked-note-event-path-discovery-v19.json"

EXCLUDED_TOKENS = (
    "candidate", "diagnostic", "manifest", "review", "localization",
    "timing-map", "identity", "score", "comparison", "full-song",
)

MEASURE_KEYS = ("measure", "measureNumber", "measure_number", "bar", "barNumber")
STRING_KEYS = ("string", "stringIndex", "string_index", "stringNumber")
FRET_KEYS = ("fret", "fretNumber", "fret_number")
TIME_KEYS = ("time", "start", "startTime", "onset", "beat", "offset")


def first_int(mapping: dict[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
    return None


def first_present(mapping: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    return next((key for key in keys if key in mapping), None)


def walk(value: Any, path: str, inherited_measure: int | None, hits: list[dict[str, Any]]) -> None:
    if isinstance(value, dict):
        local_measure = first_int(value, MEASURE_KEYS)
        measure = local_measure if local_measure is not None else inherited_measure
        string_key = first_present(value, STRING_KEYS)
        fret_key = first_present(value, FRET_KEYS)
        if string_key and fret_key and measure is not None and 1 <= measure <= 16:
            hits.append({
                "path": path,
                "measure": measure,
                "stringKey": string_key,
                "fretKey": fret_key,
                "timeKey": first_present(value, TIME_KEYS),
                "keys": sorted(value.keys()),
                "sample": {
                    key: value.get(key)
                    for key in (measure and [string_key, fret_key] or [])
                },
            })
        for key, child in value.items():
            walk(child, f"{path}.{key}", measure, hits)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk(child, f"{path}[{index}]", inherited_measure, hits)


def main() -> None:
    sources = []
    for path in sorted(PUBLIC.glob("gomyway*.json")):
        name = path.name.lower()
        if any(token in name for token in EXCLUDED_TOKENS):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        hits: list[dict[str, Any]] = []
        walk(data, "$", None, hits)
        measures = sorted({hit["measure"] for hit in hits})
        if not hits:
            continue
        path_counts: dict[str, int] = {}
        for hit in hits:
            normalized = hit["path"].split("[")[0]
            path_counts[normalized] = path_counts.get(normalized, 0) + 1
        sources.append({
            "source": str(path.relative_to(ROOT)),
            "eventLikeObjects": len(hits),
            "lockedMeasuresCovered": measures,
            "complete1To16Coverage": measures == list(range(1, 17)),
            "paths": sorted(path_counts.items(), key=lambda item: (-item[1], item[0]))[:20],
            "samples": hits[:12],
        })

    sources.sort(
        key=lambda item: (
            not item["complete1To16Coverage"],
            -len(item["lockedMeasuresCovered"]),
            -item["eventLikeObjects"],
            item["source"],
        )
    )
    complete = [item for item in sources if item["complete1To16Coverage"]]
    output = {
        "diagnosticName": "Gomyway schema-aware locked note event discovery v19",
        "sourcesWithStringAndFretObjects": len(sources),
        "complete1To16Sources": len(complete),
        "sources": sources,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEventsExtracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "select-verified-locked-event-path-and-build-template-library-v20",
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Schema-aware locked note event discovery v19 complete")
    print(f"Sources with string+fret objects: {len(sources)}")
    print(f"Complete 1-16 sources: {len(complete)}")
    for index, item in enumerate(sources[:10], start=1):
        print(
            f"{index}. {item['source']} | events={item['eventLikeObjects']} | "
            f"coverage={len(item['lockedMeasuresCovered'])}/16 | "
            f"complete={item['complete1To16Coverage']}"
        )
        for path_name, count in item["paths"][:3]:
            print(f"   {path_name} -> {count}")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
