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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-multiphase-training-q-selector-v25.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-multiphase-training-q-selector-v25-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 4

# V25 is explicitly exploratory. This grid was informed by V24's diagnostic
# sweeps, so a success here must later be frozen and tested on untouched phases.
Q_GRID = (0.02, 0.025, 0.03, 0.05, 0.075, 0.10, 0.20)

# Use multiple training-only boundary geometries rather than tuning to one
# particular outer phase. No outer-heldout labels are used by the selector.
INNER_PHASES = (0.25, 0.75)

# These are the V23 confirmation geometries. V25 is a challenger on them, not a
# confirmation run, because their outcomes are already known from V23/V24.
CHALLENGE_PHASES = (0.125, 0.375, 0.625, 0.875)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pass_at_q(scores: np.ndarray, yy: np.ndarray, q: float) -> tuple[bool, float, dict[str, Any], dict[str, Any]]:
    return v17.pass_at_q(scores, yy, q)


def choose_q_train_only_multiphase(
    x_train: np.ndarray,
    y_train: np.ndarray,
    measures_train: np.ndarray,
    radius: int,
    lam: float,
    base_q: float,
) -> tuple[float, dict[str, Any]]:
    lo, hi = int(np.min(measures_train)), int(np.max(measures_train))
    q_candidates = sorted(set(float(q) for q in Q_GRID + (float(base_q),)))
    stats = {
        q: {"q": q, "passes": 0, "total": 0, "liftSum": 0.0, "lifts": [], "phasePasses": {}}
        for q in q_candidates
    }
    details: list[dict[str, Any]] = []

    for phase in INNER_PHASES:
        ids = np.asarray(
            [v18.phased_fold(int(m), lo, hi, INNER_FOLDS, phase) for m in measures_train],
            dtype=np.int16,
        )
        for inner_fold in range(INNER_FOLDS):
            val = ids == inner_fold
            subtrain = ~val
            if int(np.sum(val)) == 0 or int(np.sum(subtrain)) == 0:
                continue

            model = v2.fit_pairwise_ranker(
                x_train[subtrain], y_train[subtrain], measures_train[subtrain], radius, lam
            )
            scores = v2.scores_for(x_train[val], model)
            fold_result = {"phase": phase, "innerFold": inner_fold, "q": {}}

            for q in q_candidates:
                passed, lift, held, base = pass_at_q(scores, y_train[val], q)
                st = stats[q]
                st["passes"] += int(passed)
                st["total"] += 1
                st["liftSum"] += float(lift)
                st["lifts"].append(float(lift))
                st["phasePasses"].setdefault(str(phase), 0)
                st["phasePasses"][str(phase)] += int(passed)
                fold_result["q"][str(q)] = {
                    "passed": bool(passed),
                    "lift": round(float(lift), 2),
                    "selected": int(held["selected"]),
                    "true": int(held["true"]),
                    "false": int(held["false"]),
                    "precision": float(held["precision"]),
                    "basePrecision": float(base["precision"]),
                }
            details.append(fold_result)

    ranked = []
    for q in q_candidates:
        st = stats[q]
        phase_values = list(st["phasePasses"].values()) or [0]
        min_phase_passes = min(phase_values)
        mean_lift = st["liftSum"] / max(1, st["total"])
        # Robustness first: maximize worst-phase pass count, then total passes,
        # then mean lift. Final tie-break stays closest to the original base q.
        key = (min_phase_passes, st["passes"], mean_lift, -abs(q - float(base_q)))
        ranked.append((key, q, min_phase_passes, mean_lift))

    ranked.sort(reverse=True)
    _, chosen_q, min_phase_passes, mean_lift = ranked[0]

    summary = []
    for q in q_candidates:
        st = stats[q]
        summary.append({
            "q": q,
            "passes": int(st["passes"]),
            "total": int(st["total"]),
            "phasePasses": st["phasePasses"],
            "minPhasePasses": min(st["phasePasses"].values()) if st["phasePasses"] else 0,
            "meanLift": round(st["liftSum"] / max(1, st["total"]), 3),
        })

    return float(chosen_q), {
        "baseQ": float(base_q),
        "chosenQ": float(chosen_q),
        "qGrid": list(q_candidates),
        "innerPhases": list(INNER_PHASES),
        "selectionObjective": "max-min-phase-passes_then-total-passes_then-mean-lift_then-closest-to-base-q",
        "winnerMinPhasePasses": int(min_phase_passes),
        "winnerMeanLift": round(float(mean_lift), 3),
        "qSummary": summary,
        "innerFolds": details,
        "outerHeldoutLabelsUsed": False,
        "exploratoryPostV24Grid": True,
    }


