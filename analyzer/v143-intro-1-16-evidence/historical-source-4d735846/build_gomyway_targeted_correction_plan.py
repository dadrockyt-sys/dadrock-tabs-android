from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
BEST_PATH = ROOT / "public" / "training" / "gomyway-rhythm-17-113-v3" / "best.json"
OUTPUT_JSON = ROOT / "public" / "gomyway-targeted-rhythm-correction-plan.json"
OUTPUT_TEXT = ROOT / "public" / "gomyway-targeted-rhythm-correction-plan.txt"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def note_signature(event: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    notes = event.get("notes", [])
    return tuple(sorted((int(note["string"]), int(note["fret"])) for note in notes))


def technique_signature(event: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(str(value) for value in event.get("techniques", [])))


def event_map(events: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    mapped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        mapped[int(event["quantizedStep"])].append(event)
    return mapped


def main() -> None:
    reference = load(REFERENCE_PATH)
    best = load(BEST_PATH)

    reference_measures = {
        int(measure["measureNumber"]): measure
        for measure in reference.get("measures", [])
    }
    candidates_by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in best.get("candidateEvents", []):
        candidates_by_measure[int(event["measureNumber"])].append(event)

    measure_reports: list[dict[str, Any]] = []
    totals = {
        "referenceEvents": 0,
        "candidateEvents": 0,
        "matchedSteps": 0,
        "unresolvedReferenceEvents": 0,
        "extraCandidateEvents": 0,
        "exactNoteFretMatches": 0,
        "exactDurationMatches": 0,
        "exactTechniqueMatches": 0,
    }

    for measure_number in range(17, 114):
        measure = reference_measures[measure_number]
        reference_events = list(measure.get("events", []))
        candidate_events = list(candidates_by_measure.get(measure_number, []))
        reference_steps = event_map(reference_events)
        candidate_steps = event_map(candidate_events)

        unresolved: list[dict[str, Any]] = []
        extras: list[dict[str, Any]] = []
        mismatches: list[dict[str, Any]] = []
        matched_steps = 0
        exact_note_fret = 0
        exact_duration = 0
        exact_technique = 0

        all_steps = sorted(set(reference_steps) | set(candidate_steps))
        for step in all_steps:
            refs = reference_steps.get(step, [])
            cands = candidate_steps.get(step, [])
            if not refs:
                extras.extend(cands)
                continue
            if not cands:
                unresolved.extend(refs)
                continue

            matched_steps += 1
            reference_event = refs[0]
            candidate_event = cands[0]
            note_match = note_signature(reference_event) == note_signature(candidate_event)
            duration_match = int(reference_event.get("durationSteps", 1)) == int(candidate_event.get("durationSteps", 1))
            technique_match = technique_signature(reference_event) == technique_signature(candidate_event)
            exact_note_fret += int(note_match)
            exact_duration += int(duration_match)
            exact_technique += int(technique_match)

            if not (note_match and duration_match and technique_match):
                mismatches.append({
                    "step": step,
                    "reference": {
                        "durationSteps": int(reference_event.get("durationSteps", 1)),
                        "notes": reference_event.get("notes", []),
                        "techniques": reference_event.get("techniques", []),
                    },
                    "candidate": {
                        "durationSteps": int(candidate_event.get("durationSteps", 1)),
                        "notes": candidate_event.get("notes", []),
                        "techniques": candidate_event.get("techniques", []),
                        "confidence": candidate_event.get("confidence"),
                    },
                    "noteFretMatch": note_match,
                    "durationMatch": duration_match,
                    "techniqueMatch": technique_match,
                })

            if len(cands) > 1:
                extras.extend(cands[1:])
            if len(refs) > 1:
                unresolved.extend(refs[1:])

        priority_score = (
            len(unresolved) * 6
            + len(extras) * 4
            + sum(4 for item in mismatches if not item["noteFretMatch"])
            + sum(2 for item in mismatches if not item["durationMatch"])
            + sum(2 for item in mismatches if not item["techniqueMatch"])
        )

        report = {
            "measureNumber": measure_number,
            "section": measure.get("section"),
            "sectionVariant": measure.get("sectionVariant"),
            "referenceEventCount": len(reference_events),
            "candidateEventCount": len(candidate_events),
            "matchedStepCount": matched_steps,
            "unresolvedReferenceCount": len(unresolved),
            "extraCandidateCount": len(extras),
            "mismatchCount": len(mismatches),
            "exactNoteFretMatches": exact_note_fret,
            "exactDurationMatches": exact_duration,
            "exactTechniqueMatches": exact_technique,
            "priorityScore": priority_score,
            "unresolvedReferenceEvents": unresolved,
            "extraCandidateEvents": extras,
            "matchedStepMismatches": mismatches,
            "source": measure.get("source"),
        }
        measure_reports.append(report)

        totals["referenceEvents"] += len(reference_events)
        totals["candidateEvents"] += len(candidate_events)
        totals["matchedSteps"] += matched_steps
        totals["unresolvedReferenceEvents"] += len(unresolved)
        totals["extraCandidateEvents"] += len(extras)
        totals["exactNoteFretMatches"] += exact_note_fret
        totals["exactDurationMatches"] += exact_duration
        totals["exactTechniqueMatches"] += exact_technique

    ranked = sorted(measure_reports, key=lambda item: (-int(item["priorityScore"]), int(item["measureNumber"])))
    correction_plan = {
        "schemaVersion": 1,
        "title": "Gomyway targeted rhythm correction plan",
        "sourceBestAttempt": best.get("attempt"),
        "sourceCompositePercent": best.get("compositePercent"),
        "sourceParameters": best.get("parameters"),
        "professionalReferenceReadOnly": True,
        "automaticPromotionAllowed": False,
        "protectedBaselinesChanged": False,
        "totals": totals,
        "priorityMeasures": [item["measureNumber"] for item in ranked if item["priorityScore"] > 0],
        "topPriorityMeasures": [item["measureNumber"] for item in ranked[:12]],
        "measures": measure_reports,
    }
    write_json(OUTPUT_JSON, correction_plan)

    lines = [
        "Gomyway targeted rhythm correction plan",
        f"Best attempt: {best.get('attempt')}",
        f"Best composite: {best.get('compositePercent')}",
        f"Reference events: {totals['referenceEvents']}",
        f"Candidate events: {totals['candidateEvents']}",
        f"Unresolved reference events: {totals['unresolvedReferenceEvents']}",
        f"Extra candidate events: {totals['extraCandidateEvents']}",
        "",
        "Top priority measures:",
    ]
    for item in ranked[:20]:
        lines.append(
            f"M{item['measureNumber']:03d} score={item['priorityScore']:3d} "
            f"unresolved={item['unresolvedReferenceCount']} extras={item['extraCandidateCount']} "
            f"mismatches={item['mismatchCount']} section={item.get('section')}"
        )
    OUTPUT_TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Targeted correction plan complete")
    print("Best attempt:", best.get("attempt"))
    print("Best composite:", best.get("compositePercent"))
    print("Reference events:", totals["referenceEvents"])
    print("Candidate events:", totals["candidateEvents"])
    print("Unresolved reference events:", totals["unresolvedReferenceEvents"])
    print("Extra candidate events:", totals["extraCandidateEvents"])
    print("Top priority measures:", correction_plan["topPriorityMeasures"])
    print("JSON:", OUTPUT_JSON.relative_to(ROOT))
    print("Text:", OUTPUT_TEXT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
