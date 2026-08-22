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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v17-frozen-unseen-phase-confirmation-v23.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v17-frozen-unseen-phase-confirmation-v23-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5

# These phases were not used in V14, V17, V18, V19, V20, V21, or V22.
# V23 performs no tuning and does not change the frozen V17 policy.
UNSEEN_PHASES = (0.125, 0.375, 0.625, 0.875)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    lo: int,
    hi: int,
    name: str,
    phase: float,
    shifted_policy: bool,
) -> tuple[int, list[dict[str, Any]]]:
    ids = np.asarray(
        [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures],
        dtype=np.int16,
    )
    passes = 0
    rows: list[dict[str, Any]] = []

    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test

        print("    heartbeat V23 frozen V17 model selection", flush=True)
        chosen = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])
        base_q = float(chosen["tailQuantile"])

        if shifted_policy:
            print("    heartbeat V23 frozen V17 shifted-only q selector", flush=True)
            selected_q, selector = v17.choose_q_train_only_shifted(
                x[train], y[train], measures[train], radius, lam, base_q
            )
        else:
            selected_q = base_q
            selector = {
                "baseQ": base_q,
                "chosenQ": base_q,
                "switchedToTightQ": False,
                "rule": "frozen-v17-selector-disabled-for-section-like-confirmation",
            }

        model = v2.fit_pairwise_ranker(
            x[train], y[train], measures[train], radius, lam
        )
        scores = v2.scores_for(x[test], model)
        passed, lift, held, base = v18.pass_at_q(scores, y[test], selected_q)
        passes += int(passed)

        rows.append({
            "scheme": name,
            "phase": phase,
            "fold": fold,
            "shiftedPolicy": shifted_policy,
            "chosenModel": chosen,
            "selector": selector,
            "outerQ": float(selected_q),
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(float(lift), 2),
            "passed": bool(passed),
        })

        print(
            f"  phase={phase} baseQ={base_q} chosenQ={selected_q} "
            f"held={held['true']}/{held['false']} precision={held['precision']} "
            f"base={base['precision']} lift={round(lift,2)} pass={passed}",
            flush=True,
        )

    return passes, rows


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
    x = np.concatenate([x_base, v18.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V23 frozen V17 unseen-phase confirmation", flush=True)
    print("Frozen V17 policy only; no new tuning, q values, periods, or selector rules", flush=True)
    print("Unseen confirmation phases:", UNSEEN_PHASES, flush=True)

    schemes: list[dict[str, Any]] = []
    total_passes = 0
    total_folds = 0

    for phase in UNSEEN_PHASES:
        name = f"sectionConfirmPhase{phase}"
        p, rr = evaluate(x, y, measures, lo, hi, name, phase, False)
        schemes.append({
            "name": name,
            "phase": phase,
            "policy": "frozen-v17-section-like-base-q",
            "passes": p,
            "folds": rr,
        })
        total_passes += p
        total_folds += OUTER_FOLDS

    for phase in UNSEEN_PHASES:
        name = f"shiftedConfirmPhase{phase}"
        p, rr = evaluate(x, y, measures, lo, hi, name, phase, True)
        schemes.append({
            "name": name,
            "phase": phase,
            "policy": "frozen-v17-shifted-training-only-q-selector",
            "passes": p,
            "folds": rr,
        })
        total_passes += p
        total_folds += OUTER_FOLDS

    min_scheme = min(s["passes"] for s in schemes)
    all_pass = total_passes == total_folds
    strong_confirmation = min_scheme >= 4 and total_passes >= 36

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V23")

    output = {
        "schemaVersion": 23,
        "profileType": "36.76-rhythm24-v17-frozen-unseen-phase-confirmation",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenChampion": "V17",
        "frozenPeriods": [2, 4],
        "unseenPhases": list(UNSEEN_PHASES),
        "newTuningPerformed": False,
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": total_folds,
        "minimumSchemePasses": min_scheme,
        "allConfirmationFoldsPassed": all_pass,
        "strongConfirmation": strong_confirmation,
        "schemes": schemes,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseQ": False,
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
        "schemaVersion": 23,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "frozenChampion": "V17",
        "unseenPhases": list(UNSEEN_PHASES),
        "newTuningPerformed": False,
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": total_folds,
        "minimumSchemePasses": min_scheme,
        "allConfirmationFoldsPassed": all_pass,
        "strongConfirmation": strong_confirmation,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V17 FROZEN UNSEEN-PHASE CONFIRMATION V23 COMPLETE")
    print("Confirmation folds passed:", total_passes, "/", total_folds)
    for s in schemes:
        print(s["name"], "passes:", s["passes"], "/ 5")
    print("Minimum scheme passes:", min_scheme, "/ 5")
    print("All confirmation folds passed:", all_pass)
    print("Strong confirmation:", strong_confirmation)
    print("New tuning performed: False")
    print("Professional reference used to choose q: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
