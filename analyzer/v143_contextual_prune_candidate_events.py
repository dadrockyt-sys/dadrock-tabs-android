from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from v143_contextual_prune_shadow_correction import ShadowCorrectionResult
from v143_reference_free_rhythm_pipeline import ReferenceFreeRhythmResult
from v143_reference_free_timing import ReferenceFreeTimingEstimate
from v143_rhythm_event_assembly import RhythmEventAssemblyResult
from v143_rhythm_guitar_note_mapper import resolve_joint_chord_voicing


SPECTRUM_MIDI_MIN = 28
MAX_GUITAR_STRINGS = 6

EventKey = tuple[int, int]


@dataclass(frozen=True)
class CorrectedCandidateAssembly:
    source: ReferenceFreeRhythmResult
    assembly: RhythmEventAssemblyResult
    corrected_attack_count: int
    rendered_note_count: int
    supported_pitch_count: int
    rendered_pitch_count: int
    voicing_dropped_pitch_count: int

    def diagnostics(self) -> dict[str, Any]:
        return {
            "correctedAttackCount": int(self.corrected_attack_count),
            "renderedNoteCount": int(self.rendered_note_count),
            "supportedPitchCount": int(self.supported_pitch_count),
            "renderedPitchCount": int(self.rendered_pitch_count),
            "voicingDroppedPitchCount": int(self.voicing_dropped_pitch_count),
            "everyCorrectedAttackRendered": self.corrected_attack_count
            == len({(int(event["measure"]), int(event["step"])) for event in self.assembly.events}),
            "candidateAddsUnobservedPitch": False,
            "candidateRelocatesEvents": False,
            "referenceFree": True,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


def _finite(value: Any, fallback: float = -99.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return number if math.isfinite(number) else float(fallback)


def _vector_value(vector: Any, midi: int) -> float:
    index = int(midi) - SPECTRUM_MIDI_MIN
    if not isinstance(vector, Sequence) or isinstance(vector, (str, bytes, bytearray)):
        return -99.0
    if index < 0 or index >= len(vector):
        return -99.0
    return _finite(vector[index])


def _pitch_evidence(row: Mapping[str, Any], midi: int) -> dict[str, float]:
    view_a = row.get("viewA") if isinstance(row.get("viewA"), Mapping) else {}
    view_b = row.get("viewB") if isinstance(row.get("viewB"), Mapping) else {}
    attack = min(
        _vector_value(view_a.get("attackMax"), midi),
        _vector_value(view_b.get("attackMax"), midi),
    )
    early = min(
        _vector_value(view_a.get("earlyMean"), midi),
        _vector_value(view_b.get("earlyMean"), midi),
    )
    sustain = min(
        _vector_value(view_a.get("sustainMean"), midi),
        _vector_value(view_b.get("sustainMean"), midi),
    )
    body = max(early, sustain)
    continuity = min(early, sustain)
    score = attack + 0.65 * body + 0.15 * continuity
    return {
        "attack": float(attack),
        "early": float(early),
        "sustain": float(sustain),
        "body": float(body),
        "continuity": float(continuity),
        "score": float(score),
    }


def _grid_by_measure(grid: Mapping[EventKey, float]) -> dict[int, list[tuple[int, float]]]:
    out: dict[int, list[tuple[int, float]]] = {}
    for key, value in grid.items():
        measure, step = int(key[0]), int(key[1])
        time_value = float(value)
        if math.isfinite(time_value):
            out.setdefault(measure, []).append((step, time_value))
    for values in out.values():
        values.sort(key=lambda item: item[0])
    return out


def _best_rows_by_slot(
    rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
) -> dict[EventKey, dict[str, Any]]:
    grid_rows = _grid_by_measure(grid)
    best: dict[EventKey, dict[str, Any]] = {}
    for raw in rows:
        try:
            measure = int(raw["measure"])
            onset = float(raw["onsetTime"])
        except (KeyError, TypeError, ValueError):
            continue
        slots = grid_rows.get(measure) or ()
        if not slots:
            continue
        step, slot_time = min(slots, key=lambda item: (abs(onset - item[1]), item[0]))
        key = (measure, int(step))
        error = abs(onset - slot_time)
        candidate_midis = [
            int(value)
            for value in raw.get("candidateMidis") or ()
            if 28 <= int(value) <= 112
        ]
        strongest = max(
            (_pitch_evidence(raw, midi)["score"] for midi in candidate_midis),
            default=-99.0,
        )
        strength = float(
            strongest
            + 0.10 * min(4, max(0, int(raw.get("sweepSupportMax") or 0)))
            + 0.03 * min(16, max(0, int(raw.get("detectionCountSum") or 0)))
            - 2.0 * error
        )
        current = best.get(key)
        if current is None or strength > float(current["_candidateStrength"]):
            row = dict(raw)
            row["_candidateStrength"] = strength
            row["_candidateGridErrorSeconds"] = float(error)
            best[key] = row
    return best


def _voicing_for_supported_midis(
    row: Mapping[str, Any],
    supported_midis: Sequence[int],
) -> tuple[list[int], dict[int, dict[str, Any]], dict[int, dict[str, float]]]:
    evidence = {int(midi): _pitch_evidence(row, int(midi)) for midi in supported_midis}
    ranked = sorted(
        evidence,
        key=lambda midi: (
            -evidence[midi]["score"],
            -evidence[midi]["attack"],
            -evidence[midi]["body"],
            int(midi),
        ),
    )
    selected: list[int] = []
    voicing: dict[int, dict[str, Any]] | None = None
    for midi in ranked:
        if len(selected) >= MAX_GUITAR_STRINGS:
            break
        trial = selected + [int(midi)]
        trial_voicing = resolve_joint_chord_voicing(trial)
        if trial_voicing is None:
            continue
        selected = trial
        voicing = trial_voicing
    if not selected or voicing is None:
        raise RuntimeError("Corrected physical pitch set has no playable guitar voicing")
    return selected, voicing, evidence


def build_corrected_candidate_assembly(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    correction: ShadowCorrectionResult,
    timing: ReferenceFreeTimingEstimate,
) -> CorrectedCandidateAssembly:
    """Map accepted reference-free correction evidence into isolated guitar events.

    The correction has already decided which physical attack slots and pitch
    candidates survive. This adapter only resolves a playable six-string voicing.
    It never consults a professional reference, never relocates an attack, and
    never adds a pitch outside the correction's physically supported set.
    """
    if not isinstance(correction, ShadowCorrectionResult):
        raise TypeError("correction must be ShadowCorrectionResult")
    if not isinstance(timing, ReferenceFreeTimingEstimate):
        raise TypeError("timing must be ReferenceFreeTimingEstimate")

    rows_by_slot = _best_rows_by_slot(carrier_rows, grid)
    corrected_keys = sorted(correction.corrected_events)
    if not corrected_keys:
        raise RuntimeError("Corrected candidate contains no attacks")

    source_rows: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    supported_pitch_count = 0
    rendered_pitch_count = 0

    for rank, key in enumerate(corrected_keys, start=1):
        row = rows_by_slot.get(key)
        if row is None:
            raise RuntimeError(f"Corrected attack has no physical carrier row: {key}")
        supported = tuple(int(value) for value in correction.pitch_sets.get(key, ()))
        if not supported:
            raise RuntimeError(f"Corrected attack has no supported pitch set: {key}")
        supported_pitch_count += len(supported)

        selected_midis, voicing, evidence = _voicing_for_supported_midis(row, supported)
        rendered_pitch_count += len(selected_midis)
        dominant_midi = int(selected_midis[0])
        grid_time = float(grid[key])
        physical_onset = float(row.get("onsetTime") or grid_time)

        pitch_hypotheses = []
        for midi in supported:
            item = evidence[int(midi)]
            pitch_hypotheses.append(
                {
                    "midi": int(midi),
                    "physicalAttack": float(item["attack"]),
                    "physicalBody": float(item["body"]),
                    "physicalContinuity": float(item["continuity"]),
                    "physicalScore": float(item["score"]),
                    "stemSupport": int(row.get("stemSupportMax") or 0),
                    "sweepSupport": int(row.get("sweepSupportMax") or 0),
                    "detectionCount": int(row.get("detectionCountSum") or 0),
                    "source": "reference-free-two-view-cqt-consensus",
                }
            )

        source_row = {
            "measure": int(key[0]),
            "step": int(key[1]),
            "timeSeconds": grid_time,
            "onsetTime": physical_onset,
            "dominantMidi": dominant_midi,
            "pitchHypotheses": deepcopy(pitch_hypotheses),
            "v143Score": float(row.get("_candidateStrength") or 0.0),
            "v143Rank": int(rank),
            "v143Selected": True,
            "candidateMode": "contextual-prune-reference-free-corrected-shadow",
        }
        source_rows.append(source_row)

        ordered_midis = sorted(
            selected_midis,
            key=lambda midi: (
                int(voicing[int(midi)]["stringIndex"]),
                int(midi),
            ),
        )
        for note_index, midi in enumerate(ordered_midis):
            position = voicing[int(midi)]
            event = deepcopy(source_row)
            event["midi"] = int(midi)
            event["stringIndex"] = int(position["stringIndex"])
            event["stringName"] = str(position["stringName"])
            event["fret"] = int(position["fret"])
            event["rhythmTechniques"] = []
            event["noteMapping"] = {
                "version": 3,
                "mode": "reference-free-corrected-physical-joint-voicing",
                "tuning": "standard",
                "jointChordVoicingResolved": True,
                "sourceAttackMidi": dominant_midi,
                "chordNoteIndex": int(note_index),
                "chordNoteCount": len(ordered_midis),
                "primaryTechniqueNote": int(midi) == dominant_midi,
                "professionalReferenceUsed": False,
                "runtimeLabelsRequired": False,
            }
            events.append(event)

    source = ReferenceFreeRhythmResult(
        timing=timing,
        candidates=tuple(deepcopy(row) for row in source_rows),
        rows=tuple(deepcopy(row) for row in source_rows),
    )
    assembly = RhythmEventAssemblyResult(
        source=source,
        events=tuple(deepcopy(event) for event in events),
    )

    emitted_keys = {(int(event["measure"]), int(event["step"])) for event in events}
    if emitted_keys != set(corrected_keys):
        raise RuntimeError("Corrected candidate event adapter changed attack identity")

    for event in events:
        key = (int(event["measure"]), int(event["step"]))
        if int(event["midi"]) not in set(correction.pitch_sets[key]):
            raise RuntimeError(f"Candidate adapter invented pitch at {key}")

    return CorrectedCandidateAssembly(
        source=source,
        assembly=assembly,
        corrected_attack_count=len(corrected_keys),
        rendered_note_count=len(events),
        supported_pitch_count=int(supported_pitch_count),
        rendered_pitch_count=int(rendered_pitch_count),
        voicing_dropped_pitch_count=int(supported_pitch_count - rendered_pitch_count),
    )


__all__ = [
    "CorrectedCandidateAssembly",
    "build_corrected_candidate_assembly",
]
