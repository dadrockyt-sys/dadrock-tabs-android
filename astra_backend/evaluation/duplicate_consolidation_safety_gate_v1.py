"""Duplicate Consolidation Safety Gate V1.

Diagnostic-only decision layer for duplicate-class guitar/bass stem pairs.

The gate consumes separator-output pair evidence only.  Ground-truth/reference
audio is deliberately absent from this module.  Evaluation code may score the
chosen action against a reference *after* this decision has been made.

V1 is intentionally conservative: automatic full merge is authorized only for
pairs that look like near-zero-lag, phase-consistent, spectrally overlapping
views of the same waveform with meaningful time-varying allocation between the
two stems.  Obvious delay/phase or spectral-split behavior is preserved.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import numpy as np
from scipy.signal import stft


@dataclass(frozen=True)
class ConsolidationSafetyConfig:
    # Analysis
    n_fft: int = 1024
    hop: int = 256
    max_lag_ms: float = 10.0
    active_floor_db: float = -55.0
    low_high_split_hz: float = 700.0

    # Frozen prospective merge-safe rule.
    merge_zero_lag_corr_min: float = 0.97
    merge_best_lag_ms_max: float = 1.0
    merge_spectral_shared_min: float = 0.65
    merge_phase_consistency_min: float = 0.90
    merge_energy_share_swing_min: float = 0.12

    # Strong preserve-separate evidence.
    preserve_best_lag_ms_min: float = 2.5
    preserve_spectral_shared_max: float = 0.35
    preserve_phase_consistency_max: float = 0.70

    def to_dict(self):
        return asdict(self)


def _mono(x: np.ndarray) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    return a if a.ndim == 1 else np.mean(a, axis=1)


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    n = min(len(a), len(b))
    if n < 8:
        return 0.0
    aa = np.asarray(a[:n], dtype=np.float64)
    bb = np.asarray(b[:n], dtype=np.float64)
    aa = aa - np.mean(aa)
    bb = bb - np.mean(bb)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    return 0.0 if den <= 1e-20 else float(np.dot(aa, bb) / den)


def _best_lag_corr(a: np.ndarray, b: np.ndarray, fs: int, max_lag_ms: float):
    aa = _mono(a)
    bb = _mono(b)
    n = min(len(aa), len(bb))
    aa = aa[:n]
    bb = bb[:n]
    max_lag = max(1, int(round(fs * max_lag_ms / 1000.0)))
    best_abs = -1.0
    best_signed = 0.0
    best_lag = 0
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            xa = aa[-lag:]
            xb = bb[: len(xa)]
        elif lag > 0:
            xa = aa[:-lag]
            xb = bb[lag:]
        else:
            xa = aa
            xb = bb
        if len(xa) < 8:
            continue
        c = _corr(xa, xb)
        if abs(c) > best_abs:
            best_abs = abs(c)
            best_signed = c
            best_lag = lag
    return float(max(best_abs, 0.0)), float(best_signed), int(best_lag)


def _stft_mono(x: np.ndarray, fs: int, cfg: ConsolidationSafetyConfig):
    f, _, z = stft(
        _mono(x),
        fs=fs,
        nperseg=cfg.n_fft,
        noverlap=cfg.n_fft - cfg.hop,
        boundary="zeros",
        padded=True,
    )
    return f, z.astype(np.complex128)


def _frame_energy(x: np.ndarray, frame: int, hop: int) -> np.ndarray:
    y = _mono(x)
    if len(y) < frame:
        return np.array([float(np.mean(y * y)) if len(y) else 0.0], dtype=np.float64)
    vals = []
    for start in range(0, len(y) - frame + 1, hop):
        q = y[start : start + frame]
        vals.append(float(np.mean(q * q)))
    return np.asarray(vals, dtype=np.float64)


def pair_safety_metrics(
    a: np.ndarray,
    b: np.ndarray,
    fs: int,
    cfg: ConsolidationSafetyConfig = ConsolidationSafetyConfig(),
) -> dict:
    n = min(len(a), len(b))
    a = np.asarray(a[:n], dtype=np.float64)
    b = np.asarray(b[:n], dtype=np.float64)

    zero = _corr(_mono(a), _mono(b))
    best_abs, best_signed, lag = _best_lag_corr(a, b, fs, cfg.max_lag_ms)

    f, za = _stft_mono(a, fs, cfg)
    _, zb = _stft_mono(b, fs, cfg)
    pa = np.abs(za) ** 2
    pb = np.abs(zb) ** 2
    total_a = float(np.sum(pa))
    total_b = float(np.sum(pb))
    shared = float(np.sum(np.minimum(pa, pb)))
    union = float(np.sum(np.maximum(pa, pb)))
    unique_a = float(np.sum(np.maximum(pa - pb, 0.0)))
    unique_b = float(np.sum(np.maximum(pb - pa, 0.0)))

    spectral_shared = shared / (union + 1e-20)
    unique_a_frac = unique_a / (total_a + 1e-20)
    unique_b_frac = unique_b / (total_b + 1e-20)

    low = f < cfg.low_high_split_hz
    high = ~low
    def band_ratio(p):
        lo = float(np.sum(p[low]))
        hi = float(np.sum(p[high]))
        return 10.0 * np.log10((lo + 1e-20) / (hi + 1e-20))

    peak = max(float(np.max(pa)) if pa.size else 0.0, float(np.max(pb)) if pb.size else 0.0)
    active = (pa > peak * 10.0 ** (cfg.active_floor_db / 10.0)) & (
        pb > peak * 10.0 ** (cfg.active_floor_db / 10.0)
    )
    cross = za * np.conj(zb)
    if np.any(active):
        unit = cross[active] / (np.abs(cross[active]) + 1e-20)
        weights = np.sqrt(pa[active] * pb[active])
        phase_consistency = float(abs(np.sum(weights * unit) / (np.sum(weights) + 1e-20)))
    else:
        phase_consistency = 0.0

    ea = _frame_energy(a, cfg.n_fft, cfg.hop)
    eb = _frame_energy(b, cfg.n_fft, cfg.hop)
    m = min(len(ea), len(eb))
    ea = ea[:m]
    eb = eb[:m]
    frame_corr = _corr(ea, eb) if m >= 3 else 0.0
    share = ea / (ea + eb + 1e-20)
    if len(share):
        share_swing = float(np.percentile(share, 95) - np.percentile(share, 5))
    else:
        share_swing = 0.0

    return {
        "zeroLagCorr": float(zero),
        "bestLagAbsCorr": best_abs,
        "bestLagSignedCorr": best_signed,
        "bestLagSamples": lag,
        "bestLagMs": float(1000.0 * lag / fs),
        "spectralSharedFraction": float(spectral_shared),
        "spectralUniqueFractionA": float(unique_a_frac),
        "spectralUniqueFractionB": float(unique_b_frac),
        "lowHighBalanceDbA": float(band_ratio(pa)),
        "lowHighBalanceDbB": float(band_ratio(pb)),
        "phaseConsistency": phase_consistency,
        "frameEnergyCorrelation": float(frame_corr),
        "energyShareSwing": share_swing,
    }


def decide_consolidation(
    pair_state: str,
    metrics: dict,
    cfg: ConsolidationSafetyConfig = ConsolidationSafetyConfig(),
) -> dict:
    duplicate = pair_state in {"duplicate_guitar_candidate", "duplicate_bass_candidate"}
    if not duplicate:
        return {
            "decision": "preserve_separate",
            "reason": "pair_classifier_not_duplicate_candidate",
            "automaticAction": "none",
        }

    lag_abs = abs(float(metrics["bestLagMs"]))
    merge_safe = (
        float(metrics["zeroLagCorr"]) >= cfg.merge_zero_lag_corr_min
        and lag_abs <= cfg.merge_best_lag_ms_max
        and float(metrics["spectralSharedFraction"]) >= cfg.merge_spectral_shared_min
        and float(metrics["phaseConsistency"]) >= cfg.merge_phase_consistency_min
        and float(metrics["energyShareSwing"]) >= cfg.merge_energy_share_swing_min
    )
    if merge_safe:
        return {
            "decision": "merge_safe",
            "reason": "high_coherence_zero_lag_shared_spectrum_phase_consistent_time_varying_allocation",
            "automaticAction": "full_merge",
        }

    preserve = (
        lag_abs >= cfg.preserve_best_lag_ms_min
        or float(metrics["spectralSharedFraction"]) <= cfg.preserve_spectral_shared_max
        or float(metrics["phaseConsistency"]) <= cfg.preserve_phase_consistency_max
    )
    if preserve:
        return {
            "decision": "preserve_separate",
            "reason": "strong_delay_phase_or_spectral_separation_evidence",
            "automaticAction": "none",
        }

    return {
        "decision": "uncertain",
        "reason": "duplicate_candidate_but_merge_safety_not_established",
        "automaticAction": "none",
    }
