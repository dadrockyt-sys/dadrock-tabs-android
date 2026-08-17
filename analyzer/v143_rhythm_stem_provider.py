from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from v143_modal_rhythm_router import RhythmStemBundle
from v143_production_separator import build_v143_stems


SeparatorBuilder = Callable[[Path | str, Path | str], dict[str, Any]]


def build_rhythm_stem_bundle(
    normalized_full_mix_path: str | Path,
    *,
    separator_builder: SeparatorBuilder = build_v143_stems,
) -> RhythmStemBundle:
    """Build the authoritative V143 Rhythm Guitar stem bundle.

    The frozen separator produces two independently-derived guitar views:

    1. direct Demucs6s Guitar
    2. BS-RoFormer Instrumental -> Demucs6s Guitar

    Candidate detection is allowed to consume both separated guitar views for
    high recall. The frozen V143 carrier uses the same two views as its explicit
    paired A/B carrier contract; pair_patch() later converts them into the
    historical mean:: / agree:: feature substrate.

    The output directory is created beside the already-normalized request audio,
    so its lifetime is owned by the enclosing request temporary directory. This
    avoids returning paths from a nested TemporaryDirectory that would disappear
    before V143 consumes them.
    """
    normalized = Path(normalized_full_mix_path)
    if not normalized.exists() or normalized.stat().st_size <= 0:
        raise FileNotFoundError(normalized)

    output_dir = normalized.parent / "v143-rhythm-stems"
    result = separator_builder(normalized, output_dir)

    if not isinstance(result, dict):
        raise TypeError("V143 separator builder must return a dict")

    direct_raw = str(result.get("directGuitar") or "").strip()
    cascade_raw = str(result.get("cascadeGuitar") or "").strip()
    if not direct_raw or not cascade_raw:
        raise RuntimeError(
            "V143 separator did not return both directGuitar and cascadeGuitar"
        )

    direct = Path(direct_raw)
    cascade = Path(cascade_raw)

    for label, path in (("direct", direct), ("cascade", cascade)):
        if not path.exists() or path.stat().st_size <= 0:
            raise RuntimeError(f"V143 {label} guitar stem is missing: {path}")

    if direct.resolve() == cascade.resolve():
        raise RuntimeError("V143 paired carrier stems must be independent files")

    return RhythmStemBundle(
        candidate_stem_paths=(direct, cascade),
        carrier_stem_a_path=direct,
        carrier_stem_b_path=cascade,
    ).validate()


__all__ = ["build_rhythm_stem_bundle"]
