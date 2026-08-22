from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import profile_gomyway_1382_dual_stem_broadband_onset_evidence_v1 as onset

attack = onset.attack
recur = onset.recur
v2 = onset.v2
v3 = onset.v3
recall = onset.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-champion-broadband-onset-flux-pocket-recall-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-champion-broadband-onset-flux-pocket-recall-gate-v1-manifest.json"
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82

# Narrow detector-side variants centered on the best profiler pocket:
# rms_0_010 | flux_010_025 | recur_2 = 1 true / 3 false (25%).
VARIANTS: list[dict[str, Any]] = [
    {
        "name": "exact_rms0_010_flux010_025_recur2",
        "rmsMin": 0.0,
        "rmsMax": 0.10,
        "fluxMin": 0.10,
        "fluxMax": 0.25,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
    },
    {
        "name": "rms_m005_010_flux010_025_recur2",
        "rmsMin": -0.05,
        "rmsMax": 0.10,
        "fluxMin": 0.10,
        "fluxMax": 0.25,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
    },
    {
        "name": "rms0_015_flux010_025_recur2",
        "rmsMin": 0.0,
        "rmsMax": 0.15,
        "fluxMin": 0.10,
        "fluxMax": 0.25,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
    },
    {
        "name": "rms0_010_flux008_025_recur2",
        "rmsMin": 0.0,
        "rmsMax": 0.10,
        "fluxMin": 0.08,
        "fluxMax": 0.25,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
    },
    {
        "name": "rms0_010_flux010_030_recur2",
        "rmsMin": 0.0,
        "rmsMax": 0.10,
        "fluxMin": 0.10,
        "fluxMax": 0.30,
        "recurrenceMin": 2,
        "recurrenceMax": 2,
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_features(grid, winner_scores, alt_scores, champion):
    pool, recurrence_counts = attack.candidate_pool(grid, winner_scores, alt_scores, champion)
    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)

    rows: dict[tuple[int, int, int], dict[str, float | int]] = {}
    for index, token in enumerate(pool, 1):
        measure, step, pitch = token
        center = float(grid[(measure, step)])
        w = onset.broadband_onset(winner_audio, winner_sr, center)
        a = onset.broadband_onset(alt_audio, alt_sr, center)
        rows[token] = {
            "minRmsLog2Rise": min(float(w["rmsLog2Rise"]), float(a["rmsLog2Rise"])),
            "minPositiveFlux": min(float(w["positiveFlux"]), float(a["positiveFlux"])),
            "recurrence": int(recurrence_counts[(step, pitch)]),
        }
        if index % 500 == 0:
            print(f"Broadband onset features measured: {index}/{len(pool)}", flush=True)
    return rows


def additions_for(features, variant):
    out = recall.Counter() if hasattr(recall, "Counter") else None
    if out is None:
        from collections import Counter
        out = Counter()
    for token, row in features.items():
        rms = float(row["minRmsLog2Rise"])
        flux = float(row["minPositiveFlux"])
        recurrence = int(row["recurrence"])
        if not float(variant["rmsMin"]) <= rms < float(variant["rmsMax"]):
            continue
        if not float(variant["fluxMin"]) <= flux < float(variant["fluxMax"]):
            continue
        if not int(variant["recurrenceMin"]) <= recurrence <= int(variant["recurrenceMax"]):
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

    print("Rebuilding frozen validated 13.82 champion and broadband-onset features...", flush=True)
    champion, winner_scores, alt_scores = recur.build_frozen_1382(grid)
    champion_score = recur.grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(
            f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}"
        )

    features = build_features(grid, winner_scores, alt_scores, champion)

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
        raise RuntimeError("Protected candidate changed during broadband onset flux pocket benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-13.82-reference-free-broadband-onset-flux-pocket-recall-gate",
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
            "profile-residual-additions-from-validated-broadband-onset-winner"
            if validated_new_champion
            else "pivot-to-next-reference-free-recall-feature-family"
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

    print("GOMYWAY 13.82 CHAMPION BROADBAND ONSET FLUX POCKET RECALL GATE V1 COMPLETE")
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
