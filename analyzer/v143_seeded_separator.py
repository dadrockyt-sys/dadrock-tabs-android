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


def seeded_audio_separator_cli() -> list[str]:
    return [sys.executable, "-m", "v143_seeded_audio_separator_cli"]


def build_seeded_v143_stems(
    input_audio: Path | str,
    output_dir: Path | str,
) -> dict[str, Any]:
    """Run the frozen V143 separator graph through a seeded CLI wrapper.

    The model choices and production parameters remain exactly the frozen V143
    values: Demucs6s Guitar, shifts=1, overlap=.10, segment=6, plus
    BS-RoFormer Instrumental -> Demucs6s.

    PYTHONHASHSEED must be inherited by each child interpreter at process
    startup; setting it inside v143_seeded_audio_separator_cli.py is too late to
    affect Python's hash randomization. This parent boundary therefore exports
    only startup RNG environment values while leaving all frozen separator math
    and model parameters unchanged.
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

    previous_hash_seed = os.environ.get("PYTHONHASHSEED")
    previous_separator_seed = os.environ.get("V143_SEPARATOR_SEED")
    os.environ["PYTHONHASHSEED"] = SEPARATOR_SEED
    os.environ["V143_SEPARATOR_SEED"] = SEPARATOR_SEED
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
        if previous_hash_seed is None:
            os.environ.pop("PYTHONHASHSEED", None)
        else:
            os.environ["PYTHONHASHSEED"] = previous_hash_seed
        if previous_separator_seed is None:
            os.environ.pop("V143_SEPARATOR_SEED", None)
        else:
            os.environ["V143_SEPARATOR_SEED"] = previous_separator_seed

    direct_out = root / "direct-demucs6s-guitar.wav"
    cascade_out = root / "bsroformer-demucs6s-guitar.wav"
    shutil.copy2(direct["path"], direct_out)
    shutil.copy2(cascade["path"], cascade_out)

    if (
        not direct_out.exists()
        or direct_out.stat().st_size <= 0
        or not cascade_out.exists()
        or cascade_out.stat().st_size <= 0
    ):
        raise RuntimeError("Seeded V143 separator outputs were not created correctly")

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
            "deterministicSeed": 143,
            "pythonHashSeedAtChildStartup": 143,
        },
        "referenceFree": True,
        "diagnosticOnly": True,
    }


__all__ = [
    "seeded_audio_separator_cli",
    "build_seeded_v143_stems",
]
