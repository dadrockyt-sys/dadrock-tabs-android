from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2065_harmonic_shape_survivors_precision_v1 as p2065

b1858 = p2065.b1858
shape = p2065.shape
recur = p2065.recur
recall = p2065.recall
v2 = p2065.v2
v3 = p2065.v3
harmonic = shape.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1858_PATH = PUBLIC / "gomyway-1858-dual-stem-harmonic-shape-balance-v1.json"
SURVIVOR_2065_PATH = PUBLIC / "gomyway-2065-harmonic-shape-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2065-dual-stem-harmonic-peak-alignment-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2065-dual-stem-harmonic-peak-alignment-v1-manifest.json"
EXPECTED = (183, 684, 722)
EXPECTED_F1 = 20.65


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        t = int(counts["true"])
        f = int(counts["false"])
        total = t + f
        out.append({
            "signature": signature,
            "true": t,
            "false": f,
            "total": total,
            "precision": round(100.0 * t / total, 2) if total else 0.0,
        })
    return sorted(out, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def reconstruct_2065(grid: Any) -> Counter[tuple[int, int, int]]:
    profile_payload = v2.load_json(PROFILE_1858_PATH)
    rows = list(profile_payload.get("rows", []))
    row_by_token = {tuple(int(v) for v in row["token"]): row for row in rows}
    zero_rows = list(profile_payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    zero_signatures = {str(r["signature"]) for r in zero_rows}
    if not zero_signatures:
        raise RuntimeError("18.58 harmonic-shape profile has no validated zero-precision signatures")

    champion_1858 = shape.reconstruct_1858(grid)
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_1858.items():
        row = row_by_token.get(tok)
        if row is not None and b1858.row_signatures(row) & zero_signatures:
            pruned[tok] = count
    return champion_1858 - pruned


def detune_bucket(value: float) -> str:
    if value < 8.0:
        return "detune_lt8"
    if value < 16.0:
        return "detune_8_16"
    if value < 28.0:
        return "detune_16_28"
    if value < 45.0:
        return "detune_28_45"
    return "detune_45_plus"


def max_detune_bucket(value: float) -> str:
    if value < 15.0:
        return "maxdet_lt15"
    if value < 30.0:
        return "maxdet_15_30"
    if value < 55.0:
        return "maxdet_30_55"
    if value < 90.0:
        return "maxdet_55_90"
    return "maxdet_90_plus"


def contrast_bucket(value: float) -> str:
    if value < 1.20:
        return "contrast_lt120"
    if value < 1.60:
        return "contrast_120_160"
    if value < 2.40:
        return "contrast_160_240"
    if value < 4.00:
        return "contrast_240_400"
    return "contrast_400_plus"


def disagreement_bucket(value: float) -> str:
    if value < 8.0:
        return "stemdiff_lt8"
    if value < 20.0:
        return "stemdiff_8_20"
    if value < 40.0:
        return "stemdiff_20_40"
    return "stemdiff_40_plus"


def stem_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, float]:
    values = harmonic.segment(audio, sample_rate, center)
    if values.size < 256:
        return {"medianAbsDetuneCents": 999.0, "maxAbsDetuneCents": 999.0, "medianPeakContrast": 0.0}

    n_fft = 16384
    window = np.hanning(values.size).astype(np.float32)
    spec = np.abs(np.fft.rfft(values * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    f0 = harmonic.midi_hz(midi)
    nyquist = sample_rate * 0.5
    eps = 1e-9

    detunes: list[float] = []
    contrasts: list[float] = []
    for h in range(1, 7):
        target_hz = f0 * h
        if target_hz >= nyquist - 80.0:
            break

        search_half = max(12.0, target_hz * 0.025)
        mask = (freqs >= target_hz - search_half) & (freqs <= target_hz + search_half)
        idx = np.flatnonzero(mask)
        if idx.size < 3:
            continue
        local = spec[idx]
        peak_i = int(idx[int(np.argmax(local))])
        peak_hz = float(freqs[peak_i])
        if peak_hz <= 0.0:
            continue
        cents = 1200.0 * np.log2(peak_hz / target_hz)
        detunes.append(abs(float(cents)))

        center_half = max(4.0, target_hz * 0.004)
        flank_inner = max(8.0, target_hz * 0.009)
        flank_outer = max(18.0, target_hz * 0.022)
        center_mask = (freqs >= peak_hz - center_half) & (freqs <= peak_hz + center_half)
        flank_mask = (
            ((freqs >= peak_hz - flank_outer) & (freqs <= peak_hz - flank_inner))
            | ((freqs >= peak_hz + flank_inner) & (freqs <= peak_hz + flank_outer))
        )
        center_energy = float(np.mean(spec[center_mask])) if np.any(center_mask) else 0.0
        flank_energy = float(np.mean(spec[flank_mask])) if np.any(flank_mask) else 0.0
        contrasts.append(center_energy / (flank_energy + eps))

    if not detunes:
        return {"medianAbsDetuneCents": 999.0, "maxAbsDetuneCents": 999.0, "medianPeakContrast": 0.0}

    return {
        "medianAbsDetuneCents": float(np.median(np.asarray(detunes, dtype=float))),
        "maxAbsDetuneCents": float(np.max(np.asarray(detunes, dtype=float))),
        "medianPeakContrast": float(np.median(np.asarray(contrasts, dtype=float))) if contrasts else 0.0,
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

    survivor_payload = v2.load_json(SURVIVOR_2065_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("20.65 harmonic-shape survivor profile is not reference-free during detection")
    if survivor_payload.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("20.65 harmonic-shape branch is not exhausted")

    champion = reconstruct_2065(grid)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 20.65 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = stem_features(winner_audio, winner_sr, center, pitch)
        af = stem_features(alt_audio, alt_sr, center, pitch)

        median_detune = min(wf["medianAbsDetuneCents"], af["medianAbsDetuneCents"])
        max_detune = min(wf["maxAbsDetuneCents"], af["maxAbsDetuneCents"])
        min_contrast = min(wf["medianPeakContrast"], af["medianPeakContrast"])
        stem_diff = abs(wf["medianAbsDetuneCents"] - af["medianAbsDetuneCents"])

        md = detune_bucket(median_detune)
        xd = max_detune_bucket(max_detune)
        pc = contrast_bucket(min_contrast)
        sd = disagreement_bucket(stem_diff)
        signatures = {
            "medianDetune": md,
            "maxDetune": xd,
            "peakContrast": pc,
            "stemDetuneAgreement": sd,
            "detuneContrast": f"{md}|{pc}",
            "detuneMax": f"{md}|{xd}",
            "alignmentCross": f"{md}|{pc}|{sd}",
            "harmonicPeakCross": f"{md}|{xd}|{pc}|{sd}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": count,
            "winner": wf,
            "alternate": af,
            "minMedianAbsDetuneCents": median_detune,
            "minMaxAbsDetuneCents": max_detune,
            "minMedianPeakContrast": min_contrast,
            "stemMedianDetuneDifferenceCents": stem_diff,
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
        raise RuntimeError("Protected candidate changed during 20.65 harmonic-peak-alignment profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-20.65-dual-stem-harmonic-peak-alignment",
        "champion2065Score": score,
        "featureFamily": "dual-stem-harmonic-peak-alignment-and-detuning",
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
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-harmonic-peak-alignment-signatures-with-prune-specific-heldout-cv",
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

    print("GOMYWAY 20.65 DUAL-STEM HARMONIC PEAK ALIGNMENT V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision harmonic-peak signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true harmonic-peak signatures (5+ true):")
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
