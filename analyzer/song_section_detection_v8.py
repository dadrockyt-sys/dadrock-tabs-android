from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import ceil
from statistics import median
from typing import Any


@dataclass(frozen=True)
class MeasureFingerprint:
    measure_number: int
    start: float
    end: float
    pitch_classes: tuple[int, ...]
    note_count: int
    chord_hits: int
    average_pitch: float
    pitch_range: int
    technique_count: int
    muted_count: int

    @property
    def density(self) -> float:
        duration = max(self.end - self.start, 0.001)
        return self.note_count / duration

    @property
    def lead_activity(self) -> float:
        return self.pitch_range + self.technique_count * 4 + self.density


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def _event_end(event: dict[str, Any]) -> float:
    start = _event_start(event)
    return max(start, float(event.get("end") or event.get("end_time") or start))


def _event_pitch(event: dict[str, Any]) -> int:
    return int(event.get("midiPitch") or event.get("pitch") or 0)


def _is_technique_event(event: dict[str, Any]) -> bool:
    technique_keys = (
        "bend",
        "release",
        "slide",
        "hammerOn",
        "pullOff",
        "vibrato",
        "harmonic",
        "tap",
    )
    return any(bool(event.get(key)) for key in technique_keys)


def _is_muted_event(event: dict[str, Any]) -> bool:
    return bool(
        event.get("muted")
        or event.get("palmMuted")
        or event.get("isMuted")
        or str(event.get("articulation") or "").lower() in {"mute", "muted", "palm-mute"}
    )


def build_measure_fingerprints(
    events: list[dict[str, Any]],
    *,
    tempo: float = 120.0,
    beats_per_measure: int = 4,
    chord_ranges: list[dict[str, Any]] | None = None,
) -> list[MeasureFingerprint]:
    safe_tempo = max(float(tempo or 120.0), 1.0)
    seconds_per_measure = beats_per_measure * 60.0 / safe_tempo
    song_end = max((_event_end(event) for event in events), default=0.0)
    measure_count = max(1, int(ceil(song_end / seconds_per_measure)))
    chord_ranges = chord_ranges or []

    fingerprints: list[MeasureFingerprint] = []
    for index in range(measure_count):
        start = index * seconds_per_measure
        end = min(start + seconds_per_measure, song_end)
        if end <= start:
            end = start + min(seconds_per_measure, 0.001)
        measure_events = [
            event
            for event in events
            if _event_start(event) < end and _event_end(event) >= start
        ]
        pitches = [_event_pitch(event) for event in measure_events if _event_pitch(event) > 0]
        pitch_classes = tuple(sorted(set(pitch % 12 for pitch in pitches)))
        chord_hits = sum(
            1
            for chord in chord_ranges
            if float(chord.get("start") or 0.0) < end
            and float(chord.get("end") or 0.0) >= start
        )
        fingerprints.append(
            MeasureFingerprint(
                measure_number=index + 1,
                start=round(start, 6),
                end=round(end, 6),
                pitch_classes=pitch_classes,
                note_count=len(measure_events),
                chord_hits=chord_hits,
                average_pitch=(sum(pitches) / len(pitches)) if pitches else 0.0,
                pitch_range=(max(pitches) - min(pitches)) if len(pitches) > 1 else 0,
                technique_count=sum(1 for event in measure_events if _is_technique_event(event)),
                muted_count=sum(1 for event in measure_events if _is_muted_event(event)),
            )
        )
    return fingerprints


def _signature(measure: MeasureFingerprint) -> tuple[Any, ...]:
    density_bucket = round(measure.density / 2.0)
    pitch_bucket = round(measure.average_pitch / 4.0) if measure.average_pitch else 0
    return (
        measure.pitch_classes,
        density_bucket,
        pitch_bucket,
        min(measure.chord_hits, 4),
        min(measure.technique_count, 4),
    )


def _block_signature(measures: list[MeasureFingerprint], start: int, size: int = 4) -> tuple[Any, ...]:
    return tuple(_signature(measure) for measure in measures[start : start + size])


def _stabilize_boundaries(boundaries: list[int], total: int, minimum_section: int = 4) -> list[int]:
    stable = [0]
    for boundary in boundaries[1:-1]:
        if boundary - stable[-1] >= minimum_section:
            stable.append(boundary)
    if total - stable[-1] < minimum_section and len(stable) > 1:
        stable.pop()
    stable.append(total)
    return stable


def _merge_adjacent_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for section in sections:
        if merged and merged[-1]["label"] == section["label"]:
            merged[-1]["endMeasure"] = section["endMeasure"]
            merged[-1]["confidence"] = round(
                max(float(merged[-1]["confidence"]), float(section["confidence"])),
                2,
            )
        else:
            merged.append(dict(section))
    return merged


