from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import zlib
from typing import Any, Iterable


ASYNC_PROTOCOL_VERSION = 1
ASYNC_JOB_TOKEN_PREFIX = "v143a1"
ASYNC_RESULT_TTL_SECONDS = 15 * 60
ASYNC_RESULT_CHUNK_BYTES = 700_000
ASYNC_RESULT_MAX_COMPRESSED_BYTES = 12_000_000
ASYNC_RESULT_MAX_JSON_BYTES = 24_000_000

_JOB_ID_RE = re.compile(r"^[A-Za-z0-9_-]{20,64}$")


def _require_secret(secret: str) -> bytes:
    normalized = str(secret or "").encode("utf-8")
    if len(normalized) < 16:
        raise ValueError("Async job signing secret is not configured.")
    return normalized


def create_job_id() -> str:
    job_id = secrets.token_urlsafe(24)
    if not _JOB_ID_RE.fullmatch(job_id):
        raise RuntimeError("Generated async job id was invalid.")
    return job_id


def _signature(job_id: str, secret: str) -> str:
    if not _JOB_ID_RE.fullmatch(str(job_id or "")):
        raise ValueError("Invalid async job id.")
    digest = hmac.new(
        _require_secret(secret),
        job_id.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def build_job_token(job_id: str, secret: str) -> str:
    return f"{ASYNC_JOB_TOKEN_PREFIX}.{job_id}.{_signature(job_id, secret)}"


def parse_job_token(token: str, secret: str) -> str:
    parts = str(token or "").split(".")
    if len(parts) != 3 or parts[0] != ASYNC_JOB_TOKEN_PREFIX:
        raise ValueError("Invalid async job token.")

    job_id = parts[1]
    supplied_signature = parts[2]
    expected_signature = _signature(job_id, secret)
    if not supplied_signature or not hmac.compare_digest(
        supplied_signature,
        expected_signature,
    ):
        raise ValueError("Invalid async job token.")
    return job_id


def _json_bytes(value: Any) -> bytes:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Async result must contain structured JSON values only."
        ) from error

    if len(encoded) > ASYNC_RESULT_MAX_JSON_BYTES:
        raise ValueError("Async structured result is too large.")
    return encoded


def encode_result_envelope(envelope: dict[str, Any]) -> list[Any]:
    if not isinstance(envelope, dict):
        raise ValueError("Async result envelope must be an object.")

    encoded = _json_bytes(envelope)
    compressed = zlib.compress(encoded, level=6)
    if len(compressed) > ASYNC_RESULT_MAX_COMPRESSED_BYTES:
        raise ValueError("Async compressed result is too large.")

    chunks = [
        compressed[offset : offset + ASYNC_RESULT_CHUNK_BYTES]
        for offset in range(0, len(compressed), ASYNC_RESULT_CHUNK_BYTES)
    ] or [b""]

    header = {
        "schemaVersion": ASYNC_PROTOCOL_VERSION,
        "encoding": "zlib-json",
        "chunkCount": len(chunks),
        "compressedBytes": len(compressed),
    }
    return [header, *chunks]


def decode_result_items(items: Iterable[Any]) -> dict[str, Any]:
    materialized = list(items)
    if not materialized or not isinstance(materialized[0], dict):
        raise ValueError("Async result envelope is incomplete.")

    header = materialized[0]
    if header.get("schemaVersion") != ASYNC_PROTOCOL_VERSION:
        raise ValueError("Async result schema version is invalid.")
    if header.get("encoding") != "zlib-json":
        raise ValueError("Async result encoding is invalid.")

    chunk_count = header.get("chunkCount")
    compressed_bytes = header.get("compressedBytes")
    if not isinstance(chunk_count, int) or chunk_count < 1:
        raise ValueError("Async result chunk count is invalid.")
    if not isinstance(compressed_bytes, int) or not (
        0 <= compressed_bytes <= ASYNC_RESULT_MAX_COMPRESSED_BYTES
    ):
        raise ValueError("Async compressed length is invalid.")

    chunks = materialized[1:]
    if len(chunks) != chunk_count or not all(
        isinstance(chunk, bytes) for chunk in chunks
    ):
        raise ValueError("Async result chunks are incomplete.")

    compressed = b"".join(chunks)
    if len(compressed) != compressed_bytes:
        raise ValueError("Async compressed result length mismatch.")

    try:
        encoded = zlib.decompress(compressed)
    except zlib.error as error:
        raise ValueError("Async result could not be decompressed.") from error

    if len(encoded) > ASYNC_RESULT_MAX_JSON_BYTES:
        raise ValueError("Async decompressed result is too large.")

    try:
        envelope = json.loads(encoded.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Async result JSON is invalid.") from error

    if not isinstance(envelope, dict):
        raise ValueError("Async result JSON must be an object.")
    return envelope


def build_completed_envelope(result: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ValueError("Analyzer result must be an object.")
    if not str(result.get("generatedTab") or "").strip():
        raise ValueError("Analyzer result contained no tablature.")

    # _json_bytes is intentionally called here as an early fail-closed check.
    # Binary audio/stem payloads cannot cross this boundary because they are not
    # JSON serializable; only the existing structured analyzer response may pass.
    _json_bytes(result)
    return {
        "schemaVersion": ASYNC_PROTOCOL_VERSION,
        "status": "completed",
        "result": result,
    }


def build_failed_envelope(
    message: str = "The analyzer could not complete the request.",
) -> dict[str, Any]:
    return {
        "schemaVersion": ASYNC_PROTOCOL_VERSION,
        "status": "failed",
        "error": str(message or "The analyzer could not complete the request.")[
            :240
        ],
    }


__all__ = [
    "ASYNC_JOB_TOKEN_PREFIX",
    "ASYNC_PROTOCOL_VERSION",
    "ASYNC_RESULT_CHUNK_BYTES",
    "ASYNC_RESULT_MAX_COMPRESSED_BYTES",
    "ASYNC_RESULT_MAX_JSON_BYTES",
    "ASYNC_RESULT_TTL_SECONDS",
    "build_completed_envelope",
    "build_failed_envelope",
    "build_job_token",
    "create_job_id",
    "decode_result_items",
    "encode_result_envelope",
    "parse_job_token",
]
