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
    / "intro-harmonic-family-rank-diagnostic.json"
)

WINDOWS_MS = (50, 75, 100, 125, 150, 200)
HARMONIC_OFFSETS = (
    (12, 1.00),
    (19, 0.78),
    (24, 0.62),
    (28, 0.48),
    (31, 0.36),
    (36, 0.25),
)


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
    out: list[dict[str, Any]] = []
    for cluster in clusters:
        harmonic = harmonic_by_cluster.get(int(cluster.get("clusterId") or 0))
        if harmonic is None:
            continue
        row = dict(cluster)
        row["harmonic"] = dict(harmonic.get("combined") or {})
        out.append(row)
    return out


def _clusters_by_measure(clusters: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for cluster in clusters:
        out.setdefault(int(cluster["measure"]), []).append(cluster)
    for rows in out.values():
        rows.sort(key=lambda row: (float(row["onsetTime"]), int(row["midi"]), int(row["clusterId"])))
    return out


def _h(row: dict[str, Any], name: str) -> float:
    return _safe_float((row.get("harmonic") or {}).get(name), 0.0)


def _row_support(row: dict[str, Any], target_time: float) -> float:
    residual = abs(float(row["onsetTime"]) - float(target_time))
    time_score = math.exp(-0.5 * (residual / 0.060) ** 2)
    stem = min(float(row.get("stemSupport") or 0) / 2.0, 1.0)
    sweep = min(float(row.get("sweepSupport") or 0) / 4.0, 1.0)
    detection = min(float(row.get("detectionCount") or 0) / 8.0, 1.0)
    amplitude = max(0.0, min(_safe_float(row.get("maxAmplitude")), 1.0))
    return 0.42 * time_score + 0.16 * stem + 0.14 * sweep + 0.12 * detection + 0.16 * amplitude


def _best_per_midi(rows: list[dict[str, Any]], target_time: float) -> dict[int, dict[str, Any]]:
    best: dict[int, dict[str, Any]] = {}
    for row in rows:
        midi = int(row["midi"])
        residual = abs(float(row["onsetTime"]) - float(target_time))
        quality = (
            _row_support(row, target_time),
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
            chosen["_residual"] = residual
            chosen["_support"] = float(quality[0])
            best[midi] = chosen
    return best


def _aligned_family_support(
    best: dict[int, dict[str, Any]],
    midi: int,
    direction: int,
) -> float:
    base = best.get(midi)
    if base is None:
        return 0.0
    base_onset = float(base["onsetTime"])
    total = 0.0
    denom = 0.0
    for offset, weight in HARMONIC_OFFSETS:
        family_midi = midi + direction * int(offset)
        family = best.get(family_midi)
        if family is None:
            continue
        onset_delta = abs(float(family["onsetTime"]) - base_onset)
        alignment = math.exp(-0.5 * (onset_delta / 0.035) ** 2)
        total += float(weight) * alignment * float(family.get("_support") or 0.0)
        denom += float(weight)
    return total / denom if denom else 0.0


def _score_lowest(midi: int, _row: dict[str, Any], _best: dict[int, dict[str, Any]], _target: float) -> float:
    return -float(midi)


def _score_upper_family(midi: int, row: dict[str, Any], best: dict[int, dict[str, Any]], target: float) -> float:
    return 0.30 * float(row.get("_support") or 0.0) + 0.70 * _aligned_family_support(best, midi, +1)


def _score_alias_suppressed(midi: int, row: dict[str, Any], best: dict[int, dict[str, Any]], target: float) -> float:
    upper = _aligned_family_support(best, midi, +1)
    lower = _aligned_family_support(best, midi, -1)
    return 0.35 * float(row.get("_support") or 0.0) + 0.85 * upper - 1.00 * lower


def _score_spectral_ownership(midi: int, row: dict[str, Any], best: dict[int, dict[str, Any]], target: float) -> float:
    upper = _aligned_family_support(best, midi, +1)
    lower = _aligned_family_support(best, midi, -1)
    fund = _h(row, "meanFundAttack")
    harmonic = _h(row, "meanHarmonicMean")
    local = _h(row, "meanLocalPeakMargin")
    lower_oct = _h(row, "meanLowerOctave")
    lower_19 = _h(row, "meanLowerNineteenth")
    sub_penalty = max(lower_oct, lower_19)
    return (
        0.25 * float(row.get("_support") or 0.0)
        + 0.70 * upper
        - 0.75 * lower
        + 0.16 * fund
        + 0.18 * harmonic
        + 0.10 * local
        - 0.12 * sub_penalty
    )


def _score_ownership_time(midi: int, row: dict[str, Any], best: dict[int, dict[str, Any]], target: float) -> float:
    residual = abs(float(row["onsetTime"]) - float(target))
    time_score = math.exp(-0.5 * (residual / 0.055) ** 2)
    return _score_spectral_ownership(midi, row, best, target) + 0.30 * time_score


RANKERS: dict[str, Callable[[int, dict[str, Any], dict[int, dict[str, Any]], float], float]] = {
    "lowestMidi": _score_lowest,
    "upperFamily": _score_upper_family,
    "aliasSuppressed": _score_alias_suppressed,
    "spectralOwnership": _score_spectral_ownership,
    "ownershipTime": _score_ownership_time,
}


def _rank_midis(
    rows: list[dict[str, Any]],
    target_time: float,
    scorer: Callable[[int, dict[str, Any], dict[int, dict[str, Any]], float], float],
) -> list[int]:
    best = _best_per_midi(rows, target_time)
    scored: list[tuple[float, int, dict[str, Any]]] = []
    for midi, row in best.items():
        score = float(scorer(midi, row, best, target_time))
        scored.append((score, midi, row))
    scored.sort(
        key=lambda item: (
            -item[0],
            float(item[2]["_residual"]),
            -int(item[2].get("stemSupport") or 0),
            -int(item[2].get("sweepSupport") or 0),
            int(item[1]),
        )
    )
    return [int(midi) for _score, midi, _row in scored]


def _evaluate(
    clusters: list[dict[str, Any]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    window_ms: int,
    scorer: Callable[[int, dict[str, Any], dict[int, dict[str, Any]], float], float],
) -> dict[str, Any]:
    by_measure = _clusters_by_measure(clusters)
    window = float(window_ms) / 1000.0
    total = available = top1 = top3 = top5 = 0
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
        rank_lookup = {midi: i + 1 for i, midi in enumerate(ranking)}
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
    ordered = sorted(ranks)
    p90 = ordered[min(len(ordered) - 1, math.ceil(0.90 * len(ordered)) - 1)] if ordered else None
    return {
        "referencePitchEventCount": total,
        "availabilityRecallPercent": pct(available),
        "top1RecallPercent": pct(top1),
        "top3RecallPercent": pct(top3),
        "top5RecallPercent": pct(top5),
        "medianCorrectPitchRankWhenAvailable": round(float(median(ranks)), 3) if ranks else None,
        "p90CorrectPitchRankWhenAvailable": int(p90) if p90 is not None else None,
        "medianCandidatePitchCountPerReferenceLocation": round(float(median(candidate_counts)), 3) if candidate_counts else 0.0,
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

    print("=== V143 HARMONIC-FAMILY PITCH OWNERSHIP DIAGNOSTIC ===")
    print("joinedClusterCount:", len(clusters))
    print("Purpose: test whether false pitches are harmonic aliases of lower candidate fundamentals")
    print("Professional reference used by analyzer: False")
    print("Production modified: False")

    report: dict[str, Any] = {
        "reportVersion": 1,
        "scope": "offline-reference-location-harmonic-family-pitch-ownership",
        "windows": {},
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineDiagnostic": True,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }

    for window_ms in WINDOWS_MS:
        result = {"development": {}, "holdout": {}}
        print()
        print(f"=== WINDOW {window_ms}ms ===")
        print("ranker              devTop1 devTop3 holdTop1 holdTop3 holdAvail medianHoldRank")
        for name, scorer in RANKERS.items():
            dev = _evaluate(clusters, grid, dev_reference, window_ms, scorer)
            hold = _evaluate(clusters, grid, hold_reference, window_ms, scorer)
            result["development"][name] = dev
            result["holdout"][name] = hold
            print(
                f"{name:<19} "
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
                -row["medianCorrectPitchRankWhenAvailable"],
            ) > (
                best_hold["top1RecallPercent"],
                best_hold["top3RecallPercent"],
                best_hold["top5RecallPercent"],
                -best_hold["medianCorrectPitchRankWhenAvailable"],
            ):
                best_hold = row

    report["bestHoldoutDiagnostic"] = best_hold
    if best_hold is None:
        diagnosis = "no-harmonic-family-result"
    elif float(best_hold["top1RecallPercent"]) >= 40.0:
        diagnosis = "harmonic-family-ownership-is-strong-enough-to-build-structured-pitch-decoder"
    elif float(best_hold["top3RecallPercent"]) >= 55.0:
        diagnosis = "harmonic-family-ownership-narrows-candidates-needs-learned-set-decoder"
    else:
        diagnosis = "candidate-ranking-is-the-wrong-abstraction-capture-onset-level-spectrum-for-joint-set-decomposition"
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
