import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v17 as base

engine = base.engine
app = modal.App("dadrock-tab-analyzer")
image = base.image.add_local_python_source("modal_analyzer_v17")

POSITION_RADIUS = {
    "lead": 4,
    "rhythm": 3,
    "bass": 4,
}
MAX_CANDIDATES_PER_GROUP = 48
BEAM_WIDTH = 18


def to_json_safe(value: Any) -> Any:
    return base.to_json_safe(value)


def phrase_anchor(
    phrase: list[list[dict[str, Any]]],
    transcription_type: str,
) -> int:
    """Choose one practical hand position for an entire musical phrase."""
    anchors = range(0, 18)
    best_anchor = 5 if transcription_type != "rhythm" else 2
    best_cost = float("inf")

    for anchor in anchors:
        total = 0.0
        playable_notes = 0

        for group in phrase:
            for note in group:
                positions = engine.playable_positions(
                    int(note["midi"]),
                    transcription_type,
                )
                if not positions:
                    total += 100.0
                    continue

                def position_cost(position: tuple[int, int]) -> float:
                    string_index, fret = position
                    if fret == 0:
                        open_cost = (
                            -0.8
                            if transcription_type in {"rhythm", "bass"}
                            else 1.1
                        )
                    else:
                        open_cost = 0.0

                    distance = abs(fret - anchor)
                    high_fret_cost = max(0, fret - 15) * 0.7
                    edge_string_cost = (
                        0.18
                        if transcription_type == "lead"
                        and string_index >= 4
                        else 0.0
                    )
                    return (
                        distance
                        + open_cost
                        + high_fret_cost
                        + edge_string_cost
                    )

                total += min(position_cost(position) for position in positions)
                playable_notes += 1

        if playable_notes:
            total /= playable_notes

        # Mild preference for normal working areas, never enough to override notes.
        preferred = (
            5
            if transcription_type == "bass"
            else 2
            if transcription_type == "rhythm"
            else 5
        )
        total += abs(anchor - preferred) * 0.025

        if total < best_cost:
            best_cost = total
            best_anchor = anchor

    return best_anchor


def positions_near_anchor(
    midi_pitch: int,
    transcription_type: str,
    anchor: int,
) -> list[tuple[int, int]]:
    all_positions = engine.playable_positions(
        midi_pitch,
        transcription_type,
    )
    if not all_positions:
        return []

    radius = POSITION_RADIUS[transcription_type]
    nearby = [
        position
        for position in all_positions
        if position[1] == 0
        or abs(position[1] - anchor) <= radius
    ]

    # Do not force an impossible position; retain the closest real option.
    return nearby or sorted(
        all_positions,
        key=lambda position: abs(position[1] - anchor),
    )[:2]


def group_assignments(
    group: list[dict[str, Any]],
    transcription_type: str,
    anchor: int,
) -> list[list[tuple[dict[str, Any], int, int]]]:
    ordered = sorted(
        group,
        key=lambda note: int(note["midi"]),
        reverse=True,
    )
    assignments: list[list[tuple[dict[str, Any], int, int]]] = [[]]

    for note in ordered:
        next_assignments: list[
            list[tuple[dict[str, Any], int, int]]
        ] = []

        for assignment in assignments:
            used_strings = {item[1] for item in assignment}
            for string_index, fret in positions_near_anchor(
                int(note["midi"]),
                transcription_type,
                anchor,
            ):
                if string_index in used_strings:
                    continue
                next_assignments.append(
                    assignment + [(note, string_index, fret)]
                )

        assignments = next_assignments[:MAX_CANDIDATES_PER_GROUP]
        if not assignments:
            break

    if assignments:
        return assignments

    # Noise can create impossible oversized chords. Keep the strongest note.
    loudest = max(
        group,
        key=lambda note: (
            float(note.get("amplitude") or 0),
            float(note.get("duration") or 0),
        ),
    )
    return [
        [(loudest, string_index, fret)]
        for string_index, fret in positions_near_anchor(
            int(loudest["midi"]),
            transcription_type,
            anchor,
        )
    ]


def assignment_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    if not assignment:
        return 1000.0

    frets = [item[2] for item in assignment]
    strings = [item[1] for item in assignment]
    non_open = [fret for fret in frets if fret > 0]

    cost = sum(
        abs(fret - anchor) * 0.75
        for fret in non_open
    )

    if frets:
        span = max(frets) - min(frets)
        comfort = 5 if transcription_type == "lead" else 4
        cost += max(0, span - comfort) * 5.0

    if len(strings) > 1:
        string_span = max(strings) - min(strings)
        gaps = string_span + 1 - len(set(strings))
        cost += gaps * 1.2

    cost += sum(max(0, fret - 15) * 1.2 for fret in frets)

    if transcription_type in {"rhythm", "bass"}:
        cost -= sum(0.55 for fret in frets if fret == 0)
    elif any(fret == 0 for fret in frets) and anchor >= 4:
        cost += 0.8

    return cost


