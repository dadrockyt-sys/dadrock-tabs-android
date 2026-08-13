from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V57_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v78-v57-cosine-only-phase-global-v79.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v78-v57-cosine-only-phase-global-v79-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
Q = float(v28.FROZEN_Q)
# V17 phase feature order: p2-sin, p2-cos, p4-sin, p4-cos.
# V79 keeps only the two cosine terms after V75 showed p2-sin globally redundant
# and p4-sin globally harmful on the already-exposed V57 family.
KEEP = [1, 3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pass_at_q(scores: np.ndarray, yy: np.ndarray):
    held = v1.select_top_fraction(scores, yy, Q)
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    passed = bool(held["true"] > 0 and lift >= 5.0)
    return passed, lift, held, base


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
    pf = v17.phase_features(rows)
    x = np.concatenate([xb, pf[:, KEEP]], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    total = full_total = rescues = regressions = 0
    phase_rows = []
    flips = Counter()

    print("Starting V79 cosine-only phase global diagnostic on already-exposed V57 family", flush=True)
    print("Representation: base + p2-cos + p4-cos; V57 radius/lambda frozen; q frozen at 0.20", flush=True)

    for scheme in v57.get("schemes") or []:
        phase = float(scheme["phase"])
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        saved_folds = {int(r["fold"]): r for r in (scheme.get("folds") or [])}
        phase_pass = full_phase_pass = 0

        for fold in range(OUTER_FOLDS):
            saved = saved_folds[fold]
            chosen = saved.get("chosenModel") or {}
            radius = int(chosen["pairRadius"])
            lam = float(chosen["lambda"])
            test = ids == fold
            train = ~test

            print(f"phase={phase} fold={fold} V79 cosine-only global ...", flush=True)
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            passed, lift, held, base = pass_at_q(v2.scores_for(x[test], model), y[test])

            cmp = saved.get("v28Comparison") or {}
            full_pass = bool(cmp.get("passed"))
            full_lift = float(cmp.get("heldoutPrecisionLift", 0.0))

            total += int(passed)
            full_total += int(full_pass)
            phase_pass += int(passed)
            full_phase_pass += int(full_pass)
            rescues += int(passed and not full_pass)
            regressions += int(full_pass and not passed)

            if passed and not full_pass:
                flip = "cosine-rescue"
            elif full_pass and not passed:
                flip = "fullphase-rescue"
            else:
                flip = "same"
            flips[flip] += 1

        phase_rows.append({
            "phase": phase,
            "cosineOnlyPasses": int(phase_pass),
            "fullPhaseAnchorPasses": int(full_phase_pass),
        })

    min_cos = min(r["cosineOnlyPasses"] for r in phase_rows)
    min_full = min(r["fullPhaseAnchorPasses"] for r in phase_rows)
    bottlenecks = [r["phase"] for r in phase_rows if r["cosineOnlyPasses"] == min_cos]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V79")

    out = {
        "schemaVersion": 79,
        "profileType": "v78-v57-cosine-only-phase-global-diagnostic",
        "diagnosticScope": "already-exposed-v57-1over64-family-only",
        "representation": "base+p2-cos+p4-cos",
        "qFrozen": Q,
        "modelHyperparametersFrozenFromV57": True,
        "cosineOnlyPasses": int(total),
        "fullPhaseAnchorPasses": int(full_total),
        "rescuesVsFullPhaseAnchor": int(rescues),
        "regressionsVsFullPhaseAnchor": int(regressions),
        "minimumCosineOnlyPhasePasses": int(min_cos),
        "minimumFullPhaseAnchorPasses": int(min_full),
        "cosineOnlyBottleneckPhases": bottlenecks,
        "flipCounts": dict(flips),
        "phaseRows": phase_rows,
        "diagnosticOutcomesTaintedForSelection": True,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: out[k] for k in [
        "schemaVersion", "representation", "qFrozen", "modelHyperparametersFrozenFromV57",
        "cosineOnlyPasses", "fullPhaseAnchorPasses", "rescuesVsFullPhaseAnchor",
        "regressionsVsFullPhaseAnchor", "minimumCosineOnlyPhasePasses",
        "minimumFullPhaseAnchorPasses", "cosineOnlyBottleneckPhases", "flipCounts",
        "diagnosticOutcomesTaintedForSelection", "newReserved1over128OddNumeratorPhasesReferenced",
        "newTuningPerformed", "validatedNewChampion", "protected949CandidateHashUnchanged",
        "productionPromotionAllowed"
    ]}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V79 COSINE-ONLY PHASE GLOBAL DIAGNOSTIC COMPLETE")
    print("Cosine-only representation passes:", total, "/ 160")
    print("Full-phase anchor passes:", full_total, "/ 160")
    print("Rescues vs full-phase anchor:", rescues)
    print("Regressions vs full-phase anchor:", regressions)
    print("Minimum cosine-only phase passes:", min_cos, "/ 5")
    print("Minimum full-phase anchor passes:", min_full, "/ 5")
    print("Cosine-only bottleneck phases:", bottlenecks)
    print("Flip counts:", dict(flips))
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
