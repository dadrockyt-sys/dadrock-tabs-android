from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from v143_modal_rhythm_router import RhythmStemBundle
from v143_rhythm_event_assembly import RhythmEventAssemblyResult


BEND_AMOUNTS = (1, 2, 3)
MIN_EVENT_DURATION_SECONDS = 0.16


def _finite(value: Any, fallback: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return result if math.isfinite(result) else float(fallback)


def _event_time(event: dict[str, Any]) -> float:
    return _finite(event.get("timeSeconds"), 0.0)


def _event_duration(event: dict[str, Any]) -> float:
    sustain = event.get("rhythmSustain") or {}
    return max(0.0, _finite(sustain.get("durationSeconds"), 0.0))


def _event_midi(event: dict[str, Any]) -> int | None:
    value = event.get("midi", event.get("dominantMidi"))
    try:
        midi = int(round(float(value)))
    except (TypeError, ValueError):
        return None
    return midi if 24 <= midi <= 96 else None


def _band_energy(cqt: Any, midi_bins: Any, centre: float, half_width: float = 0.45) -> Any:
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


@dataclass
class PitchEnergyView:
    times: Any
    cqt: Any
    midi_bins: Any
    source_name: str

    def __post_init__(self) -> None:
        self._energy_cache: dict[int, Any] = {}

    def energy(self, midi: int) -> Any:
        key = int(midi)
        cached = self._energy_cache.get(key)
        if cached is not None:
            return cached

        # Fundamental + first octave harmonic is deliberately the same robust
        # evidence family proven by the earlier GOMYWAY bend benchmarks, but it
        # is now evaluated from runtime event pitch rather than any song fixture.
        energy = (
            _band_energy(self.cqt, self.midi_bins, float(key))
            + 0.52 * _band_energy(self.cqt, self.midi_bins, float(key + 12))
        )
        energy = _smooth(energy, 5)
        self._energy_cache[key] = energy
        return energy


def build_pitch_energy_view(audio_path: str | Path) -> PitchEnergyView:
    """Build a reference-free harmonic CQT view from one separated guitar stem."""
    import librosa
    import numpy as np

    path = Path(audio_path)
    if not path.exists() or path.stat().st_size <= 0:
        raise FileNotFoundError(path)

    audio, sample_rate = librosa.load(str(path), sr=22050, mono=True)
    harmonic = librosa.effects.harmonic(audio, margin=3.0)
    hop_length = 256
    bins_per_octave = 48
    fmin = librosa.note_to_hz("C2")
    cqt = np.abs(
        librosa.cqt(
            harmonic,
            sr=sample_rate,
            hop_length=hop_length,
            fmin=fmin,
            n_bins=240,
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
    return PitchEnergyView(
        times=times,
        cqt=cqt,
        midi_bins=midi_bins,
        source_name=path.name,
    )


def evaluate_event_bend(
    view: PitchEnergyView,
    *,
    onset: float,
    duration: float,
    source_midi: int,
) -> dict[str, Any] | None:
    """Find a continuous upward bend from one runtime-selected V143 event.

    No artist/song fixture, professional transcription, or runtime label is used.
    The source pitch and attack time come only from the selected V143 event.
    """
    import numpy as np

    if duration < MIN_EVENT_DURATION_SECONDS:
        return None

    times = view.times
    source_energy = view.energy(source_midi)
    window_end = onset + min(1.15, max(0.56, duration + 0.28))
    indices = np.where((times >= onset - 0.10) & (times <= window_end))[0]
    if len(indices) < 8:
        return None

    local_times = times[indices]
    local_source_raw = source_energy[indices]
    best: dict[str, Any] | None = None

    for amount in BEND_AMOUNTS:
        target_energy = view.energy(source_midi + amount)[indices]
        combined = local_source_raw + target_energy
        scale = float(np.percentile(combined, 95))
        if scale <= 1e-9:
            continue

        source = local_source_raw / scale
        target = target_energy / scale

        early_mask = local_times <= onset + min(0.30, max(0.16, duration * 0.45))
        target_mask = (
            (local_times >= onset + 0.035)
            & (local_times <= onset + min(0.72, max(0.32, duration + 0.18)))
        )
        if not np.any(early_mask) or not np.any(target_mask):
            continue

        source_candidates = np.where(early_mask)[0]
        source_index = int(
            source_candidates[
                np.argmax(
                    source[source_candidates]
                    - 0.30 * target[source_candidates]
                )
            ]
        )
        target_candidates = np.where(
            target_mask & (np.arange(len(local_times)) > source_index)
        )[0]
        if len(target_candidates) == 0:
            continue

        target_index = int(
            target_candidates[
                np.argmax(
                    target[target_candidates]
                    - 0.18 * source[target_candidates]
                )
            ]
        )

        rise_duration = float(local_times[target_index] - local_times[source_index])
        source_strength = float(source[source_index])
        target_strength = float(target[target_index])
        target_gain = float(target[target_index] - target[source_index])

        path_support = True
        path_strength = 0.0
        if amount >= 2:
            middle_midi = source_midi + max(1, amount // 2)
            middle = view.energy(middle_midi)[indices] / scale
            between = np.where(
                (np.arange(len(local_times)) > source_index)
                & (np.arange(len(local_times)) < target_index)
            )[0]
            if len(between):
                path_strength = float(np.max(middle[between]))
                path_support = path_strength >= 0.028
            else:
                path_support = False

        release_candidates = np.where(
            (np.arange(len(local_times)) > target_index)
            & (local_times <= window_end)
        )[0]
        release_detected = False
        release_time: float | None = None
        release_drop = 0.0
        source_rebound = 0.0
        if len(release_candidates):
            release_index = int(
                release_candidates[
                    np.argmax(
                        source[release_candidates]
                        - 0.22 * target[release_candidates]
                    )
                ]
            )
            release_drop = float(target[target_index] - target[release_index])
            source_rebound = float(source[release_index] - source[target_index])
            release_detected = bool(
                release_drop >= 0.018
                and source[release_index] >= 0.042
                and source_rebound >= -0.015
            )
            if release_detected:
                release_time = float(local_times[release_index])

        passed = bool(
            source_strength >= 0.060
            and target_strength >= 0.078
            and 0.025 <= rise_duration <= 0.62
            and target_gain >= 0.022
            and path_support
        )
        if not passed:
            continue

        # Favour a clearly reached terminal pitch over an intermediate pitch that
        # naturally appears on the way to a larger bend.
        score = (
            target_strength
            + 1.45 * target_gain
            + 0.035 * float(amount)
            + 0.20 * path_strength
            + (0.035 if release_detected else 0.0)
        )
        candidate = {
            "type": "bend-release" if release_detected else "bend",
            "bendSemitones": int(amount),
            "sourceMidi": int(source_midi),
            "targetMidi": int(source_midi + amount),
            "bendStart": round(float(local_times[source_index]), 4),
            "targetTime": round(float(local_times[target_index]), 4),
            "releaseTime": round(release_time, 4) if release_time is not None else None,
            "release": bool(release_detected),
            "sourceStrength": round(source_strength, 4),
            "targetStrength": round(target_strength, 4),
            "targetGain": round(target_gain, 4),
            "pathStrength": round(path_strength, 4),
            "riseDuration": round(rise_duration, 4),
            "releaseDrop": round(release_drop, 4),
            "sourceRebound": round(source_rebound, 4),
            "score": round(float(score), 6),
            "source": view.source_name,
        }
        if best is None or float(candidate["score"]) > float(best["score"]):
            best = candidate

    return best


def _agreeing_bend(
    detections: Iterable[dict[str, Any] | None],
) -> dict[str, Any] | None:
    present = [item for item in detections if isinstance(item, dict)]
    if not present:
        return None

    by_amount: dict[int, list[dict[str, Any]]] = {}
    for item in present:
        by_amount.setdefault(int(item["bendSemitones"]), []).append(item)

    # Production uses two independently-separated guitar views. Require both to
    # agree when both views are available; a single-view path remains supported
    # for deterministic unit verification and emergency fallback.
    required = 2 if len(present) >= 2 else 1
    agreed = [
        (amount, items)
        for amount, items in by_amount.items()
        if len(items) >= required
    ]
    if not agreed:
        return None

    amount, items = max(
        agreed,
        key=lambda pair: (
            sum(float(item.get("score") or 0.0) for item in pair[1]) / len(pair[1]),
            pair[0],
        ),
    )
    release = sum(1 for item in items if item.get("release")) >= (len(items) + 1) // 2
    return {
        "type": "bend-release" if release else "bend",
        "bendSemitones": int(amount),
        "release": bool(release),
        "sourceMidi": int(items[0]["sourceMidi"]),
        "targetMidi": int(items[0]["targetMidi"]),
        "bendStart": min(float(item["bendStart"]) for item in items),
        "targetTime": sum(float(item["targetTime"]) for item in items) / len(items),
        "releaseTime": (
            sum(float(item["releaseTime"]) for item in items if item.get("releaseTime") is not None)
            / sum(1 for item in items if item.get("releaseTime") is not None)
            if any(item.get("releaseTime") is not None for item in items)
            else None
        ),
        "score": round(
            sum(float(item.get("score") or 0.0) for item in items) / len(items),
            6,
        ),
        "viewAgreement": len(items),
        "views": [deepcopy(item) for item in items],
    }


def enrich_rhythm_assembly_with_audio_bends(
    assembly: RhythmEventAssemblyResult,
    *,
    carrier_stem_paths: Iterable[str | Path],
    view_builder: Callable[[str | Path], PitchEnergyView] = build_pitch_energy_view,
) -> RhythmEventAssemblyResult:
    if not isinstance(assembly, RhythmEventAssemblyResult):
        raise TypeError("assembly must be RhythmEventAssemblyResult")

    unique_paths: list[Path] = []
    for raw_path in carrier_stem_paths:
        path = Path(raw_path)
        if path not in unique_paths:
            unique_paths.append(path)
    if not unique_paths:
        return assembly

    views = [view_builder(path) for path in unique_paths[:2]]
    enriched: list[dict[str, Any]] = []

    for raw_event in assembly.events:
        event = deepcopy(raw_event)
        midi = _event_midi(event)
        duration = _event_duration(event)
        if midi is None or duration < MIN_EVENT_DURATION_SECONDS:
            enriched.append(event)
            continue

        detections = [
            evaluate_event_bend(
                view,
                onset=_event_time(event),
                duration=duration,
                source_midi=midi,
            )
            for view in views
        ]
        bend = _agreeing_bend(detections)
        if bend is None:
            enriched.append(event)
            continue

        amount = int(bend["bendSemitones"])
        fret = int(event.get("fret") or 0)
        event["bendSemitones"] = amount
        event["bendTargetMidi"] = int(bend["targetMidi"])
        event["bendTargetFret"] = fret + amount
        event["bendRelease"] = bool(bend["release"])
        event["bendEvidence"] = {
            "version": 1,
            "mode": "reference-free-cross-separated-harmonic-contour",
            "viewAgreement": int(bend["viewAgreement"]),
            "score": float(bend["score"]),
            "bendStart": float(bend["bendStart"]),
            "targetTime": float(bend["targetTime"]),
            "releaseTime": bend["releaseTime"],
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "views": deepcopy(bend["views"]),
        }

        techniques = [
            deepcopy(item)
            for item in event.get("rhythmTechniques", [])
            if isinstance(item, dict)
        ]
        existing = {str(item.get("type") or "") for item in techniques}
        if "bend" not in existing:
            techniques.append({
                "type": "bend",
                "source": "reference-free-audio-pitch-contour",
            })
        if bend["release"] and "bend-release" not in existing:
            techniques.append({
                "type": "bend-release",
                "source": "reference-free-audio-pitch-contour",
            })
        event["rhythmTechniques"] = techniques
        enriched.append(event)

    return RhythmEventAssemblyResult(
        source=assembly.source,
        events=tuple(enriched),
    )


def enrich_router_assembly_with_bends(
    assembly: RhythmEventAssemblyResult,
    bundle: RhythmStemBundle,
) -> RhythmEventAssemblyResult:
    """Router hook: enrich only after frozen V143 selection and note mapping."""
    return enrich_rhythm_assembly_with_audio_bends(
        assembly,
        carrier_stem_paths=(
            bundle.carrier_stem_a_path,
            bundle.carrier_stem_b_path,
        ),
    )


__all__ = [
    "BEND_AMOUNTS",
    "MIN_EVENT_DURATION_SECONDS",
    "PitchEnergyView",
    "build_pitch_energy_view",
    "evaluate_event_bend",
    "enrich_rhythm_assembly_with_audio_bends",
    "enrich_router_assembly_with_bends",
]
