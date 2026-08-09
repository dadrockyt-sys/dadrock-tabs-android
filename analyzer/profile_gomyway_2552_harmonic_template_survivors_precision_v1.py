from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2476_dual_stem_harmonic_template_competition_v1 as comp

p2476 = comp.p2476
recur = comp.recur
recall = comp.recall
v2 = comp.v2
v3 = comp.v3
harmonic = comp.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PROFILE_PATH = PUBLIC / "gomyway-2476-dual-stem-harmonic-template-competition-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2552-harmonic-template-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2552-harmonic-template-survivors-precision-v1-manifest.json"
EXPECTED_2476 = (183, 684, 428)
EXPECTED_2476_F1 = 24.76
EXPECTED_2552 = (183, 684, 384)
EXPECTED_2552_F1 = 25.52
EXPECTED_ZERO_SIGNATURES = 11
EXPECTED_PRUNE_COUNT = 44


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        t = int(counts["true"])
        f = int(counts["false"])
        total = t + f
        rows.append({
            "signature": signature,
            "true": t,
            "false": f,
            "total": total,
            "precision": round(100.0 * t / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def reconstruct_2552(
    grid: dict[tuple[int, int], float],
    winner_audio,
    winner_sr: int,
    alt_audio,
    alt_sr: int,
    exact_signatures: set[str],
) -> tuple[Counter[tuple[int, int, int]], Counter[tuple[int, int, int]]]:
    champion2476 = p2476.reconstruct_2476(grid, winner_audio, winner_sr, alt_audio, alt_sr)
    pruned: Counter[tuple[int, int, int]] = Counter()

    for tok, count in champion2476.items():
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = comp.stem_features(winner_audio, winner_sr, center, pitch)
        af = comp.stem_features(alt_audio, alt_sr, center, pitch)
        signatures = comp.signatures_for(wf, af)
        if signatures & exact_signatures:
            pruned[tok] = count

    return champion2476 - pruned, pruned


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    source_profile = v2.load_json(SOURCE_PROFILE_PATH)
    if source_profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("24.76 harmonic-template profile is not reference-free during detection")

    zero_rows = list(source_profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_ZERO_SIGNATURES} validated harmonic-template signatures, got {len(zero_rows)}"
        )
    for row in zero_rows:
        if int(row.get("true", -1)) != 0 or int(row.get("false", 0)) < 5:
            raise RuntimeError(f"Invalid validated harmonic-template zero-precision row: {row}")
    exact_signatures = {str(row["signature"]) for row in zero_rows}

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    champion2476 = p2476.reconstruct_2476(grid, winner_audio, winner_sr, alt_audio, alt_sr)
    score2476 = recur.grade(champion2476, reference)
    actual2476 = (
        int(score2476["matched"]),
        int(score2476["missing"]),
        int(score2476["extra"]),
    )
    if actual2476 != EXPECTED_2476 or abs(float(score2476["pitchF1"]) - EXPECTED_2476_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 24.76 champion {EXPECTED_2476}/{EXPECTED_2476_F1}, got {actual2476}/{score2476['pitchF1']}"
        )

    champion2552, pruned = reconstruct_2552(
        grid,
        winner_audio,
        winner_sr,
        alt_audio,
        alt_sr,
        exact_signatures,
    )
    prune_count = int(sum(pruned.values()))
    if prune_count != EXPECTED_PRUNE_COUNT:
        raise RuntimeError(f"Expected exact 25.52 harmonic-template prune count {EXPECTED_PRUNE_COUNT}, got {prune_count}")

    true_pruned = int(sum((pruned & reference).values()))
    if true_pruned != 0:
        raise RuntimeError(f"25.52 reconstruction pruned {true_pruned} professional-reference matches")

    score2552 = recur.grade(champion2552, reference)
    actual2552 = (
        int(score2552["matched"]),
        int(score2552["missing"]),
        int(score2552["extra"]),
    )
    if actual2552 != EXPECTED_2552 or abs(float(score2552["pitchF1"]) - EXPECTED_2552_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 25.52 champion {EXPECTED_2552}/{EXPECTED_2552_F1}, got {actual2552}/{score2552['pitchF1']}"
        )

    matched = champion2552 & reference
    extras = champion2552 - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = comp.stem_features(winner_audio, winner_sr, center, pitch)
        af = comp.stem_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(comp.signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "maxBestNeighborRatio": max(wf["bestNeighborRatio"], af["bestNeighborRatio"]),
            "minTargetMarginDb": min(wf["targetMarginDb"], af["targetMarginDb"]),
            "maxOctaveAliasRatio": max(wf["octaveAliasRatio"], af["octaveAliasRatio"]),
            "signatures": signatures,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero_precision = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero_precision.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported_true = [r for r in ranked if int(r["true"]) >= 5]
    supported_true.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 25.52 harmonic-template survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-25.52-harmonic-template-survivor-precision",
        "baseline2476Score": score2476,
        "champion2552Score": score2552,
        "validatedRuleCount": len(exact_signatures),
        "validatedPruneCount": prune_count,
        "validatedTruePruned": true_pruned,
        "zeroPrecisionGeneralizableSignaturesMin5False": zero_precision,
        "supportedTrueSignaturesMin5True": supported_true,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score2552["pitchF1"],
        "matched": score2552["matched"],
        "missing": score2552["missing"],
        "extra": score2552["extra"],
        "validatedPruneCount": prune_count,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 25.52 HARMONIC-TEMPLATE SURVIVOR PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Baseline 24.76 pitch F1:", score2476["pitchF1"])
    print("Validated harmonic-template prune count:", prune_count)
    print("Validated true pruned:", true_pruned)
    print("Champion pitch F1:", score2552["pitchF1"])
    print("Champion matched/missing/extra:", score2552["matched"], "/", score2552["missing"], "/", score2552["extra"])
    print("Generalizable zero-precision harmonic-template survivor signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true harmonic-template survivor signatures (5+ true):")
    for row in supported_true[:30]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
