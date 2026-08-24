from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Iterable

APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
RETIRED_EVENT_SHA256 = "a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb"
ATTACK_COUNT = 725
MEASURE_COUNT = 113
STEPS_PER_MEASURE = 16
PHASE_OFFSETS = (0, 4, 8, 12)
EPSILON = 1e-12


def _quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
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
        "q25": _quantile(values, 0.25),
        "median": statistics.median(values) if values else None,
        "mean": statistics.mean(values) if values else None,
        "q75": _quantile(values, 0.75),
        "max": max(values) if values else None,
    }


def _hypothesis_map(attack: list[Any]) -> dict[int, list[Any]]:
    return {int(item[0]): item for item in attack[4]}


def _validate_and_build_support(evidence: dict[str, Any]) -> tuple[dict[tuple[int, int], float], float]:
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

    support: dict[tuple[int, int], float] = {}
    for index, attack in enumerate(attacks):
        measure = int(attack[0])
        step = int(attack[1])
        primary = int(attack[3])
        if measure < 1 or measure > MEASURE_COUNT or step < 0 or step >= STEPS_PER_MEASURE:
            raise RuntimeError(f"invalid frozen grid coordinate at attack {index}")
        key = (measure, step)
        if key in support:
            raise RuntimeError(f"duplicate frozen attack coordinate {key}")
        hypotheses = _hypothesis_map(attack)
        if primary not in hypotheses:
            raise RuntimeError(f"primary missing from hypotheses at attack {index}")
        primary_attack_support = float(hypotheses[primary][1])
        if not math.isfinite(primary_attack_support) or primary_attack_support < 0.0:
            raise RuntimeError(f"invalid primary attack support at attack {index}")
        support[key] = primary_attack_support

    return support, tempo


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _phase_metrics(
    support: dict[tuple[int, int], float], measures: Iterable[int], offset: int
) -> dict[str, Any]:
    measure_list = list(measures)
    if not measure_list:
        raise RuntimeError("empty phase-analysis measure scope")
    beat_steps = tuple((offset + delta) % STEPS_PER_MEASURE for delta in (0, 4, 8, 12))
    downbeat_step = beat_steps[0]
    other_steps = beat_steps[1:]

    downbeat_zero = [support.get((measure, downbeat_step), 0.0) for measure in measure_list]
    other_zero = [
        support.get((measure, step), 0.0)
        for measure in measure_list
        for step in other_steps
    ]
    downbeat_occupied = [
        support[(measure, downbeat_step)]
        for measure in measure_list
        if (measure, downbeat_step) in support
    ]
    other_occupied = [
        support[(measure, step)]
        for measure in measure_list
        for step in other_steps
        if (measure, step) in support
    ]

    zero_downbeat_mean = _mean(downbeat_zero)
    zero_other_mean = _mean(other_zero)
    occupied_downbeat_mean = statistics.mean(downbeat_occupied) if downbeat_occupied else None
    occupied_other_mean = statistics.mean(other_occupied) if other_occupied else None
    occupied_contrast = None
    if occupied_downbeat_mean is not None and occupied_other_mean is not None:
        occupied_contrast = occupied_downbeat_mean - occupied_other_mean

    return {
        "offsetSixteenthStepsFromCurrent": offset,
        "measureCount": len(measure_list),
        "beatStepsModuloCurrentMeasure": list(beat_steps),
        "zeroFilled": {
            "downbeatMean": zero_downbeat_mean,
            "otherWholeBeatMean": zero_other_mean,
            "downbeatContrastVsOtherBeats": zero_downbeat_mean - zero_other_mean,
        },
        "occupancy": {
            "downbeatCount": len(downbeat_occupied),
            "downbeatRate": len(downbeat_occupied) / len(measure_list),
            "otherWholeBeatCount": len(other_occupied),
            "otherWholeBeatRate": len(other_occupied) / (3 * len(measure_list)),
        },
        "occupiedOnly": {
            "downbeatMean": occupied_downbeat_mean,
            "otherWholeBeatMean": occupied_other_mean,
            "downbeatContrastVsOtherBeats": occupied_contrast,
        },
    }


