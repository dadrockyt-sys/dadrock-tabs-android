from __future__ import annotations

from urllib.parse import urlsplit


VERCEL_BLOB_API_HOST = "blob.vercel-storage.com"
VERCEL_BLOB_HOST_SUFFIX = ".blob.vercel-storage.com"


def is_vercel_blob_https_url(audio_url: str) -> bool:
    """Return True only for HTTPS URLs owned by Vercel Blob.

    The Vercel Blob bearer token is a storage credential and must never be
    forwarded to arbitrary audio hosts. Public URLs such as raw GitHub should
    therefore be downloaded without this Authorization header.
    """
    try:
        parsed = urlsplit(str(audio_url or "").strip())
        hostname = (parsed.hostname or "").lower().rstrip(".")
    except (TypeError, ValueError):
        return False

    if parsed.scheme.lower() != "https":
        return False

    return (
        hostname == VERCEL_BLOB_API_HOST
        or hostname.endswith(VERCEL_BLOB_HOST_SUFFIX)
    )


def build_audio_download_headers(
    audio_url: str,
    blob_token: str,
) -> dict[str, str]:
    """Build download headers without leaking the Blob token cross-origin."""
    token = str(blob_token or "").strip()
    if not token or not is_vercel_blob_https_url(audio_url):
        return {}

    return {"Authorization": f"Bearer {token}"}


__all__ = [
    "VERCEL_BLOB_API_HOST",
    "VERCEL_BLOB_HOST_SUFFIX",
    "build_audio_download_headers",
    "is_vercel_blob_https_url",
]
