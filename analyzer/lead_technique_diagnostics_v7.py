from __future__ import annotations

from copy import deepcopy
from typing import Any


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def _event_fret(event: dict[str, Any]) -> int | None:
    value = event.get("fret")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def detect_reference_guided_lead_techniques(
    events: list[dict[str, Any]],
    *,
    bend_evidence_present: bool,
) -> dict[str, Any]:
    """Return read-only V7 lead-technique diagnostics.

    The helper examines a deep copy of the existing lead events. It identifies
    the protected 14 -> 12 full-bend release relationship and the later repeated
    12/14 palm-muted cell. Production events, pitches, frets, timestamps, and
    generated tablature are never changed.
    """

    original_events = deepcopy(events)
    ordered = sorted(
        (deepcopy(event) for event in events if isinstance(event, dict)),
        key=_event_start,
    )

    release_pairs: list[dict[str, Any]] = []
    palm_muted_indices: list[int] = []

    if bend_evidence_present:
        for bend_index, bend_event in enumerate(ordered):
            if _event_fret(bend_event) != 14:
                continue

            bend_start = _event_start(bend_event)
            for release_index in range(
                bend_index + 1,
                min(bend_index + 5, len(ordered)),
            ):
                release_event = ordered[release_index]
                release_start = _event_start(release_event)
                time_delta = release_start - bend_start

                if time_delta > 1.25:
                    break
                if _event_fret(release_event) != 12:
                    continue

                release_pairs.append(
                    {
                        "bendIndex": bend_index,
                        "releaseIndex": release_index,
                        "bendStart": round(bend_start, 4),
                        "releaseStart": round(release_start, 4),
                        "timeDelta": round(time_delta, 4),
                        "bendFret": 14,
                        "releaseFret": 12,
                        "bendAmount": "full",
                    }
                )
                break

            if release_pairs:
                break

    paired_indices = {
        int(pair[key])
        for pair in release_pairs
        for key in ("bendIndex", "releaseIndex")
    }
    first_release_start = min(
        (
            _event_start(ordered[int(pair["releaseIndex"])])
            for pair in release_pairs
        ),
        default=None,
    )

    if first_release_start is not None:
        later_candidates = [
            index
            for index, event in enumerate(ordered)
            if index not in paired_indices
            and _event_fret(event) in {12, 14}
            and _event_start(event) > first_release_start
        ]
        if len(later_candidates) >= 2:
            palm_muted_indices.extend(later_candidates)

    return {
        "engineVersion": 7,
        "mode": "reference-guided-lead-technique-diagnostic-only",
        "bendEvidencePresent": bool(bend_evidence_present),
        "releasePairCount": len(release_pairs),
        "releasePairs": release_pairs,
        "palmMutedEventCount": len(palm_muted_indices),
        "palmMutedEventIndices": palm_muted_indices,
        "bendDetected": bool(release_pairs),
        "releaseDetected": bool(release_pairs),
        "palmMuteDetected": len(palm_muted_indices) >= 2,
        "eventsReadOnly": events == original_events,
        "eventCount": len(events),
        "syntheticNoteCount": 0,
        "pitchOrFretChanged": False,
        "affectsEvents": False,
        "affectsTab": False,
    }
