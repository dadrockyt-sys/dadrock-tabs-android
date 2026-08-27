#!/usr/bin/env python3
"""Reference-free V154 CPU transcriber for broad Other + Bass stems.

This stage never reads professional references. It converts two already-separated
CPU stems into frozen note/onset streams for later scoring.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
from typing import Any

TEMPO_BPM = 129.19921875
STEPS_PER_BEAT = 4
STEPS_PER_MEASURE = 16
STEP_SECONDS = (60.0 / TEMPO_BPM) / STEPS_PER_BEAT
STREAM_RANGES = {
    "combinedGuitar": (40, 88),
    "bass": (28, 67),
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    h = hashlib.sha256()
    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = child.relative_to(path).as_posix().encode("utf-8")
        payload = child.read_bytes()
        h.update(len(rel).to_bytes(8, "big"))
        h.update(rel)
        h.update(len(payload).to_bytes(8, "big"))
        h.update(payload)
    return h.hexdigest()


def hz_for_midi(midi: int) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "tolist"):
        return json_safe(value.tolist())
    if hasattr(value, "item"):
        return json_safe(value.item())
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    raise TypeError(f"unsupported Basic Pitch metadata type: {type(value)!r}")


def grid_location(seconds: float) -> tuple[int, float, int]:
    absolute_step_float = seconds / STEP_SECONDS
    measure = int(math.floor(max(0.0, absolute_step_float) / STEPS_PER_MEASURE)) + 1
    step = absolute_step_float - (measure - 1) * STEPS_PER_MEASURE
    nearest_absolute_step = int(round(absolute_step_float))
    return measure, step, nearest_absolute_step


def transcribe_stream(audio: Path, stream: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if stream not in STREAM_RANGES:
        raise ValueError(stream)
    if not audio.is_file():
        raise FileNotFoundError(audio)

    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict

    package_version = importlib.metadata.version("basic-pitch")
    if package_version != "0.4.0":
        raise RuntimeError(f"Basic Pitch version mismatch: {package_version}")
    model_path = Path(ICASSP_2022_MODEL_PATH)
    minimum_midi, maximum_midi = STREAM_RANGES[stream]

    _model_output, _midi_data, note_events = predict(
        audio,
        model_or_model_path=model_path,
        onset_threshold=0.5,
        frame_threshold=0.3,
        minimum_note_length=127.7,
        minimum_frequency=hz_for_midi(minimum_midi),
        maximum_frequency=hz_for_midi(maximum_midi),
        multiple_pitch_bends=False,
        melodia_trick=True,
    )

    rows: list[dict[str, Any]] = []
    for source_index, note in enumerate(note_events):
        if len(note) < 4:
            raise RuntimeError(f"unexpected Basic Pitch note tuple: {note!r}")
        start = float(note[0])
        end = float(note[1])
        midi = int(round(float(note[2])))
        amplitude = float(note[3])
        pitch_bend = note[4] if len(note) > 4 else None
        if not (math.isfinite(start) and math.isfinite(end) and math.isfinite(amplitude)):
            raise RuntimeError("non-finite Basic Pitch note")
        if end < start:
            raise RuntimeError("Basic Pitch note ends before it starts")
        if not minimum_midi <= midi <= maximum_midi:
            raise RuntimeError(f"Basic Pitch emitted MIDI outside frozen {stream} range: {midi}")
        measure, step, nearest_absolute_step = grid_location(start)
        rows.append({
            "sourceIndex": source_index,
            "measure": measure,
            "step": step,
            "nearestAbsoluteStep": nearest_absolute_step,
            "midi": midi,
            "startSeconds": start,
            "endSeconds": end,
            "durationSeconds": end - start,
            "amplitude": amplitude,
            "pitchBend": json_safe(pitch_bend),
        })

    metadata = {
        "audioPath": str(audio),
        "audioBytes": audio.stat().st_size,
        "audioSha256": sha256_file(audio),
        "minimumMidi": minimum_midi,
        "maximumMidi": maximum_midi,
        "noteEventCount": len(rows),
        "basicPitchVersion": package_version,
        "modelPath": str(model_path),
        "modelSha256": sha256_path(model_path),
    }
    return rows, metadata


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--other", type=Path, required=True)
    ap.add_argument("--bass", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise RuntimeError(f"frozen output already exists: {args.output}")

    combined_guitar, guitar_meta = transcribe_stream(args.other, "combinedGuitar")
    bass, bass_meta = transcribe_stream(args.bass, "bass")
    payload = {
        "schema": "dadrock.tabs.v154.cpu-multitrack-generated.v1",
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "classification": "reference-free-broad-other-and-bass-cpu-transcription",
        "grid": {
            "tempoBpm": TEMPO_BPM,
            "stepsPerBeat": STEPS_PER_BEAT,
            "stepsPerMeasure": STEPS_PER_MEASURE,
            "stepDurationSeconds": STEP_SECONDS,
        },
        "streams": {
            "combinedGuitar": combined_guitar,
            "bass": bass,
        },
        "streamMetadata": {
            "combinedGuitar": guitar_meta,
            "bass": bass_meta,
        },
        "basicPitchSettings": {
            "onsetThreshold": 0.5,
            "frameThreshold": 0.3,
            "minimumNoteLengthMs": 127.7,
            "multiplePitchBends": False,
            "melodiaTrick": True,
            "thresholdSweep": False,
        },
        "safety": {
            "referenceRead": False,
            "humanCorrection": False,
            "referenceGuidedFiltering": False,
            "modalUsed": False,
            "cudaGpuUsed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "combinedGuitarNotes": len(combined_guitar),
        "bassNotes": len(bass),
        "referenceRead": False,
        "cudaGpuUsed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
