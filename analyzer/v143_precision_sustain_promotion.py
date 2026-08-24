from __future__ import annotations

import math
from typing import Any, Iterable, Mapping

from v143_rhythm_sustain_technique_enricher import step_seconds_from_tempo, sustain_tier


def _finite(value: Any, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return number if math.isfinite(number) else float(fallback)


def promote_candidate_sustain(
    events: Iterable[Mapping[str, Any]],
    tempo_bpm: float,
) -> list[dict[str, Any]]:
    """Promote candidate sustain without erasing physical attack provenance.

    `timeSeconds`, `start`, `end`, and `duration` remain the quantized tab-grid
    presentation contract. `onsetTime` remains the physical detected attack that
    arrived from candidate assembly. Sustain consensus is currently grid-anchored,
    so `offsetTime` remains the same absolute grid-start-plus-duration endpoint.
    The timing bases are serialized explicitly so downstream code cannot mistake
    the physical attack provenance for the quantized presentation start.
    """
    one_step = step_seconds_from_tempo(float(tempo_bpm))
    output: list[dict[str, Any]] = []

    for index, raw in enumerate(events):
        event = dict(raw)
        shadow = event.get("rhythmSustainShadow") if isinstance(event.get("rhythmSustainShadow"), Mapping) else {}
        duration_steps = max(1, int(shadow.get("durationSteps") or 1))
        duration_seconds = _finite(shadow.get("durationSeconds"), one_step)
        if duration_seconds <= 0.0:
            duration_seconds = float(one_step)

        start = _finite(event.get("timeSeconds"), 0.0)
        physical_onset = _finite(event.get("onsetTime"), start)
        end = start + duration_seconds

        event["rhythmSustain"] = {
            "version": 4,
            "durationSeconds": float(duration_seconds),
            "durationSteps": int(duration_steps),
            "stepSeconds": float(one_step),
            "tier": sustain_tier(duration_steps),
            "source": "reference-free-two-view-harmonic-persistence-repaired-timing-precision-candidate",
            "attackTimingChanged": False,
            "physicalOnsetPreserved": True,
            "analysisTimingBasis": "quantized-timeSeconds",
            "presentationStartBasis": "quantized-timeSeconds",
            "offsetTimingBasis": "quantized-timeSeconds-plus-durationSeconds",
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
        }
        event["eventIndex"] = int(index)
        event["start"] = float(start)
        event["end"] = float(end)
        event["duration"] = float(duration_seconds)
        event["onsetTime"] = float(physical_onset)
        event["offsetTime"] = float(end)
        event["physicalOnsetDeltaFromGridSeconds"] = float(physical_onset - start)
        output.append(event)

    return output


__all__ = ["promote_candidate_sustain"]
