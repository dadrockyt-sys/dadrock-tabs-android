from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_v5_v9_hybrid_sectionpass_nested_cv_v10 as v10
import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pointwise_ridge_section_calibrated_nested_cv_v9 as v9
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V10_PATH = PUBLIC / "gomyway-3676-patch-v5-v9-hybrid-sectionpass-nested-cv-v10.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-v10-cross-architecture-score-blend-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-v10-cross-architecture-score-blend-v1-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
# Predeclared diagnostic blend weights. Alpha is the pointwise V9 contribution.
ALPHAS = [0.10, 0.25, 0.50]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scheme_ids(measures: np.ndarray, scheme: str) -> np.ndarray:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    if scheme == "normal":
        return np.asarray([int(m) % OUTER_FOLDS for m in measures], dtype=np.int16)
    if scheme == "section":
        return np.asarray([v1.contiguous_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)
    if scheme == "shiftedWindow":
        return np.asarray([v1.shifted_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)
    raise ValueError(f"Unknown scheme: {scheme}")


def training_z(train_scores: np.ndarray, test_scores: np.ndarray) -> np.ndarray:
    train_scores = np.asarray(train_scores, dtype=np.float64)
    test_scores = np.asarray(test_scores, dtype=np.float64)
    mean = float(np.mean(train_scores))
    std = float(np.std(train_scores))
    if std <= 1e-8:
        std = 1.0
    return (test_scores - mean) / std


def evaluate(scores: np.ndarray, y: np.ndarray, q: float) -> dict[str, Any]:
    held = v1.select_top_fraction(scores, y, q)
    base = v1.base_stats(y)
    lift = float(held["precision"]) - float(base["precision"])
    passed = int(held["true"]) > 0 and lift >= 5.0
    return {
        "q": float(q),
        "true": int(held["true"]),
        "false": int(held["false"]),
        "precision": held["precision"],
        "selectedPct": held["selectedPct"],
        "basePrecision": base["precision"],
        "lift": round(lift, 2),
        "passed": bool(passed),
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source profile not anchored to frozen 36.76 champion")
    source_rows = list(source.get("candidateSlots") or [])
    if not source_rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing")

    v10_payload = json.loads(V10_PATH.read_text(encoding="utf-8"))
    feature_names = sorted((source_rows[0].get("features") or {}).keys())
    x = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in source_rows],
        dtype=np.float64,
    )
    y = np.asarray([str(r.get("label")) == "true" for r in source_rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in source_rows], dtype=np.int32)

    baseline_rows: list[dict[str, Any]] = []
    policy_rows: dict[str, list[dict[str, Any]]] = {str(a): [] for a in ALPHAS}

    for scheme in ("normal", "section", "shiftedWindow"):
        ids = scheme_ids(measures, scheme)
        saved_by_fold = {int(r["fold"]): r for r in list(v10_payload.get(scheme) or [])}
        for fold in range(OUTER_FOLDS):
            print(f"{scheme}: fold {fold + 1}/{OUTER_FOLDS}", flush=True)
            saved = saved_by_fold[fold]
            test = ids == fold
            train = ~test

            # Recompute both choices using training data only. These are exactly the two
            # architectures available to V10 before the outer fold is graded.
            print("    heartbeat blend V5 model selection", flush=True)
            v5_choice = v5.choose_model(x[train], y[train], measures[train])
            print("    heartbeat blend V9 model selection", flush=True)
            v9_choice = v9.choose_model(x[train], y[train], measures[train])
            architecture = v10.choose_hybrid(v5_choice, v9_choice)

            v5_model = v2.fit_pairwise_ranker(
                x[train], y[train], measures[train],
                int(v5_choice["pairRadius"]), float(v5_choice["lambda"]),
            )
            v9_model = v9.fit_pointwise_ridge(x[train], y[train], float(v9_choice["lambda"]))

            v5_train = v2.scores_for(x[train], v5_model)
            v5_test = v2.scores_for(x[test], v5_model)
            v9_train = v9.scores_for(x[train], v9_model)
            v9_test = v9.scores_for(x[test], v9_model)
            v5z = training_z(v5_train, v5_test)
            v9z = training_z(v9_train, v9_test)

            if architecture == "v9":
                base_scores = v9_test
                base_q = float(v9_choice["tailQuantile"])
            else:
                base_scores = v5_test
                base_q = float(v5_choice["tailQuantile"])

            baseline_eval = evaluate(base_scores, y[test], base_q)
            baseline_rows.append({
                "scheme": scheme,
                "fold": fold,
                "architecture": architecture,
                "v5Q": float(v5_choice["tailQuantile"]),
                "v9Q": float(v9_choice["tailQuantile"]),
                "evaluation": baseline_eval,
            })

            for alpha in ALPHAS:
                # Preserve V10's V9-selected folds exactly. Only V5 residual folds receive
                # cross-family score blending, and V5's training-only q remains fixed.
                if architecture == "v5":
                    scores = (1.0 - float(alpha)) * v5z + float(alpha) * v9z
                    q = float(v5_choice["tailQuantile"])
                    applied = True
                else:
                    scores = v9_test
                    q = float(v9_choice["tailQuantile"])
                    applied = False

                ev = evaluate(scores, y[test], q)
                policy_rows[str(alpha)].append({
                    "scheme": scheme,
                    "fold": fold,
                    "v10Architecture": architecture,
                    "blendApplied": applied,
                    "alphaV9": float(alpha),
                    "q": q,
                    "evaluation": ev,
                    "baselinePassed": bool(baseline_eval["passed"]),
                    "flip": (
                        "failToPass" if (not baseline_eval["passed"] and ev["passed"])
                        else "passToFail" if (baseline_eval["passed"] and not ev["passed"])
                        else "none"
                    ),
                })

    baseline_passes = sum(bool(r["evaluation"]["passed"]) for r in baseline_rows)
    if baseline_passes != 12:
        print(f"Warning: recomputed V10 baseline expected 12/15, found {baseline_passes}/15", flush=True)

    policies: list[dict[str, Any]] = []
    supported: list[float] = []
    for alpha in ALPHAS:
        rows = policy_rows[str(alpha)]
        passes = sum(bool(r["evaluation"]["passed"]) for r in rows)
        rescues = [{"scheme": r["scheme"], "fold": r["fold"]} for r in rows if r["flip"] == "failToPass"]
        collateral = [{"scheme": r["scheme"], "fold": r["fold"]} for r in rows if r["flip"] == "passToFail"]
        rec = {
            "alphaV9": float(alpha),
            "passes": passes,
            "rescues": rescues,
            "collateralLosses": collateral,
            "netDelta": passes - baseline_passes,
            "supported": passes > baseline_passes and len(collateral) == 0,
        }
        policies.append(rec)
        if rec["supported"]:
            supported.append(float(alpha))
        print("POLICY", rec, flush=True)

    ready = len(supported) > 0
    next_target = (
        "strict-training-only-v10-cross-architecture-score-blend-cv"
        if ready
        else "retire-cross-architecture-score-blend-and-pivot-residual-strategy"
    )

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V10 score-blend diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-v10-cross-architecture-score-blend-diagnostic",
        "importantCaveat": "Blend weights are predeclared. Both score normalizations use training-partition statistics only. Outer labels are used only afterward for diagnostic grading; supported alpha must be re-run in a fresh strict nested benchmark before any architectural claim.",
        "alphas": ALPHAS,
        "baselineV10Passes": baseline_passes,
        "baselineV10Total": len(baseline_rows),
        "policies": policies,
        "supportedAlphas": supported,
        "crossArchitectureScoreBlendSignalReady": ready,
        "nextTarget": next_target,
        "baselineRows": baseline_rows,
        "policyRows": policy_rows,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseBlend": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "baselineV10Passes": baseline_passes,
        "supportedAlphas": supported,
        "crossArchitectureScoreBlendSignalReady": ready,
        "nextTarget": next_target,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH V10 CROSS-ARCHITECTURE SCORE BLEND V1 COMPLETE")
    print("V10 passes:", baseline_passes, "/", len(baseline_rows))
    for p in policies:
        print(
            f"alpha={p['alphaV9']} passes={p['passes']} rescues={p['rescues']} "
            f"collateralLosses={p['collateralLosses']} supported={p['supported']}"
        )
    print("Supported alphas:", supported)
    print("Cross-architecture score-blend signal ready:", ready)
    print("Next target:", next_target)
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Professional reference used to choose blend: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
