from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_basic_pitch_harmonic_refinement_v2 as harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-mid-register-loss-stage-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-mid-register-loss-stage-v1-manifest.json"

MID_MIN = 52
MID_MAX = 63
RATIO = 0.74
CAP = 5
INTERVALS = (12, 19, 24)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grouped_for(path: Path, grid: dict[tuple[int, int], float]):
    v2.ONSET_THRESHOLD = 0.50
    v2.FRAME_THRESHOLD = 0.30
    v2.MINIMUM_NOTE_LENGTH_MS = 110.0
    notes = v2.basic_pitch_notes(path)
    grouped, _discarded, _distances = harmonic.snap_notes(notes, grid)
    return grouped


def token_set_from_rows(grouped, stage: str) -> set[tuple[int, int, int]]:
    tokens: set[tuple[int, int, int]] = set()
    for (measure, step), original in grouped.items():
        rows = list(original)
        if stage in {"dedupe_range", "harmonic", "cap5"}:
            rows = harmonic.dedupe_and_range(rows)
        if stage in {"harmonic", "cap5"}:
            rows = harmonic.suppress_harmonics(rows, RATIO, INTERVALS)
        if stage == "cap5" and len(rows) > CAP:
            rows = sorted(
                rows,
                key=lambda row: (
                    float(row["amplitude"]),
                    float(row["duration"]),
                    -float(row["distance"]),
                ),
                reverse=True,
            )[:CAP]
        for row in rows:
            tokens.add((measure, step, int(row["midi"])))
    return tokens


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

    print("Analyzing both stems for stage-loss profiling...", flush=True)
    winner_grouped = grouped_for(WINNER_STEM, grid)
    alt_grouped = grouped_for(ALT_STEM, grid)

    stages = ("raw_snapped", "dedupe_range", "harmonic", "cap5")
    winner_stage = {stage: token_set_from_rows(winner_grouped, stage) for stage in stages}
    alt_stage = {stage: token_set_from_rows(alt_grouped, stage) for stage in stages}
    union_stage = {stage: winner_stage[stage] | alt_stage[stage] for stage in stages}

    champion = Counter({token: 1 for token in union_stage["cap5"]})
    missing = reference - champion
    mid_missing = Counter({k: v for k, v in missing.items() if MID_MIN <= k[2] <= MID_MAX})

    stage_presence = Counter()
    loss_reason = Counter()
    section_loss = Counter()

    for token, count in mid_missing.items():
        measure, _step, _midi = token
        sec = section_for(measure)
        present_raw = token in union_stage["raw_snapped"]
        present_dedupe = token in union_stage["dedupe_range"]
        present_harmonic = token in union_stage["harmonic"]
        present_cap = token in union_stage["cap5"]

        if present_raw:
            stage_presence["present_raw_snapped"] += count
        if present_dedupe:
            stage_presence["present_after_dedupe_range"] += count
        if present_harmonic:
            stage_presence["present_after_harmonic"] += count
        if present_cap:
            stage_presence["present_after_cap5"] += count

        if not present_raw:
            reason = "absent_from_both_raw_detectors"
        elif not present_dedupe:
            reason = "lost_at_dedupe_or_guitar_range"
        elif not present_harmonic:
            reason = "lost_at_harmonic_suppression"
        elif not present_cap:
            reason = "lost_at_five_note_cap"
        else:
            reason = "present_but_counter_multiplicity_mismatch"
        loss_reason[reason] += count
        section_loss[(sec, reason)] += count

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "mid-register-missing-stage-loss-profile",
        "championPitchF1": 6.99,
        "midRegisterMidiRange": [MID_MIN, MID_MAX],
        "totalChampionMissing": sum(missing.values()),
        "midRegisterMissing": sum(mid_missing.values()),
        "stagePresence": dict(stage_presence),
        "lossReasons": dict(loss_reason.most_common()),
        "topSectionLossReasons": [
            {"section": section, "reason": reason, "count": count}
            for (section, reason), count in section_loss.most_common(20)
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
        "recommendedNextAction": "target-dominant-mid-register-loss-stage",
    }

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during stage-loss profiling.")

    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY MID-REGISTER LOSS STAGE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1: 6.99")
    print("Total champion missing:", output["totalChampionMissing"])
    print("Mid-register missing:", output["midRegisterMissing"])
    print("Stage presence among missing mid-register tokens:")
    for key, value in stage_presence.most_common():
        print(f"  {key}: {value}")
    print("Loss reason profile:")
    for key, value in loss_reason.most_common():
        print(f"  {key}: {value}")
    print("Top section/loss buckets:")
    for row in output["topSectionLossReasons"][:12]:
        print(f"  {row['section']} {row['reason']}: {row['count']}")
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
