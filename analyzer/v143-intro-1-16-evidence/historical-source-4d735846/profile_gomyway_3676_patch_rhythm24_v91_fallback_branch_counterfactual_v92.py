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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v91-fallback-branch-counterfactual-v92.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v91-fallback-branch-counterfactual-v92-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q_bucket(old_q: float) -> str:
    if abs(old_q - v88.TIGHT_Q) < 1e-12:
        return "tight"
    if abs(old_q - v88.BROAD_Q) < 1e-12:
        return "broad"
    return "anchor"


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

    variants = {
        "v90": lambda old_bucket, safe_broad: old_bucket == "tight" or safe_broad,
        "v92_anchor_fallback": lambda old_bucket, safe_broad: old_bucket == "tight" or safe_broad or old_bucket == "anchor",
        "v92_unsafe_broad_fallback": lambda old_bucket, safe_broad: old_bucket == "tight" or safe_broad or (old_bucket == "broad" and not safe_broad),
        "v92_all_fallback": lambda old_bucket, safe_broad: True,
    }

    totals = {
        name: {
            "passes": 0,
            "rescuesVsV28": 0,
            "regressionsVsV28": 0,
            "gainsVsV90": 0,
            "lossesVsV90": 0,
            "phasePasses": [],
        }
        for name in variants
    }

    changed_rows = []

    print("Starting V92 exposed fallback-branch counterfactual", flush=True)

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text())

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            ids = np.asarray([
                v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase)
                for m in measures
            ], dtype=np.int16)
            folds = {int(r["fold"]): r for r in scheme.get("folds") or []}
            per_variant_phase = {name: 0 for name in variants}

            for fold in range(OUTER_FOLDS):
                row = folds[fold]
                train = ids != fold
                test = ~train

                v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
                old_q = float(row.get("outerQ", v88.ANCHOR_Q))
                old_bucket = q_bucket(old_q)
                q, decision = v88.selected_q(row)
                safe_broad = old_bucket == "broad" and decision == "keep-broad-low-dispersion"

                cm = row.get("chosenModel") or {}
                radius = cm.get("pairRadius")
                lam = cm.get("lambda")

                need_challenger = any(fn(old_bucket, safe_broad) for fn in variants.values())
                challenger_pass = v28_pass

                if need_challenger:
                    if radius is None or lam is None:
                        chosen = v5.choose_model(x_full[train], y[train], measures[train])
                        radius = int(chosen["pairRadius"])
                        lam = float(chosen["lambda"])
                    else:
                        radius = int(radius)
                        lam = float(lam)

                    model = v2.fit_pairwise_ranker(
                        x_cos[train], y[train], measures[train], radius, lam
                    )
                    challenger_pass, _ = v88.pass_at_q(
                        v2.scores_for(x_cos[test], model), y[test], q
                    )

                outcomes = {}
                for name, fn in variants.items():
                    use = fn(old_bucket, safe_broad)
                    passed = challenger_pass if use else v28_pass
                    outcomes[name] = bool(passed)
                    per_variant_phase[name] += int(passed)
                    totals[name]["passes"] += int(passed)
                    totals[name]["rescuesVsV28"] += int(passed and not v28_pass)
                    totals[name]["regressionsVsV28"] += int(v28_pass and not passed)

                v90_pass = outcomes["v90"]
                for name in variants:
                    if name == "v90":
                        continue
                    totals[name]["gainsVsV90"] += int(outcomes[name] and not v90_pass)
                    totals[name]["lossesVsV90"] += int(v90_pass and not outcomes[name])

                if any(outcomes[name] != v90_pass for name in variants if name != "v90"):
                    changed_rows.append({
                        "source": source_name,
                        "phase": phase,
                        "fold": fold,
                        "oldQBucket": old_bucket,
                        "decision": decision,
                        "safeBroad": safe_broad,
                        "v28Passed": v28_pass,
                        "v90Passed": v90_pass,
                        "challengerPassed": bool(challenger_pass),
                        "pairRadius": radius,
                        "lambda": lam,
                        "outcomes": outcomes,
                    })

            for name in variants:
                totals[name]["phasePasses"].append({
                    "source": source_name,
                    "phase": phase,
                    "passes": per_variant_phase[name],
                })

    summary = {}
    for name, rec in totals.items():
        minimum = min(x["passes"] for x in rec["phasePasses"])
        summary[name] = {
            "foldsPassed": rec["passes"],
            "foldsTotal": 280,
            "rescuesVsV28": rec["rescuesVsV28"],
            "regressionsVsV28": rec["regressionsVsV28"],
            "gainsVsV90": rec["gainsVsV90"],
            "lossesVsV90": rec["lossesVsV90"],
            "minimumPhasePassesAcrossSources": minimum,
            "bottleneckPhases": [
                {"source": x["source"], "phase": x["phase"]}
                for x in rec["phasePasses"]
                if x["passes"] == minimum
            ],
        }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V92")

    out = {
        "schemaVersion": 92,
        "profileType": "exposed-v90-fallback-branch-counterfactual",
        "hypothesis": "V91 showed V90 fallback-to-V28 had the highest branch-level failure prevalence; test fixed representation-only expansion separately on anchor fallback, unsafe-broad fallback, and all fallback folds.",
        "summary": summary,
        "changedRows": changed_rows,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v84OpenedConfirmationReferenced": False,
        "newReserved1over256OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "diagnosticOutcomesTaintedForSelection": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n")

    print("\nGOMYWAY V92 EXPOSED FALLBACK-BRANCH COUNTERFACTUAL COMPLETE")
    for name in variants:
        print(name, summary[name])
    print("Changed rows vs V90:", len(changed_rows))
    print("V84 opened confirmation referenced: False")
    print("New reserved 1/256 phases referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
