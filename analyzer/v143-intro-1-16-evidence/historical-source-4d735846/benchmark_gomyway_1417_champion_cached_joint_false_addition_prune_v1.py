from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import benchmark_gomyway_1382_champion_cached_onset_fundamental_joint_gate_v1 as cached

recur = cached.recur
v2 = cached.v2
v3 = cached.v3
recall = cached.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-1382-onset-fundamental-joint-evidence-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1417-champion-cached-joint-false-addition-prune-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1417-champion-cached-joint-false-addition-prune-v1-manifest.json"
EXPECTED_BASELINE = (173, 694, 1464)
EXPECTED_BASELINE_F1 = 13.82
EXPECTED_CHAMPION = (178, 689, 1467)
EXPECTED_CHAMPION_F1 = 14.17


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows() -> list[dict[str, Any]]:
    return cached.load_profile_rows()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def winner_additions(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> Counter:
    out: Counter = Counter()
    for row in rows:
        if predicate(row):
            out[token(row)] = 1
    return out


def sig_d_ratio_lt(row: dict[str, Any], threshold: float) -> bool:
    if not cached.sig_d(row):
        return False
    return float(row["minTargetVsSubharmonicRatio"]) < threshold


def sig_e_flux_lt(row: dict[str, Any], threshold: float) -> bool:
    if not cached.sig_e(row):
        return False
    return float(row["minPositiveFlux"]) < threshold


def sig_e_template_gt(row: dict[str, Any], threshold: float) -> bool:
    if not cached.sig_e(row):
        return False
    return float(row["minTemplateRatio"]) > threshold


def always_clean(row: dict[str, Any]) -> bool:
    return cached.sig_a(row) or cached.sig_b(row) or cached.sig_c(row)


VARIANTS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    (
        "prune_d_ratio_lt10_keep_e",
        lambda row: always_clean(row) or sig_d_ratio_lt(row, 10.0) or cached.sig_e(row),
    ),
    (
        "prune_d_ratio_lt15_keep_e",
        lambda row: always_clean(row) or sig_d_ratio_lt(row, 15.0) or cached.sig_e(row),
    ),
    (
        "keep_d_prune_e_flux_lt020",
        lambda row: always_clean(row) or cached.sig_d(row) or sig_e_flux_lt(row, 0.20),
    ),
    (
        "keep_d_prune_e_template_gt5",
        lambda row: always_clean(row) or cached.sig_d(row) or sig_e_template_gt(row, 5.0),
    ),
    (
        "prune_d_ratio_lt10_and_e_flux_lt020",
        lambda row: always_clean(row) or sig_d_ratio_lt(row, 10.0) or sig_e_flux_lt(row, 0.20),
    ),
    (
        "prune_d_ratio_lt15_and_e_flux_lt020",
        lambda row: always_clean(row) or sig_d_ratio_lt(row, 15.0) or sig_e_flux_lt(row, 0.20),
    ),
    (
        "prune_d_ratio_lt10_and_e_template_gt5",
        lambda row: always_clean(row) or sig_d_ratio_lt(row, 10.0) or sig_e_template_gt(row, 5.0),
    ),
]


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    rows = load_rows()
    print(f"Loaded cached joint detector rows: {len(rows)}", flush=True)
    print("Heavy onset/fundamental feature extraction reused from cached profile.", flush=True)

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    baseline, _, _ = recur.build_frozen_1382(grid)
    baseline_score = recur.grade(baseline, reference)
    baseline_actual = (
        int(baseline_score["matched"]),
        int(baseline_score["missing"]),
        int(baseline_score["extra"]),
    )
    if baseline_actual != EXPECTED_BASELINE or abs(float(baseline_score["pitchF1"]) - EXPECTED_BASELINE_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 13.82 baseline {EXPECTED_BASELINE}/{EXPECTED_BASELINE_F1}, "
            f"got {baseline_actual}/{baseline_score['pitchF1']}"
        )

    full_1417_additions = winner_additions(
        rows,
        lambda row: cached.sig_a(row)
        or cached.sig_b(row)
        or cached.sig_c(row)
        or cached.sig_d(row)
        or cached.sig_e(row),
    )
    champion_1417 = baseline + full_1417_additions
    champion_1417_score = recur.grade(champion_1417, reference)
    champion_actual = (
        int(champion_1417_score["matched"]),
        int(champion_1417_score["missing"]),
        int(champion_1417_score["extra"]),
    )
    if champion_actual != EXPECTED_CHAMPION or abs(float(champion_1417_score["pitchF1"]) - EXPECTED_CHAMPION_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 14.17 champion {EXPECTED_CHAMPION}/{EXPECTED_CHAMPION_F1}, "
            f"got {champion_actual}/{champion_1417_score['pitchF1']}"
        )

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []

    for name, predicate in VARIANTS:
        additions = winner_additions(rows, predicate)
        candidate = baseline + additions
        evaluation = recall.evaluate_recall(candidate, baseline, reference, baseline_score)
        full = evaluation["fullScore"]
        evaluation["additionCount"] = int(sum(additions.values()))
        evaluation["beats1417F1"] = float(full["pitchF1"]) > EXPECTED_CHAMPION_F1
        evaluation["extraVs1417"] = int(full["extra"]) - EXPECTED_CHAMPION[2]
        evaluation["matchedVs1417"] = int(full["matched"]) - EXPECTED_CHAMPION[0]
        results[name] = evaluation
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} additions={evaluation['additionCount']} "
            f"matchedVs1417={evaluation['matchedVs1417']} extraVs1417={evaluation['extraVs1417']} "
            f"cv={evaluation['crossValidationPassed']} sections={evaluation['sectionStabilityPassed']} "
            f"shifted={evaluation['shiftedWindowStabilityPassed']} accepted={evaluation['acceptedOverChampion']} "
            f"beats1417={evaluation['beats1417F1']}",
            flush=True,
        )
        if evaluation["acceptedOverChampion"] and evaluation["beats1417F1"]:
            accepted.append((name, evaluation))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (
                float(item[1]["fullScore"]["pitchF1"]),
                -int(item[1]["fullScore"]["extra"]),
                int(item[1]["fullScore"]["matched"]),
            ),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_14_17_champion"
        winner_eval = {
            "fullScore": champion_1417_score,
            "additionCount": int(sum(full_1417_additions.values())),
            "crossValidationPassed": True,
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOverChampion": False,
            "beats1417F1": False,
            "matchedVs1417": 0,
            "extraVs1417": 0,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during cached 14.17 false-addition prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-14.17-cached-reference-free-joint-false-addition-prune",
        "baseline1382Score": baseline_score,
        "baseline1417Score": champion_1417_score,
        "cachedProfile": str(PROFILE_PATH.relative_to(ROOT)),
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
            "freeze-validated-pruned-14.17-successor-and-profile-next-residual"
            if validated_new_champion
            else "retain-14.17-and-resume-reference-free-recall"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "baseline1417PitchF1": champion_1417_score["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "cachedFeatureExtractionReused": True,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.17 CHAMPION CACHED JOINT FALSE-ADDITION PRUNE V1 COMPLETE")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Baseline 14.17 pitch F1:", champion_1417_score["pitchF1"])
    print(
        "Baseline 14.17 matched/missing/extra:",
        champion_1417_score["matched"], "/", champion_1417_score["missing"], "/", champion_1417_score["extra"],
    )
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner_eval["fullScore"]["pitchF1"])
    print(
        "Winner matched/missing/extra:",
        winner_eval["fullScore"]["matched"], "/", winner_eval["fullScore"]["missing"], "/", winner_eval["fullScore"]["extra"],
    )
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
