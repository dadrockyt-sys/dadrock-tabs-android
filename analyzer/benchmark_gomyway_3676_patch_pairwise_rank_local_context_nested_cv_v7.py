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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-local-context-nested-cv-v7.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-local-context-nested-cv-v7-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
TAIL_QUANTILES = list(v5.TAIL_QUANTILES)
CONTEXT_RADII = [2, 4, 8]
CONTEXT_ALPHAS = [0.25, 0.5, 1.0]
EPS = 1e-8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_family(name: str) -> str:
    s = str(name).lower()
    if "shift" in s:
        return "shiftedWindow"
    if "section" in s or "contig" in s:
        return "section"
    return "normal"


def local_context_scores(raw_scores: np.ndarray, measures: np.ndarray, radius: int, alpha: float) -> np.ndarray:
    raw_scores = np.asarray(raw_scores, dtype=np.float64)
    measures = np.asarray(measures, dtype=np.int32)
    global_mean = float(np.mean(raw_scores))
    global_std = float(np.std(raw_scores))
    if global_std < EPS:
        global_std = 1.0
    global_z = (raw_scores - global_mean) / global_std

    local_z = np.zeros_like(raw_scores)
    for i in range(len(raw_scores)):
        mask = np.abs(measures - measures[i]) <= int(radius)
        neighborhood = raw_scores[mask]
        if len(neighborhood) < 3:
            local_z[i] = global_z[i]
            continue
        med = float(np.median(neighborhood))
        mad = float(np.median(np.abs(neighborhood - med)))
        robust_scale = 1.4826 * mad
        if robust_scale < EPS:
            robust_scale = float(np.std(neighborhood))
        if robust_scale < EPS:
            robust_scale = global_std
        local_z[i] = (raw_scores[i] - med) / robust_scale
    return global_z + float(alpha) * local_z


def evaluate_context_choice(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    pair_radius: int,
    lam: float,
    context_radius: int,
    alpha: float,
    q: float,
) -> dict[str, Any]:
    folds: list[dict[str, Any]] = []
    for split_name, train, test in v1.inner_masks(measures):
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], pair_radius, lam)
        raw = v2.scores_for(x[test], model)
        scores = local_context_scores(raw, measures[test], context_radius, alpha)
        held = v1.select_top_fraction(scores, y[test], q)
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        folds.append({
            "split": split_name,
            "family": split_family(split_name),
            "true": int(held["true"]),
            "false": int(held["false"]),
            "precision": held["precision"],
            "selectedPct": held["selectedPct"],
            "basePrecision": base["precision"],
            "lift": round(lift, 2),
            "passed": bool(passed),
        })
    section = [f for f in folds if f["family"] == "section"]
    return {
        "folds": folds,
        "sectionPassCount": sum(bool(f["passed"]) for f in section),
        "sectionFoldCount": len(section),
        "sectionMeanLift": round(float(np.mean([float(f["lift"]) for f in section])), 3) if section else -999.0,
        "overallPassCount": sum(bool(f["passed"]) for f in folds),
        "overallFoldCount": len(folds),
        "overallMeanLift": round(float(np.mean([float(f["lift"]) for f in folds])), 3) if folds else -999.0,
        "trueTotal": sum(int(f["true"]) for f in folds),
        "falseTotal": sum(int(f["false"]) for f in folds),
    }


