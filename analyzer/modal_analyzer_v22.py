import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v21 as previous

base = previous.base
engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v21")

LOOKAHEAD_WINDOWS = 2
MIN_STRONG_CHORD_CONFIDENCE = 0.68
MAX_POSITION_JUMP_WITHOUT_EVIDENCE = 4

# Common, guitarist-friendly transitions. These are general harmonic movement
# preferences, not song-specific tablature.
CHORD_TRANSITION_BONUS: dict[tuple[str, str], float] = {
    ("Am", "C"): 1.2,
    ("Am", "C/G"): 1.4,
    ("C", "D/F#"): 1.1,
    ("C/G", "D/F#"): 1.35,
    ("D", "Fmaj7"): 0.7,
    ("D/F#", "Fmaj7"): 1.0,
    ("Fmaj7", "G/B"): 1.25,
    ("Fmaj7", "G"): 0.95,
    ("G/B", "Am"): 1.35,
    ("G", "Am"): 1.0,
    ("Em", "G"): 0.8,
    ("C", "G/B"): 0.9,
}


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def flatten_windows(
    phrases: list[list[list[dict[str, Any]]]],
    transcription_type: str,
) -> list[list[list[dict[str, Any]]]]:
    windows: list[list[list[dict[str, Any]]]] = []
    for phrase in phrases:
        windows.extend(previous.previous.split_harmonic_windows(phrase, transcription_type))
    return windows


def chord_candidates(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
) -> list[tuple[str | None, dict[int, tuple[int, int]], float]]:
    if transcription_type == "bass":
        return [(None, {}, 0.0)]

    notes = [note for group in window for note in group]
    if len(notes) < 2:
        return [(None, {}, 0.0)]

    note_midis = [int(note["midi"]) for note in notes]
    distinct_classes = {midi % 12 for midi in note_midis}
    ranked: list[tuple[str | None, dict[int, tuple[int, int]], float]] = []

    for name, shape in previous.OPEN_CHORD_SHAPES.items():
        pitch_map = previous.shape_pitch_map(shape)
        shape_classes = {midi % 12 for midi in pitch_map}
        exact = sum(1 for midi in note_midis if midi in pitch_map)
        class_only = sum(
            1
            for midi in note_midis
            if midi not in pitch_map and midi % 12 in shape_classes
        )
        coverage = (exact + class_only * 0.28) / max(len(note_midis), 1)
        overlap = len(distinct_classes & shape_classes)
        if overlap < min(2, len(distinct_classes)):
            continue

        lowest = min(note_midis)
        bass_bonus = 0.1 if lowest in pitch_map else 0.0
        register_penalty = sum(
            0.06
            for midi in note_midis
            if midi % 12 in shape_classes and midi not in pitch_map
        )
        score = coverage + bass_bonus - register_penalty
        if score >= 0.46:
            ranked.append((name, pitch_map, score))

    ranked.sort(key=lambda item: item[2], reverse=True)
    return ranked[:4] + [(None, {}, 0.0)]


def progression_cost(
    previous_name: str | None,
    current_name: str | None,
    current_confidence: float,
) -> float:
    if current_name is None:
        return 0.0

    cost = 0.0
    if current_confidence < MIN_STRONG_CHORD_CONFIDENCE:
        cost += (MIN_STRONG_CHORD_CONFIDENCE - current_confidence) * 5.0

    if previous_name:
        cost -= CHORD_TRANSITION_BONUS.get((previous_name, current_name), 0.0)
        if previous_name == current_name:
            cost -= 0.9
    return cost


def future_support(
    candidate_name: str | None,
    future_candidates: list[list[tuple[str | None, dict[int, tuple[int, int]], float]]],
) -> float:
    if candidate_name is None:
        return 0.0

    support = 0.0
    for distance, options in enumerate(future_candidates[:LOOKAHEAD_WINDOWS], start=1):
        weight = 1.0 / distance
        for future_name, _, confidence in options:
            if future_name is None:
                continue
            transition = CHORD_TRANSITION_BONUS.get((candidate_name, future_name), 0.0)
            same = 0.5 if candidate_name == future_name else 0.0
            support += (transition + same) * confidence * weight
    return support


