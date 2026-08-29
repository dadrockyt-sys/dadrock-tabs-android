#!/usr/bin/env python3
"""Analyze the frozen V167 Guitar recovery sweep without new reference access.

This script reads only the terminal whole-variant sweep report plus the immutable
reference-blind upstream evidence pool. It does not read the professional reference,
scorer, or any per-event match assignment. Its purpose is to explain the first
Guitar recovery grid at aggregate-rule level and expose structural evidence features
for a genuinely new preregistered Guitar hypothesis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

EXPECTED_REPORT_SHA256 = "1bcc5eca05df31270ff7ff638cca6def3166a0e5084c4874d70d710d4696836f"
EXPECTED_POOL_SHA256 = "1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673"
EXPECTED_GUITAR_BASELINE_F1 = 0.419156774457634
EXPECTED_GUITAR_VARIANTS = 49
EXPECTED_GUITAR_POOL_ROWS = 13328
EXPECTED_GUITAR_POOL_SITES = 272


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def q(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * p))
    return float(ordered[index])


def summarize_numeric(values: Iterable[float]) -> dict[str, Any]:
    rows = [float(x) for x in values]
    if not rows:
        return {"count": 0, "min": None, "p10": None, "p25": None, "median": None, "p75": None, "p90": None, "max": None, "mean": None}
    return {
        "count": len(rows),
        "min": min(rows),
        "p10": q(rows, 0.10),
        "p25": q(rows, 0.25),
        "median": q(rows, 0.50),
        "p75": q(rows, 0.75),
        "p90": q(rows, 0.90),
        "max": max(rows),
        "mean": mean(rows),
    }


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mx, my = mean(xs), mean(ys)
    numerator = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return numerator / (dx * dy)


def compact_variant(row: dict[str, Any]) -> dict[str, Any]:
    m = row["metrics"]
    d = row["deltaVsIteration002"]
    s = row.get("generationSummary") or {}
    return {
        "id": row["id"],
        "config": row["config"],
        "added": int(s.get("added", 0)),
        "eligible": int(s.get("eligible", 0)),
        "sitesWithAdds": int(s.get("sitesWithAdds", 0)),
        "f1": float(m["primaryF1"]),
        "precision": float(m["primaryPrecision"]),
        "recall": float(m["primaryRecall"]),
        "matched": int(m["matched"]),
        "generated": int(m["generated"]),
        "falsePositive": int(m["falsePositive"]),
        "falseNegative": int(m["falseNegative"]),
        "f1DeltaPercentagePoints": float(d["f1PercentagePoints"]),
        "precisionDeltaPercentagePoints": float(d["precisionPercentagePoints"]),
        "recallDeltaPercentagePoints": float(d["recallPercentagePoints"]),
        "matchedDelta": int(d["matched"]),
        "generatedDelta": int(d["generated"]),
        "falsePositiveDelta": int(d["falsePositive"]),
        "falseNegativeDelta": int(d["falseNegative"]),
    }


def factor_summary(nonbaseline: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in nonbaseline:
        value = row["config"].get(key)
        groups[json.dumps(value, sort_keys=True)].append(row)
    out: dict[str, Any] = {}
    for encoded, rows in sorted(groups.items()):
        value = json.loads(encoded)
        best = min(rows, key=lambda r: (-r["f1"], -r["precision"], r["added"], r["id"]))
        out[str(value).lower() if isinstance(value, bool) else str(value)] = {
            "variantCount": len(rows),
            "meanAdded": mean(r["added"] for r in rows),
            "meanF1DeltaPercentagePoints": mean(r["f1DeltaPercentagePoints"] for r in rows),
            "meanPrecisionDeltaPercentagePoints": mean(r["precisionDeltaPercentagePoints"] for r in rows),
            "meanRecallDeltaPercentagePoints": mean(r["recallDeltaPercentagePoints"] for r in rows),
            "bestVariant": best,
        }
    return out


def bucket_added(value: int) -> str:
    if value <= 25:
        return "000-025"
    if value <= 50:
        return "026-050"
    if value <= 100:
        return "051-100"
    if value <= 150:
        return "101-150"
    if value <= 200:
        return "151-200"
    if value <= 300:
        return "201-300"
    return "301+"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise RuntimeError(f"analysis output already exists: {args.output}")
    if sha256_file(args.report) != EXPECTED_REPORT_SHA256:
        raise RuntimeError("frozen sweep report SHA256 mismatch")
    if sha256_file(args.pool) != EXPECTED_POOL_SHA256:
        raise RuntimeError("frozen upstream pool SHA256 mismatch")

    report = json.loads(args.report.read_text(encoding="utf-8"))
    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    rows = [compact_variant(r) for r in report.get("variants") or [] if r.get("stream") == "combinedGuitar"]
    if len(rows) != EXPECTED_GUITAR_VARIANTS:
        raise RuntimeError(f"Guitar sweep count drift: {len(rows)}")
    baseline = next((r for r in rows if bool((r.get("config") or {}).get("baseline", False))), None)
    if baseline is None or abs(baseline["f1"] - EXPECTED_GUITAR_BASELINE_F1) > 1e-12:
        raise RuntimeError("Guitar baseline drift")
    nonbaseline = [r for r in rows if not bool((r.get("config") or {}).get("baseline", False))]
    ranked = sorted(nonbaseline, key=lambda r: (-r["f1"], -r["precision"], r["added"], r["id"]))

    addition_buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in nonbaseline:
        addition_buckets[bucket_added(row["added"])].append(row)
    addition_bucket_summary: dict[str, Any] = {}
    for name, group in sorted(addition_buckets.items()):
        best = min(group, key=lambda r: (-r["f1"], -r["precision"], r["added"], r["id"]))
        addition_bucket_summary[name] = {
            "variantCount": len(group),
            "added": summarize_numeric([r["added"] for r in group]),
            "f1DeltaPercentagePoints": summarize_numeric([r["f1DeltaPercentagePoints"] for r in group]),
            "precisionDeltaPercentagePoints": summarize_numeric([r["precisionDeltaPercentagePoints"] for r in group]),
            "recallDeltaPercentagePoints": summarize_numeric([r["recallDeltaPercentagePoints"] for r in group]),
            "bestVariant": best,
        }

    guitar_pool = (pool.get("upstreamPitchPools") or {}).get("guitarStandaloneHarmonic") or {}
    candidates = list(guitar_pool.get("candidates") or [])
    if len(candidates) != EXPECTED_GUITAR_POOL_ROWS:
        raise RuntimeError(f"Guitar evidence pool row drift: {len(candidates)}")
    by_site: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        by_site[int(row["siteFrame"])].append(row)
    if len(by_site) != EXPECTED_GUITAR_POOL_SITES:
        raise RuntimeError(f"Guitar evidence site drift: {len(by_site)}")

    structural_sites: list[dict[str, Any]] = []
    nearest_interval_hist = Counter()
    top_inactive_template_ratio: list[float] = []
    top_inactive_rank_gap: list[float] = []
    top_inactive_score_gap: list[float] = []
    active_pitch_counts: list[int] = []
    inactive_eligible_counts: list[int] = []
    sites_without_active = 0
    sites_with_inactive_eligible = 0

    for site in sorted(by_site):
        site_rows = by_site[site]
        active = sorted({int(r["midi"]) for r in site_rows if bool(r.get("basicPitchActiveAtSite", False))})
        active_pitch_counts.append(len(active))
        if not active:
            sites_without_active += 1
        active_scores = [float(r.get("templateScore", 0.0)) for r in site_rows if bool(r.get("basicPitchActiveAtSite", False))]
        max_active_score = max(active_scores) if active_scores else 0.0

        eligible = [
            r for r in site_rows
            if not bool(r.get("basicPitchActiveAtSite", False))
            and bool(r.get("fundamentalPresent", False))
            and float(r.get("templateRank", 0.0)) >= 0.80
            and float(r.get("onsetSupport", 0.0)) >= 0.35
            and float(r.get("activitySupport", 0.0)) >= 0.05
        ]
        inactive_eligible_counts.append(len(eligible))
        if eligible:
            sites_with_inactive_eligible += 1
        eligible.sort(key=lambda r: (
            -float(r.get("templateRank", 0.0)),
            -float(r.get("templateScore", 0.0)),
            -float(r.get("onsetSupport", 0.0)),
            -float(r.get("activitySupport", 0.0)),
            int(r["midi"]),
        ))
        if not eligible:
            continue

        top = eligible[0]
        top_score = float(top.get("templateScore", 0.0))
        top_rank = float(top.get("templateRank", 0.0))
        second_score = float(eligible[1].get("templateScore", 0.0)) if len(eligible) > 1 else 0.0
        second_rank = float(eligible[1].get("templateRank", 0.0)) if len(eligible) > 1 else 0.0
        ratio = top_score / max_active_score if max_active_score > 0 else None
        if ratio is not None:
            top_inactive_template_ratio.append(ratio)
        top_inactive_rank_gap.append(top_rank - second_rank)
        top_inactive_score_gap.append(top_score - second_score)

        nearest = min((abs(int(top["midi"]) - midi) for midi in active), default=None)
        if nearest is not None:
            nearest_interval_hist[str(nearest)] += 1
        structural_sites.append({
            "siteFrame": site,
            "siteSeconds": float(top["siteSeconds"]),
            "activeMidiCount": len(active),
            "inactiveEligibleCount": len(eligible),
            "topInactiveMidi": int(top["midi"]),
            "topInactiveTemplateRank": top_rank,
            "topInactiveTemplateScore": top_score,
            "topInactiveOnsetSupport": float(top.get("onsetSupport", 0.0)),
            "topInactiveActivitySupport": float(top.get("activitySupport", 0.0)),
            "topInactiveToMaxActiveTemplateScoreRatio": ratio,
            "topVsSecondInactiveTemplateRankGap": top_rank - second_rank,
            "topVsSecondInactiveTemplateScoreGap": top_score - second_score,
            "nearestActiveSemitoneDistance": nearest,
        })

    xs = [float(r["added"]) for r in nonbaseline]
    ys_f1 = [float(r["f1DeltaPercentagePoints"]) for r in nonbaseline]
    ys_precision = [float(r["precisionDeltaPercentagePoints"]) for r in nonbaseline]
    ys_recall = [float(r["recallDeltaPercentagePoints"]) for r in nonbaseline]

    analysis = {
        "schema": "dadrock.tabs.v167.guitar-recovery-sweep-aggregate-analysis.v1",
        "version": "V167",
        "status": "TERMINAL_SWEEP_AGGREGATE_ANALYSIS_FROZEN",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "sweepReportSha256": sha256_file(args.report),
            "upstreamEvidencePoolSha256": sha256_file(args.pool),
        },
        "policy": {
            "professionalReferenceReadByAnalysis": False,
            "scorerReadByAnalysis": False,
            "newReferenceFacingScoreCalls": 0,
            "perEventReferenceMatchAssignmentsRead": False,
            "aggregateWholeVariantScoresOnly": True,
            "candidateEvidenceIsReferenceBlind": True,
            "newRuleSelectedByThisAnalysis": False,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
            "generalizationClaim": False,
        },
        "baseline": baseline,
        "bestNonBaseline": ranked[0],
        "topNonBaselineVariants": ranked[:12],
        "allNonBaselineVariantsBeatBaseline": all(r["f1"] > baseline["f1"] for r in nonbaseline),
        "nonBaselineVariantsBeatingBaseline": sum(r["f1"] > baseline["f1"] for r in nonbaseline),
        "nonBaselineVariantsMatchingOrBeatingBaseline": sum(r["f1"] >= baseline["f1"] - 1e-12 for r in nonbaseline),
        "nonBaselineCount": len(nonbaseline),
        "correlationsAcross48WholeRules": {
            "addedVsF1Delta": pearson(xs, ys_f1),
            "addedVsPrecisionDelta": pearson(xs, ys_precision),
            "addedVsRecallDelta": pearson(xs, ys_recall),
        },
        "additionBuckets": addition_bucket_summary,
        "factorSummaries": {
            "templateRankMin": factor_summary(nonbaseline, "templateRankMin"),
            "onsetSupportMin": factor_summary(nonbaseline, "onsetSupportMin"),
            "maxAddsPerSite": factor_summary(nonbaseline, "maxAddsPerSite"),
            "basicPitchInactiveOnly": factor_summary(nonbaseline, "basicPitchInactiveOnly"),
        },
        "referenceBlindStructuralEvidence": {
            "siteCount": len(by_site),
            "candidateCount": len(candidates),
            "sitesWithoutAnyBasicPitchActiveMidi": sites_without_active,
            "sitesWithAtLeastOneInactiveEligibleCandidateAtFirstGridFloor": sites_with_inactive_eligible,
            "activeMidiCountPerSite": summarize_numeric(active_pitch_counts),
            "inactiveEligibleCandidateCountPerSiteAtFirstGridFloor": summarize_numeric(inactive_eligible_counts),
            "topInactiveToMaxActiveTemplateScoreRatio": summarize_numeric(top_inactive_template_ratio),
            "topVsSecondInactiveTemplateRankGap": summarize_numeric(top_inactive_rank_gap),
            "topVsSecondInactiveTemplateScoreGap": summarize_numeric(top_inactive_score_gap),
            "nearestActiveSemitoneDistanceHistogramForTopInactive": dict(sorted(nearest_interval_hist.items(), key=lambda kv: int(kv[0]))),
            "siteRows": structural_sites,
        },
        "interpretationGuardrails": {
            "allowed": "Use only aggregate whole-rule score behavior plus reference-blind evidence distributions to preregister a structurally new rule family.",
            "forbidden": "Do not inspect which individual recovery candidates matched or missed the professional reference, and do not select individual events from reference feedback.",
        },
    }
    write_json(args.output, analysis)
    print(json.dumps({
        "bestNonBaseline": analysis["bestNonBaseline"],
        "nonBaselineVariantsBeatingBaseline": analysis["nonBaselineVariantsBeatingBaseline"],
        "correlations": analysis["correlationsAcross48WholeRules"],
        "structuralEvidence": {
            "sites": len(by_site),
            "sitesWithInactiveEligible": sites_with_inactive_eligible,
            "templateRatio": analysis["referenceBlindStructuralEvidence"]["topInactiveToMaxActiveTemplateScoreRatio"],
            "nearestActiveIntervals": analysis["referenceBlindStructuralEvidence"]["nearestActiveSemitoneDistanceHistogramForTopInactive"],
        },
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
