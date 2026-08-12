from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V52_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v51-trainingonly-anchor-hole-escape-v52.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v52-hole-escape-outcome-map-v53.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v52-hole-escape-outcome-map-v53-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm_reason(row: dict) -> str:
    sel = row.get("selector") or {}
    for key in ("reason", "selectionReason", "chosenReason", "decisionReason"):
        if key in sel:
            return str(sel.get(key))
    for key in ("reason", "selectionReason", "chosenReason", "decisionReason"):
        if key in row:
            return str(row.get(key))
    q = float(row.get("outerQ", row.get("chosenQ", 0.2)))
    if q < 0.2 - 1e-12:
        return "tight"
    if q > 0.2 + 1e-12:
        return "broad"
    return "anchor"


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(V52_PATH.read_text(encoding="utf-8"))

    q_counts = Counter()
    reason_counts = Counter()
    outcome_by_reason = defaultdict(lambda: Counter({"bothPass": 0, "bothFail": 0, "rescue": 0, "regression": 0}))
    outcome_by_q = defaultdict(lambda: Counter({"bothPass": 0, "bothFail": 0, "rescue": 0, "regression": 0}))
    changed_from_v46 = Counter()
    phase_rows = defaultdict(list)
    rows = []

    for scheme in payload.get("schemes", []):
        phase = float(scheme.get("phase"))
        for fold in scheme.get("folds", []):
            passed = bool(fold.get("passed"))
            v28p = bool((fold.get("v28Comparison") or {}).get("passed"))
            if passed and v28p:
                status = "bothPass"
            elif passed and not v28p:
                status = "rescue"
            elif (not passed) and v28p:
                status = "regression"
            else:
                status = "bothFail"

            q = float(fold.get("outerQ", fold.get("chosenQ", 0.2)))
            qk = f"{q:.3f}"
            reason = norm_reason(fold)
            q_counts[qk] += 1
            reason_counts[reason] += 1
            outcome_by_reason[reason][status] += 1
            outcome_by_q[qk][status] += 1

            v46 = fold.get("v46Comparison") or {}
            if v46:
                v46p = bool(v46.get("passed"))
                if passed and not v46p:
                    changed_from_v46["rescueVsV46"] += 1
                elif v46p and not passed:
                    changed_from_v46["regressionVsV46"] += 1
                else:
                    changed_from_v46["sameVsV46"] += 1

            entry = {"phase": phase, "fold": int(fold.get("fold", -1)), "statusVsV28": status,
                     "outerQ": q, "reason": reason, "passed": passed, "v28Passed": v28p,
                     "heldoutPrecisionLift": fold.get("heldoutPrecisionLift"),
                     "v28Lift": (fold.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
                     "selector": fold.get("selector")}
            rows.append(entry)
            phase_rows[phase].append(entry)

    phase_summary = []
    for phase in sorted(phase_rows):
        rr = phase_rows[phase]
        phase_summary.append({
            "phase": phase,
            "passes": sum(int(r["passed"]) for r in rr),
            "rescues": sum(int(r["statusVsV28"] == "rescue") for r in rr),
            "regressions": sum(int(r["statusVsV28"] == "regression") for r in rr),
            "qCounts": dict(Counter(f"{r['outerQ']:.3f}" for r in rr)),
            "reasonCounts": dict(Counter(r["reason"] for r in rr)),
        })

    min_pass = min((p["passes"] for p in phase_summary), default=0)
    bottlenecks = [p for p in phase_summary if p["passes"] == min_pass]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V53")

    out = {
        "schemaVersion": 53,
        "profileType": "v52-hole-escape-outcome-diagnostic",
        "qCounts": dict(q_counts),
        "reasonCounts": dict(reason_counts),
        "outcomesByReason": {k: dict(v) for k, v in outcome_by_reason.items()},
        "outcomesByQ": {k: dict(v) for k, v in outcome_by_q.items()},
        "changedFromV46": dict(changed_from_v46),
        "minimumPhasePasses": min_pass,
        "bottleneckPhases": bottlenecks,
        "phaseSummary": phase_summary,
        "rows": rows,
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 53,
        "qCounts": dict(q_counts),
        "reasonCounts": dict(reason_counts),
        "outcomesByReason": {k: dict(v) for k, v in outcome_by_reason.items()},
        "outcomesByQ": {k: dict(v) for k, v in outcome_by_q.items()},
        "changedFromV46": dict(changed_from_v46),
        "minimumPhasePasses": min_pass,
        "bottleneckPhases": bottlenecks,
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V52 HOLE-ESCAPE OUTCOME MAP V53 COMPLETE")
    print("Chosen q counts:", dict(q_counts))
    print("Reason counts:", dict(reason_counts))
    print("Outcomes by reason:", {k: dict(v) for k, v in outcome_by_reason.items()})
    print("Outcomes by q:", {k: dict(v) for k, v in outcome_by_q.items()})
    print("Changed from V46:", dict(changed_from_v46))
    print("Minimum phase passes:", min_pass)
    print("Bottleneck phases:", bottlenecks)
    print("New reserved 1/64 odd phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
