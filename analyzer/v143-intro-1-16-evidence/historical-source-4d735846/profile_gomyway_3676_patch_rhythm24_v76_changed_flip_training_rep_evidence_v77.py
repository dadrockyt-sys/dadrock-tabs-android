from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v28_exact_anchor_unanimous_training_tighten_v38 as v38
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V57_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json"
V76_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v75-drop-p4sin-flip-anatomy-v76.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v76-changed-flip-training-rep-evidence-v77.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v76-changed-flip-training-rep-evidence-v77-manifest.json"
EXPECTED = (272, 595, 341)
INNER_FOLDS = 4
INNER_SCHEMES = ("normal", "section", "shiftedWindow")
Q = float(v28.FROZEN_Q)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pass_at_q(scores: np.ndarray, yy: np.ndarray):
    held = v1.select_top_fraction(scores, yy, Q)
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    return bool(held["true"] > 0 and lift >= 5.0), float(lift)


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    v57 = json.loads(V57_PATH.read_text(encoding="utf-8"))
    v76 = json.loads(V76_PATH.read_text(encoding="utf-8"))

    base_names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows], dtype=np.float64)
    pf = v17.phase_features(rows)
    x_full = np.concatenate([xb, pf], axis=1)
    x_drop = np.concatenate([xb, pf[:, [0, 1, 3]]], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)

    # Reconstruct outer train masks from saved V57 schemes; held-out labels are never used to form training evidence.
    scheme_lookup = {float(s["phase"]): s for s in (v57.get("schemes") or [])}
    status_summary = Counter()
    rows_out = []

    print("Starting V77 training-only representation evidence on V76 changed folds", flush=True)
    print("Comparing full V17 phase representation vs drop-p4-sin inside outer-training data only", flush=True)

    for ch in (v76.get("changedOutcomes") or []):
        phase = float(ch["phase"])
        fold = int(ch["fold"])
        status = str(ch["status"])
        s = scheme_lookup[phase]
        saved = {int(r["fold"]): r for r in (s.get("folds") or [])}[fold]
        chosen = saved.get("chosenModel") or {}
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])

        # Use saved outer fold membership through the exact phase/fold row's heldout base mask definition indirectly
        # by reconstructing with the same phased-fold helper imported by V57 through saved indices is not available here.
        # V57's outer train set is all rows except the target phase/fold. Import locally to avoid changing architecture.
        import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
        lo, hi = int(np.min(measures)), int(np.max(measures))
        outer_ids = np.asarray([v18.phased_fold(int(m), lo, hi, 5, phase) for m in measures], dtype=np.int16)
        outer_train = outer_ids != fold

        xF = x_full[outer_train]
        xD = x_drop[outer_train]
        ytr = y[outer_train]
        mtr = measures[outer_train]

        scheme_rows = []
        drop_better_schemes = 0
        drop_nonworse_schemes = 0
        drop_lift_better_schemes = 0
        all_pass_delta = 0
        all_lift_deltas = []

        for inner_scheme in INNER_SCHEMES:
            ids = v38.inner_ids(mtr, inner_scheme)
            fp = dp = 0
            flifts = []
            dlifts = []
            for inner_fold in range(INNER_FOLDS):
                val = ids == inner_fold
                sub = ~val
                if not np.any(val) or not np.any(sub):
                    continue
                mf = v2.fit_pairwise_ranker(xF[sub], ytr[sub], mtr[sub], radius, lam)
                md = v2.fit_pairwise_ranker(xD[sub], ytr[sub], mtr[sub], radius, lam)
                pfold, lfull = pass_at_q(v2.scores_for(xF[val], mf), ytr[val])
                pdrop, ldrop = pass_at_q(v2.scores_for(xD[val], md), ytr[val])
                fp += int(pfold)
                dp += int(pdrop)
                flifts.append(lfull)
                dlifts.append(ldrop)

            mean_full = float(np.mean(flifts)) if flifts else 0.0
            mean_drop = float(np.mean(dlifts)) if dlifts else 0.0
            pass_delta = int(dp - fp)
            lift_delta = float(mean_drop - mean_full)
            drop_better_schemes += int(pass_delta > 0)
            drop_nonworse_schemes += int(pass_delta >= 0)
            drop_lift_better_schemes += int(lift_delta > 0)
            all_pass_delta += pass_delta
            all_lift_deltas.append(lift_delta)
            scheme_rows.append({
                "scheme": inner_scheme,
                "fullPasses": int(fp),
                "dropPasses": int(dp),
                "passDeltaDropMinusFull": pass_delta,
                "meanFullLift": round(mean_full, 6),
                "meanDropLift": round(mean_drop, 6),
                "meanLiftDeltaDropMinusFull": round(lift_delta, 6),
            })

        evidence = {
            "phase": phase,
            "fold": fold,
            "status": status,
            "pairRadius": radius,
            "lambda": lam,
            "dropBetterSchemeCount": int(drop_better_schemes),
            "dropNonWorseSchemeCount": int(drop_nonworse_schemes),
            "dropLiftBetterSchemeCount": int(drop_lift_better_schemes),
            "totalInnerPassDeltaDropMinusFull": int(all_pass_delta),
            "meanSchemeLiftDeltaDropMinusFull": round(float(np.mean(all_lift_deltas)), 6),
            "schemes": scheme_rows,
        }
        rows_out.append(evidence)
        status_summary[(status, drop_better_schemes, drop_nonworse_schemes, drop_lift_better_schemes)] += 1
        print("Evidence:", {k: evidence[k] for k in ["phase", "fold", "status", "dropBetterSchemeCount", "dropNonWorseSchemeCount", "dropLiftBetterSchemeCount", "totalInnerPassDeltaDropMinusFull", "meanSchemeLiftDeltaDropMinusFull"]})

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V77")

    summary = {str(k): int(v) for k, v in status_summary.items()}
    out = {
        "schemaVersion": 77,
        "profileType": "v76-changed-flip-training-representation-evidence-diagnostic",
        "diagnosticScope": "13 already-exposed V76 changed folds only",
        "representationComparison": "full-v17-phase-vs-drop-p4-sin",
        "qFrozen": Q,
        "modelHyperparametersFrozenFromV57": True,
        "heldoutOutcomesUsedToChooseTrainingEvidence": False,
        "changedFoldStatusesUsedOnlyForPosthocGrouping": True,
        "statusEvidenceSummary": summary,
        "rows": rows_out,
        "diagnosticOutcomesTaintedForSelection": True,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: out[k] for k in [
        "schemaVersion", "representationComparison", "qFrozen", "modelHyperparametersFrozenFromV57",
        "heldoutOutcomesUsedToChooseTrainingEvidence", "changedFoldStatusesUsedOnlyForPosthocGrouping",
        "statusEvidenceSummary", "diagnosticOutcomesTaintedForSelection",
        "newReserved1over128OddNumeratorPhasesReferenced", "newTuningPerformed",
        "validatedNewChampion", "protected949CandidateHashUnchanged", "productionPromotionAllowed"
    ]}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V77 CHANGED-FLIP TRAINING REPRESENTATION EVIDENCE COMPLETE")
    print("Changed folds analyzed:", len(rows_out))
    print("Status/evidence summary:", summary)
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
