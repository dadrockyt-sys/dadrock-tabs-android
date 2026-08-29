#!/usr/bin/env python3
"""V167 fixed whole-stream Bass pitch-rule calibration sweep.

Every alternative MIDI comes only from audio-derived evidence already stored on
frozen Iteration 002 Bass events (`stateMidi` and `medianPyinMidi`). Timing and
event cardinality are preserved exactly. The professional reference grades only
complete predeclared rules; it never selects an individual event's MIDI.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

VOICED_THRESHOLDS = (0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85)
DELTA_THRESHOLDS = (3, 5, 7, 9, 11)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_bass_pitch_scorer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scorer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rounded_pyin(event: Mapping[str, Any]) -> int | None:
    value = event.get("medianPyinMidi")
    if value is None:
        return None
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(x):
        return None
    return int(round(x))


def state_midi(event: Mapping[str, Any]) -> int | None:
    value = event.get("stateMidi")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def state_confidence(event: Mapping[str, Any]) -> float:
    try:
        x = float(event.get("stateVoicedProbability", 0.0))
    except (TypeError, ValueError):
        return 0.0
    return x if math.isfinite(x) else 0.0


def pyin_confidence(event: Mapping[str, Any]) -> float:
    try:
        x = float(event.get("medianPyinVoicedProbability", 0.0))
    except (TypeError, ValueError):
        return 0.0
    return x if math.isfinite(x) else 0.0


def build_rules() -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = [
        {"name": "baseline_current", "kind": "baseline"},
        {"name": "state_all", "kind": "state_all"},
        {"name": "pyin_round_all", "kind": "pyin_all"},
    ]
    for threshold in VOICED_THRESHOLDS:
        tag = int(round(threshold * 100))
        rules.extend([
            {"name": f"state_if_state_voiced_ge_{tag}", "kind": "state_if_conf", "threshold": threshold},
            {"name": f"pyin_if_pyin_voiced_ge_{tag}", "kind": "pyin_if_conf", "threshold": threshold},
            {"name": f"lower_state_if_state_voiced_ge_{tag}", "kind": "lower_state_if_conf", "threshold": threshold},
        ])
    for delta in DELTA_THRESHOLDS:
        for threshold in (0.55, 0.65, 0.75, 0.85):
            tag = int(round(threshold * 100))
            rules.append({
                "name": f"state_if_current_above_state_by_{delta}_and_voiced_ge_{tag}",
                "kind": "state_if_downward_delta",
                "delta": delta,
                "threshold": threshold,
            })
    return rules


RULES = build_rules()


def choose_midi(event: Mapping[str, Any], rule: Mapping[str, Any]) -> int:
    current = int(event["midi"])
    state = state_midi(event)
    pyin = rounded_pyin(event)
    kind = str(rule["kind"])
    if kind == "baseline":
        return current
    if kind == "state_all":
        return current if state is None else state
    if kind == "pyin_all":
        return current if pyin is None else pyin
    if kind == "state_if_conf":
        return state if state is not None and state_confidence(event) + 1e-12 >= float(rule["threshold"]) else current
    if kind == "pyin_if_conf":
        return pyin if pyin is not None and pyin_confidence(event) + 1e-12 >= float(rule["threshold"]) else current
    if kind == "lower_state_if_conf":
        return state if state is not None and state < current and state_confidence(event) + 1e-12 >= float(rule["threshold"]) else current
    if kind == "state_if_downward_delta":
        return state if (
            state is not None
            and current - state >= int(rule["delta"])
            and state_confidence(event) + 1e-12 >= float(rule["threshold"])
        ) else current
    raise KeyError(kind)


def apply_rule(events: Sequence[Mapping[str, Any]], rule: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out: list[dict[str, Any]] = []
    changed = 0
    delta_hist: dict[str, int] = {}
    changed_examples: list[dict[str, Any]] = []
    for event in events:
        current = int(event["midi"])
        chosen = choose_midi(event, rule)
        if not 0 <= chosen <= 127:
            raise RuntimeError(f"invalid chosen MIDI {chosen}")
        delta = chosen - current
        delta_hist[str(delta)] = delta_hist.get(str(delta), 0) + 1
        if delta != 0:
            changed += 1
            if len(changed_examples) < 25:
                changed_examples.append({
                    "measure": int(event["measure"]),
                    "step": float(event["step"]),
                    "currentMidi": current,
                    "chosenMidi": chosen,
                    "stateMidi": state_midi(event),
                    "medianPyinMidi": event.get("medianPyinMidi"),
                    "stateVoicedProbability": state_confidence(event),
                    "medianPyinVoicedProbability": pyin_confidence(event),
                })
        out.append({
            "measure": int(event["measure"]),
            "step": float(event["step"]),
            "midi": chosen,
        })
    if len(out) != len(events):
        raise AssertionError("event cardinality changed")
    return out, {
        "changedMidiEvents": changed,
        "deltaMidiHistogram": dict(sorted(delta_hist.items(), key=lambda item: int(item[0]))),
        "changedExamples": changed_examples,
    }


def score(scorer, generated, reference, tolerance: float):
    pairs = scorer.optimal_one_to_one_match(generated, reference, tolerance)
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
    payload = scorer.load_json(args.candidate)
    reference_payload = scorer.load_json(args.reference)
    _, normalized_bass = scorer.load_generated(payload)
    _, ref_bass, reference_counts = scorer.load_reference(reference_payload)
    raw_bass = (payload.get("streams") or {}).get("bass")
    if not isinstance(raw_bass, list) or len(raw_bass) != len(normalized_bass):
        raise ValueError("Iteration 002 Bass stream unavailable or contains excluded events")

    rows: list[dict[str, Any]] = []
    for rule in RULES:
        generated, metadata = apply_rule(raw_bass, rule)
        primary = score(scorer, generated, ref_bass, scorer.STEP_TOLERANCE)
        gross = score(scorer, generated, ref_bass, scorer.GROSS_STEP_TOLERANCE)
        rows.append({"rule": rule, "primary": primary, "gross": gross, **metadata})

    baseline = next(row for row in rows if row["rule"]["name"] == "baseline_current")
    best = max(
        rows,
        key=lambda row: (
            float(row["primary"]["f1"]),
            int(row["primary"]["matched"]),
            -int(row["changedMidiEvents"]),
            -RULES.index(row["rule"]),
        ),
    )
    report = {
        "schema": "dadrock.tabs.v167.fixed-bass-audio-evidence-pitch-rule-sweep.v1",
        "version": "V167",
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "referenceCounts": reference_counts,
        "rules": RULES,
        "baseline": baseline,
        "best": best,
        "deltaRecognitionPercent": (float(best["primary"]["f1"]) - float(baseline["primary"]["f1"])) * 100.0,
        "rows": rows,
        "policy": {
            "referenceFacing": True,
            "calibrationOnly": True,
            "referenceSelectsWholeRuleOnly": True,
            "referenceSelectsIndividualEventMidi": False,
            "candidateFileModified": False,
            "timingModified": False,
            "eventCardinalityModified": False,
            "alternativeMidiDerivedOnlyFromStoredAudioEvidence": True,
            "directReferenceCopy": False,
            "generalizationClaim": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({
        "baselinePercent": float(baseline["primary"]["f1"]) * 100.0,
        "best": best,
        "deltaPercent": report["deltaRecognitionPercent"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
