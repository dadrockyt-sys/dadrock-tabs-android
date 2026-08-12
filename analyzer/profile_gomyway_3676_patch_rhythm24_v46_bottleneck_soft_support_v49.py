from __future__ import annotations

import hashlib
import json
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V46_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v45-strict-support-only-broaden-v46.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v46-bottleneck-soft-support-v49.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v46-bottleneck-soft-support-v49-manifest.json"
BOTTLENECK_PHASE = 0.09375


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(V46_PATH.read_text(encoding="utf-8"))

    rows = []
    soft_hist = {"0": 0, "1": 0, "2": 0, "3": 0}
    failure_soft_hist = {"0": 0, "1": 0, "2": 0, "3": 0}
    outcome_by_soft = {str(i): {"bothPass": 0, "bothFail": 0, "rescue": 0, "regression": 0} for i in range(4)}
    lift_delta_by_soft = {str(i): [] for i in range(4)}

    for scheme in payload.get("schemes", []):
        if abs(float(scheme.get("phase")) - BOTTLENECK_PHASE) > 1e-12:
            continue
        for fold in scheme.get("folds", []):
            selector = fold.get("selector") or {}
            soft = 0
            scheme_details = []
            for s in selector.get("schemes", []):
                ap = int(s.get("anchorPasses", 0))
                bp = int(s.get("broadPasses", 0))
                al = float(s.get("meanAnchorLift", 0.0))
                bl = float(s.get("meanBroadLift", 0.0))
                strict = bool(s.get("strictPassPreferenceForBroad", bp > ap))
                tied_lift = bp == ap and bl > al
                supports = strict or tied_lift
                soft += int(supports)
                scheme_details.append({"scheme": s.get("scheme"), "strict": strict, "tiedLift": tied_lift,
                                       "softSupportsBroad": supports, "anchorPasses": ap, "broadPasses": bp,
                                       "meanAnchorLift": al, "meanBroadLift": bl, "meanLiftDelta": bl - al})
            passed = bool(fold.get("passed"))
            v28p = bool((fold.get("v28Comparison") or {}).get("passed"))
            status = "bothPass" if passed and v28p else "rescue" if passed and not v28p else "regression" if (not passed and v28p) else "bothFail"
            soft_hist[str(soft)] += 1
            outcome_by_soft[str(soft)][status] += 1
            if not passed:
                failure_soft_hist[str(soft)] += 1
            mean_delta = sum(d["meanLiftDelta"] for d in scheme_details) / max(1, len(scheme_details))
            lift_delta_by_soft[str(soft)].append(mean_delta)
            rows.append({"phase": BOTTLENECK_PHASE, "fold": int(fold.get("fold", -1)), "status": status,
                         "strictSupportCount": int(selector.get("strictSupportCount", 0)), "softSupportCount": soft,
                         "outerQ": float(fold.get("outerQ", 0.0)), "passed": passed, "v28Passed": v28p,
                         "heldoutPrecisionLift": fold.get("heldoutPrecisionLift"),
                         "v28Lift": (fold.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
                         "meanTrainingLiftDeltaBroadMinusAnchor": mean_delta,
                         "schemes": scheme_details})

    summaries = {}
    for k, vals in lift_delta_by_soft.items():
        summaries[k] = {"count": len(vals), "mean": (sum(vals)/len(vals) if vals else None),
                        "min": (min(vals) if vals else None), "max": (max(vals) if vals else None)}

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V49")

    out = {"schemaVersion": 49, "profileType": "v46-bottleneck-soft-support-diagnostic",
           "diagnosticScope": "already-exposed-v46-bottleneck-phase-only", "bottleneckPhase": BOTTLENECK_PHASE,
           "softSupportHistogram": soft_hist, "failureSoftSupportHistogram": failure_soft_hist,
           "outcomesBySoftSupport": outcome_by_soft, "trainingLiftDeltaSummaryBySoftSupport": summaries,
           "rows": rows, "newReserved1over64OddPhasesReferenced": False,
           "reservedUntouchedPhasesConsumed": False, "newTuningPerformed": False,
           "heldoutLabelsUsedForDiagnosticComparison": True, "validatedNewChampion": False,
           "protected949CandidateHashUnchanged": before == after, "productionPromotionAllowed": False}
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: out[k] for k in ["schemaVersion","bottleneckPhase","softSupportHistogram","failureSoftSupportHistogram","outcomesBySoftSupport","newReserved1over64OddPhasesReferenced","reservedUntouchedPhasesConsumed","newTuningPerformed","validatedNewChampion","protected949CandidateHashUnchanged","productionPromotionAllowed"]}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V46 BOTTLENECK SOFT SUPPORT V49 COMPLETE")
    print("Soft support histogram:", soft_hist)
    print("Failure soft-support histogram:", failure_soft_hist)
    print("Outcomes by soft support:", outcome_by_soft)
    print("Training lift delta summary by soft support:", summaries)
    print("New reserved 1/64 odd phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

if __name__ == "__main__":
    main()
