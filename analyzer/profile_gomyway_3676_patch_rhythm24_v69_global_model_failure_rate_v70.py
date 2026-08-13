from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V57_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json"
V65_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v64-bottleneck-failure-anatomy-v65.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v69-global-model-failure-rate-v70.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v69-global-model-failure-rate-v70-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_key(chosen: dict) -> str:
    return f"r={int(chosen.get('pairRadius'))}|lambda={chosen.get('lambda')}"


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v57 = json.loads(V57_PATH.read_text(encoding="utf-8"))
    v65 = json.loads(V65_PATH.read_text(encoding="utf-8"))
    bottleneck_phases = {float(x) for x in (v65.get("bottleneckPhases") or [])}

    totals = Counter()
    failures = Counter()
    passes = Counter()
    bottleneck_totals = Counter()
    bottleneck_failures = Counter()
    nonbottleneck_totals = Counter()
    nonbottleneck_failures = Counter()
    phase_model = defaultdict(Counter)

    for phase in v57.get("schemes") or []:
        ph = float(phase["phase"])
        for row in phase.get("folds") or []:
            key = model_key(row.get("chosenModel") or {})
            passed = bool(row.get("passed"))
            totals[key] += 1
            passes[key] += int(passed)
            failures[key] += int(not passed)
            phase_model[ph][key] += 1
            if ph in bottleneck_phases:
                bottleneck_totals[key] += 1
                bottleneck_failures[key] += int(not passed)
            else:
                nonbottleneck_totals[key] += 1
                nonbottleneck_failures[key] += int(not passed)

    rates = {}
    for key in sorted(totals):
        n = totals[key]
        bn = bottleneck_totals[key]
        nn = nonbottleneck_totals[key]
        rates[key] = {
            "total": n,
            "passes": passes[key],
            "failures": failures[key],
            "failureRate": failures[key] / n if n else None,
            "bottleneckTotal": bn,
            "bottleneckFailures": bottleneck_failures[key],
            "bottleneckFailureRate": bottleneck_failures[key] / bn if bn else None,
            "nonBottleneckTotal": nn,
            "nonBottleneckFailures": nonbottleneck_failures[key],
            "nonBottleneckFailureRate": nonbottleneck_failures[key] / nn if nn else None,
        }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V70")

    out = {
        "schemaVersion": 70,
        "profileType": "v69-global-model-failure-rate-diagnostic",
        "source": str(V57_PATH.relative_to(ROOT)),
        "bottleneckPhases": sorted(bottleneck_phases),
        "modelFailureRates": rates,
        "phaseModelCounts": {str(k): dict(v) for k, v in phase_model.items()},
        "heldoutOutcomesDiagnosticOnly": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 70,
        "bottleneckPhases": sorted(bottleneck_phases),
        "modelFailureRates": rates,
        "heldoutOutcomesDiagnosticOnly": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V69 GLOBAL MODEL FAILURE-RATE V70 COMPLETE")
    print("Bottleneck phases:", sorted(bottleneck_phases))
    for key, r in sorted(rates.items()):
        print("Model", key,
              "global", f"{r['failures']}/{r['total']}",
              "rate", round(r['failureRate'], 3),
              "bottleneck", f"{r['bottleneckFailures']}/{r['bottleneckTotal']}",
              "nonbottleneck", f"{r['nonBottleneckFailures']}/{r['nonBottleneckTotal']}")
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
