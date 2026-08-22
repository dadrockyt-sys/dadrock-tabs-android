from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter
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

SOURCES = {
    "v56_exposed_120": PUBLIC / "gomyway-3676-patch-rhythm24-v55-unanimous-tight-lift-escape-v56.json",
    "v57_exposed_160": PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json",
}

OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v88-exposed-v83-floor-pattern-v89.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v88-exposed-v83-floor-pattern-v89-manifest.json"

EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
TIGHT_Q = 0.175
ANCHOR_Q = 0.20
BROAD_Q = 0.225
TIGHT_STD_MIN = 0.50
BROAD_STD_MAX = 0.90


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lift_std(selector: dict[str, Any], side: str) -> float | None:
    vals = []
    for s in selector.get("schemes") or []:
        anchor = s.get("meanAnchorLift")
        other = s.get("meanTightLift") if side == "tight" else s.get("meanBroadLift")
        if anchor is None or other is None:
            return None
        vals.append(float(other) - float(anchor))
    if len(vals) < 2:
        return None
    return float(statistics.pstdev(vals))


def selected_q(row: dict[str, Any]):
    old_q = float(row.get("outerQ", ANCHOR_Q))
    selector = row.get("selector") or {}

    if abs(old_q - TIGHT_Q) < 1e-12:
        std = lift_std(selector, "tight")
        if std >= TIGHT_STD_MIN:
            return TIGHT_Q, "keep-tight-high-dispersion", std
        return ANCHOR_Q, "revert-tight-to-anchor-low-dispersion", std

    if abs(old_q - BROAD_Q) < 1e-12:
        std = lift_std(selector, "broad")
        if std <= BROAD_STD_MAX:
            return BROAD_Q, "keep-broad-low-dispersion", std
        return ANCHOR_Q, "revert-broad-to-anchor-high-dispersion", std

    return ANCHOR_Q, "keep-anchor", None


def pass_at_q(scores, yy, q):
    held = v1.select_top_fraction(scores, yy, q)
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    return bool(held["true"] > 0 and lift >= 5.0), lift


def main():
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text())
    rows = list(payload.get("candidateSlots") or [])

    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([
        [float((r.get("features") or {}).get(f, 0.0)) for f in base_names]
        for r in rows
    ], dtype=np.float64)

    pf = v17.phase_features(rows)
    x_full = np.concatenate([xb, pf], axis=1)
    x_cos = np.concatenate([xb, pf[:, [1, 3]]], axis=1)

    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)

    lo, hi = int(np.min(measures)), int(np.max(measures))

    all_floor_failures = []
    source_results = []

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text())
        phase_rows = []
        fold_rows = []

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            ids = np.asarray([
                v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase)
                for m in measures
            ])

            folds = {int(r["fold"]): r for r in scheme.get("folds") or []}
            phase_passes = 0

            for fold in range(OUTER_FOLDS):
                row = folds[fold]
                test = ids == fold
                train = ~test

                v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
                old_q = float(row.get("outerQ", ANCHOR_Q))

                if abs(old_q - TIGHT_Q) < 1e-12:
                    old_bucket = "tight"
                elif abs(old_q - BROAD_Q) < 1e-12:
                    old_bucket = "broad"
                else:
                    old_bucket = "anchor"

                selector = row.get("selector") or {}
                use_guard = old_bucket == "tight"

                if not use_guard:
                    v83_pass = v28_pass
                    decision = "v83-fallback-v28"
                    q = ANCHOR_Q
                    dispersion = None
                    cm = row.get("chosenModel") or {}
                    radius = cm.get("pairRadius")
                    lam = cm.get("lambda")
                else:
                    cm = row.get("chosenModel") or {}

                    if "pairRadius" in cm and "lambda" in cm:
                        radius = int(cm["pairRadius"])
                        lam = float(cm["lambda"])
                    else:
                        chosen = v5.choose_model(
                            x_full[train],
                            y[train],
                            measures[train]
                        )
                        radius = int(chosen["pairRadius"])
                        lam = float(chosen["lambda"])

                    q, decision, dispersion = selected_q(row)

                    model = v2.fit_pairwise_ranker(
                        x_cos[train],
                        y[train],
                        measures[train],
                        radius,
                        lam
                    )

                    v83_pass, _ = pass_at_q(
                        v2.scores_for(x_cos[test], model),
                        y[test],
                        q
                    )

                phase_passes += int(v83_pass)

                fold_rows.append({
                    "source": source_name,
                    "phase": phase,
                    "fold": fold,
                    "v83Passed": bool(v83_pass),
                    "v28Passed": bool(v28_pass),
                    "oldQBucket": old_bucket,
                    "guardAppliedV80": use_guard,
                    "v80Decision": decision,
                    "finalQ": q,
                    "dispersion": dispersion,
                    "pairRadius": radius,
                    "lambda": lam,
                    "selectionReason": selector.get("selectionReason"),
                    "strictBroadSupportCount": selector.get("strictBroadSupportCount"),
                    "unanimousTightEscape": selector.get("unanimousTightEscape"),
                })

            phase_rows.append({
                "phase": phase,
                "passes": phase_passes
            })

        minimum = min(x["passes"] for x in phase_rows)
        bottlenecks = [x["phase"] for x in phase_rows if x["passes"] == minimum]

        failures = [
            r for r in fold_rows
            if not r["v83Passed"] and r["phase"] in set(bottlenecks)
        ]

        all_floor_failures.extend(failures)

        source_results.append({
            "source": source_name,
            "minimumPhasePasses": minimum,
            "bottleneckPhases": bottlenecks,
            "floorFailureCount": len(failures),
            "floorFailures": failures,
        })

        print(source_name, "minimum", minimum, "bottlenecks", bottlenecks)

        for row in failures:
            print("FloorFailure:", row)

    def counts(field):
        return dict(Counter(str(r.get(field)) for r in all_floor_failures))

    summary = {
        "floorFailureCount": len(all_floor_failures),
        "byOldQBucket": counts("oldQBucket"),
        "byDecision": counts("v80Decision"),
        "byPairRadius": counts("pairRadius"),
        "byLambda": counts("lambda"),
        "bySelectionReason": counts("selectionReason"),
        "byStrictBroadSupportCount": counts("strictBroadSupportCount"),
        "byUnanimousTightEscape": counts("unanimousTightEscape"),
    }

    after = sha256(candidate_path)

    if before != after:
        raise RuntimeError("Protected candidate changed during V89")

    out = {
        "schemaVersion": 89,
        "profileType": "exposed-v83-floor-pattern-diagnostic",
        "sources": source_results,
        "summary": summary,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v84OpenedConfirmationReferenced": False,
        "newReserved1over256OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n")

    print("\nGOMYWAY V89 EXPOSED V83 FLOOR-PATTERN DIAGNOSTIC COMPLETE")
    print("Summary:", summary)
    print("V84 opened confirmation referenced: False")
    print("New reserved 1/256 phases referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
