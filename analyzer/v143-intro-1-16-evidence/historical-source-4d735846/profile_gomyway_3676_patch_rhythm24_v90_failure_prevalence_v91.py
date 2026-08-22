from __future__ import annotations

import hashlib
import json
from collections import defaultdict
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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v90-failure-prevalence-v91.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v90-failure-prevalence-v91-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(old_q: float) -> str:
    if abs(old_q - v88.TIGHT_Q) < 1e-12:
        return "tight"
    if abs(old_q - v88.BROAD_Q) < 1e-12:
        return "broad"
    return "anchor"


def add_stat(stats, field, value, failed, bottleneck_failed):
    rec = stats[field][str(value)]
    rec["total"] += 1
    rec["failures"] += int(failed)
    rec["bottleneckFailures"] += int(bottleneck_failed)


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

    all_fold_rows = []
    source_results = []

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text())
        source_fold_rows = []
        phase_passes = []

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
            folds = {int(r["fold"]): r for r in scheme.get("folds") or []}
            passes = 0

            for fold in range(OUTER_FOLDS):
                row = folds[fold]
                train = ids != fold
                test = ~train
                v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
                old_q = float(row.get("outerQ", v88.ANCHOR_Q))
                old_bucket = bucket(old_q)
                q, decision = v88.selected_q(row)
                safe_broad = old_bucket == "broad" and decision == "keep-broad-low-dispersion"
                use_v90 = old_bucket == "tight" or safe_broad
                selector = row.get("selector") or {}
                cm = row.get("chosenModel") or {}
                radius = cm.get("pairRadius")
                lam = cm.get("lambda")

                if use_v90:
                    if radius is None or lam is None:
                        chosen = v5.choose_model(x_full[train], y[train], measures[train])
                        radius = int(chosen["pairRadius"])
                        lam = float(chosen["lambda"])
                    else:
                        radius = int(radius)
                        lam = float(lam)
                    model = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
                    v90_pass, _ = v88.pass_at_q(v2.scores_for(x_cos[test], model), y[test], q)
                else:
                    v90_pass = v28_pass

                passes += int(v90_pass)
                source_fold_rows.append({
                    "source": source_name,
                    "phase": phase,
                    "fold": fold,
                    "v90Passed": bool(v90_pass),
                    "v28Passed": bool(v28_pass),
                    "oldQBucket": old_bucket,
                    "v90Decision": decision if use_v90 else "v90-fallback-v28",
                    "guardAppliedV90": bool(use_v90),
                    "pairRadius": radius,
                    "lambda": lam,
                    "selectionReason": selector.get("selectionReason"),
                    "strictBroadSupportCount": selector.get("strictBroadSupportCount"),
                    "unanimousTightEscape": selector.get("unanimousTightEscape"),
                })

            phase_passes.append({"phase": phase, "passes": passes})

        minimum = min(x["passes"] for x in phase_passes)
        bottlenecks = {x["phase"] for x in phase_passes if x["passes"] == minimum}
        for r in source_fold_rows:
            r["isBottleneckPhase"] = r["phase"] in bottlenecks
        source_results.append({
            "source": source_name,
            "foldsTotal": len(source_fold_rows),
            "v90Passes": sum(int(r["v90Passed"]) for r in source_fold_rows),
            "minimumPhasePasses": minimum,
            "bottleneckPhases": sorted(bottlenecks),
        })
        all_fold_rows.extend(source_fold_rows)

    stats = defaultdict(lambda: defaultdict(lambda: {"total": 0, "failures": 0, "bottleneckFailures": 0}))
    fields = [
        "oldQBucket", "v90Decision", "guardAppliedV90", "pairRadius", "lambda",
        "selectionReason", "strictBroadSupportCount", "unanimousTightEscape",
    ]
    for r in all_fold_rows:
        failed = not r["v90Passed"]
        bottleneck_failed = failed and r["isBottleneckPhase"]
        for field in fields:
            add_stat(stats, field, r.get(field), failed, bottleneck_failed)

    serial_stats = {}
    for field, buckets in stats.items():
        rows_out = []
        for value, rec in buckets.items():
            total = rec["total"]
            failures = rec["failures"]
            rows_out.append({
                "value": value,
                **rec,
                "failureRate": failures / total if total else 0.0,
            })
        serial_stats[field] = sorted(rows_out, key=lambda x: (-x["failureRate"], -x["failures"], x["value"]))

    combined = {
        "foldsTotal": len(all_fold_rows),
        "v90Passes": sum(int(r["v90Passed"]) for r in all_fold_rows),
        "failures": sum(int(not r["v90Passed"]) for r in all_fold_rows),
        "rescuesVsV28": sum(int(r["v90Passed"] and not r["v28Passed"]) for r in all_fold_rows),
        "regressionsVsV28": sum(int(r["v28Passed"] and not r["v90Passed"]) for r in all_fold_rows),
        "minimumPhasePassesAcrossSources": min(r["minimumPhasePasses"] for r in source_results),
    }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V91")

    out = {
        "schemaVersion": 91,
        "profileType": "exposed-v90-failure-prevalence-diagnostic",
        "sources": source_results,
        "combined": combined,
        "prevalence": serial_stats,
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

    print("\nGOMYWAY V91 EXPOSED V90 FAILURE PREVALENCE COMPLETE")
    print("Combined:", combined)
    for field in fields:
        print(f"\n{field}:")
        for r in serial_stats[field]:
            print(f"  {r['value']}: failures={r['failures']}/{r['total']} rate={r['failureRate']:.3f} bottleneckFailures={r['bottleneckFailures']}")
    print("\nV84 opened confirmation referenced: False")
    print("New reserved 1/256 phases referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
