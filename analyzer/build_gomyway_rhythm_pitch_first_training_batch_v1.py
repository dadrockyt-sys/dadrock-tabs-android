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
PLAN_PATH = PUBLIC / "gomyway-rhythm-professional-grade-training-plan-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pitch-first-training-batch-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-pitch-first-training-batch-v1-manifest.json"
EXPECTED_EVENT_COUNT = 949
STANDARD_GUITAR_OPEN_MIDI = {1: 64, 2: 59, 3: 55, 4: 50, 5: 45, 6: 40}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected object: {path}")
    return value


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


def notes_of(event: dict[str, Any]) -> list[dict[str, Any]]:
    value = event.get("notes")
    if isinstance(value, list):
        return [note for note in value if isinstance(note, dict)]
    return []


def string_of(note: dict[str, Any]) -> int | None:
    return integer(note.get("string", note.get("stringIndex")))


def fret_of(note: dict[str, Any]) -> int | None:
    return integer(note.get("fret"))


def midi_of(note: dict[str, Any]) -> int | None:
    value = integer(note.get("midi", note.get("midiPitch")))
    if value is not None:
        return value
    string = string_of(note)
    fret = fret_of(note)
    if string in STANDARD_GUITAR_OPEN_MIDI and fret is not None:
        return STANDARD_GUITAR_OPEN_MIDI[string] + fret
    return None


def main() -> None:
    before = sha256(CANDIDATE_PATH)
    candidate = load(CANDIDATE_PATH)
    reference = load(REFERENCE_PATH)
    plan = load(PLAN_PATH)
    events = rows(candidate)
    if len(events) != EXPECTED_EVENT_COUNT:
        raise RuntimeError(f"Protected candidate count changed: {len(events)}")
    if plan.get("passed") is not True or plan.get("readyForPitchFirstTrainingBatch") is not True:
        raise RuntimeError("Pitch-first plan is not green")
    if plan.get("primarySystemBottleneck") != "pitch-detection":
        raise RuntimeError("Primary bottleneck changed unexpectedly")
    if reference.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference must remain scoring/training-label only")

    batch_measures = plan.get("priorityBatchMeasures")
    if not isinstance(batch_measures, list) or len(batch_measures) != 12:
        raise RuntimeError("Expected 12 pitch-first priority measures")
    batch_measures = [int(x) for x in batch_measures]

    candidate_steps: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for event in events:
        measure = measure_of(event)
        step = step_of(event)
        if measure in batch_measures and step is not None:
            candidate_steps[measure][step].append(event)

    ref_by_measure = {
        int(row["measureNumber"]): row
        for row in reference.get("measures", [])
        if isinstance(row, dict) and "measureNumber" in row
    }

    training_rows: list[dict[str, Any]] = []
    total_missing = 0
    total_extra = 0
    total_matched = 0

    for measure in batch_measures:
        ref_measure = ref_by_measure.get(measure)
        if not isinstance(ref_measure, dict):
            raise RuntimeError(f"Missing professional measure {measure}")
        ref_steps: dict[int, dict[str, Any]] = {}
        for event in ref_measure.get("events", []):
            if isinstance(event, dict):
                step = integer(event.get("quantizedStep"))
                if step is not None:
                    ref_steps[step] = event

        step_rows: list[dict[str, Any]] = []
        for step in sorted(set(candidate_steps.get(measure, {})) | set(ref_steps)):
            cand_midis: Counter[int] = Counter()
            ref_midis: Counter[int] = Counter()
            cand_tabs: list[dict[str, int]] = []
            ref_tabs: list[dict[str, int]] = []

            for event in candidate_steps.get(measure, {}).get(step, []):
                for note in notes_of(event):
                    midi = midi_of(note)
                    string = string_of(note)
                    fret = fret_of(note)
                    if midi is not None:
                        cand_midis[midi] += 1
                    if string is not None and fret is not None:
                        cand_tabs.append({"string": string, "fret": fret})

            ref_event = ref_steps.get(step)
            if isinstance(ref_event, dict):
                for note in notes_of(ref_event):
                    midi = midi_of(note)
                    string = string_of(note)
                    fret = fret_of(note)
                    if midi is not None:
                        ref_midis[midi] += 1
                    if string is not None and fret is not None:
                        ref_tabs.append({"string": string, "fret": fret})

            matched = cand_midis & ref_midis
            missing = ref_midis - cand_midis
            extra = cand_midis - ref_midis
            matched_count = sum(matched.values())
            missing_count = sum(missing.values())
            extra_count = sum(extra.values())
            total_matched += matched_count
            total_missing += missing_count
            total_extra += extra_count

            step_rows.append({
                "quantizedStep": step,
                "candidateMidi": sorted(cand_midis.elements()),
                "professionalLabelMidi": sorted(ref_midis.elements()),
                "matchedMidi": sorted(matched.elements()),
                "missingProfessionalMidi": sorted(missing.elements()),
                "extraCandidateMidi": sorted(extra.elements()),
                "candidateTab": cand_tabs,
                "professionalLabelTab": ref_tabs,
                "professionalReferenceRole": "training-label-and-grading-only",
            })

        training_rows.append({
            "measureNumber": measure,
            "section": ref_measure.get("section"),
            "sectionVariant": ref_measure.get("sectionVariant"),
            "steps": step_rows,
            "professionalReferenceCopiedIntoProtectedCandidate": False,
        })

    after = sha256(CANDIDATE_PATH)
    unchanged = before == after
    passed = bool(unchanged and len(training_rows) == 12)
    recommended = "train-gomyway-rhythm-pitch-error-model-v1" if passed else "diagnose-gomyway-rhythm-pitch-first-training-batch-v1"

    output = {
        "schemaVersion": 1,
        "passed": passed,
        "trainingBatchType": "read-only-pitch-first-supervised-error-labels",
        "priorityMeasures": batch_measures,
        "measureCount": len(training_rows),
        "primaryTrainingDomain": "pitch-detection",
        "professionalReferenceRole": "training-label-and-grading-only",
        "summary": {
            "matchedPitchTokens": total_matched,
            "missingProfessionalPitchTokens": total_missing,
            "extraCandidatePitchTokens": total_extra,
        },
        "trainingRows": training_rows,
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
        "readyForPitchErrorModelTraining": passed,
        "recommendedNextAction": recommended,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "priorityMeasures": batch_measures,
        "matchedPitchTokens": total_matched,
        "missingProfessionalPitchTokens": total_missing,
        "extraCandidatePitchTokens": total_extra,
        "candidateHashUnchanged": unchanged,
        "productionPromotionAllowed": False,
        "recommendedNextAction": recommended,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM PITCH-FIRST TRAINING BATCH V1 COMPLETE")
    print("Passed:", passed)
    print("Priority measures:", batch_measures)
    print("Primary training domain: pitch-detection")
    print("Matched pitch tokens:", total_matched)
    print("Missing professional pitch tokens:", total_missing)
    print("Extra candidate pitch tokens:", total_extra)
    for row in training_rows:
        missing = sum(len(step["missingProfessionalMidi"]) for step in row["steps"])
        extra = sum(len(step["extraCandidateMidi"]) for step in row["steps"])
        matched = sum(len(step["matchedMidi"]) for step in row["steps"])
        print(f"measure={row['measureNumber']} matched={matched} missing={missing} extra={extra}")
    print("Professional reference role: training-label-and-grading-only")
    print("Candidate hash unchanged:", unchanged)
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for pitch error-model training:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
