from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

from v143_production_engine import V143ProductionEngine


PERIODS = (2, 4)
PHASE_LABELS = ("p2sin", "p2cos", "p4sin", "p4cos")
LOWBAND_FEATURES = (
    "mean::lowBurst",
    "mean::lowRise",
    "mean::lowDecay30",
    "mean::lowPostSlope",
)
OFFSETS = (-0.090, -0.060, -0.030, 0.000, 0.030, 0.060, 0.120)
WINDOW_S = 0.028
BANDS = (
    (70.0, 220.0, "low"),
    (220.0, 500.0, "lowMid"),
    (500.0, 1200.0, "mid"),
    (1200.0, 2400.0, "highMid"),
    (2400.0, 4200.0, "high"),
)
SPECTRAL_STAGES = ("Burst", "Rise", "Decay30", "Decay60", "PostSlope")
EPS = 1e-9


@dataclass(frozen=True)
class CandidateSlot:
    measure: int
    step: int
    time_seconds: float
    metadata: dict[str, Any]


def _extract(audio: np.ndarray, sr: int, center_time: float, window_s: float) -> np.ndarray:
    half = max(8, int(round(sr * window_s / 2.0)))
    center = int(round(center_time * sr))
    lo = max(0, center - half)
    hi = min(len(audio), center + half)
    return np.asarray(audio[lo:hi], dtype=np.float64)


def _spectrum(x: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    if x.size < 32:
        return np.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.float64)
    mag = np.abs(np.fft.rfft(x * np.hanning(x.size)))
    freqs = np.fft.rfftfreq(x.size, d=1.0 / sr)
    return mag, freqs


def _band_power(mag: np.ndarray, freqs: np.ndarray, lo: float, hi: float) -> float:
    mask = (freqs >= lo) & (freqs <= hi)
    if not np.any(mask):
        return 0.0
    return float(np.sum(np.square(mag[mask], dtype=np.float64)))


def band_log_power(x: np.ndarray, sr: int, lo: float, hi: float) -> float:
    mag, freqs = _spectrum(x, sr)
    p = _band_power(mag, freqs, lo, hi)
    return math.log1p(max(0.0, p))


def stem_patch(audio: np.ndarray, sr: int, t: float) -> dict[str, float]:
    windows = [_extract(audio, sr, t + off, WINDOW_S) for off in OFFSETS]
    out: dict[str, float] = {}
    for lo, hi, name in BANDS:
        vals = [band_log_power(w, sr, lo, hi) for w in windows]
        for ti, value in enumerate(vals):
            out[f"{name}T{ti}"] = float(value)
        out[f"{name}Rise"] = float(vals[3] - vals[2])
        out[f"{name}Decay30"] = float(vals[3] - vals[4])
        out[f"{name}Decay60"] = float(vals[3] - vals[5])
        out[f"{name}PostSlope"] = float(vals[4] - vals[6])
        out[f"{name}Burst"] = float(vals[3] - 0.5 * (vals[2] + vals[4]))
    return out


def pair_patch(a: dict[str, float], b: dict[str, float]) -> dict[str, float]:
    if set(a) != set(b):
        raise RuntimeError("Stem patch schemas differ")
    out: dict[str, float] = {}
    for key in sorted(a):
        av = float(a[key])
        bv = float(b[key])
        out[f"mean::{key}"] = 0.5 * (av + bv)
        out[f"agree::{key}"] = 1.0 / (1.0 + abs(av - bv))
    return out


def normalize_candidate_slots(rows: Iterable[dict[str, Any] | CandidateSlot]) -> list[CandidateSlot]:
    out: list[CandidateSlot] = []
    for raw in rows:
        if isinstance(raw, CandidateSlot):
            slot = raw
        else:
            data = dict(raw)
            if "measure" not in data or "step" not in data:
                raise ValueError("Each candidate requires measure and step")
            if "time_seconds" in data:
                t = data["time_seconds"]
            elif "time" in data:
                t = data["time"]
            elif "startTime" in data:
                t = data["startTime"]
            elif "start_time" in data:
                t = data["start_time"]
            else:
                raise ValueError("Each candidate requires absolute time_seconds/time/startTime")
            metadata = {
                key: value
                for key, value in data.items()
                if key not in {"measure", "step", "time_seconds", "time", "startTime", "start_time"}
            }
            slot = CandidateSlot(
                measure=int(data["measure"]),
                step=int(data["step"]),
                time_seconds=float(t),
                metadata=metadata,
            )

        if slot.measure < 0 or slot.step < 0:
            raise ValueError(f"Invalid candidate location: {slot}")
        if not math.isfinite(slot.time_seconds) or slot.time_seconds < 0.0:
            raise ValueError(f"Invalid candidate time: {slot.time_seconds}")
        out.append(slot)

    if not out:
        raise ValueError("No candidate slots supplied")
    return out


