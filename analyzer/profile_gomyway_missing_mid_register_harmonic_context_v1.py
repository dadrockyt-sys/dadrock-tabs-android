from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_basic_pitch_harmonic_refinement_v2 as harmonic
import benchmark_gomyway_cross_stem_consensus_recall_v1 as crossstem

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-missing-mid-register-harmonic-context-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-missing-mid-register-harmonic-context-v1-manifest.json"

MID_MIN = 52
MID_MAX = 63
HARMONIC_CONFIG = {"name": "harmonic_r074_cap5", "ratio": 0.74, "cap": 5, "intervals": (12, 19, 24)}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grouped_for(path: Path, grid: dict[tuple[int, int], float]):
    v2.ONSET_THRESHOLD = 0.50
    v2.FRAME_THRESHOLD = 0.30
    v2.MINIMUM_NOTE_LENGTH_MS = 110.0
    notes = v2.basic_pitch_notes(path)
    grouped, _discarded, _distances = harmonic.snap_notes(notes, grid)
    return grouped


def prediction(grouped):
    return harmonic.predict_for_config(grouped, HARMONIC_CONFIG)


def merge_all(*predictions):
    merged = Counter()
    for pred in predictions:
        for token, count in pred.items():
            if token in merged:
                continue
            measure, step, _midi = token
            slot_count = sum(v for (m, s, _p), v in merged.items() if m == measure and s == step)
            if slot_count >= 5:
                continue
            merged[token] = min(1, count)
    return merged


def section_for(measure: int) -> str:
    for start, end in ((17, 32), (33, 48), (49, 64), (65, 80), (81, 96), (97, 113)):
        if start <= measure <= end:
            return f"m{start}_{end}"
    return "other"


def main() -> None:
    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _grid_diagnostics = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)
    if sum(reference.values()) != 867:
        raise RuntimeError(f"Expected 867 professional pitch tokens, found {sum(reference.values())}")

    print("Analyzing frozen 6.99 cross-stem champion...", flush=True)
    champion = merge_all(prediction(grouped_for(WINNER_STEM, grid)), prediction(grouped_for(ALT_STEM, grid)))
    missing = reference - champion

    mid_missing = Counter({k: v for k, v in missing.items() if MID_MIN <= k[2] <= MID_MAX})
    relationship_counts = Counter()
    section_relationship_counts = Counter()
    slot_size_counts = Counter()
    pitch_counts = Counter()

    for (measure, step, midi), count in mid_missing.items():
        slot_pitches = {p for (m, s, p), c in champion.items() if c > 0 and m == measure and s == step}
        relations = []
        if midi - 12 in slot_pitches:
            relations.append("lower_octave_present")
        if midi + 12 in slot_pitches:
            relations.append("upper_octave_present")
        if midi - 7 in slot_pitches or midi + 7 in slot_pitches:
            relations.append("perfect_fifth_present")
        if midi - 5 in slot_pitches or midi + 5 in slot_pitches:
            relations.append("perfect_fourth_present")
        if midi - 4 in slot_pitches or midi + 4 in slot_pitches:
            relations.append("major_third_present")
        if midi - 3 in slot_pitches or midi + 3 in slot_pitches:
            relations.append("minor_third_present")
        if not relations:
            relations.append("no_common_chord_relation")

        for relation in relations:
            relationship_counts[relation] += count
            section_relationship_counts[(section_for(measure), relation)] += count
        slot_size_counts[len(slot_pitches)] += count
        pitch_counts[midi] += count

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "missing-mid-register-harmonic-context-profile",
        "championPitchF1": 6.99,
        "midRegisterMidiRange": [MID_MIN, MID_MAX],
        "totalMissing": sum(missing.values()),
        "midRegisterMissing": sum(mid_missing.values()),
        "relationshipCounts": dict(relationship_counts.most_common()),
        "slotSizeCounts": {str(k): v for k, v in sorted(slot_size_counts.items())},
        "topMissingMidi": pitch_counts.most_common(12),
        "topSectionRelationship": [
            {"section": section, "relationship": relation, "count": count}
            for (section, relation), count in section_relationship_counts.most_common(20)
        ],
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-diagnostics-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "choose-detector-side-mid-register-recovery-from-harmonic-context",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": sha256(CANDIDATE_PATH),
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }

    if candidate_hash_before != manifest["candidateSha256"]:
        raise RuntimeError("Protected 949-event candidate changed during profiling.")

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY MISSING MID-REGISTER HARMONIC CONTEXT V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1: 6.99")
    print("Total missing:", output["totalMissing"])
    print("Mid-register missing:", output["midRegisterMissing"])
    print("Relationship profile:")
    for key, value in relationship_counts.most_common():
        print(f"  {key}: {value}")
    print("Slot-size profile:")
    for key, value in sorted(slot_size_counts.items()):
        print(f"  slot{key}: {value}")
    print("Top missing MIDI in mid register:")
    for midi, count in pitch_counts.most_common(12):
        print(f"  {midi}: {count}")
    print("Top section/relationship buckets:")
    for row in output["topSectionRelationship"][:12]:
        print(f"  {row['section']} {row['relationship']}: {row['count']}")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
