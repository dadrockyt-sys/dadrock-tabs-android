from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_mid_register_audio_preconditioning_v1 as precond
import benchmark_gomyway_mid_register_spectral_specialist_v1 as spectral
import benchmark_gomyway_spectral_specialist_precision_gate_v1 as gate
import benchmark_gomyway_spectral_top1_adaptive_local_gate_v1 as adaptive

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-adaptive-spectral-temporal-recurrence-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-adaptive-spectral-temporal-recurrence-gate-v1-manifest.json"

FOLDS = 5
BLOCKS = [(17, 32), (33, 48), (49, 64), (65, 80), (81, 96), (97, 113)]
SHIFTED_WINDOWS = [(17, 28), (25, 36), (33, 44), (41, 52), (49, 60), (57, 68), (65, 76), (73, 84), (81, 92), (89, 100), (97, 108), (105, 113)]
CURRENT_CHAMPION_F1 = 6.99
TOP1_RULE = {"name": "either8_top1_per_slot", "kind": "ranked", "threshold": 8.0, "topn": 1}
FROZEN_ADAPTIVE_RULE = {"name": "local5_med13", "radius": 2, "median": 13.0}

# All rules are detector-side and fixed before grading.
RULES = [
    {"name": "repeat_m1_step1", "measureRadius": 1, "stepRadius": 1, "bothFloor": None},
    {"name": "repeat_m2_step1", "measureRadius": 2, "stepRadius": 1, "bothFloor": None},
    {"name": "repeat_m2_step2", "measureRadius": 2, "stepRadius": 2, "bothFloor": None},
    {"name": "repeat_m1_step1_or_both10", "measureRadius": 1, "stepRadius": 1, "bothFloor": 10.0},
    {"name": "repeat_m2_step1_or_both10", "measureRadius": 2, "stepRadius": 1, "bothFloor": 10.0},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grade(predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]]) -> dict[str, float | int]:
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    expected = sum(reference.values())
    return {
        "pitchF1": round(100.0 * v2.f1(matched, predicted_count, expected), 2),
        "matched": matched,
        "missing": sum((reference - predicted).values()),
        "extra": sum((predicted - reference).values()),
        "predictions": predicted_count,
    }


def fold_subset(counter: Counter[tuple[int, int, int]], fold: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if ((token[0] - 17) % FOLDS) == fold})


def range_subset(counter: Counter[tuple[int, int, int]], start: int, end: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if start <= token[0] <= end})


def recurrent(
    token: tuple[int, int, int],
    pool: set[tuple[int, int, int]],
    measure_radius: int,
    step_radius: int,
) -> bool:
    measure, step, pitch = token
    for other_measure in range(max(17, measure - measure_radius), min(113, measure + measure_radius) + 1):
        for other_step in range(max(0, step - step_radius), step + step_radius + 1):
            other = (other_measure, other_step, pitch)
            if other != token and other in pool:
                return True
    return False


def recurrence_gate(
    additions: Counter[tuple[int, int, int]],
    winner_scores: dict[tuple[int, int, int], float],
    alt_scores: dict[tuple[int, int, int], float],
    rule: dict[str, Any],
) -> Counter[tuple[int, int, int]]:
    pool = set(additions)
    accepted: Counter[tuple[int, int, int]] = Counter()
    for token in additions:
        keep = recurrent(token, pool, int(rule["measureRadius"]), int(rule["stepRadius"]))
        both_floor = rule.get("bothFloor")
        if both_floor is not None:
            keep = keep or (
                float(winner_scores.get(token, 0.0)) >= float(both_floor)
                and float(alt_scores.get(token, 0.0)) >= float(both_floor)
            )
        if keep:
            accepted[token] = 1
    return accepted


