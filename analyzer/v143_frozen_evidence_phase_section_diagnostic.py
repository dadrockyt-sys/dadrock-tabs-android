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
HARMONIC_INTERVALS = {12, 19, 24, 28, 31, 36}
EPSILON = 1e-12


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


def _hypothesis_map(attack: list[Any]) -> dict[int, list[Any]]:
    return {int(item[0]): item for item in attack[4]}


def _primary_sustain(attack: list[Any]) -> bool:
    primary = int(attack[3])
    for note in attack[5]:
        if int(note[1]) == primary:
            return bool(note[4])
    return False


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _circular_delta(new: int, old: int) -> int:
    delta = (int(new) - int(old)) % STEPS_PER_MEASURE
    if delta > STEPS_PER_MEASURE // 2:
        delta -= STEPS_PER_MEASURE
    return delta


def _load_rows(evidence: dict[str, Any]) -> tuple[list[dict[str, Any]], float]:
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

    seen: set[tuple[int, int]] = set()
    rows: list[dict[str, Any]] = []
    for index, attack in enumerate(attacks):
        measure = int(attack[0])
        step = int(attack[1])
        time_seconds = float(attack[2])
        primary = int(attack[3])
        key = (measure, step)
        if not (1 <= measure <= MEASURE_COUNT and 0 <= step < STEPS_PER_MEASURE):
            raise RuntimeError(f"invalid grid coordinate at attack {index}")
        if key in seen:
            raise RuntimeError(f"duplicate frozen attack coordinate {key}")
        seen.add(key)
        hypotheses = _hypothesis_map(attack)
        if primary not in hypotheses:
            raise RuntimeError(f"primary missing from hypotheses at attack {index}")
        hyp = hypotheses[primary]
        attack_support = float(hyp[1])
        body_support = float(hyp[2])
        persistence_support = float(hyp[3])
        combined_score = float(hyp[4])
        if not all(math.isfinite(v) for v in (time_seconds, attack_support, body_support, persistence_support, combined_score)):
            raise RuntimeError(f"non-finite frozen evidence at attack {index}")
        primary_score = combined_score
        upper_outscores = any(
            int(midi) - primary in HARMONIC_INTERVALS and float(other[4]) > primary_score
            for midi, other in hypotheses.items()
        )
        rows.append({
            "index": index,
            "measure": measure,
            "step": step,
            "timeSeconds": time_seconds,
            "primaryMidi": primary,
            "attackSupport": attack_support,
            "bodySupport": body_support,
            "frontMinusBody": attack_support - body_support,
            "persistenceSupport": persistence_support,
            "combinedScore": combined_score,
            "primarySustainEvidence": _primary_sustain(attack),
            "upperHarmonicOutscoresPrimary": upper_outscores,
        })
    rows.sort(key=lambda row: float(row["timeSeconds"]))
    return rows, tempo


def _attach_repeat_physics(rows: list[dict[str, Any]], tempo: float) -> dict[str, float]:
    attack_supports = [float(row["attackSupport"]) for row in rows]
    body_supports = [float(row["bodySupport"]) for row in rows]
    front_minus_body = [float(row["frontMinusBody"]) for row in rows]
    attack_q25 = float(_quantile(attack_supports, 0.25) or 0.0)
    body_median = float(statistics.median(body_supports))
    front_body_q25 = float(_quantile(front_minus_body, 0.25) or 0.0)
    step_seconds = 60.0 / tempo / 4.0
    previous_by_midi: dict[int, dict[str, Any]] = {}
    for row in rows:
        row["shortSamePrimaryRepeat"] = False
        row["carryoverQ25Suspect"] = False
        row["strictCarryoverSuspect"] = False
        primary = int(row["primaryMidi"])
        previous = previous_by_midi.get(primary)
        if previous is not None:
            gap_steps = (float(row["timeSeconds"]) - float(previous["timeSeconds"])) / step_seconds
            if 0.0 < gap_steps <= 2.35:
                row["shortSamePrimaryRepeat"] = True
                if bool(previous["primarySustainEvidence"]) and float(row["frontMinusBody"]) <= front_body_q25:
                    row["carryoverQ25Suspect"] = True
                if (
                    bool(previous["primarySustainEvidence"])
                    and float(row["attackSupport"]) <= attack_q25
                    and float(row["bodySupport"]) >= body_median
                    and float(row["frontMinusBody"]) < 0.0
                ):
                    row["strictCarryoverSuspect"] = True
        previous_by_midi[primary] = row
    return {
        "primaryAttackQ25": attack_q25,
        "primaryBodyMedian": body_median,
        "attackMinusBodyQ25": front_body_q25,
        "sixteenthStepSeconds": step_seconds,
    }


