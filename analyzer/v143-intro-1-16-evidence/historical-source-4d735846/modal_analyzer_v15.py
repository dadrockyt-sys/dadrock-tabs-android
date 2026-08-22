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
MAX_RENDERED_GROUPS = 320
GROUP_START_TOLERANCE = 0.075
PHRASE_GAP_SECONDS = 0.65
BEAM_WIDTH = 24


def get_tuning(transcription_type: str) -> list[tuple[str, int]]:
    return (
        STANDARD_BASS_TUNING
        if transcription_type == "bass"
        else STANDARD_GUITAR_TUNING
    )


def extract_note_event(note_event: Any) -> dict[str, Any] | None:
    if isinstance(note_event, dict):
        start = float(
            note_event.get("start_time")
            or note_event.get("start")
            or 0
        )
        end = float(
            note_event.get("end_time")
            or note_event.get("end")
            or start
        )
        midi = int(
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
        start = float(values[0])
        end = float(values[1])
        midi = int(values[2])
        amplitude = (
            float(values[3])
            if len(values) > 3
            and isinstance(values[3], (int, float))
            else 0.0
        )
        pitch_bends = values[4] if len(values) > 4 else None

    if midi <= 0 or end < start:
        return None

    return {
        "start": round(start, 4),
        "end": round(end, 4),
        "duration": round(max(0.0, end - start), 4),
        "midi": midi,
        "amplitude": round(amplitude, 4),
        "pitchBends": pitch_bends,
    }


def playable_positions(
    midi_pitch: int,
    transcription_type: str,
) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    for string_index, (_, open_pitch) in enumerate(
        get_tuning(transcription_type)
    ):
        fret = midi_pitch - open_pitch
        if 0 <= fret <= MAX_FRET:
            positions.append((string_index, fret))
    return positions


def estimate_bend_semitones(pitch_bends: Any) -> float:
    if pitch_bends is None:
        return 0.0
    try:
        values = list(pitch_bends)
    except TypeError:
        return 0.0

    numeric: list[float] = []
    for value in values:
        if isinstance(value, (int, float)):
            numeric.append(float(value))
        elif isinstance(value, (list, tuple)) and value:
            candidate = value[-1]
            if isinstance(candidate, (int, float)):
                numeric.append(float(candidate))

    if not numeric:
        return 0.0

    maximum = max(abs(value) for value in numeric)
    if maximum <= 12:
        return maximum
    return min(2.0, maximum / 8192.0 * 2.0)


def group_simultaneous_notes(
    notes: list[dict[str, Any]],
) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []

    for note in sorted(notes, key=lambda item: (item["start"], item["midi"])):
        if not groups:
            groups.append([note])
            continue

        current = groups[-1]
        anchor = min(item["start"] for item in current)

        if note["start"] - anchor <= GROUP_START_TOLERANCE:
            # Avoid duplicate pitch detections in the same onset group.
            duplicate = next(
                (item for item in current if item["midi"] == note["midi"]),
                None,
            )
            if duplicate is None:
                current.append(note)
            elif note["amplitude"] > duplicate["amplitude"]:
                current.remove(duplicate)
                current.append(note)
        else:
            groups.append([note])

    return groups


def split_phrases(
    groups: list[list[dict[str, Any]]],
) -> list[list[list[dict[str, Any]]]]:
    phrases: list[list[list[dict[str, Any]]]] = []
    current: list[list[dict[str, Any]]] = []
    previous_end: float | None = None

    for group in groups:
        group_start = min(note["start"] for note in group)
        group_end = max(note["end"] for note in group)

        if (
            current
            and previous_end is not None
            and group_start - previous_end > PHRASE_GAP_SECONDS
        ):
            phrases.append(current)
            current = []

        current.append(group)
        previous_end = max(previous_end or group_end, group_end)

    if current:
        phrases.append(current)

    return phrases


def generate_group_assignments(
    group: list[dict[str, Any]],
    transcription_type: str,
) -> list[list[tuple[dict[str, Any], int, int]]]:
    ordered = sorted(group, key=lambda note: note["midi"], reverse=True)
    assignments: list[list[tuple[dict[str, Any], int, int]]] = [[]]

    for note in ordered:
        next_assignments: list[list[tuple[dict[str, Any], int, int]]] = []
        for assignment in assignments:
            used_strings = {item[1] for item in assignment}
            for string_index, fret in playable_positions(
                note["midi"],
                transcription_type,
            ):
                if string_index in used_strings:
                    continue
                next_assignments.append(
                    assignment + [(note, string_index, fret)]
                )

        assignments = next_assignments[:120]
        if not assignments:
            break

    if assignments:
        return assignments

    # Monophonic fallback when a noisy chord cannot fit unique strings.
    loudest = max(group, key=lambda note: note["amplitude"])
    return [
        [(loudest, string_index, fret)]
        for string_index, fret in playable_positions(
            loudest["midi"],
            transcription_type,
        )
    ]


def local_assignment_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
) -> float:
    frets = [item[2] for item in assignment]
    strings = [item[1] for item in assignment]
    ideal_fret = (
        5
        if transcription_type == "bass"
        else 3
        if transcription_type == "rhythm"
        else 7
    )

    cost = sum(abs(fret - ideal_fret) * 0.18 for fret in frets)

    if frets:
        fret_span = max(frets) - min(frets)
        cost += max(0, fret_span - 4) * 2.4

    if len(strings) > 1:
        string_span = max(strings) - min(strings)
        cost += max(0, string_span - len(strings)) * 0.7

    if transcription_type in {"rhythm", "bass"}:
        cost -= sum(0.35 for fret in frets if fret == 0)
    else:
        cost += sum(0.25 for fret in frets if fret == 0)

    return cost


