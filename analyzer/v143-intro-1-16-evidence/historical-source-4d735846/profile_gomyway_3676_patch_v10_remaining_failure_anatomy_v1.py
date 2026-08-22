from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_v5_v9_hybrid_sectionpass_nested_cv_v10 as v10
import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pointwise_ridge_section_calibrated_nested_cv_v9 as v9
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V10_PATH = PUBLIC / "gomyway-3676-patch-v5-v9-hybrid-sectionpass-nested-cv-v10.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-v10-remaining-failure-anatomy-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-v10-remaining-failure-anatomy-v1-manifest.json"
EXPECTED = (272, 595, 341)
DIAGNOSTIC_Q = [0.025, 0.05, 0.075, 0.10, 0.125, 0.15, 0.20]
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def auc_from_scores(y: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(y, dtype=bool)
    scores = np.asarray(scores, dtype=np.float64)
    pos = scores[y]
    neg = scores[~y]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    wins = 0.0
    for p in pos:
        wins += float(np.sum(p > neg)) + 0.5 * float(np.sum(p == neg))
    return float(wins / (len(pos) * len(neg)))


def scheme_ids(measures: np.ndarray, scheme: str) -> np.ndarray:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    if scheme == "normal":
        return np.asarray([int(m) % OUTER_FOLDS for m in measures], dtype=np.int16)
    if scheme == "section":
        return np.asarray([v1.contiguous_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)
    if scheme == "shiftedWindow":
        return np.asarray([v1.shifted_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)
    raise ValueError(f"Unknown scheme: {scheme}")


def q_sweep(scores: np.ndarray, y: np.ndarray) -> list[dict[str, Any]]:
    base = v1.base_stats(y)
    out: list[dict[str, Any]] = []
    for q in DIAGNOSTIC_Q:
        held = v1.select_top_fraction(scores, y, q)
        lift = float(held["precision"]) - float(base["precision"])
        passed = int(held["true"]) > 0 and lift >= 5.0
        out.append({
            "q": float(q),
            "true": int(held["true"]),
            "false": int(held["false"]),
            "precision": held["precision"],
            "selectedPct": held["selectedPct"],
            "basePrecision": base["precision"],
            "lift": round(lift, 2),
            "wouldPassDiagnostic": bool(passed),
        })
    return out


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source profile not anchored to frozen 36.76 champion")
    candidate_slots = list(source.get("candidateSlots") or [])
    if not candidate_slots:
        raise RuntimeError("Spectro-temporal candidateSlots missing")

    hybrid = json.loads(V10_PATH.read_text(encoding="utf-8"))
    feature_names = sorted((candidate_slots[0].get("features") or {}).keys())
    x = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in candidate_slots],
        dtype=np.float64,
    )
    y = np.asarray([str(r.get("label")) == "true" for r in candidate_slots], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in candidate_slots], dtype=np.int32)

    failures: list[dict[str, Any]] = []
    for scheme in ("normal", "section", "shiftedWindow"):
        ids = scheme_ids(measures, scheme)
        for row in list(hybrid.get(scheme) or []):
            if bool(row.get("passed")):
                continue

            fold = int(row["fold"])
            test = ids == fold
            train = ~test
            architecture = str(row.get("architectureChosen") or "v5")

            if architecture == "v9":
                chosen = dict(row.get("v9Choice") or row.get("chosen") or {})
                model = v9.fit_pointwise_ridge(x[train], y[train], float(chosen["lambda"]))
                scores = v9.scores_for(x[test], model)
                chosen_q = float(chosen["tailQuantile"])
                model_detail = {"lambda": float(chosen["lambda"])}
            else:
                chosen = dict(row.get("v5Choice") or row.get("chosen") or {})
                model = v2.fit_pairwise_ranker(
                    x[train], y[train], measures[train], int(chosen["pairRadius"]), float(chosen["lambda"])
                )
                scores = v2.scores_for(x[test], model)
                chosen_q = float(chosen["tailQuantile"])
                model_detail = {
                    "pairRadius": int(chosen["pairRadius"]),
                    "lambda": float(chosen["lambda"]),
                    "pairCount": int(model["pairCount"]),
                }

            auc = auc_from_scores(y[test], scores)
            sweep = q_sweep(scores, y[test])
            passing_q = [r for r in sweep if bool(r["wouldPassDiagnostic"])]
            best = max(sweep, key=lambda r: (float(r["lift"]), int(r["true"]), -int(r["false"])))

            if passing_q:
                failure_type = "operatingPointRecoverableDiagnostic"
            elif auc < 0.5:
                failure_type = "rankingInversion"
            elif auc < 0.55:
                failure_type = "weakRankSeparation"
            else:
                failure_type = "rankSignalButTailNotRecoverable"

            rec = {
                "scheme": scheme,
                "fold": fold,
                "architectureChosen": architecture,
                "chosenQ": chosen_q,
                "modelDetail": model_detail,
                "v5SectionPassCount": int((row.get("v5Choice") or {}).get("sectionPassCount", -1)),
                "v9SectionPassCount": int((row.get("v9Choice") or {}).get("sectionPassCount", -1)),
                "heldoutPrecisionLift": float(row.get("heldoutPrecisionLift", 0.0)),
                "aucDiagnostic": round(auc, 6),
                "failureType": failure_type,
                "diagnosticPassingQs": [float(r["q"]) for r in passing_q],
                "bestDiagnosticQ": float(best["q"]),
                "bestDiagnosticLift": float(best["lift"]),
                "qSweep": sweep,
            }
            failures.append(rec)
            print("FAILURE", rec, flush=True)

    type_counts: dict[str, int] = {}
    scheme_counts: dict[str, int] = {}
    architecture_counts: dict[str, int] = {}
    for r in failures:
        type_counts[r["failureType"]] = type_counts.get(r["failureType"], 0) + 1
        scheme_counts[r["scheme"]] = scheme_counts.get(r["scheme"], 0) + 1
        architecture_counts[r["architectureChosen"]] = architecture_counts.get(r["architectureChosen"], 0) + 1

    recoverable = type_counts.get("operatingPointRecoverableDiagnostic", 0)
    rank_problem = (
        type_counts.get("rankingInversion", 0)
        + type_counts.get("weakRankSeparation", 0)
        + type_counts.get("rankSignalButTailNotRecoverable", 0)
    )

    if recoverable == len(failures) and failures:
        next_target = "find-new-training-only-calibration-signal-for-v10-residuals"
    elif rank_problem >= 2:
        next_target = "new-complementary-ranking-representation-for-v10-residuals"
    else:
        next_target = "mixed-residual-mechanisms-profile-fold-specific-signals"

    summary = {
        "remainingFailureCount": len(failures),
        "schemeFailureCounts": scheme_counts,
        "architectureFailureCounts": architecture_counts,
        "failureTypeCounts": type_counts,
        "meanFailureAuc": round(float(np.mean([r["aucDiagnostic"] for r in failures])), 6) if failures else None,
        "diagnosticallyRecoverableOperatingPointFailures": recoverable,
        "rankingRelatedFailures": rank_problem,
        "nextTarget": next_target,
    }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V10 remaining-failure diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-v10-remaining-failure-anatomy-diagnostic",
        "importantCaveat": "Held-out labels are used only after the strict V10 architecture has scored each outer fold. Diagnostic q sweep is explanatory only and must not be used directly for promotion or selector fitting.",
        "summary": summary,
        "failures": failures,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseHybrid": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "remainingFailureCount": len(failures),
        "nextTarget": next_target,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH V10 REMAINING FAILURE ANATOMY V1 COMPLETE")
    print("Remaining failures:", len(failures))
    print("Failure type counts:", type_counts)
    print("Scheme failure counts:", scheme_counts)
    print("Architecture failure counts:", architecture_counts)
    print("Mean failure AUC:", summary["meanFailureAuc"])
    print("Next target:", next_target)
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Professional reference used to choose hybrid: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
