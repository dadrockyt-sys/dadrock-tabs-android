from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V124_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v122-reserved-5mod16-over1024-confirmation-v124.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v124-failure-anatomy-v125.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v124-failure-anatomy-v125-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def structural_key(row: dict) -> tuple[str, str, int, float]:
    model = row.get("chosenModel") or {}
    return (
        str(row.get("originalQBucket")),
        str(row.get("v96Decision")),
        int(model.get("pairRadius")),
        float(model.get("lambda")),
    )


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v124 = json.loads(V124_PATH.read_text(encoding="utf-8"))
    if int(v124.get("schemaVersion", -1)) != 124:
        raise RuntimeError("V124 output missing or wrong schema")
    if not bool(v124.get("validatedNewChampion")):
        raise RuntimeError("V124 must be a validated confirmation")
    if int(v124.get("v122Passes", -1)) != 308 or int(v124.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V124 does not match frozen 308/320 champion result")

    rows = []
    for scheme in v124.get("schemes") or []:
        phase = float(scheme.get("phase"))
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r.setdefault("phase", phase)
            rows.append(r)
    if len(rows) != 320:
        raise RuntimeError(f"Expected 320 V124 rows, got {len(rows)}")

    failures = [r for r in rows if not bool(r.get("v122Passed"))]
    if len(failures) != 12:
        raise RuntimeError(f"Expected 12 V122 failures, got {len(failures)}")

    by_structural = Counter()
    by_rep = Counter()
    by_selected = Counter()
    by_policy_applied = Counter()
    by_phase = Counter()
    relation = Counter()
    structural_details = defaultdict(lambda: {"failures": 0, "rows": 0, "passes": 0})

    for r in rows:
        key = structural_key(r)
        structural_details[key]["rows"] += 1
        structural_details[key]["passes"] += int(bool(r.get("v122Passed")))

    failure_rows = []
    for r in failures:
        key = structural_key(r)
        by_structural[key] += 1
        by_rep[str(r.get("finalRepresentation"))] += 1
        by_selected[bool(r.get("selectedForV112"))] += 1
        by_policy_applied[bool(r.get("structuralPolicyApplied"))] += 1
        by_phase[float(r.get("phase"))] += 1
        structural_details[key]["failures"] += 1

        v118 = bool(r.get("v118Passed"))
        v96 = bool(r.get("v96Passed"))
        v28 = bool(r.get("v28Passed"))
        if v118:
            relation["regression_vs_v118"] += 1
        else:
            relation["shared_failure_vs_v118"] += 1
        if v96:
            relation["regression_vs_v96"] += 1
        else:
            relation["shared_failure_vs_v96"] += 1
        if v28:
            relation["regression_vs_v28"] += 1
        else:
            relation["shared_failure_vs_v28"] += 1

        failure_rows.append({
            "phase": float(r.get("phase")),
            "fold": int(r.get("fold")),
            "originalQBucket": key[0],
            "v96Decision": key[1],
            "pairRadius": key[2],
            "lambda": key[3],
            "selectedForV112": bool(r.get("selectedForV112")),
            "structuralPolicyApplied": bool(r.get("structuralPolicyApplied")),
            "structuralRepresentation": r.get("structuralRepresentation"),
            "finalRepresentation": r.get("finalRepresentation"),
            "v28Passed": bool(r.get("v28Passed")),
            "v96Passed": bool(r.get("v96Passed")),
            "v115Passed": bool(r.get("v115Passed")),
            "v118Passed": bool(r.get("v118Passed")),
            "heldoutPrecisionLift": r.get("heldoutPrecisionLift"),
        })

    structural_summary = []
    for key, d in structural_details.items():
        if d["failures"] <= 0:
            continue
        structural_summary.append({
            "originalQBucket": key[0],
            "v96Decision": key[1],
            "pairRadius": key[2],
            "lambda": key[3],
            "rows": int(d["rows"]),
            "passes": int(d["passes"]),
            "failures": int(d["failures"]),
            "failureRate": round(d["failures"] / d["rows"], 6),
        })
    structural_summary.sort(key=lambda x: (-x["failures"], -x["failureRate"], x["originalQBucket"], x["v96Decision"]))

    bottlenecks = [float(x) for x in (v124.get("v122BottleneckPhases") or [])]
    bottleneck_rows = [r for r in failure_rows if float(r["phase"]) in bottlenecks]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V125")

    summary = {
        "foldsTotal": 320,
        "v122Passes": 308,
        "v122ScorePercent": 96.25,
        "failureCount": len(failures),
        "failuresWhereV118Passed": int(relation["regression_vs_v118"]),
        "failuresWhereV96Passed": int(relation["regression_vs_v96"]),
        "failuresWhereV28Passed": int(relation["regression_vs_v28"]),
        "sharedHardFailuresVsV118": int(relation["shared_failure_vs_v118"]),
        "failuresInsideStructuralPolicy": int(by_policy_applied[True]),
        "failuresOutsideStructuralPolicy": int(by_policy_applied[False]),
        "failuresSelectedForV112": int(by_selected[True]),
        "failuresNotSelectedForV112": int(by_selected[False]),
        "bottleneckPhases": bottlenecks,
        "bottleneckFailureRows": len(bottleneck_rows),
    }

    out = {
        "schemaVersion": 125,
        "profileType": "v124-v122-confirmation-failure-anatomy-diagnostic",
        "summary": summary,
        "failureCountsByRepresentation": dict(by_rep),
        "failureCountsByPhase": {str(k): int(v) for k, v in sorted(by_phase.items())},
        "topFailureStructuralSignatures": structural_summary,
        "failureRows": failure_rows,
        "bottleneckFailureRows": bottleneck_rows,
        "heldoutLabelsUsedForDiagnosisOnly": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "candidatePolicyChanged": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k not in {"failureRows", "bottleneckFailureRows"}}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V125 V124 FAILURE ANATOMY DIAGNOSTIC COMPLETE")
    print(f"Frozen V122 champion: 308/320 = 96.2500%")
    print(f"Remaining failures: {len(failures)}")
    print(f"Failures where V118 passed: {summary['failuresWhereV118Passed']}")
    print(f"Failures where V96 passed: {summary['failuresWhereV96Passed']}")
    print(f"Failures where V28 passed: {summary['failuresWhereV28Passed']}")
    print(f"Shared hard failures vs V118: {summary['sharedHardFailuresVsV118']}")
    print(f"Failures inside structural policy: {summary['failuresInsideStructuralPolicy']}")
    print(f"Failures outside structural policy: {summary['failuresOutsideStructuralPolicy']}")
    print(f"Failures selected/not selected for V112: {summary['failuresSelectedForV112']}/{summary['failuresNotSelectedForV112']}")
    print("\n=== TOP FAILURE STRUCTURAL SIGNATURES ===")
    for r in structural_summary[:12]:
        print(r)
    print("\n=== FAILURE REPRESENTATIONS ===")
    for k, v in by_rep.most_common():
        print(f"{k}: {v}")
    print("\n=== BOTTLENECK FAILURE ROWS ===")
    for r in bottleneck_rows:
        print(r)
    print("\nHeld-out labels used for diagnosis only: True")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
