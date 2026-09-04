import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import modal

app = modal.App("dadrock-tab-analyzer")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "basic-pitch",
        "fastapi[standard]",
        "requests",
    )
)

STANDARD_GUITAR_TUNING = [
    ("e", 64),
    ("B", 59),
    ("G", 55),
    ("D", 50),
    ("A", 45),
    ("E", 40),
]

STANDARD_BASS_TUNING = [
    ("G", 43),
    ("D", 38),
    ("A", 33),
    ("E", 28),
]

MAX_FRET = 24
MIN_AUDIO_DURATION_SECONDS = 3.0
MAX_AUDIO_DURATION_SECONDS = 15 * 60
MAX_AUDIO_SIZE_BYTES = 50 * 1024 * 1024
NORMALIZED_SAMPLE_RATE = 44100
NORMALIZED_CHANNELS = 2
MAX_RENDERED_NOTES = 320
NOTES_PER_SYSTEM = 20


def get_tuning(transcription_type: str) -> list[tuple[str, int]]:
    return (
        STANDARD_BASS_TUNING
        if transcription_type == "bass"
        else STANDARD_GUITAR_TUNING
    )


def choose_string_and_fret(
    midi_pitch: int,
    transcription_type: str,
    previous_string_index: int | None = None,
    previous_fret: int | None = None,
) -> tuple[int, int] | None:
    tuning = get_tuning(transcription_type)
    candidates: list[tuple[int, int]] = []

    for string_index, (_, open_pitch) in enumerate(tuning):
        fret = midi_pitch - open_pitch
        if 0 <= fret <= MAX_FRET:
            candidates.append((string_index, fret))

    if not candidates:
        return None

    def candidate_score(candidate: tuple[int, int]) -> float:
        string_index, fret = candidate

        ideal_fret = (
            5
            if transcription_type == "bass"
            else 3
            if transcription_type == "rhythm"
            else 7
        )

        score = abs(fret - ideal_fret) * 0.35

        if fret == 0:
            score += (
                -1.0
                if transcription_type in {"rhythm", "bass"}
                else 1.25
            )

        if previous_fret is not None:
            fret_distance = abs(fret - previous_fret)
            score += fret_distance * 1.15
            if fret_distance > 5:
                score += (fret_distance - 5) * 2.0

        if previous_string_index is not None:
            string_distance = abs(
                string_index - previous_string_index
            )
            score += string_distance * 0.8
            if string_distance > 2:
                score += (string_distance - 2) * 1.5

        return score

    return min(candidates, key=candidate_score)


def estimate_bend_semitones(pitch_bends: Any) -> float:
    if pitch_bends is None:
        return 0.0

    try:
        bend_values = list(pitch_bends)
    except TypeError:
        return 0.0

    numeric_values: list[float] = []

    for value in bend_values:
        if isinstance(value, (int, float)):
            numeric_values.append(float(value))
        elif isinstance(value, (list, tuple)) and value:
            candidate = value[-1]
            if isinstance(candidate, (int, float)):
                numeric_values.append(float(candidate))

    if not numeric_values:
        return 0.0

    maximum_absolute_bend = max(abs(value) for value in numeric_values)

    if maximum_absolute_bend <= 12:
        return maximum_absolute_bend

    return min(
        2.0,
        maximum_absolute_bend / 8192.0 * 2.0,
    )


def normalize_note_event(
    note_event: Any,
    transcription_type: str,
    previous_string_index: int | None = None,
    previous_fret: int | None = None,
) -> dict[str, Any] | None:
    if isinstance(note_event, dict):
        start_time = float(
            note_event.get("start_time")
            or note_event.get("start")
            or 0
        )
        end_time = float(
            note_event.get("end_time")
            or note_event.get("end")
            or start_time
        )
        midi_pitch = int(
            note_event.get("pitch_midi")
            or note_event.get("pitch")
            or note_event.get("midi")
            or 0
        )
        amplitude = float(
            note_event.get("amplitude")
            or note_event.get("velocity")
            or 0
        )
        pitch_bends = note_event.get("pitch_bends")
    else:
        values = list(note_event)

        if len(values) < 3:
            return None

        start_time = float(values[0])
        end_time = float(values[1])
        midi_pitch = int(values[2])
        amplitude = (
            float(values[3])
            if len(values) > 3
            and isinstance(values[3], (int, float))
            else 0.0
        )
        pitch_bends = values[4] if len(values) > 4 else None

    string_position = choose_string_and_fret(
        midi_pitch,
        transcription_type,
        previous_string_index,
        previous_fret,
    )

    if string_position is None:
        return None

    string_index, fret = string_position
    bend_semitones = estimate_bend_semitones(pitch_bends)

    return {
        "start": round(start_time, 3),
        "end": round(end_time, 3),
        "duration": round(max(0.0, end_time - start_time), 3),
        "midi": midi_pitch,
        "amplitude": round(amplitude, 4),
        "stringIndex": string_index,
        "fret": fret,
        "technique": "bend" if bend_semitones >= 0.35 else None,
        "bendSemitones": round(bend_semitones, 2),
    }


