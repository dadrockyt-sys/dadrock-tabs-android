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
    / "intro-raw-attack-harmonic-cache.json"
)

TARGET_SR = 22050
HOP_LENGTH = 128
BINS_PER_OCTAVE = 36
CQT_MIDI_MIN = 28
CQT_MIDI_MAX = 112
GUITAR_MIDI_MIN = 40
GUITAR_MIDI_MAX = 88

# Candidate-specific harmonic offsets in semitones. These correspond to the
# octave, octave+fifth, two octaves, etc. and are useful on distorted guitar,
# where upper partials can dominate the fundamental.
HARMONIC_OFFSETS = (
    (12, 1.00),
    (19, 0.70),
    (24, 0.55),
    (28, 0.40),
    (31, 0.30),
    (36, 0.20),
)

# rhythm_image already contains the frozen deterministic separator and the
# reference-free V143 runtime. Package the live endpoint plus this diagnostic's
# clustering helper so the remote module can hydrate cleanly.
stage_image = rhythm_image.add_local_python_source(
    "v143_modal_live_endpoint",
    "v143_intro_raw_attack_temporal_diagnostic",
)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


@app.function(
    image=stage_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def capture_raw_attack_harmonic_evidence(
    source_audio: bytes,
    targets: list[dict[str, Any]],
    suffix: str = ".m4a",
) -> dict[str, Any]:
    """Capture candidate-specific harmonic evidence at exact raw attack times.

    No professional transcription or runtime labels are present in this remote
    function. Targets contain only reference-free raw attack cluster metadata.
    """
    import tempfile

    import librosa
    import numpy as np
    import soundfile as sf

    import modal_analyzer as legacy
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )

    safe_suffix = str(suffix or ".audio").lower()
    if safe_suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        safe_suffix = ".audio"

    clean_targets: list[dict[str, Any]] = []
    for raw in targets:
        if not isinstance(raw, dict):
            continue
        cluster_id = int(raw.get("clusterId") or 0)
        measure = int(raw.get("measure") or 0)
        midi = int(raw.get("midi") or 0)
        onset_time = _safe_float(raw.get("onsetTime"), -1.0)
        if (
            cluster_id > 0
            and 1 <= measure <= 16
            and GUITAR_MIDI_MIN <= midi <= GUITAR_MIDI_MAX
            and onset_time >= 0.0
        ):
            clean_targets.append(
                {
                    "clusterId": cluster_id,
                    "measure": measure,
                    "midi": midi,
                    "onsetTime": onset_time,
                }
            )
    if not clean_targets:
        raise RuntimeError("No valid raw attack clusters supplied")

    with tempfile.TemporaryDirectory(prefix="v143-raw-harmonic-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("Raw harmonic source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        bundle = build_deterministic_rhythm_stem_bundle(normalized).validate()
        stem_paths = [Path(path) for path in bundle.candidate_stem_paths]
        if len(stem_paths) != 2:
            raise RuntimeError(f"Expected two deterministic guitar views, got {len(stem_paths)}")

        crop_seconds = max(item["onsetTime"] for item in clean_targets) + 0.40
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

        def midi_bin(midi: int) -> int:
            return int(round((int(midi) - CQT_MIDI_MIN) * bins_per_semitone))

        def frame_bounds(time_start: float, time_end: float, frame_count: int) -> tuple[int, int]:
            lo = int(math.floor(max(0.0, time_start) * TARGET_SR / HOP_LENGTH))
            hi = int(math.ceil(max(0.0, time_end) * TARGET_SR / HOP_LENGTH)) + 1
            lo = max(0, min(frame_count - 1, lo))
            hi = max(lo + 1, min(frame_count, hi))
            return lo, hi

        def midi_window_value(
            log_cqt: np.ndarray,
            midi: int,
            time_start: float,
            time_end: float,
            reducer: str,
        ) -> float:
            if midi < CQT_MIDI_MIN or midi > CQT_MIDI_MAX:
                return -12.0
            idx = midi_bin(midi)
            bin_lo = max(0, idx - 1)
            bin_hi = min(log_cqt.shape[0], idx + 2)
            frame_lo, frame_hi = frame_bounds(time_start, time_end, log_cqt.shape[1])
            block = log_cqt[bin_lo:bin_hi, frame_lo:frame_hi]
            if block.size == 0:
                return -12.0
            if reducer == "mean":
                return float(np.mean(block))
            return float(np.max(block))

        def baseline_window(
            log_cqt: np.ndarray,
            time_start: float,
            time_end: float,
        ) -> float:
            values = [
                midi_window_value(log_cqt, midi, time_start, time_end, "max")
                for midi in range(GUITAR_MIDI_MIN, GUITAR_MIDI_MAX + 1)
            ]
            return float(np.median(values))

        def one_view_features(log_cqt: np.ndarray, onset: float, midi: int) -> dict[str, float]:
            attack_start, attack_end = onset - 0.020, onset + 0.045
            early_start, early_end = onset + 0.020, onset + 0.095
            sustain_start, sustain_end = onset + 0.070, onset + 0.180

            attack_baseline = baseline_window(log_cqt, attack_start, attack_end)
            early_baseline = baseline_window(log_cqt, early_start, early_end)
            sustain_baseline = baseline_window(log_cqt, sustain_start, sustain_end)

            fund_attack = (
                midi_window_value(log_cqt, midi, attack_start, attack_end, "max")
                - attack_baseline
            )
            fund_early = (
                midi_window_value(log_cqt, midi, early_start, early_end, "mean")
                - early_baseline
            )
            fund_sustain = (
                midi_window_value(log_cqt, midi, sustain_start, sustain_end, "mean")
                - sustain_baseline
            )

            neighbor_attack = [
                midi_window_value(log_cqt, other, attack_start, attack_end, "max")
                - attack_baseline
                for other in (midi - 2, midi - 1, midi + 1, midi + 2)
                if CQT_MIDI_MIN <= other <= CQT_MIDI_MAX
            ]
            local_peak_margin = fund_attack - max(neighbor_attack) if neighbor_attack else 0.0

            harmonic_values: list[tuple[float, float]] = []
            for offset, weight in HARMONIC_OFFSETS:
                harmonic_midi = midi + offset
                if harmonic_midi > CQT_MIDI_MAX:
                    continue
                value = (
                    midi_window_value(
                        log_cqt,
                        harmonic_midi,
                        early_start,
                        early_end,
                        "mean",
                    )
                    - early_baseline
                )
                harmonic_values.append((float(weight), float(value)))
            harmonic_weight = sum(weight for weight, _value in harmonic_values) or 1.0
            harmonic_mean = sum(weight * value for weight, value in harmonic_values) / harmonic_weight
            harmonic_floor = min((value for _weight, value in harmonic_values), default=0.0)

            lower_octave = (
                midi_window_value(log_cqt, midi - 12, early_start, early_end, "mean")
                - early_baseline
                if midi - 12 >= CQT_MIDI_MIN
                else -12.0
            )
            lower_nineteenth = (
                midi_window_value(log_cqt, midi - 19, early_start, early_end, "mean")
                - early_baseline
                if midi - 19 >= CQT_MIDI_MIN
                else -12.0
            )
            subharmonic_max = max(lower_octave, lower_nineteenth)

            return {
                "fundAttack": fund_attack,
                "fundEarly": fund_early,
                "fundSustain": fund_sustain,
                "localPeakMargin": local_peak_margin,
                "harmonicMean": harmonic_mean,
                "harmonicFloor": harmonic_floor,
                "harmonicPlusFund": 0.55 * fund_early + 0.45 * harmonic_mean,
                "harmonicMinusSub": harmonic_mean - subharmonic_max,
                "lowerOctave": lower_octave,
                "lowerNineteenth": lower_nineteenth,
            }

        rows: list[dict[str, Any]] = []
        for index, target in enumerate(clean_targets, start=1):
            onset = float(target["onsetTime"])
            midi = int(target["midi"])
            a = one_view_features(views[0], onset, midi)
            b = one_view_features(views[1], onset, midi)

            combined: dict[str, float] = {}
            for key in a:
                av = float(a[key])
                bv = float(b[key])
                combined[f"mean{key[0].upper()}{key[1:]}"] = 0.5 * (av + bv)
                combined[f"min{key[0].upper()}{key[1:]}"] = min(av, bv)
                combined[f"max{key[0].upper()}{key[1:]}"] = max(av, bv)
                combined[f"agreement{key[0].upper()}{key[1:]}"] = 1.0 / (1.0 + abs(av - bv))

            rows.append(
                {
                    **target,
                    "viewA": {key: round(float(value), 6) for key, value in a.items()},
                    "viewB": {key: round(float(value), 6) for key, value in b.items()},
                    "combined": {
                        key: round(float(value), 6) for key, value in combined.items()
                    },
                }
            )
            if index % 1000 == 0:
                print(f"harmonic evidence {index}/{len(clean_targets)}")

        return {
            "cacheVersion": 1,
            "scope": "raw-physical-attack-candidate-specific-harmonic-evidence",
            "targetSampleRate": TARGET_SR,
            "hopLength": HOP_LENGTH,
            "binsPerOctave": BINS_PER_OCTAVE,
            "cqtMidiMin": CQT_MIDI_MIN,
            "cqtMidiMax": CQT_MIDI_MAX,
            "candidateStemCount": len(stem_paths),
            "clusterCount": len(rows),
            "rows": rows,
            "referenceFree": True,
            "professionalReferenceUsedByAnalyzer": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
            "sourceDurationSeconds": source_metadata.get("duration"),
        }


@app.local_entrypoint(name="capture_intro_raw_attack_harmonic_cache")
def capture_intro_raw_attack_harmonic_cache(
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
    targets = [
        {
            "clusterId": int(cluster["clusterId"]),
            "measure": int(cluster["measure"]),
            "midi": int(cluster["midi"]),
            "onsetTime": float(cluster["onsetTime"]),
        }
        for cluster in clusters
        if 1 <= int(cluster["measure"]) <= 16
    ]
    if not targets:
        raise RuntimeError("Raw attack cache produced no physical clusters")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("Capturing candidate-specific harmonic evidence at exact raw attack times...")
    print("physicalAttackClusterCount:", len(targets))
    result = capture_raw_attack_harmonic_evidence.remote(payload, targets, source.suffix)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n")

    print()
    print("=== V143 INTRO RAW ATTACK HARMONIC CACHE CAPTURED ===")
    print("clusterCount:", result.get("clusterCount"))
    print("candidateStemCount:", result.get("candidateStemCount"))
    print("targetSampleRate:", result.get("targetSampleRate"))
    print("hopLength:", result.get("hopLength"))
    print("binsPerOctave:", result.get("binsPerOctave"))
    print("referenceFree:", result.get("referenceFree") is True)
    print("Professional reference used by analyzer: False")
    print("Production modified: False")
    print("Cache:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("READY FOR CANDIDATE-SPECIFIC HARMONIC RANKING: True")


if __name__ == "__main__":
    capture_intro_raw_attack_harmonic_cache()
