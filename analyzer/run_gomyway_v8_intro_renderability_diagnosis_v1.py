from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
SOURCE_PATH = PUBLIC_DIR / "gomyway-full-song-v8-render-events-overlay-v1.json"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-v8-intro-renderability-diagnosis-v1.json"

INTRO_MEASURES = range(1, 17)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected object: {path}")
    return value


def number(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def measure_of(event: dict[str, Any]) -> int:
    return number(
        event.get("measureNumber", event.get("measure", event.get("barNumber", event.get("bar")))),
        0,
    )


def step_of(event: dict[str, Any]) -> int:
    return number(
        event.get("quantizedStep", event.get("step", event.get("positionInMeasure"))),
        0,
    )


def duration_of(event: dict[str, Any]) -> int:
    return max(1, number(event.get("durationSteps"), 1))


def notes_of(event: dict[str, Any]) -> list[tuple[int, int]]:
    rows: list[tuple[int, int]] = []
    notes = event.get("notes")
    if isinstance(notes, list):
        for note in notes:
            if not isinstance(note, dict):
                continue
            string = note.get("string", note.get("stringIndex"))
            fret = note.get("fret")
            if string is not None and fret is not None:
                rows.append((number(string), number(fret)))
    if not rows:
        string = event.get("string", event.get("stringIndex"))
        fret = event.get("fret")
        if string is not None and fret is not None:
            rows.append((number(string), number(fret)))
    return sorted(rows)


def signature(event: dict[str, Any]) -> str:
    return json.dumps(
        {
            "measure": measure_of(event),
            "step": step_of(event),
            "duration": duration_of(event),
            "notes": notes_of(event),
            "techniques": sorted(map(str, event.get("techniques") or [])),
        },
        sort_keys=True,
    )


def main() -> None:
    source = load_json(SOURCE_PATH)
    events = source.get("renderEvents")
    if not isinstance(events, list):
        raise ValueError("renderEvents missing")

    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        if isinstance(event, dict):
            by_measure[measure_of(event)].append(event)

    reports = []
    intro_raw = 0
    intro_unique = 0
    intro_steps: set[tuple[int, int]] = set()

    for measure in INTRO_MEASURES:
        rows = by_measure.get(measure, [])
        signatures = Counter(signature(row) for row in rows)
        step_counts = Counter(step_of(row) for row in rows)
        unique_step_counts = Counter()
        unique_rows = []
        seen = set()
        for row in rows:
            sig = signature(row)
            if sig in seen:
                continue
            seen.add(sig)
            unique_rows.append(row)
            unique_step_counts[step_of(row)] += 1
            intro_steps.add((measure, step_of(row)))

        intro_raw += len(rows)
        intro_unique += len(unique_rows)
        reports.append(
            {
                "measure": measure,
                "rawEventCount": len(rows),
                "uniqueEventCount": len(unique_rows),
                "rawDistinctSteps": sorted(step_counts),
                "uniqueDistinctSteps": sorted(unique_step_counts),
                "duplicateCount": len(rows) - len(unique_rows),
                "mostRepeatedSignatures": [
                    {"count": count, "signature": json.loads(sig)}
                    for sig, count in signatures.most_common(5)
                ],
                "uniqueEvents": [
                    {
                        "step": step_of(row),
                        "duration": duration_of(row),
                        "notes": notes_of(row),
                        "techniques": row.get("techniques") or [],
                    }
                    for row in unique_rows
                ],
            }
        )

    measures_with_one_or_fewer_steps = [
        row["measure"] for row in reports if len(row["uniqueDistinctSteps"]) <= 1
    ]
    expected_professional_like = all(
        len(row["uniqueDistinctSteps"]) >= 4 for row in reports[:12]
    )

    result = {
        "schemaVersion": 1,
        "auditType": "v8-intro-renderability-diagnosis",
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
        "introRawEvents": intro_raw,
        "introUniqueEvents": intro_unique,
        "introDistinctMeasureSteps": len(intro_steps),
        "measuresWithOneOrFewerUniqueSteps": measures_with_one_or_fewer_steps,
        "introContainsProfessionalLikeAttackDensity": expected_professional_like,
        "diagnosis": (
            "The PDF renderer can only place attacks present in renderEvents. "
            "If most intro measures contain one unique quantized step, the source is a chord/measure summary rather than a full rhythmic transcription. "
            "A renderer rewrite cannot recover absent attacks; the intro must be rebuilt from the locked 12-slot template or a denser approved event source."
        ),
        "measures": reports,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("V8 intro renderability diagnosis V1 complete")
    print("Intro raw events:", intro_raw)
    print("Intro visually unique events:", intro_unique)
    print("Intro distinct measure/step positions:", len(intro_steps))
    print("Measures with <=1 unique step:", measures_with_one_or_fewer_steps)
    print("Intro contains professional-like attack density:", expected_professional_like)
    print()
    for row in reports:
        print(
            f"measure={row['measure']} raw={row['rawEventCount']} unique={row['uniqueEventCount']} "
            f"steps={row['uniqueDistinctSteps']} duplicates={row['duplicateCount']}"
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
