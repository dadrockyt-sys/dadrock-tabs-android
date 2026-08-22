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
OUTPUT_PATH = PUBLIC / "gomyway-spectral-specialist-failure-structure-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-spectral-specialist-failure-structure-v1-manifest.json"

VARIANT = {"name": "either_snr8", "snr": 8.0, "mode": "either"}
BLOCKS = [(17, 32), (33, 48), (49, 64), (65, 80), (81, 96), (97, 113)]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block_name(measure: int) -> str:
    for start, end in BLOCKS:
        if start <= measure <= end:
            return f"m{start}_{end}"
    return "outside"


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

    print("Computing either_snr8 specialist evidence...", flush=True)
    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    additions = spectral.additions_for_variant(VARIANT, winner_scores, alt_scores, champion)

    true_add = additions & (reference - champion)
    false_add = additions - true_add

    block_rows: dict[str, dict[str, int | float]] = {}
    for start, end in BLOCKS:
        name = f"m{start}_{end}"
        t = sum(count for (measure, _step, _midi), count in true_add.items() if start <= measure <= end)
        f = sum(count for (measure, _step, _midi), count in false_add.items() if start <= measure <= end)
        total = t + f
        block_rows[name] = {
            "trueAdditions": t,
            "falseAdditions": f,
            "precisionPercent": round(100.0 * t / total, 2) if total else 0.0,
        }

    midi_profile: dict[int, dict[str, int | float]] = {}
    for midi in range(spectral.MID_MIN, spectral.MID_MAX + 1):
        t = sum(count for (_measure, _step, pitch), count in true_add.items() if pitch == midi)
        f = sum(count for (_measure, _step, pitch), count in false_add.items() if pitch == midi)
        total = t + f
        midi_profile[midi] = {
            "trueAdditions": t,
            "falseAdditions": f,
            "precisionPercent": round(100.0 * t / total, 2) if total else 0.0,
        }

    score_buckets: dict[str, dict[str, int | float]] = {}
    bucket_defs = [
        ("8_10", 8.0, 10.0),
        ("10_12", 10.0, 12.0),
        ("12_16", 12.0, 16.0),
        ("16_plus", 16.0, float("inf")),
    ]
    for name, lo, hi in bucket_defs:
        t = f = 0
        for token, count in additions.items():
            score = max(winner_scores.get(token, 0.0), alt_scores.get(token, 0.0))
            if lo <= score < hi:
                if true_add.get(token, 0) > 0:
                    t += count
                else:
                    f += count
        total = t + f
        score_buckets[name] = {
            "trueAdditions": t,
            "falseAdditions": f,
            "precisionPercent": round(100.0 * t / total, 2) if total else 0.0,
        }

    agreement_profile = {
        "bothStemsAbove8": {"trueAdditions": 0, "falseAdditions": 0},
        "winnerOnlyAbove8": {"trueAdditions": 0, "falseAdditions": 0},
        "altOnlyAbove8": {"trueAdditions": 0, "falseAdditions": 0},
    }
    for token, count in additions.items():
        w = winner_scores.get(token, 0.0) >= 8.0
        a = alt_scores.get(token, 0.0) >= 8.0
        if w and a:
            key = "bothStemsAbove8"
        elif w:
            key = "winnerOnlyAbove8"
        else:
            key = "altOnlyAbove8"
        field = "trueAdditions" if true_add.get(token, 0) > 0 else "falseAdditions"
        agreement_profile[key][field] += count

    for row in agreement_profile.values():
        total = int(row["trueAdditions"]) + int(row["falseAdditions"])
        row["precisionPercent"] = round(100.0 * int(row["trueAdditions"]) / total, 2) if total else 0.0

    top_false_by_block_midi = Counter((block_name(m), midi) for (m, _s, midi), count in false_add.items() for _ in range(count))
    top_true_by_block_midi = Counter((block_name(m), midi) for (m, _s, midi), count in true_add.items() for _ in range(count))

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during failure profiling.")

    output: dict[str, Any] = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "spectral-specialist-failure-structure",
        "variant": VARIANT,
        "totalAdditions": sum(additions.values()),
        "trueAdditions": sum(true_add.values()),
        "falseAdditions": sum(false_add.values()),
        "overallAdditionPrecisionPercent": round(100.0 * sum(true_add.values()) / max(1, sum(additions.values())), 2),
        "blockProfile": block_rows,
        "midiProfile": midi_profile,
        "scoreBucketProfile": score_buckets,
        "stemAgreementProfile": agreement_profile,
        "topFalseBlockMidi": [
            {"bucket": f"{block}_midi{midi}", "count": count}
            for (block, midi), count in top_false_by_block_midi.most_common(20)
        ],
        "topTrueBlockMidi": [
            {"bucket": f"{block}_midi{midi}", "count": count}
            for (block, midi), count in top_true_by_block_midi.most_common(20)
        ],
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "derive-detector-side-spectral-false-positive-suppression-from-profile-then-revalidate",
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

    print("GOMYWAY SPECTRAL SPECIALIST FAILURE STRUCTURE V1 COMPLETE")
    print("Passed: True")
    print("Variant:", VARIANT["name"])
    print("Total/true/false additions:", output["totalAdditions"], "/", output["trueAdditions"], "/", output["falseAdditions"])
    print("Overall addition precision %:", output["overallAdditionPrecisionPercent"])
    print("Block profile:")
    for name, row in block_rows.items():
        print(name, row)
    print("Score bucket profile:")
    for name, row in score_buckets.items():
        print(name, row)
    print("Stem agreement profile:")
    for name, row in agreement_profile.items():
        print(name, row)
    print("Top false block/MIDI buckets:")
    for row in output["topFalseBlockMidi"]:
        print(row["bucket"], row["count"])
    print("Top true block/MIDI buckets:")
    for row in output["topTrueBlockMidi"]:
        print(row["bucket"], row["count"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