def render_fret(event: dict[str, Any]) -> str:
    fret = str(event["fret"])

    if event.get("technique") == "bend":
        bend_amount = float(event.get("bendSemitones") or 0)

        if bend_amount >= 1.75:
            return f"{fret}b{int(event['fret']) + 2}"
        if bend_amount >= 0.75:
            return f"{fret}b{int(event['fret']) + 1}"
        return f"{fret}b"

    return fret


def create_tab(
    events: list[dict[str, Any]],
    transcription_type: str,
) -> str:
    tuning = get_tuning(transcription_type)

    if not events:
        return "No playable notes were detected."

    sorted_events = sorted(events, key=lambda event: event["start"])
    columns: list[list[str]] = []

    for event in sorted_events[:MAX_RENDERED_NOTES]:
        rendered_note = render_fret(event)
        column_width = max(3, len(rendered_note) + 1)
        column = ["-" * column_width for _ in tuning]
        column[event["stringIndex"]] = rendered_note.ljust(
            column_width,
            "-",
        )
        columns.append(column)

    tab_lines: list[str] = []

    for start_index in range(
        0,
        len(columns),
        NOTES_PER_SYSTEM,
    ):
        section = columns[
            start_index : start_index + NOTES_PER_SYSTEM
        ]

        for string_index, (label, _) in enumerate(tuning):
            body = "".join(
                column[string_index]
                for column in section
            )
            tab_lines.append(f"{label}|{body}|")

        tab_lines.append("")

    return "\n".join(tab_lines).strip()


def inspect_audio_file(audio_path: str) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        audio_path,
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError(
            "The uploaded audio inspection timed out."
        ) from error

    if completed.returncode != 0:
        raise ValueError(
            "The uploaded file could not be read as audio."
        )

    try:
        probe_data = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The uploaded audio returned invalid metadata."
        ) from error

    audio_stream = next(
        (
            stream
            for stream in probe_data.get("streams", [])
            if stream.get("codec_type") == "audio"
        ),
        None,
    )

    if not audio_stream:
        raise ValueError(
            "The uploaded file contains no audio stream."
        )

    format_data = probe_data.get("format", {})

    def safe_float(value: Any) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    def safe_int(value: Any) -> int:
        try:
            return int(float(value or 0))
        except (TypeError, ValueError):
            return 0

    duration_seconds = safe_float(
        format_data.get("duration")
        or audio_stream.get("duration")
    )

    return {
        "durationSeconds": round(duration_seconds, 3),
        "sampleRate": safe_int(audio_stream.get("sample_rate")),
        "channels": safe_int(audio_stream.get("channels")),
        "channelLayout": audio_stream.get("channel_layout") or None,
        "codec": audio_stream.get("codec_name") or None,
        "bitrate": safe_int(
            format_data.get("bit_rate")
            or audio_stream.get("bit_rate")
        ),
        "formatName": format_data.get("format_name") or None,
        "fileSize": safe_int(format_data.get("size")),
    }


def validate_audio_metadata(metadata: dict[str, Any]) -> None:
    duration_seconds = float(
        metadata.get("durationSeconds") or 0
    )
    file_size = int(metadata.get("fileSize") or 0)
    sample_rate = int(metadata.get("sampleRate") or 0)
    channels = int(metadata.get("channels") or 0)

    if duration_seconds < MIN_AUDIO_DURATION_SECONDS:
        raise ValueError(
            "The uploaded audio must be at least 3 seconds long."
        )
    if duration_seconds > MAX_AUDIO_DURATION_SECONDS:
        raise ValueError(
            "The uploaded audio cannot be longer than 15 minutes."
        )
    if file_size <= 0:
        raise ValueError(
            "The uploaded audio file appears to be empty."
        )
    if file_size > MAX_AUDIO_SIZE_BYTES:
        raise ValueError(
            "The uploaded audio cannot be larger than 50 MB."
        )
    if sample_rate <= 0:
        raise ValueError(
            "The uploaded audio sample rate could not be detected."
        )
    if channels <= 0:
        raise ValueError(
            "The uploaded audio channel information could not be detected."
        )


