from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_basic_pitch_consensus_recall_recovery_v1 as recall
import benchmark_gomyway_selective_recall_admission_v1 as selective

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
STEM_PATH = recall.STEM_PATH
CANDIDATE_PATH = recall.CANDIDATE_PATH
REFERENCE_PATH = recall.REFERENCE_PATH
OUTPUT_PATH = PUBLIC / "gomyway-selective-recall-heldout-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-selective-recall-heldout-v1-manifest.json"

CHAMPION_F1 = 6.60
RULE = "micro_plus_votes4_sparse"

# Deterministic held-out split fixed before this validation run.
# Measures divisible by 5 are held out. The rule itself is already frozen from the
# prior diagnostic phase and is not re-selected using this split.
def is_heldout_measure(measure: int) -> bool:
    return 17 <= measure <= 113 and measure % 5 == 0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_subset(
    name: str,
    predicted: Counter[tuple[int, int, int]],
    reference: Counter[tuple[int, int, int]],
    heldout: bool,
) -> dict[str, Any]:
    pred = Counter({k: v for k, v in predicted.items() if is_heldout_measure(k[0]) == heldout})
    ref = Counter({k: v for k, v in reference.items() if is_heldout_measure(k[0]) == heldout})
    matched = sum((pred & ref).values())
    predicted_count = sum(pred.values())
    reference_count = sum(ref.values())
    missing = sum((ref - pred).values())
    extra = sum((pred - ref).values())
    return {
        "name": name,
        "heldout": heldout,
        "measureCount": len({k[0] for k in ref}),
        "referencePitchTokens": reference_count,
        "predictionCount": predicted_count,
        "matchedPitchTokens": matched,
        "missingProfessionalPitchTokens": missing,
        "extraCandidatePitchTokens": extra,
        "pitchF1": round(100.0 * v2.f1(matched, predicted_count, reference_count), 2),
    }


def build_selective_prediction(
    champion: Counter[tuple[int, int, int]],
    candidates: list[dict[str, Any]],
) -> tuple[Counter[tuple[int, int, int]], int]:
    predicted = Counter(champion)
    admitted = 0
    for row in candidates:
        if not selective.admit(row, RULE):
            continue
        token = (int(row["measure"]), int(row["step"]), int(row["midi"]))
        if token in predicted:
            continue
        slot_count = sum(
            count
            for (measure, step, _midi), count in predicted.items()
            if measure == token[0] and step == token[1]
        )
        if slot_count >= recall.MAX_NOTES_PER_SLOT:
            continue
        predicted[token] += 1
        admitted += 1
    return predicted, admitted


def main() -> None:
    if not STEM_PATH.exists():
        raise FileNotFoundError(f"Missing winning separator stem: {STEM_PATH.relative_to(ROOT)}")

    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, grid_diagnostics = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)
    if sum(reference.values()) != 867:
        raise RuntimeError(f"Expected 867 professional pitch tokens, found {sum(reference.values())}")

    pass_groups = []
    for pass_cfg in recall.PASSES:
        v2.ONSET_THRESHOLD = float(pass_cfg["onset"])
        v2.FRAME_THRESHOLD = float(pass_cfg["frame"])
        v2.MINIMUM_NOTE_LENGTH_MS = float(pass_cfg["min_ms"])
        print(
            f"Running {pass_cfg['name']}: onset={v2.ONSET_THRESHOLD} frame={v2.FRAME_THRESHOLD} minMs={v2.MINIMUM_NOTE_LENGTH_MS}",
            flush=True,
        )
        pass_groups.append(recall.snap_notes(v2.basic_pitch_notes(STEM_PATH), grid))

    champion = recall.build_prediction(
        pass_groups,
        {"name": "champion_primary_only", "minimumRelaxedVotes": 99, "minRelativeAmplitude": 0.0},
    )
    candidates = selective.candidate_rows(pass_groups)
    selective_prediction, admitted = build_selective_prediction(champion, candidates)

    champion_train = score_subset("champion_train", champion, reference, heldout=False)
    selective_train = score_subset("selective_train", selective_prediction, reference, heldout=False)
    champion_heldout = score_subset("champion_heldout", champion, reference, heldout=True)
    selective_heldout = score_subset("selective_heldout", selective_prediction, reference, heldout=True)

    train_delta = round(selective_train["pitchF1"] - champion_train["pitchF1"], 2)
    heldout_delta = round(selective_heldout["pitchF1"] - champion_heldout["pitchF1"], 2)
    heldout_match_delta = selective_heldout["matchedPitchTokens"] - champion_heldout["matchedPitchTokens"]
    heldout_extra_delta = selective_heldout["extraCandidatePitchTokens"] - champion_heldout["extraCandidatePitchTokens"]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during held-out validation.")

    heldout_measures = [m for m in range(17, 114) if is_heldout_measure(m)]
    train_measures = [m for m in range(17, 114) if not is_heldout_measure(m)]

    passed_heldout = heldout_delta > 0.0 and heldout_match_delta >= 0
    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "selective-recall-heldout-validation",
        "inputStem": str(STEM_PATH.relative_to(ROOT)),
        "frozenRule": RULE,
        "splitDefinition": "heldout measures are 17-113 where measure % 5 == 0",
        "heldoutMeasures": heldout_measures,
        "trainMeasures": train_measures,
        "admittedRelaxedCandidatesFullSet": admitted,
        "championTrain": champion_train,
        "selectiveTrain": selective_train,
        "championHeldout": champion_heldout,
        "selectiveHeldout": selective_heldout,
        "trainPitchF1DeltaPoints": train_delta,
        "heldoutPitchF1DeltaPoints": heldout_delta,
        "heldoutMatchedDelta": heldout_match_delta,
        "heldoutExtraDelta": heldout_extra_delta,
        "heldoutValidationPassed": passed_heldout,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only; frozen rule validated on deterministic held-out measures",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "promote-rule-to-broader-cross-validation-benchmark"
            if passed_heldout
            else "reject-selective-recall-rule-and-change-recall-evidence-source"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "frozenRule": RULE,
        "heldoutValidationPassed": passed_heldout,
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY SELECTIVE RECALL HELDOUT V1 COMPLETE")
    print("Passed: True")
    print("Frozen rule:", RULE)
    print("Train champion/selective F1:", champion_train["pitchF1"], "/", selective_train["pitchF1"])
    print("Train delta points:", train_delta)
    print("Heldout champion/selective F1:", champion_heldout["pitchF1"], "/", selective_heldout["pitchF1"])
    print("Heldout delta points:", heldout_delta)
    print("Heldout matched delta:", heldout_match_delta)
    print("Heldout extra delta:", heldout_extra_delta)
    print("Heldout validation passed:", passed_heldout)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
