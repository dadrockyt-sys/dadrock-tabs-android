from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Callable, Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as pairwise

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
BENCHMARK_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-nested-cv-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-pair-coverage-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-pair-coverage-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
MAX_PAIRS = pairwise.MAX_PAIRS


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contiguous_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + width / 2.0) % span
    return min(folds - 1, int(pos / width))


def fold_rows(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    rows = payload.get(key)
    if rows is None:
        rows = payload.get(f"{key}Cv")
    return list(rows or [])


def build_pairs_like_v1(y: np.ndarray, measures: np.ndarray, radius: int) -> tuple[list[tuple[int, int]], int]:
    pos = np.flatnonzero(y)
    neg = np.flatnonzero(~y)
    pairs: list[tuple[int, int]] = []
    eligible_total = 0
    for i in pos:
        near = neg[np.abs(measures[neg] - measures[i]) <= radius]
        eligible_total += int(near.size)
        if len(pairs) < MAX_PAIRS:
            remaining = MAX_PAIRS - len(pairs)
            for j in near[:remaining]:
                pairs.append((int(i), int(j)))
    if eligible_total < 20:
        eligible_total = int(pos.size * neg.size)
        pairs = []
        for i in pos:
            for j in neg:
                pairs.append((int(i), int(j)))
                if len(pairs) >= MAX_PAIRS:
                    break
            if len(pairs) >= MAX_PAIRS:
                break
    return pairs, eligible_total


def coverage_for_fold(
    y_train: np.ndarray,
    m_train: np.ndarray,
    radius: int,
) -> dict[str, Any]:
    pairs, eligible_total = build_pairs_like_v1(y_train, m_train, radius)
    pos_all = np.flatnonzero(y_train)
    neg_all = np.flatnonzero(~y_train)
    pos_used = sorted({i for i, _ in pairs})
    neg_used = sorted({j for _, j in pairs})
    pos_measures_all = sorted({int(m_train[i]) for i in pos_all})
    neg_measures_all = sorted({int(m_train[i]) for i in neg_all})
    pos_measures_used = sorted({int(m_train[i]) for i in pos_used})
    neg_measures_used = sorted({int(m_train[i]) for i in neg_used})

    def pct(a: int, b: int) -> float:
        return round(100.0 * a / b, 2) if b else 0.0

    return {
        "radius": int(radius),
        "eligiblePairs": int(eligible_total),
        "keptPairs": int(len(pairs)),
        "pairRetentionPct": pct(len(pairs), eligible_total),
        "positiveRows": int(pos_all.size),
        "positiveRowsUsed": int(len(pos_used)),
        "positiveRowCoveragePct": pct(len(pos_used), int(pos_all.size)),
        "negativeRows": int(neg_all.size),
        "negativeRowsUsed": int(len(neg_used)),
        "negativeRowCoveragePct": pct(len(neg_used), int(neg_all.size)),
        "positiveMeasures": len(pos_measures_all),
        "positiveMeasuresUsed": len(pos_measures_used),
        "positiveMeasureCoveragePct": pct(len(pos_measures_used), len(pos_measures_all)),
        "negativeMeasures": len(neg_measures_all),
        "negativeMeasuresUsed": len(neg_measures_used),
        "negativeMeasureCoveragePct": pct(len(neg_measures_used), len(neg_measures_all)),
        "positiveUsedMeasureMin": min(pos_measures_used) if pos_measures_used else None,
        "positiveUsedMeasureMax": max(pos_measures_used) if pos_measures_used else None,
        "positiveAllMeasureMin": min(pos_measures_all) if pos_measures_all else None,
        "positiveAllMeasureMax": max(pos_measures_all) if pos_measures_all else None,
    }


def main() -> None:
    candidate_path = pairwise.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")
    rows = list(source.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing")
    if not BENCHMARK_PATH.exists():
        raise RuntimeError("Pairwise nested-CV output missing; run V1 benchmark first")
    benchmark = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))

    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % OUTER_FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS)),
        ("shiftedWindow", lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS)),
    ]

    out_rows: list[dict[str, Any]] = []
    for scheme, fold_fn in schemes:
        saved = {int(r.get("fold", -1)): r for r in fold_rows(benchmark, scheme)}
        ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
        for fold in range(OUTER_FOLDS):
            train = ids != fold
            saved_row = saved.get(fold, {})
            chosen = dict(saved_row.get("chosen") or {})
            radius = int(chosen.get("pairRadius", 4))
            cov = coverage_for_fold(y[train], measures[train], radius)
            row = {
                "scheme": scheme,
                "fold": fold,
                "heldoutPassed": bool(saved_row.get("passed", False)),
                "heldoutLift": float(saved_row.get("heldoutPrecisionLift", 0.0)),
                **cov,
            }
            out_rows.append(row)
            print("COVERAGE", row, flush=True)

    capped = [r for r in out_rows if int(r["eligiblePairs"]) > MAX_PAIRS]
    low_pos_measure = [r for r in out_rows if float(r["positiveMeasureCoveragePct"]) < 80.0]
    mean_pos_measure_cov = float(np.mean([r["positiveMeasureCoveragePct"] for r in out_rows])) if out_rows else 0.0
    mean_pair_retention = float(np.mean([r["pairRetentionPct"] for r in out_rows])) if out_rows else 0.0
    cap_bias_suspected = len(capped) >= 10 and (len(low_pos_measure) >= 5 or mean_pair_retention < 50.0)

    scheme_summary: dict[str, Any] = {}
    for scheme, _ in schemes:
        sr = [r for r in out_rows if r["scheme"] == scheme]
        scheme_summary[scheme] = {
            "folds": len(sr),
            "cappedFolds": sum(int(r["eligiblePairs"]) > MAX_PAIRS for r in sr),
            "meanPairRetentionPct": round(float(np.mean([r["pairRetentionPct"] for r in sr])), 2),
            "meanPositiveMeasureCoveragePct": round(float(np.mean([r["positiveMeasureCoveragePct"] for r in sr])), 2),
            "meanNegativeMeasureCoveragePct": round(float(np.mean([r["negativeMeasureCoveragePct"] for r in sr])), 2),
        }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during pair coverage diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-pair-coverage-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "maxPairs": MAX_PAIRS,
        "folds": out_rows,
        "schemeSummary": scheme_summary,
        "meanPairRetentionPct": round(mean_pair_retention, 2),
        "meanPositiveMeasureCoveragePct": round(mean_pos_measure_cov, 2),
        "pairCapCoverageBiasSuspected": cap_bias_suspected,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "pairCapCoverageBiasSuspected": cap_bias_suspected,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE PAIR COVERAGE V1 COMPLETE")
    print("SCHEME SUMMARY", scheme_summary)
    print("Mean pair retention pct:", round(mean_pair_retention, 2))
    print("Mean positive-measure coverage pct:", round(mean_pos_measure_cov, 2))
    print("Pair-cap coverage bias suspected:", cap_bias_suspected)
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
