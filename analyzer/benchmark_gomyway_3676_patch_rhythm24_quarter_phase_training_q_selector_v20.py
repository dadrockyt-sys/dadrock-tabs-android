from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-quarter-phase-training-q-selector-v20.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-quarter-phase-training-q-selector-v20-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 4
PHASE = 0.25
PERIODS = (2, 4)
EXPLORATORY_QS = (0.025, 0.03, 0.04)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase_features(rows: list[dict[str, Any]]) -> np.ndarray:
    out = []
    for r in rows:
        step = int(r["step"])
        vals = []
        for p in PERIODS:
            a = 2.0 * math.pi * (step % p) / float(p)
            vals.extend([math.sin(a), math.cos(a)])
        out.append(vals)
    return np.asarray(out, dtype=np.float64)


def pass_at_q(scores: np.ndarray, yy: np.ndarray, q: float):
    held = v1.select_top_fraction(scores, yy, q)
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    passed = held["true"] > 0 and lift >= 5.0
    return bool(passed), float(lift), held, base


def choose_q_train_only_quarter_phase(
    x_train: np.ndarray,
    y_train: np.ndarray,
    measures_train: np.ndarray,
    radius: int,
    lam: float,
    base_q: float,
) -> tuple[float, dict[str, Any]]:
    lo, hi = int(np.min(measures_train)), int(np.max(measures_train))
    inner_ids = np.asarray(
        [v18.phased_fold(int(m), lo, hi, INNER_FOLDS, PHASE) for m in measures_train],
        dtype=np.int16,
    )

    candidates = []
    seen = set()
    q_values = [float(base_q), *EXPLORATORY_QS]
    q_values = [q for q in q_values if not (q in seen or seen.add(q))]

    for q in q_values:
        pass_count = 0
        lifts = []
        details = []
        for inner_fold in range(INNER_FOLDS):
            val = inner_ids == inner_fold
            subtrain = ~val
            if int(np.sum(val)) == 0 or int(np.sum(subtrain)) == 0:
                continue
            model = v2.fit_pairwise_ranker(
                x_train[subtrain], y_train[subtrain], measures_train[subtrain], radius, lam
            )
            scores = v2.scores_for(x_train[val], model)
            passed, lift, held, base = pass_at_q(scores, y_train[val], q)
            pass_count += int(passed)
            lifts.append(lift)
            details.append({
                "innerFold": inner_fold,
                "q": float(q),
                "passed": bool(passed),
                "lift": round(float(lift), 2),
                "candidate": held,
                "base": base,
            })

        mean_lift = float(np.mean(lifts)) if lifts else -999.0
        candidates.append({
            "q": float(q),
            "innerPasses": int(pass_count),
            "meanLift": round(mean_lift, 4),
            "distanceFromBaseQ": abs(float(q) - float(base_q)),
            "innerFolds": details,
        })

    # Training-only selection. Primary criterion is number of passing inner folds,
    # secondary is mean precision lift. If still tied, stay closest to V14/V17's
    # already-established base q rather than preferring a post-hoc tighter value.
    candidates.sort(
        key=lambda c: (
            int(c["innerPasses"]),
            float(c["meanLift"]),
            -float(c["distanceFromBaseQ"]),
        ),
        reverse=True,
    )
    winner = candidates[0]
    return float(winner["q"]), {
        "baseQ": float(base_q),
        "candidateQs": [float(q) for q in q_values],
        "chosenQ": float(winner["q"]),
        "switchedFromBase": abs(float(winner["q"]) - float(base_q)) > 1e-12,
        "rule": "quarter-phase-inner-pass-count-then-mean-lift-then-base-proximity",
        "candidates": candidates,
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows],
        dtype=np.float64,
    )
    x = np.concatenate([x_base, phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    ids = np.asarray(
        [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, PHASE) for m in measures],
        dtype=np.int16,
    )

    print("Starting V20 quarter-phase training-only q-selector exploratory benchmark", flush=True)
    print("Unique phase-0.25 partition only; duplicate V18 scheme labels removed", flush=True)
    print("Q=0.03 is exploratory because it was identified after V19; confirmation must use unseen phases", flush=True)

    results = []
    passes = 0
    switched = []

    for fold in range(OUTER_FOLDS):
        print(f"quarterPhase0.25: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test

        print("    heartbeat V20 V5 model selection", flush=True)
        chosen = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])
        base_q = float(chosen["tailQuantile"])

        print("    heartbeat V20 quarter-phase training-only q selector", flush=True)
        selected_q, selector = choose_q_train_only_quarter_phase(
            x[train], y[train], measures[train], radius, lam, base_q
        )

        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)
        passed, lift, held, base = pass_at_q(scores, y[test], selected_q)
        passes += int(passed)
        if selector["switchedFromBase"]:
            switched.append({"fold": fold, "baseQ": base_q, "chosenQ": selected_q})

        results.append({
            "phase": PHASE,
            "fold": fold,
            "chosenModel": chosen,
            "selector": selector,
            "outerQ": float(selected_q),
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(float(lift), 2),
            "passed": bool(passed),
        })

        print(
            f"  baseQ={base_q} chosenQ={selected_q} held={held['true']}/{held['false']} "
            f"precision={held['precision']} base={base['precision']} lift={round(lift,2)} pass={passed}",
            flush=True,
        )

    exploratory_success = passes == OUTER_FOLDS
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V20")

    output = {
        "schemaVersion": 20,
        "profileType": "36.76-rhythm24-quarter-phase-training-q-selector-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "periods": list(PERIODS),
        "phase": PHASE,
        "candidateQs": ["baseQ", *EXPLORATORY_QS],
        "q003WasPostHocFromV19": True,
        "outerFoldsPassed": passes,
        "outerFoldsTotal": OUTER_FOLDS,
        "switchedFolds": switched,
        "quarterPhaseExploratorySuccess": exploratory_success,
        "results": results,
        "requiresUnseenPhaseConfirmation": True,
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
        "schemaVersion": 20,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "outerFoldsPassed": passes,
        "outerFoldsTotal": OUTER_FOLDS,
        "quarterPhaseExploratorySuccess": exploratory_success,
        "requiresUnseenPhaseConfirmation": True,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 QUARTER-PHASE TRAINING Q SELECTOR V20 COMPLETE")
    print("Quarter-phase folds passed:", passes, "/", OUTER_FOLDS)
    print("Switched folds:", switched)
    print("Quarter-phase exploratory success:", exploratory_success)
    print("Requires unseen-phase confirmation: True")
    print("Validated new champion: False")
    print("Professional reference used to choose q: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
