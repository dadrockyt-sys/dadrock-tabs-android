from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28
import benchmark_gomyway_3676_patch_rhythm24_v42_strict_or_two_soft_broaden_v43 as v43

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v43-reserved-1over32-confirmation-v44.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v43-reserved-1over32-confirmation-v44-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)
RESERVED_PHASES = (
    0.03125, 0.09375, 0.15625, 0.21875,
    0.28125, 0.34375, 0.40625, 0.46875,
    0.53125, 0.59375, 0.65625, 0.71875,
    0.78125, 0.84375, 0.90625, 0.96875,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows], dtype=np.float64)
    x = np.concatenate([xb, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)

    print("Starting V44 untouched confirmation of frozen V43 architecture", flush=True)
    print("Reserved 1/32 phase family is being consumed now for confirmation", flush=True)
    print("No parameter search or architecture changes are permitted in this run", flush=True)

    schemes = []
    total = v28_total = rescues = regressions = broadened = folds_total = 0
    for phase in RESERVED_PHASES:
        lo, hi = int(np.min(measures)), int(np.max(measures))
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures], dtype=np.int16)
        phase_rows = []
        phase_pass = phase_v28 = 0
        for fold in range(OUTER_FOLDS):
            print(f"phase={phase} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
            test = ids == fold
            train = ~test
            chosen_model = v5.choose_model(x[train], y[train], measures[train])
            radius = int(chosen_model["pairRadius"])
            lam = float(chosen_model["lambda"])

            # Freeze V43 exactly: same training-only selector and fixed q candidates.
            q, selector = v43.choose_q(x[train], y[train], measures[train], radius, lam)
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)
            passed, lift, held, base = v17.pass_at_q(scores, y[test], q)
            vp, vl, vh, _ = v17.pass_at_q(scores, y[test], ANCHOR_Q)

            phase_pass += int(passed)
            phase_v28 += int(vp)
            broadened += int(q > ANCHOR_Q)
            rescues += int(passed and not vp)
            regressions += int(vp and not passed)
            phase_rows.append({
                "phase": float(phase), "fold": int(fold), "chosenModel": chosen_model,
                "selector": selector, "outerQ": float(q), "passed": bool(passed),
                "heldoutPrecisionLift": round(float(lift), 2), "heldoutCandidate": held, "heldoutBase": base,
                "v28Comparison": {"frozenQ": ANCHOR_Q, "passed": bool(vp),
                                   "heldoutPrecisionLift": round(float(vl), 2), "heldoutCandidate": vh},
            })
            print(f"  V44 q={q:.3f} strict={selector['strictSupportCount']}/3 soft={selector['softSupportCount']}/3 pass={passed}; V28 pass={vp}", flush=True)

        schemes.append({"phase": float(phase), "passes": phase_pass, "v28Passes": phase_v28, "folds": phase_rows})
        total += phase_pass
        v28_total += phase_v28
        folds_total += len(phase_rows)

    min_phase = min(s["passes"] for s in schemes)
    # Predeclared confirmation gate mirrors the exploratory gate, now on genuinely untouched data.
    confirmation_success = total > v28_total and min_phase >= 4 and regressions <= rescues
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V44")

    output = {
        "schemaVersion": 44,
        "profileType": "v43-frozen-architecture-reserved-1over32-confirmation",
        "reservedPhases": list(RESERVED_PHASES),
        "reservedUntouchedPhasesConsumed": True,
        "architectureFrozenBeforeConfirmation": True,
        "parameterSearchPerformed": False,
        "outerHeldoutLabelsUsedToChooseParameters": False,
        "foldsPassed": int(total), "foldsTotal": int(folds_total),
        "minimumPhasePasses": int(min_phase), "v28ComparisonPasses": int(v28_total),
        "rescuesVsV28": int(rescues), "regressionsVsV28": int(regressions),
        "foldsBroadenedAboveV28Q": int(broadened),
        "confirmationSuccess": bool(confirmation_success),
        "validatedNewChampion": bool(confirmation_success),
        "schemes": schemes,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 44, "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldsPassed": int(total), "foldsTotal": int(folds_total),
        "minimumPhasePasses": int(min_phase), "v28ComparisonPasses": int(v28_total),
        "rescuesVsV28": int(rescues), "regressionsVsV28": int(regressions),
        "foldsBroadenedAboveV28Q": int(broadened),
        "reservedUntouchedPhasesConsumed": True,
        "architectureFrozenBeforeConfirmation": True,
        "parameterSearchPerformed": False,
        "confirmationSuccess": bool(confirmation_success),
        "validatedNewChampion": bool(confirmation_success),
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V43 RESERVED 1/32 CONFIRMATION V44 COMPLETE")
    print("V44 folds passed:", total, "/", folds_total)
    print("Minimum V44 phase passes:", min_phase, "/ 5")
    print("V28 comparison passes:", v28_total, "/", folds_total)
    print("Rescues vs V28:", rescues)
    print("Regressions vs V28:", regressions)
    print("Folds broadened above V28 q:", broadened)
    print("Confirmation success:", confirmation_success)
    print("Validated new champion:", confirmation_success)
    print("Reserved untouched phases consumed: True")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
