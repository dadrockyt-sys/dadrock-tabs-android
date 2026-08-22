from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from v143_candidate_timing_adapter import (
    HISTORICAL_WIDE_RECALL_SWEEPS,
    build_subdivision_grid,
    nearest_timing_slot,
    note_events_from_predict,
    parse_note_event,
)
from v143_reference_free_timing import (
    ReferenceFreeTimingEstimate,
    estimate_reference_free_timing,
)


# Frozen research-carrier constants. These intentionally match the fresh-section
# captures that fed the base-0.27 + correlation-safe sequence + contextual-prune
# validation. Do not replace these with the narrower current production adapter.
WIDE_GRID_TOLERANCE_SECONDS = 0.30
CLUSTER_TOLERANCE_SECONDS = 0.030
ONSET_GROUP_TOLERANCE_SECONDS = 0.030
TARGET_SR = 22_050
HOP_LENGTH = 128
BINS_PER_OCTAVE = 36
CQT_MIDI_MIN = 28
CQT_MIDI_MAX = 112
GUITAR_MIDI_MIN = 40
GUITAR_MIDI_MAX = 88

Predictor = Callable[..., Any]
TimingEstimator = Callable[..., ReferenceFreeTimingEstimate]


@dataclass(frozen=True)
class ContextualPruneCarrier:
    """Reference-free carrier consumed by the frozen contextual-prune runtime."""

    rows: tuple[dict[str, Any], ...]
    grid_rows: tuple[dict[str, Any], ...]
    timing: ReferenceFreeTimingEstimate
    raw_event_count: int
    candidate_cluster_count: int
    sweep_event_counts: dict[str, int]
    stem_event_counts: dict[str, int]
    measure_start: int
    measure_end: int

    @property
    def rows_by_measure(self) -> dict[int, list[dict[str, Any]]]:
        out: dict[int, list[dict[str, Any]]] = {}
        for raw in self.rows:
            row = dict(raw)
            measure = int(row["measure"])
            out.setdefault(measure, []).append(row)
        for values in out.values():
            values.sort(
                key=lambda row: (
                    float(row.get("onsetTime") or 0.0),
                    int(row.get("onsetGroupId") or 0),
                )
            )
        return out

    @property
    def grid(self) -> dict[tuple[int, int], float]:
        out: dict[tuple[int, int], float] = {}
        for row in self.grid_rows:
            key = (int(row["measure"]), int(row["step"]))
            value = float(row["timeSeconds"])
            if key in out and abs(out[key] - value) > 1e-6:
                raise RuntimeError(f"Conflicting carrier grid time for {key}")
            out[key] = value
        return out

    def summary(self) -> dict[str, Any]:
        return {
            "schemaVersion": 1,
            "carrier": "v143-contextual-prune-reference-free",
            "measureStart": self.measure_start,
            "measureEnd": self.measure_end,
            "measureCount": self.measure_end - self.measure_start + 1,
            "rowCount": len(self.rows),
            "gridCount": len(self.grid_rows),
            "rawEventCount": self.raw_event_count,
            "candidateClusterCount": self.candidate_cluster_count,
            "onsetGroupCount": len(self.rows),
            "candidateStemCount": len(self.stem_event_counts),
            "sweepEventCounts": dict(self.sweep_event_counts),
            "stemEventCounts": dict(self.stem_event_counts),
            "tempoBpm": float(self.timing.tempo_bpm),
            "firstBeatInMeasure": int(self.timing.first_beat_in_measure),
            "downbeatIndexMod4": int(self.timing.downbeat_index_mod4),
            "beatConfidence": float(self.timing.beat_confidence),
            "barConfidence": float(self.timing.bar_confidence),
            "sweeps": [
                {
                    "name": str(name),
                    "onsetThreshold": float(onset),
                    "frameThreshold": float(frame),
                }
                for name, onset, frame in HISTORICAL_WIDE_RECALL_SWEEPS
            ],
            "wideGridToleranceSeconds": WIDE_GRID_TOLERANCE_SECONDS,
            "clusterToleranceSeconds": CLUSTER_TOLERANCE_SECONDS,
            "onsetGroupToleranceSeconds": ONSET_GROUP_TOLERANCE_SECONDS,
            "targetSampleRate": TARGET_SR,
            "hopLength": HOP_LENGTH,
            "binsPerOctave": BINS_PER_OCTAVE,
            "spectrumMidiMin": CQT_MIDI_MIN,
            "spectrumMidiMax": CQT_MIDI_MAX,
            "guitarMidiMin": GUITAR_MIDI_MIN,
            "guitarMidiMax": GUITAR_MIDI_MAX,
            "referenceFree": True,
            "professionalReferenceUsedByAnalyzer": False,
            "professionalReferenceRequiredAtRuntime": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


def _load_basic_pitch_predictor() -> Predictor:
    try:
        from basic_pitch.inference import predict
    except ImportError as exc:
        raise RuntimeError(
            "basic-pitch is required for contextual-prune shadow carrier capture"
        ) from exc
    return predict


def _resolve_measure_range(
    grid_slots: Sequence[Any],
    measure_start: int,
    measure_end: int | None,
) -> tuple[int, int]:
    start = int(measure_start)
    if start < 1:
        raise ValueError("measure_start must be >= 1")
    available = sorted({int(slot.measure) for slot in grid_slots if int(slot.measure) >= start})
    if not available:
        raise RuntimeError("Reference-free timing grid contains no requested measures")
    end = int(measure_end) if measure_end is not None else int(available[-1])
    if end < start:
        raise ValueError("measure_end must be >= measure_start")
    missing = [measure for measure in range(start, end + 1) if measure not in set(available)]
    if missing:
        raise RuntimeError(f"Timing grid is missing requested measures: {missing[:12]}")
    return start, end


def build_contextual_prune_reference_free_carrier(
    normalized_full_mix_path: str | Path,
    candidate_stem_paths: Sequence[str | Path],
    *,
    measure_start: int = 1,
    measure_end: int | None = None,
    predictor: Predictor | None = None,
    timing_estimator: TimingEstimator = estimate_reference_free_timing,
) -> ContextualPruneCarrier:
    """
    Recreate the label-blind four-sweep + whole-onset-CQT carrier used in validation.

    This function deliberately performs no professional-reference reads, grading,
    note naming, tab rendering, or live-route mutation. It only builds analyzer
    evidence and a 16-step timing grid for the frozen contextual-prune selector.
    """
    try:
        import librosa
        import numpy as np
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "librosa, numpy, and soundfile are required for contextual-prune carrier capture"
        ) from exc

    full_mix = Path(normalized_full_mix_path)
    stem_paths = tuple(Path(path) for path in candidate_stem_paths)
    if not full_mix.exists() or full_mix.stat().st_size <= 0:
        raise RuntimeError(f"Normalized full mix missing or empty: {full_mix}")
    if len(stem_paths) != 2:
        raise RuntimeError(
            f"Validated contextual-prune carrier requires exactly two guitar views, got {len(stem_paths)}"
        )
    for path in stem_paths:
        if not path.exists() or path.stat().st_size <= 0:
            raise RuntimeError(f"Contextual-prune candidate stem missing or empty: {path}")

    timing = timing_estimator(full_mix)
    if not isinstance(timing, ReferenceFreeTimingEstimate):
        raise TypeError("timing_estimator must return ReferenceFreeTimingEstimate")
    grid_slots = build_subdivision_grid(**timing.candidate_adapter_kwargs())
    first_measure, last_measure = _resolve_measure_range(
        grid_slots,
        measure_start,
        measure_end,
    )

    predict_fn = predictor or _load_basic_pitch_predictor()
    raw_events: list[dict[str, Any]] = []
    sweep_counts: Counter[str] = Counter()
    stem_counts: Counter[str] = Counter()
    event_id = 0

    # Exact research behavior: run all four historical wide-recall sweeps on
    # both deterministic guitar views, then collapse duplicates downstream.
    for stem_index, stem in enumerate(stem_paths):
        stem_name = f"stem{stem_index}:{stem.name}"
        for sweep_name, onset_threshold, frame_threshold in HISTORICAL_WIDE_RECALL_SWEEPS:
            detected = note_events_from_predict(
                stem,
                predictor=predict_fn,
                onset_threshold=float(onset_threshold),
                frame_threshold=float(frame_threshold),
            )
            for raw_index, raw in enumerate(detected):
                parsed = parse_note_event(raw)
                if parsed is None:
                    continue
                onset, offset, midi, amplitude = parsed
                midi = int(midi)
                if midi < GUITAR_MIDI_MIN or midi > GUITAR_MIDI_MAX:
                    continue
                nearest = nearest_timing_slot(
                    onset,
                    grid_slots,
                    max_grid_error_seconds=WIDE_GRID_TOLERANCE_SECONDS,
                )
                if nearest is None:
                    continue
                slot, error = nearest
                measure = int(slot.measure)
                if not first_measure <= measure <= last_measure:
                    continue
                event_id += 1
                sweep_counts[str(sweep_name)] += 1
                stem_counts[stem_name] += 1
                raw_events.append(
                    {
                        "eventId": event_id,
                        "stemIndex": int(stem_index),
                        "stemName": stem_name,
                        "sweepName": str(sweep_name),
                        "onsetThreshold": float(onset_threshold),
                        "frameThreshold": float(frame_threshold),
                        "rawIndex": int(raw_index),
                        "midi": midi,
                        "amplitude": float(amplitude),
                        "onsetTime": float(onset),
                        "offsetTime": float(offset),
                        "duration": float(max(0.0, offset - onset)),
                        "nearestMeasure": measure,
                        "nearestStep": int(slot.step),
                        "nearestGlobalStep": int(slot.global_step),
                        "nearestGridTime": float(slot.time_seconds),
                        "signedGridResidualSeconds": float(onset - slot.time_seconds),
                        "absoluteGridResidualSeconds": float(error),
                    }
                )

    by_pitch: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for event in raw_events:
        key = (int(event["nearestMeasure"]), int(event["midi"]))
        by_pitch.setdefault(key, []).append(event)

    candidate_clusters: list[dict[str, Any]] = []
    cluster_id = 0
    for (measure, midi), events in sorted(by_pitch.items()):
        events = sorted(
            events,
            key=lambda row: (float(row["onsetTime"]), int(row["eventId"])),
        )
        current: list[dict[str, Any]] = []
        anchor: float | None = None

        def flush_cluster() -> None:
            nonlocal current, anchor, cluster_id
            if not current:
                return
            weights = [max(float(row.get("amplitude") or 0.0), 1e-4) for row in current]
            weight_sum = float(sum(weights))
            onset_time = sum(
                float(row["onsetTime"]) * weight
                for row, weight in zip(current, weights)
            ) / weight_sum
            offset_time = max(float(row["offsetTime"]) for row in current)
            cluster_id += 1
            candidate_clusters.append(
                {
                    "clusterId": cluster_id,
                    "measure": int(measure),
                    "midi": int(midi),
                    "onsetTime": round(float(onset_time), 9),
                    "offsetTime": round(float(offset_time), 9),
                    "duration": round(max(0.0, float(offset_time - onset_time)), 9),
                    "detectionCount": len(current),
                    "stemSupport": len({int(row["stemIndex"]) for row in current}),
                    "sweepSupport": len({str(row["sweepName"]) for row in current}),
                    "maxAmplitude": max(float(row["amplitude"]) for row in current),
                    "meanAmplitude": sum(float(row["amplitude"]) for row in current) / len(current),
                }
            )
            current = []
            anchor = None

        for event in events:
            onset = float(event["onsetTime"])
            if not current:
                current = [event]
                anchor = onset
            elif abs(onset - float(anchor)) <= CLUSTER_TOLERANCE_SECONDS:
                current.append(event)
            else:
                flush_cluster()
                current = [event]
                anchor = onset
        flush_cluster()

    by_measure: dict[int, list[dict[str, Any]]] = {}
    for cluster in candidate_clusters:
        by_measure.setdefault(int(cluster["measure"]), []).append(cluster)

    onset_groups: list[dict[str, Any]] = []
    group_id = 0
    for measure in sorted(by_measure):
        clusters = sorted(
            by_measure[measure],
            key=lambda row: (
                float(row["onsetTime"]),
                int(row["midi"]),
                int(row["clusterId"]),
            ),
        )
        current: list[dict[str, Any]] = []
        anchor: float | None = None

        def flush_group() -> None:
            nonlocal current, anchor, group_id
            if not current:
                return
            weights = [max(1, int(row.get("detectionCount") or 1)) for row in current]
            weight_sum = float(sum(weights))
            onset_time = sum(
                float(row["onsetTime"]) * weight
                for row, weight in zip(current, weights)
            ) / weight_sum
            midis = sorted({int(row["midi"]) for row in current})
            group_id += 1
            onset_groups.append(
                {
                    "onsetGroupId": group_id,
                    "measure": int(measure),
                    "onsetTime": round(float(onset_time), 9),
                    "candidateMidis": midis,
                    "candidateCount": len(midis),
                    "sourceClusterCount": len(current),
                    "stemSupportMax": max(int(row.get("stemSupport") or 0) for row in current),
                    "sweepSupportMax": max(int(row.get("sweepSupport") or 0) for row in current),
                    "detectionCountSum": sum(int(row.get("detectionCount") or 0) for row in current),
                }
            )
            current = []
            anchor = None

        for cluster in clusters:
            onset = float(cluster["onsetTime"])
            if not current:
                current = [cluster]
                anchor = onset
            elif abs(onset - float(anchor)) <= ONSET_GROUP_TOLERANCE_SECONDS:
                current.append(cluster)
            else:
                flush_group()
                current = [cluster]
                anchor = onset
        flush_group()

    if not onset_groups:
        raise RuntimeError("Contextual-prune carrier produced no physical onset groups")

    # Exact whole-onset CQT evidence used by the fresh-section research caches.
    crop_seconds = max(float(group["onsetTime"]) for group in onset_groups) + 0.40
    bins_per_semitone = BINS_PER_OCTAVE // 12
    n_bins = (CQT_MIDI_MAX - CQT_MIDI_MIN + 1) * bins_per_semitone

    def load_view(path: Path) -> tuple[Any, int]:
        audio, sample_rate = sf.read(str(path), always_2d=False)
        values = np.asarray(audio, dtype=np.float32)
        if values.ndim == 2:
            values = np.mean(values, axis=1)
        if values.ndim != 1 or values.size == 0:
            raise RuntimeError(f"Unexpected contextual-prune stem shape for {path}: {values.shape}")
        values = values[: int(round(float(sample_rate) * crop_seconds))]
        if int(sample_rate) != TARGET_SR:
            values = librosa.resample(
                values,
                orig_sr=int(sample_rate),
                target_sr=TARGET_SR,
            )
            sample_rate = TARGET_SR
        return np.asarray(values, dtype=np.float32), int(sample_rate)

    def build_log_cqt(path: Path) -> Any:
        values, sample_rate = load_view(path)
        cqt = librosa.cqt(
            y=values,
            sr=sample_rate,
            hop_length=HOP_LENGTH,
            fmin=float(librosa.midi_to_hz(CQT_MIDI_MIN)),
            n_bins=int(n_bins),
            bins_per_octave=BINS_PER_OCTAVE,
            filter_scale=0.75,
        )
        return np.log(np.abs(cqt).astype(np.float64) + 1e-9)

    views = [build_log_cqt(path) for path in stem_paths]

    def frame_bounds(start: float, end: float, frame_count: int) -> tuple[int, int]:
        lo = int(math.floor(max(0.0, start) * TARGET_SR / HOP_LENGTH))
        hi = int(math.ceil(max(0.0, end) * TARGET_SR / HOP_LENGTH)) + 1
        lo = max(0, min(frame_count - 1, lo))
        hi = max(lo + 1, min(frame_count, hi))
        return lo, hi

    def semitone_vector(log_cqt: Any, start: float, end: float, reducer: str) -> list[float]:
        lo, hi = frame_bounds(start, end, int(log_cqt.shape[1]))
        values: list[float] = []
        for midi in range(CQT_MIDI_MIN, CQT_MIDI_MAX + 1):
            center = int(round((midi - CQT_MIDI_MIN) * bins_per_semitone))
            bin_lo = max(0, center - 1)
            bin_hi = min(int(log_cqt.shape[0]), center + 2)
            block = log_cqt[bin_lo:bin_hi, lo:hi]
            if block.size == 0:
                value = -12.0
            elif reducer == "max":
                value = float(np.max(block))
            else:
                value = float(np.mean(block))
            values.append(value)
        floor = float(np.median(values))
        return [round(float(value - floor), 6) for value in values]

    spectral_rows: list[dict[str, Any]] = []
    for group in onset_groups:
        onset = float(group["onsetTime"])
        windows = {
            "attackMax": (onset - 0.020, onset + 0.045, "max"),
            "earlyMean": (onset + 0.020, onset + 0.095, "mean"),
            "sustainMean": (onset + 0.070, onset + 0.180, "mean"),
        }
        row = dict(group)
        row["viewA"] = {}
        row["viewB"] = {}
        for name, (start, end, reducer) in windows.items():
            row["viewA"][name] = semitone_vector(views[0], start, end, reducer)
            row["viewB"][name] = semitone_vector(views[1], start, end, reducer)
        spectral_rows.append(row)

    section_grid = [
        {
            "globalStep": int(slot.global_step),
            "measure": int(slot.measure),
            "step": int(slot.step),
            "timeSeconds": float(slot.time_seconds),
        }
        for slot in grid_slots
        if first_measure <= int(slot.measure) <= last_measure
    ]
    expected_grid_count = (last_measure - first_measure + 1) * 16
    if len(section_grid) != expected_grid_count:
        raise RuntimeError(
            "Contextual-prune carrier grid incomplete: "
            f"{len(section_grid)} != {expected_grid_count}"
        )

    row_measures = {int(row["measure"]) for row in spectral_rows}
    missing_row_measures = [
        measure
        for measure in range(first_measure, last_measure + 1)
        if measure not in row_measures
    ]
    if missing_row_measures:
        raise RuntimeError(
            "Contextual-prune carrier has no onset rows for measures: "
            f"{missing_row_measures[:12]}"
        )

    return ContextualPruneCarrier(
        rows=tuple(spectral_rows),
        grid_rows=tuple(section_grid),
        timing=timing,
        raw_event_count=len(raw_events),
        candidate_cluster_count=len(candidate_clusters),
        sweep_event_counts=dict(sorted(sweep_counts.items())),
        stem_event_counts=dict(sorted(stem_counts.items())),
        measure_start=first_measure,
        measure_end=last_measure,
    )


__all__ = [
    "WIDE_GRID_TOLERANCE_SECONDS",
    "CLUSTER_TOLERANCE_SECONDS",
    "ONSET_GROUP_TOLERANCE_SECONDS",
    "TARGET_SR",
    "HOP_LENGTH",
    "BINS_PER_OCTAVE",
    "CQT_MIDI_MIN",
    "CQT_MIDI_MAX",
    "GUITAR_MIDI_MIN",
    "GUITAR_MIDI_MAX",
    "ContextualPruneCarrier",
    "build_contextual_prune_reference_free_carrier",
]
