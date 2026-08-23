from __future__ import annotations

from copy import deepcopy
from itertools import product
from typing import Any, Iterable


# Repository/rendering convention:
# stringIndex 0 = high e ... stringIndex 5 = low E.
STRING_NAMES_HIGH_TO_LOW = ("e", "B", "G", "D", "A", "E")
OPEN_MIDI_HIGH_TO_LOW = (64, 59, 55, 50, 45, 40)
MAX_FRET = 24

# Reference-free polyphony guardrails. These operate only on Basic Pitch
# evidence already present in each frozen V143 attack row; no song/reference
# labels are consulted.
MIN_SECONDARY_AMPLITUDE = 0.11
MIN_SECONDARY_RELATIVE_AMPLITUDE = 0.40
MIN_SECONDARY_EVENT_COUNT = 2
MAX_SECONDARY_GRID_ERROR_SECONDS = 0.06
MIN_SECONDARY_DURATION_SECONDS = 0.05
MAX_CHORD_NOTES = len(OPEN_MIDI_HIGH_TO_LOW)
MAX_CHORD_PITCH_SPAN_SEMITONES = 28
NEAR_UNISON_SEMITONES = 1
NEAR_UNISON_KEEP_RATIO = 0.80


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
        float(hypothesis.get("eventCount", 0)),
        -float(hypothesis.get("minGridError", 999.0)),
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


