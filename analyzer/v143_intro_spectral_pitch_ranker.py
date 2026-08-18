from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-analysis-cache.json"
)
SPECTRAL_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-spectral-pitch-cache.json"
)
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-spectral-pitch-ranker-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-spectral-pitch-ranker-model.json"
)

DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))
POSITIVE_CLASS_WEIGHTS = (8.0, 16.0, 32.0, 48.0, 64.0)
L2_VALUES = (0.001, 0.01, 0.05, 0.10)
THRESHOLDS = tuple(round(0.05 + 0.05 * i, 2) for i in range(18))
TOP_K_VALUES = (1, 2, 3)

FEATURE_NAMES = (
    "mean_fund",
    "min_fund",
    "mean_peak",
    "min_peak",
    "mean_harmonic",
    "min_harmonic",
    "view_agreement",
    "lower_octave_mean",
    "upper_octave_mean",
    "fund_minus_lower_octave",
    "fund_minus_upper_octave",
    "harmonic_rank_percentile",
    "fund_rank_percentile",
    "peak_rank_percentile",
    "bp_exact",
    "bp_near1",
    "bp_near2",
    "bp_support_fraction",
    "dominant_exact",
    "v143_rank_percentile",
    "v143_selected",
    "midi_normalized",
)


def _int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def _location(row: dict[str, Any]) -> tuple[int, int]:
    return (
        int(row.get("measure", row.get("measureNumber", 0)) or 0),
        int(row.get("step", 0) or 0),
    )


def _global_step(location: tuple[int, int]) -> int:
    return (int(location[0]) - 1) * 16 + int(location[1])


def _reference_by_location(payload: dict[str, Any]) -> dict[tuple[int, int], set[int]]:
    out: dict[tuple[int, int], set[int]] = {}
    for measure in payload.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if not 1 <= number <= 16:
            continue
        for event in measure.get("events", []) or []:
            if not isinstance(event, dict):
                continue
            midi = _int(event.get("midiPitch"))
            if midi is None:
                continue
            out.setdefault((number, int(event.get("step") or 0)), set()).add(midi)
    return out


def _hypothesis_midis(row: dict[str, Any]) -> set[int]:
    values: set[int] = set()
    for item in row.get("pitchHypotheses", []) or []:
        if not isinstance(item, dict):
            continue
        midi = _int(item.get("midi"))
        if midi is not None:
            values.add(midi)
    return values


def _rank_percentile(row: dict[str, Any], total_rows: int) -> float:
    rank = _int(row.get("v143Rank"))
    if rank is None or total_rows <= 1:
        return 0.5
    return float(np.clip(1.0 - (rank - 1) / float(total_rows - 1), 0.0, 1.0))


def _percent(value: float) -> float:
    return round(100.0 * float(value), 3)


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall <= 0.0 else 2.0 * precision * recall / (precision + recall)


def _percentile_ranks(values: dict[int, float]) -> dict[int, float]:
    ordered = sorted(values.items(), key=lambda item: (item[1], item[0]))
    n = len(ordered)
    if n <= 1:
        return {midi: 1.0 for midi in values}
    return {midi: index / float(n - 1) for index, (midi, _value) in enumerate(ordered)}


def _contexts(
    analysis_rows: list[dict[str, Any]],
    spectral_rows: list[dict[str, Any]],
) -> tuple[dict[tuple[int, int], dict[str, Any]], dict[tuple[int, int], dict[str, Any]]]:
    analysis = {_location(row): row for row in analysis_rows}
    spectral = {_location(row): row for row in spectral_rows}
    if set(analysis) != set(spectral):
        missing_spectral = sorted(set(analysis) - set(spectral))[:8]
        missing_analysis = sorted(set(spectral) - set(analysis))[:8]
        raise RuntimeError(
            "Analysis/spectral cache location mismatch: "
            f"missingSpectral={missing_spectral} missingAnalysis={missing_analysis}"
        )
    return analysis, spectral


