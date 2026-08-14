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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v100-representation-rescue-counterfactual-v101.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v100-representation-rescue-counterfactual-v101-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text())
    slots = list(payload.get("candidateSlots") or [])
    if not slots or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((slots[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in slots], dtype=np.float64)
    pf = v17.phase_features(slots)
    reps = {
        "base": xb,
        "phase_col3": np.concatenate([xb, pf[:, [3]]], axis=1),
        "cosine_current": np.concatenate([xb, pf[:, [1, 3]]], axis=1),
        "full_phase": np.concatenate([xb, pf], axis=1),
    }
    x_full_for_choice = reps["full_phase"]
    y = np.asarray([str(r.get("label")) == "true" for r in slots], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    stats = {name: {"passes": 0, "gainsVsV96": 0, "lossesVsV96": 0, "rescuesVsV28": 0, "regressionsVsV28": 0, "rescuesOfV96Failures": 0} for name in reps}
    total = 0
    v28_passes = 0
    v96_passes = 0
    v96_failures = 0
    rows_out = []

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text())
        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
            folds = {int(r["fold"]): r for r in scheme.get("folds") or []}
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
                    chosen = v5.choose_model(x_full_for_choice[train], y[train], measures[train])
                    radius = int(chosen["pairRadius"])
                    lam = float(chosen["lambda"])
                elif radius is not None and lam is not None:
                    radius = int(radius)
                    lam = float(lam)

                excluded = bool(safe_broad and radius == 8 and abs(float(lam) - 1.0) < 1e-12)
                use_v96 = old_tight or (safe_broad and not excluded)

                rep_pass = {}
                if use_v96:
                    for name, x in reps.items():
                        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
                        passed, _ = v88.pass_at_q(v2.scores_for(x[test], model), y[test], q)
                        rep_pass[name] = bool(passed)
                    current_pass = rep_pass["cosine_current"]
                else:
                    rep_pass = {name: v28_pass for name in reps}
                    current_pass = v28_pass

                total += 1
                v28_passes += int(v28_pass)
                v96_passes += int(current_pass)
                v96_failures += int(not current_pass)

                rec = {"source": source_name, "phase": phase, "fold": fold, "v28Passed": v28_pass, "v96Passed": current_pass, "pairRadius": radius, "lambda": lam, "decision": decision, "excluded": excluded, "representationPasses": rep_pass}
                rows_out.append(rec)

                for name, passed in rep_pass.items():
                    s = stats[name]
                    s["passes"] += int(passed)
                    s["gainsVsV96"] += int(passed and not current_pass)
                    s["lossesVsV96"] += int(current_pass and not passed)
                    s["rescuesVsV28"] += int(passed and not v28_pass)
                    s["regressionsVsV28"] += int(v28_pass and not passed)
                    s["rescuesOfV96Failures"] += int((not current_pass) and passed)

    for s in stats.values():
        s["scorePercent"] = round(100.0 * s["passes"] / total, 4)
        s["netVsV96"] = s["gainsVsV96"] - s["lossesVsV96"]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V101")

    out = {
        "schemaVersion": 101,
        "profileType": "fixed-hyperparameter-representation-rescue-counterfactual-on-old-exposed-v56-v57",
        "baseline": {"rows": total, "v28Passes": v28_passes, "v96Passes": v96_passes, "v96Failures": v96_failures, "v96ScorePercent": round(100.0*v96_passes/total, 4)},
        "representationStats": stats,
        "rows": rows_out,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2) + "\n")

    print("GOMYWAY V101 EXPOSED REPRESENTATION RESCUE COUNTERFACTUAL COMPLETE")
    print(f"V96 scoreboard: {v96_passes}/{total} = {100.0*v96_passes/total:.4f}%")
    print(f"V96 failures available to rescue: {v96_failures}")
    print("\n=== REPRESENTATION COUNTERFACTUALS ===")
    for name, s in sorted(stats.items(), key=lambda kv: (-kv[1]["passes"], kv[1]["regressionsVsV28"], kv[0])):
        print(name, s)
    print("\nPreviously exposed V56/V57 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
