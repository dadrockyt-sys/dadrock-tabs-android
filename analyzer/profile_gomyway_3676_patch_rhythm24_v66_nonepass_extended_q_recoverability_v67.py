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
V66_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v65-bottleneck-triad-recoverability-v66.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v66-nonepass-extended-q-recoverability-v67.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v66-nonepass-extended-q-recoverability-v67-manifest.json"

EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = 0.20
DIAGNOSTIC_QS = tuple(round(float(q), 3) for q in np.arange(0.05, 0.401, 0.025))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(source.get("candidateSlots") or [])
    if not rows or tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    v66 = json.loads(V66_PATH.read_text(encoding="utf-8"))
    nonepass = [d for d in (v66.get("diagnostics") or []) if d.get("recoverabilityClass") == "none-pass"]
    if not nonepass:
        raise RuntimeError("No V66 none-pass bottleneck failures found")

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows], dtype=np.float64)
    x = np.concatenate([xb, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    diagnostics = []
    recovery_counts = Counter()

    for item in nonepass:
        phase = float(item["phase"])
        fold = int(item["fold"])
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        test = ids == fold
        train = ~test
        print(f"phase={phase} fold={fold} extended-q diagnostic ...", flush=True)

        chosen_model = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)

        q_rows = []
        passing = []
        for q in DIAGNOSTIC_QS:
            passed, lift, held, base = v17.pass_at_q(scores, y[test], float(q))
            q_rows.append({
                "q": float(q),
                "passed": bool(passed),
                "heldoutPrecisionLift": round(float(lift), 2),
                "heldoutCandidate": held,
                "heldoutBase": base,
            })
            if passed:
                passing.append(float(q))

        if not passing:
            cls = "none-pass-extended"
            passing_range = None
        else:
            passing_range = [min(passing), max(passing)]
            tighter = any(q < 0.175 - 1e-12 for q in passing)
            broader = any(q > 0.225 + 1e-12 for q in passing)
            inside = any(0.175 - 1e-12 <= q <= 0.225 + 1e-12 for q in passing)
            if tighter and not broader and not inside:
                cls = "recover-tighter-outside-triad"
            elif broader and not tighter and not inside:
                cls = "recover-broader-outside-triad"
            elif not inside:
                cls = "recover-outside-triad-mixed"
            else:
                cls = "recover-including-triad-grid-point"
        recovery_counts[cls] += 1

        diagnostics.append({
            "phase": phase,
            "fold": fold,
            "v64NewBranch": item.get("v64NewBranch"),
            "v64Decision": item.get("v64Decision"),
            "chosenModel": chosen_model,
            "passingQCount": len(passing),
            "passingQRange": passing_range,
            "recoveryClass": cls,
            "qSweep": q_rows,
        })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V67")

    out = {
        "schemaVersion": 67,
        "profileType": "v66-nonepass-extended-q-recoverability-diagnostic",
        "diagnosticScope": "already-exposed-v57-v64-bottleneck-nonepass-folds-only",
        "diagnosticQGrid": list(DIAGNOSTIC_QS),
        "nonePassFoldCount": len(nonepass),
        "recoveryCounts": dict(recovery_counts),
        "diagnostics": diagnostics,
        "heldoutLabelsUsedForDiagnosticSweep": True,
        "diagnosticQValuesTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 67,
        "nonePassFoldCount": len(nonepass),
        "recoveryCounts": dict(recovery_counts),
        "heldoutLabelsUsedForDiagnosticSweep": True,
        "diagnosticQValuesTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V66 NONE-PASS EXTENDED-Q RECOVERABILITY V67 COMPLETE")
    print("None-pass fold count:", len(nonepass))
    print("Recovery counts:", dict(recovery_counts))
    for d in diagnostics:
        print("Failure", d["phase"], "fold", d["fold"], "=>", d["recoveryClass"], "passing q range:", d["passingQRange"])
    print("Diagnostic q values tainted for selection: True")
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
