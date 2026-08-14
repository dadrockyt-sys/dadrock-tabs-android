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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v109-lowband-cross-source-residual-predictability-v110.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v109-lowband-cross-source-residual-predictability-v110-manifest.json"
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
    # Mann-Whitney formulation; ties count half.
    wins = 0.0
    for p in pos:
        wins += float(np.sum(p > neg)) + 0.5 * float(np.sum(p == neg))
    return float(wins / (len(pos) * len(neg)))


def fit_ridge_logistic(x: np.ndarray, y: np.ndarray, lam: float = 4.0, steps: int = 80) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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


def predict(x: np.ndarray, fit: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
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
        raise RuntimeError(f"Missing predeclared V110 features: {missing}")

    xb = np.asarray([[float((s.get("features") or {}).get(f, 0.0)) for f in names] for s in slots], dtype=np.float64)
    measures = np.asarray([int(s["measure"]) for s in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    feature_labels = []
    for n in LOWBAND:
        feature_labels.extend([f"trainMean:{n}", f"trainStd:{n}"])

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
        v96_pass = bool(r.get("v96Passed"))
        oracle_pass = bool(r.get("jointRepresentationQOraclePassed"))
        fold_rows.append({
            "source": str(r.get("source")),
            "phase": phase,
            "fold": fold,
            "v96Passed": v96_pass,
            "oraclePassed": oracle_pass,
            "residualHardFailure": (not v96_pass) and (not oracle_pass),
            "x": vals,
        })

    sources = sorted(set(r["source"] for r in fold_rows))
    if len(sources) != 2:
        raise RuntimeError(f"Expected exactly two exposed sources, got {sources}")

    transfers = []
    all_scores = np.zeros(len(fold_rows), dtype=np.float64)
    all_test_mask = np.zeros(len(fold_rows), dtype=bool)

    for train_source, test_source in ((sources[0], sources[1]), (sources[1], sources[0])):
        train_idx = [i for i, r in enumerate(fold_rows) if r["source"] == train_source]
        test_idx = [i for i, r in enumerate(fold_rows) if r["source"] == test_source]
        xtr = np.asarray([fold_rows[i]["x"] for i in train_idx], dtype=np.float64)
        ytr = np.asarray([fold_rows[i]["residualHardFailure"] for i in train_idx], dtype=bool)
        xte = np.asarray([fold_rows[i]["x"] for i in test_idx], dtype=np.float64)
        yte = np.asarray([fold_rows[i]["residualHardFailure"] for i in test_idx], dtype=bool)

        fit = fit_ridge_logistic(xtr, ytr)
        score = predict(xte, fit)
        auc = auc_score(yte, score)
        for i, s in zip(test_idx, score):
            all_scores[i] = float(s)
            all_test_mask[i] = True

        transfers.append({
            "trainSource": train_source,
            "testSource": test_source,
            "trainRows": len(train_idx),
            "trainResiduals": int(np.sum(ytr)),
            "testRows": len(test_idx),
            "testResiduals": int(np.sum(yte)),
            "testAUC": round(auc, 6),
        })

    y_all = np.asarray([r["residualHardFailure"] for r in fold_rows], dtype=bool)
    pooled_cross_source_auc = auc_score(y_all[all_test_mask], all_scores[all_test_mask])

    # Also report ranking concentration without selecting a threshold/challenger.
    order = np.argsort(-all_scores)
    concentration = []
    for k in (10, 20, 40, 80):
        kk = min(k, len(order))
        picked = order[:kk]
        concentration.append({
            "topK": kk,
            "residualsCaptured": int(np.sum(y_all[picked])),
            "residualCaptureRate": round(float(np.sum(y_all[picked])) / max(int(np.sum(y_all)), 1), 6),
            "precision": round(float(np.mean(y_all[picked])) if kk else 0.0, 6),
        })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V110")

    summary = {
        "rows": len(fold_rows),
        "residualHardFailures": int(np.sum(y_all)),
        "nonResidualRows": int(np.sum(~y_all)),
        "predeclaredTrainingContextFeatures": feature_labels,
        "crossSourceTransfers": transfers,
        "pooledCrossSourceAUC": round(pooled_cross_source_auc, 6),
        "rankingConcentration": concentration,
    }
    out = {
        "schemaVersion": 110,
        "profileType": "low-band-training-context-cross-source-residual-predictability-diagnostic",
        "summary": summary,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "v109DiagnosticFamilyUsed": True,
        "crossSourceOutcomeLabelsUsedForDiagnosisOnly": True,
        "thresholdOrGuardChosen": False,
        "newProductionTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n")

    print("GOMYWAY V110 LOW-BAND CROSS-SOURCE RESIDUAL PREDICTABILITY DIAGNOSTIC COMPLETE")
    print(f"Rows: {len(fold_rows)}")
    print(f"Residual hard failures: {int(np.sum(y_all))}")
    print("\n=== CROSS-SOURCE TRANSFER ===")
    for item in transfers:
        print(item)
    print(f"Pooled cross-source AUC: {pooled_cross_source_auc:.4f}")
    print("\n=== RANKING CONCENTRATION ===")
    for item in concentration:
        print(item)
    print("\nImportant: V109 train/test correlations are complement-coupled and are NOT by themselves evidence of predictability.")
    print("V110 tests predictability by fitting on one exposed source and scoring the other source.")
    print("Previously exposed V56/V57 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("Threshold or guard chosen: False")
    print("New production tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
