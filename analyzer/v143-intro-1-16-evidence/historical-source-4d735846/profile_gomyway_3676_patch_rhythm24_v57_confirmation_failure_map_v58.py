from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v57-confirmation-failure-map-v58.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v57-confirmation-failure-map-v58-manifest.json"

TIGHT_Q = 0.175
ANCHOR_Q = 0.20
BROAD_Q = 0.225


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q_branch(q: float) -> str:
    if abs(q - TIGHT_Q) < 1e-12:
        return "tight"
    if abs(q - BROAD_Q) < 1e-12:
        return "broad"
    return "anchor"


def status(row: dict) -> str:
    p = bool(row.get("passed"))
    vp = bool((row.get("v28Comparison") or {}).get("passed"))
    if p and vp:
        return "bothPass"
    if p and not vp:
        return "rescue"
    if (not p) and vp:
        return "regression"
    return "bothFail"


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Missing V57 output: {SOURCE_PATH}")
    src = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    by_branch = defaultdict(Counter)
    by_reason = defaultdict(Counter)
    phase_rows = []
    changed = []
    all_rows = []

    for phase in src.get("schemes") or []:
        ph = float(phase["phase"])
        passes = 0
        v28passes = 0
        rescues = 0
        regressions = 0
        qcounts = Counter()
        reasoncounts = Counter()

        for row in phase.get("folds") or []:
            st = status(row)
            q = float(row.get("outerQ", ANCHOR_Q))
            branch = q_branch(q)
            selector = row.get("selector") or {}
            reason = str(selector.get("selectionReason") or branch)
            by_branch[branch][st] += 1
            by_reason[reason][st] += 1
            qcounts[branch] += 1
            reasoncounts[reason] += 1
            passes += int(bool(row.get("passed")))
            v28passes += int(bool((row.get("v28Comparison") or {}).get("passed")))
            rescues += int(st == "rescue")
            regressions += int(st == "regression")

            compact = {
                "phase": ph,
                "fold": int(row.get("fold", -1)),
                "status": st,
                "branch": branch,
                "outerQ": q,
                "reason": reason,
                "heldoutPrecisionLift": row.get("heldoutPrecisionLift"),
                "v28HeldoutPrecisionLift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
                "selector": selector,
            }
            all_rows.append(compact)
            if st in ("rescue", "regression"):
                changed.append(compact)

        phase_rows.append({
            "phase": ph,
            "passes": passes,
            "v28Passes": v28passes,
            "rescues": rescues,
            "regressions": regressions,
            "qBranchCounts": dict(qcounts),
            "reasonCounts": dict(reasoncounts),
        })

    min_phase = min(r["passes"] for r in phase_rows)
    bottlenecks = [r for r in phase_rows if r["passes"] == min_phase]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V58")

    out = {
        "schemaVersion": 58,
        "profileType": "v57-confirmation-failure-map",
        "sourceConfirmationSuccess": bool(src.get("confirmationSuccess")),
        "sourceValidatedNewChampion": bool(src.get("validatedNewChampion")),
        "sourceFoldsPassed": src.get("foldsPassed"),
        "sourceFoldsTotal": src.get("foldsTotal"),
        "sourceV28ComparisonPasses": src.get("v28ComparisonPasses"),
        "minimumPhasePasses": min_phase,
        "outcomesByBranch": {k: dict(v) for k, v in by_branch.items()},
        "outcomesByReason": {k: dict(v) for k, v in by_reason.items()},
        "bottleneckPhases": bottlenecks,
        "changedOutcomeRows": changed,
        "phaseSummary": phase_rows,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "heldoutLabelsDiagnosticOnly": True,
        "protected949CandidateHashUnchanged": before == after,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 58,
        "sourceFoldsPassed": src.get("foldsPassed"),
        "sourceFoldsTotal": src.get("foldsTotal"),
        "sourceV28ComparisonPasses": src.get("v28ComparisonPasses"),
        "minimumPhasePasses": min_phase,
        "outcomesByBranch": {k: dict(v) for k, v in by_branch.items()},
        "bottleneckPhases": bottlenecks,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "protected949CandidateHashUnchanged": before == after,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V57 CONFIRMATION FAILURE MAP V58 COMPLETE")
    print("Outcomes by branch:", {k: dict(v) for k, v in by_branch.items()})
    print("Outcomes by reason:", {k: dict(v) for k, v in by_reason.items()})
    print("Minimum phase passes:", min_phase)
    print("Bottleneck phases:", bottlenecks)
    print("Changed outcomes:", changed)
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
