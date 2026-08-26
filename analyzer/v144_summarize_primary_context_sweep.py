#!/usr/bin/env python3
"""Create a compact, decision-oriented summary of the persisted V144 context sweep."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

METRICS = ("exactEvent", "pitchContent", "pitchClassContent", "measurePitch", "measurePitchClass")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def family(name: str) -> str:
    if name == "v6-current-primary":
        return "baseline-current"
    if name == "source-top-score":
        return "baseline-top-score"
    if name.startswith("local-neighbor-"):
        return "local-neighbor"
    if name.startswith("dp-"):
        return "dynamic-programming"
    if name.startswith("repeat-"):
        return "repeat-consensus"
    return "other"


def compact(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "policy": row["policy"],
        "family": family(str(row["policy"])),
        "robustImprovedMetrics": list(row.get("robustImprovedMetrics") or []),
        "regressedMetrics": list(row.get("regressedMetrics") or []),
        "changedPrimaryCount": int(row.get("changedPrimaryCount") or 0),
        "primaryExactHitCount": int(row.get("primaryExactHitCount") or 0),
        "primaryExactHitDeltaVsV6": int(row.get("primaryExactHitDeltaVsV6") or 0),
        "improvementsVsV6F1": {m: float((row.get("improvementsVsV6F1") or {}).get(m) or 0.0) for m in METRICS},
        "splitImprovementsVsV6F1": {
            split: {m: float((((row.get("splitImprovementsVsV6F1") or {}).get(split) or {}).get(m)) or 0.0) for m in METRICS}
            for split in ("oddMeasures", "evenMeasures")
        },
    }


def metric_best(policies: list[Mapping[str, Any]], metric: str) -> dict[str, Any]:
    row = max(policies, key=lambda r: float((r.get("improvementsVsV6F1") or {}).get(metric) or 0.0))
    return compact(row)


def family_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        len(row.get("robustImprovedMetrics") or []),
        -len(row.get("regressedMetrics") or []),
        int(row.get("primaryExactHitDeltaVsV6") or 0),
        float((row.get("improvementsVsV6F1") or {}).get("exactEvent") or 0.0),
        float((row.get("improvementsVsV6F1") or {}).get("measurePitch") or 0.0),
        -int(row.get("changedPrimaryCount") or 0),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("report", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    report = load_json(args.report)
    policies = report.get("policies") if isinstance(report, Mapping) else None
    if not isinstance(policies, list) or len(policies) != 47:
        raise ValueError(f"expected 47 context policies, got {len(policies) if isinstance(policies, list) else 'invalid'}")

    max_robust = max(len(row.get("robustImprovedMetrics") or []) for row in policies)
    zero_regression = [row for row in policies if not (row.get("regressedMetrics") or [])]
    multi_robust = [row for row in policies if len(row.get("robustImprovedMetrics") or []) >= 2]
    positive_primary = [row for row in policies if int(row.get("primaryExactHitDeltaVsV6") or 0) > 0]

    by_family: dict[str, list[Mapping[str, Any]]] = {}
    for row in policies:
        by_family.setdefault(family(str(row["policy"])), []).append(row)

    best_per_family = {
        fam: compact(max(rows, key=family_key))
        for fam, rows in sorted(by_family.items())
    }

    top10 = [compact(row) for row in policies[:10]]
    best_metric = {metric: metric_best(policies, metric) for metric in METRICS}
    best_primary = compact(max(policies, key=lambda r: int(r.get("primaryExactHitDeltaVsV6") or 0)))

    # Count how often each metric is robustly improved and how often it regresses overall.
    robust_counts = {m: 0 for m in METRICS}
    regression_counts = {m: 0 for m in METRICS}
    for row in policies:
        for m in row.get("robustImprovedMetrics") or []:
            if m in robust_counts:
                robust_counts[m] += 1
        for m in row.get("regressedMetrics") or []:
            if m in regression_counts:
                regression_counts[m] += 1

    # A V7-worthy selector must improve at least 2 metrics robustly, have no overall regressions,
    # and not reduce exact-primary hit count.
    promotable = [
        row for row in policies
        if len(row.get("robustImprovedMetrics") or []) >= 2
        and not (row.get("regressedMetrics") or [])
        and int(row.get("primaryExactHitDeltaVsV6") or 0) >= 0
    ]

    summary = {
        "schemaVersion": 1,
        "classification": "v144-primary-context-sweep-compact-summary",
        "sourceReportClassification": report.get("classification"),
        "policyCount": len(policies),
        "candidateGenerated": False,
        "candidateModified": False,
        "modalInvoked": False,
        "productionModified": False,
        "calibrationReferenceUsedForGrading": True,
        "maxRobustImprovedMetricCount": max_robust,
        "zeroRegressionPolicyCount": len(zero_regression),
        "multiRobustPolicyCount": len(multi_robust),
        "positivePrimaryExactHitPolicyCount": len(positive_primary),
        "promotablePolicyCount": len(promotable),
        "robustImprovementCountsByMetric": robust_counts,
        "overallRegressionCountsByMetric": regression_counts,
        "bestPrimaryExactHitPolicy": best_primary,
        "bestPolicyByOverallMetricDelta": best_metric,
        "bestPolicyPerFamily": best_per_family,
        "top10ByOriginalRanking": top10,
        "promotablePolicies": [compact(row) for row in promotable],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
