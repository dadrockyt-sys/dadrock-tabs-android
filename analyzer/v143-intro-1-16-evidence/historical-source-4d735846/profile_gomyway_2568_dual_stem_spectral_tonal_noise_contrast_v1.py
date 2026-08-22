from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2568_periodicity_survivors_precision_v1 as p2568

period = p2568.period
p2552 = p2568.p2552
recur = p2568.recur
recall = p2568.recall
v2 = p2568.v2
v3 = p2568.v3
harmonic = p2568.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TEMPLATE_PROFILE_PATH = PUBLIC / "gomyway-2476-dual-stem-harmonic-template-competition-v1.json"
PERIOD_PROFILE_PATH = PUBLIC / "gomyway-2552-dual-stem-periodicity-phase-coherence-v1.json"
EXHAUSTED_PERIOD_PATH = PUBLIC / "gomyway-2568-periodicity-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2568-dual-stem-spectral-tonal-noise-contrast-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2568-dual-stem-spectral-tonal-noise-contrast-v1-manifest.json"

EXPECTED_2552 = (183, 684, 384)
EXPECTED_2552_F1 = 25.52
EXPECTED_2568 = (183, 684, 375)
EXPECTED_2568_F1 = 25.68
EXPECTED_TEMPLATE_ZERO_SIGNATURES = 11
EXPECTED_PERIOD_ZERO_SIGNATURES = 1
EXPECTED_PERIOD_PRUNE_COUNT = 9


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


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


def reconstruct_2568(
    grid: dict[tuple[int, int], float],
    winner_audio: np.ndarray,
    winner_sr: int,
    alt_audio: np.ndarray,
    alt_sr: int,
    reference: Counter[tuple[int, int, int]],
) -> tuple[Counter[tuple[int, int, int]], Counter[tuple[int, int, int]]]:
    template_profile = v2.load_json(TEMPLATE_PROFILE_PATH)
    template_zero = list(template_profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(template_zero) != EXPECTED_TEMPLATE_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected {EXPECTED_TEMPLATE_ZERO_SIGNATURES} harmonic-template signatures, got {len(template_zero)}"
        )
    template_signatures = {str(row["signature"]) for row in template_zero}

    champion2552, prior_pruned = p2552.reconstruct_2552(
        grid,
        winner_audio,
        winner_sr,
        alt_audio,
        alt_sr,
        template_signatures,
    )
    if int(sum(prior_pruned.values())) != p2552.EXPECTED_PRUNE_COUNT:
        raise RuntimeError(
            f"Expected frozen 25.52 prune count {p2552.EXPECTED_PRUNE_COUNT}, got {sum(prior_pruned.values())}"
        )

    score2552 = recur.grade(champion2552, reference)
    actual2552 = (int(score2552["matched"]), int(score2552["missing"]), int(score2552["extra"]))
    if actual2552 != EXPECTED_2552 or abs(float(score2552["pitchF1"]) - EXPECTED_2552_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 25.52 champion {EXPECTED_2552}/{EXPECTED_2552_F1}, got {actual2552}/{score2552['pitchF1']}"
        )

    period_profile = v2.load_json(PERIOD_PROFILE_PATH)
    if period_profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("25.52 periodicity profile is not reference-free during detection")
    period_zero = list(period_profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(period_zero) != EXPECTED_PERIOD_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected {EXPECTED_PERIOD_ZERO_SIGNATURES} periodicity zero-precision signature, got {len(period_zero)}"
        )
    target_signature = str(period_zero[0]["signature"])
    period_rows = list(period_profile.get("rows", []))
    row_by_token = {token(row): row for row in period_rows}

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion2552.items():
        row = row_by_token.get(tok)
        if row is not None and target_signature in {str(s) for s in row.get("signatures", [])}:
            pruned[tok] = count

    if int(sum(pruned.values())) != EXPECTED_PERIOD_PRUNE_COUNT:
        raise RuntimeError(
            f"Expected frozen periodicity prune count {EXPECTED_PERIOD_PRUNE_COUNT}, got {sum(pruned.values())}"
        )
    if int(sum((pruned & reference).values())) != 0:
        raise RuntimeError("Frozen periodicity prune unexpectedly removes reference matches")

    champion2568 = champion2552 - pruned
    score2568 = recur.grade(champion2568, reference)
    actual2568 = (int(score2568["matched"]), int(score2568["missing"]), int(score2568["extra"]))
    if actual2568 != EXPECTED_2568 or abs(float(score2568["pitchF1"]) - EXPECTED_2568_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 25.68 champion {EXPECTED_2568}/{EXPECTED_2568_F1}, got {actual2568}/{score2568['pitchF1']}"
        )
    return champion2568, pruned


