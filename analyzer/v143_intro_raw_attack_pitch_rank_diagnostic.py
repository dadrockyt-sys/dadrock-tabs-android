from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import median
from typing import Any, Callable

from v143_intro_raw_attack_temporal_diagnostic import (
    CACHE_PATH,
    REFERENCE_PATH,
    _cluster_events,
    _grid_lookup,
)
from v143_intro_supervised_temporal_assignment import (
    DEVELOPMENT_MEASURES,
    HOLDOUT_MEASURES,
    REPO_ROOT,
    _reference_sets,
)

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-raw-attack-pitch-rank-diagnostic.json"
)

WINDOWS_MS = (50, 75, 100, 125, 150, 200)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _clusters_by_measure(clusters: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for cluster in clusters:
        out.setdefault(int(cluster["measure"]), []).append(cluster)
    for rows in out.values():
        rows.sort(key=lambda row: (float(row["onsetTime"]), int(row["midi"]), int(row["clusterId"])))
    return out


def _best_cluster_per_midi(
    rows: list[dict[str, Any]], target_time: float
) -> dict[int, dict[str, Any]]:
    best: dict[int, dict[str, Any]] = {}
    for row in rows:
        midi = int(row["midi"])
        residual = abs(float(row["onsetTime"]) - float(target_time))
        quality = (
            -residual,
            int(row.get("stemSupport") or 0),
            int(row.get("sweepSupport") or 0),
            int(row.get("detectionCount") or 0),
            _safe_float(row.get("maxAmplitude")),
            -int(row.get("clusterId") or 0),
        )
        current = best.get(midi)
        if current is None or quality > current["_quality"]:
            enriched = dict(row)
            enriched["_quality"] = quality
            enriched["_residual"] = residual
            best[midi] = enriched
    return best


def _score_nearest(row: dict[str, Any], _target_time: float) -> float:
    return -float(row["_residual"])


def _score_amplitude(row: dict[str, Any], _target_time: float) -> float:
    return _safe_float(row.get("maxAmplitude"))


def _score_stem(row: dict[str, Any], _target_time: float) -> float:
    return float(row.get("stemSupport") or 0)


def _score_sweep(row: dict[str, Any], _target_time: float) -> float:
    return float(row.get("sweepSupport") or 0)


def _score_detection(row: dict[str, Any], _target_time: float) -> float:
    return float(row.get("detectionCount") or 0)


def _score_composite(row: dict[str, Any], _target_time: float) -> float:
    residual = float(row["_residual"])
    time_score = math.exp(-0.5 * (residual / 0.060) ** 2)
    stem = min(float(row.get("stemSupport") or 0) / 2.0, 1.0)
    sweep = min(float(row.get("sweepSupport") or 0) / 4.0, 1.0)
    detection = min(float(row.get("detectionCount") or 0) / 8.0, 1.0)
    amplitude = max(0.0, min(_safe_float(row.get("maxAmplitude")), 1.0))
    spread = max(0.0, float(row.get("maxOnsetTime") or 0.0) - float(row.get("minOnsetTime") or 0.0))
    coherence = math.exp(-0.5 * (spread / 0.030) ** 2)
    return (
        0.50 * time_score
        + 0.13 * stem
        + 0.12 * sweep
        + 0.10 * detection
        + 0.08 * amplitude
        + 0.07 * coherence
    )


RANKERS: dict[str, Callable[[dict[str, Any], float], float]] = {
    "nearestTime": _score_nearest,
    "maxAmplitude": _score_amplitude,
    "stemSupport": _score_stem,
    "sweepSupport": _score_sweep,
    "detectionCount": _score_detection,
    "composite": _score_composite,
}


def _rank_midis(
    rows: list[dict[str, Any]],
    target_time: float,
    scorer: Callable[[dict[str, Any], float], float],
) -> list[int]:
    best = _best_cluster_per_midi(rows, target_time)
    ordered = sorted(
        best.values(),
        key=lambda row: (
            -float(scorer(row, target_time)),
            float(row["_residual"]),
            -int(row.get("stemSupport") or 0),
            -int(row.get("sweepSupport") or 0),
            -int(row.get("detectionCount") or 0),
            -_safe_float(row.get("maxAmplitude")),
            int(row["midi"]),
        ),
    )
    return [int(row["midi"]) for row in ordered]


def _evaluate(
    clusters: list[dict[str, Any]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    window_ms: int,
    scorer: Callable[[dict[str, Any], float], float],
) -> dict[str, Any]:
    by_measure = _clusters_by_measure(clusters)
    window = float(window_ms) / 1000.0
    total = 0
    available = 0
    top1 = 0
    top3 = 0
    top5 = 0
    ranks: list[int] = []
    candidate_counts: list[int] = []

    for (measure, step), expected_midis in sorted(reference.items()):
        target_time = grid.get((int(measure), int(step)))
        if target_time is None:
            continue
        rows = [
            row
            for row in by_measure.get(int(measure), [])
            if abs(float(row["onsetTime"]) - float(target_time)) <= window
        ]
        ranking = _rank_midis(rows, float(target_time), scorer)
        candidate_counts.append(len(ranking))
        rank_lookup = {midi: index + 1 for index, midi in enumerate(ranking)}
        for midi in sorted(expected_midis):
            total += 1
            rank = rank_lookup.get(int(midi))
            if rank is None:
                continue
            available += 1
            ranks.append(rank)
            if rank <= 1:
                top1 += 1
            if rank <= 3:
                top3 += 1
            if rank <= 5:
                top5 += 1

    pct = lambda n: round(100.0 * n / max(total, 1), 3)
    return {
        "referencePitchEventCount": total,
        "availabilityRecallPercent": pct(available),
        "top1RecallPercent": pct(top1),
        "top3RecallPercent": pct(top3),
        "top5RecallPercent": pct(top5),
        "medianCorrectPitchRankWhenAvailable": round(float(median(ranks)), 3) if ranks else None,
        "p90CorrectPitchRankWhenAvailable": (
            int(sorted(ranks)[min(len(ranks) - 1, math.ceil(0.90 * len(ranks)) - 1)]) if ranks else None
        ),
        "medianCandidatePitchCountPerReferenceLocation": (
            round(float(median(candidate_counts)), 3) if candidate_counts else 0.0
        ),
    }


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Missing raw attack cache: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference_payload = json.loads(REFERENCE_PATH.read_text())
    grid = _grid_lookup(cache)
    clusters = _cluster_events(cache)
    dev_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    hold_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    print("=== V143 RAW ATTACK PITCH-RANK DIAGNOSTIC ===")
    print("physicalAttackClusterCount:", len(clusters))
    print("Purpose: isolate pitch discrimination with the correct rhythmic location supplied only for offline diagnosis")
    print("Professional reference used by analyzer: False")
    print("Production modified: False")

    report: dict[str, Any] = {
        "reportVersion": 1,
        "scope": "offline-reference-location-pitch-rank-diagnostic",
        "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
        "holdoutMeasures": sorted(HOLDOUT_MEASURES),
        "windows": {},
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineDiagnostic": True,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }

    for window_ms in WINDOWS_MS:
        window_result: dict[str, Any] = {"development": {}, "holdout": {}}
        print()
        print(f"=== WINDOW {window_ms}ms ===")
        print("ranker         devTop1  devTop3  holdTop1 holdTop3 holdAvail medianHoldRank")
        for name, scorer in RANKERS.items():
            dev = _evaluate(clusters, grid, dev_reference, window_ms, scorer)
            hold = _evaluate(clusters, grid, hold_reference, window_ms, scorer)
            window_result["development"][name] = dev
            window_result["holdout"][name] = hold
            print(
                f"{name:<14} "
                f"{dev['top1RecallPercent']:>7.3f}% "
                f"{dev['top3RecallPercent']:>7.3f}% "
                f"{hold['top1RecallPercent']:>7.3f}% "
                f"{hold['top3RecallPercent']:>7.3f}% "
                f"{hold['availabilityRecallPercent']:>7.3f}% "
                f"{str(hold['medianCorrectPitchRankWhenAvailable']):>14}"
            )
        report["windows"][str(window_ms)] = window_result

    best_hold = None
    for window_key, window_result in report["windows"].items():
        for name, metrics in window_result["holdout"].items():
            row = {
                "windowMs": int(window_key),
                "ranker": name,
                **metrics,
            }
            if best_hold is None or (
                row["top1RecallPercent"],
                row["top3RecallPercent"],
                row["top5RecallPercent"],
                -row["medianCandidatePitchCountPerReferenceLocation"],
            ) > (
                best_hold["top1RecallPercent"],
                best_hold["top3RecallPercent"],
                best_hold["top5RecallPercent"],
                -best_hold["medianCandidatePitchCountPerReferenceLocation"],
            ):
                best_hold = row

    report["bestHoldoutDiagnostic"] = best_hold
    if best_hold is None:
        diagnosis = "no-pitch-ranking-result"
    elif float(best_hold["top1RecallPercent"]) >= 60.0:
        diagnosis = "raw-cluster-metadata-can-rank-pitch-next-build-structured-decoder"
    elif float(best_hold["top3RecallPercent"]) >= 75.0:
        diagnosis = "correct-pitch-is-usually-near-top-but-needs-richer-ranking-features"
    else:
        diagnosis = "raw-cluster-metadata-cannot-discriminate-pitch-capture-candidate-specific-harmonic-audio-evidence"
    report["diagnosis"] = diagnosis

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print()
    print("BEST HOLDOUT DIAGNOSTIC:")
    print(json.dumps(best_hold, indent=2))
    print("DIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