def _paired_eight_vs_zero(
    support: dict[tuple[int, int], float], measures: Iterable[int]
) -> dict[str, Any]:
    measure_list = list(measures)
    diffs = [
        support.get((measure, 8), 0.0) - support.get((measure, 0), 0.0)
        for measure in measure_list
    ]
    wins = sum(value > EPSILON for value in diffs)
    losses = sum(value < -EPSILON for value in diffs)
    ties = len(diffs) - wins - losses
    non_ties = wins + losses
    occupied_both = sum((measure, 8) in support and (measure, 0) in support for measure in measure_list)
    return {
        "definition": "paired within-current-measure zero-filled primary attack support at step 8 minus step 0",
        "supportDifferenceEightMinusZero": _summary(diffs),
        "phase8Wins": wins,
        "phase0Wins": losses,
        "ties": ties,
        "phase8WinFractionAllMeasures": wins / len(diffs) if diffs else None,
        "phase8WinFractionNonTies": wins / non_ties if non_ties else None,
        "bothPositionsOccupiedCount": occupied_both,
    }


def _scope_metrics(
    support: dict[tuple[int, int], float], start_measure: int, end_measure: int
) -> dict[str, Any]:
    measures = list(range(start_measure, end_measure + 1))
    phases = [_phase_metrics(support, measures, offset) for offset in PHASE_OFFSETS]
    zero_ranking = sorted(
        (
            (
                float(item["zeroFilled"]["downbeatContrastVsOtherBeats"]),
                int(item["offsetSixteenthStepsFromCurrent"]),
            )
            for item in phases
        ),
        reverse=True,
    )
    occupied_valid = [
        (
            float(item["occupiedOnly"]["downbeatContrastVsOtherBeats"]),
            int(item["offsetSixteenthStepsFromCurrent"]),
        )
        for item in phases
        if item["occupiedOnly"]["downbeatContrastVsOtherBeats"] is not None
    ]
    occupied_ranking = sorted(occupied_valid, reverse=True)
    phase_by_offset = {int(item["offsetSixteenthStepsFromCurrent"]): item for item in phases}
    zero_diff = (
        float(phase_by_offset[8]["zeroFilled"]["downbeatContrastVsOtherBeats"])
        - float(phase_by_offset[0]["zeroFilled"]["downbeatContrastVsOtherBeats"])
    )
    return {
        "startMeasure": start_measure,
        "endMeasure": end_measure,
        "measureCount": len(measures),
        "phases": phases,
        "zeroFilledContrastWinnerOffset": zero_ranking[0][1],
        "zeroFilledContrastRanking": [offset for _, offset in zero_ranking],
        "occupiedOnlyContrastWinnerOffset": occupied_ranking[0][1] if occupied_ranking else None,
        "zeroFilledContrastDifferenceEightMinusZero": zero_diff,
        "pairedEightVsZero": _paired_eight_vs_zero(support, measures),
    }


def _window_series(
    support: dict[tuple[int, int], float], width: int, stride: int, final_measure: int = 112
) -> list[dict[str, Any]]:
    windows: list[dict[str, Any]] = []
    start = 1
    while start + width - 1 <= final_measure:
        windows.append(_scope_metrics(support, start, start + width - 1))
        start += stride
    return windows


def _window_vote_summary(windows: list[dict[str, Any]]) -> dict[str, Any]:
    diffs = [float(item["zeroFilledContrastDifferenceEightMinusZero"]) for item in windows]
    wins = sum(value > EPSILON for value in diffs)
    losses = sum(value < -EPSILON for value in diffs)
    ties = len(diffs) - wins - losses
    winners = [int(item["zeroFilledContrastWinnerOffset"]) for item in windows]
    return {
        "windowCount": len(windows),
        "phase8Vs0ContrastDifference": _summary(diffs),
        "phase8WinsVs0": wins,
        "phase0WinsVs8": losses,
        "ties": ties,
        "phase8WinFractionVs0": wins / len(windows) if windows else None,
        "phase8OverallPhaseWinnerCount": sum(offset == 8 for offset in winners),
        "overallPhaseWinnerOffsets": winners,
    }


