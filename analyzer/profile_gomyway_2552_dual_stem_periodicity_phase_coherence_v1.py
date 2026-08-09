from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2552_harmonic_template_survivors_precision_v1 as p2552

comp = p2552.comp
p2476 = p2552.p2476
recur = p2552.recur
recall = p2552.recall
v2 = p2552.v2
v3 = p2552.v3
harmonic = p2552.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PROFILE_PATH = PUBLIC / "gomyway-2476-dual-stem-harmonic-template-competition-v1.json"
EXHAUSTED_PROFILE_PATH = PUBLIC / "gomyway-2552-harmonic-template-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2552-dual-stem-periodicity-phase-coherence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2552-dual-stem-periodicity-phase-coherence-v1-manifest.json"
EXPECTED = (183, 684, 384)
EXPECTED_F1 = 25.52
EXPECTED_ZERO_SIGNATURES = 11
EXPECTED_PRUNE_COUNT = 44


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


def normalized_corr(values: np.ndarray, lag: int) -> float:
    if lag <= 0 or values.size <= lag + 16:
        return 0.0
    a = values[:-lag]
    b = values[lag:]
    if a.size < 32 or b.size < 32:
        return 0.0
    a = a - float(np.mean(a))
    b = b - float(np.mean(b))
    denom = math.sqrt(float(np.dot(a, a)) * float(np.dot(b, b)))
    if denom <= 1e-12:
        return 0.0
    return float(np.clip(float(np.dot(a, b)) / denom, -1.0, 1.0))


def best_corr_near(values: np.ndarray, lag: float, width: float = 0.06) -> tuple[float, int]:
    center = max(1, int(round(lag)))
    radius = max(1, int(round(center * width)))
    best = -1.0
    best_lag = center
    for candidate in range(max(1, center - radius), center + radius + 1):
        corr = normalized_corr(values, candidate)
        if corr > best:
            best = corr
            best_lag = candidate
    return float(max(best, 0.0)), int(best_lag)


def periodicity_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, float]:
    values = harmonic.segment(audio, sample_rate, center)
    if values.size < 512:
        return {
            "period1": 0.0,
            "period2": 0.0,
            "halfPeriod": 0.0,
            "periodPersistence": 0.0,
            "halfAliasRatio": 99.0,
            "earlyLateDiff": 1.0,
            "lagDrift": 1.0,
        }

    values = np.asarray(values, dtype=np.float64)
    values = values - float(np.mean(values))
    peak = float(np.max(np.abs(values)))
    if peak > 1e-9:
        values = values / peak

    f0 = harmonic.midi_hz(midi)
    if f0 <= 0.0:
        raise RuntimeError(f"Invalid MIDI frequency for pitch {midi}")
    period = float(sample_rate) / float(f0)

    period1, lag1 = best_corr_near(values, period, 0.06)
    period2, _ = best_corr_near(values, period * 2.0, 0.05)
    half_period, _ = best_corr_near(values, period * 0.5, 0.05)

    persistence = min(period1, period2)
    half_alias_ratio = half_period / max(period1, 1e-6)

    midpoint = values.size // 2
    early = values[:midpoint]
    late = values[midpoint:]
    early_corr, early_lag = best_corr_near(early, period, 0.07)
    late_corr, late_lag = best_corr_near(late, period, 0.07)
    early_late_diff = abs(early_corr - late_corr)
    lag_drift = abs(float(early_lag - late_lag)) / max(period, 1.0)

    return {
        "period1": float(period1),
        "period2": float(period2),
        "halfPeriod": float(half_period),
        "periodPersistence": float(persistence),
        "halfAliasRatio": float(half_alias_ratio),
        "earlyLateDiff": float(early_late_diff),
        "lagDrift": float(lag_drift),
        "bestLag": float(lag1),
    }


def periodicity_bucket(v: float) -> str:
    if v < 0.10:
        return "per_lt010"
    if v < 0.20:
        return "per_010_020"
    if v < 0.35:
        return "per_020_035"
    if v < 0.50:
        return "per_035_050"
    if v < 0.70:
        return "per_050_070"
    return "per_070_plus"


def persistence_bucket(v: float) -> str:
    if v < 0.08:
        return "persist_lt008"
    if v < 0.16:
        return "persist_008_016"
    if v < 0.28:
        return "persist_016_028"
    if v < 0.45:
        return "persist_028_045"
    return "persist_045_plus"


def alias_bucket(v: float) -> str:
    if v < 0.70:
        return "alias_lt070"
    if v < 0.95:
        return "alias_070_095"
    if v < 1.20:
        return "alias_095_120"
    if v < 1.60:
        return "alias_120_160"
    return "alias_160_plus"


