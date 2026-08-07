from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-professional-grade-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-professional-grade-v2-manifest.json"

EXPECTED_CANDIDATE_EVENT_COUNT = 949
MEASURE_START = 17
MEASURE_END = 113
EXPECTED_REFERENCE_MEASURE_COUNT = 97

WEIGHTS = {
    "rhythmPlacement": 0.35,
    "noteFretAccuracy": 0.25,
    "chordMultiplicity": 0.15,
    "completeness": 0.15,
    "technique": 0.10,
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def measure_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def string_of(note: dict[str, Any]) -> int | None:
    for key in ("string", "stringIndex"):
        value = integer(note.get(key))
        if value is not None:
            return value
    return None


def fret_of(note: dict[str, Any]) -> int | None:
    return integer(note.get("fret"))


def candidate_notes(event: dict[str, Any]) -> list[dict[str, Any]]:
    nested = event.get("notes")
    if isinstance(nested, list):
        result = [note for note in nested if isinstance(note, dict)]
        if result:
            return result
    if string_of(event) is not None and fret_of(event) is not None:
        return [event]
    return []


def reference_notes(event: dict[str, Any]) -> list[dict[str, Any]]:
    nested = event.get("notes")
    if not isinstance(nested, list):
        return []
    return [note for note in nested if isinstance(note, dict)]


def normalize_techniques(value: Any) -> list[str]:
    if value in (None, False, "", [], {}):
        return []
    if isinstance(value, str):
        return [value.strip().lower().replace("_", "-")]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(normalize_techniques(item))
        return result
    if value is True:
        return ["present"]
    return [str(value).strip().lower().replace("_", "-")]


def techniques_of(event: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for key in (
        "techniques", "technique", "articulations", "articulation", "bend",
        "vibrato", "slide", "hammerOn", "pullOff", "palmMute", "harmonic",
        "pinchHarmonic", "tap",
    ):
        if key not in event:
            continue
        values = normalize_techniques(event.get(key))
        if values == ["present"]:
            values = [key.lower()]
        result.extend(values)
    return sorted(set(result))


def f1(tp: int, predicted: int, expected: int) -> float:
    if predicted == 0 and expected == 0:
        return 1.0
    if tp <= 0 or predicted <= 0 or expected <= 0:
        return 0.0
    precision = tp / predicted
    recall = tp / expected
    return 2 * precision * recall / (precision + recall)


def multiset_tp(a: Counter[Any], b: Counter[Any]) -> int:
    return sum((a & b).values())


def ratio_similarity(a: int, b: int) -> float:
    if a == 0 and b == 0:
        return 1.0
    if a <= 0 or b <= 0:
        return 0.0
    return min(a, b) / max(a, b)


def completeness(candidate_count: int, reference_count: int) -> float:
    if candidate_count == 0 and reference_count == 0:
        return 1.0
    denominator = max(candidate_count, reference_count, 1)
    return max(0.0, 1.0 - abs(candidate_count - reference_count) / denominator)


def pct(value: float) -> float:
    return round(value * 100.0, 2)


def main() -> None:
    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate_payload = load_json(CANDIDATE_PATH)
    candidate_events = rows(candidate_payload)
    if len(candidate_events) != EXPECTED_CANDIDATE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_CANDIDATE_EVENT_COUNT} protected candidate events, found {len(candidate_events)}."
        )

    # Freeze independent candidate before professional truth is loaded.
    frozen_candidate = json.loads(json.dumps(candidate_events))

    reference = load_json(REFERENCE_PATH)
    if reference.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference must remain scoring-only.")
    if reference.get("instrument") != "rhythm-guitar":
        raise RuntimeError("Professional reference instrument changed unexpectedly.")
    if integer(reference.get("humanApprovedMeasureCount")) != EXPECTED_REFERENCE_MEASURE_COUNT:
        raise RuntimeError("Professional reference approved-measure count changed unexpectedly.")

    ref_measures = reference.get("measures")
    if not isinstance(ref_measures, list):
        raise RuntimeError("Professional reference measures missing.")
    ref_by_measure = {
        int(row["measureNumber"]): row
        for row in ref_measures
        if isinstance(row, dict) and "measureNumber" in row
    }
    if sorted(ref_by_measure) != list(range(MEASURE_START, MEASURE_END + 1)):
        raise RuntimeError("Professional reference measure range is not exactly 17-113.")

    candidate_by_measure_step: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    candidate_nested_note_count = 0
    candidate_direct_note_count = 0
    for event in frozen_candidate:
        measure = measure_of(event)
        step = step_of(event)
        if measure is None or step is None or not MEASURE_START <= measure <= MEASURE_END:
            continue
        candidate_by_measure_step[measure][step].append(event)
        nested = event.get("notes")
        if isinstance(nested, list) and any(isinstance(note, dict) for note in nested):
            candidate_nested_note_count += sum(1 for note in nested if isinstance(note, dict))
        elif string_of(event) is not None and fret_of(event) is not None:
            candidate_direct_note_count += 1

    if candidate_nested_note_count == 0 and candidate_direct_note_count == 0:
        raise RuntimeError("Corrected grader still found no usable candidate notes.")

    total_step_tp = 0
    total_candidate_steps = 0
    total_reference_steps = 0
    global_candidate_notes: Counter[tuple[int, int, int, int]] = Counter()
    global_reference_notes: Counter[tuple[int, int, int, int]] = Counter()
    global_candidate_techniques: Counter[tuple[int, int, str]] = Counter()
    global_reference_techniques: Counter[tuple[int, int, str]] = Counter()
    chord_scores: list[float] = []
    completeness_scores: list[float] = []
    duration_scores: list[float] = []
    measure_scores: list[dict[str, Any]] = []

    for measure in range(MEASURE_START, MEASURE_END + 1):
        ref_measure = ref_by_measure[measure]
        ref_events = ref_measure.get("events")
        if not isinstance(ref_events, list):
            raise RuntimeError(f"Reference measure {measure} has no events list.")

        candidate_steps = candidate_by_measure_step.get(measure, {})
        ref_by_step: dict[int, dict[str, Any]] = {}
        for event in ref_events:
            if isinstance(event, dict):
                step = integer(event.get("quantizedStep"))
                if step is not None:
                    ref_by_step[step] = event

        candidate_occupied = set(candidate_steps)
        ref_occupied = set(ref_by_step)
        shared = candidate_occupied & ref_occupied
        rhythm_score = f1(len(shared), len(candidate_occupied), len(ref_occupied))
        total_step_tp += len(shared)
        total_candidate_steps += len(candidate_occupied)
        total_reference_steps += len(ref_occupied)

        measure_candidate_notes: Counter[tuple[int, int, int]] = Counter()
        measure_reference_notes: Counter[tuple[int, int, int]] = Counter()
        measure_candidate_techniques: Counter[tuple[int, str]] = Counter()
        measure_reference_techniques: Counter[tuple[int, str]] = Counter()

        candidate_note_count = 0
        reference_note_count = 0
        per_step_chord_scores: list[float] = []

        for step in sorted(candidate_occupied | ref_occupied):
            candidate_event_rows = candidate_steps.get(step, [])
            candidate_notes_at_step: list[dict[str, Any]] = []
            for row in candidate_event_rows:
                candidate_notes_at_step.extend(candidate_notes(row))
                for technique in techniques_of(row):
                    measure_candidate_techniques[(step, technique)] += 1
                    global_candidate_techniques[(measure, step, technique)] += 1

            ref_event = ref_by_step.get(step)
            ref_notes_at_step = reference_notes(ref_event) if isinstance(ref_event, dict) else []

            candidate_note_count += len(candidate_notes_at_step)
            reference_note_count += len(ref_notes_at_step)
            per_step_chord_scores.append(ratio_similarity(len(candidate_notes_at_step), len(ref_notes_at_step)))

            for note in candidate_notes_at_step:
                string = string_of(note)
                fret = fret_of(note)
                if string is None or fret is None:
                    continue
                measure_candidate_notes[(step, string, fret)] += 1
                global_candidate_notes[(measure, step, string, fret)] += 1

            if isinstance(ref_event, dict):
                for note in ref_notes_at_step:
                    string = string_of(note)
                    fret = fret_of(note)
                    if string is None or fret is None:
                        continue
                    measure_reference_notes[(step, string, fret)] += 1
                    global_reference_notes[(measure, step, string, fret)] += 1
                for technique in normalize_techniques(ref_event.get("techniques", [])):
                    measure_reference_techniques[(step, technique)] += 1
                    global_reference_techniques[(measure, step, technique)] += 1

                ref_duration = integer(ref_event.get("durationSteps"))
                if ref_duration is not None and candidate_event_rows:
                    candidate_durations = [integer(row.get("durationSteps")) for row in candidate_event_rows]
                    comparable = [value for value in candidate_durations if value is not None]
                    if comparable:
                        candidate_duration = max(1, round(sum(comparable) / len(comparable)))
                        duration_scores.append(ratio_similarity(candidate_duration, max(1, ref_duration)))

        note_tp = multiset_tp(measure_candidate_notes, measure_reference_notes)
        note_score = f1(note_tp, sum(measure_candidate_notes.values()), sum(measure_reference_notes.values()))
        chord_score = sum(per_step_chord_scores) / len(per_step_chord_scores) if per_step_chord_scores else 1.0
        completeness_score = completeness(candidate_note_count, reference_note_count)
        technique_tp = multiset_tp(measure_candidate_techniques, measure_reference_techniques)
        technique_score = f1(
            technique_tp,
            sum(measure_candidate_techniques.values()),
            sum(measure_reference_techniques.values()),
        )

        chord_scores.append(chord_score)
        completeness_scores.append(completeness_score)

        overall = (
            rhythm_score * WEIGHTS["rhythmPlacement"]
            + note_score * WEIGHTS["noteFretAccuracy"]
            + chord_score * WEIGHTS["chordMultiplicity"]
            + completeness_score * WEIGHTS["completeness"]
            + technique_score * WEIGHTS["technique"]
        )

        measure_scores.append({
            "measureNumber": measure,
            "section": ref_measure.get("section"),
            "sectionVariant": ref_measure.get("sectionVariant"),
            "candidateOccupiedSteps": sorted(candidate_occupied),
            "referenceOccupiedSteps": sorted(ref_occupied),
            "sharedOccupiedSteps": sorted(shared),
            "missingReferenceSteps": sorted(ref_occupied - candidate_occupied),
            "extraCandidateSteps": sorted(candidate_occupied - ref_occupied),
            "candidateNoteCount": candidate_note_count,
            "referenceNoteCount": reference_note_count,
            "scores": {
                "rhythmPlacement": pct(rhythm_score),
                "noteFretAccuracy": pct(note_score),
                "chordMultiplicity": pct(chord_score),
                "completeness": pct(completeness_score),
                "technique": pct(technique_score),
                "overall": pct(overall),
            },
            "professionalReferenceRole": "grading-training-label-only",
        })

    rhythm_global = f1(total_step_tp, total_candidate_steps, total_reference_steps)
    note_tp_global = multiset_tp(global_candidate_notes, global_reference_notes)
    note_global = f1(note_tp_global, sum(global_candidate_notes.values()), sum(global_reference_notes.values()))
    chord_global = sum(chord_scores) / len(chord_scores) if chord_scores else 0.0
    completeness_global = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0
    technique_tp_global = multiset_tp(global_candidate_techniques, global_reference_techniques)
    technique_global = f1(
        technique_tp_global,
        sum(global_candidate_techniques.values()),
        sum(global_reference_techniques.values()),
    )
    timing_global = sum(duration_scores) / len(duration_scores) if duration_scores else None

    overall_global = (
        rhythm_global * WEIGHTS["rhythmPlacement"]
        + note_global * WEIGHTS["noteFretAccuracy"]
        + chord_global * WEIGHTS["chordMultiplicity"]
        + completeness_global * WEIGHTS["completeness"]
        + technique_global * WEIGHTS["technique"]
    )

    weakest = sorted(measure_scores, key=lambda row: float(row["scores"]["overall"]))[:12]
    strongest = sorted(measure_scores, key=lambda row: float(row["scores"]["overall"]), reverse=True)[:12]
    priorities = [int(row["measureNumber"]) for row in weakest]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    candidate_unchanged = candidate_hash_before == candidate_hash_after
    passed = bool(candidate_unchanged and len(measure_scores) == EXPECTED_REFERENCE_MEASURE_COUNT)

    output = {
        "schemaVersion": 2,
        "gradeType": "read-only-independent-rhythm-output-vs-professional-reference",
        "passed": passed,
        "candidateFrozenBeforeProfessionalReferenceLoad": True,
        "candidateNoteRepresentation": "nested-notes-preferred-with-direct-fallback",
        "candidateNestedNoteCount": candidate_nested_note_count,
        "candidateDirectFallbackNoteCount": candidate_direct_note_count,
        "measuresGraded": len(measure_scores),
        "scores": {
            "overall": pct(overall_global),
            "rhythmPlacement": pct(rhythm_global),
            "noteFretAccuracy": pct(note_global),
            "chordMultiplicity": pct(chord_global),
            "completeness": pct(completeness_global),
            "technique": pct(technique_global),
            "timingDuration": pct(timing_global) if timing_global is not None else None,
        },
        "weakestMeasures": weakest,
        "strongestMeasures": strongest,
        "recommendedTrainingPriorityMeasures": priorities,
        "measureScores": measure_scores,
        "professionalReferenceRole": "grading-training-label-only",
        "professionalReferenceCopiedIntoCandidate": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "thresholdRelaxationAllowed": False,
        "automaticApplyAllowed": False,
        "candidateHashBefore": candidate_hash_before,
        "candidateHashAfter": candidate_hash_after,
        "candidateHashUnchanged": candidate_unchanged,
        "readyForTargetedProfessionalGradeTraining": passed,
        "recommendedNextAction": (
            "train-gomyway-rhythm-from-professional-grade-priorities-v2"
            if passed
            else "diagnose-gomyway-rhythm-professional-grade-v2"
        ),
    }

    manifest = {
        "schemaVersion": 2,
        "passed": passed,
        "overallScore": pct(overall_global),
        "rhythmPlacementScore": pct(rhythm_global),
        "noteFretAccuracyScore": pct(note_global),
        "chordMultiplicityScore": pct(chord_global),
        "completenessScore": pct(completeness_global),
        "techniqueScore": pct(technique_global),
        "timingDurationScore": pct(timing_global) if timing_global is not None else None,
        "candidateNestedNoteCount": candidate_nested_note_count,
        "recommendedTrainingPriorityMeasures": priorities,
        "candidateHashUnchanged": candidate_unchanged,
        "professionalReferenceRole": "grading-training-label-only",
        "automaticApplyAllowed": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": output["recommendedNextAction"],
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM PROFESSIONAL GRADE V2 COMPLETE")
    print("Passed:", passed)
    print("Candidate note representation: nested-notes-preferred-with-direct-fallback")
    print("Candidate nested note count:", candidate_nested_note_count)
    print("Candidate direct fallback note count:", candidate_direct_note_count)
    print("Measures graded:", len(measure_scores))
    print("Overall rhythm transcription score:", pct(overall_global))
    print("Rhythm placement:", pct(rhythm_global))
    print("Note/fret accuracy:", pct(note_global))
    print("Chord multiplicity:", pct(chord_global))
    print("Completeness:", pct(completeness_global))
    print("Technique:", pct(technique_global))
    print("Timing/duration:", pct(timing_global) if timing_global is not None else "NOT SCORED")
    print("Weakest measures:")
    for row in weakest:
        scores = row["scores"]
        print(
            f"  measure={row['measureNumber']} overall={scores['overall']} "
            f"rhythm={scores['rhythmPlacement']} notes={scores['noteFretAccuracy']} "
            f"chords={scores['chordMultiplicity']} completeness={scores['completeness']} "
            f"technique={scores['technique']}"
        )
    print("Strongest measures:")
    for row in strongest:
        print(f"  measure={row['measureNumber']} overall={row['scores']['overall']}")
    print("Recommended training priority measures:", priorities)
    print("Candidate event count:", len(candidate_events))
    print("Candidate hash unchanged:", candidate_unchanged)
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for targeted professional-grade training:", passed)
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
