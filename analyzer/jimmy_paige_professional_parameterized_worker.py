from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

app = modal.App("dadrock-jimmy-paige-professional-worker")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("basic-pitch")
)


def _normalize_note_event(event: Any) -> dict[str, Any] | None:
    if isinstance(event, dict):
        start = event.get("start_time", event.get("start", 0.0))
        end = event.get("end_time", event.get("end", start))
        pitch = event.get(
            "pitch_midi",
            event.get("midi_pitch", event.get("midiPitch", event.get("pitch"))),
        )
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
            "midiPitch": int(round(float(pitch))),
            "confidence": float(confidence or 0.0),
        }
    except (TypeError, ValueError):
        return None


@app.function(image=image, timeout=1200, memory=4096)
def extract_parameterized(audio_bytes: bytes, parameters: dict[str, Any]) -> bytes:
    from basic_pitch.inference import predict

    started = time.time()
    with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as handle:
        audio_path = Path(handle.name)
        handle.write(audio_bytes)

    try:
        _, _, note_events = predict(
            audio_path,
            onset_threshold=float(parameters.get("onset_threshold", 0.35)),
            frame_threshold=float(parameters.get("frame_threshold", 0.20)),
            minimum_note_length=float(parameters.get("minimum_note_length", 75.0)),
            minimum_frequency=parameters.get("minimum_frequency", 100.0),
            maximum_frequency=parameters.get("maximum_frequency", 1400.0),
            multiple_pitch_bends=bool(parameters.get("multiple_pitch_bends", False)),
            melodia_trick=True,
        )
        events = [
            item
            for raw in note_events
            if (item := _normalize_note_event(raw)) is not None
        ]
        return json.dumps(
            {
                "events": events,
                "parameters": parameters,
                "remoteElapsedSeconds": round(time.time() - started, 3),
            }
        ).encode("utf-8")
    finally:
        audio_path.unlink(missing_ok=True)
