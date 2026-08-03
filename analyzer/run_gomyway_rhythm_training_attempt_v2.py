from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "analyzer" / "training_profiles" / "rhythm-guitar-reference.json"
OPEN_PITCH = {6: 40, 5: 45, 4: 50, 3: 55, 2: 59, 1: 64}
TUNING = [(6, 40), (5, 45), (4, 50), (3, 55), (2, 59), (1, 64)]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


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


def notes(event: dict[str, Any]) -> list[dict[str, int]]:
    raw = event.get("notes") if isinstance(event.get("notes"), list) else [event]
    output: list[dict[str, int]] = []
    for note in raw:
        if not isinstance(note, dict):
            continue
        string = as_int(note.get("string", note.get("stringIndex", 0)))
        fret = as_int(note.get("fret", -1), -1)
        midi = as_int(note.get("midi", note.get("midiPitch", note.get("pitch", -1))), -1)
        if midi < 0 and string in OPEN_PITCH and fret >= 0:
            midi = OPEN_PITCH[string] + fret
        output.append({"string": string, "fret": fret, "midi": midi})
    return output


def techniques(event: dict[str, Any]) -> set[str]:
    value = event.get("techniques", event.get("technique", []))
    if isinstance(value, str):
        value = [value]
    return {str(item).strip().lower() for item in value if str(item).strip()} if isinstance(value, list) else set()


