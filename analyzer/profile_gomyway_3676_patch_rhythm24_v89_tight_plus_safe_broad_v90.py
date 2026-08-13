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
import profile_gomyway_3676_patch_rhythm24_v87_old_tight_radius2_counterfactual_v88 as v88

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"

SOURCES = {
    "v56_exposed_120":
        PUBLIC / "gomyway-3676-patch-rhythm24-v55-unanimous-tight-lift-escape-v56.json",
    "v57_exposed_160":
        PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json",
}

OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v89-tight-plus-safe-broad-v90.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v89-tight-plus-safe-broad-v90-manifest.json"

EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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

    all_results = []

    print("Starting V90 tight + predeclared safe-broad challenger", flush=True)

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text())

        phase_rows = []
        v28_total = 0
        v83_total = 0
        v90_total = 0

        v90_rescues = 0
        v90_regressions = 0
        v90_gain_vs_v83 = 0
        v90_loss_vs_v83 = 0

        tight_guarded = 0
        broad_guarded = 0

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])

            ids = np.asarray([
                v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase)
                for m in measures
            ], dtype=np.int16)

            folds = {int(r["fold"]): r for r in scheme.get("folds") or []}

            p83 = 0
            p90 = 0

            for fold in range(OUTER_FOLDS):
                row = folds[fold]

                test = ids == fold
                train = ~test

                v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
                old_q = float(row.get("outerQ", v88.ANCHOR_Q))

                q, decision = v88.selected_q(row)

                old_tight = abs(old_q - v88.TIGHT_Q) < 1e-12
                safe_broad = (
                    abs(old_q - v88.BROAD_Q) < 1e-12
                    and decision == "keep-broad-low-dispersion"
                )

                # V83 baseline = old-tight only.
                use_v83 = old_tight

                # V90 = V83 plus independently predeclared safe broad branch.
                use_v90 = old_tight or safe_broad

                cm = row.get("chosenModel") or {}

                if use_v83 or use_v90:
                    if "pairRadius" in cm and "lambda" in cm:
                        radius = int(cm["pairRadius"])
                        lam = float(cm["lambda"])
                    else:
                        chosen = v5.choose_model(
                            x_full[train],
                            y[train],
                            measures[train],
                        )
                        radius = int(chosen["pairRadius"])
                        lam = float(chosen["lambda"])

                    model = v2.fit_pairwise_ranker(
                        x_cos[train],
                        y[train],
                        measures[train],
                        radius,
                        lam,
                    )

                    challenger_pass, _ = v88.pass_at_q(
                        v2.scores_for(x_cos[test], model),
                        y[test],
                        q,
                    )
                else:
                    challenger_pass = v28_pass

                v83_pass = challenger_pass if use_v83 else v28_pass
                v90_pass = challenger_pass if use_v90 else v28_pass

                if old_tight:
                    tight_guarded += 1
                if safe_broad:
                    broad_guarded += 1

                p83 += int(v83_pass)
                p90 += int(v90_pass)

                v28_total += int(v28_pass)
                v83_total += int(v83_pass)
                v90_total += int(v90_pass)

                v90_rescues += int(v90_pass and not v28_pass)
                v90_regressions += int(v28_pass and not v90_pass)

                v90_gain_vs_v83 += int(v90_pass and not v83_pass)
                v90_loss_vs_v83 += int(v83_pass and not v90_pass)

            phase_rows.append({
                "phase": phase,
                "v83Passes": p83,
                "v90Passes": p90,
            })

        min83 = min(r["v83Passes"] for r in phase_rows)
        min90 = min(r["v90Passes"] for r in phase_rows)

        result = {
            "source": source_name,
            "foldsTotal": sum(len(s.get("folds") or []) for s in src.get("schemes") or []),
            "v28Passes": v28_total,
            "v83Passes": v83_total,
            "v90Passes": v90_total,
            "v90RescuesVsV28": v90_rescues,
            "v90RegressionsVsV28": v90_regressions,
            "v90GainsVsV83": v90_gain_vs_v83,
            "v90LossesVsV83": v90_loss_vs_v83,
            "tightGuardedFolds": tight_guarded,
            "safeBroadGuardedFolds": broad_guarded,
            "v83MinimumPhasePasses": min83,
            "v90MinimumPhasePasses": min90,
            "v90BottleneckPhases": [
                r["phase"] for r in phase_rows
                if r["v90Passes"] == min90
            ],
        }

        all_results.append(result)
        print(source_name, result, flush=True)

    combined = {
        "foldsTotal": sum(r["foldsTotal"] for r in all_results),
        "v28Passes": sum(r["v28Passes"] for r in all_results),
        "v83Passes": sum(r["v83Passes"] for r in all_results),
        "v90Passes": sum(r["v90Passes"] for r in all_results),
        "v90RescuesVsV28": sum(r["v90RescuesVsV28"] for r in all_results),
        "v90RegressionsVsV28": sum(r["v90RegressionsVsV28"] for r in all_results),
        "v90GainsVsV83": sum(r["v90GainsVsV83"] for r in all_results),
        "v90LossesVsV83": sum(r["v90LossesVsV83"] for r in all_results),
        "v83MinimumPhasePassesAcrossSources":
            min(r["v83MinimumPhasePasses"] for r in all_results),
        "v90MinimumPhasePassesAcrossSources":
            min(r["v90MinimumPhasePasses"] for r in all_results),
    }

    after = sha256(candidate_path)

    if before != after:
        raise RuntimeError("Protected candidate changed during V90")

    out = {
        "schemaVersion": 90,
        "profileType": "v83-plus-predeclared-safe-broad-exposed-counterfactual",
        "guard":
            "apply cosine dual-dispersion challenger when original branch is tight "
            "OR original branch is broad and frozen V64 dispersion decision is "
            "keep-broad-low-dispersion; otherwise fallback to V28",
        "results": all_results,
        "combined": combined,
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

    print("\nGOMYWAY V90 TIGHT + SAFE-BROAD CHALLENGER COMPLETE")
    print("Combined:", combined)
    print("V84 opened confirmation referenced: False")
    print("New reserved 1/256 phases referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
