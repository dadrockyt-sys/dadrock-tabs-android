# Astra V2 corrected Stage-A adjudication design V1

Date: 2026-09-28
Status: **PROSPECTIVE ZERO-RENDER ADJUDICATION DESIGN**

## Purpose

Define a new Stage-A admission version that corrects only the invalid polyphonic per-note pitch measurement while preserving the original Stage-A scientific configuration.

The original Stage-A run remains failed under its original contract and is not rewritten.

## Frozen evidence inputs

Original Stage-A execution:
- result path: `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_RESULT_V1.json`
- workflow run 36484128430
- artifact 10997847232
- full result JSON SHA-256 `5778104fe505f5a38b4e2a0ed3e049a9993db92a9a1a3a078851c6cb7df8e0c2`

Measurement-validity review:
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_MEASUREMENT_VALIDITY_REVIEW_V1.json`

Source-isolating pitch diagnostic:
- `docs/astra/SOURCE_DOMAIN_V2_SOURCE_ISOLATING_PITCH_RESULT_V1.json`
- workflow run 36488106137
- artifact 10999874443
- result JSON SHA-256 `3e3cc594a58a9ab29ae9dbbed8bf1f3107b71b9e2076e3b25e7924b031cf5561`

## Corrected gate mapping

Retain every original Stage-A gate exactly except the invalid mixed-waveform pitch gate.

Required original Stage-A gates:
- deterministic rerender identity = true;
- state identity = true;
- onset identity = true;
- reference identity = true;
- finite audio/features = true;
- final peak under 0.999 = true;
- no unlabeled transient injection = true;
- prepared-CQT changed for every positive selected row = true;
- manifest binding exact = true;
- selected rows exact = true;
- render ceiling = true;
- audio-seconds ceiling = true;
- wall-time ceiling = true.

Replace only:
- original `fundamentalWithin15Cents` mixed-waveform result

with:
- source-isolating diagnostic `allIsolatedMeasurableWithin15Cents = true`;
- all original 86 measurable attacked events retained;
- no missing isolated measurement;
- tolerance remains exactly ±15 cents.

## No new rendering

This adjudication performs:
- waveform renders 0;
- synthetic audio seconds 0;
- model loads 0;
- optimizer steps 0;
- threshold work 0;
- P1/P2/P3 access 0.

It reads only frozen result JSON and checks identities/gates.

## Pass condition

Corrected Stage-A V2 admission passes iff:
1. all retained original Stage-A gates are true;
2. the source-isolating diagnostic passed;
3. all 86 original measurable attacked events were retained;
4. zero isolated attacked events exceeded ±15 cents;
5. frozen control/manifest identities match across both evidence packages.

No gate may be relaxed.

## Meaning

A pass establishes that the frozen V2 Stage-A sample satisfies the intended acoustic admission contract after correcting the validated polyphonic measurement defect.

It does not:
- rewrite the historical original Stage-A failure;
- prove Stage-B coverage;
- authorize model training;
- authorize P1/P2/P3.

A pass permits only the already-prospective model-free Stage-B preparation/coverage evaluation.

## Decision

GO for one zero-render corrected Stage-A adjudication.
