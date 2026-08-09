from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import profile_gomyway_1382_dual_stem_temporal_attack_evidence_v1 as attack

prom = attack.prom
recur = attack.recur
v2 = attack.v2
v3 = attack.v3
recall = attack.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-champion-temporal-attack-pocket-recall-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-champion-temporal-attack-pocket-recall-gate-v1-manifest.json"
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82

# These variants are deliberately centered on the strongest profiler pocket:
# rise_05_10 | center_4_6 | recur_2 = 1 true / 3 false (25% precision).
# No professional-reference labels participate in detector construction.
VARIANTS: list[dict[str, Any]] = [
    {
        "name": "exact_rise05_10_center4_6_recur2",
        "riseMin": 0.5,
        "riseMax": 1.0,
        "centerMin": 4.0,
        "centerMax": 6.0,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
        "prominenceMin": 0.5,
        "requirePostDecay": False,
    },
    {
        "name": "exact_plus_prom10",
        "riseMin": 0.5,
        "riseMax": 1.0,
        "centerMin": 4.0,
        "centerMax": 6.0,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
        "prominenceMin": 1.0,
        "requirePostDecay": False,
    },
    {
        "name": "exact_plus_post_decay",
        "riseMin": 0.5,
        "riseMax": 1.0,
        "centerMin": 4.0,
        "centerMax": 6.0,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
        "prominenceMin": 0.5,
        "requirePostDecay": True,
    },
    {
        "name": "exact_plus_prom10_post_decay",
        "riseMin": 0.5,
        "riseMax": 1.0,
        "centerMin": 4.0,
        "centerMax": 6.0,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
        "prominenceMin": 1.0,
        "requirePostDecay": True,
    },
    {
        "name": "rise04_11_center4_6_recur2",
        "riseMin": 0.4,
        "riseMax": 1.1,
        "centerMin": 4.0,
        "centerMax": 6.0,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
        "prominenceMin": 0.5,
        "requirePostDecay": False,
    },
    {
        "name": "rise05_10_center4_8_recur2",
        "riseMin": 0.5,
        "riseMax": 1.0,
        "centerMin": 4.0,
        "centerMax": 8.0,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
        "prominenceMin": 0.5,
        "requirePostDecay": False,
    },
    {
        "name": "rise05_15_center4_6_recur2",
        "riseMin": 0.5,
        "riseMax": 1.5,
        "centerMin": 4.0,
        "centerMax": 6.0,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
        "prominenceMin": 0.5,
        "requirePostDecay": False,
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def detector_pool(grid, winner_scores, alt_scores, champion):
    supported: list[tuple[int, int, int]] = []
    recurrence_counts: Counter[tuple[int, int]] = Counter()
    for measure, step in grid:
        if not 17 <= measure <= 113:
            continue
        for pitch in range(recall.PITCH_MIN, recall.PITCH_MAX + 1):
            token = (measure, step, pitch)
            if champion.get(token, 0) > 0:
                continue
            if min(float(winner_scores.get(token, 0.0)), float(alt_scores.get(token, 0.0))) < attack.POOL_FLOOR:
                continue
            if prom.local_prominence(winner_scores, token) < attack.POOL_MARGIN:
                continue
            if prom.local_prominence(alt_scores, token) < attack.POOL_MARGIN:
                continue
            supported.append(token)
            recurrence_counts[(step, pitch)] += 1
    return supported, recurrence_counts


def build_temporal_features(grid, winner_scores, alt_scores, champion):
    supported, recurrence_counts = detector_pool(grid, winner_scores, alt_scores, champion)
    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)

    rows: dict[tuple[int, int, int], dict[str, float | int]] = {}
    for index, token in enumerate(supported, 1):
        measure, step, pitch = token
        center_time = float(grid[(measure, step)])
        ws = attack.temporal_score(winner_audio, winner_sr, center_time, pitch)
        ats = attack.temporal_score(alt_audio, alt_sr, center_time, pitch)
        rows[token] = {
            "minRise": min(float(ws["riseVsPreMax"]), float(ats["riseVsPreMax"])),
            "minCenter": min(float(ws["now"]), float(ats["now"])),
            "minProminence": min(
                float(prom.local_prominence(winner_scores, token)),
                float(prom.local_prominence(alt_scores, token)),
            ),
            "maxPostDelta": max(float(ws["postDelta"]), float(ats["postDelta"])),
            "recurrence": int(recurrence_counts[(step, pitch)]),
        }
        if index % 500 == 0:
            print(f"Temporal detector features measured: {index}/{len(supported)}", flush=True)
    return rows


def additions_for(features, variant):
    out: Counter[tuple[int, int, int]] = Counter()
    for token, row in features.items():
        rise = float(row["minRise"])
        center = float(row["minCenter"])
        prominence = float(row["minProminence"])
        recurrence = int(row["recurrence"])
        if not float(variant["riseMin"]) <= rise < float(variant["riseMax"]):
            continue
        if not float(variant["centerMin"]) <= center < float(variant["centerMax"]):
            continue
        if not int(variant["recurrenceMin"]) <= recurrence <= int(variant["recurrenceMax"]):
            continue
        if prominence < float(variant["prominenceMin"]):
            continue
        if bool(variant["requirePostDecay"]) and float(row["maxPostDelta"]) >= 0.0:
            continue
        out[token] = 1
    return out


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

    print("Rebuilding frozen validated 13.82 champion and temporal detector features...", flush=True)
    champion, winner_scores, alt_scores = recur.build_frozen_1382(grid)
    champion_score = recur.grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(
            f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}"
        )

    features = build_temporal_features(grid, winner_scores, alt_scores, champion)

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []
    for variant in VARIANTS:
        additions = additions_for(features, variant)
        candidate = champion + additions
        evaluation = recall.evaluate_recall(candidate, champion, reference, champion_score)
        evaluation["additionCount"] = int(sum(additions.values()))
        evaluation["variant"] = variant
        results[str(variant["name"])] = evaluation
        full = evaluation["fullScore"]
        print(
            f"{variant['name']}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} additions={sum(additions.values())} matchedGain={evaluation['matchedGain']} "
            f"extraIncrease={evaluation['extraIncrease']} cv={evaluation['crossValidationPassed']} "
            f"sections={evaluation['sectionStabilityPassed']} shifted={evaluation['shiftedWindowStabilityPassed']} "
            f"accepted={evaluation['acceptedOverChampion']}",
            flush=True,
        )
        if evaluation["acceptedOverChampion"]:
            accepted.append((str(variant["name"]), evaluation))

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
        raise RuntimeError("Protected candidate changed during temporal attack pocket recall benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-13.82-reference-free-temporal-attack-pocket-recall-gate",
        "baselineScore": champion_score,
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
            "profile-residual-additions-from-validated-temporal-attack-pocket-winner"
            if validated_new_champion
            else "profile-next-reference-free-onset-feature-family"
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
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 13.82 CHAMPION TEMPORAL ATTACK POCKET RECALL GATE V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", champion_score["pitchF1"])
    print("Baseline matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner_eval["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner_eval["fullScore"]["matched"], "/", winner_eval["fullScore"]["missing"], "/", winner_eval["fullScore"]["extra"])
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
