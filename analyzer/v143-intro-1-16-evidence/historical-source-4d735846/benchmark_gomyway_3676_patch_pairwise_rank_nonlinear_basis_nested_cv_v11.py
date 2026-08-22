from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-nonlinear-basis-nested-cv-v11.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-nonlinear-basis-nested-cv-v11-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
CLIP_ABS = 1_000_000.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nonlinear_basis(x: np.ndarray, feature_names: list[str]) -> tuple[np.ndarray, list[str]]:
    """Fixed label-free nonlinear basis.

    The transform is predeclared and uses no fitted parameters or labels:
      1) original feature
      2) signed sqrt magnitude
      3) signed log1p magnitude

    V2/V5 still perform train-only mean/std normalization when fitting each model.
    A fixed extreme-value clip protects numerical stability without observing labels
    or held-out fold statistics.
    """
    raw = np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=CLIP_ABS, neginf=-CLIP_ABS)
    raw = np.clip(raw, -CLIP_ABS, CLIP_ABS)
    sqrt_term = np.sign(raw) * np.sqrt(np.abs(raw))
    log_term = np.sign(raw) * np.log1p(np.abs(raw))
    expanded = np.concatenate([raw, sqrt_term, log_term], axis=1)
    names = (
        [f"linear::{n}" for n in feature_names]
        + [f"signedSqrt::{n}" for n in feature_names]
        + [f"signedLog1p::{n}" for n in feature_names]
    )
    return expanded, names


def evaluate_scheme(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    feature_names: list[str],
    name: str,
    fold_fn: Callable[[int], int],
) -> tuple[bool, list[dict[str, Any]]]:
    ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
    rows: list[dict[str, Any]] = []
    passes = 0

    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test

        print("    heartbeat nonlinear-basis V5 model selection", flush=True)
        chosen = v5.choose_model(x[train], y[train], measures[train])
        model = v2.fit_pairwise_ranker(
            x[train],
            y[train],
            measures[train],
            int(chosen["pairRadius"]),
            float(chosen["lambda"]),
        )
        scores = v2.scores_for(x[test], model)
        q = float(chosen["tailQuantile"])
        held = v1.select_top_fraction(scores, y[test], q)
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        passes += int(passed)

        coef = np.asarray(model["coef"], dtype=np.float64)
        top_idx = np.argsort(np.abs(coef))[::-1][:10]
        top_weights = [
            {"feature": feature_names[int(j)], "weight": round(float(coef[int(j)]), 6)}
            for j in top_idx
        ]

        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train)),
            "testRows": int(np.sum(test)),
            "representation": "fixed-linear-plus-signed-sqrt-plus-signed-log1p",
            "chosen": chosen,
            "pairCount": int(model["pairCount"]),
            "tailQuantile": q,
            "topWeights": top_weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": bool(passed),
        }
        rows.append(row)

        print(
            f"  nonlinear radius={chosen['pairRadius']} lambda={chosen['lambda']} q={q} "
            f"innerSectionPass={chosen['sectionPassCount']}/{chosen['sectionFoldCount']} "
            f"held={held['true']}/{held['false']} selectedPct={held['selectedPct']} "
            f"precision={held['precision']} base={base['precision']} lift={round(lift,2)} pass={passed}",
            flush=True,
        )

    return passes == OUTER_FOLDS, rows


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_rows = list(payload.get("candidateSlots") or [])
    if not source_rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing; run patch stability profiler first")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")

    base_feature_names = sorted((source_rows[0].get("features") or {}).keys())
    x_base = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in base_feature_names] for r in source_rows],
        dtype=np.float64,
    )
    x, feature_names = nonlinear_basis(x_base, base_feature_names)
    y = np.asarray([str(r.get("label")) == "true" for r in source_rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in source_rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V11 nonlinear-basis pairwise nested CV", flush=True)
    print(
        f"Representation: {len(base_feature_names)} raw features -> {len(feature_names)} fixed nonlinear basis features", flush=True
    )
    print("Basis is label-free: linear + signed sqrt + signed log1p; V5 selection remains training-only", flush=True)

    normal_pass, normal = evaluate_scheme(
        x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS
    )
    section_pass, section = evaluate_scheme(
        x, y, measures, feature_names, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS)
    )
    shifted_pass, shifted = evaluate_scheme(
        x, y, measures, feature_names, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS)
    )

    all_rows = normal + section + shifted
    total_passes = sum(bool(r["passed"]) for r in all_rows)
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V11 nonlinear-basis nested CV")

    output = {
        "schemaVersion": 11,
        "profileType": "36.76-patch-pairwise-rank-nonlinear-basis-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "baseFeatureCount": len(base_feature_names),
        "expandedFeatureCount": len(feature_names),
        "representation": "fixed-linear-plus-signed-sqrt-plus-signed-log1p",
        "representationUsesOuterHeldoutLabels": False,
        "modelSelection": "V5-training-only-inner-contiguous-section-priority",
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": len(all_rows),
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "nonlinearBasisV11Generalizes": generalizes,
        "normal": normal,
        "section": section,
        "shiftedWindow": shifted,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 11,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "outerFoldsPassed": total_passes,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "nonlinearBasisV11Generalizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE NONLINEAR BASIS NESTED CV V11 COMPLETE")
    print("Outer folds passed:", total_passes, "/", len(all_rows))
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Nonlinear-basis V11 generalizes:", generalizes)
    print("Validated new champion: False")
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