def _phase_contrast(rows_by_key: dict[tuple[int, int], dict[str, Any]], measures: list[int], offset: int) -> dict[str, Any]:
    beat_steps = [(offset + delta) % STEPS_PER_MEASURE for delta in (0, 4, 8, 12)]
    downbeat = beat_steps[0]
    others = beat_steps[1:]
    down_values = [float(rows_by_key.get((m, downbeat), {}).get("attackSupport", 0.0)) for m in measures]
    other_values = [
        float(rows_by_key.get((m, step), {}).get("attackSupport", 0.0))
        for m in measures
        for step in others
    ]
    down_count = sum((m, downbeat) in rows_by_key for m in measures)
    other_count = sum((m, step) in rows_by_key for m in measures for step in others)
    down_mean = _mean(down_values)
    other_mean = _mean(other_values)
    return {
        "offset": offset,
        "contrast": down_mean - other_mean,
        "downbeatMeanZeroFilled": down_mean,
        "otherBeatMeanZeroFilled": other_mean,
        "downbeatOccupancyRate": down_count / len(measures),
        "otherBeatOccupancyRate": other_count / (3 * len(measures)),
    }


def _window(rows: list[dict[str, Any]], rows_by_key: dict[tuple[int, int], dict[str, Any]], start: int, end: int) -> dict[str, Any]:
    measures = list(range(start, end + 1))
    scoped = [row for row in rows if start <= int(row["measure"]) <= end]
    phases = [_phase_contrast(rows_by_key, measures, offset) for offset in range(STEPS_PER_MEASURE)]
    ranking = sorted(phases, key=lambda item: (float(item["contrast"]), -int(item["offset"])), reverse=True)
    coarse = [item for item in phases if int(item["offset"]) in (0, 4, 8, 12)]
    coarse_ranking = sorted(coarse, key=lambda item: (float(item["contrast"]), -int(item["offset"])), reverse=True)
    attack_supports = [float(row["attackSupport"]) for row in scoped]
    front_body = [float(row["frontMinusBody"]) for row in scoped]
    attack_count = len(scoped)
    carry_q25 = sum(bool(row["carryoverQ25Suspect"]) for row in scoped)
    strict = sum(bool(row["strictCarryoverSuspect"]) for row in scoped)
    upper_outscore = sum(bool(row["upperHarmonicOutscoresPrimary"]) for row in scoped)
    repeat_count = sum(bool(row["shortSamePrimaryRepeat"]) for row in scoped)
    return {
        "startMeasure": start,
        "endMeasure": end,
        "measureCount": len(measures),
        "finePhaseWinnerOffset": int(ranking[0]["offset"]),
        "finePhaseWinnerContrast": float(ranking[0]["contrast"]),
        "finePhaseRunnerUpOffset": int(ranking[1]["offset"]),
        "finePhaseWinnerMargin": float(ranking[0]["contrast"]) - float(ranking[1]["contrast"]),
        "finePhaseTopFour": [
            {"offset": int(item["offset"]), "contrast": float(item["contrast"])}
            for item in ranking[:4]
        ],
        "coarsePhaseWinnerOffset": int(coarse_ranking[0]["offset"]),
        "coarsePhaseRanking": [int(item["offset"]) for item in coarse_ranking],
        "coarsePhaseContrasts": {str(item["offset"]): float(item["contrast"]) for item in coarse},
        "features": {
            "attackCount": attack_count,
            "attackDensityPerGridStep": attack_count / (len(measures) * STEPS_PER_MEASURE),
            "meanPrimaryAttackSupport": statistics.mean(attack_supports) if attack_supports else None,
            "medianAttackMinusBody": statistics.median(front_body) if front_body else None,
            "shortSamePrimaryRepeatCount": repeat_count,
            "shortSamePrimaryRepeatRate": repeat_count / attack_count if attack_count else 0.0,
            "carryoverQ25SuspectCount": carry_q25,
            "carryoverQ25SuspectRate": carry_q25 / attack_count if attack_count else 0.0,
            "strictCarryoverSuspectCount": strict,
            "strictCarryoverSuspectRate": strict / attack_count if attack_count else 0.0,
            "upperHarmonicOutscoresPrimaryCount": upper_outscore,
            "upperHarmonicOutscoresPrimaryRate": upper_outscore / attack_count if attack_count else 0.0,
        },
    }


