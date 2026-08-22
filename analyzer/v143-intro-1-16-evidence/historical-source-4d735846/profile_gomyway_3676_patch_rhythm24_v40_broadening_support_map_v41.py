from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v40-broadening-support-map-v41.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v40-broadening-support-map-v41-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
INNER_FOLDS = 4
INNER_SCHEMES = ("normal", "section", "shiftedWindow")
CHALLENGE_PHASES = v28.CONFIRM_PHASES
ANCHOR_Q = float(v28.FROZEN_Q)
BROAD_Q = 0.225


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scheme_support(x_train: np.ndarray, y_train: np.ndarray, measures_train: np.ndarray, radius: int, lam: float) -> list[dict[str, Any]]:
    out = []
    for scheme in INNER_SCHEMES:
        ids = v38.inner_ids(measures_train, scheme)
        anchor_passes = broad_passes = 0
        anchor_lifts = []
        broad_lifts = []
        folds = []
        for fold in range(INNER_FOLDS):
            val = ids == fold
            subtrain = ~val
            if not np.any(val) or not np.any(subtrain):
                continue
            model = v2.fit_pairwise_ranker(x_train[subtrain], y_train[subtrain], measures_train[subtrain], radius, lam)
            scores = v2.scores_for(x_train[val], model)
            ap, al, ah, ab = v17.pass_at_q(scores, y_train[val], ANCHOR_Q)
            bp, bl, bh, _ = v17.pass_at_q(scores, y_train[val], BROAD_Q)
            anchor_passes += int(ap)
            broad_passes += int(bp)
            anchor_lifts.append(float(al))
            broad_lifts.append(float(bl))
            folds.append({"fold": int(fold), "anchorPassed": bool(ap), "broadPassed": bool(bp),
                          "anchorLift": round(float(al), 2), "broadLift": round(float(bl), 2),
                          "anchorHeld": ah, "broadHeld": bh, "base": ab})
        prefers = broad_passes > anchor_passes
        ties_pass_but_lift_better = broad_passes == anchor_passes and np.mean(broad_lifts) > np.mean(anchor_lifts)
        out.append({"scheme": scheme, "anchorPasses": int(anchor_passes), "broadPasses": int(broad_passes),
                    "strictPassPreferenceForBroad": bool(prefers),
                    "equalPassesButMeanLiftHigher": bool(ties_pass_but_lift_better),
                    "meanAnchorLift": float(np.mean(anchor_lifts)), "meanBroadLift": float(np.mean(broad_lifts)),
                    "folds": folds})
    return out


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")
    base_names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows], dtype=np.float64)
    x = np.concatenate([x_base, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)

    histogram = {"0": 0, "1": 0, "2": 0, "3": 0}
    soft_histogram = {"0": 0, "1": 0, "2": 0, "3": 0}
    records = []
    for phase in CHALLENGE_PHASES:
        lo, hi = int(np.min(measures)), int(np.max(measures))
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures], dtype=np.int16)
        for fold in range(OUTER_FOLDS):
            print(f"phase={phase} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
            test = ids == fold
            train = ~test
            chosen_model = v5.choose_model(x[train], y[train], measures[train])
            schemes = scheme_support(x[train], y[train], measures[train], int(chosen_model["pairRadius"]), float(chosen_model["lambda"]))
            strict = sum(int(s["strictPassPreferenceForBroad"]) for s in schemes)
            soft = sum(int(s["strictPassPreferenceForBroad"] or s["equalPassesButMeanLiftHigher"]) for s in schemes)
            histogram[str(strict)] += 1
            soft_histogram[str(soft)] += 1
            records.append({"phase": float(phase), "fold": int(fold), "strictBroadSupportCount": strict,
                            "softBroadSupportCount": soft, "schemes": schemes})

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V41")
    output = {"schemaVersion": 41, "profileType": "v40-broadening-training-support-map",
              "anchorQ": ANCHOR_Q, "broadQ": BROAD_Q,
              "strictSupportHistogram": histogram, "softSupportHistogram": soft_histogram,
              "records": records, "reservedUntouchedPhasesConsumed": False,
              "newTuningPerformed": False, "outerHeldoutLabelsUsedToChooseCalibrationParameters": False,
              "protected949CandidateHashUnchanged": before == after, "productionPromotionAllowed": False}
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({"schemaVersion": 41, "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "strictSupportHistogram": histogram, "softSupportHistogram": soft_histogram,
        "reservedUntouchedPhasesConsumed": False, "newTuningPerformed": False,
        "protected949CandidateHashUnchanged": before == after, "productionPromotionAllowed": False}, indent=2) + "\n", encoding="utf-8")
    print("GOMYWAY 36.76 RHYTHM24 V40 BROADENING SUPPORT MAP V41 COMPLETE")
    print("Strict broad support histogram:", histogram)
    print("Soft broad support histogram:", soft_histogram)
    print("Reserved untouched phases consumed: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
