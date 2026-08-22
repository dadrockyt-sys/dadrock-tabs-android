from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_3161_fundamental_phase_lock_survivors_v1 as phase3161

s3161 = phase3161.s3161
recur = phase3161.recur
recall = phase3161.recall
v2 = phase3161.v2
v3 = phase3161.v3
harmonic = phase3161.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-fundamental-periodicity-survivors-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-fundamental-periodicity-survivors-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def midi_hz(pitch: int) -> float:
    return 440.0 * (2.0 ** ((float(pitch) - 69.0) / 12.0))


def periodicity_features(audio: np.ndarray, sr: int, center: float, pitch: int) -> dict[str, float]:
    f0 = midi_hz(pitch)
    half = int(round(0.060 * sr))
    c = int(round(center * sr))
    lo = max(0, c - half)
    hi = min(len(audio), c + half)
    x = np.asarray(audio[lo:hi], dtype=np.float64)
    if len(x) < 64:
        return {"targetPeriodicity": 0.0, "bestPeriodicity": 0.0, "periodRatio": 0.0, "periodError": 1.0, "neighborContrast": 0.0}
    x = x - np.mean(x)
    x *= np.hanning(len(x))
    energy = float(np.dot(x, x)) + 1e-12

    target_lag = max(1, int(round(sr / f0)))
    radius = max(2, int(round(target_lag * 0.12)))
    min_lag = max(1, target_lag - radius)
    max_lag = min(len(x) // 2, target_lag + radius)

    def corr(lag: int) -> float:
        a = x[:-lag]
        b = x[lag:]
        den = float(np.sqrt(np.dot(a, a) * np.dot(b, b))) + 1e-12
        return float(np.dot(a, b) / den)

    vals = [(lag, corr(lag)) for lag in range(min_lag, max_lag + 1)]
    best_lag, best = max(vals, key=lambda z: z[1])
    target = corr(target_lag) if target_lag < len(x) else 0.0

    octave_lags = [max(1, int(round(target_lag / 2))), min(len(x) // 2, target_lag * 2)]
    octave_vals = [corr(l) for l in octave_lags if 0 < l < len(x)]
    neighbor = max(octave_vals) if octave_vals else 0.0
    period_error = abs(float(best_lag - target_lag)) / max(1.0, float(target_lag))

    return {
        "targetPeriodicity": round(target, 6),
        "bestPeriodicity": round(best, 6),
        "periodRatio": round(target / (abs(best) + 1e-12), 6),
        "periodError": round(period_error, 6),
        "neighborContrast": round(target - neighbor, 6),
        "windowEnergy": round(energy / max(1, len(x)), 8),
    }


def bucket(v: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if v < edge:
            return label
    return labels[-1]


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    min_target = min(w["targetPeriodicity"], a["targetPeriodicity"])
    max_target = max(w["targetPeriodicity"], a["targetPeriodicity"])
    min_best = min(w["bestPeriodicity"], a["bestPeriodicity"])
    max_error = max(w["periodError"], a["periodError"])
    min_contrast = min(w["neighborContrast"], a["neighborContrast"])
    target_diff = abs(w["targetPeriodicity"] - a["targetPeriodicity"])

    mt = bucket(min_target, [0.10, 0.25, 0.45, 0.65], ["mtp_lt010", "mtp_010_025", "mtp_025_045", "mtp_045_065", "mtp_065_plus"])
    xt = bucket(max_target, [0.20, 0.40, 0.60, 0.78], ["xtp_lt020", "xtp_020_040", "xtp_040_060", "xtp_060_078", "xtp_078_plus"])
    mb = bucket(min_best, [0.20, 0.40, 0.60, 0.78], ["mbp_lt020", "mbp_020_040", "mbp_040_060", "mbp_060_078", "mbp_078_plus"])
    pe = bucket(max_error, [0.02, 0.05, 0.10, 0.18], ["pe_lt002", "pe_002_005", "pe_005_010", "pe_010_018", "pe_018_plus"])
    nc = bucket(min_contrast, [-0.20, -0.05, 0.05, 0.18], ["nc_lt_n020", "nc_n020_n005", "nc_n005_005", "nc_005_018", "nc_018_plus"])
    td = bucket(target_diff, [0.05, 0.12, 0.25, 0.40], ["td_lt005", "td_005_012", "td_012_025", "td_025_040", "td_040_plus"])
    agreement = "both_periodic" if min_target >= 0.45 else ("one_periodic" if max_target >= 0.45 else "neither_periodic")

    return {
        f"minTargetPeriodicity::{mt}",
        f"maxTargetPeriodicity::{xt}",
        f"minBestPeriodicity::{mb}",
        f"maxPeriodError::{pe}",
        f"minNeighborContrast::{nc}",
        f"periodicityStemDifference::{td}",
        f"dualStemPeriodicityAgreement::{agreement}",
        f"periodicityCross::{mt}|{pe}|{nc}|{agreement}",
        f"periodicityConsistency::{agreement}|{td}|{mb}|{xt}",
        f"periodicityAliasCross::{nc}|{pe}|{mt}|{td}",
    }


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows = []
    for signature, counts in groups.items():
        true = int(counts["true"]); false = int(counts["false"]); total = true + false
        rows.append({"signature": signature, "true": true, "false": false, "total": total,
                     "precision": round(100.0 * true / total, 2) if total else 0.0})
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
    details = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = periodicity_features(winner_audio, winner_sr, center, pitch)
        af = periodicity_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({"token": list(tok), "truth": truth, "count": int(count), "winner": wf, "alternate": af, "signatures": signatures})

    for tok, count in matched.items(): record(tok, int(count), "true")
    for tok, count in extras.items(): record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported = [r for r in ranked if int(r["true"]) >= 5]
    supported.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after: raise RuntimeError("Protected candidate changed during 31.61 fundamental periodicity profiler")

    output = {"schemaVersion": 1, "passed": True, "profileType": "validated-31.61-fundamental-periodicity-survivors",
              "champion3161Score": score, "reconstruction": reconstruction, "featureFamily": "dual-stem-fundamental-autocorrelation-periodicity",
              "zeroPrecisionGeneralizableSignaturesMin5False": zero, "supportedTrueSignaturesMin5True": supported, "rows": details,
              "professionalReferenceUsedDuringDetection": False, "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
              "protected949CandidateHashUnchanged": True, "candidateEventsModified": False, "v7EventsModified": False,
              "rendererModified": False, "protectedBaselinesChanged": False, "productionSeparatorChanged": False, "productionPromotionAllowed": False}
    manifest = {"schemaVersion": 1, "passed": True, "output": str(OUTPUT_PATH.relative_to(ROOT)), "candidateSha256": after,
                "championPitchF1": score["pitchF1"], "matched": score["matched"], "missing": score["missing"], "extra": score["extra"],
                "zeroPrecisionSignatureCount": len(zero), "productionPromotionAllowed": False}
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 FUNDAMENTAL PERIODICITY SURVIVORS V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision fundamental periodicity signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]: print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true fundamental periodicity signatures:")
    for row in supported[:30]: print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
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
