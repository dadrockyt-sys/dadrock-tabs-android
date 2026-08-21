from __future__ import annotations

import concurrent.futures
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_historical_band_diagnostic_modal import (
    _build_shadow_stems,
    _research_normalize_audio,
    _safe_suffix,
    _sha256,
    diagnostic_image,
)


app = modal.App("dadrock-v143-section2-pcm-stabilization-survey")
survey_image = diagnostic_image.add_local_python_source(
    "v143_contextual_prune_historical_band_diagnostic_modal"
)

WORKER_COUNT = 5
CLEAR_BITS = tuple(range(0, 9))


def _quantized_pcm_hashes(path: Path) -> dict[str, Any]:
    import numpy as np
    import soundfile as sf

    audio, sample_rate = sf.read(str(path), dtype="int16", always_2d=True)
    base = audio.astype(np.int32, copy=False)
    hashes: dict[str, str] = {}
    for bits in CLEAR_BITS:
        if bits == 0:
            quantized = audio
        else:
            mask = ~((1 << bits) - 1)
            quantized = (base & mask).astype(np.int16)
        hashes[str(bits)] = hashlib.sha256(quantized.tobytes()).hexdigest()

    return {
        "sampleRate": int(sample_rate),
        "frames": int(audio.shape[0]),
        "channels": int(audio.shape[1]),
        "clearLowBitsSha256": hashes,
        "minSample": int(audio.min()),
        "maxSample": int(audio.max()),
        "meanAbsSample": float(np.mean(np.abs(base))),
    }


@app.function(image=survey_image, gpu="L4", timeout=1800, memory=12288)
def survey_worker(source_audio: bytes, suffix: str, worker_index: int) -> dict[str, Any]:
    if not source_audio:
        raise ValueError("Diagnostic audio is empty")

    with tempfile.TemporaryDirectory(prefix=f"v143-pcm-survey-{worker_index}-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, normalized)
        stems, direct, cascade = _build_shadow_stems(normalized, root / "stems")

        return {
            "worker": int(worker_index),
            "normalizedSha256": _sha256(normalized),
            "separator": {
                "deterministicFlag": stems.get("deterministic") is True,
                "referenceFree": stems.get("referenceFree") is True,
                "directFileSha256": _sha256(direct),
                "cascadeFileSha256": _sha256(cascade),
                "directPcm": _quantized_pcm_hashes(direct),
                "cascadePcm": _quantized_pcm_hashes(cascade),
            },
        }


def _survey(rows: list[dict[str, Any]], stem: str) -> dict[str, Any]:
    unique_counts: dict[str, int] = {}
    hashes_by_bits: dict[str, list[str]] = {}
    first_exact: int | None = None
    for bits in CLEAR_BITS:
        key = str(bits)
        values = [
            row["separator"][stem]["clearLowBitsSha256"][key]
            for row in rows
        ]
        hashes_by_bits[key] = values
        count = len(set(values))
        unique_counts[key] = count
        if first_exact is None and count == 1:
            first_exact = bits
    return {
        "uniqueHashCountByClearedLowBits": unique_counts,
        "firstClearedLowBitsWithExactCrossWorkerPcm": first_exact,
        "hashesByClearedLowBits": hashes_by_bits,
    }


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    payload = source.read_bytes()

    def invoke(index: int) -> dict[str, Any]:
        return survey_worker.remote(payload, source.suffix, index)

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKER_COUNT) as pool:
        workers = list(pool.map(invoke, range(1, WORKER_COUNT + 1)))
    workers.sort(key=lambda row: int(row["worker"]))

    result = {
        "schemaVersion": 1,
        "gate": "v143-section2-pcm-stabilization-survey",
        "executionStrategy": "five-independent-l4-separations-int16-low-bit-clearing-hash-survey",
        "workerCount": WORKER_COUNT,
        "clearLowBitsTested": list(CLEAR_BITS),
        "sourceSha256": hashlib.sha256(payload).hexdigest(),
        "workers": workers,
        "directPcmSurvey": _survey(workers, "directPcm"),
        "cascadePcmSurvey": _survey(workers, "cascadePcm"),
        "invariants": {
            "professionalReferenceOpened": False,
            "runtimeLabelsRequired": False,
            "frozenModelModified": False,
            "frozenPredictionsModified": False,
            "thresholdsModified": False,
            "liveEndpointDeployedOrModified": False,
            "productionModified": False,
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
