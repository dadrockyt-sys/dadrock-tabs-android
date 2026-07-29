import itertools
import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v47 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v47")

v25 = previous.v25
LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX
_original_render_path = v25.render_path
_LOCAL_CORRECTIONS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def upper_frets(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> list[int]:
    return [
        int(fret)
        for note, _, fret in assignment
        if int(note.get("midi") or 0) > LOW_BASS_MIDI_MAX and int(fret) > 0
    ]


def upper_center(
    assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> float | None:
    if not assignment:
        return None
    frets = upper_frets(assignment)
    return float(statistics.median(frets)) if frets else None


def mid_positions(
    note: dict[str, Any],
    transcription_type: str,
) -> list[tuple[int, int]]:
    return [
        (int(string_index), int(fret))
        for string_index, fret in engine.playable_positions(
            int(note["midi"]),
            transcription_type,
        )
        if 4 <= int(fret) <= 9
    ]


def candidate_group_score(
    candidate: list[tuple[dict[str, Any], int, int]],
    previous_center: float | None,
    next_center: float | None,
) -> float:
    frets = upper_frets(candidate)
    if not frets:
        return 0.0

    center = float(statistics.median(frets))
    target_centers = [value for value in (previous_center, next_center) if value is not None and value <= 9.0]
    target = float(statistics.median(target_centers)) if target_centers else 6.5

    score = abs(center - target) * 4.0
    score += max(0, max(frets) - min(frets) - 3) * 4.0
    score += max(0.0, center - 8.0) * 5.0

    # Higher notes should normally live on physically higher strings. String index
    # zero is high E, so MIDI pitch and string index should move in opposite directions.
    ordered = sorted(
        (
            int(note["midi"]),
            int(string_index),
        )
        for note, string_index, _ in candidate
        if int(note.get("midi") or 0) > LOW_BASS_MIDI_MAX
    )
    for (midi_a, string_a), (midi_b, string_b) in zip(ordered, ordered[1:]):
        if midi_b > midi_a and string_b > string_a:
            score += 8.0

    return score


def correct_high_assignment(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    previous_center: float | None,
    next_center: float | None,
) -> tuple[list[tuple[dict[str, Any], int, int]], dict[str, Any] | None]:
    original_center = upper_center(assignment)
    if original_center is None or original_center <= 8.0:
        return assignment, None

    upper_items = [
        (index, note, int(string_index), int(fret))
        for index, (note, string_index, fret) in enumerate(assignment)
        if int(note.get("midi") or 0) > LOW_BASS_MIDI_MAX
    ]
    if not upper_items:
        return assignment, None

    position_sets = [mid_positions(note, transcription_type) for _, note, _, _ in upper_items]
    if any(not positions for positions in position_sets):
        return assignment, None

    best_assignment: list[tuple[dict[str, Any], int, int]] | None = None
    best_score = float("inf")

    for combination in itertools.product(*position_sets):
        strings = [string_index for string_index, _ in combination]
        if len(strings) != len(set(strings)):
            continue

        candidate = list(assignment)
        for (item_index, note, _, _), (string_index, fret) in zip(upper_items, combination):
            candidate[item_index] = (note, int(string_index), int(fret))

        score = candidate_group_score(candidate, previous_center, next_center)
        if score < best_score:
            best_score = score
            best_assignment = candidate

    if best_assignment is None:
        return assignment, None

    corrected_center = upper_center(best_assignment)
    if corrected_center is None or corrected_center >= original_center:
        return assignment, None

    return best_assignment, {
        "originalCenter": round(original_center, 3),
        "correctedCenter": round(corrected_center, 3),
        "original": [
            {
                "midi": int(note.get("midi") or 0),
                "stringIndex": int(string_index),
                "fret": int(fret),
            }
            for note, string_index, fret in assignment
        ],
        "corrected": [
            {
                "midi": int(note.get("midi") or 0),
                "stringIndex": int(string_index),
                "fret": int(fret),
            }
            for note, string_index, fret in best_assignment
        ],
    }


def locally_corrected_render_path(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> list[list[dict[str, Any]]]:
    corrected_path: list[list[tuple[dict[str, Any], int, int]]] = []

    for group_index, assignment in enumerate(path):
        previous_center = upper_center(corrected_path[-1]) if corrected_path else None
        next_center = upper_center(path[group_index + 1]) if group_index + 1 < len(path) else None
        corrected, diagnostic = correct_high_assignment(
            assignment,
            "lead",
            previous_center,
            next_center,
        )
        corrected_path.append(corrected)
        if diagnostic is not None:
            _LOCAL_CORRECTIONS.append(
                {
                    "groupIndex": group_index,
                    "start": round(
                        min(float(note.get("start") or 0.0) for note, _, _ in assignment),
                        4,
                    ),
                    **diagnostic,
                }
            )

    return _original_render_path(corrected_path)


v25.render_path = locally_corrected_render_path


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _LOCAL_CORRECTIONS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["localHighIslandCorrections"] = {
        "benchmarkBaseline": 63.0,
        "correctionCount": len(_LOCAL_CORRECTIONS),
        "corrections": list(_LOCAL_CORRECTIONS),
        "policy": (
            "after-the-winning-window-path-is-selected-remap-only-local-groups-"
            "whose-upper-median-exceeds-eight-when-the-same-pitches-have-a-compact-"
            "four-to-nine-fret-realization"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "5.5-phase-1-local-high-island-correction"
    result["guitarBrainLesson"] = (
        "keep-the-winning-harmonic-window-but-lower-small-high-position-islands-"
        "into-the-nearest-playable-mid-neck-shape"
    )
    return result


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
