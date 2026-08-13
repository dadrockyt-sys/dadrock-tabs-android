from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

import numpy as np

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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v79-cosine-dual-dispersion-combined-v80.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v79-cosine-dual-dispersion-combined-v80-manifest.json"
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


def selected_q(row: dict[str, Any]) -> tuple[float, str, float | None]:
    old_q = float(row.get("outerQ", ANCHOR_Q))
    selector = row.get("selector") or {}
    if abs(old_q - TIGHT_Q) < 1e-12:
        std = lift_std(selector, "tight")
        if std is None:
            raise RuntimeError("Missing tight dispersion inputs")
        if std >= TIGHT_STD_MIN:
            return TIGHT_Q, "keep-tight-high-dispersion", std
        return ANCHOR_Q, "revert-tight-to-anchor-low-dispersion", std
    if abs(old_q - BROAD_Q) < 1e-12:
        std = lift_std(selector, "broad")
        if std is None:
            raise RuntimeError("Missing broad dispersion inputs")
        if std <= BROAD_STD_MAX:
            return BROAD_Q, "keep-broad-low-dispersion", std
        return ANCHOR_Q, "revert-broad-to-anchor-high-dispersion", std
    return ANCHOR_Q, "keep-anchor", None


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
    x = np.concatenate([xb, pf[:, [1, 3]]], axis=1)  # p2-cos + p4-cos only
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    all_results = []
    print("Starting V80 cosine-only + V64 dual-dispersion diagnostic on exposed V56/V57 families", flush=True)

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text(encoding="utf-8"))
        total = v28_total = rescues = regressions = 0
        phase_rows = []
        q_counts = {"tight": 0, "anchor": 0, "broad": 0}
        decision_counts: dict[str, int] = {}

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
            folds = {int(r["fold"]): r for r in (scheme.get("folds") or [])}
            pp = pv = 0

            for fold in range(OUTER_FOLDS):
                row = folds[fold]
                cm = row.get("chosenModel") or {}
                radius = int(cm["pairRadius"])
                lam = float(cm["lambda"])
                q, decision, _ = selected_q(row)
                decision_counts[decision] = decision_counts.get(decision, 0) + 1
                if abs(q - TIGHT_Q) < 1e-12:
                    q_counts["tight"] += 1
                elif abs(q - BROAD_Q) < 1e-12:
                    q_counts["broad"] += 1
                else:
                    q_counts["anchor"] += 1

                test = ids == fold
                train = ~test
                print(f"{source_name} phase={phase} fold={fold} V80 cosine+dual-dispersion ...", flush=True)
                model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
                passed, _ = pass_at_q(v2.scores_for(x[test], model), y[test], q)
                v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))

                pp += int(passed)
                pv += int(v28_pass)
                total += int(passed)
                v28_total += int(v28_pass)
                rescues += int(passed and not v28_pass)
                regressions += int(v28_pass and not passed)

            phase_rows.append({"phase": phase, "passes": pp, "v28Passes": pv})

        min_phase = min(r["passes"] for r in phase_rows)
        bottlenecks = [r["phase"] for r in phase_rows if r["passes"] == min_phase]
        result = {
            "source": source_name,
            "foldsPassed": total,
            "foldsTotal": sum(len(s.get("folds") or []) for s in src.get("schemes") or []),
            "v28ComparisonPasses": v28_total,
            "rescuesVsV28": rescues,
            "regressionsVsV28": regressions,
            "minimumPhasePasses": min_phase,
            "bottleneckPhases": bottlenecks,
            "selectedQCounts": q_counts,
            "decisionCounts": decision_counts,
        }
        all_results.append(result)
        print(source_name, result, flush=True)

    combined = {
        "foldsPassed": sum(r["foldsPassed"] for r in all_results),
        "foldsTotal": sum(r["foldsTotal"] for r in all_results),
        "v28ComparisonPasses": sum(r["v28ComparisonPasses"] for r in all_results),
        "rescuesVsV28": sum(r["rescuesVsV28"] for r in all_results),
        "regressionsVsV28": sum(r["regressionsVsV28"] for r in all_results),
        "minimumPhasePassesAcrossSources": min(r["minimumPhasePasses"] for r in all_results),
    }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V80")

    out = {
        "schemaVersion": 80,
        "profileType": "cosine-only-plus-v64-dual-dispersion-combined-diagnostic",
        "representation": "base+p2-cos+p4-cos",
        "modelHyperparametersFrozenFromSources": True,
        "fixedTightLiftDeltaStdMinimum": TIGHT_STD_MIN,
        "fixedBroadLiftDeltaStdMaximum": BROAD_STD_MAX,
        "thresholdsChosenFromExposedDiagnostics": True,
        "results": all_results,
        "combined": combined,
        "diagnosticOutcomesTaintedForSelection": True,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V80 COSINE-ONLY + DUAL-DISPERSION COMBINED DIAGNOSTIC COMPLETE")
    for r in all_results:
        print(r["source"], "passes", r["foldsPassed"], "/", r["foldsTotal"], "V28", r["v28ComparisonPasses"],
              "rescues", r["rescuesVsV28"], "regressions", r["regressionsVsV28"], "min", r["minimumPhasePasses"],
              "bottlenecks", r["bottleneckPhases"])
    print("Combined:", combined)
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