def evaluate_phase(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    lo: int,
    hi: int,
    phase: float,
) -> tuple[int, list[dict[str, Any]]]:
    ids = np.asarray(
        [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures],
        dtype=np.int16,
    )
    passes = 0
    rows: list[dict[str, Any]] = []

    for fold in range(OUTER_FOLDS):
        print(f"phase={phase}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test

        print("    heartbeat V25 frozen V17 model-selection policy", flush=True)
        chosen = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])
        base_q = float(chosen["tailQuantile"])

        print("    heartbeat V25 training-only multiphase q selector", flush=True)
        selected_q, selector = choose_q_train_only_multiphase(
            x[train], y[train], measures[train], radius, lam, base_q
        )

        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)
        passed, lift, held, base = pass_at_q(scores, y[test], selected_q)
        passes += int(passed)

        row = {
            "phase": phase,
            "fold": fold,
            "chosenModel": chosen,
            "selector": selector,
            "outerQ": float(selected_q),
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(float(lift), 2),
            "passed": bool(passed),
        }
        rows.append(row)

        print(
            f"  baseQ={base_q} chosenQ={selected_q} held={held['true']}/{held['false']} "
            f"precision={held['precision']} base={base['precision']} lift={round(lift,2)} pass={passed}",
            flush=True,
        )

    return passes, rows


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows],
        dtype=np.float64,
    )
    x = np.concatenate([x_base, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V25 rhythm24 multiphase training-only q-selector challenger", flush=True)
    print("Frozen V17 representation/model-selection; exploratory post-V24 q grid", flush=True)
    print("Inner training-only phases:", INNER_PHASES, flush=True)
    print("Challenge phases:", CHALLENGE_PHASES, flush=True)

    schemes = []
    total_passes = 0
    total_folds = 0

    for phase in CHALLENGE_PHASES:
        p, rr = evaluate_phase(x, y, measures, lo, hi, phase)
        schemes.append({"phase": phase, "passes": p, "folds": rr})
        total_passes += p
        total_folds += OUTER_FOLDS

    min_phase_passes = min(s["passes"] for s in schemes)
    exploratory_success = total_passes >= 18 and min_phase_passes >= 4

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V25")

    output = {
        "schemaVersion": 25,
        "profileType": "36.76-rhythm24-multiphase-training-only-q-selector-exploratory-challenger",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenReferenceChampion": "V17",
        "frozenPeriods": [2, 4],
        "innerPhases": list(INNER_PHASES),
        "challengePhases": list(CHALLENGE_PHASES),
        "qGrid": list(Q_GRID),
        "postV24ExploratoryGrid": True,
        "outerHeldoutLabelsUsedForSelection": False,
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": total_folds,
        "minimumPhasePasses": min_phase_passes,
        "exploratorySuccess": exploratory_success,
        "requiresUntouchedPhaseConfirmation": True,
        "schemes": schemes,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseQ": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 25,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": total_folds,
        "minimumPhasePasses": min_phase_passes,
        "exploratorySuccess": exploratory_success,
        "requiresUntouchedPhaseConfirmation": True,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 MULTIPHASE TRAINING Q SELECTOR V25 COMPLETE")
    print("Challenge folds passed:", total_passes, "/", total_folds)
    for s in schemes:
        print("phase", s["phase"], "passes:", s["passes"], "/ 5")
    print("Minimum phase passes:", min_phase_passes, "/ 5")
    print("Exploratory success:", exploratory_success)
    print("Requires untouched-phase confirmation: True")
    print("Outer heldout labels used for selection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
