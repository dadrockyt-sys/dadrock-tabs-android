#!/usr/bin/env python3
"""V167 fixed global step-selection rule sweep.

Every admitted Iteration 001 event retains exactly three audio-derived lattice
candidates under stepSelection.candidates. This calibration sweep applies a small
predeclared set of deterministic whole-stream rules to those stored candidates.
The professional reference is used only to score each complete global rule; it
never selects an individual event's lattice choice.

Iteration 001 already applied a shared -12 global phase correction to final event
coordinates while leaving nested candidate.step values in the pre-correction
absolute lattice. Therefore any nested choice selected here is converted with:

    corrected_absolute_step = candidate.step - 12

MIDI values and stream cardinality are immutable throughout the sweep.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

STEPS_PER_MEASURE = 16
GLOBAL_PHASE_CORRECTION = -12


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_step_rule_scorer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scorer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compact_event(event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "measure": int(event["measure"]),
        "step": float(event["step"]),
        "midi": int(event["midi"]),
    }


def candidate_value(candidate: Mapping[str, Any], rule: str) -> float:
    score = float(candidate["score"])
    instrument = float(candidate["instrumentSupport"])
    shared = float(candidate["sharedSupport"])
    if rule == "max_score":
        return score
    if rule == "max_instrument_support":
        return instrument
    if rule == "max_shared_support":
        return shared
    if rule == "max_score_x_instrument":
        return score * instrument
    if rule == "max_score_x_shared":
        return score * shared
    if rule == "weighted_score50_instrument50":
        return 0.50 * score + 0.50 * instrument
    if rule == "weighted_score50_shared50":
        return 0.50 * score + 0.50 * shared
    if rule == "weighted_score50_instrument25_shared25":
        return 0.50 * score + 0.25 * instrument + 0.25 * shared
    if rule == "weighted_score60_instrument20_shared20":
        return 0.60 * score + 0.20 * instrument + 0.20 * shared
    raise ValueError(f"unknown rule: {rule}")


RULES = (
    "baseline",
    "max_score",
    "max_instrument_support",
    "max_shared_support",
    "max_score_x_instrument",
    "max_score_x_shared",
    "weighted_score50_instrument50",
    "weighted_score50_shared50",
    "weighted_score50_instrument25_shared25",
    "weighted_score60_instrument20_shared20",
)


def choose_candidate(event: Mapping[str, Any], rule: str) -> Mapping[str, Any] | None:
    if rule == "baseline":
        return None
    selection = event.get("stepSelection")
    if not isinstance(selection, Mapping):
        raise ValueError("event missing stepSelection")
    candidates = selection.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 3:
        raise ValueError("event must have exactly three stepSelection candidates")

    valid: list[Mapping[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            raise ValueError("stepSelection candidate is not an object")
        corrected = int(candidate["step"]) + GLOBAL_PHASE_CORRECTION
        if corrected >= 0:
            valid.append(candidate)
    if not valid:
        return None

    # Deterministic tie-breaking never consults the reference. Prefer the rule
    # value, then raw audio score/support, then closeness to the event's stored
    # nearest lattice step, then the earlier absolute step.
    nearest = int(event.get("nearestLatticeStep", valid[0]["step"]))
    return max(
        valid,
        key=lambda candidate: (
            candidate_value(candidate, rule),
            float(candidate["score"]),
            float(candidate["instrumentSupport"]),
            float(candidate["sharedSupport"]),
            -abs(int(candidate["step"]) - nearest),
            -int(candidate["step"]),
        ),
    )


def apply_rule(events: Sequence[Mapping[str, Any]], rule: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    transformed: list[dict[str, Any]] = []
    changed = 0
    fallback = 0
    displacement_histogram: dict[str, int] = {}

    for event in events:
        baseline = compact_event(event)
        candidate = choose_candidate(event, rule)
        if candidate is None:
            transformed.append(baseline)
            if rule != "baseline":
                fallback += 1
            continue

        corrected_abs = int(candidate["step"]) + GLOBAL_PHASE_CORRECTION
        new_event = {
            "measure": corrected_abs // STEPS_PER_MEASURE + 1,
            "step": float(corrected_abs % STEPS_PER_MEASURE),
            "midi": int(event["midi"]),
        }
        old_abs = (int(event["measure"]) - 1) * STEPS_PER_MEASURE + int(float(event["step"]))
        displacement = corrected_abs - old_abs
        displacement_histogram[str(displacement)] = displacement_histogram.get(str(displacement), 0) + 1
        if displacement != 0:
            changed += 1
        transformed.append(new_event)

    if len(transformed) != len(events):
        raise AssertionError("stream cardinality changed")
    if [int(e["midi"]) for e in transformed] != [int(e["midi"]) for e in events]:
        raise AssertionError("MIDI sequence changed")

    return transformed, {
        "changedEvents": changed,
        "fallbackToBaselineEvents": fallback,
        "displacementHistogramGridSteps": dict(sorted(displacement_histogram.items(), key=lambda kv: int(kv[0]))),
    }


def score(scorer, generated, reference):
    pairs = scorer.optimal_one_to_one_match(generated, reference, scorer.STEP_TOLERANCE)
    return scorer.prf(len(pairs), len(generated), len(reference))


def gross(scorer, generated, reference):
    pairs = scorer.optimal_one_to_one_match(generated, reference, scorer.GROSS_STEP_TOLERANCE)
    return scorer.prf(len(pairs), len(generated), len(reference))


def sweep_stream(scorer, events, reference):
    baseline_events, baseline_metadata = apply_rule(events, "baseline")
    baseline_primary = score(scorer, baseline_events, reference)
    variants = []

    for rule in RULES:
        transformed, metadata = apply_rule(events, rule)
        primary = score(scorer, transformed, reference)
        variants.append({
            "rule": rule,
            "primary": primary,
            "gross": gross(scorer, transformed, reference),
            **metadata,
        })

    selected = max(
        variants,
        key=lambda variant: (
            float(variant["primary"]["f1"]),
            int(variant["primary"]["matched"]),
            -int(variant["changedEvents"]),
            -RULES.index(str(variant["rule"])),
        ),
    )
    selected = dict(selected)
    selected["recognitionPercent"] = float(selected["primary"]["f1"]) * 100.0
    selected["deltaRecognitionPercent"] = (
        float(selected["primary"]["f1"]) - float(baseline_primary["f1"])
    ) * 100.0

    return {
        "baseline": {
            "primary": baseline_primary,
            "gross": gross(scorer, baseline_events, reference),
            **baseline_metadata,
        },
        "selected": selected,
        "variants": variants,
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
    generated_payload = json.loads(args.candidate.read_text(encoding="utf-8"))
    reference_payload = scorer.load_json(args.reference)
    ref_guitar, ref_bass, reference_counts = scorer.load_reference(reference_payload)

    if generated_payload.get("version") != "V167":
        raise ValueError("candidate must be V167")
    calibration = generated_payload.get("calibration") or {}
    if calibration.get("iteration") != 1:
        raise ValueError("candidate must be frozen Iteration 001")
    transform = calibration.get("transform") or {}
    if int(transform.get("shiftGridSteps")) != GLOBAL_PHASE_CORRECTION:
        raise ValueError("candidate global phase correction is not -12")

    streams = generated_payload.get("streams") or {}
    guitar = streams.get("combinedGuitar")
    bass = streams.get("bass")
    if not isinstance(guitar, list) or not isinstance(bass, list):
        raise ValueError("candidate missing scored streams")
    if len(guitar) != 1050 or len(bass) != 402:
        raise ValueError("unexpected frozen Iteration 001 cardinality")

    guitar_sweep = sweep_stream(scorer, guitar, ref_guitar)
    bass_sweep = sweep_stream(scorer, bass, ref_bass)

    report = {
        "schema": "dadrock.tabs.v167.global-step-selection-rule-sweep.v1",
        "version": "V167",
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "rules": list(RULES),
        "coordinateRule": {
            "storedCandidateStepLattice": "pre-V167-global-phase absolute step",
            "globalPhaseCorrectionGridSteps": GLOBAL_PHASE_CORRECTION,
            "correctedAbsoluteStepFormula": "candidate.step - 12",
            "stepsPerMeasure": STEPS_PER_MEASURE,
        },
        "referenceCounts": reference_counts,
        "combinedGuitar": guitar_sweep,
        "bass": bass_sweep,
        "invariants": {
            "combinedGuitarEventCount": len(guitar),
            "bassEventCount": len(bass),
            "eventCountsUnchanged": True,
            "midiSequencesUnchanged": True,
        },
        "policy": {
            "referenceFacing": True,
            "calibrationOnly": True,
            "referenceUsedOnlyToScoreWholeGlobalRules": True,
            "referenceUsedToChooseIndividualEventAlternatives": False,
            "eventAlternativesDerivedOnlyFromStoredCandidateAudioEvidence": True,
            "directReferenceCopy": False,
            "generalizationClaim": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "combinedGuitar": report["combinedGuitar"]["selected"],
        "bass": report["bass"]["selected"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
