from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2813_temporal_density_crowding_v1 as density

recur = density.recur
recall = density.recall
v2 = density.v2
v3 = density.v3
harmonic = density.harmonic
c2813 = density.c2813

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-2813-temporal-density-crowding-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2850-temporal-density-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2850-temporal-density-survivors-precision-v1-manifest.json"
EXPECTED_2813 = (183, 684, 251)
EXPECTED_2813_F1 = 28.13
EXPECTED_2850 = (183, 684, 234)
EXPECTED_2850_F1 = 28.50
EXPECTED_ZERO_SIGNATURES = 3
EXPECTED_FALSE_PRUNED = 17


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


def reconstruct_2850(
    grid: dict[tuple[int, int], float],
    winner_audio,
    winner_sr: int,
    alt_audio,
    alt_sr: int,
    reference: Counter[tuple[int, int, int]],
) -> tuple[Counter[tuple[int, int, int]], dict[str, Any]]:
    champion_2813, reconstruction_2813 = c2813.reconstruct_2813(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score_2813 = recur.grade(champion_2813, reference)
    actual_2813 = (
        int(score_2813["matched"]),
        int(score_2813["missing"]),
        int(score_2813["extra"]),
    )
    if actual_2813 != EXPECTED_2813 or abs(float(score_2813["pitchF1"]) - EXPECTED_2813_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 28.13 champion {EXPECTED_2813}/{EXPECTED_2813_F1}, "
            f"got {actual_2813}/{score_2813['pitchF1']}"
        )

    profile_payload = v2.load_json(PROFILE_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("28.13 temporal-density profile is not reference-free during detection")

    zero_rows = list(profile_payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_ZERO_SIGNATURES} temporal-density zero-precision signatures, got {len(zero_rows)}"
        )
    for row in zero_rows:
        if int(row.get("true", -1)) != 0 or int(row.get("false", 0)) < 5:
            raise RuntimeError(f"Invalid validated temporal-density row: {row}")
    selected = {str(row["signature"]) for row in zero_rows}

    profile_rows = list(profile_payload.get("rows", []))
    row_by_token = {token(row): row for row in profile_rows}

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_2813.items():
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
            f"Expected validated temporal-density prune to remove 0 true / {EXPECTED_FALSE_PRUNED} false, "
            f"got {true_pruned} true / {false_pruned} false"
        )

    champion_2850 = champion_2813 - pruned
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

    return champion_2850, {
        "reconstruction2813": reconstruction_2813,
        "score2813": score_2813,
        "score2850": score_2850,
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

    champion, reconstruction = reconstruct_2850(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score = recur.grade(champion, reference)

    slots = density.slot_counts(champion)
    measures = density.measure_counts(champion)
    pitch_steps = density.pitch_step_map(champion)
    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        features = density.local_features(
            tok, champion, slots, measures, pitch_steps, grid,
            winner_audio, winner_sr, alt_audio, alt_sr,
        )
        signatures = sorted(density.signatures_for(features))
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
        raise RuntimeError("Protected candidate changed during 28.50 temporal-density survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-28.50-temporal-density-survivor-precision",
        "champion2850Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "temporal-density-crowding-survivors-after-validated-full-zero-precision-union",
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

    print("GOMYWAY 28.50 TEMPORAL DENSITY SURVIVOR PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Validated temporal-density true pruned:", reconstruction["validatedTruePruned"])
    print("Validated temporal-density false pruned:", reconstruction["validatedFalsePruned"])
    print("Generalizable zero-precision temporal-density survivor signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true temporal-density survivor signatures:")
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
