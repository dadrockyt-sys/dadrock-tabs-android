import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
DISCOVERY_PATH = PUBLIC / "gomyway-locked-note-event-path-discovery-v19.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-event-consensus-v20.json"

CANONICAL_SOURCE = PUBLIC / "gomyway-professional-rhythm-reference-full-machine.json"
COMPARISON_SOURCES = [
    PUBLIC / "gomyway-professional-measures-1-16-pitch-recall-by-note.json",
    PUBLIC / "gomyway-professional-rhythm-reference-v2.json",
]
LOCKED_START = 1
LOCKED_END = 16

STRING_KEYS = (
    "stringIndex",
    "string_index",
    "string",
    "stringNumber",
    "string_number",
)
FRET_KEYS = ("fret", "fretNumber", "fret_number")
MEASURE_KEYS = ("measure", "measureNumber", "measure_number", "measureIndex")
TIME_KEYS = (
    "beat",
    "beatPosition",
    "beat_position",
    "offset",
    "start",
    "startTime",
    "start_time",
    "time",
)
TECHNIQUE_KEYS = (
    "technique",
    "articulation",
    "bend",
    "slide",
    "hammerOn",
    "pullOff",
    "palmMute",
    "muted",
)


def first_value(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return None


def walk(value: Any, measure_context: int | None = None) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    if isinstance(value, dict):
        own_measure = first_value(value, MEASURE_KEYS)
        if isinstance(own_measure, (int, float)):
            measure_context = int(own_measure)

        string_value = first_value(value, STRING_KEYS)
        fret_value = first_value(value, FRET_KEYS)
        if string_value is not None and fret_value is not None:
            measure_value = measure_context
            if measure_value is not None and LOCKED_START <= measure_value <= LOCKED_END:
                event = {
                    "measure": measure_value,
                    "string": string_value,
                    "fret": fret_value,
                    "time": first_value(value, TIME_KEYS),
                    "technique": {
                        key: value[key] for key in TECHNIQUE_KEYS if key in value
                    },
                }
                output.append(event)

        for child in value.values():
            output.extend(walk(child, measure_context))
    elif isinstance(value, list):
        for child in value:
            output.extend(walk(child, measure_context))
    return output


def normalized_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "measure": int(event["measure"]),
        "string": event["string"],
        "fret": event["fret"],
        "time": event.get("time"),
        "technique": event.get("technique") or {},
    }


def event_sort_key(event: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        json.dumps(event.get(key), sort_keys=True, separators=(",", ":"))
        for key in ("measure", "time", "string", "fret", "technique")
    )


def load_events(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    events = [normalized_event(event) for event in walk(data)]
    return sorted(events, key=event_sort_key)


def digest(events: list[dict[str, Any]]) -> str:
    payload = json.dumps(events, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> None:
    if not DISCOVERY_PATH.exists():
        raise RuntimeError(f"Missing v19 discovery: {DISCOVERY_PATH.relative_to(ROOT)}")

    discovery = json.loads(DISCOVERY_PATH.read_text(encoding="utf-8"))
    if int(discovery.get("complete1To16Sources", 0)) < 3:
        raise RuntimeError("V19 did not find at least three complete locked event sources")

    source_paths = [CANONICAL_SOURCE, *COMPARISON_SOURCES]
    missing = [str(path.relative_to(ROOT)) for path in source_paths if not path.exists()]
    if missing:
        raise RuntimeError(f"Missing locked event sources: {missing}")

    source_reports = []
    event_sets = []
    print("Locked professional event consensus v20 starting", flush=True)

    for path in source_paths:
        events = load_events(path)
        measures = sorted({int(event["measure"]) for event in events})
        report = {
            "source": str(path.relative_to(ROOT)),
            "eventCount": len(events),
            "measureCoverage": measures,
            "complete1To16Coverage": measures == list(range(1, 17)),
            "sha256": digest(events),
            "uniqueFrets": sorted({str(event["fret"]) for event in events}),
            "uniqueStrings": sorted({str(event["string"]) for event in events}),
        }
        source_reports.append(report)
        event_sets.append(events)
        print(
            f"Source: {report['source']} | events={len(events)} | "
            f"coverage={len(measures)}/16 | sha256={report['sha256'][:16]}",
            flush=True,
        )

    canonical_events = event_sets[0]
    exact_consensus = all(events == canonical_events for events in event_sets[1:])
    all_counts_144 = all(len(events) == 144 for events in event_sets)
    all_complete = all(report["complete1To16Coverage"] for report in source_reports)
    consensus_passed = exact_consensus and all_counts_144 and all_complete

    per_measure_counts = {
        str(measure): sum(1 for event in canonical_events if event["measure"] == measure)
        for measure in range(1, 17)
    }

    output = {
        "diagnosticName": "Gomyway locked professional event consensus v20",
        "referenceType": "locked-professional-rhythm-note-event-consensus",
        "canonicalSource": str(CANONICAL_SOURCE.relative_to(ROOT)),
        "comparisonSources": [str(path.relative_to(ROOT)) for path in COMPARISON_SOURCES],
        "sources": source_reports,
        "canonicalEventCount": len(canonical_events),
        "perMeasureEventCounts": per_measure_counts,
        "exactThreeSourceConsensus": exact_consensus,
        "allSourcesHave144Events": all_counts_144,
        "allSourcesCoverMeasures1To16": all_complete,
        "consensusPassed": consensus_passed,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "localize-locked-events-to-professional-pdf-glyphs-v21",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked professional event consensus v20 complete")
    print(f"Canonical event count: {len(canonical_events)}")
    print(f"Exact three-source consensus: {exact_consensus}")
    print(f"All sources have 144 events: {all_counts_144}")
    print(f"All sources cover measures 1-16: {all_complete}")
    print(f"Consensus passed: {consensus_passed}")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not consensus_passed:
        raise RuntimeError("Locked professional event sources did not reach exact consensus")


if __name__ == "__main__":
    main()
