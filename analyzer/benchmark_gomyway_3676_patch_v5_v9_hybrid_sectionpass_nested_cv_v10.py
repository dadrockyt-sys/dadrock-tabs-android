from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pointwise_ridge_section_calibrated_nested_cv_v9 as v9
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-v5-v9-hybrid-sectionpass-nested-cv-v10.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-v5-v9-hybrid-sectionpass-nested-cv-v10-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose_hybrid(v5_choice: dict[str, Any], v9_choice: dict[str, Any]) -> str:
    """Predeclared training-only selector validated by the V5/V9 signal profiler.

    Choose pointwise V9 only when it wins strictly on inner contiguous-section
    pass count. Ties always fall back to the stronger standalone V5 baseline.
    No outer held-out labels or professional-reference outcomes enter here.
    """
    return "v9" if int(v9_choice["sectionPassCount"]) > int(v5_choice["sectionPassCount"]) else "v5"


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

        print("    heartbeat hybrid V5 model selection", flush=True)
        v5_choice = v5.choose_model(x[train], y[train], measures[train])
        print("    heartbeat hybrid V9 model selection", flush=True)
        v9_choice = v9.choose_model(x[train], y[train], measures[train])

        architecture = choose_hybrid(v5_choice, v9_choice)
        print(
            "    heartbeat hybrid selector "
            f"v5SectionPass={v5_choice['sectionPassCount']}/{v5_choice['sectionFoldCount']} "
            f"v9SectionPass={v9_choice['sectionPassCount']}/{v9_choice['sectionFoldCount']} "
            f"chosen={architecture}",
            flush=True,
        )

        if architecture == "v9":
            model = v9.fit_pointwise_ridge(x[train], y[train], float(v9_choice["lambda"]))
            scores = v9.scores_for(x[test], model)
            q = float(v9_choice["tailQuantile"])
            learner = "class-balanced-pointwise-ridge-v1"
            chosen = v9_choice
            model_detail = {"lambda": float(v9_choice["lambda"])}
            coef = np.asarray(model["coef"])
        else:
            model = v2.fit_pairwise_ranker(
                x[train],
                y[train],
                measures[train],
                int(v5_choice["pairRadius"]),
                float(v5_choice["lambda"]),
            )
            scores = v2.scores_for(x[test], model)
            q = float(v5_choice["tailQuantile"])
            learner = "pairwise-rank-stratified-v2-section-calibrated-v5"
            chosen = v5_choice
            model_detail = {
                "pairRadius": int(v5_choice["pairRadius"]),
                "lambda": float(v5_choice["lambda"]),
                "pairCount": int(model["pairCount"]),
            }
            coef = np.asarray(model["coef"])

        held = v1.select_top_fraction(scores, y[test], q)
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        passes += int(passed)

        top_idx = np.argsort(np.abs(coef))[::-1][:8]
        top_weights = [
            {"feature": feature_names[int(j)], "weight": round(float(coef[int(j)]), 6)}
            for j in top_idx
        ]

        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train)),
            "testRows": int(np.sum(test)),
            "hybridSelector": "choose-v9-only-if-inner-section-pass-count-strictly-exceeds-v5",
            "architectureChosen": architecture,
            "v5Choice": v5_choice,
            "v9Choice": v9_choice,
            "chosen": chosen,
            "learner": learner,
            "modelDetail": model_detail,
            "tailQuantile": q,
            "topWeights": top_weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": bool(passed),
        }
        rows.append(row)

        print(
            f"  hybrid={architecture} q={q} held={held['true']}/{held['false']} "
            f"selectedPct={held['selectedPct']} precision={held['precision']} "
            f"base={base['precision']} lift={round(lift,2)} pass={passed}",
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

    feature_names = sorted((source_rows[0].get("features") or {}).keys())
    x = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in source_rows],
        dtype=np.float64,
    )
    y = np.asarray([str(r.get("label")) == "true" for r in source_rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in source_rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting strict V5/V9 hybrid nested CV V10", flush=True)
    print(
        "Selector is fixed before outer grading: choose V9 only when its training-only "
        "inner section pass count strictly exceeds V5; otherwise use V5.",
        flush=True,
    )

    normal_pass, normal = evaluate_scheme(
        x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS
    )
    section_pass, section = evaluate_scheme(
        x,
        y,
        measures,
        feature_names,
        "section",
        lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS),
    )
    shifted_pass, shifted = evaluate_scheme(
        x,
        y,
        measures,
        feature_names,
        "shiftedWindow",
        lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS),
    )

    all_rows = normal + section + shifted
    total_passes = sum(bool(r["passed"]) for r in all_rows)
    v9_selected = sum(str(r["architectureChosen"]) == "v9" for r in all_rows)
    v5_selected = len(all_rows) - v9_selected
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V10 hybrid nested CV")

    output = {
        "schemaVersion": 10,
        "profileType": "36.76-patch-v5-v9-hybrid-sectionpass-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "hybridSelector": "choose-v9-only-if-inner-section-pass-count-strictly-exceeds-v5",
        "selectorUsesOuterHeldoutLabels": False,
        "selectorUsesProfessionalReferenceHeldoutOutcomes": False,
        "v5Architecture": "pairwise-rank-stratified-v2-section-calibrated-v5",
        "v9Architecture": "class-balanced-pointwise-ridge-v9",
        "v5SelectedFolds": v5_selected,
        "v9SelectedFolds": v9_selected,
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": len(all_rows),
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "hybridV10Generalizes": generalizes,
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
        "schemaVersion": 10,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "hybridSelector": output["hybridSelector"],
        "v5SelectedFolds": v5_selected,
        "v9SelectedFolds": v9_selected,
        "outerFoldsPassed": total_passes,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "hybridV10Generalizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH V5/V9 HYBRID SECTION-PASS NESTED CV V10 COMPLETE")
    print("Outer folds passed:", total_passes, "/", len(all_rows))
    print("V5 selected folds:", v5_selected)
    print("V9 selected folds:", v9_selected)
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Hybrid V10 generalizes:", generalizes)
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Professional reference used to choose hybrid: False")
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
