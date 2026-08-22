from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
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
OUTPUT_PATH = PUBLIC / "gomyway-adaptive-spectral-shifted-window-failure-profile-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-adaptive-spectral-shifted-window-failure-profile-v1-manifest.json"

WINDOWS = [(17, 28), (25, 36), (33, 44), (41, 52), (49, 60), (57, 68), (65, 76), (73, 84), (81, 92), (89, 100), (97, 108), (105, 113), (113, 113)]
FROZEN_RULE = {"name": "local5_med13", "radius": 2, "median": 13.0}
TOP1_RULE = {"name": "either8_top1_per_slot", "kind": "ranked", "threshold": 8.0, "topn": 1}


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


def subset(counter: Counter[tuple[int, int, int]], start: int, end: int) -> Counter[tuple[int, int, int]]:
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

    print("Building frozen 6.99 champion and spectral evidence...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    champion = precond.merge_with_cap(base_winner, base_alt)
    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(TOP1_RULE, winner_scores, alt_scores, champion)
    additions = adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)
    prediction = precond.merge_with_cap(champion, additions)

    champion_slots = {(m, s) for m, s, _p in champion}
    rows: list[dict[str, Any]] = []
    for start, end in WINDOWS:
        add_tokens = [token for token in additions if start <= token[0] <= end]
        scores = [max(float(winner_scores.get(t, 0.0)), float(alt_scores.get(t, 0.0))) for t in add_tokens]
        margins = [abs(float(winner_scores.get(t, 0.0)) - float(alt_scores.get(t, 0.0))) for t in add_tokens]
        both = [t for t in add_tokens if float(winner_scores.get(t, 0.0)) >= 8.0 and float(alt_scores.get(t, 0.0)) >= 8.0]
        occupied = [t for t in add_tokens if (t[0], t[1]) in champion_slots]
        c = grade(subset(champion, start, end), subset(reference, start, end))
        p = grade(subset(prediction, start, end), subset(reference, start, end))
        delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
        md = int(p["matched"]) - int(c["matched"])
        ed = int(p["extra"]) - int(c["extra"])
        span = max(1, end - start + 1)
        row = {
            "window": f"m{start}_{end}",
            "additionCount": len(add_tokens),
            "additionsPerMeasure": round(len(add_tokens) / span, 3),
            "bothStemFraction": round(len(both) / len(add_tokens), 4) if add_tokens else 0.0,
            "occupiedSlotFraction": round(len(occupied) / len(add_tokens), 4) if add_tokens else 0.0,
            "medianBestScore": round(statistics.median(scores), 3) if scores else 0.0,
            "medianStemMargin": round(statistics.median(margins), 3) if margins else 0.0,
            "matchedDelta": md,
            "extraDelta": ed,
            "deltaPoints": delta,
        }
        rows.append(row)

    negatives = [r for r in rows if float(r["deltaPoints"]) <= 0.0]
    positives = [r for r in rows if float(r["deltaPoints"]) > 0.0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during failure profiling.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "adaptive-spectral-shifted-window-failure-profile",
        "frozenRule": FROZEN_RULE,
        "windows": rows,
        "negativeWindows": negatives,
        "positiveWindows": positives,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "derive-detector-side-gate-from-negative-vs-positive-window-signature",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY ADAPTIVE SPECTRAL SHIFTED WINDOW FAILURE PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Frozen rule: local5_med13")
    print("Negative/flat windows:")
    for row in negatives:
        print(
            f"{row['window']} adds={row['additionCount']} perMeasure={row['additionsPerMeasure']} "
            f"bothFrac={row['bothStemFraction']} occupiedFrac={row['occupiedSlotFraction']} "
            f"medianScore={row['medianBestScore']} medianMargin={row['medianStemMargin']} "
            f"matchedDelta={row['matchedDelta']} extraDelta={row['extraDelta']} delta={row['deltaPoints']}"
        )
    print("Positive windows:")
    for row in positives:
        print(
            f"{row['window']} adds={row['additionCount']} perMeasure={row['additionsPerMeasure']} "
            f"bothFrac={row['bothStemFraction']} occupiedFrac={row['occupiedSlotFraction']} "
            f"medianScore={row['medianBestScore']} medianMargin={row['medianStemMargin']} "
            f"matchedDelta={row['matchedDelta']} extraDelta={row['extraDelta']} delta={row['deltaPoints']}"
        )
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