def transition_cost(
    previous: list[tuple[dict[str, Any], int, int]] | None,
    current: list[tuple[dict[str, Any], int, int]],
) -> float:
    if not previous:
        return 0.0

    previous_frets = [item[2] for item in previous]
    current_frets = [item[2] for item in current]
    previous_strings = [item[1] for item in previous]
    current_strings = [item[1] for item in current]

    previous_centre = sum(previous_frets) / len(previous_frets)
    current_centre = sum(current_frets) / len(current_frets)
    hand_shift = abs(current_centre - previous_centre)

    cost = hand_shift * 1.15
    if hand_shift > 5:
        cost += (hand_shift - 5) * 2.2

    previous_string_centre = sum(previous_strings) / len(previous_strings)
    current_string_centre = sum(current_strings) / len(current_strings)
    cost += abs(current_string_centre - previous_string_centre) * 0.45

    # Reward retaining identical pitch/string choices across repeated notes.
    previous_map = {item[0]["midi"]: (item[1], item[2]) for item in previous}
    for note, string_index, fret in current:
        if previous_map.get(note["midi"]) == (string_index, fret):
            cost -= 0.8

    return cost


def map_phrase_to_fretboard(
    phrase: list[list[dict[str, Any]]],
    transcription_type: str,
) -> list[list[dict[str, Any]]]:
    beam: list[
        tuple[
            float,
            list[list[tuple[dict[str, Any], int, int]]],
        ]
    ] = [(0.0, [])]

    for group in phrase:
        candidates = generate_group_assignments(group, transcription_type)
        next_beam: list[
            tuple[
                float,
                list[list[tuple[dict[str, Any], int, int]]],
            ]
        ] = []

        for accumulated_cost, path in beam:
            previous = path[-1] if path else None
            for candidate in candidates:
                cost = (
                    accumulated_cost
                    + local_assignment_cost(candidate, transcription_type)
                    + transition_cost(previous, candidate)
                )
                next_beam.append((cost, path + [candidate]))

        next_beam.sort(key=lambda item: item[0])
        beam = next_beam[:BEAM_WIDTH]

    if not beam:
        return []

    best_path = beam[0][1]
    mapped_groups: list[list[dict[str, Any]]] = []

    for assignment in best_path:
        mapped_group: list[dict[str, Any]] = []
        for note, string_index, fret in assignment:
            bend = estimate_bend_semitones(note.get("pitchBends"))
            mapped_group.append(
                {
                    **note,
                    "stringIndex": string_index,
                    "fret": fret,
                    "technique": "bend" if bend >= 0.35 else None,
                    "bendSemitones": round(bend, 2),
                }
            )
        mapped_groups.append(mapped_group)

    return mapped_groups


def render_fret(event: dict[str, Any]) -> str:
    fret = str(event["fret"])
    if event.get("technique") == "bend":
        amount = float(event.get("bendSemitones") or 0)
        if amount >= 1.75:
            return f"{fret}b{int(event['fret']) + 2}"
        if amount >= 0.75:
            return f"{fret}b{int(event['fret']) + 1}"
        return f"{fret}b"
    return fret


def create_tab(
    grouped_events: list[list[dict[str, Any]]],
    transcription_type: str,
) -> str:
    tuning = get_tuning(transcription_type)
    if not grouped_events:
        return "No playable notes were detected."

    columns: list[list[str]] = []

    for group in grouped_events[:MAX_RENDERED_GROUPS]:
        rendered = [render_fret(event) for event in group]
        width = max(3, max((len(value) for value in rendered), default=1) + 1)
        column = ["-" * width for _ in tuning]

        for event, value in zip(group, rendered):
            column[event["stringIndex"]] = value.ljust(width, "-")

        columns.append(column)

    tab_lines: list[str] = []
    groups_per_system = 18

    for start_index in range(0, len(columns), groups_per_system):
        section = columns[start_index : start_index + groups_per_system]
        for string_index, (label, _) in enumerate(tuning):
            body = "".join(column[string_index] for column in section)
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
        raise ValueError("The uploaded audio inspection timed out.") from error

    if completed.returncode != 0:
        raise ValueError("The uploaded file could not be read as audio.")

    try:
        probe_data = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("The uploaded audio returned invalid metadata.") from error

    audio_stream = next(
        (
            stream
            for stream in probe_data.get("streams", [])
            if stream.get("codec_type") == "audio"
        ),
        None,
    )
    if not audio_stream:
        raise ValueError("The uploaded file contains no audio stream.")

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

    duration = safe_float(
        format_data.get("duration") or audio_stream.get("duration")
    )

    return {
        "durationSeconds": round(duration, 3),
        "sampleRate": safe_int(audio_stream.get("sample_rate")),
        "channels": safe_int(audio_stream.get("channels")),
        "codec": audio_stream.get("codec_name") or None,
        "formatName": format_data.get("format_name") or None,
        "fileSize": safe_int(format_data.get("size")),
    }


