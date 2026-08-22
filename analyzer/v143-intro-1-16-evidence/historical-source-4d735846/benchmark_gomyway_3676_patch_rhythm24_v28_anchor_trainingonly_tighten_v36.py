from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28
import benchmark_gomyway_3676_patch_rhythm24_oof_percentile_logit_calibration_v30 as v30
import benchmark_gomyway_3676_patch_rhythm24_oof_conservative_allscheme_consensus_v34 as v34

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-anchor-trainingonly-tighten-v36.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-anchor-trainingonly-tighten-v36-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
CHALLENGE_PHASES = v28.CONFIRM_PHASES
MIN_LIFT = 5.0
# Frozen V28 q=0.20 corresponds to a predeclared percentile floor of 0.80.
# This is an architecture anchor from the already-frozen V28 policy, not a value
# copied from V29/V31/V33/V35 diagnostics.
V28_PERCENTILE_FLOOR = 1.0 - float(v28.FROZEN_Q)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def derive_cutoff(x_train: np.ndarray, y_train: np.ndarray, measures_train: np.ndarray, radius: int, lam: float) -> tuple[float, dict[str, Any]]:
    training_cutoff, info = v34.derive_training_only_cutoff(x_train, y_train, measures_train, radius, lam)
    cutoff = max(V28_PERCENTILE_FLOOR, float(training_cutoff))
    return cutoff, {
        "architecture": "frozen-v28-percentile-floor-plus-training-only-tightening",
        "v28FrozenQ": float(v28.FROZEN_Q),
        "v28PercentileFloor": float(V28_PERCENTILE_FLOOR),
        "trainingOnlyConservativeCutoff": float(training_cutoff),
        "derivedPercentileCutoff": float(cutoff),
        "tightenedBeyondV28Floor": bool(training_cutoff > V28_PERCENTILE_FLOOR),
        "trainingOnlyDetail": info,
        "outerHeldoutLabelsUsed": False,
        "v29DiagnosticQValuesUsed": False,
        "v31ObservedCutoffCopied": False,
        "v33ObservedNumericCutoffCopied": False,
        "v35ObservedNumericCutoffCopied": False,
    }


