from __future__ import annotations

import hashlib
import json
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V50_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v46-bottleneck-operating-point-direction-v50.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v50-anchor-hole-structure-v51.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v50-anchor-hole-structure-v51-manifest.json"
ANCHOR_Q = 0.20


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contiguous_runs(rows, passed_value: bool):
    runs = []
    start = prev = None
    for r in rows:
        q = float(r["q"])
        matches = bool(r["passed"]) == passed_value
        if matches and start is None:
            start = prev = q
        elif matches:
            prev = q
        elif start is not None:
            runs.append([start, prev])
            start = prev = None
    if start is not None:
        runs.append([start, prev])
    return runs


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(V50_PATH.read_text(encoding="utf-8"))

    rows = []
    anchor_hole_count = 0
    pass_on_both_sides_count = 0
    for d in payload.get("diagnostics", []):
        sweep = sorted(d.get("qSweep", []), key=lambda r: float(r["q"]))
        pass_runs = contiguous_runs(sweep, True)
        fail_runs = contiguous_runs(sweep, False)
        anchor_row = min(sweep, key=lambda r: abs(float(r["q"]) - ANCHOR_Q))
        lower_pass = [float(r["q"]) for r in sweep if float(r["q"]) < ANCHOR_Q and bool(r["passed"])]
        upper_pass = [float(r["q"]) for r in sweep if float(r["q"]) > ANCHOR_Q and bool(r["passed"])]
        both_sides = bool(lower_pass and upper_pass)
        anchor_hole = (not bool(anchor_row["passed"])) and both_sides
        pass_on_both_sides_count += int(both_sides)
        anchor_hole_count += int(anchor_hole)

        nearest_lower = max(lower_pass) if lower_pass else None
        nearest_upper = min(upper_pass) if upper_pass else None
        rows.append({
            "phase": d.get("phase"),
            "fold": d.get("fold"),
            "anchorPassed": bool(anchor_row["passed"]),
            "anchorLift": anchor_row.get("lift"),
            "passingRuns": pass_runs,
            "failingRuns": fail_runs,
            "passesOnBothSidesOfAnchor": both_sides,
            "anchorIsolatedFailureHole": anchor_hole,
            "nearestPassingQBelowAnchor": nearest_lower,
            "nearestPassingQAboveAnchor": nearest_upper,
            "nearestPassingDistanceBelow": (ANCHOR_Q - nearest_lower if nearest_lower is not None else None),
            "nearestPassingDistanceAbove": (nearest_upper - ANCHOR_Q if nearest_upper is not None else None),
            "qSweep": sweep,
        })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V51")

    out = {
        "schemaVersion": 51,
        "profileType": "v50-anchor-hole-structure-diagnostic",
        "diagnosticScope": "already-exposed-v50-q-sweeps-only",
        "anchorQ": ANCHOR_Q,
        "diagnosticFoldCount": len(rows),
        "passOnBothSidesOfAnchorCount": pass_on_both_sides_count,
        "anchorIsolatedFailureHoleCount": anchor_hole_count,
        "rows": rows,
        "v50DiagnosticQValuesRemainTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 51,
        "diagnosticFoldCount": len(rows),
        "passOnBothSidesOfAnchorCount": pass_on_both_sides_count,
        "anchorIsolatedFailureHoleCount": anchor_hole_count,
        "v50DiagnosticQValuesRemainTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V50 ANCHOR-HOLE STRUCTURE V51 COMPLETE")
    print("Diagnostic folds:", len(rows))
    print("Pass on both sides of anchor:", pass_on_both_sides_count)
    print("Anchor isolated failure holes:", anchor_hole_count)
    for r in rows:
        print("Fold", r["fold"], "pass runs:", r["passingRuns"], "fail runs:", r["failingRuns"],
              "anchorHole:", r["anchorIsolatedFailureHole"])
    print("V50 diagnostic q values remain tainted for selection: True")
    print("New reserved 1/64 odd phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
