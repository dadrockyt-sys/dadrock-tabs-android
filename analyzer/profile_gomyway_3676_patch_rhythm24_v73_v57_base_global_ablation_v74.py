from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V57_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v73-v57-base-global-ablation-v74.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v73-v57-base-global-ablation-v74-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    v57 = json.loads(V57_PATH.read_text(encoding="utf-8"))
    base_names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    total = full_total = rescues = regressions = 0
    schemes = []
    flip_counts = Counter()

    print("Starting V74 global V57 base-representation ablation", flush=True)
    print("Model radius/lambda frozen from already-exposed V57 rows; q frozen at 0.20", flush=True)

    for scheme in v57.get("schemes") or []:
        phase = float(scheme["phase"])
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        phase_pass = full_phase_pass = 0
        fold_rows = []
        saved_folds = {int(r["fold"]): r for r in (scheme.get("folds") or [])}

        for fold in range(OUTER_FOLDS):
            saved = saved_folds[fold]
            chosen = saved.get("chosenModel") or {}
            radius = int(chosen["pairRadius"])
            lam = float(chosen["lambda"])
            test = ids == fold
            train = ~test

            print(f"phase={phase} fold={fold} base-representation global ablation ...", flush=True)
            model = v2.fit_pairwise_ranker(xb[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(xb[test], model)
            passed, lift, held, base = v1.recurrent.ridge.patch.richer.onset.prof.recall.pass_at_q(scores, y[test], ANCHOR_Q) if False else (None, None, None, None)
            # Use the same pass definition as V17/V28 without importing the V17 phase representation.
            held = v1.select_top_fraction(scores, y[test], ANCHOR_Q)
            base = v1.base_stats(y[test])
            lift = float(held["precision"]) - float(base["precision"])
            passed = bool(held["true"] > 0 and lift >= 5.0)

            full_pass = bool((saved.get("v28Comparison") or {}).get("passed"))
            full_lift = float((saved.get("v28Comparison") or {}).get("heldoutPrecisionLift", 0.0))
            phase_pass += int(passed)
            full_phase_pass += int(full_pass)
            total += int(passed)
            full_total += int(full_pass)
            rescues += int(passed and not full_pass)
            regressions += int(full_pass and not passed)

            if passed and not full_pass:
                flip = "base-rescue"
            elif full_pass and not passed:
                flip = "fullphase-rescue"
            else:
                flip = "same"
            flip_counts[flip] += 1

            fold_rows.append({
                "phase": phase,
                "fold": fold,
                "pairRadius": radius,
                "lambda": lam,
                "basePassed": bool(passed),
                "baseLift": round(float(lift), 2),
                "fullPhaseAnchorPassed": full_pass,
                "fullPhaseAnchorLift": full_lift,
                "flip": flip,
                "baseCandidate": held,
                "heldoutBase": base,
            })

        schemes.append({
            "phase": phase,
            "basePasses": int(phase_pass),
            "fullPhaseAnchorPasses": int(full_phase_pass),
            "folds": fold_rows,
        })

    min_base = min(s["basePasses"] for s in schemes)
    min_full = min(s["fullPhaseAnchorPasses"] for s in schemes)
    bottlenecks = [s["phase"] for s in schemes if s["basePasses"] == min_base]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V74")

    out = {
        "schemaVersion": 74,
        "profileType": "v73-v57-base-global-ablation-diagnostic",
        "diagnosticScope": "already-exposed-v57-1over64-family-only",
        "qFrozen": ANCHOR_Q,
        "modelHyperparametersFrozenFromV57": True,
        "basePasses": int(total),
        "fullPhaseAnchorPasses": int(full_total),
        "rescuesVsFullPhaseAnchor": int(rescues),
        "regressionsVsFullPhaseAnchor": int(regressions),
        "minimumBasePasses": int(min_base),
        "minimumFullPhaseAnchorPasses": int(min_full),
        "baseBottleneckPhases": bottlenecks,
        "flipCounts": dict(flip_counts),
        "schemes": schemes,
        "diagnosticOutcomesTaintedForSelection": True,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    manifest = {k: out[k] for k in [
        "schemaVersion", "qFrozen", "modelHyperparametersFrozenFromV57", "basePasses",
        "fullPhaseAnchorPasses", "rescuesVsFullPhaseAnchor", "regressionsVsFullPhaseAnchor",
        "minimumBasePasses", "minimumFullPhaseAnchorPasses", "baseBottleneckPhases",
        "flipCounts", "diagnosticOutcomesTaintedForSelection",
        "newReserved1over128OddNumeratorPhasesReferenced", "newTuningPerformed",
        "validatedNewChampion", "protected949CandidateHashUnchanged", "productionPromotionAllowed"
    ]}
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V73 V57 BASE GLOBAL ABLATION V74 COMPLETE")
    print("Base representation passes:", total, "/ 160")
    print("Full-phase anchor passes:", full_total, "/ 160")
    print("Rescues vs full-phase anchor:", rescues)
    print("Regressions vs full-phase anchor:", regressions)
    print("Minimum base passes:", min_base, "/ 5")
    print("Minimum full-phase anchor passes:", min_full, "/ 5")
    print("Base bottleneck phases:", bottlenecks)
    print("Flip counts:", dict(flip_counts))
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
