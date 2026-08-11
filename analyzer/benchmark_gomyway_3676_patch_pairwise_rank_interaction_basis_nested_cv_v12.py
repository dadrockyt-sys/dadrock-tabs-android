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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-interaction-basis-nested-cv-v12.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-interaction-basis-nested-cv-v12-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
CLIP_ABS = 1_000_000.0
TOP_FEATURES = 6
MAX_INTERACTIONS = 15


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose_interactions_train_only(
    x_train: np.ndarray,
    y_train: np.ndarray,
    measures_train: np.ndarray,
    feature_names: list[str],
) -> list[tuple[int, int]]:
    """Choose a tiny interaction set using training data only.

    We fit the already-established V5-selected linear pairwise model on the outer
    training split, rank raw features by absolute coefficient, then predeclare all
    pair products among the strongest TOP_FEATURES. No outer held-out values or
    labels participate in interaction selection.
    """
    chosen = v5.choose_model(x_train, y_train, measures_train)
    model = v2.fit_pairwise_ranker(
        x_train,
        y_train,
        measures_train,
        int(chosen["pairRadius"]),
        float(chosen["lambda"]),
    )
    coef = np.asarray(model["coef"], dtype=np.float64)
    top = np.argsort(np.abs(coef))[::-1][: min(TOP_FEATURES, len(feature_names))]
    pairs: list[tuple[int, int]] = []
    for a in range(len(top)):
        for b in range(a + 1, len(top)):
            pairs.append((int(top[a]), int(top[b])))
    return pairs[:MAX_INTERACTIONS]


def interaction_basis(
    x: np.ndarray,
    feature_names: list[str],
    pairs: list[tuple[int, int]],
) -> tuple[np.ndarray, list[str]]:
    raw = np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=CLIP_ABS, neginf=-CLIP_ABS)
    raw = np.clip(raw, -CLIP_ABS, CLIP_ABS)
    if not pairs:
        return raw, list(feature_names)

    cols = [raw]
    names = list(feature_names)
    for i, j in pairs:
        product = raw[:, i] * raw[:, j]
        product = np.nan_to_num(product, nan=0.0, posinf=CLIP_ABS, neginf=-CLIP_ABS)
        product = np.clip(product, -CLIP_ABS, CLIP_ABS)
        cols.append(product[:, None])
        names.append(f"interaction::{feature_names[i]}*{feature_names[j]}")
    return np.concatenate(cols, axis=1), names


def evaluate_scheme(
    x_base: np.ndarray,
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

        print("    heartbeat training-only interaction discovery", flush=True)
        pairs = choose_interactions_train_only(x_base[train], y[train], measures[train], feature_names)
        x, expanded_names = interaction_basis(x_base, feature_names, pairs)

        print("    heartbeat interaction-basis V5 model selection", flush=True)
        chosen = v5.choose_model(x[train], y[train], measures[train])
        model = v2.fit_pairwise_ranker(
            x[train], y[train], measures[train], int(chosen["pairRadius"]), float(chosen["lambda"])
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
            {"feature": expanded_names[int(j)], "weight": round(float(coef[int(j)]), 6)}
            for j in top_idx
        ]
        interaction_names = [f"{feature_names[i]}*{feature_names[j]}" for i, j in pairs]

        rows.append({
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train)),
            "testRows": int(np.sum(test)),
            "representation": "raw-plus-training-only-top6-pair-products",
            "interactionCount": len(pairs),
            "interactions": interaction_names,
            "chosen": chosen,
            "pairCount": int(model["pairCount"]),
            "tailQuantile": q,
            "topWeights": top_weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": bool(passed),
        })

        print(
            f"  interactions={len(pairs)} radius={chosen['pairRadius']} lambda={chosen['lambda']} q={q} "
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

    feature_names = sorted((source_rows[0].get("features") or {}).keys())
    x_base = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in source_rows],
        dtype=np.float64,
    )
    y = np.asarray([str(r.get("label")) == "true" for r in source_rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in source_rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V12 controlled interaction-basis pairwise nested CV", flush=True)
    print(
        f"Representation: {len(feature_names)} raw features + at most {MAX_INTERACTIONS} pair products "
        f"among training-only top {TOP_FEATURES} linear features",
        flush=True,
    )
    print("Outer held-out labels are never used to select interactions", flush=True)

    normal_pass, normal = evaluate_scheme(x_base, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(
        x_base, y, measures, feature_names, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS)
    )
    shifted_pass, shifted = evaluate_scheme(
        x_base, y, measures, feature_names, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS)
    )

    all_rows = normal + section + shifted
    total_passes = sum(bool(r["passed"]) for r in all_rows)
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V12 interaction-basis nested CV")

    output = {
        "schemaVersion": 12,
        "profileType": "36.76-patch-pairwise-rank-controlled-interaction-basis-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "baseFeatureCount": len(feature_names),
        "maxInteractionCount": MAX_INTERACTIONS,
        "interactionTopFeatureCount": TOP_FEATURES,
        "representation": "raw-plus-training-only-top6-pair-products",
        "representationUsesOuterHeldoutLabels": False,
        "modelSelection": "V5-training-only-inner-contiguous-section-priority",
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": len(all_rows),
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "interactionBasisV12Generalizes": generalizes,
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
        "schemaVersion": 12,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "outerFoldsPassed": total_passes,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "interactionBasisV12Generalizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE CONTROLLED INTERACTION BASIS NESTED CV V12 COMPLETE")
    print("Outer folds passed:", total_passes, "/", len(all_rows))
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Interaction-basis V12 generalizes:", generalizes)
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
