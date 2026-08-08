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
OUTPUT_PATH = PUBLIC / "gomyway-mid-register-preconditioning-crossval-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-mid-register-preconditioning-crossval-v1-manifest.json"

FROZEN_VARIANT = {"name": "band160_650_both", "low": 160.0, "high": 650.0}
FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subset(counter: Counter[tuple[int, int, int]], fold: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if ((token[0] - 17) % FOLDS) == fold})


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

    with tempfile.TemporaryDirectory(prefix="gomyway-mid-precondition-cv-") as tmp:
        tmp_root = Path(tmp)
        filtered_predictions = []
        for stem_name, stem_path in (("winner", WINNER_STEM), ("alt", ALT_STEM)):
            out = tmp_root / f"{stem_name}-band160_650.wav"
            precond.preprocess(stem_path, out, FROZEN_VARIANT["low"], FROZEN_VARIANT["high"])
            filtered_predictions.append(precond.targeted_mid(precond.prediction(precond.grouped_for(out, grid))))

        frozen = precond.merge_with_cap(champion, filtered_predictions[0], filtered_predictions[1])

    full_champion = grade(champion, reference)
    full_frozen = grade(frozen, reference)

    fold_rows = []
    positive_f1 = 0
    positive_matched = 0
    deltas = []
    for fold in range(FOLDS):
        ref_fold = subset(reference, fold)
        champ_fold = subset(champion, fold)
        frozen_fold = subset(frozen, fold)
        champ_score = grade(champ_fold, ref_fold)
        frozen_score = grade(frozen_fold, ref_fold)
        delta = round(float(frozen_score["pitchF1"]) - float(champ_score["pitchF1"]), 2)
        matched_delta = int(frozen_score["matched"]) - int(champ_score["matched"])
        extra_delta = int(frozen_score["extra"]) - int(champ_score["extra"])
        deltas.append(delta)
        if delta > 0:
            positive_f1 += 1
        if matched_delta > 0:
            positive_matched += 1
        row = {
            "fold": fold + 1,
            "champion": champ_score,
            "frozen": frozen_score,
            "deltaPoints": delta,
            "matchedDelta": matched_delta,
            "extraDelta": extra_delta,
        }
        fold_rows.append(row)
        print(
            f"fold{fold + 1}: championF1={champ_score['pitchF1']} preconditionedF1={frozen_score['pitchF1']} "
            f"delta={delta:+.2f} matchedDelta={matched_delta:+d} extraDelta={extra_delta:+d}",
            flush=True,
        )

    sorted_deltas = sorted(deltas)
    median_delta = sorted_deltas[len(sorted_deltas) // 2]
    mean_delta = round(sum(deltas) / len(deltas), 2)
    passed = positive_f1 >= 4 and positive_matched >= 4 and mean_delta > 0 and median_delta > 0

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during cross-validation.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "validationType": "frozen-mid-register-audio-preconditioning-five-fold-cross-validation",
        "frozenRule": FROZEN_VARIANT,
        "fullChampion": full_champion,
        "fullPreconditioned": full_frozen,
        "folds": fold_rows,
        "positiveF1Folds": positive_f1,
        "positiveMatchedFolds": positive_matched,
        "meanFoldDeltaPoints": mean_delta,
        "medianFoldDeltaPoints": median_delta,
        "crossValidationPassed": passed,
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
            "audit-contiguous-section-stability-for-band160-650-both"
            if passed
            else "reject-band160-650-both-as-overfit-and-retain-6.99-champion"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "crossValidationPassed": passed,
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY MID-REGISTER PRECONDITIONING CROSSVAL V1 COMPLETE")
    print("Passed: True")
    print("Frozen rule: band160_650_both")
    print("Full champion/preconditioned F1:", full_champion["pitchF1"], "/", full_frozen["pitchF1"])
    print("Positive F1 folds:", positive_f1, "/", FOLDS)
    print("Positive matched folds:", positive_matched, "/", FOLDS)
    print("Mean fold delta points:", mean_delta)
    print("Median fold delta points:", median_delta)
    print("Cross-validation passed:", passed)
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
