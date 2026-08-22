import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
DISCOVERY_PATH = PUBLIC / "gomyway-locked-reference-source-discovery-v15.json"
OUTPUT_PATH = PUBLIC / "gomyway-authoritative-locked-reference-v16.json"

LOCKED_MEASURES = set(range(1, 17))
EXCLUDED_NAME_PARTS = (
    "diagnostic",
    "manifest",
    "review-pack",
    "visual-validation",
    "localization",
    "symbol-candidates",
    "glyph-hypotheses",
    "source-discovery",
    "timing-map",
    "identity",
    "candidate-summary",
)
EVENT_KEYS = {
    "events",
    "noteEvents",
    "notes",
    "tabEvents",
    "rhythmEvents",
    "professionalEvents",
}


def walk(node: Any):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def measure_number(item: dict[str, Any]) -> int | None:
    for key in ("measure", "measureNumber", "bar", "barNumber"):
        value = item.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def event_richness(item: dict[str, Any]) -> int:
    score = 0
    for key in ("string", "stringIndex", "fret", "pitch", "start", "startTime", "duration", "beat"):
        if key in item:
            score += 1
    return score


def inspect_file(path: Path) -> dict[str, Any] | None:
    name = path.name.lower()
    if any(part in name for part in EXCLUDED_NAME_PARTS):
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    measures: set[int] = set()
    event_like_objects = 0
    event_key_hits = 0
    richness = 0
    rhythm_markers = 0
    professional_markers = 0

    for item in walk(data):
        measure = measure_number(item)
        if measure in LOCKED_MEASURES:
            measures.add(measure)
        if any(key in item for key in EVENT_KEYS):
            event_key_hits += 1
        item_richness = event_richness(item)
        if item_richness >= 2:
            event_like_objects += 1
            richness += item_richness
        text = json.dumps(item, ensure_ascii=False).lower()
        if "rhythm" in text:
            rhythm_markers += 1
        if "professional" in text or "verified" in text or "locked" in text:
            professional_markers += 1

    if measures != LOCKED_MEASURES:
        return None
    if event_like_objects == 0 and event_key_hits == 0:
        return None

    score = (
        event_like_objects * 20
        + event_key_hits * 10
        + richness
        + min(rhythm_markers, 20) * 3
        + min(professional_markers, 20) * 2
    )
    return {
        "path": str(path.relative_to(ROOT)),
        "score": score,
        "lockedMeasureCoverage": sorted(measures),
        "eventLikeObjects": event_like_objects,
        "eventKeyHits": event_key_hits,
        "eventRichness": richness,
        "rhythmMarkers": rhythm_markers,
        "professionalMarkers": professional_markers,
    }


def main() -> None:
    if not DISCOVERY_PATH.exists():
        raise RuntimeError(f"Missing v15 discovery: {DISCOVERY_PATH.relative_to(ROOT)}")

    candidates = []
    for path in sorted(PUBLIC.glob("*.json")):
        result = inspect_file(path)
        if result:
            candidates.append(result)

    candidates.sort(key=lambda item: (-item["score"], item["path"]))
    selected = candidates[0] if candidates else None
    unambiguous = bool(selected) and (
        len(candidates) == 1 or selected["score"] > candidates[1]["score"]
    )

    output = {
        "diagnosticName": "Gomyway authoritative locked professional reference selection v16",
        "candidateCount": len(candidates),
        "candidates": candidates,
        "selectedSource": selected,
        "selectionUnambiguous": unambiguous,
        "lockedMeasures1To16Modified": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEventsExtracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "build-locked-glyph-template-library-v17"
            if unambiguous
            else "review-v16-ranked-authoritative-reference-candidates"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Authoritative locked reference selection v16 complete")
    print(f"Qualified event-bearing sources: {len(candidates)}")
    for index, candidate in enumerate(candidates[:10], start=1):
        print(
            f"{index}. {candidate['path']} | score={candidate['score']} | "
            f"events={candidate['eventLikeObjects']} | eventKeys={candidate['eventKeyHits']}"
        )
    print(f"Selection unambiguous: {unambiguous}")
    print(f"Selected source: {selected['path'] if selected else None}")
    print("Locked measures 1-16 modified: False")
    print("Glyph templates built: False")
    print("Semantic note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not candidates:
        raise RuntimeError("No complete event-bearing professional 1-16 reference source found")


if __name__ == "__main__":
    main()
