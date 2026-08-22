from __future__ import annotations

import json
import math
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from v143_modal_live_endpoint import app, rhythm_image


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "fresh-section4-reference-free-cache.json"
)

FIRST_MEASURE = 65
LAST_MEASURE = 80
WIDE_GRID_TOLERANCE_SECONDS = 0.30
CLUSTER_TOLERANCE_SECONDS = 0.030
ONSET_GROUP_TOLERANCE_SECONDS = 0.030

TARGET_SR = 22050
HOP_LENGTH = 128
BINS_PER_OCTAVE = 36
CQT_MIDI_MIN = 28
CQT_MIDI_MAX = 112
GUITAR_MIDI_MIN = 40
GUITAR_MIDI_MAX = 88

stage_image = rhythm_image.add_local_python_source("v143_modal_live_endpoint")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


@app.function(
    image=stage_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def capture_fresh_section4_reference_free(source_audio: bytes, suffix: str = ".m4a") -> dict[str, Any]:
    """Capture raw attacks + whole-onset spectra for measures 65-80.

    This function is intentionally label blind. No professional reference or target
    note data is imported, mounted, or passed to Modal. It uses the same frozen
    V143 deterministic separator and reference-free timing stack used by the intro
    calibration work, but writes a completely separate fresh-section cache.
    """
    import librosa
    import numpy as np
    import soundfile as sf

    import modal_analyzer as legacy
    from v143_candidate_timing_adapter import (
        HISTORICAL_WIDE_RECALL_SWEEPS,
        build_subdivision_grid,
        nearest_timing_slot,
        note_events_from_predict,
        parse_note_event,
    )
    from v143_reference_free_timing import estimate_reference_free_timing
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )

    safe_suffix = str(suffix or ".audio").lower()
    if safe_suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        safe_suffix = ".audio"

    with tempfile.TemporaryDirectory(prefix="v143-fresh-section4-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("Fresh Section 4 source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        timing = estimate_reference_free_timing(normalized)
        grid = build_subdivision_grid(**timing.candidate_adapter_kwargs())
        bundle = build_deterministic_rhythm_stem_bundle(normalized).validate()
        stem_paths = [Path(path) for path in bundle.candidate_stem_paths]
        if len(stem_paths) != 2:
            raise RuntimeError(f"Expected two deterministic guitar views, got {len(stem_paths)}")

        raw_events: list[dict[str, Any]] = []
        sweep_counts: Counter[str] = Counter()
        stem_counts: Counter[str] = Counter()
        event_id = 0

        for stem_index, stem in enumerate(stem_paths):
            stem_name = f"stem{stem_index}:{stem.name}"
            for sweep_name, onset_threshold, frame_threshold in HISTORICAL_WIDE_RECALL_SWEEPS:
                detected = note_events_from_predict(
                    stem,
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
                        grid,
                        max_grid_error_seconds=WIDE_GRID_TOLERANCE_SECONDS,
                    )
                    if nearest is None:
                        continue
                    slot, error = nearest
                    measure = int(slot.measure)
                    if not FIRST_MEASURE <= measure <= LAST_MEASURE:
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

        # First collapse duplicate detections of the same MIDI attack across stems
        # and sweep thresholds. This remains entirely reference free.
        by_pitch: dict[tuple[int, int], list[dict[str, Any]]] = {}
        for event in raw_events:
            key = (int(event["nearestMeasure"]), int(event["midi"]))
            by_pitch.setdefault(key, []).append(event)

        candidate_clusters: list[dict[str, Any]] = []
        cluster_id = 0
        for (measure, midi), events in sorted(by_pitch.items()):
            events = sorted(events, key=lambda row: (float(row["onsetTime"]), int(row["eventId"])))
            current: list[dict[str, Any]] = []
            anchor: float | None = None

            def flush_cluster() -> None:
                nonlocal current, anchor, cluster_id
                if not current:
                    return
                weights = [max(float(row.get("amplitude") or 0.0), 1e-4) for row in current]
                weight_sum = float(sum(weights))
                onset_time = sum(float(row["onsetTime"]) * w for row, w in zip(current, weights)) / weight_sum
                offset_time = max(float(row["offsetTime"]) for row in current)
                cluster_id += 1
                candidate_clusters.append(
                    {
                        "clusterId": cluster_id,
                        "measure": measure,
                        "midi": midi,
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

        # Then collapse pitch hypotheses that occur at the same physical attack.
        by_measure: dict[int, list[dict[str, Any]]] = {}
        for cluster in candidate_clusters:
            by_measure.setdefault(int(cluster["measure"]), []).append(cluster)

        onset_groups: list[dict[str, Any]] = []
        group_id = 0
        for measure in sorted(by_measure):
            clusters = sorted(
                by_measure[measure],
                key=lambda row: (float(row["onsetTime"]), int(row["midi"]), int(row["clusterId"])),
            )
            current: list[dict[str, Any]] = []
            anchor: float | None = None

            def flush_group() -> None:
                nonlocal current, anchor, group_id
                if not current:
                    return
                weights = [max(1, int(row.get("detectionCount") or 1)) for row in current]
                weight_sum = float(sum(weights))
                onset_time = sum(float(row["onsetTime"]) * w for row, w in zip(current, weights)) / weight_sum
                midis = sorted({int(row["midi"]) for row in current})
                group_id += 1
                onset_groups.append(
                    {
                        "onsetGroupId": group_id,
                        "measure": measure,
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
            raise RuntimeError("No fresh Section 4 physical onset groups produced")

        crop_seconds = max(float(group["onsetTime"]) for group in onset_groups) + 0.40
        bins_per_semitone = BINS_PER_OCTAVE // 12
        n_bins = (CQT_MIDI_MAX - CQT_MIDI_MIN + 1) * bins_per_semitone

        def load_view(path: Path) -> tuple[np.ndarray, int]:
            audio, sr = sf.read(str(path), always_2d=False)
            y = np.asarray(audio, dtype=np.float32)
            if y.ndim == 2:
                y = np.mean(y, axis=1)
            if y.ndim != 1 or y.size == 0:
                raise RuntimeError(f"Unexpected stem shape for {path}: {y.shape}")
            y = y[: int(round(float(sr) * crop_seconds))]
            if int(sr) != TARGET_SR:
                y = librosa.resample(y, orig_sr=int(sr), target_sr=TARGET_SR)
                sr = TARGET_SR
            return np.asarray(y, dtype=np.float32), int(sr)

        def build_log_cqt(path: Path) -> np.ndarray:
            y, sr = load_view(path)
            cqt = librosa.cqt(
                y=y,
                sr=sr,
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

        def semitone_vector(log_cqt: np.ndarray, start: float, end: float, reducer: str) -> list[float]:
            lo, hi = frame_bounds(start, end, log_cqt.shape[1])
            values: list[float] = []
            for midi in range(CQT_MIDI_MIN, CQT_MIDI_MAX + 1):
                center = int(round((midi - CQT_MIDI_MIN) * bins_per_semitone))
                bin_lo = max(0, center - 1)
                bin_hi = min(log_cqt.shape[0], center + 2)
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
        for index, group in enumerate(onset_groups, start=1):
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
            if index % 250 == 0:
                print(f"fresh Section 4 onset spectra {index}/{len(onset_groups)}")

        section_grid = [
            {
                "globalStep": int(slot.global_step),
                "measure": int(slot.measure),
                "step": int(slot.step),
                "timeSeconds": float(slot.time_seconds),
            }
            for slot in grid
            if FIRST_MEASURE <= int(slot.measure) <= LAST_MEASURE
        ]

        return {
            "cacheVersion": 1,
            "scope": "fresh-section4-measures-65-80-reference-free",
            "section": {"name": "Fresh Section 4", "startMeasure": FIRST_MEASURE, "endMeasure": LAST_MEASURE},
            "timing": {
                "tempoBpm": float(timing.tempo_bpm),
                "firstBeatInMeasure": int(timing.first_beat_in_measure),
                "downbeatIndexMod4": int(timing.downbeat_index_mod4),
                "beatConfidence": float(timing.beat_confidence),
                "barConfidence": float(timing.bar_confidence),
            },
            "grid": section_grid,
            "rawEventCount": len(raw_events),
            "candidateClusterCount": len(candidate_clusters),
            "onsetGroupCount": len(spectral_rows),
            "rows": spectral_rows,
            "sweepEventCounts": dict(sorted(sweep_counts.items())),
            "stemEventCounts": dict(sorted(stem_counts.items())),
            "candidateStemCount": len(stem_paths),
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
            "sourceDurationSeconds": source_metadata.get("duration"),
        }


@app.local_entrypoint(name="capture_fresh_section4")
def capture_fresh_section4(audio_path: str = str(DEFAULT_AUDIO_PATH)) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("=== V143 FRESH SECTION 4 REFERENCE-FREE CAPTURE ===")
    print("Measures: 65-80")
    print("Professional reference available to remote analyzer: False")
    print("Running frozen deterministic separator + raw attacks + onset spectra...")
    result = capture_fresh_section4_reference_free.remote(payload, source.suffix)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n")

    print()
    print("=== V143 FRESH SECTION 4 CACHE CAPTURED ===")
    print("measureRange: 65..80")
    print("rawEventCount:", result.get("rawEventCount"))
    print("candidateClusterCount:", result.get("candidateClusterCount"))
    print("onsetGroupCount:", result.get("onsetGroupCount"))
    print("candidateStemCount:", result.get("candidateStemCount"))
    print("tempoBpm:", result.get("timing", {}).get("tempoBpm"))
    print("spectrumMidiRange:", f"{result.get('spectrumMidiMin')}..{result.get('spectrumMidiMax')}")
    print("referenceFree:", result.get("referenceFree") is True)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Cache:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("READY FOR FROZEN-MODEL PREDICTION:", True)


if __name__ == "__main__":
    # Allows py_compile/import while keeping Modal as the execution path.
    pass
