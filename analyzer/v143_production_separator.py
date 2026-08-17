from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


BS_ROFORMER_MODEL = os.environ.get(
    "JIMMY_BS_ROFORMER_MODEL",
    "model_bs_roformer_ep_317_sdr_12.9755.ckpt",
)

DEMUCS_6S_MODEL = os.environ.get(
    "JIMMY_DEMUCS_6S_MODEL",
    "htdemucs_6s.yaml",
)


def find_audio_separator() -> list[str]:
    executable = shutil.which("audio-separator")

    if executable:
        return [executable]

    probe = subprocess.run(
        [sys.executable, "-m", "audio_separator", "--help"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if probe.returncode == 0:
        return [sys.executable, "-m", "audio_separator"]

    raise RuntimeError(
        "audio-separator unavailable"
    )


def discover_audio(directory: Path) -> list[Path]:
    if not directory.exists():
        return []

    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix.lower()
        in {".wav", ".flac", ".mp3", ".m4a", ".ogg"}
    )


def choose_stem(
    paths: list[Path],
    keywords: tuple[str, ...],
) -> Path | None:
    scored: list[tuple[int, int, Path]] = []

    for path in paths:
        lower = path.name.lower()

        score = sum(
            1
            for keyword in keywords
            if keyword.lower() in lower
        )

        if score:
            scored.append(
                (score, path.stat().st_size, path)
            )

    if not scored:
        return None

    scored.sort(reverse=True)

    return scored[0][2]


def run_separator(
    command: list[str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        text=True,
    )


def separate_demucs_guitar(
    cli: list[str],
    input_audio: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = cli + [
        str(input_audio),
        "--model_filename",
        DEMUCS_6S_MODEL,
        "--output_dir",
        str(output_dir),
        "--output_format",
        "WAV",
        "--single_stem",
        "Guitar",
        "--demucs_shifts",
        "1",
        "--demucs_overlap",
        "0.10",
        "--demucs_segment_size",
        "6",
        "--use_soundfile",
    ]

    started = time.monotonic()

    result = run_separator(command)

    elapsed = round(
        time.monotonic() - started,
        3,
    )

    outputs = discover_audio(output_dir)

    guitar = choose_stem(
        outputs,
        ("guitar",),
    )

    if result.returncode != 0 or guitar is None:
        raise RuntimeError(
            "Demucs guitar separation failed: "
            f"returnCode={result.returncode}, "
            f"outputs={[str(p) for p in outputs]}"
        )

    return {
        "path": guitar,
        "model": DEMUCS_6S_MODEL,
        "elapsedSeconds": elapsed,
    }


def separate_roformer_instrumental(
    cli: list[str],
    input_audio: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = cli + [
        str(input_audio),
        "--model_filename",
        BS_ROFORMER_MODEL,
        "--output_dir",
        str(output_dir),
        "--output_format",
        "WAV",
        "--single_stem",
        "Instrumental",
        "--mdxc_batch_size",
        "1",
        "--use_soundfile",
    ]

    started = time.monotonic()

    result = run_separator(command)

    elapsed = round(
        time.monotonic() - started,
        3,
    )

    outputs = discover_audio(output_dir)

    instrumental = choose_stem(
        outputs,
        (
            "instrumental",
            "no_vocals",
            "novocals",
            "other",
        ),
    )

    if result.returncode != 0 or instrumental is None:
        raise RuntimeError(
            "BS-RoFormer instrumental separation failed: "
            f"returnCode={result.returncode}, "
            f"outputs={[str(p) for p in outputs]}"
        )

    return {
        "path": instrumental,
        "model": BS_ROFORMER_MODEL,
        "elapsedSeconds": elapsed,
    }



def normalize_input_audio(
    input_audio: Path,
    output_dir: Path,
) -> Path:
    """
    Decode arbitrary user audio through FFmpeg into a SoundFile-safe
    float WAV before running either frozen V143 separator path.
    """
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise RuntimeError("ffmpeg unavailable")

    destination = output_dir / "input-normalized.wav"

    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_audio),
        "-vn",
        "-c:a",
        "pcm_s16le",
        str(destination),
    ]

    result = subprocess.run(
        command,
        check=False,
        text=True,
    )

    if (
        result.returncode != 0
        or not destination.exists()
        or destination.stat().st_size <= 0
    ):
        raise RuntimeError(
            "Input audio normalization failed: "
            f"returnCode={result.returncode}"
        )

    return destination


def build_v143_stems(
    input_audio: Path | str,
    output_dir: Path | str,
) -> dict[str, Any]:
    input_audio = Path(input_audio)
    output_dir = Path(output_dir)

    if not input_audio.exists():
        raise FileNotFoundError(input_audio)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    cli = find_audio_separator()

    work = output_dir / "_work"

    normalized_input = normalize_input_audio(
        input_audio,
        work / "normalized",
    )

    # Preserve the historical direct path exactly: Demucs receives
    # the original uploaded/source file. This path already succeeds
    # with the Go My Way M4A in the current environment.
    direct = separate_demucs_guitar(
        cli,
        normalized_input,
        work / "direct",
    )

    # BS-RoFormer uses SoundFile internally and cannot read this M4A
    # here, so only the cascade branch receives a deterministic PCM16
    # WAV decode.
    roformer = separate_roformer_instrumental(
        cli,
        normalized_input,
        work / "roformer",
    )

    cascade = separate_demucs_guitar(
        cli,
        Path(roformer["path"]),
        work / "cascade",
    )

    direct_out = output_dir / "direct-demucs6s-guitar.wav"
    cascade_out = output_dir / "bsroformer-demucs6s-guitar.wav"

    shutil.copy2(
        direct["path"],
        direct_out,
    )

    shutil.copy2(
        cascade["path"],
        cascade_out,
    )

    if (
        not direct_out.exists()
        or direct_out.stat().st_size == 0
        or not cascade_out.exists()
        or cascade_out.stat().st_size == 0
    ):
        raise RuntimeError(
            "V143 separator outputs were not created correctly"
        )

    return {
        "directGuitar": str(direct_out),
        "cascadeGuitar": str(cascade_out),

        "models": {
            "demucs": DEMUCS_6S_MODEL,
            "bsRoformer": BS_ROFORMER_MODEL,
        },

        "settings": {
            "demucsSingleStem": "Guitar",
            "demucsShifts": 1,
            "demucsOverlap": 0.10,
            "demucsSegmentSize": 6,
            "roformerSingleStem": "Instrumental",
            "roformerBatchSize": 1,
            "useSoundfile": True,
        },

        "referenceFree": True,
    }


def describe() -> dict[str, Any]:
    return {
        "directPath": "audio -> Demucs6s Guitar",
        "cascadePath": (
            "audio -> BS-RoFormer Instrumental "
            "-> Demucs6s Guitar"
        ),
        "demucsModel": DEMUCS_6S_MODEL,
        "bsRoformerModel": BS_ROFORMER_MODEL,
        "demucsShifts": 1,
        "demucsOverlap": 0.10,
        "demucsSegmentSize": 6,
        "referenceFree": True,
    }


if __name__ == "__main__":
    import json

    print("V143 PRODUCTION SEPARATOR DEFINITION")
    print(
        json.dumps(
            describe(),
            indent=2,
        )
    )
