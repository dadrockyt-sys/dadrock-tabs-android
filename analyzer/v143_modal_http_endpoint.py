from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Callable

import modal
import modal_analyzer as legacy
from v143_async_job_protocol import (
    ASYNC_RESULT_TTL_SECONDS,
    build_completed_envelope,
    build_failed_envelope,
    build_job_token,
    create_job_id,
    decode_result_items,
    encode_result_envelope,
    parse_job_token,
)


HTTP_APP_NAME = str(
    os.environ.get("V143_HTTP_APP_NAME")
    or "dadrock-v143-http-bridge"
).strip()
WORKER_APP_NAME = "dadrock-v143-ai-tab-live"
WORKER_FUNCTION_NAME = "rhythm_v143_request"
ASYNC_RESULT_QUEUE_NAME = str(
    os.environ.get("V143_ASYNC_RESULT_QUEUE_NAME")
    or "dadrock-v143-async-results"
).strip()

if not HTTP_APP_NAME or not ASYNC_RESULT_QUEUE_NAME:
    raise RuntimeError("V143 async bridge resource names must not be empty.")

app = modal.App(HTTP_APP_NAME)

LegacyHandler = Callable[[dict[str, Any]], dict[str, Any]]
RhythmHandler = Callable[[dict[str, Any]], dict[str, Any]]

# Keep the public HTTP container deliberately lightweight. The resource names
# are resolved by the deploy process and then baked into the function image so
# isolated gate deployments retain their isolated Queue/app identity remotely.
http_image = (
    legacy.image.add_local_python_source("modal_analyzer")
    .add_local_python_source("v143_async_job_protocol")
    .env(
        {
            "V143_HTTP_APP_NAME": HTTP_APP_NAME,
            "V143_ASYNC_RESULT_QUEUE_NAME": ASYNC_RESULT_QUEUE_NAME,
        }
    )
)

# Queue entries are transient structured-result handoff only. Each partition is
# scoped to one random job id, is cleared after browser acknowledgement, and has
# a hard 15-minute TTL if the browser disappears. Raw audio/stems never enter it.
async_result_queue = modal.Queue.from_name(
    ASYNC_RESULT_QUEUE_NAME,
    create_if_missing=True,
)


def _authorize(payload: dict[str, Any], expected_token: str) -> None:
    supplied_token = str(payload.get("token") or "")
    if not expected_token or supplied_token != expected_token:
        raise PermissionError("Unauthorized analyzer request.")


def dispatch_authorized_request(
    payload: dict[str, Any],
    *,
    expected_token: str,
    legacy_handler: LegacyHandler,
    rhythm_handler: RhythmHandler,
) -> dict[str, Any]:
    _authorize(payload, expected_token)

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


def _worker_handle() -> modal.Function:
    return modal.Function.from_name(
        WORKER_APP_NAME,
        WORKER_FUNCTION_NAME,
    )


def _validate_rhythm_start_payload(payload: dict[str, Any]) -> None:
    transcription_type = str(
        payload.get("transcriptionType") or ""
    ).strip().lower()
    if transcription_type != "rhythm":
        raise ValueError("Async analyzer jobs are available only for rhythm.")

    audio_url = str(payload.get("audioUrl") or "").strip()
    pathname = str(payload.get("pathname") or "").strip()
    if not audio_url.startswith(("https://", "http://")):
        raise ValueError("A valid audioUrl is required.")
    if not pathname:
        raise ValueError("A Vercel Blob pathname is required.")


def _queue_job_envelope(job_id: str, envelope: dict[str, Any]) -> None:
    items = encode_result_envelope(envelope)
    async_result_queue.put_many(
        items,
        partition=job_id,
        partition_ttl=ASYNC_RESULT_TTL_SECONDS,
        timeout=30,
    )


@app.function(
    image=http_image,
    timeout=60,
    memory=512,
    secrets=[
        modal.Secret.from_name("dadrock-analyzer-secret")
    ],
)
def async_protocol_smoke() -> dict[str, Any]:
    """Exercise token + Queue transport without audio or model execution."""
    expected_token = str(
        os.environ.get("ANALYZER_API_TOKEN") or ""
    )
    job_id = create_job_id()
    job_token = build_job_token(job_id, expected_token)
    token_verified = parse_job_token(job_token, expected_token) == job_id

    synthetic_result = {
        "generatedTab": "e|--0--|",
        "liveV143": {
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "referenceRuntimeInputUsed": False,
            "runtimeLabelsRequired": False,
        },
    }
    _queue_job_envelope(
        job_id,
        build_completed_envelope(synthetic_result),
    )

    items = list(
        async_result_queue.iterate(
            partition=job_id,
            item_poll_timeout=0.0,
        )
    )
    decoded = decode_result_items(items)
    roundtrip_ok = (
        decoded.get("status") == "completed"
        and decoded.get("result") == synthetic_result
    )

    async_result_queue.clear(partition=job_id)
    remaining = list(
        async_result_queue.iterate(
            partition=job_id,
            item_poll_timeout=0.0,
        )
    )

    return {
        "appName": HTTP_APP_NAME,
        "queueName": ASYNC_RESULT_QUEUE_NAME,
        "tokenVerified": token_verified,
        "queueRoundtrip": roundtrip_ok,
        "queueCleared": not remaining,
        "resultTtlSeconds": ASYNC_RESULT_TTL_SECONDS,
        "rawAudioQueued": False,
        "stemBytesQueued": False,
        "modelExecuted": False,
        "audioRead": False,
        "referenceFacingInputs": 0,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
    }


