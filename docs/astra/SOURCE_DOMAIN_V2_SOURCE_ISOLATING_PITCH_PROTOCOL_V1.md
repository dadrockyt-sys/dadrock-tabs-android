# Astra V2 source-isolating pitch-preservation protocol V1

Date: 2026-09-28  
Status: **PROSPECTIVE DIAGNOSTIC DESIGN FROZEN — NO EXECUTION YET**

## Purpose

Correct the measurement defect identified in the frozen Stage-A V2 fundamental-preservation gate without changing the scientific source-domain configuration.

The original Stage-A result remains failed under its original mixed-waveform estimator.

This protocol defines a separate model-free diagnostic to answer the narrower question:

> For every attacked note in the frozen Stage-A sample, does the deterministic V2 note-generation path preserve that note's fundamental within ±15 cents when measured without simultaneous-note interference?

## What does not change

This protocol does not change:
- V2 manifest content;
- selected Stage-A rows;
- clip-level parameter values;
- categorical assignments;
- per-note parameter distributions;
- waveform synthesis equations;
- CQT frontend;
- labels/references/timing;
- the ±15-cent tolerance;
- Stage-B gates;
- model architecture/loss/sampler/thresholds;
- P1/P2/P3 policy.

No model is loaded or run.

## Why a new diagnostic is required

The frozen mixed-waveform helper searches a broad target-relative FFT band and selects the strongest peak.

In chords, simultaneous note fundamentals or harmonics can occupy that band and be selected instead of the target event.

A valid per-note pitch-preservation check therefore needs source isolation.

## Frozen diagnostic sample

Use exactly the same **28 Stage-A V2 manifest rows**:
- train local positions 0 and 29 in each family;
- primary-challenge local positions 0 and 5 in each family.

Probe every attacked event in those rows.

Do not substitute rows.

Expected attacked-event count is fixed from the frozen Stage-A result:
- **86 measurable attacked events** in the original mixed-waveform review.

Negative-only rows have no attacked probes.

## Isolated diagnostic probe construction

For each attacked event:

1. Reconstruct the exact frozen Stage-A row context:
   - family;
   - row index;
   - effective template;
   - variant;
   - V2 manifest clip-level overrides;
   - historical S9 chord-template handling when applicable.

2. Reuse the exact V1/V2 per-note deterministic substreams for the original event index:
   - note rise multiplier;
   - note damping multiplier;
   - note amplitude multiplier;
   - component RNG.

3. Generate **only that one note component** using the same:
   - pitch;
   - event duration;
   - damping;
   - pick position;
   - brightness;
   - attack rise;
   - transient gain/decay;
   - soft/palm semantics.

4. Place that component at the same absolute event start in a 2-second silent clip.

5. Apply the same clip-level deterministic post chain:
   - high-pass / low-pass / spectral tilt;
   - nonlinear transform using the same active/drive/wet settings;
   - broadband-noise and hum settings from the exact row;
   - fixed body filter;
   - final peak normalization;
   - 44.1 kHz to 22.05 kHz polyphase resampling;
   - final peak guard.

This probe changes **only source multiplicity**: one event is isolated so no other musical note can compete in the estimator.

It does not alter that event's own source parameters.

## Pitch estimator

Measure the isolated probe in the same stable-sustain window rule used by Stage A:
- start = min(event end - 40 ms, event start + 100 ms);
- end = min(event end, start + 120 ms).

Use the same frozen FFT estimator:
- Hann window;
- zero-padding to next power-of-two >= 4× signal length;
- target band 0.85× .. 1.15× expected frequency;
- strongest peak in band;
- report cents relative to expected pitch.

Because only one musical note is present, the estimator's original single-source assumption is now satisfied.

## Hard diagnostic admission

All must pass:

1. deterministic isolated rerender:
   - every probe byte-identical across two renders;

2. finite and bounded:
   - no nonfinite values;
   - final peak < 0.999;

3. event identity:
   - exact original row/event index and expected MIDI pitch recorded;
   - exact clip-level manifest parameters hash back to the frozen manifest;

4. source isolation:
   - exactly one musical note component is generated per probe;
   - no other labeled musical event is present;

5. pitch preservation:
   - every measurable attacked-event isolated probe is within **±15 cents**;
   - required pass count = all measurable attacked probes;

6. no silent omission:
   - every attacked event that was measurable in the original Stage-A result must produce a measurable isolated diagnostic result.

No tolerance relaxation is allowed.

## Additional non-gating comparison

For auditability, report:
- original mixed-waveform cents from frozen Stage A;
- isolated-probe cents;
- absolute change in measurement error;
- family/kind/row/event.

The comparison is descriptive only.

## Execution ceilings

This diagnostic is not a Stage-A rerun.

Hard ceilings:
- attacked-event probe renders: <= **172** (86 events × two deterministic renders);
- 2-second synthetic probe audio: <= **344 seconds**;
- CPU only;
- wall time <= **20 minutes**;
- persisted result <= **100 MB**;
- model loads 0;
- inference false;
- optimizer steps 0;
- threshold work false;
- P1/P2/P3 access false;
- automatic retry false;
- main/Production mutation false.

## Failure handling

If any isolated probe exceeds ±15 cents:
- freeze the failure;
- do not alter the threshold;
- do not rerun automatically;
- review the exact source/post-processing path before any Stage-A replacement design.

If every isolated probe passes:
- this establishes that the original Stage-A pitch-gate failure was measurement-confounded for polyphony;
- it does **not** retroactively convert the original Stage-A run into a pass;
- a separately versioned Stage-A admission design may then replace only the pitch measurement method while preserving every other gate and sample.

## Decision

**GO for one bounded source-isolating diagnostic implementation/execution after package verification.**

No Stage-A rerun and no Stage B/model work is authorized by this protocol.
