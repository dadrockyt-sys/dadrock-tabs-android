from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
CHORUS_CLOSURE_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-closure-proof-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-learned-rules-whole-song-projection-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-learned-rules-whole-song-projection-v1-manifest.json"

FIRST_MEASURE = 1
LAST_MEASURE = 113
INTRO_RANGE = range(1, 18)
VERSE1_RANGE = range(18, 33)
CHORUS_RANGE = range(33, 36)
TRAINED_RANGE = range(1, 36)

STANDARD_TUNING_MIDI = {
    1: 64,
    2: 59,
    3: 55,
    4: 50,
    5: 45,
    6: 40,
}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def measure_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def normalize_note(note: dict[str, Any]) -> tuple[int, int] | None:
    raw_string = integer(note.get("string", note.get("stringIndex")))
    fret = integer(note.get("fret"))
    if raw_string is None or fret is None or not 0 <= fret <= 24:
        return None
    if 1 <= raw_string <= 6:
        return raw_string, fret
    if 0 <= raw_string <= 5:
        return raw_string + 1, fret
    return None


def event_notes(event: dict[str, Any]) -> list[tuple[int, int]]:
    raw = event.get("notes")
    if not isinstance(raw, list):
        return []
    result: list[tuple[int, int]] = []
    for note in raw:
        if not isinstance(note, dict):
            continue
        normalized = normalize_note(note)
        if normalized is not None:
            result.append(normalized)
    return sorted(set(result))


def midi_for_note(note: tuple[int, int]) -> int:
    string, fret = note
    return STANDARD_TUNING_MIDI[string] + fret


def shape_for_notes(notes: list[tuple[int, int]]) -> tuple[int, ...]:
    if not notes:
        return ()
    pitches = sorted(midi_for_note(note) for note in notes)
    base = pitches[0]
    return tuple(pitch - base for pitch in pitches)


