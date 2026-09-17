# BLOCKER — Songsterr Fresh EGSet12 Authorized Execution Pre-Media Gate

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Frozen PRE: `docs/checkpoints/SONGSTERR_FRESH_EGSET12_REAL_EVALUATION_PRE.md`
Frozen PRE commit: `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a`
Execution-confirmation authority: user instruction `Please continue 💚`
Preflight parent head: `35e3cab66068e918544535af5e9ecb60d7b54bec`

Status: **BLOCKED_PRE_MEDIA_AUDIO_PREPARATION_UNFROZEN / NO EGSET12 MEDIA OPENED / NO MODEL OUTPUT / NO SCORE**

## 1. AUTHORIZATION NOW RECORDED

The user's `Please continue 💚` instruction arrived after PRE `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a` had been frozen and explicitly presented as the post-PRE execution boundary. It is therefore recorded as the required post-freeze confirmation for the exact intended action described by that PRE: EGSet12 v1 / Zenodo record `11406378`, provenance preflight, exact prior Songsterr-fresh Basic Pitch identity, one raw-proposal run per track, exact frozen `S AND E AND O AND K` qualification, frozen note-birth scoring, and immutable first-result recording.

This confirmation does not authorize changing the PRE after observing real/model output, resuming V143/Gomyway, changing Production, or silently inventing preprocessing that was not prospectively frozen.

## 2. PRE-MEDIA BASIC PITCH IDENTITY RECOVERED

Before opening any EGSet12 media, the prior Songsterr-fresh proposal-generation lineage was reconciled to the immutable successful EGFxSet proposal run:

- source run: `34936227380`, attempt 1;
- workflow: `.github/workflows/songsterr-egfxset-repaired-one-shot.yml`;
- workflow head: `b37d400b186a926985bb16b91702e2f88e55d785`;
- Python: `3.10.21`;
- NumPy: `1.26.4`;
- `tflite-runtime`: `2.14.0`;
- `basic-pitch`: `0.4.0`;
- exact transcription script: `scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py`;
- historical script Git blob: `e9137496363f14cbe6194e32304c8b17b0b6569c`;
- current branch script Git blob: `e9137496363f14cbe6194e32304c8b17b0b6569c` — unchanged;
- model call: `basic_pitch.inference.predict()` exactly once per input;
- frozen decoded-note range: MIDI `40..88`;
- onset threshold: `0.5`;
- frame threshold: `0.3`;
- minimum note length: `127.7 ms`;
- `multiple_pitch_bends=False`;
- `melodia_trick=True`;
- input path is passed directly to Basic Pitch; no Songsterr-fresh wrapper resampler/channel transform is applied before `predict()`;
- decoded proposal ordering/IDs are deterministically reissued after sort by onset, MIDI, and diagnostic model end.

A later execution harness could still record the installed Basic Pitch default model-file path/hash before inference, as required by the PRE when available. No inference or model output was opened during this reconciliation.

## 3. FROZEN POSITIVE-CORE DSP SAMPLE GRID

The candidate method is not only the Boolean composer. Its frozen KKT/support dependency reaches the unchanged V6 onset-innovation implementation:

- positive-core composer: `scripts/songsterr-fresh/v7_fail_closed_positive_core_v1.py`, frozen blob `6174a95c14a58ddd4dca47f021e591ebee8ee736`;
- KKT diagnostic: `scripts/songsterr-fresh/v7_kkt_raw_necessity_diagnostics_v1.py`, frozen blob `2daa9f7f6983a3ec894fc08a86e9bced7b1f96c4`;
- V6 onset-birth dependency: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, frozen blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.

The V6 dependency hard-freezes:

- `SAMPLE_RATE = 44100`;
- `FFT_SIZE = 8192`;
- onset framing and frequency grid derived from that `44100 Hz` constant.

The positive-core/KKT API accepts an audio sample array and onset sample index; it does not accept a runtime sample-rate argument and it contains no native-rate conversion path.