def _feature_rows_for_location(
    location: tuple[int, int],
    analysis_by_loc: dict[tuple[int, int], dict[str, Any]],
    spectral_by_loc: dict[tuple[int, int], dict[str, Any]],
) -> dict[int, np.ndarray]:
    analysis = analysis_by_loc[location]
    spectral = spectral_by_loc[location]
    midi_features = spectral.get("midiFeatures") or {}
    if not midi_features:
        raise RuntimeError(f"No spectral MIDI features at {location}")

    mean_harmonic = {int(midi): _float(features.get("meanHarmonic")) for midi, features in midi_features.items()}
    mean_fund = {int(midi): _float(features.get("meanFund")) for midi, features in midi_features.items()}
    mean_peak = {int(midi): _float(features.get("meanPeak")) for midi, features in midi_features.items()}
    harmonic_ranks = _percentile_ranks(mean_harmonic)
    fund_ranks = _percentile_ranks(mean_fund)
    peak_ranks = _percentile_ranks(mean_peak)

    exact_bp = _hypothesis_midis(analysis)
    center_global = _global_step(location)
    all_locations = set(analysis_by_loc)

    def near_bp(midi: int, radius: int) -> tuple[bool, int]:
        support = 0
        found = False
        for delta in range(-radius, radius + 1):
            global_step = center_global + delta
            measure = global_step // 16 + 1
            step = global_step % 16
            neighbor = analysis_by_loc.get((measure, step))
            if neighbor is None:
                continue
            if midi in _hypothesis_midis(neighbor):
                found = True
                support += 1
        return found, support

    total_rows = len(analysis_by_loc)
    dominant = _int(analysis.get("dominantMidi"))
    output: dict[int, np.ndarray] = {}
    midi_keys = sorted(int(midi) for midi in midi_features)
    midi_min = min(midi_keys)
    midi_max = max(midi_keys)
    midi_span = max(1, midi_max - midi_min)

    for midi in midi_keys:
        f = midi_features[str(midi)]
        near1, support1 = near_bp(midi, 1)
        near2, support2 = near_bp(midi, 2)
        output[midi] = np.asarray(
            [
                _float(f.get("meanFund")),
                _float(f.get("minFund")),
                _float(f.get("meanPeak")),
                _float(f.get("minPeak")),
                _float(f.get("meanHarmonic")),
                _float(f.get("minHarmonic")),
                _float(f.get("viewAgreement")),
                _float(f.get("lowerOctaveMean")),
                _float(f.get("upperOctaveMean")),
                _float(f.get("meanFund")) - _float(f.get("lowerOctaveMean")),
                _float(f.get("meanFund")) - _float(f.get("upperOctaveMean")),
                harmonic_ranks[midi],
                fund_ranks[midi],
                peak_ranks[midi],
                1.0 if midi in exact_bp else 0.0,
                1.0 if near1 else 0.0,
                1.0 if near2 else 0.0,
                float(support2) / 5.0,
                1.0 if dominant == midi else 0.0,
                _rank_percentile(analysis, total_rows),
                1.0 if analysis.get("v143Selected") is True else 0.0,
                (midi - midi_min) / float(midi_span),
            ],
            dtype=np.float64,
        )
    return output


def _dataset(
    analysis_by_loc: dict[tuple[int, int], dict[str, Any]],
    spectral_by_loc: dict[tuple[int, int], dict[str, Any]],
    reference_by_loc: dict[tuple[int, int], set[int]],
    measures: set[int],
) -> tuple[np.ndarray, np.ndarray, list[tuple[tuple[int, int], int]]]:
    x: list[np.ndarray] = []
    y: list[float] = []
    keys: list[tuple[tuple[int, int], int]] = []
    for location in sorted(analysis_by_loc):
        if location[0] not in measures:
            continue
        expected = reference_by_loc.get(location, set())
        feature_rows = _feature_rows_for_location(location, analysis_by_loc, spectral_by_loc)
        for midi, features in feature_rows.items():
            x.append(features)
            y.append(1.0 if midi in expected else 0.0)
            keys.append((location, midi))
    if not x:
        raise RuntimeError("No spectral pitch-ranking examples built")
    return np.vstack(x), np.asarray(y, dtype=np.float64), keys


def _sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-z))


def _fit_logistic(
    x: np.ndarray,
    y: np.ndarray,
    *,
    positive_weight: float,
    l2: float,
    epochs: int = 1200,
    learning_rate: float = 0.06,
) -> dict[str, Any]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale = np.where(scale < 1e-8, 1.0, scale)
    xn = (x - mean) / scale
    weights = np.zeros(xn.shape[1], dtype=np.float64)
    bias = 0.0
    sample_weight = np.where(y > 0.5, float(positive_weight), 1.0)
    denom = float(np.sum(sample_weight))
    for epoch in range(epochs):
        probabilities = _sigmoid(xn @ weights + bias)
        error = (probabilities - y) * sample_weight
        gradient = (xn.T @ error) / denom + float(l2) * weights
        bias_gradient = float(np.sum(error) / denom)
        step = learning_rate / math.sqrt(1.0 + epoch / 250.0)
        weights -= step * gradient
        bias -= step * bias_gradient
    return {"mean": mean, "scale": scale, "weights": weights, "bias": float(bias)}


def _predict(model: dict[str, Any], x: np.ndarray) -> np.ndarray:
    xn = (x - model["mean"]) / model["scale"]
    return _sigmoid(xn @ model["weights"] + float(model["bias"]))


