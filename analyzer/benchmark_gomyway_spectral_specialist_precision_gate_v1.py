from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_mid_register_audio_preconditioning_v1 as precond
import benchmark_gomyway_mid_register_spectral_specialist_v1 as spectral

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-spectral-specialist-precision-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-spectral-specialist-precision-gate-v1-manifest.json"

FOLDS = 5
BLOCKS = [(17, 32), (33, 48), (49, 64), (65, 80), (81, 96), (97, 113)]
CURRENT_CHAMPION_F1 = 6.99

# These rules use detector-side spectral evidence only. They are intentionally
# declared before scoring so the professional reference cannot steer detection.
RULES: list[dict[str, Any]] = [
    {"name": "both8", "kind": "both", "threshold": 8.0},
    {"name": "both10", "kind": "both", "threshold": 10.0},
    {"name": "either12", "kind": "either", "threshold": 12.0},
    {"name": "either16", "kind": "either", "threshold": 16.0},
    {"name": "both8_or_either16", "kind": "hybrid", "both": 8.0, "either": 16.0},
    {"name": "either8_top1_per_slot", "kind": "ranked", "threshold": 8.0, "topn": 1},
    {"name": "either8_top2_per_slot", "kind": "ranked", "threshold": 8.0, "topn": 2},
    {"name": "hybrid_top2_per_slot", "kind": "hybrid_ranked", "both": 8.0, "either": 12.0, "topn": 2},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grade(predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]]) -> dict[str, float | int]:
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    expected = sum(reference.values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())
    return {
        "pitchF1": round(100.0 * v2.f1(matched, predicted_count, expected), 2),
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "predictions": predicted_count,
    }


def subset(counter: Counter[tuple[int, int, int]], fold: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if ((token[0] - 17) % FOLDS) == fold})


def block_subset(counter: Counter[tuple[int, int, int]], start: int, end: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if start <= token[0] <= end})


