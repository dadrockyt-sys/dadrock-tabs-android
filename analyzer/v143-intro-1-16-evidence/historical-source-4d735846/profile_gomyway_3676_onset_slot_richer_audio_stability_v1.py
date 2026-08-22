from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

import profile_gomyway_3676_onset_slot_stability_v1 as onset

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-stability-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5

FEATURE_NAMES = [
    "attackShortMean",
    "attackMediumMean",
    "fluxShortMean",
    "fluxMediumMean",
    "lowBandAttackMean",
    "midBandAttackMean",
    "highBandAttackMean",
    "centroidShiftMean",
    "crestMean",
    "transientContrastMean",
    "sustainShortMean",
    "sustainLongMean",
    "stemAttackAgreement",
    "stemFluxAgreement",
    "stemPeakTimingAgreement",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contiguous_fold(measure: int, lo: int, hi: int) -> int:
    span = max(1, hi - lo + 1)
    return min(FOLD_COUNT - 1, int(FOLD_COUNT * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / FOLD_COUNT
    pos = ((measure - lo) + width / 2.0) % span
    return min(FOLD_COUNT - 1, int(pos / width))


def rms(x: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)) + 1e-12))


def extract(audio: np.ndarray, sr: int, center_time: float, window_s: float) -> np.ndarray:
    half = max(8, int(round(sr * window_s / 2.0)))
    center = int(round(center_time * sr))
    lo = max(0, center - half)
    hi = min(len(audio), center + half)
    return np.asarray(audio[lo:hi], dtype=np.float64)


def spectrum(x: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    if x.size < 32:
        return np.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.float64)
    mag = np.abs(np.fft.rfft(x * np.hanning(x.size)))
    freqs = np.fft.rfftfreq(x.size, d=1.0 / sr)
    return mag, freqs


def band_power(mag: np.ndarray, freqs: np.ndarray, lo: float, hi: float) -> float:
    mask = (freqs >= lo) & (freqs <= hi)
    if not np.any(mask):
        return 0.0
    return float(np.sum(np.square(mag[mask], dtype=np.float64)))


def spectral_flux(pre: np.ndarray, now: np.ndarray, sr: int) -> float:
    a, _ = spectrum(pre, sr)
    b, _ = spectrum(now, sr)
    n = min(a.size, b.size)
    if n <= 1:
        return 0.0
    a = a[:n] / (np.linalg.norm(a[:n]) + 1e-12)
    b = b[:n] / (np.linalg.norm(b[:n]) + 1e-12)
    return float(np.sum(np.maximum(b - a, 0.0)))


def spectral_centroid(x: np.ndarray, sr: int) -> float:
    mag, freqs = spectrum(x, sr)
    denom = float(np.sum(mag)) + 1e-12
    return float(np.sum(mag * freqs) / denom)


def peak_attack_offset(audio: np.ndarray, sr: int, t: float) -> float:
    radius_s = 0.045
    radius = max(8, int(sr * radius_s))
    center = int(round(t * sr))
    lo = max(1, center - radius)
    hi = min(len(audio) - 1, center + radius)
    if hi - lo < 16:
        return 0.0
    x = np.asarray(audio[lo:hi], dtype=np.float64)
    env = np.abs(x)
    smooth_n = max(3, int(sr * 0.004))
    kernel = np.ones(smooth_n, dtype=np.float64) / smooth_n
    smooth = np.convolve(env, kernel, mode="same")
    diff = np.diff(smooth, prepend=smooth[0])
    idx = int(np.argmax(diff))
    sample = lo + idx
    return float((sample - center) / sr)


