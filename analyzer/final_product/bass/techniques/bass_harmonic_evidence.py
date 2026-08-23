from __future__ import annotations

import math
from copy import deepcopy
from pathlib import Path
from typing import Any, Sequence

from final_product.bass.techniques.bass_technique_evidence import (
    REQUIRED_VIEW_AGREEMENT,
    AudioBassTechniqueView,
    build_bass_technique_view,
)


STANDARD_BASS_OPEN_MIDI = (43, 38, 33, 28)  # G2, D2, A1, E1
STANDARD_BASS_STRING_LABELS = ("G", "D", "A", "E")
COMMON_NATURAL_HARMONIC_INTERVALS = (
    (12, 12),  # octave harmonic, physical node near fret 12
    (19, 7),   # third partial, physical node near fret 7
    (24, 5),   # double-octave harmonic, physical node near fret 5
)

MIN_HARMONIC_DURATION_SECONDS = 0.18
MIN_HARMONIC_DURATION_STEPS = 2
MAX_HARMONIC_ONSET_STRENGTH = 0.42
MIN_HARMONIC_TONAL_PURITY = 0.68
MIN_HARMONIC_UPPER_PARTIAL_RATIO = 0.22
MAX_HARMONIC_SUBHARMONIC_RATIO = 0.10


def _finite(value: Any, fallback: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return result if math.isfinite(result) else float(fallback)


def _integer(event: dict[str, Any], key: str) -> int | None:
    try:
        return int(round(float(event.get(key))))
    except (TypeError, ValueError):
        return None


def _band_energy(view: AudioBassTechniqueView, midi: float, half_width: float = 0.38) -> Any:
    import numpy as np

    indices = np.where(
        (view.midi_bins >= float(midi) - half_width)
        & (view.midi_bins <= float(midi) + half_width)
    )[0]
    if len(indices) == 0:
        return np.zeros(view.cqt.shape[1], dtype=float)
    return np.sum(view.cqt[indices, :], axis=0)


def natural_harmonic_sources(midi: int) -> list[dict[str, int | str]]:
    """Return common standard-Bass natural-harmonic origins for a sounding MIDI."""
    out: list[dict[str, int | str]] = []
    value = int(midi)
    for string_index, open_midi in enumerate(STANDARD_BASS_OPEN_MIDI):
        for interval, physical_node_fret in COMMON_NATURAL_HARMONIC_INTERVALS:
            if int(open_midi) + int(interval) == value:
                out.append(
                    {
                        "stringIndex": int(string_index),
                        "stringLabel": STANDARD_BASS_STRING_LABELS[string_index],
                        "openMidi": int(open_midi),
                        "soundingMidi": value,
                        "harmonicIntervalSemitones": int(interval),
                        "physicalNodeFret": int(physical_node_fret),
                    }
                )
    return out


def evaluate_natural_harmonic_view(
    view: AudioBassTechniqueView,
    event: dict[str, Any],
) -> dict[str, Any] | None:
    """Require a conservative natural-harmonic-like spectrum from one Bass view.

    This does not infer a physical fret from the mapped TAB position. It only
    considers pitches reachable as common open-string natural harmonics and then
    requires tonal purity, upper-partial support, weak subharmonic energy and a
    non-aggressive onset in the separated Bass audio.
    """
    import numpy as np

    midi = _integer(event, "midi")
    if midi is None or not 28 <= midi <= 67:
        return None
    sources = natural_harmonic_sources(midi)
    if not sources:
        return None

    onset = _finite(event.get("timeSeconds"), -1.0)
    duration = max(0.0, _finite(event.get("durationSeconds"), 0.0))
    duration_steps = max(1, int(_finite(event.get("durationSteps"), 1.0)))
    if onset < 0.0:
        return None
    if duration < MIN_HARMONIC_DURATION_SECONDS or duration_steps < MIN_HARMONIC_DURATION_STEPS:
        return None

    window_end = onset + min(0.48, max(0.20, duration))
    indices = np.where(
        (view.times >= onset + 0.025)
        & (view.times <= window_end)
    )[0]
    if len(indices) < 8:
        return None

    fundamental = _band_energy(view, midi)[indices]
    octave = _band_energy(view, midi + 12)[indices]
    third_partial = _band_energy(view, midi + 19)[indices]
    lower_octave = _band_energy(view, midi - 12)[indices]
    lower_third = _band_energy(view, midi - 19)[indices]
    neighbour_low = _band_energy(view, midi - 1.0, half_width=0.32)[indices]
    neighbour_high = _band_energy(view, midi + 1.0, half_width=0.32)[indices]

    fundamental_level = float(np.percentile(fundamental, 75))
    if fundamental_level <= 1.0e-10:
        return None

    octave_level = float(np.percentile(octave, 75))
    third_level = float(np.percentile(third_partial, 75))
    lower_level = float(np.percentile(lower_octave + 0.5 * lower_third, 75))
    neighbour_level = float(np.percentile(neighbour_low + neighbour_high, 75))

    tonal_purity = fundamental_level / max(fundamental_level + neighbour_level, 1.0e-10)
    upper_partial_ratio = (octave_level + 0.5 * third_level) / fundamental_level
    subharmonic_ratio = lower_level / fundamental_level
    onset_strength = float(view.onset_strength(onset))

    if tonal_purity < MIN_HARMONIC_TONAL_PURITY:
        return None
    if upper_partial_ratio < MIN_HARMONIC_UPPER_PARTIAL_RATIO:
        return None
    if subharmonic_ratio > MAX_HARMONIC_SUBHARMONIC_RATIO:
        return None
    if onset_strength > MAX_HARMONIC_ONSET_STRENGTH:
        return None

    purity_score = min(1.0, max(0.0, (tonal_purity - 0.5) / 0.5))
    partial_score = min(1.0, upper_partial_ratio / 0.75)
    subharmonic_score = max(0.0, 1.0 - subharmonic_ratio / MAX_HARMONIC_SUBHARMONIC_RATIO)
    onset_score = max(0.0, 1.0 - onset_strength / MAX_HARMONIC_ONSET_STRENGTH)
    score = 0.40 * purity_score + 0.30 * partial_score + 0.20 * subharmonic_score + 0.10 * onset_score

    return {
        "type": "harmonic",
        "family": "harmonic",
        "source": view.source_name,
        "score": round(float(score), 6),
        "soundingMidi": int(midi),
        "durationSeconds": round(duration, 5),
        "durationSteps": int(duration_steps),
        "tonalPurity": round(tonal_purity, 6),
        "upperPartialRatio": round(upper_partial_ratio, 6),
        "subharmonicRatio": round(subharmonic_ratio, 6),
        "onsetStrength": round(onset_strength, 6),
        "naturalHarmonicSources": deepcopy(sources),
        "referenceFree": True,
    }


def _harmonic_consensus(rows: Sequence[dict[str, Any] | None]) -> dict[str, Any] | None:
    present = [row for row in rows if isinstance(row, dict) and row.get("type") == "harmonic"]
    if len(present) < REQUIRED_VIEW_AGREEMENT:
        return None
    return {
        "type": "harmonic",
        "family": "harmonic",
        "score": round(
            sum(_finite(row.get("score"), 0.0) for row in present) / len(present),
            6,
        ),
        "viewAgreement": len(present),
        "requiredViewAgreement": REQUIRED_VIEW_AGREEMENT,
        "consensusPassed": True,
        "views": [deepcopy(row) for row in present],
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "detector": "standard-bass-natural-harmonic-spectrum-v1",
    }


def enrich_bass_events_with_harmonic_evidence(
    events: Sequence[dict[str, Any]],
    *,
    stem_paths: Sequence[str | Path],
) -> dict[str, Any]:
    """Append only two-view harmonic evidence without changing musical identity."""
    if len(stem_paths) < REQUIRED_VIEW_AGREEMENT:
        raise ValueError("Bass harmonic evidence requires direct and cascade Bass stems")

    views = [build_bass_technique_view(path) for path in stem_paths[:2]]
    enriched = [deepcopy(event) for event in events]
    harmonic_event_count = 0

    for event in enriched:
        consensus = _harmonic_consensus(
            [evaluate_natural_harmonic_view(view, event) for view in views]
        )
        labels = list(event.get("techniques") or [])
        evidence = list(event.get("bassTechniqueEvidence") or [])
        if consensus is not None:
            if "harmonic" not in labels:
                labels.append("harmonic")
            evidence.append(deepcopy(consensus))
            harmonic_event_count += 1
        event["techniques"] = labels
        event["bassTechniqueEvidence"] = evidence
        event["bassHarmonicEnrichment"] = {
            "version": 1,
            "mode": "reference-free-two-view-natural-harmonic-spectrum",
            "requiredViewAgreement": REQUIRED_VIEW_AGREEMENT,
            "noteTimingPlayabilityChanged": False,
            "harmonicEvidenceImplemented": True,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
        }

    return {
        "events": enriched,
        "diagnostics": {
            "eventCount": len(enriched),
            "harmonicEventCount": harmonic_event_count,
            "harmonicEvidenceObserved": harmonic_event_count > 0,
            "harmonicFamilyProven": harmonic_event_count > 0,
            "requiredViewAgreement": REQUIRED_VIEW_AGREEMENT,
            "harmonicEvidenceImplemented": True,
            "detector": "standard-bass-natural-harmonic-spectrum-v1",
            "thresholds": {
                "minimumDurationSeconds": MIN_HARMONIC_DURATION_SECONDS,
                "minimumDurationSteps": MIN_HARMONIC_DURATION_STEPS,
                "maximumOnsetStrength": MAX_HARMONIC_ONSET_STRENGTH,
                "minimumTonalPurity": MIN_HARMONIC_TONAL_PURITY,
                "minimumUpperPartialRatio": MIN_HARMONIC_UPPER_PARTIAL_RATIO,
                "maximumSubharmonicRatio": MAX_HARMONIC_SUBHARMONIC_RATIO,
            },
            "futureHighRiskFamiliesEnabled": False,
            "referenceFree": True,
        },
    }


__all__ = [
    "STANDARD_BASS_OPEN_MIDI",
    "COMMON_NATURAL_HARMONIC_INTERVALS",
    "natural_harmonic_sources",
    "evaluate_natural_harmonic_view",
    "enrich_bass_events_with_harmonic_evidence",
]
