from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol

from v143_modal_rhythm_router import RhythmStemBundle
from v143_rhythm_bend_evidence import PitchEnergyView, build_pitch_energy_view
from v143_rhythm_event_assembly import RhythmEventAssemblyResult


MIN_PAIR_SECONDS = 0.045
MAX_PAIR_SECONDS = 0.50
MAX_FRET_DISTANCE = 7
LEGATO_TYPES = ("hammer-on", "pull-off", "slide-up", "slide-down")


def _finite(value: Any, fallback: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return result if math.isfinite(result) else float(fallback)


def _event_time(event: dict[str, Any]) -> float:
    return _finite(event.get("timeSeconds"), 0.0)


def _event_int(event: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = event.get(key)
        if value is None:
            continue
        try:
            return int(round(float(value)))
        except (TypeError, ValueError):
            continue
    return None


class LegatoView(Protocol):
    source_name: str
    times: Any

    def energy(self, midi: int) -> Any: ...

    def onset_strength(self, time_seconds: float, radius: float = 0.045) -> float: ...


@dataclass
class AudioLegatoView:
    pitch_view: PitchEnergyView
    onset_times: Any
    onset_envelope: Any

    @property
    def source_name(self) -> str:
        return self.pitch_view.source_name

    @property
    def times(self) -> Any:
        return self.pitch_view.times

    def energy(self, midi: int) -> Any:
        return self.pitch_view.energy(midi)

    def onset_strength(self, time_seconds: float, radius: float = 0.045) -> float:
        import numpy as np

        centre = float(time_seconds)
        indices = np.where(
            (self.onset_times >= centre - radius)
            & (self.onset_times <= centre + radius)
        )[0]
        if len(indices) == 0:
            return 0.0
        return float(np.max(self.onset_envelope[indices]))


def build_legato_view(audio_path: str | Path) -> AudioLegatoView:
    """Build reference-free pitch-path and re-attack evidence from one carrier."""
    import librosa
    import numpy as np

    path = Path(audio_path)
    if not path.exists() or path.stat().st_size <= 0:
        raise FileNotFoundError(path)

    pitch_view = build_pitch_energy_view(path)
    audio, sample_rate = librosa.load(str(path), sr=22050, mono=True)
    hop_length = 256
    onset_envelope = librosa.onset.onset_strength(
        y=audio,
        sr=sample_rate,
        hop_length=hop_length,
    )
    onset_envelope = np.asarray(onset_envelope, dtype=float)
    scale = float(np.percentile(onset_envelope, 95)) if len(onset_envelope) else 0.0
    if scale > 1e-9:
        onset_envelope = onset_envelope / scale
    onset_times = librosa.times_like(
        onset_envelope,
        sr=sample_rate,
        hop_length=hop_length,
    )
    return AudioLegatoView(
        pitch_view=pitch_view,
        onset_times=onset_times,
        onset_envelope=onset_envelope,
    )


def _transition_path_strength(
    view: LegatoView,
    *,
    source_midi: int,
    target_midi: int,
    start_time: float,
    end_time: float,
    scale: float,
) -> float:
    import numpy as np

    interval = abs(int(target_midi) - int(source_midi))
    if interval <= 1:
        return 0.0

    direction = 1 if target_midi > source_midi else -1
    intermediate = [
        source_midi + direction * offset
        for offset in range(1, interval)
    ]
    times = view.times
    indices = np.where(
        (times >= start_time + 0.025)
        & (times <= end_time - 0.010)
    )[0]
    if len(indices) == 0:
        return 0.0

    strengths: list[float] = []
    for midi in intermediate:
        energy = view.energy(midi)[indices] / max(scale, 1e-9)
        strengths.append(float(np.max(energy)) if len(energy) else 0.0)
    if not strengths:
        return 0.0
    return float(sum(strengths) / len(strengths))


def evaluate_pair_legato(
    view: LegatoView,
    *,
    source_time: float,
    target_time: float,
    source_midi: int,
    target_midi: int,
    source_fret: int,
    target_fret: int,
) -> dict[str, Any] | None:
    """Classify one same-string V143 note pair from carrier audio evidence only."""
    import numpy as np

    delta_time = float(target_time - source_time)
    fret_delta = int(target_fret - source_fret)
    interval = abs(int(target_midi) - int(source_midi))
    if not MIN_PAIR_SECONDS <= delta_time <= MAX_PAIR_SECONDS:
        return None
    if fret_delta == 0 or abs(fret_delta) > MAX_FRET_DISTANCE:
        return None
    if interval == 0 or interval > MAX_FRET_DISTANCE:
        return None

    times = view.times
    indices = np.where(
        (times >= source_time - 0.035)
        & (times <= target_time + 0.115)
    )[0]
    if len(indices) < 5:
        return None

    source_energy = view.energy(source_midi)[indices]
    target_energy = view.energy(target_midi)[indices]
    scale = float(np.percentile(source_energy + target_energy, 95))
    if scale <= 1e-9:
        return None
    source_energy = source_energy / scale
    target_energy = target_energy / scale
    local_times = times[indices]

    before_target = np.where(
        (local_times >= max(source_time, target_time - 0.11))
        & (local_times <= target_time - 0.015)
    )[0]
    after_target = np.where(
        (local_times >= target_time - 0.010)
        & (local_times <= target_time + 0.090)
    )[0]
    source_window = np.where(
        (local_times >= source_time - 0.020)
        & (local_times <= source_time + 0.090)
    )[0]
    if len(after_target) == 0 or len(source_window) == 0:
        return None

    target_before = (
        float(np.max(target_energy[before_target]))
        if len(before_target)
        else float(target_energy[0])
    )
    target_after = float(np.max(target_energy[after_target]))
    target_gain = target_after - target_before
    source_strength = float(np.max(source_energy[source_window]))

    source_attack = max(0.001, view.onset_strength(source_time))
    target_attack = max(0.0, view.onset_strength(target_time))
    attack_ratio = target_attack / source_attack

    path_strength = _transition_path_strength(
        view,
        source_midi=source_midi,
        target_midi=target_midi,
        start_time=source_time,
        end_time=target_time,
        scale=scale,
    )

    technique: str | None = None
    # Slides require audible energy along the semitone path and no dominant new pick.
    if (
        interval >= 2
        and path_strength >= 0.050
        and target_gain >= 0.030
        and attack_ratio <= 0.95
    ):
        technique = "slide-up" if fret_delta > 0 else "slide-down"
    # Hammer-ons/pull-offs require the target pitch to appear without a strong re-attack.
    elif (
        target_gain >= 0.040
        and source_strength >= 0.050
        and attack_ratio <= 0.72
    ):
        technique = "hammer-on" if fret_delta > 0 else "pull-off"

    if technique is None:
        return None

    score = (
        target_gain
        + 0.22 * source_strength
        + (0.24 * path_strength if technique.startswith("slide") else 0.0)
        + max(0.0, 0.72 - min(attack_ratio, 0.72)) * 0.12
    )
    return {
        "type": technique,
        "sourceMidi": int(source_midi),
        "targetMidi": int(target_midi),
        "sourceFret": int(source_fret),
        "targetFret": int(target_fret),
        "sourceTime": round(float(source_time), 4),
        "targetTime": round(float(target_time), 4),
        "deltaTime": round(delta_time, 4),
        "targetGain": round(float(target_gain), 5),
        "sourceStrength": round(float(source_strength), 5),
        "attackRatio": round(float(attack_ratio), 5),
        "pathStrength": round(float(path_strength), 5),
        "score": round(float(score), 6),
        "source": view.source_name,
    }


def _agreeing_technique(
    detections: Iterable[dict[str, Any] | None],
    *,
    required_views: int,
) -> dict[str, Any] | None:
    present = [item for item in detections if isinstance(item, dict)]
    if not present:
        return None
    by_type: dict[str, list[dict[str, Any]]] = {}
    for item in present:
        by_type.setdefault(str(item.get("type") or ""), []).append(item)
    agreed = [
        (technique, items)
        for technique, items in by_type.items()
        if technique in LEGATO_TYPES and len(items) >= required_views
    ]
    if not agreed:
        return None
    technique, items = max(
        agreed,
        key=lambda pair: (
            sum(float(item.get("score") or 0.0) for item in pair[1]) / len(pair[1]),
            pair[0],
        ),
    )
    return {
        "type": technique,
        "score": round(
            sum(float(item.get("score") or 0.0) for item in items) / len(items),
            6,
        ),
        "viewAgreement": len(items),
        "requiredViewAgreement": required_views,
        "consensusPassed": True,
        "views": [deepcopy(item) for item in items],
    }


def enrich_rhythm_assembly_with_legato(
    assembly: RhythmEventAssemblyResult,
    *,
    carrier_stem_paths: Iterable[str | Path],
    view_builder: Callable[[str | Path], LegatoView] = build_legato_view,
) -> RhythmEventAssemblyResult:
    """Append strict two-view slide/hammer/pull evidence after frozen V143 assembly."""
    if not isinstance(assembly, RhythmEventAssemblyResult):
        raise TypeError("assembly must be RhythmEventAssemblyResult")

    paths: list[Path] = []
    for raw_path in carrier_stem_paths:
        path = Path(raw_path)
        if path not in paths:
            paths.append(path)
    if not paths:
        return assembly

    views = [view_builder(path) for path in paths[:2]]
    required_views = min(2, len(views))
    events = [deepcopy(event) for event in assembly.events]
    ordered_indices = sorted(
        range(len(events)),
        key=lambda index: (
            _event_time(events[index]),
            _event_int(events[index], "stringIndex") or 0,
            _event_int(events[index], "fret") or 0,
        ),
    )

    next_by_string: dict[int, int] = {}
    # Walk backwards so each event is compared only with the next selected event
    # on the same mapped string. This avoids inventing long-range legato links.
    for index in reversed(ordered_indices):
        event = events[index]
        string_index = _event_int(event, "stringIndex")
        if string_index is None:
            continue
        target_index = next_by_string.get(string_index)
        next_by_string[string_index] = index
        if target_index is None:
            continue

        target = events[target_index]
        source_time = _event_time(event)
        target_time = _event_time(target)
        source_fret = _event_int(event, "fret")
        target_fret = _event_int(target, "fret")
        source_midi = _event_int(event, "midi", "dominantMidi")
        target_midi = _event_int(target, "midi", "dominantMidi")
        if None in {source_fret, target_fret, source_midi, target_midi}:
            continue
        if event.get("bendSemitones") is not None or target.get("bendSemitones") is not None:
            continue

        detections = [
            evaluate_pair_legato(
                view,
                source_time=source_time,
                target_time=target_time,
                source_midi=int(source_midi),
                target_midi=int(target_midi),
                source_fret=int(source_fret),
                target_fret=int(target_fret),
            )
            for view in views
        ]
        consensus = _agreeing_technique(
            detections,
            required_views=required_views,
        )
        if consensus is None:
            continue

        technique = str(consensus["type"])
        event["legatoTargetEventIndex"] = int(target_index)
        event["legatoTargetFret"] = int(target_fret)
        event["legatoTargetMidi"] = int(target_midi)
        event["legatoEvidence"] = {
            "version": 1,
            "mode": "reference-free-cross-separated-pitch-path-and-reattack",
            **deepcopy(consensus),
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
        }
        techniques = [
            deepcopy(item)
            for item in event.get("rhythmTechniques", [])
            if isinstance(item, dict)
        ]
        if technique not in {str(item.get("type") or "") for item in techniques}:
            techniques.append({
                "type": technique,
                "source": "reference-free-audio-legato-evidence",
            })
        event["rhythmTechniques"] = techniques
        target["legatoContinuationFromEventIndex"] = int(index)
        target["legatoContinuationType"] = technique

    return RhythmEventAssemblyResult(
        source=assembly.source,
        events=tuple(events),
    )


def enrich_router_assembly_with_legato(
    assembly: RhythmEventAssemblyResult,
    bundle: RhythmStemBundle,
) -> RhythmEventAssemblyResult:
    return enrich_rhythm_assembly_with_legato(
        assembly,
        carrier_stem_paths=(
            bundle.carrier_stem_a_path,
            bundle.carrier_stem_b_path,
        ),
    )


__all__ = [
    "MIN_PAIR_SECONDS",
    "MAX_PAIR_SECONDS",
    "MAX_FRET_DISTANCE",
    "LEGATO_TYPES",
    "AudioLegatoView",
    "build_legato_view",
    "evaluate_pair_legato",
    "enrich_rhythm_assembly_with_legato",
    "enrich_router_assembly_with_legato",
]
