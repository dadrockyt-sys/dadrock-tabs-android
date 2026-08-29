#!/usr/bin/env python3
"""V167 self-repeat completion sweep.

Added events are inferred only from the generated candidate's own repeated measure
patterns. The professional reference is used solely to score fixed parameter
variants in this explicitly labeled single-song calibration lane.

No trial recursively feeds another: every parameter combination starts from the
same immutable Iteration 001 generated streams.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

THRESHOLDS = (0.50, 0.67, 0.75, 0.80, 0.90, 1.00)
MAX_ADDITIONS = (1, 2, 4, 8)
MIN_TARGET_EVENTS = (1, 2, 3)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_repeat_scorer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scorer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def key(note: Mapping[str, Any]) -> tuple[float, int]:
    return (float(note["step"]), int(note["midi"]))


def notes_by_measure(events: Sequence[Mapping[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for note in events:
        out[int(note["measure"])].append(
            {"measure": int(note["measure"]), "step": float(note["step"]), "midi": int(note["midi"])}
        )
    for rows in out.values():
        rows.sort(key=lambda n: (float(n["step"]), int(n["midi"])))
    return dict(out)


def counter(rows: Sequence[Mapping[str, Any]]) -> Counter:
    return Counter(key(row) for row in rows)


def overlap_count(a: Counter, b: Counter) -> int:
    return sum((a & b).values())


def extras_from_donor(target: Counter, donor: Counter) -> list[tuple[float, int]]:
    diff = donor - target
    out: list[tuple[float, int]] = []
    for event_key in sorted(diff):
        out.extend([event_key] * int(diff[event_key]))
    return out


def complete_stream(
    events: Sequence[Mapping[str, Any]],
    *,
    threshold: float,
    max_additions: int,
    min_target_events: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Complete close-superset repeated measures using generated data only."""
    original = [
        {"measure": int(n["measure"]), "step": float(n["step"]), "midi": int(n["midi"])}
        for n in events
    ]
    measures = notes_by_measure(original)
    counters = {m: counter(rows) for m, rows in measures.items()}
    additions: list[dict[str, Any]] = []
    changes: list[dict[str, Any]] = []

    for target_measure in sorted(measures):
        target_rows = measures[target_measure]
        target_count = len(target_rows)
        if target_count < min_target_events:
            continue
        target_counter = counters[target_measure]
        candidates = []
        for donor_measure in sorted(measures):
            if donor_measure == target_measure:
                continue
            donor_rows = measures[donor_measure]
            donor_count = len(donor_rows)
            if donor_count <= target_count:
                continue
            donor_counter = counters[donor_measure]
            overlap = overlap_count(target_counter, donor_counter)
            similarity = overlap / target_count if target_count else 0.0
            if similarity + 1e-12 < threshold:
                continue
            extras = extras_from_donor(target_counter, donor_counter)
            if not extras or len(extras) > max_additions:
                continue
            candidates.append(
                (
                    similarity,
                    overlap,
                    -len(extras),
                    -abs(donor_measure - target_measure),
                    -donor_measure,
                    donor_measure,
                    extras,
                )
            )
        if not candidates:
            continue
        candidates.sort(reverse=True)
        similarity, overlap, _, _, _, donor_measure, extras = candidates[0]
        added_rows = [
            {"measure": target_measure, "step": float(step), "midi": int(midi)}
            for step, midi in extras
        ]
        additions.extend(added_rows)
        changes.append(
            {
                "targetMeasure": target_measure,
                "donorMeasure": donor_measure,
                "targetEventCount": target_count,
                "donorEventCount": len(measures[donor_measure]),
                "overlapCount": overlap,
                "targetCoverageByDonor": similarity,
                "added": [{"step": row["step"], "midi": row["midi"]} for row in added_rows],
            }
        )

    completed = original + additions
    completed.sort(key=lambda n: (int(n["measure"]), float(n["step"]), int(n["midi"])))
    return completed, {
        "addedEvents": len(additions),
        "changedMeasures": len(changes),
        "changes": changes,
    }


