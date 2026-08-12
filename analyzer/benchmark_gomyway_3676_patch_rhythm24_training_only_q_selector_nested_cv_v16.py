from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-training-only-q-selector-nested-cv-v16.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-training-only-q-selector-nested-cv-v16-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 4
PERIODS = (2, 4)
TIGHT_Q = 0.025


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase_features(rows: list[dict[str, Any]]) -> np.ndarray:
    out = []
    for r in rows:
        step = int(r["step"])
        vals = []
        for p in PERIODS:
            a = 2.0 * math.pi * (step % p) / float(p)
            vals.extend([math.sin(a), math.cos(a)])
        out.append(vals)
    return np.asarray(out, dtype=np.float64)


def pass_at_q(scores: np.ndarray, yy: np.ndarray, q: float) -> tuple[bool, float, dict[str, Any], dict[str, Any]]:
    held = v1.select_top_fraction(scores, yy, q)
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    passed = held["true"] > 0 and lift >= 5.0
    return bool(passed), float(lift), held, base


def choose_q_train_only(
    x_train: np.ndarray,
    y_train: np.ndarray,
    measures_train: np.ndarray,
    radius: int,
    lam: float,
    base_q: float,
) -> tuple[float, dict[str, Any]]:
    """Choose between V14 q and 0.025 using only outer-training data.

    Inner validation uses shifted-window folds over the outer training partition.
    The tighter q wins only on a strict inner pass-count advantage. Ties retain
    V14's original q, so the selector cannot switch merely on small lift changes.
    """
    lo, hi = int(np.min(measures_train)), int(np.max(measures_train))
    inner_ids = np.asarray(
        [v1.shifted_fold(int(m), lo, hi, INNER_FOLDS) for m in measures_train],
        dtype=np.int16,
    )
    base_passes = 0
    tight_passes = 0
    base_lifts: list[float] = []
    tight_lifts: list[float] = []
    details = []

    for inner_fold in range(INNER_FOLDS):
        val = inner_ids == inner_fold
        subtrain = ~val
        if int(np.sum(val)) == 0 or int(np.sum(subtrain)) == 0:
            continue
        model = v2.fit_pairwise_ranker(
            x_train[subtrain],
            y_train[subtrain],
            measures_train[subtrain],
            radius,
            lam,
        )
        scores = v2.scores_for(x_train[val], model)
        bp, bl, bh, bb = pass_at_q(scores, y_train[val], base_q)
        tp, tl, th, _ = pass_at_q(scores, y_train[val], TIGHT_Q)
        base_passes += int(bp)
        tight_passes += int(tp)
        base_lifts.append(bl)
        tight_lifts.append(tl)
        details.append({
            "innerFold": inner_fold,
            "baseQ": base_q,
            "basePassed": bp,
            "baseLift": round(bl, 2),
            "tightQ": TIGHT_Q,
            "tightPassed": tp,
            "tightLift": round(tl, 2),
            "baseCandidate": bh,
            "tightCandidate": th,
            "base": bb,
        })

    chosen_q = TIGHT_Q if tight_passes > base_passes else base_q
    return float(chosen_q), {
        "baseQ": float(base_q),
        "tightQ": TIGHT_Q,
        "baseInnerPasses": int(base_passes),
        "tightInnerPasses": int(tight_passes),
        "baseMeanLift": round(float(np.mean(base_lifts)) if base_lifts else 0.0, 3),
        "tightMeanLift": round(float(np.mean(tight_lifts)) if tight_lifts else 0.0, 3),
        "chosenQ": float(chosen_q),
        "switchedToTightQ": bool(chosen_q == TIGHT_Q and abs(base_q - TIGHT_Q) > 1e-12),
        "rule": "tight-q-only-on-strict-inner-shifted-pass-count-advantage",
        "innerFolds": details,
    }


def evaluate_scheme(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    name: str,
    fold_fn: Callable[[int], int],
) -> tuple[int, list[dict[str, Any]]]:
    ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
    rows = []
    passes = 0

    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test

        print("    heartbeat V16 V5 model selection", flush=True)
        chosen = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])
        base_q = float(chosen["tailQuantile"])

        print("    heartbeat V16 training-only shifted q selector", flush=True)
        selected_q, selector = choose_q_train_only(
            x[train], y[train], measures[train], radius, lam, base_q
        )

        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)
        passed, lift, held, base = pass_at_q(scores, y[test], selected_q)
        passes += int(passed)

        rows.append({
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train)),
            "testRows": int(np.sum(test)),
            "periods": list(PERIODS),
            "chosenModel": chosen,
            "selector": selector,
            "outerQ": float(selected_q),
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": bool(passed),
        })

        print(
            f"  baseQ={base_q} innerBasePass={selector['baseInnerPasses']}/{INNER_FOLDS} "
            f"tightPass={selector['tightInnerPasses']}/{INNER_FOLDS} chosenQ={selected_q} "
            f"held={held['true']}/{held['false']} precision={held['precision']} "
            f"base={base['precision']} lift={round(lift,2)} pass={passed}",
            flush=True,
        )

    return passes, rows


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows],
        dtype=np.float64,
    )
    x = np.concatenate([x_base, phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V16 rhythm24 training-only q-selector strict nested CV", flush=True)
    print("Periods fixed at [2,4]; q=0.025 may replace V14 q only via inner shifted pass-count win", flush=True)

    n, nr = evaluate_scheme(x, y, measures, "normal", lambda m: m % OUTER_FOLDS)
    s, sr = evaluate_scheme(
        x, y, measures, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS)
    )
    w, wr = evaluate_scheme(
        x, y, measures, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS)
    )

    total = n + s + w
    switched = [
        {"scheme": r["scheme"], "fold": r["fold"], "chosenQ": r["outerQ"]}
        for r in (nr + sr + wr)
        if r["selector"]["switchedToTightQ"]
    ]
    generalizes = n == 5 and s == 5 and w == 5

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V16")

    output = {
        "schemaVersion": 16,
        "profileType": "36.76-rhythm24-training-only-q-selector-strict-nested-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "periods": list(PERIODS),
        "tightQ": TIGHT_Q,
        "selectorRule": "tight-q-only-on-strict-inner-shifted-pass-count-advantage",
        "outerFoldsPassed": total,
        "outerFoldsTotal": 15,
        "normalPasses": n,
        "sectionPasses": s,
        "shiftedPasses": w,
        "normalCvPassed": n == 5,
        "sectionStabilityPassed": s == 5,
        "shiftedWindowStabilityPassed": w == 5,
        "switchedToTightQFolds": switched,
        "rhythm24QSelectorV16Generalizes": generalizes,
        "normal": nr,
        "section": sr,
        "shiftedWindow": wr,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseQ": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 16,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "outerFoldsPassed": total,
        "normalPasses": n,
        "sectionPasses": s,
        "shiftedPasses": w,
        "switchedToTightQFolds": switched,
        "rhythm24QSelectorV16Generalizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 TRAINING-ONLY Q SELECTOR NESTED CV V16 COMPLETE")
    print("Outer folds passed:", total, "/ 15")
    print("Normal passes:", n, "/ 5")
    print("Section passes:", s, "/ 5")
    print("Shifted-window passes:", w, "/ 5")
    print("Switched-to-tight-q folds:", switched)
    print("Rhythm24 q-selector V16 generalizes:", generalizes)
    print("Validated new champion: False")
    print("Professional reference used to choose q: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
