from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any

from v143_production_separator import (
    BS_ROFORMER_MODEL,
    DEMUCS_6S_MODEL,
    normalize_input_audio,
    separate_demucs_guitar,
    separate_roformer_instrumental,
)


SEPARATOR_SEED = "143"
CUBLAS_WORKSPACE_CONFIG = ":4096:8"


def seeded_audio_separator_cli() -> list[str]:
    return [sys.executable, "-m", "v143_seeded_audio_separator_cli"]


def build_seeded_v143_stems(
    input_audio: Path | str,
    output_dir: Path | str,
) -> dict[str, Any]:
    """Run the frozen V143 separator graph through a deterministic child boundary.

    The model choices and production parameters remain exactly the frozen V143
    values: Demucs6s Guitar, shifts=1, overlap=.10, segment=6, plus
    BS-RoFormer Instrumental -> Demucs6s.

    Startup environment is exported before each child interpreter launches so
    Python hash randomization and CUDA/cuBLAS determinism are configured before
    Torch/audio-separator imports. No song/reference labels or target counts enter.
    """
    input_path = Path(input_audio)
    root = Path(output_dir)
    if not input_path.exists() or input_path.stat().st_size <= 0:
        raise FileNotFoundError(input_path)

    root.mkdir(parents=True, exist_ok=True)
    cli = seeded_audio_separator_cli()
    work = root / "_work"

    normalized_input = normalize_input_audio(
        input_path,
        work / "normalized",
    )

    managed_env = {
        "PYTHONHASHSEED": SEPARATOR_SEED,
        "V143_SEPARATOR_SEED": SEPARATOR_SEED,
        "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
        # Explicitly disable NVIDIA TF32 override; child Torch also disables
        # TF32 through backend settings before audio-separator is imported.
        "NVIDIA_TF32_OVERRIDE": "0",
    }
    previous = {key: os.environ.get(key) for key in managed_env}
    os.environ.update(managed_env)
    try:
        direct = separate_demucs_guitar(
            cli,
            normalized_input,
            work / "direct",
        )
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
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    direct_out = root / "direct-demucs6s-guitar.wav"
    roformer_out = root / "bsroformer-instrumental.wav"
    cascade_out = root / "bsroformer-demucs6s-guitar.wav"
    shutil.copy2(direct["path"], direct_out)
    shutil.copy2(roformer["path"], roformer_out)
    shutil.copy2(cascade["path"], cascade_out)

    if (
        not direct_out.exists()
        or direct_out.stat().st_size <= 0
        or not roformer_out.exists()
        or roformer_out.stat().st_size <= 0
        or not cascade_out.exists()
        or cascade_out.stat().st_size <= 0
    ):
        raise RuntimeError("Seeded V143 separator outputs were not created correctly")

    return {
        "directGuitar": str(direct_out),
        "roformerInstrumental": str(roformer_out),
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
            "deterministicSeed": 143,
            "pythonHashSeedAtChildStartup": 143,
            "cublasWorkspaceConfig": CUBLAS_WORKSPACE_CONFIG,
            "tf32Disabled": True,
            "torchDeterministicAlgorithms": True,
        },
        "referenceFree": True,
        "diagnosticOnly": True,
    }


__all__ = [
    "SEPARATOR_SEED",
    "CUBLAS_WORKSPACE_CONFIG",
    "seeded_audio_separator_cli",
    "build_seeded_v143_stems",
]
