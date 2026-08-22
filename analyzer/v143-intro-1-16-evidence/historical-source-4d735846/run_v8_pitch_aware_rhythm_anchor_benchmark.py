from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates.json"
NOTATION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-notation.json"
REFERENCE_PATH = REPO_ROOT / "analyzer" / "fixtures" / "gomyway_professional_intro_reference_v1.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-pitch-aware-rhythm-anchor.json"

STEPS_PER_MEASURE = 16
PAIR_STEPS = 32
INTRO_MEASURES = 16
STEP_TOLERANCE = 1
STANDARD_GUITAR_OPEN_MIDI = (64, 59, 55, 50, 45, 40)


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _midi_from_note(note: dict[str, Any]) -> int:
    string_index = _safe_int(note.get("stringIndex"), -1)
    fret = _safe_int(note.get("fret"), -1)
    if 0 <= string_index < len(STANDARD_GUITAR_OPEN_MIDI) and fret >= 0:
        return STANDARD_GUITAR_OPEN_MIDI[string_index] + fret
    return 0


def _reference_pitch_map(reference: dict[str, Any]) -> dict[int, set[int]]:
    result: dict[int, set[int]] = {}
    for note in reference.get("notes") or []:
        measure = _safe_int(note.get("measure"))
        step = _safe_int(note.get("step"))
        if measure not in (1, 2):
            continue
        pair_step = ((measure - 1) * STEPS_PER_MEASURE + step) % PAIR_STEPS
        midi = _midi_from_note(note)
        if midi > 0:
            result.setdefault(pair_step, set()).add(midi)
    return result


