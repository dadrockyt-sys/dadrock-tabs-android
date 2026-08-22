from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import benchmark_gomyway_1419_cached_pitch_periodicity_gate_v1 as gate
import profile_gomyway_1430_periodicity_champion_additions_precision_v1 as p1430

bench = gate.bench
cached = gate.cached
recur = gate.recur
v2 = gate.v2
v3 = gate.v3
recall = gate.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PERIODICITY_PATH = PUBLIC / "gomyway-1419-dual-stem-pitch-periodicity-residual-v1.json"
PRECISION_PATH = PUBLIC / "gomyway-1430-periodicity-champion-additions-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1430-cached-periodicity-zero-precision-prune-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1430-cached-periodicity-zero-precision-prune-v1-manifest.json"

EXPECTED_1419 = (178, 689, 1464)
EXPECTED_1430 = (183, 684, 1510)
EXPECTED_1430_F1 = 14.30


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fine_buckets(row: dict[str, Any]) -> dict[str, str]:
    return {
        "maxc": p1430.fine_bucket(float(row["maxTargetCorr"]), (0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.48, 0.55), "maxc"),
        "minc": p1430.fine_bucket(float(row["minTargetCorr"]), (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.38, 0.45), "minc"),
        "maxm": p1430.fine_bucket(float(row["maxTargetMargin"]), (-0.05, 0.00, 0.03, 0.06, 0.10, 0.15, 0.20), "maxm"),
        "maxo": p1430.fine_bucket(float(row["maxTargetOrOctaveCorr"]), (0.20, 0.30, 0.40, 0.50, 0.60, 0.70), "maxo"),
        "mino": p1430.fine_bucket(float(row["minTargetOrOctaveCorr"]), (0.10, 0.20, 0.30, 0.40, 0.50, 0.60), "mino"),
    }


def pred_a(row: dict[str, Any]) -> bool:
    b = fine_buckets(row)
    return (
        str(row.get("ratioBucket")) == "ratio_100_200"
        and b["maxc"] == "maxc_lt_0p48"
        and b["maxm"] == "maxm_lt_0p2"
    )


def pred_b(row: dict[str, Any]) -> bool:
    b = fine_buckets(row)
    return b["minc"] == "minc_lt_0p38" and b["maxm"] == "maxm_lt_0p15"


def pred_c(row: dict[str, Any]) -> bool:
    b = fine_buckets(row)
    return (
        b["maxo"] == "maxo_lt_0p5"
        and b["mino"] == "mino_lt_0p5"
        and b["maxm"] == "maxm_lt_0p2"
    )


def pred_d(row: dict[str, Any]) -> bool:
    b = fine_buckets(row)
    return b["maxc"] == "maxc_lt_0p48" and b["minc"] == "minc_lt_0p38"


