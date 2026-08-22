from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

PLAN_PATH = PUBLIC / "gomyway-chorus-33-35-chord-recovery-plan-v1.json"
EVIDENCE_PATH = PUBLIC / "gomyway-chorus-33-35-audio-chord-evidence-v1.json"
SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-chord-candidate-projection-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-chord-candidate-projection-v1-manifest.json"

STANDARD_TUNING_MIDI = {
    1: 64,
    2: 59,
    3: 55,
    4: 50,
    5: 45,
    6: 40,
}

MAX_FRET = 12
MAX_FRET_SPAN = 4
MAX_CANDIDATES_PER_TARGET = 12
MAX_NOTES_PER_STRING = 4


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def measure_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def normalize_source_note(note: dict[str, Any]) -> tuple[int, int] | None:
    raw_string = integer(note.get("string", note.get("stringIndex")))
    fret = integer(note.get("fret"))
    if raw_string is None or fret is None or not 0 <= fret <= 24:
        return None
    if "string" in note and 1 <= raw_string <= 6:
        return raw_string, fret
    if 1 <= raw_string <= 6:
        return raw_string, fret
    if 0 <= raw_string <= 5:
        return raw_string + 1, fret
    return None


def notes_for_event(event: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    raw = event.get("notes")
    if not isinstance(raw, list):
        return ()
    result = {
        normalized
        for note in raw
        if isinstance(note, dict)
        for normalized in [normalize_source_note(note)]
        if normalized is not None
    }
    return tuple(sorted(result))


def current_notes_at(source: list[dict[str, Any]], measure: int, step: int) -> tuple[tuple[int, int], ...]:
    result: set[tuple[int, int]] = set()
    for event in source:
        if measure_of(event) == measure and step_of(event) == step:
            result.update(notes_for_event(event))
    return tuple(sorted(result))


def pitch_class(string: int, fret: int) -> int:
    return (STANDARD_TUNING_MIDI[string] + fret) % 12


def fret_span(notes: tuple[tuple[int, int], ...]) -> int:
    fretted = [fret for _string, fret in notes if fret > 0]
    return max(fretted) - min(fretted) if len(fretted) >= 2 else 0


def average_fret(notes: tuple[tuple[int, int], ...]) -> float:
    return sum(fret for _string, fret in notes) / len(notes)


def candidate_pitch_classes(notes: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    return tuple(sorted({pitch_class(string, fret) for string, fret in notes}))


def note_distance(a: tuple[tuple[int, int], ...], b: tuple[tuple[int, int], ...]) -> float:
    if not a or not b:
        return 8.0
    by_string_a = {string: fret for string, fret in a}
    by_string_b = {string: fret for string, fret in b}
    all_strings = set(by_string_a) | set(by_string_b)
    total = 0.0
    for string in all_strings:
        if string in by_string_a and string in by_string_b:
            total += abs(by_string_a[string] - by_string_b[string])
        else:
            total += 3.5
    return total / max(1, len(all_strings))


def shape_match_score(candidate: tuple[tuple[int, int], ...], reference: list[dict[str, Any]]) -> float:
    ref_notes = tuple(
        sorted(
            (int(row["string"]), int(row["fret"]))
            for row in reference
            if isinstance(row, dict) and integer(row.get("string")) and integer(row.get("fret")) is not None
        )
    )
    if not ref_notes:
        return 0.0
    distance = note_distance(candidate, ref_notes)
    return max(0.0, 1.0 - distance / 8.0)


def playable_options_for_string(string: int, desired_classes: set[int], salience: dict[int, float]) -> list[tuple[int, float]]:
    options: list[tuple[int, float]] = []
    for fret in range(MAX_FRET + 1):
        pc = pitch_class(string, fret)
        if pc not in desired_classes:
            continue
        score = float(salience.get(pc, 0.0))
        options.append((fret, score))
    options.sort(key=lambda item: (-item[1], item[0]))
    return options[:MAX_NOTES_PER_STRING]


def enumerate_candidates(
    desired_classes: set[int],
    target_multiplicity: int,
    salience: dict[int, float],
) -> list[tuple[tuple[int, int], ...]]:
    target_multiplicity = max(2, min(6, target_multiplicity))
    candidates: set[tuple[tuple[int, int], ...]] = set()

    options_by_string = {
        string: playable_options_for_string(string, desired_classes, salience)
        for string in range(1, 7)
    }

    for strings in itertools.combinations(range(1, 7), target_multiplicity):
        option_lists = [options_by_string[string] for string in strings]
        if any(not options for options in option_lists):
            continue
        for frets in itertools.product(*option_lists):
            notes = tuple(sorted((string, fret_score[0]) for string, fret_score in zip(strings, frets)))
            if fret_span(notes) > MAX_FRET_SPAN:
                continue
            if len(candidate_pitch_classes(notes)) < min(2, len(desired_classes)):
                continue
            candidates.add(notes)

    return sorted(candidates)


def score_candidate(
    candidate: tuple[tuple[int, int], ...],
    desired_classes: set[int],
    salience: dict[int, float],
    current_notes: tuple[tuple[int, int], ...],
    reference_shape: list[dict[str, Any]],
) -> dict[str, float]:
    pcs = candidate_pitch_classes(candidate)
    audio_score = sum(salience.get(pc, 0.0) for pc in pcs) / max(1, len(pcs))
    coverage_score = len(set(pcs) & desired_classes) / max(1, len(desired_classes))
    current_continuity = max(0.0, 1.0 - note_distance(candidate, current_notes) / 10.0)
    playability = max(0.0, 1.0 - fret_span(candidate) / max(1.0, MAX_FRET_SPAN + 1.0))
    register_penalty = max(0.0, (average_fret(candidate) - 10.0) / 10.0)
    reference_score = shape_match_score(candidate, reference_shape)

    total = (
        audio_score * 0.38
        + coverage_score * 0.24
        + current_continuity * 0.16
        + playability * 0.14
        + reference_score * 0.08
        - register_penalty * 0.08
    )

    return {
        "audioScore": round(audio_score, 6),
        "pitchClassCoverageScore": round(coverage_score, 6),
        "currentSourceContinuityScore": round(current_continuity, 6),
        "playabilityScore": round(playability, 6),
        "professionalBenchmarkScore": round(reference_score, 6),
        "registerPenalty": round(register_penalty, 6),
        "totalScore": round(total, 6),
    }


def main() -> None:
    plan = load(PLAN_PATH)
    evidence = load(EVIDENCE_PATH)
    source = load(SOURCE_PATH)

    if evidence.get("passed") is not True:
        raise RuntimeError("Audio chord evidence is not green.")
    if evidence.get("readyForReadOnlyChordCandidateProjection") is not True:
        raise RuntimeError("Audio chord evidence is not ready for projection.")

    source_events = source_rows(source)
    if len(source_events) != 949:
        raise RuntimeError(f"Expected 949 protected source events, found {len(source_events)}.")

    plan_targets = {
        (int(row["measureNumber"]), int(row["quantizedStep"])): row
        for row in plan.get("targets", [])
        if isinstance(row, dict)
    }

    projection_rows: list[dict[str, Any]] = []
    unsupported_rows: list[dict[str, Any]] = []

    for evidence_row in evidence.get("rows", []):
        if not isinstance(evidence_row, dict):
            continue
        measure = int(evidence_row["measureNumber"])
        step = int(evidence_row["quantizedStep"])
        target = plan_targets.get((measure, step))
        if target is None:
            continue

        if evidence_row.get("audioSupportsChordRecovery") is not True:
            unsupported_rows.append({
                "measureNumber": measure,
                "quantizedStep": step,
                "reason": "insufficient-audio-support",
                "readOnly": True,
            })
            continue

        desired_classes = {
            int(value) % 12
            for value in evidence_row.get("referencePitchClassesForScoringOnly", [])
            if isinstance(value, (int, float))
        }
        salience = {
            int(key): float(value)
            for key, value in evidence_row.get("pitchClassSalience", {}).items()
        }
        target_multiplicity = int(target.get("targetAttackMultiplicity", 2))
        current_notes = current_notes_at(source_events, measure, step)
        reference_shape = target.get("referenceStringFretShapeForScoringOnly", [])

        candidates = enumerate_candidates(desired_classes, target_multiplicity, salience)
        ranked = []
        for candidate in candidates:
            scores = score_candidate(
                candidate,
                desired_classes,
                salience,
                current_notes,
                reference_shape if isinstance(reference_shape, list) else [],
            )
            ranked.append({
                "notes": [{"string": string, "fret": fret} for string, fret in candidate],
                "pitchClasses": list(candidate_pitch_classes(candidate)),
                "fretSpan": fret_span(candidate),
                "scores": scores,
            })

        ranked.sort(key=lambda row: row["scores"]["totalScore"], reverse=True)
        ranked = ranked[:MAX_CANDIDATES_PER_TARGET]

        projection_rows.append({
            "measureNumber": measure,
            "quantizedStep": step,
            "attackSeconds": evidence_row.get("attackSeconds"),
            "targetAttackMultiplicity": target_multiplicity,
            "currentSourceNotes": [
                {"string": string, "fret": fret}
                for string, fret in current_notes
            ],
            "audioSupportedPitchClasses": sorted(desired_classes),
            "audioReferenceSupport": evidence_row.get("referencePitchClassSupport"),
            "audioMissingPitchSupport": evidence_row.get("missingPitchClassSupport"),
            "candidateCount": len(ranked),
            "selectedCandidate": ranked[0] if ranked else None,
            "rankedCandidates": ranked,
            "selectionStatus": "read-only-candidate" if ranked else "no-playable-candidate",
            "professionalReferenceUsedForScoringOnly": True,
            "professionalNotesCopiedIntoOutput": False,
            "sourceEventsModified": False,
            "productionEligible": False,
        })

    ready_rows = [row for row in projection_rows if row.get("selectedCandidate") is not None]
    output = {
        "schemaVersion": 1,
        "projectionType": "audio-supported-playable-chord-candidates",
        "passed": len(projection_rows) == evidence.get("audioSupportedTargetCount"),
        "supportedTargetCount": evidence.get("audioSupportedTargetCount"),
        "unsupportedTargetCount": evidence.get("unsupportedTargetCount"),
        "projectedTargetCount": len(projection_rows),
        "readyCandidateCount": len(ready_rows),
        "readyForFocusedChorusProof": len(ready_rows) == len(projection_rows) and len(ready_rows) > 0,
        "rows": projection_rows,
        "unsupportedRows": unsupported_rows,
        "professionalReferenceUsedForScoringOnly": True,
        "professionalNotesCopiedIntoOutput": False,
        "sourceEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": output["passed"],
        "projectedTargetCount": output["projectedTargetCount"],
        "readyCandidateCount": output["readyCandidateCount"],
        "unsupportedTargetCount": output["unsupportedTargetCount"],
        "readyForFocusedChorusProof": output["readyForFocusedChorusProof"],
        "sourceEventsModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 CHORD CANDIDATE PROJECTION V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Audio-supported targets:", output["supportedTargetCount"])
    print("Projected targets:", output["projectedTargetCount"])
    print("Ready candidates:", output["readyCandidateCount"])
    print("Unsupported targets preserved:", output["unsupportedTargetCount"])
    print("Ready for focused chorus proof:", output["readyForFocusedChorusProof"])
    for row in projection_rows:
        selected = row.get("selectedCandidate")
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"candidates={row['candidateCount']} "
            f"selected={selected['notes'] if selected else None} "
            f"score={selected['scores']['totalScore'] if selected else None}"
        )
    print("Professional reference used for scoring only: True")
    print("Professional notes copied into output: False")
    print("Source events modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
