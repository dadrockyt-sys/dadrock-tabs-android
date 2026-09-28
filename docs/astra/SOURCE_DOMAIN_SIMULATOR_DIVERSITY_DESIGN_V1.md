# Astra source-domain simulator diversity design V1

Date: 2026-09-28  
Status: **PROSPECTIVE MODEL-FREE DESIGN FROZEN — NO TRAINING / NO LAUNCH**

## Purpose

Define one waveform-level synthetic source-domain diversity package that broadens the repo-owned procedural guitar simulator **before** the frozen CQT frontend.

This design follows:
- successful frozen P1/P2 integrity audit V2;
- failed S12 feature-space robustness intervention;
- failed S13 feature-space robustness intervention;
- corrected simulator/representation strategy review V2.

The package is intended to test whether broader source-domain variation can be represented without corrupting labels. It is **not** fit to the eight exposed P1/P2 examples and is not claimed to reproduce any one performer, guitar, pickup, interface, room, or amplifier.

## Boundary

This document authorizes no model execution.

During V1 implementation/review:
- P1/P2 media remain closed;
- P3 remains sealed;
- optimizer steps = 0;
- models loaded = 0;
- model inference = false;
- thresholds remain 0.50 / 0.50;
- no decoder, sampler, loss, architecture, or frontend change;
- no main/Production mutation.

## Control

The control remains the frozen S9/S11 procedural path:
- 294 clips;
- seven families: isolated, scales, chords, repeated, legato, palmmute, mixed;
- two seconds per clip;
- deterministic labels/splits/templates;
- frozen 22,050 Hz frontend and CQT preprocessing.

The new package must preserve the same template labels, state/onset targets, references and split identity.

## Single intervention: factorized source-domain randomization package

The intervention is one **joint waveform-generation package**. It varies source/acquisition-like properties at render time, before resampling/CQT.

It is not a menu of separately selected experiments. All ranges below are frozen prospectively as broad engineering priors. No parameter may be changed after seeing P1/P2 outcomes.

### A. Excitation / attack envelope

For each clip, draw one clip-level base attack profile. Each attacked note then receives a small deterministic note-level perturbation around that profile.

Base attack rise time:
- distribution: log-uniform;
- minimum: **0.0015 s**;
- maximum: **0.050 s**.

Per-note multiplier:
- log-uniform from **0.75 to 1.35**;
- final rise time clipped to **0.001 s .. 0.060 s**.

Transient-noise gain relative to existing synthesized harmonic peak:
- uniform **0.00 .. 0.20**.

Transient decay constant:
- log-uniform **0.003 .. 0.020 s**.

Rationale: broaden attack speed and attack/noise contrast without changing event timing or pitch identity.

### B. String/body decay and spectral brightness

Clip-level damping multiplier applied to the existing S0 damping:
- log-uniform **0.60 .. 1.80**.

Existing harmonic-brightness parameter:
- uniform **0.55 .. 0.92**.

Pick-position parameter:
- uniform **0.08 .. 0.48**.

Per-note damping jitter:
- log-uniform **0.85 .. 1.20**.

These ranges are broad source-synthesis priors, not measurements of P1/P2.

### C. Pickup/electrical coloration

Apply one deterministic stable biquad/one-pole coloration chain per clip after note summation and before output normalization/resampling.

Low-pass cutoff:
- log-uniform **2800 .. 12000 Hz**.

Low-shelf / high-shelf tilt surrogate:
- signed first-order spectral tilt parameter corresponding to at most approximately **±6 dB across the modeled guitar band**.

DC blocking/high-pass corner:
- uniform **20 .. 80 Hz**.

The implementation must use a stable deterministic filter and test that pitch fundamentals are not shifted.

### D. Mild nonlinear/compression-like behavior

One clip-level nonlinear wet mix:
- probability active: **0.50**;
- tanh drive if active: uniform **1.0 .. 2.5**;
- wet fraction: uniform **0.00 .. 0.30**.

This is a bounded acquisition/electronics surrogate, not an amplifier model. Hard clipping is forbidden in ordinary intervention generation.

### E. Noise floor / interference surrogate

Additive broadband noise RMS relative to pre-normalization clip RMS:
- log-uniform **1e-5 .. 3e-3**.

Optional low-frequency hum surrogate:
- probability active: **0.35**;
- fundamental: choose deterministically from **50 Hz or 60 Hz** with equal probability;
- include harmonics 2x and 3x at decreasing amplitude;
- combined hum RMS <= **1e-3** of clip RMS.

Noise is independent of labels and may not create labeled attacks.

### F. Source-level dynamic variation

Per-note amplitude multiplier:
- log-normal with sigma **0.18** in log space;
- clipped to **0.55 .. 1.60**.

Clip-level master amplitude is allowed only before the existing frozen RMS normalization and therefore is not itself considered a meaningful diversity axis.

## Deterministic random-number streams

All randomization must be reproducible from SHA-256-derived seeds and must not depend on execution order.

Root namespace:
`astra-source-domain-diversity-v1`

For each clip:
`seed = SHA256(root|templateId|variant|source-domain-v1)`

