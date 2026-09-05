"""Exact, fail-closed stage-cache primitives for V143 diagnostics.

This module is intentionally production-disconnected. It provides byte-exact cache
semantics for structural testing only; callers choose an ephemeral cache root.
It does not define retention policy and must not be wired to user audio until that
policy is explicitly resolved.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

_REQUIRED_FINGERPRINT_FIELDS = frozenset(
    {
        "schema_version",
        "normalized_source_sha256",
        "separator_model",
        "separator_weights_sha256",
        "demucs_parameters",
        "shift_policy",
        "audio_format",
        "runtime_controls",
        "code_policy_version",
    }
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class FingerprintError(ValueError):
    """Raised when an exact-cache fingerprint is incomplete or ambiguous."""


class CacheWriteError(RuntimeError):
    """Raised when a cache entry cannot be written without ambiguity."""


@dataclass(frozen=True)
class CacheResolution:
    """Result of resolving an exact stage through the diagnostic cache."""

    payloads: dict[str, bytes]
    cache_hit: bool
    cache_write_succeeded: bool | None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise FingerprintError(f"{field} must be a non-empty string")
    return value


def _require_sha256(value: Any, field: str) -> str:
    value = _require_nonempty_string(value, field)
    if not _SHA256_RE.fullmatch(value):
        raise FingerprintError(f"{field} must be a lowercase SHA-256 hex digest")
    return value


def validate_fingerprint(fingerprint: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(fingerprint, Mapping):
        raise FingerprintError("fingerprint must be a mapping")

    keys = set(fingerprint)
    missing = _REQUIRED_FINGERPRINT_FIELDS - keys
    extra = keys - _REQUIRED_FINGERPRINT_FIELDS
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing={sorted(missing)}")
        if extra:
            details.append(f"extra={sorted(extra)}")
        raise FingerprintError("fingerprint field set mismatch: " + ", ".join(details))

    if not isinstance(fingerprint["schema_version"], int) or isinstance(
        fingerprint["schema_version"], bool
    ) or fingerprint["schema_version"] != SCHEMA_VERSION:
        raise FingerprintError(
            f"schema_version must equal {SCHEMA_VERSION}, got {fingerprint['schema_version']!r}"
        )

    _require_sha256(fingerprint["normalized_source_sha256"], "normalized_source_sha256")
    _require_nonempty_string(fingerprint["separator_model"], "separator_model")
    _require_sha256(fingerprint["separator_weights_sha256"], "separator_weights_sha256")
    _require_nonempty_string(fingerprint["code_policy_version"], "code_policy_version")

    for field in ("demucs_parameters", "shift_policy", "audio_format", "runtime_controls"):
        value = fingerprint[field]
        if not isinstance(value, Mapping) or not value:
            raise FingerprintError(f"{field} must be a non-empty mapping")

    audio_format = fingerprint["audio_format"]
    sample_rate = audio_format.get("sample_rate_hz")
    channels = audio_format.get("channels")
    if not isinstance(sample_rate, int) or isinstance(sample_rate, bool) or sample_rate <= 0:
        raise FingerprintError("audio_format.sample_rate_hz must be a positive integer")
    if not isinstance(channels, int) or isinstance(channels, bool) or channels <= 0:
        raise FingerprintError("audio_format.channels must be a positive integer")

    runtime = fingerprint["runtime_controls"]
    for field in (
        "torch_intraop_threads",
        "torch_interop_threads",
        "omp_num_threads",
        "mkl_num_threads",
    ):
        value = runtime.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise FingerprintError(f"runtime_controls.{field} must be a positive integer")
    if not isinstance(runtime.get("onednn_enabled"), bool):
        raise FingerprintError("runtime_controls.onednn_enabled must be boolean")

    try:
        canonical = json.dumps(
            fingerprint,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        normalized = json.loads(canonical)
    except (TypeError, ValueError) as exc:
        raise FingerprintError(f"fingerprint is not canonically JSON-serializable: {exc}") from exc

    return normalized


def canonical_fingerprint_bytes(fingerprint: Mapping[str, Any]) -> bytes:
    normalized = validate_fingerprint(fingerprint)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def cache_key(fingerprint: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_fingerprint_bytes(fingerprint))


def _safe_payload_name(name: str) -> str:
    if (
        not isinstance(name, str)
        or not name
        or name in {".", "..", "manifest.json"}
        or "/" in name
        or "\\" in name
        or Path(name).name != name
    ):
        raise ValueError(f"unsafe cache payload name: {name!r}")
    return name


def _normalize_payloads(payloads: Mapping[str, bytes]) -> dict[str, bytes]:
    if not isinstance(payloads, Mapping) or not payloads:
        raise CacheWriteError("payloads must be a non-empty mapping")

    normalized_payloads: dict[str, bytes] = {}
    for raw_name, raw_data in payloads.items():
        try:
            name = _safe_payload_name(raw_name)
        except ValueError as exc:
            raise CacheWriteError(str(exc)) from exc
        if not isinstance(raw_data, bytes):
            raise CacheWriteError(f"payload {name!r} must be bytes")
        normalized_payloads[name] = raw_data
    return normalized_payloads


class ExactStageCache:
    """Byte-exact, fail-closed content-addressed cache for isolated diagnostics."""

    def __init__(self, root: os.PathLike[str] | str):
        self.root = Path(root)

    def entry_path(self, fingerprint: Mapping[str, Any]) -> Path:
        return self.root / cache_key(fingerprint)

    def lookup(self, fingerprint: Mapping[str, Any]) -> dict[str, bytes] | None:
        normalized = validate_fingerprint(fingerprint)
        key = cache_key(normalized)
        entry = self.root / key
        manifest_path = entry / "manifest.json"

        try:
            if entry.is_symlink() or not entry.is_dir():
                return None
            if manifest_path.is_symlink() or not manifest_path.is_file():
                return None

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(manifest, dict):
                return None
            if manifest.get("schema_version") != SCHEMA_VERSION:
                return None
            if manifest.get("cache_key") != key:
                return None
            if manifest.get("fingerprint") != normalized:
                return None

            payload_meta = manifest.get("payloads")
            if not isinstance(payload_meta, dict) or not payload_meta:
                return None

            expected_names = set(payload_meta)
            for name in expected_names:
                _safe_payload_name(name)

            actual_names = {child.name for child in entry.iterdir()}
            if actual_names != expected_names | {"manifest.json"}:
                return None

            payloads: dict[str, bytes] = {}
            for name, metadata in payload_meta.items():
                if not isinstance(metadata, dict):
                    return None
                expected_sha = metadata.get("sha256")
                expected_size = metadata.get("size")
                if not isinstance(expected_sha, str) or not _SHA256_RE.fullmatch(expected_sha):
                    return None
                if (
                    not isinstance(expected_size, int)
                    or isinstance(expected_size, bool)
                    or expected_size < 0
                ):
                    return None

                path = entry / name
                if path.is_symlink() or not path.is_file():
                    return None
                data = path.read_bytes()
                if len(data) != expected_size or sha256_bytes(data) != expected_sha:
                    return None
                payloads[name] = data

            return payloads
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError):
            return None

    def store(self, fingerprint: Mapping[str, Any], payloads: Mapping[str, bytes]) -> str:
        normalized = validate_fingerprint(fingerprint)
        key = cache_key(normalized)
        normalized_payloads = _normalize_payloads(payloads)

        self.root.mkdir(parents=True, exist_ok=True)
        if self.root.is_symlink() or not self.root.is_dir():
            raise CacheWriteError("cache root must be a real directory")

        final = self.root / key
        if final.exists() or final.is_symlink():
            existing = self.lookup(normalized)
            if existing == normalized_payloads:
                return key
            raise CacheWriteError("existing cache entry is missing, corrupt, or byte-different")

        temp = self.root / f".{key}.{uuid.uuid4().hex}.tmp"
        try:
            temp.mkdir(mode=0o700)
            payload_meta: dict[str, dict[str, Any]] = {}
            for name in sorted(normalized_payloads):
                data = normalized_payloads[name]
                path = temp / name
                with path.open("xb") as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
                payload_meta[name] = {"sha256": sha256_bytes(data), "size": len(data)}

            manifest = {
                "schema_version": SCHEMA_VERSION,
                "cache_key": key,
                "fingerprint": normalized,
                "payloads": payload_meta,
            }
            manifest_text = json.dumps(
                manifest,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
            manifest_path = temp / "manifest.json"
            with manifest_path.open("x", encoding="utf-8") as handle:
                handle.write(manifest_text)
                handle.flush()
                os.fsync(handle.fileno())

            try:
                os.rename(temp, final)
            except FileExistsError:
                existing = self.lookup(normalized)
                if existing == normalized_payloads:
                    shutil.rmtree(temp, ignore_errors=True)
                    return key
                raise CacheWriteError("cache-entry creation raced with a non-identical entry")

            return key
        except CacheWriteError:
            raise
        except OSError as exc:
            raise CacheWriteError(f"cache write failed: {exc}") from exc
        finally:
            if temp.exists():
                shutil.rmtree(temp, ignore_errors=True)

    def resolve(
        self,
        fingerprint: Mapping[str, Any],
        compute: Callable[[], Mapping[str, bytes]],
    ) -> CacheResolution:
        """Return an exact hit or compute exact bytes and best-effort populate the cache.

        Cache acceptance is fail-closed. A miss, corrupt entry, or write failure never
        substitutes alternate bytes: the supplied exact compute path runs and its
        validated output is returned unchanged. Invalid compute output is not hidden.
        """

        normalized = validate_fingerprint(fingerprint)
        hit = self.lookup(normalized)
        if hit is not None:
            return CacheResolution(
                payloads=hit,
                cache_hit=True,
                cache_write_succeeded=None,
            )

        computed = _normalize_payloads(compute())
        try:
            self.store(normalized, computed)
            write_succeeded = True
        except CacheWriteError:
            write_succeeded = False

        return CacheResolution(
            payloads=computed,
            cache_hit=False,
            cache_write_succeeded=write_succeeded,
        )

    def remove(self, fingerprint: Mapping[str, Any]) -> None:
        entry = self.entry_path(fingerprint)
        if entry.exists() and not entry.is_symlink():
            shutil.rmtree(entry)
