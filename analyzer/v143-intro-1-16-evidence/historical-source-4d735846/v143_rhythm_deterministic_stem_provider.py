from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from v143_deterministic_separator import build_deterministic_v143_stems
from v143_rhythm_stem_provider import build_rhythm_stem_bundle


DeterministicSeparatorBuilder = Callable[[Path | str, Path | str], dict[str, Any]]


def build_deterministic_rhythm_stem_bundle(
    normalized_full_mix_path: str | Path,
    *,
    separator_builder: DeterministicSeparatorBuilder = build_deterministic_v143_stems,
):
    """Build the authoritative Rhythm bundle through the deterministic separator."""
    return build_rhythm_stem_bundle(
        normalized_full_mix_path,
        separator_builder=separator_builder,
    )


__all__ = ["build_deterministic_rhythm_stem_bundle"]
