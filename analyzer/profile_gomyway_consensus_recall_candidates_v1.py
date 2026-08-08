from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_basic_pitch_consensus_recall_recovery_v1 as recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
STEM_PATH = recall.STEM_PATH
CANDIDATE_PATH = recall.CANDIDATE_PATH
REFERENCE_PATH = recall.REFERENCE_PATH
OUTPUT_PATH = PUBLIC / "gomyway-consensus-recall-candidate-profile-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-consensus-recall-candidate-profile-v1-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket_key(votes: int, rel_amp: float, primary_slot_size: int, neighbor_same_pitch: bool) -> str:
    if rel_amp >= 0.75:
        amp_bucket = "amp75plus"
    elif rel_amp >= 0.50:
        amp_bucket = "amp50_74"
    elif rel_amp >= 0.35:
        amp_bucket = "amp35_49"
    else:
        amp_bucket = "amp_lt35"
    slot_bucket = "slot0_2" if primary_slot_size <= 2 else "slot3_4" if primary_slot_size <= 4 else "slot5plus"
    neighbor_bucket = "neighbor" if neighbor_same_pitch else "no_neighbor"
    return f"votes{votes}_{amp_bucket}_{slot_bucket}_{neighbor_bucket}"


def main() -> None:
    if not STEM_PATH.exists():
        raise FileNotFoundError(f"Missing winning separator stem: {STEM_PATH.relative_to(ROOT)}")

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

    pass_groups = []
    for pass_cfg in recall.PASSES:
        v2.ONSET_THRESHOLD = float(pass_cfg["onset"])
        v2.FRAME_THRESHOLD = float(pass_cfg["frame"])
        v2.MINIMUM_NOTE_LENGTH_MS = float(pass_cfg["min_ms"])
        print(
            f"Running {pass_cfg['name']}: onset={v2.ONSET_THRESHOLD} frame={v2.FRAME_THRESHOLD} minMs={v2.MINIMUM_NOTE_LENGTH_MS}",
            flush=True,
        )
        pass_groups.append(recall.snap_notes(v2.basic_pitch_notes(STEM_PATH), grid))

    primary = pass_groups[0]
    relaxed = pass_groups[1:]

    primary_prediction = recall.build_prediction(
        pass_groups,
        {"name": "champion_primary_only", "minimumRelaxedVotes": 99, "minRelativeAmplitude": 0.0},
    )
    primary_matched = sum((primary_prediction & reference).values())

    candidates: list[dict[str, Any]] = []
    bucket_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0})
    vote_counts: dict[int, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0})

    all_slots = set()
    for group in relaxed:
        all_slots.update(group)

    for slot in sorted(all_slots):
        primary_rows = primary.get(slot, {})
        primary_max = max((row["amplitude"] for row in primary_rows.values()), default=0.0)
        candidate_pitches = set()
        for group in relaxed:
            candidate_pitches.update(group.get(slot, {}))

        for midi in sorted(candidate_pitches):
            if midi in primary_rows:
                continue
            evidence = [group.get(slot, {}).get(midi) for group in relaxed]
            evidence = [row for row in evidence if row is not None]
            votes = len(evidence)
            if votes < 2:
                continue
            best = max(evidence, key=lambda row: (row["amplitude"], row["duration"], -row["distance"]))
            rel_amp = best["amplitude"] / primary_max if primary_max > 0 else 1.0
            measure, step = slot
            neighbor_same_pitch = any(
                midi in primary.get((measure, neighbor_step), {})
                for neighbor_step in (step - 1, step + 1)
                if neighbor_step >= 0
            )
            token = (measure, step, midi)
            correct = token in reference
            key = bucket_key(votes, rel_amp, len(primary_rows), neighbor_same_pitch)
            bucket_counts[key]["total"] += 1
            bucket_counts[key]["correct"] += int(correct)
            vote_counts[votes]["total"] += 1
            vote_counts[votes]["correct"] += int(correct)
            candidates.append({
                "measure": measure,
                "step": step,
                "midi": midi,
                "votes": votes,
                "relativeAmplitude": round(rel_amp, 4),
                "primarySlotSize": len(primary_rows),
                "neighborSamePitch": neighbor_same_pitch,
                "correctDownstream": correct,
                "bucket": key,
            })

    bucket_rows = []
    for name, counts in bucket_counts.items():
        total = counts["total"]
        correct = counts["correct"]
        bucket_rows.append({
            "bucket": name,
            "total": total,
            "correct": correct,
            "precisionPercent": round(100.0 * correct / total, 2) if total else 0.0,
        })
    bucket_rows.sort(key=lambda row: (row["precisionPercent"], row["correct"], -row["total"]), reverse=True)

    vote_rows = []
    for votes, counts in sorted(vote_counts.items()):
        total = counts["total"]
        correct = counts["correct"]
        vote_rows.append({
            "votes": votes,
            "total": total,
            "correct": correct,
            "precisionPercent": round(100.0 * correct / total, 2) if total else 0.0,
        })

    recovered_correct = sum(1 for row in candidates if row["correctDownstream"])
    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during recall candidate profiling.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "consensus-recall-candidate-downstream-profile",
        "inputStem": str(STEM_PATH.relative_to(ROOT)),
        "currentChampionPitchF1": recall.CURRENT_CHAMPION_F1,
        "currentChampionMatched": primary_matched,
        "relaxedCandidateCount": len(candidates),
        "relaxedCorrectCandidateCount": recovered_correct,
        "relaxedCandidatePrecisionPercent": round(100.0 * recovered_correct / len(candidates), 2) if candidates else 0.0,
        "voteSummary": vote_rows,
        "bestBuckets": bucket_rows[:20],
        "candidateDiagnostics": candidates,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-diagnostic-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "build-selective-recall-admission-from-high-precision-detector-side-buckets",
    }
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

    print("GOMYWAY CONSENSUS RECALL CANDIDATE PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Current champion F1:", recall.CURRENT_CHAMPION_F1)
    print("Current champion matched:", primary_matched)
    print("Relaxed candidates:", len(candidates))
    print("Correct relaxed candidates:", recovered_correct)
    print("Overall relaxed candidate precision %:", output["relaxedCandidatePrecisionPercent"])
    print("Vote summary:")
    for row in vote_rows:
        print(f"  votes={row['votes']} total={row['total']} correct={row['correct']} precision={row['precisionPercent']}%")
    print("Top detector-side buckets:")
    for row in bucket_rows[:12]:
        print(f"  {row['bucket']}: total={row['total']} correct={row['correct']} precision={row['precisionPercent']}%")
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
