from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_rhythm_phase_nested_cv_v13 as v13
import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-rhythm-phase-period-ablation-v14.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-rhythm-phase-period-ablation-v14-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
PERIOD_SETS = ((2,), (4,), (8,), (16,), (2, 4), (4, 8), (8, 16), (2, 4, 8), (4, 8, 16))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase_features(rows: list[dict[str, Any]], periods: tuple[int, ...]) -> np.ndarray:
    out = []
    for r in rows:
        step = int(r["step"])
        vals = []
        for period in periods:
            angle = 2.0 * math.pi * (step % period) / float(period)
            vals.extend([math.sin(angle), math.cos(angle)])
        out.append(vals)
    return np.asarray(out, dtype=np.float64)


def eval_scheme(x, y, measures, fold_fn: Callable[[int], int]) -> tuple[int, list[dict[str, Any]]]:
    ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
    passes = 0
    rows = []
    for fold in range(OUTER_FOLDS):
        test = ids == fold
        train = ~test
        chosen = v5.choose_model(x[train], y[train], measures[train])
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], int(chosen["pairRadius"]), float(chosen["lambda"]))
        scores = v2.scores_for(x[test], model)
        held = v1.select_top_fraction(scores, y[test], float(chosen["tailQuantile"]))
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        passes += int(passed)
        rows.append({"fold": fold, "chosen": chosen, "heldoutBase": base, "heldoutCandidate": held, "heldoutPrecisionLift": round(lift, 2), "passed": bool(passed)})
    return passes, rows


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_rows = list(payload.get("candidateSlots") or [])
    if not source_rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((source_rows[0].get("features") or {}).keys())
    x_base = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in source_rows], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in source_rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in source_rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    policies = []
    best = None
    for periods in PERIOD_SETS:
        print("heartbeat V14 periods", periods, flush=True)
        x = np.concatenate([x_base, phase_features(source_rows, periods)], axis=1)
        n, nr = eval_scheme(x, y, measures, lambda m: m % OUTER_FOLDS)
        s, sr = eval_scheme(x, y, measures, lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS))
        w, wr = eval_scheme(x, y, measures, lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS))
        total = n + s + w
        min_scheme = min(n, s, w)
        item = {"periods": list(periods), "normalPasses": n, "sectionPasses": s, "shiftedPasses": w, "outerFoldsPassed": total, "minSchemePasses": min_scheme, "normal": nr, "section": sr, "shiftedWindow": wr}
        policies.append(item)
        print("V14", periods, "passes", total, "/15 schemes", n, s, w, flush=True)
        key = (min_scheme, total, -len(periods))
        if best is None or key > best[0]:
            best = (key, item)

    winner = best[1]
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V14")

    generalizes = winner["normalPasses"] == 5 and winner["sectionPasses"] == 5 and winner["shiftedPasses"] == 5
    output = {"schemaVersion": 14, "profileType": "36.76-rhythm-phase-period-ablation", "baselinePitchF1": EXPECTED_F1, "baselineMatchedMissingExtra": list(EXPECTED), "policies": policies, "bestPeriods": winner["periods"], "bestOuterFoldsPassed": winner["outerFoldsPassed"], "bestMinSchemePasses": winner["minSchemePasses"], "bestGeneralizes": generalizes, "validatedNewChampion": False, "professionalReferenceUsedDuringDetection": False, "protected949CandidateHashUnchanged": before == after, "candidateEventsModified": False, "v7EventsModified": False, "rendererModified": False, "protectedBaselinesChanged": False, "productionSeparatorChanged": False, "productionPromotionAllowed": False}
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({"schemaVersion": 14, "output": str(OUTPUT_PATH.relative_to(ROOT)), "bestPeriods": winner["periods"], "bestOuterFoldsPassed": winner["outerFoldsPassed"], "bestGeneralizes": generalizes, "validatedNewChampion": False, "productionPromotionAllowed": False}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE RHYTHM PHASE PERIOD ABLATION V14 COMPLETE")
    print("Best periods:", winner["periods"])
    print("Best outer folds passed:", winner["outerFoldsPassed"], "/ 15")
    print("Best scheme passes:", winner["normalPasses"], winner["sectionPasses"], winner["shiftedPasses"])
    print("Best generalizes:", generalizes)
    print("Validated new champion: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
