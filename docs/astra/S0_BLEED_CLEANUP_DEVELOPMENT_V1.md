# S0 Bleed Cleanup Development Result V1

Date: 2026-10-02
Branch: `astra-work`
Status: **CLEANUP MATH IMPLEMENTED + SYNTHETIC UNIT TEST PASSED**

## What was built

- `astra_backend/evaluation/stem_bleed_cleanup_v1.py`
- `astra_backend/evaluation/evaluate_s0_bleed_cleanup_v1.py`
- `astra_backend/evaluation/separator_adapter_v1.py`

The cleaner performs soft cross-stem time-frequency competition. It never hard-zeros a target bin. The current conservative configuration is:

- FFT: 2048
- hop: 512
- magnitude power: 2.0
- competing-stem weight: 0.50
- minimum retained gain: 0.60

An exact residual is retained so cleaned stems + residual reconstruct the input mixture.

## Development test

Test source:
- all 12 frozen S0 mixtures;
- exact ground-truth stems;
- deterministic symmetric cross-stem contamination injected at **-18 dB**;
- no learned separator involved.

Result:
- mixtures evaluated: **12**
- all 12 improved: **yes**
- mean SI-SDR improvement: **+2.665 dB**
- worst mixture improvement: **+1.175 dB**
- maximum mixture reconstruction absolute error after adding residual: **5.96e-08**

The earlier more aggressive cleanup configuration harmed several mixtures. It was rejected. The current conservative configuration was retained because every S0 mixture improved under this unit-test contamination model.

## What this proves

It proves only that:
- cross-stem competition code works;
- known injected bleed can be reduced without hard muting;
- the conservative setting improved all 12 current S0 unit-test mixtures;
- the residual path preserves mixture consistency to floating-point precision.

## What this does not prove

It does not prove:
- any real separator produces this kind of bleed;
- the same improvement occurs on separator outputs;
- commercial-song isolation quality;
- note-transcription improvement;
- perceptual superiority;
- guitar/bass full-song readiness.

## Separator integration

`separator_adapter_v1.py` defines an immutable identity contract:
- separator name/version;
- repository revision;
- checkpoint SHA-256;
- rights/license basis.

The default adapter is disabled and refuses execution.

The next empirical step is to plug in exactly one rights-cleared separator, produce S0 estimated stems, and evaluate raw separator output vs cleaned output against the exact S0 ground truth. Cleanup settings should remain frozen for that first comparison.
