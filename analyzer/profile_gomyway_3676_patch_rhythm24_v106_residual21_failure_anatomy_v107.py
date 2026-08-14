from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V106_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v105-joint-representation-q-rescue-ceiling-v106.json"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v106-residual21-failure-anatomy-v107.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v106-residual21-failure-anatomy-v107-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_key(v):
    if isinstance(v, float):
        return round(v, 9)
    return v


def summarize_counter(rows, key):
    c = Counter(safe_key(r.get(key)) for r in rows)
    return {str(k): int(v) for k, v in sorted(c.items(), key=lambda kv: (-kv[1], str(kv[0])))}


def cohen_d(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return 0.0
    va = float(np.var(a, ddof=1))
    vb = float(np.var(b, ddof=1))
    pooled_num = (len(a) - 1) * va + (len(b) - 1) * vb
    pooled_den = len(a) + len(b) - 2
    if pooled_den <= 0:
        return 0.0
    pooled = math.sqrt(max(pooled_num / pooled_den, 0.0))
    if pooled < 1e-12:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled)


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v106 = json.loads(V106_PATH.read_text())
    rows = list(v106.get("rowsDetail") or [])
    if not rows:
        raise RuntimeError("V106 rowsDetail missing")

    source = json.loads(SOURCE_PATH.read_text())
    slots = list(source.get("candidateSlots") or [])
    if not slots or tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    residual = [
        r for r in rows
        if (not bool(r.get("v96Passed"))) and (not bool(r.get("jointRepresentationQOraclePassed")))
    ]
    rescued_failures = [
        r for r in rows
        if (not bool(r.get("v96Passed"))) and bool(r.get("jointRepresentationQOraclePassed"))
    ]
    v96_pass_rows = [r for r in rows if bool(r.get("v96Passed"))]

    names = sorted((slots[0].get("features") or {}).keys())
    xb = np.asarray([[float((s.get("features") or {}).get(f, 0.0)) for f in names] for s in slots], dtype=np.float64)
    pf = np.asarray(v17.phase_features(slots), dtype=np.float64)
    y = np.asarray([str(s.get("label")) == "true" for s in slots], dtype=bool)
    measures = np.asarray([int(s["measure"]) for s in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    fold_metrics = []
    for r in rows:
        phase = float(r["phase"])
        fold = int(r["fold"])
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        test = ids == fold
        if not np.any(test):
            raise RuntimeError(f"Empty test fold for phase={phase} fold={fold}")

        metrics = {
            "source": r.get("source"),
            "phase": phase,
            "fold": fold,
            "v96Passed": bool(r.get("v96Passed")),
            "oraclePassed": bool(r.get("jointRepresentationQOraclePassed")),
            "decision": r.get("decision"),
            "pairRadius": r.get("pairRadius"),
            "lambda": r.get("lambda"),
            "excluded": bool(r.get("excluded")),
            "testSize": int(np.sum(test)),
            "testPositiveRate": float(np.mean(y[test])),
        }
        for j, f in enumerate(names):
            metrics[f"mean:{f}"] = float(np.mean(xb[test, j]))
            metrics[f"std:{f}"] = float(np.std(xb[test, j]))
        for j in range(pf.shape[1]):
            metrics[f"mean:phaseFeature{j}"] = float(np.mean(pf[test, j]))
            metrics[f"std:phaseFeature{j}"] = float(np.std(pf[test, j]))
        fold_metrics.append(metrics)

    metric_by_key = {(r["source"], float(r["phase"]), int(r["fold"])): r for r in fold_metrics}
    residual_metrics = [metric_by_key[(r["source"], float(r["phase"]), int(r["fold"]))] for r in residual]
    rescued_metrics = [metric_by_key[(r["source"], float(r["phase"]), int(r["fold"]))] for r in rescued_failures]
    pass_metrics = [metric_by_key[(r["source"], float(r["phase"]), int(r["fold"]))] for r in v96_pass_rows]

    numeric_keys = [k for k in fold_metrics[0].keys() if k.startswith("mean:") or k.startswith("std:")]
    numeric_keys += ["testSize", "testPositiveRate"]

    effects_vs_rescued = []
    effects_vs_pass = []
    for key in numeric_keys:
        rv = [m[key] for m in residual_metrics]
        qv = [m[key] for m in rescued_metrics]
        pv = [m[key] for m in pass_metrics]
        d_rescued = cohen_d(rv, qv)
        d_pass = cohen_d(rv, pv)
        effects_vs_rescued.append({
            "feature": key,
            "cohenD": round(d_rescued, 6),
            "absCohenD": round(abs(d_rescued), 6),
            "residualMean": round(float(np.mean(rv)), 8),
            "rescuedFailureMean": round(float(np.mean(qv)), 8) if qv else None,
        })
        effects_vs_pass.append({
            "feature": key,
            "cohenD": round(d_pass, 6),
            "absCohenD": round(abs(d_pass), 6),
            "residualMean": round(float(np.mean(rv)), 8),
            "v96PassMean": round(float(np.mean(pv)), 8) if pv else None,
        })

    effects_vs_rescued.sort(key=lambda x: (-x["absCohenD"], x["feature"]))
    effects_vs_pass.sort(key=lambda x: (-x["absCohenD"], x["feature"]))

    phase_bins = defaultdict(int)
    for r in residual:
        b = int(math.floor((float(r["phase"]) % 1.0) * 16.0))
        phase_bins[f"{b}/16-{b+1}/16"] += 1

    residual_rows_out = []
    for r in residual:
        key = (r["source"], float(r["phase"]), int(r["fold"]))
        m = metric_by_key[key]
        residual_rows_out.append({
            "source": r.get("source"),
            "phase": float(r["phase"]),
            "fold": int(r["fold"]),
            "decision": r.get("decision"),
            "pairRadius": r.get("pairRadius"),
            "lambda": r.get("lambda"),
            "excluded": bool(r.get("excluded")),
            "currentQ": r.get("currentQ"),
            "testSize": m["testSize"],
            "testPositiveRate": m["testPositiveRate"],
        })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V107")

    summary = {
        "rows": len(rows),
        "v96Failures": len([r for r in rows if not bool(r.get("v96Passed"))]),
        "rescuedByRepresentationQOracle": len(rescued_failures),
        "residualUnrescuedFailures": len(residual),
        "residualBySource": summarize_counter(residual, "source"),
        "residualByDecision": summarize_counter(residual, "decision"),
        "residualByPairRadius": summarize_counter(residual, "pairRadius"),
        "residualByLambda": summarize_counter(residual, "lambda"),
        "residualByExcluded": summarize_counter(residual, "excluded"),
        "residualByPhaseBin1over16": dict(sorted(phase_bins.items())),
        "topFeatureEffectsResidualVsRescuedFailures": effects_vs_rescued[:20],
        "topFeatureEffectsResidualVsV96Passes": effects_vs_pass[:20],
    }

    out = {
        "schemaVersion": 107,
        "profileType": "residual-21-failure-anatomy-after-representation-q-oracle-on-old-exposed-v56-v57",
        "summary": summary,
        "residualRows": residual_rows_out,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "heldoutLabelsUsedForDiagnosisOnly": True,
        "newProductionTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "residualRows"}, indent=2) + "\n")

    print("GOMYWAY V107 RESIDUAL-21 FAILURE ANATOMY DIAGNOSTIC COMPLETE")
    print(f"V96 failures: {summary['v96Failures']}")
    print(f"Rescued by representation+q oracle: {summary['rescuedByRepresentationQOracle']}")
    print(f"Residual unrescued failures: {summary['residualUnrescuedFailures']}")
    print("Residual by source:", summary["residualBySource"])
    print("Residual by decision:", summary["residualByDecision"])
    print("Residual by pairRadius:", summary["residualByPairRadius"])
    print("Residual by lambda:", summary["residualByLambda"])
    print("Residual by phase bin 1/16:", summary["residualByPhaseBin1over16"])

    print("\n=== TOP FEATURE EFFECTS: RESIDUAL vs RESCUED V96 FAILURES ===")
    for item in summary["topFeatureEffectsResidualVsRescuedFailures"][:12]:
        print(item)

    print("\n=== TOP FEATURE EFFECTS: RESIDUAL vs V96 PASSES ===")
    for item in summary["topFeatureEffectsResidualVsV96Passes"][:12]:
        print(item)

    print("\nPreviously exposed V56/V57 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("Held-out labels used for diagnosis only: True")
    print("New production tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
