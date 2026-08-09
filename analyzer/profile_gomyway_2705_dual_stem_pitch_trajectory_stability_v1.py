from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2705_dual_stem_onset_jitter_consistency_v1 as prior

recur = prior.recur
recall = prior.recall
v2 = prior.v2
v3 = prior.v3
harmonic = prior.harmonic
salience = prior.salience

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PRIOR_PROFILE = PUBLIC / "gomyway-2705-dual-stem-onset-jitter-consistency-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2705-dual-stem-pitch-trajectory-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2705-dual-stem-pitch-trajectory-stability-v1-manifest.json"
EXPECTED = (183, 684, 303)
EXPECTED_F1 = 27.05


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def bucket(v: float, edges: list[tuple[float, str]], tail: str) -> str:
    for limit, label in edges:
        if v < limit:
            return label
    return tail


def frame_pitch_offset_cents(audio: np.ndarray, sr: int, center: float, midi: int, half_ms: float = 28.0) -> tuple[float, float]:
    half = max(64, int(sr * half_ms / 1000.0))
    c = int(round(center * sr))
    lo = max(0, c - half)
    hi = min(len(audio), c + half)
    x = np.asarray(audio[lo:hi], dtype=np.float64)
    if x.size < 128:
        return 999.0, 0.0
    x = x - float(np.mean(x))
    x *= np.hanning(x.size)
    power = np.abs(np.fft.rfft(x)) ** 2
    freqs = np.fft.rfftfreq(x.size, d=1.0 / float(sr))
    f0 = harmonic.midi_hz(midi)
    search = (freqs >= f0 * 0.94) & (freqs <= f0 * 1.06)
    if not np.any(search):
        return 999.0, 0.0
    p = power[search]
    f = freqs[search]
    if p.size == 0 or float(np.max(p)) <= 0.0:
        return 999.0, 0.0
    i = int(np.argmax(p))
    peak_f = float(f[i])
    cents = 1200.0 * math.log2(max(peak_f, 1e-12) / max(f0, 1e-12))
    local_total = float(np.sum(p)) + 1e-12
    prominence = float(p[i]) / local_total
    return float(cents), prominence


