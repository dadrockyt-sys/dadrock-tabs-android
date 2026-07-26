import math
import os
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
    ("e", 64),  # High E4
    ("B", 59),
    ("G", 55),
    ("D", 50),
    ("A", 45),
    ("E", 40),  # Low E2
]

STANDARD_BASS_TUNING = [
    ("G", 43),
    ("D", 38),
    ("A", 33),
    ("E", 28),
]

MAX_FRET = 24


def choose_string_and_fret(
    midi_pitch: int,
    transcription_type: str,
) -> tuple[int, int] | None:
    tuning = (
        STANDARD_BASS_TUNING
        if transcription_type == "bass"
        else STANDARD_GUITAR_TUNING
    )

    candidates: list[tuple[int, int]] = []

    for string_index, (_, open_pitch) in enumerate(tuning):
        fret = midi_pitch - open_pitch

        if 0 <= fret <= MAX_FRET:
            candidates.append((string_index, fret))

    if not candidates:
        return None

    # First version:
    # favour lower fret numbers, then thicker strings.
    return min(
        candidates,
        key=lambda item: (
            item[1],
            -item[0],
        ),
    )


def estimate_bend_semitones(
    pitch_bends: Any,
) -> float:
    if pitch_bends is None:
        return 0.0

    try:
        bend_values = list(pitch_bends)
    except TypeError:
        return 0.0

    if not bend_values:
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

    maximum_absolute_bend = max(
        abs(value) for value in numeric_values
    )

    # Basic Pitch may expose pitch movement in different
    # representations depending on runtime/version.
    # Values already near musical semitone ranges are retained.
    if maximum_absolute_bend <= 12:
        return maximum_absolute_bend

    # MIDI pitch bend convention:
    # -8192 to +8191, normally representing ±2 semitones.
    return min(
        2.0,
        maximum_absolute_bend / 8192.0 * 2.0,
    )


def normalize_note_event(
    note_event: Any,
    transcription_type: str,
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

        pitch_bends = (
            values[4]
            if len(values) > 4
            else None
        )

    string_position = choose_string_and_fret(
        midi_pitch,
        transcription_type,
    )

    if string_position is None:
        return None

    string_index, fret = string_position

    bend_semitones = estimate_bend_semitones(
        pitch_bends
    )

    technique = None

    if bend_semitones >= 0.35:
        technique = "bend"

    return {
        "start": round(start_time, 3),
        "end": round(end_time, 3),
        "duration": round(
            max(0.0, end_time - start_time),
            3,
        ),
        "midi": midi_pitch,
        "amplitude": round(amplitude, 4),
        "stringIndex": string_index,
        "fret": fret,
        "technique": technique,
        "bendSemitones": round(
            bend_semitones,
            2,
        ),
    }


def render_fret(event: dict[str, Any]) -> str:
    fret = str(event["fret"])

    if event["technique"] == "bend":
        bend_amount = event["bendSemitones"]

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
    tuning = (
        STANDARD_BASS_TUNING
        if transcription_type == "bass"
        else STANDARD_GUITAR_TUNING
    )

    if not events:
        return "No playable notes were detected."

    events = sorted(
        events,
        key=lambda event: event["start"],
    )

    columns: list[list[str]] = []

    for event in events[:160]:
        rendered_note = render_fret(event)

        column_width = max(
            3,
            len(rendered_note) + 1,
        )

        column = [
            "-" * column_width
            for _ in tuning
        ]

        column[event["stringIndex"]] = (
            rendered_note.ljust(
                column_width,
                "-",
            )
        )

        columns.append(column)

    tab_lines: list[str] = []

    section_size = 20

    for start_index in range(
        0,
        len(columns),
        section_size,
    ):
        section = columns[
            start_index:
            start_index + section_size
        ]

        for string_index, (label, _) in enumerate(tuning):
            body = "".join(
                column[string_index]
                for column in section
            )

            tab_lines.append(
                f"{label}|{body}|"
            )

        tab_lines.append("")

    return "\n".join(tab_lines).strip()


def analyze_audio_file(
    audio_path: str,
    transcription_type: str,
) -> dict[str, Any]:
    from basic_pitch.inference import predict

    _, _, note_events = predict(audio_path)

    normalized_events: list[dict[str, Any]] = []

    for note_event in note_events:
        normalized_event = normalize_note_event(
            note_event,
            transcription_type,
        )

        if normalized_event is not None:
            normalized_events.append(
                normalized_event
            )

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

    expected_token = os.environ.get(
        "ANALYZER_API_TOKEN"
    )

    supplied_token = str(
        payload.get("token") or ""
    )

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

    if not audio_url.startswith(
        ("https://", "http://")
    ):
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

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / (
            f"uploaded{suffix}"
        )

        blob_token = str(
    payload.get("blobToken") or ""
).strip()

request_headers = {}

if blob_token:
    request_headers["Authorization"] = (
        f"Bearer {blob_token}"
    )

response = requests.get(
    audio_url,
    headers=request_headers,
    timeout=120,
)

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail=(
                    "The analyzer could not "
                    "download the audio file."
                ),
            )

        audio_path.write_bytes(
            response.content
        )

        result = analyze_audio_file(
            str(audio_path),
            transcription_type,
        )

    return result
