from __future__ import annotations

import hashlib
import json
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V52_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v51-trainingonly-anchor-hole-escape-v52.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v52-bottleneck-scheme-signature-v55.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v52-bottleneck-scheme-signature-v55-manifest.json"
BOTTLENECK_PHASE = 0.09375


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(V52_PATH.read_text(encoding="utf-8"))

    rows = []
    for phase_row in payload.get("schemes", []):
        if abs(float(phase_row.get("phase")) - BOTTLENECK_PHASE) > 1e-12:
            continue
        for fold in phase_row.get("folds", []):
            selector = fold.get("selector") or {}
            passed = bool(fold.get("passed"))
            v28_passed = bool((fold.get("v28Comparison") or {}).get("passed"))
            status = "bothPass" if passed and v28_passed else "rescue" if passed and not v28_passed else "regression" if (not passed and v28_passed) else "bothFail"
            scheme_rows = []
            for s in selector.get("schemes", []):
                tight = int(s.get("tightPasses", 0))
                anchor = int(s.get("anchorPasses", 0))
                broad = int(s.get("broadPasses", 0))
                tight_lift = float(s.get("meanTightLift", 0.0))
                anchor_lift = float(s.get("meanAnchorLift", 0.0))
                broad_lift = float(s.get("meanBroadLift", 0.0))
                scheme_rows.append({
                    "scheme": s.get("scheme"),
                    "passes": {"tight": tight, "anchor": anchor, "broad": broad},
                    "lift": {"tight": tight_lift, "anchor": anchor_lift, "broad": broad_lift},
                    "tightMinusAnchorPasses": tight - anchor,
                    "broadMinusAnchorPasses": broad - anchor,
                    "tightMinusAnchorLift": tight_lift - anchor_lift,
                    "broadMinusAnchorLift": broad_lift - anchor_lift,
                })
            rows.append({
                "fold": int(fold.get("fold", -1)),
                "status": status,
                "outerQ": float(fold.get("outerQ", 0.0)),
                "selectionReason": selector.get("selectionReason"),
                "aggregateInnerPasses": selector.get("aggregateInnerPasses"),
                "strictBroadSupportCount": int(selector.get("strictBroadSupportCount", 0)),
                "trainingAnchorHoleDetected": bool(selector.get("trainingAnchorHoleDetected", False)),
                "schemes": scheme_rows,
            })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V55")

    out = {
        "schemaVersion": 55,
        "profileType": "v52-bottleneck-scheme-signature-diagnostic",
        "diagnosticScope": "already-exposed-v52-bottleneck-phase-only",
        "bottleneckPhase": BOTTLENECK_PHASE,
        "rows": rows,
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "newTuningPerformed": False,
        "heldoutLabelsUsedForDiagnosticComparison": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 55,
        "bottleneckPhase": BOTTLENECK_PHASE,
        "rowCount": len(rows),
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V52 BOTTLENECK SCHEME SIGNATURE V55 COMPLETE")
    for row in rows:
        print(f"Fold {row['fold']} status={row['status']} q={row['outerQ']:.3f} reason={row['selectionReason']} strict={row['strictBroadSupportCount']} hole={row['trainingAnchorHoleDetected']}")
        for s in row['schemes']:
            p = s['passes']; l = s['lift']
            print(f"  {s['scheme']}: passes(T,A,B)=({p['tight']},{p['anchor']},{p['broad']}) dPass(T-A,B-A)=({s['tightMinusAnchorPasses']},{s['broadMinusAnchorPasses']}) dLift(T-A,B-A)=({s['tightMinusAnchorLift']:.3f},{s['broadMinusAnchorLift']:.3f})")
    print("New reserved 1/64 odd phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
