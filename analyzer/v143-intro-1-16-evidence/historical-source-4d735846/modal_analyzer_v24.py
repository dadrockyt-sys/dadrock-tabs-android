import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v23 as previous

base = previous.base
engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v23")

TOP_PATHS = 4
ANCHOR_CANDIDATES = (0, 2, 5, 7)


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def arpeggio_texture(window: list[list[dict[str, Any]]]) -> float:
    """Estimate whether a passage behaves like a ringing acoustic arpeggio."""
    groups = [group for group in window if group]
    if not groups:
        return 0.0

    single_ratio = sum(1 for group in groups if len(group) == 1) / len(groups)
    overlap_hits = 0
    overlap_total = 0
    for current, nxt in zip(groups, groups[1:]):
        current_end = max(float(note.get("end") or note["start"]) for note in current)
        next_start = min(float(note["start"]) for note in nxt)
        overlap_total += 1
        if current_end > next_start + 0.03:
            overlap_hits += 1

    overlap_ratio = overlap_hits / max(overlap_total, 1)
    return min(1.0, single_ratio * 0.65 + overlap_ratio * 0.35)


def style_metrics(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> dict[str, float]:
    notes = [item for assignment in path for item in assignment]
    if not notes:
        return {
            "upperStringRatio": 0.0,
            "bassTrebleAlternation": 0.0,
            "closedPositionRatio": 0.0,
            "openChordRatio": 0.0,
            "compactSpan": 0.0,
        }

    upper = sum(1 for _, string_index, _ in notes if string_index <= 2)
    open_notes = sum(1 for _, _, fret in notes if fret == 0)
    closed_notes = sum(1 for _, _, fret in notes if 4 <= fret <= 9)

    alternations = 0
    opportunities = 0
    prior_zone = None
    for assignment in path:
        if not assignment:
            continue
        mean_string = statistics.mean(item[1] for item in assignment)
        zone = "treble" if mean_string <= 2.5 else "bass"
        if prior_zone is not None:
            opportunities += 1
            if zone != prior_zone:
                alternations += 1
        prior_zone = zone

    frets = [fret for _, _, fret in notes if fret > 0]
    span = max(frets) - min(frets) if frets else 0
    compact = max(0.0, 1.0 - span / 8.0)

    return {
        "upperStringRatio": round(upper / len(notes), 3),
        "bassTrebleAlternation": round(alternations / max(opportunities, 1), 3),
        "closedPositionRatio": round(closed_notes / len(notes), 3),
        "openChordRatio": round(open_notes / len(notes), 3),
        "compactSpan": round(compact, 3),
    }


def classic_rock_arpeggio_adjustment(
    path: list[list[tuple[dict[str, Any], int, int]]],
    texture: float,
    chord_confidence: float,
) -> float:
    """General classic-rock acoustic heuristics, not song-specific tablature."""
    metrics = style_metrics(path)
    cost = 0.0

    # Closed arpeggios commonly live around frets 5-8 and alternate bass/treble.
    if texture >= 0.55:
        cost -= metrics["closedPositionRatio"] * 3.2
        cost -= metrics["bassTrebleAlternation"] * 2.2
        cost -= metrics["upperStringRatio"] * 1.0
        cost -= metrics["compactSpan"] * 1.4

    # Open strings should win only when harmonic evidence strongly supports them.
    if chord_confidence >= 0.72:
        if 0.08 <= metrics["openChordRatio"] <= 0.48:
            cost -= metrics["openChordRatio"] * 2.0
    elif metrics["openChordRatio"] > 0.22:
        cost += (metrics["openChordRatio"] - 0.22) * 7.0

    return cost


def candidate_anchors(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
    previous_anchor: int | None,
    chord_confidence: float,
) -> list[int]:
    inferred = previous.previous.previous.previous.choose_window_anchor(
        window,
        transcription_type,
        previous_anchor,
    )
    anchors = [inferred]

    if transcription_type != "bass":
        anchors.extend(ANCHOR_CANDIDATES)
        if chord_confidence >= 0.72:
            anchors.extend([0, 2])
        if arpeggio_texture(window) >= 0.55:
            anchors.extend([5, 7])

    if previous_anchor is not None:
        anchors.append(previous_anchor)

    result: list[int] = []
    for anchor in anchors:
        anchor = max(0, min(17, int(anchor)))
        if anchor not in result:
            result.append(anchor)
    return result


def style_path_candidates(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
    previous_anchor: int | None,
    chord_name: str | None,
    chord_map: dict[int, tuple[int, int]],
    chord_confidence: float,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    candidates = previous.window_path_candidates(
        window,
        transcription_type,
        anchor,
        previous_assignment,
        previous_anchor,
        chord_name,
        chord_map,
        chord_confidence,
    )
    texture = arpeggio_texture(window)
    rescored = [
        (
            score + classic_rock_arpeggio_adjustment(
                path,
                texture,
                chord_confidence,
            ),
            path,
        )
        for score, path in candidates
    ]
    rescored.sort(key=lambda item: item[0])
    return rescored


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
    windows = previous.previous.flatten_windows(phrases, transcription_type)
    chord_sequence = previous.previous.choose_chord_sequence(
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

    for index, (window, chord_info) in enumerate(zip(windows, chord_sequence)):
        chord_name, chord_map, chord_confidence = chord_info
        all_candidates: list[
            tuple[float, int, list[list[tuple[dict[str, Any], int, int]]]]
        ] = []

        for anchor in candidate_anchors(
            window,
            transcription_type,
            previous_anchor,
            chord_confidence,
        ):
            for score, path in style_path_candidates(
                window,
                transcription_type,
                anchor,
                previous_assignment,
                previous_anchor,
                chord_name,
                chord_map,
                chord_confidence,
            ):
                all_candidates.append((score, anchor, path))

        if not all_candidates:
            continue

        # Deduplicate full paths produced from different anchors.
        unique: dict[tuple, tuple[float, int, list]] = {}
        for score, anchor, path in all_candidates:
            key = tuple(previous.assignment_key(assignment) for assignment in path)
            current = unique.get(key)
            if current is None or score < current[0]:
                unique[key] = (score, anchor, path)

        ranked = sorted(unique.values(), key=lambda item: item[0])[:TOP_PATHS]
        winning_score, winning_anchor, winning_path = ranked[0]

        mapped_groups.extend(
            previous.render_path(
                winning_path,
                chord_name,
                chord_confidence,
            )
        )
        previous_assignment = winning_path[-1] if winning_path else previous_assignment
        previous_anchor = winning_anchor

        anchors.append(winning_anchor)
        detected_chords.append(chord_name)
        chord_confidences.append(round(float(chord_confidence), 3))
        candidate_diagnostics.append({
            "windowIndex": index,
            "texture": round(arpeggio_texture(window), 3),
            "chosenAnchor": winning_anchor,
            "chord": chord_name,
            "chordConfidence": round(float(chord_confidence), 3),
            "candidates": [
                {
                    **previous.path_debug_summary(score, path),
                    "anchor": anchor,
                    "styleMetrics": style_metrics(path),
                }
                for score, anchor, path in ranked
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
        "candidateDiagnostics": candidate_diagnostics,
        "styleProfile": "classic-rock-acoustic-arpeggio",
        "engineVersion": "2.4-multi-anchor-classic-rock-guitar-intelligence",
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
