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
QUALIFIER = ROOT / "scripts" / "songsterr-fresh" / "qualify_basic_pitch_note_births_v2.py"
IDENTITY_SHA = "c" * 64


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
        "diagnosticModelEndSeconds": start + 0.25,
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


def statuses(payload: dict) -> list[str]:
    return [row["status"] for row in payload["proposals"]]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="songsterr-dsp-qualifier-v2-") as tmp:
        root = Path(tmp)

        # 1. Normal in-clip path remains unchanged: true E2 birth corroborates,
        # later fifth-harmonic-area proposal rejects.
        normal_audio, _rng = _synth_events(
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
        normal_notes = [
            note("normal-e2", 0.25, 40, 0.79),
            note("normal-harmonic", 0.65, 68, 0.35),
        ]
        normal = run_qualifier(root, "normal", normal_audio, normal_notes)
        assert statuses(normal) == ["corroborated", "rejected"], json.dumps(normal, indent=2)
        assert all(row["provenance"]["qualificationMode"] == "normal-in-clip-onset-birth" for row in normal["proposals"])

        # 2. Basic Pitch confidence remains diagnostic-only.
        flipped = run_qualifier(
            root,
            "confidence-flipped",
            normal_audio,
            [
                note("normal-e2", 0.25, 40, 0.01),
                note("normal-harmonic", 0.65, 68, 0.99),
            ],
        )
        assert statuses(flipped) == statuses(normal)
        assert flipped["candidateConfidenceUsedForDecision"] is False
        assert flipped["independentOfBasicPitchCandidateConfidence"] is True

        # 3. Genuine clip-start single notes across several MIDI values must be
        # recoverable without fabricated pre-context.
        boundary_true_midis = [40, 45, 52, 68]
        boundary_true_statuses = {}
        for midi in boundary_true_midis:
            audio, _rng = _synth_events(
                1.0,
                [{
                    "onsetSeconds": 0.011,
                    "stopSeconds": 0.9,
                    "midi": midi,
                    "amplitude": 0.8,
                    "decayPerSecond": 0.45,
                }],
                seed=100 + midi,
            )
            result = run_qualifier(
                root,
                f"boundary-true-{midi}",
                audio,
                [note(f"boundary-true-{midi}", 0.011, midi, 0.4)],
            )
            assert statuses(result) == ["corroborated"], json.dumps(result, indent=2)
            row = result["proposals"][0]
            assert row["provenance"]["qualificationMode"] == "clip-start-one-sided-pitch-presence"
            assert row["provenance"]["leftBoundaryZeroPaddingSamples"] == 0
            assert row["provenance"]["syntheticPreContextUsed"] is False
            boundary_true_statuses[str(midi)] = row["status"]

        # 4. On clip-start E2 audio, E2 corroborates while its octave and
        # fifth-harmonic-area aliases reject.
        boundary_e2, _rng = _synth_events(
            1.0,
            [{
                "onsetSeconds": 0.011,
                "stopSeconds": 0.9,
                "midi": 40,
                "amplitude": 0.8,
                "decayPerSecond": 0.45,
            }],
            seed=211,
        )
        alias_result = run_qualifier(
            root,
            "boundary-aliases",
            boundary_e2,
            [
                note("boundary-e2", 0.011, 40, 0.2),
                note("boundary-octave-alias", 0.011, 52, 0.9),
                note("boundary-fifth-alias", 0.011, 68, 0.99),
            ],
        )
        assert statuses(alias_result) == ["corroborated", "rejected", "rejected"], json.dumps(alias_result, indent=2)
        fifth_owner_rows = alias_result["proposals"][2]["provenance"].get("harmonicOwners") or []
        assert any(row.get("lowerMidi") == 40 and row.get("dominant") is True for row in fifth_owner_rows)

        # 5. Harmonic relationship alone may not erase a genuine second note.
        # With both E2 and G#4 genuinely present and the selected G#4 having
        # greater independent necessity than its lower harmonic owner, both
        # proposals corroborate.
        poly_audio, _rng = _synth_events(
            1.0,
            [
                {
                    "onsetSeconds": 0.011,
                    "stopSeconds": 0.9,
                    "midi": 40,
                    "amplitude": 0.4,
                    "decayPerSecond": 0.45,
                    "phase": 0.17,
                },
                {
                    "onsetSeconds": 0.011,
                    "stopSeconds": 0.9,
                    "midi": 68,
                    "amplitude": 0.8,
                    "decayPerSecond": 0.45,
                    "phase": 0.39,
                },
            ],
            seed=313,
        )
        poly = run_qualifier(
            root,
            "boundary-real-polyphony",
            poly_audio,
            [note("poly-e2", 0.011, 40, 0.1), note("poly-gsharp4", 0.011, 68, 0.9)],
        )
        assert statuses(poly) == ["corroborated", "corroborated"], json.dumps(poly, indent=2)

        # 6. Noise-only clip-start evidence must not corroborate a pitch.
        rng = np.random.default_rng(404)
        noise_audio = 0.02 * rng.standard_normal(int(round(1.0 * SAMPLE_RATE)))
        noise = run_qualifier(root, "boundary-noise", noise_audio, [note("noise", 0.011, 52, 0.5)])
        assert statuses(noise)[0] != "corroborated", json.dumps(noise, indent=2)

        # 7. Clip-start mode never invents missing future audio.
        short_audio, _rng = _synth_events(
            0.15,
            [{
                "onsetSeconds": 0.011,
                "stopSeconds": 0.14,
                "midi": 45,
                "amplitude": 0.8,
                "decayPerSecond": 0.45,
            }],
            seed=515,
        )
        short = run_qualifier(root, "boundary-short", short_audio, [note("short", 0.011, 45, 0.4)])
        assert statuses(short) == ["insufficient"], json.dumps(short, indent=2)

        # 8. Normal right-edge missing context still fails closed.
        right_edge = run_qualifier(root, "normal-right-edge", normal_audio, [note("right-edge", 1.59, 40, 0.99)])
        assert statuses(right_edge) == ["insufficient"], json.dumps(right_edge, indent=2)

        print(json.dumps({
            "contract": "songsterr-fresh-independent-note-qualification-v2-test",
            "status": "PASS",
            "cases": 8,
            "normalStatuses": statuses(normal),
            "confidenceInvariant": True,
            "boundaryTrueStatuses": boundary_true_statuses,
            "boundaryAliasStatuses": statuses(alias_result),
            "boundaryPolyphonyStatuses": statuses(poly),
            "noiseDidNotCorroborate": True,
            "missingPostContextInsufficient": True,
            "syntheticPreContextUsed": False,
            "modelInferenceInvoked": False,
            "realCorpusEvaluated": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
        }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
