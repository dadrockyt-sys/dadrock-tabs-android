#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile

from onset_birth_corroboration_v6 import SAMPLE_RATE, _synth_events

ROOT = Path(__file__).resolve().parents[2]
QUALIFIER = ROOT / "scripts" / "songsterr-fresh" / "qualify_basic_pitch_note_births_v1.py"
IDENTITY_SHA = "b" * 64


def model_payload(notes: list[dict]) -> dict:
    return {
        "contract": "songsterr-fresh-basic-pitch-isolated-guitar-v1",
        "version": 1,
        "referenceBlind": True,
        "role": "guitar",
        "notes": notes,
        "noteInferenceIdentity": {
            "contract": "songsterr-fresh-basic-pitch-note-identity-v1",
            "version": 1,
            "algorithm": "sha256",
            "eventCount": len(notes),
            "sha256": IDENTITY_SHA,
        },
        "diagnostics": {"modelNoteEndsUsedAsDuration": False},
        "provenance": {
            "modelInvoked": True,
            "gpuInvoked": False,
            "modelValidationComplete": False,
            "separationSource": "synthetic-isolated-guitar-fixture",
            "audioSource": "synthetic-unit-test",
        },
    }


def note(note_id: str, start: float, midi: int, confidence: float) -> dict:
    return {
        "noteId": note_id,
        "startSeconds": start,
        "diagnosticModelEndSeconds": start + 0.2,
        "midi": midi,
        "confidence": confidence,
    }


def write_pcm16(path: Path, audio: np.ndarray) -> None:
    peak = max(1.0, float(np.max(np.abs(audio))) / 0.95)
    clipped = np.clip(audio / peak, -1.0, 1.0)
    wavfile.write(path, SAMPLE_RATE, np.round(clipped * 32767.0).astype(np.int16))


def run_qualifier(root: Path, label: str, audio: np.ndarray, notes: list[dict]) -> dict:
    wav_path = root / f"{label}.wav"
    model_path = root / f"{label}-model.json"
    output_path = root / f"{label}-qualification.json"
    write_pcm16(wav_path, audio)
    model_path.write_text(json.dumps(model_payload(notes), indent=2) + "\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(QUALIFIER),
            "--audio",
            str(wav_path),
            "--model-notes",
            str(model_path),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"{label} qualifier failed: {result.stderr}\n{result.stdout}")
    return json.loads(output_path.read_text(encoding="utf-8"))


def assert_statuses(payload: dict, expected: list[str]) -> None:
    actual = [row["status"] for row in payload["proposals"]]
    if actual != expected:
        raise AssertionError(f"statuses changed: actual={actual} expected={expected}\npayload={json.dumps(payload, indent=2)}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="songsterr-dsp-qualifier-v1-") as tmp:
        root = Path(tmp)

        # Case 1: a real E2 birth followed by a proposal at its fifth harmonic
        # while the original E2 is already sustaining. The harmonic proposal
        # must not be promoted as a new note birth.
        audio, _rng = _synth_events(
            1.6,
            [{
                "onsetSeconds": 0.25,
                "stopSeconds": 1.5,
                "midi": 40,
                "amplitude": 0.8,
                "decayPerSecond": 0.35,
            }],
            seed=17,
        )
        baseline_notes = [
            note("proposal-e2", 0.25, 40, 0.79),
            note("proposal-fifth-harmonic", 0.65, 68, 0.35),
        ]
        baseline = run_qualifier(root, "baseline", audio, baseline_notes)
        assert_statuses(baseline, ["corroborated", "rejected"])
        assert baseline["candidateConfidenceUsedForDecision"] is False
        assert baseline["independentOfBasicPitchCandidateConfidence"] is True
        assert baseline["proposals"][1]["provenance"]["candidateConfidenceReadForDecision"] is False

        # Case 2: invert Basic Pitch confidences. Independent DSP qualification
        # must remain identical.
        flipped_notes = [
            note("proposal-e2", 0.25, 40, 0.01),
            note("proposal-fifth-harmonic", 0.65, 68, 0.99),
        ]
        flipped = run_qualifier(root, "confidence-flipped", audio, flipped_notes)
        assert_statuses(flipped, ["corroborated", "rejected"])
        assert [row["status"] for row in flipped["proposals"]] == [row["status"] for row in baseline["proposals"]]

        # Case 3: near-left-boundary birth. The wrapper must provide
        # deterministic pre-context padding and reach an actual finite DSP
        # decision rather than fail for missing left frames. The fixed DSP is
        # allowed to corroborate or reject; boundary padding itself must not
        # force a positive decision.
        boundary_audio, _rng = _synth_events(
            1.0,
            [{
                "onsetSeconds": 0.011,
                "stopSeconds": 0.9,
                "midi": 45,
                "amplitude": 0.8,
                "decayPerSecond": 0.45,
            }],
            seed=23,
        )
        boundary = run_qualifier(
            root,
            "left-boundary",
            boundary_audio,
            [note("proposal-left-boundary", 0.011, 45, 0.4)],
        )
        boundary_row = boundary["proposals"][0]
        assert boundary_row["status"] in {"corroborated", "rejected"}
        assert boundary_row["status"] != "insufficient"
        assert boundary_row["provenance"]["leftBoundaryZeroPaddingSamples"] > 0
        assert boundary_row["provenance"]["v6Reason"] not in {
            "INSUFFICIENT_PRECONTEXT",
            "INSUFFICIENT_FRAME_CONTEXT",
        }

        # Case 4: insufficient right-edge context must remain unresolved. The
        # wrapper is not allowed to invent future audio by right-padding.
        right_edge = run_qualifier(
            root,
            "right-edge",
            audio,
            [note("proposal-right-edge", 1.59, 40, 0.99)],
        )
        assert_statuses(right_edge, ["insufficient"])

        print(json.dumps({
            "contract": "songsterr-fresh-independent-note-birth-qualifier-v1-test",
            "status": "PASS",
            "cases": 4,
            "baselineStatuses": [row["status"] for row in baseline["proposals"]],
            "confidenceInvariant": True,
            "leftBoundaryPaddingValidated": True,
            "leftBoundaryDecision": boundary_row["status"],
            "rightBoundaryFailsClosed": True,
            "modelInferenceInvoked": False,
            "realCorpusEvaluated": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
        }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
