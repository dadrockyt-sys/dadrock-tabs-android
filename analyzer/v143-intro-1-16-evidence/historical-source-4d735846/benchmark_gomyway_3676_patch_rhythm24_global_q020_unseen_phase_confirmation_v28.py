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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-global-q020-unseen-phase-confirmation-v28.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-global-q020-unseen-phase-confirmation-v28-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5

# Frozen before this run from the V27 diagnostic. V28 does not search q.
FROZEN_Q = 0.20

# These phases were not used in V18/V19/V20/V23/V24/V25/V27.
# They fill the gaps between the previously examined eighth/quarter boundaries.
CONFIRM_PHASES = (0.0625, 0.1875, 0.3125, 0.4375, 0.5625, 0.6875, 0.8125, 0.9375)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows],
        dtype=np.float64,
    )
    x = np.concatenate([x_base, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V28 frozen q=0.20 unseen-phase confirmation", flush=True)
    print("q=0.20 was frozen before this run from V27; no q search occurs in V28", flush=True)
    print("Untouched confirmation phases:", CONFIRM_PHASES, flush=True)

    schemes: list[dict[str, Any]] = []
    total_passes = 0
    total_folds = 0

    for phase in CONFIRM_PHASES:
        ids = np.asarray(
            [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures],
            dtype=np.int16,
        )
        phase_rows: list[dict[str, Any]] = []
        phase_passes = 0

        for fold in range(OUTER_FOLDS):
            print(f"phase={phase} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
            test = ids == fold
            train = ~test

            print("    heartbeat V28 frozen V17 representation/model-selection", flush=True)
            chosen = v5.choose_model(x[train], y[train], measures[train])
            radius = int(chosen["pairRadius"])
            lam = float(chosen["lambda"])

            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)
            passed, lift, held, base = v17.pass_at_q(scores, y[test], FROZEN_Q)

            phase_passes += int(passed)
            total_passes += int(passed)
            total_folds += 1

            row = {
                "phase": float(phase),
                "fold": int(fold),
                "chosenModel": chosen,
                "frozenQ": FROZEN_Q,
                "heldoutBase": base,
                "heldoutCandidate": held,
                "heldoutPrecisionLift": round(float(lift), 2),
                "passed": bool(passed),
            }
            phase_rows.append(row)

            print(
                f"  q={FROZEN_Q} held={held['true']}/{held['false']} precision={held['precision']} "
                f"base={base['precision']} lift={round(lift, 2)} pass={passed}",
                flush=True,
            )

        schemes.append({"phase": float(phase), "passes": int(phase_passes), "folds": phase_rows})

    min_phase_passes = min(s["passes"] for s in schemes)
    perfect_confirmation = total_passes == total_folds
    strong_confirmation = total_passes >= 36 and min_phase_passes >= 4

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V28")

    output = {
        "schemaVersion": 28,
        "profileType": "36.76-rhythm24-global-q020-unseen-phase-confirmation",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenReferenceRepresentation": "V17-rhythm24",
        "candidateSourceDiagnostic": "V27",
        "frozenQ": FROZEN_Q,
        "qSearchPerformedInV28": False,
        "confirmationPhases": list(CONFIRM_PHASES),
        "confirmationFoldsPassed": int(total_passes),
        "confirmationFoldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase_passes),
        "perfectConfirmation": bool(perfect_confirmation),
        "strongConfirmation": bool(strong_confirmation),
        "outerHeldoutLabelsUsedToChooseQInV28": False,
        "schemes": schemes,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 28,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "frozenQ": FROZEN_Q,
        "confirmationFoldsPassed": int(total_passes),
        "confirmationFoldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase_passes),
        "perfectConfirmation": bool(perfect_confirmation),
        "strongConfirmation": bool(strong_confirmation),
        "qSearchPerformedInV28": False,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 GLOBAL Q020 UNSEEN-PHASE CONFIRMATION V28 COMPLETE")
    print("Frozen q:", FROZEN_Q)
    print("Confirmation folds passed:", total_passes, "/", total_folds)
    for s in schemes:
        print("phase", s["phase"], "passes:", s["passes"], "/ 5")
    print("Minimum phase passes:", min_phase_passes, "/ 5")
    print("Perfect confirmation:", perfect_confirmation)
    print("Strong confirmation:", strong_confirmation)
    print("q search performed in V28: False")
    print("Outer heldout labels used to choose q in V28: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
