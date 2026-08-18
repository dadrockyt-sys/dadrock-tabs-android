from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal

from v143_modal_live_endpoint import rhythm_image


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
ANALYSIS_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-analysis-cache.json"
)
SPECTRAL_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-spectral-pitch-cache.json"
)

MIDI_MIN = 40
MIDI_MAX = 88
CQT_MIDI_MIN = 36
CQT_MIDI_MAX = 112
BINS_PER_OCTAVE = 36
TARGET_SR = 22050
HOP_LENGTH = 256
FRAME_RADIUS = 2
HARMONIC_OFFSETS = ((12, 0.55), (19, 0.35), (24, 0.25), (28, 0.15))

spectral_app = modal.App("dadrock-v143-intro-spectral-pitch-capture")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if result == result else default
    except (TypeError, ValueError):
        return default


@spectral_app.function(
    image=rhythm_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def capture_spectral_pitch_evidence(
    source_audio: bytes,
    targets: list[dict[str, Any]],
    suffix: str = ".m4a",
) -> dict[str, Any]:
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
        measure = int(raw.get("measure") or 0)
        step = int(raw.get("step") or 0)
        time_seconds = _safe_float(raw.get("timeSeconds"), -1.0)
        if 1 <= measure <= 16 and 0 <= step < 16 and time_seconds >= 0.0:
            clean_targets.append(
                {
                    "measure": measure,
                    "step": step,
                    "timeSeconds": time_seconds,
                }
            )
    if not clean_targets:
        raise RuntimeError("No valid intro targets supplied")

    with tempfile.TemporaryDirectory(prefix="v143-spectral-pitch-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("Spectral capture source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        bundle = build_deterministic_rhythm_stem_bundle(normalized).validate()
        stem_paths = [bundle.carrier_stem_a_path, bundle.carrier_stem_b_path]

        max_target_time = max(item["timeSeconds"] for item in clean_targets)
        crop_seconds = max_target_time + 1.25

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
            n_bins = (CQT_MIDI_MAX - CQT_MIDI_MIN + 1) * (BINS_PER_OCTAVE // 12)
            cqt = librosa.cqt(
                y=y,
                sr=sr,
                hop_length=HOP_LENGTH,
                fmin=float(librosa.midi_to_hz(CQT_MIDI_MIN)),
                n_bins=int(n_bins),
                bins_per_octave=BINS_PER_OCTAVE,
                filter_scale=0.75,
            )
            magnitude = np.abs(cqt).astype(np.float64)
            return np.log(magnitude + 1e-8)

        view_a = build_log_cqt(Path(stem_paths[0]))
        view_b = build_log_cqt(Path(stem_paths[1]))

        bins_per_semitone = BINS_PER_OCTAVE // 12

        def midi_bin(midi: int) -> int:
            return int(round((int(midi) - CQT_MIDI_MIN) * bins_per_semitone))

        def frame_spectrum(log_cqt: np.ndarray, time_seconds: float) -> dict[int, float]:
            center = int(round(time_seconds * TARGET_SR / HOP_LENGTH))
            lo = max(0, center - FRAME_RADIUS)
            hi = min(log_cqt.shape[1], center + FRAME_RADIUS + 1)
            if lo >= hi:
                lo = max(0, min(log_cqt.shape[1] - 1, center))
                hi = min(log_cqt.shape[1], lo + 1)

            values: dict[int, float] = {}
            for midi in range(CQT_MIDI_MIN, CQT_MIDI_MAX + 1):
                idx = midi_bin(midi)
                bin_lo = max(0, idx - 1)
                bin_hi = min(log_cqt.shape[0], idx + 2)
                values[midi] = float(np.max(log_cqt[bin_lo:bin_hi, lo:hi]))

            baseline = float(np.median([values[m] for m in range(MIDI_MIN, MIDI_MAX + 1)]))
            return {midi: float(value - baseline) for midi, value in values.items()}

        def one_view_features(spectrum: dict[int, float], midi: int) -> dict[str, float]:
            fund = float(spectrum.get(midi, -12.0))
            neighbors = [
                float(spectrum.get(other, -12.0))
                for other in range(max(CQT_MIDI_MIN, midi - 2), min(CQT_MIDI_MAX, midi + 2) + 1)
                if other != midi
            ]
            local_median = float(np.median(neighbors)) if neighbors else -12.0
            peak = fund - local_median
            harmonic = fund
            for offset, weight in HARMONIC_OFFSETS:
                harmonic += float(weight) * float(spectrum.get(midi + offset, -12.0))
            lower_octave = float(spectrum.get(midi - 12, -12.0))
            upper_octave = float(spectrum.get(midi + 12, -12.0))
            return {
                "fund": fund,
                "peak": peak,
                "harmonic": harmonic,
                "lowerOctave": lower_octave,
                "upperOctave": upper_octave,
            }

        output_rows: list[dict[str, Any]] = []
        for target in clean_targets:
            spec_a = frame_spectrum(view_a, target["timeSeconds"])
            spec_b = frame_spectrum(view_b, target["timeSeconds"])
            midi_features: dict[str, dict[str, float]] = {}
            for midi in range(MIDI_MIN, MIDI_MAX + 1):
                a = one_view_features(spec_a, midi)
                b = one_view_features(spec_b, midi)
                midi_features[str(midi)] = {
                    "aFund": round(a["fund"], 6),
                    "bFund": round(b["fund"], 6),
                    "meanFund": round(0.5 * (a["fund"] + b["fund"]), 6),
                    "minFund": round(min(a["fund"], b["fund"]), 6),
                    "aPeak": round(a["peak"], 6),
                    "bPeak": round(b["peak"], 6),
                    "meanPeak": round(0.5 * (a["peak"] + b["peak"]), 6),
                    "minPeak": round(min(a["peak"], b["peak"]), 6),
                    "aHarmonic": round(a["harmonic"], 6),
                    "bHarmonic": round(b["harmonic"], 6),
                    "meanHarmonic": round(0.5 * (a["harmonic"] + b["harmonic"]), 6),
                    "minHarmonic": round(min(a["harmonic"], b["harmonic"]), 6),
                    "viewAgreement": round(1.0 / (1.0 + abs(a["fund"] - b["fund"])), 6),
                    "lowerOctaveMean": round(0.5 * (a["lowerOctave"] + b["lowerOctave"]), 6),
                    "upperOctaveMean": round(0.5 * (a["upperOctave"] + b["upperOctave"]), 6),
                }
            output_rows.append(
                {
                    **target,
                    "midiFeatures": midi_features,
                }
            )

        return {
            "cacheVersion": 1,
            "scope": "professional-measures-1-16",
            "midiMin": MIDI_MIN,
            "midiMax": MIDI_MAX,
            "targetSampleRate": TARGET_SR,
            "hopLength": HOP_LENGTH,
            "binsPerOctave": BINS_PER_OCTAVE,
            "frameRadius": FRAME_RADIUS,
            "rowCount": len(output_rows),
            "rows": output_rows,
            "referenceFree": True,
            "professionalReferenceUsedByAnalyzer": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
            "sourceDurationSeconds": source_metadata.get("duration"),
        }


@spectral_app.local_entrypoint()
def capture_spectral_cache(audio_path: str = str(DEFAULT_AUDIO_PATH)) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")
    if not ANALYSIS_CACHE_PATH.exists():
        raise RuntimeError(f"Analysis cache missing: {ANALYSIS_CACHE_PATH}")

    analysis_cache = json.loads(ANALYSIS_CACHE_PATH.read_text())
    intro_rows = analysis_cache.get("analysis", {}).get("introRows", []) or []
    targets = [
        {
            "measure": int(row.get("measure") or 0),
            "step": int(row.get("step") or 0),
            "timeSeconds": _safe_float(row.get("timeSeconds"), -1.0),
        }
        for row in intro_rows
        if isinstance(row, dict)
    ]
    if not targets:
        raise RuntimeError("Analysis cache contains no intro targets")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("Capturing deterministic dual-view CQT pitch evidence for the intro...")
    result = capture_spectral_pitch_evidence.remote(payload, targets, source.suffix)

    SPECTRAL_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPECTRAL_CACHE_PATH.write_text(json.dumps(result, indent=2) + "\n")

    print()
    print("=== V143 INTRO SPECTRAL PITCH CACHE CAPTURED ===")
    print("rowCount:", result.get("rowCount"))
    print("midiRange:", f"{result.get('midiMin')}..{result.get('midiMax')}")
    print("referenceFree:", result.get("referenceFree") is True)
    print("Professional reference used by analyzer: False")
    print("Production modified: False")
    print("Cache:", SPECTRAL_CACHE_PATH.relative_to(REPO_ROOT))
    print("READY FOR LOCAL SPECTRAL PITCH RANKING: True")


if __name__ == "__main__":
    capture_spectral_cache()
