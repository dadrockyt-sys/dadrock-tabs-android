#!/usr/bin/env python3
"""Reference-blind aggregate/structural diagnosis after frozen V167 Iteration 005.

Inputs are limited to frozen aggregate whole-rule score reports, immutable generated
candidates, and the reference-blind upstream evidence pool. This analyzer never
opens the professional reference or scorer and never computes per-event reference
matches. It explains the state-split result and summarizes structural evidence for
whether a genuinely new sparse Guitar family is defensible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping

EXPECTED = {
    "contextualReportSha256": "6b661f6dfa27d31204f4e8a9035d286d5324440b947eb3e49db99205dad9320e",
    "stateSplitReportSha256": "f4dfd04849eab3f15290cadb2b9ff0a2903bc6174beb428b35c71aa7c7347562",
    "poolSha256": "1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673",
    "i003Sha256": "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115",
    "i005Sha256": "86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31",
    "i005GuitarF1": 0.42794058610999597,
    "i005GuitarCount": 1098,
    "i003GuitarCount": 1050,
    "selectedAdditionCount": 48,
    "poolRows": 13328,
    "poolSites": 272,
}

EPS = 1e-12
HARMONIC_INTERVALS = frozenset({12, 19, 24})
CHORD_INTERVALS = frozenset({3, 4, 5, 7, 8, 9, 10})


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def quantile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(x) for x in values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * p
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    weight = pos - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def summarize_numeric(values: Iterable[float]) -> dict[str, Any]:
    rows = [float(x) for x in values]
    if not rows:
        return {
            "count": 0,
            "min": None,
            "p10": None,
            "p25": None,
            "median": None,
            "p75": None,
            "p90": None,
            "max": None,
            "mean": None,
        }
    return {
        "count": len(rows),
        "min": min(rows),
        "p10": quantile(rows, 0.10),
        "p25": quantile(rows, 0.25),
        "median": quantile(rows, 0.50),
        "p75": quantile(rows, 0.75),
        "p90": quantile(rows, 0.90),
        "max": max(rows),
        "mean": mean(rows),
    }


def normalized_coords(events: list[Mapping[str, Any]]) -> list[tuple[int, float, int]]:
    return sorted(
        (int(row["measure"]), float(row["step"]), int(row["midi"]))
        for row in events
        if not bool(row.get("excludeFromScoring", False))
    )


def compact_metric(row: Mapping[str, Any]) -> dict[str, Any]:
    metric = row.get("metrics") or {}
    summary = row.get("generationSummary") or {}
    return {
        "id": row.get("id"),
        "f1": float(metric["primaryF1"]),
        "precision": float(metric["primaryPrecision"]),
        "recall": float(metric["primaryRecall"]),
        "matched": int(metric["matched"]),
        "generated": int(metric["generated"]),
        "falsePositive": int(metric["falsePositive"]),
        "falseNegative": int(metric["falseNegative"]),
        "added": int(summary.get("added", 0)),
        "activeAdded": int(summary.get("activeAdded", 0)),
        "inactiveAdded": int(summary.get("inactiveAdded", 0)),
    }


def interval_category(value: int | None) -> str:
    if value is None:
        return "no_different_active"
    if value in HARMONIC_INTERVALS:
        return "harmonic_octave"
    if value in CHORD_INTERVALS:
        return "chord_interval"
    if value <= 2:
        return "near_unison_1_2"
    if value <= 11:
        return "other_within_octave"
    return "other_above_octave"


def nearest_different_interval(candidate: int, active_midis: list[int]) -> int | None:
    vals = [abs(candidate - midi) for midi in active_midis if midi != candidate]
    return min(vals) if vals else None


def active_only_eligible(row: Mapping[str, Any], site_rows: list[Mapping[str, Any]]) -> bool:
    if not bool(row.get("basicPitchActiveAtSite", False)):
        return False
    if not bool(row.get("fundamentalPresent", False)):
        return False
    if float(row.get("templateRank", 0.0)) + EPS < 0.975:
        return False
    if float(row.get("onsetSupport", 0.0)) + EPS < 0.50:
        return False
    if float(row.get("activitySupport", 0.0)) + EPS < 0.05:
        return False
    active = [r for r in site_rows if bool(r.get("basicPitchActiveAtSite", False))]
    if not active:
        return False
    max_score = max(float(r.get("templateScore", 0.0)) for r in active)
    if max_score <= EPS:
        return False
    ratio = float(row.get("templateScore", 0.0)) / max_score
    if ratio + EPS < 1.00:
        return False
    active_midis = sorted({int(r["midi"]) for r in active})
    nearest = nearest_different_interval(int(row["midi"]), active_midis)
    if nearest in HARMONIC_INTERVALS:
        return False
    return True


def compare_onset_pairs(contextual: Mapping[str, Any]) -> dict[str, Any]:
    rows = [
        row for row in contextual.get("variants") or []
        if not bool((row.get("config") or {}).get("baseline", False))
    ]
    by_key: dict[tuple[Any, ...], dict[float, Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        config = row.get("config") or {}
        key = (
            float(config.get("candidateToMaxActiveTemplateScoreMin")),
            str(config.get("activeStateMode")),
            str(config.get("intervalContextPolicy")),
        )
        onset = float(config.get("onsetSupportMin"))
        by_key[key][onset] = row

    pairs: list[dict[str, Any]] = []
    for key, versions in sorted(by_key.items(), key=lambda item: str(item[0])):
        if 0.50 not in versions or 0.65 not in versions:
            continue
        low = compact_metric(versions[0.50])
        high = compact_metric(versions[0.65])
        config = versions[0.50].get("config") or {}
        pairs.append({
            "ratio": key[0],
            "activeStateMode": key[1],
            "intervalContextPolicy": key[2],
            "lowId": low["id"],
            "highId": high["id"],
            "deltaHighMinusLow": {
                "f1PercentagePoints": 100.0 * (high["f1"] - low["f1"]),
                "precisionPercentagePoints": 100.0 * (high["precision"] - low["precision"]),
                "recallPercentagePoints": 100.0 * (high["recall"] - low["recall"]),
                "matched": high["matched"] - low["matched"],
                "generated": high["generated"] - low["generated"],
                "falsePositive": high["falsePositive"] - low["falsePositive"],
                "falseNegative": high["falseNegative"] - low["falseNegative"],
                "added": high["added"] - low["added"],
            },
            "low": low,
            "high": high,
            "configExceptOnset": {
                "candidateToMaxActiveTemplateScoreMin": config.get(
                    "candidateToMaxActiveTemplateScoreMin"
                ),
                "activeStateMode": config.get("activeStateMode"),
                "intervalContextPolicy": config.get("intervalContextPolicy"),
            },
        })

    def summary(group: list[dict[str, Any]]) -> dict[str, Any]:
        if not group:
            return {"pairCount": 0}
        deltas = [row["deltaHighMinusLow"] for row in group]
        return {
            "pairCount": len(group),
            "higherOnsetImprovedF1": sum(d["f1PercentagePoints"] > EPS for d in deltas),
            "higherOnsetTiedF1": sum(abs(d["f1PercentagePoints"]) <= EPS for d in deltas),
            "higherOnsetReducedF1": sum(d["f1PercentagePoints"] < -EPS for d in deltas),
            "meanF1DeltaPercentagePoints": mean(d["f1PercentagePoints"] for d in deltas),
            "meanPrecisionDeltaPercentagePoints": mean(d["precisionPercentagePoints"] for d in deltas),
            "meanRecallDeltaPercentagePoints": mean(d["recallPercentagePoints"] for d in deltas),
            "meanMatchedDelta": mean(d["matched"] for d in deltas),
            "meanGeneratedDelta": mean(d["generated"] for d in deltas),
            "meanFalsePositiveDelta": mean(d["falsePositive"] for d in deltas),
            "meanAddedDelta": mean(d["added"] for d in deltas),
        }

    allow_active = [p for p in pairs if p["activeStateMode"] == "allow_active"]
    inactive_only = [p for p in pairs if p["activeStateMode"] == "inactive_only"]
    noharm_allow = [
        p for p in pairs
        if p["activeStateMode"] == "allow_active"
        and p["intervalContextPolicy"] == "exclude_harmonic_octave"
    ]
    q100_noharm_allow = [
        p for p in noharm_allow
        if abs(float(p["ratio"]) - 1.0) <= EPS
    ]
    return {
        "pairs": pairs,
        "overall": summary(pairs),
        "allowActive": summary(allow_active),
        "inactiveOnly": summary(inactive_only),
        "allowActiveExcludeHarmonicOctave": summary(noharm_allow),
        "closestToI004StructureRatio1AllowActiveNoHarm": summary(q100_noharm_allow),
        "closestToI004StructurePair": q100_noharm_allow[0] if len(q100_noharm_allow) == 1 else q100_noharm_allow,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contextual-report", type=Path, required=True)
    ap.add_argument("--state-split-report", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--i003", type=Path, required=True)
    ap.add_argument("--i005", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"post-I005 analysis output already exists: {args.output}")
    for path, expected in (
        (args.contextual_report, EXPECTED["contextualReportSha256"]),
        (args.state_split_report, EXPECTED["stateSplitReportSha256"]),
        (args.pool, EXPECTED["poolSha256"]),
        (args.i003, EXPECTED["i003Sha256"]),
        (args.i005, EXPECTED["i005Sha256"]),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen post-I005 input SHA mismatch: {path}: {actual}")

    contextual = json.loads(args.contextual_report.read_text(encoding="utf-8"))
    state = json.loads(args.state_split_report.read_text(encoding="utf-8"))
    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    i003 = json.loads(args.i003.read_text(encoding="utf-8"))
    i005 = json.loads(args.i005.read_text(encoding="utf-8"))

    if contextual.get("schema") != "dadrock.tabs.v167.contextual-guitar-recovery-sweep.v1":
        raise RuntimeError("unexpected contextual report schema")
    if state.get("schema") != "dadrock.tabs.v167.state-split-guitar-sweep.v1":
        raise RuntimeError("unexpected state-split report schema")
    if state.get("winner", {}).get("id") != "gss-active-only":
        raise RuntimeError("state-split winner drift")
    if abs(float(state["winner"]["metrics"]["primaryF1"]) - EXPECTED["i005GuitarF1"]) > EPS:
        raise RuntimeError("state-split winner F1 drift")
    if int((i005.get("calibration") or {}).get("iteration", -1)) != 5:
        raise RuntimeError("post-I005 analysis requires frozen Iteration 005")

    i003_guitar = list((i003.get("streams") or {}).get("combinedGuitar") or [])
    i005_guitar = list((i005.get("streams") or {}).get("combinedGuitar") or [])
    if len(i003_guitar) != EXPECTED["i003GuitarCount"]:
        raise RuntimeError("I003 Guitar count drift")
    if len(i005_guitar) != EXPECTED["i005GuitarCount"]:
        raise RuntimeError("I005 Guitar count drift")

    parent_coords = set(normalized_coords(i003_guitar))
    additions = [
        row for row in i005_guitar
        if (int(row["measure"]), float(row["step"]), int(row["midi"])) not in parent_coords
    ]
    if len(additions) != EXPECTED["selectedAdditionCount"]:
        raise RuntimeError(f"I005 addition-count drift: {len(additions)}")

    guitar_pool = (pool.get("upstreamPitchPools") or {}).get("guitarStandaloneHarmonic") or {}
    pool_rows = list(guitar_pool.get("candidates") or [])
    if len(pool_rows) != EXPECTED["poolRows"]:
        raise RuntimeError("Guitar pool-row drift")
    by_site: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for row in pool_rows:
        by_site[int(row["siteFrame"])].append(row)
    if len(by_site) != EXPECTED["poolSites"]:
        raise RuntimeError("Guitar pool-site drift")

    selected_rows: list[dict[str, Any]] = []
    selected_site_frames: set[int] = set()
    for event in additions:
        wrapper = event.get("v167RecoverySweepEvidence") or {}
        evidence = wrapper.get("evidence") or {}
        rule = wrapper.get("rule") or {}
        if rule.get("id") != "gss-active-only":
            raise RuntimeError("I005 addition rule identity drift")
        if evidence.get("stateSplitBranch") != "active_max":
            raise RuntimeError("I005 addition is not active-max branch")
        site = int(evidence["siteFrame"])
        selected_site_frames.add(site)
        site_rows = by_site.get(site) or []
        active_rows = [r for r in site_rows if bool(r.get("basicPitchActiveAtSite", False))]
        active_midis = sorted({int(r["midi"]) for r in active_rows})
        max_active = max(float(r.get("templateScore", 0.0)) for r in active_rows)
        max_ties = [
            int(r["midi"]) for r in active_rows
            if abs(float(r.get("templateScore", 0.0)) - max_active) <= EPS
        ]
        eligible = [r for r in site_rows if active_only_eligible(r, site_rows)]
        nearest = evidence.get("nearestDifferentActiveSemitoneDistance")
        nearest = int(nearest) if nearest is not None else None
        selected_rows.append({
            "siteFrame": site,
            "midi": int(event["midi"]),
            "onsetSupport": float(evidence["onsetSupport"]),
            "activitySupport": float(evidence["activitySupport"]),
            "templateRank": float(evidence["templateRank"]),
            "templateScore": float(evidence["templateScore"]),
            "candidateToMaxActiveTemplateScoreRatio": float(
                evidence["candidateToMaxActiveTemplateScoreRatio"]
            ),
            "activeMidiCountAtSite": len(active_midis),
            "maxActiveTieCountAtSite": len(max_ties),
            "eligibleActiveOnlyCandidateCountAtSite": len(eligible),
            "nearestDifferentActiveSemitoneDistance": nearest,
            "nearestDifferentActiveIntervalCategory": interval_category(nearest),
        })

    current_eligible_sites: list[dict[str, Any]] = []
    for site, site_rows in sorted(by_site.items()):
        eligible = [r for r in site_rows if active_only_eligible(r, site_rows)]
        if not eligible:
            continue
        active_rows = [r for r in site_rows if bool(r.get("basicPitchActiveAtSite", False))]
        active_midis = sorted({int(r["midi"]) for r in active_rows})
        max_active = max(float(r.get("templateScore", 0.0)) for r in active_rows)
        max_ties = [
            int(r["midi"]) for r in active_rows
            if abs(float(r.get("templateScore", 0.0)) - max_active) <= EPS
        ]
        current_eligible_sites.append({
            "siteFrame": site,
            "selectedByI005": site in selected_site_frames,
            "eligibleCount": len(eligible),
            "activeMidiCount": len(active_midis),
            "maxActiveTieCount": len(max_ties),
            "eligibleOnsetSupport": sorted({float(r["onsetSupport"]) for r in eligible}),
            "eligibleActivitySupport": sorted({float(r["activitySupport"]) for r in eligible}),
        })

    if len(current_eligible_sites) != EXPECTED["selectedAdditionCount"]:
        raise RuntimeError(
            "active-only current-rule eligible site count no longer equals 48"
        )
    if not all(row["selectedByI005"] for row in current_eligible_sites):
        raise RuntimeError("I005 selected-site set differs from active-only eligible-site set")

    state_rows = [compact_metric(row) for row in state.get("variants") or []]
    state_baseline = next(row for row in state_rows if row["id"] == "i004-baseline")
    state_new = [row for row in state_rows if row["id"] != "i004-baseline"]
    active_only = next(row for row in state_new if row["id"] == "gss-active-only")
    inactive_comparisons = []
    for row in state_new:
        if row["id"] == "gss-active-only":
            continue
        inactive_comparisons.append({
            "id": row["id"],
            "inactiveAdded": row["inactiveAdded"],
            "deltaVsActiveOnly": {
                "f1PercentagePoints": 100.0 * (row["f1"] - active_only["f1"]),
                "precisionPercentagePoints": 100.0 * (row["precision"] - active_only["precision"]),
                "recallPercentagePoints": 100.0 * (row["recall"] - active_only["recall"]),
                "matched": row["matched"] - active_only["matched"],
                "generated": row["generated"] - active_only["generated"],
                "falsePositive": row["falsePositive"] - active_only["falsePositive"],
                "falseNegative": row["falseNegative"] - active_only["falseNegative"],
            },
        })

    onset_pairs = compare_onset_pairs(contextual)

    selected_onset = [row["onsetSupport"] for row in selected_rows]
    selected_activity = [row["activitySupport"] for row in selected_rows]
    selected_rank = [row["templateRank"] for row in selected_rows]
    selected_ratio = [row["candidateToMaxActiveTemplateScoreRatio"] for row in selected_rows]
    active_counts = Counter(str(row["activeMidiCountAtSite"]) for row in selected_rows)
    tie_counts = Counter(str(row["maxActiveTieCountAtSite"]) for row in selected_rows)
    eligible_counts = Counter(str(row["eligibleActiveOnlyCandidateCountAtSite"]) for row in selected_rows)
    interval_hist = Counter(
        str(row["nearestDifferentActiveSemitoneDistance"])
        if row["nearestDifferentActiveSemitoneDistance"] is not None
        else "none"
        for row in selected_rows
    )
    interval_category_hist = Counter(
        row["nearestDifferentActiveIntervalCategory"] for row in selected_rows
    )

    onset_survival = {
        f"ge_{threshold:.2f}": sum(value + EPS >= threshold for value in selected_onset)
        for threshold in (0.55, 0.60, 0.65, 0.70, 0.75)
    }

    analysis = {
        "schema": "dadrock.tabs.v167.post-i005-active-only-aggregate-analysis.v1",
        "version": "V167",
        "status": "POST_I005_AGGREGATE_REFERENCE_BLIND_ANALYSIS_FROZEN",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "contextualReportSha256": sha256_file(args.contextual_report),
            "stateSplitReportSha256": sha256_file(args.state_split_report),
            "poolSha256": sha256_file(args.pool),
            "iteration003Sha256": sha256_file(args.i003),
            "iteration005Sha256": sha256_file(args.i005),
        },
        "policy": {
            "professionalReferenceReadByAnalysis": False,
            "scorerReadByAnalysis": False,
            "newReferenceFacingScoreCalls": 0,
            "perEventReferenceMatchAssignmentsRead": False,
            "wholeRuleAggregateMetricsRead": True,
            "referenceBlindStructuralEvidenceRead": True,
            "newRuleSelectedByThisAnalysis": False,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
            "generalizationClaim": False,
        },
        "stateSplitWholeRuleMechanism": {
            "i004Baseline": state_baseline,
            "i005ActiveOnlyWinner": active_only,
            "inactiveBranchVariantsVsActiveOnly": inactive_comparisons,
            "allFourNewRulesBeatI004": int(state.get("newVariantsBeatingIteration004", -1)) == 4,
        },
        "contextualOnset050Vs065WholeRuleEvidence": onset_pairs,
        "i005SelectedAdditionStructure": {
            "additionCount": len(selected_rows),
            "onsetSupport": summarize_numeric(selected_onset),
            "activitySupport": summarize_numeric(selected_activity),
            "templateRank": summarize_numeric(selected_rank),
            "candidateToMaxActiveTemplateScoreRatio": summarize_numeric(selected_ratio),
            "activeMidiCountAtSiteHistogram": dict(sorted(active_counts.items())),
            "maxActiveTieCountAtSiteHistogram": dict(sorted(tie_counts.items())),
            "eligibleActiveOnlyCandidateCountAtSiteHistogram": dict(sorted(eligible_counts.items())),
            "nearestDifferentActiveSemitoneDistanceHistogram": dict(sorted(interval_hist.items())),
            "nearestDifferentActiveIntervalCategoryHistogram": dict(sorted(interval_category_hist.items())),
            "onsetThresholdSurvivalCounts": onset_survival,
            "selectedRowsReferenceBlind": selected_rows,
        },
        "currentActiveOnlyEligibleSiteStructure": {
            "eligibleSiteCount": len(current_eligible_sites),
            "allEligibleSitesSelectedByI005": all(row["selectedByI005"] for row in current_eligible_sites),
            "sites": current_eligible_sites,
        },
        "diagnosticInterpretation": {
            "inactiveBranchConclusion": (
                "At whole-rule aggregate level, every tested inactive-enabled state-split rule "
                "underperformed active-only even though all still beat I004. This supports keeping "
                "the inactive branch closed for the next hypothesis."
            ),
            "activeRatioConclusion": (
                "Because an active candidate participates in max-active itself, ratio >=1.00 "
                "selects only max-score ties; the I005 active branch is therefore already a "
                "max-active-tie rule rather than a broad ratio threshold."
            ),
            "nextQuestion": (
                "The remaining defensible sparse question is whether a reference-blind structural "
                "subfilter inside the 48 max-active additions can improve precision without "
                "material recall collapse. Aggregate onset 0.50-vs-0.65 behavior and the frozen "
                "selected-addition distributions should be used only to preregister a small new "
                "whole-rule family, never to label or keep individual events by reference."
            ),
        },
    }
    write_json(args.output, analysis)
    print(json.dumps({
        "additionCount": len(selected_rows),
        "onsetPairSummary": onset_pairs["allowActiveExcludeHarmonicOctave"],
        "closestOnsetPair": onset_pairs["closestToI004StructurePair"],
        "onsetSupport": analysis["i005SelectedAdditionStructure"]["onsetSupport"],
        "onsetThresholdSurvivalCounts": onset_survival,
        "activeMidiCountHistogram": dict(sorted(active_counts.items())),
        "maxActiveTieCountHistogram": dict(sorted(tie_counts.items())),
        "intervalCategoryHistogram": dict(sorted(interval_category_hist.items())),
        "newReferenceFacingScoreCalls": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
