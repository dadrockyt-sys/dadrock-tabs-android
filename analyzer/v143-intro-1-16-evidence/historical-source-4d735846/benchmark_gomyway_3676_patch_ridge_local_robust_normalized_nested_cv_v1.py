from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_ridge_recurrent_feature_gate_nested_cv_v1 as recurrent
import profile_gomyway_3676_patch_local_context_distribution_shift_v1 as shift

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-ridge-local-robust-normalized-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-ridge-local-robust-normalized-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 3
RADII = [2, 4, 8]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contiguous_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + width / 2.0) % span
    return min(folds - 1, int(pos / width))


def inner_masks(measures: np.ndarray) -> list[tuple[str, np.ndarray, np.ndarray]]:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % INNER_FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS)),
        ("shifted", lambda m: shifted_fold(m, lo, hi, INNER_FOLDS)),
    ]
    out: list[tuple[str, np.ndarray, np.ndarray]] = []
    for name, fold_fn in schemes:
        ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
        for fold in range(INNER_FOLDS):
            test = ids == fold
            train = ~test
            if np.any(train) and np.any(test):
                out.append((f"{name}:{fold}", train, test))
    return out


def choose_radius_label_free(x: np.ndarray, measures: np.ndarray) -> dict[str, Any]:
    splits = inner_masks(measures)
    candidates: list[dict[str, Any]] = []
    for radius in RADII:
        print(f"    heartbeat radius-shift evaluation R{radius}", flush=True)
        xx = shift.robust_local_normalize(x, measures, radius)
        medians: list[float] = []
        p90s: list[float] = []
        for _, train_mask, test_mask in splits:
            stats = shift.shift_stats(xx[train_mask], xx[test_mask])
            medians.append(float(stats["medianAbsSmd"]))
            p90s.append(float(stats["p90AbsSmd"]))
        candidates.append(
            {
                "radius": radius,
                "innerSplitCount": len(splits),
                "meanMedianAbsSmd": round(float(np.mean(medians)), 6),
                "meanP90AbsSmd": round(float(np.mean(p90s)), 6),
            }
        )
    chosen = min(
        candidates,
        key=lambda row: (
            float(row["meanMedianAbsSmd"]),
            float(row["meanP90AbsSmd"]),
            int(row["radius"]),
        ),
    )
    return {"chosen": chosen, "candidates": candidates}


def evaluate_scheme(
    x_raw: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    feature_names: list[str],
    name: str,
    fold_fn: Callable[[int], int],
) -> tuple[bool, list[dict[str, Any]]]:
    ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
    rows: list[dict[str, Any]] = []
    pass_count = 0

    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test_mask = ids == fold
        train_mask = ~test_mask

        # Radius is selected using OUTER-TRAIN covariates only, without labels.
        radius_choice = choose_radius_label_free(x_raw[train_mask], measures[train_mask])
        radius = int(radius_choice["chosen"]["radius"])
        print(
            f"    chosen local robust radius R{radius} "
            f"medianShift={radius_choice['chosen']['meanMedianAbsSmd']} "
            f"p90Shift={radius_choice['chosen']['meanP90AbsSmd']}",
            flush=True,
        )

        # Apply the frozen label-free normalization rule to the full inference context.
        # It uses only patch covariates + measure proximity, never grading labels.
        x_norm_full = shift.robust_local_normalize(x_raw, measures, radius)
        x_train = x_norm_full[train_mask]
        x_test = x_norm_full[test_mask]
        y_train = y[train_mask]
        y_test = y[test_mask]
        m_train = measures[train_mask]

        chosen = recurrent.choose_outer_train_model(
            x_train,
            y_train,
            m_train,
            feature_names,
        )
        final_gate = recurrent.recurrent_gate(
            x_train,
            y_train,
            m_train,
            feature_names,
            float(chosen["gateLambda"]),
            int(chosen["support"]),
        )
        indices = list(final_gate["indices"])
        lam = float(chosen["lambda"])
        q = float(chosen["tailQuantile"])

        model = recurrent.ridge.fit_ridge(x_train[:, indices], y_train, lam)
        train_scores = recurrent.ridge.scores_for(x_train[:, indices], model)
        threshold = (
            float(np.quantile(train_scores, 1.0 - q))
            if train_scores.size
            else float("inf")
        )
        held = recurrent.apply_scores(
            recurrent.ridge.scores_for(x_test[:, indices], model),
            y_test,
            threshold,
        )
        base = recurrent.base_stats(y_test)
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        pass_count += int(passed)

        local_names = [feature_names[j] for j in indices]
        weights = recurrent.ridge.top_weights(
            local_names, model[0], n=min(8, len(local_names))
        )
        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train_mask)),
            "testRows": int(np.sum(test_mask)),
            "normalization": {
                "type": "localRobust",
                "radius": radius,
                "radiusSelection": radius_choice,
                "labelsUsedForRadiusSelection": False,
            },
            "chosen": chosen,
            "featureGate": final_gate["features"],
            "lambda": lam,
            "tailQuantile": q,
            "threshold": threshold,
            "topWeights": weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": passed,
        }
        rows.append(row)
        print(
            f"  R{radius} gateLambda={chosen['gateLambda']} support={chosen['support']} "
            f"features={len(indices)} lambda={lam} q={q} "
            f"held={held['true']}/{held['false']} precision={held['precision']} "
            f"base={base['precision']} lift={round(lift, 2)} pass={passed}",
            flush=True,
        )

    return pass_count == OUTER_FOLDS, rows


def main() -> None:
    candidate_path = recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing; run patch stability profiler first")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")

    feature_names = sorted((rows[0].get("features") or {}).keys())
    x_raw = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in rows],
        dtype=np.float64,
    )
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting strict local-robust normalized recurrent patch ridge nested CV V1", flush=True)
    print("Patch features:", len(feature_names), flush=True)
    print("Radius candidates:", RADII, flush=True)
    print("Radius selection uses labels: False", flush=True)

    normal_pass, normal = evaluate_scheme(
        x_raw, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS
    )
    section_pass, section = evaluate_scheme(
        x_raw,
        y,
        measures,
        feature_names,
        "section",
        lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS),
    )
    shifted_pass, shifted = evaluate_scheme(
        x_raw,
        y,
        measures,
        feature_names,
        "shiftedWindow",
        lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS),
    )
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during normalized patch ridge CV")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-ridge-local-robust-normalized-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "featureCount": len(feature_names),
        "radiusCandidates": RADII,
        "radiusSelectionUsesLabels": False,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "localRobustNormalizedPatchRidgeGeneralizes": generalizes,
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
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "localRobustNormalizedPatchRidgeGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH RIDGE LOCAL ROBUST NORMALIZED NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Local-robust normalized patch ridge generalizes:", generalizes)
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
