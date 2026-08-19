from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from v143_modal_live_endpoint import app, rhythm_image


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
RAW_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-raw-attack-cache.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-onset-spectrum-cache.json"
)

TARGET_SR = 22050
HOP_LENGTH = 128
BINS_PER_OCTAVE = 36
CQT_MIDI_MIN = 28
CQT_MIDI_MAX = 112
GUITAR_MIDI_MIN = 40
GUITAR_MIDI_MAX = 88
ONSET_GROUP_TOLERANCE_SECONDS = 0.030

stage_image = rhythm_image.add_local_python_source(
    "v143_modal_live_endpoint",
    "v143_intro_raw_attack_temporal_diagnostic",
)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _group_physical_onsets(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse candidate-pitch clusters into reference-free physical onset groups.

    Candidate clusters from different MIDI hypotheses that occur within 30 ms are
    treated as the same physical attack. This preserves polyphonic candidate sets
    while removing the candidate-by-candidate abstraction that failed the earlier
    ranking diagnostics.
    """
    by_measure: dict[int, list[dict[str, Any]]] = {}
    for cluster in clusters:
        measure = int(cluster.get("measure") or 0)
        onset = _safe_float(cluster.get("onsetTime"), -1.0)
        midi = int(cluster.get("midi") or 0)
        if not (1 <= measure <= 16 and onset >= 0.0 and GUITAR_MIDI_MIN <= midi <= GUITAR_MIDI_MAX):
            continue
        by_measure.setdefault(measure, []).append(cluster)

    groups: list[dict[str, Any]] = []
    group_id = 0
    for measure in sorted(by_measure):
        rows = sorted(
            by_measure[measure],
            key=lambda row: (
                _safe_float(row.get("onsetTime")),
                int(row.get("midi") or 0),
                int(row.get("clusterId") or 0),
            ),
        )
        current: list[dict[str, Any]] = []
        anchor = None

        def flush() -> None:
            nonlocal current, anchor, group_id
            if not current:
                return
            weights = [max(1, int(row.get("detectionCount") or 1)) for row in current]
            weight_sum = float(sum(weights))
            onset_time = sum(
                _safe_float(row.get("onsetTime")) * weight
                for row, weight in zip(current, weights)
            ) / max(weight_sum, 1.0)
            midis = sorted({int(row.get("midi") or 0) for row in current})
            group_id += 1
            groups.append(
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

        for row in rows:
            onset = _safe_float(row.get("onsetTime"))
            if not current:
                current = [row]
                anchor = onset
                continue
            # Keep the group tight around the first physical attack rather than
            # allowing chain-link merging across a long run of nearby candidates.
            if abs(onset - float(anchor)) <= ONSET_GROUP_TOLERANCE_SECONDS:
                current.append(row)
            else:
                flush()
                current = [row]
                anchor = onset
        flush()

    return groups


@app.function(
    image=stage_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def capture_onset_spectra(
    source_audio: bytes,
    onset_groups: list[dict[str, Any]],
    suffix: str = ".m4a",
) -> dict[str, Any]:
    """Capture onset-level CQT spectra from both deterministic guitar views.

    No professional reference, labels, or target pitches are present remotely.
    Each row represents one physical attack and carries the whole spectral field
    needed for later joint sparse note-set decomposition.
    """
    import tempfile

    import librosa
    import numpy as np
    import soundfile as sf

    import modal_analyzer as legacy
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )

    clean_groups: list[dict[str, Any]] = []
    for raw in onset_groups:
        if not isinstance(raw, dict):
            continue
        group_id = int(raw.get("onsetGroupId") or 0)
        measure = int(raw.get("measure") or 0)
        onset = _safe_float(raw.get("onsetTime"), -1.0)
        candidate_midis = sorted(
            {
                int(value)
                for value in (raw.get("candidateMidis") or [])
                if GUITAR_MIDI_MIN <= int(value) <= GUITAR_MIDI_MAX
            }
        )
        if group_id > 0 and 1 <= measure <= 16 and onset >= 0.0:
            clean_groups.append(
                {
                    "onsetGroupId": group_id,
                    "measure": measure,
                    "onsetTime": onset,
                    "candidateMidis": candidate_midis,
                    "candidateCount": len(candidate_midis),
                    "sourceClusterCount": int(raw.get("sourceClusterCount") or 0),
                    "stemSupportMax": int(raw.get("stemSupportMax") or 0),
                    "sweepSupportMax": int(raw.get("sweepSupportMax") or 0),
                    "detectionCountSum": int(raw.get("detectionCountSum") or 0),
                }
            )
    if not clean_groups:
        raise RuntimeError("No valid onset groups supplied")

    safe_suffix = str(suffix or ".audio").lower()
    if safe_suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        safe_suffix = ".audio"

    with tempfile.TemporaryDirectory(prefix="v143-onset-spectrum-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("Onset-spectrum source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        bundle = build_deterministic_rhythm_stem_bundle(normalized).validate()
        stem_paths = [Path(path) for path in bundle.candidate_stem_paths]
        if len(stem_paths) != 2:
            raise RuntimeError(f"Expected two deterministic guitar views, got {len(stem_paths)}")

        crop_seconds = max(group["onsetTime"] for group in clean_groups) + 0.40
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

        def semitone_vector(
            log_cqt: np.ndarray,
            start: float,
            end: float,
            reducer: str,
        ) -> list[float]:
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
            # Normalize each window by its median spectral floor so that joint
            # decomposition compares relative partial structure, not view gain.
            floor = float(np.median(values))
            return [round(float(value - floor), 6) for value in values]

        rows: list[dict[str, Any]] = []
        for index, group in enumerate(clean_groups, start=1):
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
            rows.append(row)
            if index % 250 == 0:
                print(f"onset spectra {index}/{len(clean_groups)}")

        return {
            "cacheVersion": 1,
            "scope": "reference-free-physical-onset-whole-spectrum-cache",
            "targetSampleRate": TARGET_SR,
            "hopLength": HOP_LENGTH,
            "binsPerOctave": BINS_PER_OCTAVE,
            "spectrumMidiMin": CQT_MIDI_MIN,
            "spectrumMidiMax": CQT_MIDI_MAX,
            "guitarMidiMin": GUITAR_MIDI_MIN,
            "guitarMidiMax": GUITAR_MIDI_MAX,
            "onsetGroupingToleranceMs": round(1000.0 * ONSET_GROUP_TOLERANCE_SECONDS, 3),
            "candidateStemCount": len(stem_paths),
            "onsetGroupCount": len(rows),
            "rows": rows,
            "referenceFree": True,
            "professionalReferenceUsedByAnalyzer": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
            "sourceDurationSeconds": source_metadata.get("duration"),
        }


@app.local_entrypoint(name="capture_intro_onset_spectrum_cache")
def capture_intro_onset_spectrum_cache(
    audio_path: str = str(DEFAULT_AUDIO_PATH),
) -> None:
    from v143_intro_raw_attack_temporal_diagnostic import _cluster_events

    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")
    if not RAW_CACHE_PATH.exists():
        raise RuntimeError(f"Raw attack cache missing: {RAW_CACHE_PATH}")

    raw_cache = json.loads(RAW_CACHE_PATH.read_text())
    clusters = _cluster_events(raw_cache)
    onset_groups = _group_physical_onsets(clusters)
    if not onset_groups:
        raise RuntimeError("No physical onset groups produced")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("Capturing onset-level whole-spectrum evidence for joint pitch-set decomposition...")
    print("rawCandidateClusterCount:", len(clusters))
    print("physicalOnsetGroupCount:", len(onset_groups))
    result = capture_onset_spectra.remote(payload, onset_groups, source.suffix)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n")

    print()
    print("=== V143 INTRO ONSET SPECTRUM CACHE CAPTURED ===")
    print("onsetGroupCount:", result.get("onsetGroupCount"))
    print("candidateStemCount:", result.get("candidateStemCount"))
    print("targetSampleRate:", result.get("targetSampleRate"))
    print("hopLength:", result.get("hopLength"))
    print("binsPerOctave:", result.get("binsPerOctave"))
    print("spectrumMidiRange:", f"{result.get('spectrumMidiMin')}..{result.get('spectrumMidiMax')}")
    print("referenceFree:", result.get("referenceFree") is True)
    print("Professional reference used by analyzer: False")
    print("Production modified: False")
    print("Cache:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("READY FOR JOINT SPARSE PITCH-SET DECOMPOSITION:", True)
