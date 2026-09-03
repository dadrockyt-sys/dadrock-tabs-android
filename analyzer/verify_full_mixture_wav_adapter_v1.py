from __future__ import annotations

import json
import math
import os
import tempfile
import wave
from pathlib import Path

from full_mixture_wav_adapter_v1 import (
    estimate_full_mixture_structure_from_wav_v1,
)

SOURCE_RATE = 44100
CLICK_SECONDS = 0.008


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def clamp(value: float) -> float:
    return max(-1.0, min(1.0, value))


def encode_sample(value: float, width: int) -> bytes:
    value = clamp(value)
    if width == 1:
        integer = max(0, min(255, int(round(value * 127.0 + 128.0))))
        return bytes([integer])
    if width == 2:
        integer = int(round(value * 32767.0))
        return integer.to_bytes(2, "little", signed=True)
    if width == 3:
        integer = int(round(value * 8388607.0))
        if integer < 0:
            integer += 1 << 24
        return integer.to_bytes(3, "little", signed=False)
    if width == 4:
        integer = int(round(value * 2147483647.0))
        return integer.to_bytes(4, "little", signed=True)
    raise ValueError("unsupported width")


def write_click_wav(
    path: Path,
    *,
    width: int = 2,
    channels: int = 1,
    bpm: float = 120.0,
    beat_count: int = 32,
    meter: int | None = None,
    downbeat_offset: int = 0,
    opposite_polarity: bool = False,
    sample_rate: int = SOURCE_RATE,
) -> None:
    period = 60.0 / bpm
    duration = beat_count * period + 0.5
    frame_count = int(round(duration * sample_rate))
    click_length = max(1, int(round(CLICK_SECONDS * sample_rate)))
    mono = [0.0] * frame_count

    for beat_index in range(beat_count):
        amplitude = 1.0
        if meter is not None:
            amplitude = (
                1.0
                if (beat_index - downbeat_offset) % meter == 0
                else 0.4
            )
        start = int(round(beat_index * period * sample_rate))
        for offset in range(click_length):
            index = start + offset
            if index >= frame_count:
                break
            mono[index] += amplitude * (1.0 - offset / click_length)

    raw = bytearray()
    for value in mono:
        first = clamp(value)
        for channel_index in range(channels):
            channel_value = first
            if opposite_polarity and channel_index % 2 == 1:
                channel_value = -first
            raw.extend(encode_sample(channel_value, width))

    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(width)
        writer.setframerate(sample_rate)
        writer.writeframes(bytes(raw))


def field_value(result: dict, name: str):
    field = result.get(name)
    return field.get("value") if isinstance(field, dict) else None


results: dict[str, str] = {}

