from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE = PUBLIC / "gomyway-3676-patch-rhythm24-v57-confirmation-failure-map-v58.json"
OUTPUT = PUBLIC / "gomyway-3676-patch-rhythm24-v58-changed-outcome-branch-summary-v59.json"
MANIFEST = PUBLIC / "gomyway-3676-patch-rhythm24-v58-changed-outcome-branch-summary-v59-manifest.json"


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    d = json.loads(SOURCE.read_text(encoding="utf-8"))

    changed = list(d.get("changedOutcomes") or [])
    bottlenecks = list(d.get("bottleneckPhases") or [])
    outcomes_by_branch = d.get("outcomesByBranch") or {}
    outcomes_by_reason = d.get("outcomesByReason") or {}

    branch_changed = Counter()
    reason_changed = Counter()
    phase_changed = Counter()
    strict_support_changed = Counter()
    unanimous_escape_changed = Counter()

    compact = []
    for r in changed:
        status = str(r.get("status"))
        branch = str(r.get("branch"))
        reason = str(r.get("reason"))
        phase = r.get("phase")
        fold = r.get("fold")
        sel = r.get("selector") or {}
        branch_changed[(branch, status)] += 1
        reason_changed[(reason, status)] += 1
        phase_changed[(phase, status)] += 1
        strict_support_changed[(int(sel.get("strictBroadSupportCount", 0)), status)] += 1
        unanimous_escape_changed[(bool(sel.get("unanimousTightEscape", False)), status)] += 1
        compact.append({
            "phase": phase,
            "fold": fold,
            "status": status,
            "branch": branch,
            "reason": reason,
            "outerQ": r.get("outerQ"),
            "heldoutPrecisionLift": r.get("heldoutPrecisionLift"),
            "v28HeldoutPrecisionLift": r.get("v28HeldoutPrecisionLift"),
            "strictBroadSupportCount": int(sel.get("strictBroadSupportCount", 0)),
            "unanimousTightEscape": bool(sel.get("unanimousTightEscape", False)),
        })

    out = {
        "schemaVersion": 59,
        "profileType": "v58-changed-outcome-branch-summary",
        "source": str(SOURCE.relative_to(ROOT)),
        "outcomesByBranch": outcomes_by_branch,
        "outcomesByReason": outcomes_by_reason,
        "bottleneckPhases": bottlenecks,
        "changedOutcomeCount": len(changed),
        "branchChangedSummary": {f"{k[0]}|{k[1]}": v for k, v in sorted(branch_changed.items())},
        "reasonChangedSummary": {f"{k[0]}|{k[1]}": v for k, v in sorted(reason_changed.items())},
        "phaseChangedSummary": {f"{k[0]}|{k[1]}": v for k, v in sorted(phase_changed.items(), key=lambda x: (float(x[0][0]), x[0][1]))},
        "strictSupportChangedSummary": {f"{k[0]}|{k[1]}": v for k, v in sorted(strict_support_changed.items())},
        "unanimousEscapeChangedSummary": {f"{k[0]}|{k[1]}": v for k, v in sorted(unanimous_escape_changed.items())},
        "changedOutcomes": compact,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "schemaVersion": 59,
        "changedOutcomeCount": len(changed),
        "bottleneckPhases": bottlenecks,
        "branchChangedSummary": out["branchChangedSummary"],
        "reasonChangedSummary": out["reasonChangedSummary"],
        "strictSupportChangedSummary": out["strictSupportChangedSummary"],
        "unanimousEscapeChangedSummary": out["unanimousEscapeChangedSummary"],
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V58 CHANGED-OUTCOME BRANCH SUMMARY V59 COMPLETE")
    print("Outcomes by branch:", outcomes_by_branch)
    print("Outcomes by reason:", outcomes_by_reason)
    print("Bottleneck phases:", bottlenecks)
    print("Changed outcome count:", len(changed))
    print("Changed outcomes by branch/status:", out["branchChangedSummary"])
    print("Changed outcomes by reason/status:", out["reasonChangedSummary"])
    print("Changed outcomes by strict-support/status:", out["strictSupportChangedSummary"])
    print("Changed outcomes by unanimous-escape/status:", out["unanimousEscapeChangedSummary"])
    for r in compact:
        print("Changed:", r)
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Manifest:", MANIFEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
