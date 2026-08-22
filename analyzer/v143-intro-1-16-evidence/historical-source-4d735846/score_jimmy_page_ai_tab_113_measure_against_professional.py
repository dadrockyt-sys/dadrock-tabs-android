import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

CANDIDATE_PATH = PUBLIC / "gomyway-ai-tab-113-measure-shadow-transcription.json"
INTRO_REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-v2.json"
HUMAN_ANNOTATIONS_PATH = PUBLIC / "gomyway-jimmy-paige-professional-value-human-annotations.json"
OUTPUT_PATH = PUBLIC / "gomyway-ai-tab-113-measure-professional-score.json"

EXPECTED_MEASURES = 113
REQUIRED_SCORE = 90.0
CRITICAL_SECTION_MINIMUM = 85.0

SECTION_PLAN = [
    ("Intro", 1, 16, False),
    ("Verse 1", 17, 32, False),
    ("Chorus 1", 33, 38, True),
    ("Riff 1", 39, 46, False),
    ("Verse 2", 47, 62, False),
    ("Chorus 2", 63, 69, True),
    ("Bridge", 70, 77, False),
    ("Solo Backing", 78, 94, False),
    ("Return Riff and Out-Chorus", 95, 113, True),
]

WEIGHTS = {
    "pitchStringFret": 40.0,
    "attackTiming": 25.0,
    "durationRhythm": 15.0,
    "technique": 15.0,
    "measureStructure": 5.0,
}


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def measure_number(row: dict[str, Any], index: int) -> int:
    for key in ("measureNumber", "measure", "barNumber", "bar"):
        value = row.get(key)
        if isinstance(value, int) and 1 <= value <= EXPECTED_MEASURES:
            return value
    return index + 1


def measure_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        for key in ("measures", "annotations", "measureRows", "transcription"):
            value = payload.get(key)
            if isinstance(value, list) and all(isinstance(row, dict) for row in value):
                return value
    return []


def event_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "notes", "noteEvents", "attacks"):
        value = row.get(key)
        if isinstance(value, list):
            return [event for event in value if isinstance(event, dict)]
    return []


