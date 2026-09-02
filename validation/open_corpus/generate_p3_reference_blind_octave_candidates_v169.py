#!/usr/bin/env python3
"""Audio-only P3 candidate generation for the preregistered V169 bridge.

IMPORTANT: This process accepts audio only. It must run after the P3 source ZIP
has been removed from the candidate workspace and before any reference MIDI is
extracted. It generates a frozen Basic Pitch baseline plus a pitch-only stream
corrected by the already-frozen V2 harmonic octave selector.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from basic_pitch import ICASSP_2022_MODEL_PATH
from basic_pitch.inference import Model, predict

from analyze_guitar_techs_harmonic_octave_v169 import load_mono_audio
from evaluate_harmonic_candidate_ranking_v2_v169 import best_candidate_window

EXPECTED_MODEL_SHA256 = "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"
EXPECTED_V2_BLOB = "95e1e7d20a4bb5b15962cb803fa2da4d065743ae"
EXPECTED_HELPER_BLOB = "c39305df4f875bf6aec0d5e9d5b6448a5f7404df"

BASIC_PITCH_CONFIG = {
    "version": "0.4.0",
    "onsetThreshold": 0.5,
    "frameThreshold": 0.3,
    "minimumNoteLengthMs": 127.70,
    "minimumFrequency": None,
    "maximumFrequency": None,
    "multiplePitchBends": False,
    "melodiaTrick": True,
    "midiTempo": 120.0,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_number(value: Any) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return int(value)
    return float(value)


def normalized_basic_pitch_events(note_events: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in note_events:
        start, end, pitch, amplitude = raw[:4]
        rows.append(
            {
                "start": float(start),
                "end": float(end),
                "pitch": int(pitch),
                "amplitude": float(amplitude),
            }
        )
    rows.sort(key=lambda row: (row["start"], row["end"], row["pitch"], row["amplitude"]))
    for event_id, row in enumerate(rows):
        row["eventId"] = event_id
    return rows


def correct_events(
    audio,
    sample_rate: int,
    baseline_events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int, int]:
    corrected: list[dict[str, Any]] = []
    changed = 0
    boundary_unscored = 0

    for event in baseline_events:
        pitch = int(event["pitch"])
        candidates = (pitch - 12, pitch, pitch + 12)
        features: dict[int, dict[str, Any]] = {}
        for candidate_pitch in candidates:
            row = best_candidate_window(
                audio,
                sample_rate,
                float(event["start"]),
                0.0,
                candidate_pitch,
            )
            if row is None:
                features = {}
                break
            features[candidate_pitch] = row

        if len(features) == 3:
            winner = sorted(candidates, key=lambda value: (-float(features[value]["score"]), value))[0]
        else:
            # Prospectively frozen boundary behavior: when no valid analysis
            # window exists, preserve the Basic Pitch proposal unchanged.
            winner = pitch
            boundary_unscored += 1

        if winner != pitch:
            changed += 1
        corrected.append(
            {
                "eventId": int(event["eventId"]),
                "start": float(event["start"]),
                "end": float(event["end"]),
                "pitch": int(winner),
                "amplitude": float(event["amplitude"]),
            }
        )

    return corrected, changed, boundary_unscored


def discover_audio(audio_root: Path) -> list[tuple[str, str, Path]]:
    rows: list[tuple[str, str, Path]] = []
    for capture, prefix in (("directInput", "directinput"), ("micAmp", "micamp")):
        for index in range(1, 13):
            suffix = f"{index:02d}"
            path = audio_root / f"{prefix}_{suffix}.wav"
            if not path.is_file():
                raise RuntimeError(f"missing expected audio file: {path}")
            rows.append((capture, suffix, path))
    extras = sorted(path.name for path in audio_root.glob("*.wav") if path.is_file())
    expected = sorted(path.name for _, _, path in rows)
    if extras != expected:
        raise RuntimeError(f"unexpected audio inventory: expected={expected!r} actual={extras!r}")
    return rows


def self_test() -> dict[str, Any]:
    fake = [
        (0.20, 0.50, 45, 0.75, None),
        (0.10, 0.30, 40, 0.50, None),
    ]
    normalized = normalized_basic_pitch_events(fake)
    if [row["pitch"] for row in normalized] != [40, 45]:
        raise RuntimeError("event normalization/sort self-test failed")
    if [row["eventId"] for row in normalized] != [0, 1]:
        raise RuntimeError("event ID self-test failed")
    return {
        "status": "P3_CANDIDATE_WRAPPER_SELF_TEST_PASS",
        "audioOnlyCli": True,
        "referenceRead": False,
        "v168ReferenceFacingScoreCalls": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.audio_root is None or args.output_dir is None:
        raise SystemExit("--audio-root and --output-dir are required")

    model_path = Path(ICASSP_2022_MODEL_PATH)
    model_sha = sha256_file(model_path)
    if model_sha != EXPECTED_MODEL_SHA256:
        raise RuntimeError(f"Basic Pitch model SHA256 mismatch: {model_sha}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model = Model(model_path)
    file_receipts: list[dict[str, Any]] = []
    total_baseline_events = 0
    total_changed = 0
    total_boundary_unscored = 0

    for capture, index, audio_path in discover_audio(args.audio_root):
        _, _, note_events = predict(
            audio_path,
            model_or_model_path=model,
            onset_threshold=0.5,
            frame_threshold=0.3,
            minimum_note_length=127.70,
            minimum_frequency=None,
            maximum_frequency=None,
            multiple_pitch_bends=False,
            melodia_trick=True,
            midi_tempo=120.0,
        )
        baseline = normalized_basic_pitch_events(note_events)
        audio, sample_rate = load_mono_audio(audio_path)
        corrected, changed, boundary_unscored = correct_events(audio, sample_rate, baseline)
        if len(baseline) != len(corrected):
            raise RuntimeError("event-count identity violated inside candidate generator")

        payload = {
            "schema": "dadrock.tabs.open-corpus.p3-reference-blind-octave-candidate.v1",
            "dataset": "Guitar-TECHS",
            "player": "P3",
            "workIndex": index,
            "capture": capture,
            "sourceAudioFile": audio_path.name,
            "sourceAudioSha256": sha256_file(audio_path),
            "basicPitch": {
                **BASIC_PITCH_CONFIG,
                "modelSha256": model_sha,
            },
            "v2": {
                "evaluatorGitBlob": EXPECTED_V2_BLOB,
                "helperGitBlob": EXPECTED_HELPER_BLOB,
                "candidateOffsetsSemitones": [-12, 0, 12],
                "alignmentSeconds": 0.0,
                "tieBreak": "smallest-midi",
                "boundaryNoWindowBehavior": "preserve-basic-pitch",
            },
            "baselineEventCount": len(baseline),
            "correctedEventCount": len(corrected),
            "changedPitchCount": changed,
            "boundaryUnscoredCount": boundary_unscored,
            "baselineEvents": baseline,
            "correctedEvents": corrected,
            "referenceRead": False,
            "v168ReferenceFacingScoreCalls": 0,
            "v168PoliciesModified": False,
            "goatHoldoutSelectionModified": False,
        }
        filename = f"{capture}-{index}.json"
        output_path = args.output_dir / filename
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        receipt = {
            "file": filename,
            "sha256": sha256_file(output_path),
            "capture": capture,
            "workIndex": index,
            "baselineEventCount": len(baseline),
            "correctedEventCount": len(corrected),
            "changedPitchCount": changed,
            "boundaryUnscoredCount": boundary_unscored,
        }
        file_receipts.append(receipt)
        total_baseline_events += len(baseline)
        total_changed += changed
        total_boundary_unscored += boundary_unscored
        print(json.dumps({"candidateFrozen": receipt}, sort_keys=True), flush=True)

    manifest = {
        "schema": "dadrock.tabs.open-corpus.p3-reference-blind-octave-freeze-manifest.v1",
        "dataset": "Guitar-TECHS",
        "player": "P3",
        "workIndices": [f"{index:02d}" for index in range(1, 13)],
        "captures": ["directInput", "micAmp"],
        "candidateFileCount": len(file_receipts),
        "files": sorted(file_receipts, key=lambda row: (row["capture"], row["workIndex"])),
        "totalBaselineEventCount": total_baseline_events,
        "totalCorrectedEventCount": total_baseline_events,
        "totalChangedPitchCount": total_changed,
        "totalBoundaryUnscoredCount": total_boundary_unscored,
        "basicPitch": {**BASIC_PITCH_CONFIG, "modelSha256": model_sha},
        "v2": {
            "evaluatorGitBlob": EXPECTED_V2_BLOB,
            "helperGitBlob": EXPECTED_HELPER_BLOB,
            "candidateOffsetsSemitones": [-12, 0, 12],
            "alignmentSeconds": 0.0,
        },
        "referenceRead": False,
        "v168ReferenceFacingScoreCalls": 0,
        "v168PoliciesModified": False,
        "goatHoldoutSelectionModified": False,
    }
    manifest_path = args.output_dir / "candidate-freeze-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "P3_REFERENCE_BLIND_CANDIDATES_FROZEN",
        "candidateFileCount": len(file_receipts),
        "totalBaselineEventCount": total_baseline_events,
        "totalChangedPitchCount": total_changed,
        "totalBoundaryUnscoredCount": total_boundary_unscored,
        "freezeManifestSha256": sha256_file(manifest_path),
        "referenceRead": False,
        "v168ReferenceFacingScoreCalls": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
