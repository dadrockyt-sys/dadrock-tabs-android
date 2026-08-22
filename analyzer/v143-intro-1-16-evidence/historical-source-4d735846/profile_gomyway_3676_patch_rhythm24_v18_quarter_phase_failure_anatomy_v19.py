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
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v18-quarter-phase-failure-anatomy-v19.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v18-quarter-phase-failure-anatomy-v19-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
PHASE = 0.25
Q_SWEEP = (0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.075, 0.10, 0.125, 0.15)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase_features(rows: list[dict[str, Any]]) -> np.ndarray:
    out = []
    for r in rows:
        step = int(r["step"])
        vals = []
        for p in (2, 4):
            a = 2.0 * math.pi * (step % p) / float(p)
            vals.extend([math.sin(a), math.cos(a)])
        out.append(vals)
    return np.asarray(out, dtype=np.float64)


def auc_rank(scores: np.ndarray, y: np.ndarray) -> float:
    pos = np.flatnonzero(y)
    neg = np.flatnonzero(~y)
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    wins = 0.0
    for i in pos:
        for j in neg:
            if scores[i] > scores[j]:
                wins += 1.0
            elif scores[i] == scores[j]:
                wins += 0.5
    return wins / float(len(pos) * len(neg))


def pass_at_q(scores: np.ndarray, yy: np.ndarray, q: float):
    held = v1.select_top_fraction(scores, yy, q)
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    passed = held["true"] > 0 and lift >= 5.0
    return bool(passed), float(lift), held, base


def analyze_scheme(x, y, measures, lo, hi, name: str, selector_enabled: bool):
    ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, PHASE) for m in measures], dtype=np.int16)
    results = []
    failures = []
    for fold in range(OUTER_FOLDS):
        test = ids == fold
        train = ~test
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        chosen = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])
        base_q = float(chosen["tailQuantile"])
        if selector_enabled:
            selected_q, selector = v17.choose_q_train_only_shifted(x[train], y[train], measures[train], radius, lam, base_q)
        else:
            selected_q = base_q
            selector = {"chosenQ": base_q, "switchedToTightQ": False, "rule": "selector-disabled"}
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)
        passed, lift, held, base = pass_at_q(scores, y[test], selected_q)
        sweep = []
        for q in Q_SWEEP:
            qp, qlift, qheld, _ = pass_at_q(scores, y[test], q)
            sweep.append({"q": q, "passed": qp, "lift": round(qlift, 2), "candidate": qheld})
        best_pass = next((s for s in sweep if s["passed"]), None)
        row = {
            "scheme": name,
            "phase": PHASE,
            "fold": fold,
            "baseQ": base_q,
            "selectedQ": selected_q,
            "selector": selector,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "auc": round(float(auc_rank(scores, y[test])), 6),
            "passed": passed,
            "qSweep": sweep,
            "operatingPointRecoverable": bool(best_pass is not None),
            "bestPassingSweepPoint": best_pass,
        }
        results.append(row)
        if not passed:
            failures.append(row)
        print(f"  q={selected_q} held={held['true']}/{held['false']} lift={round(lift,2)} auc={row['auc']} pass={passed}", flush=True)
    return results, failures


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows], dtype=np.float64)
    x = np.concatenate([x_base, phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V19 quarter-phase stress failure anatomy", flush=True)
    section_rows, section_failures = analyze_scheme(x, y, measures, lo, hi, "sectionStressPhase0.25", False)
    shifted_rows, shifted_failures = analyze_scheme(x, y, measures, lo, hi, "shiftedStressPhase0.25", True)
    failures = section_failures + shifted_failures

    all_recoverable = bool(failures) and all(bool(f["operatingPointRecoverable"]) for f in failures)
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V19")

    output = {
        "schemaVersion": 19,
        "profileType": "36.76-rhythm24-v18-quarter-phase-failure-anatomy",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "phase": PHASE,
        "failureCount": len(failures),
        "failures": failures,
        "allFailuresOperatingPointRecoverable": all_recoverable,
        "section": section_rows,
        "shifted": shifted_rows,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseQ": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 19,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "failureCount": len(failures),
        "allFailuresOperatingPointRecoverable": all_recoverable,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V18 QUARTER-PHASE FAILURE ANATOMY V19 COMPLETE")
    print("Remaining quarter-phase failures:", len(failures))
    for f in failures:
        print("Failure:", f["scheme"], "fold", f["fold"], "auc", f["auc"], "selectedQ", f["selectedQ"])
        print("  Operating-point recoverable:", f["operatingPointRecoverable"])
        print("  Best passing sweep point:", f["bestPassingSweepPoint"])
    print("All failures operating-point recoverable:", all_recoverable)
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