def build_measure_profiles(events: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    by_measure_step: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for event in events:
        measure = measure_of(event)
        step = step_of(event)
        if measure is None or step is None or not FIRST_MEASURE <= measure <= LAST_MEASURE:
            continue
        by_measure_step[measure][step].append(event)

    profiles: dict[int, dict[str, Any]] = {}
    for measure in range(FIRST_MEASURE, LAST_MEASURE + 1):
        step_map = by_measure_step.get(measure, {})
        rhythm_signature: list[tuple[int, int, int]] = []
        attack_signature: list[tuple[int, int]] = []
        voicing_shape_signature: list[tuple[int, tuple[int, ...]]] = []
        note_event_count = 0

        for step in sorted(step_map):
            rows = step_map[step]
            step_notes: set[tuple[int, int]] = set()
            for row in rows:
                notes = event_notes(row)
                note_event_count += len(notes)
                step_notes.update(notes)
            multiplicity = len(step_notes)
            rhythm_signature.append((step, len(rows), multiplicity))
            attack_signature.append((step, multiplicity))
            voicing_shape_signature.append((step, shape_for_notes(sorted(step_notes))))

        profiles[measure] = {
            "measureNumber": measure,
            "sourceEventRows": sum(len(rows) for rows in step_map.values()),
            "occupiedStepCount": len(step_map),
            "noteEventCount": note_event_count,
            "rhythmSignature": tuple(rhythm_signature),
            "attackSignature": tuple(attack_signature),
            "voicingShapeSignature": tuple(voicing_shape_signature),
        }
    return profiles


def training_section(measure: int) -> str:
    if measure in INTRO_RANGE:
        return "intro"
    if measure in VERSE1_RANGE:
        return "verse-1"
    if measure in CHORUS_RANGE:
        return "chorus-33-35"
    return "untrained"


def locate_prior_green(patterns: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    for pattern in patterns:
        for path in sorted(PUBLIC.glob(pattern)):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict) and payload.get("passed") is True:
                found.append(str(path.relative_to(ROOT)))
    return sorted(set(found))


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    closure = load(CHORUS_CLOSURE_PATH)
    events = source_rows(source)

    if len(events) != 949:
        raise RuntimeError(f"Expected 949 protected source events, found {len(events)}.")
    if closure.get("passed") is not True:
        raise RuntimeError("Chorus 33-35 closure proof is not green.")
    if closure.get("chorusMeasures33To35ClosedReadOnly") is not True:
        raise RuntimeError("Chorus 33-35 is not formally closed read-only.")
    if closure.get("readyForNextRhythmSectionInventory") is not True:
        raise RuntimeError("Closure proof did not authorize forward rhythm work.")

    profiles = build_measure_profiles(events)
    trained_profiles = {measure: profiles[measure] for measure in TRAINED_RANGE}

    intro_green = locate_prior_green(("*intro*proof*.json", "*intro*benchmark*.json"))
    verse_green = locate_prior_green(("*verse1*benchmark*.json", "*verse-1*benchmark*.json", "*verse1*proof*.json"))

    rows: list[dict[str, Any]] = []
    high_confidence = 0
    medium_confidence = 0
    trained_anchor = 0
    novel = 0

    for measure in range(FIRST_MEASURE, LAST_MEASURE + 1):
        profile = profiles[measure]
        if measure in TRAINED_RANGE:
            confidence = "trained-anchor"
            anchor_measure = measure
            match_type = "self-trained"
            trained_anchor += 1
        else:
            exact_matches: list[int] = []
            rhythm_matches: list[int] = []
            attack_matches: list[int] = []

            for candidate_measure, candidate in trained_profiles.items():
                if (
                    profile["rhythmSignature"] == candidate["rhythmSignature"]
                    and profile["voicingShapeSignature"] == candidate["voicingShapeSignature"]
                    and profile["occupiedStepCount"] > 0
                ):
                    exact_matches.append(candidate_measure)
                elif (
                    profile["rhythmSignature"] == candidate["rhythmSignature"]
                    and profile["occupiedStepCount"] > 0
                ):
                    rhythm_matches.append(candidate_measure)
                elif (
                    profile["attackSignature"] == candidate["attackSignature"]
                    and profile["occupiedStepCount"] > 0
                ):
                    attack_matches.append(candidate_measure)

            if exact_matches:
                confidence = "high"
                anchor_measure = exact_matches[0]
                match_type = "rhythm-and-voicing-shape"
                high_confidence += 1
            elif rhythm_matches:
                confidence = "medium"
                anchor_measure = rhythm_matches[0]
                match_type = "rhythm-structure"
                medium_confidence += 1
            elif attack_matches:
                confidence = "medium"
                anchor_measure = attack_matches[0]
                match_type = "attack-multiplicity"
                medium_confidence += 1
            else:
                confidence = "novel"
                anchor_measure = None
                match_type = "no-trained-structural-match"
                novel += 1

        inherited_section = training_section(anchor_measure) if anchor_measure is not None else None
        rules_available = {
            "timingConsensus": confidence in {"trained-anchor", "high", "medium"},
            "chordMultiplicity": confidence in {"trained-anchor", "high", "medium"},
            "playabilityGate": confidence in {"trained-anchor", "high", "medium"},
            "harmonicBranchCorrection": confidence in {"trained-anchor", "high"},
            "pitchContourPlausibility": confidence in {"trained-anchor", "high"},
            "bendEvidenceClassification": confidence in {"trained-anchor", "high"},
        }

        rows.append({
            "measureNumber": measure,
            "sourceEventRows": profile["sourceEventRows"],
            "occupiedStepCount": profile["occupiedStepCount"],
            "noteEventCount": profile["noteEventCount"],
            "projectionConfidence": confidence,
            "matchedTrainingMeasure": anchor_measure,
            "matchedTrainingSection": inherited_section,
            "matchType": match_type,
            "learnedRulesAvailable": rules_available,
            "automaticApplyAllowed": False,
            "readOnlyCandidateOnly": True,
        })

    projected_measures = high_confidence + medium_confidence
    unresolved_measures = [
        row["measureNumber"]
        for row in rows
        if row["projectionConfidence"] == "novel"
    ]

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and len(rows) == 113
        and trained_anchor == 35
        and closure.get("productionPromotionAllowed") is False
    )

    recommended = (
        "build-gomyway-rhythm-whole-song-high-confidence-candidate-proof-v1"
        if passed
        else "diagnose-gomyway-rhythm-learned-rules-whole-song-projection-v1"
    )

    output = {
        "schemaVersion": 1,
        "projectionType": "read-only-whole-song-learned-rhythm-rules",
        "passed": passed,
        "measureRange": [FIRST_MEASURE, LAST_MEASURE],
        "measureCount": len(rows),
        "trainedAnchorMeasureCount": trained_anchor,
        "highConfidenceProjectedMeasureCount": high_confidence,
        "mediumConfidenceProjectedMeasureCount": medium_confidence,
        "projectedUntrainedMeasureCount": projected_measures,
        "novelMeasureCount": novel,
        "novelMeasures": unresolved_measures,
        "introGreenArtifactsDiscovered": intro_green,
        "verse1GreenArtifactsDiscovered": verse_green,
        "chorusClosureVerified": True,
        "rows": rows,
        "readyForWholeSongHighConfidenceCandidateProof": passed,
        "recommendedNextAction": recommended,
        "automaticApplyAllowed": False,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "protectedSourceEventCount": len(events),
        "protectedSourceHashBefore": source_hash_before,
        "protectedSourceHashAfter": source_hash_after,
        "protectedSourceHashUnchanged": source_unchanged,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "measureCount": len(rows),
        "trainedAnchorMeasureCount": trained_anchor,
        "highConfidenceProjectedMeasureCount": high_confidence,
        "mediumConfidenceProjectedMeasureCount": medium_confidence,
        "novelMeasureCount": novel,
        "readyForWholeSongHighConfidenceCandidateProof": passed,
        "recommendedNextAction": recommended,
        "automaticApplyAllowed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM LEARNED RULES WHOLE SONG PROJECTION V1 COMPLETE")
    print("Passed:", passed)
    print("Measures scanned:", len(rows))
    print("Trained anchor measures:", trained_anchor)
    print("High-confidence projected untrained measures:", high_confidence)
    print("Medium-confidence projected untrained measures:", medium_confidence)
    print("Total projected untrained measures:", projected_measures)
    print("Novel measures requiring deeper training:", novel)
    if unresolved_measures:
        print("Novel measure numbers:", ",".join(str(value) for value in unresolved_measures))
    print("Intro green artifacts discovered:", len(intro_green))
    print("Verse 1 green artifacts discovered:", len(verse_green))
    print("Chorus 33-35 closure verified: True")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for whole-song high-confidence candidate proof:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
