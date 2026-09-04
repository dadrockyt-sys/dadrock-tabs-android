from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "analyzer" / "v143_audio_download_auth.py"

spec = importlib.util.spec_from_file_location("v143_audio_download_auth", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load V143 audio download auth policy.")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

build_audio_download_headers = module.build_audio_download_headers
is_vercel_blob_https_url = module.is_vercel_blob_https_url

TOKEN = "test-blob-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    cases = [
        (
            "raw GitHub public audio gets no Blob credential",
            "https://raw.githubusercontent.com/dadrockyt-sys/dadrock-tabs-android/main/public/test.m4a",
            TOKEN,
            {},
        ),
        (
            "Vercel public Blob gets Blob credential",
            "https://abc123.public.blob.vercel-storage.com/audio/test.m4a",
            TOKEN,
            AUTH,
        ),
        (
            "Vercel private Blob gets Blob credential",
            "https://abc123.private.blob.vercel-storage.com/audio/test.m4a",
            TOKEN,
            AUTH,
        ),
        (
            "Vercel Blob API host gets Blob credential",
            "https://blob.vercel-storage.com/audio/test.m4a",
            TOKEN,
            AUTH,
        ),
        (
            "deceptive suffix host gets no credential",
            "https://blob.vercel-storage.com.evil.example/audio/test.m4a",
            TOKEN,
            {},
        ),
        (
            "lookalike host gets no credential",
            "https://evilblob.vercel-storage.com/audio/test.m4a",
            TOKEN,
            {},
        ),
        (
            "HTTP Blob URL gets no bearer credential",
            "http://abc123.public.blob.vercel-storage.com/audio/test.m4a",
            TOKEN,
            {},
        ),
        (
            "empty token gets no Authorization header",
            "https://abc123.public.blob.vercel-storage.com/audio/test.m4a",
            "",
            {},
        ),
        (
            "malformed URL gets no Authorization header",
            "https://[broken",
            TOKEN,
            {},
        ),
        (
            "uppercase/trailing-dot Blob hostname is normalized",
            "https://ABC123.PUBLIC.BLOB.VERCEL-STORAGE.COM./audio/test.m4a",
            TOKEN,
            AUTH,
        ),
    ]

    for label, url, token, expected in cases:
        assert_equal(build_audio_download_headers(url, token), expected, label)

    assert_equal(
        is_vercel_blob_https_url(
            "https://raw.githubusercontent.com/example/audio.m4a"
        ),
        False,
        "raw GitHub classification",
    )
    assert_equal(
        is_vercel_blob_https_url(
            "https://store.public.blob.vercel-storage.com/audio.m4a"
        ),
        True,
        "Vercel Blob classification",
    )

    print(f"V143 audio download auth policy: PASS ({len(cases)} header cases + 2 classifier cases)")


if __name__ == "__main__":
    main()
