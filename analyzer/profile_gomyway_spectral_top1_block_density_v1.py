from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_mid_register_audio_preconditioning_v1 as precond
import benchmark_gomyway_mid_register_spectral_specialist_v1 as spectral
import benchmark_gomyway_spectral_specialist_precision_gate_v1 as gate

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-spectral-top1-block-density-profile-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-spectral-top1-block-density-profile-v1-manifest.json"

RULE = {"name": "either8_top1_per_slot", "kind": "ranked", "threshold": 8.0, "topn": 1}
BLOCKS = [(17, 32), (33, 48), (49, 64), (65, 80), (81, 96), (97, 113)]


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


def in_block(counter: Counter[tuple[int, int, int]], start: int, end: int) -> Counter[tuple[int, int, int]]:
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

    print("Building frozen 6.99 champion...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    champion = precond.merge_with_cap(base_winner, base_alt)

    print("Computing frozen either8_top1_per_slot evidence...", flush=True)
    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    additions = gate.accepted_tokens(RULE, winner_scores, alt_scores, champion)
    prediction = precond.merge_with_cap(champion, additions)

    rows = []
    for start, end in BLOCKS:
        block_add = in_block(additions, start, end)
        block_champ = in_block(champion, start, end)
        block_pred = in_block(prediction, start, end)
        block_ref = in_block(reference, start, end)

        slots = sorted({(m, s) for (m, s, _p) in block_add})
        champion_slots = defaultdict(int)
        for (m, s, _p), count in block_champ.items():
            champion_slots[(m, s)] += count

        best_scores: list[float] = []
        margins: list[float] = []
        both_count = 0
        one_stem_count = 0
        occupied_before = 0
        empty_before = 0
        for token in block_add:
            w = float(winner_scores.get(token, 0.0))
            a = float(alt_scores.get(token, 0.0))
            best_scores.append(max(w, a))
            margins.append(abs(w - a))
            if w >= 8.0 and a >= 8.0:
                both_count += 1
            else:
                one_stem_count += 1
            if champion_slots[(token[0], token[1])] > 0:
                occupied_before += 1
            else:
                empty_before += 1

        c = grade(block_champ, block_ref)
        p = grade(block_pred, block_ref)
        delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
        matched_delta = int(p["matched"]) - int(c["matched"])
        extra_delta = int(p["extra"]) - int(c["extra"])
        true_add = sum((block_add & (block_ref - block_champ)).values())
        add_count = sum(block_add.values())

        row = {
            "block": f"m{start}_{end}",
            "additionCount": add_count,
            "additionSlots": len(slots),
            "additionsPerMeasure": round(add_count / (end - start + 1), 3),
            "bothStemFraction": round(both_count / add_count, 4) if add_count else 0.0,
            "oneStemFraction": round(one_stem_count / add_count, 4) if add_count else 0.0,
            "occupiedSlotFraction": round(occupied_before / add_count, 4) if add_count else 0.0,
            "emptySlotFraction": round(empty_before / add_count, 4) if add_count else 0.0,
            "meanBestScore": round(statistics.fmean(best_scores), 3) if best_scores else 0.0,
            "medianBestScore": round(statistics.median(best_scores), 3) if best_scores else 0.0,
            "meanStemMargin": round(statistics.fmean(margins), 3) if margins else 0.0,
            "medianStemMargin": round(statistics.median(margins), 3) if margins else 0.0,
            "trueAdditions": true_add,
            "additionPrecisionPercent": round(100.0 * true_add / add_count, 2) if add_count else 0.0,
            "championF1": c["pitchF1"],
            "specialistF1": p["pitchF1"],
            "deltaPoints": delta,
            "matchedDelta": matched_delta,
            "extraDelta": extra_delta,
        }
        rows.append(row)
        print(row, flush=True)

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during block-density profile.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "either8-top1-detector-side-block-density",
        "rule": RULE,
        "blocks": rows,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "derive-predeclared-density-or-agreement-gate-from-detector-side-block-profile-and-run-cv-plus-section-validation",
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

    print("GOMYWAY SPECTRAL TOP1 BLOCK DENSITY PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Rule: either8_top1_per_slot")
    print("Block detector-side profile:")
    for row in rows:
        print(
            row["block"],
            "adds=", row["additionCount"],
            "perMeasure=", row["additionsPerMeasure"],
            "bothFrac=", row["bothStemFraction"],
            "occupiedFrac=", row["occupiedSlotFraction"],
            "medianScore=", row["medianBestScore"],
            "medianMargin=", row["medianStemMargin"],
            "precision%=", row["additionPrecisionPercent"],
            "delta=", row["deltaPoints"],
        )
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