def diagnose(evidence: dict[str, Any]) -> dict[str, Any]:
    support, tempo = _validate_and_build_support(evidence)
    global_scope = _scope_metrics(support, 1, MEASURE_COUNT)
    windows8 = _window_series(support, width=8, stride=8)
    windows16 = _window_series(support, width=16, stride=8)
    vote8 = _window_vote_summary(windows8)
    vote16 = _window_vote_summary(windows16)

    global_diff = float(global_scope["zeroFilledContrastDifferenceEightMinusZero"])
    stable_phase8 = (
        global_diff > 0.0
        and float(vote8["phase8WinFractionVs0"] or 0.0) >= 0.75
        and float(vote16["phase8WinFractionVs0"] or 0.0) >= 0.75
        and float(vote8["phase8Vs0ContrastDifference"]["median"] or 0.0) > 0.0
        and float(vote16["phase8Vs0ContrastDifference"]["median"] or 0.0) > 0.0
    )
    mixed_sign = (
        int(vote8["phase8WinsVs0"]) > 0
        and int(vote8["phase0WinsVs8"]) > 0
    )
    interpretation = (
        "stable-phase8-physical-accent-clue"
        if stable_phase8
        else "sectional-or-mixed-phase-accent-clue"
        if global_diff > 0.0 and mixed_sign
        else "no-stable-phase8-physical-accent-clue"
    )

    return {
        "schemaVersion": 1,
        "mode": "v143-frozen-evidence-phase-stability-diagnostic",
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
        "attackCount": len(support),
        "tempoBpm": tempo,
        "method": {
            "purpose": "test whether the apparent half-bar attack-accent preference survives edge-safe, occupancy-aware local analysis",
            "edgeSafety": "all phase offsets are compared on the identical current-measure set; beat positions rotate modulo 16, so no leading/trailing attacks are discarded by phase",
            "occupancyHandling": "missing attacks at a tested beat position contribute zero support; occupied-only means are reported separately",
            "localStability": "non-overlapping 8-measure windows plus 16-measure windows with 8-measure stride; both stop at measure 112 so the single final measure cannot dominate a window vote",
            "phaseSelectionPerformed": False,
        },
        "globalMeasures1To113": global_scope,
        "windows8MeasuresNonOverlapping": windows8,
        "windows16MeasuresStride8": windows16,
        "windowVoteSummary": {
            "eightMeasure": vote8,
            "sixteenMeasure": vote16,
        },
        "diagnosticInterpretation": interpretation,
        "stablePhase8PhysicalAccentClue": stable_phase8,
        "invariants": {
            "all725AttacksRead": len(support) == ATTACK_COUNT,
            "sameMeasureSetForAllPhases": True,
            "phaseEdgeTruncation": False,
            "missingAttackSupportZeroFilled": True,
            "eventsMutated": False,
            "attackGridMutated": False,
            "pitchSelectionMutated": False,
            "referenceConsulted": False,
        },
    }


def main(source: str, destination: str) -> None:
    evidence = json.loads(Path(source).read_text(encoding="utf-8"))
    report = diagnose(evidence)
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    compact = {
        "attackCount": report["attackCount"],
        "globalWinner": report["globalMeasures1To113"]["zeroFilledContrastWinnerOffset"],
        "globalEightMinusZero": report["globalMeasures1To113"]["zeroFilledContrastDifferenceEightMinusZero"],
        "eightMeasureVotes": report["windowVoteSummary"]["eightMeasure"],
        "sixteenMeasureVotes": report["windowVoteSummary"]["sixteenMeasure"],
        "interpretation": report["diagnosticInterpretation"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_frozen_evidence_phase_stability_diagnostic.py EVIDENCE OUTPUT")
    main(sys.argv[1], sys.argv[2])
