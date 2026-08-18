from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Iterable

from v143_modal_rhythm_router import RhythmStemBundle
from v143_rhythm_bend_evidence import (
    PitchEnergyView,
    build_pitch_energy_view,
    enrich_rhythm_assembly_with_audio_bends,
)
from v143_rhythm_event_assembly import RhythmEventAssemblyResult


BEND_EVIDENCE_SOURCE = "reference-free-audio-pitch-contour"
BEND_FIELDS = (
    "bendSemitones",
    "bendTargetMidi",
    "bendTargetFret",
    "bendRelease",
    "bendEvidence",
)


def _unique_paths(paths: Iterable[str | Path]) -> tuple[Path, ...]:
    unique: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path not in unique:
            unique.append(path)
    return tuple(unique)


def _strip_unconfirmed_bend(event: dict[str, Any]) -> dict[str, Any]:
    cleaned = deepcopy(event)
    for field in BEND_FIELDS:
        cleaned.pop(field, None)

    techniques = []
    for item in cleaned.get("rhythmTechniques", []) or []:
        if not isinstance(item, dict):
            techniques.append(deepcopy(item))
            continue
        technique_type = str(item.get("type") or "")
        source = str(item.get("source") or "")
        if (
            technique_type in {"bend", "bend-release"}
            and source == BEND_EVIDENCE_SOURCE
        ):
            continue
        techniques.append(deepcopy(item))
    cleaned["rhythmTechniques"] = techniques
    return cleaned


def enforce_bend_view_consensus(
    assembly: RhythmEventAssemblyResult,
    *,
    required_views: int,
) -> RhythmEventAssemblyResult:
    """Remove audio-derived bend annotations that lack the required view agreement."""
    if not isinstance(assembly, RhythmEventAssemblyResult):
        raise TypeError("assembly must be RhythmEventAssemblyResult")

    required = max(1, int(required_views))
    events: list[dict[str, Any]] = []

    for raw_event in assembly.events:
        event = deepcopy(raw_event)
        evidence = event.get("bendEvidence")
        if not isinstance(evidence, dict):
            events.append(event)
            continue

        agreement = int(evidence.get("viewAgreement") or 0)
        if agreement < required:
            event = _strip_unconfirmed_bend(event)
        else:
            event["bendEvidence"] = dict(evidence)
            event["bendEvidence"]["requiredViewAgreement"] = required
            event["bendEvidence"]["consensusPassed"] = True
        events.append(event)

    return RhythmEventAssemblyResult(
        source=assembly.source,
        events=tuple(events),
    )


def enrich_rhythm_assembly_with_consensus_bends(
    assembly: RhythmEventAssemblyResult,
    *,
    carrier_stem_paths: Iterable[str | Path],
    view_builder: Callable[[str | Path], PitchEnergyView] = build_pitch_energy_view,
) -> RhythmEventAssemblyResult:
    """Run reference-free bend evidence and require every available carrier view.

    Production supplies two independently separated guitar carriers. When both are
    present, a bend must be detected with the same semitone amount in both views.
    A single-carrier fallback remains deterministic for isolated verification only.
    """
    paths = _unique_paths(carrier_stem_paths)
    if not paths:
        return assembly

    enriched = enrich_rhythm_assembly_with_audio_bends(
        assembly,
        carrier_stem_paths=paths,
        view_builder=view_builder,
    )
    required_views = min(2, len(paths))
    return enforce_bend_view_consensus(
        enriched,
        required_views=required_views,
    )


def enrich_router_assembly_with_consensus_bends(
    assembly: RhythmEventAssemblyResult,
    bundle: RhythmStemBundle,
) -> RhythmEventAssemblyResult:
    """Production router hook requiring agreement across both carrier stems."""
    return enrich_rhythm_assembly_with_consensus_bends(
        assembly,
        carrier_stem_paths=(
            bundle.carrier_stem_a_path,
            bundle.carrier_stem_b_path,
        ),
    )


__all__ = [
    "BEND_EVIDENCE_SOURCE",
    "BEND_FIELDS",
    "enforce_bend_view_consensus",
    "enrich_rhythm_assembly_with_consensus_bends",
    "enrich_router_assembly_with_consensus_bends",
]
