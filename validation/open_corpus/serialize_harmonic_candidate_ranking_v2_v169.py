#!/usr/bin/env python3
"""Serialization-only recovery adapter for the frozen V2 candidate ranker.

This file MUST NOT implement or modify candidate scoring. It imports the frozen
V2 evaluator and only converts NumPy scalar/container values to ordinary Python
objects after the evaluator has returned its result.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_harmonic_candidate_ranking_v2_v169 import evaluate_capture
from analyze_guitar_techs_harmonic_octave_v169 import load_mono_audio, load_notes


def clean_json_value(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return [clean_json_value(item) for item in value.tolist()]
    if isinstance(value, dict):
        return {str(key): clean_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json_value(item) for item in value]
    return value


def serializer_self_test() -> dict[str, Any]:
    fixture = {
        "int64": np.int64(7),
        "float32": np.float32(0.25),
        "bool": np.bool_(True),
        "array": np.asarray([1, 2, 3], dtype=np.int64),
        "nested": {"value": np.float64(1.5)},
    }
    cleaned = clean_json_value(fixture)
    encoded = json.dumps(cleaned, sort_keys=True)
    decoded = json.loads(encoded)
    expected = {
        "array": [1, 2, 3],
        "bool": True,
        "float32": 0.25,
        "int64": 7,
        "nested": {"value": 1.5},
    }
    if decoded != expected:
        raise RuntimeError(f"serializer self-test mismatch: {decoded!r}")
    return {
        "status": "SERIALIZER_SELF_TEST_PASS",
        "scoringImplementationImported": "evaluate_harmonic_candidate_ranking_v2_v169.evaluate_capture",
        "candidateScoringModified": False,
        "v168ReferenceFacingScoreCalls": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--midi", type=Path)
    parser.add_argument("--audio", type=Path)
    parser.add_argument("--capture-label")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(serializer_self_test(), indent=2, sort_keys=True))
        return 0
    if not all((args.midi, args.audio, args.capture_label, args.output)):
        raise SystemExit("--midi --audio --capture-label --output are required")

    notes, instruments = load_notes(args.midi)
    audio, sample_rate = load_mono_audio(args.audio)
    report = {
        "schema": "dadrock.tabs.open-corpus.harmonic-candidate-ranking.v2",
        "captureLabel": args.capture_label,
        "candidateOffsetsSemitones": [-12, 0, 12],
        "tieBreak": "smallest-midi",
        "scoreFormula": "C/(1+0.50*L/(C+eps)); Q=(E/M)^0.25",
        "midiNoteCount": len(notes),
        "midiInstruments": instruments,
        "result": evaluate_capture(audio, sample_rate, notes),
        "serializationRecovery": True,
        "candidateScoringModified": False,
        "v168ReferenceFacingScoreCalls": 0,
        "v168PoliciesModified": False,
        "goatHoldoutSelectionModified": False,
    }
    cleaned = clean_json_value(report)
    payload = json.dumps(cleaned, indent=2, sort_keys=True) + "\n"
    args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
