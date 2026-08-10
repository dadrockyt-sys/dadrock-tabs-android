from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np

import profile_gomyway_3676_pitch_register_interval_recovery_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PITCH_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-spectral-harmonic-onset-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-spectral-harmonic-onset-stability-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision(t: int, f: int) -> float:
    return 100.0 * t / (t + f) if t + f else 0.0


def contiguous_fold(measure: int, lo: int, hi: int) -> int:
    span = max(1, hi - lo + 1)
    return min(FOLD_COUNT - 1, int(FOLD_COUNT * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / FOLD_COUNT
    pos = ((measure - lo) + width / 2.0) % span
    return min(FOLD_COUNT - 1, int(pos / width))


def bucket(value: float, cuts: list[float], labels: list[str]) -> str:
    for cut, label in zip(cuts, labels):
        if value <= cut:
            return label
    return labels[-1]


def midi_hz(pitch: int) -> float:
    return 440.0 * (2.0 ** ((pitch - 69) / 12.0))


def rms(x: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)) + 1e-12))


def spectral_band_energy(audio: np.ndarray, sr: int, center_time: float, center_hz: float, half_width_hz: float = 10.0, window_s: float = 0.12) -> float:
    half = max(32, int(sr * window_s / 2.0))
    center = int(round(center_time * sr))
    lo = max(0, center - half)
    hi = min(len(audio), center + half)
    x = np.asarray(audio[lo:hi], dtype=np.float64)
    if x.size < 64:
        return 0.0
    win = np.hanning(x.size)
    spec = np.abs(np.fft.rfft(x * win)) ** 2
    freqs = np.fft.rfftfreq(x.size, 1.0 / sr)
    mask = np.abs(freqs - center_hz) <= half_width_hz
    if not np.any(mask):
        return 0.0
    return float(np.sum(spec[mask]))


def broadband_energy(audio: np.ndarray, sr: int, center_time: float, lo_hz: float = 70.0, hi_hz: float = 1600.0, window_s: float = 0.12) -> float:
    half = max(32, int(sr * window_s / 2.0))
    center = int(round(center_time * sr))
    lo = max(0, center - half)
    hi = min(len(audio), center + half)
    x = np.asarray(audio[lo:hi], dtype=np.float64)
    if x.size < 64:
        return 0.0
    win = np.hanning(x.size)
    spec = np.abs(np.fft.rfft(x * win)) ** 2
    freqs = np.fft.rfftfreq(x.size, 1.0 / sr)
    mask = (freqs >= lo_hz) & (freqs <= hi_hz)
    return float(np.sum(spec[mask])) if np.any(mask) else 0.0


