from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from v143_intro_raw_attack_temporal_diagnostic import (
    CACHE_PATH as RAW_CACHE_PATH,
    REFERENCE_PATH,
    _grid_lookup,
)
from v143_intro_supervised_temporal_assignment import (
    DEVELOPMENT_MEASURES,
    HOLDOUT_MEASURES,
    REPO_ROOT,
    _reference_sets,
)


SPECTRUM_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-onset-spectrum-cache.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-joint-sparse-pitchset-diagnostic.json"
)

WINDOWS_MS = (50, 75, 100, 125, 150, 200)
MIXES = {
    "attack": (1.00, 0.00, 0.00),
    "attackEarly": (0.45, 0.55, 0.00),
    "allWindows": (0.25, 0.50, 0.25),
}
VIEW_MODES = ("mean", "min")
POOL_MODES = ("raw", "lower12", "lower12_19")
SECOND_GAIN_RATIOS = (0.15, 0.25, 0.40, 0.60)
MAX_POLYPHONY = 3

# Approximate harmonic-series offsets in semitones through the eighth partial.
PARTIAL_OFFSETS = (0, 12, 19, 24, 28, 31, 34, 36)
TEMPLATE_PROFILES = {
    # Useful when the fundamental survives distortion reasonably well.
    "fundamental": (1.35, 0.85, 0.65, 0.50, 0.40, 0.34, 0.29, 0.25),
    # Neutral guitar spectrum.
    "balanced": (1.00, 0.95, 0.78, 0.64, 0.55, 0.48, 0.42, 0.36),
    # Explicitly allows the octave / upper partials to dominate the fundamental.
    "distorted": (0.55, 1.00, 0.92, 0.80, 0.72, 0.64, 0.58, 0.52),
}


def _pct(numerator: float, denominator: float) -> float:
    return round(100.0 * float(numerator) / float(denominator), 3) if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall <= 0.0 else 2.0 * precision * recall / (precision + recall)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _rows_by_measure(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        measure = int(row.get("measure") or 0)
        if 1 <= measure <= 16:
            out.setdefault(measure, []).append(row)
    for values in out.values():
        values.sort(key=lambda row: (float(row.get("onsetTime") or 0.0), int(row.get("onsetGroupId") or 0)))
    return out


def _nearest_group(
    by_measure: dict[int, list[dict[str, Any]]],
    measure: int,
    target_time: float,
    window_ms: int,
) -> dict[str, Any] | None:
    window = float(window_ms) / 1000.0
    candidates = [
        row
        for row in by_measure.get(int(measure), [])
        if abs(float(row.get("onsetTime") or 0.0) - float(target_time)) <= window
    ]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda row: (
            abs(float(row.get("onsetTime") or 0.0) - float(target_time)),
            -int(row.get("stemSupportMax") or 0),
            -int(row.get("sweepSupportMax") or 0),
            -int(row.get("detectionCountSum") or 0),
            int(row.get("onsetGroupId") or 0),
        ),
    )


def _array(row: dict[str, Any], view: str, window: str, expected_len: int) -> np.ndarray:
    values = ((row.get(view) or {}).get(window) or [])
    arr = np.asarray(values, dtype=np.float64)
    if arr.ndim != 1 or arr.size != expected_len:
        raise RuntimeError(
            f"Bad spectrum vector for onsetGroupId={row.get('onsetGroupId')} {view}/{window}: {arr.shape}"
        )
    arr[~np.isfinite(arr)] = 0.0
    return arr


def _observed_vector(
    row: dict[str, Any],
    spectrum_len: int,
    mix_name: str,
    view_mode: str,
) -> np.ndarray:
    weights = MIXES[mix_name]
    names = ("attackMax", "earlyMean", "sustainMean")
    combined = np.zeros(spectrum_len, dtype=np.float64)
    for weight, name in zip(weights, names):
        if weight <= 0.0:
            continue
        a = _array(row, "viewA", name, spectrum_len)
        b = _array(row, "viewB", name, spectrum_len)
        if view_mode == "min":
            view = np.minimum(a, b)
        else:
            view = 0.5 * (a + b)
        combined += float(weight) * view

    # The cache stores log-CQT energy relative to each window's median floor.
    # Positive evidence is converted back toward an amplitude-ratio domain while
    # clipping extreme distortion peaks so one overtone cannot dominate the fit.
    positive = np.maximum(combined, 0.0)
    positive = np.expm1(np.clip(positive, 0.0, 4.0))
    norm = float(np.linalg.norm(positive))
    if norm > 1e-12:
        positive /= norm
    return positive


