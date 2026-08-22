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
import benchmark_gomyway_3676_patch_rhythm24_v28_exact_anchor_unanimous_training_tighten_v38 as v38

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v51-trainingonly-anchor-hole-escape-v52.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v51-trainingonly-anchor-hole-escape-v52-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
INNER_FOLDS = 4
INNER_SCHEMES = ("normal", "section", "shiftedWindow")
ANCHOR_Q = float(v28.FROZEN_Q)
STEP = 0.025
TIGHT_Q = ANCHOR_Q - STEP
BROAD_Q = ANCHOR_Q + STEP

# Already-exposed exploratory phase pool only. The new 1/64 odd-offset reserve is forbidden here.
EXPOSED_PHASES = tuple(v28.CONFIRM_PHASES) + (
    0.03125, 0.09375, 0.15625, 0.21875, 0.28125, 0.34375, 0.40625, 0.46875,
    0.53125, 0.59375, 0.65625, 0.71875, 0.78125, 0.84375, 0.90625, 0.96875,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose_q_train_only(xtr, ytr, mtr, radius, lam):
    scheme_rows = []
    totals = {TIGHT_Q: 0, ANCHOR_Q: 0, BROAD_Q: 0}
    lift_sums = {TIGHT_Q: [], ANCHOR_Q: [], BROAD_Q: []}
    strict_broad_count = 0

    for scheme in INNER_SCHEMES:
        ids = v38.inner_ids(mtr, scheme)
        counts = {TIGHT_Q: 0, ANCHOR_Q: 0, BROAD_Q: 0}
        lifts = {TIGHT_Q: [], ANCHOR_Q: [], BROAD_Q: []}
        for fold in range(INNER_FOLDS):
            val = ids == fold
            sub = ~val
            if not np.any(val) or not np.any(sub):
                continue
            model = v2.fit_pairwise_ranker(xtr[sub], ytr[sub], mtr[sub], radius, lam)
            scores = v2.scores_for(xtr[val], model)
            for q in (TIGHT_Q, ANCHOR_Q, BROAD_Q):
                passed, lift, *_ = v17.pass_at_q(scores, ytr[val], q)
                counts[q] += int(passed)
                lifts[q].append(float(lift))

        strict_broad = counts[BROAD_Q] > counts[ANCHOR_Q]
        strict_broad_count += int(strict_broad)
        for q in (TIGHT_Q, ANCHOR_Q, BROAD_Q):
            totals[q] += counts[q]
            lift_sums[q].extend(lifts[q])
        scheme_rows.append({
            "scheme": scheme,
            "tightPasses": counts[TIGHT_Q],
            "anchorPasses": counts[ANCHOR_Q],
            "broadPasses": counts[BROAD_Q],
            "meanTightLift": float(np.mean(lifts[TIGHT_Q])),
            "meanAnchorLift": float(np.mean(lifts[ANCHOR_Q])),
            "meanBroadLift": float(np.mean(lifts[BROAD_Q])),
            "strictBroadSupport": bool(strict_broad),
        })

    # V51-inspired architecture, but selection is entirely training-only.
    # The +/-0.025 candidates are symmetric around the frozen q=0.20 anchor;
    # 0.025 is the same predeclared one-step size already used by V40/V42/V46.
    # If the anchor is strictly worse in aggregate inner-fold pass count than BOTH neighbors,
    # escape the local training hole by choosing the stronger neighbor. Otherwise preserve V46:
    # broaden only when at least one inner scheme strictly prefers broadening.
    anchor_hole = totals[ANCHOR_Q] < totals[TIGHT_Q] and totals[ANCHOR_Q] < totals[BROAD_Q]
    reason = "anchor"
    if anchor_hole:
        if totals[BROAD_Q] > totals[TIGHT_Q]:
            q = BROAD_Q
            reason = "training-anchor-hole-broad"
        elif totals[TIGHT_Q] > totals[BROAD_Q]:
            q = TIGHT_Q
            reason = "training-anchor-hole-tight"
        else:
            tight_mean = float(np.mean(lift_sums[TIGHT_Q]))
            broad_mean = float(np.mean(lift_sums[BROAD_Q]))
            q = BROAD_Q if broad_mean >= tight_mean else TIGHT_Q
            reason = "training-anchor-hole-tie-break-lift"
    elif strict_broad_count >= 1:
        q = BROAD_Q
        reason = "v46-strict-broad-support"
    else:
        q = ANCHOR_Q

    return q, {
        "architecture": "v46-plus-trainingonly-symmetric-anchor-hole-escape",
        "tightQ": TIGHT_Q,
        "anchorQ": ANCHOR_Q,
        "broadQ": BROAD_Q,
        "aggregateInnerPasses": {
            "tight": totals[TIGHT_Q], "anchor": totals[ANCHOR_Q], "broad": totals[BROAD_Q]
        },
        "strictBroadSupportCount": strict_broad_count,
        "trainingAnchorHoleDetected": bool(anchor_hole),
        "selectionReason": reason,
        "chosenQ": q,
        "outerHeldoutLabelsUsed": False,
        "v51DiagnosticInformedArchitecture": True,
        "schemes": scheme_rows,
    }


def main():
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

    schemes = []
    total = v28_total = rescues = regressions = folds_total = 0
    chosen_counts = {"tight": 0, "anchor": 0, "broad": 0}
    hole_count = 0

    for phase in EXPOSED_PHASES:
        lo, hi = int(np.min(measures)), int(np.max(measures))
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures], dtype=np.int16)
        pp = pv = 0
        prows = []
        for fold in range(OUTER_FOLDS):
            print(f"phase={phase} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
            test = ids == fold
            train = ~test
            cm = v5.choose_model(x[train], y[train], measures[train])
            radius = int(cm["pairRadius"])
            lam = float(cm["lambda"])
            q, sel = choose_q_train_only(x[train], y[train], measures[train], radius, lam)
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)
            passed, lift, held, base = v17.pass_at_q(scores, y[test], q)
            vp, vl, vh, _ = v17.pass_at_q(scores, y[test], ANCHOR_Q)

            pp += int(passed)
            pv += int(vp)
            rescues += int(passed and not vp)
            regressions += int(vp and not passed)
            hole_count += int(sel["trainingAnchorHoleDetected"])
            if abs(q - TIGHT_Q) < 1e-12:
                chosen_counts["tight"] += 1
            elif abs(q - BROAD_Q) < 1e-12:
                chosen_counts["broad"] += 1
            else:
                chosen_counts["anchor"] += 1

            prows.append({
                "phase": float(phase), "fold": int(fold), "selector": sel,
                "outerQ": float(q), "passed": bool(passed),
                "heldoutPrecisionLift": round(float(lift), 2),
                "heldoutCandidate": held, "heldoutBase": base,
                "v28Comparison": {"passed": bool(vp), "heldoutPrecisionLift": round(float(vl), 2), "heldoutCandidate": vh},
            })
            print(f"  V52 q={q:.3f} reason={sel['selectionReason']} pass={passed}; V28 pass={vp}", flush=True)

        schemes.append({"phase": float(phase), "passes": pp, "v28Passes": pv, "folds": prows})
        total += pp
        v28_total += pv
        folds_total += len(prows)

    minp = min(s["passes"] for s in schemes)
    promising = total > v28_total and minp >= 4 and regressions <= rescues
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V52")

    out = {
        "schemaVersion": 52,
        "profileType": "v51-trainingonly-anchor-hole-escape",
        "challengeSource": "combined-already-exposed-v28-and-v44-phases",
        "foldsPassed": total, "foldsTotal": folds_total,
        "minimumPhasePasses": minp, "v28ComparisonPasses": v28_total,
        "rescuesVsV28": rescues, "regressionsVsV28": regressions,
        "chosenQCounts": chosen_counts,
        "trainingAnchorHoleDetectedFolds": hole_count,
        "exploratoryPromising": promising,
        "architectureTaintedByV51Diagnostic": True,
        "requiresFreshUntouchedConfirmation": True,
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "validatedNewChampion": False,
        "schemes": schemes,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: out[k] for k in [
        "schemaVersion", "foldsPassed", "foldsTotal", "minimumPhasePasses", "v28ComparisonPasses",
        "rescuesVsV28", "regressionsVsV28", "chosenQCounts", "trainingAnchorHoleDetectedFolds",
        "exploratoryPromising", "architectureTaintedByV51Diagnostic", "requiresFreshUntouchedConfirmation",
        "newReserved1over64OddPhasesReferenced", "reservedUntouchedPhasesConsumed", "validatedNewChampion",
        "protected949CandidateHashUnchanged", "productionPromotionAllowed"
    ]}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V51 TRAINING-ONLY ANCHOR-HOLE ESCAPE V52 COMPLETE")
    print("V52 folds passed:", total, "/", folds_total)
    print("Minimum V52 phase passes:", minp, "/ 5")
    print("V28 comparison passes:", v28_total, "/", folds_total)
    print("Rescues vs V28:", rescues)
    print("Regressions vs V28:", regressions)
    print("Chosen q counts:", chosen_counts)
    print("Training anchor-hole detected folds:", hole_count)
    print("Exploratory promising:", promising)
    print("New reserved 1/64 odd phases referenced: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
