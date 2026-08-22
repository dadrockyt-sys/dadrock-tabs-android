from __future__ import annotations

import itertools
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V97_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v96-reserved-1over512-confirmation-v97.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v98-failure-signature-mining-v99.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v98-failure-signature-mining-v99-manifest.json"

FEATURES = [
    "branch",
    "v96Decision",
    "originalQBucket",
    "finalQBucket",
    "pairRadius",
    "lambda",
    "selectionReason",
    "strictBroadSupportCount",
    "unanimousTightEscape",
    "phaseBin1over32",
]

MIN_ROWS = 8
MAX_SIGNATURE_WIDTH = 3
TOP_N = 30


def branch_name(row: dict) -> str:
    if row.get("excludedSafeBroadR8Lambda1"):
        return "excluded-safe-broad-r8-lambda1"
    if row.get("guardAppliedV96") and row.get("tightGuard"):
        return "tight"
    if row.get("guardAppliedV96") and row.get("safeBroadGuardBeforeExclusion"):
        return "safe-broad"
    return "fallback-v28"


def phase_bin_1over32(phase: float) -> str:
    idx = int(float(phase) * 32.0)
    idx = max(0, min(31, idx))
    return f"{idx}/32-{idx + 1}/32"


def norm(v):
    if isinstance(v, float):
        return round(v, 12)
    return v


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
            base_pass = bool((fold.get("v28Comparison") or {}).get("passed"))
            passed = bool(fold.get("passed"))
            rows.append({
                "phase": phase,
                "fold": int(fold.get("fold", -1)),
                "branch": branch_name(fold),
                "v96Decision": fold.get("v96Decision"),
                "originalQBucket": fold.get("originalQBucket"),
                "finalQBucket": fold.get("finalQBucket"),
                "pairRadius": cm.get("pairRadius"),
                "lambda": cm.get("lambda"),
                "selectionReason": selector.get("selectionReason"),
                "strictBroadSupportCount": selector.get("strictBroadSupportCount"),
                "unanimousTightEscape": selector.get("unanimousTightEscape"),
                "phaseBin1over32": phase_bin_1over32(phase),
                "passed": passed,
                "v28Passed": base_pass,
                "failed": not passed,
                "bottleneckFailure": (not passed) and phase in bottlenecks,
                "rescueVsV28": passed and not base_pass,
                "regressionVsV28": base_pass and not passed,
            })

    total_rows = len(rows)
    total_failures = sum(int(r["failed"]) for r in rows)
    total_bottleneck_failures = sum(int(r["bottleneckFailure"]) for r in rows)
    overall_failure_rate = total_failures / total_rows if total_rows else 0.0

    signatures = []

    for width in range(1, MAX_SIGNATURE_WIDTH + 1):
        for cols in itertools.combinations(FEATURES, width):
            groups = defaultdict(list)
            for r in rows:
                key = tuple(norm(r.get(c)) for c in cols)
                groups[key].append(r)

            for key, members in groups.items():
                n = len(members)
                if n < MIN_ROWS:
                    continue
                failures = sum(int(r["failed"]) for r in members)
                if failures == 0:
                    continue
                bottleneck_failures = sum(int(r["bottleneckFailure"]) for r in members)
                rescues = sum(int(r["rescueVsV28"]) for r in members)
                regressions = sum(int(r["regressionVsV28"]) for r in members)
                failure_rate = failures / n
                coverage = failures / total_failures if total_failures else 0.0
                bottleneck_coverage = (
                    bottleneck_failures / total_bottleneck_failures
                    if total_bottleneck_failures else 0.0
                )
                lift = failure_rate / overall_failure_rate if overall_failure_rate else 0.0

                signatures.append({
                    "width": width,
                    "features": list(cols),
                    "values": {c: key[i] for i, c in enumerate(cols)},
                    "rows": n,
                    "failures": failures,
                    "failureRate": round(failure_rate, 6),
                    "failureRateLiftVsOverall": round(lift, 4),
                    "failureCoverage": round(coverage, 6),
                    "bottleneckFailures": bottleneck_failures,
                    "bottleneckFailureCoverage": round(bottleneck_coverage, 6),
                    "rescuesVsV28": rescues,
                    "regressionsVsV28": regressions,
                    "netVsV28WithinSignature": rescues - regressions,
                })

    # Prefer signatures that explain many failures, then high concentration, then smaller/simple signatures.
    ranked = sorted(
        signatures,
        key=lambda s: (
            -s["failures"],
            -s["bottleneckFailures"],
            -s["failureRateLiftVsOverall"],
            s["width"],
            -s["rows"],
        ),
    )

    # Separate "surgical" signatures: concentrated enough to be interesting and not huge buckets.
    surgical = [
        s for s in signatures
        if s["failureRateLiftVsOverall"] >= 1.5
        and s["failures"] >= 4
        and s["rows"] <= 256
    ]
    surgical = sorted(
        surgical,
        key=lambda s: (
            -s["failureRateLiftVsOverall"],
            -s["failures"],
            -s["bottleneckFailures"],
            s["width"],
        ),
    )

    out = {
        "schemaVersion": 99,
        "profileType": "saved-v97-multidimensional-failure-signature-mining",
        "source": str(V97_PATH.relative_to(ROOT)),
        "foldPassScorePercent": round(100.0 * int(d["foldsPassed"]) / int(d["foldsTotal"]), 4),
        "foldsTotal": total_rows,
        "failureCount": total_failures,
        "overallFailureRate": round(overall_failure_rate, 6),
        "bottleneckFailureCount": total_bottleneck_failures,
        "minimumRowsPerSignature": MIN_ROWS,
        "maximumSignatureWidth": MAX_SIGNATURE_WIDTH,
        "topFailureCoverageSignatures": ranked[:TOP_N],
        "topSurgicalSignatures": surgical[:TOP_N],
        "usesSavedV97Only": True,
        "v97OutcomesTaintedForFutureSelection": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "protectedCandidateTouched": False,
        "productionPromotionAllowed": False,
        "metricNote": "The 88.9063% score is the fold-pass benchmark score, not a direct event-by-event professional-reference agreement percentage.",
    }

    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 99,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldPassScorePercent": out["foldPassScorePercent"],
        "failureCount": total_failures,
        "bottleneckFailureCount": total_bottleneck_failures,
        "usesSavedV97Only": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V99 SAVED V97 FAILURE SIGNATURE MINING COMPLETE")
    print(f"Jimmy fold-pass score: {out['foldPassScorePercent']:.4f}%")
    print(f"Remaining failures: {total_failures}/{total_rows} ({100.0 * overall_failure_rate:.2f}%)")
    print("Bottleneck failures:", total_bottleneck_failures)

    print("\n=== TOP FAILURE-COVERAGE SIGNATURES ===")
    for i, s in enumerate(ranked[:12], 1):
        print(
            f"#{i} features={s['features']} values={s['values']} "
            f"rows={s['rows']} failures={s['failures']} rate={s['failureRate']:.3f} "
            f"lift={s['failureRateLiftVsOverall']:.2f}x bottleneck={s['bottleneckFailures']} "
            f"rescues={s['rescuesVsV28']} regressions={s['regressionsVsV28']}"
        )

    print("\n=== TOP SURGICAL SIGNATURES ===")
    for i, s in enumerate(surgical[:12], 1):
        print(
            f"#{i} features={s['features']} values={s['values']} "
            f"rows={s['rows']} failures={s['failures']} rate={s['failureRate']:.3f} "
            f"lift={s['failureRateLiftVsOverall']:.2f}x bottleneck={s['bottleneckFailures']} "
            f"rescues={s['rescuesVsV28']} regressions={s['regressionsVsV28']}"
        )

    print("\nUses saved V97 only: True")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
