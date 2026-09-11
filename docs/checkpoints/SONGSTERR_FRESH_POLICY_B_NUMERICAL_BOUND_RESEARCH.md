# Songsterr Fresh — Policy B Numerical Boundary Research

Updated: 2026-09-10 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: reference-blind model-evidence validation only. Duration/release work remains paused.

## Question

Can the fresh pipeline justify an onset decision uncertainty boundary independently of the observed A/B/C fixture, so that a threshold-boundary Basic Pitch inventory toggle can be admitted or rejected without fitting a tolerance to the current sample?

## Current finding

**No justified end-to-end numerical admission bound was found.**

The current A/B/C evidence remains measurement evidence only. The B-only MIDI-55 event is a proven Basic Pitch `threshold-onset-pass` toggle, but neither its observed threshold margins nor any package regression tolerance is sufficient to define an admission band for the full Demucs → Basic Pitch chain.

`modelValidationComplete` must remain `false`. Customer-eligible events remain 0. Duration research remains paused.

## Evidence reviewed

### 1. Basic Pitch v0.4.0 decoder semantics have a hard threshold, not an uncertainty band

Spotify Basic Pitch v0.4.0 `basic_pitch/note_creation.py`:

- inferred onsets are combined with predicted onsets;
- strict local maxima are found with `scipy.signal.argrelmax`;
- threshold-onset candidates are selected with `np.where(peak_thresh_mat >= onset_thresh)`;
- the default onset threshold used by `predict()` is 0.5.

Source:
- https://github.com/spotify/basic-pitch/blob/v0.4.0/basic_pitch/note_creation.py
- https://github.com/spotify/basic-pitch/blob/v0.4.0/basic_pitch/inference.py

Implication: a dead-band around 0.5 would be a new pipeline admission policy. It is not part of Basic Pitch v0.4.0 decoder semantics.

### 2. Spotify's v0.4.0 tests use `atol=1e-4`, but this is a regression-test tolerance

Spotify Basic Pitch v0.4.0 `tests/test_inference.py` compares the `vocadito_10.wav` expected model-output arrays and expected note events with:

`np.testing.assert_allclose(..., atol=1e-4, rtol=0)`

Source:
- https://github.com/spotify/basic-pitch/blob/v0.4.0/tests/test_inference.py

The v0.4.0 GitHub Actions test matrix runs the test suite on Ubuntu and Windows across Python 3.8–3.11, plus macOS Python 3.10.11/3.11.8.

Source:
- https://github.com/spotify/basic-pitch/blob/v0.4.0/.github/workflows/tox.yml

This is useful independent evidence that the project itself allows small numerical regression differences for a fixed test fixture. It is **not** documented as a worst-case error guarantee for arbitrary inputs, arbitrary model activations, or downstream decoder inventory.

Therefore `1e-4` must not be imported as a fresh-pipeline admission tolerance.

### 3. Basic Pitch v0.4.0 can use different inference runtimes by platform

The v0.4.0 package declares `tflite-runtime` for Linux with Python <3.11, TensorFlow for non-Darwin Python >=3.11, and other platform-specific runtimes are supported by the package.

Source:
- https://github.com/spotify/basic-pitch/blob/v0.4.0/pyproject.toml

The current fresh canary uses Linux/Python 3.10, so Basic Pitch follows the TFLite path. The package-level multi-platform regression test does not establish a universal per-activation error bound across all supported runtime implementations.

### 4. The upstream Demucs stage is PyTorch-based and PyTorch does not provide the required cross-platform reproducibility guarantee

PyTorch's official reproducibility documentation states that completely reproducible results are not guaranteed across releases, individual commits, or different platforms. Its deterministic guidance is scoped to controlled software/hardware conditions rather than an arbitrary cross-host numerical error envelope.

Source:
- https://docs.pytorch.org/docs/stable/notes/randomness.html

This matters because Basic Pitch does not receive a fixed canonical tensor in the fresh pipeline; it receives a Demucs-produced guitar stem. A Basic Pitch-only regression tolerance cannot bound perturbations introduced upstream by the separator.

### 5. TensorFlow determinism guidance does not supply a cross-hardware error bound

TensorFlow's official determinism API documentation requires the same hardware configuration and same software environment for deterministic guarantees, and notes determinism is not guaranteed across TensorFlow versions.

Source:
- https://www.tensorflow.org/api_docs/python/tf/config/experimental/enable_op_determinism

This does not provide the missing arbitrary-host activation-error bound for the fresh pipeline.

### 6. XNNPACK has a consistency mode, but its scope is narrower than the needed contract

XNNPACK exposes `XNN_FLAG_SLOW_CONSISTENT_ARITHMETIC`, described as attempting numerically consistent results from a **specific build of XNNPACK** by avoiding codepaths inconsistent with other codepaths in that same compiled library.

Source:
- https://github.com/google/XNNPACK/blob/master/include/xnnpack.h

Basic Pitch v0.4.0's normal TFLite model loading path does not establish that this mode is enabled, and even that flag is not an end-to-end Demucs → Basic Pitch cross-platform error guarantee.

## Why machine epsilon is not enough

A bound based only on float32 machine epsilon would not be justified. The threshold is applied after a long numerical chain: audio decoding/resampling, Demucs neural inference, model serialization/runtime kernels, Basic Pitch inference, window concatenation/unwrapping, inferred-onset differencing/rescaling, and local-maximum selection.

Without an independently established forward-error/Lipschitz bound for that chain, machine epsilon cannot be converted into a valid maximum activation error at the decoder's 0.5 threshold.

## Policy conclusion

Policy B currently has **no independently justified numerical admission contract** for threshold-boundary inventory toggles across the supported fresh execution environments.

The following are explicitly insufficient as admission bounds:

- A/B/C observed threshold margins;
- observed matrix maxima or current min/max envelope;
- Spotify's `1e-4` fixture regression tolerance;
- float32 machine epsilon alone;
- one-frame or current 7/20-frame decoder span differences;
- CPU/vendor identity;
- exact output hashes;
- historical frequency/event count;
- candidate confidence;
- downstream agreement;
- reference/professional tabs or archived V143/Gomyway scoring.

## Engineering consequence

Until a separately justified end-to-end numerical contract exists, a semantic inventory toggle at the Basic Pitch threshold remains unresolved model-evidence variation. It must keep `MODEL_EVIDENCE_VALIDATION_PENDING` active rather than being absorbed by a fitted tolerance.

Future independent canaries should continue to collect exact decoder traces through `.github/workflows/songsterr-fresh-decoder-trace-followup.yml`. Those observations may characterize mechanism and frequency, but additional samples alone do not create an admission tolerance.

The archived V143/Gomyway pipeline remains out of scope unless explicitly requested.
