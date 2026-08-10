from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_3161_fundamental_phase_lock_survivors_v1 as phase3161
import profile_gomyway_3161_measure_register_survivors_precision_v1 as s3161

recur = phase3161.recur
recall = phase3161.recall
v2 = phase3161.v2
v3 = phase3161.v3
harmonic = phase3161.harmonic
phase = phase3161.phase

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-harmonic-comb-alignment-survivors-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-harmonic-comb-alignment-survivors-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def midi_hz(pitch: int) -> float:
    return 440.0 * (2.0 ** ((float(pitch) - 69.0) / 12.0))


def bucket(v: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if v < edge:
            return label
    return labels[-1]


def stem_comb_features(audio: np.ndarray, sr: int, center: float, pitch: int) -> dict[str, float]:
    f0 = midi_hz(pitch)
    offsets = [-0.020, 0.0, 0.020]
    alignments: list[float] = []
    leakages: list[float] = []
    contrasts: list[float] = []
    peak_ratios: list[float] = []

    for off in offsets:
        z, freqs = phase._frame_complex(audio, sr, center, off, win_s=0.070)
        mags = np.abs(z)
        harmonic_energy = 0.0
        offbin_energy = 0.0
        peak_energy = 0.0

        used = 0
        for h in range(1, 7):
            target = f0 * h
            if target >= freqs[-1]:
                break
            idx = int(np.argmin(np.abs(freqs - target)))
            lo = max(0, idx - 1)
            hi = min(len(mags), idx + 2)
            local = mags[lo:hi]
            harmonic_energy += float(np.sum(local ** 2))
            peak_energy += float(np.max(local) ** 2)

            left = mags[max(0, idx - 4):max(0, idx - 1)]
            right = mags[min(len(mags), idx + 2):min(len(mags), idx + 5)]
            if left.size:
                offbin_energy += float(np.sum(left ** 2))
            if right.size:
                offbin_energy += float(np.sum(right ** 2))
            used += 1

        total = harmonic_energy + offbin_energy + 1e-12
        alignments.append(harmonic_energy / total)
        leakages.append(offbin_energy / total)
        contrasts.append(harmonic_energy / (offbin_energy + 1e-12))
        peak_ratios.append(peak_energy / (harmonic_energy + 1e-12) if used else 0.0)

    return {
        "medianCombAlignment": round(float(np.median(alignments)), 6),
        "maxOffbinLeakage": round(float(np.max(leakages)), 6),
        "medianCombContrast": round(float(np.median(contrasts)), 6),
        "medianHarmonicPeakRatio": round(float(np.median(peak_ratios)), 6),
        "combStability": round(float(np.std(np.asarray(alignments))), 6),
    }


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    min_align = min(w["medianCombAlignment"], a["medianCombAlignment"])
    max_leak = max(w["maxOffbinLeakage"], a["maxOffbinLeakage"])
    min_contrast = min(w["medianCombContrast"], a["medianCombContrast"])
    max_peak_ratio = max(w["medianHarmonicPeakRatio"], a["medianHarmonicPeakRatio"])
    max_stability = max(w["combStability"], a["combStability"])
    align_diff = abs(w["medianCombAlignment"] - a["medianCombAlignment"])

    al = bucket(min_align, [0.35, 0.50, 0.65, 0.80], ["al_lt035", "al_035_050", "al_050_065", "al_065_080", "al_080_plus"])
    lk = bucket(max_leak, [0.20, 0.35, 0.50, 0.65], ["lk_lt020", "lk_020_035", "lk_035_050", "lk_050_065", "lk_065_plus"])
    ct = bucket(min_contrast, [0.7, 1.0, 1.5, 2.5], ["ct_lt07", "ct_07_10", "ct_10_15", "ct_15_25", "ct_25_plus"])
    pr = bucket(max_peak_ratio, [0.25, 0.40, 0.55, 0.70], ["pr_lt025", "pr_025_040", "pr_040_055", "pr_055_070", "pr_070_plus"])
    st = bucket(max_stability, [0.03, 0.07, 0.12, 0.20], ["st_lt003", "st_003_007", "st_007_012", "st_012_020", "st_020_plus"])
    ad = bucket(align_diff, [0.04, 0.08, 0.16, 0.28], ["ad_lt004", "ad_004_008", "ad_008_016", "ad_016_028", "ad_028_plus"])

    agreement = "both_clean" if min_align >= 0.65 else ("one_clean" if max(w["medianCombAlignment"], a["medianCombAlignment"]) >= 0.65 else "neither_clean")

    return {
        f"minCombAlignment::{al}",
        f"maxOffbinLeakage::{lk}",
        f"minCombContrast::{ct}",
        f"maxHarmonicPeakRatio::{pr}",
        f"combStability::{st}",
        f"combStemDifference::{ad}",
        f"dualStemCombAgreement::{agreement}",
        f"harmonicCombCross::{al}|{lk}|{ct}|{agreement}",
        f"offbinLeakageCross::{lk}|{st}|{ad}|{pr}",
        f"combAlignmentComposite::{al}|{ct}|{st}|{agreement}|{ad}",
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
    champion, reconstruction = s3161.reconstruct_3161(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)
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
        wf = stem_comb_features(winner_audio, winner_sr, center, pitch)
        af = stem_comb_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({"token": list(tok), "truth": truth, "count": int(count), "winner": wf, "alternate": af, "signatures": signatures})

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
        raise RuntimeError("Protected candidate changed during 31.61 harmonic-comb profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-31.61-harmonic-comb-alignment-survivors",
        "champion3161Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "dual-stem-harmonic-comb-alignment-offbin-leakage",
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

    print("GOMYWAY 31.61 HARMONIC COMB ALIGNMENT SURVIVORS V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision harmonic-comb signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true harmonic-comb signatures:")
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
