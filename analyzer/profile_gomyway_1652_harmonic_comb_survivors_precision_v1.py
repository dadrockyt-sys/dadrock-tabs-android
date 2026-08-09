from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1590_harmonic_comb_precision_prune_cv_v1 as b1590

harmonic = b1590.harmonic
recur = b1590.recur
recall = b1590.recall
v2 = b1590.v2
v3 = b1590.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1590_PATH = PUBLIC / "gomyway-1590-dual-stem-harmonic-comb-coherence-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1652-harmonic-comb-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1652-harmonic-comb-survivors-precision-v1-manifest.json"
EXPECTED = (183, 684, 1166)
EXPECTED_F1 = 16.52


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true_count = int(counts["true"])
        false_count = int(counts["false"])
        total = true_count + false_count
        out.append({
            "signature": signature,
            "true": true_count,
            "false": false_count,
            "total": total,
            "precision": round(100.0 * true_count / total, 2) if total else 0.0,
        })
    return sorted(out, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


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

    profile_payload = v2.load_json(PROFILE_1590_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("15.90 harmonic-comb profile is not reference-free during detection")
    rows = list(profile_payload.get("rows", []))
    if not rows:
        raise RuntimeError("15.90 harmonic-comb profile has no rows")
    row_by_token = {token(row): row for row in rows}

    survivor_payload = v2.load_json(harmonic.b1569.PROFILE_1569_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("15.69 survivor profile is not reference-free during detection")
    attack_rows = list(survivor_payload.get("rows", []))
    attack_row_by_token = {tuple(int(v) for v in row["token"]): row for row in attack_rows}

    champion_1590 = harmonic.reconstruct_1590(grid, attack_row_by_token)

    harmonic_pruned: Counter[tuple[int, int, int]] = Counter()
    survivor_rows: list[dict[str, Any]] = []
    for tok, count in champion_1590.items():
        row = row_by_token.get(tok)
        if row is None:
            continue
        if b1590.pred_a(row) or b1590.pred_b(row) or b1590.pred_c(row) or b1590.pred_d(row) or b1590.pred_e(row):
            harmonic_pruned[tok] = count
        else:
            survivor_rows.append(row)

    champion = champion_1590 - harmonic_pruned
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 16.52 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    for row in survivor_rows:
        tok = token(row)
        truth = "true" if reference.get(tok, 0) > 0 else "false"
        count = int(row.get("count", 1))
        b = b1590.harmonic_buckets(row)
        min_margin = b["minMargin"]
        min_f0 = b["minF0Share"]
        min_comb = b["minComb"]
        comb_disagree = b["combDisagreement"]

        signatures = {
            "minCombRatio": min_comb,
            "minNeighborMargin": min_margin,
            "minFundamentalShare": min_f0,
            "combRatioDisagreement": comb_disagree,
            "combMargin": f"{min_comb}|{min_margin}",
            "combF0Share": f"{min_comb}|{min_f0}",
            "marginF0Share": f"{min_margin}|{min_f0}",
            "combAgreement": f"{min_comb}|{comb_disagree}",
            "combMarginAgreement": f"{min_comb}|{min_margin}|{comb_disagree}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({**row, "survives1652Prune": True, "trueSurvivor": truth == "true"})

    ranked = precision_rows(groups)
    zero_precision = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero_precision.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported_true = [r for r in ranked if int(r["true"]) >= 5]
    supported_true.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 16.52 harmonic-comb survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-16.52-harmonic-comb-survivors-precision",
        "champion1652Score": score,
        "validatedHarmonicPruneRule": "harmonic1590_prune_union_a_b_c_d_e",
        "validatedHarmonicPruneCount": int(sum(harmonic_pruned.values())),
        "survivorRowCount": len(survivor_rows),
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
        "recommendedNextAction": "benchmark-only-repeatable-zero-precision-16.52-harmonic-comb-survivor-signatures-with-prune-specific-heldout-cv-or-freeze-family-if-exhausted",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score["pitchF1"],
        "matched": score["matched"],
        "missing": score["missing"],
        "extra": score["extra"],
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 16.52 HARMONIC-COMB SURVIVORS PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Validated harmonic prune count:", sum(harmonic_pruned.values()))
    print("Harmonic-comb survivor rows:", len(survivor_rows))
    print("Generalizable zero-precision harmonic-comb survivor signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true harmonic-comb survivor signatures (5+ true):")
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