def evaluate_phase(x: np.ndarray, y: np.ndarray, measures: np.ndarray, phase: float) -> tuple[int, list[dict[str, Any]]]:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
    rows = []
    passes = 0
    for fold in range(OUTER_FOLDS):
        print(f"phase={phase} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test
        print("    heartbeat V36 frozen V17 representation/model-selection", flush=True)
        chosen_model = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])
        print("    heartbeat V36 V28 anchor plus training-only tightening", flush=True)
        cutoff, calibration = derive_cutoff(x[train], y[train], measures[train], radius, lam)
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        train_scores = v2.scores_for(x[train], model)
        test_scores = v2.scores_for(x[test], model)
        test_pct = v30.empirical_percentile(train_scores, test_scores)
        chosen = test_pct >= cutoff
        true = int(np.sum(y[test][chosen]))
        false = int(np.sum(~y[test][chosen]))
        selected = int(np.sum(chosen))
        precision = 100.0 * true / selected if selected else 0.0
        held = {"selected": selected, "true": true, "false": false, "precision": round(float(precision), 2)}
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = bool(true > 0 and lift >= MIN_LIFT)
        v28_passed, v28_lift, v28_held, _ = v17.pass_at_q(test_scores, y[test], v28.FROZEN_Q)
        passes += int(passed)
        rows.append({
            "phase": float(phase), "fold": int(fold), "chosenModel": chosen_model,
            "trainingOnlyCalibration": calibration, "heldoutBase": base,
            "heldoutCandidate": held, "heldoutPrecisionLift": round(float(lift), 2), "passed": passed,
            "v28Comparison": {"frozenQ": float(v28.FROZEN_Q), "heldoutCandidate": v28_held,
                               "heldoutPrecisionLift": round(float(v28_lift), 2), "passed": bool(v28_passed)},
        })
        print(f"  V36 cutoff={cutoff:.6f} held={true}/{false} lift={round(lift,2)} pass={passed}; V28 pass={v28_passed}", flush=True)
    return passes, rows


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows], dtype=np.float64)
    x = np.concatenate([x_base, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)

    print("Starting V36 frozen-V28 anchor plus training-only tightening challenger", flush=True)
    print("V28 q=0.20 is used only as the previously frozen policy anchor", flush=True)
    print("No numeric cutoff from V29/V31/V33/V35 is copied", flush=True)
    print("Reserved 1/32 confirmation phases are not referenced", flush=True)

    schemes = []
    total_passes = total_folds = v28_total = rescues = regressions = 0
    tightened = 0
    for phase in CHALLENGE_PHASES:
        phase_passes, phase_rows = evaluate_phase(x, y, measures, float(phase))
        v28_phase = sum(int(r["v28Comparison"]["passed"]) for r in phase_rows)
        schemes.append({"phase": float(phase), "passes": phase_passes, "v28Passes": v28_phase, "folds": phase_rows})
        total_passes += phase_passes
        v28_total += v28_phase
        total_folds += len(phase_rows)
        for row in phase_rows:
            vp, bp = bool(row["passed"]), bool(row["v28Comparison"]["passed"])
            rescues += int(vp and not bp)
            regressions += int(bp and not vp)
            tightened += int(row["trainingOnlyCalibration"]["tightenedBeyondV28Floor"])

    min_phase = min(s["passes"] for s in schemes)
    exploratory_promising = total_passes > v28_total and min_phase >= 4 and regressions <= rescues
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V36")

    output = {
        "schemaVersion": 36,
        "profileType": "36.76-rhythm24-frozen-v28-anchor-training-only-tighten",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenReferenceRepresentation": "V17-rhythm24",
        "challengeSource": "already-exposed-V28-phases",
        "challengePhases": list(CHALLENGE_PHASES),
        "reservedUntouchedPhasesConsumed": False,
        "v28FrozenQAnchor": float(v28.FROZEN_Q),
        "v28PercentileFloor": float(V28_PERCENTILE_FLOOR),
        "foldsTightenedBeyondV28Floor": int(tightened),
        "qSearchPerformed": False,
        "v29DiagnosticQValuesUsed": False,
        "v31ObservedCutoffCopied": False,
        "v33ObservedNumericCutoffCopied": False,
        "v35ObservedNumericCutoffCopied": False,
        "outerHeldoutLabelsUsedToChooseCalibrationParameters": False,
        "challengeHeldoutLabelsUsedForEvaluationOnly": True,
        "foldsPassed": int(total_passes), "foldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase), "v28ComparisonPasses": int(v28_total),
        "rescuesVsV28": int(rescues), "regressionsVsV28": int(regressions),
        "exploratoryPromising": bool(exploratory_promising),
        "requiresUntouchedConfirmationBeforeValidation": True,
        "validatedNewChampion": False, "schemes": schemes,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False, "v7EventsModified": False, "rendererModified": False,
        "protectedBaselinesChanged": False, "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 36, "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldsPassed": int(total_passes), "foldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase), "v28ComparisonPasses": int(v28_total),
        "rescuesVsV28": int(rescues), "regressionsVsV28": int(regressions),
        "foldsTightenedBeyondV28Floor": int(tightened),
        "exploratoryPromising": bool(exploratory_promising),
        "reservedUntouchedPhasesConsumed": False,
        "qSearchPerformed": False, "v29DiagnosticQValuesUsed": False,
        "outerHeldoutLabelsUsedToChooseCalibrationParameters": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V28-ANCHOR TRAINING-ONLY TIGHTEN V36 COMPLETE")
    print("V36 folds passed:", total_passes, "/", total_folds)
    print("Minimum V36 phase passes:", min_phase, "/ 5")
    print("V28 comparison passes:", v28_total, "/", total_folds)
    print("Rescues vs V28:", rescues)
    print("Regressions vs V28:", regressions)
    print("Folds tightened beyond V28 floor:", tightened)
    print("Exploratory promising:", exploratory_promising)
    print("Reserved untouched phases consumed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
