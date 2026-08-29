import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

import modal

app = modal.App("dadrock-backing-track-studio")

DEMUCS_6S_MODEL = os.environ.get(
    "BTS_DEMUCS_MODEL",
    "htdemucs_6s.yaml",
)

MAX_AUDIO_SIZE_BYTES = 50 * 1024 * 1024
MIN_AUDIO_DURATION_SECONDS = 3.0
MAX_AUDIO_DURATION_SECONDS = 15 * 60

REMOVAL_MODES = {
    "guitar": {"guitar"},
    "bass": {"bass"},
    "guitar-bass": {"guitar", "bass"},
}

EXPECTED_STEMS = (
    "vocals",
    "drums",
    "bass",
    "other",
    "guitar",
    "piano",
)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "audio-separator[cpu]==0.30.2",
        "fastapi[standard]",
        "requests",
    )
)


def discover_audio(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix.lower()
        in {".wav", ".flac", ".mp3", ".m4a", ".ogg"}
    )


def choose_stem(paths: list[Path], stem_name: str) -> Path | None:
    matches = [
        path
        for path in paths
        if stem_name.lower() in path.name.lower()
    ]

    if not matches:
        return None

    return max(matches, key=lambda path: path.stat().st_size)


def validate_blob_source(audio_url: str, pathname: str) -> None:
    parsed = urlparse(audio_url)

    if parsed.scheme != "https":
        raise ValueError("A secure Vercel Blob URL is required.")

    if (
        not parsed.hostname
        or not parsed.hostname.endswith(".blob.vercel-storage.com")
    ):
        raise ValueError("The uploaded audio must come from Vercel Blob.")

    decoded_path = unquote(parsed.path.lstrip("/"))

    if decoded_path != pathname:
        raise ValueError("The audio URL does not match the uploaded pathname.")

    if not pathname.startswith("bts-audio/") or ".." in pathname:
        raise ValueError("Invalid Backing Track Studio audio pathname.")


def inspect_duration(input_audio: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(input_audio),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        raise ValueError("Unable to inspect the uploaded audio.")

    try:
        data = json.loads(result.stdout or "{}")
        duration = float(data.get("format", {}).get("duration") or 0)
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(
            "Unable to determine the uploaded audio duration."
        ) from error

    if duration < MIN_AUDIO_DURATION_SECONDS:
        raise ValueError(
            "The uploaded audio must be at least 3 seconds long."
        )

    if duration > MAX_AUDIO_DURATION_SECONDS:
        raise ValueError(
            "The uploaded audio cannot be longer than 15 minutes."
        )

    return duration


def normalize_audio(input_audio: Path, output_audio: Path) -> None:
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_audio),
            "-vn",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(output_audio),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )

    if (
        result.returncode != 0
        or not output_audio.exists()
        or output_audio.stat().st_size <= 0
    ):
        raise ValueError("Unable to normalize the uploaded audio.")


def separate_stems(input_audio: Path, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "audio_separator",
        str(input_audio),
        "--model_filename",
        DEMUCS_6S_MODEL,
        "--output_dir",
        str(output_dir),
        "--output_format",
        "WAV",
        "--demucs_shifts",
        "1",
        "--demucs_overlap",
        "0.10",
        "--demucs_segment_size",
        "6",
        "--use_soundfile",
    ]

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=3300,
            env={
                **os.environ,
                "CUDA_VISIBLE_DEVICES": "",
            },
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            "Demucs stem separation timed out on CPU."
        ) from error

    outputs = discover_audio(output_dir)

    if result.returncode != 0 or not outputs:
        detail = (result.stderr or result.stdout or "").strip()[-1500:]
        raise RuntimeError(
            f"Demucs stem separation failed. {detail}"
        )

    stems: dict[str, Path] = {}

    for stem_name in EXPECTED_STEMS:
        stem_path = choose_stem(outputs, stem_name)

        if stem_path is None:
            raise RuntimeError(
                f"Demucs did not produce the expected {stem_name} stem."
            )

        stems[stem_name] = stem_path

    return stems