def choose_context(x: np.ndarray, y: np.ndarray, measures: np.ndarray, pair_radius: int, lam: float) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    total = len(CONTEXT_RADII) * len(CONTEXT_ALPHAS) * len(TAIL_QUANTILES)
    done = 0
    for context_radius in CONTEXT_RADII:
        for alpha in CONTEXT_ALPHAS:
            for q in TAIL_QUANTILES:
                done += 1
                if done == 1 or done % 9 == 0 or done == total:
                    print(f"    heartbeat local-context search {done}/{total}", flush=True)
                ev = evaluate_context_choice(x, y, measures, pair_radius, lam, context_radius, alpha, q)
                candidates.append({
                    "contextRadius": context_radius,
                    "contextAlpha": alpha,
                    "tailQuantile": q,
                    "sectionPassCount": ev["sectionPassCount"],
                    "sectionFoldCount": ev["sectionFoldCount"],
                    "sectionMeanLift": ev["sectionMeanLift"],
                    "overallPassCount": ev["overallPassCount"],
                    "overallFoldCount": ev["overallFoldCount"],
                    "overallMeanLift": ev["overallMeanLift"],
                    "trueTotal": ev["trueTotal"],
                    "falseTotal": ev["falseTotal"],
                    "folds": ev["folds"],
                })
    return max(
        candidates,
        key=lambda r: (
            int(r["sectionPassCount"]),
            float(r["sectionMeanLift"]),
            int(r["overallPassCount"]),
            float(r["overallMeanLift"]),
            int(r["trueTotal"]) - int(r["falseTotal"]),
            int(r["trueTotal"]),
            -float(r["tailQuantile"]),
            -float(r["contextAlpha"]),
            -int(r["contextRadius"]),
        ),
    )


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

        base_choice = v5.choose_model(x[train], y[train], measures[train])
        pair_radius = int(base_choice["pairRadius"])
        lam = float(base_choice["lambda"])
        context = choose_context(x[train], y[train], measures[train], pair_radius, lam)

        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], pair_radius, lam)
        raw = v2.scores_for(x[test], model)
        scores = local_context_scores(raw, measures[test], int(context["contextRadius"]), float(context["contextAlpha"]))
        held = v1.select_top_fraction(scores, y[test], float(context["tailQuantile"]))
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        passes += int(passed)

        coef = np.asarray(model["coef"])
        top_idx = np.argsort(np.abs(coef))[::-1][:8]
        top_weights = [{"feature": feature_names[int(j)], "weight": round(float(coef[int(j)]), 6)} for j in top_idx]
        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train)),
            "testRows": int(np.sum(test)),
            "pairRadius": pair_radius,
            "lambda": lam,
            "contextChoice": context,
            "pairCount": int(model["pairCount"]),
            "rankArchitecture": "pairwise-global-plus-unlabeled-local-robust-context",
            "topWeights": top_weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": bool(passed),
        }
        rows.append(row)
        print(
            f"  pairRadius={pair_radius} lambda={lam} contextRadius={context['contextRadius']} "
            f"alpha={context['contextAlpha']} q={context['tailQuantile']} "
            f"innerSectionPass={context['sectionPassCount']}/{context['sectionFoldCount']} "
            f"held={held['true']}/{held['false']} precision={held['precision']} "
            f"base={base['precision']} lift={round(lift, 2)} pass={passed}",
            flush=True,
        )
    return passes == OUTER_FOLDS, rows


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing; run patch stability profiler first")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")

    feature_names = sorted((rows[0].get("features") or {}).keys())
    x = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in rows], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V7 local-context pairwise ranking architecture pivot", flush=True)
    print("Base pairwise ranker is V5/V2; local context uses held-out scores/measures only, never labels", flush=True)

    normal_pass, normal = evaluate_scheme(x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(x, y, measures, feature_names, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(x, y, measures, feature_names, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS))

    all_rows = normal + section + shifted
    total_passes = sum(bool(r["passed"]) for r in all_rows)
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V7 local-context CV")

    output = {
        "schemaVersion": 7,
        "profileType": "36.76-patch-pairwise-rank-local-context-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "architecture": "pairwise-global-plus-unlabeled-local-robust-context",
        "contextRadii": CONTEXT_RADII,
        "contextAlphas": CONTEXT_ALPHAS,
        "tailQuantiles": TAIL_QUANTILES,
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": len(all_rows),
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pairwiseLocalContextV7Generalizes": generalizes,
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
        "schemaVersion": 7,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "outerFoldsPassed": total_passes,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pairwiseLocalContextV7Generalizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE LOCAL CONTEXT NESTED CV V7 COMPLETE")
    print("Outer folds passed:", total_passes, "/", len(all_rows))
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Pairwise local-context V7 generalizes:", generalizes)
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