def build_carrier_rows(
    candidates: Iterable[dict[str, Any] | CandidateSlot],
    stem_a_audio: np.ndarray,
    stem_a_sr: int,
    stem_b_audio: np.ndarray,
    stem_b_sr: int,
) -> list[dict[str, Any]]:
    slots = normalize_candidate_slots(candidates)
    a_audio = np.asarray(stem_a_audio, dtype=np.float64).reshape(-1)
    b_audio = np.asarray(stem_b_audio, dtype=np.float64).reshape(-1)

    if int(stem_a_sr) <= 0 or int(stem_b_sr) <= 0:
        raise ValueError("Sample rates must be positive")
    if a_audio.size == 0 or b_audio.size == 0:
        raise ValueError("Both production stem inputs must contain audio")
    if not np.isfinite(a_audio).all() or not np.isfinite(b_audio).all():
        raise ValueError("Stem audio contains non-finite values")

    rows: list[dict[str, Any]] = []
    for slot in slots:
        pa = stem_patch(a_audio, int(stem_a_sr), slot.time_seconds)
        pb = stem_patch(b_audio, int(stem_b_sr), slot.time_seconds)
        row = {
            "measure": slot.measure,
            "step": slot.step,
            "timeSeconds": slot.time_seconds,
            "features": pair_patch(pa, pb),
        }
        row.update(slot.metadata)
        rows.append(row)
    return rows


def phase_features(rows: Sequence[dict[str, Any]]) -> np.ndarray:
    out: list[list[float]] = []
    for row in rows:
        step = int(row["step"])
        vals: list[float] = []
        for period in PERIODS:
            angle = 2.0 * math.pi * (step % period) / float(period)
            vals.extend([math.sin(angle), math.cos(angle)])
        out.append(vals)
    return np.asarray(out, dtype=np.float64)


def build_phase_interactions(
    xb: np.ndarray,
    names: Sequence[str],
    pf: np.ndarray,
) -> tuple[np.ndarray, list[str]]:
    index = {str(name): i for i, name in enumerate(names)}
    missing = [name for name in LOWBAND_FEATURES if name not in index]
    if missing:
        raise RuntimeError(f"Missing V112 low-band features: {missing}")
    if pf.ndim != 2 or pf.shape[1] != 4:
        raise RuntimeError(f"Expected four rhythm phase columns, got {pf.shape}")

    cols: list[np.ndarray] = []
    labels: list[str] = []
    for low_name in LOWBAND_FEATURES:
        low = xb[:, index[low_name]]
        for j, phase_name in enumerate(PHASE_LABELS):
            cols.append(low * pf[:, j])
            labels.append(f"{low_name}*{phase_name}")
    return np.column_stack(cols).astype(np.float64), labels


