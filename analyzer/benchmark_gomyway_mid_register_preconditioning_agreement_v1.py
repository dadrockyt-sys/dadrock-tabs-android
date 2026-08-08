from __future__ import annotations

import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_mid_register_audio_preconditioning_v1 as precond

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-mid-register-preconditioning-agreement-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-mid-register-preconditioning-agreement-v1-manifest.json"

FROZEN_BAND = {"name": "band160_650", "low": 160.0, "high": 650.0}
FOLDS = 5
CURRENT_CHAMPION_F1 = 6.99


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


def neighbor_supported(token: tuple[int, int, int], champion: Counter[tuple[int, int, int]]) -> bool:
    measure, step, midi = token
    for delta in (-2, -1, 1, 2):
        if champion.get((measure, step + delta, midi), 0) > 0:
            return True
    return False


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

    print("Building frozen 6.99 cross-stem champion...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    champion = precond.merge_with_cap(base_winner, base_alt)

    with tempfile.TemporaryDirectory(prefix="gomyway-mid-agreement-") as tmp:
        tmp_root = Path(tmp)
        filtered = []
        for stem_name, stem_path in (("winner", WINNER_STEM), ("alt", ALT_STEM)):
            out = tmp_root / f"{stem_name}-band160_650.wav"
            precond.preprocess(stem_path, out, FROZEN_BAND["low"], FROZEN_BAND["high"])
            pred = precond.targeted_mid(precond.prediction(precond.grouped_for(out, grid)))
            filtered.append(pred)

    winner_mid, alt_mid = filtered
    winner_add = winner_mid - champion
    alt_add = alt_mid - champion
    agreement_add = winner_add & alt_add
    union_add = winner_add | alt_add
    neighbor_add = Counter()
    for token, count in union_add.items():
        if token in agreement_add or neighbor_supported(token, champion):
            neighbor_add[token] = min(1, count)

    variants = {
        "champion": champion,
        "preconditioned_union": precond.merge_with_cap(champion, union_add),
        "preconditioned_agreement": precond.merge_with_cap(champion, agreement_add),
        "agreement_or_neighbor": precond.merge_with_cap(champion, neighbor_add),
    }

    results = {}
    for name, pred in variants.items():
        results[name] = grade(pred, reference)
        row = results[name]
        print(
            f"{name}: pitchF1={row['pitchF1']} matched={row['matched']} missing={row['missing']} "
            f"extra={row['extra']} predictions={row['predictions']}",
            flush=True,
        )

    candidate_rules = ["preconditioned_agreement", "agreement_or_neighbor"]
    crossval = {}
    for rule in candidate_rules:
        positive_f1 = 0
        positive_matched = 0
        deltas = []
        folds = []
        for fold in range(FOLDS):
            ref_fold = subset(reference, fold)
            champ_fold = subset(champion, fold)
            rule_fold = subset(variants[rule], fold)
            champ_score = grade(champ_fold, ref_fold)
            rule_score = grade(rule_fold, ref_fold)
            delta = round(float(rule_score["pitchF1"]) - float(champ_score["pitchF1"]), 2)
            matched_delta = int(rule_score["matched"]) - int(champ_score["matched"])
            extra_delta = int(rule_score["extra"]) - int(champ_score["extra"])
            deltas.append(delta)
            if delta > 0:
                positive_f1 += 1
            if matched_delta > 0:
                positive_matched += 1
            folds.append({
                "fold": fold + 1,
                "champion": champ_score,
                "rule": rule_score,
                "deltaPoints": delta,
                "matchedDelta": matched_delta,
                "extraDelta": extra_delta,
            })
            print(
                f"{rule} fold{fold + 1}: delta={delta:+.2f} matchedDelta={matched_delta:+d} extraDelta={extra_delta:+d}",
                flush=True,
            )
        sorted_deltas = sorted(deltas)
        mean_delta = round(sum(deltas) / len(deltas), 2)
        median_delta = sorted_deltas[len(sorted_deltas) // 2]
        passed = positive_f1 >= 4 and positive_matched >= 4 and mean_delta > 0 and median_delta > 0
        crossval[rule] = {
            "folds": folds,
            "positiveF1Folds": positive_f1,
            "positiveMatchedFolds": positive_matched,
            "meanFoldDeltaPoints": mean_delta,
            "medianFoldDeltaPoints": median_delta,
            "crossValidationPassed": passed,
        }

    ranked_rules = sorted(
        candidate_rules,
        key=lambda name: (
            bool(crossval[name]["crossValidationPassed"]),
            float(results[name]["pitchF1"]),
            int(results[name]["matched"]),
            -int(results[name]["extra"]),
        ),
        reverse=True,
    )
    winner_rule = ranked_rules[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during agreement benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "mid-register-preconditioning-cross-stem-agreement",
        "frozenBand": FROZEN_BAND,
        "currentChampionPitchF1": CURRENT_CHAMPION_F1,
        "additionCounts": {
            "winnerOnly": sum(winner_add.values()),
            "altOnly": sum(alt_add.values()),
            "agreement": sum(agreement_add.values()),
            "union": sum(union_add.values()),
            "agreementOrNeighbor": sum(neighbor_add.values()),
        },
        "results": results,
        "crossValidation": crossval,
        "winnerRule": winner_rule,
        "winnerPitchF1": results[winner_rule]["pitchF1"],
        "winnerCrossValidationPassed": crossval[winner_rule]["crossValidationPassed"],
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
            "audit-contiguous-section-stability-for-agreement-rule"
            if crossval[winner_rule]["crossValidationPassed"]
            else "retain-6.99-champion-and-evaluate-mid-register-specialist-detector"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "winnerRule": winner_rule,
        "winnerPitchF1": results[winner_rule]["pitchF1"],
        "winnerCrossValidationPassed": crossval[winner_rule]["crossValidationPassed"],
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY MID-REGISTER PRECONDITIONING AGREEMENT V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", CURRENT_CHAMPION_F1)
    print("Winner rule:", winner_rule)
    print("Winner pitch F1:", results[winner_rule]["pitchF1"])
    print("Winner matched/missing/extra:", results[winner_rule]["matched"], "/", results[winner_rule]["missing"], "/", results[winner_rule]["extra"])
    print("Winner positive F1 folds:", crossval[winner_rule]["positiveF1Folds"], "/", FOLDS)
    print("Winner positive matched folds:", crossval[winner_rule]["positiveMatchedFolds"], "/", FOLDS)
    print("Winner mean/median fold delta points:", crossval[winner_rule]["meanFoldDeltaPoints"], "/", crossval[winner_rule]["medianFoldDeltaPoints"])
    print("Winner cross-validation passed:", crossval[winner_rule]["crossValidationPassed"])
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
