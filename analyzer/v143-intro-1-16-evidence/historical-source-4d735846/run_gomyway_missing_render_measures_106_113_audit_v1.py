from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
SOURCE_PATH = PUBLIC_DIR / "gomyway-full-song-v8-notation.json"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-missing-render-measures-106-113-audit-v1.json"
TARGETS = {106, 113}

MEASURE_KEYS = ("measureNumber", "measure", "barNumber", "bar")


def as_measure(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return None
    return None


def extract_measure(item: dict[str, Any]) -> int | None:
    for key in MEASURE_KEYS:
        if key in item:
            result = as_measure(item[key])
            if result is not None:
                return result
    return None


def walk(value: Any, path: str = "$", inherited_measure: int | None = None):
    if isinstance(value, dict):
        current_measure = extract_measure(value) or inherited_measure
        if current_measure in TARGETS:
            yield path, value, current_measure
        for key, child in value.items():
            yield from walk(child, f"{path}.{key}", current_measure)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]", inherited_measure)


def summarize(item: dict[str, Any]) -> dict[str, Any]:
    keep = {
        "measureNumber", "measure", "section", "status", "reviewStatus",
        "eventStatus", "humanApproved", "sourceResolved", "patternId",
        "chord", "chordSymbol", "duration", "durationSteps", "step",
        "start", "startTime", "position", "positionInMeasure", "stringIndex",
        "string", "fret", "technique", "techniques", "tie", "tied",
        "sustain", "fullMeasure", "rest", "isRest", "notes",
    }
    return {key: value for key, value in item.items() if key in keep}


def main() -> None:
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rhythm_events = source.get("rhythmEvents", [])

    coverage = {
        int(event.get("measureNumber") or event.get("measure"))
        for event in rhythm_events
        if isinstance(event, dict)
        and (event.get("measureNumber") is not None or event.get("measure") is not None)
    }

    findings: dict[int, list[dict[str, Any]]] = {106: [], 113: []}
    for path, item, measure in walk(source):
        findings[measure].append({
            "jsonPath": path,
            "keys": sorted(item.keys()),
            "summary": summarize(item),
        })

    report = {
        "schemaVersion": 1,
        "auditType": "missing-render-measures-106-113",
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
        "missingFromRhythmEvents": sorted(TARGETS - coverage),
        "findings": {str(key): value for key, value in findings.items()},
        "measure106HasAlternateEvidence": bool(findings[106]),
        "measure113HasAlternateEvidence": bool(findings[113]),
        "readyForTargetedReconciliation": bool(findings[106] and findings[113]),
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Missing render measures 106/113 audit V1 complete")
    print("Missing from rhythmEvents:", report["missingFromRhythmEvents"])
    print("Measure 106 alternate findings:", len(findings[106]))
    print("Measure 113 alternate findings:", len(findings[113]))
    print("Ready for targeted reconciliation:", report["readyForTargetedReconciliation"])
    print()
    for measure in sorted(TARGETS):
        print(f"MEASURE {measure}")
        for item in findings[measure][:20]:
            print(" path:", item["jsonPath"])
            print(" summary:", item["summary"])
        print()
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
