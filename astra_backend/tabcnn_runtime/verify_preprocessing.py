#!/usr/bin/env python3
"""Numerically compare Astra's minimal preprocessing against exact pinned source files.

No model/checkpoint is loaded or executed.
"""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import sys
from pathlib import Path

import librosa
import numpy as np
import scipy
import torch

from preprocessing import describe_array, preprocess_waveform


def synthetic_audio() -> np.ndarray:
    sr = 22050
    n = sr * 3
    t = np.arange(n, dtype=np.float64) / sr
    envelope = np.linspace(0.35, 1.0, n, dtype=np.float64)
    signal = (
        0.37 * np.sin(2 * np.pi * 82.4068892282175 * t)
        + 0.23 * np.sin(2 * np.pi * 110.0 * t + 0.17)
        + 0.19 * np.sin(2 * np.pi * 164.813778456435 * t + 0.31)
        + 0.07 * np.sin(2 * np.pi * (220.0 + 18.0 * t) * t)
    )
    return (signal * envelope).astype(np.float32)


def load_reference(source_root: Path):
    sys.path.insert(0, str(source_root))
    try:
        source_utils = importlib.import_module("amt_tools.tools.utils")
        source_cqt = importlib.import_module("amt_tools.features.cqt")
    finally:
        sys.path.pop(0)
    return source_utils, source_cqt


def max_abs(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        raise AssertionError(f"shape mismatch: {a.shape} != {b.shape}")
    return float(np.max(np.abs(a.astype(np.float64) - b.astype(np.float64))))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--receipt-out", required=True)
    args = parser.parse_args()

    source_utils, source_cqt = load_reference(Path(args.source_root))
    audio = synthetic_audio()

    reference_normalized = source_utils.rms_norm(audio.copy())
    reference_processor = source_cqt.CQT(
        sample_rate=22050,
        hop_length=512,
        decibels=True,
        fmin=None,
        n_bins=192,
        bins_per_octave=24,
    )
    reference_features = reference_processor.process_audio(reference_normalized)
    reference_batched = np.expand_dims(reference_features, axis=0)
    reference_windows = source_utils.framify_activations(
        reference_batched, 9, pad=True
    )
    reference_windows = reference_windows.transpose(-2, -3)
    reference_windows = reference_windows.transpose(-3, -4)

    astra = preprocess_waveform(audio.copy())

    diffs = {
        "normalized_audio": max_abs(astra["normalized_audio"], reference_normalized),
        "features": max_abs(astra["features"], reference_features),
        "model_windows": max_abs(astra["model_windows"], reference_windows),
    }

    tolerance = 1e-7
    if any(value > tolerance for value in diffs.values()):
        raise AssertionError(f"preprocessing mismatch beyond {tolerance}: {diffs}")

    receipt = {
        "schema": "astra-tabcnn-preprocessing-reproduction-v1",
        "modelInvoked": False,
        "checkpointLoaded": False,
        "syntheticAudioOnly": True,
        "sourceRevision": "f50309ad06dc734ddae5e3a0eda756fca221e2e7",
        "sourceBlobs": {
            "featureCommon": "79b71e763bc12d9d8a26d5bcce5b8ff9800bea92",
            "vqt": "a4e5e7d4958ec64d2d149eb51acdaf936e649b00",
            "cqt": "7f08cbd3448765c5406b28f8627a8a8fb66f27b7",
            "utils": "55e989685f95593605566a4e730b8aa2e0eabc12",
            "constants": "79666ea0c5b0214ca664da454069b8d286cc5c18",
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "librosa": librosa.__version__,
            "torch": torch.__version__,
        },
        "contract": {
            "sampleRateHz": 22050,
            "hopLengthSamples": 512,
            "cqtBins": 192,
            "binsPerOctave": 24,
            "fmin": "C1",
            "gamma": 0,
            "decibelReference": "max",
            "featureScale": "db_div_80_plus_1",
            "frameContext": 9,
            "audioNormalization": "rms",
        },
        "maxAbsoluteDifference": diffs,
        "syntheticAudio": describe_array(audio),
        "normalizedAudio": describe_array(astra["normalized_audio"]),
        "features": describe_array(astra["features"]),
        "modelWindows": describe_array(astra["model_windows"]),
    }

    out = Path(args.receipt_out)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("TABCNN_PREPROCESS_RECEIPT_JSON=" + json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
