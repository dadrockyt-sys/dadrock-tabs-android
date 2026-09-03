from __future__ import annotations

import math
import wave
from pathlib import Path
from typing import Any

from full_mixture_auto_structure_estimator_v1 import (
    estimate_full_mixture_structure_v1,
)

ADAPTER_VERSION = 1
TARGET_ENVELOPE_RATE = 4000
CHUNK_FRAMES = 16384


def _clamp_unit(value: float) -> float:
    return max(-1.0, min(1.0, float(value)))


def _decode_sample(raw: bytes, sample_width: int) -> float:
    if sample_width == 1:
        return _clamp_unit((raw[0] - 128) / 128.0)
    if sample_width == 2:
        value = int.from_bytes(raw, byteorder="little", signed=True)
        return _clamp_unit(value / 32768.0)
    if sample_width == 3:
        unsigned = raw[0] | (raw[1] << 8) | (raw[2] << 16)
        if unsigned & 0x800000:
            unsigned -= 1 << 24
        return _clamp_unit(unsigned / 8388608.0)
    if sample_width == 4:
        value = int.from_bytes(raw, byteorder="little", signed=True)
        return _clamp_unit(value / 2147483648.0)
    raise ValueError("Unsupported PCM sample width")


def _admit_wav(reader: wave.Wave_read) -> dict[str, int]:
    if reader.getcomptype() != "NONE":
        raise ValueError("WAV compression must be PCM/NONE")

    channels = int(reader.getnchannels())
    sample_rate = int(reader.getframerate())
    sample_width = int(reader.getsampwidth())
    frame_count = int(reader.getnframes())

    if channels < 1 or channels > 8:
        raise ValueError("WAV channels must be between 1 and 8")
    if sample_rate < 8000 or sample_rate > 192000:
        raise ValueError("WAV sample rate must be between 8000 and 192000 Hz")
    if sample_width not in {1, 2, 3, 4}:
        raise ValueError("WAV sample width must be 1, 2, 3, or 4 bytes")
    if frame_count <= 0:
        raise ValueError("WAV must contain at least one PCM frame")

    return {
        "channels": channels,
        "sampleRate": sample_rate,
        "sampleWidth": sample_width,
        "frameCount": frame_count,
    }


def _full_mixture_envelope(
    reader: wave.Wave_read,
    *,
    channels: int,
    sample_rate: int,
    sample_width: int,
) -> tuple[list[float], int]:
    envelope_rate = min(TARGET_ENVELOPE_RATE, sample_rate)
    bytes_per_frame = channels * sample_width
    envelope: list[float] = []

    current_bin: int | None = None
    sum_squares = 0.0
    bin_count = 0
    source_frame_index = 0
    previous_value = 0.0

    def flush_bin(bin_index: int) -> None:
        nonlocal sum_squares, bin_count, previous_value
        while len(envelope) < bin_index:
            envelope.append(previous_value)
        value = math.sqrt(sum_squares / bin_count) if bin_count > 0 else previous_value
        envelope.append(value)
        previous_value = value
        sum_squares = 0.0
        bin_count = 0

    while True:
        raw = reader.readframes(CHUNK_FRAMES)
        if not raw:
            break

        complete_frames = len(raw) // bytes_per_frame
        for frame_offset in range(complete_frames):
            byte_offset = frame_offset * bytes_per_frame
            channel_magnitudes: list[float] = []

            for channel_index in range(channels):
                start = byte_offset + channel_index * sample_width
                end = start + sample_width
                channel_sample = _decode_sample(raw[start:end], sample_width)
                channel_magnitudes.append(abs(channel_sample))

            frame_magnitude = sum(channel_magnitudes) / channels
            bin_index = int(source_frame_index * envelope_rate / sample_rate)

            if current_bin is None:
                current_bin = bin_index
            elif bin_index != current_bin:
                flush_bin(current_bin)
                if bin_index > current_bin + 1:
                    while len(envelope) < bin_index:
                        envelope.append(previous_value)
                current_bin = bin_index

            sum_squares += frame_magnitude * frame_magnitude
            bin_count += 1
            source_frame_index += 1

    if current_bin is not None:
        flush_bin(current_bin)

    return envelope, envelope_rate


def estimate_full_mixture_structure_from_wav_v1(path: str | Path) -> dict[str, Any]:
    wav_path = Path(path)
    if not wav_path.is_file():
        raise ValueError("WAV path does not exist")

    try:
        with wave.open(str(wav_path), "rb") as reader:
            admitted = _admit_wav(reader)
            envelope, envelope_rate = _full_mixture_envelope(
                reader,
                channels=admitted["channels"],
                sample_rate=admitted["sampleRate"],
                sample_width=admitted["sampleWidth"],
            )
    except (wave.Error, EOFError) as error:
        raise ValueError("Invalid or unsupported PCM WAV") from error

    result = estimate_full_mixture_structure_v1(envelope, envelope_rate)
    diagnostics = dict(result.get("diagnostics") or {})
    diagnostics["wavAdapter"] = {
        "version": ADAPTER_VERSION,
        "sourceChannels": admitted["channels"],
        "sourceSampleRate": admitted["sampleRate"],
        "sourceSampleWidthBytes": admitted["sampleWidth"],
        "sourceFrameCount": admitted["frameCount"],
        "sourceDurationSeconds": round(
            admitted["frameCount"] / admitted["sampleRate"], 6
        ),
        "envelopeSampleRate": envelope_rate,
        "envelopeSampleCount": len(envelope),
        "downmix": "mean-absolute-channel-energy",
        "envelope": "target-bin-rms",
        "chunkFrames": CHUNK_FRAMES,
        "fullMixtureOnly": True,
        "separatedCarrierUsed": False,
        "transcribedEventInputUsed": False,
    }
    result["diagnostics"] = diagnostics
    return result
