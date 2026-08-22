from __future__ import annotations

import hashlib
import json
import math
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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v114-selective-v112-top2over7-challenger-v115.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v114-selective-v112-top2over7-challenger-v115-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
LOWBAND = ["mean::lowBurst", "mean::lowRise", "mean::lowDecay30", "mean::lowPostSlope"]
PHASE_LABELS = ["p2sin", "p2cos", "p4sin", "p4cos"]
GATE_NUM = 2
GATE_DEN = 7


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
        raise RuntimeError(f"Missing V115 low-band features: {missing}")

    xb = np.asarray([[float((s.get("features") or {}).get(f, 0.0)) for f in names] for s in slots], dtype=np.float64)
    pf = np.asarray(v17.phase_features(slots), dtype=np.float64)
    measures = np.asarray([int(s["measure"]) for s in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

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

        v96_pass = bool(r.get("v96Passed"))
        v112_pass = bool(r.get("v112Passed"))
        fold_rows.append({
            "source": str(r.get("source")),
            "phase": phase,
            "fold": fold,
            "v28Passed": bool(r.get("v28Passed")),
            "v96Passed": v96_pass,
            "v112Passed": v112_pass,
            "gain": (not v96_pass) and v112_pass,
            "loss": v96_pass and (not v112_pass),
            "x": vals,
        })

    sources = sorted(set(r["source"] for r in fold_rows))
    if len(sources) != 2:
        raise RuntimeError(f"Expected exactly two exposed sources, got {sources}")

    selected = np.zeros(len(fold_rows), dtype=bool)
    scores = np.zeros(len(fold_rows), dtype=np.float64)
    source_gate_summaries = []

    for train_source, test_source in ((sources[0], sources[1]), (sources[1], sources[0])):
        tr_idx = [i for i, r in enumerate(fold_rows) if r["source"] == train_source]
        te_idx = [i for i, r in enumerate(fold_rows) if r["source"] == test_source]
        xtr = np.asarray([fold_rows[i]["x"] for i in tr_idx], dtype=np.float64)
        ytr = np.asarray([fold_rows[i]["gain"] for i in tr_idx], dtype=bool)
        xte = np.asarray([fold_rows[i]["x"] for i in te_idx], dtype=np.float64)

        fit = v110.fit_ridge_logistic(xtr, ytr, lam=8.0, steps=100)
        score = v110.predict(xte, fit)
        for i, s in zip(te_idx, score):
            scores[i] = float(s)

        k = int(math.ceil(len(te_idx) * GATE_NUM / GATE_DEN))
        local_order = np.argsort(-score)
        chosen_local = local_order[:k]
        chosen_global = [te_idx[int(j)] for j in chosen_local]
        selected[chosen_global] = True

        gains = sum(1 for i in chosen_global if fold_rows[i]["gain"])
        losses = sum(1 for i in chosen_global if fold_rows[i]["loss"])
        source_gate_summaries.append({
            "trainSource": train_source,
            "testSource": test_source,
            "testRows": len(te_idx),
            "selectedRows": k,
            "selectedFraction": round(k / len(te_idx), 6),
            "gainsCaptured": gains,
            "lossesCaptured": losses,
            "netChangedOutcomeUtility": gains - losses,
        })

    v96_pass = np.asarray([r["v96Passed"] for r in fold_rows], dtype=bool)
    v112_pass = np.asarray([r["v112Passed"] for r in fold_rows], dtype=bool)
    v28_pass = np.asarray([r["v28Passed"] for r in fold_rows], dtype=bool)
    hybrid_pass = np.where(selected, v112_pass, v96_pass)

    gains_vs_v96 = int(np.sum((~v96_pass) & hybrid_pass))
    losses_vs_v96 = int(np.sum(v96_pass & (~hybrid_pass)))
    rescues_vs_v28 = int(np.sum(hybrid_pass & (~v28_pass)))
    regressions_vs_v28 = int(np.sum((~hybrid_pass) & v28_pass))
    both_pass = int(np.sum(hybrid_pass & v28_pass))
    both_fail = int(np.sum((~hybrid_pass) & (~v28_pass)))
    hybrid_passes = int(np.sum(hybrid_pass))
    v96_passes = int(np.sum(v96_pass))

    detail = []
    for i, r in enumerate(fold_rows):
        detail.append({
            "source": r["source"],
            "phase": r["phase"],
            "fold": r["fold"],
            "gateScore": float(scores[i]),
            "selectedForV112": bool(selected[i]),
            "v28Passed": bool(v28_pass[i]),
            "v96Passed": bool(v96_pass[i]),
            "v112Passed": bool(v112_pass[i]),
            "v115Passed": bool(hybrid_pass[i]),
            "gainVsV96": bool((not v96_pass[i]) and hybrid_pass[i]),
            "lossVsV96": bool(v96_pass[i] and (not hybrid_pass[i])),
        })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V115")

    summary = {
        "foldsTotal": len(fold_rows),
        "v96Passes": v96_passes,
        "v96ScorePercent": round(100.0 * v96_passes / len(fold_rows), 4),
        "v115Passes": hybrid_passes,
        "v115ScorePercent": round(100.0 * hybrid_passes / len(fold_rows), 4),
        "selectedRows": int(np.sum(selected)),
        "gateFraction": f"{GATE_NUM}/{GATE_DEN}",
        "gainsVsV96": gains_vs_v96,
        "lossesVsV96": losses_vs_v96,
        "netVsV96": gains_vs_v96 - losses_vs_v96,
        "rescuesVsV28": rescues_vs_v28,
        "regressionsVsV28": regressions_vs_v28,
        "bothPassVsV28": both_pass,
        "bothFailVsV28": both_fail,
        "sourceGateSummaries": source_gate_summaries,
    }

    out = {
        "schemaVersion": 115,
        "profileType": "cross-source-selective-v112-top2over7-development-challenger",
        "summary": summary,
        "rowsDetail": detail,
        "gateMotivatedByV114ExposedDiagnostics": True,
        "developmentOutcomesTaintedForFutureSelection": True,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "newProductionTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "rowsDetail"}, indent=2) + "\n")

    print("GOMYWAY V115 CROSS-SOURCE SELECTIVE V112 TOP-2/7 DEVELOPMENT CHALLENGER COMPLETE")
    print(f"V96 scoreboard: {v96_passes}/{len(fold_rows)} = {100.0*v96_passes/len(fold_rows):.4f}%")
    print(f"V115 scoreboard: {hybrid_passes}/{len(fold_rows)} = {100.0*hybrid_passes/len(fold_rows):.4f}%")
    print(f"Selected for V112: {int(np.sum(selected))}/{len(fold_rows)}")
    print(f"Gains vs V96: {gains_vs_v96}")
    print(f"Losses vs V96: {losses_vs_v96}")
    print(f"Net vs V96: {gains_vs_v96-losses_vs_v96:+d}")
    print(f"V115 rescues vs V28: {rescues_vs_v28}")
    print(f"V115 regressions vs V28: {regressions_vs_v28}")
    print("\n=== SOURCE-WISE CROSS-SOURCE GATE UTILITY ===")
    for item in source_gate_summaries:
        print(item)
    print("\nGate motivated by V114 exposed diagnostics: True")
    print("Development outcomes tainted for future selection: True")
    print("Uses previously exposed V56/V57 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("New production tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
