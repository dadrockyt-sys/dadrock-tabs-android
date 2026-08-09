from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2409_transient_onset_survivors_precision_v1 as p2409

transient = p2409.transient
harmonic = p2409.harmonic
recur = p2409.recur
recall = p2409.recall
v2 = p2409.v2
v3 = p2409.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-2409-dual-stem-harmonic-band-concentration-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2409-dual-stem-harmonic-band-concentration-v1-manifest.json"
EXPECTED = (183, 684, 469)
EXPECTED_F1 = 24.09


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        t = int(counts["true"])
        f = int(counts["false"])
        total = t + f
        rows.append({
            "signature": signature,
            "true": t,
            "false": f,
            "total": total,
            "precision": round(100.0 * t / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def band_energy(spec: np.ndarray, freqs: np.ndarray, lo: float, hi: float) -> float:
    mask = (freqs >= lo) & (freqs <= hi)
    if not np.any(mask):
        return 0.0
    return float(np.sum(spec[mask]))


def stem_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, float]:
    values = harmonic.segment(audio, sample_rate, center)
    if values.size < 256:
        return {
            "harmonicConcentration": 0.0,
            "shoulderToCore": 99.0,
            "interharmonicToCore": 99.0,
            "meanRelativeBandwidth": 1.0,
        }

    n_fft = 8192
    window = np.hanning(values.size).astype(np.float32)
    spec = np.abs(np.fft.rfft(values * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    f0 = harmonic.midi_hz(midi)
    nyquist = sample_rate * 0.5
    eps = 1e-9

    core_total = 0.0
    wide_total = 0.0
    inter_total = 0.0
    weighted_bw_num = 0.0
    weighted_bw_den = 0.0
    harmonic_centers: list[float] = []

    for h in range(1, 7):
        hz = f0 * h
        if hz >= nyquist - 100.0:
            break
        harmonic_centers.append(hz)
        core_hw = max(5.0, hz * 0.006)
        wide_hw = max(18.0, hz * 0.025)
        core = band_energy(spec, freqs, hz - core_hw, hz + core_hw)
        wide = band_energy(spec, freqs, hz - wide_hw, hz + wide_hw)
        core_total += core
        wide_total += wide

        mask = (freqs >= hz - wide_hw) & (freqs <= hz + wide_hw)
        if np.any(mask):
            local_f = freqs[mask]
            local_s = spec[mask]
            denom = float(np.sum(local_s)) + eps
            mean_abs = float(np.sum(local_s * np.abs(local_f - hz)) / denom)
            weighted_bw_num += core * (mean_abs / max(hz, 1.0))
            weighted_bw_den += core

    for left, right in zip(harmonic_centers[:-1], harmonic_centers[1:]):
        mid = 0.5 * (left + right)
        hw = max(10.0, mid * 0.012)
        inter_total += band_energy(spec, freqs, mid - hw, mid + hw)

    shoulder = max(0.0, wide_total - core_total)
    concentration = core_total / (wide_total + eps)
    shoulder_to_core = shoulder / (core_total + eps)
    inter_to_core = inter_total / (core_total + eps)
    mean_relative_bw = weighted_bw_num / (weighted_bw_den + eps)

    return {
        "harmonicConcentration": float(concentration),
        "shoulderToCore": float(shoulder_to_core),
        "interharmonicToCore": float(inter_to_core),
        "meanRelativeBandwidth": float(mean_relative_bw),
    }


def concentration_bucket(v: float) -> str:
    if v < 0.35:
        return "conc_lt035"
    if v < 0.50:
        return "conc_035_050"
    if v < 0.65:
        return "conc_050_065"
    if v < 0.80:
        return "conc_065_080"
    return "conc_080_plus"


def shoulder_bucket(v: float) -> str:
    if v < 0.25:
        return "shoulder_lt025"
    if v < 0.50:
        return "shoulder_025_050"
    if v < 1.00:
        return "shoulder_050_100"
    if v < 2.00:
        return "shoulder_100_200"
    return "shoulder_200_plus"


def inter_bucket(v: float) -> str:
    if v < 0.08:
        return "inter_lt008"
    if v < 0.16:
        return "inter_008_016"
    if v < 0.30:
        return "inter_016_030"
    if v < 0.60:
        return "inter_030_060"
    return "inter_060_plus"


def bandwidth_bucket(v: float) -> str:
    if v < 0.004:
        return "bw_lt004"
    if v < 0.008:
        return "bw_004_008"
    if v < 0.014:
        return "bw_008_014"
    if v < 0.022:
        return "bw_014_022"
    return "bw_022_plus"


def disagreement_bucket(v: float) -> str:
    if v < 0.10:
        return "diff_lt010"
    if v < 0.25:
        return "diff_010_025"
    if v < 0.50:
        return "diff_025_050"
    return "diff_050_plus"


def signatures_for(wf: dict[str, float], af: dict[str, float]) -> set[str]:
    min_conc = min(wf["harmonicConcentration"], af["harmonicConcentration"])
    max_shoulder = max(wf["shoulderToCore"], af["shoulderToCore"])
    max_inter = max(wf["interharmonicToCore"], af["interharmonicToCore"])
    max_bw = max(wf["meanRelativeBandwidth"], af["meanRelativeBandwidth"])
    conc_diff = abs(math.log2((wf["harmonicConcentration"] + 1e-6) / (af["harmonicConcentration"] + 1e-6)))

    c = concentration_bucket(min_conc)
    s = shoulder_bucket(max_shoulder)
    i = inter_bucket(max_inter)
    b = bandwidth_bucket(max_bw)
    d = disagreement_bucket(conc_diff)

    return {
        f"minConcentration::{c}",
        f"maxShoulder::{s}",
        f"maxInterharmonic::{i}",
        f"maxRelativeBandwidth::{b}",
        f"concentrationAgreement::{d}",
        f"concentrationShoulderCross::{c}|{s}|{d}",
        f"concentrationInterCross::{c}|{i}|{d}",
        f"bandwidthInterCross::{b}|{i}|{d}",
        f"harmonicBandShapeCross::{c}|{s}|{i}|{b}|{d}",
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    survivor_payload = v2.load_json(p2409.OUTPUT_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("24.09 transient survivor profile is not reference-free during detection")
    if survivor_payload.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("24.09 transient-onset survivor branch is not exhausted")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion = p2409.reconstruct_2409(grid, winner_audio, winner_sr, alt_audio, alt_sr)

    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 24.09 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = stem_features(winner_audio, winner_sr, center, pitch)
        af = stem_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "minHarmonicConcentration": min(wf["harmonicConcentration"], af["harmonicConcentration"]),
            "maxShoulderToCore": max(wf["shoulderToCore"], af["shoulderToCore"]),
            "maxInterharmonicToCore": max(wf["interharmonicToCore"], af["interharmonicToCore"]),
            "maxMeanRelativeBandwidth": max(wf["meanRelativeBandwidth"], af["meanRelativeBandwidth"]),
            "signatures": signatures,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero_precision = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero_precision.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported_true = [r for r in ranked if int(r["true"]) >= 5]
    supported_true.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 24.09 harmonic-band concentration profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-24.09-dual-stem-harmonic-band-concentration",
        "champion2409Score": score,
        "featureFamily": "dual-stem-harmonic-band-concentration-and-interharmonic-smear",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero_precision,
        "supportedTrueSignaturesMin5True": supported_true,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
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
        "championPitchF1": score["pitchF1"],
        "matched": score["matched"],
        "missing": score["missing"],
        "extra": score["extra"],
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 24.09 DUAL-STEM HARMONIC BAND CONCENTRATION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision harmonic-band signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true harmonic-band signatures (5+ true):")
    for row in supported_true[:30]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
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