VARIANTS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("prune_a_ratio100_200_maxc48_maxm20", pred_a),
    ("prune_b_minc38_maxm15", pred_b),
    ("prune_c_dual_oct50_maxm20", pred_c),
    ("prune_d_maxc48_minc38", pred_d),
    ("prune_union_a_b", lambda row: pred_a(row) or pred_b(row)),
    ("prune_union_a_b_c", lambda row: pred_a(row) or pred_b(row) or pred_c(row)),
    ("prune_union_a_b_c_d", lambda row: pred_a(row) or pred_b(row) or pred_c(row) or pred_d(row)),
]


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    if not PERIODICITY_PATH.exists():
        raise RuntimeError(f"Missing cached periodicity profile: {PERIODICITY_PATH.relative_to(ROOT)}")
    if not PRECISION_PATH.exists():
        raise RuntimeError(f"Missing 14.30 additions precision profile: {PRECISION_PATH.relative_to(ROOT)}")

    periodicity_payload = v2.load_json(PERIODICITY_PATH)
    precision_payload = v2.load_json(PRECISION_PATH)
    if periodicity_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Periodicity profile is not marked reference-free during detection.")
    if precision_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("14.30 precision profile is not marked reference-free during detection.")

    periodicity_rows = list(periodicity_payload.get("rows", []))
    precision_rows = list(precision_payload.get("rows", []))
    precision_by_token = {token(row): row for row in precision_rows}
    if not periodicity_rows or not precision_rows:
        raise RuntimeError("Required cached profile rows are missing.")

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
    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    champion_1419_additions = bench.rows_to_counter(cached_rows, bench.champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_1419_additions
    score_1419 = recur.grade(champion_1419, reference)
    actual_1419 = (int(score_1419["matched"]), int(score_1419["missing"]), int(score_1419["extra"]))
    if actual_1419 != EXPECTED_1419:
        raise RuntimeError(f"Expected frozen 14.19 counts {EXPECTED_1419}, got {actual_1419}")

    winner_rows = [row for row in periodicity_rows if gate.sig_d(row)]
    periodicity_additions = gate.rows_to_counter(winner_rows, lambda row: True)
    champion_1430 = champion_1419 + periodicity_additions
    score_1430 = recur.grade(champion_1430, reference)
    actual_1430 = (int(score_1430["matched"]), int(score_1430["missing"]), int(score_1430["extra"]))
    if actual_1430 != EXPECTED_1430 or abs(float(score_1430["pitchF1"]) - EXPECTED_1430_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 14.30 champion {EXPECTED_1430}/{EXPECTED_1430_F1}, "
            f"got {actual_1430}/{score_1430['pitchF1']}"
        )

    # Only the 51 validated periodicity additions are eligible for pruning.
    eligible_rows: list[dict[str, Any]] = []
    for prow in winner_rows:
        tok = token(prow)
        detail = precision_by_token.get(tok)
        if detail is None:
            raise RuntimeError(f"Missing cached 14.30 precision detail for token {tok}")
        merged = dict(detail)
        merged["token"] = list(tok)
        eligible_rows.append(merged)

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []

    for name, predicate in VARIANTS:
        pruned_tokens: Counter[tuple[int, int, int]] = Counter()
        for row in eligible_rows:
            if predicate(row):
                pruned_tokens[token(row)] = 1

        candidate = champion_1430 - pruned_tokens
        full = recur.grade(candidate, reference)

        # Reuse the established fold/section/shift validation machinery, but do
        # not use its addition-oriented acceptance flag for a precision prune.
        stability = recall.evaluate_recall(candidate, champion_1430, reference, score_1430)

        matched_change = int(full["matched"]) - EXPECTED_1430[0]
        missing_change = int(full["missing"]) - EXPECTED_1430[1]
        extra_reduction = EXPECTED_1430[2] - int(full["extra"])
        strict_accepted = (
            int(full["matched"]) == EXPECTED_1430[0]
            and int(full["missing"]) == EXPECTED_1430[1]
            and int(full["extra"]) < EXPECTED_1430[2]
            and float(full["pitchF1"]) > EXPECTED_1430_F1
            and bool(stability["crossValidationPassed"])
            and bool(stability["sectionStabilityPassed"])
            and bool(stability["shiftedWindowStabilityPassed"])
        )

        result = {
            "fullScore": full,
            "pruneCount": int(sum(pruned_tokens.values())),
            "matchedChange": matched_change,
            "missingChange": missing_change,
            "extraReduction": extra_reduction,
            "crossValidationPassed": bool(stability["crossValidationPassed"]),
            "sectionStabilityPassed": bool(stability["sectionStabilityPassed"]),
            "shiftedWindowStabilityPassed": bool(stability["shiftedWindowStabilityPassed"]),
            "acceptedOver1430": strict_accepted,
        }
        results[name] = result
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={result['pruneCount']} matchedChange={matched_change} "
            f"missingChange={missing_change} extraReduction={extra_reduction} "
            f"cv={result['crossValidationPassed']} sections={result['sectionStabilityPassed']} "
            f"shifted={result['shiftedWindowStabilityPassed']} accepted={strict_accepted}",
            flush=True,
        )
        if strict_accepted:
            accepted.append((name, result))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (
                float(item[1]["fullScore"]["pitchF1"]),
                int(item[1]["extraReduction"]),
            ),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_14_30_champion"
        winner_eval = {
            "fullScore": score_1430,
            "pruneCount": 0,
            "matchedChange": 0,
            "missingChange": 0,
            "extraReduction": 0,
            "crossValidationPassed": True,
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver1430": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during cached 14.30 periodicity precision-prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-14.30-cached-periodicity-zero-precision-prune",
        "baseline1430Score": score_1430,
        "eligiblePeriodicityAdditionCount": len(eligible_rows),
        "results": results,
        "winner": winner_name,
        "winnerEvaluation": winner_eval,
        "validatedNewChampion": validated_new_champion,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "freeze-validated-precision-pruned-successor-and-profile-remaining-periodicity-additions"
            if validated_new_champion
            else "retain-14.30-and-profile-next-independent-precision-prune-family"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "baseline1430PitchF1": score_1430["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.30 CACHED PERIODICITY ZERO-PRECISION PRUNE V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", score_1430["pitchF1"])
    print("Baseline matched/missing/extra:", score_1430["matched"], "/", score_1430["missing"], "/", score_1430["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner_eval["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner_eval["fullScore"]["matched"], "/", winner_eval["fullScore"]["missing"], "/", winner_eval["fullScore"]["extra"])
    print("Winner prune count:", winner_eval["pruneCount"])
    print("Winner matched change:", winner_eval["matchedChange"])
    print("Winner missing change:", winner_eval["missingChange"])
    print("Winner extra reduction:", winner_eval["extraReduction"])
    print("Winner cross-validation passed:", winner_eval["crossValidationPassed"])
    print("Winner section stability passed:", winner_eval["sectionStabilityPassed"])
    print("Winner shifted-window stability passed:", winner_eval["shiftedWindowStabilityPassed"])
    print("Validated new champion:", validated_new_champion)
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
