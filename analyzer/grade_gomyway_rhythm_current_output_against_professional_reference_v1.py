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
ANCHOR60_TRAINING_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-60-training-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-professional-grade-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-professional-grade-v1-manifest.json"

EXPECTED_CANDIDATE_EVENT_COUNT = 949
MEASURE_START = 17
MEASURE_END = 113
EXPECTED_REFERENCE_MEASURE_COUNT = 97

# Domain weights are intentionally explicit. Timing/duration is reported separately
# and is included only if both candidate and professional reference expose comparable
# quantized duration information.
BASE_WEIGHTS = {
    "rhythmPlacement": 0.35,
    "noteFretAccuracy": 0.25,
    "chordMultiplicity": 0.15,
    "completeness": 0.15,
    "technique": 0.10,
}

TECHNIQUE_KEYS = (
    "technique",
    "techniques",
    "articulation",
    "articulations",
    "bend",
    "vibrato",
    "slide",
    "hammerOn",
    "pullOff",
    "palmMute",
    "harmonic",
    "pinchHarmonic",
    "tap",
)


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


def candidate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def measure_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def string_of(note: dict[str, Any]) -> int | None:
    for key in ("stringIndex", "string"):
        value = integer(note.get(key))
        if value is not None:
            return value
    return None


def fret_of(note: dict[str, Any]) -> int | None:
    return integer(note.get("fret"))


def normalize_technique_value(value: Any) -> list[str]:
    if value in (None, False, "", [], {}):
        return []
    if isinstance(value, str):
        return [value.strip().lower().replace("_", "-")]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(normalize_technique_value(item))
        return result
    if value is True:
        return ["present"]
    return [str(value).strip().lower().replace("_", "-")]


