from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V106_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v105-joint-representation-q-rescue-ceiling-v106.json"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v108-lowband-train-context-transport-v109.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v108-lowband-train-context-transport-v109-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
LOWBAND = ["mean::lowBurst", "mean::lowRise", "mean::lowDecay30", "mean::lowPostSlope"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cohen_d(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return 0.0
    va = float(np.var(a, ddof=1))
    vb = float(np.var(b, ddof=1))
    pooled = math.sqrt(max((((len(a)-1)*va + (len(b)-1)*vb) / max(len(a)+len(b)-2, 1)), 0.0))
    if pooled < 1e-12:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled)


def corr(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if len(a) < 2 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


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

    names = sorted((slots[0].get("features") or {}).keys())
    idx = {n: i for i, n in enumerate(names)}
    missing = [n for n in LOWBAND if n not in idx]
    if missing:
        raise RuntimeError(f"Missing predeclared V109 features: {missing}")

    xb = np.asarray([[float((s.get("features") or {}).get(f, 0.0)) for f in names] for s in slots], dtype=np.float64)
    measures = np.asarray([int(s["measure"]) for s in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    fold_rows = []
    for r in rows:
        phase = float(r["phase"])
        fold = int(r["fold"])
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        test = ids == fold
        train = ~test
        out = {
            "source": r.get("source"),
            "phase": phase,
            "fold": fold,
            "v96Passed": bool(r.get("v96Passed")),
            "oraclePassed": bool(r.get("jointRepresentationQOraclePassed")),
        }
        for name in LOWBAND:
            j = idx[name]
            out[f"trainMean:{name}"] = float(np.mean(xb[train, j]))
            out[f"testMean:{name}"] = float(np.mean(xb[test, j]))
            out[f"trainStd:{name}"] = float(np.std(xb[train, j]))
            out[f"testStd:{name}"] = float(np.std(xb[test, j]))
        fold_rows.append(out)

    residual = [r for r in fold_rows if (not r["v96Passed"]) and (not r["oraclePassed"])]
    rescued = [r for r in fold_rows if (not r["v96Passed"]) and r["oraclePassed"]]
    passes = [r for r in fold_rows if r["v96Passed"]]

    effects = []
    transport = []
    for name in LOWBAND:
        for stat in ("Mean", "Std"):
            tk = f"train{stat}:{name}"
            sk = f"test{stat}:{name}"
            rv = [r[tk] for r in residual]
            qv = [r[tk] for r in rescued]
            pv = [r[tk] for r in passes]
            effects.append({
                "metric": tk,
                "residualVsRescuedCohenD": round(cohen_d(rv, qv), 6),
                "residualVsPassCohenD": round(cohen_d(rv, pv), 6),
                "residualMean": round(float(np.mean(rv)), 8),
                "rescuedMean": round(float(np.mean(qv)), 8) if qv else None,
                "passMean": round(float(np.mean(pv)), 8) if pv else None,
            })
            transport.append({
                "feature": name,
                "stat": stat.lower(),
                "trainTestCorrelationAcrossFolds": round(corr([r[tk] for r in fold_rows], [r[sk] for r in fold_rows]), 6),
                "trainResidualVsPassAbsD": round(abs(cohen_d(rv, pv)), 6),
                "testResidualVsPassAbsD": round(abs(cohen_d([r[sk] for r in residual], [r[sk] for r in passes])), 6),
            })

    effects.sort(key=lambda x: (-abs(x["residualVsPassCohenD"]), -abs(x["residualVsRescuedCohenD"]), x["metric"]))
    transport.sort(key=lambda x: (-x["trainResidualVsPassAbsD"], -abs(x["trainTestCorrelationAcrossFolds"]), x["feature"], x["stat"]))

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V109")

    summary = {
        "rows": len(fold_rows),
        "residualUnrescuedFailures": len(residual),
        "rescuedV96Failures": len(rescued),
        "v96Passes": len(passes),
        "predeclaredLowBandFeatures": LOWBAND,
        "topTrainingContextEffects": effects,
        "trainToTestTransport": transport,
    }
    out = {
        "schemaVersion": 109,
        "profileType": "low-band-train-context-transport-diagnostic-after-v108-negative-augmentation",
        "summary": summary,
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
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n")

    print("GOMYWAY V109 LOW-BAND TRAIN-CONTEXT TRANSPORT DIAGNOSTIC COMPLETE")
    print(f"Residual unrescued failures: {len(residual)}")
    print(f"Rescued V96 failures: {len(rescued)}")
    print(f"V96 passes: {len(passes)}")
    print("\n=== TOP TRAINING-CONTEXT EFFECTS ===")
    for item in effects[:12]:
        print(item)
    print("\n=== TRAIN->TEST TRANSPORT ===")
    for item in transport:
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
