#!/usr/bin/env python3
"""V167 read-only shared section timing diagnostic.

Starting from frozen calibration Iteration 001, partition the song into fixed
8-measure blocks. For each block, shift *both* generated Guitar and Bass events
whose pre-shift onset belongs to that block by one shared integer offset in
[-3,+3]. Select the block offset that maximizes total primary matches across the
same frozen Guitar+Bass scorer, with deterministic conservative tie-breaking.

The professional reference is used only to evaluate the fixed parameter grid.
No candidate file is modified and no reference event is copied into generated
output. This is explicitly single-song calibration, not holdout evaluation.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

STEPS_PER_MEASURE = 16
BLOCK_MEASURES = 8
MIN_SHIFT = -3
MAX_SHIFT = 3


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_block_phase_scorer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scorer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def move_note(note: Mapping[str, Any], shift: int) -> dict[str, Any] | None:
    absolute = (int(note["measure"]) - 1) * STEPS_PER_MEASURE + int(float(note["step"]))
    moved = absolute + shift
    if moved < 0:
        return None
    return {"measure": moved // STEPS_PER_MEASURE + 1, "step": moved % STEPS_PER_MEASURE, "midi": int(note["midi"])}


def shift_block(
    events: Sequence[Mapping[str, Any]],
    *,
    start_measure: int,
    end_measure: int,
    shift: int,
) -> list[dict[str, Any]] | None:
    out: list[dict[str, Any]] = []
    for note in events:
        measure = int(note["measure"])
        if start_measure <= measure <= end_measure:
            moved = move_note(note, shift)
            if moved is None:
                return None
            out.append(moved)
        else:
            out.append({"measure": measure, "step": float(note["step"]), "midi": int(note["midi"])})
    return out


def apply_map(
    events: Sequence[Mapping[str, Any]],
    block_map: Sequence[Mapping[str, int]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for note in events:
        measure = int(note["measure"])
        shift = 0
        for block in block_map:
            if int(block["startMeasure"]) <= measure <= int(block["endMeasure"]):
                shift = int(block["selectedShiftGridSteps"])
                break
        moved = move_note(note, shift)
        if moved is None:
            raise ValueError("selected block map produced negative absolute grid step")
        out.append(moved)
    return out


def prf_for(scorer, generated, reference):
    pairs = scorer.optimal_one_to_one_match(generated, reference, scorer.STEP_TOLERANCE)
    return scorer.prf(len(pairs), len(generated), len(reference))


def gross_for(scorer, generated, reference):
    pairs = scorer.optimal_one_to_one_match(generated, reference, scorer.GROSS_STEP_TOLERANCE)
    return scorer.prf(len(pairs), len(generated), len(reference))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--scorer", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise RuntimeError(f"output already exists: {args.output}")

    scorer = load_module(args.scorer)
    generated_payload = scorer.load_json(args.candidate)
    reference_payload = scorer.load_json(args.reference)
    guitar, bass = scorer.load_generated(generated_payload)
    ref_guitar, ref_bass, ref_counts = scorer.load_reference(reference_payload)

    baseline_g = prf_for(scorer, guitar, ref_guitar)
    baseline_b = prf_for(scorer, bass, ref_bass)
    baseline_total = int(baseline_g["matched"]) + int(baseline_b["matched"])
    max_measure = max(
        [int(n["measure"]) for n in guitar + bass + ref_guitar + ref_bass],
        default=1,
    )

    blocks = []
    for start in range(1, max_measure + 1, BLOCK_MEASURES):
        end = min(max_measure, start + BLOCK_MEASURES - 1)
        rows = []
        for shift in range(MIN_SHIFT, MAX_SHIFT + 1):
            shifted_g = shift_block(guitar, start_measure=start, end_measure=end, shift=shift)
            shifted_b = shift_block(bass, start_measure=start, end_measure=end, shift=shift)
            if shifted_g is None or shifted_b is None:
                rows.append({"shiftGridSteps": shift, "valid": False})
                continue
            g = prf_for(scorer, shifted_g, ref_guitar)
            b = prf_for(scorer, shifted_b, ref_bass)
            total = int(g["matched"]) + int(b["matched"])
            rows.append({
                "shiftGridSteps": shift,
                "valid": True,
                "jointPrimaryMatched": total,
                "deltaJointPrimaryMatchedVsIteration001": total - baseline_total,
                "combinedGuitar": g,
                "bass": b,
            })
        valid_rows = [r for r in rows if r.get("valid")]
        if not valid_rows:
            raise RuntimeError(f"no valid shifts for block {start}-{end}")
        best = max(
            valid_rows,
            key=lambda row: (
                int(row["jointPrimaryMatched"]),
                -abs(int(row["shiftGridSteps"])),
                -int(row["shiftGridSteps"]),
            ),
        )
        blocks.append({
            "startMeasure": start,
            "endMeasure": end,
            "selectedShiftGridSteps": int(best["shiftGridSteps"]),
            "selectedJointPrimaryMatchedWhenTestedAlone": int(best["jointPrimaryMatched"]),
            "selectedDeltaJointPrimaryMatchedWhenTestedAlone": int(best["deltaJointPrimaryMatchedVsIteration001"]),
            "rows": rows,
        })

    projected_guitar = apply_map(guitar, blocks)
    projected_bass = apply_map(bass, blocks)
    projected_g = prf_for(scorer, projected_guitar, ref_guitar)
    projected_b = prf_for(scorer, projected_bass, ref_bass)
    projected_gross_g = gross_for(scorer, projected_guitar, ref_guitar)
    projected_gross_b = gross_for(scorer, projected_bass, ref_bass)
    nonzero = [
        {
            "startMeasure": b["startMeasure"],
            "endMeasure": b["endMeasure"],
            "shiftGridSteps": b["selectedShiftGridSteps"],
            "isolatedDeltaMatches": b["selectedDeltaJointPrimaryMatchedWhenTestedAlone"],
        }
        for b in blocks if int(b["selectedShiftGridSteps"]) != 0
    ]

    report = {
        "schema": "dadrock.tabs.v167.shared-eight-measure-block-phase-sweep.v1",
        "version": "V167",
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "parameters": {
            "blockMeasures": BLOCK_MEASURES,
            "additionalShiftMin": MIN_SHIFT,
            "additionalShiftMax": MAX_SHIFT,
            "stepsPerMeasure": STEPS_PER_MEASURE,
            "sharedShiftAcrossGuitarAndBass": True,
            "objective": "maximize total primary matched events across combinedGuitar+bass",
            "tieBreak": "smaller absolute shift, then earlier/negative shift",
        },
        "referenceCounts": ref_counts,
        "iteration001Baseline": {
            "combinedGuitar": baseline_g,
            "bass": baseline_b,
            "jointPrimaryMatched": baseline_total,
        },
        "blocks": blocks,
        "selectedNonzeroBlocks": nonzero,
        "projectedCombinedMap": {
            "combinedGuitar": projected_g,
            "bass": projected_b,
            "combinedGuitarGross": projected_gross_g,
            "bassGross": projected_gross_b,
            "jointPrimaryMatched": int(projected_g["matched"]) + int(projected_b["matched"]),
            "deltaJointPrimaryMatchedVsIteration001": int(projected_g["matched"]) + int(projected_b["matched"]) - baseline_total,
            "recognitionPercent": {
                "combinedGuitar": float(projected_g["f1"]) * 100.0,
                "bass": float(projected_b["f1"]) * 100.0,
            },
        },
        "policy": {
            "referenceFacing": True,
            "calibrationOnly": True,
            "candidateFileModified": False,
            "midiModified": False,
            "eventByEventReferenceMove": False,
            "fixedBlockPartition": True,
            "directReferenceCopy": False,
            "generalizationClaim": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({
        "baselineJointMatches": baseline_total,
        "nonzeroBlocks": nonzero,
        "projected": report["projectedCombinedMap"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
