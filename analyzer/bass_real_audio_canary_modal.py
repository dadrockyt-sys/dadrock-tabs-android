from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_modal_live_endpoint import rhythm_image as frozen_v143_image


app = modal.App("dadrock-v143-bass-real-audio-canary")

APPROVED_FIXTURE = "public/gomywayfullaitest.m4a"
MAX_CANARY_AUDIO_BYTES = 50 * 1024 * 1024
PLAYABLE_BASS_MIN_HZ = 41.203445
PLAYABLE_BASS_MAX_HZ = 391.995436

# Reuse the frozen V143 execution image only as an ephemeral research substrate.
# The Bass scaffold is added as local source; no live Modal endpoint is deployed
# or modified by this canary.
canary_image = frozen_v143_image.add_local_python_source(
    "bass_professional_separator_scaffold"
)


def _analyze_stem(path: Path) -> dict[str, Any]:
    import librosa
    import numpy as np
    import soundfile as sf

    audio, sample_rate = sf.read(path, dtype="float32", always_2d=True)
    if audio.size == 0 or sample_rate <= 0:
        raise RuntimeError(f"Bass canary stem is empty or invalid: {path}")

    mono = np.mean(audio, axis=1).astype(np.float32, copy=False)
    duration_seconds = float(len(mono) / sample_rate)
    rms = float(np.sqrt(np.mean(np.square(mono), dtype=np.float64)))
    peak = float(np.max(np.abs(mono)))

    n_fft = 4096
    hop_length = 1024
    spectrum = np.abs(
        librosa.stft(mono, n_fft=n_fft, hop_length=hop_length, center=True)
    )
    power = np.square(spectrum, dtype=np.float64)
    frequencies = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
    musical_mask = (frequencies >= 20.0) & (
        frequencies <= min(8000.0, sample_rate / 2.0)
    )
    bass_mask = (frequencies >= 30.0) & (frequencies <= 1000.0)
    musical_energy = float(np.sum(power[musical_mask, :]))
    bass_energy = float(np.sum(power[bass_mask, :]))
    bass_band_percent = (
        100.0 * bass_energy / musical_energy if musical_energy > 0.0 else 0.0
    )

    frame_rms = librosa.feature.rms(
        y=mono,
        frame_length=n_fft,
        hop_length=hop_length,
        center=True,
    )[0]
    fundamental_hz = librosa.yin(
        mono,
        fmin=PLAYABLE_BASS_MIN_HZ,
        fmax=PLAYABLE_BASS_MAX_HZ,
        sr=sample_rate,
        frame_length=n_fft,
        hop_length=hop_length,
        center=True,
    )
    frame_count = min(len(frame_rms), len(fundamental_hz))
    frame_rms = frame_rms[:frame_count]
    fundamental_hz = fundamental_hz[:frame_count]

    active_floor = max(1e-5, float(np.max(frame_rms)) * 0.03)
    active_mask = frame_rms >= active_floor
    pitch_mask = active_mask & np.isfinite(fundamental_hz)
    pitches = fundamental_hz[pitch_mask]

    if len(pitches):
        pitch_summary = {
            "activePitchFrameCount": int(len(pitches)),
            "medianFundamentalHz": float(np.median(pitches)),
            "p10FundamentalHz": float(np.percentile(pitches, 10)),
            "p90FundamentalHz": float(np.percentile(pitches, 90)),
            "playableRangeFramePercent": float(
                100.0
                * np.mean(
                    (pitches >= PLAYABLE_BASS_MIN_HZ)
                    & (pitches <= PLAYABLE_BASS_MAX_HZ)
                )
            ),
        }
    else:
        pitch_summary = {
            "activePitchFrameCount": 0,
            "medianFundamentalHz": None,
            "p10FundamentalHz": None,
            "p90FundamentalHz": None,
            "playableRangeFramePercent": 0.0,
        }

    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": int(path.stat().st_size),
        "sampleRate": int(sample_rate),
        "channels": int(audio.shape[1]),
        "durationSeconds": duration_seconds,
        "rms": rms,
        "peak": peak,
        "bassBand30To1000HzPercent": float(bass_band_percent),
        **pitch_summary,
    }


@app.function(
    image=canary_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def analyze_approved_bass_audio(source_audio: bytes) -> dict[str, Any]:
    """Separate and inspect two real-audio Bass views, reference-free.

    This is an isolated research canary. It proves only that the approved full
    audio can be converted into deterministic Bass stems with plausible
    audio-derived Bass-frequency evidence. It does not create note placement,
    timing, techniques, professional structured identity, PDF output, training,
    customer routing, or Production promotion.
    """
    if not source_audio:
        raise ValueError("Bass canary source audio is empty")
    if len(source_audio) > MAX_CANARY_AUDIO_BYTES:
        raise ValueError("Bass canary source audio cannot exceed 50 MB")

    from bass_professional_separator_scaffold import build_diagnostic_bass_stems

    with tempfile.TemporaryDirectory(prefix="dadrock-bass-canary-") as tmp:
        root = Path(tmp)
        source = root / "approved-fixture.m4a"
        source.write_bytes(source_audio)
        outputs = build_diagnostic_bass_stems(source, root / "stems")

        direct = Path(outputs["directBass"])
        cascade = Path(outputs["cascadeBass"])
        direct_metrics = _analyze_stem(direct)
        cascade_metrics = _analyze_stem(cascade)

    return {
        "schemaVersion": 1,
        "mode": "isolated-reference-free-bass-real-audio-canary",
        "approvedFixture": APPROVED_FIXTURE,
        "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
        "sourceBytes": len(source_audio),
        "separator": {
            "directPath": "audio -> Demucs6s Bass",
            "cascadePath": "audio -> BS-RoFormer Instrumental -> Demucs6s Bass",
            "settings": outputs["settings"],
            "models": outputs["models"],
        },
        "views": {
            "direct": direct_metrics,
            "cascade": cascade_metrics,
        },
        "referenceFree": True,
        "diagnosticOnly": True,
        "trainingRunAuthorized": False,
        "analyzerRoutingEnabled": False,
        "professionalStructuredIdentityEnabled": False,
        "pdfRendererEnabled": False,
        "noteTimingTechniqueQualityProven": False,
        "liveEndpointDeployedOrModified": False,
        "vercelDeploymentAttempted": False,
        "productionModified": False,
        "productionPromotionAuthorized": False,
        "paidPurchaseAttempted": False,
        "customerTokenRedeemed": False,
        "customerEmailSent": False,
    }


@app.local_entrypoint(name="run")
def run(
    audio_path: str = APPROVED_FIXTURE,
    output_path: str = ".bass-canary/raw-bass-canary.json",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Approved Bass canary audio missing or empty: {source}")
    if source.as_posix() != APPROVED_FIXTURE:
        raise RuntimeError(
            "Bass canary is locked to the approved repository fixture: "
            f"{APPROVED_FIXTURE}"
        )
    if source.stat().st_size > MAX_CANARY_AUDIO_BYTES:
        raise RuntimeError("Approved Bass canary audio exceeds the 50 MB limit")

    result = analyze_approved_bass_audio.remote(source.read_bytes())
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print("=== BASS REAL-AUDIO CANARY COMPLETE ===")
    print(f"rawOutput={output}")
    print(f"sourceSha256={result.get('sourceSha256')}")
    print(f"referenceFree={result.get('referenceFree') is True}")
    print("analyzerRoutingEnabled=false")
    print("pdfRendererEnabled=false")
    print("productionModified=false")


if __name__ == "__main__":
    pass