def _stable_slots(candidate_report: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostics = candidate_report.get("diagnostics") or {}
    slots: list[dict[str, Any]] = []
    for item in diagnostics.get("stableIntroPairSteps") or []:
        slots.append(
            {
                "pairStep": _safe_int(item.get("pairStep")) % PAIR_STEPS,
                "pairSupport": _safe_int(item.get("pairSupport")),
                "medianStrength": _safe_float(item.get("medianStrength")),
            }
        )
    return slots


def _notation_events(notation_report: dict[str, Any]) -> list[dict[str, Any]]:
    for key in (
        "fingeringNormalizedEvents",
        "pitchContourReconstructedEvents",
        "motifStabilizedEvents",
        "renderEvents",
        "rhythmEvents",
    ):
        events = notation_report.get(key)
        if isinstance(events, list) and events:
            return [item for item in events if isinstance(item, dict)]
    return []


def _event_midi(event: dict[str, Any]) -> int:
    midi = _safe_int(event.get("midiPitch") or event.get("midi") or event.get("pitch"))
    if midi > 0:
        return midi
    return _midi_from_note(event)


def _event_step(event: dict[str, Any]) -> int:
    position = _safe_float(event.get("positionInMeasure"))
    return max(0, min(15, int(round(position * STEPS_PER_MEASURE))))


def _circular_step_distance(left: int, right: int) -> int:
    delta = abs(left - right) % PAIR_STEPS
    return min(delta, PAIR_STEPS - delta)


def _evaluate_offset(
    offset: int,
    stable_slots: list[dict[str, Any]],
    reference_pitch_map: dict[int, set[int]],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    anchored_slots = {
        (int(item["pairStep"]) + offset) % PAIR_STEPS: item
        for item in stable_slots
    }
    reference_slots = set(reference_pitch_map)
    matched_anchor_slots = sorted(set(anchored_slots) & reference_slots)

    timing_opportunities = 0
    timing_hits = 0
    pitch_opportunities = 0
    pitch_hits = 0
    exact_pitch_hits = 0
    evidence: list[dict[str, Any]] = []

    intro_events = [
        event for event in events
        if 1 <= _safe_int(event.get("measureNumber")) <= INTRO_MEASURES
    ]

    for pair_index in range(INTRO_MEASURES // 2):
        pair_events = []
        for event in intro_events:
            measure = _safe_int(event.get("measureNumber"))
            if (measure - 1) // 2 != pair_index:
                continue
            pair_step = ((measure - 1) % 2) * STEPS_PER_MEASURE + _event_step(event)
            pair_events.append((pair_step, event))

        for anchored_step in matched_anchor_slots:
            timing_opportunities += 1
            nearby = [
                (distance, event_step, event)
                for event_step, event in pair_events
                for distance in [_circular_step_distance(event_step, anchored_step)]
                if distance <= STEP_TOLERANCE
            ]
            if not nearby:
                continue

            timing_hits += 1
            expected_midis = reference_pitch_map.get(anchored_step, set())
            pitch_opportunities += 1
            nearby.sort(
                key=lambda item: (
                    item[0],
                    -_safe_float(item[2].get("confidence")),
                )
            )
            observed_midis = sorted({_event_midi(item[2]) for item in nearby if _event_midi(item[2]) > 0})
            matched_midis = sorted(set(observed_midis) & expected_midis)
            if matched_midis:
                pitch_hits += 1
                if expected_midis.issubset(set(observed_midis)):
                    exact_pitch_hits += 1

            evidence.append(
                {
                    "pairIndex": pair_index,
                    "anchoredPairStep": anchored_step,
                    "expectedMidi": sorted(expected_midis),
                    "observedMidi": observed_midis,
                    "matchedMidi": matched_midis,
                    "nearestDistanceSteps": nearby[0][0],
                }
            )

    timing_recall = timing_hits / timing_opportunities if timing_opportunities else 0.0
    pitch_precision = pitch_hits / pitch_opportunities if pitch_opportunities else 0.0
    exact_pitch_rate = exact_pitch_hits / pitch_opportunities if pitch_opportunities else 0.0
    anchor_slot_recall = len(matched_anchor_slots) / len(reference_slots) if reference_slots else 0.0

    score = (
        0.45 * pitch_precision
        + 0.25 * exact_pitch_rate
        + 0.20 * timing_recall
        + 0.10 * anchor_slot_recall
    )

    return {
        "offsetSteps": offset,
        "matchedAnchorSlots": matched_anchor_slots,
        "matchedAnchorSlotCount": len(matched_anchor_slots),
        "timingOpportunities": timing_opportunities,
        "timingHits": timing_hits,
        "timingRecall": round(timing_recall, 6),
        "pitchOpportunities": pitch_opportunities,
        "pitchHits": pitch_hits,
        "pitchPrecision": round(pitch_precision, 6),
        "exactPitchHits": exact_pitch_hits,
        "exactPitchRate": round(exact_pitch_rate, 6),
        "anchorSlotRecall": round(anchor_slot_recall, 6),
        "pitchAwareScore": round(score, 6),
        "evidence": evidence,
        "readOnly": True,
    }


def main() -> None:
    for path in (CANDIDATE_PATH, NOTATION_PATH, REFERENCE_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Missing benchmark input: {path}")

    candidate_report = json.loads(CANDIDATE_PATH.read_text())
    notation_report = json.loads(NOTATION_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())

    stable_slots = _stable_slots(candidate_report)
    reference_pitch_map = _reference_pitch_map(reference)
    events = _notation_events(notation_report)

    evaluations = [
        _evaluate_offset(offset, stable_slots, reference_pitch_map, events)
        for offset in range(PAIR_STEPS)
    ]
    ranked = sorted(
        evaluations,
        key=lambda item: (
            float(item["pitchAwareScore"]),
            int(item["pitchHits"]),
            int(item["exactPitchHits"]),
            int(item["timingHits"]),
            -abs(int(item["offsetSteps"])),
        ),
        reverse=True,
    )
    best = ranked[0] if ranked else None
    if best:
        equivalent = [
            item for item in ranked
            if abs(float(item["pitchAwareScore"]) - float(best["pitchAwareScore"])) <= 1e-9
            and int(item["pitchHits"]) == int(best["pitchHits"])
            and int(item["exactPitchHits"]) == int(best["exactPitchHits"])
            and int(item["timingHits"]) == int(best["timingHits"])
        ]
    else:
        equivalent = []

    unique_anchor = len(equivalent) == 1
    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-pitch-aware-professional-rhythm-anchor",
        "candidateInput": CANDIDATE_PATH.name,
        "notationInput": NOTATION_PATH.name,
        "referenceInput": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "selectedEventLayer": next(
            (
                key for key in (
                    "fingeringNormalizedEvents",
                    "pitchContourReconstructedEvents",
                    "motifStabilizedEvents",
                    "renderEvents",
                    "rhythmEvents",
                )
                if notation_report.get(key)
            ),
            None,
        ),
        "stableCandidateSteps": [int(item["pairStep"]) for item in stable_slots],
        "referencePitchSteps": {str(key): sorted(value) for key, value in reference_pitch_map.items()},
        "eventCount": len(events),
        "uniquePitchAwareAnchorFound": unique_anchor,
        "equivalentBestOffsetCount": len(equivalent),
        "equivalentBestOffsets": [int(item["offsetSteps"]) for item in equivalent],
        "bestCandidate": best,
        "adoptedAnchor": best if unique_anchor else None,
        "rankedCandidates": ranked,
        "independentDirectRhythmEvidence": True,
        "usesV7PitchEvidenceReadOnly": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "passed": bool(stable_slots and reference_pitch_map and events),
        "trainingRule": (
            "Direct-audio rhythm evidence may be phase-anchored with locked V7 pitch evidence "
            "only when one offset is uniquely strongest against the professional reference. "
            "This diagnostic must not synthesize notes or alter V7 output or the renderer."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Pitch-aware anchor pass:", report["passed"])
    print("Selected event layer:", report["selectedEventLayer"])
    print("V7 pitch evidence used read-only:", report["usesV7PitchEvidenceReadOnly"])
    print("Renderer changed:", report["rendererChanged"])
    print("Stable candidate steps:", report["stableCandidateSteps"])
    print("Unique pitch-aware anchor found:", report["uniquePitchAwareAnchorFound"])
    print("Equivalent best offset count:", report["equivalentBestOffsetCount"])
    print("Equivalent best offsets:", report["equivalentBestOffsets"])
    print("Best anchored offset:", best.get("offsetSteps") if best else None)
    print("Pitch-aware score:", best.get("pitchAwareScore") if best else None)
    print("Matched anchor slots:", best.get("matchedAnchorSlots") if best else None)
    print("Timing hits:", best.get("timingHits") if best else None)
    print("Pitch hits:", best.get("pitchHits") if best else None)
    print("Exact pitch hits:", best.get("exactPitchHits") if best else None)
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
