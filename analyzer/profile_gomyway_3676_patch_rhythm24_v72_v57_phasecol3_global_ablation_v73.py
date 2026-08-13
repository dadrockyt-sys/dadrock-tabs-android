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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v72-v57-phasecol3-global-ablation-v73.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v72-v57-phasecol3-global-ablation-v73-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)
PHASE_COL = 3  # V17 columns: p2 sin, p2 cos, p4 sin, p4 cos; col3 is p4 cosine.


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
    pf = v17.phase_features(rows)
    if pf.shape[1] != 4:
        raise RuntimeError(f"Expected 4 V17 phase features, got {pf.shape[1]}")
    x_col3 = np.concatenate([xb, pf[:, [PHASE_COL]]], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    total = full_total = rescues = regressions = 0
    schemes = []
    flip_counts = Counter()

    print("Starting V73 global V57 ablation of V17 phase column 3 (period-4 cosine)", flush=True)
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

            print(f"phase={phase} fold={fold} phase-col3 global ablation ...", flush=True)
            model = v2.fit_pairwise_ranker(x_col3[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x_col3[test], model)
            passed, lift, held, base = v17.pass_at_q(scores, y[test], ANCHOR_Q)

            full_pass = bool((saved.get("v28Comparison") or {}).get("passed"))
            full_lift = float((saved.get("v28Comparison") or {}).get("heldoutPrecisionLift", 0.0))
            phase_pass += int(passed)
            full_phase_pass += int(full_pass)
            total += int(passed)
            full_total += int(full_pass)
            rescues += int(passed and not full_pass)
            regressions += int(full_pass and not passed)

            if passed and not full_pass:
                flip = "col3-rescue"
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
                "phaseCol3Passed": bool(passed),
                "phaseCol3Lift": round(float(lift), 2),
                "fullPhaseAnchorPassed": full_pass,
                "fullPhaseAnchorLift": full_lift,
                "flip": flip,
                "phaseCol3Candidate": held,
                "heldoutBase": base,
            })

        schemes.append({
            "phase": phase,
            "phaseCol3Passes": int(phase_pass),
            "fullPhaseAnchorPasses": int(full_phase_pass),
            "folds": fold_rows,
        })

    min_col3 = min(s["phaseCol3Passes"] for s in schemes)
    min_full = min(s["fullPhaseAnchorPasses"] for s in schemes)
    bottlenecks = [s["phase"] for s in schemes if s["phaseCol3Passes"] == min_col3]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V73")

    out = {
        "schemaVersion": 73,
        "profileType": "v72-v57-phasecol3-global-ablation-diagnostic",
        "diagnosticScope": "already-exposed-v57-1over64-family-only",
        "phaseColumnIndex": PHASE_COL,
        "phaseColumnMeaning": "cos(2*pi*(step mod 4)/4)",
        "qFrozen": ANCHOR_Q,
        "modelHyperparametersFrozenFromV57": True,
        "phaseCol3Passes": int(total),
        "fullPhaseAnchorPasses": int(full_total),
        "rescuesVsFullPhaseAnchor": int(rescues),
        "regressionsVsFullPhaseAnchor": int(regressions),
        "minimumPhaseCol3Passes": int(min_col3),
        "minimumFullPhaseAnchorPasses": int(min_full),
        "phaseCol3BottleneckPhases": bottlenecks,
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
        "schemaVersion", "phaseColumnIndex", "phaseColumnMeaning", "qFrozen",
        "modelHyperparametersFrozenFromV57", "phaseCol3Passes", "fullPhaseAnchorPasses",
        "rescuesVsFullPhaseAnchor", "regressionsVsFullPhaseAnchor", "minimumPhaseCol3Passes",
        "minimumFullPhaseAnchorPasses", "phaseCol3BottleneckPhases", "flipCounts",
        "diagnosticOutcomesTaintedForSelection", "newReserved1over128OddNumeratorPhasesReferenced",
        "newTuningPerformed", "validatedNewChampion", "protected949CandidateHashUnchanged",
        "productionPromotionAllowed"
    ]}
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V72 V57 PHASE-COL3 GLOBAL ABLATION V73 COMPLETE")
    print("Phase column 3 meaning: cos(2*pi*(step mod 4)/4)")
    print("Phase-col3 passes:", total, "/", full_total + sum(1 for _ in []) if False else 160)
    print("Full-phase anchor passes:", full_total, "/ 160")
    print("Rescues vs full-phase anchor:", rescues)
    print("Regressions vs full-phase anchor:", regressions)
    print("Minimum phase-col3 passes:", min_col3, "/ 5")
    print("Minimum full-phase anchor passes:", min_full, "/ 5")
    print("Phase-col3 bottleneck phases:", bottlenecks)
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
