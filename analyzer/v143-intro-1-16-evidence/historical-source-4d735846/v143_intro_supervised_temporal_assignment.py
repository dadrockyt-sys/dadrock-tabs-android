from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-analysis-cache.json"
)
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-supervised-temporal-assignment-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-supervised-temporal-assignment-model.json"
)

DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))
STEPS_PER_MEASURE = 16
RADIUS = 2
POSITIVE_WEIGHTS = (4.0, 8.0, 12.0, 16.0)
L2_VALUES = (0.001, 0.01, 0.05)
THRESHOLDS = tuple(round(0.10 + 0.05 * i, 2) for i in range(15))
MAX_POLYPHONY_VALUES = (1, 2, 3)
NEGATIVE_MULTIPLIER = 40

FEATURE_NAMES = (
    "source_count",
    "event_count",
    "max_amplitude",
    "mean_amplitude",
    "grid_accuracy",
    "duration",
    "v143_rank_percentile",
    "v143_selected",
    "row_candidate_count",
    "atom_relative_quality",
    "delta_minus2",
    "delta_minus1",
    "delta_zero",
    "delta_plus1",
    "delta_plus2",
    "abs_delta",
    "source_step_sin",
    "source_step_cos",
    "target_step_sin",
    "target_step_cos",
    "midi_norm",
    "pitch_class_sin",
    "pitch_class_cos",
    "recurrence_exact",
    "recurrence_tol1",
    "recurrence_tol2",
    "source_recurrence_exact",
    "target_competition",
    "source_competition",
)


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _pct(value: float) -> float:
    return round(100.0 * value, 3)


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall <= 0.0 else 2.0 * precision * recall / (precision + recall)


def _reference_events(payload: dict[str, Any], measures: set[int]) -> list[dict[str, int]]:
    events: list[dict[str, int]] = []
    for measure in payload.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if number not in measures:
            continue
        for raw in measure.get("events", []) or []:
            if not isinstance(raw, dict):
                continue
            midi = _safe_int(raw.get("midiPitch"))
            if midi is None:
                midi = _safe_int(raw.get("soundingMidiPitch"))
            if midi is None:
                continue
            step = int(raw.get("step") or 0)
            if 0 <= step < STEPS_PER_MEASURE:
                events.append({"measure": number, "step": step, "midi": midi})
    return events


def _reference_sets(payload: dict[str, Any], measures: set[int]) -> dict[tuple[int, int], set[int]]:
    out: dict[tuple[int, int], set[int]] = {}
    for event in _reference_events(payload, measures):
        out.setdefault((event["measure"], event["step"]), set()).add(event["midi"])
    return out


def _rank_percentile(row: dict[str, Any], total_rows: int) -> float:
    rank = _safe_int(row.get("v143Rank"))
    if rank is None or total_rows <= 1:
        return 0.5
    return float(np.clip(1.0 - (rank - 1) / float(total_rows - 1), 0.0, 1.0))


