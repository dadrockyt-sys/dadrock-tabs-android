from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "analyzer" / "training_profiles" / "rhythm-guitar-reference.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def event_measure(event: dict[str, Any]) -> int:
    return as_int(event.get("measureNumber", event.get("measure")))


def event_step(event: dict[str, Any]) -> int:
    return as_int(event.get("quantizedStep", event.get("step", event.get("positionStep"))))


def event_duration(event: dict[str, Any]) -> int:
    return max(1, as_int(event.get("durationSteps", event.get("duration", 1)), 1))


def normalize_techniques(value: Any) -> set[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        values = []
    return {str(item).strip().lower() for item in values if str(item).strip()}


def normalize_notes(event: dict[str, Any]) -> list[dict[str, int]]:
    raw = event.get("notes")
    if not isinstance(raw, list):
        raw = [event]
    notes: list[dict[str, int]] = []
    for note in raw:
        if not isinstance(note, dict):
            continue
        string = as_int(note.get("string", note.get("stringIndex", 0)))
        fret = as_int(note.get("fret", -1), -1)
        midi = as_int(note.get("midi", note.get("pitch", -1)), -1)
        notes.append({"string": string, "fret": fret, "midi": midi})
    return notes


def reference_events(reference: dict[str, Any], start: int, end: int) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    measures = reference.get("measures")
    if isinstance(measures, list):
        for measure in measures:
            if not isinstance(measure, dict):
                continue
            number = as_int(measure.get("measureNumber", measure.get("measure")))
            if not start <= number <= end:
                continue
            section = str(measure.get("section", "Unknown"))
            time_signature = str(measure.get("timeSignature", "4/4"))
            tempo = as_float(measure.get("tempoBpm", 0.0))
            for event in measure.get("events") or []:
                if isinstance(event, dict):
                    output.append({
                        **event,
                        "measureNumber": number,
                        "section": section,
                        "timeSignature": time_signature,
                        "tempoBpm": tempo,
                    })
    else:
        for event in reference.get("events") or []:
            if isinstance(event, dict) and start <= event_measure(event) <= end:
                output.append(event)
    return output


def candidate_events(candidate: dict[str, Any], start: int, end: int) -> list[dict[str, Any]]:
    raw = candidate.get("candidates", candidate.get("events", []))
    return [
        event for event in raw
        if isinstance(event, dict) and start <= event_measure(event) <= end
    ]


def attempt_number(profile: dict[str, Any]) -> int:
    directory = ROOT / profile["checkpointDirectory"]
    existing = sorted(directory.glob("attempt-*.json")) if directory.exists() else []
    return len(existing) + 1


def parameters_for_attempt(attempt: int) -> dict[str, Any]:
    strength_thresholds = [0.0, 0.08, 0.12, 0.16, 0.20, 0.25, 0.30]
    timing_shifts = [0, -1, 1]
    index = max(0, attempt - 1)
    return {
        "minimumStrength": strength_thresholds[index % len(strength_thresholds)],
        "globalTimingShiftSteps": timing_shifts[(index // len(strength_thresholds)) % len(timing_shifts)],
        "allowPhraseConsensus": ((index // (len(strength_thresholds) * len(timing_shifts))) % 2) == 1,
    }


def filtered_candidates(events: list[dict[str, Any]], params: dict[str, Any]) -> list[dict[str, Any]]:
    threshold = float(params["minimumStrength"])
    shift = int(params["globalTimingShiftSteps"])
    filtered: list[dict[str, Any]] = []
    for event in events:
        strength = as_float(event.get("strength", event.get("confidence", 1.0)), 1.0)
        if strength < threshold:
            continue
        filtered.append({**event, "quantizedStep": event_step(event) + shift})
    return filtered


def nearest_candidate(
    reference: dict[str, Any],
    candidates: list[dict[str, Any]],
    used: set[int],
    tolerance: int,
) -> tuple[int | None, dict[str, Any] | None, int | None]:
    measure = event_measure(reference)
    step = event_step(reference)
    choices: list[tuple[int, float, int, dict[str, Any]]] = []
    for index, candidate in enumerate(candidates):
        if index in used or event_measure(candidate) != measure:
            continue
        distance = abs(event_step(candidate) - step)
        if distance <= tolerance:
            strength = as_float(candidate.get("strength", candidate.get("confidence", 0.0)))
            choices.append((distance, -strength, index, candidate))
    if not choices:
        return None, None, None
    choices.sort(key=lambda item: (item[0], item[1], item[2]))
    distance, _, index, candidate = choices[0]
    return index, candidate, distance


def fraction_match(reference_values: set[Any], candidate_values: set[Any]) -> float:
    if not reference_values:
        return 1.0 if not candidate_values else 0.0
    return len(reference_values & candidate_values) / len(reference_values)


def score(reference: list[dict[str, Any]], candidates: list[dict[str, Any]], tolerance: int) -> dict[str, Any]:
    used: set[int] = set()
    onset_points = duration_points = note_points = string_points = technique_points = 0.0
    unresolved: list[dict[str, Any]] = []
    matched = 0

    for ref in sorted(reference, key=lambda item: (event_measure(item), event_step(item))):
        index, cand, distance = nearest_candidate(ref, candidates, used, tolerance)
        if cand is None or index is None or distance is None:
            unresolved.append({
                "measureNumber": event_measure(ref),
                "step": event_step(ref),
                "reason": "no-candidate-within-one-sixteenth",
            })
            continue
        used.add(index)
        matched += 1
        onset_points += 1.0 if distance == 0 else 0.5

        ref_duration = event_duration(ref)
        cand_duration = event_duration(cand)
        duration_distance = abs(ref_duration - cand_duration)
        duration_points += 1.0 if duration_distance == 0 else (0.5 if duration_distance == 1 else 0.0)

        ref_notes = normalize_notes(ref)
        cand_notes = normalize_notes(cand)
        ref_frets = {(note["fret"], note["midi"]) for note in ref_notes if note["fret"] >= 0 or note["midi"] >= 0}
        cand_frets = {(note["fret"], note["midi"]) for note in cand_notes if note["fret"] >= 0 or note["midi"] >= 0}
        ref_strings = {note["string"] for note in ref_notes if note["string"] > 0}
        cand_strings = {note["string"] for note in cand_notes if note["string"] > 0}
        note_points += fraction_match(ref_frets, cand_frets)
        string_points += fraction_match(ref_strings, cand_strings)

        ref_techniques = normalize_techniques(ref.get("techniques", ref.get("technique")))
        cand_techniques = normalize_techniques(cand.get("techniques", cand.get("technique")))
        technique_points += fraction_match(ref_techniques, cand_techniques)

    denominator = max(1, len(reference))
    extra_candidates = len(candidates) - len(used)
    precision_penalty = min(0.35, extra_candidates / max(1, len(candidates)) * 0.35)

    section_measures = {
        (event_measure(item), str(item.get("section", "Unknown")), str(item.get("timeSignature", "4/4")))
        for item in reference
    }
    candidate_section_measures = {
        (event_measure(item), str(item.get("section", "Unknown")), str(item.get("timeSignature", "4/4")))
        for item in candidates
        if item.get("section") is not None
    }
    section_score = fraction_match(section_measures, candidate_section_measures)

    categories = {
        "onsetTiming": max(0.0, (onset_points / denominator - precision_penalty) * 100.0),
        "durationRhythm": max(0.0, duration_points / denominator * 100.0),
        "noteFret": max(0.0, note_points / denominator * 100.0),
        "stringChoice": max(0.0, string_points / denominator * 100.0),
        "technique": max(0.0, technique_points / denominator * 100.0),
        "sectionMeasure": max(0.0, section_score * 100.0),
    }
    return {
        "categoryScoresPercent": {key: round(value, 6) for key, value in categories.items()},
        "referenceEventCount": len(reference),
        "candidateEventCount": len(candidates),
        "matchedReferenceEventCount": matched,
        "extraCandidateEventCount": extra_candidates,
        "unresolvedReferenceEventCount": len(unresolved),
        "unresolvedReferenceEvents": unresolved[:500],
        "usedCandidateIndexes": sorted(used),
    }


def main() -> None:
    profile = load_json(PROFILE_PATH)
    result_path = ROOT / profile["attemptResultPath"]
    candidate_path = ROOT / profile["candidateEventsPath"]
    reference_path = ROOT / profile["professionalReferencePath"]
    attempt = attempt_number(profile)
    params = parameters_for_attempt(attempt)

    missing = [str(path.relative_to(ROOT)) for path in (candidate_path, reference_path) if not path.exists()]
    if missing:
        result = {
            "attempt": attempt,
            "status": "blocked-missing-input",
            "missingInputs": missing,
            "categoryScoresPercent": {key: 0.0 for key in profile["weights"]},
            "parameters": params,
            "protections": profile["protectedRules"],
            "sixteenthNoteGridUsed": True,
            "professionalReferenceUsedForScoringOnly": True,
            "rendererEventsPromoted": False,
        }
        write_json(result_path, result)
        print("TRAINING ATTEMPT BLOCKED missing:", missing, flush=True)
        return

    candidate_report = load_json(candidate_path)
    professional_reference = load_json(reference_path)
    start = as_int(profile["measureStart"])
    end = as_int(profile["measureEnd"])
    references = reference_events(professional_reference, start, end)
    candidates = filtered_candidates(candidate_events(candidate_report, start, end), params)

    if not references:
        result = {
            "attempt": attempt,
            "status": "blocked-empty-professional-reference",
            "categoryScoresPercent": {key: 0.0 for key in profile["weights"]},
            "parameters": params,
            "protections": profile["protectedRules"],
            "sixteenthNoteGridUsed": True,
            "professionalReferenceUsedForScoringOnly": True,
            "rendererEventsPromoted": False,
        }
        write_json(result_path, result)
        print("TRAINING ATTEMPT BLOCKED: professional reference has no measures 17-113 events", flush=True)
        return

    scored = score(references, candidates, as_int(profile.get("timingToleranceSteps", 1), 1))
    result = {
        "attempt": attempt,
        "status": "scored",
        "measureStart": start,
        "measureEnd": end,
        "gridSubdivision": "sixteenth-note",
        "timingToleranceSteps": 1,
        "parameters": params,
        **scored,
        "protections": profile["protectedRules"],
        "sixteenthNoteGridUsed": True,
        "professionalReferenceUsedForScoringOnly": True,
        "professionalReferenceCopiedIntoCandidate": False,
        "rendererEventsPromoted": False,
        "humanReviewRequiredBeforeRendererPromotion": True,
    }
    write_json(result_path, result)
    print("TRAINING ATTEMPT", attempt, "SCORED", flush=True)
    print("Parameters:", params, flush=True)
    print("Category scores:", result["categoryScoresPercent"], flush=True)
    print("Reference events:", result["referenceEventCount"], flush=True)
    print("Matched events:", result["matchedReferenceEventCount"], flush=True)
    print("Unresolved events:", result["unresolvedReferenceEventCount"], flush=True)
    print("Output:", result_path.relative_to(ROOT), flush=True)


if __name__ == "__main__":
    main()
