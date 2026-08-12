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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V28_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-global-q020-unseen-phase-confirmation-v28.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-failure-map-v29.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-failure-map-v29-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
Q_SWEEP = (0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.075, 0.10, 0.15, 0.20, 0.25, 0.30)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def auc_rank(scores: np.ndarray, y: np.ndarray) -> float:
    pos = scores[y]
    neg = scores[~y]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    wins = 0.0
    for p in pos:
        wins += float(np.sum(p > neg)) + 0.5 * float(np.sum(p == neg))
    return float(wins / (len(pos) * len(neg)))


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v28_result = json.loads(V28_PATH.read_text(encoding="utf-8"))
    failures = []
    for scheme in v28_result.get("schemes", []):
        for row in scheme.get("folds", []):
            if not row.get("passed", False):
                failures.append({"phase": float(row["phase"]), "fold": int(row["fold"])})

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows], dtype=np.float64)
    x = np.concatenate([x_base, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    mapped: list[dict[str, Any]] = []
    recoverable = 0

    for idx, failure in enumerate(failures, start=1):
        phase = failure["phase"]
        fold = failure["fold"]
        print(f"V29 failure {idx}/{len(failures)} phase={phase} fold={fold}", flush=True)
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        test = ids == fold
        train = ~test

        print("    heartbeat V29 frozen V17 representation/model-selection", flush=True)
        chosen = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)
        yy = y[test]
        auc = auc_rank(scores, yy)

        sweep = []
        passing = []
        for q in Q_SWEEP:
            passed, lift, held, base = v17.pass_at_q(scores, yy, float(q))
            item = {
                "q": float(q),
                "passed": bool(passed),
                "lift": round(float(lift), 2),
                "selected": int(held["selected"]),
                "true": int(held["true"]),
                "false": int(held["false"]),
                "precision": float(held["precision"]),
                "basePrecision": float(base["precision"]),
            }
            sweep.append(item)
            if passed:
                passing.append(item)

        best = None
        if passing:
            best = max(passing, key=lambda z: (z["lift"], z["true"], -abs(z["q"] - v28.FROZEN_Q)))
            recoverable += 1

        result = {
            "phase": phase,
            "fold": fold,
            "auc": round(float(auc), 6),
            "frozenQ": v28.FROZEN_Q,
            "operatingPointRecoverable": bool(passing),
            "bestPassingSweepPoint": best,
            "sweep": sweep,
        }
        mapped.append(result)
        print("    auc=", round(auc, 6), "recoverable=", bool(passing), "best=", best, flush=True)

    nonrecoverable = len(mapped) - recoverable
    all_recoverable = len(mapped) > 0 and recoverable == len(mapped)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V29")

    output = {
        "schemaVersion": 29,
        "profileType": "36.76-rhythm24-v28-unseen-phase-failure-map",
        "frozenReferenceRepresentation": "V17-rhythm24",
        "v28FrozenQ": v28.FROZEN_Q,
        "v28Failures": len(mapped),
        "operatingPointRecoverableFailures": recoverable,
        "nonRecoverableRankingFailures": nonrecoverable,
        "allFailuresOperatingPointRecoverable": all_recoverable,
        "failures": mapped,
        "newTuningPerformed": False,
        "heldoutLabelsUsedForDiagnosticSweep": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 29,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "v28Failures": len(mapped),
        "operatingPointRecoverableFailures": recoverable,
        "nonRecoverableRankingFailures": nonrecoverable,
        "allFailuresOperatingPointRecoverable": all_recoverable,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V28 FAILURE MAP V29 COMPLETE")
    print("V28 failures:", len(mapped))
    print("Operating-point recoverable failures:", recoverable, "/", len(mapped))
    print("Non-recoverable ranking failures:", nonrecoverable)
    print("All failures operating-point recoverable:", all_recoverable)
    print("Heldout labels used for diagnostic sweep: True")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