def movement_cost(
    previous: list[tuple[dict[str, Any], int, int]] | None,
    current: list[tuple[dict[str, Any], int, int]],
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
    shift = abs(current_position - previous_position)
    cost = shift * 2.0 + max(0, shift - 3) * 4.0

    previous_map = {
        int(note["midi"]): (string_index, fret)
        for note, string_index, fret in previous
    }
    for note, string_index, fret in current:
        old = previous_map.get(int(note["midi"]))
        if old == (string_index, fret):
            cost -= 1.8
        elif old is not None:
            cost += 1.2

    previous_string = statistics.mean(item[1] for item in previous)
    current_string = statistics.mean(item[1] for item in current)
    cost += abs(current_string - previous_string) * 0.55
    return cost


def map_phrase(
    phrase: list[list[dict[str, Any]]],
    transcription_type: str,
) -> tuple[list[list[dict[str, Any]]], int]:
    anchor = phrase_anchor(phrase, transcription_type)
    beam: list[
        tuple[
            float,
            list[list[tuple[dict[str, Any], int, int]]],
        ]
    ] = [(0.0, [])]

    for group in phrase:
        candidates = group_assignments(
            group,
            transcription_type,
            anchor,
        )
        next_beam = []

        for accumulated, path in beam:
            previous = path[-1] if path else None
            for candidate in candidates:
                cost = (
                    accumulated
                    + assignment_cost(
                        candidate,
                        transcription_type,
                        anchor,
                    )
                    + movement_cost(previous, candidate)
                )
                next_beam.append((cost, path + [candidate]))

        next_beam.sort(key=lambda item: item[0])
        beam = next_beam[:BEAM_WIDTH]

    if not beam:
        return [], anchor

    mapped: list[list[dict[str, Any]]] = []
    for assignment in beam[0][1]:
        mapped_group = []
        for note, string_index, fret in assignment:
            bend = engine.estimate_bend_semitones(
                note.get("pitchBends")
            )
            mapped_group.append(
                {
                    **note,
                    "stringIndex": int(string_index),
                    "fret": int(fret),
                    "technique": "bend" if bend >= 0.35 else None,
                    "bendSemitones": round(float(bend), 2),
                }
            )
        mapped.append(mapped_group)

    return mapped, anchor


def analyze_audio_file(
    audio_path: str,
    transcription_type: str,
) -> dict[str, Any]:
    from basic_pitch.inference import predict

    _, _, note_events = predict(audio_path)
    extracted = [
        parsed
        for event in note_events
        if (parsed := engine.extract_note_event(event)) is not None
    ]
    cleaned = base.clean_detected_notes(
        extracted,
        transcription_type,
    )
    onset_groups = base.guitarist_group_notes(
        cleaned,
        transcription_type,
    )
    phrases = engine.split_phrases(onset_groups)

    mapped_groups: list[list[dict[str, Any]]] = []
    anchors: list[int] = []
    for phrase in phrases:
        mapped, anchor = map_phrase(
            phrase,
            transcription_type,
        )
        mapped_groups.extend(mapped)
        anchors.append(anchor)

    generated_tab = engine.create_tab(
        mapped_groups,
        transcription_type,
    )
    flattened = [
        event for group in mapped_groups for event in group
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
        "phraseAnchors": anchors,
        "engineVersion": "1.9-phrase-position",
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
    headers = {"Authorization": f"Bearer {blob_token}"} if blob_token else {}

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"uploaded{suffix}"
        try:
            response = requests.get(
                audio_url,
                headers=headers,
                timeout=120,
            )
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
        if len(response.content) > engine.MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="The uploaded audio cannot be larger than 50 MB.",
            )

        audio_path.write_bytes(response.content)
        try:
            original_metadata = engine.inspect_audio_file(str(audio_path))
            engine.validate_audio_metadata(original_metadata)
            normalized_path = Path(temp_dir) / "normalized.wav"
            engine.normalize_audio_file(
                str(audio_path),
                str(normalized_path),
            )
            normalized_metadata = engine.inspect_audio_file(
                str(normalized_path)
            )
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

    return to_json_safe(result)
