import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v15 as engine

app = modal.App("dadrock-tab-analyzer")
image = engine.image.add_local_python_source("modal_analyzer_v15")


def to_json_safe(value: Any) -> Any:
    """Convert NumPy and other model values into JSON-safe Python types."""
    if value is None or isinstance(value, (str, bool, int, float)):
        return value

    if isinstance(value, dict):
        return {
            str(key): to_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(item) for item in value]

    # NumPy scalar values such as numpy.int64 and numpy.float32.
    item_method = getattr(value, "item", None)
    if callable(item_method):
        try:
            return to_json_safe(item_method())
        except (TypeError, ValueError):
            pass

    # NumPy arrays and similar containers.
    tolist_method = getattr(value, "tolist", None)
    if callable(tolist_method):
        try:
            return to_json_safe(tolist_method())
        except (TypeError, ValueError):
            pass

    return str(value)


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

    blob_token = str(payload.get("blobToken") or "").strip()
    headers: dict[str, str] = {}

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
            original_metadata = engine.inspect_audio_file(
                str(audio_path)
            )
            engine.validate_audio_metadata(original_metadata)

            normalized_path = Path(temp_dir) / "normalized.wav"
            engine.normalize_audio_file(
                str(audio_path),
                str(normalized_path),
            )
            normalized_metadata = engine.inspect_audio_file(
                str(normalized_path)
            )

            result = engine.analyze_audio_file(
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