def _candidate_atoms(cache: dict[str, Any]) -> list[dict[str, Any]]:
    analysis = cache.get("analysis", {}) or {}
    rows = analysis.get("introCandidates", []) or analysis.get("introRows", []) or []
    total_rows = len(rows)
    atoms: list[dict[str, Any]] = []
    atom_id = 0
    for row_index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        measure = int(row.get("measure") or 0)
        step = int(row.get("step") or 0)
        if not 1 <= measure <= 16 or not 0 <= step < STEPS_PER_MEASURE:
            continue
        hypotheses = [h for h in (row.get("pitchHypotheses", []) or []) if isinstance(h, dict)]
        dominant = _safe_int(row.get("dominantMidi"))
        if dominant is not None and all(_safe_int(h.get("midi")) != dominant for h in hypotheses):
            hypotheses.append({"midi": dominant})

        grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for hypothesis in hypotheses:
            midi = _safe_int(hypothesis.get("midi"))
            if midi is not None:
                grouped[midi].append(hypothesis)

        row_qualities: list[float] = []
        temporary: list[dict[str, Any]] = []
        for midi, values in grouped.items():
            source_count = max((_safe_float(v.get("sourceCount")) for v in values), default=0.0)
            event_count = max((_safe_float(v.get("eventCount")) for v in values), default=0.0)
            max_amplitude = max((_safe_float(v.get("maxAmplitude")) for v in values), default=0.0)
            mean_amplitude = max((_safe_float(v.get("meanAmplitude")) for v in values), default=0.0)
            min_grid_error = min((_safe_float(v.get("minGridError"), 0.10) for v in values), default=0.10)
            max_duration = max((_safe_float(v.get("maxDuration")) for v in values), default=0.0)
            quality = (
                min(source_count / 2.0, 1.0)
                + min(event_count / 4.0, 1.0)
                + float(np.clip(max_amplitude, 0.0, 1.0))
                + float(np.clip(1.0 - min_grid_error / 0.10, 0.0, 1.0))
                + float(np.clip(max_duration / 0.75, 0.0, 1.0))
            ) / 5.0
            row_qualities.append(quality)
            temporary.append(
                {
                    "midi": int(midi),
                    "sourceCount": source_count,
                    "eventCount": event_count,
                    "maxAmplitude": max_amplitude,
                    "meanAmplitude": mean_amplitude,
                    "minGridError": min_grid_error,
                    "maxDuration": max_duration,
                    "quality": quality,
                }
            )

        best_quality = max(row_qualities, default=1.0)
        for item in temporary:
            atom_id += 1
            atoms.append(
                {
                    "atomId": atom_id,
                    "rowIndex": row_index,
                    "measure": measure,
                    "sourceStep": step,
                    "midi": item["midi"],
                    "sourceCount": item["sourceCount"],
                    "eventCount": item["eventCount"],
                    "maxAmplitude": item["maxAmplitude"],
                    "meanAmplitude": item["meanAmplitude"],
                    "minGridError": item["minGridError"],
                    "maxDuration": item["maxDuration"],
                    "quality": item["quality"],
                    "relativeQuality": item["quality"] / max(best_quality, 1e-9),
                    "rowCandidateCount": len(temporary),
                    "v143RankPercentile": _rank_percentile(row, total_rows),
                    "v143Selected": 1.0 if row.get("v143Selected") is True else 0.0,
                }
            )
    return atoms


def _atoms_by_measure_step(atoms: list[dict[str, Any]]) -> dict[int, dict[int, list[dict[str, Any]]]]:
    out: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for atom in atoms:
        out[int(atom["measure"])][int(atom["sourceStep"])].append(atom)
    return out


def _teacher_matching(
    refs: list[dict[str, int]], atoms: list[dict[str, Any]], radius: int
) -> tuple[dict[int, int], int]:
    atom_indices_by_measure_midi: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, atom in enumerate(atoms):
        atom_indices_by_measure_midi[(int(atom["measure"]), int(atom["midi"]))].append(index)

    adjacency: list[list[int]] = []
    for ref in refs:
        options = [
            index
            for index in atom_indices_by_measure_midi.get((ref["measure"], ref["midi"]), [])
            if abs(int(atoms[index]["sourceStep"]) - ref["step"]) <= radius
        ]
        options.sort(
            key=lambda index: (
                abs(int(atoms[index]["sourceStep"]) - ref["step"]),
                -float(atoms[index]["quality"]),
                index,
            )
        )
        adjacency.append(options)

    atom_to_ref: dict[int, int] = {}

    def augment(ref_index: int, visited: set[int]) -> bool:
        for atom_index in adjacency[ref_index]:
            if atom_index in visited:
                continue
            visited.add(atom_index)
            previous = atom_to_ref.get(atom_index)
            if previous is None or augment(previous, visited):
                atom_to_ref[atom_index] = ref_index
                return True
        return False

    order = sorted(range(len(refs)), key=lambda idx: (len(adjacency[idx]), refs[idx]["measure"], refs[idx]["step"], refs[idx]["midi"]))
    matches = 0
    for ref_index in order:
        if augment(ref_index, set()):
            matches += 1

    labels: dict[int, int] = {}
    for atom_index, ref_index in atom_to_ref.items():
        atom = atoms[atom_index]
        ref = refs[ref_index]
        labels[int(atom["atomId"])] = int(ref["step"])
    return labels, matches


