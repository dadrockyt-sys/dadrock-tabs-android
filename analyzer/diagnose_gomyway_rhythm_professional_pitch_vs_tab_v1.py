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
GRADE_V2_PATH = PUBLIC / "gomyway-rhythm-professional-grade-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-professional-pitch-vs-tab-diagnostic-v1.json"

EXPECTED_EVENT_COUNT = 949
MEASURE_START = 17
MEASURE_END = 113
STANDARD_GUITAR_OPEN_MIDI = {
    1: 64,  # high E
    2: 59,  # B
    3: 55,  # G
    4: 50,  # D
    5: 45,  # A
    6: 40,  # low E
}


def load(path: Path) -> dict[str, Any]:
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


def candidate_notes(event: dict[str, Any]) -> list[dict[str, Any]]:
    nested = event.get("notes")
    if isinstance(nested, list):
        usable = [note for note in nested if isinstance(note, dict)]
        if usable:
            return usable
    if any(key in event for key in ("string", "stringIndex", "fret", "midi", "midiPitch")):
        return [event]
    return []


def string_of(note: dict[str, Any]) -> int | None:
    for key in ("string", "stringIndex"):
        value = integer(note.get(key))
        if value is not None:
            return value
    return None


def fret_of(note: dict[str, Any]) -> int | None:
    return integer(note.get("fret"))


def candidate_midi(note: dict[str, Any]) -> int | None:
    for key in ("midi", "midiPitch"):
        value = integer(note.get(key))
        if value is not None:
            return value
    string = string_of(note)
    fret = fret_of(note)
    if string in STANDARD_GUITAR_OPEN_MIDI and fret is not None:
        return STANDARD_GUITAR_OPEN_MIDI[string] + fret
    return None


def reference_midi(note: dict[str, Any]) -> int | None:
    string = string_of(note)
    fret = fret_of(note)
    if string in STANDARD_GUITAR_OPEN_MIDI and fret is not None:
        return STANDARD_GUITAR_OPEN_MIDI[string] + fret
    return None


def f1(tp: int, predicted: int, expected: int) -> float:
    if predicted == 0 and expected == 0:
        return 1.0
    if tp <= 0 or predicted <= 0 or expected <= 0:
        return 0.0
    precision = tp / predicted
    recall = tp / expected
    return 2.0 * precision * recall / (precision + recall)


def pct(value: float) -> float:
    return round(value * 100.0, 2)


def intersection(a: Counter[Any], b: Counter[Any]) -> int:
    return sum((a & b).values())


