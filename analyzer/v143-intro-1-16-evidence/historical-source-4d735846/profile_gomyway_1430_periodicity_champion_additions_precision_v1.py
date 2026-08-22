from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1419_cached_pitch_periodicity_gate_v1 as gate

bench = gate.bench
cached = gate.cached
recur = gate.recur
v2 = gate.v2
v3 = gate.v3
recall = gate.recall
profile = gate.profile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-1419-dual-stem-pitch-periodicity-residual-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1430-periodicity-champion-additions-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1430-periodicity-champion-additions-precision-v1-manifest.json"
EXPECTED_1419 = (178, 689, 1464)
EXPECTED_1430 = (183, 684, 1510)
EXPECTED_1430_F1 = 14.30


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision_row(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
    }


def fine_bucket(value: float, edges: tuple[float, ...], prefix: str) -> str:
    for edge in edges:
        if value < edge:
            return f"{prefix}_lt_{str(edge).replace('.', 'p').replace('-', 'm')}"
    return f"{prefix}_{str(edges[-1]).replace('.', 'p').replace('-', 'm')}_plus"


def summarize(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        out.append({"signature": signature, **precision_row(int(counts["true"]), int(counts["false"]))})
    return sorted(
        out,
        key=lambda r: (float(r["precision"]), int(r["true"]), -int(r["false"])),
        reverse=True,
    )


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    if not PROFILE_PATH.exists():
        raise RuntimeError(f"Missing cached periodicity profile: {PROFILE_PATH.relative_to(ROOT)}")
    periodicity_payload = v2.load_json(PROFILE_PATH)
    if periodicity_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Periodicity profile is not marked reference-free during detection.")
    periodicity_rows = list(periodicity_payload.get("rows", []))
    if not periodicity_rows:
        raise RuntimeError("Cached periodicity profile has no rows.")

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    cached_rows = cached.load_profile_rows()
    cached_by_token = {bench.token(row): row for row in cached_rows}

    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    champion_1419_additions = bench.rows_to_counter(cached_rows, bench.champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_1419_additions
    score_1419 = recur.grade(champion_1419, reference)
    actual_1419 = (
        int(score_1419["matched"]),
        int(score_1419["missing"]),
        int(score_1419["extra"]),
    )
    if actual_1419 != EXPECTED_1419:
        raise RuntimeError(f"Expected frozen 14.19 counts {EXPECTED_1419}, got {actual_1419}")

    winner_rows = [row for row in periodicity_rows if gate.sig_d(row)]
    winner_additions = gate.rows_to_counter(winner_rows, lambda row: True)
    champion_1430 = champion_1419 + winner_additions
    score_1430 = recur.grade(champion_1430, reference)
    actual_1430 = (
        int(score_1430["matched"]),
        int(score_1430["missing"]),
        int(score_1430["extra"]),
    )
    if actual_1430 != EXPECTED_1430 or abs(float(score_1430["pitchF1"]) - EXPECTED_1430_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 14.30 champion {EXPECTED_1430}/{EXPECTED_1430_F1}, "
            f"got {actual_1430}/{score_1430['pitchF1']}"
        )

    missing_1419 = reference - champion_1419
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    for row in winner_rows:
        tok = token(row)
        measure, step, pitch = tok
        is_true = missing_1419.get(tok, 0) > 0
        truth = "true" if is_true else "false"
        cached_row = cached_by_token.get(tok, {})

        maxcorr = float(row["maxTargetCorr"])
        mincorr = float(row["minTargetCorr"])
        maxmargin = float(row["maxTargetMargin"])
        minmargin = float(row["minTargetMargin"])
        maxoct = float(row["maxTargetOrOctaveCorr"])
        minoct = float(row["minTargetOrOctaveCorr"])
        recurrence = int(row.get("recurrence", cached_row.get("recurrence", 0)))

        maxcorr_b = fine_bucket(maxcorr, (0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.48, 0.55), "maxc")
        mincorr_b = fine_bucket(mincorr, (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.38, 0.45), "minc")
        maxmargin_b = fine_bucket(maxmargin, (-0.05, 0.00, 0.03, 0.06, 0.10, 0.15, 0.20), "maxm")
        minmargin_b = fine_bucket(minmargin, (-0.15, -0.10, -0.05, 0.00, 0.03, 0.06, 0.10), "minm")
        maxoct_b = fine_bucket(maxoct, (0.20, 0.30, 0.40, 0.50, 0.60, 0.70), "maxo")
        minoct_b = fine_bucket(minoct, (0.10, 0.20, 0.30, 0.40, 0.50, 0.60), "mino")
        recur_b = "recur_4plus" if recurrence >= 4 else f"recur_{recurrence}"
        pitch_b = f"midi_{pitch}"
        step_b = f"step_{step}"

        detector_buckets = [
            str(cached_row.get("rmsBucket", "rms_na")),
            str(cached_row.get("fluxBucket", "flux_na")),
            str(cached_row.get("ratioBucket", "ratio_na")),
            str(cached_row.get("templateBucket", "template_na")),
        ]
        rms_b, flux_b, ratio_b, template_b = detector_buckets

        signatures = (
            maxcorr_b,
            mincorr_b,
            maxmargin_b,
            minmargin_b,
            maxoct_b,
            minoct_b,
            recur_b,
            pitch_b,
            step_b,
            f"{maxcorr_b}|{mincorr_b}",
            f"{maxcorr_b}|{maxmargin_b}",
            f"{mincorr_b}|{maxmargin_b}",
            f"{maxcorr_b}|{mincorr_b}|{maxmargin_b}",
            f"{maxoct_b}|{minoct_b}|{maxmargin_b}",
            f"{maxcorr_b}|{recur_b}",
            f"{maxmargin_b}|{recur_b}",
            f"{step_b}|{pitch_b}",
            f"{step_b}|{maxcorr_b}|{maxmargin_b}",
            f"{pitch_b}|{maxcorr_b}|{maxmargin_b}",
            f"{rms_b}|{maxcorr_b}|{maxmargin_b}",
            f"{flux_b}|{maxcorr_b}|{maxmargin_b}",
            f"{ratio_b}|{maxcorr_b}|{maxmargin_b}",
            f"{template_b}|{maxcorr_b}|{maxmargin_b}",
            f"{rms_b}|{flux_b}|{maxcorr_b}",
            f"{ratio_b}|{template_b}|{maxcorr_b}",
        )
        for signature in signatures:
            groups[signature][truth] += 1

        details.append({
            "token": list(tok),
            "trueAddition": is_true,
            "measure": measure,
            "step": step,
            "pitch": pitch,
            "recurrence": recurrence,
            "maxTargetCorr": round(maxcorr, 6),
            "minTargetCorr": round(mincorr, 6),
            "maxTargetMargin": round(maxmargin, 6),
            "minTargetMargin": round(minmargin, 6),
            "maxTargetOrOctaveCorr": round(maxoct, 6),
            "minTargetOrOctaveCorr": round(minoct, 6),
            "rmsBucket": rms_b,
            "fluxBucket": flux_b,
            "ratioBucket": ratio_b,
            "templateBucket": template_b,
        })

    ranked = summarize(groups)
    repeatable = [row for row in ranked if int(row["true"]) >= 1 and int(row["total"]) >= 2]
    supported = [row for row in ranked if int(row["true"]) >= 2]
    zero_precision = [row for row in ranked if int(row["true"]) == 0 and int(row["false"]) >= 2]
    zero_precision.sort(key=lambda r: (int(r["false"]), str(r["signature"])), reverse=True)

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.30 periodicity additions profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.30-periodicity-champion-additions-precision",
        "baseline1419Score": score_1419,
        "champion1430Score": score_1430,
        "winnerRule": "periodicity_d_broader_dual_moderate",
        "additionCount": len(winner_rows),
        "trueAdditionCount": sum(1 for row in details if row["trueAddition"]),
        "falseAdditionCount": sum(1 for row in details if not row["trueAddition"]),
        "repeatableSignatures": repeatable,
        "supportedSignatures": supported,
        "zeroPrecisionSignatures": zero_precision,
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
        "recommendedNextAction": "benchmark-zero-precision-prunes-only-if-they-preserve-all-five-validated-periodicity-matches",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score_1430["pitchF1"],
        "additionCount": len(winner_rows),
        "trueAdditionCount": output["trueAdditionCount"],
        "falseAdditionCount": output["falseAdditionCount"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.30 PERIODICITY CHAMPION ADDITIONS PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score_1430["pitchF1"])
    print("Champion matched/missing/extra:", score_1430["matched"], "/", score_1430["missing"], "/", score_1430["extra"])
    print("Addition rows:", len(winner_rows))
    print("True additions:", output["trueAdditionCount"])
    print("False additions:", output["falseAdditionCount"])
    print("Top supported true signatures (2+ true):")
    for row in supported[:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Top zero-precision prune signatures (2+ false, 0 true):")
    for row in zero_precision[:25]:
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
