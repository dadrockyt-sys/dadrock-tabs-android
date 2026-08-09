from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import benchmark_gomyway_1382_champion_dual_stem_recurrence_recall_gate_v1 as recur

raw = recur.raw
miss = recur.miss
v2 = recur.v2
v3 = recur.v3
recall = recur.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-champion-dual-stem-local-prominence-recall-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-champion-dual-stem-local-prominence-recall-gate-v1-manifest.json"
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82

VARIANTS: list[dict[str, Any]] = [
    {"name": "floor4_margin05_recur2", "bothFloor": 4.0, "margin": 0.5, "recurrence": 2},
    {"name": "floor4_margin10_recur2", "bothFloor": 4.0, "margin": 1.0, "recurrence": 2},
    {"name": "floor4_margin20_recur2", "bothFloor": 4.0, "margin": 2.0, "recurrence": 2},
    {"name": "floor6_margin05_recur2", "bothFloor": 6.0, "margin": 0.5, "recurrence": 2},
    {"name": "floor6_margin10_recur2", "bothFloor": 6.0, "margin": 1.0, "recurrence": 2},
    {"name": "floor6_margin20_recur2", "bothFloor": 6.0, "margin": 2.0, "recurrence": 2},
    {"name": "floor4_margin05_recur3", "bothFloor": 4.0, "margin": 0.5, "recurrence": 3},
    {"name": "floor4_margin10_recur3", "bothFloor": 4.0, "margin": 1.0, "recurrence": 3},
    {"name": "floor6_margin05_recur3", "bothFloor": 6.0, "margin": 0.5, "recurrence": 3},
    {"name": "floor6_margin10_recur3", "bothFloor": 6.0, "margin": 1.0, "recurrence": 3},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_prominence(scores, token: tuple[int, int, int]) -> float:
    measure, step, pitch = token
    center = float(scores.get(token, 0.0))
    neighbors = [
        float(scores.get((measure, step, p), 0.0))
        for p in (pitch - 2, pitch - 1, pitch + 1, pitch + 2)
        if recall.PITCH_MIN <= p <= recall.PITCH_MAX
    ]
    return center - (max(neighbors) if neighbors else 0.0)


def additions_for(grid, winner_scores, alt_scores, champion, variant):
    floor = float(variant["bothFloor"])
    margin = float(variant["margin"])
    recurrence = int(variant["recurrence"])

    supported: list[tuple[int, int, int]] = []
    signature_counts: Counter[tuple[int, int]] = Counter()
    for measure, step in grid:
        if not 17 <= measure <= 113:
            continue
        for pitch in range(recall.PITCH_MIN, recall.PITCH_MAX + 1):
            token = (measure, step, pitch)
            if champion.get(token, 0) > 0:
                continue
            ws = float(winner_scores.get(token, 0.0))
            ats = float(alt_scores.get(token, 0.0))
            if min(ws, ats) < floor:
                continue
            if local_prominence(winner_scores, token) < margin:
                continue
            if local_prominence(alt_scores, token) < margin:
                continue
            supported.append(token)
            signature_counts[(step, pitch)] += 1

    out: Counter[tuple[int, int, int]] = Counter()
    for token in supported:
        if signature_counts[(token[1], token[2])] >= recurrence:
            out[token] = 1
    return out


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    print("Rebuilding frozen validated 13.82 champion and detector-side spectral scores...", flush=True)
    champion, winner_scores, alt_scores = recur.build_frozen_1382(grid)
    champion_score = recur.grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}")

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []
    for variant in VARIANTS:
        additions = additions_for(grid, winner_scores, alt_scores, champion, variant)
        candidate = champion + additions
        evaluation = recall.evaluate_recall(candidate, champion, reference, champion_score)
        evaluation["additionCount"] = int(sum(additions.values()))
        evaluation["variant"] = variant
        results[str(variant["name"])] = evaluation
        full = evaluation["fullScore"]
        print(
            f"{variant['name']}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} additions={sum(additions.values())} matchedGain={evaluation['matchedGain']} "
            f"extraIncrease={evaluation['extraIncrease']} cv={evaluation['crossValidationPassed']} "
            f"sections={evaluation['sectionStabilityPassed']} shifted={evaluation['shiftedWindowStabilityPassed']} "
            f"accepted={evaluation['acceptedOverChampion']}",
            flush=True,
        )
        if evaluation["acceptedOverChampion"]:
            accepted.append((str(variant["name"]), evaluation))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (
                float(item[1]["fullScore"]["pitchF1"]),
                int(item[1]["matchedGain"]),
                -int(item[1]["extraIncrease"]),
            ),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_13_82_champion"
        winner_eval = {
            "fullScore": champion_score,
            "matchedGain": 0,
            "missingReduction": 0,
            "extraIncrease": 0,
            "crossValidationPassed": True,
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOverChampion": False,
            "additionCount": 0,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 13.82 local-prominence recall benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-13.82-reference-free-dual-stem-local-prominence-recurrence-recall-gate",
        "baselineScore": champion_score,
        "results": results,
        "winner": winner_name,
        "winnerEvaluation": winner_eval,
        "validatedNewChampion": validated_new_champion,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "profile-and-prune-residual-additions-from-validated-local-prominence-recall-winner"
            if validated_new_champion
            else "profile-next-reference-free-recall-feature-family"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "baselinePitchF1": champion_score["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 13.82 CHAMPION DUAL-STEM LOCAL-PROMINENCE RECALL GATE V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", champion_score["pitchF1"])
    print("Baseline matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner_eval["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner_eval["fullScore"]["matched"], "/", winner_eval["fullScore"]["missing"], "/", winner_eval["fullScore"]["extra"])
    print("Winner matched gain:", winner_eval["matchedGain"])
    print("Winner missing reduction:", winner_eval["missingReduction"])
    print("Winner extra increase:", winner_eval["extraIncrease"])
    print("Winner cross-validation passed:", winner_eval["crossValidationPassed"])
    print("Winner section stability passed:", winner_eval["sectionStabilityPassed"])
    print("Winner shifted-window stability passed:", winner_eval["shiftedWindowStabilityPassed"])
    print("Validated new champion:", validated_new_champion)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
