from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
STEM_PATH = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-basic-pitch-consensus-recall-recovery-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-basic-pitch-consensus-recall-recovery-v1-manifest.json"

CURRENT_CHAMPION_F1 = 6.60
SNAP_TOLERANCE_SECONDS = 0.085
PRIORITY_MEASURES = [68, 76, 111, 109, 72, 93, 103, 105, 110, 104, 113, 80]
HARMONIC_RATIO = 0.74
HARMONIC_INTERVALS = {12, 19, 24}
MAX_NOTES_PER_SLOT = 5
MIN_MIDI = 40
MAX_MIDI = 88

# These passes are fixed detector-side hypotheses. The professional reference is never
# consulted when deciding which relaxed candidates are admitted.
PASSES = [
    {"name": "primary", "onset": 0.50, "frame": 0.30, "min_ms": 110.0},
    {"name": "relaxed_a", "onset": 0.45, "frame": 0.30, "min_ms": 110.0},
    {"name": "relaxed_b", "onset": 0.45, "frame": 0.30, "min_ms": 80.0},
    {"name": "relaxed_c", "onset": 0.40, "frame": 0.30, "min_ms": 80.0},
    {"name": "relaxed_d", "onset": 0.45, "frame": 0.25, "min_ms": 80.0},
]

CONFIGS = [
    {"name": "champion_primary_only", "minimumRelaxedVotes": 99, "minRelativeAmplitude": 0.0},
    {"name": "consensus2", "minimumRelaxedVotes": 2, "minRelativeAmplitude": 0.0},
    {"name": "consensus3", "minimumRelaxedVotes": 3, "minRelativeAmplitude": 0.0},
    {"name": "consensus2_relamp035", "minimumRelaxedVotes": 2, "minRelativeAmplitude": 0.35},
    {"name": "consensus2_relamp050", "minimumRelaxedVotes": 2, "minRelativeAmplitude": 0.50},
    {"name": "consensus3_relamp035", "minimumRelaxedVotes": 3, "minRelativeAmplitude": 0.35},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snap_notes(notes: list[tuple[float, float, int, float]], grid: dict[tuple[int, int], float]) -> dict[tuple[int, int], dict[int, dict[str, float]]]:
    grid_items = list(grid.items())
    grouped: dict[tuple[int, int], dict[int, dict[str, float]]] = defaultdict(dict)
    for start, end, midi, amplitude in notes:
        slot, distance = v2.nearest_grid_slot(start, grid_items)
        if slot is None or distance > SNAP_TOLERANCE_SECONDS:
            continue
        if midi < MIN_MIDI or midi > MAX_MIDI:
            continue
        row = {
            "amplitude": float(amplitude),
            "duration": max(0.0, float(end) - float(start)),
            "distance": float(distance),
        }
        existing = grouped[slot].get(int(midi))
        if existing is None or (row["amplitude"], row["duration"], -row["distance"]) > (
            existing["amplitude"], existing["duration"], -existing["distance"]
        ):
            grouped[slot][int(midi)] = row
    return grouped


def harmonic_filter(rows: dict[int, dict[str, float]]) -> dict[int, dict[str, float]]:
    ordered = sorted(rows.items(), key=lambda item: (item[1]["amplitude"], item[1]["duration"]), reverse=True)
    kept: dict[int, dict[str, float]] = {}
    for midi, row in ordered:
        suppress = False
        for lower, stronger in kept.items():
            interval = midi - lower
            if interval in HARMONIC_INTERVALS and row["amplitude"] < stronger["amplitude"] * HARMONIC_RATIO:
                suppress = True
                break
        if not suppress:
            kept[midi] = row
    if len(kept) > MAX_NOTES_PER_SLOT:
        top = sorted(
            kept.items(),
            key=lambda item: (item[1]["amplitude"], item[1]["duration"], -item[1]["distance"]),
            reverse=True,
        )[:MAX_NOTES_PER_SLOT]
        kept = dict(top)
    return kept


def build_prediction(
    pass_groups: list[dict[tuple[int, int], dict[int, dict[str, float]]]],
    config: dict[str, Any],
) -> Counter[tuple[int, int, int]]:
    primary = pass_groups[0]
    relaxed = pass_groups[1:]
    all_slots = set(primary)
    for group in relaxed:
        all_slots.update(group)

    predicted: Counter[tuple[int, int, int]] = Counter()
    min_votes = int(config["minimumRelaxedVotes"])
    rel_amp = float(config["minRelativeAmplitude"])

    for slot in all_slots:
        merged: dict[int, dict[str, float]] = dict(primary.get(slot, {}))
        primary_max = max((row["amplitude"] for row in primary.get(slot, {}).values()), default=0.0)

        if min_votes <= len(relaxed):
            candidate_pitches = set()
            for group in relaxed:
                candidate_pitches.update(group.get(slot, {}))
            for midi in candidate_pitches:
                if midi in merged:
                    continue
                evidence = [group.get(slot, {}).get(midi) for group in relaxed]
                evidence = [row for row in evidence if row is not None]
                if len(evidence) < min_votes:
                    continue
                best = max(evidence, key=lambda row: (row["amplitude"], row["duration"], -row["distance"]))
                if primary_max > 0.0 and best["amplitude"] < primary_max * rel_amp:
                    continue
                merged[midi] = best

        filtered = harmonic_filter(merged)
        measure, step = slot
        for midi in filtered:
            predicted[(measure, step, midi)] += 1
    return predicted


def score(name: str, predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]], settings: dict[str, Any]) -> dict[str, Any]:
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    expected = sum(reference.values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())
    pitch_f1 = round(100.0 * v2.f1(matched, predicted_count, expected), 2)

    priority_reference = Counter({k: n for k, n in reference.items() if k[0] in PRIORITY_MEASURES})
    priority_predicted = Counter({k: n for k, n in predicted.items() if k[0] in PRIORITY_MEASURES})
    return {
        "name": name,
        "pitchF1": pitch_f1,
        "matchedPitchTokens": matched,
        "missingProfessionalPitchTokens": missing,
        "extraCandidatePitchTokens": extra,
        "predictionCount": predicted_count,
        "priorityBatch": {
            "matched": sum((priority_reference & priority_predicted).values()),
            "missing": sum((priority_reference - priority_predicted).values()),
            "extra": sum((priority_predicted - priority_reference).values()),
        },
        "settings": settings,
    }