def accepted_tokens(
    rule: dict[str, Any],
    winner_scores: dict[tuple[int, int, int], float],
    alt_scores: dict[tuple[int, int, int], float],
    champion: Counter[tuple[int, int, int]],
) -> Counter[tuple[int, int, int]]:
    eligible: list[tuple[tuple[int, int, int], float]] = []
    kind = str(rule["kind"])
    for token in winner_scores:
        if champion.get(token, 0) > 0:
            continue
        w = float(winner_scores.get(token, 0.0))
        a = float(alt_scores.get(token, 0.0))
        best = max(w, a)
        if kind == "both":
            ok = w >= float(rule["threshold"]) and a >= float(rule["threshold"])
        elif kind == "either":
            ok = best >= float(rule["threshold"])
        elif kind == "hybrid":
            ok = (w >= float(rule["both"]) and a >= float(rule["both"])) or best >= float(rule["either"])
        elif kind == "ranked":
            ok = best >= float(rule["threshold"])
        elif kind == "hybrid_ranked":
            ok = (w >= float(rule["both"]) and a >= float(rule["both"])) or best >= float(rule["either"])
        else:
            raise ValueError(kind)
        if ok:
            eligible.append((token, best))

    if kind not in {"ranked", "hybrid_ranked"}:
        return Counter({token: 1 for token, _score in eligible})

    by_slot: dict[tuple[int, int], list[tuple[tuple[int, int, int], float]]] = defaultdict(list)
    for token, score in eligible:
        by_slot[(token[0], token[1])].append((token, score))
    result: Counter[tuple[int, int, int]] = Counter()
    topn = int(rule["topn"])
    for rows in by_slot.values():
        rows.sort(key=lambda row: (row[1], -row[0][2]), reverse=True)
        for token, _score in rows[:topn]:
            result[token] = 1
    return result


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
    if sum(reference.values()) != 867:
        raise RuntimeError(f"Expected 867 professional pitch tokens, found {sum(reference.values())}")

    print("Building frozen 6.99 cross-stem champion...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    champion = precond.merge_with_cap(base_winner, base_alt)
    champion_score = grade(champion, reference)

    print("Computing spectral evidence once...", flush=True)
    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)

    results: dict[str, Any] = {}
    for rule in RULES:
        additions = accepted_tokens(rule, winner_scores, alt_scores, champion)
        prediction = precond.merge_with_cap(champion, additions)
        full = grade(prediction, reference)

        fold_deltas: list[float] = []
        positive_f1_folds = 0
        positive_matched_folds = 0
        fold_rows = []
        for fold in range(FOLDS):
            ref_fold = subset(reference, fold)
            c = grade(subset(champion, fold), ref_fold)
            p = grade(subset(prediction, fold), ref_fold)
            delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
            md = int(p["matched"]) - int(c["matched"])
            ed = int(p["extra"]) - int(c["extra"])
            fold_deltas.append(delta)
            positive_f1_folds += int(delta > 0)
            positive_matched_folds += int(md > 0)
            fold_rows.append({"fold": fold + 1, "deltaPoints": delta, "matchedDelta": md, "extraDelta": ed})
        mean_fold = round(sum(fold_deltas) / len(fold_deltas), 2)
        median_fold = sorted(fold_deltas)[len(fold_deltas) // 2]
        cv_passed = positive_f1_folds >= 4 and positive_matched_folds >= 4 and mean_fold > 0 and median_fold > 0

        block_deltas: list[float] = []
        positive_f1_blocks = 0
        positive_matched_blocks = 0
        catastrophic = 0
        block_rows = []
        for start, end in BLOCKS:
            ref_block = block_subset(reference, start, end)
            c = grade(block_subset(champion, start, end), ref_block)
            p = grade(block_subset(prediction, start, end), ref_block)
            delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
            md = int(p["matched"]) - int(c["matched"])
            ed = int(p["extra"]) - int(c["extra"])
            block_deltas.append(delta)
            positive_f1_blocks += int(delta > 0)
            positive_matched_blocks += int(md > 0)
            catastrophic += int(delta <= -1.0)
            block_rows.append({"block": f"m{start}_{end}", "deltaPoints": delta, "matchedDelta": md, "extraDelta": ed})
        mean_block = round(sum(block_deltas) / len(block_deltas), 2)
        median_block = sorted(block_deltas)[len(block_deltas) // 2]
        section_passed = positive_f1_blocks >= 5 and positive_matched_blocks == len(BLOCKS) and catastrophic == 0 and mean_block > 0 and median_block > 0
        accepted = cv_passed and section_passed and float(full["pitchF1"]) > CURRENT_CHAMPION_F1

        results[str(rule["name"])] = {
            "rule": rule,
            "additionCount": sum(additions.values()),
            "fullScore": full,
            "folds": fold_rows,
            "positiveF1Folds": positive_f1_folds,
            "positiveMatchedFolds": positive_matched_folds,
            "meanFoldDeltaPoints": mean_fold,
            "medianFoldDeltaPoints": median_fold,
            "crossValidationPassed": cv_passed,
            "blocks": block_rows,
            "positiveF1Blocks": positive_f1_blocks,
            "positiveMatchedBlocks": positive_matched_blocks,
            "catastrophicRegressionBlocks": catastrophic,
            "meanBlockDeltaPoints": mean_block,
            "medianBlockDeltaPoints": median_block,
            "sectionStabilityPassed": section_passed,
            "acceptedOverChampion": accepted,
        }
        print(
            f"{rule['name']}: F1={full['pitchF1']} matched={full['matched']} extra={full['extra']} additions={sum(additions.values())} "
            f"cv={cv_passed} folds={positive_f1_folds}/5 section={section_passed} blocks={positive_f1_blocks}/6 "
            f"cat={catastrophic} accepted={accepted}",
            flush=True,
        )

    ranked = sorted(
        results.items(),
        key=lambda item: (
            bool(item[1]["acceptedOverChampion"]),
            bool(item[1]["sectionStabilityPassed"]),
            bool(item[1]["crossValidationPassed"]),
            float(item[1]["fullScore"]["pitchF1"]),
            int(item[1]["fullScore"]["matched"]),
            -int(item[1]["fullScore"]["extra"]),
        ),
        reverse=True,
    )
    winner_name, winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during precision gate benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "spectral-specialist-detector-side-precision-gates",
        "currentChampion": champion_score,
        "rules": RULES,
        "results": results,
        "winner": winner_name,
        "winnerAccepted": winner["acceptedOverChampion"],
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
            "lock-precision-gated-spectral-specialist-as-benchmark-champion"
            if winner["acceptedOverChampion"]
            else "retain-6.99-champion-and-stop-global-spectral-admission"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "winner": winner_name,
        "winnerAccepted": winner["acceptedOverChampion"],
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY SPECTRAL SPECIALIST PRECISION GATE V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", champion_score["pitchF1"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner["fullScore"]["matched"], "/", winner["fullScore"]["missing"], "/", winner["fullScore"]["extra"])
    print("Winner additions:", winner["additionCount"])
    print("Winner positive F1 folds:", winner["positiveF1Folds"], "/", FOLDS)
    print("Winner positive matched folds:", winner["positiveMatchedFolds"], "/", FOLDS)
    print("Winner cross-validation passed:", winner["crossValidationPassed"])
    print("Winner positive F1 blocks:", winner["positiveF1Blocks"], "/", len(BLOCKS))
    print("Winner positive matched blocks:", winner["positiveMatchedBlocks"], "/", len(BLOCKS))
    print("Winner catastrophic regression blocks:", winner["catastrophicRegressionBlocks"])
    print("Winner section stability passed:", winner["sectionStabilityPassed"])
    print("Winner accepted over 6.99 champion:", winner["acceptedOverChampion"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