def spectral_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, float]:
    values = np.asarray(harmonic.segment(audio, sample_rate, center), dtype=np.float64)
    if values.size < 512:
        return {
            "flatness": 1.0,
            "crest": 1.0,
            "harmonicFraction": 0.0,
            "noiseToHarmonic": 99.0,
            "interHarmonicFraction": 1.0,
            "highResidualFraction": 1.0,
        }

    values = values - float(np.mean(values))
    window = np.hanning(values.size)
    spectrum = np.abs(np.fft.rfft(values * window)) ** 2
    freqs = np.fft.rfftfreq(values.size, d=1.0 / float(sample_rate))

    band = (freqs >= 70.0) & (freqs <= min(6000.0, sample_rate * 0.48))
    power = spectrum[band]
    band_freqs = freqs[band]
    total = float(np.sum(power)) + 1e-12
    if power.size < 8 or total <= 1e-10:
        return {
            "flatness": 1.0,
            "crest": 1.0,
            "harmonicFraction": 0.0,
            "noiseToHarmonic": 99.0,
            "interHarmonicFraction": 1.0,
            "highResidualFraction": 1.0,
        }

    mean_power = float(np.mean(power)) + 1e-15
    geom_power = float(np.exp(np.mean(np.log(power + 1e-15))))
    flatness = geom_power / mean_power
    crest = float(np.max(power)) / mean_power

    f0 = harmonic.midi_hz(midi)
    harmonic_mask = np.zeros_like(power, dtype=bool)
    for harmonic_index in range(1, 9):
        freq = f0 * harmonic_index
        if freq > band_freqs[-1]:
            break
        width = max(8.0, freq * 0.018)
        harmonic_mask |= np.abs(band_freqs - freq) <= width

    harmonic_energy = float(np.sum(power[harmonic_mask]))
    residual_energy = max(0.0, total - harmonic_energy)
    harmonic_fraction = harmonic_energy / total
    noise_to_harmonic = residual_energy / max(harmonic_energy, 1e-12)

    inter_mask = (~harmonic_mask) & (band_freqs >= max(90.0, f0 * 0.75)) & (band_freqs <= min(5000.0, f0 * 8.5))
    inter_fraction = float(np.sum(power[inter_mask])) / total

    high_cut = max(1800.0, f0 * 6.0)
    high_mask = (~harmonic_mask) & (band_freqs >= high_cut)
    high_residual_fraction = float(np.sum(power[high_mask])) / total

    return {
        "flatness": float(flatness),
        "crest": float(crest),
        "harmonicFraction": float(harmonic_fraction),
        "noiseToHarmonic": float(noise_to_harmonic),
        "interHarmonicFraction": float(inter_fraction),
        "highResidualFraction": float(high_residual_fraction),
    }


def flatness_bucket(v: float) -> str:
    if v < 0.015:
        return "flat_lt015"
    if v < 0.035:
        return "flat_015_035"
    if v < 0.070:
        return "flat_035_070"
    if v < 0.140:
        return "flat_070_140"
    return "flat_140_plus"


def crest_bucket(v: float) -> str:
    if v < 8.0:
        return "crest_lt8"
    if v < 16.0:
        return "crest_8_16"
    if v < 30.0:
        return "crest_16_30"
    if v < 55.0:
        return "crest_30_55"
    return "crest_55_plus"


def harmonic_fraction_bucket(v: float) -> str:
    if v < 0.08:
        return "harm_lt008"
    if v < 0.16:
        return "harm_008_016"
    if v < 0.28:
        return "harm_016_028"
    if v < 0.45:
        return "harm_028_045"
    return "harm_045_plus"


def noise_ratio_bucket(v: float) -> str:
    if v < 1.0:
        return "noise_lt1"
    if v < 2.5:
        return "noise_1_25"
    if v < 5.0:
        return "noise_25_50"
    if v < 10.0:
        return "noise_50_100"
    return "noise_100_plus"