def techniques_of_candidate(event: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for key in TECHNIQUE_KEYS:
        if key not in event:
            continue
        values = normalize_technique_value(event.get(key))
        if key in ("bend", "vibrato", "slide", "hammerOn", "pullOff", "palmMute", "harmonic", "pinchHarmonic", "tap"):
            normalized_key = key.replace("On", "-on").replace("Off", "-off")
            if values and values != ["present"]:
                result.extend(values)
            elif values:
                result.append(normalized_key.lower())
        else:
            result.extend(values)
    return sorted(set(result))


def f1_from_counts(tp: int, predicted: int, expected: int) -> float:
    if predicted == 0 and expected == 0:
        return 1.0
    if predicted == 0 or expected == 0 or tp == 0:
        return 0.0
    precision = tp / predicted
    recall = tp / expected
    return 2.0 * precision * recall / (precision + recall)


def multiset_intersection_size(a: Counter[Any], b: Counter[Any]) -> int:
    return sum((a & b).values())


def multiplicity_similarity(candidate_count: int, reference_count: int) -> float:
    if candidate_count == 0 and reference_count == 0:
        return 1.0
    if candidate_count <= 0 or reference_count <= 0:
        return 0.0
    return min(candidate_count, reference_count) / max(candidate_count, reference_count)


def completeness_similarity(candidate_count: int, reference_count: int) -> float:
    if candidate_count == 0 and reference_count == 0:
        return 1.0
    denominator = max(candidate_count, reference_count, 1)
    return max(0.0, 1.0 - abs(candidate_count - reference_count) / denominator)


def percent(value: float) -> float:
    return round(value * 100.0, 2)


def main() -> None:
    # Freeze the independently produced candidate before loading professional truth.
    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate_payload = load_json(CANDIDATE_PATH)
    candidate_events = candidate_rows(candidate_payload)
    if len(candidate_events) != EXPECTED_CANDIDATE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_CANDIDATE_EVENT_COUNT} protected candidate events, "
            f"found {len(candidate_events)}."
        )
    frozen_candidate_events = [dict(row) for row in candidate_events]

    anchor60_training = load_json(ANCHOR60_TRAINING_PATH)
    if anchor60_training.get("passed") is not True:
        raise RuntimeError("Novel anchor 60 evidence-training artifact is not green.")
    if anchor60_training.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Anchor 60 training did not preserve protected source hash.")

    # Professional truth is loaded only after candidate freeze and is scoring-only.
    reference = load_json(REFERENCE_PATH)
    if reference.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not explicitly marked scoring-only.")
    if reference.get("instrument") != "rhythm-guitar":
        raise RuntimeError("Professional reference instrument changed unexpectedly.")
    if integer(reference.get("measureStart")) != MEASURE_START or integer(reference.get("measureEnd")) != MEASURE_END:
        raise RuntimeError("Professional reference measure range changed unexpectedly.")
    if integer(reference.get("humanApprovedMeasureCount")) != EXPECTED_REFERENCE_MEASURE_COUNT:
        raise RuntimeError("Professional reference approved-measure count changed unexpectedly.")
    if reference.get("readyForTraining") is not True:
        raise RuntimeError("Professional reference is not marked ready for training/scoring.")

    reference_measures = reference.get("measures")
    if not isinstance(reference_measures, list):
        raise RuntimeError("Professional reference measures are missing.")
    reference_by_measure = {
        int(row["measureNumber"]): row
        for row in reference_measures
        if isinstance(row, dict) and "measureNumber" in row
    }
    if sorted(reference_by_measure) != list(range(MEASURE_START, MEASURE_END + 1)):
        raise RuntimeError("Professional reference does not contain exactly measures 17-113.")

    candidate_by_measure_step: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for event in frozen_candidate_events:
        measure = measure_of(event)
        step = step_of(event)
        if measure is None or step is None or not MEASURE_START <= measure <= MEASURE_END:
            continue
        candidate_by_measure_step[measure][step].append(event)

    measure_scores: list[dict[str, Any]] = []
    all_candidate_note_tokens: Counter[tuple[int, int, int, int]] = Counter()
    all_reference_note_tokens: Counter[tuple[int, int, int, int]] = Counter()
    all_candidate_technique_tokens: Counter[tuple[int, int, str]] = Counter()
    all_reference_technique_tokens: Counter[tuple[int, int, str]] = Counter()

    total_step_tp = 0
    total_candidate_steps = 0
    total_reference_steps = 0
    multiplicity_samples: list[float] = []
    completeness_samples: list[float] = []
    duration_samples: list[float] = []
    comparable_duration_event_count = 0

    for measure in range(MEASURE_START, MEASURE_END + 1):
        reference_measure = reference_by_measure[measure]
        reference_events = reference_measure.get("events")
        if not isinstance(reference_events, list):
            raise RuntimeError(f"Professional reference measure {measure} has no events list.")

        candidate_steps = candidate_by_measure_step.get(measure, {})
        candidate_occupied = set(candidate_steps)
        reference_by_step: dict[int, dict[str, Any]] = {}
        for event in reference_events:
            if not isinstance(event, dict):
                continue
            step = integer(event.get("quantizedStep"))
            if step is not None:
                reference_by_step[step] = event
        reference_occupied = set(reference_by_step)

        shared_steps = candidate_occupied & reference_occupied
        total_step_tp += len(shared_steps)
        total_candidate_steps += len(candidate_occupied)
        total_reference_steps += len(reference_occupied)
        rhythm_f1 = f1_from_counts(len(shared_steps), len(candidate_occupied), len(reference_occupied))

        measure_candidate_notes: Counter[tuple[int, int, int]] = Counter()
        measure_reference_notes: Counter[tuple[int, int, int]] = Counter()
        measure_candidate_techniques: Counter[tuple[int, str]] = Counter()
        measure_reference_techniques: Counter[tuple[int, str]] = Counter()

        union_steps = sorted(candidate_occupied | reference_occupied)
        per_step_multiplicity: list[float] = []
        candidate_note_count = 0
        reference_note_count = 0

        for step in union_steps:
            candidate_rows_at_step = candidate_steps.get(step, [])
            reference_event = reference_by_step.get(step)
            reference_notes = reference_event.get("notes", []) if isinstance(reference_event, dict) else []
            if not isinstance(reference_notes, list):
                reference_notes = []

            candidate_count = len(candidate_rows_at_step)
            reference_count = len([note for note in reference_notes if isinstance(note, dict)])
            candidate_note_count += candidate_count
            reference_note_count += reference_count
            per_step_multiplicity.append(multiplicity_similarity(candidate_count, reference_count))

            for row in candidate_rows_at_step:
                string = string_of(row)
                fret = fret_of(row)
                if string is not None and fret is not None:
                    token = (step, string, fret)
                    measure_candidate_notes[token] += 1
                    all_candidate_note_tokens[(measure, step, string, fret)] += 1
                for technique in techniques_of_candidate(row):
                    measure_candidate_techniques[(step, technique)] += 1
                    all_candidate_technique_tokens[(measure, step, technique)] += 1

            if isinstance(reference_event, dict):
                for note in reference_notes:
                    if not isinstance(note, dict):
                        continue
                    string = string_of(note)
                    fret = fret_of(note)
                    if string is not None and fret is not None:
                        token = (step, string, fret)
                        measure_reference_notes[token] += 1
                        all_reference_note_tokens[(measure, step, string, fret)] += 1
                techniques = reference_event.get("techniques", [])
                if isinstance(techniques, list):
                    for technique in techniques:
                        for normalized in normalize_technique_value(technique):
                            measure_reference_techniques[(step, normalized)] += 1
                            all_reference_technique_tokens[(measure, step, normalized)] += 1

                duration_steps = integer(reference_event.get("durationSteps"))
                if duration_steps is not None and candidate_rows_at_step:
                    candidate_duration_steps = [integer(row.get("durationSteps")) for row in candidate_rows_at_step]
                    comparable = [value for value in candidate_duration_steps if value is not None]
                    if comparable:
                        reference_duration = max(1, duration_steps)
                        candidate_duration = max(1, round(sum(comparable) / len(comparable)))
                        duration_samples.append(multiplicity_similarity(candidate_duration, reference_duration))
                        comparable_duration_event_count += 1

        chord_score = sum(per_step_multiplicity) / len(per_step_multiplicity) if per_step_multiplicity else 1.0
        completeness_score = completeness_similarity(candidate_note_count, reference_note_count)
        note_tp = multiset_intersection_size(measure_candidate_notes, measure_reference_notes)
        note_score = f1_from_counts(note_tp, sum(measure_candidate_notes.values()), sum(measure_reference_notes.values()))
        technique_tp = multiset_intersection_size(measure_candidate_techniques, measure_reference_techniques)
        technique_score = f1_from_counts(
            technique_tp,
            sum(measure_candidate_techniques.values()),
            sum(measure_reference_techniques.values()),
        )

        multiplicity_samples.append(chord_score)
        completeness_samples.append(completeness_score)

        weighted = (
            rhythm_f1 * BASE_WEIGHTS["rhythmPlacement"]
            + note_score * BASE_WEIGHTS["noteFretAccuracy"]
            + chord_score * BASE_WEIGHTS["chordMultiplicity"]
            + completeness_score * BASE_WEIGHTS["completeness"]
            + technique_score * BASE_WEIGHTS["technique"]
        )

        measure_scores.append({
            "measureNumber": measure,
            "section": reference_measure.get("section"),
            "sectionVariant": reference_measure.get("sectionVariant"),
            "candidateOccupiedSteps": sorted(candidate_occupied),
            "referenceOccupiedSteps": sorted(reference_occupied),
            "sharedOccupiedSteps": sorted(shared_steps),
            "missingReferenceSteps": sorted(reference_occupied - candidate_occupied),
            "extraCandidateSteps": sorted(candidate_occupied - reference_occupied),
            "candidateNoteCount": candidate_note_count,
            "referenceNoteCount": reference_note_count,
            "scores": {
                "rhythmPlacement": percent(rhythm_f1),
                "noteFretAccuracy": percent(note_score),
                "chordMultiplicity": percent(chord_score),
                "completeness": percent(completeness_score),
                "technique": percent(technique_score),
                "overall": percent(weighted),
            },
            "professionalReferenceRole": "grading-training-label-only",
        })

    rhythm_global = f1_from_counts(total_step_tp, total_candidate_steps, total_reference_steps)
    note_tp_global = multiset_intersection_size(all_candidate_note_tokens, all_reference_note_tokens)
    note_global = f1_from_counts(
        note_tp_global,
        sum(all_candidate_note_tokens.values()),
        sum(all_reference_note_tokens.values()),
    )
    chord_global = sum(multiplicity_samples) / len(multiplicity_samples) if multiplicity_samples else 0.0
    completeness_global = sum(completeness_samples) / len(completeness_samples) if completeness_samples else 0.0
    technique_tp_global = multiset_intersection_size(all_candidate_technique_tokens, all_reference_technique_tokens)
    technique_global = f1_from_counts(
        technique_tp_global,
        sum(all_candidate_technique_tokens.values()),
        sum(all_reference_technique_tokens.values()),
    )

    overall = (
        rhythm_global * BASE_WEIGHTS["rhythmPlacement"]
        + note_global * BASE_WEIGHTS["noteFretAccuracy"]
        + chord_global * BASE_WEIGHTS["chordMultiplicity"]
        + completeness_global * BASE_WEIGHTS["completeness"]
        + technique_global * BASE_WEIGHTS["technique"]
    )

    timing_scored = comparable_duration_event_count > 0
    timing_score = (
        percent(sum(duration_samples) / len(duration_samples))
        if duration_samples
        else None
    )

    weakest = sorted(measure_scores, key=lambda row: float(row["scores"]["overall"]))[:12]
    strongest = sorted(measure_scores, key=lambda row: float(row["scores"]["overall"]), reverse=True)[:12]
    weak_priority = [int(row["measureNumber"]) for row in weakest]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    candidate_unchanged = candidate_hash_before == candidate_hash_after
    if not candidate_unchanged:
        raise RuntimeError("Protected candidate changed during professional-reference grading.")

    passed = bool(
        candidate_unchanged
        and len(measure_scores) == EXPECTED_REFERENCE_MEASURE_COUNT
        and reference.get("professionalReferenceUsedForScoringOnly") is True
    )

    output = {
        "schemaVersion": 1,
        "gradeType": "read-only-independent-rhythm-output-vs-professional-reference",
        "passed": passed,
        "candidatePath": str(CANDIDATE_PATH.relative_to(ROOT)),
        "professionalReferencePath": str(REFERENCE_PATH.relative_to(ROOT)),
        "professionalReferenceRole": "grading-training-label-only",
        "candidateFrozenBeforeProfessionalReferenceLoad": True,
        "measureRange": [MEASURE_START, MEASURE_END],
        "measuresGraded": len(measure_scores),
        "candidateProtectedEventCount": len(candidate_events),
        "domainWeights": BASE_WEIGHTS,
        "scores": {
            "overall": percent(overall),
            "rhythmPlacement": percent(rhythm_global),
            "noteFretAccuracy": percent(note_global),
            "chordMultiplicity": percent(chord_global),
            "completeness": percent(completeness_global),
            "technique": percent(technique_global),
            "timingDuration": timing_score,
        },
        "scoredDomains": [
            "rhythmPlacement",
            "noteFretAccuracy",
            "chordMultiplicity",
            "completeness",
            "technique",
        ],
        "unscoredDomains": ([] if timing_scored else ["timingDuration"]),
        "timingDurationComparableEventCount": comparable_duration_event_count,
        "weakestMeasures": weakest,
        "strongestMeasures": strongest,
        "recommendedTrainingPriorityMeasures": weak_priority,
        "measureScores": measure_scores,
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "professionalReferenceModified": False,
        "professionalReferenceCopiedIntoCandidate": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "thresholdRelaxationAllowed": False,
        "candidateHashBefore": candidate_hash_before,
        "candidateHashAfter": candidate_hash_after,
        "candidateHashUnchanged": candidate_unchanged,
        "readyForTargetedProfessionalGradeTraining": passed,
        "recommendedNextAction": (
            "train-gomyway-rhythm-from-professional-grade-priorities-v1"
            if passed
            else "diagnose-gomyway-rhythm-professional-grade-v1"
        ),
    }

    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "measuresGraded": len(measure_scores),
        "overallScore": percent(overall),
        "rhythmPlacementScore": percent(rhythm_global),
        "noteFretAccuracyScore": percent(note_global),
        "chordMultiplicityScore": percent(chord_global),
        "completenessScore": percent(completeness_global),
        "techniqueScore": percent(technique_global),
        "timingDurationScore": timing_score,
        "recommendedTrainingPriorityMeasures": weak_priority,
        "professionalReferenceRole": "grading-training-label-only",
        "candidateHashUnchanged": candidate_unchanged,
        "automaticApplyAllowed": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": output["recommendedNextAction"],
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM PROFESSIONAL GRADE V1 COMPLETE")
    print("Passed:", passed)
    print("Professional reference role: grading-training-label-only")
    print("Candidate frozen before professional reference load: True")
    print("Measures graded:", len(measure_scores))
    print("Overall rhythm transcription score:", percent(overall))
    print("Rhythm placement:", percent(rhythm_global))
    print("Note/fret accuracy:", percent(note_global))
    print("Chord multiplicity:", percent(chord_global))
    print("Completeness:", percent(completeness_global))
    print("Technique:", percent(technique_global))
    print("Timing/duration:", timing_score if timing_scored else "NOT SCORED - no comparable quantized duration data")
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
        scores = row["scores"]
        print(f"  measure={row['measureNumber']} overall={scores['overall']}")
    print("Recommended training priority measures:", weak_priority)
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