def stem_features(audio: np.ndarray, sr: int, t: float) -> dict[str, float]:
    pre_short = extract(audio, sr, t - 0.030, 0.030)
    now_short = extract(audio, sr, t + 0.010, 0.030)
    pre_med = extract(audio, sr, t - 0.050, 0.070)
    now_med = extract(audio, sr, t + 0.018, 0.070)
    later_short = extract(audio, sr, t + 0.075, 0.045)
    later_long = extract(audio, sr, t + 0.165, 0.070)

    pre_short_rms = rms(pre_short)
    now_short_rms = rms(now_short)
    pre_med_rms = rms(pre_med)
    now_med_rms = rms(now_med)
    later_short_rms = rms(later_short)
    later_long_rms = rms(later_long)

    attack_short = now_short_rms / (pre_short_rms + 1e-9)
    attack_med = now_med_rms / (pre_med_rms + 1e-9)
    flux_short = spectral_flux(pre_short, now_short, sr)
    flux_med = spectral_flux(pre_med, now_med, sr)

    pre_mag, pre_freqs = spectrum(pre_med, sr)
    now_mag, now_freqs = spectrum(now_med, sr)
    bands = ((70.0, 350.0), (350.0, 1200.0), (1200.0, 3500.0))
    band_attacks: list[float] = []
    for lo, hi in bands:
        p = band_power(pre_mag, pre_freqs, lo, hi)
        n = band_power(now_mag, now_freqs, lo, hi)
        band_attacks.append(math.log1p(n) - math.log1p(p))

    centroid_shift = (spectral_centroid(now_med, sr) - spectral_centroid(pre_med, sr)) / 1000.0
    peak = float(np.max(np.abs(now_short))) if now_short.size else 0.0
    crest = peak / (now_short_rms + 1e-9)
    transient_contrast = peak / (later_short_rms + 1e-9)
    sustain_short = later_short_rms / (now_med_rms + 1e-9)
    sustain_long = later_long_rms / (now_med_rms + 1e-9)

    return {
        "attackShort": attack_short,
        "attackMedium": attack_med,
        "fluxShort": flux_short,
        "fluxMedium": flux_med,
        "lowBandAttack": band_attacks[0],
        "midBandAttack": band_attacks[1],
        "highBandAttack": band_attacks[2],
        "centroidShift": centroid_shift,
        "crest": crest,
        "transientContrast": transient_contrast,
        "sustainShort": sustain_short,
        "sustainLong": sustain_long,
        "peakOffset": peak_attack_offset(audio, sr, t),
    }


def pair_features(a: dict[str, float], b: dict[str, float]) -> dict[str, float]:
    def mean(name: str) -> float:
        return (float(a[name]) + float(b[name])) / 2.0

    attack_log_delta = abs(math.log(max(float(a["attackShort"]), 1e-9)) - math.log(max(float(b["attackShort"]), 1e-9)))
    flux_delta = abs(float(a["fluxShort"]) - float(b["fluxShort"]))
    peak_delta = abs(float(a["peakOffset"]) - float(b["peakOffset"]))
    return {
        "attackShortMean": mean("attackShort"),
        "attackMediumMean": mean("attackMedium"),
        "fluxShortMean": mean("fluxShort"),
        "fluxMediumMean": mean("fluxMedium"),
        "lowBandAttackMean": mean("lowBandAttack"),
        "midBandAttackMean": mean("midBandAttack"),
        "highBandAttackMean": mean("highBandAttack"),
        "centroidShiftMean": mean("centroidShift"),
        "crestMean": mean("crest"),
        "transientContrastMean": mean("transientContrast"),
        "sustainShortMean": mean("sustainShort"),
        "sustainLongMean": mean("sustainLong"),
        "stemAttackAgreement": 1.0 / (1.0 + attack_log_delta),
        "stemFluxAgreement": 1.0 / (1.0 + flux_delta),
        "stemPeakTimingAgreement": 1.0 / (1.0 + 40.0 * peak_delta),
    }


def effect(rows: list[dict[str, Any]], feature: str) -> float:
    true_vals = [float(r["features"][feature]) for r in rows if r["label"] == "true"]
    false_vals = [float(r["features"][feature]) for r in rows if r["label"] != "true"]
    if not true_vals or not false_vals:
        return 0.0
    all_vals = np.asarray(true_vals + false_vals, dtype=np.float64)
    sd = float(np.std(all_vals))
    if not math.isfinite(sd) or sd < 1e-9:
        return 0.0
    return (float(np.mean(true_vals)) - float(np.mean(false_vals))) / sd


