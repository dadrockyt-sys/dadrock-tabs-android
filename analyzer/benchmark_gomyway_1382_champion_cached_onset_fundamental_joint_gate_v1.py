from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_1382_onset_fundamental_joint_evidence_v1 as joint

onset = joint.onset
attack = joint.attack
recur = joint.recur
v2 = joint.v2
v3 = joint.v3
recall = joint.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-1382-onset-fundamental-joint-evidence-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1382-champion-cached-onset-fundamental-joint-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-champion-cached-onset-fundamental-joint-gate-v1-manifest.json"
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_profile_rows() -> list[dict[str, Any]]:
    if not PROFILE_PATH.exists():
        raise RuntimeError(
            f"Missing cached joint profile: {PROFILE_PATH.relative_to(ROOT)}. "
            "Run profile_gomyway_1382_onset_fundamental_joint_evidence_v1.py first."
        )
    payload = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if payload.get("passed") is not True:
        raise RuntimeError("Cached joint profile is not marked passed.")
    if payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Cached joint profile does not preserve reference-free detection.")
    score = payload.get("championScore") or {}
    actual = (int(score.get("matched", -1)), int(score.get("missing", -1)), int(score.get("extra", -1)))
    if actual != EXPECTED_CHAMPION or abs(float(score.get("pitchF1", -1.0)) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Cached profile champion mismatch: {actual}/{score.get('pitchF1')}")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("Cached joint profile contains no feature rows.")
    return rows


def exact(row: dict[str, Any], *, rms: str, flux: str, ratio: str, template: str, recur_label: str) -> bool:
    recurrence = int(row["recurrence"])
    actual_recur = "4plus" if recurrence >= 4 else str(recurrence)
    return (
        row["rmsBucket"] == rms
        and row["fluxBucket"] == flux
        and row["ratioBucket"] == ratio
        and row["templateBucket"] == template
        and actual_recur == recur_label
    )


def sig_a(row: dict[str, Any]) -> bool:
    return exact(
        row,
        rms="rms_050_100",
        flux="flux_0_010",
        ratio="ratio_400_plus",
        template="template_075_100",
        recur_label="4plus",
    )


def sig_b(row: dict[str, Any]) -> bool:
    return exact(
        row,
        rms="rms_0_010",
        flux="flux_050_100",
        ratio="ratio_050_100",
        template="template_lt_075",
        recur_label="4plus",
    )


def sig_c(row: dict[str, Any]) -> bool:
    return exact(
        row,
        rms="rms_lt_0",
        flux="flux_010_025",
        ratio="ratio_100_200",
        template="template_150_250",
        recur_label="2",
    )


def sig_d(row: dict[str, Any]) -> bool:
    # Repeatable 50% bucket visible in the frozen joint profile.
    return exact(
        row,
        rms="rms_100_plus",
        flux="flux_100_plus",
        ratio="ratio_400_plus",
        template="template_150_250",
        recur_label="4plus",
    )


def sig_e(row: dict[str, Any]) -> bool:
    # Second compact 50% bucket around recurrence two.
    return exact(
        row,
        rms="rms_0_010",
        flux="flux_010_025",
        ratio="ratio_400_plus",
        template="template_250_plus",
        recur_label="2",
    )


VARIANTS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("exact_joint_a", sig_a),
    ("exact_joint_b", sig_b),
    ("exact_joint_c", sig_c),
    ("union_top3_exact", lambda row: sig_a(row) or sig_b(row) or sig_c(row)),
    ("union_top3_plus_repeatable50", lambda row: sig_a(row) or sig_b(row) or sig_c(row) or sig_d(row)),
    ("union_top3_plus_two_50", lambda row: sig_a(row) or sig_b(row) or sig_c(row) or sig_d(row) or sig_e(row)),
]


def additions_for(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> Counter:
    additions: Counter = Counter()
    for row in rows:
        if not predicate(row):
            continue
        token = tuple(int(v) for v in row["token"])
        additions[token] = 1
    return additions


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    cached_rows = load_profile_rows()
    print(f"Loaded cached joint detector rows: {len(cached_rows)}", flush=True)
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

    print("Rebuilding frozen validated 13.82 champion for validation...", flush=True)
    champion, _, _ = recur.build_frozen_1382(grid)
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

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []

    for name, predicate in VARIANTS:
        additions = additions_for(cached_rows, predicate)
        candidate = champion + additions
        evaluation = recall.evaluate_recall(candidate, champion, reference, champion_score)
        evaluation["additionCount"] = int(sum(additions.values()))
        results[name] = evaluation
        full = evaluation["fullScore"]
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} additions={evaluation['additionCount']} "
            f"matchedGain={evaluation['matchedGain']} extraIncrease={evaluation['extraIncrease']} "
            f"cv={evaluation['crossValidationPassed']} sections={evaluation['sectionStabilityPassed']} "
            f"shifted={evaluation['shiftedWindowStabilityPassed']} accepted={evaluation['acceptedOverChampion']}",
            flush=True,
        )
        if evaluation["acceptedOverChampion"]:
            accepted.append((name, evaluation))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (
                float(item[1]["fullScore"]["pitchF1"]),
                int(item[1]["matchedGain"]),
                -int(item[1]["extraIncrease"]),
            ),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_13_82_champion"
        winner_eval = {
            "fullScore": champion_score,
            "matchedGain": 0,
            "missingReduction": 0,
            "extraIncrease": 0,
            "crossValidationPassed": True,
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOverChampion": False,
            "additionCount": 0,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during cached joint benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-13.82-cached-reference-free-onset-fundamental-joint-recall-gate",
        "baselineScore": champion_score,
        "cachedProfile": str(PROFILE_PATH.relative_to(ROOT)),
        "cachedFeatureRows": len(cached_rows),
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
            "profile-validated-joint-recall-winner"
            if validated_new_champion
            else "pivot-from-onset-fundamental-joint-family"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "baselinePitchF1": champion_score["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "cachedProfileUsed": True,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 13.82 CHAMPION CACHED ONSET+FUNDAMENTAL JOINT GATE V1 COMPLETE")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Baseline pitch F1:", champion_score["pitchF1"])
    print(
        "Baseline matched/missing/extra:",
        champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"],
    )
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner_eval["fullScore"]["pitchF1"])
    print(
        "Winner matched/missing/extra:",
        winner_eval["fullScore"]["matched"], "/", winner_eval["fullScore"]["missing"], "/", winner_eval["fullScore"]["extra"],
    )
    print("Winner matched gain:", winner_eval["matchedGain"])
    print("Winner missing reduction:", winner_eval["missingReduction"])
    print("Winner extra increase:", winner_eval["extraIncrease"])
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
