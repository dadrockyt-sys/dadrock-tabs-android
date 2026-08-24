from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
RETIRED_EVENT_SHA256 = "a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb"
HARMONIC_INTERVALS = {12, 19, 24, 28, 31, 36}


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


def _summary(values: list[float]) -> dict[str, float | int | None]:
    return {
        "count": len(values),
        "min": min(values) if values else None,
        "q10": _quantile(values, 0.10),
        "q25": _quantile(values, 0.25),
        "median": statistics.median(values) if values else None,
        "q75": _quantile(values, 0.75),
        "q90": _quantile(values, 0.90),
        "max": max(values) if values else None,
    }


def _hypothesis_map(attack: list[Any]) -> dict[int, list[Any]]:
    return {int(item[0]): item for item in attack[4]}


def _primary_sustain(attack: list[Any]) -> bool:
    primary = int(attack[3])
    for note in attack[5]:
        if int(note[1]) == primary:
            return bool(note[4])
    return False


def _jaccard(left: set[int], right: set[int]) -> float:
    union = left | right
    if not union:
        return 1.0
    return len(left & right) / len(union)


def _phase_metrics(rows: list[dict[str, Any]], offset_steps: int) -> dict[str, Any]:
    total_steps = 113 * 16
    bars: dict[int, dict[int, dict[str, Any]]] = {}
    for row in rows:
        global_step = (int(row["measure"]) - 1) * 16 + int(row["step"])
        shifted = global_step - int(offset_steps)
        if shifted < 0 or shifted >= total_steps:
            continue
        bar = shifted // 16 + 1
        step = shifted % 16
        bars.setdefault(bar, {})[step] = row

    lag_metrics: dict[str, Any] = {}
    for lag in (1, 2, 4):
        occupancy_scores: list[float] = []
        primary_equal = 0
        primary_shared = 0
        pitch_jaccards: list[float] = []
        for bar in range(1, 114 - lag):
            left = bars.get(bar) or {}
            right = bars.get(bar + lag) or {}
            if not left or not right:
                continue
            occupancy_scores.append(_jaccard(set(left), set(right)))
            for step in sorted(set(left) & set(right)):
                primary_shared += 1
                primary_equal += int(int(left[step]["primaryMidi"]) == int(right[step]["primaryMidi"]))
                pitch_jaccards.append(_jaccard(set(left[step]["selectedMidis"]), set(right[step]["selectedMidis"])))
        lag_metrics[str(lag)] = {
            "barPairCount": len(occupancy_scores),
            "occupancyJaccardMean": statistics.mean(occupancy_scores) if occupancy_scores else None,
            "occupancyJaccardMedian": statistics.median(occupancy_scores) if occupancy_scores else None,
            "sharedStepCount": primary_shared,
            "primaryAgreement": primary_equal / primary_shared if primary_shared else None,
            "selectedPitchSetJaccardMean": statistics.mean(pitch_jaccards) if pitch_jaccards else None,
        }

    step_attack: dict[int, list[float]] = {step: [] for step in range(16)}
    for bar_rows in bars.values():
        for step, row in bar_rows.items():
            step_attack[int(step)].append(float(row["primaryAttackSupport"]))
    beat_step_means = {
        str(step): statistics.mean(step_attack[step]) if step_attack[step] else None
        for step in (0, 4, 8, 12)
    }
    other_beat_means = [value for step, value in beat_step_means.items() if step != "0" and value is not None]
    downbeat_mean = beat_step_means["0"]
    downbeat_contrast = None
    if downbeat_mean is not None and other_beat_means:
        downbeat_contrast = downbeat_mean - statistics.mean(other_beat_means)

    return {
        "offsetSixteenthStepsFromCurrent": int(offset_steps),
        "retainedAttackCount": sum(len(value) for value in bars.values()),
        "populatedBarCount": len(bars),
        "lagRecurrence": lag_metrics,
        "beatStepPrimaryAttackMeans": beat_step_means,
        "downbeatAttackContrastVsOtherBeats": downbeat_contrast,
    }


