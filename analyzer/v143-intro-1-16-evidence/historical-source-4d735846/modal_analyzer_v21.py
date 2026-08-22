import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v20 as previous

base = previous.base
engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v20")

# String indexes follow the analyzer's guitar order: 0=e, 1=B, 2=G,
# 3=D, 4=A, 5=low E. These are common open-position shapes, not
# song-specific tablature.
OPEN_CHORD_SHAPES: dict[str, dict[int, int]] = {
    "Am": {0: 0, 1: 1, 2: 2, 3: 2, 4: 0},
    "A": {0: 0, 1: 2, 2: 2, 3: 2, 4: 0},
    "C": {0: 0, 1: 1, 2: 0, 3: 2, 4: 3},
    "C/G": {0: 0, 1: 1, 2: 0, 3: 2, 4: 3, 5: 3},
    "D": {0: 2, 1: 3, 2: 2, 3: 0},
    "D/F#": {0: 2, 1: 3, 2: 2, 3: 0, 5: 2},
    "Em": {0: 0, 1: 0, 2: 0, 3: 2, 4: 2, 5: 0},
    "E": {0: 0, 1: 0, 2: 1, 3: 2, 4: 2, 5: 0},
    "Fmaj7": {0: 0, 1: 1, 2: 2, 3: 3},
    "G": {0: 3, 1: 0, 2: 0, 3: 0, 4: 2, 5: 3},
    "G/B": {0: 3, 1: 0, 2: 0, 3: 0, 4: 2},
}

GUITAR_OPEN_MIDI = [64, 59, 55, 50, 45, 40]
MIN_TEMPLATE_COVERAGE = 0.58


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def shape_pitch_map(shape: dict[int, int]) -> dict[int, tuple[int, int]]:
    return {
        GUITAR_OPEN_MIDI[string_index] + fret: (string_index, fret)
        for string_index, fret in shape.items()
    }


def detect_window_chord(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
) -> tuple[str | None, dict[int, tuple[int, int]], float]:
    if transcription_type == "bass":
        return None, {}, 0.0

    notes = [note for group in window for note in group]
    if len(notes) < 3:
        return None, {}, 0.0

    note_midis = [int(note["midi"]) for note in notes]
    distinct_pitch_classes = {midi % 12 for midi in note_midis}
    best_name: str | None = None
    best_map: dict[int, tuple[int, int]] = {}
    best_score = 0.0

    for name, shape in OPEN_CHORD_SHAPES.items():
        pitch_map = shape_pitch_map(shape)
        shape_classes = {midi % 12 for midi in pitch_map}
        exact_matches = sum(1 for midi in note_midis if midi in pitch_map)
        class_matches = sum(1 for midi in note_midis if midi % 12 in shape_classes)
        coverage = (exact_matches + 0.35 * (class_matches - exact_matches)) / len(note_midis)

        # Require enough harmonic information to avoid forcing a chord onto a melody.
        class_overlap = len(distinct_pitch_classes & shape_classes)
        if class_overlap < min(3, len(distinct_pitch_classes)):
            continue

        # Prefer exact guitar-register matches and shapes that explain the bass note.
        lowest = min(note_midis)
        bass_bonus = 0.12 if lowest in pitch_map else 0.0
        score = coverage + bass_bonus
        if score > best_score:
            best_name = name
            best_map = pitch_map
            best_score = score

    if best_score < MIN_TEMPLATE_COVERAGE:
        return None, {}, best_score
    return best_name, best_map, best_score


def template_assignment(
    group: list[dict[str, Any]],
    pitch_map: dict[int, tuple[int, int]],
) -> list[tuple[dict[str, Any], int, int]] | None:
    assignment: list[tuple[dict[str, Any], int, int]] = []
    used_strings: set[int] = set()

    for note in sorted(group, key=lambda item: int(item["midi"]), reverse=True):
        position = pitch_map.get(int(note["midi"]))
        if position is None:
            return None
        string_index, fret = position
        if string_index in used_strings:
            return None
        used_strings.add(string_index)
        assignment.append((note, string_index, fret))

    return assignment


def map_window_with_chord_memory(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
    previous_anchor: int | None,
    chord_name: str | None,
    chord_map: dict[int, tuple[int, int]],
) -> tuple[list[list[dict[str, Any]]], list[tuple[dict[str, Any], int, int]] | None]:
    beam: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = [(0.0, [])]

    for group in window:
        candidates = previous.previous.group_assignments(group, transcription_type, anchor)
        shape_candidate = template_assignment(group, chord_map) if chord_map else None
        if shape_candidate:
            candidates = [shape_candidate] + candidates

        next_beam: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = []
        for accumulated, path in beam:
            prior = path[-1] if path else previous_assignment
            for candidate in candidates:
                cost = accumulated + previous.chord_shape_cost(
                    candidate,
                    transcription_type,
                    anchor,
                ) + previous.guitarist_movement_cost(
                    prior,
                    candidate,
                    previous_anchor if not path else anchor,
                    anchor,
                )

                # A recognized chord is a strong structural hint. Reward its exact shape,
                # but retain generic candidates when pitch detection does not fit cleanly.
                if shape_candidate and candidate == shape_candidate:
                    cost -= 6.0
                    if chord_name and any(item[2] == 0 for item in candidate):
                        cost -= 0.8
                elif chord_map:
                    explained = sum(
                        1
                        for note, string_index, fret in candidate
                        if chord_map.get(int(note["midi"])) == (string_index, fret)
                    )
                    cost -= explained * 1.1

                next_beam.append((cost, path + [candidate]))

        next_beam.sort(key=lambda item: item[0])
        beam = next_beam[: previous.BEAM_WIDTH]

    if not beam:
        return [], previous_assignment

    winning_path = beam[0][1]
    mapped: list[list[dict[str, Any]]] = []
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
                "harmonicContext": chord_name,
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
    detected_chords: list[str | None] = []
    chord_confidences: list[float] = []
    previous_assignment = None
    previous_anchor = None

    for phrase in phrases:
        for window in previous.split_harmonic_windows(phrase, transcription_type):
            chord_name, chord_map, chord_confidence = detect_window_chord(
                window,
                transcription_type,
            )
            anchor = previous.choose_window_anchor(window, transcription_type, previous_anchor)
            if chord_name:
                anchor = min(anchor, 2)

            mapped, previous_assignment = map_window_with_chord_memory(
                window,
                transcription_type,
                anchor,
                previous_assignment,
                previous_anchor,
                chord_name,
                chord_map,
            )
            mapped_groups.extend(mapped)
            anchors.append(anchor)
            detected_chords.append(chord_name)
            chord_confidences.append(round(float(chord_confidence), 3))
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
        "detectedChords": detected_chords,
        "chordConfidences": chord_confidences,
        "engineVersion": "2.1-open-chord-template-intelligence",
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
