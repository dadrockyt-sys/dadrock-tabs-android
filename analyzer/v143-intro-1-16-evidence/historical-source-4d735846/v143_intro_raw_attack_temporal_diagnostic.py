from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-raw-attack-cache.json"
)
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-raw-attack-temporal-diagnostic.json"
)

DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))
CLUSTER_TOLERANCE_SECONDS = 0.030
WINDOWS_MS = (25, 50, 75, 100, 125, 150, 200, 250, 300)


def _percent(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 3) if denominator else 100.0


def _quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * float(q)
    lo = int(position)
    hi = min(lo + 1, len(ordered) - 1)
    fraction = position - lo
    return ordered[lo] * (1.0 - fraction) + ordered[hi] * fraction


def _reference_events(reference: dict[str, Any], measures: set[int]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for measure in reference.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        measure_number = int(measure.get("measureNumber") or 0)
        if measure_number not in measures:
            continue
        for event_index, raw in enumerate(measure.get("events", []) or []):
            if not isinstance(raw, dict):
                continue
            midi = raw.get("midiPitch")
            step = raw.get("step")
            if midi is None or step is None:
                continue
            events.append(
                {
                    "referenceId": len(events),
                    "measure": measure_number,
                    "step": int(step),
                    "midi": int(round(float(midi))),
                    "eventIndex": int(event_index),
                }
            )
    return events


def _grid_lookup(cache: dict[str, Any]) -> dict[tuple[int, int], float]:
    lookup: dict[tuple[int, int], float] = {}
    for row in cache.get("grid", []) or []:
        if not isinstance(row, dict):
            continue
        key = (int(row.get("measure") or 0), int(row.get("step") or 0))
        lookup[key] = float(row.get("timeSeconds"))
    return lookup


def _cluster_events(cache: dict[str, Any]) -> list[dict[str, Any]]:
    """Collapse duplicate sweep/view detections into physical attack clusters.

    Clustering is reference-free: same MIDI, same measure, and onset proximity only.
    A cluster can then advertise independent stem and threshold-sweep support without
    letting duplicated Basic Pitch detections inflate collision-aware recall.
    """
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for raw in cache.get("events", []) or []:
        if not isinstance(raw, dict):
            continue
        measure = int(raw.get("nearestMeasure") or 0)
        midi = int(raw.get("midi") or 0)
        grouped[(measure, midi)].append(dict(raw))

    clusters: list[dict[str, Any]] = []
    cluster_id = 0
    for (measure, midi), events in sorted(grouped.items()):
        events.sort(key=lambda row: (float(row["onsetTime"]), int(row.get("eventId") or 0)))
        current: list[dict[str, Any]] = []
        center = 0.0

        def flush(rows: list[dict[str, Any]]) -> None:
            nonlocal cluster_id
            if not rows:
                return
            cluster_id += 1
            onsets = [float(row["onsetTime"]) for row in rows]
            amplitudes = [float(row.get("amplitude") or 0.0) for row in rows]
            stems = sorted({int(row.get("stemIndex") or 0) for row in rows})
            sweeps = sorted({str(row.get("sweepName") or "") for row in rows})
            clusters.append(
                {
                    "clusterId": cluster_id,
                    "measure": int(measure),
                    "midi": int(midi),
                    "onsetTime": float(median(onsets)),
                    "minOnsetTime": min(onsets),
                    "maxOnsetTime": max(onsets),
                    "detectionCount": len(rows),
                    "stemSupport": len(stems),
                    "sweepSupport": len(sweeps),
                    "stems": stems,
                    "sweeps": sweeps,
                    "maxAmplitude": max(amplitudes) if amplitudes else 0.0,
                    "meanAmplitude": sum(amplitudes) / len(amplitudes) if amplitudes else 0.0,
                    "productionAccepted": any(bool(row.get("withinProductionGridTolerance")) for row in rows),
                }
            )

        for event in events:
            onset = float(event["onsetTime"])
            if not current:
                current = [event]
                center = onset
                continue
            if abs(onset - center) <= CLUSTER_TOLERANCE_SECONDS:
                current.append(event)
                center = float(median([float(row["onsetTime"]) for row in current]))
            else:
                flush(current)
                current = [event]
                center = onset
        flush(current)

    return clusters


def _maximum_matching(
    refs: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
    grid: dict[tuple[int, int], float],
    window_seconds: float,
    predicate,
) -> tuple[int, list[float]]:
    """Maximum one-to-one same-pitch matching with onset-window edges."""
    cluster_index = {int(cluster["clusterId"]): cluster for cluster in clusters}
    adjacency: dict[int, list[tuple[int, float]]] = {}
    eligible_refs: list[dict[str, Any]] = []

    for ref in refs:
        target_time = grid.get((int(ref["measure"]), int(ref["step"])))
        if target_time is None:
            continue
        edges: list[tuple[int, float]] = []
        for cluster in clusters:
            if int(cluster["measure"]) != int(ref["measure"]):
                continue
            if int(cluster["midi"]) != int(ref["midi"]):
                continue
            if not predicate(cluster):
                continue
            delta = float(cluster["onsetTime"]) - float(target_time)
            if abs(delta) <= window_seconds:
                edges.append((int(cluster["clusterId"]), delta))
        edges.sort(key=lambda item: (abs(item[1]), item[0]))
        adjacency[int(ref["referenceId"])] = edges
        eligible_refs.append(ref)

    match_cluster_to_ref: dict[int, int] = {}
    chosen_delta: dict[tuple[int, int], float] = {}

    def visit(ref_id: int, seen: set[int]) -> bool:
        for cluster_id, delta in adjacency.get(ref_id, []):
            if cluster_id in seen:
                continue
            seen.add(cluster_id)
            previous_ref = match_cluster_to_ref.get(cluster_id)
            if previous_ref is None or visit(previous_ref, seen):
                match_cluster_to_ref[cluster_id] = ref_id
                chosen_delta[(ref_id, cluster_id)] = delta
                return True
        return False

    for ref in eligible_refs:
        visit(int(ref["referenceId"]), set())

    residuals: list[float] = []
    for cluster_id, ref_id in match_cluster_to_ref.items():
        cluster = cluster_index[cluster_id]
        target_ref = next(ref for ref in eligible_refs if int(ref["referenceId"]) == ref_id)
        target_time = grid[(int(target_ref["measure"]), int(target_ref["step"]))]
        residuals.append(float(cluster["onsetTime"]) - float(target_time))
    return len(match_cluster_to_ref), residuals


def _diagnose_scope(
    name: str,
    refs: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
    grid: dict[tuple[int, int], float],
) -> dict[str, Any]:
    predicates = {
        "anyCluster": lambda cluster: True,
        "productionAccepted": lambda cluster: bool(cluster["productionAccepted"]),
        "dualView": lambda cluster: int(cluster["stemSupport"]) >= 2,
        "multiSweep": lambda cluster: int(cluster["sweepSupport"]) >= 2,
        "strictConsensus": lambda cluster: int(cluster["stemSupport"]) >= 2 and int(cluster["sweepSupport"]) >= 2,
    }

    windows: dict[str, Any] = {}
    for window_ms in WINDOWS_MS:
        window_seconds = window_ms / 1000.0
        row: dict[str, Any] = {"windowMs": window_ms}
        for predicate_name, predicate in predicates.items():
            matches, residuals = _maximum_matching(
                refs,
                clusters,
                grid,
                window_seconds,
                predicate,
            )
            row[predicate_name] = {
                "matches": matches,
                "recallPercent": _percent(matches, len(refs)),
                "medianSignedResidualMs": round(1000.0 * median(residuals), 3) if residuals else None,
            }
        windows[str(window_ms)] = row

    # Nearest same-pitch physical attack with a generous 500 ms guard. This is
    # diagnostic only and reveals the continuous onset-error distribution.
    nearest_residuals: list[float] = []
    nearest_abs_residuals: list[float] = []
    missing = 0
    for ref in refs:
        target_time = grid.get((int(ref["measure"]), int(ref["step"])))
        if target_time is None:
            missing += 1
            continue
        candidates = [
            cluster
            for cluster in clusters
            if int(cluster["measure"]) == int(ref["measure"])
            and int(cluster["midi"]) == int(ref["midi"])
            and abs(float(cluster["onsetTime"]) - float(target_time)) <= 0.5
        ]
        if not candidates:
            missing += 1
            continue
        best = min(
            candidates,
            key=lambda cluster: (
                abs(float(cluster["onsetTime"]) - float(target_time)),
                -int(cluster["stemSupport"]),
                -int(cluster["sweepSupport"]),
                int(cluster["clusterId"]),
            ),
        )
        residual = float(best["onsetTime"]) - float(target_time)
        nearest_residuals.append(residual)
        nearest_abs_residuals.append(abs(residual))

    residual_summary = {
        "matchedReferenceEvents": len(nearest_residuals),
        "missingReferenceEvents": missing,
        "medianSignedResidualMs": round(1000.0 * median(nearest_residuals), 3) if nearest_residuals else None,
        "medianAbsoluteResidualMs": round(1000.0 * median(nearest_abs_residuals), 3) if nearest_abs_residuals else None,
        "p75AbsoluteResidualMs": round(1000.0 * float(_quantile(nearest_abs_residuals, 0.75)), 3) if nearest_abs_residuals else None,
        "p90AbsoluteResidualMs": round(1000.0 * float(_quantile(nearest_abs_residuals, 0.90)), 3) if nearest_abs_residuals else None,
        "p95AbsoluteResidualMs": round(1000.0 * float(_quantile(nearest_abs_residuals, 0.95)), 3) if nearest_abs_residuals else None,
    }

    return {
        "scope": name,
        "referenceEventCount": len(refs),
        "windows": windows,
        "nearestSamePitchResiduals": residual_summary,
    }


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Missing raw attack cache: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())
    grid = _grid_lookup(cache)
    clusters = _cluster_events(cache)
    dev_refs = _reference_events(reference, DEVELOPMENT_MEASURES)
    hold_refs = _reference_events(reference, HOLDOUT_MEASURES)

    dev = _diagnose_scope("development-measures-1-12", dev_refs, clusters, grid)
    hold = _diagnose_scope("holdout-measures-13-16", hold_refs, clusters, grid)

    report = {
        "diagnosticVersion": 1,
        "scope": "raw-unaggregated-attack-temporal-availability",
        "clusterToleranceMs": int(round(CLUSTER_TOLERANCE_SECONDS * 1000.0)),
        "rawEventCount": int(cache.get("rawEventCount") or 0),
        "physicalAttackClusterCount": len(clusters),
        "development": dev,
        "holdout": hold,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineDiagnostic": True,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("=== V143 RAW ATTACK TEMPORAL DIAGNOSTIC ===")
    print("rawEventCount:", report["rawEventCount"])
    print("physicalAttackClusterCount:", report["physicalAttackClusterCount"])
    print("clusterToleranceMs:", report["clusterToleranceMs"])

    for label, section in (("DEVELOPMENT 1-12", dev), ("HOLDOUT 13-16", hold)):
        print()
        print(f"=== {label} ===")
        print("referenceEventCount:", section["referenceEventCount"])
        print("window  anyRecall  dualView  multiSweep  strictConsensus")
        for window_ms in WINDOWS_MS:
            row = section["windows"][str(window_ms)]
            print(
                f"{window_ms:>4}ms  "
                f"{row['anyCluster']['recallPercent']:>7.3f}%  "
                f"{row['dualView']['recallPercent']:>7.3f}%  "
                f"{row['multiSweep']['recallPercent']:>7.3f}%  "
                f"{row['strictConsensus']['recallPercent']:>7.3f}%"
            )
        print("nearestSamePitchResiduals:")
        print(json.dumps(section["nearestSamePitchResiduals"], indent=2))

    hold_100 = hold["windows"]["100"]["anyCluster"]["recallPercent"]
    hold_200 = hold["windows"]["200"]["anyCluster"]["recallPercent"]
    hold_strict_150 = hold["windows"]["150"]["strictConsensus"]["recallPercent"]
    if hold_100 >= 80.0:
        diagnosis = "continuous-raw-onset-evidence-is-strong-within-production-scale-window"
    elif hold_200 >= 85.0:
        diagnosis = "correct-pitches-exist-but-basic-pitch-onsets-are-materially-displaced"
    elif hold_strict_150 >= 70.0:
        diagnosis = "cross-view-consensus-is-more-informative-than-single-event-timing"
    else:
        diagnosis = "raw-basic-pitch-attacks-remain-insufficient-for-direct-temporal-reconstruction"

    report["diagnosis"] = diagnosis
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    print()
    print("DIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
