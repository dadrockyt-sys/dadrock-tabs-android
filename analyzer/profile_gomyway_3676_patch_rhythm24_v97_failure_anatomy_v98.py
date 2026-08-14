from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V97_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v96-reserved-1over512-confirmation-v97.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v97-failure-anatomy-v98.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v97-failure-anatomy-v98-manifest.json"


def branch_name(row: dict) -> str:
    if row.get("excludedSafeBroadR8Lambda1"):
        return "excluded-safe-broad-r8-lambda1"
    if row.get("guardAppliedV96") and row.get("tightGuard"):
        return "tight"
    if row.get("guardAppliedV96") and row.get("safeBroadGuardBeforeExclusion"):
        return "safe-broad"
    return "fallback-v28"


def phase_bin_1over32(phase: float) -> str:
    # Diagnostic grouping only; does not alter any model or threshold.
    idx = int(float(phase) * 32.0)
    idx = max(0, min(31, idx))
    return f"{idx}/32-{idx + 1}/32"


def summarize(rows: list[dict], key_fn):
    groups = defaultdict(lambda: {
        "rows": 0,
        "failures": 0,
        "bottleneckFailures": 0,
        "rescuesVsV28": 0,
        "regressionsVsV28": 0,
        "bothPass": 0,
        "bothFail": 0,
    })
    for r in rows:
        k = str(key_fn(r))
        g = groups[k]
        g["rows"] += 1
        failed = not bool(r["passed"])
        base_pass = bool((r.get("v28Comparison") or {}).get("passed"))
        if failed:
            g["failures"] += 1
        if failed and r.get("isBottleneckPhase"):
            g["bottleneckFailures"] += 1
        if bool(r["passed"]) and not base_pass:
            g["rescuesVsV28"] += 1
        if base_pass and not bool(r["passed"]):
            g["regressionsVsV28"] += 1
        if bool(r["passed"]) and base_pass:
            g["bothPass"] += 1
        if (not bool(r["passed"])) and (not base_pass):
            g["bothFail"] += 1

    out = {}
    for k, g in groups.items():
        g["failureRate"] = round(g["failures"] / g["rows"], 6) if g["rows"] else 0.0
        out[k] = g
    return dict(sorted(out.items(), key=lambda kv: (-kv[1]["failureRate"], -kv[1]["rows"], kv[0])))


def main() -> None:
    d = json.loads(V97_PATH.read_text(encoding="utf-8"))
    if int(d.get("schemaVersion", -1)) != 97:
        raise RuntimeError("V97 output missing or wrong schema")

    bottlenecks = {float(x) for x in d.get("bottleneckPhases") or []}
    rows = []
    for scheme in d.get("schemes") or []:
        phase = float(scheme["phase"])
        for fold in scheme.get("folds") or []:
            cm = fold.get("chosenModel") or {}
            selector = fold.get("selector") or {}
            row = dict(fold)
            row["phase"] = phase
            row["branch"] = branch_name(fold)
            row["pairRadius"] = cm.get("pairRadius")
            row["lambda"] = cm.get("lambda")
            row["selectionReason"] = selector.get("selectionReason")
            row["strictBroadSupportCount"] = selector.get("strictBroadSupportCount")
            row["unanimousTightEscape"] = selector.get("unanimousTightEscape")
            row["isBottleneckPhase"] = phase in bottlenecks
            row["phaseBin1over32"] = phase_bin_1over32(phase)
            rows.append(row)

    failures = [r for r in rows if not bool(r["passed"])]
    bottleneck_failures = [r for r in failures if r["isBottleneckPhase"]]

    score_pct = 100.0 * int(d["foldsPassed"]) / int(d["foldsTotal"])
    v28_pct = 100.0 * int(d["v28ComparisonPasses"]) / int(d["foldsTotal"])

    summary = {
        "foldPassScorePercent": round(score_pct, 4),
        "v28FoldPassScorePercent": round(v28_pct, 4),
        "percentagePointGainVsV28": round(score_pct - v28_pct, 4),
        "foldsPassed": int(d["foldsPassed"]),
        "foldsTotal": int(d["foldsTotal"]),
        "failureCount": len(failures),
        "bottleneckPhaseCount": len(bottlenecks),
        "bottleneckFailureCount": len(bottleneck_failures),
        "rescuesVsV28": int(d["rescuesVsV28"]),
        "regressionsVsV28": int(d["regressionsVsV28"]),
        "minimumPhasePasses": int(d["minimumPhasePasses"]),
        "byBranch": summarize(rows, lambda r: r["branch"]),
        "byDecision": summarize(rows, lambda r: r.get("v96Decision")),
        "byOriginalQBucket": summarize(rows, lambda r: r.get("originalQBucket")),
        "byFinalQBucket": summarize(rows, lambda r: r.get("finalQBucket")),
        "byPairRadius": summarize(rows, lambda r: r.get("pairRadius")),
        "byLambda": summarize(rows, lambda r: r.get("lambda")),
        "bySelectionReason": summarize(rows, lambda r: r.get("selectionReason")),
        "byStrictBroadSupportCount": summarize(rows, lambda r: r.get("strictBroadSupportCount")),
        "byUnanimousTightEscape": summarize(rows, lambda r: r.get("unanimousTightEscape")),
        "byPhaseBin1over32": summarize(rows, lambda r: r.get("phaseBin1over32")),
    }

    out = {
        "schemaVersion": 98,
        "profileType": "v97-saved-output-failure-anatomy",
        "source": str(V97_PATH.relative_to(ROOT)),
        "summary": summary,
        "bottleneckFailures": bottleneck_failures,
        "usesSavedV97Only": True,
        "v97OutcomesTaintedForFutureSelection": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "protectedCandidateTouched": False,
        "productionPromotionAllowed": False,
        "metricNote": "foldPassScorePercent is the V97 fold-pass benchmark score, not yet a direct event-by-event professional-reference note agreement percentage",
    }

    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 98,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldPassScorePercent": summary["foldPassScorePercent"],
        "v28FoldPassScorePercent": summary["v28FoldPassScorePercent"],
        "percentagePointGainVsV28": summary["percentagePointGainVsV28"],
        "failureCount": summary["failureCount"],
        "bottleneckFailureCount": summary["bottleneckFailureCount"],
        "usesSavedV97Only": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V98 V97 SAVED-OUTPUT FAILURE ANATOMY COMPLETE")
    print(f"Jimmy V97 fold-pass score: {summary['foldPassScorePercent']:.4f}%")
    print(f"V28 fold-pass score: {summary['v28FoldPassScorePercent']:.4f}%")
    print(f"Gain vs V28: +{summary['percentagePointGainVsV28']:.4f} percentage points")
    print("Failures:", summary["failureCount"], "bottleneck failures:", summary["bottleneckFailureCount"])
    for key in [
        "byBranch",
        "byDecision",
        "byPairRadius",
        "byLambda",
        "bySelectionReason",
        "byStrictBroadSupportCount",
        "byUnanimousTightEscape",
        "byPhaseBin1over32",
    ]:
        print(f"\n{key}:")
        for name, stats in summary[key].items():
            print(name, stats)
    print("\nUses saved V97 only: True")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