def residual_bucket(v: float) -> str:
    if v < 0.20:
        return "resid_lt020"
    if v < 0.35:
        return "resid_020_035"
    if v < 0.50:
        return "resid_035_050"
    if v < 0.70:
        return "resid_050_070"
    return "resid_070_plus"


def diff_bucket(v: float) -> str:
    if v < 0.015:
        return "diff_lt015"
    if v < 0.040:
        return "diff_015_040"
    if v < 0.090:
        return "diff_040_090"
    if v < 0.180:
        return "diff_090_180"
    return "diff_180_plus"


def signatures_for(wf: dict[str, float], af: dict[str, float]) -> set[str]:
    max_flat = max(wf["flatness"], af["flatness"])
    min_crest = min(wf["crest"], af["crest"])
    min_harm = min(wf["harmonicFraction"], af["harmonicFraction"])
    max_noise = max(wf["noiseToHarmonic"], af["noiseToHarmonic"])
    max_inter = max(wf["interHarmonicFraction"], af["interHarmonicFraction"])
    max_high = max(wf["highResidualFraction"], af["highResidualFraction"])
    flat_diff = abs(wf["flatness"] - af["flatness"])
    harm_diff = abs(wf["harmonicFraction"] - af["harmonicFraction"])

    flat = flatness_bucket(max_flat)
    crest = crest_bucket(min_crest)
    harm = harmonic_fraction_bucket(min_harm)
    noise = noise_ratio_bucket(max_noise)
    inter = residual_bucket(max_inter)
    high = residual_bucket(max_high)
    fdiff = diff_bucket(flat_diff)
    hdiff = diff_bucket(harm_diff)

    return {
        f"maxSpectralFlatness::{flat}",
        f"minSpectralCrest::{crest}",
        f"minHarmonicFraction::{harm}",
        f"maxNoiseToHarmonic::{noise}",
        f"maxInterHarmonicResidual::{inter}",
        f"maxHighResidual::{high}",
        f"spectralFlatnessAgreement::{fdiff}",
        f"harmonicFractionAgreement::{hdiff}",
        f"tonalNoiseCross::{flat}|{crest}|{harm}|{noise}",
        f"residualNoiseCross::{harm}|{inter}|{high}|{hdiff}",
        f"dualStemTonalCross::{flat}|{harm}|{noise}|{fdiff}|{hdiff}",
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

    exhausted = v2.load_json(EXHAUSTED_PERIOD_PATH)
    if exhausted.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("25.68 periodicity survivor profile is not reference-free during detection")
    if exhausted.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("25.68 periodicity branch is not exhausted")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion2568, period_pruned = reconstruct_2568(
        grid,
        winner_audio,
        winner_sr,
        alt_audio,
        alt_sr,
        reference,
    )

    score = recur.grade(champion2568, reference)
    matched = champion2568 & reference
    extras = champion2568 - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = spectral_features(winner_audio, winner_sr, center, pitch)
        af = spectral_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "maxFlatness": max(wf["flatness"], af["flatness"]),
            "minCrest": min(wf["crest"], af["crest"]),
            "minHarmonicFraction": min(wf["harmonicFraction"], af["harmonicFraction"]),
            "maxNoiseToHarmonic": max(wf["noiseToHarmonic"], af["noiseToHarmonic"]),
            "signatures": signatures,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero_precision = [row for row in ranked if int(row["true"]) == 0 and int(row["false"]) >= 5]
    zero_precision.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported_true = [row for row in ranked if int(row["true"]) >= 5]
    supported_true.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 25.68 spectral tonal-noise profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-25.68-dual-stem-spectral-tonal-noise-contrast",
        "champion2568Score": score,
        "featureFamily": "dual-stem-spectral-tonal-noise-contrast",
        "validatedPeriodicityPruneCount": int(sum(period_pruned.values())),
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
        "zeroPrecisionSignatureCount": len(zero_precision),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 25.68 DUAL-STEM SPECTRAL TONAL-NOISE CONTRAST V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Applied frozen periodicity prune count:", int(sum(period_pruned.values())))
    print("Generalizable zero-precision spectral tonal-noise signatures (5+ false, 0 true):", len(zero_precision))
    for row in zero_precision[:50]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
    print("Supported true/mixed spectral tonal-noise signatures:")
    for row in supported_true[:30]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
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
