from __future__ import annotations

import hashlib
import json
import statistics
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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v87-old-tight-radius2-counterfactual-v88.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v87-old-tight-radius2-counterfactual-v88-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
TIGHT_Q = 0.175
ANCHOR_Q = 0.20
BROAD_Q = 0.225
TIGHT_STD_MIN = 0.50
BROAD_STD_MAX = 0.90
FORCED_RADIUS = 2


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


def selected_q(row: dict[str, Any]) -> tuple[float, str]:
    old_q = float(row.get("outerQ", ANCHOR_Q))
    selector = row.get("selector") or {}
    if abs(old_q - TIGHT_Q) < 1e-12:
        std = lift_std(selector, "tight")
        if std is None:
            raise RuntimeError("Missing tight dispersion inputs")
        return (TIGHT_Q, "keep-tight-high-dispersion") if std >= TIGHT_STD_MIN else (ANCHOR_Q, "revert-tight-to-anchor-low-dispersion")
    if abs(old_q - BROAD_Q) < 1e-12:
        std = lift_std(selector, "broad")
        if std is None:
            raise RuntimeError("Missing broad dispersion inputs")
        return (BROAD_Q, "keep-broad-low-dispersion") if std <= BROAD_STD_MAX else (ANCHOR_Q, "revert-broad-to-anchor-high-dispersion")
    return ANCHOR_Q, "keep-anchor"


def pass_at_q(scores: np.ndarray, yy: np.ndarray, q: float) -> tuple[bool, float]:
    held = v1.select_top_fraction(scores, yy, q)
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    return bool(held["true"] > 0 and lift >= 5.0), lift


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
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

    all_results = []
    print("Starting V88 old-tight guarded radius-2 counterfactual on exposed V56/V57 families", flush=True)

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text(encoding="utf-8"))
        phase_rows = []
        v28_total = v83_total = v88_total = 0
        v83_rescues = v83_regressions = 0
        v88_rescues = v88_regressions = 0
        v88_vs_v83_gain = v88_vs_v83_loss = 0
        guarded = 0

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
            folds = {int(r["fold"]): r for r in (scheme.get("folds") or [])}
            p28 = p83 = p88 = 0

            for fold in range(OUTER_FOLDS):
                row = folds[fold]
                test = ids == fold
                train = ~test
                v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
                old_q = float(row.get("outerQ", ANCHOR_Q))
                use_guard = abs(old_q - TIGHT_Q) < 1e-12

                if not use_guard:
                    v83_pass = v28_pass
                    v88_pass = v28_pass
                else:
                    guarded += 1
                    cm = row.get("chosenModel") or {}
                    if "pairRadius" in cm and "lambda" in cm:
                        base_radius = int(cm["pairRadius"])
                        lam = float(cm["lambda"])
                    else:
                        cm = v5.choose_model(x_full[train], y[train], measures[train])
                        base_radius = int(cm["pairRadius"])
                        lam = float(cm["lambda"])

                    q, _ = selected_q(row)
                    model83 = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], base_radius, lam)
                    v83_pass, _ = pass_at_q(v2.scores_for(x_cos[test], model83), y[test], q)
                    model88 = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], FORCED_RADIUS, lam)
                    v88_pass, _ = pass_at_q(v2.scores_for(x_cos[test], model88), y[test], q)

                p28 += int(v28_pass)
                p83 += int(v83_pass)
                p88 += int(v88_pass)
                v28_total += int(v28_pass)
                v83_total += int(v83_pass)
                v88_total += int(v88_pass)
                v83_rescues += int(v83_pass and not v28_pass)
                v83_regressions += int(v28_pass and not v83_pass)
                v88_rescues += int(v88_pass and not v28_pass)
                v88_regressions += int(v28_pass and not v88_pass)
                v88_vs_v83_gain += int(v88_pass and not v83_pass)
                v88_vs_v83_loss += int(v83_pass and not v88_pass)

            phase_rows.append({"phase": phase, "v28Passes": p28, "v83Passes": p83, "v88Passes": p88})

        min83 = min(r["v83Passes"] for r in phase_rows)
        min88 = min(r["v88Passes"] for r in phase_rows)
        result = {
            "source": source_name,
            "foldsTotal": sum(len(s.get("folds") or []) for s in src.get("schemes") or []),
            "guardedOldTightFolds": guarded,
            "v28Passes": v28_total,
            "v83Passes": v83_total,
            "v88Passes": v88_total,
            "v83RescuesVsV28": v83_rescues,
            "v83RegressionsVsV28": v83_regressions,
            "v88RescuesVsV28": v88_rescues,
            "v88RegressionsVsV28": v88_regressions,
            "v88GainsVsV83": v88_vs_v83_gain,
            "v88LossesVsV83": v88_vs_v83_loss,
            "v83MinimumPhasePasses": min83,
            "v88MinimumPhasePasses": min88,
            "v88BottleneckPhases": [r["phase"] for r in phase_rows if r["v88Passes"] == min88],
        }
        all_results.append(result)
        print(source_name, result, flush=True)

    combined = {
        "foldsTotal": sum(r["foldsTotal"] for r in all_results),
        "guardedOldTightFolds": sum(r["guardedOldTightFolds"] for r in all_results),
        "v28Passes": sum(r["v28Passes"] for r in all_results),
        "v83Passes": sum(r["v83Passes"] for r in all_results),
        "v88Passes": sum(r["v88Passes"] for r in all_results),
        "v83RescuesVsV28": sum(r["v83RescuesVsV28"] for r in all_results),
        "v83RegressionsVsV28": sum(r["v83RegressionsVsV28"] for r in all_results),
        "v88RescuesVsV28": sum(r["v88RescuesVsV28"] for r in all_results),
        "v88RegressionsVsV28": sum(r["v88RegressionsVsV28"] for r in all_results),
        "v88GainsVsV83": sum(r["v88GainsVsV83"] for r in all_results),
        "v88LossesVsV83": sum(r["v88LossesVsV83"] for r in all_results),
        "v83MinimumPhasePassesAcrossSources": min(r["v83MinimumPhasePasses"] for r in all_results),
        "v88MinimumPhasePassesAcrossSources": min(r["v88MinimumPhasePasses"] for r in all_results),
    }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V88")

    out = {
        "schemaVersion": 88,
        "profileType": "old-tight-guarded-radius2-counterfactual-on-exposed-families",
        "forcedRadius": FORCED_RADIUS,
        "lambdaFrozenFromOriginalTrainingOnlyModelChoice": True,
        "representation": "base+p2-cos+p4-cos",
        "v83GuardFrozen": "apply V80 only when original outerQ is tight; otherwise fallback to V28",
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
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V88 OLD-TIGHT RADIUS-2 COUNTERFACTUAL COMPLETE")
    print("Combined:", combined)
    print("Uses only previously exposed V56/V57 families: True")
    print("V84 opened confirmation referenced: False")
    print("New reserved 1/256 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
