# Astra simulator/representation strategy review V2

Date: 2026-09-28  
Status: **CORRECTED POST-S13 REVIEW — V2 REAL-DOMAIN INTEGRITY EVIDENCE INCLUDED — NO MODEL EXECUTION AUTHORIZED**

## Why V2 exists

V1 of this strategy review incorrectly treated the P1/P2 preparation-integrity audit as still pending. The repository already contained a successful frozen corrected V2 audit before the later S12/S13 sequence. This document supersedes V1 wherever they differ.

No historical result is rewritten. No P1/P2 source is reopened here. No model is loaded or trained. Optimizer steps = 0. P3 remains sealed. Main/Production are unchanged.

## Frozen evidence considered

1. `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_RESULT_V2.json`
2. `docs/astra/REAL_DOMAIN_FAILURE_LOCALIZATION_RESULT_V1.json`
3. `docs/astra/SYNTHETIC_ONSET_ENVELOPE_S12_RESULT_V1.json`
4. `docs/astra/SYNTHETIC_S13_RESULT_V1.json`
5. frozen S0/S11 generator/model source
6. frozen preprocessing contract
7. S13 transform-design review and frozen S13 design

## Real-domain integrity evidence that must now carry forward

The corrected V2 audit already established, on the exact bounded development examples:

- P1 eligible acoustic attacks: **16** across four captures;
- P2 eligible acoustic attacks: **11** across three eligible captures;
- the P2 Drop3_7 chord was prospectively excluded because its events are too close to the start boundary for the fixed windows.

Event-weighted P2/P1 median ratios:
- raw post-attack RMS: **0.537**;
- raw first-difference energy: **0.0947**;
- prepared-CQT positive flux: **0.871**.

Capture-balanced P2/P1 ratios from the frozen V2 values:
- raw post-attack RMS: about **0.899**;
- raw first-difference energy: about **0.792**;
- prepared-CQT positive flux: about **0.952**.

The event-weighted first-difference contrast is therefore strongly affected by event/category composition. The evidence supports **weaker and variable real attack-envelope contrast on these examples**, not a universal tenfold P2 weakness.

Timing/downmix findings:
- event-weighted raw peak median difference P2 minus P1: about **-1.61 ms**;
- prepared-CQT median peak offset: **0 frames for both**;
- P2 stereo-channel attack metrics were identical;
- frozen stereo-to-mono decoding increased amplitude by about sqrt(2), rather than attenuating it;
- existing RMS normalization removes fixed global gain before CQT.

Therefore:
- gross fixed timing error is **not supported** as the main P2 explanation;
- stereo/downmix attenuation is **not supported**;
- weak/variable source attack contrast is a **supported domain factor**;
- one unique causal mechanism is **not established**.

## Combined interpretation after S12 and S13

### S12

S12's recursive frame-wide softening produced positive challenge gains in all three seeds, but:
- mean challenge F1 gain **+0.0370**, below +0.05;
- mean challenge recall gain **+0.0413**, below +0.08;
- ordinary onset F1 mean delta **-0.0508**;
- ordinary state admission mean delta **-0.0775**;
- ordinary joint admission mean delta **-0.0646**.

The later model-free transform review showed that S12 modified more than attack contrast and recursively altered context, so it is not a clean physical or identity-preserving source model.

### S13

S13 used a narrower nonrecursive positive-increment transform, but:
- challenge onset F1 mean delta **-0.0121**;
- challenge recall mean delta **-0.0233**;
- challenge F1 positive in **1/3** seeds;
- challenge recall positive in **0/3** seeds;
- individual ordinary precision/state-admission guards also failed.

Thus both feature-space robustness interventions are rejected.

## Project-level diagnosis

The strongest defensible diagnosis is now **two-factor domain risk**, not one onset-only failure:

1. **Attack-envelope/source-domain mismatch**
   - directly supported by the frozen V2 model-free audit on bounded real examples;
   - heterogeneous across categories/captures;
   - not explained by gross timing or stereo attenuation.

2. **State/pitch representation transfer failure**
   - separately supported by P1 candidate localization;
   - candidate true-state probability mean **0.0305**;
   - candidate silence probability mean **0.7171**;
   - pitch-only top-1 **31.25%**;
   - median absolute semitone error **11.5**.