Independent named substreams:
- `attack`
- `decay`
- `brightness`
- `pickup`
- `nonlinear`
- `noise`
- `dynamics`

Per-note substreams additionally include the event index.

No RNG state may be shared with split creation, label generation, sampler plans or model initialization.

## Dataset identity policy

Model-free preparation must create three deterministic views from the same frozen template/split identities.

### Control
Bit-identical to the frozen S9/S11 source path.

### Intervention
- training rows: source-domain randomization package applied to **all training waveform renders**;
- validation/test rows: bit-identical to control;
- row count unchanged;
- labels/references/split/family/template IDs bit-identical.

Using all training rows avoids another outcome-selected transformed-subset fraction.

### Prospective challenge
- train/validation rows: bit-identical to control;
- test rows only: rendered with a fixed held-out source-domain challenge profile described below;
- all labels/references remain bit-identical.

## Held-out synthetic source-domain challenge V1

Challenge parameters are fixed now and may not be changed after training results.

For every test clip:
- attack rise time base: **0.045 s**;
- per-note rise multiplier: deterministic alternating **0.90 / 1.10** by event index;
- transient-noise gain: **0.03**;
- transient decay: **0.012 s**;
- damping multiplier: **1.45**;
- brightness: **0.60**;
- pick position: **0.42**;
- low-pass cutoff: **3500 Hz**;
- spectral tilt: dark-side fixed tilt equivalent to approximately **-4 dB across modeled guitar band**;
- high-pass corner: **45 Hz**;
- nonlinear drive: **1.8**;
- nonlinear wet fraction: **0.20**;
- broadband noise RMS: **1e-3** of pre-normalization clip RMS;
- hum: **off**;
- per-note amplitude multipliers: deterministic sequence [0.70, 1.00, 1.30, 0.85] repeated by event index.

This is deliberately one fixed, moderately soft/dark acquisition challenge. It is not numerically matched to P1/P2.

## Model-free admission review required before training

Implementation must generate only a small fixed diagnostic fixture set first.

Required fixture families:
1. isolated attacked note;
2. repeated same pitch;
3. scale passage;
4. simultaneous chord;
5. palm-muted repetition;
6. legato event with attack=false transition;
7. negative-only/no-note structure.

For each fixture, save/record:
- exact waveform hash;
- peak amplitude and RMS;
- attack 10%-90% rise-time estimate for attacked events;
- short-window first-difference energy;
- fundamental-frequency estimate at stable sustain;
- harmonic spectral centroid proxy;
- frozen prepared-CQT hash;
- prepared-CQT positive-flux measure;
- state/onset/reference hashes.

Admission criteria:
- deterministic rerender hashes match exactly;
- labels/references are bit-identical to control;
- no nonfinite values;
- ordinary intervention peak magnitude < 0.999 after final output scaling;
- no attack is added where onset label is false;
- attacked-note fundamental estimate remains within **±15 cents** of control during stable sustain;
- intervention attack rise-time fixture span includes at least a **4x** max/min ratio;
- source-domain changes survive frozen CQT preprocessing: at least one of attack flux / spectral centroid / temporal envelope differs from control in each positive fixture;
- negative-only fixture remains unlabeled;
- no split/template identity changes.

Failure of any admission criterion is a design/implementation failure, not permission to tune against P1/P2.

## Challenge identity checks

Before any future optimizer work:
- challenge train/validation waveform/features must equal control exactly;
- intervention validation/test waveform/features must equal control exactly;
- all non-audio/non-feature arrays must match control exactly;
- challenge test labels/references must match control exactly;
- control dataset hashes must match the frozen source path.

## Preparation ceiling

For offline implementation/review only:
- no model loading;
- no optimizer;
- no external/corpus audio;
- no P1/P2/P3 access;
- <= **60** diagnostic fixture renders before full deterministic dataset preparation;
- <= **900** total rendered clips if full model-free intervention/challenge preparation is later performed;
- <= **1,800 synthetic audio seconds** for that preparation;
- <= **500 MB** persisted preparation artifacts;
- CPU only;
- <= **45 minutes** wall time;
- $0 paid compute;
- no automatic retry loop.

## Future model experiment boundary

Even after model-free admission passes, training is not automatic.

A separate prospective design must freeze:
- whether the frozen S11 architecture remains the comparator/candidate architecture;
- exact three seeds;
- exact optimizer/batch/step counts;
- paired initialization/batches;
- exact ordinary and source-domain challenge gates;
- family guards;
- negative-only FP guards;
- compute ceiling;
- single-use execution controls.

The future model experiment may vary only the **source-domain training data package**. It may not simultaneously change architecture, frontend, loss, sampler, decoder or thresholds.

## Interpretation limits

Passing model-free admission would show that the package:
- is deterministic;
- preserves labels/timing under its construction;
- spans source-level acoustic variation;
- produces measurable representation differences after the frozen frontend.

It would **not** show:
- that it matches real guitar distributions;
- that it will improve P1/P2;
- that the current architecture is adequate;
- that P3 should be opened.

## Decision

**GO for offline implementation and model-free admission tests only.**

No model run is authorized by this design.
