from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import profile_gomyway_3676_patch_rhythm24_v109_lowband_cross_source_residual_predictability_v110 as v110

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V112_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v111-lowband-phase-interaction-augmentation-v112.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v113-cross-source-selective-v112-gate-v114.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v113-cross-source-selective-v112-gate-v114-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
LOWBAND = ["mean::lowBurst", "mean::lowRise", "mean::lowDecay30", "mean::lowPostSlope"]
PHASE_LABELS = ["p2sin", "p2cos", "p4sin", "p4cos"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text())
    slots = list(payload.get("candidateSlots") or [])
    if not slots or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")
    if not V112_PATH.exists():
        raise RuntimeError(f"Missing saved V112 output: {V112_PATH}")

    v112 = json.loads(V112_PATH.read_text())
    rows = list(v112.get("rowsDetail") or [])
    if len(rows) != 280:
        raise RuntimeError(f"Expected 280 saved V112 rows, got {len(rows)}")

    names = sorted((slots[0].get("features") or {}).keys())
    idx = {n: i for i, n in enumerate(names)}
    missing = [n for n in LOWBAND if n not in idx]
    if missing:
        raise RuntimeError(f"Missing V114 low-band features: {missing}")

    xb = np.asarray([[float((s.get("features") or {}).get(f, 0.0)) for f in names] for s in slots], dtype=np.float64)
    pf = np.asarray(v17.phase_features(slots), dtype=np.float64)
    measures = np.asarray([int(s["measure"]) for s in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    feature_labels: list[str] = []
    for n in LOWBAND:
        feature_labels.extend([f"trainMean:{n}", f"trainStd:{n}"])
    for n in LOWBAND:
        for j, p in enumerate(PHASE_LABELS):
            feature_labels.extend([f"trainMean:{n}*{p}", f"trainStd:{n}*{p}"])

    fold_rows = []
    for r in rows:
        phase = float(r["phase"])
        fold = int(r["fold"])
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        train = ids != fold
        vals: list[float] = []
        for n in LOWBAND:
            col = xb[train, idx[n]]
            vals.extend([float(np.mean(col)), float(np.std(col))])
        for n in LOWBAND:
            low = xb[train, idx[n]]
            for j in range(4):
                prod = low * pf[train, j]
                vals.extend([float(np.mean(prod)), float(np.std(prod))])
        fold_rows.append({
            "source": str(r.get("source")),
            "phase": phase,
            "fold": fold,
            "gain": bool(r.get("gainVsV96")),
            "loss": bool(r.get("lossVsV96")),
            "changed": bool(r.get("gainVsV96")) or bool(r.get("lossVsV96")),
            "x": vals,
        })

    sources = sorted(set(r["source"] for r in fold_rows))
    if len(sources) != 2:
        raise RuntimeError(f"Expected exactly two exposed sources, got {sources}")

    all_scores = np.zeros(len(fold_rows), dtype=np.float64)
    scored = np.zeros(len(fold_rows), dtype=bool)
    transfers = []

    for train_source, test_source in ((sources[0], sources[1]), (sources[1], sources[0])):
        tr_idx = [i for i, r in enumerate(fold_rows) if r["source"] == train_source]
        te_idx = [i for i, r in enumerate(fold_rows) if r["source"] == test_source]
        xtr = np.asarray([fold_rows[i]["x"] for i in tr_idx], dtype=np.float64)
        ytr = np.asarray([fold_rows[i]["gain"] for i in tr_idx], dtype=bool)
        xte = np.asarray([fold_rows[i]["x"] for i in te_idx], dtype=np.float64)
        yte = np.asarray([fold_rows[i]["gain"] for i in te_idx], dtype=bool)

        fit = v110.fit_ridge_logistic(xtr, ytr, lam=8.0, steps=100)
        score = v110.predict(xte, fit)
        auc = v110.auc_score(yte, score)
        for i, s in zip(te_idx, score):
            all_scores[i] = float(s)
            scored[i] = True

        test_losses = np.asarray([fold_rows[i]["loss"] for i in te_idx], dtype=bool)
        transfers.append({
            "trainSource": train_source,
            "testSource": test_source,
            "trainRows": len(tr_idx),
            "trainGains": int(np.sum(ytr)),
            "trainLosses": int(sum(fold_rows[i]["loss"] for i in tr_idx)),
            "testRows": len(te_idx),
            "testGains": int(np.sum(yte)),
            "testLosses": int(np.sum(test_losses)),
            "testGainAUC": round(float(auc), 6),
        })

    y_gain = np.asarray([r["gain"] for r in fold_rows], dtype=bool)
    y_loss = np.asarray([r["loss"] for r in fold_rows], dtype=bool)
    pooled_auc = v110.auc_score(y_gain[scored], all_scores[scored])

    order = np.argsort(-all_scores)
    ranking = []
    for k in (5, 10, 20, 40, 80):
        kk = min(k, len(order))
        picked = order[:kk]
        gains = int(np.sum(y_gain[picked]))
        losses = int(np.sum(y_loss[picked]))
        ranking.append({
            "topK": kk,
            "gainsCaptured": gains,
            "lossesCaptured": losses,
            "netChangedOutcomeUtility": gains - losses,
            "precisionAmongChanged": round(gains / max(gains + losses, 1), 6),
        })

    changed_idx = np.where(y_gain | y_loss)[0]
    changed_auc = v110.auc_score(y_gain[changed_idx], all_scores[changed_idx]) if len(changed_idx) else 0.5

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V114")

    summary = {
        "rows": len(fold_rows),
        "v112GainsVsV96": int(np.sum(y_gain)),
        "v112LossesVsV96": int(np.sum(y_loss)),
        "changedRows": int(np.sum(y_gain | y_loss)),
        "predeclaredTrainingContextFeatures": feature_labels,
        "crossSourceTransfers": transfers,
        "pooledCrossSourceGainAUCAllRows": round(float(pooled_auc), 6),
        "pooledCrossSourceGainVsLossAUCChangedRows": round(float(changed_auc), 6),
        "fixedTopKUtilityDiagnostics": ranking,
    }

    out = {
        "schemaVersion": 114,
        "profileType": "cross-source-training-context-selective-v112-gate-diagnostic",
        "summary": summary,
        "usesSavedV112OutcomesOnlyOnPreviouslyExposedV56V57": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "heldoutOutcomeChangesUsedOnlyAsCrossSourceDiagnosticLabels": True,
        "thresholdOrGateChosen": False,
        "newProductionTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n")

    print("GOMYWAY V114 CROSS-SOURCE SELECTIVE V112 GATE DIAGNOSTIC COMPLETE")
    print(f"Rows: {len(fold_rows)}")
    print(f"V112 gains/losses vs V96: {int(np.sum(y_gain))}/{int(np.sum(y_loss))}")
    print("\n=== CROSS-SOURCE TRANSFER ===")
    for item in transfers:
        print(item)
    print(f"Pooled cross-source gain AUC, all rows: {pooled_auc:.4f}")
    print(f"Pooled cross-source gain-vs-loss AUC, changed rows only: {changed_auc:.4f}")
    print("\n=== FIXED TOP-K SELECTIVE-V112 UTILITY ===")
    for item in ranking:
        print(item)
    print("\nUses saved V112 outcomes only on previously exposed V56/V57: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("Threshold or gate chosen: False")
    print("New production tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
