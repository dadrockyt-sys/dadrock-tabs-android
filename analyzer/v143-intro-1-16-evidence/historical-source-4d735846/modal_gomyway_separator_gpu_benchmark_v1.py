from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import modal


APP_NAME = "jimmy-paige-separator-gpu-benchmark-v1"

BS_ROFORMER_MODEL = os.environ.get(
    "JIMMY_BS_ROFORMER_MODEL",
    "model_bs_roformer_ep_317_sdr_12.9755.ckpt",
)

DEMUCS_6S_MODEL = os.environ.get(
    "JIMMY_DEMUCS_6S_MODEL",
    "htdemucs_6s.yaml",
)

OUTPUT_STEM_NAME = "gomyway-bsroformer-demucs6s-gpu-hq-guitar.wav"

CONTROL_PITCH_F1 = 4.73
CURRENT_WINNER_PITCH_F1 = 6.12

app = modal.App(APP_NAME)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "audio-separator",
        "onnxruntime-gpu",
        "soundfile",
    )
)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def discover_outputs(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix.lower()
        in {
            ".wav",
            ".flac",
            ".mp3",
            ".m4a",
            ".ogg",
        }
    )


def choose_stem(
    paths: list[Path],
    keywords: tuple[str, ...],
) -> Path | None:
    scored: list[tuple[int, Path]] = []

    for path in paths:
        name = path.name.lower()
        score = sum(
            1
            for keyword in keywords
            if keyword in name
        )
        if score:
            scored.append((score, path))

    if not scored:
        return None

    scored.sort(
        key=lambda row: (
            row[0],
            row[1].stat().st_size,
        ),
        reverse=True,
    )
    return scored[0][1]


def separate(
    input_audio: Path,
    model: str,
    output_dir: Path,
    *,
    shifts: int | None = None,
    overlap: float | None = None,
    segment_size: int | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    before = set(discover_outputs(output_dir))

    command = [
        "audio-separator",
        str(input_audio),
        "--model_filename",
        model,
        "--output_dir",
        str(output_dir),
        "--output_format",
        "WAV",
        "--use_soundfile",
    ]

    if shifts is not None:
        command.extend(["--demucs_shifts", str(shifts)])
    if overlap is not None:
        command.extend(["--demucs_overlap", str(overlap)])
    if segment_size is not None:
        command.extend(["--demucs_segment_size", str(segment_size)])

    started = time.monotonic()
    result = run(command)
    elapsed = round(time.monotonic() - started, 3)

    after = set(discover_outputs(output_dir))
    created = sorted(after - before)

    return {
        "model": model,
        "command": command,
        "returnCode": result.returncode,
        "elapsedSeconds": elapsed,
        "outputs": [str(path) for path in created],
        "logTail": result.stdout[-8000:],
    }


@app.function(
    image=image,
    gpu="L4",
    timeout=3600,
    memory=16384,
)
def generate_gpu_hq_winner_stem(
    audio_bytes: bytes,
    audio_name: str,
) -> dict[str, Any]:
    suffix = Path(audio_name).suffix or ".m4a"

    with tempfile.TemporaryDirectory(
        prefix="jimmy-gpu-separator-v1-"
    ) as temporary_directory:
        temp_root = Path(temporary_directory)

        input_audio = temp_root / f"input{suffix}"
        input_audio.write_bytes(audio_bytes)

        roformer_dir = temp_root / "bs-roformer"
        roformer = separate(
            input_audio,
            BS_ROFORMER_MODEL,
            roformer_dir,
        )

        roformer_outputs = [Path(path) for path in roformer["outputs"]]
        instrumental = choose_stem(
            roformer_outputs,
            (
                "instrumental",
                "no_vocals",
                "novocals",
                "other",
            ),
        )

        roformer["selectedInstrumentalStem"] = (
            str(instrumental) if instrumental else None
        )
        roformer["passed"] = (
            roformer["returnCode"] == 0
            and instrumental is not None
        )

        if not roformer["passed"]:
            raise RuntimeError(
                "BS-RoFormer GPU benchmark did not produce a recognizable "
                "instrumental stem.\n"
                + roformer["logTail"]
            )

        demucs_dir = temp_root / "roformer-then-demucs6s"
        demucs = separate(
            instrumental,
            DEMUCS_6S_MODEL,
            demucs_dir,
            shifts=4,
            overlap=0.25,
            segment_size=12,
        )

        demucs_outputs = [Path(path) for path in demucs["outputs"]]
        guitar = choose_stem(demucs_outputs, ("guitar",))

        demucs["selectedGuitarStem"] = str(guitar) if guitar else None
        demucs["passed"] = (
            demucs["returnCode"] == 0
            and guitar is not None
        )

        if not demucs["passed"]:
            raise RuntimeError(
                "BS-RoFormer -> HTDemucs 6s GPU benchmark did not produce "
                "a recognizable guitar stem.\n"
                + demucs["logTail"]
            )

        guitar_bytes = guitar.read_bytes()

        report = {
            "schemaVersion": 1,
            "passed": True,
            "benchmarkType": "gpu-hq-winning-separator-cascade",
            "architecture": "bsroformer-then-demucs6s",
            "gpu": "L4",
            "models": {
                "bsRoFormer": BS_ROFORMER_MODEL,
                "demucs6s": DEMUCS_6S_MODEL,
            },
            "qualitySettings": {
                "demucsShifts": 4,
                "demucsOverlap": 0.25,
                "demucsSegmentSize": 12,
                "useSoundfile": True,
            },
            "controlPitchF1": CONTROL_PITCH_F1,
            "currentWinnerPitchF1": CURRENT_WINNER_PITCH_F1,
            "professionalReferenceUsedForSeparation": False,
            "professionalReferenceRole": "downstream-grading-only",
            "protected949CandidateModified": False,
            "v7EventsModified": False,
            "rendererModified": False,
            "protectedBaselinesChanged": False,
            "productionSeparatorChanged": False,
            "productionPromotionAllowed": False,
            "automaticApplyAllowed": False,
            "roformerStage": roformer,
            "demucsStage": demucs,
            "outputStemName": OUTPUT_STEM_NAME,
            "readyForIdenticalBasicPitchGrading": True,
        }

        return {
            "report": report,
            "stemBytes": guitar_bytes,
        }


@app.local_entrypoint()
def main(
    audio_path: str = "public/gomywayfullaitest.m4a",
    output_path: str = (
        "public/separator-benchmark-gpu-v1/" + OUTPUT_STEM_NAME
    ),
    report_path: str = "public/gomyway-separator-gpu-benchmark-v1.json",
) -> None:
    audio_file = Path(audio_path)

    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    print("JIMMY PAIGE GPU SEPARATOR BENCHMARK V1")
    print("Architecture: BS-RoFormer -> HTDemucs 6s")
    print("GPU: L4")
    print("Demucs quality: shifts=4 overlap=0.25 segment=12")

    result = generate_gpu_hq_winner_stem.remote(
        audio_file.read_bytes(),
        audio_file.name,
    )

    report = result["report"]
    stem_bytes = result["stemBytes"]

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(stem_bytes)

    report_file = Path(report_path)
    report_file.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("GPU separator benchmark passed:", report["passed"])
    print("Output stem:", output_file)
    print("Report:", report_file)
    print("Professional reference used during separation: False")
    print("Protected 949-event candidate modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Ready for identical Basic Pitch grading: True")