def _candidate_pool(row: dict[str, Any], mode: str, guitar_min: int, guitar_max: int) -> list[int]:
    pool = {
        int(value)
        for value in (row.get("candidateMidis") or [])
        if guitar_min <= int(value) <= guitar_max
    }
    if mode in {"lower12", "lower12_19"}:
        pool.update(midi - 12 for midi in list(pool) if midi - 12 >= guitar_min)
    if mode == "lower12_19":
        pool.update(midi - 19 for midi in list(pool) if midi - 19 >= guitar_min)
    return sorted(midi for midi in pool if guitar_min <= midi <= guitar_max)


def _template(
    midi: int,
    spectrum_min: int,
    spectrum_max: int,
    profile: str,
) -> np.ndarray:
    length = spectrum_max - spectrum_min + 1
    out = np.zeros(length, dtype=np.float64)
    weights = TEMPLATE_PROFILES[profile]
    for offset, weight in zip(PARTIAL_OFFSETS, weights):
        target = int(midi) + int(offset)
        if not (spectrum_min <= target <= spectrum_max):
            continue
        index = target - spectrum_min
        out[index] += float(weight)
        # Small semitone shoulders tolerate bends, vibrato and CQT leakage without
        # turning the template into a broad chromatic matcher.
        if index - 1 >= 0:
            out[index - 1] += 0.12 * float(weight)
        if index + 1 < length:
            out[index + 1] += 0.12 * float(weight)
    norm = float(np.linalg.norm(out))
    if norm > 1e-12:
        out /= norm
    return out


def _dictionary(
    guitar_min: int,
    guitar_max: int,
    spectrum_min: int,
    spectrum_max: int,
    profile: str,
) -> dict[int, np.ndarray]:
    return {
        midi: _template(midi, spectrum_min, spectrum_max, profile)
        for midi in range(guitar_min, guitar_max + 1)
    }


def _sparse_sequence(
    observed: np.ndarray,
    candidates: list[int],
    templates: dict[int, np.ndarray],
) -> tuple[list[int], list[float]]:
    """Greedy non-negative matching pursuit over candidate fundamentals.

    Returns an ordered pitch sequence plus each pitch's residual-energy reduction.
    The caller decides whether the second/third pitch are strong enough to retain.
    """
    if not candidates or float(np.dot(observed, observed)) <= 1e-12:
        return [], []

    residual = observed.copy()
    selected: list[int] = []
    gains: list[float] = []
    for _ in range(MAX_POLYPHONY):
        remaining = [midi for midi in candidates if midi not in selected]
        if not remaining:
            break
        matrix = np.stack([templates[midi] for midi in remaining], axis=0)
        dots = matrix @ residual
        positive = np.maximum(dots, 0.0)
        # Templates are unit norm, so alpha == dot and SSE reduction == dot^2.
        candidate_gains = positive * positive
        best_index = int(np.argmax(candidate_gains))
        best_gain = float(candidate_gains[best_index])
        if best_gain <= 1e-12:
            break
        midi = int(remaining[best_index])
        alpha = float(positive[best_index])
        selected.append(midi)
        gains.append(best_gain)
        residual = np.maximum(residual - alpha * templates[midi], 0.0)
    return selected, gains


def _retain_sequence(sequence: list[int], gains: list[float], ratio: float) -> set[int]:
    if not sequence:
        return set()
    kept = [sequence[0]]
    first_gain = max(float(gains[0]), 1e-12)
    for midi, gain in zip(sequence[1:], gains[1:]):
        if float(gain) / first_gain >= float(ratio):
            kept.append(int(midi))
        else:
            break
    return set(kept)


