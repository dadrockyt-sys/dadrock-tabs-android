from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

from v143_production_separator import (
    BS_ROFORMER_MODEL,
    DEMUCS_6S_MODEL,
    choose_stem,
    discover_audio,
    normalize_input_audio,
    run_separator,
    separate_roformer_instrumental,
)


BASS_SEPARATOR_SEED = 143
BASS_DEMUCS_SHIFTS = 1
BASS_DEMUCS_OVERLAP = 0.10
BASS_DEMUCS_SEGMENT_SIZE = 6

SeparatorRunner = Callable[[list[str]], Any]


def seeded_separator_cli() -> list[str]:
    """Use the already-proven seeded separator child-process boundary."""
    return [sys.executable, "-m", "v143_seeded_audio_separator_cli"]


def demucs_bass_command(
    cli: list[str],
    input_audio: Path | str,
    output_dir: Path | str,
) -> list[str]:
    """Build the deterministic Demucs6s Bass single-stem command.

    This is an inactive Bass research scaffold. It intentionally mirrors the
    frozen Rhythm separator parameters while requesting the model's dedicated
    Bass stem rather than Guitar. It does not alter the live Rhythm separator.
    """
    return list(cli) + [
        str(input_audio),
        "--model_filename",
        DEMUCS_6S_MODEL,
        "--output_dir",
        str(output_dir),
        "--output_format",
        "WAV",
        "--single_stem",
        "Bass",
        "--demucs_shifts",
        str(BASS_DEMUCS_SHIFTS),
        "--demucs_overlap",
        f"{BASS_DEMUCS_OVERLAP:.2f}",
        "--demucs_segment_size",
        str(BASS_DEMUCS_SEGMENT_SIZE),
        "--use_soundfile",
    ]


def separate_demucs_bass(
    cli: list[str],
    input_audio: Path | str,
    output_dir: Path | str,
    *,
    runner: SeparatorRunner = run_separator,
) -> dict[str, Any]:
    """Run one deterministic Demucs6s Bass single-stem separation."""
    input_path = Path(input_audio)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    result = runner(demucs_bass_command(cli, input_path, output_path))
    outputs = discover_audio(output_path)
    bass = choose_stem(outputs, ("bass",))

    if int(getattr(result, "returncode", 1)) != 0 or bass is None:
        raise RuntimeError(
            "Demucs bass separation failed: "
            f"returnCode={getattr(result, 'returncode', None)}, "
            f"outputs={[str(path) for path in outputs]}"
        )

    return {
        "path": bass,
        "model": DEMUCS_6S_MODEL,
    }


def build_diagnostic_bass_stems(
    input_audio: Path | str,
    output_dir: Path | str,
) -> dict[str, Any]:
    """Build two reference-free Bass views without touching live routing.

    Candidate view A:
      normalized user audio -> Demucs6s Bass

    Candidate view B:
      normalized user audio -> BS-RoFormer Instrumental -> Demucs6s Bass

    This module is deliberately diagnostic-only. It creates a deterministic
    Bass separation substrate for future real-audio evaluation; it does not
    claim note/timing/technique quality, does not create a professional analyzer
    identity, and is not connected to `/api/analyze-audio-tab`.
    """
    source = Path(input_audio)
    root = Path(output_dir)

    if not source.exists() or source.stat().st_size <= 0:
        raise FileNotFoundError(source)

    root.mkdir(parents=True, exist_ok=True)
    work = root / "_work"
    normalized = normalize_input_audio(source, work / "normalized")
    cli = seeded_separator_cli()

    previous_hash_seed = os.environ.get("PYTHONHASHSEED")
    previous_separator_seed = os.environ.get("V143_SEPARATOR_SEED")
    os.environ["PYTHONHASHSEED"] = str(BASS_SEPARATOR_SEED)
    os.environ["V143_SEPARATOR_SEED"] = str(BASS_SEPARATOR_SEED)

    try:
        direct = separate_demucs_bass(
            cli,
            normalized,
            work / "direct",
        )
        instrumental = separate_roformer_instrumental(
            cli,
            normalized,
            work / "roformer",
        )
        cascade = separate_demucs_bass(
            cli,
            Path(instrumental["path"]),
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

    direct_out = root / "direct-demucs6s-bass.wav"
    cascade_out = root / "bsroformer-demucs6s-bass.wav"
    shutil.copy2(direct["path"], direct_out)
    shutil.copy2(cascade["path"], cascade_out)

    if (
        not direct_out.exists()
        or direct_out.stat().st_size <= 0
        or not cascade_out.exists()
        or cascade_out.stat().st_size <= 0
    ):
        raise RuntimeError("Diagnostic Bass separator outputs were not created correctly")

    return {
        "directBass": str(direct_out),
        "cascadeBass": str(cascade_out),
        "models": {
            "demucs": DEMUCS_6S_MODEL,
            "bsRoformer": BS_ROFORMER_MODEL,
        },
        "settings": {
            "demucsSingleStem": "Bass",
            "demucsShifts": BASS_DEMUCS_SHIFTS,
            "demucsOverlap": BASS_DEMUCS_OVERLAP,
            "demucsSegmentSize": BASS_DEMUCS_SEGMENT_SIZE,
            "roformerSingleStem": "Instrumental",
            "roformerBatchSize": 1,
            "deterministicSeed": BASS_SEPARATOR_SEED,
        },
        "referenceFree": True,
        "diagnosticOnly": True,
        "productionCandidate": False,
        "analyzerRoutingEnabled": False,
        "professionalStructuredIdentityEnabled": False,
        "liveEndpointDeployedOrModified": False,
        "productionModified": False,
        "productionPromotionAuthorized": False,
    }


def describe() -> dict[str, Any]:
    return {
        "mode": "inactive-bass-professional-separator-scaffold",
        "directPath": "audio -> Demucs6s Bass",
        "cascadePath": "audio -> BS-RoFormer Instrumental -> Demucs6s Bass",
        "demucsModel": DEMUCS_6S_MODEL,
        "bsRoformerModel": BS_ROFORMER_MODEL,
        "demucsSingleStem": "Bass",
        "demucsShifts": BASS_DEMUCS_SHIFTS,
        "demucsOverlap": BASS_DEMUCS_OVERLAP,
        "demucsSegmentSize": BASS_DEMUCS_SEGMENT_SIZE,
        "deterministicSeed": BASS_SEPARATOR_SEED,
        "referenceFree": True,
        "diagnosticOnly": True,
        "productionCandidate": False,
        "analyzerRoutingEnabled": False,
        "professionalStructuredIdentityEnabled": False,
        "liveEndpointDeployedOrModified": False,
        "productionModified": False,
        "productionPromotionAuthorized": False,
    }


__all__ = [
    "BASS_SEPARATOR_SEED",
    "BASS_DEMUCS_SHIFTS",
    "BASS_DEMUCS_OVERLAP",
    "BASS_DEMUCS_SEGMENT_SIZE",
    "seeded_separator_cli",
    "demucs_bass_command",
    "separate_demucs_bass",
    "build_diagnostic_bass_stems",
    "describe",
]