def stem_features(audio: np.ndarray, sr: int, t: float, pitch: int) -> dict[str, float]:
    f0 = midi_hz(pitch)
    bb = broadband_energy(audio, sr, t)
    harmonic_energies: list[float] = []
    for h in (1, 2, 3, 4):
        hz = f0 * h
        if hz >= sr / 2.0:
            harmonic_energies.append(0.0)
        else:
            harmonic_energies.append(spectral_band_energy(audio, sr, t, hz, max(7.0, hz * 0.012)))
    hsum = sum(harmonic_energies)
    fundamental_share = harmonic_energies[0] / (bb + 1e-12)
    harmonic_share = hsum / (bb + 1e-12)
    upper_share = sum(harmonic_energies[1:]) / (harmonic_energies[0] + 1e-12)
    harmonic_count = sum(e > max(bb * 0.005, 1e-12) for e in harmonic_energies)

    pre_n = max(8, int(sr * 0.045))
    post_n = max(8, int(sr * 0.045))
    center = int(round(t * sr))
    pre = np.asarray(audio[max(0, center - pre_n):center], dtype=np.float64)
    post = np.asarray(audio[center:min(len(audio), center + post_n)], dtype=np.float64)
    later_center = min(len(audio) - 1, center + int(sr * 0.085))
    later = np.asarray(audio[max(0, later_center - post_n // 2):min(len(audio), later_center + post_n // 2)], dtype=np.float64)
    pre_rms, post_rms, later_rms = rms(pre), rms(post), rms(later)
    attack_ratio = post_rms / (pre_rms + 1e-9)
    sustain_ratio = later_rms / (post_rms + 1e-9)
    return {
        "fundamentalShare": fundamental_share,
        "harmonicShare": harmonic_share,
        "upperVsFundamental": upper_share,
        "harmonicCount": float(harmonic_count),
        "attackRatio": attack_ratio,
        "sustainRatio": sustain_ratio,
        "postRms": post_rms,
    }


def row_signatures(features: dict[str, Any]) -> set[str]:
    hs = bucket(float(features["harmonicShareMean"]), [0.01, 0.025, 0.05, 0.10, 1e9], ["hs01", "hs025", "hs05", "hs10", "hs10p"])
    fs = bucket(float(features["fundamentalShareMean"]), [0.003, 0.008, 0.02, 0.05, 1e9], ["fs003", "fs008", "fs02", "fs05", "fs05p"])
    uv = bucket(float(features["upperVsFundamentalMean"]), [0.5, 1.0, 2.0, 4.0, 1e9], ["uv05", "uv10", "uv20", "uv40", "uv40p"])
    ar = bucket(float(features["attackRatioMean"]), [0.8, 1.1, 1.5, 2.2, 1e9], ["ar08", "ar11", "ar15", "ar22", "ar22p"])
    su = bucket(float(features["sustainRatioMean"]), [0.45, 0.70, 0.95, 1.25, 1e9], ["su045", "su070", "su095", "su125", "su125p"])
    hc = int(features["harmonicCountMin"])
    agree = int(features["harmonicAgreement"])
    return {
        f"specHarmonicShare::{hs}",
        f"specFundamentalShare::{fs}",
        f"specUpperRatio::{uv}",
        f"specAttack::{ar}",
        f"specSustain::{su}",
        f"specHarmonicCount::h{hc}",
        f"specStemAgreement::a{agree}",
        f"specCross::{hs}|{fs}|h{hc}",
        f"specCross::{hs}|{ar}|{su}",
        f"specCross::{fs}|{uv}|a{agree}",
    }


def counts(rows: list[dict[str, Any]], sig: str) -> tuple[int, int]:
    t = f = 0
    for r in rows:
        if sig not in r["signatures"]:
            continue
        if r["label"] == "true":
            t += 1
        else:
            f += 1
    return t, f


def partition_summary(rows: list[dict[str, Any]], sig: str, fold_fn: Callable[[int], int]) -> dict[str, Any]:
    parts = []
    for fold in range(FOLD_COUNT):
        held = [r for r in rows if fold_fn(r["measure"]) == fold]
        t, f = counts(held, sig)
        parts.append({"fold": fold, "true": t, "false": f, "support": t + f, "precision": round(precision(t, f), 2)})
    supported = [p for p in parts if p["support"] > 0]
    useful = [p for p in supported if p["true"] > 0 and p["precision"] >= 35.0]
    return {
        "supportedFolds": len(supported),
        "usefulFolds": len(useful),
        "meanSupportedPrecision": round(sum(p["precision"] for p in supported) / len(supported), 2) if supported else 0.0,
        "parts": parts,
    }


def main() -> None:
    before = sha256(prof.recall.CANDIDATE_PATH)
    payload = json.loads(PITCH_PATH.read_text(encoding="utf-8"))
    raw_rows = list(payload.get("candidateRows") or [])
    if tuple(payload.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Pitch profiler is not anchored to frozen 36.76 champion")
    if not raw_rows:
        raise RuntimeError("Pitch residual rows are missing")

    candidate_payload = prof.v2.load_json(prof.recall.CANDIDATE_PATH)
    events = prof.v2.candidate_rows(candidate_payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = prof.v2.build_timing_grid(events)

    winner_audio, winner_sr = prof.harmonic.load_mono(prof.harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = prof.harmonic.load_mono(prof.harmonic.legacy.ALT_STEM)

    # Detection-side measurements are completed before downstream labels are read.
    measured: list[dict[str, Any]] = []
    for idx, row in enumerate(raw_rows):
        measure, step, pitch = int(row["measure"]), int(row["step"]), int(row["pitch"])
        t = float(grid.get((measure, step), 0.0))
        a = stem_features(np.asarray(winner_audio), int(winner_sr), t, pitch)
        b = stem_features(np.asarray(alt_audio), int(alt_sr), t, pitch)
        features = {
            "fundamentalShareMean": (a["fundamentalShare"] + b["fundamentalShare"]) / 2.0,
            "harmonicShareMean": (a["harmonicShare"] + b["harmonicShare"]) / 2.0,
            "upperVsFundamentalMean": (a["upperVsFundamental"] + b["upperVsFundamental"]) / 2.0,
            "harmonicCountMin": min(a["harmonicCount"], b["harmonicCount"]),
            "attackRatioMean": (a["attackRatio"] + b["attackRatio"]) / 2.0,
            "sustainRatioMean": (a["sustainRatio"] + b["sustainRatio"]) / 2.0,
            "harmonicAgreement": int(a["harmonicCount"] >= 2 and b["harmonicCount"] >= 2),
        }
        measured.append({
            "measure": measure,
            "step": step,
            "pitch": pitch,
            "token": [measure, step, pitch],
            "features": features,
            "signatures": sorted(row_signatures(features)),
        })
        if idx and idx % 5000 == 0:
            print(f"measured {idx}/{len(raw_rows)} residual rows ...", flush=True)

    # Professional-reference-derived labels are attached only after audio measurements are frozen.
    rows = []
    for measured_row, source_row in zip(measured, raw_rows):
        rows.append({**measured_row, "label": str(source_row.get("label"))})

    residual_true = sum(r["label"] == "true" for r in rows)
    residual_false = len(rows) - residual_true
    base_precision = precision(residual_true, residual_false)
    measures = [r["measure"] for r in rows]
    lo, hi = min(measures), max(measures)
    normal_fn = lambda m: m % FOLD_COUNT
    section_fn = lambda m: contiguous_fold(m, lo, hi)
    shifted_fn = lambda m: shifted_fold(m, lo, hi)

    signature_set = sorted({s for r in rows for s in r["signatures"]})
    ranked = []
    for sig in signature_set:
        t, f = counts(rows, sig)
        if t < 3 or t + f < 5:
            continue
        p = precision(t, f)
        normal = partition_summary(rows, sig, normal_fn)
        section = partition_summary(rows, sig, section_fn)
        shifted = partition_summary(rows, sig, shifted_fn)
        agreement = sum((normal["usefulFolds"] >= 3, section["usefulFolds"] >= 3, shifted["usefulFolds"] >= 3))
        stable = (
            p >= max(35.0, base_precision + 5.0)
            and normal["supportedFolds"] >= 3
            and section["supportedFolds"] >= 3
            and shifted["supportedFolds"] >= 3
            and agreement >= 2
        )
        ranked.append({
            "signature": sig,
            "true": t,
            "false": f,
            "precision": round(p, 2),
            "agreementSchemes": agreement,
            "stableDiagnostic": stable,
            "normal": normal,
            "section": section,
            "shiftedWindow": shifted,
        })
    ranked.sort(key=lambda r: (not r["stableDiagnostic"], -r["agreementSchemes"], -r["precision"], -r["true"], r["false"]))
    stable = [r for r in ranked if r["stableDiagnostic"]]

    after = sha256(prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during spectral/harmonic/onset profiling")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-spectral-harmonic-onset-stability-diagnostic",
        "frozenChampionPitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "residualRows": len(rows),
        "residualTrue": residual_true,
        "residualFalse": residual_false,
        "residualBasePrecision": round(base_precision, 2),
        "stableDiagnosticSignatureCount": len(stable),
        "stableSignatures": stable,
        "rankedSignatures": ranked,
        "candidateRows": rows,
        "note": "Diagnostic only. Audio spectral/harmonic/onset features are computed before downstream grading labels are attached. Stable signatures require later nested training-fold validation.",
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "stableDiagnosticSignatureCount": len(stable),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 SPECTRAL HARMONIC ONSET STABILITY V1 COMPLETE")
    print("Residual base precision:", round(base_precision, 2))
    print("Stable diagnostic spectral signatures:", len(stable))
    for item in stable[:30]:
        print("STABLE", {
            "signature": item["signature"], "true": item["true"], "false": item["false"],
            "precision": item["precision"], "agreementSchemes": item["agreementSchemes"],
        })
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
