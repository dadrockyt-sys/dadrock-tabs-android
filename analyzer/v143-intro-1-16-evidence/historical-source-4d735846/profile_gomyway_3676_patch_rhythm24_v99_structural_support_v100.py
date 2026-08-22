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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v99-structural-support-v100.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v99-structural-support-v100-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branch_name(old_q: float, decision: str, excluded: bool) -> str:
    if excluded:
        return "excluded-safe-broad-r8-lambda1"
    if abs(old_q - v88.TIGHT_Q) < 1e-12:
        return "tight"
    if abs(old_q - v88.BROAD_Q) < 1e-12 and decision == "keep-broad-low-dispersion":
        return "safe-broad"
    return "fallback-v28"


def summarize(rows: list[dict], key_fn):
    groups = defaultdict(lambda: {
        "rows": 0,
        "failures": 0,
        "rescuesVsV28": 0,
        "regressionsVsV28": 0,
        "bothPass": 0,
        "bothFail": 0,
    })
    for r in rows:
        k = str(key_fn(r))
        g = groups[k]
        g["rows"] += 1
        passed = bool(r["v96Passed"])
        base = bool(r["v28Passed"])
        g["failures"] += int(not passed)
        g["rescuesVsV28"] += int(passed and not base)
        g["regressionsVsV28"] += int(base and not passed)
        g["bothPass"] += int(passed and base)
        g["bothFail"] += int((not passed) and (not base))
    out = {}
    for k, g in groups.items():
        g["failureRate"] = round(g["failures"] / g["rows"], 6) if g["rows"] else 0.0
        out[k] = g
    return dict(sorted(out.items(), key=lambda kv: (-kv[1]["failureRate"], -kv[1]["rows"], kv[0])))


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
    x_full = np.concatenate([xb, pf], axis=1)
    x_cos = np.concatenate([xb, pf[:, [1, 3]]], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in slots], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    rows = []
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
                    chosen = v5.choose_model(x_full[train], y[train], measures[train])
                    radius = int(chosen["pairRadius"])
                    lam = float(chosen["lambda"])
                elif radius is not None and lam is not None:
                    radius = int(radius)
                    lam = float(lam)

                excluded = bool(safe_broad and radius == 8 and abs(float(lam) - 1.0) < 1e-12)
                use_v96 = old_tight or (safe_broad and not excluded)
                v96_pass = v28_pass
                if use_v96:
                    model = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
                    v96_pass, _ = v88.pass_at_q(v2.scores_for(x_cos[test], model), y[test], q)

                selector = row.get("selector") or {}
                rows.append({
                    "source": source_name,
                    "phase": phase,
                    "fold": fold,
                    "branch": branch_name(old_q, decision, excluded),
                    "decision": decision if use_v96 else ("excluded-fallback-v28" if excluded else "fallback-v28"),
                    "pairRadius": radius,
                    "lambda": lam,
                    "selectionReason": selector.get("selectionReason"),
                    "strictBroadSupportCount": selector.get("strictBroadSupportCount"),
                    "unanimousTightEscape": selector.get("unanimousTightEscape"),
                    "v96Passed": bool(v96_pass),
                    "v28Passed": bool(v28_pass),
                })

    overall_fail_rate = sum(int(not r["v96Passed"]) for r in rows) / len(rows)
    candidate_signatures = {
        "tight_lambda100": lambda r: r["branch"] == "tight" and r["lambda"] == 100.0,
        "tight_r4_lambda100": lambda r: r["branch"] == "tight" and r["pairRadius"] == 4 and r["lambda"] == 100.0,
        "safe_broad_strict1": lambda r: r["branch"] == "safe-broad" and r["strictBroadSupportCount"] == 1,
        "safe_broad_r4_strict1": lambda r: r["branch"] == "safe-broad" and r["pairRadius"] == 4 and r["strictBroadSupportCount"] == 1,
        "tight_unanimous_escape": lambda r: r["branch"] == "tight" and r["unanimousTightEscape"] is True,
    }
    candidate_support = {}
    for name, pred in candidate_signatures.items():
        items = [r for r in rows if pred(r)]
        failures = sum(int(not r["v96Passed"]) for r in items)
        rescues = sum(int(r["v96Passed"] and not r["v28Passed"]) for r in items)
        regressions = sum(int(r["v28Passed"] and not r["v96Passed"]) for r in items)
        candidate_support[name] = {
            "rows": len(items),
            "failures": failures,
            "failureRate": round(failures / len(items), 6) if items else None,
            "liftVsOverallFailureRate": round((failures / len(items)) / overall_fail_rate, 3) if items and overall_fail_rate else None,
            "rescuesVsV28": rescues,
            "regressionsVsV28": regressions,
            "bothPass": sum(int(r["v96Passed"] and r["v28Passed"]) for r in items),
            "bothFail": sum(int((not r["v96Passed"]) and (not r["v28Passed"])) for r in items),
        }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V100")

    summary = {
        "rows": len(rows),
        "v96Passes": sum(int(r["v96Passed"]) for r in rows),
        "v28Passes": sum(int(r["v28Passed"]) for r in rows),
        "overallFailureRate": round(overall_fail_rate, 6),
        "byBranch": summarize(rows, lambda r: r["branch"]),
        "byBranchLambda": summarize(rows, lambda r: (r["branch"], r["lambda"])),
        "byBranchRadiusLambda": summarize(rows, lambda r: (r["branch"], r["pairRadius"], r["lambda"])),
        "byBranchStrictBroadSupport": summarize(rows, lambda r: (r["branch"], r["strictBroadSupportCount"])),
        "candidateStructuralSupport": candidate_support,
    }

    out = {
        "schemaVersion": 100,
        "profileType": "v99-motivated-structural-signatures-independent-support-on-old-exposed-v56-v57",
        "summary": summary,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "v97UsedOnlyToMotivateStructuralHypotheses": True,
        "phaseBinFromV97NotUsedForGuardSelection": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 100,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateStructuralSupport": candidate_support,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "phaseBinFromV97NotUsedForGuardSelection": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n")

    print("GOMYWAY V100 STRUCTURAL SUPPORT DIAGNOSTIC COMPLETE")
    print(f"Old exposed V56/V57 V96 score: {summary['v96Passes']}/{summary['rows']} = {100.0*summary['v96Passes']/summary['rows']:.4f}%")
    print(f"Overall failure rate: {100.0*overall_fail_rate:.2f}%")
    print("\n=== V99-MOTIVATED STRUCTURAL SIGNATURES ON OLD EXPOSED DATA ===")
    for name, stats in candidate_support.items():
        print(name, stats)
    print("\n=== BRANCH x LAMBDA ===")
    for name, stats in summary["byBranchLambda"].items():
        print(name, stats)
    print("\n=== BRANCH x STRICT-BROAD-SUPPORT ===")
    for name, stats in summary["byBranchStrictBroadSupport"].items():
        print(name, stats)
    print("\nPreviously exposed V56/V57 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("V97 phase-bin locality used to choose a guard: False")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
