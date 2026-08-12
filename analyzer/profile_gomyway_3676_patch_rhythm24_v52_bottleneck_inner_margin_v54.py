from __future__ import annotations

import hashlib
import json
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V52_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v51-trainingonly-anchor-hole-escape-v52.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v52-bottleneck-inner-margin-v54.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v52-bottleneck-inner-margin-v54-manifest.json"
BOTTLENECK_PHASE = 0.09375


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(V52_PATH.read_text(encoding="utf-8"))

    rows = []
    outcome_by_pattern = {}
    for phase in payload.get("schemes", []):
        if abs(float(phase.get("phase")) - BOTTLENECK_PHASE) > 1e-12:
            continue
        for fold in phase.get("folds", []):
            sel = fold.get("selector") or {}
            agg = sel.get("aggregateInnerPasses") or {}
            tight = int(agg.get("tight", 0))
            anchor = int(agg.get("anchor", 0))
            broad = int(agg.get("broad", 0))
            reason = str(sel.get("selectionReason", "unknown"))
            passed = bool(fold.get("passed"))
            v28p = bool((fold.get("v28Comparison") or {}).get("passed"))
            status = "bothPass" if passed and v28p else "rescue" if passed and not v28p else "regression" if (not passed and v28p) else "bothFail"
            pattern = f"T{tight}-A{anchor}-B{broad}"
            outcome_by_pattern.setdefault(pattern, {"bothPass": 0, "bothFail": 0, "rescue": 0, "regression": 0})
            outcome_by_pattern[pattern][status] += 1
            scheme_rows = []
            for s in sel.get("schemes", []):
                scheme_rows.append({
                    "scheme": s.get("scheme"),
                    "tightPasses": int(s.get("tightPasses", 0)),
                    "anchorPasses": int(s.get("anchorPasses", 0)),
                    "broadPasses": int(s.get("broadPasses", 0)),
                    "meanTightLift": float(s.get("meanTightLift", 0.0)),
                    "meanAnchorLift": float(s.get("meanAnchorLift", 0.0)),
                    "meanBroadLift": float(s.get("meanBroadLift", 0.0)),
                    "strictBroadSupport": bool(s.get("strictBroadSupport", False)),
                })
            rows.append({
                "phase": BOTTLENECK_PHASE,
                "fold": int(fold.get("fold", -1)),
                "status": status,
                "passed": passed,
                "v28Passed": v28p,
                "outerQ": float(fold.get("outerQ", 0.0)),
                "selectionReason": reason,
                "trainingAnchorHoleDetected": bool(sel.get("trainingAnchorHoleDetected", False)),
                "strictBroadSupportCount": int(sel.get("strictBroadSupportCount", 0)),
                "aggregateInnerPasses": {"tight": tight, "anchor": anchor, "broad": broad},
                "tightMinusAnchor": tight - anchor,
                "broadMinusAnchor": broad - anchor,
                "bestNeighborMinusAnchor": max(tight, broad) - anchor,
                "pattern": pattern,
                "heldoutPrecisionLift": fold.get("heldoutPrecisionLift"),
                "v28Lift": (fold.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
                "schemes": scheme_rows,
            })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V54")

    out = {
        "schemaVersion": 54,
        "profileType": "v52-bottleneck-inner-margin-diagnostic",
        "diagnosticScope": "already-exposed-v52-bottleneck-phase-only",
        "bottleneckPhase": BOTTLENECK_PHASE,
        "rows": rows,
        "outcomesByAggregatePattern": outcome_by_pattern,
        "heldoutLabelsUsedForDiagnosticComparison": True,
        "newTuningPerformed": False,
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 54,
        "bottleneckPhase": BOTTLENECK_PHASE,
        "outcomesByAggregatePattern": outcome_by_pattern,
        "newTuningPerformed": False,
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V52 BOTTLENECK INNER-MARGIN V54 COMPLETE")
    for r in rows:
        print(
            "Fold", r["fold"],
            "status:", r["status"],
            "q:", r["outerQ"],
            "reason:", r["selectionReason"],
            "inner(T,A,B):", (
                r["aggregateInnerPasses"]["tight"],
                r["aggregateInnerPasses"]["anchor"],
                r["aggregateInnerPasses"]["broad"],
            ),
            "neighbor-margin:", r["bestNeighborMinusAnchor"],
        )
    print("Outcomes by aggregate pattern:", outcome_by_pattern)
    print("New reserved 1/64 odd phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
