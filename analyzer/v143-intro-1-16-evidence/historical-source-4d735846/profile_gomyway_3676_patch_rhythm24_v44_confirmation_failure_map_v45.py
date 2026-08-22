from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v43-reserved-1over32-confirmation-v44.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v44-confirmation-failure-map-v45.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v44-confirmation-failure-map-v45-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gate_type(selector: dict) -> str:
    strict = int(selector.get("strictSupportCount", 0))
    soft = int(selector.get("softSupportCount", 0))
    if strict >= 1 and soft >= 2:
        return "strict-and-two-soft"
    if strict >= 1:
        return "strict-only"
    if soft >= 2:
        return "two-soft-only"
    return "anchor"


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = [r for scheme in payload.get("schemes", []) for r in scheme.get("folds", [])]
    if len(rows) != 80:
        raise RuntimeError(f"Expected 80 V44 confirmation rows, found {len(rows)}")

    status_counts = Counter()
    gate_counts = Counter()
    outcome_by_gate: dict[str, Counter] = {}
    changed = []
    failures = []

    for row in rows:
        vp = bool(row.get("passed"))
        bp = bool((row.get("v28Comparison") or {}).get("passed"))
        if vp and bp:
            status = "bothPass"
        elif vp and not bp:
            status = "rescue"
        elif not vp and bp:
            status = "regression"
        else:
            status = "bothFail"
        selector = row.get("selector") or {}
        gt = gate_type(selector)
        status_counts[status] += 1
        gate_counts[gt] += 1
        outcome_by_gate.setdefault(gt, Counter())[status] += 1
        if status in ("rescue", "regression"):
            changed.append({
                "phase": row.get("phase"),
                "fold": row.get("fold"),
                "status": status,
                "gateType": gt,
                "outerQ": row.get("outerQ"),
                "strictSupportCount": selector.get("strictSupportCount"),
                "softSupportCount": selector.get("softSupportCount"),
                "v43Lift": row.get("heldoutPrecisionLift"),
                "v28Lift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
                "v43Held": row.get("heldoutCandidate"),
                "v28Held": (row.get("v28Comparison") or {}).get("heldoutCandidate"),
            })
        if not vp:
            failures.append({
                "phase": row.get("phase"), "fold": row.get("fold"), "gateType": gt,
                "outerQ": row.get("outerQ"), "strictSupportCount": selector.get("strictSupportCount"),
                "softSupportCount": selector.get("softSupportCount"),
                "v28Passed": bp, "v43Lift": row.get("heldoutPrecisionLift"),
                "v28Lift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
            })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V45")

    outcome_json = {k: dict(v) for k, v in outcome_by_gate.items()}
    out = {
        "schemaVersion": 45,
        "profileType": "v44-confirmation-failure-map",
        "diagnosticScope": "already-exposed-v44-1over32-confirmation-only",
        "statusCounts": dict(status_counts),
        "gateCounts": dict(gate_counts),
        "outcomesByGateType": outcome_json,
        "changedOutcomeRows": changed,
        "v43FailureRows": failures,
        "reserved1over32AlreadyConsumed": True,
        "newReserved1over64OddPhasesReferenced": False,
        "newTuningPerformed": False,
        "parameterSearchPerformed": False,
        "heldoutLabelsUsedForDiagnosticComparison": True,
        "requiresTrainingOnlyEvidenceForNextChallenger": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 45,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "statusCounts": dict(status_counts),
        "gateCounts": dict(gate_counts),
        "outcomesByGateType": outcome_json,
        "reserved1over32AlreadyConsumed": True,
        "newReserved1over64OddPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V44 CONFIRMATION FAILURE MAP V45 COMPLETE")
    print("Status counts:", dict(status_counts))
    print("Gate counts:", dict(gate_counts))
    print("Outcomes by gate type:", outcome_json)
    print("Changed outcome rows:", changed)
    print("New reserved 1/64 odd phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
