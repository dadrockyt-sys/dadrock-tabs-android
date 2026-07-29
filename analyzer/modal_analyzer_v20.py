import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v19 as previous

base = previous.base
engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v19")

HARMONIC_WINDOW_SIZE = {
    "lead": 8,
    "rhythm": 4,
    "bass": 8,
}
BEAM_WIDTH = 22


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def split_harmonic_windows(
    phrase: list[list[dict[str, Any]]],
    transcription_type: str,
) -> list[list[list[dict[str, Any]]]]:
    """Break long phrases into short harmonic decisions instead of one fixed neck position."""
    size = HARMONIC_WINDOW_SIZE[transcription_type]
    windows: list[list[list[dict[str, Any]]]] = []
    current: list[list[dict[str, Any]]] = []

    for group in phrase:
        if current:
            gap = float(group[0]["start"]) - max(
                float(note.get("end") or note["start"])
                for note in current[-1]
            )
            if gap > 0.32 or len(current) >= size:
                windows.append(current)
                current = []
        current.append(group)

    if current:
        windows.append(current)
    return windows


def open_string_ratio(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
) -> float:
    notes = [note for group in window for note in group]
    if not notes:
        return 0.0
    open_playable = 0
    for note in notes:
        positions = engine.playable_positions(int(note["midi"]), transcription_type)
        if any(fret == 0 for _, fret in positions):
            open_playable += 1
    return open_playable / len(notes)


def choose_window_anchor(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
    previous_anchor: int | None,
) -> int:
    anchor = previous.phrase_anchor(window, transcription_type)
    ratio = open_string_ratio(window, transcription_type)

    # Guitarists often move from a closed-position arpeggio into open chord shapes.
    if transcription_type != "bass" and ratio >= 0.28:
        anchor = min(anchor, 2)

    if previous_anchor is not None and abs(anchor - previous_anchor) <= 2:
        anchor = previous_anchor
    return anchor


def chord_shape_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    cost = previous.assignment_cost(assignment, transcription_type, anchor)
    if not assignment:
        return cost

    ordered = sorted(assignment, key=lambda item: item[1])
    strings = [item[1] for item in ordered]
    frets = [item[2] for item in ordered]
    non_open = [fret for fret in frets if fret > 0]

    # Familiar chord/arpeggio shapes use adjacent strings and compact fret spreads.
    if len(strings) >= 2:
        string_span = max(strings) - min(strings)
        missing = string_span + 1 - len(set(strings))
        cost += missing * 1.8
        if missing == 0:
            cost -= 1.1

    if non_open:
        fret_span = max(non_open) - min(non_open)
        if fret_span <= 3:
            cost -= 1.25
        elif fret_span > 5:
            cost += (fret_span - 5) * 4.0

    # Open notes are valuable when combined with a low-position chord shape.
    open_count = sum(1 for fret in frets if fret == 0)
    if open_count and anchor <= 3:
        cost -= open_count * (0.9 if transcription_type == "lead" else 1.25)
    elif open_count and anchor >= 5:
        cost += open_count * 1.5

    # Prefer the lowest practical bass note on the physically lower strings.
    if len(assignment) >= 2:
        lowest_pitch_item = min(assignment, key=lambda item: int(item[0]["midi"]))
        cost -= lowest_pitch_item[1] * 0.12

    return cost


def guitarist_movement_cost(
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
    current: list[tuple[dict[str, Any], int, int]],
    previous_anchor: int | None,
    current_anchor: int,
) -> float:
    cost = previous.movement_cost(previous_assignment, current)
    if previous_anchor is not None:
        anchor_shift = abs(current_anchor - previous_anchor)
        cost += anchor_shift * 1.15
        if anchor_shift > 4:
            cost += (anchor_shift - 4) * 3.5

    if not previous_assignment:
        return cost

    previous_by_pitch = {
        int(note["midi"]): (string_index, fret)
        for note, string_index, fret in previous_assignment
    }
    for note, string_index, fret in current:
        old = previous_by_pitch.get(int(note["midi"]))
        if old == (string_index, fret):
            cost -= 2.0

    # Reward a melodic line that moves by a small fret interval on the same string.
    if len(previous_assignment) == 1 and len(current) == 1:
        _, old_string, old_fret = previous_assignment[0]
        _, new_string, new_fret = current[0]
        if old_string == new_string and abs(new_fret - old_fret) <= 3:
            cost -= 1.4

    return cost


def map_window(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
    previous_anchor: int | None,
) -> tuple[list[list[dict[str, Any]]], list[tuple[dict[str, Any], int, int]] | None]:
    beam: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = [(0.0, [])]

    for group in window:
        candidates = previous.group_assignments(group, transcription_type, anchor)
        next_beam: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = []

        for accumulated, path in beam:
            prior = path[-1] if path else previous_assignment
            for candidate in candidates:
                cost = accumulated + chord_shape_cost(
                    candidate,
                    transcription_type,
                    anchor,
                ) + guitarist_movement_cost(
                    prior,
                    candidate,
                    previous_anchor if not path else anchor,
                    anchor,
                )
                next_beam.append((cost, path + [candidate]))

        next_beam.sort(key=lambda item: item[0])
        beam = next_beam[:BEAM_WIDTH]

    if not beam:
        return [], previous_assignment

    mapped: list[list[dict[str, Any]]] = []
    winning_path = beam[0][1]
    for assignment in winning_path:
        mapped_group: list[dict[str, Any]] = []
        for note, string_index, fret in assignment:
            bend = engine.estimate_bend_semitones(note.get("pitchBends"))
            mapped_group.append({
                **note,
                "stringIndex": int(string_index),
                "fret": int(fret),
                "technique": "bend" if bend >= 0.35 else None,
                "bendSemitones": round(float(bend), 2),
            })
        mapped.append(mapped_group)

    return mapped, winning_path[-1] if winning_path else previous_assignment


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    from basic_pitch.inference import predict

    _, _, note_events = predict(audio_path)
    extracted = [
        parsed
        for event in note_events
        if (parsed := engine.extract_note_event(event)) is not None
    ]
    cleaned = base.clean_detected_notes(extracted, transcription_type)
    onset_groups = base.guitarist_group_notes(cleaned, transcription_type)
    phrases = engine.split_phrases(onset_groups)

    mapped_groups: list[list[dict[str, Any]]] = []
    anchors: list[int] = []
    previous_assignment = None
    previous_anchor = None

    for phrase in phrases:
        for window in split_harmonic_windows(phrase, transcription_type):
            anchor = choose_window_anchor(window, transcription_type, previous_anchor)
            mapped, previous_assignment = map_window(
                window,
                transcription_type,
                anchor,
                previous_assignment,
                previous_anchor,
            )
            mapped_groups.extend(mapped)
            anchors.append(anchor)
            previous_anchor = anchor

    generated_tab = engine.create_tab(mapped_groups, transcription_type)
    flattened = [event for group in mapped_groups for event in group]
    techniques = sorted({
        event["technique"]
        for event in flattened
        if event.get("technique")
    })

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
        "rawNoteCount": len(extracted),
        "cleanedNoteCount": len(cleaned),
        "onsetGroupCount": len(mapped_groups),
        "phraseCount": len(phrases),
        "harmonicWindowCount": len(anchors),
        "phraseAnchors": anchors,
        "engineVersion": "2.0-chord-aware-guitar-intelligence",
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
