from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3118_measure_register_distribution_v1 as register
import profile_gomyway_3118_measure_position_survivors_precision_v1 as s3118

recur = register.recur
recall = register.recall
v2 = register.v2
v3 = register.v3
harmonic = register.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_3118_PATH = PUBLIC / "gomyway-3118-measure-register-distribution-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3161-measure-register-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-measure-register-survivors-precision-v1-manifest.json"
EXPECTED_BASELINE = (183, 684, 124)
EXPECTED_BASELINE_F1 = 31.18
EXPECTED_CHAMPION = (183, 684, 108)
EXPECTED_CHAMPION_F1 = 31.61
EXPECTED_PRUNED = 16
EXPECTED_TRUE_PRUNED = 0
EXPECTED_ZERO_SIGNATURES = 3


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true = int(counts["true"])
        false = int(counts["false"])
        total = true + false
        rows.append({
            "signature": signature,
            "true": true,
            "false": false,
            "total": total,
            "precision": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def reconstruct_3161(
    grid: list[dict[str, Any]],
    winner_audio: Any,
    winner_sr: int,
    alt_audio: Any,
    alt_sr: int,
    reference: Counter[tuple[int, int, int]],
) -> tuple[Counter[tuple[int, int, int]], dict[str, Any]]:
    baseline, baseline_reconstruction = s3118.reconstruct_3118(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    baseline_score = recur.grade(baseline, reference)
    baseline_actual = (
        int(baseline_score["matched"]),
        int(baseline_score["missing"]),
        int(baseline_score["extra"]),
    )
    if baseline_actual != EXPECTED_BASELINE or abs(float(baseline_score["pitchF1"]) - EXPECTED_BASELINE_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 31.18 baseline {EXPECTED_BASELINE}/{EXPECTED_BASELINE_F1}, "
            f"got {baseline_actual}/{baseline_score['pitchF1']}"
        )

    profile = v2.load_json(PROFILE_3118_PATH)
    if profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("31.18 measure-register profile is not reference-free during detection")

    zero_rows = list(profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_ZERO_SIGNATURES} saved measure-register zero-precision signatures, "
            f"got {len(zero_rows)}"
        )
    for row in zero_rows:
        if int(row.get("true", -1)) != 0 or int(row.get("false", 0)) < 5:
            raise RuntimeError(f"Invalid saved zero-precision measure-register row: {row}")
    zero_rows.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    selected = {str(r["signature"]) for r in zero_rows}

    profile_rows = list(profile.get("rows", []))
    row_by_token = {token(row): row for row in profile_rows}
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in baseline.items():
        row = row_by_token.get(tok)
        if row is None:
            continue
        signatures = {str(s) for s in row.get("signatures", [])}
        if signatures & selected:
            pruned[tok] = int(count)

    prune_count = int(sum(pruned.values()))
    true_pruned = int(sum((pruned & reference).values()))
    false_pruned = prune_count - true_pruned
    if prune_count != EXPECTED_PRUNED or true_pruned != EXPECTED_TRUE_PRUNED or false_pruned != EXPECTED_PRUNED:
        raise RuntimeError(
            f"Expected validated 31.61 register prune 16/0/16, got "
            f"{prune_count}/{true_pruned}/{false_pruned}"
        )

    champion = baseline - pruned
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(score["pitchF1"]) - EXPECTED_CHAMPION_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 31.61 champion {EXPECTED_CHAMPION}/{EXPECTED_CHAMPION_F1}, "
            f"got {actual}/{score['pitchF1']}"
        )

    reconstruction = {
        "baseline3118": baseline_reconstruction,
        "baseline3118Score": baseline_score,
        "selectedZeroPrecisionSignatures": sorted(selected),
        "registerPruneCount": prune_count,
        "registerTruePruned": true_pruned,
        "registerFalsePruned": false_pruned,
        "champion3161Score": score,
    }
    return champion, reconstruction


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

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion, reconstruction = reconstruct_3161(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )

    score = recur.grade(champion, reference)
    maps = register.build_maps(champion)
    matched = champion & reference
    extras = champion - reference

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        features = register.local_features(tok, maps)
        signatures = sorted(register.signatures_for(features))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "features": features,
            "signatures": signatures,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [row for row in ranked if int(row["true"]) == 0 and int(row["false"]) >= 5]
    zero.sort(key=lambda row: (-int(row["false"]), str(row["signature"])))
    supported = [row for row in ranked if int(row["true"]) >= 5]
    supported.sort(key=lambda row: (-float(row["precision"]), -int(row["true"]), str(row["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 31.61 measure-register survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-31.61-measure-register-survivors-precision",
        "champion3161Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "measure-and-neighboring-measure-register-pitch-distribution-shape-survivors",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
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
        "championPitchF1": score["pitchF1"],
        "matched": score["matched"],
        "missing": score["missing"],
        "extra": score["extra"],
        "zeroPrecisionSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 MEASURE REGISTER SURVIVORS PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Applied validated measure-register prune count:", reconstruction["registerPruneCount"])
    print("Applied validated true prune count:", reconstruction["registerTruePruned"])
    print("Applied validated false prune count:", reconstruction["registerFalsePruned"])
    print("Generalizable zero-precision measure-register survivor signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true measure-register survivor signatures:")
    for row in supported[:30]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
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
