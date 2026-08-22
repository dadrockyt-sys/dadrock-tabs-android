from __future__ import annotations

from pathlib import Path
from typing import Any

from v143_seeded_separator import build_seeded_v143_stems


PRODUCTION_SEPARATOR_SEED = 143


def build_deterministic_v143_stems(
    input_audio: Path | str,
    output_dir: Path | str,
) -> dict[str, Any]:
    """Production-candidate deterministic wrapper for the frozen V143 graph.

    The validated seeded separator already proved two fresh full separations are
    byte-identical and produce identical notes, bends and legato output. This
    wrapper promotes that exact behavior without changing model choices or frozen
    separator parameters.
    """
    result = dict(build_seeded_v143_stems(input_audio, output_dir))
    settings = dict(result.get("settings") or {})

    if int(settings.get("demucsShifts") or 0) != 1:
        raise RuntimeError("Deterministic V143 promotion must preserve demucsShifts=1")
    if float(settings.get("demucsOverlap") or 0.0) != 0.10:
        raise RuntimeError("Deterministic V143 promotion must preserve demucsOverlap=.10")
    if int(settings.get("demucsSegmentSize") or 0) != 6:
        raise RuntimeError("Deterministic V143 promotion must preserve demucsSegmentSize=6")
    if int(settings.get("deterministicSeed") or 0) != PRODUCTION_SEPARATOR_SEED:
        raise RuntimeError("Deterministic V143 promotion must use seed 143")

    result["diagnosticOnly"] = False
    result["deterministic"] = True
    result["productionCandidate"] = True
    result["promotionCheckpoint"] = "seeded-repeatability-all-exact"
    return result


__all__ = [
    "PRODUCTION_SEPARATOR_SEED",
    "build_deterministic_v143_stems",
]
