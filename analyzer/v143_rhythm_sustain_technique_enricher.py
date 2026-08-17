from __future__ import annotations

import math
from copy import deepcopy
from typing import Any, Iterable


SUBDIVISIONS_PER_BEAT = 4
SUPPORTED_TECHNIQUES = (
    "bend",
    "bend-release",
    "pre-bend",
    "sustain-tie",
    "let-ring",
    "palm-mute",
    "slide-up",
    "slide-down",
    "hammer-on",
    "pull-off",
    "vibrato",
    "dead-note",
    "muted-strum",
    "natural-harmonic",
    "pinch-harmonic",
    "tap",
    "trill",
)


def _finite_float(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def step_seconds_from_tempo(
    tempo_bpm: float,
    *,
    subdivisions_per_beat: int = SUBDIVISIONS_PER_BEAT,
) -> float:
    tempo = _finite_float(tempo_bpm, "tempo_bpm")
    subdivisions = int(subdivisions_per_beat)
    if tempo <= 0.0:
        raise ValueError("tempo_bpm must be positive")
    if subdivisions <= 0:
        raise ValueError("subdivisions_per_beat must be positive")
    return 60.0 / tempo / float(subdivisions)


def _primary_pitch_hypothesis(event: dict[str, Any]) -> dict[str, Any] | None:
    hypotheses = list(event.get("pitchHypotheses") or [])
    if not hypotheses:
        return None

    midi = event.get("midi", event.get("dominantMidi"))
    if midi is not None:
        matching = [
            hypothesis
            for hypothesis in hypotheses
            if hypothesis.get("midi") is not None
            and int(hypothesis["midi"]) == int(midi)
        ]
        if matching:
            hypotheses = matching

    def quality(hypothesis: dict[str, Any]) -> tuple[float, ...]:
        return (
            float(hypothesis.get("sourceCount", 0)),
            float(hypothesis.get("maxAmplitude", 0.0)),
            -float(hypothesis.get("minGridError", 0.0)),
            float(hypothesis.get("maxDuration", 0.0)),
            -float(hypothesis.get("midi", 0)),
        )

    return max(hypotheses, key=quality)


def raw_duration_seconds(event: dict[str, Any]) -> tuple[float, str]:
    """Return reference-free note duration evidence without changing attack timing."""
    hypothesis = _primary_pitch_hypothesis(event)
    if hypothesis is None:
        raise ValueError("Mapped rhythm event has no pitchHypotheses duration evidence")

    onset = hypothesis.get("bestOnsetTime")
    offset = hypothesis.get("bestOffsetTime")
    if onset is not None and offset is not None:
        onset_f = _finite_float(onset, "bestOnsetTime")
        offset_f = _finite_float(offset, "bestOffsetTime")
        if offset_f >= onset_f:
            return float(offset_f - onset_f), "best-onset-offset"

    duration = hypothesis.get("maxDuration")
    if duration is None:
        raise ValueError("Primary pitch hypothesis has no usable duration evidence")
    duration_f = _finite_float(duration, "maxDuration")
    if duration_f < 0.0:
        raise ValueError("maxDuration cannot be negative")
    return duration_f, "max-duration"


def quantize_duration_steps(
    duration_seconds: float,
    tempo_bpm: float,
    *,
    subdivisions_per_beat: int = SUBDIVISIONS_PER_BEAT,
) -> tuple[int, float]:
    duration = _finite_float(duration_seconds, "duration_seconds")
    if duration < 0.0:
        raise ValueError("duration_seconds cannot be negative")

    step_seconds = step_seconds_from_tempo(
        tempo_bpm,
        subdivisions_per_beat=subdivisions_per_beat,
    )
    ratio = duration / step_seconds
    # Deterministic half-up rounding; at least one rendered grid step per attack.
    steps = max(1, int(math.floor(ratio + 0.5)))
    return steps, step_seconds


def sustain_tier(duration_steps: int) -> str:
    steps = int(duration_steps)
    if steps <= 0:
        raise ValueError("duration_steps must be positive")
    if steps == 1:
        return "short"
    if steps <= 2:
        return "medium"
    return "long"


def explicit_technique_evidence(event: dict[str, Any]) -> list[dict[str, str]]:
    """Collect only explicit upstream technique evidence; never infer from duration."""
    evidence: dict[str, str] = {}

    def add(value: Any, source: str) -> None:
        if value is None:
            return
        technique = str(value).strip().lower()
        if technique in SUPPORTED_TECHNIQUES:
            evidence.setdefault(technique, source)

    add(event.get("technique"), "upstream-technique")
    for value in event.get("techniques") or []:
        add(value, "upstream-techniques")

    bend = event.get("bendSemitones")
    if bend is not None and _finite_float(bend, "bendSemitones") >= 0.35:
        evidence.setdefault("bend", "bend-semitones")

    boolean_fields = {
        "palmMuted": "palm-mute",
        "palmMute": "palm-mute",
        "hammerOn": "hammer-on",
        "pullOff": "pull-off",
        "vibrato": "vibrato",
        "deadNote": "dead-note",
        "mutedStrum": "muted-strum",
        "naturalHarmonic": "natural-harmonic",
        "pinchHarmonic": "pinch-harmonic",
        "tap": "tap",
        "trill": "trill",
        "letRing": "let-ring",
        "sustainTie": "sustain-tie",
    }
    for field, technique in boolean_fields.items():
        if event.get(field) is True:
            evidence.setdefault(technique, f"explicit-{field}")

    slide_direction = str(event.get("slideDirection") or "").strip().lower()
    if slide_direction == "up":
        evidence.setdefault("slide-up", "explicit-slideDirection")
    elif slide_direction == "down":
        evidence.setdefault("slide-down", "explicit-slideDirection")

    return [
        {"type": technique, "source": evidence[technique]}
        for technique in sorted(evidence)
    ]


def enrich_mapped_rhythm_events(
    mapped_events: Iterable[dict[str, Any]],
    *,
    tempo_bpm: float,
    subdivisions_per_beat: int = SUBDIVISIONS_PER_BEAT,
) -> list[dict[str, Any]]:
    """
    Add duration/sustain metadata and explicit technique evidence downstream.

    Frozen V143 selection, score/rank fields, attack timing, pitch hypotheses, and
    string/fret mapping are copied unchanged. Long duration alone never creates a
    technique label such as let-ring or sustain-tie.
    """
    tempo = _finite_float(tempo_bpm, "tempo_bpm")
    out: list[dict[str, Any]] = []

    for raw_event in mapped_events:
        event = deepcopy(raw_event)
        duration, source = raw_duration_seconds(event)
        steps, step_seconds = quantize_duration_steps(
            duration,
            tempo,
            subdivisions_per_beat=subdivisions_per_beat,
        )

        event["rhythmSustain"] = {
            "version": 1,
            "durationSeconds": float(duration),
            "durationSteps": int(steps),
            "stepSeconds": float(step_seconds),
            "tier": sustain_tier(steps),
            "source": source,
            "attackTimingChanged": False,
        }
        event["rhythmTechniques"] = explicit_technique_evidence(event)
        event["techniqueEnrichment"] = {
            "version": 1,
            "mode": "explicit-evidence-only",
            "durationCreatesTechniqueLabels": False,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
        }
        out.append(event)

    return out


__all__ = [
    "SUBDIVISIONS_PER_BEAT",
    "SUPPORTED_TECHNIQUES",
    "step_seconds_from_tempo",
    "raw_duration_seconds",
    "quantize_duration_steps",
    "sustain_tier",
    "explicit_technique_evidence",
    "enrich_mapped_rhythm_events",
]
