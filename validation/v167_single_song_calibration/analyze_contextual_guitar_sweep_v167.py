#!/usr/bin/env python3
"""Post-I004 aggregate/reference-blind diagnosis of the V167 contextual Guitar sweep.

This analysis never opens the professional reference or scorer and never reads
per-event reference match assignments. It reads only the already-frozen complete
whole-rule score report, the reference-blind upstream evidence pool, and the frozen
I004 rich candidate. The goal is to explain factor behavior and expose evidence for
a genuinely new preregistered Guitar hypothesis without selecting a new rule.
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

EXPECTED_REPORT_SHA256 = "6b661f6dfa27d31204f4e8a9035d286d5324440b947eb3e49db99205dad9320e"
EXPECTED_POOL_SHA256 = "1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673"
EXPECTED_I004_SHA256 = "728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc"
EXPECTED_WINNER_ID = "gctx-o50-q100-allow-noharm"
EXPECTED_VARIANT_COUNT = 37
EXPECTED_NONBASELINE_COUNT = 36
EXPECTED_POSITIVE_COUNT = 10
EXPECTED_I004_GUITAR_COUNT = 1113
EXPECTED_I004_BASS_COUNT = 512
EXPECTED_I004_ADDITIONS = 63
EXPECTED_BASELINE_F1 = 0.419156774457634
EPS = 1e-12


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
    ordered = sorted(float(value) for value in values)
    index = int(round((len(ordered) - 1) * p))
    return ordered[index]


def summarize_numeric(values: Iterable[float]) -> dict[str, Any]:
    rows = [float(value) for value in values]
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


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mx = mean(xs)
    my = mean(ys)
    numerator = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx <= EPS or dy <= EPS:
        return None
    return numerator / (dx * dy)


def compact_variant(row: Mapping[str, Any]) -> dict[str, Any]:
    metrics = row.get("metrics") or {}
    delta = row.get("deltaVsIteration003") or {}
    summary = row.get("generationSummary") or {}
    config = row.get("config") or {}
    return {
        "id": str(row["id"]),
        "config": dict(config),
        "baseline": bool(config.get("baseline", False)),
        "added": int(summary.get("added", 0)),
        "eligible": int(summary.get("eligible", 0)),
        "sitesWithAdds": int(summary.get("sitesWithAdds", 0)),
        "sitesWithEligible": int(summary.get("sitesWithEligible", 0)),
        "sitesWithActiveContext": int(summary.get("sitesWithActiveContext", 0)),
        "f1": float(metrics["primaryF1"]),
        "precision": float(metrics["primaryPrecision"]),
        "recall": float(metrics["primaryRecall"]),
        "matched": int(metrics["matched"]),
        "generated": int(metrics["generated"]),
        "reference": int(metrics["reference"]),
        "falsePositive": int(metrics["falsePositive"]),
        "falseNegative": int(metrics["falseNegative"]),
        "f1DeltaPercentagePoints": float(delta.get("f1PercentagePoints", 0.0)),
        "precisionDeltaPercentagePoints": float(delta.get("precisionPercentagePoints", 0.0)),
        "recallDeltaPercentagePoints": float(delta.get("recallPercentagePoints", 0.0)),
        "matchedDelta": int(delta.get("matched", 0)),
        "generatedDelta": int(delta.get("generated", 0)),
        "falsePositiveDelta": int(delta.get("falsePositive", 0)),
        "falseNegativeDelta": int(delta.get("falseNegative", 0)),
    }


def variant_rank_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        -float(row["f1"]),
        -float(row["precision"]),
        int(row["added"]),
        str(row["id"]),
    )


def factor_value_key(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def factor_summary(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        value = row["config"].get(key)
        groups[factor_value_key(value)].append(row)

    output: dict[str, Any] = {}
    for value, group in sorted(groups.items()):
        ranked = sorted(group, key=variant_rank_key)
        output[value] = {
            "variantCount": len(group),
            "positiveVariantCount": sum(
                float(row["f1DeltaPercentagePoints"]) > EPS for row in group
            ),
            "added": summarize_numeric(row["added"] for row in group),
            "eligible": summarize_numeric(row["eligible"] for row in group),
            "f1DeltaPercentagePoints": summarize_numeric(
                row["f1DeltaPercentagePoints"] for row in group
            ),
            "precisionDeltaPercentagePoints": summarize_numeric(
                row["precisionDeltaPercentagePoints"] for row in group
            ),
            "recallDeltaPercentagePoints": summarize_numeric(
                row["recallDeltaPercentagePoints"] for row in group
            ),
            "matchedDelta": summarize_numeric(row["matchedDelta"] for row in group),
            "falsePositiveDelta": summarize_numeric(
                row["falsePositiveDelta"] for row in group
            ),
            "bestVariant": ranked[0],
            "rankedVariantIds": [row["id"] for row in ranked],
        }
    return output


def config_cell(
    row: Mapping[str, Any],
    exclude: str,
) -> tuple[tuple[str, Any], ...]:
    keys = (
        "onsetSupportMin",
        "candidateToMaxActiveTemplateScoreMin",
        "activeStateMode",
        "intervalContextPolicy",
    )
    return tuple(
        (key, row["config"].get(key))
        for key in keys
        if key != exclude
    )


def row_delta(high: Mapping[str, Any], low: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "higherId": high["id"],
        "lowerId": low["id"],
        "addedDelta": int(high["added"]) - int(low["added"]),
        "eligibleDelta": int(high["eligible"]) - int(low["eligible"]),
        "f1DeltaPercentagePoints": 100.0 * (float(high["f1"]) - float(low["f1"])),
        "precisionDeltaPercentagePoints": 100.0
        * (float(high["precision"]) - float(low["precision"])),
        "recallDeltaPercentagePoints": 100.0
        * (float(high["recall"]) - float(low["recall"])),
        "matchedDelta": int(high["matched"]) - int(low["matched"]),
        "falsePositiveDelta": int(high["falsePositive"])
        - int(low["falsePositive"]),
        "falseNegativeDelta": int(high["falseNegative"])
        - int(low["falseNegative"]),
    }


def paired_comparison(
    rows: list[dict[str, Any]],
    key: str,
    higher_value: Any,
    lower_value: Any,
) -> dict[str, Any]:
    high_rows: dict[tuple[tuple[str, Any], ...], dict[str, Any]] = {}
    low_rows: dict[tuple[tuple[str, Any], ...], dict[str, Any]] = {}
    for row in rows:
        value = row["config"].get(key)
        cell = config_cell(row, key)
        if value == higher_value:
            high_rows[cell] = row
        elif value == lower_value:
            low_rows[cell] = row

    common = sorted(set(high_rows) & set(low_rows), key=repr)
    pairs = [row_delta(high_rows[cell], low_rows[cell]) for cell in common]
    return {
        "factor": key,
        "higherValue": higher_value,
        "lowerValue": lower_value,
        "pairCount": len(pairs),
        "higherF1Count": sum(
            pair["f1DeltaPercentagePoints"] > EPS for pair in pairs
        ),
        "equalF1Count": sum(
            abs(pair["f1DeltaPercentagePoints"]) <= EPS for pair in pairs
        ),
        "lowerF1Count": sum(
            pair["f1DeltaPercentagePoints"] < -EPS for pair in pairs
        ),
        "addedDelta": summarize_numeric(pair["addedDelta"] for pair in pairs),
        "f1DeltaPercentagePoints": summarize_numeric(
            pair["f1DeltaPercentagePoints"] for pair in pairs
        ),
        "precisionDeltaPercentagePoints": summarize_numeric(
            pair["precisionDeltaPercentagePoints"] for pair in pairs
        ),
        "recallDeltaPercentagePoints": summarize_numeric(
            pair["recallDeltaPercentagePoints"] for pair in pairs
        ),
        "matchedDelta": summarize_numeric(pair["matchedDelta"] for pair in pairs),
        "falsePositiveDelta": summarize_numeric(
            pair["falsePositiveDelta"] for pair in pairs
        ),
        "falseNegativeDelta": summarize_numeric(
            pair["falseNegativeDelta"] for pair in pairs
        ),
        "pairs": pairs,
    }


def pair_by_two_values(
    rows: list[dict[str, Any]],
    key: str,
    high: float,
    low: float,
) -> dict[str, Any]:
    return paired_comparison(rows, key, high, low)


def histogram(values: Iterable[Any]) -> dict[str, int]:
    counter = Counter(str(value) for value in values)
    return dict(sorted(counter.items(), key=lambda item: item[0]))


def extract_i004_additions(i004: Mapping[str, Any]) -> list[dict[str, Any]]:
    streams = i004.get("streams") or {}
    guitar = list(streams.get("combinedGuitar") or [])
    bass = list(streams.get("bass") or [])
    if len(guitar) != EXPECTED_I004_GUITAR_COUNT:
        raise RuntimeError(f"I004 Guitar count drift: {len(guitar)}")
    if len(bass) != EXPECTED_I004_BASS_COUNT:
        raise RuntimeError(f"I004 Bass count drift: {len(bass)}")

    additions: list[dict[str, Any]] = []
    for row in guitar:
        evidence = row.get("v167RecoverySweepEvidence")
        if not isinstance(evidence, Mapping):
            continue
        rule = evidence.get("rule") or {}
        if str(rule.get("id")) != EXPECTED_WINNER_ID:
            continue
        additions.append(dict(row))
    if len(additions) != EXPECTED_I004_ADDITIONS:
        raise RuntimeError(
            f"I004 contextual addition count drift: {len(additions)}"
        )
    return additions


def addition_structure(additions: list[dict[str, Any]]) -> dict[str, Any]:
    active_state: list[bool] = []
    nearest_interval: list[int | None] = []
    ratios: list[float] = []
    template_ranks: list[float] = []
    template_scores: list[float] = []
    onset_supports: list[float] = []
    activity_supports: list[float] = []
    active_midi_counts: list[int] = []
    active_midi_contains_candidate: list[bool] = []

    for row in additions:
        recovery = row.get("v167RecoverySweepEvidence") or {}
        evidence = recovery.get("evidence") or {}
        active_midis = [int(value) for value in evidence.get("activeMidisAtSite") or []]
        candidate = int(evidence.get("candidateMidi", row["midi"]))
        active_state.append(bool(evidence.get("basicPitchActiveAtSite", False)))
        nearest = evidence.get("nearestDifferentActiveSemitoneDistance")
        nearest_interval.append(None if nearest is None else int(nearest))
        ratios.append(float(evidence["candidateToMaxActiveTemplateScoreRatio"]))
        template_ranks.append(float(evidence["templateRank"]))
        template_scores.append(float(evidence["templateScore"]))
        onset_supports.append(float(evidence["onsetSupport"]))
        activity_supports.append(float(evidence["activitySupport"]))
        active_midi_counts.append(len(active_midis))
        active_midi_contains_candidate.append(candidate in active_midis)

    return {
        "additionCount": len(additions),
        "candidateBasicPitchActiveAtSite": {
            "true": sum(active_state),
            "false": len(active_state) - sum(active_state),
        },
        "candidateMidiPresentInActiveMidiSet": {
            "true": sum(active_midi_contains_candidate),
            "false": len(active_midi_contains_candidate)
            - sum(active_midi_contains_candidate),
        },
        "nearestDifferentActiveSemitoneDistanceHistogram": histogram(
            "none" if value is None else value for value in nearest_interval
        ),
        "candidateToMaxActiveTemplateScoreRatio": summarize_numeric(ratios),
        "templateRank": summarize_numeric(template_ranks),
        "templateScore": summarize_numeric(template_scores),
        "onsetSupport": summarize_numeric(onset_supports),
        "activitySupport": summarize_numeric(activity_supports),
        "activeMidiCountAtSite": summarize_numeric(active_midi_counts),
    }


def structural_pool_summary(pool: Mapping[str, Any]) -> dict[str, Any]:
    guitar_pool = (
        (pool.get("upstreamPitchPools") or {}).get("guitarStandaloneHarmonic") or {}
    )
    candidates = list(guitar_pool.get("candidates") or [])
    if len(candidates) != 13328:
        raise RuntimeError(f"Guitar evidence pool row drift: {len(candidates)}")
    sites = {int(row["siteFrame"]) for row in candidates}
    if len(sites) != 272:
        raise RuntimeError(f"Guitar evidence pool site drift: {len(sites)}")
    active = [row for row in candidates if bool(row.get("basicPitchActiveAtSite", False))]
    inactive = [row for row in candidates if not bool(row.get("basicPitchActiveAtSite", False))]
    return {
        "candidateCount": len(candidates),
        "siteCount": len(sites),
        "activeCandidateCount": len(active),
        "inactiveCandidateCount": len(inactive),
        "policy": {
            "referenceBlindEvidence": True,
            "professionalReferenceReadForThisSummary": False,
            "scorerReadForThisSummary": False,
        },
    }


def mean_value(summary: Mapping[str, Any], key: str) -> float | None:
    value = (summary.get(key) or {}).get("mean")
    return None if value is None else float(value)


def diagnostic_questions(
    factor_summaries: Mapping[str, Any],
    comparisons: Mapping[str, Any],
) -> dict[str, Any]:
    noharm = comparisons["excludeHarmonicOctaveVsNone"]
    allow = comparisons["allowActiveVsInactiveOnly"]
    q100_vs_q075 = comparisons["ratio100Vs075"]
    q125_vs_q100 = comparisons["ratio125Vs100"]

    noharm_precision = mean_value(noharm, "precisionDeltaPercentagePoints")
    noharm_f1 = mean_value(noharm, "f1DeltaPercentagePoints")
    noharm_fp = mean_value(noharm, "falsePositiveDelta")
    allow_recall = mean_value(allow, "recallDeltaPercentagePoints")
    allow_matched = mean_value(allow, "matchedDelta")
    allow_fp = mean_value(allow, "falsePositiveDelta")
    q100_f1 = mean_value(q100_vs_q075, "f1DeltaPercentagePoints")
    q125_f1 = mean_value(q125_vs_q100, "f1DeltaPercentagePoints")
    q100_added = mean_value(q100_vs_q075, "addedDelta")
    q125_added = mean_value(q125_vs_q100, "addedDelta")

    ratio_summary = factor_summaries["candidateToMaxActiveTemplateScoreMin"]
    positive_by_ratio = {
        key: int(value["positiveVariantCount"])
        for key, value in ratio_summary.items()
    }

    return {
        "harmonicSuppressionPrecisionQuestion": {
            "comparison": "exclude_harmonic_octave minus none at fixed onset/ratio/active-state",
            "pairCount": int(noharm["pairCount"]),
            "meanPrecisionDeltaPercentagePoints": noharm_precision,
            "meanF1DeltaPercentagePoints": noharm_f1,
            "meanFalsePositiveDelta": noharm_fp,
            "supportsPrecisionRecovery": bool(
                noharm_precision is not None
                and noharm_precision > 0.0
                and noharm_fp is not None
                and noharm_fp < 0.0
            ),
        },
        "allowActiveReattackQuestion": {
            "comparison": "allow_active minus inactive_only at fixed onset/ratio/interval",
            "pairCount": int(allow["pairCount"]),
            "meanRecallDeltaPercentagePoints": allow_recall,
            "meanMatchedDelta": allow_matched,
            "meanFalsePositiveDelta": allow_fp,
            "supportsAdditionalRecall": bool(
                allow_recall is not None
                and allow_recall > 0.0
                and allow_matched is not None
                and allow_matched > 0.0
            ),
            "interpretationBoundary": (
                "aggregate recall/match effect only; this analysis does not read per-event reference matches and therefore cannot label any individual event a true re-attack"
            ),
        },
        "ratioMiddleRegimeQuestion": {
            "ratio100Minus075MeanF1PercentagePoints": q100_f1,
            "ratio125Minus100MeanF1PercentagePoints": q125_f1,
            "ratio100Minus075MeanAdded": q100_added,
            "ratio125Minus100MeanAdded": q125_added,
            "positiveVariantCountByRatio": positive_by_ratio,
            "supportsStableMiddleRegime": bool(
                q100_f1 is not None
                and q100_f1 > 0.0
                and q125_f1 is not None
                and q125_f1 < 0.0
            ),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--i004", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"analysis output already exists: {args.output}")
    if sha256_file(args.report) != EXPECTED_REPORT_SHA256:
        raise RuntimeError("frozen contextual sweep report SHA256 mismatch")
    if sha256_file(args.pool) != EXPECTED_POOL_SHA256:
        raise RuntimeError("frozen reference-blind evidence pool SHA256 mismatch")
    if sha256_file(args.i004) != EXPECTED_I004_SHA256:
        raise RuntimeError("frozen I004 candidate SHA256 mismatch")

    report = json.loads(args.report.read_text(encoding="utf-8"))
    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    i004 = json.loads(args.i004.read_text(encoding="utf-8"))

    if report.get("schema") != "dadrock.tabs.v167.contextual-guitar-recovery-sweep.v1":
        raise RuntimeError("unexpected frozen contextual report schema")
    if report.get("status") != "REFERENCE_GRADED_COMPLETE_PREDECLARED_CONTEXTUAL_VARIANTS":
        raise RuntimeError("unexpected frozen contextual report status")
    selection = report.get("selectionPolicy") or {}
    for key, expected in {
        "allVariantsFrozenBeforeReferenceRead": True,
        "individualEventSelectionByReference": False,
        "postScoreVariantMutation": False,
        "iteration004CreatedByThisSweep": False,
        "wholeVariantOnly": True,
    }.items():
        if selection.get(key) is not expected:
            raise RuntimeError(f"frozen contextual selection policy drift: {key}")

    rows = [compact_variant(row) for row in report.get("variants") or []]
    if len(rows) != EXPECTED_VARIANT_COUNT:
        raise RuntimeError(f"contextual variant count drift: {len(rows)}")
    baseline_rows = [row for row in rows if row["baseline"]]
    if len(baseline_rows) != 1:
        raise RuntimeError("contextual baseline count drift")
    baseline = baseline_rows[0]
    if abs(float(baseline["f1"]) - EXPECTED_BASELINE_F1) > EPS:
        raise RuntimeError("contextual baseline F1 drift")
    nonbaseline = [row for row in rows if not row["baseline"]]
    if len(nonbaseline) != EXPECTED_NONBASELINE_COUNT:
        raise RuntimeError("contextual nonbaseline count drift")
    positive = [row for row in nonbaseline if row["f1DeltaPercentagePoints"] > EPS]
    if len(positive) != EXPECTED_POSITIVE_COUNT:
        raise RuntimeError(f"positive contextual count drift: {len(positive)}")

    ranked = sorted(nonbaseline, key=variant_rank_key)
    if ranked[0]["id"] != EXPECTED_WINNER_ID:
        raise RuntimeError(f"contextual winner drift: {ranked[0]['id']}")
    report_winner = report.get("winner") or {}
    if str(report_winner.get("id")) != EXPECTED_WINNER_ID:
        raise RuntimeError("frozen report winner id drift")

    factor_summaries = {
        "onsetSupportMin": factor_summary(nonbaseline, "onsetSupportMin"),
        "candidateToMaxActiveTemplateScoreMin": factor_summary(
            nonbaseline, "candidateToMaxActiveTemplateScoreMin"
        ),
        "activeStateMode": factor_summary(nonbaseline, "activeStateMode"),
        "intervalContextPolicy": factor_summary(
            nonbaseline, "intervalContextPolicy"
        ),
    }

    comparisons = {
        "excludeHarmonicOctaveVsNone": paired_comparison(
            nonbaseline,
            "intervalContextPolicy",
            "exclude_harmonic_octave",
            "none",
        ),
        "chordIntervalVsNone": paired_comparison(
            nonbaseline,
            "intervalContextPolicy",
            "chord_interval",
            "none",
        ),
        "allowActiveVsInactiveOnly": paired_comparison(
            nonbaseline,
            "activeStateMode",
            "allow_active",
            "inactive_only",
        ),
        "ratio100Vs075": pair_by_two_values(
            nonbaseline,
            "candidateToMaxActiveTemplateScoreMin",
            1.00,
            0.75,
        ),
        "ratio125Vs100": pair_by_two_values(
            nonbaseline,
            "candidateToMaxActiveTemplateScoreMin",
            1.25,
            1.00,
        ),
        "onset65Vs50": pair_by_two_values(
            nonbaseline,
            "onsetSupportMin",
            0.65,
            0.50,
        ),
    }

    additions = extract_i004_additions(i004)
    selected_structure = addition_structure(additions)
    pool_summary = structural_pool_summary(pool)

    additions_x = [float(row["added"]) for row in nonbaseline]
    report_analysis = {
        "schema": "dadrock.tabs.v167.post-i004-contextual-guitar-aggregate-analysis.v1",
        "version": "V167",
        "status": "POST_I004_CONTEXTUAL_AGGREGATE_ANALYSIS_FROZEN",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "contextualSweepReportSha256": sha256_file(args.report),
            "referenceBlindEvidencePoolSha256": sha256_file(args.pool),
            "iteration004Sha256": sha256_file(args.i004),
        },
        "baseline": baseline,
        "winner": ranked[0],
        "variantCount": len(rows),
        "nonBaselineCount": len(nonbaseline),
        "positiveNonBaselineCount": len(positive),
        "positiveVariantIds": [row["id"] for row in sorted(positive, key=variant_rank_key)],
        "rankedNonBaseline": ranked,
        "factorSummaries": factor_summaries,
        "pairedFactorComparisons": comparisons,
        "correlationsAcross36WholeRules": {
            "additionsVsF1Delta": pearson(
                additions_x,
                [float(row["f1DeltaPercentagePoints"]) for row in nonbaseline],
            ),
            "additionsVsPrecisionDelta": pearson(
                additions_x,
                [
                    float(row["precisionDeltaPercentagePoints"])
                    for row in nonbaseline
                ],
            ),
            "additionsVsRecallDelta": pearson(
                additions_x,
                [float(row["recallDeltaPercentagePoints"]) for row in nonbaseline],
            ),
            "additionsVsFalsePositiveDelta": pearson(
                additions_x,
                [float(row["falsePositiveDelta"]) for row in nonbaseline],
            ),
            "additionsVsMatchedDelta": pearson(
                additions_x,
                [float(row["matchedDelta"]) for row in nonbaseline],
            ),
        },
        "referenceBlindStructuralEvidence": {
            "pool": pool_summary,
            "selectedI004Additions": selected_structure,
        },
        "diagnosticQuestions": diagnostic_questions(
            factor_summaries,
            comparisons,
        ),
        "policy": {
            "professionalReferenceReadByAnalysis": False,
            "scorerReadByAnalysis": False,
            "newReferenceFacingScoreCalls": 0,
            "perEventReferenceMatchAssignmentsRead": False,
            "aggregateWholeVariantScoresOnly": True,
            "referenceBlindEvidenceOnlyForEventStructure": True,
            "newRuleSelectedByThisAnalysis": False,
            "iteration005Created": False,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
            "generalizationClaim": False,
        },
    }
    write_json(args.output, report_analysis)

    print(
        json.dumps(
            {
                "winner": ranked[0]["id"],
                "positiveNonBaselineCount": len(positive),
                "correlations": report_analysis["correlationsAcross36WholeRules"],
                "diagnosticQuestions": report_analysis["diagnosticQuestions"],
                "newReferenceFacingScoreCalls": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
