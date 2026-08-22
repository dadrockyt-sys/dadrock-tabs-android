from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v17-fixed-policy-boundary-stress-v18.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v17-fixed-policy-boundary-stress-v18-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
PERIODS = (2, 4)

# These boundary phases were predeclared for this stress run and were not used
# to design V17. 0.50 is intentionally omitted because it is V17's original
# shiftedWindow outer split.
STRESS_PHASES = (0.25, 0.75)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase_features(rows: list[dict[str, Any]]) -> np.ndarray:
    out = []
    for r in rows:
        step = int(r["step"])
        vals = []
        for p in PERIODS:
            a = 2.0 * math.pi * (step % p) / float(p)
            vals.extend([math.sin(a), math.cos(a)])
        out.append(vals)
    return np.asarray(out, dtype=np.float64)


def phased_fold(measure: int, lo: int, hi: int, folds: int, phase: float) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + phase * width) % span
    return min(folds - 1, int(pos / width))


def pass_at_q(scores: np.ndarray, yy: np.ndarray, q: float) -> tuple[bool, float, dict[str, Any], dict[str, Any]]:
    held = v1.select_top_fraction(scores, yy, q)
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    passed = held["true"] > 0 and lift >= 5.0
    return bool(passed), float(lift), held, base


def evaluate_scheme(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    lo: int,
    hi: int,
    name: str,
    phase: float,
    allow_shifted_selector: bool,
) -> tuple[int, list[dict[str, Any]]]:
    ids = np.asarray([phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
    passes = 0
    rows: list[dict[str, Any]] = []

    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test

        print("    heartbeat V18 frozen V17 model-selection policy", flush=True)
        chosen = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])
        base_q = float(chosen["tailQuantile"])

        if allow_shifted_selector:
            print("    heartbeat V18 frozen V17 shifted-only q selector", flush=True)
            selected_q, selector = v17.choose_q_train_only_shifted(
                x[train], y[train], measures[train], radius, lam, base_q
            )
        else:
            selected_q = base_q
            selector = {
                "baseQ": base_q,
                "tightQ": v17.TIGHT_Q,
                "chosenQ": base_q,
                "switchedToTightQ": False,
                "rule": "selector-disabled-preserve-v14-policy",
            }

        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)
        passed, lift, held, base = pass_at_q(scores, y[test], selected_q)
        passes += int(passed)

        rows.append({
            "scheme": name,
            "phase": phase,
            "fold": fold,
            "chosenModel": chosen,
            "selector": selector,
            "outerQ": float(selected_q),
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
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
    x = np.concatenate([x_base, phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V18 fixed-policy boundary stress test", flush=True)
    print("V17 representation/policy frozen; no new q values, periods, or selector rules", flush=True)
    print("Unseen outer boundary phases:", STRESS_PHASES, flush=True)

    schemes = []
    total_passes = 0
    total_folds = 0

    # Section-like stress: same V14 behavior, selector disabled, but boundaries
    # moved by unseen quarter/three-quarter fold widths.
    for phase in STRESS_PHASES:
        name = f"sectionStressPhase{phase}"
        p, rr = evaluate_scheme(x, y, measures, lo, hi, name, phase, False)
        schemes.append({"name": name, "phase": phase, "selectorEnabled": False, "passes": p, "folds": rr})
        total_passes += p
        total_folds += OUTER_FOLDS

    # Shifted-like stress: apply exactly V17's shifted-only training selector on
    # unseen shifted outer boundaries.
    for phase in STRESS_PHASES:
        name = f"shiftedStressPhase{phase}"
        p, rr = evaluate_scheme(x, y, measures, lo, hi, name, phase, True)
        schemes.append({"name": name, "phase": phase, "selectorEnabled": True, "passes": p, "folds": rr})
        total_passes += p
        total_folds += OUTER_FOLDS

    all_pass = total_passes == total_folds
    min_scheme_passes = min(s["passes"] for s in schemes)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V18")

    output = {
        "schemaVersion": 18,
        "profileType": "36.76-rhythm24-v17-fixed-policy-unseen-boundary-stress",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenPolicy": {
            "periods": list(PERIODS),
            "normalAndSection": "V14 base-q policy",
            "shifted": "V17 training-only tight-q selector",
            "tightQ": v17.TIGHT_Q,
            "newTuningPerformed": False,
        },
        "stressPhases": list(STRESS_PHASES),
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": total_folds,
        "minimumSchemePasses": min_scheme_passes,
        "allStressFoldsPassed": all_pass,
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
        "schemaVersion": 18,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": total_folds,
        "minimumSchemePasses": min_scheme_passes,
        "allStressFoldsPassed": all_pass,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V17 FIXED-POLICY BOUNDARY STRESS V18 COMPLETE")
    print("Stress folds passed:", total_passes, "/", total_folds)
    for s in schemes:
        print(s["name"], "passes:", s["passes"], "/ 5")
    print("Minimum scheme passes:", min_scheme_passes, "/ 5")
    print("All stress folds passed:", all_pass)
    print("New tuning performed: False")
    print("Professional reference used to choose q: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