def validate_audio_metadata(metadata: dict[str, Any]) -> None:
    duration = float(metadata.get("durationSeconds") or 0)
    size = int(metadata.get("fileSize") or 0)

    if duration < MIN_AUDIO_DURATION_SECONDS:
        raise ValueError("The uploaded audio must be at least 3 seconds long.")
    if duration > MAX_AUDIO_DURATION_SECONDS:
        raise ValueError("The uploaded audio cannot be longer than 15 minutes.")
    if size <= 0:
        raise ValueError("The uploaded audio file appears to be empty.")
    if size > MAX_AUDIO_SIZE_BYTES:
        raise ValueError("The uploaded audio cannot be larger than 50 MB.")
    if int(metadata.get("sampleRate") or 0) <= 0:
        raise ValueError("The uploaded audio sample rate could not be detected.")
    if int(metadata.get("channels") or 0) <= 0:
        raise ValueError("The uploaded audio channel information could not be detected.")


def normalize_audio_file(source_path: str, output_path: str) -> None:
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
        raise ValueError("The uploaded audio normalization timed out.") from error

    if completed.returncode != 0:
        raise ValueError("The uploaded audio could not be normalized.")

    output = Path(output_path)
    if not output.exists() or output.stat().st_size <= 0:
        raise ValueError("The normalized audio file was not created.")


def analyze_audio_file(
    audio_path: str,
    transcription_type: str,
) -> dict[str, Any]:
    from basic_pitch.inference import predict

    _, _, note_events = predict(audio_path)

    raw_notes = [
        parsed
        for event in note_events
        if (parsed := extract_note_event(event)) is not None
    ]

    onset_groups = group_simultaneous_notes(raw_notes)
    phrases = split_phrases(onset_groups)

    mapped_groups: list[list[dict[str, Any]]] = []
    for phrase in phrases:
        mapped_groups.extend(
            map_phrase_to_fretboard(phrase, transcription_type)
        )

    generated_tab = create_tab(mapped_groups, transcription_type)
    flattened = [event for group in mapped_groups for event in group]

    techniques = sorted(
        {
            event["technique"]
            for event in flattened
            if event.get("technique")
        }
    )

    return {
        "generatedTab": generated_tab,
        "tuning": "Standard Bass" if transcription_type == "bass" else "E Standard",
        "tempo": None,
        "timeSignature": None,
        "keySignature": None,
        "difficulty": None,
        "techniques": techniques,
        "confidence": None,
        "events": flattened,
        "noteCount": len(flattened),
        "onsetGroupCount": len(mapped_groups),
        "phraseCount": len(phrases),
    }


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
    transcription_type = str(
        payload.get("transcriptionType") or ""
    ).strip().lower()

    if transcription_type not in {"lead", "rhythm", "bass"}:
        raise HTTPException(
            status_code=400,
            detail="transcriptionType must be lead, rhythm, or bass.",
        )

    if not audio_url.startswith(("https://", "http://")):
        raise HTTPException(status_code=400, detail="A valid audioUrl is required.")

    suffix = Path(audio_url).suffix.lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        suffix = ".audio"

    blob_token = str(payload.get("blobToken") or "").strip()
    headers: dict[str, str] = {}
    if blob_token:
        headers["Authorization"] = f"Bearer {blob_token}"

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"uploaded{suffix}"

        try:
            response = requests.get(audio_url, headers=headers, timeout=120)
        except requests.RequestException as error:
            raise HTTPException(
                status_code=502,
                detail="The analyzer could not download the audio file.",
            ) from error

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail="The analyzer could not download the audio file.",
            )

        if len(response.content) > MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="The uploaded audio cannot be larger than 50 MB.",
            )

        audio_path.write_bytes(response.content)

        try:
            original_metadata = inspect_audio_file(str(audio_path))
            validate_audio_metadata(original_metadata)

            normalized_path = Path(temp_dir) / "normalized.wav"
            normalize_audio_file(str(audio_path), str(normalized_path))
            normalized_metadata = inspect_audio_file(str(normalized_path))

            result = analyze_audio_file(
                str(normalized_path),
                transcription_type,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        result["audioMetadata"] = original_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }

    return result