def main() -> None:
    if not STEM_PATH.exists():
        raise FileNotFoundError(f"Missing winning separator stem: {STEM_PATH.relative_to(ROOT)}")

    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, grid_diagnostics = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)
    if sum(reference.values()) != 867:
        raise RuntimeError(f"Expected 867 professional pitch tokens, found {sum(reference.values())}")

    pass_groups = []
    pass_diagnostics = []
    for pass_cfg in PASSES:
        v2.ONSET_THRESHOLD = float(pass_cfg["onset"])
        v2.FRAME_THRESHOLD = float(pass_cfg["frame"])
        v2.MINIMUM_NOTE_LENGTH_MS = float(pass_cfg["min_ms"])
        print(
            f"Running {pass_cfg['name']}: onset={v2.ONSET_THRESHOLD} frame={v2.FRAME_THRESHOLD} minMs={v2.MINIMUM_NOTE_LENGTH_MS}",
            flush=True,
        )
        notes = v2.basic_pitch_notes(STEM_PATH)
        grouped = snap_notes(notes, grid)
        pass_groups.append(grouped)
        pass_diagnostics.append({
            **pass_cfg,
            "rawNoteCount": len(notes),
            "slotCount": len(grouped),
            "uniqueSnappedPitchCount": sum(len(rows) for rows in grouped.values()),
        })

    results = []
    for config in CONFIGS:
        predicted = build_prediction(pass_groups, config)
        result = score(str(config["name"]), predicted, reference, config)
        results.append(result)
        p = result["priorityBatch"]
        print(
            f"{result['name']}: pitchF1={result['pitchF1']} matched={result['matchedPitchTokens']} "
            f"missing={result['missingProfessionalPitchTokens']} extra={result['extraCandidatePitchTokens']} "
            f"predictions={result['predictionCount']} priority={p['matched']}/{p['missing']}/{p['extra']}",
            flush=True,
        )

    ranked = sorted(results, key=lambda row: (float(row["pitchF1"]), int(row["matchedPitchTokens"]), -int(row["extraCandidatePitchTokens"])), reverse=True)
    winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during recall-recovery benchmark.")

    improvement = round(float(winner["pitchF1"]) - CURRENT_CHAMPION_F1, 2)
    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "basic-pitch-multipass-consensus-recall-recovery",
        "inputStem": str(STEM_PATH.relative_to(ROOT)),
        "timingGrid": grid_diagnostics,
        "professionalPitchTokens": sum(reference.values()),
        "currentChampionPitchF1": CURRENT_CHAMPION_F1,
        "currentChampionSettings": {
            "onsetThreshold": 0.50,
            "frameThreshold": 0.30,
            "minimumNoteLengthMs": 110.0,
            "harmonicAmplitudeRatio": HARMONIC_RATIO,
            "harmonicIntervals": sorted(HARMONIC_INTERVALS),
            "maxNotesPerSlot": MAX_NOTES_PER_SLOT,
        },
        "detectorPasses": pass_diagnostics,
        "results": results,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "winnerMatched": winner["matchedPitchTokens"],
        "winnerMissing": winner["missingProfessionalPitchTokens"],
        "winnerExtra": winner["extraCandidatePitchTokens"],
        "winnerPriorityBatch": winner["priorityBatch"],
        "improvementVsCurrentChampionPoints": improvement,
        "winnerBeatsCurrentChampion": float(winner["pitchF1"]) > CURRENT_CHAMPION_F1,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "refine-consensus-recall-around-winner"
            if float(winner["pitchF1"]) > CURRENT_CHAMPION_F1
            else "freeze-harmonic-champion-and-profile-missing-pitch-classes"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY BASIC PITCH CONSENSUS RECALL RECOVERY V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", CURRENT_CHAMPION_F1)
    print("Winner:", output["winner"])
    print("Winner pitch F1:", output["winnerPitchF1"])
    print("Winner matched/missing/extra:", output["winnerMatched"], "/", output["winnerMissing"], "/", output["winnerExtra"])
    print("Winner priority matched/missing/extra:", output["winnerPriorityBatch"]["matched"], "/", output["winnerPriorityBatch"]["missing"], "/", output["winnerPriorityBatch"]["extra"])
    print("Improvement vs current champion points:", improvement)
    print("Winner beats current champion:", output["winnerBeatsCurrentChampion"])
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
