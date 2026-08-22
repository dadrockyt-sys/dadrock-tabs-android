from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable


# Repository/rendering convention:
# stringIndex 0 = high e ... stringIndex 5 = low E.
STRING_NAMES_HIGH_TO_LOW = ("e", "B", "G", "D", "A", "E")
OPEN_MIDI_HIGH_TO_LOW = (64, 59, 55, 50, 45, 40)
MAX_FRET = 24


def legal_positions_for_midi(
    midi: int,
    *,
    max_fret: int = MAX_FRET,
) -> list[dict[str, Any]]:
    midi = int(midi)
    max_fret = int(max_fret)

    if max_fret < 0:
        raise ValueError("max_fret cannot be negative")

    positions: list[dict[str, Any]] = []

    for string_index, open_midi in enumerate(OPEN_MIDI_HIGH_TO_LOW):
        fret = midi - open_midi
        if 0 <= fret <= max_fret:
            positions.append(
                {
                    "stringIndex": int(string_index),
                    "stringName": STRING_NAMES_HIGH_TO_LOW[string_index],
                    "fret": int(fret),
                }
            )

    if not positions:
        raise ValueError(
            f"MIDI {midi} is not playable in standard tuning "
            f"within frets 0-{max_fret}"
        )

    # Deterministic checkpoint policy only.
    # Prefer the lowest fret; stringIndex breaks any theoretical tie.
    positions.sort(
        key=lambda position: (
            int(position["fret"]),
            int(position["stringIndex"]),
        )
    )
    return positions


def _hypothesis_quality(hypothesis: dict[str, Any]) -> tuple[float, ...]:
    return (
        float(hypothesis.get("sourceCount", 0)),
        float(hypothesis.get("maxAmplitude", 0.0)),
        -float(hypothesis.get("minGridError", 0.0)),
        float(hypothesis.get("maxDuration", 0.0)),
        -float(hypothesis.get("midi", 0)),
    )


def dominant_midi_from_row(row: dict[str, Any]) -> int:
    if row.get("dominantMidi") is not None:
        return int(row["dominantMidi"])

    hypotheses = list(row.get("pitchHypotheses") or [])
    if not hypotheses:
        raise ValueError(
            "Selected V143 row has neither dominantMidi nor pitchHypotheses"
        )

    best = max(hypotheses, key=_hypothesis_quality)
    return int(best["midi"])


def map_pitch_hypothesis(
    hypothesis: dict[str, Any],
) -> dict[str, Any]:
    out = deepcopy(hypothesis)
    midi = int(out["midi"])

    positions = legal_positions_for_midi(midi)
    preferred = positions[0]

    out["legalPositions"] = positions
    out["preferredPosition"] = deepcopy(preferred)

    return out


def map_selected_v143_rows(
    ranked_rows: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert frozen V143-selected rhythm attacks into guitar-note events.

    This layer does not score, rank, select, re-time, or modify pitch evidence.
    The primary position is deliberately deterministic and conservative.
    All pitch hypotheses are retained for later chord/voicing resolution.
    """
    events: list[dict[str, Any]] = []

    for raw_row in ranked_rows:
        if raw_row.get("v143Selected") is not True:
            continue

        row = deepcopy(raw_row)
        midi = dominant_midi_from_row(row)

        positions = legal_positions_for_midi(midi)
        preferred = positions[0]

        row["midi"] = int(midi)
        row["stringIndex"] = int(preferred["stringIndex"])
        row["stringName"] = str(preferred["stringName"])
        row["fret"] = int(preferred["fret"])

        original_hypotheses = list(row.get("pitchHypotheses") or [])
        row["mappedPitchHypotheses"] = [
            map_pitch_hypothesis(hypothesis)
            for hypothesis in original_hypotheses
        ]

        row["noteMapping"] = {
            "version": 1,
            "mode": "dominant-midi-lowest-fret",
            "tuning": "standard",
            "stringOrder": "high-to-low",
            "maxFret": MAX_FRET,
            "jointChordVoicingResolved": False,
        }

        events.append(row)

    return events


__all__ = [
    "STRING_NAMES_HIGH_TO_LOW",
    "OPEN_MIDI_HIGH_TO_LOW",
    "MAX_FRET",
    "legal_positions_for_midi",
    "dominant_midi_from_row",
    "map_pitch_hypothesis",
    "map_selected_v143_rows",
]
