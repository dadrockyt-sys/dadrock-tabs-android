from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Protocol, Sequence


MIN_LEGATO_PAIR_SECONDS = 0.045
MAX_LEGATO_PAIR_SECONDS = 0.45
MAX_LEGATO_FRET_DISTANCE = 7
MIN_SUSTAIN_SECONDS = 0.16
MAX_MUTE_SECONDS = 0.20
REQUIRED_VIEW_AGREEMENT = 2
SUPPORTED_TECHNIQUES = (
    "slide-up",
    "slide-down",
    "hammer-on",
    "pull-off",
    "mute",
    "sustain",
)
INITIAL_FAMILY_ALIASES = {
    "slide-up": "slide",
    "slide-down": "slide",
    "hammer-on": "hammer_on",
    "pull-off": "pull_off",
    "mute": "mute",
    "sustain": "sustain",
}


def _finite(value: Any, fallback: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return result if math.isfinite(result) else float(fallback)


def _integer(event: dict[str, Any], key: str) -> int | None:
    try:
        value = int(round(float(event.get(key))))
    except (TypeError, ValueError):
        return None
    return value


def _band_energy(cqt: Any, midi_bins: Any, centre: float, half_width: float = 0.42) -> Any:
    import numpy as np

    indices = np.where(
        (midi_bins >= centre - half_width)
        & (midi_bins <= centre + half_width)
    )[0]
    if len(indices) == 0:
        return np.zeros(cqt.shape[1], dtype=float)
    return np.sum(cqt[indices, :], axis=0)


def _smooth(values: Any, width: int = 5) -> Any:
    import numpy as np

    if width <= 1:
        return values
    kernel = np.ones(width, dtype=float) / float(width)
    return np.convolve(values, kernel, mode="same")


class TechniqueView(Protocol):
    source_name: str
    times: Any

    def pitch_energy(self, midi: int) -> Any: ...

    def onset_strength(self, time_seconds: float, radius: float = 0.040) -> float: ...


@dataclass
class AudioBassTechniqueView:
    times: Any
    cqt: Any
    midi_bins: Any
    onset_times: Any
    onset_envelope: Any
    source_name: str

    def __post_init__(self) -> None:
        self._pitch_cache: dict[int, Any] = {}

    def pitch_energy(self, midi: int) -> Any:
        key = int(midi)
        cached = self._pitch_cache.get(key)
        if cached is not None:
            return cached
        # Bass-specific evidence weights the fundamental most heavily while the
        # first octave harmonic provides robustness when the fundamental is weak.
        energy = (
            _band_energy(self.cqt, self.midi_bins, float(key))
            + 0.34 * _band_energy(self.cqt, self.midi_bins, float(key + 12))
        )
        energy = _smooth(energy, 5)
        self._pitch_cache[key] = energy
        return energy

    def onset_strength(self, time_seconds: float, radius: float = 0.040) -> float:
        import numpy as np

        centre = float(time_seconds)
        indices = np.where(
            (self.onset_times >= centre - radius)
            & (self.onset_times <= centre + radius)
        )[0]
        if len(indices) == 0:
            return 0.0
        return float(np.max(self.onset_envelope[indices]))


def build_bass_technique_view(audio_path: str | Path) -> AudioBassTechniqueView:
    """Build a reference-free low-register pitch/onset view from one Bass stem."""
    import librosa
    import numpy as np

    path = Path(audio_path)
    if not path.is_file() or path.stat().st_size <= 0:
        raise FileNotFoundError(path)

    audio, sample_rate = librosa.load(str(path), sr=22050, mono=True)
    harmonic = librosa.effects.harmonic(audio, margin=2.5)
    hop_length = 256
    bins_per_octave = 48
    fmin = librosa.midi_to_hz(24)  # C1; safely below standard four-string Bass E1.
    cqt = np.abs(
        librosa.cqt(
            harmonic,
            sr=sample_rate,
            hop_length=hop_length,
            fmin=fmin,
            n_bins=288,
            bins_per_octave=bins_per_octave,
        )
    )
    midi_bins = librosa.hz_to_midi(
        librosa.cqt_frequencies(
            cqt.shape[0],
            fmin=fmin,
            bins_per_octave=bins_per_octave,
        )
    )
    times = librosa.times_like(cqt[0], sr=sample_rate, hop_length=hop_length)

    onset_envelope = librosa.onset.onset_strength(
        y=audio,
        sr=sample_rate,
        hop_length=hop_length,
        fmin=35.0,
        fmax=1200.0,
    )
    onset_envelope = np.asarray(onset_envelope, dtype=float)
    scale = float(np.percentile(onset_envelope, 95)) if len(onset_envelope) else 0.0
    if scale > 1.0e-9:
        onset_envelope = onset_envelope / scale
    onset_times = librosa.times_like(
        onset_envelope,
        sr=sample_rate,
        hop_length=hop_length,
    )

    return AudioBassTechniqueView(
        times=times,
        cqt=cqt,
        midi_bins=midi_bins,
        onset_times=onset_times,
        onset_envelope=onset_envelope,
        source_name=path.name,
    )


def _local_pitch_metrics(
    view: TechniqueView,
    *,
    midi: int,
    onset: float,
    duration: float,
) -> dict[str, float] | None:
    import numpy as np

    duration = max(0.0, float(duration))
    window_end = onset + min(0.90, max(0.26, duration + 0.12))
    indices = np.where((view.times >= onset - 0.035) & (view.times <= window_end))[0]
    if len(indices) < 6:
        return None

    energy = view.pitch_energy(int(midi))[indices]
    local_times = view.times[indices]
    attack_indices = np.where(
        (local_times >= onset - 0.020) & (local_times <= onset + 0.075)
    )[0]
    if len(attack_indices) == 0:
        return None
    attack_peak = float(np.max(energy[attack_indices]))
    if attack_peak <= 1.0e-10:
        return None

    late_start = onset + max(0.10, min(duration * 0.55, max(0.10, duration - 0.055)))
    late_end = onset + min(0.82, max(0.18, duration + 0.035))
    late_indices = np.where((local_times >= late_start) & (local_times <= late_end))[0]
    late_peak = float(np.max(energy[late_indices])) if len(late_indices) else 0.0

    decay_start = onset + 0.105
    decay_end = onset + 0.205
    decay_indices = np.where(
        (local_times >= decay_start) & (local_times <= decay_end)
    )[0]
    decay_peak = float(np.max(energy[decay_indices])) if len(decay_indices) else 0.0

    return {
        "attackPeak": attack_peak,
        "latePeak": late_peak,
        "lateToAttackRatio": late_peak / attack_peak,
        "decayPeak": decay_peak,
        "decayToAttackRatio": decay_peak / attack_peak,
        "onsetStrength": float(view.onset_strength(onset)),
    }


def evaluate_event_articulation(
    view: TechniqueView,
    event: dict[str, Any],
) -> dict[str, Any] | None:
    """Detect only strong sustain or mute evidence from one Bass view."""
    midi = _integer(event, "midi")
    if midi is None or not 28 <= midi <= 67:
        return None
    onset = _finite(event.get("timeSeconds"), -1.0)
    duration = max(0.0, _finite(event.get("durationSeconds"), 0.0))
    duration_steps = max(1, int(_finite(event.get("durationSteps"), 1.0)))
    if onset < 0.0:
        return None

    metrics = _local_pitch_metrics(
        view,
        midi=midi,
        onset=onset,
        duration=duration,
    )
    if metrics is None:
        return None

    technique: str | None = None
    # Duration gates eligibility only; persistent audio energy in this view is
    # required, so a long Basic Pitch duration alone never creates "sustain".
    if (
        duration >= MIN_SUSTAIN_SECONDS
        and duration_steps >= 2
        and metrics["lateToAttackRatio"] >= 0.22
    ):
        technique = "sustain"
    # Mute requires a clear attack followed by unusually rapid pitch-energy
    # collapse. It is deliberately unavailable when onset evidence is weak.
    elif (
        duration <= MAX_MUTE_SECONDS
        and duration_steps <= 2
        and metrics["onsetStrength"] >= 0.18
        and metrics["decayToAttackRatio"] <= 0.10
    ):
        technique = "mute"

    if technique is None:
        return None
    score = (
        metrics["lateToAttackRatio"]
        if technique == "sustain"
        else max(0.0, 1.0 - metrics["decayToAttackRatio"])
        * min(1.0, metrics["onsetStrength"])
    )
    return {
        "type": technique,
        "source": view.source_name,
        "score": round(float(score), 6),
        "durationSeconds": round(duration, 5),
        "durationSteps": duration_steps,
        "lateToAttackRatio": round(metrics["lateToAttackRatio"], 6),
        "decayToAttackRatio": round(metrics["decayToAttackRatio"], 6),
        "onsetStrength": round(metrics["onsetStrength"], 6),
    }


def _transition_path_strength(
    view: TechniqueView,
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
    intermediate = [source_midi + direction * offset for offset in range(1, interval)]
    indices = np.where(
        (view.times >= start_time + 0.020)
        & (view.times <= end_time - 0.008)
    )[0]
    if len(indices) == 0:
        return 0.0

    strengths: list[float] = []
    for midi in intermediate:
        energy = view.pitch_energy(midi)[indices] / max(scale, 1.0e-9)
        strengths.append(float(np.max(energy)) if len(energy) else 0.0)
    return float(sum(strengths) / len(strengths)) if strengths else 0.0


def evaluate_pair_legato(
    view: TechniqueView,
    source_event: dict[str, Any],
    target_event: dict[str, Any],
) -> dict[str, Any] | None:
    """Classify one same-string Bass transition using pitch path + re-attack evidence."""
    import numpy as np

    source_time = _finite(source_event.get("timeSeconds"), -1.0)
    target_time = _finite(target_event.get("timeSeconds"), -1.0)
    source_midi = _integer(source_event, "midi")
    target_midi = _integer(target_event, "midi")
    source_fret = _integer(source_event, "fret")
    target_fret = _integer(target_event, "fret")
    source_string = _integer(source_event, "stringIndex")
    target_string = _integer(target_event, "stringIndex")
    if None in {
        source_midi,
        target_midi,
        source_fret,
        target_fret,
        source_string,
        target_string,
    }:
        return None
    if source_string != target_string:
        return None

    delta_time = target_time - source_time
    fret_delta = int(target_fret) - int(source_fret)
    interval = abs(int(target_midi) - int(source_midi))
    if not MIN_LEGATO_PAIR_SECONDS <= delta_time <= MAX_LEGATO_PAIR_SECONDS:
        return None
    if fret_delta == 0 or not 1 <= abs(fret_delta) <= MAX_LEGATO_FRET_DISTANCE:
        return None
    if interval == 0 or interval > MAX_LEGATO_FRET_DISTANCE:
        return None

    indices = np.where(
        (view.times >= source_time - 0.030)
        & (view.times <= target_time + 0.095)
    )[0]
    if len(indices) < 5:
        return None

    source_energy = view.pitch_energy(int(source_midi))[indices]
    target_energy = view.pitch_energy(int(target_midi))[indices]
    scale = float(np.percentile(source_energy + target_energy, 95))
    if scale <= 1.0e-9:
        return None
    source_energy = source_energy / scale
    target_energy = target_energy / scale
    local_times = view.times[indices]

    source_window = np.where(
        (local_times >= source_time - 0.015) & (local_times <= source_time + 0.075)
    )[0]
    target_before = np.where(
        (local_times >= max(source_time, target_time - 0.10))
        & (local_times <= target_time - 0.012)
    )[0]
    target_after = np.where(
        (local_times >= target_time - 0.008) & (local_times <= target_time + 0.075)
    )[0]
    if len(source_window) == 0 or len(target_after) == 0:
        return None

    source_strength = float(np.max(source_energy[source_window]))
    target_before_strength = (
        float(np.max(target_energy[target_before])) if len(target_before) else 0.0
    )
    target_after_strength = float(np.max(target_energy[target_after]))
    target_gain = target_after_strength - target_before_strength

    source_attack = max(0.001, float(view.onset_strength(source_time)))
    target_attack = max(0.0, float(view.onset_strength(target_time)))
    attack_ratio = target_attack / source_attack
    path_strength = _transition_path_strength(
        view,
        source_midi=int(source_midi),
        target_midi=int(target_midi),
        start_time=source_time,
        end_time=target_time,
        scale=scale,
    )

    technique: str | None = None
    if (
        interval >= 2
        and path_strength >= 0.065
        and target_gain >= 0.035
        and attack_ratio <= 0.65
    ):
        technique = "slide-up" if fret_delta > 0 else "slide-down"
    elif (
        target_gain >= 0.055
        and source_strength >= 0.080
        and attack_ratio <= 0.48
    ):
        technique = "hammer-on" if fret_delta > 0 else "pull-off"

    if technique is None:
        return None

    score = (
        target_gain
        + 0.20 * source_strength
        + (0.28 * path_strength if technique.startswith("slide") else 0.0)
        + max(0.0, 0.48 - min(attack_ratio, 0.48)) * 0.10
    )
    return {
        "type": technique,
        "source": view.source_name,
        "score": round(float(score), 6),
        "sourceMidi": int(source_midi),
        "targetMidi": int(target_midi),
        "sourceFret": int(source_fret),
        "targetFret": int(target_fret),
        "sourceTime": round(source_time, 5),
        "targetTime": round(target_time, 5),
        "deltaTime": round(delta_time, 5),
        "sourceStrength": round(source_strength, 6),
        "targetGain": round(target_gain, 6),
        "attackRatio": round(attack_ratio, 6),
        "pathStrength": round(path_strength, 6),
    }


def _consensus(
    detections: Iterable[dict[str, Any] | None],
    *,
    required_views: int = REQUIRED_VIEW_AGREEMENT,
) -> dict[str, Any] | None:
    present = [item for item in detections if isinstance(item, dict)]
    by_type: dict[str, list[dict[str, Any]]] = {}
    for item in present:
        technique = str(item.get("type") or "")
        if technique in SUPPORTED_TECHNIQUES:
            by_type.setdefault(technique, []).append(item)

    agreed = [
        (technique, rows)
        for technique, rows in by_type.items()
        if len(rows) >= int(required_views)
    ]
    if not agreed:
        return None

    technique, rows = max(
        agreed,
        key=lambda pair: (
            sum(_finite(row.get("score"), 0.0) for row in pair[1]) / len(pair[1]),
            pair[0],
        ),
    )
    return {
        "type": technique,
        "family": INITIAL_FAMILY_ALIASES[technique],
        "score": round(
            sum(_finite(row.get("score"), 0.0) for row in rows) / len(rows),
            6,
        ),
        "viewAgreement": len(rows),
        "requiredViewAgreement": int(required_views),
        "consensusPassed": True,
        "views": [deepcopy(row) for row in rows],
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
    }


def enrich_bass_events_with_techniques(
    events: Sequence[dict[str, Any]],
    *,
    stem_paths: Sequence[str | Path],
) -> dict[str, Any]:
    """Add conservative two-view Bass technique evidence without moving notes."""
    if len(stem_paths) < REQUIRED_VIEW_AGREEMENT:
        raise ValueError("Bass technique evidence requires direct and cascade stems")

    views = [build_bass_technique_view(path) for path in stem_paths[:2]]
    enriched = [deepcopy(event) for event in events]
    evidence_by_event: dict[int, list[dict[str, Any]]] = {}

    # Event-local sustain/mute evidence.
    for index, event in enumerate(enriched):
        consensus = _consensus(
            [evaluate_event_articulation(view, event) for view in views]
        )
        if consensus is not None:
            evidence_by_event.setdefault(index, []).append(consensus)

    # Same-string transitions: compare each event only with the next authenticated
    # event on its mapped string, preventing invented long-range legato links.
    ordered_indices = sorted(
        range(len(enriched)),
        key=lambda index: (
            _finite(enriched[index].get("timeSeconds"), 0.0),
            _integer(enriched[index], "stringIndex") or 0,
            _integer(enriched[index], "fret") or 0,
        ),
    )
    next_by_string: dict[int, int] = {}
    for index in reversed(ordered_indices):
        event = enriched[index]
        string_index = _integer(event, "stringIndex")
        if string_index is None:
            continue
        target_index = next_by_string.get(string_index)
        next_by_string[string_index] = index
        if target_index is None:
            continue
        target = enriched[target_index]
        consensus = _consensus(
            [evaluate_pair_legato(view, event, target) for view in views]
        )
        if consensus is not None:
            consensus = deepcopy(consensus)
            consensus["targetEventIndex"] = int(target_index)
            evidence_by_event.setdefault(index, []).append(consensus)

    technique_counts = {technique: 0 for technique in SUPPORTED_TECHNIQUES}
    family_counts: dict[str, int] = {}
    technique_event_count = 0

    for index, event in enumerate(enriched):
        evidences = evidence_by_event.get(index, [])
        # At most one articulation and one transition label can exist on an event.
        labels: list[str] = []
        seen: set[str] = set()
        for evidence in evidences:
            technique = str(evidence.get("type") or "")
            if technique in SUPPORTED_TECHNIQUES and technique not in seen:
                labels.append(technique)
                seen.add(technique)
                technique_counts[technique] += 1
                family = INITIAL_FAMILY_ALIASES[technique]
                family_counts[family] = family_counts.get(family, 0) + 1

        event["techniques"] = labels
        event["bassTechniqueEvidence"] = [deepcopy(row) for row in evidences]
        event["bassTechniqueEnrichment"] = {
            "version": 1,
            "mode": "reference-free-two-view-audio-evidence",
            "requiredViewAgreement": REQUIRED_VIEW_AGREEMENT,
            "noteTimingPlayabilityChanged": False,
            "durationAloneCreatesSustain": False,
            "harmonicEvidenceImplemented": False,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
        }
        if labels:
            technique_event_count += 1

    proven_families = sorted(family for family, count in family_counts.items() if count > 0)
    initial_families = ("slide", "hammer_on", "pull_off", "mute", "harmonic", "sustain")
    unproven_families = [family for family in initial_families if family not in proven_families]

    return {
        "events": enriched,
        "diagnostics": {
            "eventCount": len(enriched),
            "techniqueEventCount": technique_event_count,
            "techniqueCounts": technique_counts,
            "techniqueFamilyCounts": family_counts,
            "provenTechniqueFamilies": proven_families,
            "unprovenInitialTechniqueFamilies": unproven_families,
            "allInitialTechniqueFamiliesProven": len(unproven_families) == 0,
            "requiredViewAgreement": REQUIRED_VIEW_AGREEMENT,
            "supportedTechniques": list(SUPPORTED_TECHNIQUES),
            "harmonicEvidenceImplemented": False,
            "futureHighRiskFamiliesEnabled": False,
            "referenceFree": True,
        },
    }


__all__ = [
    "MIN_LEGATO_PAIR_SECONDS",
    "MAX_LEGATO_PAIR_SECONDS",
    "MAX_LEGATO_FRET_DISTANCE",
    "MIN_SUSTAIN_SECONDS",
    "MAX_MUTE_SECONDS",
    "REQUIRED_VIEW_AGREEMENT",
    "SUPPORTED_TECHNIQUES",
    "AudioBassTechniqueView",
    "build_bass_technique_view",
    "evaluate_event_articulation",
    "evaluate_pair_legato",
    "enrich_bass_events_with_techniques",
]
