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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v111-lowband-phase-interaction-augmentation-v112.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v111-lowband-phase-interaction-augmentation-v112-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5

# Fixed from the coherent V107 low-band residual signature.  V112 does not tune this list.
LOWBAND_FEATURES = ["mean::lowBurst", "mean::lowRise", "mean::lowDecay30", "mean::lowPostSlope"]
PHASE_LABELS = ["p2sin", "p2cos", "p4sin", "p4cos"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_phase_interactions(
    xb: np.ndarray,
    names: list[str],
    pf: np.ndarray,
) -> tuple[np.ndarray, list[str]]:
    idx = {name: i for i, name in enumerate(names)}
    missing = [name for name in LOWBAND_FEATURES if name not in idx]
    if missing:
        raise RuntimeError(f"Missing predeclared V112 low-band features: {missing}")
    if pf.ndim != 2 or pf.shape[1] != 4:
        raise RuntimeError(f"Expected four rhythm phase columns, got shape={pf.shape}")

    cols = []
    labels = []
    # New information is specifically low-band envelope x rhythmic-grid position.
    # No low-band squares/products are included (V108 showed those were harmful).
    for low_name in LOWBAND_FEATURES:
        low = xb[:, idx[low_name]]
        for j, phase_name in enumerate(PHASE_LABELS):
            cols.append(low * pf[:, j])
            labels.append(f"{low_name}*{phase_name}")
    return np.column_stack(cols).astype(np.float64), labels


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text())
    slots = list(payload.get("candidateSlots") or [])
    if not slots or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((slots[0].get("features") or {}).keys())
    xb = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in slots],
        dtype=np.float64,
    )
    pf = np.asarray(v17.phase_features(slots), dtype=np.float64)

    # V96 backbone = base features + the two cosine columns (p2cos, p4cos).
    x_current = np.concatenate([xb, pf[:, [1, 3]]], axis=1)
    phase_interactions, interaction_names = build_phase_interactions(xb, names, pf)
    x_v112 = np.concatenate([x_current, phase_interactions], axis=1)
    x_full = np.concatenate([xb, pf], axis=1)

    y = np.asarray([str(r.get("label")) == "true" for r in slots], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    total = v28_passes = v96_passes = v112_passes = 0
    gains = losses = rescues_v28 = regressions_v28 = rescued_v96_failures = 0
    source_summaries = []
    rows_out = []

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text())
        st = {
            "source": source_name,
            "foldsTotal": 0,
            "v28Passes": 0,
            "v96Passes": 0,
            "v112Passes": 0,
            "gainsVsV96": 0,
            "lossesVsV96": 0,
            "rescuesVsV28": 0,
            "regressionsVsV28": 0,
            "rescuesOfV96Failures": 0,
        }

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            ids = np.asarray(
                [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures],
                dtype=np.int16,
            )
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
                    current_model = v2.fit_pairwise_ranker(
                        x_current[train], y[train], measures[train], radius, lam
                    )
                    current_scores = v2.scores_for(x_current[test], current_model)
                    v96_pass, _ = v88.pass_at_q(current_scores, y[test], current_q)

                    new_model = v2.fit_pairwise_ranker(
                        x_v112[train], y[train], measures[train], radius, lam
                    )
                    new_scores = v2.scores_for(x_v112[test], new_model)
                    v112_pass, _ = v88.pass_at_q(new_scores, y[test], current_q)
                else:
                    v96_pass = v28_pass
                    v112_pass = v28_pass

                gain = (not v96_pass) and bool(v112_pass)
                loss = bool(v96_pass) and (not v112_pass)
                rescue = (not v28_pass) and bool(v112_pass)
                regression = bool(v28_pass) and (not v112_pass)

                total += 1
                v28_passes += int(v28_pass)
                v96_passes += int(v96_pass)
                v112_passes += int(v112_pass)
                gains += int(gain)
                losses += int(loss)
                rescues_v28 += int(rescue)
                regressions_v28 += int(regression)
                rescued_v96_failures += int(gain)

                st["foldsTotal"] += 1
                st["v28Passes"] += int(v28_pass)
                st["v96Passes"] += int(v96_pass)
                st["v112Passes"] += int(v112_pass)
                st["gainsVsV96"] += int(gain)
                st["lossesVsV96"] += int(loss)
                st["rescuesVsV28"] += int(rescue)
                st["regressionsVsV28"] += int(regression)
                st["rescuesOfV96Failures"] += int(gain)

                rows_out.append({
                    "source": source_name,
                    "phase": phase,
                    "fold": fold,
                    "decision": decision,
                    "pairRadius": radius,
                    "lambda": lam,
                    "excluded": excluded,
                    "v28Passed": v28_pass,
                    "v96Passed": bool(v96_pass),
                    "v112Passed": bool(v112_pass),
                    "gainVsV96": bool(gain),
                    "lossVsV96": bool(loss),
                })

        st["v96ScorePercent"] = round(100.0 * st["v96Passes"] / st["foldsTotal"], 4)
        st["v112ScorePercent"] = round(100.0 * st["v112Passes"] / st["foldsTotal"], 4)
        source_summaries.append(st)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V112")

    summary = {
        "foldsTotal": total,
        "v28Passes": v28_passes,
        "v96Passes": v96_passes,
        "v112Passes": v112_passes,
        "v96ScorePercent": round(100.0 * v96_passes / total, 4),
        "v112ScorePercent": round(100.0 * v112_passes / total, 4),
        "gainsVsV96": gains,
        "lossesVsV96": losses,
        "netVsV96": gains - losses,
        "v112RescuesVsV28": rescues_v28,
        "v112RegressionsVsV28": regressions_v28,
        "rescuesOfV96Failures": rescued_v96_failures,
        "predeclaredLowbandFeatures": LOWBAND_FEATURES,
        "phaseFeatures": PHASE_LABELS,
        "derivedInteractionFeatures": interaction_names,
        "sourceSummaries": source_summaries,
    }

    out = {
        "schemaVersion": 112,
        "profileType": "lowband-envelope-by-rhythmic-phase-interaction-augmentation-on-old-exposed-v56-v57",
        "summary": summary,
        "rowsDetail": rows_out,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "v107DiagnosisMotivatedLowbandFamily": True,
        "v108HarmfulLowbandOnlyNonlinearTermsExcluded": True,
        "diagnosticOutcomesTaintedForFutureSelection": True,
        "newProductionTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(
        json.dumps({k: v for k, v in out.items() if k != "rowsDetail"}, indent=2) + "\n"
    )

    print("GOMYWAY V112 LOW-BAND x RHYTHMIC-PHASE INTERACTION DIAGNOSTIC COMPLETE")
    print(f"V96 scoreboard: {v96_passes}/{total} = {100.0*v96_passes/total:.4f}%")
    print(f"V112 scoreboard: {v112_passes}/{total} = {100.0*v112_passes/total:.4f}%")
    print(f"Gains vs V96: {gains}")
    print(f"Losses vs V96: {losses}")
    print(f"Net vs V96: {gains-losses:+d}")
    print(f"V112 rescues vs V28: {rescues_v28}")
    print(f"V112 regressions vs V28: {regressions_v28}")
    print(f"V96 failures rescued by V112: {rescued_v96_failures}")
    print("Predeclared low-band features:", LOWBAND_FEATURES)
    print("Rhythmic phase features:", PHASE_LABELS)
    print("Derived interaction count:", len(interaction_names))
    print("\nPreviously exposed V56/V57 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("Diagnostic outcomes tainted for future selection: True")
    print("New production tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
