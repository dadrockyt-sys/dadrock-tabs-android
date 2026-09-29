#!/usr/bin/env python3
"""PRE-V9-MEASUREMENT-V1: common-unit timing reference from committed records only.

Inputs are committed JSON records. No audio decoding, model import, inference, optimizer,
or network access is performed. The synthetic comparator reproduces the retained V8 L0
attack templates, then applies the prospective acoustic-attack-group contract.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable

from astra_backend.synthetic.v9_measurement_contract_v1 import (
    ContractError,
    group_acoustic_attacks,
    validate_group_times,
)

TOLERANCE_SECONDS = 0.010
REPEAT_THRESHOLD_SECONDS = 0.250
LONG_GAP_THRESHOLD_SECONDS = 0.700
ENDPOINT_POLICY = "half-open [0,duration)"
QUANTILE_CONVENTION = "linear interpolation at h=(n-1)*p (NumPy default linear convention)"
V8_RUNNER_BLOB_SHA = "3c7efea4ce00d737a9ed1bb2711185b7a5fb1955"

FAMILIES = ("isolated", "scales", "chords", "repeated", "legato", "palmmute", "mixed")
BASES_PER_FAMILY = 14
VARIANTS_PER_BASE = 3


def linear_quantile(values: Iterable[float], p: float) -> float | None:
    xs = sorted(float(x) for x in values)
    if not xs:
        return None
    if not (0.0 <= p <= 1.0):
        raise ContractError("quantile p must be in [0,1]")
    h = (len(xs) - 1) * p
    lo = math.floor(h)
    hi = math.ceil(h)
    return xs[lo] + (h - lo) * (xs[hi] - xs[lo])


def summarize_grouped_clips(rows: list[dict]) -> dict:
    all_iois: list[float] = []
    rates: list[float] = []
    group_total = 0
    note_total = 0
    seconds = 0.0
    for row in rows:
        duration = float(row["durationSeconds"])
        groups = list(row["attackGroups"])
        validate_group_times(groups, duration, include_endpoint=False)
        iois = [b - a for a, b in zip(groups, groups[1:])]
        if any(x <= 0 for x in iois):
            raise ContractError("group IOIs must be strictly positive")
        all_iois.extend(iois)
        rates.append(len(groups) / duration)
        group_total += len(groups)
        note_total += int(row.get("noteLabelCount", len(groups)))
        seconds += duration
    return {
        "clipCount": len(rows),
        "noteLabelCount": note_total,
        "attackGroupCount": group_total,
        "seconds": seconds,
        "aggregateAttackGroupsPerSecond": group_total / seconds if seconds else None,
        "clipRateP10": linear_quantile(rates, 0.10),
        "clipRateP50": linear_quantile(rates, 0.50),
        "clipRateP90": linear_quantile(rates, 0.90),
        "eligiblePositiveIoiCount": len(all_iois),
        "ioiP10Seconds": linear_quantile(all_iois, 0.10),
        "ioiP50Seconds": linear_quantile(all_iois, 0.50),
        "ioiP90Seconds": linear_quantile(all_iois, 0.90),
        "repeat250Fraction": (
            sum(x <= REPEAT_THRESHOLD_SECONDS for x in all_iois) / len(all_iois)
            if all_iois else None
        ),
        "longGap700Fraction": (
            sum(x >= LONG_GAP_THRESHOLD_SECONDS for x in all_iois) / len(all_iois)
            if all_iois else None
        ),
    }


def correction_map(correction_doc: dict) -> dict[str, float]:
    return {str(x["id"]): float(x["corrected"]) for x in correction_doc["corrections"]}


def v2b_rows(manifest: dict, annotations: dict, corrections: dict[str, float]) -> list[dict]:
    rows = []
    for clip in manifest["clips"]:
        if clip["kind"] != "positive":
            continue
        clip_id = clip["id"]
        duration = corrections.get(
            clip_id,
            float(clip["evaluationEndSeconds"]) - float(clip["evaluationStartSeconds"]),
        )
        raw = [float(x) for x in annotations["clips"][clip_id]["onsets"]]
        groups = group_acoustic_attacks(raw, TOLERANCE_SECONDS)
        rows.append(
            {
                "id": clip_id,
                "durationSeconds": duration,
                "rawLandmarkCount": len(raw),
                "attackGroups": groups,
                "noteLabelCount": len(groups),  # detector landmarks have no note-multiplicity truth
                "mergedWithinToleranceCount": len(raw) - len(groups),
            }
        )
    return rows


def base_attacks(family: str, base: int) -> tuple[list[float], bool]:
    if family == "isolated":
        return [0.32], False
    if family == "scales":
        return [0.22, 0.58, 0.94, 1.30], False
    if family == "chords":
        return [0.32, 0.32, 0.32, 1.08, 1.08, 1.08], False
    if family == "repeated":
        return [0.28, 0.68, 1.08, 1.48], False
    if family == "legato":
        return [0.28], False
    if family == "palmmute":
        return [0.28, 0.62, 0.96, 1.30, 1.64], False
    if family == "mixed":
        negative = (base % 2) == 0
        return ([] if negative else [0.36]), negative
    raise ContractError(f"unknown family {family}")


def v8_l0_rows() -> list[dict]:
    rows = []
    for family in FAMILIES:
        for base in range(BASES_PER_FAMILY):
            notes, negative = base_attacks(family, base)
            if negative:
                continue
            for variant in range(VARIANTS_PER_BASE):
                groups = group_acoustic_attacks(notes, TOLERANCE_SECONDS)
                rows.append(
                    {
                        "id": f"{family}:{base}:{variant}",
                        "family": family,
                        "durationSeconds": 2.0,
                        "noteLabelCount": len(notes),
                        "attackGroups": groups,
                        "mergedNoteMultiplicityCount": len(notes) - len(groups),
                    }
                )
    return rows


def per_clip(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        groups = row["attackGroups"]
        iois = [b - a for a, b in zip(groups, groups[1:])]
        out.append(
            {
                "id": row["id"],
                "durationSeconds": row["durationSeconds"],
                "rawLandmarkCount": row.get("rawLandmarkCount"),
                "attackGroupCount": len(groups),
                "mergedWithinToleranceCount": row.get("mergedWithinToleranceCount", 0),
                "attackGroupsPerSecond": len(groups) / row["durationSeconds"],
                "eligiblePositiveIoiCount": len(iois),
                "ioiP50Seconds": linear_quantile(iois, 0.50),
                "ioiP90Seconds": linear_quantile(iois, 0.90),
                "repeat250Fraction": (
                    sum(x <= REPEAT_THRESHOLD_SECONDS for x in iois) / len(iois)
                    if iois else None
                ),
                "longGap700Fraction": (
                    sum(x >= LONG_GAP_THRESHOLD_SECONDS for x in iois) / len(iois)
                    if iois else None
                ),
            }
        )
    return out


def per_family(rows: list[dict]) -> dict[str, dict]:
    return {family: summarize_grouped_clips([r for r in rows if r["family"] == family]) for family in FAMILIES}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--corrections", required=True)
    ap.add_argument("--annotations", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    corrections_doc = json.loads(Path(args.corrections).read_text())
    annotations = json.loads(Path(args.annotations).read_text())
    corrections = correction_map(corrections_doc)

    real_rows = v2b_rows(manifest, annotations, corrections)
    synthetic_rows = v8_l0_rows()
    v2b_summary = summarize_grouped_clips(real_rows)
    synthetic_summary = summarize_grouped_clips(synthetic_rows)

    negative_seconds = 0.0
    for clip in manifest["clips"]:
        if clip["kind"] == "negative-only":
            negative_seconds += corrections.get(
                clip["id"],
                float(clip["evaluationEndSeconds"]) - float(clip["evaluationStartSeconds"]),
            )

    out = {
        "schema": "astra-pre-v9-common-unit-measurement-v1",
        "contract": {
            "timingUnit": "acoustic-attack-group",
            "noteLabelUnitSeparate": True,
            "simultaneousToleranceSeconds": TOLERANCE_SECONDS,
            "cropOrigin": "evaluation-crop-local",
            "endpointPolicy": ENDPOINT_POLICY,
            "quantileConvention": QUANTILE_CONVENTION,
            "ioiDefinition": "positive difference between consecutive attack groups within one clip",
            "repeat250Definition": "fraction of eligible positive IOIs <=0.250 s",
            "longGap700Definition": "fraction of eligible positive IOIs >=0.700 s",
            "positiveDensityDenominator": "positive evaluation seconds only",
            "negativeDurationSeparate": True,
        },
        "v2b": {
            "summary": v2b_summary,
            "negativeSeconds": negative_seconds,
            "perClip": per_clip(real_rows),
            "qualification": (
                "Frozen spectral-flux landmarks; not exhaustive human-verified audible attacks. "
                "No note multiplicity is inferred from detector timestamps."
            ),
        },
        "syntheticV8L0": {
            "sourceRunnerBlobSha": V8_RUNNER_BLOB_SHA,
            "summary": synthetic_summary,
            "perFamily": per_family(synthetic_rows),
            "qualification": "V8 L0 source-template reconstruction under the new attack-group contract; historical V8 metrics remain unchanged.",
        },
        "comparison": {
            "densityDeltaSyntheticMinusV2b": synthetic_summary["aggregateAttackGroupsPerSecond"] - v2b_summary["aggregateAttackGroupsPerSecond"],
            "ioiP50DeltaSecondsSyntheticMinusV2b": synthetic_summary["ioiP50Seconds"] - v2b_summary["ioiP50Seconds"],
            "ioiP90DeltaSecondsSyntheticMinusV2b": synthetic_summary["ioiP90Seconds"] - v2b_summary["ioiP90Seconds"],
            "repeat250DeltaSyntheticMinusV2b": synthetic_summary["repeat250Fraction"] - v2b_summary["repeat250Fraction"],
            "longGap700DeltaSyntheticMinusV2b": synthetic_summary["longGap700Fraction"] - v2b_summary["longGap700Fraction"],
        },
        "execution": {
            "audioDecoded": False,
            "modelInferenceCount": 0,
            "optimizerSteps": 0,
            "candidateV9TimingPopulationGenerated": False,
        },
    }
    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