def _evaluate(
    by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    decoded: dict[int, tuple[list[int], list[float], set[int]]],
    window_ms: int,
    second_gain_ratio: float,
) -> dict[str, Any]:
    reference_locations = 0
    covered_locations = 0
    exact_sets = 0
    reference_pitch_events = 0
    predicted_pitch_events = 0
    correct_pitch_events = 0
    candidate_available = 0

    for (measure, step), expected in sorted(reference.items()):
        target_time = grid.get((int(measure), int(step)))
        if target_time is None:
            continue
        reference_locations += 1
        reference_pitch_events += len(expected)
        group = _nearest_group(by_measure, int(measure), float(target_time), int(window_ms))
        if group is None:
            continue
        covered_locations += 1
        group_id = int(group.get("onsetGroupId") or 0)
        sequence, gains, pool = decoded.get(group_id, ([], [], set()))
        candidate_available += len(set(expected) & set(pool))
        predicted = _retain_sequence(sequence, gains, float(second_gain_ratio))
        predicted_pitch_events += len(predicted)
        correct_pitch_events += len(predicted & set(expected))
        if predicted == set(expected):
            exact_sets += 1

    precision = correct_pitch_events / predicted_pitch_events if predicted_pitch_events else 0.0
    recall = correct_pitch_events / reference_pitch_events if reference_pitch_events else 0.0
    return {
        "referenceLocationCount": reference_locations,
        "coveredLocationCount": covered_locations,
        "referenceLocationCoveragePercent": _pct(covered_locations, reference_locations),
        "referencePitchEventCount": reference_pitch_events,
        "predictedPitchEventCount": predicted_pitch_events,
        "correctPitchEventCount": correct_pitch_events,
        "candidatePitchAvailabilityRecallPercent": _pct(candidate_available, reference_pitch_events),
        "pitchPrecisionPercent": round(100.0 * precision, 3),
        "pitchRecallPercent": round(100.0 * recall, 3),
        "pitchF1Percent": round(100.0 * _f1(precision, recall), 3),
        "exactPitchSetPercent": _pct(exact_sets, reference_locations),
    }


