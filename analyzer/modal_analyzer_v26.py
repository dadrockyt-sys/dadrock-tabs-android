import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v25 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v25")


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def local_chord_shape_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    """Self-contained playability score for one simultaneous note group."""
    if not assignment:
        return 0.0

    strings = [int(string_index) for _, string_index, _ in assignment]
    frets = [int(fret) for _, _, fret in assignment]
    fretted = [fret for fret in frets if fret > 0]
    cost = 0.0

    if len(set(strings)) != len(strings):
        return 1000.0

    if fretted:
        median_fret = float(statistics.median(fretted))
        span = max(fretted) - min(fretted)
        cost += abs(median_fret - float(anchor)) * 0.9
        cost += span * 1.35

        if span > 4:
            cost += (span - 4) * 7.0
        if max(fretted) > 17:
            cost += (max(fretted) - 17) * 2.5

    if len(strings) >= 2:
        string_span = max(strings) - min(strings)
        missing_strings = string_span + 1 - len(set(strings))
        cost += string_span * 0.3
        cost += missing_strings * 2.4

    open_count = sum(1 for fret in frets if fret == 0)
    if transcription_type != "bass":
        if anchor <= 2:
            cost -= min(open_count, 3) * 0.65
        elif open_count:
            cost += open_count * 1.5

    return cost


def corrected_guitarist_assignment_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    cost = local_chord_shape_cost(
        assignment,
        transcription_type,
        anchor,
    )

    frets = [int(item[2]) for item in assignment]
    strings = [int(item[1]) for item in assignment]
    non_open = [fret for fret in frets if fret > 0]

    if non_open:
        span = max(non_open) - min(non_open)
        if span > 4:
            cost += (span - 4) * 7.0
        if statistics.median(non_open) > 12 and anchor < 10:
            cost += 5.0

    if len(strings) >= 2:
        gaps = max(strings) - min(strings) + 1 - len(set(strings))
        cost += gaps * 2.3

    highest = max(assignment, key=lambda item: int(item[0]["midi"]))
    if transcription_type == "lead":
        if highest[1] <= 2:
            cost -= 1.5
        else:
            cost += 1.4

    return cost


# V25 accidentally followed the import chain to v21 for chord_shape_cost.
# Replace that scoring callback with the self-contained v26 implementation.
previous.guitarist_assignment_cost = corrected_guitarist_assignment_cost


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    result["engineVersion"] = "2.6-self-contained-phrase-scoring"
    result["scoringFix"] = "local-chord-shape-cost"
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
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
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