def _evaluate(
    probabilities: np.ndarray,
    keys: list[tuple[tuple[int, int], int]],
    reference_by_loc: dict[tuple[int, int], set[int]],
    measures: set[int],
    *,
    threshold: float,
    top_k: int,
) -> dict[str, Any]:
    grouped: dict[tuple[int, int], list[tuple[int, float]]] = {}
    for probability, (location, midi) in zip(probabilities, keys):
        grouped.setdefault(location, []).append((midi, float(probability)))

    predicted: dict[tuple[int, int], set[int]] = {}
    for location, values in grouped.items():
        selected = [item for item in sorted(values, key=lambda item: (-item[1], item[0])) if item[1] >= threshold]
        if selected:
            predicted[location] = {int(midi) for midi, _score in selected[:top_k]}

    reference = {loc: set(midis) for loc, midis in reference_by_loc.items() if loc[0] in measures}
    reference_locations = set(reference)
    predicted_locations = set(predicted)
    location_hits = len(reference_locations & predicted_locations)
    location_precision = location_hits / max(len(predicted_locations), 1)
    location_recall = location_hits / max(len(reference_locations), 1)

    reference_event_count = sum(len(values) for values in reference.values())
    predicted_event_count = sum(len(values) for values in predicted.values())
    pitch_hits = sum(len(predicted.get(location, set()) & expected) for location, expected in reference.items())
    pitch_precision = pitch_hits / max(predicted_event_count, 1)
    pitch_recall = pitch_hits / max(reference_event_count, 1)
    exact_sets = sum(1 for location, expected in reference.items() if predicted.get(location, set()) == expected)

    return {
        "referenceLocationCount": len(reference_locations),
        "predictedLocationCount": len(predicted_locations),
        "locationPrecisionPercent": _percent(location_precision),
        "locationRecallPercent": _percent(location_recall),
        "locationF1Percent": _percent(_f1(location_precision, location_recall)),
        "referencePitchEventCount": reference_event_count,
        "predictedPitchEventCount": predicted_event_count,
        "pitchPrecisionPercent": _percent(pitch_precision),
        "pitchRecallPercent": _percent(pitch_recall),
        "pitchF1Percent": _percent(_f1(pitch_precision, pitch_recall)),
        "exactPitchSetPercent": _percent(exact_sets / max(len(reference), 1)),
    }


def _raw_topk_baseline(
    spectral_by_loc: dict[tuple[int, int], dict[str, Any]],
    reference_by_loc: dict[tuple[int, int], set[int]],
    measures: set[int],
    feature_name: str,
    top_k: int,
) -> dict[str, float]:
    hits = 0
    predicted_count = 0
    reference_count = 0
    for location, expected in reference_by_loc.items():
        if location[0] not in measures:
            continue
        reference_count += len(expected)
        row = spectral_by_loc.get(location)
        if row is None:
            continue
        values = [
            (int(midi), _float(features.get(feature_name)))
            for midi, features in (row.get("midiFeatures") or {}).items()
        ]
        selected = {midi for midi, _score in sorted(values, key=lambda item: (-item[1], item[0]))[:top_k]}
        predicted_count += len(selected)
        hits += len(selected & expected)
    precision = hits / max(predicted_count, 1)
    recall = hits / max(reference_count, 1)
    return {
        "precisionPercent": _percent(precision),
        "recallPercent": _percent(recall),
        "f1Percent": _percent(_f1(precision, recall)),
    }