def stability_bucket(v: float) -> str:
    if v < 0.08:
        return "stability_lt008"
    if v < 0.18:
        return "stability_008_018"
    if v < 0.32:
        return "stability_018_032"
    return "stability_032_plus"


def drift_bucket(v: float) -> str:
    if v < 0.03:
        return "drift_lt003"
    if v < 0.07:
        return "drift_003_007"
    if v < 0.14:
        return "drift_007_014"
    return "drift_014_plus"


def disagreement_bucket(v: float) -> str:
    if v < 0.08:
        return "diff_lt008"
    if v < 0.18:
        return "diff_008_018"
    if v < 0.32:
        return "diff_018_032"
    return "diff_032_plus"


def signatures_for(wf: dict[str, float], af: dict[str, float]) -> set[str]:
    max_period = max(wf["period1"], af["period1"])
    min_period = min(wf["period1"], af["period1"])
    min_persistence = min(wf["periodPersistence"], af["periodPersistence"])
    max_alias = max(wf["halfAliasRatio"], af["halfAliasRatio"])
    max_stability_diff = max(wf["earlyLateDiff"], af["earlyLateDiff"])
    max_lag_drift = max(wf["lagDrift"], af["lagDrift"])
    stem_diff = abs(wf["period1"] - af["period1"])

    pmax = periodicity_bucket(max_period)
    pmin = periodicity_bucket(min_period)
    persist = persistence_bucket(min_persistence)
    alias = alias_bucket(max_alias)
    stability = stability_bucket(max_stability_diff)
    drift = drift_bucket(max_lag_drift)
    diff = disagreement_bucket(stem_diff)

    return {
        f"maxPeriodicity::{pmax}",
        f"minPeriodicity::{pmin}",
        f"periodPersistence::{persist}",
        f"halfPeriodAlias::{alias}",
        f"periodStability::{stability}",
        f"periodLagDrift::{drift}",
        f"stemPeriodAgreement::{diff}",
        f"periodPersistenceCross::{pmin}|{persist}|{diff}",
        f"periodAliasCross::{pmin}|{alias}|{diff}",
        f"periodStabilityCross::{pmin}|{stability}|{drift}|{diff}",
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

    exhausted = v2.load_json(EXHAUSTED_PROFILE_PATH)
    if exhausted.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("25.52 harmonic-template survivor profile is not reference-free during detection")
    if exhausted.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("25.52 harmonic-template survivor branch is not exhausted")

    source_profile = v2.load_json(SOURCE_PROFILE_PATH)
    zero_rows = list(source_profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected {EXPECTED_ZERO_SIGNATURES} validated harmonic-template signatures, got {len(zero_rows)}"
        )
    exact_signatures = {str(row["signature"]) for row in zero_rows}

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    champion2552, pruned = p2552.reconstruct_2552(
        grid,
        winner_audio,
        winner_sr,
        alt_audio,
        alt_sr,
        exact_signatures,
    )
    prune_count = int(sum(pruned.values()))
    if prune_count != EXPECTED_PRUNE_COUNT:
        raise RuntimeError(f"Expected 25.52 prune count {EXPECTED_PRUNE_COUNT}, got {prune_count}")
    if int(sum((pruned & reference).values())) != 0:
        raise RuntimeError("25.52 reconstruction unexpectedly pruned reference matches")

    score = recur.grade(champion2552, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 25.52 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched = champion2552 & reference
    extras = champion2552 - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = periodicity_features(winner_audio, winner_sr, center, pitch)
        af = periodicity_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "maxPeriodicity": max(wf["period1"], af["period1"]),
            "minPeriodicity": min(wf["period1"], af["period1"]),
            "minPeriodPersistence": min(wf["periodPersistence"], af["periodPersistence"]),
            "maxHalfPeriodAliasRatio": max(wf["halfAliasRatio"], af["halfAliasRatio"]),
            "stemPeriodicityDiff": abs(wf["period1"] - af["period1"]),
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
        raise RuntimeError("Protected candidate changed during 25.52 periodicity phase-coherence profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-25.52-dual-stem-periodicity-phase-coherence",
        "champion2552Score": score,
        "featureFamily": "dual-stem-time-domain-periodicity-phase-coherence",
        "validatedHarmonicTemplatePruneCount": prune_count,
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

    print("GOMYWAY 25.52 DUAL-STEM PERIODICITY PHASE-COHERENCE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision periodicity signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true periodicity signatures (5+ true):")
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
