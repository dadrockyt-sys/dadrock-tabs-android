from __future__ import annotations

import hashlib
import json
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V84_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v83-reserved-1over128-confirmation-v84.json"
OUT = PUBLIC / "gomyway-3676-patch-rhythm24-v84-confirmation-floor-failure-anatomy-v85.json"
MANIFEST = PUBLIC / "gomyway-3676-patch-rhythm24-v84-confirmation-floor-failure-anatomy-v85-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate)
    d = json.loads(V84_PATH.read_text(encoding="utf-8"))
    if int(d.get("schemaVersion", -1)) != 84:
        raise RuntimeError("V84 output missing or wrong schema")

    minimum = int(d["minimumPhasePasses"])
    bottlenecks = set(float(x) for x in d.get("bottleneckPhases") or [])
    floor_rows = []
    rescue_rows = []
    failure_rows = []

    for scheme in d.get("schemes") or []:
        phase = float(scheme["phase"])
        for row in scheme.get("folds") or []:
            passed = bool(row.get("passed"))
            base = bool((row.get("v28Comparison") or {}).get("passed"))
            if passed and not base:
                rescue_rows.append({"phase": phase, "fold": int(row["fold"])})
            if not passed:
                failure_rows.append({"phase": phase, "fold": int(row["fold"])})
            if phase in bottlenecks and not passed:
                cm = row.get("chosenModel") or {}
                sel = row.get("selector") or {}
                floor_rows.append({
                    "phase": phase,
                    "fold": int(row["fold"]),
                    "guardAppliedV80": bool(row.get("guardAppliedV80")),
                    "originalQBucket": row.get("originalQBucket"),
                    "finalQBucket": row.get("finalQBucket"),
                    "v80Decision": row.get("v80Decision"),
                    "dispersion": row.get("dispersion"),
                    "pairRadius": cm.get("pairRadius"),
                    "lambda": cm.get("lambda"),
                    "selectionReason": sel.get("selectionReason"),
                    "strictBroadSupportCount": sel.get("strictBroadSupportCount"),
                    "unanimousTightEscape": sel.get("unanimousTightEscape"),
                    "heldoutPrecisionLift": row.get("heldoutPrecisionLift"),
                    "v28Passed": base,
                    "v28HeldoutPrecisionLift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
                })

    after = sha256(candidate)
    if before != after:
        raise RuntimeError("Protected candidate changed during V85")

    out = {
        "schemaVersion": 85,
        "profileType": "v84-confirmation-floor-failure-anatomy-diagnostic",
        "v84Summary": {
            "foldsPassed": d.get("foldsPassed"),
            "foldsTotal": d.get("foldsTotal"),
            "minimumPhasePasses": minimum,
            "bottleneckPhases": sorted(bottlenecks),
            "v28ComparisonPasses": d.get("v28ComparisonPasses"),
            "rescuesVsV28": d.get("rescuesVsV28"),
            "regressionsVsV28": d.get("regressionsVsV28"),
            "confirmationSuccess": d.get("confirmationSuccess"),
        },
        "floorFailureRows": floor_rows,
        "allFailureCount": len(failure_rows),
        "rescueCount": len(rescue_rows),
        "v84OutcomesTaintedForFutureSelection": True,
        "newReservedPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({k: out[k] for k in [
        "schemaVersion", "v84Summary", "allFailureCount", "rescueCount",
        "v84OutcomesTaintedForFutureSelection", "newReservedPhasesReferenced",
        "newTuningPerformed", "validatedNewChampion",
        "protected949CandidateHashUnchanged", "productionPromotionAllowed"
    ]}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V85 V84 CONFIRMATION FLOOR FAILURE ANATOMY COMPLETE")
    print("V84 summary:", out["v84Summary"])
    print("Floor failure rows:")
    for row in floor_rows:
        print(" FloorFailure:", row)
    print("All failures:", len(failure_rows), "Rescues:", len(rescue_rows))
    print("V84 outcomes tainted for future selection: True")
    print("New reserved phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUT.relative_to(ROOT))
    print("Manifest:", MANIFEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