def reference_events(reference: dict[str, Any]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for measure in reference.get("measures", []):
        number = as_int(measure.get("measureNumber"))
        if not 17 <= number <= 113:
            continue
        for event in measure.get("events", []):
            if isinstance(event, dict):
                output.append({**event, "measureNumber": number, "section": measure.get("section", "Unknown"), "timeSignature": measure.get("timeSignature", "4/4")})
    return output


def attempt_number(profile: dict[str, Any]) -> int:
    directory = ROOT / profile["checkpointDirectory"]
    return len(list(directory.glob("attempt-*.json"))) + 1 if directory.exists() else 1


def parameters(attempt: int) -> dict[str, Any]:
    tempos = [127.5, 128.0, 128.5, 129.0, 129.5, 130.0, 130.5]
    origins = [-0.18, -0.12, -0.06, 0.0, 0.06, 0.12]
    octave_modes = [0, -12]
    index = max(0, attempt - 1)
    return {
        "tempoBpm": tempos[index % len(tempos)],
        "audioOriginSeconds": origins[(index // len(tempos)) % len(origins)],
        "octaveShift": octave_modes[(index // (len(tempos) * len(origins))) % len(octave_modes)],
        "stringStrategy": "rhythm-heavy" if (index // (len(tempos) * len(origins) * len(octave_modes))) % 2 == 0 else "lowest-fret",
        "minimumConfidence": [0.0, 0.08, 0.14][(index // 2) % 3],
    }


def choose_position(midi: int, strategy: str) -> tuple[int, int] | None:
    choices: list[tuple[int, int]] = []
    for string, open_pitch in TUNING:
        fret = midi - open_pitch
        if 0 <= fret <= 24:
            choices.append((string, fret))
    if not choices:
        return None
    if strategy == "rhythm-heavy":
        return min(choices, key=lambda item: (item[1] > 12, -item[0], item[1]))
    return min(choices, key=lambda item: (item[1], -item[0]))


def generate(raw: list[dict[str, Any]], reference: dict[str, Any], params: dict[str, Any]) -> list[dict[str, Any]]:
    tempo = float(params["tempoBpm"])
    measure_seconds = 240.0 / tempo
    step_seconds = measure_seconds / 16.0
    origin = float(params["audioOriginSeconds"])
    octave = int(params["octaveShift"])
    threshold = float(params["minimumConfidence"])
    metadata = {as_int(m.get("measureNumber")): m for m in reference.get("measures", [])}
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)

    for source in sorted(raw, key=lambda item: (as_float(item.get("start")), as_float(item.get("end")))):
        confidence = as_float(source.get("confidence"))
        if confidence < threshold:
            continue
        start = as_float(source.get("start")) - origin
        end = max(start, as_float(source.get("end")) - origin)
        measure = int(start // measure_seconds) + 1
        if not 17 <= measure <= 113:
            continue
        measure_start = (measure - 1) * measure_seconds
        step = int(round((start - measure_start) / step_seconds))
        if step >= 16:
            measure += 1
            step = 0
        if not 17 <= measure <= 113:
            continue
        midi = as_int(source.get("midiPitch")) + octave
        position = choose_position(midi, str(params["stringStrategy"]))
        if position is None:
            continue
        string, fret = position
        grouped[(measure, step)].append({
            "string": string, "fret": fret, "midi": midi, "confidence": confidence,
            "durationSteps": max(1, min(16, int(round((end - start) / step_seconds)))),
        })

    output: list[dict[str, Any]] = []
    for (measure, step), raw_notes in sorted(grouped.items()):
        unique: dict[int, dict[str, Any]] = {}
        for note in raw_notes:
            midi = note["midi"]
            if midi not in unique or note["confidence"] > unique[midi]["confidence"]:
                unique[midi] = note
        selected = sorted(unique.values(), key=lambda item: (-item["string"], item["fret"]))
        meta = metadata.get(measure, {})
        output.append({
            "measureNumber": measure,
            "quantizedStep": step,
            "durationSteps": max(n["durationSteps"] for n in selected),
            "notes": [{"string": n["string"], "fret": n["fret"], "midi": n["midi"]} for n in selected],
            "techniques": [],
            "confidence": sum(n["confidence"] for n in selected) / len(selected),
            "section": meta.get("section", "Unknown"),
            "timeSignature": meta.get("timeSignature", "4/4"),
        })
    return output


def nearest(ref: dict[str, Any], candidates: list[dict[str, Any]], used: set[int], tolerance: int) -> tuple[int | None, dict[str, Any] | None, int | None]:
    choices = []
    for index, candidate in enumerate(candidates):
        if index in used or event_measure(candidate) != event_measure(ref):
            continue
        distance = abs(event_step(candidate) - event_step(ref))
        if distance <= tolerance:
            choices.append((distance, -as_float(candidate.get("confidence")), index, candidate))
    if not choices:
        return None, None, None
    distance, _, index, candidate = min(choices)
    return index, candidate, distance


def fraction(reference: set[Any], candidate: set[Any]) -> float:
    if not reference:
        return 1.0 if not candidate else 0.0
    return len(reference & candidate) / len(reference)


def score(refs: list[dict[str, Any]], candidates: list[dict[str, Any]], tolerance: int) -> dict[str, Any]:
    used: set[int] = set()
    onset = duration = pitch = fret = string = technique = 0.0
    matched = 0
    unresolved = []
    for ref in sorted(refs, key=lambda item: (event_measure(item), event_step(item))):
        index, candidate, distance = nearest(ref, candidates, used, tolerance)
        if candidate is None or index is None or distance is None:
            unresolved.append({"measureNumber": event_measure(ref), "step": event_step(ref)})
            continue
        used.add(index)
        matched += 1
        onset += 1.0 if distance == 0 else 0.5
        delta = abs(event_duration(ref) - event_duration(candidate))
        duration += 1.0 if delta == 0 else (0.5 if delta == 1 else 0.0)
        rn, cn = notes(ref), notes(candidate)
        pitch += fraction({n["midi"] for n in rn if n["midi"] >= 0}, {n["midi"] for n in cn if n["midi"] >= 0})
        fret += fraction({n["fret"] for n in rn if n["fret"] >= 0}, {n["fret"] for n in cn if n["fret"] >= 0})
        string += fraction({n["string"] for n in rn if n["string"] > 0}, {n["string"] for n in cn if n["string"] > 0})
        technique += fraction(techniques(ref), techniques(candidate))

    denominator = max(1, len(refs))
    extra = len(candidates) - len(used)
    penalty = min(0.35, extra / max(1, len(candidates)) * 0.35)
    ref_sections = {(event_measure(e), str(e.get("section", "Unknown")), str(e.get("timeSignature", "4/4"))) for e in refs}
    cand_sections = {(event_measure(e), str(e.get("section", "Unknown")), str(e.get("timeSignature", "4/4"))) for e in candidates}
    categories = {
        "onsetTiming": max(0.0, (onset / denominator - penalty) * 100.0),
        "durationRhythm": duration / denominator * 100.0,
        "noteFret": ((pitch * 0.7 + fret * 0.3) / denominator) * 100.0,
        "stringChoice": string / denominator * 100.0,
        "technique": technique / denominator * 100.0,
        "sectionMeasure": fraction(ref_sections, cand_sections) * 100.0,
    }
    return {
        "categoryScoresPercent": {key: round(value, 6) for key, value in categories.items()},
        "referenceEventCount": len(refs), "candidateEventCount": len(candidates),
        "matchedReferenceEventCount": matched, "extraCandidateEventCount": extra,
        "unresolvedReferenceEventCount": len(unresolved), "unresolvedReferenceEvents": unresolved[:500],
    }


def main() -> None:
    profile = load(PROFILE_PATH)
    attempt = attempt_number(profile)
    params = parameters(attempt)
    reference = load(ROOT / profile["professionalReferencePath"])
    source = load(ROOT / profile["candidateSourceEventsPath"])
    refs = reference_events(reference)
    candidates = generate(source.get("events", []), reference, params)
    result = {
        "attempt": attempt, "status": "scored-active-regeneration-v2", "parameters": params,
        **score(refs, candidates, as_int(profile.get("timingToleranceSteps", 1), 1)),
        "candidateEvents": candidates,
        "protections": profile["protectedRules"],
        "sixteenthNoteGridUsed": True,
        "professionalReferenceUsedForScoringOnly": True,
        "professionalReferenceCopiedIntoCandidate": False,
        "rendererEventsPromoted": False,
        "humanReviewRequiredBeforeRendererPromotion": True,
    }
    write(ROOT / profile["attemptResultPath"], result)
    print("ACTIVE REGENERATION ATTEMPT", attempt, "SCORED", flush=True)
    print("Parameters:", params, flush=True)
    print("Candidate events:", len(candidates), flush=True)
    print("Category scores:", result["categoryScoresPercent"], flush=True)
    print("Matched:", result["matchedReferenceEventCount"], "Unresolved:", result["unresolvedReferenceEventCount"], flush=True)


if __name__ == "__main__":
    main()