def summarize_feature(rows: list[dict[str, Any]], feature: str, schemes: list[tuple[str, Callable[[int], int]]]) -> dict[str, Any]:
    fold_effects: list[dict[str, Any]] = []
    for scheme_name, fold_fn in schemes:
        for fold in range(FOLD_COUNT):
            held = [r for r in rows if fold_fn(int(r["measure"])) == fold]
            e = effect(held, feature)
            fold_effects.append({"scheme": scheme_name, "fold": fold, "effect": round(e, 6)})

    nonzero = [x for x in fold_effects if abs(float(x["effect"])) >= 0.02]
    pos = sum(float(x["effect"]) > 0 for x in nonzero)
    neg = sum(float(x["effect"]) < 0 for x in nonzero)
    dominant = "positive" if pos >= neg else "negative"
    dominant_count = max(pos, neg)
    consistency = 100.0 * dominant_count / len(nonzero) if nonzero else 0.0
    full_effect = effect(rows, feature)
    stable = len(nonzero) >= 8 and consistency >= 80.0 and abs(full_effect) >= 0.08
    return {
        "feature": feature,
        "fullEffect": round(full_effect, 6),
        "dominantDirection": dominant,
        "directionConsistencyPct": round(consistency, 2),
        "positiveFolds": pos,
        "negativeFolds": neg,
        "nonzeroFolds": len(nonzero),
        "stableDiagnostic": stable,
        "foldEffects": fold_effects,
    }


def main() -> None:
    before = sha256(onset.prof.recall.CANDIDATE_PATH)
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_slots = list(source.get("candidateSlots") or [])
    if not source_slots:
        raise RuntimeError("Onset-slot source candidateSlots are missing")
    if tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Onset-slot source is not anchored to frozen 36.76 champion")

    candidate_payload = onset.prof.v2.load_json(onset.prof.recall.CANDIDATE_PATH)
    events = onset.prof.v2.candidate_rows(candidate_payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = onset.prof.v2.build_timing_grid(events)

    winner_audio, winner_sr = onset.prof.harmonic.load_mono(onset.prof.harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = onset.prof.harmonic.load_mono(onset.prof.harmonic.legacy.ALT_STEM)
    winner_audio = np.asarray(winner_audio)
    alt_audio = np.asarray(alt_audio)

    # Detection-side richer audio measurements are completed before labels are read.
    measured: list[dict[str, Any]] = []
    for idx, slot in enumerate(source_slots):
        measure = int(slot["measure"])
        step = int(slot["step"])
        t = float(grid.get((measure, step), 0.0))
        a = stem_features(winner_audio, int(winner_sr), t)
        b = stem_features(alt_audio, int(alt_sr), t)
        measured.append({
            "measure": measure,
            "step": step,
            "features": pair_features(a, b),
        })
        if idx and idx % 250 == 0:
            print(f"measured {idx}/{len(source_slots)} richer onset slots ...", flush=True)

    # Professional-reference-derived slot labels are attached only after audio measurements are frozen.
    rows: list[dict[str, Any]] = []
    for measured_row, source_row in zip(measured, source_slots):
        rows.append({**measured_row, "label": str(source_row.get("label"))})

    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % FOLD_COUNT),
        ("section", lambda m: contiguous_fold(m, lo, hi)),
        ("shiftedWindow", lambda m: shifted_fold(m, lo, hi)),
    ]

    summaries = [summarize_feature(rows, feature, schemes) for feature in FEATURE_NAMES]
    summaries.sort(key=lambda r: (not r["stableDiagnostic"], -r["directionConsistencyPct"], -abs(r["fullEffect"]), r["feature"]))
    stable = [r for r in summaries if r["stableDiagnostic"]]

    after = sha256(onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during richer onset-slot profiling")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-onset-slot-richer-audio-stability-diagnostic",
        "frozenChampionPitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "slotCount": len(rows),
        "featureNames": FEATURE_NAMES,
        "stableFeatureCount": len(stable),
        "stableFeatures": stable,
        "featureSummaries": summaries,
        "candidateSlots": rows,
        "note": "Diagnostic only. Richer multi-window transient/spectral/stem-agreement features are computed before downstream grading labels are attached. No candidate or champion promotion is allowed.",
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
        "stableFeatureCount": len(stable),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT RICHER AUDIO STABILITY V1 COMPLETE")
    print("Measured slots:", len(rows))
    print("Stable richer-audio features:", len(stable))
    for item in stable:
        print("STABLE", {
            "feature": item["feature"],
            "fullEffect": item["fullEffect"],
            "direction": item["dominantDirection"],
            "consistencyPct": item["directionConsistencyPct"],
            "positiveFolds": item["positiveFolds"],
            "negativeFolds": item["negativeFolds"],
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
