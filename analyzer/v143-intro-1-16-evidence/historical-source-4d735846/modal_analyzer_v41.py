import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v40 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v40")

v25 = previous.v25
LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def is_low_bass(
    assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> bool:
    return previous.is_unavoidable_low_bass_group(assignment)


def upper_center(
    assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> float | None:
    if not assignment:
        return None
    frets = [
        int(fret)
        for note, _, fret in assignment
        if int(note["midi"]) > LOW_BASS_MIDI_MAX and int(fret) > 0
    ]
    return float(statistics.median(frets)) if frets else None


def upper_memory_cost(
    upper_memory: list[tuple[dict[str, Any], int, int]] | None,
    current: list[tuple[dict[str, Any], int, int]],
    anchor: int,
) -> float:
    """Score upper voices against their own persistent hand-position memory."""
    if not upper_memory or is_low_bass(current):
        return 0.0

    prior_center = upper_center(upper_memory)
    current_center = upper_center(current)
    if prior_center is None or current_center is None:
        return 0.0

    cost = 0.0
    shift = abs(current_center - prior_center)
    cost += shift * 2.8

    # A stable mid-neck arpeggio must not be reset by an intervening bass reach.
    if prior_center >= 4.0 and current_center <= 2.0:
        cost += 16.0 + (prior_center - 4.0) * 2.2

    if prior_center >= 4.0 and current_center >= 4.0:
        cost -= max(0.0, 5.0 - shift) * 1.4

    # Shared upper-string locations are strong evidence of a held chord shape.
    prior_map = {
        int(string_index): int(fret)
        for note, string_index, fret in upper_memory
        if int(note["midi"]) > LOW_BASS_MIDI_MAX
    }
    current_map = {
        int(string_index): int(fret)
        for note, string_index, fret in current
        if int(note["midi"]) > LOW_BASS_MIDI_MAX
    }
    shared = sum(
        1
        for string_index in set(prior_map) & set(current_map)
        if prior_map[string_index] == current_map[string_index]
    )
    cost -= shared * 2.2

    # The phrase anchor remains a secondary guide, not a replacement for memory.
    cost += abs(current_center - float(anchor)) * 0.35
    return cost


def dual_memory_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    """Beam search with independent bass and upper-voice position memories."""
    initial_upper = None if is_low_bass(previous_assignment) else previous_assignment
    beam: list[
        tuple[
            float,
            list[list[tuple[dict[str, Any], int, int]]],
            list[tuple[dict[str, Any], int, int]] | None,
        ]
    ] = [(0.0, [], initial_upper)]

    for group in groups:
        assignments = v25.all_group_assignments(group, transcription_type, anchor)
        if not assignments:
            assignments = v25.previous.previous.previous.previous.previous.group_assignments(
                group,
                transcription_type,
                anchor,
            )

        next_beam: list[
            tuple[
                float,
                list[list[tuple[dict[str, Any], int, int]]],
                list[tuple[dict[str, Any], int, int]] | None,
            ]
        ] = []

        for accumulated, path, upper_memory in beam:
            prior = path[-1] if path else previous_assignment
            for assignment in assignments:
                cost = accumulated
                cost += v25.guitarist_assignment_cost(
                    assignment,
                    transcription_type,
                    anchor,
                )
                cost += v25.phrase_movement_cost(prior, assignment, anchor)
                cost += upper_memory_cost(upper_memory, assignment, anchor)

                next_upper = upper_memory if is_low_bass(assignment) else assignment
                next_beam.append((cost, path + [assignment], next_upper))

        next_beam.sort(key=lambda item: item[0])
        beam = next_beam[: max(int(v25.PATH_BEAM_WIDTH), 96)]

    rescored: list[
        tuple[float, list[list[tuple[dict[str, Any], int, int]]]]
    ] = []
    for base_cost, path, _ in beam:
        metrics = v25.previous.previous.path_metrics(path)
        total = base_cost
        total += metrics["positionShiftTotal"] * 1.2
        total += metrics["largeShiftCount"] * 8.0
        total -= metrics["repeatConsistency"] * 5.5
        rescored.append((total, path))

    rescored.sort(key=lambda item: item[0])
    return rescored[:4]


# Replace the phrase beam itself so the second memory exists inside every path.
v25.build_phrase_paths = dual_memory_build_phrase_paths
v25.PATH_BEAM_WIDTH = max(int(getattr(v25, "PATH_BEAM_WIDTH", 88)), 96)


def summarize_dual_memory(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "bassMemory": "updates-on-low-bass-groups",
        "upperVoiceMemory": "updates-only-on-upper-or-mixed-groups",
        "beamWidth": int(v25.PATH_BEAM_WIDTH),
        "policy": (
            "temporary-low-bass-reaches-never-reset-the-persistent-upper-voice-anchor"
        ),
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["dualPositionMemory"] = summarize_dual_memory(result)
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "4.1-phase-1-dual-position-memory"
    result["guitarBrainLesson"] = (
        "remember-bass-reaches-and-upper-arpeggio-position-independently"
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
        raise HTTPException(
            status_code=400,
            detail="transcriptionType must be lead, rhythm, or bass.",
        )
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
