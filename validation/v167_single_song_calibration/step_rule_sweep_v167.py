#!/usr/bin/env python3
"""V167 fixed global step-selection-rule sweep.

Each admitted event already stores three audio-derived absolute-lattice candidates.
Iteration 001 moved the final event coordinates by the proven shared -12 phase,
while the nested stepSelection candidates intentionally remain on the original
lattice. This diagnostic applies one deterministic selection rule to a complete
instrument stream, subtracts 12 from the selected stored absolute step, preserves
MIDI and event cardinality, and scores the resulting whole-stream variant.

The professional reference grades only complete predeclared rules. It never
chooses an individual event's lattice alternative.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

STEPS_PER_MEASURE = 16
GLOBAL_PHASE_CORRECTION = -12


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_step_rule_scorer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scorer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def f(row: Mapping[str, Any], key: str) -> float:
    value = row.get(key, 0.0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def rule_value(name: str, row: Mapping[str, Any]) -> float:
    score = f(row, "score")
    inst = f(row, "instrumentSupport")
    shared = f(row, "sharedSupport")
    if name == "max_score":
        return score
    if name == "max_instrument_support":
        return inst
    if name == "max_shared_support":
        return shared
    if name == "max_score_x_instrument":
        return score * inst
    if name == "max_score_x_shared":
        return score * shared
    if name == "max_score_x_mean_support":
        return score * (inst + shared) / 2.0
    if name == "max_score_x_inst75_shared25":
        return score * (0.75 * inst + 0.25 * shared)
    if name == "max_score_x_inst25_shared75":
        return score * (0.25 * inst + 0.75 * shared)
    if name == "max_mean_score_instrument":
        return (score + inst) / 2.0
    if name == "max_mean_score_shared":
        return (score + shared) / 2.0
    raise KeyError(name)


RULES = (
    "baseline_current",
    "max_score",
    "max_instrument_support",
    "max_shared_support",
    "max_score_x_instrument",
    "max_score_x_shared",
    "max_score_x_mean_support",
    "max_score_x_inst75_shared25",
    "max_score_x_inst25_shared75",
    "max_mean_score_instrument",
    "max_mean_score_shared",
)


def baseline_note(event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "measure": int(event["measure"]),
        "step": float(event["step"]),
        "midi": int(event["midi"]),
    }


def select_candidate(rule: str, event: Mapping[str, Any]) -> Mapping[str, Any] | None:
    step_selection = event.get("stepSelection")
    if not isinstance(step_selection, Mapping):
        return None
    candidates = step_selection.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return None

    # Deterministic tie-break: higher rule value, then higher native score,
    # then higher instrument/shared support, then closer to frozen pre-correction
    # nearest lattice, then earlier absolute step.
    nearest = float(event.get("nearestLatticeStep", event.get("absoluteGridStep", 0) - GLOBAL_PHASE_CORRECTION))
    ranked = []
    for index, row in enumerate(candidates):
        if not isinstance(row, Mapping) or "step" not in row:
            continue
        step = float(row["step"])
        ranked.append((
            rule_value(rule, row),
            f(row, "score"),
            f(row, "instrumentSupport"),
            f(row, "sharedSupport"),
            -abs(step - nearest),
            -step,
            -index,
            row,
        ))
    if not ranked:
        return None
    ranked.sort(reverse=True, key=lambda item: item[:-1])
    return ranked[0][-1]


def apply_rule(events: Sequence[Mapping[str, Any]], rule: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if rule == "baseline_current":
        return [baseline_note(event) for event in events], {
            "movedEvents": 0,
            "fallbackEvents": 0,
            "deltaGridStepHistogram": {"0": len(events)},
            "meanAbsGridDelta": 0.0,
            "maxAbsGridDelta": 0.0,
        }

    out: list[dict[str, Any]] = []
    moved = 0
    fallback = 0
    deltas: list[int] = []
    histogram: dict[str, int] = {}
    for event in events:
        current_abs = (int(event["measure"]) - 1) * STEPS_PER_MEASURE + int(round(float(event["step"])))
        selected = select_candidate(rule, event)
        if selected is None:
            fallback += 1
            new_abs = current_abs
        else:
            stored_abs = int(round(float(selected["step"])))
            corrected_abs = stored_abs + GLOBAL_PHASE_CORRECTION
            if corrected_abs < 0:
                fallback += 1
                new_abs = current_abs
            else:
                new_abs = corrected_abs
        delta = new_abs - current_abs
        deltas.append(delta)
        histogram[str(delta)] = histogram.get(str(delta), 0) + 1
        if delta != 0:
            moved += 1
        out.append({
            "measure": new_abs // STEPS_PER_MEASURE + 1,
            "step": float(new_abs % STEPS_PER_MEASURE),
            "midi": int(event["midi"]),
        })
    if len(out) != len(events):
        raise AssertionError("event cardinality changed")
    return out, {
        "movedEvents": moved,
        "fallbackEvents": fallback,
        "deltaGridStepHistogram": dict(sorted(histogram.items(), key=lambda kv: int(kv[0]))),
        "meanAbsGridDelta": sum(abs(d) for d in deltas) / len(deltas) if deltas else 0.0,
        "maxAbsGridDelta": max((abs(d) for d in deltas), default=0),
    }


def score(scorer, generated, reference, tolerance: float):
    pairs = scorer.optimal_one_to_one_match(generated, reference, tolerance)
    return scorer.prf(len(pairs), len(generated), len(reference))


def sweep_stream(scorer, raw_events, reference):
    rows = []
    for rule in RULES:
        generated, metadata = apply_rule(raw_events, rule)
        primary = score(scorer, generated, reference, scorer.STEP_TOLERANCE)
        gross = score(scorer, generated, reference, scorer.GROSS_STEP_TOLERANCE)
        rows.append({
            "rule": rule,
            "primary": primary,
            "gross": gross,
            **metadata,
        })
    baseline = next(row for row in rows if row["rule"] == "baseline_current")
    best = max(
        rows,
        key=lambda row: (
            float(row["primary"]["f1"]),
            int(row["primary"]["matched"]),
            -int(row["movedEvents"]),
            -float(row["meanAbsGridDelta"]),
            -RULES.index(row["rule"]),
        ),
    )
    return {
        "baseline": baseline,
        "best": best,
        "deltaRecognitionPercent": (float(best["primary"]["f1"]) - float(baseline["primary"]["f1"])) * 100.0,
        "rows": rows,
    }


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
    payload = scorer.load_json(args.candidate)
    reference_payload = scorer.load_json(args.reference)
    normalized_guitar, normalized_bass = scorer.load_generated(payload)
    ref_guitar, ref_bass, reference_counts = scorer.load_reference(reference_payload)

    streams = payload.get("streams") or {}
    raw_guitar = streams.get("combinedGuitar")
    raw_bass = streams.get("bass")
    if not isinstance(raw_guitar, list) or not isinstance(raw_bass, list):
        raise ValueError("candidate missing raw scored streams")
    if len(raw_guitar) != len(normalized_guitar) or len(raw_bass) != len(normalized_bass):
        raise ValueError("unexpected excluded scored event in Iteration 001")

    report = {
        "schema": "dadrock.tabs.v167.fixed-global-step-selection-rule-sweep.v1",
        "version": "V167",
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "globalPhaseCorrectionGridSteps": GLOBAL_PHASE_CORRECTION,
        "stepsPerMeasure": STEPS_PER_MEASURE,
        "rules": list(RULES),
        "referenceCounts": reference_counts,
        "combinedGuitar": sweep_stream(scorer, raw_guitar, ref_guitar),
        "bass": sweep_stream(scorer, raw_bass, ref_bass),
        "policy": {
            "referenceFacing": True,
            "calibrationOnly": True,
            "referenceSelectsWholeRuleOnly": True,
            "referenceSelectsIndividualEventAlternative": False,
            "candidateFileModified": False,
            "midiModified": False,
            "eventCardinalityModified": False,
            "alternativesDerivedFromStoredAudioEvidence": True,
            "directReferenceCopy": False,
            "generalizationClaim": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({
        "combinedGuitar": {
            "baselinePercent": report["combinedGuitar"]["baseline"]["primary"]["f1"] * 100.0,
            "best": report["combinedGuitar"]["best"],
            "deltaPercent": report["combinedGuitar"]["deltaRecognitionPercent"],
        },
        "bass": {
            "baselinePercent": report["bass"]["baseline"]["primary"]["f1"] * 100.0,
            "best": report["bass"]["best"],
            "deltaPercent": report["bass"]["deltaRecognitionPercent"],
        },
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
