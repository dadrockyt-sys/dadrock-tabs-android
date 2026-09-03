# FULL_MIXTURE_WAV_ADAPTER_V1 — PRE-IMPLEMENTATION FREEZE

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`REFERENCE-BLIND CPU WAV ADAPTER AUTHORIZED / SHADOW ONLY / RUNTIME WIRING NOT AUTHORIZED`**

## Purpose

Bridge an already-normalized full-mixture PCM WAV file to the Phase 5 waveform estimator without using note events, separated stems, Modal execution or reference data.

The adapter must be practical for long songs: it may not materialize every 44.1 kHz stereo PCM sample as a Python float list before analysis.

## Frozen module/API

`analyzer/full_mixture_wav_adapter_v1.py`

```python
estimate_full_mixture_structure_from_wav_v1(path) -> dict
```

The returned object is the Phase 5 trusted full-mixture observation plus adapter diagnostics.

## WAV admission — FROZEN

Accept only RIFF/WAVE PCM readable by Python `wave` with:

- compression type exactly `NONE`;
- channels integer `1..8`;
- sample rate `8000..192000` Hz;
- sample width exactly `1`, `2`, `3`, or `4` bytes;
- frame count > 0.

Reject unsupported/corrupt WAV fail-closed with `ValueError`.

## PCM decode — FROZEN

Decode little-endian PCM per channel:

- 8-bit: unsigned, zero-centered by subtracting 128, scale 128;
- 16-bit: signed little-endian, scale 32768;
- 24-bit: signed little-endian with explicit sign extension, scale 8388608;
- 32-bit: signed little-endian integer PCM, scale 2147483648.

Values are clamped to `[-1,1]` after decode.

## Full-mixture downmix — FROZEN

For rhythmic structure, avoid destructive stereo phase cancellation.

For each source PCM frame:

```text
frameMagnitude = mean(abs(channelSample)) across all channels
```

This is explicitly a **full-mixture energy-preserving downmix**, not a separated source and not a musical-note feature.

## Bounded analysis-rate envelope — FROZEN

Target analysis rate: **4000 Hz**.

Do not create a signed resampled waveform. Instead create an energy-preserving mono amplitude envelope:

- map source frames into consecutive target-rate time bins;
- each output sample = RMS of `frameMagnitude` values in that bin;
- output sample count is approximately duration * 4000;
- empty bins, if any, repeat the previous envelope value, starting from 0.

This keeps Phase 5 memory bounded while preserving transient energy better than signed averaging/decimation.

For source sample rate already <= 4000 Hz, preserve one envelope value per source frame and report the actual output rate as the source rate. Current admitted minimum is 8000 Hz, so normal admitted files use 4000 Hz.

## Chunked IO — FROZEN

Read WAV frames in chunks of **16384 source frames**. The adapter must not call `readframes(total_frame_count)` for the whole file.

## Phase 5 call — FROZEN

Call only:

```python
estimate_full_mixture_structure_v1(envelope_samples, envelope_sample_rate)
```

Do not call Basic Pitch, V34 event diagnostics, V143 carrier logic, separation, or any scorer.

## Adapter diagnostics — FROZEN

Add under `diagnostics.wavAdapter`:

- `version=1`;
- `sourceChannels`;
- `sourceSampleRate`;
- `sourceSampleWidthBytes`;
- `sourceFrameCount`;
- `sourceDurationSeconds`;
- `envelopeSampleRate`;
- `envelopeSampleCount`;
- `downmix="mean-absolute-channel-energy"`;
- `envelope="target-bin-rms"`;
- `chunkFrames=16384`;
- `fullMixtureOnly=true`;
- `separatedCarrierUsed=false`;
- `transcribedEventInputUsed=false`.

The Phase 5 provenance object itself remains unchanged: `full-mixture`, `request-audio`, reference blind, no reference runtime input.

## Frozen synthetic tests — W1–W10

W1. Deterministic mono 16-bit PCM WAV at 44.1 kHz, 120 BPM clicks -> tempo within 1 BPM.

W2. Deterministic stereo 16-bit PCM WAV, clicks in both channels -> tempo within 1 BPM.

W3. Opposite-polarity stereo clicks -> tempo still resolves near 120 BPM, proving no destructive signed stereo cancellation.

W4. Stereo accented 4/4 WAV -> time signature resolves 4/4.

W5. Stereo one-beat-pickup 4/4 WAV -> pickup within 0.15 beat.

W6. 8-bit PCM decode path -> 120 BPM tempo resolves within tolerance.

W7. 24-bit PCM decode path -> 120 BPM tempo resolves within tolerance.

W8. 32-bit integer PCM decode path -> 120 BPM tempo resolves within tolerance.

W9. Invalid/non-WAV or unsupported admission fails closed.

W10. Adapter diagnostics/provenance: full-mixture only, 4000 Hz bounded envelope, no carrier/event/reference use; route/runtime remains disconnected.

All WAVs are generated deterministically inside the verifier. No external audio assets.

## Integration boundary

Phase 6 must not modify `/api/analyze-audio-tab`, Modal analyzers, V143 endpoint selection, PDF routes, Product output or Production.

It creates a reusable file adapter only. A later separately frozen analyzer-runtime shadow wiring phase may call this adapter on the already-normalized full-mixture WAV **before any separation/carrier-specific interpretation**, but Phase 6 itself does not.

## Safety accounting

- reference score calls = 0;
- external audio assets = 0;
- GuitarSet read = false;
- SplitMySong read = false;
- GOAT restricted bytes read = false;
- separated carrier used = false;
- transcribed events used = false;
- Modal invoked = false;
- GPU used = false;
- route/runtime estimator connected = false;
- Product/PDF modified = false;
- Production modified = false;
- Production promotion authorized = false.

## Success meaning

A W1–W10 pass proves that real PCM WAV bytes can be converted into bounded full-mixture rhythmic envelope input for Phase 5 according to this fixed contract. It does not prove real-song transcription accuracy and does not authorize runtime/Product connection.
