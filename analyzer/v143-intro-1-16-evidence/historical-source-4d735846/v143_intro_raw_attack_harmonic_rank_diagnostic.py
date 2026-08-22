from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import median
from typing import Any, Callable

from v143_intro_raw_attack_temporal_diagnostic import (
    CACHE_PATH as RAW_CACHE_PATH,
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

HARMONIC_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-raw-attack-harmonic-cache.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-raw-attack-harmonic-rank-diagnostic.json"
)

WINDOWS_MS = (50, 75, 100, 125, 150, 200)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _harmonic_rows(cache: dict[str, Any]) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for raw in cache.get("rows", []) or []:
        if not isinstance(raw, dict):
            continue
        cluster_id = int(raw.get("clusterId") or 0)
        if cluster_id > 0:
            rows[cluster_id] = raw
    return rows


def _enrich_clusters(
    clusters: list[dict[str, Any]],
    harmonic_by_cluster: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for cluster in clusters:
        cluster_id = int(cluster.get("clusterId") or 0)
        harmonic = harmonic_by_cluster.get(cluster_id)
        if harmonic is None:
            continue
        row = dict(cluster)
        row["harmonic"] = dict(harmonic.get("combined") or {})
        row["viewA"] = dict(harmonic.get("viewA") or {})
        row["viewB"] = dict(harmonic.get("viewB") or {})
        enriched.append(row)
    return enriched


def _clusters_by_measure(clusters: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for cluster in clusters:
        out.setdefault(int(cluster["measure"]), []).append(cluster)
    for rows in out.values():
        rows.sort(
            key=lambda row: (
                float(row["onsetTime"]),
                int(row["midi"]),
                int(row["clusterId"]),
            )
        )
    return out


def _feature(row: dict[str, Any], name: str) -> float:
    return _safe_float((row.get("harmonic") or {}).get(name), 0.0)


def _score_mean_fund_attack(row: dict[str, Any], _target_time: float) -> float:
    return _feature(row, "meanFundAttack")


def _score_min_fund_attack(row: dict[str, Any], _target_time: float) -> float:
    return _feature(row, "minFundAttack")


def _score_mean_fund_early(row: dict[str, Any], _target_time: float) -> float:
    return _feature(row, "meanFundEarly")


def _score_mean_harmonic(row: dict[str, Any], _target_time: float) -> float:
    return _feature(row, "meanHarmonicMean")


def _score_min_harmonic(row: dict[str, Any], _target_time: float) -> float:
    return _feature(row, "minHarmonicMean")


def _score_harmonic_plus_fund(row: dict[str, Any], _target_time: float) -> float:
    return _feature(row, "meanHarmonicPlusFund")


def _score_harmonic_minus_sub(row: dict[str, Any], _target_time: float) -> float:
    return _feature(row, "meanHarmonicMinusSub")


def _score_local_peak(row: dict[str, Any], _target_time: float) -> float:
    return _feature(row, "meanLocalPeakMargin")


def _score_cross_view(row: dict[str, Any], _target_time: float) -> float:
    return (
        0.30 * _feature(row, "minFundAttack")
        + 0.25 * _feature(row, "minFundEarly")
        + 0.25 * _feature(row, "minHarmonicMean")
        + 0.20 * _feature(row, "minLocalPeakMargin")
    )


def _score_harmonic_composite(row: dict[str, Any], _target_time: float) -> float:
    return (
        0.24 * _feature(row, "meanFundAttack")
        + 0.16 * _feature(row, "meanFundEarly")
        + 0.10 * _feature(row, "meanFundSustain")
        + 0.20 * _feature(row, "meanHarmonicMean")
        + 0.12 * _feature(row, "meanHarmonicPlusFund")
        + 0.10 * _feature(row, "meanHarmonicMinusSub")
        + 0.08 * _feature(row, "meanLocalPeakMargin")
    )


def _score_harmonic_time(row: dict[str, Any], target_time: float) -> float:
    residual = abs(float(row["onsetTime"]) - float(target_time))
    time_score = math.exp(-0.5 * (residual / 0.060) ** 2)
    harmonic = _score_harmonic_composite(row, target_time)
    return harmonic + 0.35 * time_score


RANKERS: dict[str, Callable[[dict[str, Any], float], float]] = {
    "meanFundAttack": _score_mean_fund_attack,
    "minFundAttack": _score_min_fund_attack,
    "meanFundEarly": _score_mean_fund_early,
    "meanHarmonic": _score_mean_harmonic,
    "minHarmonic": _score_min_harmonic,
    "harmonicPlusFund": _score_harmonic_plus_fund,
    "harmonicMinusSub": _score_harmonic_minus_sub,
    "localPeak": _score_local_peak,
    "crossView": _score_cross_view,
    "harmonicComposite": _score_harmonic_composite,
    "harmonicTime": _score_harmonic_time,
}


def _best_cluster_per_midi(
    rows: list[dict[str, Any]],
    target_time: float,
    scorer: Callable[[dict[str, Any], float], float],
) -> dict[int, dict[str, Any]]:
    best: dict[int, dict[str, Any]] = {}
    for row in rows:
        midi = int(row["midi"])
        residual = abs(float(row["onsetTime"]) - float(target_time))
        score = float(scorer(row, target_time))
        quality = (
            score,
            -residual,
            int(row.get("stemSupport") or 0),
            int(row.get("sweepSupport") or 0),
            int(row.get("detectionCount") or 0),
            -int(row.get("clusterId") or 0),
        )
        current = best.get(midi)
        if current is None or quality > current["_quality"]:
            chosen = dict(row)
            chosen["_quality"] = quality
            chosen["_score"] = score
            chosen["_residual"] = residual
            best[midi] = chosen
    return best


def _rank_midis(
    rows: list[dict[str, Any]],
    target_time: float,
    scorer: Callable[[dict[str, Any], float], float],
) -> list[int]:
    best = _best_cluster_per_midi(rows, target_time, scorer)
    ordered = sorted(
        best.values(),
        key=lambda row: (
            -float(row["_score"]),
            float(row["_residual"]),
            -int(row.get("stemSupport") or 0),
            -int(row.get("sweepSupport") or 0),
            -int(row.get("detectionCount") or 0),
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
            int(sorted(ranks)[min(len(ranks) - 1, math.ceil(0.90 * len(ranks)) - 1)])
            if ranks
            else None
        ),
        "medianCandidatePitchCountPerReferenceLocation": (
            round(float(median(candidate_counts)), 3) if candidate_counts else 0.0
        ),
    }


def main() -> None:
    if not RAW_CACHE_PATH.exists():
        raise RuntimeError(f"Missing raw attack cache: {RAW_CACHE_PATH}")
    if not HARMONIC_CACHE_PATH.exists():
        raise RuntimeError(f"Missing harmonic cache: {HARMONIC_CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    raw_cache = json.loads(RAW_CACHE_PATH.read_text())
    harmonic_cache = json.loads(HARMONIC_CACHE_PATH.read_text())
    reference_payload = json.loads(REFERENCE_PATH.read_text())

    grid = _grid_lookup(raw_cache)
    raw_clusters = _cluster_events(raw_cache)
    harmonic_by_cluster = _harmonic_rows(harmonic_cache)
    clusters = _enrich_clusters(raw_clusters, harmonic_by_cluster)
    dev_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    hold_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    print("=== V143 RAW ATTACK HARMONIC PITCH-RANK DIAGNOSTIC ===")
    print("physicalAttackClusterCount:", len(raw_clusters))
    print("harmonicEvidenceClusterCount:", len(harmonic_by_cluster))
    print("joinedClusterCount:", len(clusters))
    print("Purpose: test whether candidate-specific harmonic audio evidence can rank the correct MIDI pitch")
    print("Professional reference used by analyzer: False")
    print("Production modified: False")

    report: dict[str, Any] = {
        "reportVersion": 1,
        "scope": "offline-reference-location-candidate-specific-harmonic-pitch-rank-diagnostic",
        "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
        "holdoutMeasures": sorted(HOLDOUT_MEASURES),
        "physicalAttackClusterCount": len(raw_clusters),
        "harmonicEvidenceClusterCount": len(harmonic_by_cluster),
        "joinedClusterCount": len(clusters),
        "windows": {},
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineDiagnostic": True,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }

    for window_ms in WINDOWS_MS:
        result: dict[str, Any] = {"development": {}, "holdout": {}}
        print()
        print(f"=== WINDOW {window_ms}ms ===")
        print("ranker               devTop1 devTop3 holdTop1 holdTop3 holdAvail medianHoldRank")
        for name, scorer in RANKERS.items():
            dev = _evaluate(clusters, grid, dev_reference, window_ms, scorer)
            hold = _evaluate(clusters, grid, hold_reference, window_ms, scorer)
            result["development"][name] = dev
            result["holdout"][name] = hold
            print(
                f"{name:<20} "
                f"{dev['top1RecallPercent']:>7.3f}% "
                f"{dev['top3RecallPercent']:>7.3f}% "
                f"{hold['top1RecallPercent']:>7.3f}% "
                f"{hold['top3RecallPercent']:>7.3f}% "
                f"{hold['availabilityRecallPercent']:>7.3f}% "
                f"{str(hold['medianCorrectPitchRankWhenAvailable']):>14}"
            )
        report["windows"][str(window_ms)] = result

    best_hold = None
    for window_key, result in report["windows"].items():
        for name, metrics in result["holdout"].items():
            row = {"windowMs": int(window_key), "ranker": name, **metrics}
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
        diagnosis = "no-harmonic-ranking-result"
    elif float(best_hold["top1RecallPercent"]) >= 55.0:
        diagnosis = "harmonic-audio-evidence-can-discriminate-pitch-build-supervised-runtime-ranker"
    elif float(best_hold["top3RecallPercent"]) >= 65.0:
        diagnosis = "harmonic-audio-evidence-substantially-narrows-pitch-needs-learned-feature-combination"
    elif float(best_hold["top1RecallPercent"]) >= 25.0:
        diagnosis = "harmonic-audio-evidence-helps-but-is-not-yet-sufficient"
    else:
        diagnosis = "single-candidate-cqt-harmonic-evidence-remains-insufficient"
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
