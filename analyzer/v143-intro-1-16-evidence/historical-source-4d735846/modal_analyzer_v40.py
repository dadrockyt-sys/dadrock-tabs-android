import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v39 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v39")

# Reach the active Phase 1 beam-search callbacks.
v38 = previous.previous
v37 = v38.previous
v36 = v37.previous
v25 = v36.v25

LOW_BASS_MIDI_MAX = 43


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def is_unavoidable_low_bass_group(
    assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> bool:
    """Return True when a group is only a very low guitar bass note.

    Notes such as MIDI 41 have no mid-neck equivalent in standard tuning. They
    must not be allowed to redefine the left-hand anchor for the upper arpeggio.
    """
    if not assignment:
        return False
    return all(int(note["midi"]) <= LOW_BASS_MIDI_MAX for note, _, _ in assignment)


def upper_voice_center(
    assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> float | None:
    if not assignment:
        return None

    upper_frets = [
        int(fret)
        for note, _, fret in assignment
        if int(note["midi"]) > LOW_BASS_MIDI_MAX and int(fret) > 0
    ]
    if upper_frets:
        return float(statistics.median(upper_frets))

    fretted = [int(fret) for _, _, fret in assignment if int(fret) > 0]
    return float(statistics.median(fretted)) if fretted else 0.0


def bass_exception_transition_cost(
    prior: list[tuple[dict[str, Any], int, int]] | None,
    current: list[tuple[dict[str, Any], int, int]],
    anchor: int,
) -> float:
    """Preserve the upper-hand position across unavoidable low bass notes."""
    base_cost = v36.phrase_path_transition_cost(prior, current, anchor)

    prior_is_bass = is_unavoidable_low_bass_group(prior)
    current_is_bass = is_unavoidable_low_bass_group(current)

    # A single low bass note is played as a temporary reach or separate finger.
    # It should not be scored as though the entire fretting hand relocated.
    if current_is_bass and not prior_is_bass:
        current_fret = min(int(fret) for _, _, fret in current)
        if current_fret <= 3:
            base_cost -= 8.0
        return base_cost

    # When returning from a low bass note to the upper arpeggio, compare the new
    # upper voice with the established anchor rather than with the bass fret.
    if prior_is_bass and not current_is_bass:
        current_center = upper_voice_center(current)
        if current_center is not None:
            distance_to_anchor = abs(current_center - float(anchor))
            base_cost -= max(0.0, 9.0 - distance_to_anchor * 1.8)
            if current_center >= 4.0:
                base_cost -= 4.0
            elif int(anchor) >= 5:
                base_cost += 7.5
        return base_cost

    return base_cost


def bass_exception_assignment_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    cost = v36.candidate_harmony_cost(assignment, transcription_type, anchor)

    if is_unavoidable_low_bass_group(assignment):
        # Do not punish the only physically available location for a low note.
        lowest_fret = min(int(fret) for _, _, fret in assignment)
        if lowest_fret <= 3:
            cost -= 5.0
        return cost

    # For mixed or upper-voice groups, preserve the selected phrase region.
    center = upper_voice_center(assignment)
    if center is not None and int(anchor) >= 5:
        if center >= 4.0:
            cost -= min(4.0, 0.7 * (10.0 - abs(center - float(anchor))))
        elif center <= 2.0:
            cost += 8.0

    return cost


# Install the lesson at the actual V25 beam callbacks.
v25.guitarist_assignment_cost = bass_exception_assignment_cost
v25.phrase_movement_cost = bass_exception_transition_cost


def summarize_bass_exception_training(result: dict[str, Any]) -> dict[str, Any]:
    inventory = (
        result.get("musicalUnderstanding", {})
        .get("candidateInventory", {})
    )
    notes_without_mid = list(inventory.get("notesWithoutMidNeckPositions") or [])
    unavoidable = [
        item for item in notes_without_mid
        if int(item.get("midi") or 999) <= LOW_BASS_MIDI_MAX
    ]
    return {
        "lowBassThresholdMidi": LOW_BASS_MIDI_MAX,
        "unavoidableLowBassNotes": unavoidable,
        "count": len(unavoidable),
        "policy": (
            "low-bass-notes-without-mid-neck-equivalents-do-not-reset-"
            "the-upper-voice-hand-position"
        ),
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["bassPositionExceptions"] = summarize_bass_exception_training(result)
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "4.0-phase-1-low-bass-position-exceptions"
    result["guitarBrainLesson"] = (
        "keep-the-upper-arpeggio-hand-position-while-reaching-unavoidable-low-bass-notes"
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
