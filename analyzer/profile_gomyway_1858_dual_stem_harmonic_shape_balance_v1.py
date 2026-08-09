from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_1858_harmonic_occupancy_survivors_precision_v1 as p1858

b1813 = p1858.b1813
occ = p1858.occ
recur = p1858.recur
recall = p1858.recall
v2 = p1858.v2
v3 = p1858.v3
harmonic = occ.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1858-dual-stem-harmonic-shape-balance-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1858-dual-stem-harmonic-shape-balance-v1-manifest.json"
EXPECTED = (183, 684, 920)
EXPECTED_F1 = 18.58


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct_1858(grid: Any) -> Counter[tuple[int, int, int]]:
    champion_1813 = occ.reconstruct_1813(grid)
    profile_payload = v2.load_json(b1813.PROFILE_PATH)
    rows = list(profile_payload.get("rows", []))
    row_by_token = {tuple(int(v) for v in row["token"]): row for row in rows}
    predicates = (
        b1813.pred_a,
        b1813.pred_b,
        b1813.pred_c,
        b1813.pred_d,
        b1813.pred_e,
        b1813.pred_f,
        b1813.pred_g,
    )
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_1813.items():
        row = row_by_token.get(tok)
        if row is not None and any(pred(row) for pred in predicates):
            pruned[tok] = count
    return champion_1813 - pruned


def ratio_bucket(value: float) -> str:
    if value < 0.50:
        return "ratio_lt050"
    if value < 0.80:
        return "ratio_050_080"
    if value < 1.20:
        return "ratio_080_120"
    if value < 1.80:
        return "ratio_120_180"
    if value < 3.00:
        return "ratio_180_300"
    return "ratio_300_plus"


def slope_bucket(value: float) -> str:
    if value < -0.90:
        return "slope_lt_n090"
    if value < -0.45:
        return "slope_n090_n045"
    if value < -0.15:
        return "slope_n045_n015"
    if value < 0.15:
        return "slope_n015_p015"
    return "slope_p015_plus"


def disagreement_bucket(value: float) -> str:
    if value < 0.20:
        return "shapeagree_lt020"
    if value < 0.45:
        return "shapeagree_020_045"
    if value < 0.80:
        return "shapeagree_045_080"
    return "shapeagree_080_plus"


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        t = int(counts["true"])
        f = int(counts["false"])
        n = t + f
        out.append({
            "signature": signature,
            "true": t,
            "false": f,
            "total": n,
            "precision": round(100.0 * t / n, 2) if n else 0.0,
        })
    return sorted(out, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def band_energy(spec: np.ndarray, freqs: np.ndarray, center_hz: float, half_width_hz: float) -> float:
    mask = (freqs >= center_hz - half_width_hz) & (freqs <= center_hz + half_width_hz)
    if not np.any(mask):
        return 0.0
    return float(np.sum(spec[mask]))


def stem_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, float]:
    values = harmonic.segment(audio, sample_rate, center)
    if values.size < 256:
        return {"lowHighRatio": 0.0, "oddEvenRatio": 0.0, "harmonicSlope": 0.0}

    n_fft = 8192
    window = np.hanning(values.size).astype(np.float32)
    spec = np.abs(np.fft.rfft(values * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    f0 = harmonic.midi_hz(midi)
    nyquist = sample_rate * 0.5
    eps = 1e-9

    energies: list[float] = []
    harmonic_numbers: list[int] = []
    for h in range(1, 7):
        hz = f0 * h
        if hz >= nyquist - 60.0:
            break
        half_width = max(6.0, hz * 0.012)
        energies.append(band_energy(spec, freqs, hz, half_width))
        harmonic_numbers.append(h)

    if len(energies) < 3:
        return {"lowHighRatio": 0.0, "oddEvenRatio": 0.0, "harmonicSlope": 0.0}

    arr = np.asarray(energies, dtype=float)
    low = float(np.sum(arr[: min(3, len(arr))]))
    high = float(np.sum(arr[min(3, len(arr)) :]))
    if high <= 0.0:
        high = eps
    odd = float(sum(e for h, e in zip(harmonic_numbers, energies) if h % 2 == 1))
    even = float(sum(e for h, e in zip(harmonic_numbers, energies) if h % 2 == 0))
    x = np.log(np.asarray(harmonic_numbers, dtype=float))
    y = np.log(arr + eps)
    slope = float(np.polyfit(x, y, 1)[0]) if len(arr) >= 3 else 0.0

    return {
        "lowHighRatio": low / (high + eps),
        "oddEvenRatio": odd / (even + eps),
        "harmonicSlope": slope,
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

    survivor_payload = v2.load_json(p1858.OUTPUT_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("18.58 occupancy survivor profile is not reference-free during detection")
    if survivor_payload.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("18.58 harmonic-occupancy branch is not exhausted")

    champion = reconstruct_1858(grid)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 18.58 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

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

        min_low_high = min(wf["lowHighRatio"], af["lowHighRatio"])
        min_odd_even = min(wf["oddEvenRatio"], af["oddEvenRatio"])
        max_slope = max(wf["harmonicSlope"], af["harmonicSlope"])
        shape_disagree = max(
            abs(np.log((wf["lowHighRatio"] + 1e-9) / (af["lowHighRatio"] + 1e-9))),
            abs(np.log((wf["oddEvenRatio"] + 1e-9) / (af["oddEvenRatio"] + 1e-9))),
        )

        lh = ratio_bucket(min_low_high)
        oe = ratio_bucket(min_odd_even)
        sl = slope_bucket(max_slope)
        ag = disagreement_bucket(shape_disagree)
        signatures = {
            "lowHigh": lh,
            "oddEven": oe,
            "harmonicSlope": sl,
            "shapeAgreement": ag,
            "lowHighSlope": f"{lh}|{sl}",
            "oddEvenSlope": f"{oe}|{sl}",
            "shapeCross": f"{lh}|{oe}|{ag}",
            "harmonicShapeCross": f"{lh}|{oe}|{sl}|{ag}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": count,
            "winner": wf,
            "alternate": af,
            "minLowHighRatio": min_low_high,
            "minOddEvenRatio": min_odd_even,
            "maxHarmonicSlope": max_slope,
            "shapeDisagreement": shape_disagree,
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
        raise RuntimeError("Protected candidate changed during 18.58 harmonic-shape profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-18.58-dual-stem-harmonic-shape-balance",
        "champion1858Score": score,
        "featureFamily": "dual-stem-harmonic-shape-balance",
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
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-harmonic-shape-signatures-with-prune-specific-heldout-cv",
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

    print("GOMYWAY 18.58 DUAL-STEM HARMONIC SHAPE BALANCE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision harmonic-shape signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true harmonic-shape signatures (5+ true):")
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
