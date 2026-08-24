from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
RETIRED_EVENT_SHA256 = "a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb"
ATTACK_COUNT = 725
MEASURE_COUNT = 113
STEPS_PER_MEASURE = 16


def _quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    weight = position - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def _summary(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "min": min(values) if values else None,
        "q10": _quantile(values, 0.10),
        "q25": _quantile(values, 0.25),
        "median": statistics.median(values) if values else None,
        "mean": statistics.mean(values) if values else None,
        "q75": _quantile(values, 0.75),
        "q90": _quantile(values, 0.90),
        "max": max(values) if values else None,
    }


def _linear_fit(points: list[tuple[float, float]]) -> tuple[float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    mx = statistics.mean(xs)
    my = statistics.mean(ys)
    denominator = sum((x - mx) ** 2 for x in xs)
    if denominator <= 0.0:
        raise RuntimeError("degenerate grid coordinates")
    slope = sum((x - mx) * (y - my) for x, y in points) / denominator
    intercept = my - slope * mx
    return slope, intercept


def _correlation(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mx = statistics.mean(xs)
    my = statistics.mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denominator = math.sqrt(sum(v * v for v in dx) * sum(v * v for v in dy))
    if denominator == 0.0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / denominator


def _load_points(evidence: dict[str, Any]) -> tuple[list[dict[str, Any]], float]:
    provenance = evidence.get("provenance") or {}
    if provenance.get("sourceAudioSha256") != APPROVED_AUDIO_SHA256:
        raise RuntimeError("approved frozen source audio changed")
    if provenance.get("retiredFrozenEventSha256") != RETIRED_EVENT_SHA256:
        raise RuntimeError("frozen source identity changed")
    if provenance.get("referenceFree") is not True:
        raise RuntimeError("frozen evidence is not reference-free")
    if provenance.get("professionalReferenceUsed") is not False:
        raise RuntimeError("professional reference provenance is unsafe")
    if provenance.get("referenceRuntimeInputUsed") is not False:
        raise RuntimeError("reference entered runtime evidence")
    if provenance.get("preScorer") is not True:
        raise RuntimeError("evidence is not sealed pre-scorer evidence")

    attacks = list(evidence.get("attacks") or [])
    tempo = float(evidence.get("tempoBpm") or 0.0)
    if len(attacks) != ATTACK_COUNT or tempo <= 0.0:
        raise RuntimeError("frozen attack cardinality/tempo changed")

    rows: list[dict[str, Any]] = []
    seen: set[int] = set()
    for index, attack in enumerate(attacks):
        measure = int(attack[0])
        step = int(attack[1])
        time_seconds = float(attack[2])
        global_step = (measure - 1) * STEPS_PER_MEASURE + step
        if not (1 <= measure <= MEASURE_COUNT and 0 <= step < STEPS_PER_MEASURE):
            raise RuntimeError(f"invalid grid coordinate at attack {index}")
        if global_step in seen:
            raise RuntimeError(f"duplicate frozen grid step {global_step}")
        if not math.isfinite(time_seconds):
            raise RuntimeError(f"non-finite attack time at attack {index}")
        seen.add(global_step)
        rows.append({
            "measure": measure,
            "step": step,
            "globalStep": global_step,
            "timeSeconds": time_seconds,
        })
    rows.sort(key=lambda row: int(row["globalStep"]))
    return rows, tempo


def _window_rows(rows: list[dict[str, Any]], start: int, end: int) -> list[dict[str, Any]]:
    return [row for row in rows if start <= int(row["measure"]) <= end]


def diagnose(evidence: dict[str, Any]) -> dict[str, Any]:
    rows, tempo = _load_points(evidence)
    points = [(float(row["globalStep"]), float(row["timeSeconds"])) for row in rows]
    nominal_step_seconds = 60.0 / tempo / 4.0
    fit_slope, fit_intercept = _linear_fit(points)
    fitted_tempo = 60.0 / (4.0 * fit_slope)
    nominal_intercept = statistics.median(
        float(row["timeSeconds"]) - nominal_step_seconds * float(row["globalStep"])
        for row in rows
    )

    nominal_residual_seconds = [
        float(row["timeSeconds"]) - (nominal_intercept + nominal_step_seconds * float(row["globalStep"]))
        for row in rows
    ]
    nominal_residual_steps = [value / nominal_step_seconds for value in nominal_residual_seconds]
    fitted_residual_seconds = [
        float(row["timeSeconds"]) - (fit_intercept + fit_slope * float(row["globalStep"]))
        for row in rows
    ]
    fitted_residual_steps = [value / fit_slope for value in fitted_residual_seconds]

    local_step_seconds: list[float] = []
    local_pairs: list[dict[str, Any]] = []
    for left, right in zip(rows, rows[1:]):
        delta_step = int(right["globalStep"]) - int(left["globalStep"])
        if delta_step <= 0 or delta_step > 8:
            continue
        delta_time = float(right["timeSeconds"]) - float(left["timeSeconds"])
        per_step = delta_time / delta_step
        if per_step <= 0.0:
            continue
        local_step_seconds.append(per_step)
        local_pairs.append({
            "leftGlobalStep": int(left["globalStep"]),
            "rightGlobalStep": int(right["globalStep"]),
            "gridStepGap": delta_step,
            "secondsPerGridStep": per_step,
            "impliedBpm": 60.0 / (4.0 * per_step),
        })

    windows = []
    for start in range(1, 113, 8):
        end = start + 7
        scoped = _window_rows(rows, start, end)
        if not scoped:
            continue
        residuals = [
            (float(row["timeSeconds"]) - (nominal_intercept + nominal_step_seconds * float(row["globalStep"]))) / nominal_step_seconds
            for row in scoped
        ]
        scoped_points = [(float(row["globalStep"]), float(row["timeSeconds"])) for row in scoped]
        window_slope = None
        window_bpm = None
        if len(scoped_points) >= 2:
            window_slope, _ = _linear_fit(scoped_points)
            if window_slope > 0.0:
                window_bpm = 60.0 / (4.0 * window_slope)
        windows.append({
            "startMeasure": start,
            "endMeasure": end,
            "attackCount": len(scoped),
            "medianNominalResidualSixteenthSteps": statistics.median(residuals),
            "meanNominalResidualSixteenthSteps": statistics.mean(residuals),
            "windowLinearFitSecondsPerSixteenthStep": window_slope,
            "windowLinearFitBpm": window_bpm,
        })

    centers = [(float(item["startMeasure"]) + float(item["endMeasure"])) / 2.0 for item in windows]
    medians = [float(item["medianNominalResidualSixteenthSteps"]) for item in windows]
    residual_trend_correlation = _correlation(centers, medians)
    fitted_tempo_percent_delta = (fitted_tempo - tempo) / tempo * 100.0
    nominal_span_steps = max(nominal_residual_steps) - min(nominal_residual_steps)
    fitted_span_steps = max(fitted_residual_steps) - min(fitted_residual_steps)

    return {
        "schemaVersion": 1,
        "mode": "v143-frozen-evidence-grid-timestamp-diagnostic",
        "sourceAudioSha256": APPROVED_AUDIO_SHA256,
        "sourceRetiredEventSha256": RETIRED_EVENT_SHA256,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "modalUsed": False,
        "productionModified": False,
        "protectedRuntimeModified": False,
        "candidateRenderProduced": False,
        "eventMutationProposed": False,
        "attackCount": len(rows),
        "tempoMetadataBpm": tempo,
        "nominalSecondsPerSixteenthStep": nominal_step_seconds,
        "globalLinearFit": {
            "secondsPerSixteenthStep": fit_slope,
            "interceptSeconds": fit_intercept,
            "impliedBpm": fitted_tempo,
            "impliedBpmMinusMetadataPercent": fitted_tempo_percent_delta,
        },
        "nominalTempoResidual": {
            "interceptMedianFitSeconds": nominal_intercept,
            "residualSeconds": _summary(nominal_residual_seconds),
            "residualSixteenthSteps": _summary(nominal_residual_steps),
            "spanSixteenthSteps": nominal_span_steps,
        },
        "bestLinearFitResidual": {
            "residualSeconds": _summary(fitted_residual_seconds),
            "residualSixteenthSteps": _summary(fitted_residual_steps),
            "spanSixteenthSteps": fitted_span_steps,
        },
        "adjacentSelectedAttackLocalGrid": {
            "definition": "adjacent selected attacks separated by 1..8 labeled sixteenth steps",
            "pairCount": len(local_pairs),
            "secondsPerGridStep": _summary(local_step_seconds),
            "impliedBpm": _summary([float(item["impliedBpm"]) for item in local_pairs]),
        },
        "eightMeasureWindows": windows,
        "windowMedianNominalResidualTrendCorrelation": residual_trend_correlation,
        "diagnosticFlags": {
            "metadataTempoDiffersFromGlobalTimestampFitByMoreThanHalfPercent": abs(fitted_tempo_percent_delta) > 0.5,
            "nominalTempoResidualSpanExceedsOneSixteenthStep": nominal_span_steps > 1.0,
            "bestLinearFitResidualSpanExceedsOneSixteenthStep": fitted_span_steps > 1.0,
            "strongMonotonicNominalResidualTrendAcrossEightMeasureWindows": residual_trend_correlation is not None and abs(residual_trend_correlation) >= 0.8,
        },
        "interpretationBoundary": "this tests internal consistency of frozen timestamp/grid labels only; it does not assume the song is constant-tempo and does not select or mutate a grid",
        "invariants": {
            "all725AttacksRead": len(rows) == ATTACK_COUNT,
            "eventsMutated": False,
            "attackGridMutated": False,
            "pitchSelectionMutated": False,
            "referenceConsulted": False,
            "tempoOrOriginSelected": False,
        },
    }


def main(source: str, destination: str) -> None:
    evidence = json.loads(Path(source).read_text(encoding="utf-8"))
    report = diagnose(evidence)
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "tempoMetadataBpm": report["tempoMetadataBpm"],
        "globalLinearFit": report["globalLinearFit"],
        "nominalTempoResidual": report["nominalTempoResidual"],
        "bestLinearFitResidual": report["bestLinearFitResidual"],
        "windowTrendCorrelation": report["windowMedianNominalResidualTrendCorrelation"],
        "flags": report["diagnosticFlags"],
    }, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_frozen_evidence_grid_timestamp_diagnostic.py EVIDENCE OUTPUT")
    main(sys.argv[1], sys.argv[2])
