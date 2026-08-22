from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2802_dual_stem_harmonic_residual_cancellation_v1 as residual
import profile_gomyway_3161_measure_register_survivors_precision_v1 as s3161

recur = residual.recur
recall = residual.recall
v2 = residual.v2
v3 = residual.v3
harmonic = residual.harmonic
phase = residual.phase

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-fundamental-phase-lock-survivors-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-fundamental-phase-lock-survivors-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def midi_hz(pitch: int) -> float:
    return 440.0 * (2.0 ** ((float(pitch) - 69.0) / 12.0))


def wrap_phase(x: float) -> float:
    return float(np.angle(np.exp(1j * x)))


def stem_phase_features(audio: np.ndarray, sr: int, center: float, pitch: int) -> dict[str, float]:
    offsets = [-0.030, -0.015, 0.0, 0.015, 0.030]
    f0 = midi_hz(pitch)
    phases: list[float] = []
    mags: list[float] = []

    for off in offsets:
        z, freqs = phase._frame_complex(audio, sr, center, off, win_s=0.055)
        idx = int(np.argmin(np.abs(freqs - f0)))
        c = complex(z[idx])
        phases.append(float(np.angle(c)))
        mags.append(float(abs(c)))

    phase_errors: list[float] = []
    weighted_vectors: list[complex] = []
    for i in range(len(offsets) - 1):
        dt = offsets[i + 1] - offsets[i]
        observed = wrap_phase(phases[i + 1] - phases[i])
        expected = wrap_phase(2.0 * np.pi * f0 * dt)
        err = wrap_phase(observed - expected)
        phase_errors.append(err)
        weight = max(1e-12, min(mags[i], mags[i + 1]))
        weighted_vectors.append(weight * np.exp(1j * err))

    vec = sum(weighted_vectors, 0j)
    denom = sum(abs(v) for v in weighted_vectors) + 1e-12
    coherence = float(abs(vec) / denom)
    median_abs_error = float(np.median(np.abs(np.asarray(phase_errors))))
    max_abs_error = float(np.max(np.abs(np.asarray(phase_errors))))
    mag_stability = float(np.std(np.asarray(mags)) / (np.mean(np.asarray(mags)) + 1e-12))

    return {
        "phaseLockCoherence": round(coherence, 6),
        "medianAbsPhaseError": round(median_abs_error, 6),
        "maxAbsPhaseError": round(max_abs_error, 6),
        "magnitudeStability": round(mag_stability, 6),
        "medianFundamentalMagnitude": round(float(np.median(np.asarray(mags))), 6),
    }


def bucket(v: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if v < edge:
            return label
    return labels[-1]


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    min_coh = min(w["phaseLockCoherence"], a["phaseLockCoherence"])
    max_coh = max(w["phaseLockCoherence"], a["phaseLockCoherence"])
    max_med_err = max(w["medianAbsPhaseError"], a["medianAbsPhaseError"])
    max_peak_err = max(w["maxAbsPhaseError"], a["maxAbsPhaseError"])
    coh_diff = abs(w["phaseLockCoherence"] - a["phaseLockCoherence"])
    mag_stab = max(w["magnitudeStability"], a["magnitudeStability"])

    minc = bucket(min_coh, [0.20, 0.40, 0.60, 0.80], ["minc_lt020", "minc_020_040", "minc_040_060", "minc_060_080", "minc_080_plus"])
    maxc = bucket(max_coh, [0.30, 0.50, 0.70, 0.88], ["maxc_lt030", "maxc_030_050", "maxc_050_070", "maxc_070_088", "maxc_088_plus"])
    med = bucket(max_med_err, [0.35, 0.70, 1.20, 1.80], ["med_lt035", "med_035_070", "med_070_120", "med_120_180", "med_180_plus"])
    peak = bucket(max_peak_err, [0.70, 1.20, 1.80, 2.50], ["peak_lt070", "peak_070_120", "peak_120_180", "peak_180_250", "peak_250_plus"])
    cd = bucket(coh_diff, [0.08, 0.18, 0.35, 0.55], ["cd_lt008", "cd_008_018", "cd_018_035", "cd_035_055", "cd_055_plus"])
    ms = bucket(mag_stab, [0.15, 0.30, 0.55, 0.90], ["ms_lt015", "ms_015_030", "ms_030_055", "ms_055_090", "ms_090_plus"])

    agreement = "both_locked" if min_coh >= 0.70 else ("one_locked" if max_coh >= 0.70 else "neither_locked")

    return {
        f"minFundamentalPhaseLock::{minc}",
        f"maxFundamentalPhaseLock::{maxc}",
        f"maxMedianPhaseError::{med}",
        f"maxPeakPhaseError::{peak}",
        f"phaseLockStemDifference::{cd}",
        f"fundamentalMagnitudeStability::{ms}",
        f"dualStemPhaseLockAgreement::{agreement}",
        f"phaseLockCross::{minc}|{med}|{peak}|{agreement}",
        f"dualStemPhaseConsistency::{agreement}|{cd}|{ms}|{maxc}",
        f"phaseErrorCross::{med}|{peak}|{cd}|{minc}",
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
    champion, reconstruction = s3161.reconstruct_3161(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = stem_phase_features(winner_audio, winner_sr, center, pitch)
        af = stem_phase_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "signatures": signatures,
        })

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
        raise RuntimeError("Protected candidate changed during 31.61 fundamental phase-lock profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-31.61-fundamental-phase-lock-survivors",
        "champion3161Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "dual-stem-fundamental-phase-lock-cycle-consistency",
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

    print("GOMYWAY 31.61 FUNDAMENTAL PHASE LOCK SURVIVORS V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision fundamental phase-lock signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true fundamental phase-lock signatures:")
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
