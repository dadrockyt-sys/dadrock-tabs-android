from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

app = modal.App("dadrock-jimmy-paige-training-worker")
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("basic-pitch")
)


def _normalize(event: Any) -> dict[str, Any] | None:
    if isinstance(event, dict):
        start = event.get("start_time", event.get("start", 0.0))
        end = event.get("end_time", event.get("end", start))
        pitch = event.get("pitch_midi", event.get("midi_pitch", event.get("midiPitch", event.get("pitch"))))
        confidence = event.get("amplitude", event.get("confidence", 0.0))
    elif isinstance(event, (list, tuple)) and len(event) >= 3:
        start, end, pitch = event[0], event[1], event[2]
        confidence = event[3] if len(event) >= 4 else 0.0
    else:
        return None

    try:
        return {
            "start": float(start),
            "end": float(end),
            "midiPitch": int(pitch),
            "confidence": float(confidence or 0.0),
        }
    except (TypeError, ValueError):
        return None


def _run(audio_bytes: bytes, parameters: dict[str, Any]) -> bytes:
    from basic_pitch.inference import predict

    started = time.time()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        path = Path(handle.name)
        handle.write(audio_bytes)

    try:
        _, _, raw_events = predict(
            path,
            onset_threshold=float(parameters["onset_threshold"]),
            frame_threshold=float(parameters["frame_threshold"]),
            minimum_note_length=float(parameters["minimum_note_length"]),
            minimum_frequency=parameters.get("minimum_frequency"),
            maximum_frequency=parameters.get("maximum_frequency"),
            multiple_pitch_bends=False,
            melodia_trick=True,
        )
        events = []
        for event in raw_events:
            normalized = _normalize(event)
            if normalized is not None:
                events.append(normalized)
        return json.dumps({
            "events": events,
            "remoteElapsedSeconds": round(time.time() - started, 3),
        }).encode("utf-8")
    finally:
        path.unlink(missing_ok=True)


@app.function(image=image, timeout=900, memory=4096, scaledown_window=600)
def default(audio_bytes: bytes) -> bytes:
    return _run(audio_bytes, {"onset_threshold": 0.50, "frame_threshold": 0.30, "minimum_note_length": 127.7})


@app.function(image=image, timeout=900, memory=4096, scaledown_window=600)
def lower_onset(audio_bytes: bytes) -> bytes:
    return _run(audio_bytes, {"onset_threshold": 0.40, "frame_threshold": 0.30, "minimum_note_length": 127.7})


@app.function(image=image, timeout=900, memory=4096, scaledown_window=600)
def lower_frame(audio_bytes: bytes) -> bytes:
    return _run(audio_bytes, {"onset_threshold": 0.50, "frame_threshold": 0.22, "minimum_note_length": 127.7})


@app.function(image=image, timeout=900, memory=4096, scaledown_window=600)
def sensitive_balanced(audio_bytes: bytes) -> bytes:
    return _run(audio_bytes, {"onset_threshold": 0.40, "frame_threshold": 0.22, "minimum_note_length": 100.0})


@app.function(image=image, timeout=900, memory=4096, scaledown_window=600)
def short_note_recovery(audio_bytes: bytes) -> bytes:
    return _run(audio_bytes, {"onset_threshold": 0.45, "frame_threshold": 0.25, "minimum_note_length": 75.0})


@app.function(image=image, timeout=900, memory=4096, scaledown_window=600)
def upper_string_recovery(audio_bytes: bytes) -> bytes:
    return _run(audio_bytes, {"onset_threshold": 0.35, "frame_threshold": 0.20, "minimum_note_length": 75.0, "minimum_frequency": 100.0, "maximum_frequency": 1400.0})
