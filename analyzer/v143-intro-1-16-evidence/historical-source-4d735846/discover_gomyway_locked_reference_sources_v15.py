import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-locked-reference-source-discovery-v15.json"
LOCKED_START = 1
LOCKED_END = 16


def walk(value: Any, path: str = "$") -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            key_lower = str(key).lower()
            if any(token in key_lower for token in ("measure", "event", "note", "fret", "string", "pitch")):
                hits.append({"path": child_path, "valueType": type(child).__name__})
            hits.extend(walk(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(walk(child, f"{path}[{index}]"))
    return hits


def extract_measure_numbers(value: Any) -> set[int]:
    found: set[int] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            key_lower = str(key).lower()
            if "measure" in key_lower:
                if isinstance(child, int):
                    found.add(child)
                elif isinstance(child, list):
                    for item in child:
                        if isinstance(item, int):
                            found.add(item)
            found.update(extract_measure_numbers(child))
    elif isinstance(value, list):
        for child in value:
            found.update(extract_measure_numbers(child))
    return found


def main() -> None:
    candidates: list[dict[str, Any]] = []
    parse_errors: list[str] = []

    print("Locked professional reference source discovery v15 starting", flush=True)

    for path in sorted(PUBLIC.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            parse_errors.append(str(path.relative_to(ROOT)))
            continue

        measures = sorted(extract_measure_numbers(data))
        locked = [measure for measure in measures if LOCKED_START <= measure <= LOCKED_END]
        if not locked:
            continue

        structural_hits = walk(data)
        candidates.append(
            {
                "path": str(path.relative_to(ROOT)),
                "lockedMeasuresObserved": locked,
                "lockedCoverageCount": len(set(locked)),
                "complete1To16Coverage": sorted(set(locked)) == list(range(1, 17)),
                "structuralFieldHits": structural_hits[:200],
                "structuralFieldHitCount": len(structural_hits),
            }
        )
        print(
            f"Candidate: {path.name}, locked coverage={len(set(locked))}/16, "
            f"complete={sorted(set(locked)) == list(range(1, 17))}",
            flush=True,
        )

    complete_sources = [item for item in candidates if item["complete1To16Coverage"]]
    output = {
        "diagnosticName": "Gomyway locked professional reference source discovery v15",
        "lockedMeasureStart": LOCKED_START,
        "lockedMeasureEnd": LOCKED_END,
        "candidateSourceCount": len(candidates),
        "completeLockedSourceCount": len(complete_sources),
        "candidateSources": candidates,
        "parseErrors": parse_errors,
        "candidateAudioUsed": False,
        "lockedMeasuresModified": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEventsExtracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "select-authoritative-locked-reference-source-and-build-glyph-templates"
            if complete_sources
            else "inspect-partial-locked-reference-artifacts"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked professional reference source discovery v15 complete")
    print(f"Candidate sources: {len(candidates)}")
    print(f"Complete 1-16 sources: {len(complete_sources)}")
    print("Locked measures modified: False")
    print("Glyph templates built: False")
    print("Semantic note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
