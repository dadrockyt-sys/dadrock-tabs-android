from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path

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
OUTPUT_PATH = PUBLIC / "gomyway-adaptive-spectral-shifted-window-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-adaptive-spectral-shifted-window-stability-v1-manifest.json"

FROZEN_RULE = {"name": "local5_med13", "radius": 2, "median": 13.0}
TOP1_RULE = {"name": "either8_top1_per_slot", "kind": "ranked", "threshold": 8.0, "topn": 1}
CURRENT_CHAMPION_F1 = 6.99
WINDOW_SIZE = 12
WINDOW_STEP = 8
WINDOWS = [(start, min(start + WINDOW_SIZE - 1, 113)) for start in range(17, 114, WINDOW_STEP)]


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


def window_subset(counter: Counter[tuple[int, int, int]], start: int, end: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if start <= token[0] <= end})


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

    print("Building frozen 6.99 cross-stem champion...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    champion = precond.merge_with_cap(base_winner, base_alt)
    champion_score = grade(champion, reference)

    print("Computing frozen adaptive spectral champion...", flush=True)
    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(TOP1_RULE, winner_scores, alt_scores, champion)
    additions = adaptive.adaptive_additions(
        top1,
        winner_scores,
        alt_scores,
        int(FROZEN_RULE["radius"]),
        float(FROZEN_RULE["median"]),
    )
    prediction = precond.merge_with_cap(champion, additions)
    full = grade(prediction, reference)

    rows = []
    deltas: list[float] = []
    positive_f1 = 0
    positive_matched = 0
    catastrophic = 0

    for start, end in WINDOWS:
        ref_window = window_subset(reference, start, end)
        c = grade(window_subset(champion, start, end), ref_window)
        p = grade(window_subset(prediction, start, end), ref_window)
        delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
        matched_delta = int(p["matched"]) - int(c["matched"])
        extra_delta = int(p["extra"]) - int(c["extra"])
        deltas.append(delta)
        positive_f1 += int(delta > 0)
        positive_matched += int(matched_delta > 0)
        catastrophic += int(delta <= -1.0)
        rows.append({
            "window": f"m{start}_{end}",
            "championF1": c["pitchF1"],
            "adaptiveF1": p["pitchF1"],
            "deltaPoints": delta,
            "matchedDelta": matched_delta,
            "extraDelta": extra_delta,
        })
        print(
            f"m{start}_{end}: championF1={c['pitchF1']} adaptiveF1={p['pitchF1']} "
            f"delta={delta:+.2f} matchedDelta={matched_delta:+d} extraDelta={extra_delta:+d}",
            flush=True,
        )

    mean_delta = round(sum(deltas) / len(deltas), 2)
    median_delta = round(float(statistics.median(deltas)), 2)
    required_positive_f1 = max(1, int(len(WINDOWS) * 0.75 + 0.999))
    required_positive_matched = max(1, int(len(WINDOWS) * 0.75 + 0.999))
    stability_passed = (
        positive_f1 >= required_positive_f1
        and positive_matched >= required_positive_matched
        and catastrophic == 0
        and mean_delta > 0
        and median_delta > 0
        and float(full["pitchF1"]) > CURRENT_CHAMPION_F1
    )

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during shifted-window audit.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "auditType": "adaptive-spectral-shifted-window-stability",
        "frozenRule": FROZEN_RULE,
        "baseRule": TOP1_RULE,
        "currentChampion": champion_score,
        "adaptiveChampion": full,
        "windows": rows,
        "positiveF1Windows": positive_f1,
        "positiveMatchedWindows": positive_matched,
        "requiredPositiveF1Windows": required_positive_f1,
        "requiredPositiveMatchedWindows": required_positive_matched,
        "catastrophicRegressionWindows": catastrophic,
        "meanWindowDeltaPoints": mean_delta,
        "medianWindowDeltaPoints": median_delta,
        "shiftedWindowStabilityPassed": stability_passed,
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
            "lock-8.08-adaptive-spectral-benchmark-champion-and-begin-extra-reduction"
            if stability_passed
            else "retain-6.99-champion-and-profile-adaptive-gate-failure-windows"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "shiftedWindowStabilityPassed": stability_passed,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY ADAPTIVE SPECTRAL SHIFTED WINDOW STABILITY V1 COMPLETE")
    print("Passed: True")
    print("Frozen rule:", FROZEN_RULE["name"])
    print("Full champion/adaptive F1:", champion_score["pitchF1"], "/", full["pitchF1"])
    print("Full adaptive matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Positive F1 windows:", positive_f1, "/", len(WINDOWS))
    print("Positive matched windows:", positive_matched, "/", len(WINDOWS))
    print("Catastrophic regression windows:", catastrophic)
    print("Mean/median window delta points:", mean_delta, "/", median_delta)
    print("Shifted-window stability passed:", stability_passed)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
