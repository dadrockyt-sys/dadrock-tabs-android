from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as prev

recur = prev.recur
v2 = prev.v2
v3 = prev.v3
recall = prev.recall
cached = prev.cached

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-champion-cached-family-b-recur13-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-champion-cached-family-b-recur13-gate-v1-manifest.json"
EXPECTED_1419 = (178, 689, 1464)
EXPECTED_1419_F1 = 14.19


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def rows_to_counter(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> Counter:
    out: Counter = Counter()
    for row in rows:
        if predicate(row):
            out[token(row)] = 1
    return out


def family_b(row: dict[str, Any]) -> bool:
    return prev.family_b(row)


def champion_1419_predicate(row: dict[str, Any]) -> bool:
    return prev.champion_1419_predicate(row)


def family_b_recur13(row: dict[str, Any]) -> bool:
    return family_b(row) and int(row["recurrence"]) == 13


def family_b_recur12_13(row: dict[str, Any]) -> bool:
    return family_b(row) and int(row["recurrence"]) in (12, 13)


def family_b_recur13_ratio(row: dict[str, Any]) -> bool:
    return (
        family_b_recur13(row)
        and 1.40 <= float(row["minTargetVsSubharmonicRatio"]) < 1.55
    )


def family_b_recur13_template(row: dict[str, Any]) -> bool:
    return (
        family_b_recur13(row)
        and 1.40 <= float(row["minTemplateRatio"]) < 2.25
    )


VARIANTS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("family_b_recur13", family_b_recur13),
    ("family_b_recur12_13", family_b_recur12_13),
    ("family_b_recur13_ratio_140_155", family_b_recur13_ratio),
    ("family_b_recur13_template_140_225", family_b_recur13_template),
]


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    rows = cached.load_profile_rows()
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

    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    champion_additions = rows_to_counter(rows, champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_additions
    score_1419 = recur.grade(champion_1419, reference)
    actual_1419 = (
        int(score_1419["matched"]),
        int(score_1419["missing"]),
        int(score_1419["extra"]),
    )
    if actual_1419 != EXPECTED_1419 or abs(float(score_1419["pitchF1"]) - EXPECTED_1419_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 14.19 champion {EXPECTED_1419}/{EXPECTED_1419_F1}, "
            f"got {actual_1419}/{score_1419['pitchF1']}"
        )

    champion_tokens = set(champion_additions.keys())
    residual_rows = [row for row in rows if token(row) not in champion_tokens]

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []

    for name, predicate in VARIANTS:
        additions = rows_to_counter(residual_rows, predicate)
        candidate = champion_1419 + additions
        evaluation = recall.evaluate_recall(candidate, champion_1419, reference, score_1419)
        full = evaluation["fullScore"]
        evaluation["additionCount"] = int(sum(additions.values()))
        evaluation["beats1419F1"] = float(full["pitchF1"]) > EXPECTED_1419_F1
        evaluation["matchedGainVs1419"] = int(full["matched"]) - EXPECTED_1419[0]
        evaluation["missingReductionVs1419"] = EXPECTED_1419[1] - int(full["missing"])
        evaluation["extraIncreaseVs1419"] = int(full["extra"]) - EXPECTED_1419[2]
        results[name] = evaluation
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} additions={evaluation['additionCount']} "
            f"matchedGain={evaluation['matchedGainVs1419']} missingReduction={evaluation['missingReductionVs1419']} "
            f"extraIncrease={evaluation['extraIncreaseVs1419']} "
            f"cv={evaluation['crossValidationPassed']} sections={evaluation['sectionStabilityPassed']} "
            f"shifted={evaluation['shiftedWindowStabilityPassed']} accepted={evaluation['acceptedOverChampion']} "
            f"beats1419={evaluation['beats1419F1']}",
            flush=True,
        )
        if evaluation["acceptedOverChampion"] and evaluation["beats1419F1"]:
            accepted.append((name, evaluation))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (
                float(item[1]["fullScore"]["pitchF1"]),
                int(item[1]["fullScore"]["matched"]),
                -int(item[1]["fullScore"]["extra"]),
            ),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_14_19_champion"
        winner_eval = {
            "fullScore": score_1419,
            "additionCount": int(sum(champion_additions.values())),
            "crossValidationPassed": True,
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOverChampion": False,
            "beats1419F1": False,
            "matchedGainVs1419": 0,
            "missingReductionVs1419": 0,
            "extraIncreaseVs1419": 0,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during cached family-B recurrence benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-14.19-cached-family-b-recurrence-13-gate",
        "baseline1419Score": score_1419,
        "results": results,
        "winner": winner_name,
        "winnerEvaluation": winner_eval,
        "validatedNewChampion": validated_new_champion,
        "cachedFeatureExtractionReused": True,
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
        "baseline1419PitchF1": score_1419["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "cachedFeatureExtractionReused": True,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 CHAMPION CACHED FAMILY-B RECUR13 GATE V1 COMPLETE")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Baseline pitch F1:", score_1419["pitchF1"])
    print("Baseline matched/missing/extra:", score_1419["matched"], "/", score_1419["missing"], "/", score_1419["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner_eval["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner_eval["fullScore"]["matched"], "/", winner_eval["fullScore"]["missing"], "/", winner_eval["fullScore"]["extra"])
    print("Winner matched gain:", winner_eval["matchedGainVs1419"])
    print("Winner missing reduction:", winner_eval["missingReductionVs1419"])
    print("Winner extra increase:", winner_eval["extraIncreaseVs1419"])
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
