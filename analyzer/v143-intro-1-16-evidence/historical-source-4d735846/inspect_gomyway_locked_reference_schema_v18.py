import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-locked-reference-schema-inspection-v18.json"

CANDIDATES = [
    PUBLIC / "gomyway-professional-rhythm-reference-full-machine.json",
    PUBLIC / "gomyway-professional-rhythm-reference-v1.json",
    PUBLIC / "gomyway-professional-rhythm-reference-v2.json",
    PUBLIC / "gomyway-professional-rhythm-reference.json",
]

INTERESTING_KEYS = {
    "measures",
    "measure",
    "events",
    "notes",
    "noteevents",
    "note_events",
    "tab",
    "strings",
    "frets",
    "fret",
    "string",
    "stringindex",
    "string_index",
    "beats",
    "rhythm",
    "duration",
    "start",
    "starttime",
    "start_time",
    "technique",
    "articulation",
}


def shape(value: Any) -> str:
    if isinstance(value, dict):
        return f"dict[{len(value)}]"
    if isinstance(value, list):
        return f"list[{len(value)}]"
    return type(value).__name__


def scalar_preview(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        text = value
        if isinstance(text, str) and len(text) > 120:
            return text[:117] + "..."
        return text
    return None


def inspect(value: Any, path: str, depth: int, results: list[dict[str, Any]]) -> None:
    if depth > 6:
        return

    if isinstance(value, dict):
        keys = list(value.keys())
        results.append(
            {
                "path": path,
                "shape": shape(value),
                "keys": keys[:40],
            }
        )
        for key, child in value.items():
            lowered = str(key).replace("-", "").replace("_", "").lower()
            child_path = f"{path}.{key}" if path else str(key)
            if lowered in {item.replace("_", "") for item in INTERESTING_KEYS}:
                entry = {
                    "path": child_path,
                    "shape": shape(child),
                    "preview": scalar_preview(child),
                }
                if isinstance(child, dict):
                    entry["keys"] = list(child.keys())[:40]
                elif isinstance(child, list) and child:
                    entry["firstItemShape"] = shape(child[0])
                    if isinstance(child[0], dict):
                        entry["firstItemKeys"] = list(child[0].keys())[:40]
                    else:
                        entry["firstItemPreview"] = scalar_preview(child[0])
                results.append(entry)
            inspect(child, child_path, depth + 1, results)

    elif isinstance(value, list):
        results.append(
            {
                "path": path,
                "shape": shape(value),
                "firstItemShape": shape(value[0]) if value else None,
            }
        )
        for index, child in enumerate(value[:3]):
            inspect(child, f"{path}[{index}]", depth + 1, results)


def main() -> None:
    files = []
    print("Locked reference schema inspection v18 starting", flush=True)

    for path in CANDIDATES:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        entries: list[dict[str, Any]] = []
        inspect(data, "$", 0, entries)
        files.append(
            {
                "path": str(path.relative_to(ROOT)),
                "topLevelShape": shape(data),
                "topLevelKeys": list(data.keys())[:80] if isinstance(data, dict) else [],
                "schemaEntries": entries,
            }
        )
        print(f"Source: {path.name}")
        print(f"  top-level: {shape(data)}")
        if isinstance(data, dict):
            print(f"  keys: {list(data.keys())[:30]}")
        interesting = [
            entry for entry in entries
            if any(token in entry["path"].lower() for token in (
                "measure", "event", "note", "fret", "string", "tab", "rhythm"
            ))
        ]
        for entry in interesting[:20]:
            print(f"  {entry['path']}: {entry['shape']}")

    output = {
        "diagnosticName": "Gomyway locked professional reference schema inspection v18",
        "candidateSourcesInspected": len(files),
        "files": files,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEventsExtracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "select-authoritative-schema-path-and-build-glyph-templates-v19",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked reference schema inspection v18 complete")
    print(f"Candidate sources inspected: {len(files)}")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not files:
        raise RuntimeError("No locked professional rhythm reference source files were found")


if __name__ == "__main__":
    main()
