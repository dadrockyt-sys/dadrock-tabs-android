from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
GRADE_PATH = PUBLIC / "gomyway-rhythm-professional-grade-v2.json"
PITCH_DIAG_PATH = PUBLIC / "gomyway-rhythm-professional-pitch-vs-tab-diagnostic-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-professional-grade-training-plan-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-professional-grade-training-plan-v2-manifest.json"

EXPECTED_EVENT_COUNT = 949
TOP_BATCH_SIZE = 12


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def main() -> None:
    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = load(CANDIDATE_PATH)
    grade = load(GRADE_PATH)
    pitch_diag = load(PITCH_DIAG_PATH)
    reference = load(REFERENCE_PATH)

    events = None
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        value = candidate.get(key)
        if isinstance(value, list):
            events = value
            break
    if not isinstance(events, list) or len(events) != EXPECTED_EVENT_COUNT:
        raise RuntimeError("Protected candidate event count changed unexpectedly.")
    if grade.get("passed") is not True:
        raise RuntimeError("Professional grade V2 is not green.")
    if pitch_diag.get("passed") is not True:
        raise RuntimeError("Pitch-vs-tab diagnostic V1 is not green.")
    if reference.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not scoring-only.")
    if pitch_diag.get("alternateStringPositionIssueLikely") is not False:
        raise RuntimeError("Pitch-first training is unsafe while alternate-position issue is unresolved.")

    grade_rows = grade.get("measureScores")
    pitch_rows = pitch_diag.get("measureScores")
    if not isinstance(grade_rows, list) or not isinstance(pitch_rows, list):
        raise RuntimeError("Required per-measure score rows are missing.")

    grade_by_measure = {
        int(row["measureNumber"]): row
        for row in grade_rows
        if isinstance(row, dict) and "measureNumber" in row
    }
    pitch_by_measure = {
        int(row["measureNumber"]): row
        for row in pitch_rows
        if isinstance(row, dict) and "measureNumber" in row
    }

    ranked: list[dict[str, Any]] = []
    for measure in sorted(set(grade_by_measure) & set(pitch_by_measure)):
        grade_row = grade_by_measure[measure]
        pitch_row = pitch_by_measure[measure]
        scores = grade_row.get("scores") if isinstance(grade_row.get("scores"), dict) else {}

        rhythm = as_float(scores.get("rhythmPlacement"))
        note_tab = as_float(scores.get("noteFretAccuracy"))
        chord = as_float(scores.get("chordMultiplicity"))
        completeness = as_float(scores.get("completeness"))
        technique = as_float(scores.get("technique"))
        overall = as_float(scores.get("overall"))
        pitch = as_float(pitch_row.get("pitchF1"))
        exact_tab = as_float(pitch_row.get("exactTabF1"))

        # Pitch is the primary bottleneck proven by the pitch-vs-tab diagnostic.
        priority_score = (
            (100.0 - pitch) * 0.45
            + (100.0 - rhythm) * 0.20
            + (100.0 - completeness) * 0.15
            + (100.0 - chord) * 0.10
            + (100.0 - technique) * 0.05
            + (100.0 - overall) * 0.05
        )

        if pitch < 25.0:
            primary = "pitch-detection"
        elif rhythm < 50.0:
            primary = "rhythm-placement"
        elif completeness < 60.0:
            primary = "event-completeness"
        elif chord < 60.0:
            primary = "chord-multiplicity"
        elif technique < 50.0:
            primary = "technique"
        else:
            primary = "mixed-refinement"

        ranked.append({
            "measureNumber": measure,
            "priorityScore": round(priority_score, 3),
            "primaryTrainingDomain": primary,
            "scores": {
                "pitchF1": pitch,
                "exactTabF1": exact_tab,
                "rhythmPlacement": rhythm,
                "chordMultiplicity": chord,
                "completeness": completeness,
                "technique": technique,
                "overall": overall,
            },
            "professionalReferenceRole": "training-label-and-grading-only",
            "candidateMutationAllowed": False,
        })

    ranked.sort(key=lambda row: float(row["priorityScore"]), reverse=True)
    batch = ranked[:TOP_BATCH_SIZE]
    batch_measures = [int(row["measureNumber"]) for row in batch]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    unchanged = candidate_hash_before == candidate_hash_after
    passed = bool(unchanged and len(batch) == TOP_BATCH_SIZE)

    output = {
        "schemaVersion": 2,
        "trainingPlanType": "read-only-professional-grade-pitch-first-priority-plan",
        "passed": passed,
        "professionalReferenceRole": "training-label-and-grading-only",
        "globalPitchF1": pitch_diag.get("globalPitchF1"),
        "globalExactTabF1": pitch_diag.get("globalExactTabF1"),
        "alternateStringPositionIssueLikely": pitch_diag.get("alternateStringPositionIssueLikely"),
        "primarySystemBottleneck": "pitch-detection",
        "priorityBatchMeasures": batch_measures,
        "priorityBatch": batch,
        "allRankedMeasures": ranked,
        "trainingPolicy": {
            "useProfessionalReferenceToGenerateProductionEvents": False,
            "useProfessionalReferenceAsTrainingLabels": True,
            "mutateProtectedCandidate": False,
            "mutateV7": False,
            "mutateRenderer": False,
            "automaticApplyAllowed": False,
            "thresholdRelaxationAllowed": False,
        },
        "candidateHashBefore": candidate_hash_before,
        "candidateHashAfter": candidate_hash_after,
        "candidateHashUnchanged": unchanged,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "readyForPitchFirstTrainingBatch": passed,
        "recommendedNextAction": (
            "build-gomyway-rhythm-pitch-first-training-batch-v1"
            if passed
            else "diagnose-gomyway-rhythm-professional-grade-training-plan-v2"
        ),
    }

    manifest = {
        "schemaVersion": 2,
        "passed": passed,
        "primarySystemBottleneck": "pitch-detection",
        "priorityBatchMeasures": batch_measures,
        "candidateHashUnchanged": unchanged,
        "automaticApplyAllowed": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": output["recommendedNextAction"],
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM PROFESSIONAL-GRADE TRAINING PLAN V2 COMPLETE")
    print("Passed:", passed)
    print("Global pitch F1:", pitch_diag.get("globalPitchF1"))
    print("Global exact-tab F1:", pitch_diag.get("globalExactTabF1"))
    print("Alternate string-position issue likely:", pitch_diag.get("alternateStringPositionIssueLikely"))
    print("Primary system bottleneck: pitch-detection")
    print("Priority training batch:", batch_measures)
    for row in batch:
        scores = row["scores"]
        print(
            f"measure={row['measureNumber']} priority={row['priorityScore']} "
            f"domain={row['primaryTrainingDomain']} pitch={scores['pitchF1']} "
            f"rhythm={scores['rhythmPlacement']} completeness={scores['completeness']} "
            f"chords={scores['chordMultiplicity']} technique={scores['technique']}"
        )
    print("Professional reference role: training-label-and-grading-only")
    print("Candidate hash unchanged:", unchanged)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for pitch-first training batch:", passed)
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
