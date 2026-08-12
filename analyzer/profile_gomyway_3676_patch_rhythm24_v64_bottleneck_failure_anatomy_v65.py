from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v64-bottleneck-failure-anatomy-v65.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v64-bottleneck-failure-anatomy-v65-manifest.json"

TIGHT_Q = 0.175
ANCHOR_Q = 0.20
BROAD_Q = 0.225
TIGHT_STD_MIN = 0.50
BROAD_STD_MAX = 0.90


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lift_std(selector: dict[str, Any], side: str) -> float | None:
    vals = []
    for s in selector.get("schemes") or []:
        anchor = s.get("meanAnchorLift")
        other = s.get("meanTightLift") if side == "tight" else s.get("meanBroadLift")
        if anchor is None or other is None:
            return None
        vals.append(float(other) - float(anchor))
    if len(vals) < 2:
        return None
    return float(statistics.pstdev(vals))


def branch(q: float) -> str:
    if abs(q - TIGHT_Q) < 1e-12:
        return "tight"
    if abs(q - BROAD_Q) < 1e-12:
        return "broad"
    return "anchor"


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    src = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    phase_rows = []
    failures = []
    all_rows = []
    after_branch_counts = Counter()

    for phase in src.get("schemes") or []:
        ph = float(phase["phase"])
        passes = 0
        rows = []
        for row in phase.get("folds") or []:
            old_pass = bool(row.get("passed"))
            v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
            q = float(row.get("outerQ", ANCHOR_Q))
            selector = row.get("selector") or {}
            old_branch = branch(q)
            new_pass = old_pass
            new_branch = old_branch
            decision = "keep-current"
            std = None

            if old_branch == "tight":
                std = lift_std(selector, "tight")
                if std is None:
                    raise RuntimeError("Missing tight dispersion inputs")
                if std < TIGHT_STD_MIN:
                    new_pass = v28_pass
                    new_branch = "anchor"
                    decision = "revert-tight-to-anchor-low-dispersion"
                else:
                    decision = "keep-tight-high-dispersion"
            elif old_branch == "broad":
                std = lift_std(selector, "broad")
                if std is None:
                    raise RuntimeError("Missing broad dispersion inputs")
                if std > BROAD_STD_MAX:
                    new_pass = v28_pass
                    new_branch = "anchor"
                    decision = "revert-broad-to-anchor-high-dispersion"
                else:
                    decision = "keep-broad-low-dispersion"

            after_branch_counts[new_branch] += 1
            passes += int(new_pass)
            compact = {
                "phase": ph,
                "fold": int(row.get("fold", -1)),
                "oldBranch": old_branch,
                "newBranch": new_branch,
                "decision": decision,
                "oldQ": q,
                "dispersion": std,
                "newPass": bool(new_pass),
                "v28Pass": bool(v28_pass),
                "strictBroadSupportCount": selector.get("strictBroadSupportCount"),
                "unanimousTightEscape": selector.get("unanimousTightEscape"),
                "selectionReason": selector.get("selectionReason"),
                "schemes": selector.get("schemes") or [],
                "heldoutPrecisionLift": row.get("heldoutPrecisionLift"),
                "v28HeldoutPrecisionLift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
            }
            rows.append(compact)
            all_rows.append(compact)
            if not new_pass:
                failures.append(compact)
        phase_rows.append({"phase": ph, "passes": passes, "rows": rows})

    min_phase = min(x["passes"] for x in phase_rows)
    bottleneck_phases = [x["phase"] for x in phase_rows if x["passes"] == min_phase]
    bottleneck_failures = [x for x in failures if x["phase"] in bottleneck_phases]

    fail_branch_counts = Counter(x["newBranch"] for x in bottleneck_failures)
    fail_decision_counts = Counter(x["decision"] for x in bottleneck_failures)
    fail_strict_counts = Counter(str(x.get("strictBroadSupportCount")) for x in bottleneck_failures)
    fail_unanimous_counts = Counter(str(x.get("unanimousTightEscape")) for x in bottleneck_failures)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V65")

    out = {
        "schemaVersion": 65,
        "profileType": "v64-dual-gate-bottleneck-failure-anatomy",
        "source": str(SOURCE_PATH.relative_to(ROOT)),
        "fixedTightStdMinimum": TIGHT_STD_MIN,
        "fixedBroadStdMaximum": BROAD_STD_MAX,
        "minimumPhasePasses": min_phase,
        "bottleneckPhases": bottleneck_phases,
        "bottleneckFailureCount": len(bottleneck_failures),
        "bottleneckFailureBranchCounts": dict(fail_branch_counts),
        "bottleneckFailureDecisionCounts": dict(fail_decision_counts),
        "bottleneckFailureStrictSupportCounts": dict(fail_strict_counts),
        "bottleneckFailureUnanimousTightCounts": dict(fail_unanimous_counts),
        "bottleneckFailures": bottleneck_failures,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "heldoutLabelsDiagnosticOnly": True,
        "protected949CandidateHashUnchanged": before == after,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 65,
        "minimumPhasePasses": min_phase,
        "bottleneckPhases": bottleneck_phases,
        "bottleneckFailureCount": len(bottleneck_failures),
        "bottleneckFailureBranchCounts": dict(fail_branch_counts),
        "bottleneckFailureDecisionCounts": dict(fail_decision_counts),
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "protected949CandidateHashUnchanged": before == after,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V64 BOTTLENECK FAILURE ANATOMY V65 COMPLETE")
    print("Minimum phase passes:", min_phase)
    print("Bottleneck phases:", bottleneck_phases)
    print("Bottleneck failure count:", len(bottleneck_failures))
    print("Failure branches after V64 gate:", dict(fail_branch_counts))
    print("Failure decisions:", dict(fail_decision_counts))
    print("Failure strict-support counts:", dict(fail_strict_counts))
    print("Failure unanimous-tight counts:", dict(fail_unanimous_counts))
    for x in bottleneck_failures:
        print("Failure:", {k: x[k] for k in ["phase","fold","oldBranch","newBranch","decision","dispersion","strictBroadSupportCount","unanimousTightEscape","selectionReason","heldoutPrecisionLift","v28HeldoutPrecisionLift"]})
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
