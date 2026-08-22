from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V23_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v17-frozen-unseen-phase-confirmation-v23.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v23-failure-map-v24.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v23-failure-map-v24-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
Q_SWEEP = (0.02, 0.025, 0.03, 0.04, 0.05, 0.075, 0.10, 0.125, 0.15, 0.20)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def auc_binary(y: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(y, dtype=bool)
    scores = np.asarray(scores, dtype=float)
    pos = scores[y]
    neg = scores[~y]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    wins = 0.0
    total = float(len(pos) * len(neg))
    for p in pos:
        wins += float(np.sum(p > neg)) + 0.5 * float(np.sum(p == neg))
    return wins / total


def test_signature(measures: np.ndarray) -> str:
    vals = sorted(int(x) for x in measures.tolist())
    return hashlib.sha256(",".join(map(str, vals)).encode("utf-8")).hexdigest()[:16]


def main() -> None:
    if not V23_PATH.exists():
        raise RuntimeError(
            "V23 output is missing. Run benchmark_gomyway_3676_patch_rhythm24_v17_frozen_unseen_phase_confirmation_v23.py first."
        )

    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(source.get("candidateSlots") or [])
    if not rows or tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    v23 = json.loads(V23_PATH.read_text(encoding="utf-8"))
    failures: list[dict[str, Any]] = []
    for scheme in v23.get("schemes") or []:
        for fold_row in scheme.get("folds") or []:
            if not bool(fold_row.get("passed")):
                failures.append({
                    "scheme": scheme.get("name"),
                    "phase": float(scheme.get("phase")),
                    "fold": int(fold_row.get("fold")),
                    "outerQ": float(fold_row.get("outerQ")),
                    "shiftedPolicy": bool(fold_row.get("shiftedPolicy")),
                })

    base_names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows],
        dtype=np.float64,
    )
    x = np.concatenate([x_base, v18.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V24 frozen-V17 unseen-phase failure map", flush=True)
    print("V23 failures to diagnose:", len(failures), flush=True)
    print("No selector/model changes; q sweep is diagnostic only", flush=True)

    details: list[dict[str, Any]] = []
    recoverable = 0
    rank_failures = 0
    signature_counts: dict[str, int] = {}

    for i, fail in enumerate(failures, start=1):
        phase = float(fail["phase"])
        fold = int(fail["fold"])
        ids = np.asarray(
            [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures],
            dtype=np.int16,
        )
        test = ids == fold
        train = ~test

        sig = test_signature(measures[test])
        signature_counts[sig] = signature_counts.get(sig, 0) + 1

        print(
            f"heartbeat V24 failure {i}/{len(failures)} {fail['scheme']} phase={phase} fold={fold} signature={sig}",
            flush=True,
        )

        chosen = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)
        auc = auc_binary(y[test], scores)

        sweep = []
        passing = []
        for q in Q_SWEEP:
            passed, lift, held, base = v18.pass_at_q(scores, y[test], float(q))
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

        is_recoverable = len(passing) > 0
        recoverable += int(is_recoverable)
        rank_failures += int(not is_recoverable)
        best = max(passing, key=lambda z: (z["lift"], -z["q"])) if passing else None

        detail = {
            **fail,
            "testSignature": sig,
            "testRows": int(np.sum(test)),
            "positiveRows": int(np.sum(y[test])),
            "negativeRows": int(np.sum(~y[test])),
            "auc": round(float(auc), 6),
            "chosenModel": chosen,
            "operatingPointRecoverable": bool(is_recoverable),
            "bestPassingSweepPoint": best,
            "sweep": sweep,
        }
        details.append(detail)

        print(
            f"  auc={auc:.6f} selectedQ={fail['outerQ']} recoverable={is_recoverable} best={best}",
            flush=True,
        )

    unique_partitions = len(signature_counts)
    duplicate_evaluations = len(failures) - unique_partitions
    all_recoverable = recoverable == len(failures) and len(failures) > 0

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V24")

    output = {
        "schemaVersion": 24,
        "profileType": "36.76-rhythm24-v23-unseen-phase-failure-map-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenChampion": "V17",
        "v23Failures": len(failures),
        "uniqueFailurePartitions": unique_partitions,
        "duplicateFailureEvaluations": duplicate_evaluations,
        "operatingPointRecoverableFailures": recoverable,
        "nonRecoverableRankingFailures": rank_failures,
        "allFailuresOperatingPointRecoverable": all_recoverable,
        "failureSignatureCounts": signature_counts,
        "failures": details,
        "newTuningPerformed": False,
        "diagnosticQSweepOnly": True,
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
        "schemaVersion": 24,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "v23Failures": len(failures),
        "uniqueFailurePartitions": unique_partitions,
        "operatingPointRecoverableFailures": recoverable,
        "nonRecoverableRankingFailures": rank_failures,
        "allFailuresOperatingPointRecoverable": all_recoverable,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V23 FAILURE MAP V24 COMPLETE")
    print("V23 failures:", len(failures))
    print("Unique failure partitions:", unique_partitions)
    print("Duplicate failure evaluations:", duplicate_evaluations)
    print("Operating-point recoverable failures:", recoverable, "/", len(failures))
    print("Non-recoverable ranking failures:", rank_failures)
    print("All failures operating-point recoverable:", all_recoverable)
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