def main() -> None:
    for path in (ANALYSIS_CACHE_PATH, SPECTRAL_CACHE_PATH, REFERENCE_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing required calibration input: {path}")

    analysis_cache = json.loads(ANALYSIS_CACHE_PATH.read_text())
    spectral_cache = json.loads(SPECTRAL_CACHE_PATH.read_text())
    reference_payload = json.loads(REFERENCE_PATH.read_text())
    analysis_rows = [dict(row) for row in analysis_cache.get("analysis", {}).get("introRows", []) or []]
    spectral_rows = [dict(row) for row in spectral_cache.get("rows", []) or []]
    if not analysis_rows or not spectral_rows:
        raise RuntimeError("Calibration cache is empty")

    analysis_by_loc, spectral_by_loc = _contexts(analysis_rows, spectral_rows)
    reference_by_loc = _reference_by_location(reference_payload)

    x_dev, y_dev, keys_dev = _dataset(
        analysis_by_loc, spectral_by_loc, reference_by_loc, DEVELOPMENT_MEASURES
    )
    x_hold, _y_hold, keys_hold = _dataset(
        analysis_by_loc, spectral_by_loc, reference_by_loc, HOLDOUT_MEASURES
    )

    raw_baselines = {
        "development": {},
        "holdout": {},
    }
    for feature in ("meanFund", "meanPeak", "meanHarmonic"):
        for top_k in TOP_K_VALUES:
            key = f"{feature}-top{top_k}"
            raw_baselines["development"][key] = _raw_topk_baseline(
                spectral_by_loc, reference_by_loc, DEVELOPMENT_MEASURES, feature, top_k
            )
            raw_baselines["holdout"][key] = _raw_topk_baseline(
                spectral_by_loc, reference_by_loc, HOLDOUT_MEASURES, feature, top_k
            )

    best: dict[str, Any] | None = None
    trials = 0
    for positive_weight in POSITIVE_CLASS_WEIGHTS:
        for l2 in L2_VALUES:
            model = _fit_logistic(
                x_dev,
                y_dev,
                positive_weight=positive_weight,
                l2=l2,
            )
            p_dev = _predict(model, x_dev)
            p_hold = _predict(model, x_hold)
            for threshold in THRESHOLDS:
                for top_k in TOP_K_VALUES:
                    trials += 1
                    development = _evaluate(
                        p_dev,
                        keys_dev,
                        reference_by_loc,
                        DEVELOPMENT_MEASURES,
                        threshold=threshold,
                        top_k=top_k,
                    )
                    objective = (
                        0.80 * development["pitchF1Percent"]
                        + 0.10 * development["locationF1Percent"]
                        + 0.10 * development["exactPitchSetPercent"]
                    )
                    candidate = {
                        "configuration": {
                            "positiveClassWeight": positive_weight,
                            "l2": l2,
                            "threshold": threshold,
                            "topK": top_k,
                        },
                        "developmentObjectivePercent": round(objective, 3),
                        "development": development,
                        "holdout": _evaluate(
                            p_hold,
                            keys_hold,
                            reference_by_loc,
                            HOLDOUT_MEASURES,
                            threshold=threshold,
                            top_k=top_k,
                        ),
                        "model": model,
                    }
                    if best is None or (
                        candidate["developmentObjectivePercent"],
                        development["pitchF1Percent"],
                        development["pitchRecallPercent"],
                        -development["predictedPitchEventCount"],
                    ) > (
                        best["developmentObjectivePercent"],
                        best["development"]["pitchF1Percent"],
                        best["development"]["pitchRecallPercent"],
                        -best["development"]["predictedPitchEventCount"],
                    ):
                        best = candidate

    if best is None:
        raise RuntimeError("No spectral pitch-ranker trial completed")

    model = best.pop("model")
    coefficients = sorted(
        zip(FEATURE_NAMES, model["weights"]),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )
    report = {
        "reportVersion": 1,
        "scope": "professional-intro-dual-view-spectral-pitch-ranking",
        "trialCount": trials,
        "rawSpectralBaselines": raw_baselines,
        "bestConfiguration": best["configuration"],
        "developmentObjectivePercent": best["developmentObjectivePercent"],
        "development": best["development"],
        "holdout": best["holdout"],
        "topCoefficients": [
            {"feature": name, "weight": round(float(weight), 6)}
            for name, weight in coefficients[:12]
        ],
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineTraining": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    model_payload = {
        "schemaVersion": 1,
        "status": "development-only-not-promoted",
        "featureNames": list(FEATURE_NAMES),
        "configuration": best["configuration"],
        "mean": [float(value) for value in model["mean"]],
        "scale": [float(value) for value in model["scale"]],
        "weights": [float(value) for value in model["weights"]],
        "bias": float(model["bias"]),
        "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
        "holdoutMeasures": sorted(HOLDOUT_MEASURES),
        "professionalReferenceUsedForTraining": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionPromotionAllowed": False,
    }
    MODEL_PATH.write_text(json.dumps(model_payload, indent=2) + "\n")

    print("=== V143 DUAL-VIEW SPECTRAL PITCH RANKER ===")
    print("analysisRows:", len(analysis_rows))
    print("spectralRows:", len(spectral_rows))
    print("trainingPositiveExamples:", int(np.sum(y_dev)))
    print("trialCount:", trials)
    print()
    print("RAW SPECTRAL HOLDOUT BASELINES:")
    print(json.dumps(raw_baselines["holdout"], indent=2))
    print()
    print("BEST DEVELOPMENT CONFIGURATION:")
    print(json.dumps(report["bestConfiguration"], indent=2))
    print()
    print("DEVELOPMENT:")
    print(json.dumps(report["development"], indent=2))
    print()
    print("HOLDOUT (measures 13-16, never used to fit or choose configuration):")
    print(json.dumps(report["holdout"], indent=2))
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