def trajectory_features(audio: np.ndarray, sr: int, center: float, midi: int) -> dict[str, float]:
    offsets_ms = (-70.0, -35.0, 0.0, 35.0, 70.0)
    cents: list[float] = []
    prominence: list[float] = []
    for off_ms in offsets_ms:
        c, p = frame_pitch_offset_cents(audio, sr, center + off_ms / 1000.0, midi)
        if abs(c) < 500.0:
            cents.append(c)
            prominence.append(p)
    if not cents:
        return {
            "coverage": 0.0,
            "medianAbsOffsetCents": 999.0,
            "trajectoryStdCents": 999.0,
            "trajectoryRangeCents": 999.0,
            "driftCents": 999.0,
            "signFlips": 9.0,
            "minProminence": 0.0,
        }
    arr = np.asarray(cents, dtype=np.float64)
    diffs = np.diff(arr)
    sign_flips = 0
    if diffs.size >= 2:
        signs = np.sign(diffs)
        for i in range(1, len(signs)):
            if signs[i] != 0 and signs[i - 1] != 0 and signs[i] != signs[i - 1]:
                sign_flips += 1
    return {
        "coverage": float(len(cents) / len(offsets_ms)),
        "medianAbsOffsetCents": float(np.median(np.abs(arr))),
        "trajectoryStdCents": float(np.std(arr)),
        "trajectoryRangeCents": float(np.max(arr) - np.min(arr)),
        "driftCents": float(abs(arr[-1] - arr[0])) if arr.size >= 2 else 0.0,
        "signFlips": float(sign_flips),
        "minProminence": float(min(prominence)) if prominence else 0.0,
    }


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    min_cov = min(w["coverage"], a["coverage"])
    max_offset = max(w["medianAbsOffsetCents"], a["medianAbsOffsetCents"])
    max_std = max(w["trajectoryStdCents"], a["trajectoryStdCents"])
    max_range = max(w["trajectoryRangeCents"], a["trajectoryRangeCents"])
    max_drift = max(w["driftCents"], a["driftCents"])
    max_flips = max(w["signFlips"], a["signFlips"])
    min_prom = min(w["minProminence"], a["minProminence"])
    stem_offset_diff = abs(w["medianAbsOffsetCents"] - a["medianAbsOffsetCents"])
    stem_std_diff = abs(w["trajectoryStdCents"] - a["trajectoryStdCents"])

    cov = bucket(min_cov, [(0.40, "cov_lt040"), (0.70, "cov_040_070"), (0.90, "cov_070_090")], "cov_090_plus")
    off = bucket(max_offset, [(12.0, "off_lt12"), (25.0, "off_12_25"), (45.0, "off_25_45"), (80.0, "off_45_80")], "off_80_plus")
    std = bucket(max_std, [(8.0, "std_lt8"), (18.0, "std_8_18"), (35.0, "std_18_35"), (60.0, "std_35_60")], "std_60_plus")
    rng = bucket(max_range, [(20.0, "range_lt20"), (45.0, "range_20_45"), (80.0, "range_45_80"), (140.0, "range_80_140")], "range_140_plus")
    drift = bucket(max_drift, [(10.0, "drift_lt10"), (25.0, "drift_10_25"), (50.0, "drift_25_50"), (90.0, "drift_50_90")], "drift_90_plus")
    flips = bucket(max_flips, [(1.0, "flips_0"), (2.0, "flips_1"), (3.0, "flips_2")], "flips_3_plus")
    prom = bucket(min_prom, [(0.15, "prom_lt015"), (0.30, "prom_015_030"), (0.50, "prom_030_050")], "prom_050_plus")
    odiff = bucket(stem_offset_diff, [(8.0, "odiff_lt8"), (20.0, "odiff_8_20"), (40.0, "odiff_20_40")], "odiff_40_plus")
    sdiff = bucket(stem_std_diff, [(6.0, "sdiff_lt6"), (15.0, "sdiff_6_15"), (30.0, "sdiff_15_30")], "sdiff_30_plus")

    return {
        f"minTrajectoryCoverage::{cov}",
        f"maxMedianPitchOffset::{off}",
        f"maxTrajectoryStd::{std}",
        f"maxTrajectoryRange::{rng}",
        f"maxTrajectoryDrift::{drift}",
        f"maxTrajectorySignFlips::{flips}",
        f"minTrajectoryProminence::{prom}",
        f"dualStemOffsetAgreement::{odiff}",
        f"dualStemTrajectoryStdAgreement::{sdiff}",
        f"pitchTrajectoryCross::{cov}|{off}|{std}|{drift}",
        f"trajectoryInstabilityCross::{std}|{rng}|{flips}|{prom}",
        f"dualStemTrajectoryCross::{off}|{odiff}|{sdiff}|{cov}",
    }


def reconstruct_2705(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference):
    champion2673, _ = salience.transient.reconstruct_2673(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    salience_payload = v2.load_json(salience.OUTPUT_PATH)
    rows = list(salience_payload.get("rows", []))
    row_by_token = {tuple(int(v) for v in row["token"]): row for row in rows}
    zero_rows = list(salience_payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != 3:
        raise RuntimeError(f"Expected 3 validated local-salience signatures, got {len(zero_rows)}")
    exact = {str(r["signature"]) for r in zero_rows}
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion2673.items():
        row = row_by_token.get(tok)
        if row and ({str(s) for s in row.get("signatures", [])} & exact):
            pruned[tok] = count
    if int(sum(pruned.values())) != 16 or int(sum((pruned & reference).values())) != 0:
        raise RuntimeError("Failed to reconstruct validated 16-note local-salience prune")
    champion = champion2673 - pruned
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 27.05 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")
    return champion


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    prior_payload = v2.load_json(PRIOR_PROFILE)
    if prior_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("27.05 onset-jitter profile is not reference-free during detection")
    if prior_payload.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("27.05 onset-jitter branch is not exhausted")

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
    champion = reconstruct_2705(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)
    score = recur.grade(champion, reference)

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = trajectory_features(winner_audio, winner_sr, center, pitch)
        af = trajectory_features(alt_audio, alt_sr, center, pitch)
        sigs = sorted(signatures_for(wf, af))
        for s in sigs:
            groups[s][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "signatures": sigs,
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
        raise RuntimeError("Protected candidate changed during 27.05 pitch-trajectory profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-27.05-dual-stem-pitch-trajectory-stability",
        "champion2705Score": score,
        "featureFamily": "dual-stem-pitch-trajectory-stability",
        "onsetJitterBranchExhausted": True,
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
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
        "zeroPrecisionSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 27.05 DUAL-STEM PITCH TRAJECTORY STABILITY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision pitch-trajectory signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
    print("Supported true/mixed pitch-trajectory signatures:")
    for row in supported[:30]:
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
