import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v22 as previous

base = previous.base
engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v22")

TOP_PATHS = 3
PHRASE_BEAM_WIDTH = 36


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def assignment_key(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        sorted(
            (int(note["midi"]), int(string_index), int(fret))
            for note, string_index, fret in assignment
        )
    )


def path_metrics(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> dict[str, float]:
    positions: list[float] = []
    open_notes = 0
    total_notes = 0
    repeated_consistency = 0
    repeated_opportunities = 0
    prior_by_pitch: dict[int, tuple[int, int]] = {}

    for assignment in path:
        frets = [fret for _, _, fret in assignment if fret > 0]
        if frets:
            positions.append(float(statistics.median(frets)))
        elif assignment:
            positions.append(0.0)

        for note, string_index, fret in assignment:
            total_notes += 1
            if fret == 0:
                open_notes += 1
            midi = int(note["midi"])
            if midi in prior_by_pitch:
                repeated_opportunities += 1
                if prior_by_pitch[midi] == (string_index, fret):
                    repeated_consistency += 1
            prior_by_pitch[midi] = (string_index, fret)

    position_shifts = sum(
        abs(current - previous_position)
        for previous_position, current in zip(positions, positions[1:])
    )
    large_shifts = sum(
        1
        for previous_position, current in zip(positions, positions[1:])
        if abs(current - previous_position) > 4
    )

    return {
        "positionShiftTotal": round(position_shifts, 3),
        "largeShiftCount": float(large_shifts),
        "openStringRatio": round(open_notes / max(total_notes, 1), 3),
        "repeatConsistency": round(
            repeated_consistency / max(repeated_opportunities, 1),
            3,
        ),
    }


def whole_path_adjustment(
    path: list[list[tuple[dict[str, Any], int, int]]],
    transcription_type: str,
) -> float:
    metrics = path_metrics(path)
    cost = metrics["positionShiftTotal"] * 0.8
    cost += metrics["largeShiftCount"] * 6.0
    cost -= metrics["repeatConsistency"] * 4.0

    if transcription_type != "bass":
        # Open strings are useful in genuine low-position harmony, but too many
        # can indicate the mapper is forcing an unrelated open chord shape.
        ratio = metrics["openStringRatio"]
        if 0.08 <= ratio <= 0.42:
            cost -= 1.2
        elif ratio > 0.62:
            cost += (ratio - 0.62) * 8.0

    return cost


def window_path_candidates(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
    previous_anchor: int | None,
    chord_name: str | None,
    chord_map: dict[int, tuple[int, int]],
    chord_confidence: float,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    beam: list[
        tuple[float, list[list[tuple[dict[str, Any], int, int]]]]
    ] = [(0.0, [])]

    for group in window:
        generic = previous.previous.previous.previous.group_assignments(
            group,
            transcription_type,
            anchor,
        )
        shape_candidate = (
            previous.previous.template_assignment(group, chord_map)
            if chord_map
            else None
        )
        candidates = ([shape_candidate] if shape_candidate else []) + generic

        unique: list[list[tuple[dict[str, Any], int, int]]] = []
        seen = set()
        for candidate in candidates:
            key = assignment_key(candidate)
            if key in seen:
                continue
            seen.add(key)
            unique.append(candidate)

        next_beam = []
        for accumulated, path in beam:
            prior = path[-1] if path else previous_assignment
            prior_position = previous.assignment_position(prior)
            for candidate in unique:
                cost = accumulated
                cost += previous.previous.previous.chord_shape_cost(
                    candidate,
                    transcription_type,
                    anchor,
                )
                cost += previous.previous.previous.guitarist_movement_cost(
                    prior,
                    candidate,
                    previous_anchor if not path else anchor,
                    anchor,
                )

                if shape_candidate and candidate == shape_candidate:
                    cost -= 3.0 + chord_confidence * 2.5
                elif chord_map:
                    explained = sum(
                        1
                        for note, string_index, fret in candidate
                        if chord_map.get(int(note["midi"]))
                        == (string_index, fret)
                    )
                    cost -= explained * (0.6 + chord_confidence * 0.8)

                current_position = previous.assignment_position(candidate)
                if prior_position is not None and current_position is not None:
                    jump = abs(current_position - prior_position)
                    if jump > previous.MAX_POSITION_JUMP_WITHOUT_EVIDENCE:
                        cost += (
                            jump - previous.MAX_POSITION_JUMP_WITHOUT_EVIDENCE
                        ) * (5.5 if chord_confidence < 0.75 else 2.0)

                next_beam.append((cost, path + [candidate]))

        next_beam.sort(key=lambda item: item[0])
        beam = next_beam[:PHRASE_BEAM_WIDTH]

    rescored = [
        (
            base_cost + whole_path_adjustment(path, transcription_type),
            path,
        )
        for base_cost, path in beam
    ]
    rescored.sort(key=lambda item: item[0])
    return rescored[:TOP_PATHS]


def render_path(
    path: list[list[tuple[dict[str, Any], int, int]]],
    chord_name: str | None,
    chord_confidence: float,
) -> list[list[dict[str, Any]]]:
    mapped: list[list[dict[str, Any]]] = []
    for assignment in path:
        group: list[dict[str, Any]] = []
        for note, string_index, fret in assignment:
            bend = engine.estimate_bend_semitones(note.get("pitchBends"))
            group.append({
                **note,
                "stringIndex": int(string_index),
                "fret": int(fret),
                "technique": "bend" if bend >= 0.35 else None,
                "bendSemitones": round(float(bend), 2),
                "harmonicContext": chord_name,
                "harmonicConfidence": round(float(chord_confidence), 3),
            })
        mapped.append(group)
    return mapped


def path_debug_summary(
    score: float,
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> dict[str, Any]:
    compact_path = []
    for assignment in path:
        compact_path.append([
            {
                "midi": int(note["midi"]),
                "stringIndex": int(string_index),
                "fret": int(fret),
            }
            for note, string_index, fret in assignment
        ])
    return {
        "score": round(float(score), 3),
        "metrics": path_metrics(path),
        "path": compact_path,
    }


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
    windows = previous.flatten_windows(phrases, transcription_type)
    chord_sequence = previous.choose_chord_sequence(
        windows,
        transcription_type,
    )

    mapped_groups: list[list[dict[str, Any]]] = []
    anchors: list[int] = []
    detected_chords: list[str | None] = []
    chord_confidences: list[float] = []
    candidate_diagnostics: list[dict[str, Any]] = []
    previous_assignment = None
    previous_anchor = None

    for index, (window, chord_info) in enumerate(
        zip(windows, chord_sequence)
    ):
        chord_name, chord_map, chord_confidence = chord_info
        anchor = previous.previous.previous.choose_window_anchor(
            window,
            transcription_type,
            previous_anchor,
        )
        if chord_name and chord_confidence >= previous.MIN_STRONG_CHORD_CONFIDENCE:
            anchor = min(anchor, 2)

        candidates = window_path_candidates(
            window,
            transcription_type,
            anchor,
            previous_assignment,
            previous_anchor,
            chord_name,
            chord_map,
            chord_confidence,
        )
        if not candidates:
            continue

        winning_score, winning_path = candidates[0]
        mapped_groups.extend(
            render_path(
                winning_path,
                chord_name,
                chord_confidence,
            )
        )
        previous_assignment = winning_path[-1] if winning_path else previous_assignment
        previous_anchor = anchor

        anchors.append(anchor)
        detected_chords.append(chord_name)
        chord_confidences.append(round(float(chord_confidence), 3))
        candidate_diagnostics.append({
            "windowIndex": index,
            "anchor": anchor,
            "chord": chord_name,
            "chordConfidence": round(float(chord_confidence), 3),
            "candidates": [
                path_debug_summary(score, path)
                for score, path in candidates
            ],
            "winningScore": round(float(winning_score), 3),
        })

    generated_tab = engine.create_tab(mapped_groups, transcription_type)
    flattened = [event for group in mapped_groups for event in group]
    techniques = sorted({
        event["technique"]
        for event in flattened
        if event.get("technique")
    })

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
        "harmonicWindowCount": len(windows),
        "phraseAnchors": anchors,
        "detectedChords": detected_chords,
        "chordConfidences": chord_confidences,
        "candidateDiagnostics": candidate_diagnostics,
        "engineVersion": "2.3-whole-path-candidate-diagnostics",
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
        raise HTTPException(
            status_code=401,
            detail="Unauthorized analyzer request.",
        )

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

    headers: dict[str, str] = {}
    blob_token = str(payload.get("blobToken") or "").strip()
    if blob_token:
        headers["Authorization"] = f"Bearer {blob_token}"

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
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

        result["audioMetadata"] = original_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }

    return to_json_safe(result)
