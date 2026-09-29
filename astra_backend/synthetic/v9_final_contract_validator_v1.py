#!/usr/bin/env python3
"""Pure static validator for the frozen V9 final empirical contract.

This module does not generate candidate timing values, render audio, import a model,
run inference, or perform optimization.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


class ContractError(ValueError):
    pass


POSITIVE_CLIPS = {
    "isolated": 42,
    "scales": 42,
    "chords": 42,
    "repeated": 42,
    "legato": 42,
    "palmmute": 42,
    "mixed": 21,
}


def _finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ContractError(f"{name} must be finite numeric")
    return float(value)


def timing_distance(row, target):
    return (
        abs(row["repeat250"] - target["repeat250"])
        + abs(row["ioiP50"] - target["ioiP50"]) / target["ioiP50"]
        + abs(row["ioiP90"] - target["ioiP90"]) / target["ioiP90"]
        + 0.5 * abs(row["density"] - target["density"]) / target["density"]
        + 0.5 * abs(row["longGap700"] - target["longGap700"]) / target["longGap700"]
    )


def validate(contract):
    if contract.get("schema") != "astra-v9-final-empirical-contract-v1":
        raise ContractError("wrong schema")
    if contract.get("status") != "frozen-execution-not-authorized":
        raise ContractError("contract must remain frozen and unauthorized")

    intervention = contract["intervention"]
    if intervention["clipSeconds"] != 4.0:
        raise ContractError("V9 must have exactly one 4-second intervention")

    counts = intervention["attackGroupsPerPositiveClip"]
    attack_total = sum(POSITIVE_CLIPS[k] * int(counts[k]) for k in POSITIVE_CLIPS)
    if attack_total != intervention["attackGroupCount"] or attack_total != 1638:
        raise ContractError("attack-group arithmetic mismatch")
    if intervention["positiveSeconds"] != 273 * 4:
        raise ContractError("positive-second arithmetic mismatch")
    if not math.isclose(intervention["attackGroupDensity"], attack_total / intervention["positiveSeconds"], rel_tol=0, abs_tol=1e-15):
        raise ContractError("attack-group density mismatch")

    # Three attacked note labels per chord group, one per other attack group.
    note_total = attack_total + 2 * POSITIVE_CLIPS["chords"] * counts["chords"]
    if note_total != intervention["attackedNoteLabelCount"] or note_total != 1806:
        raise ContractError("attacked note-label arithmetic mismatch")

    multisets = intervention["gapClassMultisets"]
    supports = intervention["gapClasses"]
    agg = {"S": 0, "M": 0, "L": 0}
    for family, clip_count in POSITIVE_CLIPS.items():
        expected_gaps = counts[family] - 1
        classes = multisets[family]
        if len(classes) != expected_gaps:
            raise ContractError(f"{family} gap count mismatch")
        for klass in classes:
            if klass not in agg:
                raise ContractError("unknown gap class")
            agg[klass] += clip_count
    if agg != {k: intervention["aggregateGapClassCounts"][k] for k in ("S", "M", "L")}:
        raise ContractError("aggregate gap classes mismatch")
    if sum(agg.values()) != intervention["aggregateGapClassCounts"]["total"] or sum(agg.values()) != 1365:
        raise ContractError("total gap count mismatch")

    total = sum(agg.values())
    for klass in agg:
        expected = agg[klass] / total
        if not math.isclose(expected, intervention["aggregateGapClassFractions"][klass], rel_tol=0, abs_tol=1e-15):
            raise ContractError("gap fraction mismatch")

    s_lo, s_hi = map(float, supports["S"]["supportSeconds"])
    m_lo, m_hi = map(float, supports["M"]["supportSeconds"])
    l_lo, l_hi = map(float, supports["L"]["supportSeconds"])
    if not (0 < s_lo <= s_hi <= 0.250 < m_lo <= m_hi < l_lo <= l_hi):
        raise ContractError("gap supports overlap or violate repeat semantics")

    first_hi = float(intervention["firstAttackSupportSeconds"][1])
    final_margin = float(intervention["finalMarginSeconds"])
    for family, classes in multisets.items():
        worst = first_hi + final_margin + sum(
            supports[k]["supportSeconds"][1] for k in classes
        )
        if worst >= intervention["clipSeconds"]:
            raise ContractError(f"{family} worst-case gap support does not fit: {worst}")

    sustain_lo, sustain_hi = map(float, intervention["sustainSupportSeconds"])
    if sustain_lo <= 0 or sustain_hi < sustain_lo or final_margin < sustain_lo:
        raise ContractError("sustain/final-margin contract invalid")

    target = contract["reference"]["v2b"]
    baseline = contract["reference"]["v8L0CommonUnit"]
    d = timing_distance(baseline, target)
    if not math.isclose(d, baseline["timingDistanceV1"], rel_tol=0, abs_tol=1e-12):
        raise ContractError("baseline timing distance mismatch")

    gate = contract["v9aGate"]
    if gate["maxAdvancingArms"] != 1:
        raise ContractError("only one arm may advance")
    if gate["attackGroupCountExactly"] != 1638 or gate["attackedNoteLabelCountExactly"] != 1806:
        raise ContractError("gate identity counts mismatch")
    if any(gate[k] != 0 for k in (
        "infeasibleClipCountExactly",
        "invalidLabelCountExactly",
        "invalidOffsetCountExactly",
        "fallbackOperationCountExactly",
    )):
        raise ContractError("fail-closed zero-count gates changed")

    training = contract["training"]
    if training["models"] != 2 or training["optimizerStepsPerModel"] != 500 or training["maxOptimizerStepsTotal"] != 1000:
        raise ContractError("training ceiling mismatch")
    if training["stateThreshold"] != 0.5 or training["onsetThreshold"] != 0.5:
        raise ContractError("thresholds changed")
    if contract["launch"]["armed"]:
        raise ContractError("launch must not be armed by contract preparation")
    if contract["boundaries"]["executionAuthorized"]:
        raise ContractError("execution must remain unauthorized")

    return {
        "valid": True,
        "attackGroupCount": attack_total,
        "attackedNoteLabelCount": note_total,
        "gapClassCounts": agg,
        "worstCaseFamilySeconds": {
            family: first_hi + final_margin + sum(supports[k]["supportSeconds"][1] for k in classes)
            for family, classes in multisets.items()
        },
        "baselineTimingDistanceV1": d,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    args = ap.parse_args()
    contract = json.loads(Path(args.contract).read_text())
    print(json.dumps(validate(contract), sort_keys=True))


if __name__ == "__main__":
    main()
