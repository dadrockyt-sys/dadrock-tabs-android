from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np

import profile_gomyway_3676_pitch_register_interval_recovery_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PITCH_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-stability-v1-manifest.json"
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


def rms(x: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)) + 1e-12))


def frame(audio: np.ndarray, sr: int, center_time: float, window_s: float = 0.060) -> np.ndarray:
    half = max(32, int(sr * window_s / 2.0))
    center = int(round(center_time * sr))
    lo = max(0, center - half)
    hi = min(len(audio), center + half)
    return np.asarray(audio[lo:hi], dtype=np.float64)


def spectrum(x: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    if x.size < 64:
        return np.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.float64)
    win = np.hanning(x.size)
    mag = np.abs(np.fft.rfft(x * win))
    freqs = np.fft.rfftfreq(x.size, 1.0 / sr)
    return mag, freqs


def band_energy(mag: np.ndarray, freqs: np.ndarray, lo: float, hi: float) -> float:
    mask = (freqs >= lo) & (freqs <= hi)
    if not np.any(mask):
        return 0.0
    return float(np.sum(np.square(mag[mask], dtype=np.float64)))


def stem_slot_features(audio: np.ndarray, sr: int, t: float) -> dict[str, float]:
    pre = frame(audio, sr, t - 0.045)
    now = frame(audio, sr, t + 0.012)
    later = frame(audio, sr, t + 0.090)

    pre_rms = rms(pre)
    now_rms = rms(now)
    later_rms = rms(later)
    attack_ratio = now_rms / (pre_rms + 1e-9)
    sustain_ratio = later_rms / (now_rms + 1e-9)

    pre_mag, pre_freqs = spectrum(pre, sr)
    now_mag, now_freqs = spectrum(now, sr)
    n = min(pre_mag.size, now_mag.size)
    if n > 1:
        pre_norm = pre_mag[:n] / (np.linalg.norm(pre_mag[:n]) + 1e-12)
        now_norm = now_mag[:n] / (np.linalg.norm(now_mag[:n]) + 1e-12)
        flux = float(np.sum(np.maximum(now_norm - pre_norm, 0.0)))
    else:
        flux = 0.0

    low = band_energy(now_mag, now_freqs, 70.0, 350.0)
    mid = band_energy(now_mag, now_freqs, 350.0, 1200.0)
    high = band_energy(now_mag, now_freqs, 1200.0, 3500.0)
    total = low + mid + high + 1e-12

    return {
        "attackRatio": attack_ratio,
        "sustainRatio": sustain_ratio,
        "spectralFlux": flux,
        "midShare": mid / total,
        "highShare": high / total,
        "nowRms": now_rms,
    }


def signatures_for(f: dict[str, Any]) -> set[str]:
    attack = bucket(float(f["attackMean"]), [0.85, 1.05, 1.30, 1.70, 2.50, 1e9], ["a085", "a105", "a130", "a170", "a250", "a250p"])
    flux = bucket(float(f["fluxMean"]), [0.08, 0.16, 0.28, 0.45, 0.70, 1e9], ["f008", "f016", "f028", "f045", "f070", "f070p"])
    sustain = bucket(float(f["sustainMean"]), [0.45, 0.70, 0.95, 1.20, 1e9], ["s045", "s070", "s095", "s120", "s120p"])
    mid = bucket(float(f["midShareMean"]), [0.20, 0.35, 0.50, 0.65, 1e9], ["m020", "m035", "m050", "m065", "m065p"])
    high = bucket(float(f["highShareMean"]), [0.08, 0.16, 0.28, 0.42, 1e9], ["h008", "h016", "h028", "h042", "h042p"])
    agree = int(f["onsetAgreement"])
    return {
        f"onsetAttack::{attack}",
        f"onsetFlux::{flux}",
        f"onsetSustain::{sustain}",
        f"onsetMidShare::{mid}",
        f"onsetHighShare::{high}",
        f"onsetStemAgreement::a{agree}",
        f"onsetCross::{attack}|{flux}|a{agree}",
        f"onsetCross::{attack}|{sustain}|{mid}",
        f"onsetCross::{flux}|{mid}|{high}",
        f"onsetCross::{attack}|{flux}|{sustain}|a{agree}",
    }


def counts(rows: list[dict[str, Any]], sig: str) -> tuple[int, int]:
    t = f = 0
    for row in rows:
        if sig not in row["signatures"]:
            continue
        if row["label"] == "true":
            t += 1
        else:
            f += 1
    return t, f