def spectral_shape_features(
    xb: np.ndarray,
    names: Sequence[str],
) -> tuple[np.ndarray, list[str]]:
    index = {str(name): i for i, name in enumerate(names)}
    band_names = ("low", "lowMid", "mid", "highMid", "high")
    axis = np.asarray([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=np.float64)

    cols: list[np.ndarray] = []
    labels: list[str] = []
    for stage in SPECTRAL_STAGES:
        required = [f"mean::{band}{stage}" for band in band_names]
        missing = [name for name in required if name not in index]
        if missing:
            raise RuntimeError(f"Missing V143 spectral-shape inputs: {missing}")

        values = np.column_stack([xb[:, index[name]] for name in required])
        energy = np.abs(values) + EPS
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
    return np.column_stack(cols).astype(np.float64), labels


def build_v143_matrix(
    carrier_rows: Sequence[dict[str, Any]],
    engine: V143ProductionEngine | None = None,
) -> tuple[np.ndarray, tuple[str, ...]]:
    if not carrier_rows:
        raise ValueError("No carrier rows supplied")

    base_names = sorted((carrier_rows[0].get("features") or {}).keys())
    if len(base_names) != 120:
        raise RuntimeError(f"Expected 120 carrier features, found {len(base_names)}")

    for row in carrier_rows:
        row_names = sorted((row.get("features") or {}).keys())
        if row_names != base_names:
            raise RuntimeError("Carrier feature schema changed between rows")

    xb = np.asarray(
        [
            [float((row.get("features") or {})[name]) for name in base_names]
            for row in carrier_rows
        ],
        dtype=np.float64,
    )
    if not np.isfinite(xb).all():
        raise RuntimeError("Carrier matrix contains non-finite values")

    pf = phase_features(carrier_rows)
    interactions, interaction_names = build_phase_interactions(xb, base_names, pf)

    # Frozen winning representation is V112: base + p2cos + p4cos + 16 interactions.
    representation = np.concatenate([xb, pf[:, [1, 3]], interactions], axis=1)
    representation_names = (
        list(base_names)
        + ["phase::col1", "phase::col3"]
        + interaction_names
    )

    family, family_names = spectral_shape_features(xb, base_names)
    matrix = np.concatenate([representation, family], axis=1)
    feature_names = tuple(representation_names + family_names)

    scorer = engine or V143ProductionEngine()

    if scorer.representation != "v112_interactions":
        raise RuntimeError(
            f"Frozen model representation changed: {scorer.representation}"
        )
    if scorer.family != "spectral_shape":
        raise RuntimeError(f"Frozen model family changed: {scorer.family}")
    if matrix.shape[1] != 148:
        raise RuntimeError(f"Expected 148 V143 features, got {matrix.shape[1]}")
    if feature_names != scorer.feature_names:
        for i, (actual, expected) in enumerate(zip(feature_names, scorer.feature_names)):
            if actual != expected:
                raise RuntimeError(
                    "V143 feature ordering mismatch at "
                    f"column {i}: actual={actual!r}, expected={expected!r}"
                )
        raise RuntimeError(
            f"V143 feature schema length mismatch: {len(feature_names)} != "
            f"{len(scorer.feature_names)}"
        )
    if not np.isfinite(matrix).all():
        raise RuntimeError("V143 feature matrix contains non-finite values")

    return matrix, feature_names


def score_carrier_rows(
    carrier_rows: Sequence[dict[str, Any]],
    engine: V143ProductionEngine | None = None,
) -> np.ndarray:
    scorer = engine or V143ProductionEngine()
    matrix, _ = build_v143_matrix(carrier_rows, scorer)
    return scorer.score_matrix(matrix)


def rank_and_select(
    carrier_rows: Sequence[dict[str, Any]],
    engine: V143ProductionEngine | None = None,
) -> list[dict[str, Any]]:
    scorer = engine or V143ProductionEngine()
    scores = score_carrier_rows(carrier_rows, scorer)
    n = int(scores.size)
    k = max(1, int(round(scorer.q * n))) if n else 0

    # Exact historical selection ordering: descending np.argsort(scores).
    order = np.argsort(scores)[::-1]
    selected = set(int(i) for i in order[:k])

    ranked: list[dict[str, Any]] = []
    ranks = np.empty(n, dtype=np.int64)
    ranks[order] = np.arange(1, n + 1, dtype=np.int64)

    for i, row in enumerate(carrier_rows):
        out = dict(row)
        out["v143Score"] = float(scores[i])
        out["v143Rank"] = int(ranks[i])
        out["v143Selected"] = bool(i in selected)
        ranked.append(out)
    return ranked


def analyze_candidates(
    candidates: Iterable[dict[str, Any] | CandidateSlot],
    stem_a_audio: np.ndarray,
    stem_a_sr: int,
    stem_b_audio: np.ndarray,
    stem_b_sr: int,
    engine: V143ProductionEngine | None = None,
) -> list[dict[str, Any]]:
    carrier_rows = build_carrier_rows(
        candidates,
        stem_a_audio,
        stem_a_sr,
        stem_b_audio,
        stem_b_sr,
    )
    return rank_and_select(carrier_rows, engine)


def load_mono_wav(path: str | Path) -> tuple[np.ndarray, int]:
    """
    Lightweight production adapter for already-converted WAV/FLAC-like inputs.

    The website/API layer should convert arbitrary uploads before calling this
    runtime. soundfile is imported lazily so importing the V143 scorer itself
    does not require audio I/O dependencies.
    """
    try:
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "soundfile is required to load production audio files"
        ) from exc

    audio, sr = sf.read(str(path), always_2d=False)
    x = np.asarray(audio, dtype=np.float64)
    if x.ndim == 2:
        x = np.mean(x, axis=1)
    if x.ndim != 1:
        raise RuntimeError(f"Unexpected audio shape for {path}: {x.shape}")
    return x, int(sr)


__all__ = [
    "CandidateSlot",
    "analyze_candidates",
    "band_log_power",
    "build_carrier_rows",
    "build_phase_interactions",
    "build_v143_matrix",
    "load_mono_wav",
    "normalize_candidate_slots",
    "pair_patch",
    "phase_features",
    "rank_and_select",
    "score_carrier_rows",
    "spectral_shape_features",
    "stem_patch",
]
