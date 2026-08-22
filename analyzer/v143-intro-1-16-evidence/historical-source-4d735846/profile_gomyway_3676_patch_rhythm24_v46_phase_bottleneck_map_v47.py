from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT = PUBLIC / "gomyway-3676-patch-rhythm24-v45-strict-support-only-broaden-v46.json"
OUTPUT = PUBLIC / "gomyway-3676-patch-rhythm24-v46-phase-bottleneck-map-v47.json"
MANIFEST = PUBLIC / "gomyway-3676-patch-rhythm24-v46-phase-bottleneck-map-v47-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)
    d = json.loads(INPUT.read_text(encoding="utf-8"))
    if int(d.get("schemaVersion", -1)) != 46:
        raise RuntimeError("V46 input schema mismatch")

    phase_rows = []
    failure_rows = []
    rescue_rows = []
    regression_rows = []
    strict_hist = Counter()

    for phase in d.get("schemes", []):
        p = float(phase["phase"])
        passes = int(phase["passes"])
        v28passes = int(phase["v28Passes"])
        rows = list(phase.get("folds", []))
        failures = 0
        broadened = 0
        rescues = 0
        regressions = 0
        strict_counts = Counter()
        for row in rows:
            selector = row.get("selector", {})
            strict = int(selector.get("strictSupportCount", 0))
            strict_counts[str(strict)] += 1
            strict_hist[str(strict)] += 1
            broaden = float(row.get("outerQ", 0.20)) > 0.20
            broadened += int(broaden)
            vp = bool(row.get("passed"))
            bp = bool((row.get("v28Comparison") or {}).get("passed"))
            if not vp:
                failures += 1
                failure_rows.append({
                    "phase": p, "fold": int(row["fold"]), "strictSupportCount": strict,
                    "outerQ": row.get("outerQ"), "v46Lift": row.get("heldoutPrecisionLift"),
                    "v28Lift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
                    "v46Held": row.get("heldoutCandidate"), "v28Held": (row.get("v28Comparison") or {}).get("heldoutCandidate"),
                })
            if vp and not bp:
                rescues += 1
                rescue_rows.append({"phase": p, "fold": int(row["fold"]), "strictSupportCount": strict,
                                    "outerQ": row.get("outerQ"), "v46Lift": row.get("heldoutPrecisionLift"),
                                    "v28Lift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift")})
            if bp and not vp:
                regressions += 1
                regression_rows.append({"phase": p, "fold": int(row["fold"]), "strictSupportCount": strict,
                                        "outerQ": row.get("outerQ"), "v46Lift": row.get("heldoutPrecisionLift"),
                                        "v28Lift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift")})
        phase_rows.append({
            "phase": p, "v46Passes": passes, "v28Passes": v28passes,
            "failures": failures, "broadenedFolds": broadened,
            "rescuesVsV28": rescues, "regressionsVsV28": regressions,
            "strictSupportHistogram": dict(sorted(strict_counts.items())),
        })

    min_pass = min(r["v46Passes"] for r in phase_rows)
    bottlenecks = [r for r in phase_rows if r["v46Passes"] == min_pass]

    out = {
        "schemaVersion": 47,
        "profileType": "v46-phase-bottleneck-diagnostic",
        "diagnosticScope": "already-exposed-v28-and-v44-phases-only",
        "v46Summary": {
            "foldsPassed": d.get("foldsPassed"), "foldsTotal": d.get("foldsTotal"),
            "v28ComparisonPasses": d.get("v28ComparisonPasses"),
            "minimumPhasePasses": d.get("minimumPhasePasses"),
            "rescuesVsV28": d.get("rescuesVsV28"), "regressionsVsV28": d.get("regressionsVsV28"),
            "foldsBroadenedAboveV28Q": d.get("foldsBroadenedAboveV28Q"),
        },
        "bottleneckPhases": bottlenecks,
        "allPhases": phase_rows,
        "failureRows": failure_rows,
        "rescueRows": rescue_rows,
        "regressionRows": regression_rows,
        "strictSupportHistogramAllFolds": dict(sorted(strict_hist.items())),
        "newReserved1over64OddPhasesReferenced": False,
        "newTuningPerformed": False,
        "heldoutLabelsUsedForDiagnosticComparison": True,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "schemaVersion": 47,
        "output": str(OUTPUT.relative_to(ROOT)),
        "minimumPhasePasses": min_pass,
        "bottleneckPhases": [r["phase"] for r in bottlenecks],
        "failureCount": len(failure_rows),
        "rescueCount": len(rescue_rows),
        "regressionCount": len(regression_rows),
        "newReserved1over64OddPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V46 PHASE BOTTLENECK MAP V47 COMPLETE")
    print("V46 summary:", out["v46Summary"])
    print("Bottleneck phases:", [r["phase"] for r in bottlenecks])
    print("Failures:", len(failure_rows), "Rescues:", len(rescue_rows), "Regressions:", len(regression_rows))
    print("Strict support histogram:", dict(sorted(strict_hist.items())))
    print("New reserved 1/64 odd phases referenced: False")
    print("New tuning performed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Manifest:", MANIFEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
