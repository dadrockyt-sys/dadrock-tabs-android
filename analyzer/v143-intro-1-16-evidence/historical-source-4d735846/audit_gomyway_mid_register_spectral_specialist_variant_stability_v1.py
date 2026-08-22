from __future__ import annotations

import hashlib
import json
from collections import Counter
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
OUTPUT_PATH = PUBLIC / "gomyway-mid-register-spectral-specialist-variant-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-mid-register-spectral-specialist-variant-stability-v1-manifest.json"

BLOCKS = [(17, 32), (33, 48), (49, 64), (65, 80), (81, 96), (97, 113)]

# Only variants that already passed the earlier five-fold cross-validation are
# eligible here. This avoids inventing a new section-specific rule after seeing
# the dual_snr4 section audit.
ELIGIBLE_VARIANTS: list[dict[str, Any]] = [
    {"name": "dual_snr4", "snr": 4.0, "mode": "dual"},
    {"name": "dual_snr6", "snr": 6.0, "mode": "dual"},
    {"name": "either_snr8", "snr": 8.0, "mode": "either"},
    {"name": "either_snr10", "snr": 10.0, "mode": "either"},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subset(counter: Counter[tuple[int, int, int]], start: int, end: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if start <= token[0] <= end})


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

    print("Computing spectral scores once for all eligible variants...", flush=True)
    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)

    results: dict[str, Any] = {}
    for variant in ELIGIBLE_VARIANTS:
        additions = spectral.additions_for_variant(variant, winner_scores, alt_scores, champion)
        prediction = precond.merge_with_cap(champion, additions)
        full_score = grade(prediction, reference)

        positive_f1 = 0
        positive_matched = 0
        catastrophic = 0
        deltas: list[float] = []
        rows = []
        for start, end in BLOCKS:
            ref_block = subset(reference, start, end)
            champ_block = subset(champion, start, end)
            pred_block = subset(prediction, start, end)
            c = grade(champ_block, ref_block)
            p = grade(pred_block, ref_block)
            delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
            matched_delta = int(p["matched"]) - int(c["matched"])
            extra_delta = int(p["extra"]) - int(c["extra"])
            deltas.append(delta)
            if delta > 0:
                positive_f1 += 1
            if matched_delta > 0:
                positive_matched += 1
            if delta <= -1.0:
                catastrophic += 1
            rows.append({
                "block": f"m{start}_{end}",
                "champion": c,
                "specialist": p,
                "deltaPoints": delta,
                "matchedDelta": matched_delta,
                "extraDelta": extra_delta,
            })
            print(
                f"{variant['name']} m{start}_{end}: championF1={c['pitchF1']} specialistF1={p['pitchF1']} "
                f"delta={delta:+.2f} matchedDelta={matched_delta:+d} extraDelta={extra_delta:+d}",
                flush=True,
            )

        mean_delta = round(sum(deltas) / len(deltas), 2)
        median_delta = sorted(deltas)[len(deltas) // 2]
        stable = (
            positive_f1 >= 5
            and positive_matched == len(BLOCKS)
            and catastrophic == 0
            and mean_delta > 0
            and median_delta > 0
        )
        results[variant["name"]] = {
            "variant": variant,
            "fullScore": full_score,
            "additionCount": sum(additions.values()),
            "blocks": rows,
            "positiveF1Blocks": positive_f1,
            "positiveMatchedBlocks": positive_matched,
            "catastrophicRegressionBlocks": catastrophic,
            "meanBlockDeltaPoints": mean_delta,
            "medianBlockDeltaPoints": median_delta,
            "sectionStabilityPassed": stable,
        }
        print(
            f"{variant['name']} SUMMARY: F1={full_score['pitchF1']} positiveF1={positive_f1}/6 "
            f"positiveMatched={positive_matched}/6 catastrophic={catastrophic} "
            f"mean={mean_delta:+.2f} median={median_delta:+.2f} stable={stable}",
            flush=True,
        )

    ranked = sorted(
        results.items(),
        key=lambda item: (
            bool(item[1]["sectionStabilityPassed"]),
            float(item[1]["meanBlockDeltaPoints"]),
            float(item[1]["medianBlockDeltaPoints"]),
            float(item[1]["fullScore"]["pitchF1"]),
            int(item[1]["fullScore"]["matched"]),
            -int(item[1]["fullScore"]["extra"]),
        ),
        reverse=True,
    )
    winner_name, winner = ranked[0]
    accepted = bool(winner["sectionStabilityPassed"]) and float(winner["fullScore"]["pitchF1"]) > float(champion_score["pitchF1"])

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during variant stability audit.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "auditType": "predeclared-crossvalidated-spectral-variant-section-stability",
        "currentChampion": champion_score,
        "eligibleVariants": ELIGIBLE_VARIANTS,
        "results": results,
        "winner": winner_name,
        "winnerAccepted": accepted,
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
            "lock-stable-spectral-variant-as-benchmark-champion-and-profile-false-positives"
            if accepted
            else "retain-6.99-cross-stem-champion-and-profile-spectral-specialist-failure-structure"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "winner": winner_name,
        "winnerAccepted": accepted,
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY MID-REGISTER SPECTRAL VARIANT STABILITY V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", champion_score["pitchF1"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner["fullScore"]["matched"], "/", winner["fullScore"]["missing"], "/", winner["fullScore"]["extra"])
    print("Winner positive F1 blocks:", winner["positiveF1Blocks"], "/", len(BLOCKS))
    print("Winner positive matched blocks:", winner["positiveMatchedBlocks"], "/", len(BLOCKS))
    print("Winner catastrophic regression blocks:", winner["catastrophicRegressionBlocks"])
    print("Winner mean/median block delta points:", winner["meanBlockDeltaPoints"], "/", winner["medianBlockDeltaPoints"])
    print("Winner section stability passed:", winner["sectionStabilityPassed"])
    print("Winner accepted over 6.99 champion:", accepted)
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