with tempfile.TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    # W1 mono 16-bit 120 BPM
    path = root / "w1-mono16.wav"
    write_click_wav(path, width=2, channels=1)
    w1 = estimate_full_mixture_structure_from_wav_v1(path)
    bpm = field_value(w1, "tempoBpm")
    assert_true(bpm is not None and abs(bpm - 120.0) <= 1.0, f"W1 expected ~120 BPM, got {bpm}")
    results["W1"] = "PASS"

    # W2 stereo 16-bit
    path = root / "w2-stereo16.wav"
    write_click_wav(path, width=2, channels=2)
    w2 = estimate_full_mixture_structure_from_wav_v1(path)
    bpm = field_value(w2, "tempoBpm")
    assert_true(bpm is not None and abs(bpm - 120.0) <= 1.0, f"W2 expected ~120 BPM, got {bpm}")
    results["W2"] = "PASS"

    # W3 opposite-polarity stereo must not cancel
    path = root / "w3-opposite.wav"
    write_click_wav(path, width=2, channels=2, opposite_polarity=True)
    w3 = estimate_full_mixture_structure_from_wav_v1(path)
    bpm = field_value(w3, "tempoBpm")
    assert_true(bpm is not None and abs(bpm - 120.0) <= 1.0, f"W3 expected ~120 BPM despite opposite polarity, got {bpm}")
    results["W3"] = "PASS"

    # W4 accented 4/4
    path = root / "w4-meter.wav"
    write_click_wav(path, width=2, channels=2, meter=4, beat_count=40)
    w4 = estimate_full_mixture_structure_from_wav_v1(path)
    assert_true(field_value(w4, "timeSignature") == {"numerator": 4, "denominator": 4}, f"W4 expected 4/4, got {field_value(w4, 'timeSignature')}")
    results["W4"] = "PASS"

    # W5 one-beat pickup
    path = root / "w5-pickup.wav"
    write_click_wav(path, width=2, channels=2, meter=4, downbeat_offset=1, beat_count=40)
    w5 = estimate_full_mixture_structure_from_wav_v1(path)
    pickup = field_value(w5, "pickupBeats")
    assert_true(pickup is not None and abs(pickup - 1.0) <= 0.15, f"W5 expected ~1 beat pickup, got {pickup}")
    results["W5"] = "PASS"

    # W6 8-bit PCM
    path = root / "w6-8bit.wav"
    write_click_wav(path, width=1, channels=1)
    w6 = estimate_full_mixture_structure_from_wav_v1(path)
    bpm = field_value(w6, "tempoBpm")
    assert_true(bpm is not None and abs(bpm - 120.0) <= 1.0, f"W6 expected ~120 BPM, got {bpm}")
    results["W6"] = "PASS"

    # W7 24-bit PCM
    path = root / "w7-24bit.wav"
    write_click_wav(path, width=3, channels=2)
    w7 = estimate_full_mixture_structure_from_wav_v1(path)
    bpm = field_value(w7, "tempoBpm")
    assert_true(bpm is not None and abs(bpm - 120.0) <= 1.0, f"W7 expected ~120 BPM, got {bpm}")
    results["W7"] = "PASS"

    # W8 32-bit integer PCM
    path = root / "w8-32bit.wav"
    write_click_wav(path, width=4, channels=2)
    w8 = estimate_full_mixture_structure_from_wav_v1(path)
    bpm = field_value(w8, "tempoBpm")
    assert_true(bpm is not None and abs(bpm - 120.0) <= 1.0, f"W8 expected ~120 BPM, got {bpm}")
    results["W8"] = "PASS"

    # W9 invalid/non-admitted input fails closed
    invalid = root / "w9-invalid.wav"
    invalid.write_bytes(b"not-a-wave-file")
    try:
        estimate_full_mixture_structure_from_wav_v1(invalid)
        raise AssertionError("W9 invalid WAV must fail closed")
    except ValueError:
        pass

    low_rate = root / "w9-low-rate.wav"
    write_click_wav(low_rate, width=2, channels=1, sample_rate=4000)
    try:
        estimate_full_mixture_structure_from_wav_v1(low_rate)
        raise AssertionError("W9 unsupported sample rate must fail closed")
    except ValueError:
        pass
    results["W9"] = "PASS"

    # W10 diagnostics + provenance + bounded envelope
    adapter = w2["diagnostics"]["wavAdapter"]
    provenance = w2["provenance"]
    assert_true(adapter["version"] == 1, "W10 adapter version must be 1")
    assert_true(adapter["sourceChannels"] == 2, "W10 source channels must be 2")
    assert_true(adapter["sourceSampleRate"] == SOURCE_RATE, "W10 source rate mismatch")
    assert_true(adapter["envelopeSampleRate"] == 4000, "W10 envelope rate must be 4000 Hz")
    assert_true(adapter["downmix"] == "mean-absolute-channel-energy", "W10 downmix mismatch")
    assert_true(adapter["envelope"] == "target-bin-rms", "W10 envelope method mismatch")
    assert_true(adapter["chunkFrames"] == 16384, "W10 chunk size mismatch")
    assert_true(adapter["fullMixtureOnly"] is True, "W10 fullMixtureOnly must be true")
    assert_true(adapter["separatedCarrierUsed"] is False, "W10 carrier use must be false")
    assert_true(adapter["transcribedEventInputUsed"] is False, "W10 event use must be false")
    assert_true(provenance["sourceKind"] == "full-mixture", "W10 sourceKind mismatch")
    assert_true(provenance["sourceIdentity"] == "request-audio", "W10 sourceIdentity mismatch")
    assert_true(provenance["referenceBlind"] is True, "W10 referenceBlind must be true")
    assert_true(provenance["referenceRuntimeInputUsed"] is False, "W10 reference runtime input must be false")
    expected_envelope = adapter["sourceDurationSeconds"] * 4000
    assert_true(abs(adapter["envelopeSampleCount"] - expected_envelope) <= 2.0, "W10 envelope sample count must remain bounded at ~duration*4000")
    results["W10"] = "PASS"


evidence = {
    "schemaVersion": 1,
    "gate": "full-mixture-wav-adapter-v1",
    "referenceBlind": True,
    "referenceScoreAuthorized": False,
    "syntheticWavOnly": True,
    "externalAudioAssetsUsed": False,
    "fullMixtureOnly": True,
    "separatedCarrierUsed": False,
    "transcribedEventInputUsed": False,
    "guitarSetRead": False,
    "splitMySongRead": False,
    "goatRestrictedBytesRead": False,
    "modalInvoked": False,
    "gpuUsed": False,
    "routeRuntimeConnected": False,
    "productModified": False,
    "productionModified": False,
    "productionPromotionAuthorized": False,
    "tests": results,
    "passed": all(value == "PASS" for value in results.values()),
}

result_path = os.environ.get("FULL_MIXTURE_WAV_ADAPTER_V1_RESULT_PATH", "").strip()
if result_path:
    output = Path(result_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

print(json.dumps(evidence, indent=2))
print("FULL MIXTURE WAV ADAPTER V1 W1-W10 VERIFIED")
