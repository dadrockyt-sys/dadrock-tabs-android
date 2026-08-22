from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V106_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v105-joint-representation-q-rescue-ceiling-v106.json"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v110-lowband-cross-source-fallback-utility-v111.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v110-lowband-cross-source-fallback-utility-v111-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
LOWBAND = ["mean::lowBurst", "mean::lowRise", "mean::lowDecay30", "mean::lowPostSlope"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def auc_score(y: np.ndarray, score: np.ndarray) -> float:
    y = np.asarray(y, dtype=bool)
    score = np.asarray(score, dtype=np.float64)
    pos = score[y]
    neg = score[~y]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    wins = 0.0
    for p in pos:
        wins += float(np.sum(p > neg)) + 0.5 * float(np.sum(p == neg))
    return float(wins / (len(pos) * len(neg)))


def fit_ridge_logistic(x: np.ndarray, y: np.ndarray, lam: float = 4.0, steps: int = 80):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    mu = np.mean(x, axis=0)
    sd = np.std(x, axis=0)
    sd = np.where(sd < 1e-9, 1.0, sd)
    z = (x - mu) / sd
    z = np.concatenate([np.ones((len(z), 1)), z], axis=1)
    w = np.zeros(z.shape[1], dtype=np.float64)
    reg = np.eye(len(w), dtype=np.float64) * lam
    reg[0, 0] = 0.0
    for _ in range(steps):
        eta = np.clip(z @ w, -30.0, 30.0)
        p = 1.0 / (1.0 + np.exp(-eta))
        grad = z.T @ (p - y) + reg @ w
        s = np.maximum(p * (1.0 - p), 1e-6)
        h = z.T @ (z * s[:, None]) + reg
        try:
            delta = np.linalg.solve(h, grad)
        except np.linalg.LinAlgError:
            delta = np.linalg.pinv(h) @ grad
        w -= delta
        if float(np.linalg.norm(delta)) < 1e-8:
            break
    return w, mu, sd


def predict(x: np.ndarray, fit) -> np.ndarray:
    w, mu, sd = fit
    z = (np.asarray(x, dtype=np.float64) - mu) / sd
    z = np.concatenate([np.ones((len(z), 1)), z], axis=1)
    return z @ w


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
        raise RuntimeError(f"Missing predeclared V111 features: {missing}")

    xb = np.asarray([[float((s.get("features") or {}).get(f, 0.0)) for f in names] for s in slots], dtype=np.float64)
    measures = np.asarray([int(s["measure"]) for s in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    fold_rows = []
    for r in rows:
        phase = float(r["phase"])
        fold = int(r["fold"])
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        train = ids != fold
        vals = []
        for n in LOWBAND:
            j = idx[n]
            vals.append(float(np.mean(xb[train, j])))
            vals.append(float(np.std(xb[train, j])))
        v96 = bool(r.get("v96Passed"))
        v28 = bool(r.get("v28Passed"))
        fold_rows.append({
            "source": str(r.get("source")),
            "phase": phase,
            "fold": fold,
            "v96Passed": v96,
            "v28Passed": v28,
            "fallbackBeneficial": (not v96) and v28,
            "fallbackHarmful": v96 and (not v28),
            "bothPass": v96 and v28,
            "bothFail": (not v96) and (not v28),
            "x": vals,
        })

    sources = sorted(set(r["source"] for r in fold_rows))
    if len(sources) != 2:
        raise RuntimeError(f"Expected two exposed sources, got {sources}")

    all_scores = np.zeros(len(fold_rows), dtype=np.float64)
    direction_results = []

    for train_source, test_source in ((sources[0], sources[1]), (sources[1], sources[0])):
        tri = [i for i, r in enumerate(fold_rows) if r["source"] == train_source]
        tei = [i for i, r in enumerate(fold_rows) if r["source"] == test_source]
        xtr = np.asarray([fold_rows[i]["x"] for i in tri], dtype=np.float64)
        ytr = np.asarray([fold_rows[i]["fallbackBeneficial"] for i in tri], dtype=bool)
        xte = np.asarray([fold_rows[i]["x"] for i in tei], dtype=np.float64)
        yte = np.asarray([fold_rows[i]["fallbackBeneficial"] for i in tei], dtype=bool)
        fit = fit_ridge_logistic(xtr, ytr)
        score = predict(xte, fit)
        for i, s in zip(tei, score):
            all_scores[i] = float(s)
        direction_results.append({
            "trainSource": train_source,
            "testSource": test_source,
            "trainRows": len(tri),
            "trainBeneficial": int(np.sum(ytr)),
            "testRows": len(tei),
            "testBeneficial": int(np.sum(yte)),
            "testAUCForBeneficialFallback": round(auc_score(yte, score), 6),
        })

    beneficial = np.asarray([r["fallbackBeneficial"] for r in fold_rows], dtype=bool)
    harmful = np.asarray([r["fallbackHarmful"] for r in fold_rows], dtype=bool)
    v96_pass = np.asarray([r["v96Passed"] for r in fold_rows], dtype=bool)
    v28_pass = np.asarray([r["v28Passed"] for r in fold_rows], dtype=bool)

    pooled_auc = auc_score(beneficial, all_scores)
    order = np.argsort(-all_scores)
    ranking = []
    for k in (5, 10, 20, 40, 80):
        kk = min(k, len(order))
        picked = order[:kk]
        b = int(np.sum(beneficial[picked]))
        h = int(np.sum(harmful[picked]))
        hybrid = v96_pass.copy()
        hybrid[picked] = v28_pass[picked]
        ranking.append({
            "topK": kk,
            "beneficialFallbacks": b,
            "harmfulFallbacks": h,
            "netDeltaVsV96": b - h,
            "hybridPasses": int(np.sum(hybrid)),
            "hybridScorePercent": round(100.0 * float(np.mean(hybrid)), 4),
            "precisionBeneficial": round(float(b) / kk if kk else 0.0, 6),
        })

    # Upper bound for ANY fallback-to-V28 gate, regardless of predictability.
    perfect_fallback_oracle = v96_pass | v28_pass

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V111")

    summary = {
        "rows": len(fold_rows),
        "v96Passes": int(np.sum(v96_pass)),
        "v28Passes": int(np.sum(v28_pass)),
        "beneficialFallbackRows": int(np.sum(beneficial)),
        "harmfulFallbackRows": int(np.sum(harmful)),
        "bothPassRows": int(np.sum(v96_pass & v28_pass)),
        "bothFailRows": int(np.sum((~v96_pass) & (~v28_pass))),
        "crossSourceTransfers": direction_results,
        "pooledCrossSourceAUCForBeneficialFallback": round(pooled_auc, 6),
        "fixedTopKDiagnostics": ranking,
        "perfectFallbackToV28OraclePasses": int(np.sum(perfect_fallback_oracle)),
        "perfectFallbackToV28OracleScorePercent": round(100.0 * float(np.mean(perfect_fallback_oracle)), 4),
    }

    out = {
        "schemaVersion": 111,
        "profileType": "low-band-cross-source-fallback-to-v28-utility-diagnostic",
        "summary": summary,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "crossSourceOutcomeLabelsUsedForDiagnosisOnly": True,
        "thresholdOrGuardChosen": False,
        "newProductionTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n")

    print("GOMYWAY V111 LOW-BAND CROSS-SOURCE FALLBACK UTILITY DIAGNOSTIC COMPLETE")
    print(f"V96 scoreboard: {int(np.sum(v96_pass))}/{len(v96_pass)} = {100*np.mean(v96_pass):.4f}%")
    print(f"Beneficial fallback rows (V96 fail, V28 pass): {int(np.sum(beneficial))}")
    print(f"Harmful fallback rows (V96 pass, V28 fail): {int(np.sum(harmful))}")
    print(f"Perfect fallback-to-V28 oracle: {int(np.sum(perfect_fallback_oracle))}/{len(v96_pass)} = {100*np.mean(perfect_fallback_oracle):.4f}%")
    print("\n=== CROSS-SOURCE BENEFICIAL-FALLBACK PREDICTABILITY ===")
    for item in direction_results:
        print(item)
    print(f"Pooled cross-source beneficial-fallback AUC: {pooled_auc:.4f}")
    print("\n=== FIXED TOP-K FALLBACK DIAGNOSTICS ===")
    for item in ranking:
        print(item)
    print("\nPreviously exposed V56/V57 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("Threshold or guard chosen: False")
    print("New production tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
