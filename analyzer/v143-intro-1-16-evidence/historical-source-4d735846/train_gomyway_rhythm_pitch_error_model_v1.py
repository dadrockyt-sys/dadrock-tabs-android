from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
BATCH_PATH = PUBLIC / "gomyway-rhythm-pitch-first-training-batch-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pitch-error-model-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-pitch-error-model-v1-manifest.json"

EXPECTED_EVENT_COUNT = 949
EXPECTED_BATCH_SIZE = 12


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def nearest_signed_delta(target: int, candidates: list[int]) -> int | None:
    if not candidates:
        return None
    # candidate - target; tie-break toward the smaller absolute/raw delta.
    return min((candidate - target for candidate in candidates), key=lambda d: (abs(d), abs(d % 12), d))


def octave_folded_abs(delta: int) -> int:
    value = abs(delta) % 12
    return min(value, 12 - value)


def pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(100.0 * numerator / denominator, 2)


def main() -> None:
    before = sha256(CANDIDATE_PATH)
    candidate = load(CANDIDATE_PATH)
    batch = load(BATCH_PATH)

    events = candidate_rows(candidate)
    if len(events) != EXPECTED_EVENT_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_EVENT_COUNT} protected candidate events, found {len(events)}")
    if batch.get("passed") is not True or batch.get("readyForPitchErrorModelTraining") is not True:
        raise RuntimeError("Pitch-first training batch is not green")
    if batch.get("professionalReferenceRole") != "training-label-and-grading-only":
        raise RuntimeError("Professional reference role changed unexpectedly")

    training_rows = batch.get("trainingRows")
    priority_measures = batch.get("priorityMeasures")
    if not isinstance(training_rows, list) or len(training_rows) != EXPECTED_BATCH_SIZE:
        raise RuntimeError("Expected 12 training rows")
    if not isinstance(priority_measures, list) or len(priority_measures) != EXPECTED_BATCH_SIZE:
        raise RuntimeError("Expected 12 priority measures")

    signed_delta_hist: Counter[int] = Counter()
    abs_delta_hist: Counter[int] = Counter()
    octave_folded_hist: Counter[int] = Counter()
    candidate_pitch_hist: Counter[int] = Counter()
    label_pitch_hist: Counter[int] = Counter()

    nearest_deltas: list[int] = []
    steps_with_labels = 0
    steps_with_candidate = 0
    steps_with_both = 0
    exact_step_pitch_matches = 0
    label_tokens = 0
    candidate_tokens = 0
    labels_without_any_candidate_same_step = 0

    per_measure: list[dict[str, Any]] = []

    for measure_row in training_rows:
        if not isinstance(measure_row, dict):
            continue
        measure = int(measure_row.get("measureNumber"))
        steps = measure_row.get("steps")
        if not isinstance(steps, list):
            continue

        measure_deltas: list[int] = []
        measure_labels = 0
        measure_candidates = 0
        measure_steps_both = 0
        measure_label_steps = 0
        measure_candidate_steps = 0
        measure_no_candidate_for_label = 0

        for step_row in steps:
            if not isinstance(step_row, dict):
                continue
            candidate_midis = [int(x) for x in step_row.get("candidateMidi", [])]
            label_midis = [int(x) for x in step_row.get("professionalLabelMidi", [])]

            candidate_tokens += len(candidate_midis)
            label_tokens += len(label_midis)
            measure_candidates += len(candidate_midis)
            measure_labels += len(label_midis)
            candidate_pitch_hist.update(candidate_midis)
            label_pitch_hist.update(label_midis)

            if candidate_midis:
                steps_with_candidate += 1
                measure_candidate_steps += 1
            if label_midis:
                steps_with_labels += 1
                measure_label_steps += 1
            if candidate_midis and label_midis:
                steps_with_both += 1
                measure_steps_both += 1

            # Keep the already-observed exact matches explicit even though batch V1 had zero overall.
            exact_matches = len(set(candidate_midis) & set(label_midis))
            exact_step_pitch_matches += exact_matches

            for label in label_midis:
                delta = nearest_signed_delta(label, candidate_midis)
                if delta is None:
                    labels_without_any_candidate_same_step += 1
                    measure_no_candidate_for_label += 1
                    continue
                nearest_deltas.append(delta)
                measure_deltas.append(delta)
                signed_delta_hist[delta] += 1
                abs_delta_hist[abs(delta)] += 1
                octave_folded_hist[octave_folded_abs(delta)] += 1

        overproduction_ratio = round(measure_candidates / measure_labels, 3) if measure_labels else None
        per_measure.append({
            "measureNumber": measure,
            "labelPitchTokens": measure_labels,
            "candidatePitchTokens": measure_candidates,
            "candidateToLabelRatio": overproduction_ratio,
            "labelSteps": measure_label_steps,
            "candidateSteps": measure_candidate_steps,
            "stepsWithBoth": measure_steps_both,
            "labelsWithoutCandidateAtSameStep": measure_no_candidate_for_label,
            "nearestDeltaMedianSemitones": round(float(median(measure_deltas)), 2) if measure_deltas else None,
            "nearestDeltaAbsMedianSemitones": round(float(median(abs(x) for x in measure_deltas)), 2) if measure_deltas else None,
            "octaveEquivalentWithin1SemitoneCount": sum(1 for x in measure_deltas if octave_folded_abs(x) <= 1),
            "professionalReferenceRole": "training-label-and-grading-only",
        })

    overproduction_ratio = round(candidate_tokens / label_tokens, 3) if label_tokens else None
    within_1 = sum(count for delta, count in octave_folded_hist.items() if delta <= 1)
    within_2 = sum(count for delta, count in octave_folded_hist.items() if delta <= 2)
    exact_octave_equiv = octave_folded_hist.get(0, 0)

    dominant_signed = signed_delta_hist.most_common(10)
    dominant_abs = abs_delta_hist.most_common(10)
    dominant_octave_folded = octave_folded_hist.most_common(7)

    severe_overproduction = bool(overproduction_ratio is not None and overproduction_ratio >= 2.0)
    octave_or_transposition_pattern = bool(nearest_deltas and pct(exact_octave_equiv, len(nearest_deltas)) >= 40.0)
    near_pitch_pattern = bool(nearest_deltas and pct(within_1, len(nearest_deltas)) >= 50.0)

    if severe_overproduction and not near_pitch_pattern:
        primary_error_mode = "over-detection-plus-wrong-pitch"
        recommended = "calibrate-gomyway-rhythm-pitch-candidate-filtering-v1"
    elif octave_or_transposition_pattern:
        primary_error_mode = "systematic-octave-or-transposition"
        recommended = "calibrate-gomyway-rhythm-pitch-transposition-v1"
    elif near_pitch_pattern:
        primary_error_mode = "near-pitch-selection-error"
        recommended = "calibrate-gomyway-rhythm-near-pitch-selection-v1"
    else:
        primary_error_mode = "mixed-pitch-detection-error"
        recommended = "diagnose-gomyway-rhythm-pitch-detector-source-v1"

    after = sha256(CANDIDATE_PATH)
    unchanged = before == after
    passed = bool(unchanged and label_tokens > 0 and candidate_tokens > 0)

    output = {
        "schemaVersion": 1,
        "passed": passed,
        "modelType": "read-only-supervised-pitch-error-model",
        "priorityMeasures": [int(x) for x in priority_measures],
        "professionalReferenceRole": "training-label-and-grading-only",
        "summary": {
            "labelPitchTokens": label_tokens,
            "candidatePitchTokens": candidate_tokens,
            "candidateToLabelRatio": overproduction_ratio,
            "stepsWithProfessionalLabels": steps_with_labels,
            "stepsWithCandidatePitches": steps_with_candidate,
            "stepsWithBoth": steps_with_both,
            "exactStepPitchMatches": exact_step_pitch_matches,
            "labelsWithoutAnyCandidateAtSameStep": labels_without_any_candidate_same_step,
            "nearestComparableLabelTokens": len(nearest_deltas),
            "octaveEquivalentExactPercent": pct(exact_octave_equiv, len(nearest_deltas)),
            "octaveFoldedWithin1SemitonePercent": pct(within_1, len(nearest_deltas)),
            "octaveFoldedWithin2SemitonePercent": pct(within_2, len(nearest_deltas)),
        },
        "dominantSignedSemitoneDeltas": [{"delta": d, "count": c} for d, c in dominant_signed],
        "dominantAbsoluteSemitoneDeltas": [{"delta": d, "count": c} for d, c in dominant_abs],
        "dominantOctaveFoldedDistances": [{"distance": d, "count": c} for d, c in dominant_octave_folded],
        "candidatePitchHistogram": dict(sorted(candidate_pitch_hist.items())),
        "professionalLabelPitchHistogram": dict(sorted(label_pitch_hist.items())),
        "perMeasure": per_measure,
        "severeOverproductionDetected": severe_overproduction,
        "systematicOctaveOrTranspositionPatternDetected": octave_or_transposition_pattern,
        "nearPitchPatternDetected": near_pitch_pattern,
        "primaryErrorMode": primary_error_mode,
        "candidateHashBefore": before,
        "candidateHashAfter": after,
        "candidateHashUnchanged": unchanged,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "professionalReferenceCopiedIntoProtectedCandidate": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "automaticApplyAllowed": False,
        "productionPromotionAllowed": False,
        "readyForPitchDetectorCalibration": passed,
        "recommendedNextAction": recommended if passed else "diagnose-gomyway-rhythm-pitch-error-model-v1",
    }

    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "primaryErrorMode": primary_error_mode,
        "candidateToLabelRatio": overproduction_ratio,
        "octaveFoldedWithin1SemitonePercent": pct(within_1, len(nearest_deltas)),
        "candidateHashUnchanged": unchanged,
        "productionPromotionAllowed": False,
        "recommendedNextAction": output["recommendedNextAction"],
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM PITCH ERROR MODEL V1 COMPLETE")
    print("Passed:", passed)
    print("Priority measures:", [int(x) for x in priority_measures])
    print("Professional label pitch tokens:", label_tokens)
    print("Candidate pitch tokens:", candidate_tokens)
    print("Candidate / label ratio:", overproduction_ratio)
    print("Steps with professional labels:", steps_with_labels)
    print("Steps with candidate pitches:", steps_with_candidate)
    print("Steps with both:", steps_with_both)
    print("Exact same-step pitch matches:", exact_step_pitch_matches)
    print("Labels with no candidate at same step:", labels_without_any_candidate_same_step)
    print("Comparable nearest-pitch labels:", len(nearest_deltas))
    print("Octave-equivalent exact percent:", pct(exact_octave_equiv, len(nearest_deltas)))
    print("Octave-folded within 1 semitone percent:", pct(within_1, len(nearest_deltas)))
    print("Octave-folded within 2 semitones percent:", pct(within_2, len(nearest_deltas)))
    print("Dominant signed semitone deltas:", dominant_signed)
    print("Dominant octave-folded distances:", dominant_octave_folded)
    print("Severe overproduction detected:", severe_overproduction)
    print("Systematic octave/transposition pattern detected:", octave_or_transposition_pattern)
    print("Near-pitch pattern detected:", near_pitch_pattern)
    print("Primary error mode:", primary_error_mode)
    print("Candidate hash unchanged:", unchanged)
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for pitch detector calibration:", passed)
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
