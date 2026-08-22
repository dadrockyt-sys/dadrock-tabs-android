from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V128_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v128-failure-anatomy-v129.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v128-failure-anatomy-v129-manifest.json"


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

    v128 = json.loads(V128_PATH.read_text(encoding="utf-8"))
    if int(v128.get("schemaVersion", -1)) != 128:
        raise RuntimeError("V128 output missing or wrong schema")
    if not bool(v128.get("validatedNewChampion")):
        raise RuntimeError("V128 must be a validated confirmation")
    if int(v128.get("v128Passes", -1)) != 309 or int(v128.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V128 does not match frozen 309/320 guarded champion result")

    rows = []
    for scheme in v128.get("schemes") or []:
        phase = float(scheme.get("phase"))
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r.setdefault("phase", phase)
            rows.append(r)
    if len(rows) != 320:
        raise RuntimeError(f"Expected 320 V128 rows, got {len(rows)}")

    failures = [r for r in rows if not bool(r.get("v128Passed"))]
    if len(failures) != 11:
        raise RuntimeError(f"Expected 11 V128 failures, got {len(failures)}")

    by_structural = Counter()
    by_rep = Counter()
    by_selected = Counter()
    by_policy_applied = Counter()
    by_guard_applied = Counter()
    by_phase = Counter()
    relation = Counter()
    structural_details = defaultdict(lambda: {"failures": 0, "rows": 0, "passes": 0})

    for r in rows:
        key = structural_key(r)
        structural_details[key]["rows"] += 1
        structural_details[key]["passes"] += int(bool(r.get("v128Passed")))

    failure_rows = []
    for r in failures:
        key = structural_key(r)
        by_structural[key] += 1
        by_rep[str(r.get("finalRepresentation"))] += 1
        by_selected[bool(r.get("selectedForV112"))] += 1
        by_policy_applied[bool(r.get("structuralPolicyApplied"))] += 1
        by_guard_applied[bool(r.get("v127GuardApplied"))] += 1
        by_phase[float(r.get("phase"))] += 1
        structural_details[key]["failures"] += 1

        states = {
            "v122": bool(r.get("v122Passed")),
            "v118": bool(r.get("v118Passed")),
            "v96": bool(r.get("v96Passed")),
            "v28": bool(r.get("v28Passed")),
        }
        for name, passed in states.items():
            relation[f"regression_vs_{name}"] += int(passed)
            relation[f"shared_failure_vs_{name}"] += int(not passed)

        failure_rows.append({
            "phase": float(r.get("phase")),
            "fold": int(r.get("fold")),
            "gateScore": r.get("gateScore"),
            "originalQBucket": key[0],
            "v96Decision": key[1],
            "pairRadius": key[2],
            "lambda": key[3],
            "selectedForV112": bool(r.get("selectedForV112")),
            "structuralPolicyApplied": bool(r.get("structuralPolicyApplied")),
            "structuralRepresentation": r.get("structuralRepresentation"),
            "v127GuardApplied": bool(r.get("v127GuardApplied")),
            "finalRepresentation": r.get("finalRepresentation"),
            "v28Passed": bool(r.get("v28Passed")),
            "v96Passed": bool(r.get("v96Passed")),
            "v115Passed": bool(r.get("v115Passed")),
            "v118Passed": bool(r.get("v118Passed")),
            "v122Passed": bool(r.get("v122Passed")),
            "v128Passed": bool(r.get("v128Passed")),
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

    bottlenecks = [float(x) for x in (v128.get("v128BottleneckPhases") or [])]
    bottleneck_rows = [r for r in failure_rows if float(r["phase"]) in bottlenecks]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V129")

    summary = {
        "foldsTotal": 320,
        "v128Passes": 309,
        "v128ScorePercent": 96.5625,
        "failureCount": len(failures),
        "failuresWhereV122Passed": int(relation["regression_vs_v122"]),
        "failuresWhereV118Passed": int(relation["regression_vs_v118"]),
        "failuresWhereV96Passed": int(relation["regression_vs_v96"]),
        "failuresWhereV28Passed": int(relation["regression_vs_v28"]),
        "sharedHardFailuresVsV122": int(relation["shared_failure_vs_v122"]),
        "sharedHardFailuresVsV118": int(relation["shared_failure_vs_v118"]),
        "failuresInsideStructuralPolicy": int(by_policy_applied[True]),
        "failuresOutsideStructuralPolicy": int(by_policy_applied[False]),
        "failuresWhereV127GuardApplied": int(by_guard_applied[True]),
        "failuresWhereV127GuardNotApplied": int(by_guard_applied[False]),
        "failuresSelectedForV112": int(by_selected[True]),
        "failuresNotSelectedForV112": int(by_selected[False]),
        "bottleneckPhases": bottlenecks,
        "bottleneckFailureRows": len(bottleneck_rows),
    }

    out = {
        "schemaVersion": 129,
        "profileType": "v128-guarded-champion-failure-anatomy-diagnostic",
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

    print("GOMYWAY V129 V128 FAILURE ANATOMY DIAGNOSTIC COMPLETE")
    print("Frozen guarded champion: 309/320 = 96.5625%")
    print(f"Remaining failures: {len(failures)}")
    print(f"Failures where V122 passed: {summary['failuresWhereV122Passed']}")
    print(f"Failures where V118 passed: {summary['failuresWhereV118Passed']}")
    print(f"Failures where V96 passed: {summary['failuresWhereV96Passed']}")
    print(f"Failures where V28 passed: {summary['failuresWhereV28Passed']}")
    print(f"Shared hard failures vs V122: {summary['sharedHardFailuresVsV122']}")
    print(f"Shared hard failures vs V118: {summary['sharedHardFailuresVsV118']}")
    print(f"Failures inside/outside structural policy: {summary['failuresInsideStructuralPolicy']}/{summary['failuresOutsideStructuralPolicy']}")
    print(f"Failures where V127 guard applied/not applied: {summary['failuresWhereV127GuardApplied']}/{summary['failuresWhereV127GuardNotApplied']}")
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
