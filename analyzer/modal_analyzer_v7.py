from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import modal

try:
    from modal_analyzer import (
        MAX_AUDIO_SIZE_BYTES,
        analyze_audio_file as _analyze_audio_file_v6,
        inspect_audio_file,
        normalize_audio_file,
        validate_audio_metadata,
    )
    from production_chord_diagnostics import (
        attach_rhythm_chord_diagnostics,
    )
except ImportError:
    from analyzer.modal_analyzer import (
        MAX_AUDIO_SIZE_BYTES,
        analyze_audio_file as _analyze_audio_file_v6,
        inspect_audio_file,
        normalize_audio_file,
        validate_audio_metadata,
    )
    from analyzer.production_chord_diagnostics import (
        attach_rhythm_chord_diagnostics,
    )


app = modal.App("dadrock-tab-analyzer")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "basic-pitch",
        "fastapi[standard]",
        "requests",
    )
    .add_local_python_source(
        "modal_analyzer",
        "production_chord_diagnostics",
        "chord_sustain",
    )
)


def analyze_audio_file(
    audio_path: str,
    transcription_type: str,
) -> dict[str, Any]:
    """Run V6 production analysis, then attach read-only V7 diagnostics."""

    result = _analyze_audio_file_v6(
        audio_path,
        transcription_type,
    )

    return attach_rhythm_chord_diagnostics(
        result,
        transcription_type,
    )


@app.function(
    image=image,
    timeout=600,
    memory=4096,
    secrets=[
        modal.Secret.from_name(
            "dadrock-analyzer-secret"
        )
    ],
)
@modal.fastapi_endpoint(method="POST")
def analyze(payload: dict) -> dict:
    import requests
    from fastapi import HTTPException

    expected_token = os.environ.get("ANALYZER_API_TOKEN")
    supplied_token = str(payload.get("token") or "")

    if (
        not expected_token
        or supplied_token != expected_token
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized analyzer request.",
        )

    audio_url = str(
        payload.get("audioUrl") or ""
    ).strip()
    transcription_type = str(
        payload.get("transcriptionType") or ""
    ).strip().lower()

    if transcription_type not in {
        "lead",
        "rhythm",
        "bass",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "transcriptionType must be "
                "lead, rhythm, or bass."
            ),
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

    blob_token = str(
        payload.get("blobToken") or ""
    ).strip()
    request_headers: dict[str, str] = {}

    if blob_token:
        request_headers["Authorization"] = (
            f"Bearer {blob_token}"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"uploaded{suffix}"

        try:
            response = requests.get(
                audio_url,
                headers=request_headers,
                timeout=120,
            )
        except requests.RequestException as error:
            raise HTTPException(
                status_code=502,
                detail=(
                    "The analyzer could not "
                    "download the audio file."
                ),
            ) from error

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail=(
                    "The analyzer could not "
                    "download the audio file."
                ),
            )

        if len(response.content) > MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=(
                    "The uploaded audio cannot "
                    "be larger than 50 MB."
                ),
            )

        audio_path.write_bytes(response.content)

        try:
            audio_metadata = inspect_audio_file(
                str(audio_path)
            )
            validate_audio_metadata(audio_metadata)

            normalized_path = (
                Path(temp_dir) / "normalized.wav"
            )
            normalize_audio_file(
                str(audio_path),
                str(normalized_path),
            )
            normalized_metadata = inspect_audio_file(
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

        result["audioMetadata"] = audio_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }

    return result
