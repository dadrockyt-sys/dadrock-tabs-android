import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v41 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v41")

LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def upper_frets(
    assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[int]:
    if not assignment:
        return []
    return [
        int(fret)
        for note, _, fret in assignment
        if int(note["midi"]) > LOW_BASS_MIDI_MAX and int(fret) > 0
    ]


def bounded_upper_memory_cost(
    upper_memory: list[tuple[dict[str, Any], int, int]] | None,
    current: list[tuple[dict[str, Any], int, int]],
    anchor: int,
) -> float:
    """Keep upper voices near a realistic hand neighbourhood.

    V41 successfully preserved upper-position memory, but could reward any higher
    solution. This lesson treats the remembered position as a compact four-fret
    hand area and requires clear evidence before climbing beyond it.
    """
    cost = previous_upper_memory_cost(upper_memory, current, anchor)
    if previous.is_low_bass(current):
        return cost

    current_frets = upper_frets(current)
    if not current_frets:
        return cost

    current_center = float(statistics.median(current_frets))
    remembered_frets = upper_frets(upper_memory)
    remembered_center = (
        float(statistics.median(remembered_frets))
        if remembered_frets
        else float(anchor)
    )

    # A guitarist normally keeps the hand inside a four-to-five-fret box.
    lower_bound = max(1.0, remembered_center - 2.5)
    upper_bound = remembered_center + 3.0

    if current_center < lower_bound:
        cost += (lower_bound - current_center) * 4.0
    elif current_center > upper_bound:
        cost += (current_center - upper_bound) * 4.8
    else:
        cost -= 2.0

    # Strongly discourage the V41 overcorrection into frets 10-12 when the
    # phrase anchor and remembered shape live around frets 5-8.
    if remembered_center <= 8.5 and current_center >= 10.0:
        cost += 9.0 + (current_center - 10.0) * 3.5

    # Reward the classic compact mid-neck working area without hard-coding a song.
    if 4.0 <= remembered_center <= 9.0 and 4.0 <= current_center <= 9.0:
        cost -= 4.0

    # Penalize wide upper-voice shapes that exceed a normal four-fret hand span.
    span = max(current_frets) - min(current_frets)
    if span > 4:
        cost += (span - 4) * 5.0

    # Do not allow one high note to drag the entire chord shape upward.
    if max(current_frets) >= 12 and min(current_frets) <= 8:
        cost += 5.5

    return cost


# V41's beam function resolves this callback from its module globals at runtime.
previous_upper_memory_cost = previous.upper_memory_cost
previous.upper_memory_cost = bounded_upper_memory_cost


def summarize_neighbourhood_training(result: dict[str, Any]) -> dict[str, Any]:
    windows = (
        result.get("musicalUnderstanding", {})
        .get("harmonicWindows", [])
    )
    anchors = [
        int(window["chosenAnchor"])
        for window in windows
        if window.get("chosenAnchor") is not None
    ]
    return {
        "chosenAnchors": anchors,
        "preferredUpperRegion": "compact-mid-neck-when-established",
        "maximumComfortableSpanFrets": 4,
        "policy": (
            "preserve-dual-position-memory-but-confine-upper-voices-to-a-"
            "realistic-hand-neighbourhood-unless-the-melody-requires-a-shift"
        ),
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["upperHandNeighbourhood"] = summarize_neighbourhood_training(result)
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "4.2-phase-1-bounded-upper-hand-memory"
    result["guitarBrainLesson"] = (
        "keep-the-upper-hand-in-a-realistic-four-fret-neighbourhood-and-shift-only-when-needed"
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
