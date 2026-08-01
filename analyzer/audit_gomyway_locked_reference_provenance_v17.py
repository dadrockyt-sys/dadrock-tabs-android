import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V16_PATH = PUBLIC / "gomyway-authoritative-locked-reference-v16.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-reference-provenance-audit-v17.json"

LOCKED_MEASURES = set(range(1, 17))
PREFERRED_NAMES = [
    "gomyway-professional-rhythm-reference-full-machine.json",
    "gomyway-professional-rhythm-reference-v2.json",
]
FORBIDDEN_NAME_FRAGMENTS = (
    "full-song-v8-notation",
    "jimmy",
    "candidate",
    "score",
    "diagnostic",
    "comparison",
    "timing-map",
    "identity",
)


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def measure_number(item: dict[str, Any]) -> int | None:
    for key in ("measure", "measureNumber", "measure_number", "bar", "barNumber"):
        value = item.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def is_note_event(item: dict[str, Any]) -> bool:
    keys = set(item)
    has_position = bool(keys & {"string", "stringIndex", "string_index", "pitch", "midi", "midiPitch"})
    has_value = bool(keys & {"fret", "fretNumber", "fret_number", "pitch", "midi", "midiPitch"})
    return has_position and has_value


def inspect(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    events = []
    measures = set()
    for item in walk(data):
        number = measure_number(item)
        if number in LOCKED_MEASURES:
            measures.add(number)
            if is_note_event(item):
                events.append(item)
    name_lower = path.name.lower()
    forbidden = [fragment for fragment in FORBIDDEN_NAME_FRAGMENTS if fragment in name_lower]
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "lockedMeasureCoverage": sorted(measures),
        "complete1To16Coverage": measures == LOCKED_MEASURES,
        "lockedNoteEventCount": len(events),
        "forbiddenNameFragments": forbidden,
        "eligibleProfessionalReference": (
            measures == LOCKED_MEASURES
            and len(events) > 0
            and not forbidden
            and "professional-rhythm-reference" in name_lower
        ),
    }


def main() -> None:
    if not V16_PATH.exists():
        raise RuntimeError(f"Missing v16 selection: {V16_PATH.relative_to(ROOT)}")

    candidates = []
    for name in PREFERRED_NAMES:
        path = PUBLIC / name
        if path.exists():
            candidates.append(inspect(path))

    if not candidates:
        raise RuntimeError("No committed-style professional rhythm reference candidates exist locally")

    eligible = [item for item in candidates if item["eligibleProfessionalReference"]]
    selected = eligible[0] if eligible else None
    full_machine = next((item for item in candidates if item["path"].endswith(PREFERRED_NAMES[0])), None)
    v2 = next((item for item in candidates if item["path"].endswith(PREFERRED_NAMES[1])), None)
    references_identical = bool(full_machine and v2 and full_machine["sha256"] == v2["sha256"])

    output = {
        "diagnosticName": "Gomyway locked professional reference provenance audit v17",
        "v16TopSelectionAccepted": False,
        "rejectedV16SelectionReason": "generated full-song notation output is not a locked professional rhythm authority",
        "candidates": candidates,
        "eligibleCandidateCount": len(eligible),
        "selectedAuthoritativeSource": selected["path"] if selected else None,
        "fullMachineAndV2ByteIdentical": references_identical,
        "selectionPassed": selected is not None,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEventsExtracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "build-locked-glyph-template-library-v18" if selected else "repair-locked-reference-source",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked professional reference provenance audit v17 complete")
    print("V16 top selection accepted: False")
    for index, item in enumerate(candidates, start=1):
        print(
            f"{index}. {item['path']} | complete={item['complete1To16Coverage']} | "
            f"events={item['lockedNoteEventCount']} | eligible={item['eligibleProfessionalReference']}"
        )
    print(f"Eligible professional sources: {len(eligible)}")
    print(f"Selected authoritative source: {output['selectedAuthoritativeSource']}")
    print(f"Full-machine and v2 byte-identical: {references_identical}")
    print(f"Selection passed: {output['selectionPassed']}")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if selected is None:
        raise RuntimeError("No eligible locked professional rhythm reference source passed provenance audit")


if __name__ == "__main__":
    main()
