from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Callable

import modal
import modal_analyzer as legacy


HTTP_APP_NAME = "dadrock-v143-http-bridge"
WORKER_APP_NAME = "dadrock-v143-ai-tab-live"
WORKER_FUNCTION_NAME = "rhythm_v143_request"

app = modal.App(HTTP_APP_NAME)

LegacyHandler = Callable[[dict[str, Any]], dict[str, Any]]
RhythmHandler = Callable[[dict[str, Any]], dict[str, Any]]

# Keep the public HTTP container deliberately lightweight. It owns the existing
# Lead/Bass analyzer and dispatch only. The heavy V143 GPU image remains deployed
# in WORKER_APP_NAME and is looked up by name at request time.
http_image = legacy.image.add_local_python_source("modal_analyzer")


def dispatch_authorized_request(
    payload: dict[str, Any],
    *,
    expected_token: str,
    legacy_handler: LegacyHandler,
    rhythm_handler: RhythmHandler,
) -> dict[str, Any]:
    supplied_token = str(payload.get("token") or "")
    if not expected_token or supplied_token != expected_token:
        raise PermissionError("Unauthorized analyzer request.")

    transcription_type = str(
        payload.get("transcriptionType") or ""
    ).strip().lower()
    if transcription_type not in {"lead", "rhythm", "bass"}:
        raise ValueError("transcriptionType must be lead, rhythm, or bass.")

    audio_url = str(payload.get("audioUrl") or "").strip()
    if not audio_url.startswith(("https://", "http://")):
        raise ValueError("A valid audioUrl is required.")

    if transcription_type == "rhythm":
        return rhythm_handler(dict(payload))

    return legacy_handler(dict(payload))


def route_http_payload(
    payload: dict[str, Any],
    *,
    expected_token: str,
    legacy_handler: LegacyHandler,
    rhythm_handler: RhythmHandler,
) -> dict[str, Any]:
    """Pure dispatch seam used by the deployed endpoint and local verifier."""
    return dispatch_authorized_request(
        payload,
        expected_token=expected_token,
        legacy_handler=legacy_handler,
        rhythm_handler=rhythm_handler,
    )


def _download_blob_to_path(
    audio_url: str,
    blob_token: str,
    destination: Path,
) -> None:
    import requests

    headers: dict[str, str] = {}
    if blob_token:
        headers["Authorization"] = f"Bearer {blob_token}"

    try:
        response = requests.get(
            audio_url,
            headers=headers,
            timeout=120,
        )
    except requests.RequestException as error:
        raise RuntimeError(
            "The analyzer could not download the audio file."
        ) from error

    if not response.ok:
        raise RuntimeError(
            "The analyzer could not download the audio file."
        )

    if len(response.content) > legacy.MAX_AUDIO_SIZE_BYTES:
        raise ValueError(
            "The uploaded audio cannot be larger than 50 MB."
        )

    destination.write_bytes(response.content)


def _legacy_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Run Lead/Bass through the exact existing modal_analyzer functions."""
    audio_url = str(payload.get("audioUrl") or "").strip()
    blob_token = str(payload.get("blobToken") or "").strip()
    transcription_type = str(
        payload.get("transcriptionType") or ""
    ).strip().lower()

    suffix = Path(audio_url).suffix.lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        suffix = ".audio"

    with tempfile.TemporaryDirectory(prefix="dadrock-legacy-") as temp_dir:
        root = Path(temp_dir)
        audio_path = root / f"uploaded{suffix}"
        normalized_path = root / "normalized.wav"

        _download_blob_to_path(audio_url, blob_token, audio_path)
        audio_metadata = legacy.inspect_audio_file(str(audio_path))
        legacy.validate_audio_metadata(audio_metadata)
        legacy.normalize_audio_file(str(audio_path), str(normalized_path))
        normalized_metadata = legacy.inspect_audio_file(str(normalized_path))
        result = legacy.analyze_audio_file(
            str(normalized_path),
            transcription_type,
        )

    result["audioMetadata"] = audio_metadata
    result["normalizedAudio"] = {
        "sampleRate": normalized_metadata["sampleRate"],
        "channels": normalized_metadata["channels"],
        "codec": normalized_metadata["codec"],
        "formatName": normalized_metadata["formatName"],
    }
    return result


@app.function(
    image=http_image,
    timeout=1200,
    memory=4096,
    secrets=[
        modal.Secret.from_name("dadrock-analyzer-secret")
    ],
)
@modal.fastapi_endpoint(method="POST")
def analyze(payload: dict) -> dict:
    """Production HTTP bridge used by Vercel's /api/analyze-audio-tab route.

    Lead and Bass execute the existing modal_analyzer implementation in this
    lightweight web container. Rhythm is forwarded across the app boundary to
    the already-deployed frozen V143 L4 worker. Keeping those apps separate
    prevents the web container from importing/building the GPU separator stack.
    """
    from fastapi import HTTPException

    expected_token = str(
        os.environ.get("ANALYZER_API_TOKEN") or ""
    )

    def rhythm_handler(routed_payload: dict[str, Any]) -> dict[str, Any]:
        worker = modal.Function.from_name(
            WORKER_APP_NAME,
            WORKER_FUNCTION_NAME,
        )
        return worker.remote(routed_payload)

    try:
        result = route_http_payload(
            dict(payload or {}),
            expected_token=expected_token,
            legacy_handler=_legacy_request,
            rhythm_handler=rhythm_handler,
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="The analyzer could not complete the request.",
        ) from error

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=502,
            detail="The analyzer returned an invalid response.",
        )
    if not str(result.get("generatedTab") or "").strip():
        raise HTTPException(
            status_code=502,
            detail="The analyzer returned no tablature.",
        )

    return result


__all__ = [
    "HTTP_APP_NAME",
    "WORKER_APP_NAME",
    "WORKER_FUNCTION_NAME",
    "analyze",
    "http_image",
    "route_http_payload",
]