def partition_summary(rows: list[dict[str, Any]], sig: str, fold_fn: Callable[[int], int]) -> dict[str, Any]:
    parts = []
    for fold in range(FOLD_COUNT):
        held = [r for r in rows if fold_fn(int(r["measure"])) == fold]
        t, f = counts(held, sig)
        parts.append({"fold": fold, "true": t, "false": f, "support": t + f, "precision": round(precision(t, f), 2)})
    supported = [p for p in parts if p["support"] > 0]
    useful = [p for p in supported if p["true"] > 0 and p["precision"] >= 35.0]
    return {
        "supportedFolds": len(supported),
        "usefulFolds": len(useful),
        "minSupportedPrecision": round(min((p["precision"] for p in supported), default=0.0), 2),
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
    winner_audio = np.asarray(winner_audio)
    alt_audio = np.asarray(alt_audio)

    # Collapse pitch hypotheses to unique rhythmic slots before measuring audio.
    slot_sources: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in raw_rows:
        slot_sources[(int(row["measure"]), int(row["step"]))].append(row)

    # Detection-side slot measurements are completed before any labels are read.
    measured: list[dict[str, Any]] = []
    for idx, ((measure, step), source_rows) in enumerate(sorted(slot_sources.items())):
        t = float(grid.get((measure, step), 0.0))
        a = stem_slot_features(winner_audio, int(winner_sr), t)
        b = stem_slot_features(alt_audio, int(alt_sr), t)
        features = {
            "attackMean": (a["attackRatio"] + b["attackRatio"]) / 2.0,
            "fluxMean": (a["spectralFlux"] + b["spectralFlux"]) / 2.0,
            "sustainMean": (a["sustainRatio"] + b["sustainRatio"]) / 2.0,
            "midShareMean": (a["midShare"] + b["midShare"]) / 2.0,
            "highShareMean": (a["highShare"] + b["highShare"]) / 2.0,
            "onsetAgreement": int(a["attackRatio"] >= 1.10 and b["attackRatio"] >= 1.10 and a["spectralFlux"] >= 0.12 and b["spectralFlux"] >= 0.12),
        }
        measured.append({
            "measure": measure,
            "step": step,
            "candidatePitchCount": len(source_rows),
            "features": features,
            "signatures": sorted(signatures_for(features)),
        })
        if idx and idx % 500 == 0:
            print(f"measured {idx}/{len(slot_sources)} residual slots ...", flush=True)

    # Only now attach downstream grading labels. A slot is true if any residual pitch at that slot is true.
    rows: list[dict[str, Any]] = []
    measured_map = {(int(r["measure"]), int(r["step"])): r for r in measured}
    for slot, source_rows in slot_sources.items():
        measured_row = measured_map[slot]
        slot_true = any(str(r.get("label")) == "true" for r in source_rows)
        true_pitch_count = sum(str(r.get("label")) == "true" for r in source_rows)
        rows.append({
            **measured_row,
            "label": "true" if slot_true else "false",
            "truePitchCount": true_pitch_count,
        })

    residual_true = sum(r["label"] == "true" for r in rows)
    residual_false = len(rows) - residual_true
    base_precision = precision(residual_true, residual_false)
    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    normal_fn = lambda m: m % FOLD_COUNT
    section_fn = lambda m: contiguous_fold(m, lo, hi)
    shifted_fn = lambda m: shifted_fold(m, lo, hi)

    signature_set = sorted({sig for row in rows for sig in row["signatures"]})
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
            "support": t + f,
            "precision": round(p, 2),
            "liftVsSlotBasePctPoints": round(p - base_precision, 2),
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
        raise RuntimeError("Protected candidate changed during onset-slot profiling")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-onset-slot-stability-diagnostic",
        "frozenChampionPitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "sourceResidualPitchRows": len(raw_rows),
        "residualSlots": len(rows),
        "trueResidualSlots": residual_true,
        "falseResidualSlots": residual_false,
        "slotBasePrecision": round(base_precision, 2),
        "stableDiagnosticSignatureCount": len(stable),
        "stableSignatures": stable,
        "rankedSignatures": ranked,
        "candidateSlots": rows,
        "note": "Diagnostic only. Residual pitch hypotheses are collapsed to unique rhythmic slots before audio measurement. Professional-reference-derived labels are attached only after slot measurements are frozen. Stable onset signatures require later nested validation before use as a pitch-recovery gate.",
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

    print("GOMYWAY 36.76 ONSET SLOT STABILITY V1 COMPLETE")
    print("Source residual pitch rows:", len(raw_rows))
    print("Residual rhythmic slots:", len(rows))
    print("True / false residual slots:", residual_true, "/", residual_false)
    print("Slot base precision:", round(base_precision, 2))
    print("Stable diagnostic onset signatures:", len(stable))
    for item in stable[:25]:
        print("STABLE", {
            "signature": item["signature"],
            "true": item["true"],
            "false": item["false"],
            "precision": item["precision"],
            "agreementSchemes": item["agreementSchemes"],
            "normal": item["normal"],
            "section": item["section"],
            "shiftedWindow": item["shiftedWindow"],
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
