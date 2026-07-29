import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v47 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v47")

LOW_BASS_MIDI_MAX = 43
MEASURE_COUNT = 12
PREFERRED_RANGES = {
    1: (5.0, 8.0),
    2: (5.0, 8.0),
    3: (5.0, 8.0),
    4: (5.0, 8.0),
    5: (5.0, 8.0),
    6: (5.0, 8.0),
    7: (5.0, 8.0),
    8: (5.0, 8.0),
    9: (5.0, 8.0),
    10: (5.0, 8.0),
    11: (0.0, 5.0),
    12: (0.0, 5.0),
}


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def event_midi(event: dict[str, Any]) -> int:
    return int(event.get("midi") or event.get("pitch") or 0)


def event_fret(event: dict[str, Any]) -> int:
    return int(event.get("fret") or 0)


def median_upper_fret(events: list[dict[str, Any]]) -> float | None:
    frets = [
        event_fret(event)
        for event in events
        if event_midi(event) > LOW_BASS_MIDI_MAX and event_fret(event) > 0
    ]
    return float(statistics.median(frets)) if frets else None


def measure_for_start(start: float, minimum: float, maximum: float) -> int:
    duration = max(0.001, maximum - minimum)
    progress = (start - minimum) / duration
    return min(MEASURE_COUNT, max(1, int(progress * MEASURE_COUNT) + 1))


def build_measure_window_diagnostics(result: dict[str, Any]) -> dict[str, Any]:
    events = [dict(event) for event in result.get("events", []) if isinstance(event, dict)]
    windows = list(
        (result.get("musicalUnderstanding") or {}).get("harmonicWindows") or []
    )
    if not events:
        return {"measureCount": MEASURE_COUNT, "measures": [], "failingMeasures": []}

    starts = [event_start(event) for event in events]
    minimum = min(starts)
    maximum = max(starts)

    measures: list[dict[str, Any]] = []
    for measure in range(1, MEASURE_COUNT + 1):
        current = [
            event
            for event in events
            if measure_for_start(event_start(event), minimum, maximum) == measure
        ]
        center = median_upper_fret(current)
        lower, upper = PREFERRED_RANGES[measure]
        high = center is not None and center > upper
        low = center is not None and center < lower
        open_upper = sum(
            1
            for event in current
            if event_midi(event) > LOW_BASS_MIDI_MAX and event_fret(event) == 0
        )

        event_times = [event_start(event) for event in current]
        measure_start = min(event_times) if event_times else None
        measure_end = max(event_times) if event_times else None
        overlapping_windows: list[dict[str, Any]] = []
        if measure_start is not None and measure_end is not None:
            for index, window in enumerate(windows):
                window_start = float(window.get("start") or 0.0)
                window_end = float(window.get("end") or window_start)
                if window_end >= measure_start and window_start <= measure_end:
                    overlapping_windows.append(
                        {
                            "windowIndex": index,
                            "start": round(window_start, 3),
                            "end": round(window_end, 3),
                            "chosenAnchor": window.get("chosenAnchor"),
                            "chord": (window.get("chord") or {}).get("name"),
                            "texture": window.get("texture"),
                        }
                    )

        measures.append(
            {
                "measure": measure,
                "eventCount": len(current),
                "upperMedianFret": round(center, 2) if center is not None else None,
                "preferredRange": [lower, upper],
                "tooHigh": high,
                "tooLow": low,
                "openUpperCount": open_upper,
                "eventStart": round(measure_start, 3) if measure_start is not None else None,
                "eventEnd": round(measure_end, 3) if measure_end is not None else None,
                "overlappingWindows": overlapping_windows,
                "events": [
                    {
                        "start": round(event_start(event), 3),
                        "midi": event_midi(event),
                        "stringIndex": int(event.get("stringIndex") or event.get("string_index") or 0),
                        "fret": event_fret(event),
                    }
                    for event in current
                ],
            }
        )

    return {
        "measureCount": MEASURE_COUNT,
        "measures": measures,
        "failingMeasures": [
            item
            for item in measures
            if item["tooHigh"] or item["tooLow"] or item["openUpperCount"] > 0
        ],
        "policy": "map-the-benchmark-measure-median-failures-to-the-harmonic-windows-and-anchors-that-produced-their-events",
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["benchmarkMeasureWindowDiagnostics"] = build_measure_window_diagnostics(result)
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "5.4-phase-1-benchmark-measure-to-window-diagnostics"
    result["guitarBrainLesson"] = "diagnose-high-measure-medians-even-when-the-whole-window-is-not-dominantly-high"
    return result


@app.function(
    image=image,
    timeout=600,
    memory=4096,
    secrets=[modal.Secret.from_name("dadrock-analyzer-secret")],
)
@modal.fastapi_endpoint(method="POST")
def analyze(payload: dict) -> dict:
    import requests
    from fastapi import HTTPException

    expected_token = os.environ.get("ANALYZER_API_TOKEN")
    supplied_token = str(payload.get("token") or "")
    if not expected_token or supplied_token != expected_token:
        raise HTTPException(status_code=401, detail="Unauthorized analyzer request.")

    audio_url = str(payload.get("audioUrl") or "").strip()
    transcription_type = str(payload.get("transcriptionType") or "").strip().lower()
    if transcription_type not in {"lead", "rhythm", "bass"}:
        raise HTTPException(status_code=400, detail="transcriptionType must be lead, rhythm, or bass.")
    if not audio_url.startswith(("https://", "http://")):
        raise HTTPException(status_code=400, detail="A valid audioUrl is required.")

    suffix = Path(audio_url).suffix.lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        suffix = ".audio"

    headers: dict[str, str] = {}
    blob_token = str(payload.get("blobToken") or "").strip()
    if blob_token:
        headers["Authorization"] = f"Bearer {blob_token}"

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"uploaded{suffix}"
        try:
            response = requests.get(audio_url, headers=headers, timeout=120)
        except requests.RequestException as error:
            raise HTTPException(status_code=502, detail="The analyzer could not download the audio file.") from error
        if not response.ok:
            raise HTTPException(status_code=502, detail="The analyzer could not download the audio file.")
        if len(response.content) > engine.MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="The uploaded audio cannot be larger than 50 MB.")

        audio_path.write_bytes(response.content)
        try:
            original_metadata = engine.inspect_audio_file(str(audio_path))
            engine.validate_audio_metadata(original_metadata)
            normalized_path = Path(temp_dir) / "normalized.wav"
            engine.normalize_audio_file(str(audio_path), str(normalized_path))
            normalized_metadata = engine.inspect_audio_file(str(normalized_path))
            result = analyze_audio_file(str(normalized_path), transcription_type)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        result["audioMetadata"] = original_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }

    return to_json_safe(result)
