from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import profile_gomyway_3676_onset_slot_spectro_temporal_patch_stability_v1 as historical_patch
import profile_gomyway_3676_patch_rhythm24_v111_lowband_phase_interaction_augmentation_v112 as v112
from v143_production_engine import V143ProductionEngine
import v143_rhythm_runtime as runtime


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = (
    ROOT
    / "public"
    / "training"
    / "v143-final-multifamily-development"
    / "v143-production-model-candidate-v1.json"
)


def synthetic_stem(sr: int, seconds: float, variant: int) -> np.ndarray:
    n = int(round(sr * seconds))
    t = np.arange(n, dtype=np.float64) / float(sr)

    # Deterministic multi-band material with transient bursts. This deliberately
    # exercises all five frozen V143 carrier bands and several patch offsets.
    x = (
        0.20 * np.sin(2.0 * np.pi * (110.0 + 7.0 * variant) * t)
        + 0.16 * np.sin(2.0 * np.pi * (330.0 + 11.0 * variant) * t)
        + 0.12 * np.sin(2.0 * np.pi * (780.0 + 13.0 * variant) * t)
        + 0.09 * np.sin(2.0 * np.pi * (1700.0 + 17.0 * variant) * t)
        + 0.06 * np.sin(2.0 * np.pi * (3100.0 + 19.0 * variant) * t)
    )

    for center in (0.50, 0.75, 1.00, 1.25, 1.50, 1.75):
        dt = t - (center + 0.0015 * variant)
        burst = np.exp(-np.square(dt / 0.014))
        x += (0.23 + 0.015 * variant) * burst * np.sin(
            2.0 * np.pi * (620.0 + 80.0 * variant) * t
        )

    return np.asarray(x, dtype=np.float64)


def assert_dict_exact(
    actual: dict[str, float],
    expected: dict[str, float],
    label: str,
) -> None:
    if tuple(sorted(actual)) != tuple(sorted(expected)):
        raise RuntimeError(f"{label} key schema mismatch")

    names = sorted(actual)
    a = np.asarray([actual[name] for name in names], dtype=np.float64)
    b = np.asarray([expected[name] for name in names], dtype=np.float64)

    if not np.array_equal(a, b):
        delta = np.abs(a - b)
        i = int(np.argmax(delta))
        raise RuntimeError(
            f"{label} numeric mismatch at {names[i]}: "
            f"runtime={a[i]!r} historical={b[i]!r} "
            f"absDelta={delta[i]!r}"
        )