@app.function(
    image=http_image,
    timeout=1200,
    memory=4096,
)
def run_rhythm_async_job(
    job_id: str,
    routed_payload: dict[str, Any],
) -> dict[str, Any]:
    """Run the existing V143 worker and publish only transient structured JSON."""
    status = "failed"
    try:
        result = _worker_handle().remote(dict(routed_payload))
        envelope = build_completed_envelope(result)
        status = "completed"
    except Exception:
        # Never persist exception repr/traceback because routed payloads contain
        # private Blob credentials. The browser gets a bounded generic failure.
        envelope = build_failed_envelope()

    try:
        _queue_job_envelope(job_id, envelope)
    except ValueError:
        # A result that crosses the strict JSON/size envelope is converted to a
        # bounded failure result rather than leaving the browser polling forever.
        status = "failed"
        _queue_job_envelope(job_id, build_failed_envelope())

    return {
        "jobId": job_id,
        "status": status,
        "resultQueued": True,
        "resultTtlSeconds": ASYNC_RESULT_TTL_SECONDS,
        "rawAudioQueued": False,
        "stemBytesQueued": False,
    }


def _start_rhythm_job(
    payload: dict[str, Any],
    *,
    expected_token: str,
) -> dict[str, Any]:
    _authorize(payload, expected_token)
    _validate_rhythm_start_payload(payload)

    job_id = create_job_id()
    job_token = build_job_token(job_id, expected_token)

    # Keep the already-authoritative Vercel payload contract. The bridge-side
    # orchestrator is lightweight and immediately releases this HTTP request.
    run_rhythm_async_job.spawn(job_id, dict(payload))

    return {
        "status": "processing",
        "jobToken": job_token,
        "pollAfterMs": 3000,
        "expiresInSeconds": ASYNC_RESULT_TTL_SECONDS,
        "rhythmOnly": True,
        "rawAudioQueued": False,
        "stemBytesQueued": False,
    }


def _status_rhythm_job(
    payload: dict[str, Any],
    *,
    expected_token: str,
) -> dict[str, Any]:
    _authorize(payload, expected_token)
    job_id = parse_job_token(
        str(payload.get("jobToken") or ""),
        expected_token,
    )

    items = list(
        async_result_queue.iterate(
            partition=job_id,
            item_poll_timeout=0.0,
        )
    )
    if not items:
        return {
            "status": "processing",
            "pollAfterMs": 3000,
            "expiresInSeconds": ASYNC_RESULT_TTL_SECONDS,
        }

    envelope = decode_result_items(items)
    status = str(envelope.get("status") or "")
    if status == "failed":
        return {
            "status": "failed",
            "error": str(
                envelope.get("error")
                or "The analyzer could not complete the request."
            )[:240],
        }
    if status != "completed" or not isinstance(envelope.get("result"), dict):
        raise RuntimeError("The async analyzer returned an invalid result envelope.")

    return {
        "status": "completed",
        "result": envelope["result"],
    }


def _ack_rhythm_job(
    payload: dict[str, Any],
    *,
    expected_token: str,
) -> dict[str, Any]:
    _authorize(payload, expected_token)
    job_id = parse_job_token(
        str(payload.get("jobToken") or ""),
        expected_token,
    )
    async_result_queue.clear(partition=job_id)
    return {
        "status": "acknowledged",
        "resultCleared": True,
    }


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

    Default `operation=analyze` preserves the existing synchronous Lead/Bass and
    Rhythm behavior for rollback/compatibility. Rhythm may additionally use the
    async `start`/`status`/`ack` protocol so Vercel never waits on model runtime.
    """
    from fastapi import HTTPException

    routed_payload = dict(payload or {})
    expected_token = str(
        os.environ.get("ANALYZER_API_TOKEN") or ""
    )
    operation = str(
        routed_payload.get("operation") or "analyze"
    ).strip().lower()

    def rhythm_handler(value: dict[str, Any]) -> dict[str, Any]:
        return _worker_handle().remote(value)

    try:
        if operation == "start":
            return _start_rhythm_job(
                routed_payload,
                expected_token=expected_token,
            )
        if operation == "status":
            return _status_rhythm_job(
                routed_payload,
                expected_token=expected_token,
            )
        if operation == "ack":
            return _ack_rhythm_job(
                routed_payload,
                expected_token=expected_token,
            )
        if operation != "analyze":
            raise ValueError("Unsupported analyzer operation.")

        result = route_http_payload(
            routed_payload,
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
    "ASYNC_RESULT_QUEUE_NAME",
    "HTTP_APP_NAME",
    "WORKER_APP_NAME",
    "WORKER_FUNCTION_NAME",
    "analyze",
    "async_protocol_smoke",
    "async_result_queue",
    "http_image",
    "route_http_payload",
    "run_rhythm_async_job",
]
