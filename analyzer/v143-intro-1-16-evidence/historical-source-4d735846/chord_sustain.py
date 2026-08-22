from __future__ import annotations

from collections import Counter
from typing import Any


DEFAULT_CHORD_VOCABULARY = [
    {"name": "A", "pitchClasses": [9, 1, 4]},
    {"name": "A(tp2)", "pitchClasses": [9, 11, 4]},
    {"name": "D", "pitchClasses": [2, 6, 9]},
    {"name": "E", "pitchClasses": [4, 8, 11]},
    {"name": "G", "pitchClasses": [7, 11, 2]},
    {"name": "G6", "pitchClasses": [7, 11, 2, 4]},
]


def register_weight(midi: int) -> float:
    """Softly favour rhythm-guitar notes without deleting harmonic evidence."""
    if 45 <= midi <= 76:
        return 1.0
    if 40 <= midi < 45 or 76 < midi <= 84:
        return 0.65
    return 0.30


def prepare_harmonic_events(
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Create read-only harmonic events from normalized production notes."""
    harmonic_events: list[dict[str, Any]] = []

    for event in events:
        midi = int(event.get("midi") or 0)
        if midi <= 0:
            continue

        start = float(event.get("start") or 0.0)
        end = max(start, float(event.get("end") or start))

        harmonic_events.append({
            "start": start,
            "end": end,
            "duration": max(0.0, end - start),
            "midi": midi,
            "amplitude": float(event.get("amplitude") or 0.0),
            "pitchClass": midi % 12,
        })

    return harmonic_events


def build_soft_register_windows(
    events: list[dict[str, Any]],
    window_seconds: float = 0.46,
    hop_seconds: float = 0.08,
) -> list[dict[str, Any]]:
    if not events:
        return []

    first = min(float(event["start"]) for event in events)
    last = max(float(event["end"]) for event in events)
    windows: list[dict[str, Any]] = []
    cursor = first
    index = 0

    while cursor <= last:
        window_end = cursor + window_seconds
        active = [
            event
            for event in events
            if float(event["start"]) < window_end
            and float(event["end"]) > cursor
        ]

        if active:
            support: Counter[int] = Counter()
            weighted_duration: Counter[int] = Counter()
            raw_duration: Counter[int] = Counter()

            for event in active:
                pitch_class = int(event["pitchClass"])
                overlap = max(
                    0.0,
                    min(float(event["end"]), window_end)
                    - max(float(event["start"]), cursor),
                )
                weight = register_weight(int(event["midi"]))
                support[pitch_class] += 1
                raw_duration[pitch_class] += overlap
                weighted_duration[pitch_class] += overlap * weight

            ranked = sorted(
                support,
                key=lambda pitch_class: (
                    weighted_duration[pitch_class],
                    raw_duration[pitch_class],
                    support[pitch_class],
                ),
                reverse=True,
            )

            windows.append({
                "windowIndex": index,
                "start": cursor,
                "end": window_end,
                "eventCount": len(active),
                "uniqueMidiCount": len({int(event["midi"]) for event in active}),
                "midis": sorted({int(event["midi"]) for event in active}),
                "pitchClasses": sorted(support),
                "rankedPitchClasses": ranked,
                "pitchClassSupport": {
                    str(key): value for key, value in support.items()
                },
                "pitchClassWeightedDuration": {
                    str(key): round(value, 4)
                    for key, value in weighted_duration.items()
                },
                "maximumEventDuration": max(
                    float(event.get("duration") or 0.0)
                    for event in active
                ),
            })

        cursor += hop_seconds
        index += 1

    return windows


def expected_progression_name(
    window: dict[str, Any],
    progression: list[str],
    slice_start: float,
    slice_duration: float,
) -> str | None:
    if not progression or slice_duration <= 0:
        return None

    midpoint = (
        float(window.get("start") or 0.0)
        + float(window.get("end") or 0.0)
    ) / 2.0
    ratio = max(
        0.0,
        min(
            0.999999,
            (midpoint - slice_start) / slice_duration,
        ),
    )
    index = min(
        len(progression) - 1,
        int(ratio * len(progression)),
    )
    return progression[index]


def best_chord_match(
    window: dict[str, Any],
    chords: list[dict[str, Any]],
    progression_hint: str | None,
) -> dict[str, Any] | None:
    observed = {
        int(value)
        for value in window.get("pitchClasses") or []
    }
    ranked = [
        int(value)
        for value in window.get("rankedPitchClasses") or []
    ]
    top_six = set(ranked[:6])
    duration_map = {
        int(key): float(value)
        for key, value in (
            window.get("pitchClassWeightedDuration") or {}
        ).items()
    }
    total_duration = sum(duration_map.values()) or 1.0
    candidates: list[dict[str, Any]] = []

    for chord in chords:
        name = str(chord.get("name") or "")
        expected = {
            int(value)
            for value in chord.get("pitchClasses") or []
        }
        intersection = observed & expected
        coverage = len(intersection) / max(1, len(expected))
        top_coverage = len(top_six & expected) / max(1, len(expected))
        weighted_support = (
            sum(duration_map.get(pc, 0.0) for pc in expected)
            / total_duration
        )
        missing = len(expected - observed)
        extra = len(top_six - expected)

        minimum_tones = min(2, len(expected))
        enough_tones = len(intersection) >= minimum_tones
        hinted = bool(
            progression_hint and name == progression_hint
        )
        passed = enough_tones and (
            coverage >= 0.66
            or top_coverage >= 0.66
            or (hinted and weighted_support >= 0.18)
        )

        score = (
            coverage * 72.0
            + top_coverage * 28.0
            + weighted_support * 55.0
            - missing * 10.0
            - extra * 1.5
            + (18.0 if hinted else 0.0)
        )

        candidates.append({
            "name": name,
            "coverage": round(coverage, 4),
            "topCoverage": round(top_coverage, 4),
            "weightedSupport": round(weighted_support, 4),
            "missingPitchClasses": sorted(expected - observed),
            "extraTopPitchClasses": sorted(top_six - expected),
            "progressionHint": progression_hint,
            "hintMatched": hinted,
            "score": round(score, 3),
            "passed": passed,
        })

    candidates.sort(
        key=lambda item: (
            bool(item.get("passed")),
            float(item.get("score") or 0.0),
        ),
        reverse=True,
    )
    return candidates[0] if candidates else None


def collapse_matches(
    matches: list[dict[str, Any]],
    maximum_gap_seconds: float = 0.24,
) -> list[dict[str, Any]]:
    collapsed: list[dict[str, Any]] = []

    for match in matches:
        name = str(match.get("matchedChord") or "")
        if not name:
            continue

        if (
            collapsed
            and collapsed[-1].get("matchedChord") == name
            and float(match.get("start") or 0.0)
            - float(collapsed[-1].get("end") or 0.0)
            <= maximum_gap_seconds
        ):
            collapsed[-1]["end"] = match.get("end")
            collapsed[-1]["duration"] = (
                float(collapsed[-1]["end"])
                - float(collapsed[-1]["start"])
            )
            collapsed[-1]["windowCount"] = int(
                collapsed[-1].get("windowCount") or 1
            ) + 1
        else:
            item = dict(match)
            item["duration"] = (
                float(item.get("end") or 0.0)
                - float(item.get("start") or 0.0)
            )
            item["windowCount"] = 1
            collapsed.append(item)

    return collapsed


def detect_chord_sustain(
    events: list[dict[str, Any]],
    chords: list[dict[str, Any]] | None = None,
    progression: list[str] | None = None,
    slice_start: float | None = None,
    slice_duration: float | None = None,
    minimum_sustain_seconds: float = 0.35,
) -> dict[str, Any]:
    """Run the locked V6 detector without modifying note events."""
    harmonic_events = prepare_harmonic_events(events)
    chord_definitions = chords or DEFAULT_CHORD_VOCABULARY
    progression_names = progression or []

    if harmonic_events:
        resolved_start = (
            float(slice_start)
            if slice_start is not None
            else min(float(event["start"]) for event in harmonic_events)
        )
        resolved_end = max(
            float(event["end"])
            for event in harmonic_events
        )
    else:
        resolved_start = float(slice_start or 0.0)
        resolved_end = resolved_start

    resolved_duration = (
        float(slice_duration)
        if slice_duration is not None
        else max(0.0, resolved_end - resolved_start)
    )

    windows = build_soft_register_windows(harmonic_events)
    chord_windows = [
        window
        for window in windows
        if int(window.get("uniqueMidiCount") or 0) >= 3
        and len(window.get("pitchClasses") or []) >= 2
    ]

    matched_windows: list[dict[str, Any]] = []
    for window in chord_windows:
        hint = expected_progression_name(
            window,
            progression_names,
            resolved_start,
            resolved_duration,
        )
        match = best_chord_match(
            window,
            chord_definitions,
            hint,
        )
        if match and match.get("passed"):
            enriched = dict(window)
            enriched["match"] = match
            enriched["matchedChord"] = match.get("name")
            matched_windows.append(enriched)

    collapsed = collapse_matches(matched_windows)
    vocabulary = sorted({
        str(item.get("matchedChord"))
        for item in collapsed
        if item.get("matchedChord")
    })
    sustained = [
        item
        for item in collapsed
        if float(item.get("duration") or 0.0)
        >= minimum_sustain_seconds
    ]
    attack_counts: Counter[str] = Counter(
        str(item.get("matchedChord") or "")
        for item in collapsed
    )

    return {
        "engineVersion": 6,
        "analysisPath": (
            "raw-basic-pitch-soft-register-"
            "progression-aware-windows"
        ),
        "harmonicWindowCount": len(windows),
        "chordWindowCount": len(chord_windows),
        "matchedChordWindowCount": len(matched_windows),
        "collapsedChordCount": len(collapsed),
        "sustainedChordCount": len(sustained),
        "chordVocabulary": vocabulary,
        "observedProgression": [
            str(item.get("matchedChord"))
            for item in collapsed
        ],
        "repeatedAttackCounts": {
            name: count
            for name, count in attack_counts.items()
            if name and count >= 2
        },
        "chords": collapsed,
        "sustainedChords": sustained,
        "noSyntheticNotes": True,
    }