def _has_midi_near(
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    measure: int,
    target_step: int,
    midi: int,
    tolerance: int,
) -> bool:
    for delta in range(-tolerance, tolerance + 1):
        step = target_step + delta
        if 0 <= step < STEPS_PER_MEASURE and any(
            int(atom["midi"]) == midi for atom in indexed.get(measure, {}).get(step, [])
        ):
            return True
    return False


def _recurrence(
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    target_measure: int,
    target_step: int,
    midi: int,
    tolerance: int,
) -> float:
    comparison_measures = [m for m in range(1, 17) if m != target_measure]
    hits = sum(
        1
        for measure in comparison_measures
        if _has_midi_near(indexed, measure, target_step, midi, tolerance)
    )
    return hits / max(len(comparison_measures), 1)


def _competition(
    indexed: dict[int, dict[int, list[dict[str, Any]]]], measure: int, step: int
) -> float:
    midis = {int(atom["midi"]) for atom in indexed.get(measure, {}).get(step, [])}
    return float(np.clip(len(midis) / 24.0, 0.0, 1.0))


def _pair_features(
    atom: dict[str, Any], target_step: int, indexed: dict[int, dict[int, list[dict[str, Any]]]]
) -> np.ndarray:
    source_step = int(atom["sourceStep"])
    delta = target_step - source_step
    if abs(delta) > RADIUS:
        raise ValueError("pair outside temporal radius")
    phase = 2.0 * math.pi / STEPS_PER_MEASURE
    pitch_phase = 2.0 * math.pi * (int(atom["midi"]) % 12) / 12.0
    one_hot = [1.0 if delta == d else 0.0 for d in (-2, -1, 0, 1, 2)]
    measure = int(atom["measure"])
    midi = int(atom["midi"])
    return np.asarray(
        [
            min(float(atom["sourceCount"]) / 2.0, 1.0),
            min(float(atom["eventCount"]) / 4.0, 1.0),
            float(np.clip(atom["maxAmplitude"], 0.0, 1.0)),
            float(np.clip(atom["meanAmplitude"], 0.0, 1.0)),
            float(np.clip(1.0 - float(atom["minGridError"]) / 0.10, 0.0, 1.0)),
            float(np.clip(float(atom["maxDuration"]) / 0.75, 0.0, 1.0)),
            float(atom["v143RankPercentile"]),
            float(atom["v143Selected"]),
            float(np.clip(float(atom["rowCandidateCount"]) / 24.0, 0.0, 1.0)),
            float(atom["relativeQuality"]),
            *one_hot,
            abs(delta) / float(RADIUS),
            math.sin(phase * source_step),
            math.cos(phase * source_step),
            math.sin(phase * target_step),
            math.cos(phase * target_step),
            float(np.clip((midi - 40) / 48.0, 0.0, 1.0)),
            math.sin(pitch_phase),
            math.cos(pitch_phase),
            _recurrence(indexed, measure, target_step, midi, 0),
            _recurrence(indexed, measure, target_step, midi, 1),
            _recurrence(indexed, measure, target_step, midi, 2),
            _recurrence(indexed, measure, source_step, midi, 0),
            _competition(indexed, measure, target_step),
            _competition(indexed, measure, source_step),
        ],
        dtype=np.float64,
    )


