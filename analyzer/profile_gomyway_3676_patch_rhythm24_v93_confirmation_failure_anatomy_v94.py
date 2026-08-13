from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v90-reserved-1over256-confirmation-v93.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v93-confirmation-failure-anatomy-v94.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v93-confirmation-failure-anatomy-v94-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branch(row: dict) -> str:
    if row.get("tightGuard"):
        return "tight"
    if row.get("safeBroadGuard"):
        return "safe-broad"
    return "fallback-v28"


def main() -> None:
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if int(data.get("schemaVersion", -1)) != 93:
        raise RuntimeError("Expected V93 result")

    regressions = []
    rescues = []
    failures = []
    bottleneck_set = {float(x) for x in data.get("bottleneckPhases") or []}
    bottleneck_failures = []

    for scheme in data.get("schemes") or []:
        phase = float(scheme["phase"])
        for row in scheme.get("folds") or []:
            passed = bool(row.get("passed"))
            v28_passed = bool((row.get("v28Comparison") or {}).get("passed"))
            item = {
                "phase": phase,
                "fold": int(row.get("fold")),
                "branch": branch(row),
                "originalQBucket": row.get("originalQBucket"),
                "finalQBucket": row.get("finalQBucket"),
                "v90Decision": row.get("v90Decision"),
                "dispersion": row.get("dispersion"),
                "pairRadius": (row.get("chosenModel") or {}).get("pairRadius"),
                "lambda": (row.get("chosenModel") or {}).get("lambda"),
                "selectionReason": (row.get("selector") or {}).get("selectionReason"),
                "strictBroadSupportCount": (row.get("selector") or {}).get("strictBroadSupportCount"),
                "unanimousTightEscape": (row.get("selector") or {}).get("unanimousTightEscape"),
                "heldoutPrecisionLift": row.get("heldoutPrecisionLift"),
                "v28HeldoutPrecisionLift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
            }
            if passed and not v28_passed:
                rescues.append(item)
            if v28_passed and not passed:
                regressions.append(item)
            if not passed:
                failures.append(item)
                if phase in bottleneck_set:
                    bottleneck_failures.append(item)

    def count(items, key):
        return dict(Counter(str(x.get(key)) for x in items))

    summary = {
        "regressionCount": len(regressions),
        "rescueCount": len(rescues),
        "failureCount": len(failures),
        "bottleneckFailureCount": len(bottleneck_failures),
        "regressionsByBranch": count(regressions, "branch"),
        "rescuesByBranch": count(rescues, "branch"),
        "bottleneckFailuresByBranch": count(bottleneck_failures, "branch"),
        "regressionsByDecision": count(regressions, "v90Decision"),
        "regressionsByOriginalQBucket": count(regressions, "originalQBucket"),
        "regressionsByPairRadius": count(regressions, "pairRadius"),
        "regressionsByLambda": count(regressions, "lambda"),
        "bottleneckFailuresByDecision": count(bottleneck_failures, "v90Decision"),
        "bottleneckFailuresByPairRadius": count(bottleneck_failures, "pairRadius"),
        "bottleneckFailuresByLambda": count(bottleneck_failures, "lambda"),
    }

    output = {
        "schemaVersion": 94,
        "profileType": "v93-confirmation-failure-anatomy-diagnostic",
        "summary": summary,
        "regressions": regressions,
        "rescues": rescues,
        "bottleneckFailures": bottleneck_failures,
        "v93OutcomesTaintedForFutureSelection": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 94,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "regressionCount": len(regressions),
        "rescueCount": len(rescues),
        "bottleneckFailureCount": len(bottleneck_failures),
        "regressionsByBranch": summary["regressionsByBranch"],
        "bottleneckFailuresByBranch": summary["bottleneckFailuresByBranch"],
        "v93OutcomesTaintedForFutureSelection": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V94 V93 CONFIRMATION FAILURE ANATOMY COMPLETE")
    print("Summary:", summary)
    print("Regression rows:")
    for r in regressions:
        print("Regression:", r)
    print("Bottleneck failure rows:")
    for r in bottleneck_failures:
        print("BottleneckFailure:", r)
    print("V93 outcomes tainted for future selection: True")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
