# S0 Transcription Failure Attribution V1 — Result

Date: 2026-10-02  
Branch: `astra-work`

## Purpose

Measure how much downstream note transcription changes because of source separation, without changing separator output.

For each frozen S0 guitar/bass role, the same frozen Basic Pitch 0.4.0 configuration was run on:
1. the exact clean rendered S0 component; and
2. the untouched raw BS-Roformer output.

The clean-component transcription is an **oracle-audio transcriber baseline**, not musical ground truth. Exact-MIDI onsets were compared at a fixed 50 ms tolerance.

No cleanup, merge, threshold search, model training, or separator mutation occurred.

## GitHub Actions evidence

Successful run: `37090246256`  
Head commit: `57386ca1a0cc98bed124debbd1b2f4c5ed2f3552`

Artifact:
- id: `11262262754`
- digest: `sha256:e0a1b42c60f2c8aacb10a477b6f70efa8fbfdc418ac049868fcfcebdad4b74ca`

An earlier run `37090038784` failed only because Basic Pitch's TFLite runtime was incompatible with NumPy 2.x. The rerun pinned NumPy 1.26.4; no scientific setting changed.

## Aggregate result

- mixtures: **12**
- role probes: **24**
- target-present probes: **20**
- target-absent probes: **4**
- micro event agreement:
  - precision: **0.789**
  - recall: **0.632**
  - F1: **0.702**
- macro per-role F1: **0.663**
- minimum per-role F1: **0.000**
- maximum per-role F1: **1.000**
- severe agreement failures (F1 < 0.5): **5**

Target-absent behavior:
- all **4/4** absent-target separator outputs produced at least one Basic Pitch note event
- total absent-target false-note events: **53**
- S0M10 false guitar alone produced **33** note events despite guitar being absent

## Severe transcription-instability cases

- S0M03 guitar: SI-SDR **-14.84 dB**, F1 **0.000**
- S0M04 guitar: SI-SDR **-6.91 dB**, F1 **0.230**
- S0M10 bass: SI-SDR **0.07 dB**, F1 **0.302**
- S0M11 bass: SI-SDR **-14.08 dB**, F1 **0.261**
- S0M12 guitar: SI-SDR **-5.16 dB**, F1 **0.071**

Strong examples:
- S0M05 guitar: SI-SDR **34.02 dB**, F1 **1.000**
- S0M01 guitar: SI-SDR **20.05 dB**, F1 **0.972**
- S0M06 bass: SI-SDR **20.28 dB**, F1 **0.930**
- S0M08 bass: SI-SDR **15.70 dB**, F1 **0.914**

## Descriptive relationship

Across the 20 target-present probes, Pearson correlation between raw separator SI-SDR and transcription-agreement F1 was approximately **0.896**.

Descriptive groups only, not frozen gates:
- SI-SDR >= 15 dB: 12 probes, mean F1 **0.864**, minimum F1 **0.571**
- SI-SDR < 5 dB: 6 probes, mean F1 **0.250**, maximum F1 **0.638**

This is strong evidence on S0 that poor source separation can dominate downstream transcription instability.

## Error morphology

Across target-present probes:
- total unmatched separated events / false positives: **137**
- total unmatched oracle events / misses: **299**
- octave-related separated false positives: **38**
- timing-only separated false positives: **31**
- octave-related oracle misses: **30**
- near-pitch oracle misses: **1**
- timing-only oracle misses: **36**

Most failures are therefore not explainable by small semitone confusion alone. Missing note activity, timing instability, and octave/harmonic behavior are materially involved.

## Decision

Do **not** change Basic Pitch thresholds from this result.

Do **not** mutate or clean stems based on this result.

The highest-value next stage is a **no-reference transcription reliability observability diagnostic**. It should ask whether quantities available at inference time—separator-output energy/overlap diagnostics and transcriber event statistics—track the severe instability cases well enough to support a future confidence/flagging system.

The next stage must remain descriptive on these same S0 fixtures:
- collect features;
- measure associations with oracle-audio transcription agreement;
- do not fit or freeze an accept/reject threshold on S0;
- use any resulting hypothesis only to design a future prospectively frozen holdout test.

## Boundary

This is S0 synthetic-mixture evidence only. Basic Pitch clean-component events are not asserted to be correct tablature, and no commercial-recording generalization is claimed.
