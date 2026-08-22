import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v15 as engine

app = modal.App("dadrock-tab-analyzer")

image = engine.image.add_local_python_source(
    "modal_analyzer_v15"
)

MIN_NOTE_DURATION = {
    "lead": 0.055,
    "rhythm": 0.075,
    "bass": 0.075,
}
DUPLICATE_START_WINDOW = 0.09
MAX_GROUP_NOTES = {
    "lead": 5,
    "rhythm": 6,
    "bass": 4,
}


def to_json_safe(value: Any) -> Any:
    if value is None or isinstance(
        value,
        (str, bool, int, float),
    ):
        return value

    if isinstance(value, dict):
        return {
            str(key): to_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(item) for item in value]

    item_method = getattr(value, "item", None)
    if callable(item_method):
        try:
            return to_json_safe(item_method())
        except (TypeError, ValueError):
            pass

    tolist_method = getattr(value, "tolist", None)
    if callable(tolist_method):
        try:
            return to_json_safe(tolist_method())
        except (TypeError, ValueError):
            pass

    return str(value)


def clean_detected_notes(
    notes: list[dict[str, Any]],
    transcription_type: str,
) -> list[dict[str, Any]]:
    """Remove tiny, weak, duplicate Basic Pitch detections."""
    playable = [
        note
        for note in notes
        if engine.playable_positions(
            int(note["midi"]),
            transcription_type,
        )
    ]

    if not playable:
        return []

    amplitudes = [
        float(note.get("amplitude") or 0)
        for note in playable
        if float(note.get("amplitude") or 0) > 0
    ]

    median_amplitude = (
        statistics.median(amplitudes)
        if amplitudes
        else 0.0
    )

    amplitude_floor = median_amplitude * (
        0.30
        if transcription_type == "lead"
        else 0.38
    )

    minimum_duration = MIN_NOTE_DURATION[
        transcription_type
    ]

    filtered = [
        note
        for note in playable
        if float(note.get("duration") or 0)
        >= minimum_duration
        and float(note.get("amplitude") or 0)
        >= amplitude_floor
    ]

    filtered.sort(
        key=lambda note: (
            float(note["start"]),
            int(note["midi"]),
        )
    )

    deduplicated: list[dict[str, Any]] = []

    for note in filtered:
        duplicate_index = next(
            (
                index
                for index in range(
                    len(deduplicated) - 1,
                    -1,
                    -1,
                )
                if int(deduplicated[index]["midi"])
                == int(note["midi"])
                and abs(
                    float(deduplicated[index]["start"])
                    - float(note["start"])
                )
                <= DUPLICATE_START_WINDOW
            ),
            None,
        )

        if duplicate_index is None:
            deduplicated.append(note)
            continue

        existing = deduplicated[duplicate_index]
        existing_strength = (
            float(existing.get("amplitude") or 0)
            * max(
                float(existing.get("duration") or 0),
                0.05,
            )
        )
        next_strength = (
            float(note.get("amplitude") or 0)
            * max(
                float(note.get("duration") or 0),
                0.05,
            )
        )

        if next_strength > existing_strength:
            deduplicated[duplicate_index] = note

    return deduplicated


def guitarist_group_notes(
    notes: list[dict[str, Any]],
    transcription_type: str,
) -> list[list[dict[str, Any]]]:
    groups = engine.group_simultaneous_notes(notes)
    maximum_notes = MAX_GROUP_NOTES[
        transcription_type
    ]
    cleaned_groups: list[list[dict[str, Any]]] = []

    for group in groups:
        strongest_by_pitch: dict[
            int,
            dict[str, Any],
        ] = {}

        for note in group:
            pitch = int(note["midi"])
            existing = strongest_by_pitch.get(pitch)

            if (
                existing is None
                or float(note.get("amplitude") or 0)
                > float(existing.get("amplitude") or 0)
            ):
                strongest_by_pitch[pitch] = note

        reduced = sorted(
            strongest_by_pitch.values(),
            key=lambda note: (
                float(note.get("amplitude") or 0),
                float(note.get("duration") or 0),
            ),
            reverse=True,
        )[:maximum_notes]

        reduced.sort(key=lambda note: int(note["midi"]))

        if reduced:
            cleaned_groups.append(reduced)

    return cleaned_groups


def guitarist_local_assignment_cost(
    assignment: list[
        tuple[dict[str, Any], int, int]
    ],
    transcription_type: str,
) -> float:
    frets = [item[2] for item in assignment]
    strings = [item[1] for item in assignment]

    if not frets:
        return 1000.0

    position_target = (
        5
        if transcription_type == "bass"
        else 3
        if transcription_type == "rhythm"
        else 7
    )

    non_open_frets = [
        fret for fret in frets if fret > 0
    ]
    position_centre = (
        statistics.median(non_open_frets)
        if non_open_frets
        else 0
    )

    cost = abs(position_centre - position_target) * 0.12

    fret_span = max(frets) - min(frets)
    comfortable_span = (
        5 if transcription_type == "lead" else 4
    )
    cost += max(0, fret_span - comfortable_span) * 3.2

    if len(strings) > 1:
        string_span = max(strings) - min(strings)
        missing_strings = (
            string_span + 1 - len(set(strings))
        )
        cost += missing_strings * 0.65

    if transcription_type in {"rhythm", "bass"}:
        cost -= sum(
            0.45 for fret in frets if fret == 0
        )
    else:
        cost += sum(
            0.18 for fret in frets if fret == 0
        )

    cost += sum(
        0.12 * max(0, fret - 17)
        for fret in frets
    )

    return cost


