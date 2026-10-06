# Guitar-FL Stage B pre-capture hardware + acquisition QA V1

Date: 2026-10-06
Status: **FROZEN ENGINEERING CLASS / NO PROCUREMENT OR CAPTURE AUTHORIZED**

## Hardware classes

No vendor/product is selected.

### Plane A — evaluated DI
- clean magnetic guitar DI
- mono, 48 kHz, 24-bit PCM
- captured on the authoritative shared-clock multichannel acquisition device
- no effects, amp/cab, denoise, separation, normalization, or post-processing

### Plane B — physical pitch/string-fret identity
- six-string physical fret-contact matrix (resistive/capacitive/contact-state class)
- reports string + open/fretted state + fret index without deriving pitch from Plane-A audio
- timestamped from the same authoritative acquisition clock
- minimum scan rate: **1000 Hz**

### Plane C — independent event birth
- six independent bridge/body excitation sensors, one per string (piezo/force/acceleration class)
- raw sensor waveform or edge stream retained
- captured/timestamped by the same authoritative acquisition clock
- if waveform: **48 kHz minimum**
- no Plane-A waveform is an input to event-birth detection

### Shared clock
V1 requires **one authoritative hardware acquisition clock** across A/B/C.
Separate-clock fallback is not admitted in V1. This deliberately eliminates post-hoc drift fitting.

## Frozen acquisition-QA thresholds

These are transport/device-health rules only; they may never inspect model correctness or musical desirability.

1. Required channels/files present: **100%**
2. Plane-A sample rate: **exactly 48,000 Hz**
3. Plane-A bit depth: **24-bit PCM**
4. Plane-A clipped samples at full scale: **0**
5. Plane-B scan rate: **>= 1000 Hz**
6. Plane-B maximum timestamp gap: **<= 2.0 ms**
7. Plane-B malformed/unknown string-fret states: **0 at transport/schema layer** (semantic conflicts are structural-audit failures, not retake reasons)
8. Plane-C per-string channel presence: **6/6**
9. Plane-C timestamp/sample gaps: **0 missing authoritative clock frames**
10. Plane-C full-scale clipped samples: **0**
11. Shared authoritative frame counter: strictly monotonic, **0 gaps / 0 duplicates**
12. configuration/calibration/firmware identities: exact preregistered match
13. raw source SHA-256 generation: required for every A/B/C/clock artifact
14. any required artifact failing byte-integrity verification: acquisition QA fail

## Allowed acquisition-QA failure codes

- MISSING_REQUIRED_CHANNEL
- WRONG_AUDIO_FORMAT
- FULL_SCALE_CLIPPING
- REFERENCE_SCAN_RATE_TOO_LOW
- REFERENCE_TIMESTAMP_GAP_EXCEEDED
- REFERENCE_STREAM_MALFORMED
- EXCITATION_CHANNEL_MISSING
- AUTHORITATIVE_CLOCK_GAP
- AUTHORITATIVE_CLOCK_DUPLICATE
- CONFIGURATION_IDENTITY_MISMATCH
- CALIBRATION_IDENTITY_MISMATCH
- FIRMWARE_IDENTITY_MISMATCH
- MISSING_OR_CORRUPT_FILE

Only these objective failures may permit another attempt for the same frozen slot.

## Not acquisition-QA failures

Wrong notes, messy playing, hard techniques, low event count, model disagreement, poor transcription score, unusual but valid sensor states, and reference-decoder ambiguity are never retake reasons.

## Boundary

No purchase, rental, vendor/performer contact, calibration recording, holdout capture, model inference, or scoring is authorized.