def detect_song_sections(
    measures: list[MeasureFingerprint],
) -> list[dict[str, Any]]:
    if not measures:
        return []

    total = len(measures)
    block_size = 4 if total >= 12 else 2
    block_occurrences = Counter(
        _block_signature(measures, start, block_size)
        for start in range(0, max(total - block_size + 1, 1), block_size)
    )

    candidate_boundaries = [0]
    for index in range(1, total):
        previous = measures[index - 1]
        current = measures[index]
        density_change = abs(current.density - previous.density)
        pitch_change = abs(current.average_pitch - previous.average_pitch)
        chord_change = abs(current.chord_hits - previous.chord_hits)
        technique_change = abs(current.technique_count - previous.technique_count)
        if (
            density_change >= 2.5
            or pitch_change >= 7
            or chord_change >= 2
            or technique_change >= 2
        ):
            candidate_boundaries.append(index)
    candidate_boundaries.append(total)

    boundaries = _stabilize_boundaries(candidate_boundaries, total)

    # Keep the opening musical idea together instead of creating a two-measure Intro.
    if len(boundaries) > 2 and boundaries[1] < min(8, total):
        opening_end = next(
            (boundary for boundary in boundaries[1:] if boundary >= min(8, total)),
            boundaries[1],
        )
        boundaries = [0, opening_end, *[b for b in boundaries if b > opening_end]]

    groups: list[dict[str, Any]] = []
    for start, end in zip(boundaries, boundaries[1:]):
        group = measures[start:end]
        average_density = sum(item.density for item in group) / len(group)
        average_lead = sum(item.lead_activity for item in group) / len(group)
        average_chords = sum(item.chord_hits for item in group) / len(group)
        block = _block_signature(measures, start, min(block_size, end - start))
        groups.append(
            {
                "start": start,
                "end": end,
                "measures": group,
                "averageDensity": average_density,
                "averageLead": average_lead,
                "averageChords": average_chords,
                "repeated": block_occurrences.get(block, 0) >= 2,
            }
        )

    lead_values = [float(group["averageLead"]) for group in groups]
    chord_values = [float(group["averageChords"]) for group in groups]
    density_values = [float(group["averageDensity"]) for group in groups]
    lead_median = median(lead_values) if lead_values else 0.0
    chord_median = median(chord_values) if chord_values else 0.0
    density_median = median(density_values) if density_values else 0.0

    # The strongest later melodic section becomes the solo candidate.
    solo_candidate = None
    eligible_solos = [
        (index, group)
        for index, group in enumerate(groups)
        if 0.45 <= float(group["start"]) / max(total, 1) <= 0.9
        and float(group["averageLead"]) >= lead_median * 1.2
    ]
    if eligible_solos:
        solo_candidate = max(eligible_solos, key=lambda item: float(item[1]["averageLead"]))[0]

    raw_sections: list[dict[str, Any]] = []
    verse_number = 0
    for section_index, group_info in enumerate(groups):
        group = group_info["measures"]
        average_density = float(group_info["averageDensity"])
        average_lead = float(group_info["averageLead"])
        average_chords = float(group_info["averageChords"])
        repeated = bool(group_info["repeated"])

        if section_index == 0:
            label = "Intro"
            confidence = 0.84
        elif section_index == len(groups) - 1:
            sustained_finish = group[-1].note_count <= max(2, round(average_density))
            label = "Ending" if sustained_finish or len(group) <= 6 else "Outro"
            confidence = 0.8
        elif solo_candidate == section_index:
            label = "Solo"
            confidence = 0.78
        elif repeated and average_chords >= max(1.0, chord_median) and average_density >= density_median:
            label = "Chorus"
            confidence = 0.76
        elif average_chords >= max(2.0, chord_median * 1.25) and average_density >= density_median:
            label = "Riff"
            confidence = 0.7
        elif len(group) <= 6 and section_index > 1:
            label = "Bridge"
            confidence = 0.64
        else:
            verse_number += 1
            label = f"Verse {verse_number}"
            confidence = 0.66

        raw_sections.append(
            {
                "label": label,
                "startMeasure": group[0].measure_number,
                "endMeasure": group[-1].measure_number,
                "confidence": round(confidence, 2),
            }
        )

    return _merge_adjacent_sections(raw_sections)


def attach_section_metadata(
    measures: list[MeasureFingerprint],
    sections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    section_by_measure: dict[int, dict[str, Any]] = {}
    for section in sections:
        start = int(section["startMeasure"])
        end = int(section["endMeasure"])
        for measure_number in range(start, end + 1):
            section_by_measure[measure_number] = section

    return [
        {
            "measureNumber": measure.measure_number,
            "start": measure.start,
            "end": measure.end,
            "sectionLabel": section_by_measure.get(measure.measure_number, {}).get("label", ""),
            "isSectionStart": measure.measure_number
            == section_by_measure.get(measure.measure_number, {}).get("startMeasure"),
            "noteCount": measure.note_count,
            "chordHits": measure.chord_hits,
            "pitchRange": measure.pitch_range,
            "techniqueCount": measure.technique_count,
        }
        for measure in measures
    ]