def main() -> None:
    if not SPECTRUM_CACHE_PATH.exists():
        raise RuntimeError(f"Missing onset spectrum cache: {SPECTRUM_CACHE_PATH}")
    if not RAW_CACHE_PATH.exists():
        raise RuntimeError(f"Missing raw attack cache: {RAW_CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    spectrum_cache = json.loads(SPECTRUM_CACHE_PATH.read_text())
    raw_cache = json.loads(RAW_CACHE_PATH.read_text())
    reference_payload = json.loads(REFERENCE_PATH.read_text())

    rows = [dict(row) for row in (spectrum_cache.get("rows") or []) if isinstance(row, dict)]
    by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(raw_cache)
    development_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    holdout_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    spectrum_min = int(spectrum_cache.get("spectrumMidiMin") or 28)
    spectrum_max = int(spectrum_cache.get("spectrumMidiMax") or 112)
    guitar_min = int(spectrum_cache.get("guitarMidiMin") or 40)
    guitar_max = int(spectrum_cache.get("guitarMidiMax") or 88)
    spectrum_len = spectrum_max - spectrum_min + 1

    print("=== V143 JOINT SPARSE ONSET PITCH-SET DIAGNOSTIC ===")
    print("onsetGroupCount:", len(rows))
    print("Purpose: solve each physical onset jointly as a sparse set of guitar fundamentals")
    print("Development measures: 1-12")
    print("Untouched holdout measures: 13-16")
    print("Professional reference used by analyzer: False")
    print("Production modified: False")

    # Decode every onset group once per spectral configuration. Hyperparameter
    # selection below uses only development measures; holdout is evaluated once.
    decoded_by_config: dict[tuple[str, str, str, str], dict[int, tuple[list[int], list[float], set[int]]]] = {}
    total_spectral_configs = len(MIXES) * len(VIEW_MODES) * len(TEMPLATE_PROFILES) * len(POOL_MODES)
    spectral_index = 0
    for mix_name in MIXES:
        for view_mode in VIEW_MODES:
            for profile in TEMPLATE_PROFILES:
                templates = _dictionary(guitar_min, guitar_max, spectrum_min, spectrum_max, profile)
                for pool_mode in POOL_MODES:
                    spectral_index += 1
                    key = (mix_name, view_mode, profile, pool_mode)
                    decoded: dict[int, tuple[list[int], list[float], set[int]]] = {}
                    for row in rows:
                        group_id = int(row.get("onsetGroupId") or 0)
                        if group_id <= 0:
                            continue
                        observed = _observed_vector(row, spectrum_len, mix_name, view_mode)
                        pool = _candidate_pool(row, pool_mode, guitar_min, guitar_max)
                        sequence, gains = _sparse_sequence(observed, pool, templates)
                        decoded[group_id] = (sequence, gains, set(pool))
                    decoded_by_config[key] = decoded
                    print(
                        f"decoded spectral config {spectral_index}/{total_spectral_configs}: "
                        f"mix={mix_name} view={view_mode} template={profile} pool={pool_mode}"
                    )

    best: dict[str, Any] | None = None
    tested = 0
    for key, decoded in decoded_by_config.items():
        mix_name, view_mode, profile, pool_mode = key
        for window_ms in WINDOWS_MS:
            for ratio in SECOND_GAIN_RATIOS:
                tested += 1
                metrics = _evaluate(
                    by_measure,
                    grid,
                    development_reference,
                    decoded,
                    int(window_ms),
                    float(ratio),
                )
                # Favor actual pitch-set reconstruction, not merely location coverage.
                objective = (
                    0.68 * float(metrics["pitchF1Percent"])
                    + 0.32 * float(metrics["exactPitchSetPercent"])
                )
                row = {
                    "mix": mix_name,
                    "viewMode": view_mode,
                    "templateProfile": profile,
                    "poolMode": pool_mode,
                    "windowMs": int(window_ms),
                    "secondGainRatio": float(ratio),
                    "developmentObjectivePercent": round(objective, 3),
                    "development": metrics,
                }
                if best is None or (
                    row["developmentObjectivePercent"],
                    metrics["pitchF1Percent"],
                    metrics["exactPitchSetPercent"],
                    metrics["candidatePitchAvailabilityRecallPercent"],
                    -int(window_ms),
                ) > (
                    best["developmentObjectivePercent"],
                    best["development"]["pitchF1Percent"],
                    best["development"]["exactPitchSetPercent"],
                    best["development"]["candidatePitchAvailabilityRecallPercent"],
                    -int(best["windowMs"]),
                ):
                    best = row

    if best is None:
        raise RuntimeError("No joint sparse configuration evaluated")

    best_key = (
        str(best["mix"]),
        str(best["viewMode"]),
        str(best["templateProfile"]),
        str(best["poolMode"]),
    )
    holdout = _evaluate(
        by_measure,
        grid,
        holdout_reference,
        decoded_by_config[best_key],
        int(best["windowMs"]),
        float(best["secondGainRatio"]),
    )

    report = {
        "reportVersion": 1,
        "scope": "offline-reference-location-joint-sparse-onset-pitchset-diagnostic",
        "spectralConfigurationCount": total_spectral_configs,
        "developmentConfigurationCount": tested,
        "bestDevelopmentConfiguration": {
            key: value for key, value in best.items() if key != "development"
        },
        "development": best["development"],
        "holdout": holdout,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineDevelopmentSelectionAndGrading": True,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }

    hold_f1 = float(holdout["pitchF1Percent"])
    hold_exact = float(holdout["exactPitchSetPercent"])
    if hold_f1 >= 50.0 and hold_exact >= 35.0:
        diagnosis = "joint-sparse-pitchset-decomposition-is-viable-build-runtime-decoder"
    elif hold_f1 >= 25.0:
        diagnosis = "joint-decomposition-helps-but-needs-learned-spectral-dictionary-or-attack-context"
    else:
        diagnosis = "fixed-harmonic-dictionary-insufficient-use-learned-onset-level-spectral-set-model"
    report["diagnosis"] = diagnosis

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print()
    print("=== BEST DEVELOPMENT CONFIGURATION ===")
    print(json.dumps(report["bestDevelopmentConfiguration"], indent=2))
    print()
    print("=== DEVELOPMENT 1-12 ===")
    print(json.dumps(report["development"], indent=2))
    print()
    print("=== HOLDOUT 13-16 (never used to choose configuration) ===")
    print(json.dumps(report["holdout"], indent=2))
    print()
    print("DIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