These two factors may interact, but neither frozen evidence nor S12/S13 proves that one causes the other.

## Why another feature-space transform is not justified

The current synthetic generator creates a compact procedural plucked-string world:
- 294 clips;
- seven families;
- analytic harmonic sums;
- simple exponential damping;
- one scalar pick-position parameter;
- one scalar brightness parameter;
- synthetic transient burst/noise;
- fixed resampling and frozen CQT frontend.

It does not explicitly generate a broad population of source-domain variability such as:
- variable attack rise-time distributions across notes and performers;
- pick/finger/nail excitation families;
- string-age/material/damping variation;
- pickup position/electrical filtering families;
- amplifier/compressor/distortion nonlinearities;
- cable/interface frequency response;
- room/microphone path variation;
- real fret/string interaction, sympathetic resonance and inharmonicity;
- correlated background/noise and dynamic-range variation.

S12/S13 altered **already-extracted features** rather than broadening the source signal that the frontend observes. Given the V2 raw-audio evidence, continuing to warp CQT frames would risk optimizing the synthetic representation instead of addressing the source-domain gap.

## Frozen strategy decision

### NO-GO

Do not:
- run S14;
- tune another feature-space softening transform;
- alter thresholds or decoder windows;
- seed-pick;
- fit simulator parameters directly to the eight exposed P1/P2 examples;
- reopen P1/P2;
- open P3;
- swap architecture and simulator simultaneously.

### GO — offline/model-free only

The next justified work is a **prospective source-audio simulator coverage design**, not training.

Its purpose is to define a broader procedural source-domain family before any model sees it.

The design must:
1. operate at waveform/source generation, before the frozen CQT frontend;
2. keep the existing S0/S9/S11 control intact;
3. add exactly one versioned source-domain diversity package, not a bundle selected by outcome;
4. choose parameter ranges from physical/engineering priors and public/reference knowledge, not by fitting the eight exposed P1/P2 examples;
5. explicitly include attack-envelope variability while also broadening timbre/electrical/noise dimensions;
6. preserve labels by construction;
7. define model-free admission tests first;
8. define held-out synthetic challenge families prospectively;
9. predeclare a finite training budget and gates only after the simulator package passes model-free review;
10. keep P1/P2 closed and P3 sealed during design and synthetic execution.

## Required model-free admission criteria for a future simulator package

Before any optimizer work, the source-domain generator must demonstrate on handcrafted/procedural fixtures:

- exact label/timing preservation;
- finite/bounded audio;
- deterministic reproduction from frozen seeds;
- no clipping unless clipping is an explicitly labeled challenge family;
- attack rise-time/difference-energy variation without deleting note identity;
- stable pitch/fret fundamentals under non-pitch interventions;
- no accidental split leakage;
- family-balanced train/validation/test identities;
- source-waveform perturbations survive through the frozen frontend in the intended direction;
- no intervention parameter is derived from P1/P2 measurements.

The review should record waveform, spectrum and prepared-CQT diagnostics for each source-domain family before training.

## Architecture boundary

The current five-frame flattened-CQT MLP may also limit transfer, but architecture should **not** be changed in the same experiment as a new source simulator.

If the simulator package later passes a synthetic robustness gate while the frozen architecture still exhibits a clear synthetic representation ceiling, then a separately preregistered architecture experiment may be considered. That is not authorized now.

## Correct next action

Create and review one prospective **source-audio simulator diversity specification** offline.

Do not train yet.

Suggested paths:
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_DIVERSITY_DESIGN_V1.md`
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_DIVERSITY_SPEC_V1.json`

The first version should define:
- source-domain families;
- exact parameter ranges and distributions;
- deterministic RNG streams;
- label-preservation rules;
- model-free diagnostics;
- challenge construction;
- split identity rules;
- hard compute/storage ceilings for later preparation only.

Do not create a launch marker or model workflow until that design has been reviewed and frozen.

## Resume instruction

Continue with **offline source-audio simulator diversity design only**. Preserve V2, S12 and S13 frozen results. Keep P1/P2 closed, P3 sealed, thresholds 0.50/0.50, and main/Production unchanged. No model execution is authorized by this review.