def independent_spectral_shape(
    xb: np.ndarray,
    names: list[str],
) -> tuple[np.ndarray, list[str]]:
    index = {name: i for i, name in enumerate(names)}
    bands = ("low", "lowMid", "mid", "highMid", "high")
    stages = ("Burst", "Rise", "Decay30", "Decay60", "PostSlope")
    axis = np.asarray([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=np.float64)
    eps = 1e-9

    cols: list[np.ndarray] = []
    labels: list[str] = []
    for stage in stages:
        values = np.column_stack(
            [xb[:, index[f"mean::{band}{stage}"]] for band in bands]
        )
        energy = np.abs(values) + eps
        denom = np.sum(energy, axis=1)
        centroid = np.sum(energy * axis[None, :], axis=1) / denom
        spread = np.sum(
            energy * np.square(axis[None, :] - centroid[:, None]),
            axis=1,
        ) / denom
        cols.extend([centroid, spread])
        labels.extend(
            [
                f"v143::spectral_shape::{stage}::centroid",
                f"v143::spectral_shape::{stage}::spread",
            ]
        )

    return np.column_stack(cols), labels


def main() -> None:
    if not MODEL_PATH.is_file():
        raise RuntimeError(f"Frozen production model missing: {MODEL_PATH}")

    engine = V143ProductionEngine(MODEL_PATH)
    payload = json.loads(MODEL_PATH.read_text(encoding="utf-8"))

    if engine.representation != "v112_interactions":
        raise RuntimeError(f"Unexpected representation: {engine.representation}")
    if engine.family != "spectral_shape":
        raise RuntimeError(f"Unexpected family: {engine.family}")
    if engine.feature_count != 148:
        raise RuntimeError(f"Unexpected feature count: {engine.feature_count}")
    if engine.q != 0.2:
        raise RuntimeError(f"Unexpected q: {engine.q}")

    sr = 22050
    stem_a = synthetic_stem(sr, 2.4, 0)
    stem_b = synthetic_stem(sr, 2.4, 1)

    candidates = [
        {"measure": 1, "step": 0, "time_seconds": 0.50, "pitch": 52},
        {"measure": 1, "step": 1, "time_seconds": 0.75, "pitch": 55},
        {"measure": 1, "step": 2, "time_seconds": 1.00, "pitch": 57},
        {"measure": 1, "step": 3, "time_seconds": 1.25, "pitch": 59},
        {"measure": 2, "step": 0, "time_seconds": 1.50, "pitch": 60},
        {"measure": 2, "step": 1, "time_seconds": 1.75, "pitch": 64},
    ]

    # 1) Exact spectro-temporal carrier math equivalence.
    runtime_rows = runtime.build_carrier_rows(
        candidates,
        stem_a,
        sr,
        stem_b,
        sr,
    )

    for candidate, row in zip(candidates, runtime_rows):
        t = float(candidate["time_seconds"])
        runtime_a = runtime.stem_patch(stem_a, sr, t)
        runtime_b = runtime.stem_patch(stem_b, sr, t)
        history_a = historical_patch.stem_patch(stem_a, sr, t)
        history_b = historical_patch.stem_patch(stem_b, sr, t)

        assert_dict_exact(runtime_a, history_a, f"stem A @ {t}")
        assert_dict_exact(runtime_b, history_b, f"stem B @ {t}")

        historical_pair = historical_patch.pair_patch(history_a, history_b)
        assert_dict_exact(row["features"], historical_pair, f"paired carrier @ {t}")

    # 2) Exact phase feature and V112 interaction equivalence.
    runtime_pf = runtime.phase_features(runtime_rows)
    historical_pf = np.asarray(v17.phase_features(runtime_rows), dtype=np.float64)
    if not np.array_equal(runtime_pf, historical_pf):
        raise RuntimeError("Runtime phase features differ from authoritative V17")

    base_names = sorted(runtime_rows[0]["features"])
    xb = np.asarray(
        [[float(row["features"][name]) for name in base_names] for row in runtime_rows],
        dtype=np.float64,
    )

    runtime_interactions, runtime_interaction_names = runtime.build_phase_interactions(
        xb,
        base_names,
        runtime_pf,
    )
    historical_interactions, historical_interaction_names = v112.build_phase_interactions(
        xb,
        base_names,
        historical_pf,
    )

    if runtime_interaction_names != historical_interaction_names:
        raise RuntimeError("V112 interaction feature-name ordering differs")
    if not np.array_equal(runtime_interactions, historical_interactions):
        raise RuntimeError("V112 interaction numeric values differ")

    # 3) Independently rebuild the winning 138-column representation + the
    # frozen 10-column spectral_shape family, then compare against runtime.
    expected_family, expected_family_names = independent_spectral_shape(
        xb,
        base_names,
    )
    expected_representation = np.concatenate(
        [xb, historical_pf[:, [1, 3]], historical_interactions],
        axis=1,
    )
    expected_representation_names = (
        base_names
        + ["phase::col1", "phase::col3"]
        + historical_interaction_names
    )
    expected_matrix = np.concatenate(
        [expected_representation, expected_family],
        axis=1,
    )
    expected_names = tuple(expected_representation_names + expected_family_names)

    runtime_matrix, runtime_names = runtime.build_v143_matrix(runtime_rows, engine)

    if runtime_names != expected_names:
        raise RuntimeError("Independent V143 feature-name reconstruction differs")
    if runtime_names != engine.feature_names:
        raise RuntimeError("Runtime names differ from frozen model feature schema")
    if runtime_matrix.shape != (len(candidates), 148):
        raise RuntimeError(f"Unexpected runtime matrix shape: {runtime_matrix.shape}")
    if not np.array_equal(runtime_matrix, expected_matrix):
        delta = np.abs(runtime_matrix - expected_matrix)
        flat = int(np.argmax(delta))
        r, c = np.unravel_index(flat, delta.shape)
        raise RuntimeError(
            "V143 matrix numeric mismatch at "
            f"row={r} column={c} feature={runtime_names[c]} "
            f"absDelta={delta[r, c]!r}"
        )

    # 4) Score only through the production engine, then verify q selection.
    scores = engine.score_matrix(runtime_matrix)
    ranked = runtime.rank_and_select(runtime_rows, engine)
    selected = [row for row in ranked if row["v143Selected"]]
    expected_selected = max(1, int(round(engine.q * len(runtime_rows))))

    if len(scores) != len(candidates):
        raise RuntimeError("Production score count mismatch")
    if len(selected) != expected_selected:
        raise RuntimeError(
            f"Q-selection mismatch: selected={len(selected)} "
            f"expected={expected_selected}"
        )

    validation = payload.get("validation") or {}
    if validation.get("exactSerializationReplayPassed") is not True:
        raise RuntimeError("Frozen model is not marked serialization-replay passed")

    print("=== V143 RHYTHM RUNTIME ADAPTER VERIFIED ===")
    print("Historical carrier math exact: True")
    print("Historical phase math exact: True")
    print("Historical V112 interaction math exact: True")
    print("Frozen representation: v112_interactions")
    print("Frozen family: spectral_shape")
    print("Base carrier features: 120")
    print("Representation features: 138")
    print("Family features: 10")
    print("Final feature count: 148")
    print("Frozen feature ordering exact: True")
    print("Synthetic rows scored:", len(scores))
    print("Q:", engine.q)
    print("Selected rows:", len(selected))
    print("Runtime labels required: False")
    print("Professional reference used: False")
    print("READY FOR GENERIC CANDIDATE/TIMING ADAPTER: True")


if __name__ == "__main__":
    main()
