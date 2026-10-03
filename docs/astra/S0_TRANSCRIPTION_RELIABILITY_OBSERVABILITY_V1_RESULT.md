# S0 Transcription Reliability Observability V1 — Result

Date: 2026-10-02  
Branch: `astra-work`

## Purpose

Test whether simple no-reference features available at inference time track downstream transcription instability well enough to support a future confidence/flagging system.

This stage is **descriptive only**. It does not fit a threshold, train a model, define an accept/reject gate, or alter any separator output.

## GitHub Actions evidence

Run: `37090800270` — **success**  
Head commit: `977b1883f96d55ce3c690ed25950c8a832b3bbe3`

Artifact:
- id: `11262263768`
- digest: `sha256:4fb1caa6253b3cd89a98209b3160901c4aea6b9fbb6ad8d214b79dc887ae6427`

## Features observed

Separator-output diagnostics:
- stem-to-mixture energy dB
- interference pressure
- competitor dominance fraction
- target dominance fraction
- ambiguous fraction
- strongest competitor energy ratio

Transcriber-output diagnostics:
- event density
- mean / low-percentile amplitude
- mean duration
- dominant MIDI share
- pitch range
- near-synchronous octave-event fraction

Reference audio was used only to calculate the development-set transcription-agreement F1 for association analysis.

## Descriptive associations with transcription-agreement F1

Ranked by absolute Spearman correlation:

1. stem-to-mixture energy dB: Spearman **+0.594**, Pearson **+0.659**
2. interference pressure: Spearman **-0.542**, Pearson **-0.622**
3. strongest competitor energy ratio dB: Spearman **-0.533**, Pearson **-0.672**
4. mean note duration: Spearman **+0.477**, Pearson **+0.129**
5. event density / second: Spearman **+0.464**, Pearson **+0.546**
6. octave-related event fraction: Spearman **+0.434**, Pearson **+0.470**
7. competitor dominance fraction: Spearman **-0.427**, Pearson **-0.565**
8. target dominance fraction: Spearman **+0.427**, Pearson **+0.556**

Other single features were weak.

These associations are hypothesis-generating only. No cutoff is authorized from this S0 analysis.

## Absent-target behavior

Three absent-target outputs are easy no-reference failures:
- S0M07 bass: stem-to-mixture ~**-92.55 dB**, competitor dominance **1.0**, 9 false note events
- S0M08 guitar: ~**-93.24 dB**, competitor dominance **1.0**, 5 false note events
- S0M09 bass: ~**-92.02 dB**, competitor dominance **1.0**, 6 false note events

They are essentially near-silent target stems dominated by another separator output.

### S0M10 remains the hard case

S0M10 guitar is absent in ground truth, yet:
- stem-to-mixture energy: **-3.03 dB**
- interference pressure: **0.120**
- competitor dominance: **0.158**
- target dominance: **0.776**
- strongest competitor: bass
- strongest competitor energy ratio: **-0.79 dB**
- Basic Pitch events: **33**
- event density: **4.48/s**
- dominant MIDI share: **0.545**
- octave-related event fraction: **0.485**

Those are not the signatures of a trivially empty/contaminated stem. The false guitar output looks internally coherent and musically active.

The true S0M10 bass output is also active:
- stem-to-mixture: **-3.82 dB**
- event count: **33**
- event density: **4.48/s**
- transcription agreement F1 vs clean bass baseline: **0.302**

Combined with earlier duplicate-class evidence, this supports the interpretation that the separator split one bass source across both guitar and bass outputs.

## Decision

Do not build a reliability threshold from the ordinary single-stem observability features on these same S0 fixtures.

They can flag obvious near-silent failures, but they are not sufficient for the hard role-duplication case.

The highest-value next diagnostic is **cross-stem transcription overlap / role ambiguity**:

- transcribe guitar and bass separator outputs independently with the same frozen front end;
- compare exact-MIDI onset overlap and near-onset pitch-class/octave relationships between the two outputs;
- retain the frozen pair-classifier/recognizer evidence as context;
- identify whether both stems are describing the same musical events;
- produce a diagnostic confidence/ambiguity flag only;
- do not merge, mute, reassign, or suppress audio.

No thresholds should be selected from S0 until the cross-stem feature distribution has first been measured descriptively.

## Boundary

S0 synthetic mixtures only. No real/commercial recording generalization and no production action are authorized.
