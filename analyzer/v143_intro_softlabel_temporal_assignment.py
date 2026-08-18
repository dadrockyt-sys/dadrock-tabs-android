from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from v143_intro_supervised_temporal_assignment import (
    REPO_ROOT,
    CACHE_PATH,
    REFERENCE_PATH,
    DEVELOPMENT_MEASURES,
    HOLDOUT_MEASURES,
    RADIUS,
    POSITIVE_WEIGHTS,
    L2_VALUES,
    THRESHOLDS,
    MAX_POLYPHONY_VALUES,
    FEATURE_NAMES,
    _candidate_atoms,
    _atoms_by_measure_step,
    _pair_features,
    _reference_events,
    _reference_sets,
    _teacher_matching,
    _downsample_training,
    _fit_logistic,
    _predict,
    _decode,
    _grade,
)

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-softlabel-temporal-assignment-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-softlabel-temporal-assignment-model.json"
)


def _build_soft_pairs(
    atoms: list[dict[str, Any]],
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    measures: set[int],
    reference_sets: dict[tuple[int, int], set[int]] | None,
) -> tuple[np.ndarray, np.ndarray, list[tuple[int, int, int, int]]]:
    features: list[np.ndarray] = []
    labels: list[float] = []
    keys: list[tuple[int, int, int, int]] = []

    for atom in atoms:
        measure = int(atom["measure"])
        if measure not in measures:
            continue
        source_step = int(atom["sourceStep"])
        midi = int(atom["midi"])
        for delta in range(-RADIUS, RADIUS + 1):
            target_step = source_step + delta
            if not 0 <= target_step < 16:
                continue
            features.append(_pair_features(atom, target_step, indexed))
            positive = (
                reference_sets is not None
                and midi in reference_sets.get((measure, target_step), set())
            )
            labels.append(1.0 if positive else 0.0)
            keys.append((int(atom["atomId"]), measure, target_step, midi))

    if not features:
        raise RuntimeError("No temporal candidate pairs were built")
    return np.vstack(features), np.asarray(labels, dtype=np.float64), keys


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Missing analysis cache: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())
    atoms = _candidate_atoms(cache)
    indexed = _atoms_by_measure_step(atoms)

    dev_reference = _reference_sets(reference, DEVELOPMENT_MEASURES)
    hold_reference = _reference_sets(reference, HOLDOUT_MEASURES)
    dev_refs = _reference_events(reference, DEVELOPMENT_MEASURES)
    hold_refs = _reference_events(reference, HOLDOUT_MEASURES)
    _dev_teacher, dev_oracle_matches = _teacher_matching(dev_refs, atoms, RADIUS)
    _hold_teacher, hold_oracle_matches = _teacher_matching(hold_refs, atoms, RADIUS)

    x_dev_all, y_dev_all, keys_dev = _build_soft_pairs(
        atoms, indexed, DEVELOPMENT_MEASURES, dev_reference
    )
    x_hold, _y_hold, keys_hold = _build_soft_pairs(
        atoms, indexed, HOLDOUT_MEASURES, None
    )
    x_dev, y_dev = _downsample_training(x_dev_all, y_dev_all)

    print("=== V143 SOFT-LABEL TEMPORAL ASSIGNMENT ===")
    print("candidatePitchAtomCount:", len(atoms))
    print("developmentOracleMatches:", dev_oracle_matches, "/", len(dev_refs))
    print("holdoutOracleMatches:", hold_oracle_matches, "/", len(hold_refs))
    print("developmentPositivePairsBeforeDownsample:", int(np.sum(y_dev_all)))
    print("trainingPairs:", len(x_dev), "positives:", int(np.sum(y_dev)))
    print("holdoutPairs:", len(x_hold))
    print("Label policy: every acoustically equivalent candidate-target pair matching a development reference pitch is positive")

    best: dict[str, Any] | None = None
    for positive_weight in POSITIVE_WEIGHTS:
        for l2 in L2_VALUES:
            model = _fit_logistic(
                x_dev,
                y_dev,
                positive_weight=positive_weight,
                l2=l2,
                epochs=320,
            )
            p_dev = _predict(model, x_dev_all)
            for threshold in THRESHOLDS:
                for max_polyphony in MAX_POLYPHONY_VALUES:
                    prediction = _decode(
                        p_dev,
                        keys_dev,
                        threshold=threshold,
                        max_polyphony=max_polyphony,
                    )
                    grade = _grade(dev_reference, prediction)
                    objective = (
                        0.82 * grade["pitchF1Percent"]
                        + 0.08 * grade["pitchRecallPercent"]
                        + 0.05 * grade["locationF1Percent"]
                        + 0.05 * grade["exactPitchSetPercent"]
                    )
                    trial = {
                        "positiveClassWeight": positive_weight,
                        "l2": l2,
                        "threshold": threshold,
                        "maxPolyphony": max_polyphony,
                        "developmentObjectivePercent": round(objective, 3),
                        "development": grade,
                    }
                    if best is None or (
                        trial["developmentObjectivePercent"],
                        grade["pitchF1Percent"],
                        grade["pitchRecallPercent"],
                        -grade["predictedPitchEventCount"],
                    ) > (
                        best["trial"]["developmentObjectivePercent"],
                        best["trial"]["development"]["pitchF1Percent"],
                        best["trial"]["development"]["pitchRecallPercent"],
                        -best["trial"]["development"]["predictedPitchEventCount"],
                    ):
                        best = {"trial": trial, "model": model}

    if best is None:
        raise RuntimeError("No soft-label temporal assignment trial completed")

    trial = best["trial"]
    model = best["model"]
    p_hold = _predict(model, x_hold)
    hold_prediction = _decode(
        p_hold,
        keys_hold,
        threshold=float(trial["threshold"]),
        max_polyphony=int(trial["maxPolyphony"]),
    )
    hold_grade = _grade(hold_reference, hold_prediction)

    coefficients = sorted(
        zip(FEATURE_NAMES, model["weights"]),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )
    config = {k: v for k, v in trial.items() if k != "development"}
    report = {
        "reportVersion": 1,
        "scope": "soft-label-supervised-temporal-candidate-reassignment",
        "radiusSteps": RADIUS,
        "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
        "holdoutMeasures": sorted(HOLDOUT_MEASURES),
        "developmentOracleRecallPercent": round(100.0 * dev_oracle_matches / max(len(dev_refs), 1), 3),
        "holdoutOracleRecallPercent": round(100.0 * hold_oracle_matches / max(len(hold_refs), 1), 3),
        "developmentPositivePairsBeforeDownsample": int(np.sum(y_dev_all)),
        "bestConfiguration": config,
        "development": trial["development"],
        "holdout": hold_grade,
        "topCoefficients": [
            {"feature": name, "weight": round(float(weight), 6)}
            for name, weight in coefficients[:12]
        ],
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineTemporalTraining": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "status": "development-only-not-promoted",
                "featureNames": list(FEATURE_NAMES),
                "radiusSteps": RADIUS,
                "threshold": float(trial["threshold"]),
                "maxPolyphony": int(trial["maxPolyphony"]),
                "mean": [float(v) for v in model["mean"]],
                "scale": [float(v) for v in model["scale"]],
                "weights": [float(v) for v in model["weights"]],
                "bias": float(model["bias"]),
                "professionalReferenceUsedForTraining": True,
                "professionalReferenceRequiredAtRuntime": False,
                "productionPromotionAllowed": False,
            },
            indent=2,
        )
        + "\n"
    )

    print()
    print("BEST DEVELOPMENT CONFIGURATION:")
    print(json.dumps(config, indent=2))
    print()
    print("DEVELOPMENT (measures 1-12):")
    print(json.dumps(trial["development"], indent=2))
    print()
    print("HOLDOUT (measures 13-16, never used to fit or choose configuration):")
    print(json.dumps(hold_grade, indent=2))
    print()
    print("TOP MODEL COEFFICIENTS:")
    print(json.dumps(report["topCoefficients"], indent=2))
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Model:", MODEL_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
