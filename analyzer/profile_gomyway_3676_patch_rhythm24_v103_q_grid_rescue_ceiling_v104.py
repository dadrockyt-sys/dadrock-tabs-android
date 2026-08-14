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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v103-q-grid-rescue-ceiling-v104.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v103-q-grid-rescue-ceiling-v104-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
Q_GRID = [round(0.05 + 0.025 * i, 3) for i in range(15)]  # 0.05 ... 0.40


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
    x_cos = np.concatenate([xb, pf[:, [1, 3]]], axis=1)
    x_full = np.concatenate([xb, pf], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in slots], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    q_stats = {
        f"q{q:.3f}": {
            "q": q,
            "passes": 0,
            "gainsVsV96": 0,
            "lossesVsV96": 0,
            "rescuesVsV28": 0,
            "regressionsVsV28": 0,
            "rescuesOfV96Failures": 0,
        }
        for q in Q_GRID
    }

    total = v28_passes = v96_passes = 0
    oracle_passes = oracle_rescues = unrescued = 0
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

                if use_v96:
                    model = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
                    scores = v2.scores_for(x_cos[test], model)
                    v96_pass, _ = v88.pass_at_q(scores, y[test], current_q)
                    q_passes = {}
                    for q in Q_GRID:
                        passed, _ = v88.pass_at_q(scores, y[test], q)
                        q_passes[f"q{q:.3f}"] = bool(passed)
                else:
                    v96_pass = v28_pass
                    q_passes = {k: bool(v28_pass) for k in q_stats}

                total += 1
                v28_passes += int(v28_pass)
                v96_passes += int(v96_pass)
                oracle_pass = any(q_passes.values())
                oracle_passes += int(oracle_pass)
                oracle_rescues += int((not v96_pass) and oracle_pass)
                unrescued += int((not v96_pass) and not oracle_pass)

                for key, passed in q_passes.items():
                    s = q_stats[key]
                    s["passes"] += int(passed)
                    s["gainsVsV96"] += int(passed and not v96_pass)
                    s["lossesVsV96"] += int(v96_pass and not passed)
                    s["rescuesVsV28"] += int(passed and not v28_pass)
                    s["regressionsVsV28"] += int(v28_pass and not passed)
                    s["rescuesOfV96Failures"] += int((not v96_pass) and passed)

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
                    "qGridPasses": q_passes,
                    "oraclePassed": bool(oracle_pass),
                })

    for s in q_stats.values():
        s["scorePercent"] = round(100.0 * s["passes"] / total, 4)
        s["netVsV96"] = s["gainsVsV96"] - s["lossesVsV96"]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V104")

    summary = {
        "rows": total,
        "v28Passes": v28_passes,
        "v96Passes": v96_passes,
        "v96ScorePercent": round(100.0 * v96_passes / total, 4),
        "qGrid": Q_GRID,
        "qStats": q_stats,
        "perfectPerFoldQOraclePasses": oracle_passes,
        "perfectPerFoldQOracleScorePercent": round(100.0 * oracle_passes / total, 4),
        "oracleRescuesOfV96Failures": oracle_rescues,
        "v96FailuresNotRescuedByAnyQInGrid": unrescued,
    }

    out = {
        "schemaVersion": 104,
        "profileType": "fixed-cosine-fixed-model-q-grid-rescue-ceiling-on-old-exposed-v56-v57",
        "summary": summary,
        "rowsDetail": rows_out,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "diagnosticQGridEnumerated": True,
        "diagnosticOutcomesTaintedForFutureSelection": True,
        "newProductionTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "rowsDetail"}, indent=2) + "\n")

    print("GOMYWAY V104 Q-GRID RESCUE CEILING DIAGNOSTIC COMPLETE")
    print(f"Jimmy exposed V96 scoreboard: {v96_passes}/{total} = {100.0*v96_passes/total:.4f}%")
    print("\n=== FIXED-Q COUNTERFACTUALS ===")
    for key, s in sorted(q_stats.items(), key=lambda kv: (-kv[1]["passes"], kv[1]["regressionsVsV28"], kv[0])):
        print(key, s)
    print(f"\nPerfect per-fold Q oracle: {oracle_passes}/{total} = {100.0*oracle_passes/total:.4f}%")
    print(f"Oracle rescues of V96 failures: {oracle_rescues}")
    print(f"V96 failures not rescued by ANY q in grid: {unrescued}")
    print("\nPreviously exposed V56/V57 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("Diagnostic q-grid outcomes tainted for future selection: True")
    print("New production tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