def _build_pairs(
    atoms: list[dict[str, Any]],
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    measures: set[int],
    teacher_labels: dict[int, int] | None,
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
            if not 0 <= target_step < STEPS_PER_MEASURE:
                continue
            features.append(_pair_features(atom, target_step, indexed))
            positive = teacher_labels is not None and teacher_labels.get(int(atom["atomId"])) == target_step
            labels.append(1.0 if positive else 0.0)
            keys.append((int(atom["atomId"]), measure, target_step, midi))
    return np.vstack(features), np.asarray(labels, dtype=np.float64), keys


def _downsample_training(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    positive_indices = np.flatnonzero(y > 0.5)
    negative_indices = np.flatnonzero(y <= 0.5)
    if len(positive_indices) == 0:
        raise RuntimeError("No positive temporal-assignment examples")
    limit = min(len(negative_indices), len(positive_indices) * NEGATIVE_MULTIPLIER)
    # Deterministic hard-negative preference: retain negatives with the largest
    # source/evidence mass before falling back to their original order.
    hardness = (
        x[negative_indices, 0]
        + x[negative_indices, 1]
        + x[negative_indices, 2]
        + x[negative_indices, 9]
        + x[negative_indices, 24]
        + x[negative_indices, 25]
    )
    order = np.argsort(-hardness, kind="stable")[:limit]
    selected = np.concatenate([positive_indices, negative_indices[order]])
    return x[selected], y[selected]


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def _fit_logistic(
    x: np.ndarray,
    y: np.ndarray,
    *,
    positive_weight: float,
    l2: float,
    epochs: int = 240,
    learning_rate: float = 0.08,
) -> dict[str, Any]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale = np.where(scale < 1e-8, 1.0, scale)
    xn = (x - mean) / scale
    weights = np.zeros(x.shape[1], dtype=np.float64)
    bias = 0.0
    sample_weight = np.where(y > 0.5, positive_weight, 1.0)
    denom = float(np.sum(sample_weight))
    for epoch in range(epochs):
        probability = _sigmoid(xn @ weights + bias)
        error = (probability - y) * sample_weight
        grad = (xn.T @ error) / denom + l2 * weights
        bias_grad = float(np.sum(error) / denom)
        step = learning_rate / math.sqrt(1.0 + epoch / 80.0)
        weights -= step * grad
        bias -= step * bias_grad
    return {"mean": mean, "scale": scale, "weights": weights, "bias": bias}


def _predict(model: dict[str, Any], x: np.ndarray) -> np.ndarray:
    xn = (x - model["mean"]) / model["scale"]
    return _sigmoid(xn @ model["weights"] + float(model["bias"]))


def _decode(
    probabilities: np.ndarray,
    keys: list[tuple[int, int, int, int]],
    *,
    threshold: float,
    max_polyphony: int,
) -> dict[tuple[int, int], set[int]]:
    candidates = sorted(
        [
            (float(probability), atom_id, measure, target_step, midi)
            for probability, (atom_id, measure, target_step, midi) in zip(probabilities, keys)
            if probability >= threshold
        ],
        key=lambda item: (-item[0], item[2], item[3], item[4], item[1]),
    )
    used_atoms: set[int] = set()
    predicted: dict[tuple[int, int], set[int]] = defaultdict(set)
    for _probability, atom_id, measure, target_step, midi in candidates:
        if atom_id in used_atoms:
            continue
        location = (measure, target_step)
        if midi in predicted[location]:
            continue
        if len(predicted[location]) >= max_polyphony:
            continue
        predicted[location].add(midi)
        used_atoms.add(atom_id)
    return dict(predicted)


def _grade(
    reference: dict[tuple[int, int], set[int]], predicted: dict[tuple[int, int], set[int]]
) -> dict[str, Any]:
    ref_locations = set(reference)
    pred_locations = set(predicted)
    location_hits = len(ref_locations & pred_locations)
    lp = location_hits / max(len(pred_locations), 1)
    lr = location_hits / max(len(ref_locations), 1)
    ref_events = sum(len(v) for v in reference.values())
    pred_events = sum(len(v) for v in predicted.values())
    pitch_hits = sum(len(expected & predicted.get(location, set())) for location, expected in reference.items())
    pp = pitch_hits / max(pred_events, 1)
    pr = pitch_hits / max(ref_events, 1)
    exact = sum(1 for location, expected in reference.items() if predicted.get(location, set()) == expected)
    return {
        "referenceLocationCount": len(ref_locations),
        "predictedLocationCount": len(pred_locations),
        "locationPrecisionPercent": _pct(lp),
        "locationRecallPercent": _pct(lr),
        "locationF1Percent": _pct(_f1(lp, lr)),
        "referencePitchEventCount": ref_events,
        "predictedPitchEventCount": pred_events,
        "pitchPrecisionPercent": _pct(pp),
        "pitchRecallPercent": _pct(pr),
        "pitchF1Percent": _pct(_f1(pp, pr)),
        "exactPitchSetPercent": _pct(exact / max(len(ref_locations), 1)),
    }


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Missing analysis cache: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())
    atoms = _candidate_atoms(cache)
    indexed = _atoms_by_measure_step(atoms)

    dev_refs = _reference_events(reference, DEVELOPMENT_MEASURES)
    hold_refs = _reference_events(reference, HOLDOUT_MEASURES)
    dev_teacher, dev_oracle_matches = _teacher_matching(dev_refs, atoms, RADIUS)
    _hold_teacher, hold_oracle_matches = _teacher_matching(hold_refs, atoms, RADIUS)

    x_dev_all, y_dev_all, keys_dev = _build_pairs(atoms, indexed, DEVELOPMENT_MEASURES, dev_teacher)
    x_hold, _y_hold, keys_hold = _build_pairs(atoms, indexed, HOLDOUT_MEASURES, None)
    x_dev, y_dev = _downsample_training(x_dev_all, y_dev_all)

    dev_reference = _reference_sets(reference, DEVELOPMENT_MEASURES)
    hold_reference = _reference_sets(reference, HOLDOUT_MEASURES)

    print("=== V143 SUPERVISED TEMPORAL ASSIGNMENT ===")
    print("candidatePitchAtomCount:", len(atoms))
    print("developmentTeacherMatches:", dev_oracle_matches, "/", len(dev_refs))
    print("holdoutOracleMatches:", hold_oracle_matches, "/", len(hold_refs))
    print("trainingPairs:", len(x_dev), "positives:", int(np.sum(y_dev)))
    print("holdoutPairs:", len(x_hold))

    best: dict[str, Any] | None = None
    fitted: dict[tuple[float, float], dict[str, Any]] = {}
    for positive_weight in POSITIVE_WEIGHTS:
        for l2 in L2_VALUES:
            model = _fit_logistic(x_dev, y_dev, positive_weight=positive_weight, l2=l2)
            fitted[(positive_weight, l2)] = model
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
                        0.80 * grade["pitchF1Percent"]
                        + 0.10 * grade["pitchRecallPercent"]
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
        raise RuntimeError("No supervised temporal assignment trial completed")

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
    config = {k: v for k, v in trial.items() if k not in {"development"}}
    report = {
        "reportVersion": 1,
        "scope": "supervised-temporal-candidate-reassignment",
        "radiusSteps": RADIUS,
        "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
        "holdoutMeasures": sorted(HOLDOUT_MEASURES),
        "developmentOracleRecallPercent": _pct(dev_oracle_matches / max(len(dev_refs), 1)),
        "holdoutOracleRecallPercent": _pct(hold_oracle_matches / max(len(hold_refs), 1)),
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
                "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
                "holdoutMeasures": sorted(HOLDOUT_MEASURES),
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
