from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

from v143_rhythm_sustain_technique_enricher import step_seconds_from_tempo, sustain_tier


def _finite(value: Any, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return number if math.isfinite(number) else float(fallback)


def promote_candidate_sustain_preserving_physical_onset(
    events: Sequence[Mapping[str, Any]],
    tempo_bpm: float,
) -> list[dict[str, Any]]:
    """Promote sustain while keeping grid time and physical attack time distinct.

    ``timeSeconds`` / ``start`` remain the quantized tab-grid time. ``onsetTime``
    remains the already-observed physical attack time supplied by candidate
    assembly. No attack, pitch, grid key, string, fret, or event count is changed.
    If no finite physical onset exists, the grid time is the conservative fallback.
    """
    one_step = step_seconds_from_tempo(float(tempo_bpm))
    output: list[dict[str, Any]] = []
    for index, raw in enumerate(events):
        event = dict(raw)
        grid_start = _finite(event.get("timeSeconds"), 0.0)
        physical_onset = _finite(event.get("onsetTime"), grid_start)
        shadow = event.get("rhythmSustainShadow") if isinstance(event.get("rhythmSustainShadow"), Mapping) else {}
        duration_steps = max(1, int(shadow.get("durationSteps") or 1))
        duration_seconds = max(0.0, _finite(shadow.get("durationSeconds"), one_step))
        if duration_seconds <= 0.0:
            duration_seconds = float(one_step)

        event["rhythmSustain"] = {
            "version": 4,
            "durationSeconds": float(duration_seconds),
            "durationSteps": int(duration_steps),
            "stepSeconds": float(one_step),
            "tier": sustain_tier(duration_steps),
            "source": "reference-free-two-view-harmonic-persistence-repaired-timing-precision-candidate",
            "attackTimingChanged": False,
            "physicalOnsetPreserved": True,
            "gridStartUnchanged": True,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
        }
        event["eventIndex"] = int(index)
        event["start"] = float(grid_start)
        event["end"] = float(grid_start + duration_seconds)
        event["duration"] = float(duration_seconds)
        event["onsetTime"] = float(physical_onset)
        event["offsetTime"] = float(physical_onset + duration_seconds)
        output.append(event)
    return output


__all__ = ["promote_candidate_sustain_preserving_physical_onset"]