def main() -> None:
    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = load(CANDIDATE_PATH)
    reference = load(REFERENCE_PATH)
    grade_v2 = load(GRADE_V2_PATH)

    events = rows(candidate)
    if len(events) != EXPECTED_EVENT_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_EVENT_COUNT} candidate events, found {len(events)}")
    if reference.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    if grade_v2.get("passed") is not True:
        raise RuntimeError("Professional grade V2 is not green")

    ref_measures = reference.get("measures")
    if not isinstance(ref_measures, list):
        raise RuntimeError("Professional reference measures missing")
    ref_by_measure = {
        integer(row.get("measureNumber")): row
        for row in ref_measures
        if isinstance(row, dict) and integer(row.get("measureNumber")) is not None
    }

    candidate_by_measure_step: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for event in events:
        measure = measure_of(event)
        step = step_of(event)
        if measure is None or step is None or not MEASURE_START <= measure <= MEASURE_END:
            continue
        candidate_by_measure_step[measure][step].append(event)

    global_candidate_pitch: Counter[tuple[int, int, int]] = Counter()
    global_reference_pitch: Counter[tuple[int, int, int]] = Counter()
    global_candidate_tab: Counter[tuple[int, int, int, int]] = Counter()
    global_reference_tab: Counter[tuple[int, int, int, int]] = Counter()

    per_measure: list[dict[str, Any]] = []
    missing_candidate_midi = 0
    reference_notes_seen = 0
    candidate_notes_seen = 0

    for measure in range(MEASURE_START, MEASURE_END + 1):
        ref_measure = ref_by_measure.get(measure)
        if not isinstance(ref_measure, dict):
            continue
        ref_events = ref_measure.get("events")
        if not isinstance(ref_events, list):
            continue

        cand_pitch: Counter[tuple[int, int]] = Counter()
        ref_pitch: Counter[tuple[int, int]] = Counter()
        cand_tab: Counter[tuple[int, int, int]] = Counter()
        ref_tab: Counter[tuple[int, int, int]] = Counter()

        for step, step_events in candidate_by_measure_step.get(measure, {}).items():
            for event in step_events:
                for note in candidate_notes(event):
                    candidate_notes_seen += 1
                    midi = candidate_midi(note)
                    string = string_of(note)
                    fret = fret_of(note)
                    if midi is None:
                        missing_candidate_midi += 1
                    else:
                        cand_pitch[(step, midi)] += 1
                        global_candidate_pitch[(measure, step, midi)] += 1
                    if string is not None and fret is not None:
                        cand_tab[(step, string, fret)] += 1
                        global_candidate_tab[(measure, step, string, fret)] += 1

        for event in ref_events:
            if not isinstance(event, dict):
                continue
            step = integer(event.get("quantizedStep"))
            notes = event.get("notes")
            if step is None or not isinstance(notes, list):
                continue
            for note in notes:
                if not isinstance(note, dict):
                    continue
                reference_notes_seen += 1
                midi = reference_midi(note)
                string = string_of(note)
                fret = fret_of(note)
                if midi is not None:
                    ref_pitch[(step, midi)] += 1
                    global_reference_pitch[(measure, step, midi)] += 1
                if string is not None and fret is not None:
                    ref_tab[(step, string, fret)] += 1
                    global_reference_tab[(measure, step, string, fret)] += 1

        pitch_tp = intersection(cand_pitch, ref_pitch)
        tab_tp = intersection(cand_tab, ref_tab)
        pitch_f1 = f1(pitch_tp, sum(cand_pitch.values()), sum(ref_pitch.values()))
        tab_f1 = f1(tab_tp, sum(cand_tab.values()), sum(ref_tab.values()))
        per_measure.append({
            "measureNumber": measure,
            "pitchF1": pct(pitch_f1),
            "exactTabF1": pct(tab_f1),
            "pitchMinusTab": round(pct(pitch_f1) - pct(tab_f1), 2),
            "candidatePitchTokenCount": sum(cand_pitch.values()),
            "referencePitchTokenCount": sum(ref_pitch.values()),
            "candidateTabTokenCount": sum(cand_tab.values()),
            "referenceTabTokenCount": sum(ref_tab.values()),
        })

    pitch_tp_global = intersection(global_candidate_pitch, global_reference_pitch)
    tab_tp_global = intersection(global_candidate_tab, global_reference_tab)
    pitch_global = f1(pitch_tp_global, sum(global_candidate_pitch.values()), sum(global_reference_pitch.values()))
    tab_global = f1(tab_tp_global, sum(global_candidate_tab.values()), sum(global_reference_tab.values()))

    pitch_advantage = pct(pitch_global) - pct(tab_global)
    alternate_position_issue = pitch_advantage >= 5.0

    biggest_position_gaps = sorted(
        per_measure,
        key=lambda row: float(row["pitchMinusTab"]),
        reverse=True,
    )[:12]
    weakest_pitch = sorted(per_measure, key=lambda row: float(row["pitchF1"]))[:12]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    unchanged = candidate_hash_before == candidate_hash_after
    passed = bool(unchanged and candidate_notes_seen > 0 and reference_notes_seen > 0)

    recommended = (
        "separate-pitch-detection-training-from-tab-position-training-v1"
        if alternate_position_issue
        else "train-gomyway-rhythm-from-professional-grade-priorities-v2"
    )

    output = {
        "schemaVersion": 1,
        "passed": passed,
        "diagnosticType": "professional-reference-pitch-vs-exact-tab-read-only",
        "professionalReferenceRole": "grading-training-label-only",
        "candidateNoteCount": candidate_notes_seen,
        "referenceNoteCount": reference_notes_seen,
        "candidateNotesMissingMidiOrDerivablePitch": missing_candidate_midi,
        "globalPitchF1": pct(pitch_global),
        "globalExactTabF1": pct(tab_global),
        "pitchMinusTab": round(pitch_advantage, 2),
        "alternateStringPositionIssueLikely": alternate_position_issue,
        "biggestPitchVsTabGaps": biggest_position_gaps,
        "weakestPitchMeasures": weakest_pitch,
        "measureScores": per_measure,
        "candidateHashUnchanged": unchanged,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "automaticApplyAllowed": False,
        "recommendedNextAction": recommended,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM PROFESSIONAL PITCH VS TAB DIAGNOSTIC V1 COMPLETE")
    print("Passed:", passed)
    print("Candidate notes seen:", candidate_notes_seen)
    print("Reference notes seen:", reference_notes_seen)
    print("Candidate notes missing MIDI/derivable pitch:", missing_candidate_midi)
    print("Global pitch F1:", pct(pitch_global))
    print("Global exact-tab F1:", pct(tab_global))
    print("Pitch minus exact-tab:", round(pitch_advantage, 2))
    print("Alternate string-position issue likely:", alternate_position_issue)
    print("Biggest pitch-vs-tab gaps:")
    for row in biggest_position_gaps:
        print(
            f"  measure={row['measureNumber']} pitch={row['pitchF1']} "
            f"tab={row['exactTabF1']} gap={row['pitchMinusTab']}"
        )
    print("Weakest pitch measures:", [row["measureNumber"] for row in weakest_pitch])
    print("Candidate hash unchanged:", unchanged)
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