def normalize_audio_file(
    source_path: str,
    output_path: str,
) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        source_path,
        "-map",
        "0:a:0",
        "-vn",
        "-ar",
        str(NORMALIZED_SAMPLE_RATE),
        "-ac",
        str(NORMALIZED_CHANNELS),
        "-c:a",
        "pcm_s16le",
        output_path,
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError(
            "The uploaded audio normalization timed out."
        ) from error

    if completed.returncode != 0:
        raise ValueError(
            "The uploaded audio could not be normalized."
        )

    normalized_file = Path(output_path)

    if (
        not normalized_file.exists()
        or normalized_file.stat().st_size <= 0
    ):
        raise ValueError(
            "The normalized audio file was not created."
        )


def analyze_audio_file(
    audio_path: str,
    transcription_type: str,
) -> dict[str, Any]:
    from basic_pitch.inference import predict

    _, _, note_events = predict(audio_path)

    normalized_events: list[dict[str, Any]] = []
    previous_string_index: int | None = None
    previous_fret: int | None = None

    sorted_note_events = sorted(
        note_events,
        key=lambda event: (
            float(
                event.get("start_time")
                or event.get("start")
                or 0
            )
            if isinstance(event, dict)
            else float(event[0])
        ),
    )

    for note_event in sorted_note_events:
        normalized_event = normalize_note_event(
            note_event,
            transcription_type,
            previous_string_index,
            previous_fret,
        )

        if normalized_event is None:
            continue

        normalized_events.append(normalized_event)
        previous_string_index = normalized_event["stringIndex"]
        previous_fret = normalized_event["fret"]

    generated_tab = create_tab(
        normalized_events,
        transcription_type,
    )

    detected_techniques = sorted(
        {
            event["technique"]
            for event in normalized_events
            if event["technique"]
        }
    )

    return {
        "generatedTab": generated_tab,
        "tuning": (
            "Standard Bass"
            if transcription_type == "bass"
            else "E Standard"
        ),
        "tempo": None,
        "timeSignature": None,
        "keySignature": None,
        "difficulty": None,
        "techniques": detected_techniques,
        "confidence": None,
        "events": normalized_events,
        "noteCount": len(normalized_events),
    }


@app.function(
    image=image,
    timeout=600,
    memory=4096,
    secrets=[
        modal.Secret.from_name(
            "dadrock-analyzer-secret"
        )
    ],
)
@modal.fastapi_endpoint(method="POST")
def analyze(payload: dict) -> dict:
    import requests
    from fastapi import HTTPException

    expected_token = os.environ.get("ANALYZER_API_TOKEN")
    supplied_token = str(payload.get("token") or "")

    if (
        not expected_token
        or supplied_token != expected_token
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized analyzer request.",
        )

    audio_url = str(
        payload.get("audioUrl") or ""
    ).strip()
    transcription_type = str(
        payload.get("transcriptionType") or ""
    ).strip().lower()

    if transcription_type not in {
        "lead",
        "rhythm",
        "bass",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "transcriptionType must be "
                "lead, rhythm, or bass."
            ),
        )

    if not audio_url.startswith(("https://", "http://")):
        raise HTTPException(
            status_code=400,
            detail="A valid audioUrl is required.",
        )

    suffix = Path(audio_url).suffix.lower()

    if suffix not in {
        ".mp3",
        ".wav",
        ".m4a",
        ".aac",
        ".flac",
        ".ogg",
    }:
        suffix = ".audio"

    blob_token = str(
        payload.get("blobToken") or ""
    ).strip()
    request_headers: dict[str, str] = {}

    if blob_token:
        request_headers["Authorization"] = (
            f"Bearer {blob_token}"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"uploaded{suffix}"

        try:
            response = requests.get(
                audio_url,
                headers=request_headers,
                timeout=120,
            )
        except requests.RequestException as error:
            raise HTTPException(
                status_code=502,
                detail=(
                    "The analyzer could not "
                    "download the audio file."
                ),
            ) from error

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail=(
                    "The analyzer could not "
                    "download the audio file."
                ),
            )

        if len(response.content) > MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=(
                    "The uploaded audio cannot "
                    "be larger than 50 MB."
                ),
            )

        audio_path.write_bytes(response.content)

        try:
            audio_metadata = inspect_audio_file(
                str(audio_path)
            )
            validate_audio_metadata(audio_metadata)

            normalized_path = (
                Path(temp_dir) / "normalized.wav"
            )
            normalize_audio_file(
                str(audio_path),
                str(normalized_path),
            )
            normalized_metadata = inspect_audio_file(
                str(normalized_path)
            )

            try:
                from full_mixture_runtime_shadow_v1 import (
                    estimate_full_mixture_runtime_shadow_v1,
                )

                mixture_observation = (
                    estimate_full_mixture_runtime_shadow_v1(
                        str(normalized_path)
                    )
                )
            except Exception:
                mixture_observation = None

            result = analyze_audio_file(
                str(normalized_path),
                transcription_type,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

        result["audioMetadata"] = audio_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }
        result["mixtureObservation"] = mixture_observation

    return result