def credible_polyphonic_hypotheses(
    row: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Return strong simultaneous pitch evidence for one frozen attack.

    The thresholds intentionally sit above the candidate detector's low
    probability floor and require repeated/source-consistent evidence,
    onset-grid agreement, and a minimally sustained note. The frozen
    dominant MIDI is separately guaranteed by the caller.
    """
    playable: list[dict[str, Any]] = []
    for raw in row.get("pitchHypotheses") or []:
        hypothesis = deepcopy(raw)
        try:
            legal_positions_for_midi(int(hypothesis["midi"]))
        except (KeyError, TypeError, ValueError):
            continue
        playable.append(hypothesis)

    if not playable:
        return []

    max_source_count = max(int(item.get("sourceCount", 0)) for item in playable)
    top_amplitude = max(float(item.get("maxAmplitude", 0.0)) for item in playable)
    amplitude_floor = max(
        MIN_SECONDARY_AMPLITUDE,
        top_amplitude * MIN_SECONDARY_RELATIVE_AMPLITUDE,
    )

    credible = [
        item
        for item in playable
        if int(item.get("sourceCount", 0)) == max_source_count
        and float(item.get("maxAmplitude", 0.0)) >= amplitude_floor
        and int(item.get("eventCount", 0)) >= MIN_SECONDARY_EVENT_COUNT
        and float(item.get("minGridError", 999.0))
        <= MAX_SECONDARY_GRID_ERROR_SECONDS
        and float(item.get("maxDuration", 0.0))
        >= MIN_SECONDARY_DURATION_SECONDS
    ]
    credible.sort(key=_hypothesis_quality, reverse=True)
    return credible


def _suppress_weak_near_unisons(
    hypotheses: Iterable[dict[str, Any]],
    *,
    dominant_midi: int,
) -> list[dict[str, Any]]:
    """
    Suppress weak +/-1-semitone estimator ambiguity while retaining strong dyads.

    A neighboring pitch survives when its amplitude is within 80% of the
    already-retained neighbor. This keeps genuinely strong close intervals
    possible rather than banning them outright.
    """
    ranked = sorted(
        (deepcopy(item) for item in hypotheses),
        key=_hypothesis_quality,
        reverse=True,
    )
    dominant = next(
        (item for item in ranked if int(item["midi"]) == int(dominant_midi)),
        None,
    )
    ordered = ([dominant] if dominant is not None else []) + [
        item for item in ranked if item is not dominant
    ]

    kept: list[dict[str, Any]] = []
    for item in ordered:
        midi = int(item["midi"])
        amplitude = float(item.get("maxAmplitude", 0.0))
        conflict = next(
            (
                prior
                for prior in kept
                if abs(midi - int(prior["midi"])) <= NEAR_UNISON_SEMITONES
            ),
            None,
        )
        if conflict is None:
            kept.append(item)
            continue

        prior_amplitude = float(conflict.get("maxAmplitude", 0.0))
        stronger = max(amplitude, prior_amplitude)
        weaker = min(amplitude, prior_amplitude)
        if stronger <= 0.0 or weaker >= stronger * NEAR_UNISON_KEEP_RATIO:
            kept.append(item)

    return kept


def resolve_joint_chord_voicing(
    midis: Iterable[int],
) -> dict[int, dict[str, Any]] | None:
    """
    Resolve a deterministic, non-crossing guitar voicing with unique strings.

    The pitch set is fixed before this function is called. This resolver only
    chooses where those pitches can physically be played; it never adds notes.
    """
    ordered_midis = tuple(sorted({int(value) for value in midis}))
    if not ordered_midis:
        return None
    if len(ordered_midis) > MAX_CHORD_NOTES:
        return None
    if ordered_midis[-1] - ordered_midis[0] > MAX_CHORD_PITCH_SPAN_SEMITONES:
        return None

    position_sets: list[list[dict[str, Any]]] = []
    for midi in ordered_midis:
        try:
            position_sets.append(legal_positions_for_midi(midi))
        except ValueError:
            return None

    best_key: tuple[Any, ...] | None = None
    best_positions: tuple[dict[str, Any], ...] | None = None

    for positions in product(*position_sets):
        string_indices = tuple(int(item["stringIndex"]) for item in positions)
        if len(set(string_indices)) != len(string_indices):
            continue

        # ordered_midis ascends from low pitch to high pitch. With the
        # repository's high-to-low string indexing, a non-crossing voicing
        # therefore requires strictly descending string indices.
        if any(
            string_indices[index] <= string_indices[index + 1]
            for index in range(len(string_indices) - 1)
        ):
            continue

        frets = tuple(int(item["fret"]) for item in positions)
        fret_span = max(frets) - min(frets)
        key = (
            int(fret_span),
            int(max(frets)),
            int(sum(frets)),
            int(sum(1 for fret in frets if fret > 12)),
            string_indices,
            frets,
        )
        if best_key is None or key < best_key:
            best_key = key
            best_positions = positions

    if best_positions is None:
        return None

    return {
        int(midi): deepcopy(position)
        for midi, position in zip(ordered_midis, best_positions)
    }


def select_polyphonic_hypotheses(
    row: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    """
    Select a conservative playable note set from one frozen attack row.

    The original V143 attack decision remains immutable. Strong secondary
    hypotheses are admitted only when the whole set still has a physical,
    non-crossing six-string voicing.
    """
    dominant_midi = dominant_midi_from_row(row)
    hypotheses = [
        deepcopy(item)
        for item in row.get("pitchHypotheses") or []
        if item.get("midi") is not None
    ]
    by_midi = {int(item["midi"]): item for item in hypotheses}
    dominant = by_midi.get(int(dominant_midi))
    if dominant is None:
        raise ValueError(
            f"Frozen dominant MIDI {dominant_midi} is absent from pitchHypotheses"
        )

    credible = _suppress_weak_near_unisons(
        credible_polyphonic_hypotheses(row),
        dominant_midi=dominant_midi,
    )
    ordered = [dominant] + [
        item for item in credible if int(item["midi"]) != int(dominant_midi)
    ]

    selected: list[dict[str, Any]] = []
    voicing: dict[int, dict[str, Any]] | None = None
    seen_midis: set[int] = set()

    for item in ordered:
        midi = int(item["midi"])
        if midi in seen_midis:
            continue
        seen_midis.add(midi)

        if len(selected) >= MAX_CHORD_NOTES:
            break

        trial = selected + [item]
        trial_midis = [int(candidate["midi"]) for candidate in trial]
        trial_voicing = resolve_joint_chord_voicing(trial_midis)
        if trial_voicing is None:
            continue

        selected = trial
        voicing = trial_voicing

    if not selected or voicing is None:
        fallback = resolve_joint_chord_voicing([dominant_midi])
        if fallback is None:
            raise ValueError(
                f"Frozen dominant MIDI {dominant_midi} has no legal guitar position"
            )
        selected = [dominant]
        voicing = fallback

    return [deepcopy(item) for item in selected], deepcopy(voicing)


def _clear_secondary_technique_fields(event: dict[str, Any]) -> None:
    # Upstream technique attributes describe the frozen attack as a whole and
    # historically belonged to its dominant note. Do not multiply a bend,
    # slide, harmonic, mute, etc. across every newly recovered chord tone.
    fields = (
        "technique",
        "techniques",
        "bendSemitones",
        "bendTargetFret",
        "bendRelease",
        "palmMuted",
        "palmMute",
        "hammerOn",
        "pullOff",
        "vibrato",
        "deadNote",
        "mutedStrum",
        "naturalHarmonic",
        "pinchHarmonic",
        "tap",
        "trill",
        "letRing",
        "sustainTie",
        "slideDirection",
    )
    for field in fields:
        event.pop(field, None)


def map_selected_v143_rows(
    ranked_rows: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert frozen V143-selected rhythm attacks into playable guitar-note events.

    V143 score/rank/selection and attack timing remain untouched. Each selected
    attack always emits its frozen dominant note and may emit additional notes
    only from strong reference-free pitch hypotheses already attached to that
    same attack. Joint voicing resolution guarantees unique guitar strings.
    """
    events: list[dict[str, Any]] = []

    for raw_row in ranked_rows:
        if raw_row.get("v143Selected") is not True:
            continue

        row = deepcopy(raw_row)
        dominant_midi = dominant_midi_from_row(row)
        selected, voicing = select_polyphonic_hypotheses(row)
        ordered_notes = sorted(
            selected,
            key=lambda item: (
                int(voicing[int(item["midi"])]["stringIndex"]),
                int(item["midi"]),
            ),
        )
        chord_note_count = len(ordered_notes)

        original_hypotheses = list(row.get("pitchHypotheses") or [])
        mapped_hypotheses = [
            map_pitch_hypothesis(hypothesis)
            for hypothesis in original_hypotheses
            if hypothesis.get("midi") is not None
        ]

        for chord_note_index, hypothesis in enumerate(ordered_notes):
            midi = int(hypothesis["midi"])
            position = voicing[midi]
            event = deepcopy(row)

            if midi != int(dominant_midi):
                _clear_secondary_technique_fields(event)

            event["midi"] = midi
            event["stringIndex"] = int(position["stringIndex"])
            event["stringName"] = str(position["stringName"])
            event["fret"] = int(position["fret"])
            event["mappedPitchHypotheses"] = deepcopy(mapped_hypotheses)
            event["noteMapping"] = {
                "version": 2,
                "mode": "reference-free-polyphonic-joint-voicing",
                "tuning": "standard",
                "stringOrder": "high-to-low",
                "maxFret": MAX_FRET,
                "jointChordVoicingResolved": True,
                "polyphonicExpansion": chord_note_count > 1,
                "sourceAttackMidi": int(dominant_midi),
                "chordNoteIndex": int(chord_note_index),
                "chordNoteCount": int(chord_note_count),
                "primaryTechniqueNote": midi == int(dominant_midi),
                "professionalReferenceUsed": False,
                "runtimeLabelsRequired": False,
            }
            events.append(event)

    return events


__all__ = [
    "STRING_NAMES_HIGH_TO_LOW",
    "OPEN_MIDI_HIGH_TO_LOW",
    "MAX_FRET",
    "MIN_SECONDARY_AMPLITUDE",
    "MIN_SECONDARY_RELATIVE_AMPLITUDE",
    "MIN_SECONDARY_EVENT_COUNT",
    "MAX_SECONDARY_GRID_ERROR_SECONDS",
    "MIN_SECONDARY_DURATION_SECONDS",
    "MAX_CHORD_NOTES",
    "MAX_CHORD_PITCH_SPAN_SEMITONES",
    "legal_positions_for_midi",
    "dominant_midi_from_row",
    "map_pitch_hypothesis",
    "credible_polyphonic_hypotheses",
    "resolve_joint_chord_voicing",
    "select_polyphonic_hypotheses",
    "map_selected_v143_rows",
]