## 4. EGSET12 OFFICIAL RATE CONFLICT

The official EGSet12 v1 record describes the twelve recordings as captured at an **original sampling rate of 48000 Hz**, with stereo channels that are copies of each other (effectively mono).

Therefore the exact official WAV bytes frozen by PRE `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a` cannot be passed directly into the frozen positive-core DSP while preserving the DSP's `44100 Hz` time/frequency interpretation.

At least two preparation decisions are required before the frozen qualifier can be applied correctly:

1. the exact deterministic `48000 -> 44100 Hz` resampling algorithm, filter/window/padding and numeric implementation;
2. the exact stereo-to-mono/channel-selection rule before the DSP array is constructed.

Those decisions can change samples, onset indices and spectral evidence and therefore are part of the evaluated method, not harmless file plumbing.

## 5. WHY THE FROZEN PRE CANNOT SILENTLY FILL THIS GAP

PRE `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a` freezes the official WAV/JAMS identities and requires canonical audio/model/runtime preparation, but it does **not** freeze an EGSet12 `48000 -> 44100` qualifier preparation algorithm, implementation identity, filter/window, padding convention, rounding rule, output-length rule, or channel-collapse rule.

Its model-identity section requires the exact prior Basic Pitch audio decode/resampling/channel preprocessing to be recovered. That prior proposal path is recoverable and passes the native WAV path directly to Basic Pitch. It does not define the separate 44.1 kHz in-memory array required by `S AND E AND O AND K`.

Selecting `scipy.signal.resample_poly`, FFmpeg, librosa, another resampler, channel 0, channel averaging, or any other transformation now would be a new post-freeze method choice. Because the real corpus has not been opened, this can be repaired prospectively — but only in a new PRE/iteration before media access.

## 6. FAIL-CLOSED DECISION

Execution of PRE `2a2ed0e4b009f8cd96ba0bc18b384441f53ce87a` stops **before EGSet12 media access** with:

`BLOCKED_PRE_MEDIA_AUDIO_PREPARATION_UNFROZEN`

No EGSet12 WAV was downloaded/opened by the Songsterr-fresh execution path.
No EGSet12 JAMS annotation was opened for correctness.
No Basic Pitch inference was run on EGSet12.
No positive-core qualifier was run on EGSet12.
No prediction, per-track score or aggregate score was revealed.
No threshold, exclusion, rescue, candidate rule or model behavior was changed.

The untouched-lineage historical provenance scan was not consumed as an evidence-producing run; the earlier repository-surface search still showed no known pre-PRE EGSet12 Songsterr-fresh exposure, but a future executable iteration must retain the PRE's full fail-closed history preflight before media access.

## 7. NEXT SCIENTIFICALLY PERMITTED BOUNDARY

A successor prospective PRE may be written **without opening EGSet12 media** to freeze only the missing preparation boundary while preserving every already-frozen evaluation rule. It must at minimum freeze:

- exact `48000 -> 44100 Hz` resampling implementation and version;
- exact rational conversion/filter/window/padding parameters;
- exact output sample-count/onset-index rounding semantics;
- exact stereo duplicate-channel validation and mono selection/collapse rule;
- deterministic synthetic/non-EGSet12 mechanical tests for the preparation adapter;
- binding to unchanged Basic Pitch `0.4.0` proposal identity and unchanged positive-core blobs;
- unchanged official 24 file hashes, event population, 50 ms note-birth matching, abstention treatment, metrics, reveal policy, and no-post-hoc-tuning rule.

After such a successor PRE is frozen, the existing `Please continue 💚` instruction must not be silently carried across as post-freeze authorization for the new exact preparation method. Present the new PRE/corpus/action and obtain a new post-freeze confirmation before opening EGSet12 media.

## 8. UNCHANGED GLOBAL AUTHORITY

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

`main`, Production, protected-song work, blocked temporal work, and archived V143/Gomyway remain untouched.
