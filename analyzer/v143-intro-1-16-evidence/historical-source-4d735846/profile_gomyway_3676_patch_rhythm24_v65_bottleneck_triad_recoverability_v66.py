from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V65_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v64-bottleneck-failure-anatomy-v65.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v65-bottleneck-triad-recoverability-v66.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v65-bottleneck-triad-recoverability-v66-manifest.json"

EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
TRIAD_QS = (0.175, 0.20, 0.225)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(source.get("candidateSlots") or [])
    if not rows or tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    v65 = json.loads(V65_PATH.read_text(encoding="utf-8"))
    failures = list(v65.get("bottleneckFailures") or [])
    if not failures:
        raise RuntimeError("No V65 bottleneck failures found")

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows], dtype=np.float64)
    x = np.concatenate([xb, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    diagnostics = []
    recoverability = Counter()

    for item in failures:
        phase = float(item["phase"])
        fold = int(item["fold"])
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        test = ids == fold
        train = ~test
        print(f"phase={phase} fold={fold} triad diagnostic ...", flush=True)

        chosen_model = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)

        q_rows = []
        passing = []
        for q in TRIAD_QS:
            passed, lift, held, base = v17.pass_at_q(scores, y[test], q)
            q_rows.append({
                "q": q,
                "passed": bool(passed),
                "heldoutPrecisionLift": round(float(lift), 2),
                "heldoutCandidate": held,
                "heldoutBase": base,
            })
            if passed:
                passing.append(q)

        if len(passing) == 0:
            cls = "none-pass"
        elif len(passing) == 3:
            cls = "all-three-pass"
        elif passing == [0.175]:
            cls = "tight-only"
        elif passing == [0.20]:
            cls = "anchor-only"
        elif passing == [0.225]:
            cls = "broad-only"
        elif set(passing) == {0.175, 0.20}:
            cls = "tight-and-anchor"
        elif set(passing) == {0.20, 0.225}:
            cls = "anchor-and-broad"
        elif set(passing) == {0.175, 0.225}:
            cls = "neighbors-only-anchor-hole"
        else:
            cls = "other"
        recoverability[cls] += 1

        diagnostics.append({
            "phase": phase,
            "fold": fold,
            "v64NewBranch": item.get("newBranch"),
            "v64Decision": item.get("decision"),
            "v64Dispersion": item.get("dispersion"),
            "strictBroadSupportCount": item.get("strictBroadSupportCount"),
            "unanimousTightEscape": item.get("unanimousTightEscape"),
            "chosenModel": chosen_model,
            "triad": q_rows,
            "passingQs": passing,
            "recoverabilityClass": cls,
        })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V66")

    out = {
        "schemaVersion": 66,
        "profileType": "v65-bottleneck-triad-recoverability-diagnostic",
        "diagnosticScope": "already-exposed-v57-family-v64-bottleneck-failures-only",
        "diagnosticQs": list(TRIAD_QS),
        "bottleneckFailureCount": len(failures),
        "recoverabilityCounts": dict(recoverability),
        "diagnostics": diagnostics,
        "heldoutLabelsUsedForDiagnosticTriad": True,
        "diagnosticOutcomesTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 66,
        "bottleneckFailureCount": len(failures),
        "recoverabilityCounts": dict(recoverability),
        "heldoutLabelsUsedForDiagnosticTriad": True,
        "diagnosticOutcomesTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V65 BOTTLENECK TRIAD RECOVERABILITY V66 COMPLETE")
    print("Bottleneck failure count:", len(failures))
    print("Recoverability counts:", dict(recoverability))
    for d in diagnostics:
        print("Failure", d["phase"], "fold", d["fold"], "V64", d["v64NewBranch"], d["v64Decision"],
              "=>", d["recoverabilityClass"], "passing q:", d["passingQs"])
    print("Diagnostic outcomes tainted for selection: True")
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