def rebuild_backing_track(
    stems: dict[str, Path],
    removal_mode: str,
    output_path: Path,
) -> None:
    removed = REMOVAL_MODES[removal_mode]

    remaining = [
        stems[name]
        for name in EXPECTED_STEMS
        if name not in removed
    ]

    if not remaining:
        raise RuntimeError("No stems remain for the requested backing track.")

    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
    ]

    for stem_path in remaining:
        command.extend(["-i", str(stem_path)])

    mix_inputs = "".join(
        f"[{index}:a]"
        for index in range(len(remaining))
    )

    filter_complex = (
        f"{mix_inputs}amix=inputs={len(remaining)}:"
        "duration=longest:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.98[mix]"
    )

    command.extend(
        [
            "-filter_complex",
            filter_complex,
            "-map",
            "[mix]",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ]
    )

    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
    )

    if (
        result.returncode != 0
        or not output_path.exists()
        or output_path.stat().st_size <= 0
    ):
        raise RuntimeError("Unable to rebuild the backing track.")


@app.function(
    image=image,
    timeout=3600,
    memory=8192,
    secrets=[
        modal.Secret.from_name(
            "dadrock-bts-separator-secret"
        )
    ],
)
@modal.fastapi_endpoint(method="POST")
def create_backing_track(payload: dict):
    import requests
    from fastapi import HTTPException, Response

    expected_token = os.environ.get("BTS_SEPARATOR_API_TOKEN")
    supplied_token = str(payload.get("token") or "")

    if (
        not expected_token
        or supplied_token != expected_token
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized BTS separator request.",
        )

    audio_url = str(payload.get("audioUrl") or "").strip()
    pathname = str(payload.get("pathname") or "").strip()
    removal_mode = str(
        payload.get("removalMode") or ""
    ).strip().lower()
    blob_token = str(payload.get("blobToken") or "").strip()

    if removal_mode not in REMOVAL_MODES:
        raise HTTPException(
            status_code=400,
            detail=(
                "removalMode must be guitar, bass, or guitar-bass."
            ),
        )

    try:
        validate_blob_source(audio_url, pathname)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    if not blob_token:
        raise HTTPException(
            status_code=400,
            detail="Private Blob authorization is required.",
        )

    headers = {
        "Authorization": f"Bearer {blob_token}",
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        source_path = root / "uploaded-audio"
        normalized_path = root / "normalized.wav"
        stems_dir = root / "stems"
        output_path = root / "backing-track.mp3"

        try:
            response = requests.get(
                audio_url,
                headers=headers,
                timeout=180,
            )
        except requests.RequestException as error:
            raise HTTPException(
                status_code=502,
                detail="The BTS separator could not download the audio file.",
            ) from error

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail="The BTS separator could not download the audio file.",
            )

        if len(response.content) > MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="The uploaded audio cannot be larger than 50 MB.",
            )

        source_path.write_bytes(response.content)

        try:
            inspect_duration(source_path)
            normalize_audio(source_path, normalized_path)
            stems = separate_stems(normalized_path, stems_dir)
            rebuild_backing_track(
                stems,
                removal_mode,
                output_path,
            )
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

        return Response(
            content=output_path.read_bytes(),
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "private, no-store, max-age=0",
                "X-BTS-Removal-Mode": removal_mode,
                "X-BTS-Separator-Model": DEMUCS_6S_MODEL,
                "X-BTS-Compute": "cpu",
            },
        )


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "app": "dadrock-backing-track-studio",
                "model": DEMUCS_6S_MODEL,
                "removalModes": sorted(REMOVAL_MODES),
                "waveformSeparation": True,
                "compute": "cpu-only",
                "productionModified": False,
            },
            indent=2,
        )
    )
