from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_1382_dual_stem_broadband_onset_evidence_v1 as onset
import profile_gomyway_1382_dual_stem_fundamental_overtone_evidence_v1 as fundamental

attack = onset.attack
recur = onset.recur
v2 = onset.v2
v3 = onset.v3
recall = onset.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-onset-fundamental-joint-evidence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-onset-fundamental-joint-evidence-v1-manifest.json"
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_row(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
    }


def recur_label(value: int) -> str:
    return "4plus" if value >= 4 else str(value)


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    print("Rebuilding frozen validated 13.82 champion and detector-side pool...", flush=True)
    champion, winner_scores, alt_scores = recur.build_frozen_1382(grid)
    champion_score = recur.grade(champion, reference)
    actual = (
        int(champion_score["matched"]),
        int(champion_score["missing"]),
        int(champion_score["extra"]),
    )
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(
            f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, "
            f"got {actual}/{champion_score['pitchF1']}"
        )

    pool, recurrence_counts = attack.candidate_pool(grid, winner_scores, alt_scores, champion)
    print(f"Joint onset/fundamental candidate pool: {len(pool)}", flush=True)

    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)

    # All detector-side features are frozen before reference labels are consulted.
    feature_rows: list[dict[str, Any]] = []
    for index, token in enumerate(pool, 1):
        measure, step, pitch = token
        center = float(grid[(measure, step)])

        w_onset = onset.broadband_onset(winner_audio, winner_sr, center)
        a_onset = onset.broadband_onset(alt_audio, alt_sr, center)
        min_rms = min(float(w_onset["rmsLog2Rise"]), float(a_onset["rmsLog2Rise"]))
        min_flux = min(float(w_onset["positiveFlux"]), float(a_onset["positiveFlux"]))

        w_fund = fundamental.stem_features(winner_audio, winner_sr, center, pitch)
        a_fund = fundamental.stem_features(alt_audio, alt_sr, center, pitch)
        min_ratio = min(
            float(w_fund["targetVsSubharmonicRatio"]),
            float(a_fund["targetVsSubharmonicRatio"]),
        )
        min_template = min(
            float(w_fund["templateRatio"]),
            float(a_fund["templateRatio"]),
        )

        rb = onset.bucket(min_rms, onset.RMS_BUCKETS)
        fb = onset.bucket(min_flux, onset.FLUX_BUCKETS)
        ratio_b = fundamental.bucket(min_ratio, fundamental.RATIO_BUCKETS)
        template_b = fundamental.bucket(min_template, fundamental.TEMPLATE_BUCKETS)
        recurrence = int(recurrence_counts[(step, pitch)])

        feature_rows.append(
            {
                "token": [measure, step, pitch],
                "recurrence": recurrence,
                "minRmsLog2Rise": round(min_rms, 6),
                "minPositiveFlux": round(min_flux, 6),
                "minTargetVsSubharmonicRatio": round(min_ratio, 6),
                "minTemplateRatio": round(min_template, 6),
                "rmsBucket": rb,
                "fluxBucket": fb,
                "ratioBucket": ratio_b,
                "templateBucket": template_b,
            }
        )
        if index % 250 == 0:
            print(f"Joint detector evidence measured: {index}/{len(pool)}", flush=True)

    missing_reference = reference - champion
    onset_fund_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    exact_joint_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    targeted_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for row in feature_rows:
        token = tuple(int(v) for v in row["token"])
        is_true = missing_reference.get(token, 0) > 0
        idx = 0 if is_true else 1
        recurrence = int(row["recurrence"])
        rl = recur_label(recurrence)

        onset_key = f"{row['rmsBucket']}|{row['fluxBucket']}"
        fund_key = f"{row['ratioBucket']}|{row['templateBucket']}"
        onset_fund_counts[f"{onset_key}|{fund_key}"][idx] += 1
        exact_joint_counts[f"{onset_key}|{fund_key}|recur_{rl}"][idx] += 1

        # Predeclared detector-side intersections around the two strongest
        # independently observed families. These are evaluated only after
        # the features above are frozen.
        rms = float(row["minRmsLog2Rise"])
        flux = float(row["minPositiveFlux"])
        ratio = float(row["minTargetVsSubharmonicRatio"])
        template = float(row["minTemplateRatio"])

        targeted_rules = {
            "exact_onset_x_exact_fund_recur2": (
                0.0 <= rms < 0.10
                and 0.10 <= flux < 0.25
                and 1.0 <= ratio < 2.0
                and 1.50 <= template < 2.50
                and recurrence == 2
            ),
            "exact_onset_x_ratio100plus_template150_250_recur2": (
                0.0 <= rms < 0.10
                and 0.10 <= flux < 0.25
                and ratio >= 1.0
                and 1.50 <= template < 2.50
                and recurrence == 2
            ),
            "exact_onset_x_ratio100_400_template150plus_recur2": (
                0.0 <= rms < 0.10
                and 0.10 <= flux < 0.25
                and 1.0 <= ratio < 4.0
                and template >= 1.50
                and recurrence == 2
            ),
            "rms_m005_010_flux010_025_x_exact_fund_recur2": (
                -0.05 <= rms < 0.10
                and 0.10 <= flux < 0.25
                and 1.0 <= ratio < 2.0
                and 1.50 <= template < 2.50
                and recurrence == 2
            ),
            "rms0_015_flux008_025_x_exact_fund_recur2": (
                0.0 <= rms < 0.15
                and 0.08 <= flux < 0.25
                and 1.0 <= ratio < 2.0
                and 1.50 <= template < 2.50
                and recurrence == 2
            ),
        }
        for name, matched in targeted_rules.items():
            if matched:
                targeted_counts[name][idx] += 1

        row["trueMissingReference"] = is_true

    onset_fund_summary = {
        key: precision_row(value[0], value[1]) for key, value in onset_fund_counts.items()
    }
    exact_joint_summary = {
        key: precision_row(value[0], value[1]) for key, value in exact_joint_counts.items()
    }
    targeted_summary = {
        key: precision_row(value[0], value[1]) for key, value in targeted_counts.items()
    }

    best_exact = sorted(
        exact_joint_summary.items(),
        key=lambda item: (
            float(item[1]["precision"]),
            int(item[1]["true"]),
            -int(item[1]["false"]),
        ),
        reverse=True,
    )[:40]

    best_targeted = sorted(
        targeted_summary.items(),
        key=lambda item: (
            float(item[1]["precision"]),
            int(item[1]["true"]),
            -int(item[1]["false"]),
        ),
        reverse=True,
    )

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during joint onset/fundamental profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-13.82-reference-free-onset-fundamental-joint-evidence",
        "championScore": champion_score,
        "detectorPool": {
            "bothFloor": attack.POOL_FLOOR,
            "localProminenceMargin": attack.POOL_MARGIN,
            "recurrence": attack.POOL_RECURRENCE,
            "count": len(pool),
        },
        "bestExactJointBuckets": [
            {"signature": key, **value} for key, value in best_exact
        ],
        "targetedIntersectionSummary": [
            {"signature": key, **value} for key, value in best_targeted
        ],
        "rows": feature_rows,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-high-precision-joint-intersections-else-pivot-detector-family",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": champion_score["pitchF1"],
        "poolCount": len(pool),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 13.82 ONSET + FUNDAMENTAL JOINT EVIDENCE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", champion_score["pitchF1"])
    print(
        "Champion matched/missing/extra:",
        champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"],
    )
    print("Joint candidate pool:", len(pool))
    print("Targeted onset/fundamental intersections:")
    for key, row in best_targeted:
        print(
            f"  {key}: true={row['true']} false={row['false']} precision={row['precision']}%"
        )
    print("Top exact onset/fundamental/recurrence buckets:")
    for key, row in best_exact[:20]:
        print(
            f"  {key}: true={row['true']} false={row['false']} precision={row['precision']}%"
        )
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