def guitarist_transition_cost(
    previous: list[
        tuple[dict[str, Any], int, int]
    ] | None,
    current: list[
        tuple[dict[str, Any], int, int]
    ],
) -> float:
    if not previous:
        return 0.0

    previous_frets = [item[2] for item in previous]
    current_frets = [item[2] for item in current]

    previous_position = statistics.median(
        [fret for fret in previous_frets if fret > 0]
        or previous_frets
    )
    current_position = statistics.median(
        [fret for fret in current_frets if fret > 0]
        or current_frets
    )

    hand_shift = abs(
        current_position - previous_position
    )

    cost = hand_shift * 1.45

    if hand_shift > 4:
        cost += (hand_shift - 4) * 3.0

    previous_map = {
        int(note["midi"]): (string_index, fret)
        for note, string_index, fret in previous
    }

    for note, string_index, fret in current:
        previous_choice = previous_map.get(
            int(note["midi"])
        )

        if previous_choice == (string_index, fret):
            cost -= 1.25
        elif previous_choice is not None:
            cost += 0.75

    previous_string_centre = statistics.mean(
        item[1] for item in previous
    )
    current_string_centre = statistics.mean(
        item[1] for item in current
    )
    cost += abs(
        current_string_centre
        - previous_string_centre
    ) * 0.35

    return cost


def analyze_audio_file(
    audio_path: str,
    transcription_type: str,
) -> dict[str, Any]:
    from basic_pitch.inference import predict

    _, _, note_events = predict(audio_path)

    extracted = [
        parsed
        for event in note_events
        if (
            parsed := engine.extract_note_event(
                event
            )
        )
        is not None
    ]

    cleaned = clean_detected_notes(
        extracted,
        transcription_type,
    )
    onset_groups = guitarist_group_notes(
        cleaned,
        transcription_type,
    )
    phrases = engine.split_phrases(onset_groups)

    original_local_cost = (
        engine.local_assignment_cost
    )
    original_transition_cost = (
        engine.transition_cost
    )

    engine.local_assignment_cost = (
        guitarist_local_assignment_cost
    )
    engine.transition_cost = (
        guitarist_transition_cost
    )

    try:
        mapped_groups: list[
            list[dict[str, Any]]
        ] = []

        for phrase in phrases:
            mapped_groups.extend(
                engine.map_phrase_to_fretboard(
                    phrase,
                    transcription_type,
                )
            )
    finally:
        engine.local_assignment_cost = (
            original_local_cost
        )
        engine.transition_cost = (
            original_transition_cost
        )

    generated_tab = engine.create_tab(
        mapped_groups,
        transcription_type,
    )
    flattened = [
        event
        for group in mapped_groups
        for event in group
    ]

    techniques = sorted(
        {
            event["technique"]
            for event in flattened
            if event.get("technique")
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
        "techniques": techniques,
        "confidence": None,
        "events": flattened,
        "noteCount": len(flattened),
        "rawNoteCount": len(extracted),
        "cleanedNoteCount": len(cleaned),
        "onsetGroupCount": len(mapped_groups),
        "phraseCount": len(phrases),
        "engineVersion": "1.7-guitarist",
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

    blob_token = str(
        payload.get("blobToken") or ""
    ).strip()
    headers: dict[str, str] = {}

    if blob_token:
        headers["Authorization"] = (
            f"Bearer {blob_token}"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / (
            f"uploaded{suffix}"
        )

        try:
            response = requests.get(
                audio_url,
                headers=headers,
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

        if (
            len(response.content)
            > engine.MAX_AUDIO_SIZE_BYTES
        ):
            raise HTTPException(
                status_code=413,
                detail=(
                    "The uploaded audio cannot "
                    "be larger than 50 MB."
                ),
            )

        audio_path.write_bytes(response.content)

        try:
            original_metadata = (
                engine.inspect_audio_file(
                    str(audio_path)
                )
            )
            engine.validate_audio_metadata(
                original_metadata
            )

            normalized_path = (
                Path(temp_dir) / "normalized.wav"
            )
            engine.normalize_audio_file(
                str(audio_path),
                str(normalized_path),
            )
            normalized_metadata = (
                engine.inspect_audio_file(
                    str(normalized_path)
                )
            )

            result = analyze_audio_file(
                str(normalized_path),
                transcription_type,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

        result["audioMetadata"] = (
            original_metadata
        )
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata[
                "sampleRate"
            ],
            "channels": normalized_metadata[
                "channels"
            ],
            "codec": normalized_metadata[
                "codec"
            ],
            "formatName": normalized_metadata[
                "formatName"
            ],
        }

    return to_json_safe(result)