def evaluate_ranges(
    prediction: Counter[tuple[int, int, int]],
    champion: Counter[tuple[int, int, int]],
    reference: Counter[tuple[int, int, int]],
    ranges: list[tuple[int, int]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    positive_f1 = positive_matched = catastrophic = 0
    deltas: list[float] = []
    for start, end in ranges:
        ref = range_subset(reference, start, end)
        c = grade(range_subset(champion, start, end), ref)
        p = grade(range_subset(prediction, start, end), ref)
        delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
        matched_delta = int(p["matched"]) - int(c["matched"])
        extra_delta = int(p["extra"]) - int(c["extra"])
        positive_f1 += int(delta > 0)
        positive_matched += int(matched_delta > 0)
        catastrophic += int(delta <= -1.0)
        deltas.append(delta)
        rows.append({
            "range": f"m{start}_{end}",
            "deltaPoints": delta,
            "matchedDelta": matched_delta,
            "extraDelta": extra_delta,
        })
    return {
        "rows": rows,
        "positiveF1": positive_f1,
        "positiveMatched": positive_matched,
        "catastrophic": catastrophic,
        "meanDelta": round(sum(deltas) / len(deltas), 2),
        "medianDelta": round(float(statistics.median(deltas)), 2),
    }


def main() -> None:
    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    print("Building frozen 6.99 champion and local5_med13 additions...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    champion = precond.merge_with_cap(base_winner, base_alt)
    champion_score = grade(champion, reference)

    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(TOP1_RULE, winner_scores, alt_scores, champion)
    adaptive_base = adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)

    results: dict[str, Any] = {}
    for rule in RULES:
        additions = recurrence_gate(adaptive_base, winner_scores, alt_scores, rule)
        prediction = precond.merge_with_cap(champion, additions)
        full = grade(prediction, reference)

        fold_deltas: list[float] = []
        pf = pm = 0
        for fold in range(FOLDS):
            ref_fold = fold_subset(reference, fold)
            c = grade(fold_subset(champion, fold), ref_fold)
            p = grade(fold_subset(prediction, fold), ref_fold)
            delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
            fold_deltas.append(delta)
            pf += int(delta > 0)
            pm += int(int(p["matched"]) > int(c["matched"]))
        mean_fold = round(sum(fold_deltas) / FOLDS, 2)
        median_fold = round(float(statistics.median(fold_deltas)), 2)
        cv_passed = pf >= 4 and pm >= 4 and mean_fold > 0 and median_fold > 0

        blocks = evaluate_ranges(prediction, champion, reference, BLOCKS)
        section_passed = (
            int(blocks["positiveF1"]) >= 5
            and int(blocks["positiveMatched"]) >= 5
            and int(blocks["catastrophic"]) == 0
            and float(blocks["meanDelta"]) > 0
            and float(blocks["medianDelta"]) > 0
        )

        windows = evaluate_ranges(prediction, champion, reference, SHIFTED_WINDOWS)
        shifted_passed = (
            int(windows["positiveF1"]) >= 9
            and int(windows["positiveMatched"]) >= 9
            and int(windows["catastrophic"]) == 0
            and float(windows["meanDelta"]) > 0
            and float(windows["medianDelta"]) > 0
        )

        accepted = (
            float(full["pitchF1"]) > CURRENT_CHAMPION_F1
            and cv_passed
            and section_passed
            and shifted_passed
        )

        results[str(rule["name"])] = {
            "rule": rule,
            "additionCount": sum(additions.values()),
            "fullScore": full,
            "positiveF1Folds": pf,
            "positiveMatchedFolds": pm,
            "meanFoldDeltaPoints": mean_fold,
            "medianFoldDeltaPoints": median_fold,
            "crossValidationPassed": cv_passed,
            "sectionAudit": blocks,
            "sectionStabilityPassed": section_passed,
            "shiftedWindowAudit": windows,
            "shiftedWindowStabilityPassed": shifted_passed,
            "acceptedOverChampion": accepted,
        }
        print(
            f"{rule['name']}: F1={full['pitchF1']} matched={full['matched']} extra={full['extra']} additions={sum(additions.values())} "
            f"cv={cv_passed} folds={pf}/5 sections={blocks['positiveF1']}/6 shifted={windows['positiveF1']}/12 "
            f"cat={windows['catastrophic']} accepted={accepted}",
            flush=True,
        )

    ranked = sorted(results.items(), key=lambda item: (
        bool(item[1]["acceptedOverChampion"]),
        bool(item[1]["shiftedWindowStabilityPassed"]),
        bool(item[1]["sectionStabilityPassed"]),
        bool(item[1]["crossValidationPassed"]),
        float(item[1]["fullScore"]["pitchF1"]),
        int(item[1]["fullScore"]["matched"]),
        -int(item[1]["fullScore"]["extra"]),
    ), reverse=True)
    winner_name, winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during temporal recurrence benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "adaptive-spectral-temporal-recurrence-detector-side-gate",
        "currentChampion": champion_score,
        "frozenAdaptiveRule": FROZEN_ADAPTIVE_RULE,
        "rules": RULES,
        "results": results,
        "winner": winner_name,
        "winnerAccepted": bool(winner["acceptedOverChampion"]),
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "lock-temporal-recurrence-spectral-champion" if winner["acceptedOverChampion"] else "retain-6.99-and-profile-temporal-specialist-errors",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "winner": winner_name,
        "winnerAccepted": bool(winner["acceptedOverChampion"]),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY ADAPTIVE SPECTRAL TEMPORAL RECURRENCE GATE V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", champion_score["pitchF1"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner["fullScore"]["matched"], "/", winner["fullScore"]["missing"], "/", winner["fullScore"]["extra"])
    print("Winner additions:", winner["additionCount"])
    print("Winner positive F1 folds:", winner["positiveF1Folds"], "/", FOLDS)
    print("Winner positive matched folds:", winner["positiveMatchedFolds"], "/", FOLDS)
    print("Winner cross-validation passed:", winner["crossValidationPassed"])
    print("Winner positive F1 blocks:", winner["sectionAudit"]["positiveF1"], "/", len(BLOCKS))
    print("Winner catastrophic block regressions:", winner["sectionAudit"]["catastrophic"])
    print("Winner section stability passed:", winner["sectionStabilityPassed"])
    print("Winner positive shifted windows:", winner["shiftedWindowAudit"]["positiveF1"], "/", len(SHIFTED_WINDOWS))
    print("Winner positive matched shifted windows:", winner["shiftedWindowAudit"]["positiveMatched"], "/", len(SHIFTED_WINDOWS))
    print("Winner catastrophic shifted regressions:", winner["shiftedWindowAudit"]["catastrophic"])
    print("Winner shifted-window stability passed:", winner["shiftedWindowStabilityPassed"])
    print("Winner accepted over 6.99 champion:", winner["acceptedOverChampion"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