def diagnose(evidence: dict[str, Any]) -> dict[str, Any]:
    provenance = evidence.get("provenance") or {}
    if provenance.get("sourceAudioSha256") != APPROVED_AUDIO_SHA256:
        raise RuntimeError("approved frozen source audio changed")
    if provenance.get("retiredFrozenEventSha256") != RETIRED_EVENT_SHA256:
        raise RuntimeError("frozen source identity changed")
    if provenance.get("referenceFree") is not True:
        raise RuntimeError("frozen evidence is not reference-free")
    if provenance.get("professionalReferenceUsed") is not False:
        raise RuntimeError("frozen evidence provenance is unsafe")
    if provenance.get("referenceRuntimeInputUsed") is not False or provenance.get("preScorer") is not True:
        raise RuntimeError("frozen evidence is not sealed pre-scorer evidence")

    attacks = list(evidence.get("attacks") or [])
    tempo = float(evidence.get("tempoBpm") or 0.0)
    if len(attacks) != 725 or tempo <= 0.0:
        raise RuntimeError("frozen attack cardinality/tempo changed")
    attacks.sort(key=lambda row: float(row[2]))
    step_seconds = 60.0 / tempo / 4.0

    rows: list[dict[str, Any]] = []
    attack_supports: list[float] = []
    body_supports: list[float] = []
    front_minus_body: list[float] = []
    for index, attack in enumerate(attacks):
        primary = int(attack[3])
        hypotheses = _hypothesis_map(attack)
        if primary not in hypotheses:
            raise RuntimeError(f"primary missing from hypotheses at attack {index}")
        hyp = hypotheses[primary]
        attack_support = float(hyp[1])
        body_support = float(hyp[2])
        persistence_support = float(hyp[3])
        combined_score = float(hyp[4])
        attack_supports.append(attack_support)
        body_supports.append(body_support)
        front_minus_body.append(attack_support - body_support)
        rows.append({
            "index": index,
            "measure": int(attack[0]),
            "step": int(attack[1]),
            "timeSeconds": float(attack[2]),
            "primaryMidi": primary,
            "selectedMidis": sorted({int(note[1]) for note in attack[5]}),
            "primaryAttackSupport": attack_support,
            "primaryBodySupport": body_support,
            "primaryPersistenceSupport": persistence_support,
            "primaryCombinedScore": combined_score,
            "primarySustainEvidence": _primary_sustain(attack),
            "hypotheses": hypotheses,
        })

    attack_q25 = float(_quantile(attack_supports, 0.25))
    attack_median = float(statistics.median(attack_supports))
    body_median = float(statistics.median(body_supports))
    front_body_q25 = float(_quantile(front_minus_body, 0.25))

    repeat_pairs: list[dict[str, Any]] = []
    carryover_q25: list[dict[str, Any]] = []
    carryover_strict: list[dict[str, Any]] = []
    for current_index in range(1, len(rows)):
        current = rows[current_index]
        previous = None
        for prior_index in range(current_index - 1, -1, -1):
            if rows[prior_index]["primaryMidi"] == current["primaryMidi"]:
                previous = rows[prior_index]
                break
        if previous is None:
            continue
        gap = float(current["timeSeconds"] - previous["timeSeconds"])
        gap_steps = gap / step_seconds
        if gap_steps > 2.35:
            continue
        delta = float(current["primaryAttackSupport"] - current["primaryBodySupport"])
        pair = {
            "measure": current["measure"],
            "step": current["step"],
            "timeSeconds": current["timeSeconds"],
            "primaryMidi": current["primaryMidi"],
            "gapSeconds": gap,
            "gapSixteenthSteps": gap_steps,
            "previousMeasure": previous["measure"],
            "previousStep": previous["step"],
            "previousSustainEvidence": previous["primarySustainEvidence"],
            "currentSustainEvidence": current["primarySustainEvidence"],
            "currentAttackSupport": current["primaryAttackSupport"],
            "currentBodySupport": current["primaryBodySupport"],
            "currentFrontMinusBody": delta,
            "previousAttackSupport": previous["primaryAttackSupport"],
            "previousBodySupport": previous["primaryBodySupport"],
        }
        repeat_pairs.append(pair)
        if previous["primarySustainEvidence"] and delta <= front_body_q25:
            carryover_q25.append(pair)
        if (
            previous["primarySustainEvidence"]
            and current["primaryAttackSupport"] <= attack_q25
            and current["primaryBodySupport"] >= body_median
            and delta < 0.0
        ):
            carryover_strict.append(pair)

    upper_family_attacks: list[dict[str, Any]] = []
    lower_family_attacks: list[dict[str, Any]] = []
    upper_outscores_primary = 0
    lower_outscores_primary = 0
    for row in rows:
        primary = int(row["primaryMidi"])
        hypotheses = row["hypotheses"]
        primary_score = float(hypotheses[primary][4])
        upper = []
        lower = []
        for midi, hyp in hypotheses.items():
            interval = int(midi) - primary
            item = {
                "midi": int(midi),
                "interval": interval,
                "attackSupport": float(hyp[1]),
                "bodySupport": float(hyp[2]),
                "persistenceSupport": float(hyp[3]),
                "combinedScore": float(hyp[4]),
                "outscoresPrimary": float(hyp[4]) > primary_score,
            }
            if interval in HARMONIC_INTERVALS:
                upper.append(item)
            elif -interval in HARMONIC_INTERVALS:
                lower.append(item)
        if upper:
            upper_outscores_primary += int(any(item["outscoresPrimary"] for item in upper))
            upper_family_attacks.append({
                "measure": row["measure"], "step": row["step"], "primaryMidi": primary,
                "primaryScore": primary_score, "family": upper,
            })
        if lower:
            lower_outscores_primary += int(any(item["outscoresPrimary"] for item in lower))
            lower_family_attacks.append({
                "measure": row["measure"], "step": row["step"], "primaryMidi": primary,
                "primaryScore": primary_score, "family": lower,
            })

    carryover_ranked = sorted(
        carryover_q25,
        key=lambda item: (float(item["currentFrontMinusBody"]), float(item["currentAttackSupport"]), float(item["gapSixteenthSteps"])),
    )[:80]
    lower_ranked = sorted(
        lower_family_attacks,
        key=lambda item: min(float(f["combinedScore"]) - float(item["primaryScore"]) for f in item["family"]),
        reverse=True,
    )[:80]

    phase_candidates = [_phase_metrics(rows, offset) for offset in (0, 4, 8, 12)]
    metric_winners: dict[str, int] = {}
    metric_paths = {
        "lag1OccupancyJaccard": lambda p: p["lagRecurrence"]["1"]["occupancyJaccardMean"],
        "lag2OccupancyJaccard": lambda p: p["lagRecurrence"]["2"]["occupancyJaccardMean"],
        "lag4OccupancyJaccard": lambda p: p["lagRecurrence"]["4"]["occupancyJaccardMean"],
        "lag1PrimaryAgreement": lambda p: p["lagRecurrence"]["1"]["primaryAgreement"],
        "lag1PitchSetJaccard": lambda p: p["lagRecurrence"]["1"]["selectedPitchSetJaccardMean"],
        "downbeatAttackContrast": lambda p: p["downbeatAttackContrastVsOtherBeats"],
    }
    for name, getter in metric_paths.items():
        valid = [(float(getter(p)), int(p["offsetSixteenthStepsFromCurrent"])) for p in phase_candidates if getter(p) is not None]
        if valid:
            metric_winners[name] = max(valid)[1]
    winner_counts: dict[str, int] = {}
    for offset in metric_winners.values():
        key = str(offset)
        winner_counts[key] = winner_counts.get(key, 0) + 1

    return {
        "schemaVersion": 2,
        "mode": "v143-frozen-evidence-attack-physics-diagnostic",
        "sourceAudioSha256": APPROVED_AUDIO_SHA256,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "modalUsed": False,
        "productionModified": False,
        "protectedRuntimeModified": False,
        "candidateRenderProduced": False,
        "attackCount": len(rows),
        "tempoBpm": tempo,
        "sixteenthStepSeconds": step_seconds,
        "primarySupportDistributions": {
            "attack": _summary(attack_supports),
            "body": _summary(body_supports),
            "attackMinusBody": _summary(front_minus_body),
        },
        "repeatPhysics": {
            "definition": "most-recent same-primary repeat within 2.35 sixteenth steps",
            "repeatPairCount": len(repeat_pairs),
            "priorSustainAndFrontMinusBodyBottomQuartileCount": len(carryover_q25),
            "strictWeakFrontStrongBodyCount": len(carryover_strict),
            "diagnosticThresholdsFromFrozenDistribution": {
                "primaryAttackQ25": attack_q25,
                "primaryAttackMedian": attack_median,
                "primaryBodyMedian": body_median,
                "attackMinusBodyQ25": front_body_q25,
            },
            "rankedCarryoverSuspects": carryover_ranked,
            "strictCarryoverSuspects": carryover_strict[:80],
        },
        "harmonicFamilyPhysics": {
            "upperFamilyAttackCount": len(upper_family_attacks),
            "upperFamilyOutscoresPrimaryAttackCount": upper_outscores_primary,
            "lowerFamilyAttackCount": len(lower_family_attacks),
            "lowerFamilyOutscoresPrimaryAttackCount": lower_outscores_primary,
            "rankedLowerFundamentalCandidates": lower_ranked,
        },
        "barPhaseRecurrence": {
            "definition": "rotate current 16-step bar boundary by whole-beat offsets; compare recurrence and physical onset accent without changing any event",
            "candidateOffsetsSixteenthSteps": [0, 4, 8, 12],
            "candidates": phase_candidates,
            "metricWinners": metric_winners,
            "winnerCounts": winner_counts,
            "currentBoundaryOffset": 0,
            "phaseSelectedOrChanged": False,
        },
        "invariants": {
            "all725AttacksRead": len(rows) == 725,
            "eventsMutated": False,
            "attackGridMutated": False,
            "pitchSelectionMutated": False,
            "referenceConsulted": False,
        },
    }


def main(source: str, destination: str) -> None:
    evidence = json.loads(Path(source).read_text(encoding="utf-8"))
    report = diagnose(evidence)
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "attackCount": report["attackCount"],
        "repeatPhysics": {k: v for k, v in report["repeatPhysics"].items() if not k.endswith("Suspects")},
        "harmonicFamilyPhysics": {k: v for k, v in report["harmonicFamilyPhysics"].items() if not k.startswith("ranked")},
        "barPhaseMetricWinners": report["barPhaseRecurrence"]["metricWinners"],
        "barPhaseWinnerCounts": report["barPhaseRecurrence"]["winnerCounts"],
    }, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_frozen_evidence_attack_physics_diagnostic.py EVIDENCE OUTPUT")
    main(sys.argv[1], sys.argv[2])
