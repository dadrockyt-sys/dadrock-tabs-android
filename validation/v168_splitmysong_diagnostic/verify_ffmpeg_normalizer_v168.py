#!/usr/bin/env python3
"""Fail-closed verifier for the SplitMySong diagnostic FFmpeg normalizer.

This script reads no audio and has no scorer/reference inputs.  It exists only
because FFmpeg 5.1.9 and FFmpeg 7.1.5 produced different normalized PCM for the
same frozen AAC source.  Candidate generation must therefore use the exact
Debian 13 FFmpeg package that reproduced the preregistered normalized bytes.
"""
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from pathlib import Path

EXPECTED_OS_ID = "debian"
EXPECTED_OS_VERSION_ID = "13"
EXPECTED_DPKG_VERSION = "7:7.1.5-0+deb13u1"
EXPECTED_BINARY_PREFIX = "ffmpeg version 7.1.5-0+deb13u1 "
SCHEMA = "dadrock.tabs.v168.splitmysong-diagnostic-ffmpeg-normalizer.v1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg is None or ffprobe is None:
        raise RuntimeError("ffmpeg/ffprobe missing")

    os_release = platform.freedesktop_os_release()
    if os_release.get("ID") != EXPECTED_OS_ID:
        raise RuntimeError(f"OS ID mismatch: {os_release.get('ID')!r} != {EXPECTED_OS_ID!r}")
    if os_release.get("VERSION_ID") != EXPECTED_OS_VERSION_ID:
        raise RuntimeError(
            f"OS VERSION_ID mismatch: {os_release.get('VERSION_ID')!r} != {EXPECTED_OS_VERSION_ID!r}"
        )

    first_line = subprocess.check_output([ffmpeg, "-version"], text=True).splitlines()[0]
    if not first_line.startswith(EXPECTED_BINARY_PREFIX):
        raise RuntimeError(
            f"FFmpeg binary mismatch: {first_line!r}; expected prefix {EXPECTED_BINARY_PREFIX!r}"
        )

    dpkg_version = subprocess.check_output(
        ["dpkg-query", "-W", "-f=${Version}", "ffmpeg"], text=True
    ).strip()
    if dpkg_version != EXPECTED_DPKG_VERSION:
        raise RuntimeError(
            f"FFmpeg package mismatch: {dpkg_version!r} != {EXPECTED_DPKG_VERSION!r}"
        )

    payload = {
        "schema": SCHEMA,
        "status": "FFMPEG_NORMALIZER_READY",
        "validation": "PASS",
        "osId": os_release.get("ID"),
        "osVersionId": os_release.get("VERSION_ID"),
        "ffmpegPath": ffmpeg,
        "ffprobePath": ffprobe,
        "ffmpegFirstLine": first_line,
        "ffmpegDpkgVersion": dpkg_version,
        "safety": {
            "audioRead": False,
            "candidateGenerated": False,
            "pitchInferenceInvoked": False,
            "referenceRead": False,
            "scorerRead": False,
            "gpuCudaUsed": False,
        },
    }
    text = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
