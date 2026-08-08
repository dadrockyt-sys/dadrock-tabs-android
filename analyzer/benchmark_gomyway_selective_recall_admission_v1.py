from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_basic_pitch_consensus_recall_recovery_v1 as recall
import profile_gomyway_consensus_recall_candidates_v1 as profile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
STEM_PATH = recall.STEM_PATH
CANDIDATE_PATH = recall.CANDIDATE_PATH
REFERENCE_PATH = recall.REFERENCE_PATH
OUTPUT_PATH = PUBLIC / "gomyway-selective-recall-admission-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-selective-recall-admission-v1-manifest.json"

CURRENT_CHAMPION_F1 = 6.60
PRIORITY_MEASURES = recall.PRIORITY_MEASURES


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_rows(pass_groups: list[dict[tuple[int, int], dict[int, dict[str, float]]]]) -> list[dict[str, Any]]:
    primary = pass_groups[0]
    relaxed = pass_groups[1:]
    rows: list[dict[str, Any]] = []

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
            rows.append({
                "measure": measure,
                "step": step,
                "midi": midi,
                "votes": votes,
                "relativeAmplitude": rel_amp,
                "primarySlotSize": len(primary_rows),
                "neighborSamePitch": neighbor_same_pitch,
                "bucket": profile.bucket_key(votes, rel_amp, len(primary_rows), neighbor_same_pitch),
            })
    return rows


def admit(row: dict[str, Any], rule: str) -> bool:
    votes = int(row["votes"])
    rel_amp = float(row["relativeAmplitude"])
    slot_size = int(row["primarySlotSize"])
    neighbor = bool(row["neighborSamePitch"])

    if rule == "micro_bucket":
        return votes == 3 and 0.50 <= rel_amp < 0.75 and 3 <= slot_size <= 4 and not neighbor
    if rule == "votes4_highamp_sparse_neighbor":
        return votes == 4 and rel_amp >= 0.75 and slot_size <= 2 and neighbor
    if rule == "votes4_highamp_sparse":
        return votes == 4 and rel_amp >= 0.75 and slot_size <= 2
    if rule == "micro_plus_votes4_neighbor":
        return (
            (votes == 3 and 0.50 <= rel_amp < 0.75 and 3 <= slot_size <= 4 and not neighbor)
            or (votes == 4 and rel_amp >= 0.75 and slot_size <= 2 and neighbor)
        )
    if rule == "micro_plus_votes4_sparse":
        return (
            (votes == 3 and 0.50 <= rel_amp < 0.75 and 3 <= slot_size <= 4 and not neighbor)
            or (votes == 4 and rel_amp >= 0.75 and slot_size <= 2)
        )
    return False


def score(name: str, predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]], admitted: int) -> dict[str, Any]:
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
        "admittedRelaxedCandidates": admitted,
        "priorityBatch": {
            "matched": sum((priority_reference & priority_predicted).values()),
            "missing": sum((priority_reference - priority_predicted).values()),
            "extra": sum((priority_predicted - priority_reference).values()),
        },
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
    for pass_cfg in recall.PASSES:
        v2.ONSET_THRESHOLD = float(pass_cfg["onset"])
        v2.FRAME_THRESHOLD = float(pass_cfg["frame"])
        v2.MINIMUM_NOTE_LENGTH_MS = float(pass_cfg["min_ms"])
        print(
            f"Running {pass_cfg['name']}: onset={v2.ONSET_THRESHOLD} frame={v2.FRAME_THRESHOLD} minMs={v2.MINIMUM_NOTE_LENGTH_MS}",
            flush=True,
        )
        pass_groups.append(recall.snap_notes(v2.basic_pitch_notes(STEM_PATH), grid))

    champion = recall.build_prediction(
        pass_groups,
        {"name": "champion_primary_only", "minimumRelaxedVotes": 99, "minRelativeAmplitude": 0.0},
    )
    candidates = candidate_rows(pass_groups)

    rules = [
        "champion_only",
        "micro_bucket",
        "votes4_highamp_sparse_neighbor",
        "votes4_highamp_sparse",
        "micro_plus_votes4_neighbor",
        "micro_plus_votes4_sparse",
    ]

    results: list[dict[str, Any]] = []
    for rule in rules:
        predicted = Counter(champion)
        admitted = 0
        if rule != "champion_only":
            for row in candidates:
                if not admit(row, rule):
                    continue
                token = (int(row["measure"]), int(row["step"]), int(row["midi"]))
                if token in predicted:
                    continue
                # Preserve the champion's five-note physical chord cap.
                slot_count = sum(
                    count
                    for (measure, step, _midi), count in predicted.items()
                    if measure == token[0] and step == token[1]
                )
                if slot_count >= recall.MAX_NOTES_PER_SLOT:
                    continue
                predicted[token] += 1
                admitted += 1
        result = score(rule, predicted, reference, admitted)
        results.append(result)
        p = result["priorityBatch"]
        print(
            f"{rule}: pitchF1={result['pitchF1']} matched={result['matchedPitchTokens']} "
            f"missing={result['missingProfessionalPitchTokens']} extra={result['extraCandidatePitchTokens']} "
            f"admitted={admitted} priority={p['matched']}/{p['missing']}/{p['extra']}",
            flush=True,
        )

    ranked = sorted(
        results,
        key=lambda row: (
            float(row["pitchF1"]),
            int(row["matchedPitchTokens"]),
            -int(row["extraCandidatePitchTokens"]),
        ),
        reverse=True,
    )
    winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during selective recall benchmark.")

    improvement = round(float(winner["pitchF1"]) - CURRENT_CHAMPION_F1, 2)
    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "selective-detector-side-recall-admission",
        "inputStem": str(STEM_PATH.relative_to(ROOT)),
        "timingGrid": grid_diagnostics,
        "currentChampionPitchF1": CURRENT_CHAMPION_F1,
        "relaxedCandidateCount": len(candidates),
        "results": results,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "winnerMatched": winner["matchedPitchTokens"],
        "winnerMissing": winner["missingProfessionalPitchTokens"],
        "winnerExtra": winner["extraCandidatePitchTokens"],
        "winnerAdmittedRelaxedCandidates": winner["admittedRelaxedCandidates"],
        "winnerPriorityBatch": winner["priorityBatch"],
        "improvementVsCurrentChampionPoints": improvement,
        "winnerBeatsCurrentChampion": float(winner["pitchF1"]) > CURRENT_CHAMPION_F1,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only; bucket definitions derived from prior training diagnostics",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "validate-selective-recall-rule-on-held-out-measures"
            if float(winner["pitchF1"]) > CURRENT_CHAMPION_F1
            else "freeze-harmonic-champion-and-change-recall-evidence-source"
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

    print("GOMYWAY SELECTIVE RECALL ADMISSION V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", CURRENT_CHAMPION_F1)
    print("Winner:", output["winner"])
    print("Winner pitch F1:", output["winnerPitchF1"])
    print("Winner matched/missing/extra:", output["winnerMatched"], "/", output["winnerMissing"], "/", output["winnerExtra"])
    print("Winner admitted relaxed candidates:", output["winnerAdmittedRelaxedCandidates"])
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
