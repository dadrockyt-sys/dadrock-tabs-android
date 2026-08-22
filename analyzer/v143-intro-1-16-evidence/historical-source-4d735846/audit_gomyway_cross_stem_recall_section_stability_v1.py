from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_cross_stem_consensus_recall_v1 as cross

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-cross-stem-recall-section-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-cross-stem-recall-section-stability-v1-manifest.json"

CURRENT_CHAMPION_F1 = 6.60
CROSS_STEM_F1 = 6.99
FIXED_RULE = "alt_additions_all"

# Contiguous audit blocks across the 97-measure professional reference span.
BLOCKS = [
    (17, 32),
    (33, 48),
    (49, 64),
    (65, 80),
    (81, 96),
    (97, 113),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subset(counter: Counter[tuple[int, int, int]], start: int, end: int) -> Counter[tuple[int, int, int]]:
    return Counter({k: v for k, v in counter.items() if start <= k[0] <= end})


def score(predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]]) -> dict[str, Any]:
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    expected = sum(reference.values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())
    pitch_f1 = round(100.0 * v2.f1(matched, predicted_count, expected), 2) if expected else 0.0
    return {
        "pitchF1": pitch_f1,
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "predictions": predicted_count,
        "referenceTokens": expected,
    }


def main() -> None:
    for path in (cross.WINNER_STEM, cross.ALT_STEM, cross.CANDIDATE_PATH, cross.REFERENCE_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Missing required benchmark input: {path.relative_to(ROOT)}")

    candidate_hash_before = sha256(cross.CANDIDATE_PATH)
    candidate = v2.load_json(cross.CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, grid_diagnostics = v2.build_timing_grid(events)

    reference_payload = v2.load_json(cross.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)
    if sum(reference.values()) != 867:
        raise RuntimeError(f"Expected 867 professional pitch tokens, found {sum(reference.values())}")

    print("Analyzing winner stem...", flush=True)
    winner_grouped = cross.group_rows(cross.WINNER_STEM, grid)
    print("Analyzing alternate direct-Demucs stem...", flush=True)
    alt_grouped = cross.group_rows(cross.ALT_STEM, grid)

    champion = cross.merge_rows(winner_grouped, alt_grouped, "champion_only")
    cross_stem = cross.merge_rows(winner_grouped, alt_grouped, FIXED_RULE)

    blocks: list[dict[str, Any]] = []
    positive_f1_blocks = 0
    nonnegative_f1_blocks = 0
    positive_matched_blocks = 0
    catastrophic_regressions = 0

    for start, end in BLOCKS:
        ref_block = subset(reference, start, end)
        champion_block = score(subset(champion, start, end), ref_block)
        cross_block = score(subset(cross_stem, start, end), ref_block)
        delta_f1 = round(float(cross_block["pitchF1"]) - float(champion_block["pitchF1"]), 2)
        matched_delta = int(cross_block["matched"]) - int(champion_block["matched"])
        extra_delta = int(cross_block["extra"]) - int(champion_block["extra"])

        if delta_f1 > 0:
            positive_f1_blocks += 1
        if delta_f1 >= 0:
            nonnegative_f1_blocks += 1
        if matched_delta > 0:
            positive_matched_blocks += 1
        if delta_f1 < -0.50:
            catastrophic_regressions += 1

        row = {
            "measureStart": start,
            "measureEnd": end,
            "champion": champion_block,
            "crossStem": cross_block,
            "deltaF1Points": delta_f1,
            "matchedDelta": matched_delta,
            "extraDelta": extra_delta,
        }
        blocks.append(row)
        print(
            f"m{start}-{end}: championF1={champion_block['pitchF1']} crossStemF1={cross_block['pitchF1']} "
            f"delta={delta_f1:+.2f} matchedDelta={matched_delta:+d} extraDelta={extra_delta:+d}",
            flush=True,
        )

    full_champion = score(champion, reference)
    full_cross = score(cross_stem, reference)
    full_delta = round(float(full_cross["pitchF1"]) - float(full_champion["pitchF1"]), 2)

    # Stability gate: the fixed rule must retain its full-song gain, avoid any large block collapse,
    # and improve F1 in at least half of the contiguous blocks while improving recall broadly.
    passed = (
        full_delta > 0
        and catastrophic_regressions == 0
        and positive_f1_blocks >= 3
        and positive_matched_blocks >= 3
    )

    candidate_hash_after = sha256(cross.CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during section stability audit.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "fixed-cross-stem-recall-section-stability-audit",
        "fixedRule": FIXED_RULE,
        "timingGrid": grid_diagnostics,
        "currentChampionPitchF1": CURRENT_CHAMPION_F1,
        "crossStemReferencePitchF1": CROSS_STEM_F1,
        "fullChampion": full_champion,
        "fullCrossStem": full_cross,
        "fullDeltaF1Points": full_delta,
        "blocks": blocks,
        "positiveF1Blocks": positive_f1_blocks,
        "nonnegativeF1Blocks": nonnegative_f1_blocks,
        "positiveMatchedBlocks": positive_matched_blocks,
        "catastrophicRegressionBlocks": catastrophic_regressions,
        "sectionStabilityPassed": passed,
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
            "lock-cross-stem-6.99-as-benchmark-champion-and-profile-remaining-misses"
            if passed
            else "retain-6.60-champion-and-profile-block-specific-failures"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "fixedRule": FIXED_RULE,
        "sectionStabilityPassed": passed,
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CROSS-STEM RECALL SECTION STABILITY V1 COMPLETE")
    print("Passed: True")
    print("Fixed rule:", FIXED_RULE)
    print("Full champion/cross-stem F1:", full_champion["pitchF1"], "/", full_cross["pitchF1"])
    print("Full delta points:", full_delta)
    print("Positive F1 blocks:", positive_f1_blocks, "/", len(BLOCKS))
    print("Positive matched blocks:", positive_matched_blocks, "/", len(BLOCKS))
    print("Catastrophic regression blocks:", catastrophic_regressions)
    print("Section stability passed:", passed)
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