def score(scorer, generated, reference):
    pairs = scorer.optimal_one_to_one_match(generated, reference, scorer.STEP_TOLERANCE)
    return scorer.prf(len(pairs), len(generated), len(reference))


def gross(scorer, generated, reference):
    pairs = scorer.optimal_one_to_one_match(generated, reference, scorer.GROSS_STEP_TOLERANCE)
    return scorer.prf(len(pairs), len(generated), len(reference))


def sweep_stream(scorer, events, reference):
    baseline = score(scorer, events, reference)
    variants = []
    for threshold in THRESHOLDS:
        for max_additions in MAX_ADDITIONS:
            for min_target in MIN_TARGET_EVENTS:
                completed, metadata = complete_stream(
                    events,
                    threshold=threshold,
                    max_additions=max_additions,
                    min_target_events=min_target,
                )
                primary = score(scorer, completed, reference)
                variants.append(
                    {
                        "threshold": threshold,
                        "maxAdditionsPerMeasure": max_additions,
                        "minTargetEvents": min_target,
                        "primary": primary,
                        "addedEvents": metadata["addedEvents"],
                        "changedMeasures": metadata["changedMeasures"],
                    }
                )
    improving = [v for v in variants if float(v["primary"]["f1"]) > float(baseline["f1"]) + 1e-15]
    if improving:
        selected = max(
            improving,
            key=lambda v: (
                float(v["primary"]["f1"]),
                int(v["primary"]["matched"]),
                -int(v["addedEvents"]),
                float(v["threshold"]),
                -int(v["maxAdditionsPerMeasure"]),
                int(v["minTargetEvents"]),
            ),
        )
        completed, metadata = complete_stream(
            events,
            threshold=float(selected["threshold"]),
            max_additions=int(selected["maxAdditionsPerMeasure"]),
            min_target_events=int(selected["minTargetEvents"]),
        )
        selected = dict(selected)
        selected["gross"] = gross(scorer, completed, reference)
        selected["recognitionPercent"] = float(selected["primary"]["f1"]) * 100.0
        selected["deltaRecognitionPercent"] = (float(selected["primary"]["f1"]) - float(baseline["f1"])) * 100.0
        selected["detailedChanges"] = metadata["changes"]
    else:
        selected = {
            "useBaseline": True,
            "primary": baseline,
            "recognitionPercent": float(baseline["f1"]) * 100.0,
            "deltaRecognitionPercent": 0.0,
            "addedEvents": 0,
            "changedMeasures": 0,
            "detailedChanges": [],
        }
    return {"baseline": baseline, "selected": selected, "variants": variants}


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
    ref_guitar, ref_bass, reference_counts = scorer.load_reference(reference_payload)

    guitar_sweep = sweep_stream(scorer, guitar, ref_guitar)
    bass_sweep = sweep_stream(scorer, bass, ref_bass)

    report = {
        "schema": "dadrock.tabs.v167.self-repeat-completion-sweep.v1",
        "version": "V167",
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "parameters": {
            "thresholds": list(THRESHOLDS),
            "maxAdditionsPerMeasure": list(MAX_ADDITIONS),
            "minTargetEvents": list(MIN_TARGET_EVENTS),
            "donorSource": "same generated stream, another generated measure only",
            "recursivePropagation": False,
        },
        "referenceCounts": reference_counts,
        "combinedGuitar": guitar_sweep,
        "bass": bass_sweep,
        "policy": {
            "referenceFacing": True,
            "calibrationOnly": True,
            "referenceUsedOnlyToScoreFixedVariants": True,
            "addedEventsDerivedFromReference": False,
            "addedEventsDerivedOnlyFromGeneratedDonorMeasures": True,
            "directReferenceCopy": False,
            "generalizationClaim": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({
        "combinedGuitar": report["combinedGuitar"]["selected"],
        "bass": report["bass"]["selected"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
