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
    "v56_exposed_120": PUBLIC / "gomyway-3676-patch-rhythm24-v55-unanimous-tight-lift-escape-v56.json",
    "v57_exposed_160": PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json",
}
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v95-safe-broad-r8-l1-guard-v96.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v95-safe-broad-r8-l1-guard-v96-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text())
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows], dtype=np.float64)
    pf = v17.phase_features(rows)
    x_full = np.concatenate([xb, pf], axis=1)
    x_cos = np.concatenate([xb, pf[:, [1, 3]]], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    results = []

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text())
        phase_rows = []
        totals = {
            "foldsTotal": 0,
            "v28Passes": 0,
            "v90Passes": 0,
            "v96Passes": 0,
            "v96RescuesVsV28": 0,
            "v96RegressionsVsV28": 0,
            "v96GainsVsV90": 0,
            "v96LossesVsV90": 0,
            "excludedSafeBroadR8L1Folds": 0,
        }

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
            folds = {int(r["fold"]): r for r in scheme.get("folds") or []}
            p90 = 0
            p96 = 0

            for fold in range(OUTER_FOLDS):
                row = folds[fold]
                train = ids != fold
                test = ~train
                v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
                old_q = float(row.get("outerQ", v88.ANCHOR_Q))
                q, decision = v88.selected_q(row)
                old_tight = abs(old_q - v88.TIGHT_Q) < 1e-12
                safe_broad = abs(old_q - v88.BROAD_Q) < 1e-12 and decision == "keep-broad-low-dispersion"

                cm = row.get("chosenModel") or {}
                radius = cm.get("pairRadius")
                lam = cm.get("lambda")

                if (old_tight or safe_broad) and (radius is None or lam is None):
                    chosen = v5.choose_model(x_full[train], y[train], measures[train])
                    radius = int(chosen["pairRadius"])
                    lam = float(chosen["lambda"])
                elif radius is not None and lam is not None:
                    radius = int(radius)
                    lam = float(lam)

                use_v90 = old_tight or safe_broad
                excluded = bool(safe_broad and radius == 8 and abs(float(lam) - 1.0) < 1e-12)
                use_v96 = old_tight or (safe_broad and not excluded)

                challenger_pass = v28_pass
                if use_v90 or use_v96:
                    model = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
                    challenger_pass, _ = v88.pass_at_q(v2.scores_for(x_cos[test], model), y[test], q)

                v90_pass = challenger_pass if use_v90 else v28_pass
                v96_pass = challenger_pass if use_v96 else v28_pass

                totals["foldsTotal"] += 1
                totals["v28Passes"] += int(v28_pass)
                totals["v90Passes"] += int(v90_pass)
                totals["v96Passes"] += int(v96_pass)
                totals["v96RescuesVsV28"] += int(v96_pass and not v28_pass)
                totals["v96RegressionsVsV28"] += int(v28_pass and not v96_pass)
                totals["v96GainsVsV90"] += int(v96_pass and not v90_pass)
                totals["v96LossesVsV90"] += int(v90_pass and not v96_pass)
                totals["excludedSafeBroadR8L1Folds"] += int(excluded)
                p90 += int(v90_pass)
                p96 += int(v96_pass)

            phase_rows.append({"phase": phase, "v90Passes": p90, "v96Passes": p96})

        totals["v90MinimumPhasePasses"] = min(r["v90Passes"] for r in phase_rows)
        totals["v96MinimumPhasePasses"] = min(r["v96Passes"] for r in phase_rows)
        totals["v96BottleneckPhases"] = [r["phase"] for r in phase_rows if r["v96Passes"] == totals["v96MinimumPhasePasses"]]
        totals["source"] = source_name
        results.append(totals)
        print(source_name, totals, flush=True)

    combined = {
        "foldsTotal": sum(r["foldsTotal"] for r in results),
        "v28Passes": sum(r["v28Passes"] for r in results),
        "v90Passes": sum(r["v90Passes"] for r in results),
        "v96Passes": sum(r["v96Passes"] for r in results),
        "v96RescuesVsV28": sum(r["v96RescuesVsV28"] for r in results),
        "v96RegressionsVsV28": sum(r["v96RegressionsVsV28"] for r in results),
        "v96GainsVsV90": sum(r["v96GainsVsV90"] for r in results),
        "v96LossesVsV90": sum(r["v96LossesVsV90"] for r in results),
        "excludedSafeBroadR8L1Folds": sum(r["excludedSafeBroadR8L1Folds"] for r in results),
        "v90MinimumPhasePassesAcrossSources": min(r["v90MinimumPhasePasses"] for r in results),
        "v96MinimumPhasePassesAcrossSources": min(r["v96MinimumPhasePasses"] for r in results),
    }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V96")

    out = {
        "schemaVersion": 96,
        "profileType": "v90-minus-safe-broad-r8-lambda1-exposed-counterfactual",
        "guard": "V90 unchanged except safe-broad folds with pairRadius=8 and lambda=1.0 fall back to V28",
        "results": results,
        "combined": combined,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v93OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n")

    print("\nGOMYWAY V96 SAFE-BROAD R8 LAMBDA1 GUARD COMPLETE")
    print("Combined:", combined)
    print("Previously exposed V56/V57 only: True")
    print("V93 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
