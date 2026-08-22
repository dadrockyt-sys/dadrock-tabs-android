from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v45-strict-support-only-broaden-v46.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v46-bottleneck-failure-anatomy-v48.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v46-bottleneck-failure-anatomy-v48-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    schemes = list(payload.get("schemes") or [])
    if not schemes:
        raise RuntimeError("V46 result missing schemes")

    min_passes = min(int(s.get("passes", 0)) for s in schemes)
    bottlenecks = [s for s in schemes if int(s.get("passes", 0)) == min_passes]

    failure_rows = []
    outcome_by_strict = defaultdict(Counter)
    chosen_q_counts = Counter()
    v28_relation = Counter()

    for scheme in bottlenecks:
        phase = float(scheme["phase"])
        for row in scheme.get("folds") or []:
            selector = row.get("selector") or {}
            strict_count = int(selector.get("strictSupportCount", 0))
            passed = bool(row.get("passed"))
            v28_passed = bool((row.get("v28Comparison") or {}).get("passed"))
            status = "bothPass" if passed and v28_passed else "rescue" if passed else "regression" if v28_passed else "bothFail"
            outcome_by_strict[str(strict_count)][status] += 1
            chosen_q_counts[str(row.get("outerQ"))] += 1
            v28_relation[status] += 1
            if not passed:
                held = row.get("heldoutCandidate") or {}
                v28held = (row.get("v28Comparison") or {}).get("heldoutCandidate") or {}
                failure_rows.append({
                    "phase": phase,
                    "fold": int(row.get("fold", -1)),
                    "strictSupportCount": strict_count,
                    "outerQ": row.get("outerQ"),
                    "v46Lift": row.get("heldoutPrecisionLift"),
                    "v28Lift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
                    "v28Passed": v28_passed,
                    "v46Held": held,
                    "v28Held": v28held,
                    "selectedDeltaVsV28": int(held.get("selected", 0)) - int(v28held.get("selected", 0)),
                    "trueDeltaVsV28": int(held.get("true", 0)) - int(v28held.get("true", 0)),
                    "falseDeltaVsV28": int(held.get("false", 0)) - int(v28held.get("false", 0)),
                })

    failure_strict_hist = Counter(str(r["strictSupportCount"]) for r in failure_rows)
    failure_q_hist = Counter(str(r["outerQ"]) for r in failure_rows)
    selected_delta_hist = Counter(str(r["selectedDeltaVsV28"]) for r in failure_rows)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V48")

    output = {
        "schemaVersion": 48,
        "profileType": "v46-bottleneck-failure-anatomy",
        "diagnosticScope": "already-exposed-v46-phases-only",
        "minimumPhasePasses": min_passes,
        "bottleneckPhases": [float(s["phase"]) for s in bottlenecks],
        "bottleneckCount": len(bottlenecks),
        "failureCount": len(failure_rows),
        "failureStrictSupportHistogram": dict(sorted(failure_strict_hist.items())),
        "failureChosenQHistogram": dict(sorted(failure_q_hist.items())),
        "failureSelectedDeltaVsV28Histogram": dict(sorted(selected_delta_hist.items())),
        "outcomesByStrictSupport": {k: dict(v) for k, v in sorted(outcome_by_strict.items())},
        "bottleneckOutcomeVsV28": dict(v28_relation),
        "bottleneckChosenQCounts": dict(chosen_q_counts),
        "failures": failure_rows,
        "newReserved1over64OddPhasesReferenced": False,
        "newTuningPerformed": False,
        "heldoutLabelsUsedForDiagnosticComparison": True,
        "requiresTrainingOnlyEvidenceForNextChallenger": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 48,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "minimumPhasePasses": min_passes,
        "bottleneckPhases": output["bottleneckPhases"],
        "failureCount": len(failure_rows),
        "failureStrictSupportHistogram": output["failureStrictSupportHistogram"],
        "failureChosenQHistogram": output["failureChosenQHistogram"],
        "failureSelectedDeltaVsV28Histogram": output["failureSelectedDeltaVsV28Histogram"],
        "newReserved1over64OddPhasesReferenced": False,
        "newTuningPerformed": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V46 BOTTLENECK FAILURE ANATOMY V48 COMPLETE")
    print("Bottleneck phases:", output["bottleneckPhases"])
    print("Failure count:", len(failure_rows))
    print("Failure strict-support histogram:", output["failureStrictSupportHistogram"])
    print("Failure chosen-q histogram:", output["failureChosenQHistogram"])
    print("Failure selected-delta-vs-V28 histogram:", output["failureSelectedDeltaVsV28Histogram"])
    print("Outcomes by strict support:", output["outcomesByStrictSupport"])
    print("New reserved 1/64 odd phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
