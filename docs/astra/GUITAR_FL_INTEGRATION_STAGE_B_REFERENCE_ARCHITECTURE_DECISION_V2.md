# Guitar-FL Stage B hardware/reference architecture decision V2

Date: 2026-10-06  
Branch: `astra-work`  
Status: **FROZEN PRE-CAPTURE DECISION — NO PROCUREMENT, CONTACT, CALIBRATION RECORDING, OR HOLDOUT CAPTURE AUTHORIZED**

## Decision

Stage B will evaluate **clean magnetic-guitar DI only**. Authoritative reference truth is physically independent of evaluated audio and has two required planes:

1. **String/fret-state truth:** six-string physical state sensing that deterministically identifies open/fretted state and fret position.
2. **Excitation/event-birth truth:** independent per-string physical excitation sensing capable of preserving repicks/rearticulations and event-birth timing.

The reference decoder may read only the physical reference planes and their hardware clock/sync evidence. It may not read evaluated DI, spectrograms, Basic Pitch outputs, `guitar-fl.pth` outputs, downstream fretboard output, or correctness metrics.

## Clock decision

Authoritative timing must use one of exactly two preregistered topologies:

- **Preferred V1 topology:** one shared hardware acquisition clock for DI, six fret-state channels, and six excitation channels.
- **Permitted fallback topology:** separate clocks only when a hardware-sync mapping is frozen before holdout capture, hash-bound in the capture plan, and derived solely from immutable hardware sync markers visible to the participating capture systems.

Forbidden timing derivations include waveform cross-correlation, audio onset detection, spectrogram alignment, DTW to DI, transcription/model activation alignment, and manual waveform nudging.

The currently preferred concrete hardware class remains the previously frozen 16-input / 48 kHz / 24-bit shared-ADC architecture. This decision does **not** authorize purchasing it.

## Population and anti-inflation semantics

The frozen holdout contains at least six performers and exactly the five preregistered categories: `chords`, `scales`, `singlenotes`, `techniques`, and `music`.

A single underlying performance may have three synchronized views (evaluated DI, string/fret truth, event-birth truth), but those views count as **one** admitted performance. `populationId` and `underlyingPerformanceId` must be unique across admitted holdout slots. Calibration population identities and holdout identities must be disjoint.

The preregistered minimums remain unchanged: at least two admitted performances per performer/category cell, at least 60 admitted performances total, at least 3,000 pooled independent reference note births, at least 300 per performer, and at least 400 per category.

## Admission semantics

For each frozen slot, the first take that passes preregistered objective transport/acquisition validity is irrevocably admitted. A later take may not replace it because of playing quality, sparse/extra reference events, model disagreement, unattractive output, or any later correctness observation. Multiple admitted takes for one slot are forbidden.

## Rights binding

No capture session can be authorized until every performer and content item resolves through the frozen rights manifest to stable document IDs and SHA-256 digests. Required rights include performer recording/product-validation permission, recording ownership/use grant, reference-sensor-data use, composition/content provenance, product-validation use, and protected-song exclusion.

## Fail-closed synthetic gate

`scripts/songsterr-fresh/guitar_fl_stage_b_precapture_validator_v2.py` must reject at minimum:

- duplicate population identities;
- calibration/holdout leakage;
- multiple-view inflation via duplicate underlying-performance identity;
- missing or broken rights-document linkage;
- missing independent reference-plane or clock/sync hashes;
- invalid role labels;
- any later admitted take after the first transport-valid take;
- any violation of the preregistered performance or note-birth floors;
- any attempt to enable spending, procurement, contact, calibration recording, capture, inference, or reference scoring authority.

## Preserved boundary

This packet performs no vendor or performer outreach, spending, procurement, recording, real inference, real reference decoding, Stage-B scoring, threshold tuning, fretboard/quantization/role changes, Production change, or `main` modification. Product/customer use of `guitar-fl.pth` remains independently blocked pending the François-Leduc checkpoint-training-lineage rights review.
