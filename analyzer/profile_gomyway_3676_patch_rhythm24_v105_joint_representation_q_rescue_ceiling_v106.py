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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v105-joint-representation-q-rescue-ceiling-v106.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v105-joint-representation-q-rescue-ceiling-v106-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
Q_GRID = [round(0.05 + 0.025 * i, 3) for i in range(15)]


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
    x_full = reps["full_phase"]
    y = np.asarray([str(r.get("label")) == "true" for r in slots], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    total = v28_passes = v96_passes = 0
    oracle_passes = oracle_rescues = unrescued = 0
    rep_oracle_counts = {name: 0 for name in reps}
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
                current_q, decision = v88.selected_q(row)
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

                excluded = bool(safe_broad and radius == 8 and abs(float(lam) - 1.0) < 1e-12)
                use_v96 = old_tight or (safe_broad and not excluded)

                combination_passes = {}
                if use_v96:
                    current_model = v2.fit_pairwise_ranker(reps["cosine_current"][train], y[train], measures[train], radius, lam)
                    current_scores = v2.scores_for(reps["cosine_current"][test], current_model)
                    v96_pass, _ = v88.pass_at_q(current_scores, y[test], current_q)

                    for rep_name, x in reps.items():
                        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
                        scores = v2.scores_for(x[test], model)
                        rep_any = False
                        for q in Q_GRID:
                            passed, _ = v88.pass_at_q(scores, y[test], q)
                            combination_passes[f"{rep_name}|q{q:.3f}"] = bool(passed)
                            rep_any = rep_any or bool(passed)
                        rep_oracle_counts[rep_name] += int(rep_any)
                else:
                    v96_pass = v28_pass
                    for rep_name in reps:
                        rep_oracle_counts[rep_name] += int(v28_pass)
                        for q in Q_GRID:
                            combination_passes[f"{rep_name}|q{q:.3f}"] = bool(v28_pass)

                oracle_pass = any(combination_passes.values())
                total += 1
                v28_passes += int(v28_pass)
                v96_passes += int(v96_pass)
                oracle_passes += int(oracle_pass)
                oracle_rescues += int((not v96_pass) and oracle_pass)
                unrescued += int((not v96_pass) and not oracle_pass)

                rows_out.append({
                    "source": source_name,
                    "phase": phase,
                    "fold": fold,
                    "v28Passed": v28_pass,
                    "v96Passed": bool(v96_pass),
                    "currentQ": current_q,
                    "decision": decision,
                    "pairRadius": radius,
                    "lambda": lam,
                    "excluded": excluded,
                    "jointRepresentationQOraclePassed": bool(oracle_pass),
                    "combinationPasses": combination_passes,
                })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V106")

    summary = {
        "rows": total,
        "v28Passes": v28_passes,
        "v96Passes": v96_passes,
        "v96ScorePercent": round(100.0 * v96_passes / total, 4),
        "representations": list(reps.keys()),
        "qGrid": Q_GRID,
        "perRepresentationQOraclePasses": rep_oracle_counts,
        "perRepresentationQOracleScorePercent": {
            k: round(100.0 * v / total, 4) for k, v in rep_oracle_counts.items()
        },
        "perfectPerFoldJointRepresentationQOraclePasses": oracle_passes,
        "perfectPerFoldJointRepresentationQOracleScorePercent": round(100.0 * oracle_passes / total, 4),
        "oracleRescuesOfV96Failures": oracle_rescues,
        "v96FailuresNotRescuedByAnyRepresentationQCombination": unrescued,
    }

    out = {
        "schemaVersion": 106,
        "profileType": "fixed-model-joint-representation-q-rescue-ceiling-on-old-exposed-v56-v57",
        "summary": summary,
        "rowsDetail": rows_out,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "diagnosticRepresentationQGridEnumerated": True,
        "diagnosticOutcomesTaintedForFutureSelection": True,
        "newProductionTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "rowsDetail"}, indent=2) + "\n")

    print("GOMYWAY V106 JOINT REPRESENTATION+Q RESCUE CEILING DIAGNOSTIC COMPLETE")
    print(f"Jimmy exposed V96 scoreboard: {v96_passes}/{total} = {100.0*v96_passes/total:.4f}%")
    print("\n=== PER-REPRESENTATION Q ORACLE ===")
    for name in reps:
        p = rep_oracle_counts[name]
        print(f"{name}: {p}/{total} = {100.0*p/total:.4f}%")
    print(f"\nPerfect per-fold JOINT REPRESENTATION+Q oracle: {oracle_passes}/{total} = {100.0*oracle_passes/total:.4f}%")
    print(f"Oracle rescues of V96 failures: {oracle_rescues}")
    print(f"V96 failures not rescued by ANY representation+q combination: {unrescued}")
    print("\nPreviously exposed V56/V57 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("Diagnostic representation+q outcomes tainted for future selection: True")
    print("New production tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
