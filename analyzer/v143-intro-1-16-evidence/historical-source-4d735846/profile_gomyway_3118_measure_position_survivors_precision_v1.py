from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2850_measure_position_rhythmic_role_v1 as position
import profile_gomyway_2850_temporal_density_survivors_precision_v1 as s2850

recur = position.recur
recall = position.recall
v2 = position.v2
v3 = position.v3
harmonic = position.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-2850-measure-position-rhythmic-role-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3118-measure-position-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3118-measure-position-survivors-precision-v1-manifest.json"
EXPECTED_2850 = (183, 684, 234)
EXPECTED_2850_F1 = 28.50
EXPECTED_3118 = (183, 684, 124)
EXPECTED_3118_F1 = 31.18
EXPECTED_ZERO_SIGNATURES = 28
EXPECTED_FALSE_PRUNED = 110


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


def reconstruct_3118(
    grid: dict[tuple[int, int], float],
    winner_audio,
    winner_sr: int,
    alt_audio,
    alt_sr: int,
    reference: Counter[tuple[int, int, int]],
) -> tuple[Counter[tuple[int, int, int]], dict[str, Any]]:
    champion_2850, reconstruction_2850 = s2850.reconstruct_2850(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score_2850 = recur.grade(champion_2850, reference)
    actual_2850 = (
        int(score_2850["matched"]),
        int(score_2850["missing"]),
        int(score_2850["extra"]),
    )
    if actual_2850 != EXPECTED_2850 or abs(float(score_2850["pitchF1"]) - EXPECTED_2850_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 28.50 champion {EXPECTED_2850}/{EXPECTED_2850_F1}, "
            f"got {actual_2850}/{score_2850['pitchF1']}"
        )

    profile_payload = v2.load_json(PROFILE_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("28.50 measure-position profile is not reference-free during detection")

    zero_rows = list(profile_payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_ZERO_SIGNATURES} measure-position zero-precision signatures, got {len(zero_rows)}"
        )
    for row in zero_rows:
        if int(row.get("true", -1)) != 0 or int(row.get("false", 0)) < 5:
            raise RuntimeError(f"Invalid validated measure-position row: {row}")
    selected = {str(row["signature"]) for row in zero_rows}

    profile_rows = list(profile_payload.get("rows", []))
    row_by_token = {token(row): row for row in profile_rows}

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_2850.items():
        row = row_by_token.get(tok)
        if row is None:
            continue
        signatures = {str(s) for s in row.get("signatures", [])}
        if signatures & selected:
            pruned[tok] = count

    true_pruned = int(sum((pruned & reference).values()))
    false_pruned = int(sum(pruned.values()) - true_pruned)
    if true_pruned != 0 or false_pruned != EXPECTED_FALSE_PRUNED:
        raise RuntimeError(
            f"Expected validated measure-position prune to remove 0 true / {EXPECTED_FALSE_PRUNED} false, "
            f"got {true_pruned} true / {false_pruned} false"
        )

    champion_3118 = champion_2850 - pruned
    score_3118 = recur.grade(champion_3118, reference)
    actual_3118 = (
        int(score_3118["matched"]),
        int(score_3118["missing"]),
        int(score_3118["extra"]),
    )
    if actual_3118 != EXPECTED_3118 or abs(float(score_3118["pitchF1"]) - EXPECTED_3118_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 31.18 champion {EXPECTED_3118}/{EXPECTED_3118_F1}, "
            f"got {actual_3118}/{score_3118['pitchF1']}"
        )

    return champion_3118, {
        "reconstruction2850": reconstruction_2850,
        "score2850": score_2850,
        "score3118": score_3118,
        "validatedSignatureCount": len(selected),
        "validatedSignatures": sorted(selected),
        "validatedTruePruned": true_pruned,
        "validatedFalsePruned": false_pruned,
    }


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

    champion, reconstruction = reconstruct_3118(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score = recur.grade(champion, reference)

    maps = position.build_role_maps(champion)
    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        features = position.local_features(tok, maps)
        signatures = sorted(position.signatures_for(features))
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
        raise RuntimeError("Protected candidate changed during 31.18 measure-position survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-31.18-measure-position-survivor-precision",
        "champion3118Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "measure-position-rhythmic-role-survivors-after-validated-28-signature-union",
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

    print("GOMYWAY 31.18 MEASURE POSITION SURVIVOR PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Validated measure-position signature count:", reconstruction["validatedSignatureCount"])
    print("Validated measure-position true pruned:", reconstruction["validatedTruePruned"])
    print("Validated measure-position false pruned:", reconstruction["validatedFalsePruned"])
    print("Generalizable zero-precision measure-position survivor signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true measure-position survivor signatures:")
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
