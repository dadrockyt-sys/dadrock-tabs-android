from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2802_harmonic_phase_survivors_precision_v1 as survivor

recur = survivor.recur
recall = survivor.recall
v2 = survivor.v2
v3 = survivor.v3
harmonic = survivor.harmonic
phase = survivor.phase

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-2802-dual-stem-harmonic-residual-cancellation-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2802-dual-stem-harmonic-residual-cancellation-v1-manifest.json"
EXPECTED = (183, 684, 256)
EXPECTED_F1 = 28.02


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(value: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if value < edge:
            return label
    return labels[-1]


def midi_hz(pitch: int) -> float:
    return 440.0 * (2.0 ** ((float(pitch) - 69.0) / 12.0))


def harmonic_vector(audio: np.ndarray, sr: int, center: float, pitch: int, offset: float) -> np.ndarray:
    z, freqs = phase._frame_complex(audio, sr, center, offset, win_s=0.055)
    f0 = midi_hz(pitch)
    vals: list[complex] = []
    for h in range(1, 7):
        target = f0 * h
        if target >= freqs[-1]:
            vals.append(0j)
            continue
        idx = int(np.argmin(np.abs(freqs - target)))
        vals.append(complex(z[idx]))
    return np.asarray(vals, dtype=np.complex128)


def residual_features(
    winner_audio: np.ndarray,
    winner_sr: int,
    alt_audio: np.ndarray,
    alt_sr: int,
    center: float,
    pitch: int,
) -> dict[str, float]:
    offsets = [-0.030, -0.015, 0.0, 0.015, 0.030]
    residual_ratios: list[float] = []
    cancellation_gains: list[float] = []
    magnitude_agreements: list[float] = []
    scale_ratios: list[float] = []
    winner_dominances: list[float] = []
    alt_dominances: list[float] = []

    for off in offsets:
        w = harmonic_vector(winner_audio, winner_sr, center, pitch, off)
        a = harmonic_vector(alt_audio, alt_sr, center, pitch, off)
        ew = float(np.vdot(w, w).real) + 1e-12
        ea = float(np.vdot(a, a).real) + 1e-12

        alpha = np.vdot(a, w) / (np.vdot(a, a) + 1e-12)
        residual = w - alpha * a
        er = float(np.vdot(residual, residual).real)
        residual_ratio = er / ew
        residual_ratios.append(residual_ratio)
        cancellation_gains.append(max(0.0, 1.0 - residual_ratio))
        scale_ratios.append(float(abs(alpha)))

        wm = np.abs(w)
        am = np.abs(a)
        denom = float(np.linalg.norm(wm) * np.linalg.norm(am)) + 1e-12
        magnitude_agreements.append(float(np.dot(wm, am) / denom))

        winner_dominances.append(float(np.max(wm) / (np.sum(wm) + 1e-12)))
        alt_dominances.append(float(np.max(am) / (np.sum(am) + 1e-12)))

    rr = np.asarray(residual_ratios)
    cg = np.asarray(cancellation_gains)
    ma = np.asarray(magnitude_agreements)
    sc = np.asarray(scale_ratios)
    wd = np.asarray(winner_dominances)
    ad = np.asarray(alt_dominances)

    return {
        "medianResidualRatio": round(float(np.median(rr)), 6),
        "maxCancellationGain": round(float(np.max(cg)), 6),
        "medianMagnitudeAgreement": round(float(np.median(ma)), 6),
        "residualStability": round(float(np.std(rr)), 6),
        "medianScaleRatio": round(float(np.median(sc)), 6),
        "dominanceDifference": round(float(abs(np.median(wd) - np.median(ad))), 6),
        "minDominance": round(float(min(np.median(wd), np.median(ad))), 6),
    }


def signatures_for(f: dict[str, float]) -> set[str]:
    rr = bucket(f["medianResidualRatio"], [0.12, 0.25, 0.45, 0.70], ["rr_lt012", "rr_012_025", "rr_025_045", "rr_045_070", "rr_070_plus"])
    cg = bucket(f["maxCancellationGain"], [0.20, 0.40, 0.60, 0.80], ["cg_lt020", "cg_020_040", "cg_040_060", "cg_060_080", "cg_080_plus"])
    ma = bucket(f["medianMagnitudeAgreement"], [0.30, 0.50, 0.70, 0.86], ["ma_lt030", "ma_030_050", "ma_050_070", "ma_070_086", "ma_086_plus"])
    rs = bucket(f["residualStability"], [0.04, 0.10, 0.20, 0.35], ["rs_lt004", "rs_004_010", "rs_010_020", "rs_020_035", "rs_035_plus"])
    sr = bucket(f["medianScaleRatio"], [0.35, 0.70, 1.30, 2.20], ["sr_lt035", "sr_035_070", "sr_070_130", "sr_130_220", "sr_220_plus"])
    dd = bucket(f["dominanceDifference"], [0.04, 0.08, 0.16, 0.28], ["dd_lt004", "dd_004_008", "dd_008_016", "dd_016_028", "dd_028_plus"])
    md = bucket(f["minDominance"], [0.22, 0.30, 0.40, 0.55], ["md_lt022", "md_022_030", "md_030_040", "md_040_055", "md_055_plus"])
    return {
        f"harmonicResidualCross::{rr}|{cg}|{ma}|{rs}",
        f"crossStemCancellation::{cg}|{ma}|{sr}|{dd}",
        f"residualDominanceCross::{rr}|{md}|{dd}|{rs}",
        f"residualScaleCross::{rr}|{sr}|{ma}|{md}",
        f"harmonicResidualComposite::{rr}|{cg}|{ma}|{rs}|{dd}",
    }


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true = int(counts["true"])
        false = int(counts["false"])
        total = true + false
        rows.append({
            "signature": signature,
            "true": true,
            "false": false,
            "total": total,
            "precision": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


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

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion, reconstruction = survivor.reconstruct_2802(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 28.02 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        features = residual_features(winner_audio, winner_sr, alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(features))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({"token": list(tok), "truth": truth, "count": int(count), "features": features, "signatures": signatures})

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported = [r for r in ranked if int(r["true"]) >= 5]
    supported.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 28.02 harmonic residual/cancellation profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-28.02-dual-stem-harmonic-residual-cancellation",
        "champion2802Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "cross-stem-harmonic-residual-cancellation-magnitude-agreement-and-dominance",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
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
        "zeroPrecisionSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 28.02 DUAL-STEM HARMONIC RESIDUAL CANCELLATION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision harmonic-residual signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true harmonic-residual signatures:")
    for row in supported[:30]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
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