def choose_chord_sequence(
    windows: list[list[list[dict[str, Any]]]],
    transcription_type: str,
) -> list[tuple[str | None, dict[int, tuple[int, int]], float]]:
    options = [chord_candidates(window, transcription_type) for window in windows]
    beam: list[tuple[float, list[tuple[str | None, dict[int, tuple[int, int]], float]]]] = [(0.0, [])]

    for index, current_options in enumerate(options):
        next_beam = []
        future = options[index + 1 : index + 1 + LOOKAHEAD_WINDOWS]
        for accumulated, path in beam:
            previous_name = path[-1][0] if path else None
            for name, pitch_map, confidence in current_options:
                cost = accumulated + progression_cost(previous_name, name, confidence)
                cost -= future_support(name, future) * 0.55
                if name is None:
                    # Do not force a chord, but prefer a supported chord when evidence exists.
                    strongest = max((item[2] for item in current_options if item[0]), default=0.0)
                    if strongest >= MIN_STRONG_CHORD_CONFIDENCE:
                        cost += 1.4
                next_beam.append((cost, path + [(name, pitch_map, confidence)]))

        next_beam.sort(key=lambda item: item[0])
        beam = next_beam[:18]

    return beam[0][1] if beam else [(None, {}, 0.0) for _ in windows]


def assignment_position(
    assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> float | None:
    if not assignment:
        return None
    frets = [fret for _, _, fret in assignment if fret > 0]
    if not frets:
        return 0.0
    return sum(frets) / len(frets)


def map_window_with_lookahead(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
    previous_anchor: int | None,
    chord_name: str | None,
    chord_map: dict[int, tuple[int, int]],
    chord_confidence: float,
) -> tuple[list[list[dict[str, Any]]], list[tuple[dict[str, Any], int, int]] | None]:
    beam: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = [(0.0, [])]

    for group in window:
        generic = previous.previous.previous.group_assignments(
            group,
            transcription_type,
            anchor,
        )
        shape_candidate = previous.template_assignment(group, chord_map) if chord_map else None
        candidates = ([shape_candidate] if shape_candidate else []) + generic

        # Remove duplicate candidate shapes while preserving order.
        unique = []
        seen = set()
        for candidate in candidates:
            key = tuple(sorted((int(note["midi"]), string_index, fret) for note, string_index, fret in candidate))
            if key in seen:
                continue
            seen.add(key)
            unique.append(candidate)

        next_beam = []
        for accumulated, path in beam:
            prior = path[-1] if path else previous_assignment
            prior_position = assignment_position(prior)
            for candidate in unique:
                cost = accumulated
                cost += previous.previous.chord_shape_cost(candidate, transcription_type, anchor)
                cost += previous.previous.guitarist_movement_cost(
                    prior,
                    candidate,
                    previous_anchor if not path else anchor,
                    anchor,
                )

                if shape_candidate and candidate == shape_candidate:
                    cost -= 4.5 + chord_confidence * 3.5
                elif chord_map:
                    explained = sum(
                        1
                        for note, string_index, fret in candidate
                        if chord_map.get(int(note["midi"])) == (string_index, fret)
                    )
                    cost -= explained * (0.8 + chord_confidence)

                current_position = assignment_position(candidate)
                if prior_position is not None and current_position is not None:
                    jump = abs(current_position - prior_position)
                    if jump > MAX_POSITION_JUMP_WITHOUT_EVIDENCE and chord_confidence < 0.75:
                        cost += (jump - MAX_POSITION_JUMP_WITHOUT_EVIDENCE) * 4.5

                next_beam.append((cost, path + [candidate]))

        next_beam.sort(key=lambda item: item[0])
        beam = next_beam[:24]

    if not beam:
        return [], previous_assignment

    winning_path = beam[0][1]
    mapped = []
    for assignment in winning_path:
        mapped_group = []
        for note, string_index, fret in assignment:
            bend = engine.estimate_bend_semitones(note.get("pitchBends"))
            mapped_group.append({
                **note,
                "stringIndex": int(string_index),
                "fret": int(fret),
                "technique": "bend" if bend >= 0.35 else None,
                "bendSemitones": round(float(bend), 2),
                "harmonicContext": chord_name,
                "harmonicConfidence": round(float(chord_confidence), 3),
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
    windows = flatten_windows(phrases, transcription_type)
    chord_sequence = choose_chord_sequence(windows, transcription_type)

    mapped_groups = []
    anchors = []
    detected_chords = []
    chord_confidences = []
    previous_assignment = None
    previous_anchor = None

    for window, (chord_name, chord_map, chord_confidence) in zip(windows, chord_sequence):
        anchor = previous.previous.choose_window_anchor(window, transcription_type, previous_anchor)
        if chord_name and chord_confidence >= MIN_STRONG_CHORD_CONFIDENCE:
            anchor = min(anchor, 2)

        mapped, previous_assignment = map_window_with_lookahead(
            window,
            transcription_type,
            anchor,
            previous_assignment,
            previous_anchor,
            chord_name,
            chord_map,
            chord_confidence,
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
        "harmonicWindowCount": len(windows),
        "phraseAnchors": anchors,
        "detectedChords": detected_chords,
        "chordConfidences": chord_confidences,
        "engineVersion": "2.2-lookahead-progression-intelligence",
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