def _windows(rows: list[dict[str, Any]], rows_by_key: dict[tuple[int, int], dict[str, Any]], width: int, stride: int, final: int = 112) -> list[dict[str, Any]]:
    result = []
    start = 1
    while start + width - 1 <= final:
        result.append(_window(rows, rows_by_key, start, start + width - 1))
        start += stride
    return result


def _phase_runs(windows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    if not windows:
        return []
    runs: list[dict[str, Any]] = []
    current = {
        "startMeasure": int(windows[0]["startMeasure"]),
        "endMeasure": int(windows[0]["endMeasure"]),
        "winnerOffset": int(windows[0][field]),
        "windowCount": 1,
    }
    for item in windows[1:]:
        winner = int(item[field])
        if winner == int(current["winnerOffset"]):
            current["endMeasure"] = int(item["endMeasure"])
            current["windowCount"] = int(current["windowCount"]) + 1
        else:
            runs.append(current)
            current = {
                "startMeasure": int(item["startMeasure"]),
                "endMeasure": int(item["endMeasure"]),
                "winnerOffset": winner,
                "windowCount": 1,
            }
    runs.append(current)
    return runs


def _transitions(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for left, right in zip(windows, windows[1:]):
        left_winner = int(left["coarsePhaseWinnerOffset"])
        right_winner = int(right["coarsePhaseWinnerOffset"])
        if left_winner == right_winner:
            continue
        lf = left["features"]
        rf = right["features"]
        result.append({
            "boundaryMeasure": int(right["startMeasure"]),
            "leftRange": [int(left["startMeasure"]), int(left["endMeasure"])],
            "rightRange": [int(right["startMeasure"]), int(right["endMeasure"])],
            "coarseWinnerLeft": left_winner,
            "coarseWinnerRight": right_winner,
            "coarseCircularDelta": _circular_delta(right_winner, left_winner),
            "fineWinnerLeft": int(left["finePhaseWinnerOffset"]),
            "fineWinnerRight": int(right["finePhaseWinnerOffset"]),
            "fineCircularDelta": _circular_delta(int(right["finePhaseWinnerOffset"]), int(left["finePhaseWinnerOffset"])),
            "featureDeltasRightMinusLeft": {
                "attackDensityPerGridStep": float(rf["attackDensityPerGridStep"]) - float(lf["attackDensityPerGridStep"]),
                "meanPrimaryAttackSupport": float(rf["meanPrimaryAttackSupport"] or 0.0) - float(lf["meanPrimaryAttackSupport"] or 0.0),
                "medianAttackMinusBody": float(rf["medianAttackMinusBody"] or 0.0) - float(lf["medianAttackMinusBody"] or 0.0),
                "shortSamePrimaryRepeatRate": float(rf["shortSamePrimaryRepeatRate"]) - float(lf["shortSamePrimaryRepeatRate"]),
                "carryoverQ25SuspectRate": float(rf["carryoverQ25SuspectRate"]) - float(lf["carryoverQ25SuspectRate"]),
                "upperHarmonicOutscoresPrimaryRate": float(rf["upperHarmonicOutscoresPrimaryRate"]) - float(lf["upperHarmonicOutscoresPrimaryRate"]),
            },
        })
    return result


def _fine_change_summary(windows: list[dict[str, Any]]) -> dict[str, Any]:
    winners = [int(item["finePhaseWinnerOffset"]) for item in windows]
    deltas = [_circular_delta(new, old) for old, new in zip(winners, winners[1:])]
    changed = [delta for delta in deltas if delta != 0]
    small = [delta for delta in changed if abs(delta) <= 2]
    large = [delta for delta in changed if abs(delta) >= 4]
    return {
        "winnerOffsets": winners,
        "consecutiveCircularDeltas": deltas,
        "changeCount": len(changed),
        "smallOneOrTwoStepChangeCount": len(small),
        "largeFourOrMoreStepChangeCount": len(large),
        "smallChangeFractionAmongChanges": len(small) / len(changed) if changed else None,
    }


def diagnose(evidence: dict[str, Any]) -> dict[str, Any]:
    rows, tempo = _load_rows(evidence)
    thresholds = _attach_repeat_physics(rows, tempo)
    rows_by_key = {(int(row["measure"]), int(row["step"])): row for row in rows}
    windows4 = _windows(rows, rows_by_key, width=4, stride=4)
    windows8 = _windows(rows, rows_by_key, width=8, stride=8)
    windows16 = _windows(rows, rows_by_key, width=16, stride=8)
    runs8 = _phase_runs(windows8, "coarsePhaseWinnerOffset")
    transitions8 = _transitions(windows8)
    fine4 = _fine_change_summary(windows4)

    return {
        "schemaVersion": 1,
        "mode": "v143-frozen-evidence-phase-section-diagnostic",
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
        "tempoBpm": tempo,
        "repeatPhysicsThresholds": thresholds,
        "method": {
            "purpose": "map local phase winners and test whether changes co-occur with reference-free physical feature changes",
            "finePhaseOffsetsTested": list(range(16)),
            "coarsePhaseOffsets": [0, 4, 8, 12],
            "missingAttackSupportZeroFilled": True,
            "sameMeasureScopeForEveryPhaseWithinWindow": True,
            "causeNotAssumed": "phase winner changes can reflect section accents, pickup/reset behavior, or timing-grid drift; this diagnostic only localizes and characterizes them",
        },
        "fourMeasureWindows": windows4,
        "eightMeasureWindows": windows8,
        "sixteenMeasureWindowsStride8": windows16,
        "eightMeasureCoarsePhaseRuns": runs8,
        "eightMeasureCoarseTransitions": transitions8,
        "fourMeasureFinePhaseChangeSummary": fine4,
        "invariants": {
            "all725AttacksRead": len(rows) == ATTACK_COUNT,
            "eventsMutated": False,
            "attackGridMutated": False,
            "pitchSelectionMutated": False,
            "referenceConsulted": False,
            "phaseSelectionPerformed": False,
        },
    }


def main(source: str, destination: str) -> None:
    evidence = json.loads(Path(source).read_text(encoding="utf-8"))
    report = diagnose(evidence)
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "attackCount": report["attackCount"],
        "eightMeasureCoarsePhaseRuns": report["eightMeasureCoarsePhaseRuns"],
        "eightMeasureCoarseTransitions": report["eightMeasureCoarseTransitions"],
        "fourMeasureFinePhaseChangeSummary": report["fourMeasureFinePhaseChangeSummary"],
    }, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_frozen_evidence_phase_section_diagnostic.py EVIDENCE OUTPUT")
    main(sys.argv[1], sys.argv[2])
