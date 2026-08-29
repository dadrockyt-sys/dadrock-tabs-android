#!/usr/bin/env python3
"""Reference-blind temporal/recurrence diagnosis after terminal V167 topology sweep.

This analyzer reads only immutable generated candidates and frozen aggregate reports.
It never accepts the professional reference or scorer and never reads per-event match
assignments. It characterizes the exact 48 frozen I005 Guitar additions in a new
structural dimension: recurrence/clustering in grid time and MIDI relative to each
other and to the immutable 1050-event I003 Guitar base.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping

EXPECTED = {
    "i003Sha256": "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115",
    "i005Sha256": "86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31",
    "topologyReportSha256": "869825ed2a91e9f50bc6ca5ac71d922ee93dc17dd5804bf8d94d0e951e179b85",
    "postI005DiagnosisSha256": "fe7e826724a11e115a25f932d4b58ed88e3aedae67fb54142cc532cc40ab8450",
    "i003GuitarCount": 1050,
    "i005GuitarCount": 1098,
    "additionCount": 48,
}

THRESHOLDS = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def coord(row: Mapping[str, Any]) -> tuple[int, int]:
    return int(row["absoluteGridStep"]), int(row["midi"])


def quantile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(x) for x in values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * p
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    w = pos - lo
    return ordered[lo] * (1.0 - w) + ordered[hi] * w


def summarize(values: Iterable[float]) -> dict[str, Any]:
    rows = [float(x) for x in values]
    if not rows:
        return {
            "count": 0,
            "min": None,
            "p10": None,
            "p25": None,
            "median": None,
            "p75": None,
            "p90": None,
            "max": None,
            "mean": None,
        }
    return {
        "count": len(rows),
        "min": min(rows),
        "p10": quantile(rows, 0.10),
        "p25": quantile(rows, 0.25),
        "median": quantile(rows, 0.50),
        "p75": quantile(rows, 0.75),
        "p90": quantile(rows, 0.90),
        "max": max(rows),
        "mean": mean(rows),
    }


def nearest_distance(step: int, candidates: list[int]) -> int | None:
    distances = [abs(step - other) for other in candidates if other != step]
    return min(distances) if distances else None


def nearest_prior_distance(step: int, candidates: list[int]) -> int | None:
    priors = [step - other for other in candidates if other < step]
    return min(priors) if priors else None


def nearest_next_distance(step: int, candidates: list[int]) -> int | None:
    nexts = [other - step for other in candidates if other > step]
    return min(nexts) if nexts else None


def count_within(values: list[int | None]) -> dict[str, int]:
    return {
        f"le_{threshold}": sum(
            value is not None and int(value) <= threshold for value in values
        )
        for threshold in THRESHOLDS
    }


def cluster_components(steps: list[int], max_gap: int) -> list[list[int]]:
    ordered = sorted(set(steps))
    if not ordered:
        return []
    groups = [[ordered[0]]]
    for step in ordered[1:]:
        if step - groups[-1][-1] <= max_gap:
            groups[-1].append(step)
        else:
            groups.append([step])
    return groups


def run_lengths_same_midi(rows: list[dict[str, Any]], max_gap: int) -> list[dict[str, Any]]:
    by_midi: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        by_midi[int(row["midi"])].append(int(row["absoluteGridStep"]))
    runs: list[dict[str, Any]] = []
    for midi, steps in sorted(by_midi.items()):
        for component in cluster_components(steps, max_gap):
            if len(component) >= 2:
                runs.append(
                    {
                        "midi": midi,
                        "steps": component,
                        "count": len(component),
                        "spanGridSteps": component[-1] - component[0],
                    }
                )
    return runs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--i003", type=Path, required=True)
    ap.add_argument("--i005", type=Path, required=True)
    ap.add_argument("--topology-report", type=Path, required=True)
    ap.add_argument("--post-i005-diagnosis", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"temporal recurrence output already exists: {args.output}")
    for path, expected in (
        (args.i003, EXPECTED["i003Sha256"]),
        (args.i005, EXPECTED["i005Sha256"]),
        (args.topology_report, EXPECTED["topologyReportSha256"]),
        (args.post_i005_diagnosis, EXPECTED["postI005DiagnosisSha256"]),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen temporal input SHA mismatch: {path}: {actual}")

    i003 = json.loads(args.i003.read_text(encoding="utf-8"))
    i005 = json.loads(args.i005.read_text(encoding="utf-8"))
    topology_report = json.loads(args.topology_report.read_text(encoding="utf-8"))
    diagnosis = json.loads(args.post_i005_diagnosis.read_text(encoding="utf-8"))

    if int((i003.get("calibration") or {}).get("iteration", -1)) != 3:
        raise RuntimeError("temporal diagnosis base must be I003")
    if int((i005.get("calibration") or {}).get("iteration", -1)) != 5:
        raise RuntimeError("temporal diagnosis current best must be I005")
    if topology_report.get("status") != "REFERENCE_GRADED_COMPLETE_PREDECLARED_ACTIVE_TOPOLOGY_VARIANTS":
        raise RuntimeError("topology report not terminal")
    if topology_report.get("newVariantsBeatingI005") != 0:
        raise RuntimeError("temporal diagnosis expected terminal negative topology sweep")
    if topology_report.get("newVariantsMeetingPromotionEligibility") != 0:
        raise RuntimeError("unexpected topology promotion eligibility")
    if diagnosis.get("status") != "POST_I005_AGGREGATE_REFERENCE_BLIND_ANALYSIS_FROZEN":
        raise RuntimeError("post-I005 diagnosis not frozen")

    i003_guitar = list((i003.get("streams") or {}).get("combinedGuitar") or [])
    i005_guitar = list((i005.get("streams") or {}).get("combinedGuitar") or [])
    if len(i003_guitar) != EXPECTED["i003GuitarCount"]:
        raise RuntimeError("I003 Guitar count drift")
    if len(i005_guitar) != EXPECTED["i005GuitarCount"]:
        raise RuntimeError("I005 Guitar count drift")

    base_coords = {coord(row) for row in i003_guitar}
    additions = [dict(row) for row in i005_guitar if coord(row) not in base_coords]
    if len(additions) != EXPECTED["additionCount"]:
        raise RuntimeError(f"I005 addition count drift: {len(additions)}")
    additions.sort(key=lambda row: (int(row["absoluteGridStep"]), int(row["midi"])))

    addition_steps = [int(row["absoluteGridStep"]) for row in additions]
    base_steps = [int(row["absoluteGridStep"]) for row in i003_guitar]
    all_i005_steps = [int(row["absoluteGridStep"]) for row in i005_guitar]
    addition_steps_by_midi: dict[int, list[int]] = defaultdict(list)
    base_steps_by_midi: dict[int, list[int]] = defaultdict(list)
    for row in additions:
        addition_steps_by_midi[int(row["midi"])].append(int(row["absoluteGridStep"]))
    for row in i003_guitar:
        base_steps_by_midi[int(row["midi"])].append(int(row["absoluteGridStep"]))

    rows: list[dict[str, Any]] = []
    nearest_add_any: list[int | None] = []
    prior_add_any: list[int | None] = []
    next_add_any: list[int | None] = []
    nearest_add_same: list[int | None] = []
    prior_add_same: list[int | None] = []
    next_add_same: list[int | None] = []
    nearest_base_any: list[int | None] = []
    prior_base_any: list[int | None] = []
    next_base_any: list[int | None] = []
    nearest_base_same: list[int | None] = []
    prior_base_same: list[int | None] = []
    next_base_same: list[int | None] = []

    for row in additions:
        step = int(row["absoluteGridStep"])
        midi = int(row["midi"])
        wrapper = row.get("v167RecoverySweepEvidence") or {}
        evidence = wrapper.get("evidence") or {}
        if (wrapper.get("rule") or {}).get("id") != "gss-active-only":
            raise RuntimeError("unexpected I005 addition rule")

        naa = nearest_distance(step, addition_steps)
        paa = nearest_prior_distance(step, addition_steps)
        xaa = nearest_next_distance(step, addition_steps)
        nas = nearest_distance(step, addition_steps_by_midi[midi])
        pas = nearest_prior_distance(step, addition_steps_by_midi[midi])
        xas = nearest_next_distance(step, addition_steps_by_midi[midi])
        nba = min((abs(step - x) for x in base_steps), default=None)
        pba = nearest_prior_distance(step, base_steps)
        xba = nearest_next_distance(step, base_steps)
        nbs = min((abs(step - x) for x in base_steps_by_midi.get(midi, [])), default=None)
        pbs = nearest_prior_distance(step, base_steps_by_midi.get(midi, []))
        xbs = nearest_next_distance(step, base_steps_by_midi.get(midi, []))

        nearest_add_any.append(naa)
        prior_add_any.append(paa)
        next_add_any.append(xaa)
        nearest_add_same.append(nas)
        prior_add_same.append(pas)
        next_add_same.append(xas)
        nearest_base_any.append(nba)
        prior_base_any.append(pba)
        next_base_any.append(xba)
        nearest_base_same.append(nbs)
        prior_base_same.append(pbs)
        next_base_same.append(xbs)

        rows.append(
            {
                "absoluteGridStep": step,
                "midi": midi,
                "siteFrame": int(evidence["siteFrame"]),
                "onsetSupport": float(evidence["onsetSupport"]),
                "activitySupport": float(evidence["activitySupport"]),
                "nearestAdditionAnyMidiGridSteps": naa,
                "priorAdditionAnyMidiGridSteps": paa,
                "nextAdditionAnyMidiGridSteps": xaa,
                "nearestAdditionSameMidiGridSteps": nas,
                "priorAdditionSameMidiGridSteps": pas,
                "nextAdditionSameMidiGridSteps": xas,
                "nearestBaseAnyMidiGridSteps": nba,
                "priorBaseAnyMidiGridSteps": pba,
                "nextBaseAnyMidiGridSteps": xba,
                "nearestBaseSameMidiGridSteps": nbs,
                "priorBaseSameMidiGridSteps": pbs,
                "nextBaseSameMidiGridSteps": xbs,
            }
        )

    step_multiplicity = Counter(addition_steps)
    midi_multiplicity = Counter(int(row["midi"]) for row in additions)
    consecutive_any_runs_1 = [g for g in cluster_components(addition_steps, 1) if len(g) >= 2]
    compact_any_runs_2 = [g for g in cluster_components(addition_steps, 2) if len(g) >= 2]
    compact_any_runs_4 = [g for g in cluster_components(addition_steps, 4) if len(g) >= 2]
    same_midi_runs_1 = run_lengths_same_midi(rows, 1)
    same_midi_runs_2 = run_lengths_same_midi(rows, 2)
    same_midi_runs_4 = run_lengths_same_midi(rows, 4)

    output = {
        "schema": "dadrock.tabs.v167.post-topology-temporal-recurrence-analysis.v1",
        "version": "V167",
        "status": "POST_TOPOLOGY_TEMPORAL_RECURRENCE_REFERENCE_BLIND_ANALYSIS_FROZEN",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "iteration003Sha256": sha256_file(args.i003),
            "iteration005Sha256": sha256_file(args.i005),
            "terminalTopologyReportSha256": sha256_file(args.topology_report),
            "postI005DiagnosisSha256": sha256_file(args.post_i005_diagnosis),
        },
        "policy": {
            "professionalReferenceReadByAnalysis": False,
            "scorerReadByAnalysis": False,
            "newReferenceFacingScoreCalls": 0,
            "perEventReferenceMatchAssignmentsRead": False,
            "terminalAggregateTopologyScoresRead": True,
            "newRuleSelectedByThisAnalysis": False,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
            "generalizationClaim": False,
        },
        "additionCount": len(additions),
        "uniqueAdditionGridStepCount": len(step_multiplicity),
        "additionGridStepMultiplicityHistogram": dict(sorted(Counter(step_multiplicity.values()).items())),
        "additionMidiMultiplicity": dict(sorted((str(k), v) for k, v in midi_multiplicity.items())),
        "distanceDistributions": {
            "nearestAdditionAnyMidiGridSteps": summarize(x for x in nearest_add_any if x is not None),
            "priorAdditionAnyMidiGridSteps": summarize(x for x in prior_add_any if x is not None),
            "nextAdditionAnyMidiGridSteps": summarize(x for x in next_add_any if x is not None),
            "nearestAdditionSameMidiGridSteps": summarize(x for x in nearest_add_same if x is not None),
            "priorAdditionSameMidiGridSteps": summarize(x for x in prior_add_same if x is not None),
            "nextAdditionSameMidiGridSteps": summarize(x for x in next_add_same if x is not None),
            "nearestBaseAnyMidiGridSteps": summarize(x for x in nearest_base_any if x is not None),
            "priorBaseAnyMidiGridSteps": summarize(x for x in prior_base_any if x is not None),
            "nextBaseAnyMidiGridSteps": summarize(x for x in next_base_any if x is not None),
            "nearestBaseSameMidiGridSteps": summarize(x for x in nearest_base_same if x is not None),
            "priorBaseSameMidiGridSteps": summarize(x for x in prior_base_same if x is not None),
            "nextBaseSameMidiGridSteps": summarize(x for x in next_base_same if x is not None),
        },
        "withinThresholdCounts": {
            "nearestAdditionAnyMidi": count_within(nearest_add_any),
            "nearestAdditionSameMidi": count_within(nearest_add_same),
            "nearestBaseAnyMidi": count_within(nearest_base_any),
            "nearestBaseSameMidi": count_within(nearest_base_same),
            "priorBaseSameMidi": count_within(prior_base_same),
        },
        "clusterStructure": {
            "anyMidiGap1Runs": consecutive_any_runs_1,
            "anyMidiGap2Runs": compact_any_runs_2,
            "anyMidiGap4Runs": compact_any_runs_4,
            "sameMidiGap1Runs": same_midi_runs_1,
            "sameMidiGap2Runs": same_midi_runs_2,
            "sameMidiGap4Runs": same_midi_runs_4,
        },
        "selectedRowsReferenceBlind": rows,
        "diagnosticInterpretation": {
            "question": (
                "Determine whether the 48 active-state reattacks contain strong short-range "
                "same-MIDI or same-grid recurrence structure that could justify a future "
                "deterministic refractory/cluster rule."
            ),
            "ruleSelection": "none; this analysis reports distributions only",
        },
    }
    write_json(args.output, output)
    print(
        json.dumps(
            {
                "additionCount": output["additionCount"],
                "uniqueAdditionGridStepCount": output["uniqueAdditionGridStepCount"],
                "nearestAdditionAnyMidi": output["distanceDistributions"]["nearestAdditionAnyMidiGridSteps"],
                "nearestAdditionSameMidi": output["distanceDistributions"]["nearestAdditionSameMidiGridSteps"],
                "nearestBaseSameMidi": output["distanceDistributions"]["nearestBaseSameMidiGridSteps"],
                "withinThresholdCounts": output["withinThresholdCounts"],
                "sameMidiGap1RunCount": len(same_midi_runs_1),
                "sameMidiGap2RunCount": len(same_midi_runs_2),
                "sameMidiGap4RunCount": len(same_midi_runs_4),
                "newReferenceFacingScoreCalls": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
