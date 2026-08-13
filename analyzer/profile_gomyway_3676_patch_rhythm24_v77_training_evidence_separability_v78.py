from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V77_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v76-changed-flip-training-rep-evidence-v77.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v77-training-evidence-separability-v78.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v77-training-evidence-separability-v78-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(V77_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("rows") or [])
    if not rows:
        raise RuntimeError("V77 rows missing")

    # Predeclared, simple training-only guards. These are diagnostic on already-exposed outcomes;
    # no rule here is eligible for validation without a fresh untouched family.
    guards = {
        "betterSchemes_eq_0": lambda r: int(r["dropBetterSchemeCount"]) == 0,
        "betterSchemes_le_1": lambda r: int(r["dropBetterSchemeCount"]) <= 1,
        "nonWorseSchemes_ge_2": lambda r: int(r["dropNonWorseSchemeCount"]) >= 2,
        "nonWorseSchemes_eq_3": lambda r: int(r["dropNonWorseSchemeCount"]) == 3,
        "liftBetterSchemes_ge_2": lambda r: int(r["dropLiftBetterSchemeCount"]) >= 2,
        "innerPassDelta_ge_0": lambda r: int(r["totalInnerPassDeltaDropMinusFull"]) >= 0,
        "meanLiftDelta_gt_0": lambda r: float(r["meanSchemeLiftDeltaDropMinusFull"]) > 0.0,
        "better0_and_nonWorse2plus": lambda r: int(r["dropBetterSchemeCount"]) == 0 and int(r["dropNonWorseSchemeCount"]) >= 2,
        "betterLe1_and_nonWorse2plus": lambda r: int(r["dropBetterSchemeCount"]) <= 1 and int(r["dropNonWorseSchemeCount"]) >= 2,
        "better0_and_meanLiftPositive": lambda r: int(r["dropBetterSchemeCount"]) == 0 and float(r["meanSchemeLiftDeltaDropMinusFull"]) > 0.0,
    }

    exact = Counter()
    for r in rows:
        key = (
            str(r["status"]),
            int(r["dropBetterSchemeCount"]),
            int(r["dropNonWorseSchemeCount"]),
            int(r["dropLiftBetterSchemeCount"]),
            int(r["totalInnerPassDeltaDropMinusFull"]),
            round(float(r["meanSchemeLiftDeltaDropMinusFull"]), 3),
        )
        exact[key] += 1

    guard_rows = []
    for name, fn in guards.items():
        kept = [r for r in rows if fn(r)]
        counts = Counter(str(r["status"]) for r in kept)
        rescues = int(counts.get("rescue", 0))
        regressions = int(counts.get("regression", 0))
        guard_rows.append({
            "guard": name,
            "kept": len(kept),
            "rescuesKept": rescues,
            "regressionsKept": regressions,
            "netChangedOutcomeGain": rescues - regressions,
            "changedRowsKept": [
                {
                    "phase": float(r["phase"]),
                    "fold": int(r["fold"]),
                    "status": str(r["status"]),
                    "dropBetterSchemeCount": int(r["dropBetterSchemeCount"]),
                    "dropNonWorseSchemeCount": int(r["dropNonWorseSchemeCount"]),
                    "dropLiftBetterSchemeCount": int(r["dropLiftBetterSchemeCount"]),
                    "totalInnerPassDeltaDropMinusFull": int(r["totalInnerPassDeltaDropMinusFull"]),
                    "meanSchemeLiftDeltaDropMinusFull": float(r["meanSchemeLiftDeltaDropMinusFull"]),
                }
                for r in kept
            ],
        })

    guard_rows.sort(key=lambda x: (x["regressionsKept"], -x["rescuesKept"], -x["netChangedOutcomeGain"], x["kept"]))
    perfect = [g for g in guard_rows if g["regressionsKept"] == 0 and g["rescuesKept"] > 0]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V78")

    out = {
        "schemaVersion": 78,
        "profileType": "v77-training-evidence-separability-diagnostic",
        "diagnosticScope": "13 already-exposed V76 changed folds only",
        "changedFoldCount": len(rows),
        "statusCounts": dict(Counter(str(r["status"]) for r in rows)),
        "exactTrainingEvidencePatterns": {str(k): int(v) for k, v in exact.items()},
        "predeclaredGuardResults": guard_rows,
        "zeroRegressionGuards": [g["guard"] for g in perfect],
        "diagnosticOutcomesTaintedForSelection": True,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    manifest = {k: out[k] for k in [
        "schemaVersion", "changedFoldCount", "statusCounts", "zeroRegressionGuards",
        "diagnosticOutcomesTaintedForSelection", "newReserved1over128OddNumeratorPhasesReferenced",
        "newTuningPerformed", "validatedNewChampion", "protected949CandidateHashUnchanged",
        "productionPromotionAllowed"
    ]}
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V78 TRAINING-EVIDENCE SEPARABILITY COMPLETE")
    print("Changed fold count:", len(rows))
    print("Status counts:", dict(Counter(str(r["status"]) for r in rows)))
    print("Guard results:")
    for g in guard_rows:
        print(f"  {g['guard']}: kept={g['kept']} rescues={g['rescuesKept']} regressions={g['regressionsKept']} net={g['netChangedOutcomeGain']}")
    print("Zero-regression guards:", [g["guard"] for g in perfect])
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