def first_number(payload: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


def first_text(payload: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return None


def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "midi": first_number(event, ("midiPitch", "midi", "pitch")),
        "string": first_number(event, ("stringIndex", "string", "stringNumber")),
        "fret": first_number(event, ("fret", "fretNumber")),
        "timing": first_number(
            event,
            (
                "positionInMeasure",
                "normalizedPosition",
                "beatPosition",
                "startStep",
                "start_time",
                "start",
                "onset",
            ),
        ),
        "duration": first_number(
            event,
            ("durationSteps", "duration", "length", "sustainSteps"),
        ),
        "technique": first_text(
            event,
            ("technique", "techniqueFamily", "articulation", "notation"),
        ),
    }


def closeness(a: float | None, b: float | None, tolerance: float) -> float:
    if a is None or b is None:
        return 0.0
    difference = abs(a - b)
    if difference <= tolerance:
        return 1.0
    if difference >= tolerance * 4:
        return 0.0
    return max(0.0, 1.0 - ((difference - tolerance) / (tolerance * 3)))


def pitch_score(reference: dict[str, Any], candidate: dict[str, Any]) -> float:
    midi = closeness(reference["midi"], candidate["midi"], 0.0)
    string = closeness(reference["string"], candidate["string"], 0.0)
    fret = closeness(reference["fret"], candidate["fret"], 0.0)
    if reference["midi"] is not None and candidate["midi"] is not None:
        return midi
    if reference["string"] is not None and reference["fret"] is not None:
        return (string + fret) / 2.0
    return max(midi, string, fret)


def technique_score(reference: dict[str, Any], candidate: dict[str, Any]) -> float:
    ref = reference["technique"]
    cand = candidate["technique"]
    if ref is None:
        return 1.0 if cand is None else 0.75
    if cand is None:
        return 0.0
    return 1.0 if ref == cand else 0.0


def event_similarity(reference: dict[str, Any], candidate: dict[str, Any]) -> dict[str, float]:
    return {
        "pitchStringFret": pitch_score(reference, candidate),
        "attackTiming": closeness(reference["timing"], candidate["timing"], 0.04),
        "durationRhythm": closeness(reference["duration"], candidate["duration"], 0.25),
        "technique": technique_score(reference, candidate),
    }


def weighted_event_similarity(scores: dict[str, float]) -> float:
    event_weight = sum(WEIGHTS[key] for key in scores)
    return sum(scores[key] * WEIGHTS[key] for key in scores) / event_weight


def score_measure(reference_events: list[dict[str, Any]], candidate_events: list[dict[str, Any]]) -> dict[str, float]:
    normalized_reference = [normalize_event(event) for event in reference_events]
    normalized_candidate = [normalize_event(event) for event in candidate_events]

    component_totals = {key: 0.0 for key in WEIGHTS if key != "measureStructure"}
    if not normalized_reference:
        structure = 1.0 if not normalized_candidate else 0.5
        return {**component_totals, "measureStructure": structure}

    unused = set(range(len(normalized_candidate)))
    matched = 0
    for reference in normalized_reference:
        best_index = None
        best_scores = None
        best_weighted = -1.0
        for index in unused:
            scores = event_similarity(reference, normalized_candidate[index])
            weighted = weighted_event_similarity(scores)
            if weighted > best_weighted:
                best_index = index
                best_scores = scores
                best_weighted = weighted
        if best_index is not None and best_scores is not None:
            unused.remove(best_index)
            matched += 1
            for key, value in best_scores.items():
                component_totals[key] += value

    denominator = max(len(normalized_reference), len(normalized_candidate), 1)
    component_scores = {
        key: component_totals[key] / denominator for key in component_totals
    }
    component_scores["measureStructure"] = matched / denominator
    return component_scores


def build_measure_map(payload: Any) -> dict[int, list[dict[str, Any]]]:
    result: dict[int, list[dict[str, Any]]] = {}
    for index, row in enumerate(measure_rows(payload)):
        number = measure_number(row, index)
        if 1 <= number <= EXPECTED_MEASURES:
            result[number] = event_rows(row)
    return result


def merge_reference_maps() -> tuple[dict[int, list[dict[str, Any]]], list[str]]:
    merged: dict[int, list[dict[str, Any]]] = {}
    sources: list[str] = []

    if INTRO_REFERENCE_PATH.exists():
        merged.update(build_measure_map(load_json(INTRO_REFERENCE_PATH)))
        sources.append(str(INTRO_REFERENCE_PATH.relative_to(ROOT)))

    if HUMAN_ANNOTATIONS_PATH.exists():
        human_map = build_measure_map(load_json(HUMAN_ANNOTATIONS_PATH))
        for measure, events in human_map.items():
            if events:
                merged[measure] = events
        sources.append(str(HUMAN_ANNOTATIONS_PATH.relative_to(ROOT)))

    return merged, sources


def aggregate(measure_scores: dict[int, dict[str, float]], measures: list[int]) -> dict[str, Any]:
    available = [measure for measure in measures if measure in measure_scores]
    if not available:
        return {
            "measureCount": 0,
            "componentScores": {key: None for key in WEIGHTS},
            "overallScore": None,
        }

    components = {
        key: sum(measure_scores[measure][key] for measure in available) / len(available)
        for key in WEIGHTS
    }
    overall = sum(components[key] * WEIGHTS[key] for key in WEIGHTS) / sum(WEIGHTS.values())
    return {
        "measureCount": len(available),
        "componentScores": {key: round(value * 100.0, 2) for key, value in components.items()},
        "overallScore": round(overall * 100.0, 2),
    }


def main() -> None:
    candidate_payload = load_json(CANDIDATE_PATH)
    candidate_map = build_measure_map(candidate_payload)
    reference_map, reference_sources = merge_reference_maps()

    reference_coverage = sorted(reference_map)
    candidate_coverage = sorted(candidate_map)
    full_reference_coverage = reference_coverage == list(range(1, EXPECTED_MEASURES + 1))
    full_candidate_coverage = candidate_coverage == list(range(1, EXPECTED_MEASURES + 1))

    measure_scores = {
        measure: score_measure(reference_map[measure], candidate_map.get(measure, []))
        for measure in reference_coverage
    }

    verified_scope = aggregate(measure_scores, reference_coverage)
    section_rows = []
    critical_sections_passed = True
    for name, start, end, critical in SECTION_PLAN:
        section = aggregate(measure_scores, list(range(start, end + 1)))
        section_score = section["overallScore"]
        section_passed = (
            section_score is not None
            and (not critical or section_score >= CRITICAL_SECTION_MINIMUM)
        )
        if critical and not section_passed:
            critical_sections_passed = False
        section_rows.append(
            {
                "name": name,
                "startMeasure": start,
                "endMeasure": end,
                "critical": critical,
                **section,
                "minimumRequired": CRITICAL_SECTION_MINIMUM if critical else None,
                "passed": section_passed,
            }
        )

    overall_score = verified_scope["overallScore"] if full_reference_coverage else None
    score_gate_passed = bool(
        full_candidate_coverage
        and full_reference_coverage
        and overall_score is not None
        and overall_score >= REQUIRED_SCORE
        and critical_sections_passed
    )

    blockers = []
    if not full_candidate_coverage:
        blockers.append(f"candidate coverage is {len(candidate_coverage)}/113")
    if not full_reference_coverage:
        blockers.append(f"professional note-value coverage is {len(reference_coverage)}/113")
    if full_reference_coverage and overall_score is not None and overall_score < REQUIRED_SCORE:
        blockers.append(f"overall score {overall_score}% is below {REQUIRED_SCORE}%")
    if full_reference_coverage and not critical_sections_passed:
        blockers.append("one or more critical sections are below the minimum")

    output = {
        "gateName": "Jimmy Page strict professional 90 percent comparison",
        "requiredOverallScore": REQUIRED_SCORE,
        "criticalSectionMinimum": CRITICAL_SECTION_MINIMUM,
        "weights": WEIGHTS,
        "referenceSources": reference_sources,
        "candidateMeasureCoverage": len(candidate_coverage),
        "professionalNoteValueCoverage": len(reference_coverage),
        "fullCandidateCoveragePassed": full_candidate_coverage,
        "fullProfessionalReferenceCoveragePassed": full_reference_coverage,
        "verifiedScopeScore": verified_scope,
        "overallScore": overall_score,
        "sections": section_rows,
        "criticalSectionsPassed": critical_sections_passed,
        "scoreGatePassed": score_gate_passed,
        "blockers": blockers,
        "professionalPdfRemainsScoringAuthority": True,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "readyForProduction": False,
    }
    write_json(OUTPUT_PATH, output)

    print("Jimmy Page strict professional comparison complete")
    print(f"Candidate measure coverage: {len(candidate_coverage)}/113")
    print(f"Professional note-value coverage: {len(reference_coverage)}/113")
    print(f"Verified-scope score: {verified_scope['overallScore']}")
    print(f"Full-song overall score: {overall_score}")
    print(f"Required score: {REQUIRED_SCORE}")
    print(f"Critical sections passed: {critical_sections_passed}")
    print(f"Strict 90 percent score gate passed: {score_gate_passed}")
    print(f"Blockers: {blockers}")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not score_gate_passed:
        raise RuntimeError("Strict professional 90 percent score gate did not pass")


if __name__ == "__main__":
    main()
