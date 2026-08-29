#!/usr/bin/env python3
"""Apply V167 Calibration Iteration 002 from the sealed step-rule sweep.

This transform is reference-blind. It reads the immutable Iteration 001 candidate,
the frozen step-rule sweep report, and the exact frozen rule implementation. It
applies the sweep-selected whole-stream rule to each instrument, preserves MIDI
and event cardinality, and records the chosen audio-evidence lattice alternative
without rewriting the nested source evidence.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping

STEPS_PER_MEASURE = 16
GLOBAL_PHASE_CORRECTION = -12
EXPECTED_RULES = {
    "combinedGuitar": "max_score_x_shared",
    "bass": "max_score_x_mean_support",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rule_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_frozen_step_rules", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen rule module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transform_stream(events: list[dict[str, Any]], stream: str, rule: str, rule_module) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out: list[dict[str, Any]] = []
    moved = 0
    fallback = 0
    histogram: dict[str, int] = {}
    before_midis = [int(event["midi"]) for event in events]

    for event in events:
        clone = copy.deepcopy(event)
        prior_abs = int(event["absoluteGridStep"])
        invariant_abs = (int(event["measure"]) - 1) * STEPS_PER_MEASURE + int(round(float(event["step"])))
        if invariant_abs != prior_abs:
            raise ValueError(f"{stream} coordinate invariant failed before transform: {prior_abs} != {invariant_abs}")

        selected = rule_module.select_candidate(rule, event)
        if selected is None:
            fallback += 1
            corrected_abs = prior_abs
            stored_abs = None
            selected_snapshot = None
        else:
            stored_abs = int(round(float(selected["step"])))
            corrected_abs = stored_abs + GLOBAL_PHASE_CORRECTION
            if corrected_abs < 0:
                fallback += 1
                corrected_abs = prior_abs
                selected_snapshot = None
            else:
                selected_snapshot = {
                    "storedAbsoluteStep": stored_abs,
                    "time": float(selected.get("time", 0.0)),
                    "score": float(selected.get("score", 0.0)),
                    "instrumentSupport": float(selected.get("instrumentSupport", 0.0)),
                    "sharedSupport": float(selected.get("sharedSupport", 0.0)),
                }

        delta = corrected_abs - prior_abs
        histogram[str(delta)] = histogram.get(str(delta), 0) + 1
        if delta != 0:
            moved += 1

        clone["absoluteGridStep"] = corrected_abs
        clone["measure"] = corrected_abs // STEPS_PER_MEASURE + 1
        clone["step"] = corrected_abs % STEPS_PER_MEASURE
        clone["v167StepCalibration"] = {
            "iteration": 2,
            "rule": rule,
            "globalPhaseCorrectionGridSteps": GLOBAL_PHASE_CORRECTION,
            "priorAbsoluteGridStep": prior_abs,
            "correctedAbsoluteGridStep": corrected_abs,
            "deltaGridSteps": delta,
            "selectedStoredCandidate": selected_snapshot,
            "sourceEvidenceRewritten": False,
            "professionalReferenceReadByTransform": False,
        }
        out.append(clone)

    after_midis = [int(event["midi"]) for event in out]
    if before_midis != after_midis:
        raise AssertionError(f"{stream} MIDI sequence changed")
    if len(out) != len(events):
        raise AssertionError(f"{stream} event cardinality changed")
    for event in out:
        absolute = int(event["absoluteGridStep"])
        if (int(event["measure"]) - 1) * STEPS_PER_MEASURE + int(event["step"]) != absolute:
            raise AssertionError(f"{stream} coordinate invariant failed after transform")

    return out, {
        "rule": rule,
        "eventCount": len(out),
        "movedEvents": moved,
        "fallbackEvents": fallback,
        "deltaGridStepHistogram": dict(sorted(histogram.items(), key=lambda item: int(item[0]))),
        "midiChanged": False,
        "eventCardinalityChanged": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--sweep", type=Path, required=True)
    ap.add_argument("--rule-code", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--input-blob", required=True)
    ap.add_argument("--sweep-blob", required=True)
    ap.add_argument("--rule-code-blob", required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise RuntimeError(f"output already exists: {args.output}")

    source = json.loads(args.input.read_text(encoding="utf-8"))
    sweep = json.loads(args.sweep.read_text(encoding="utf-8"))
    if source.get("version") != "V167" or int((source.get("calibration") or {}).get("iteration", -1)) != 1:
        raise ValueError("Iteration 002 input must be frozen V167 Iteration 001")
    if sweep.get("schema") != "dadrock.tabs.v167.fixed-global-step-selection-rule-sweep.v1":
        raise ValueError("unexpected sweep schema")
    if int(sweep.get("globalPhaseCorrectionGridSteps")) != GLOBAL_PHASE_CORRECTION:
        raise ValueError("sweep global phase mismatch")
    for stream, expected_rule in EXPECTED_RULES.items():
        if str(sweep[stream]["best"]["rule"]) != expected_rule:
            raise ValueError(f"sealed best rule mismatch for {stream}")

    safety = source.get("safety") or {}
    if safety.get("referenceRead") is not False or safety.get("humanCorrection") is not False:
        raise ValueError("source safety flags are not scorer-compatible")

    rule_module = load_rule_module(args.rule_code)
    output = copy.deepcopy(source)
    streams = output.get("streams")
    if not isinstance(streams, dict):
        raise ValueError("source missing streams")

    summaries: dict[str, Any] = {}
    for stream, rule in EXPECTED_RULES.items():
        raw = streams.get(stream)
        if not isinstance(raw, list):
            raise ValueError(f"source missing {stream}")
        transformed, summary = transform_stream(raw, stream, rule, rule_module)
        streams[stream] = transformed
        summaries[stream] = summary

    prior_calibration = copy.deepcopy(source.get("calibration"))
    output["schema"] = "dadrock.tabs.v167.single-song-calibrated-generated.v2"
    output["version"] = "V167"
    output["status"] = "CALIBRATION_ITERATION_002_AUDIO_EVIDENCE_STEP_RULES_APPLIED"
    output["calibration"] = {
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "iteration": 2,
        "parentVersion": "V167",
        "parentIteration": 1,
        "parentCandidateGitBlob": args.input_blob,
        "parentCandidateSha256": sha256(args.input),
        "stepRuleSweepGitBlob": args.sweep_blob,
        "stepRuleCodeGitBlob": args.rule_code_blob,
        "globalPhaseCorrectionGridSteps": GLOBAL_PHASE_CORRECTION,
        "selectedRules": EXPECTED_RULES,
        "streamSummaries": summaries,
        "priorCalibration": prior_calibration,
        "professionalReferenceReadByTransform": False,
        "directReferenceEventCopy": False,
        "humanCorrection": False,
        "midiChanged": False,
        "scoredEventCardinalityChanged": False,
        "generalizationClaim": False,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "selectedRules": EXPECTED_RULES,
        "streamSummaries": summaries,
        "outputSha256": sha256(args.output),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
