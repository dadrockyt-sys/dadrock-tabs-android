# Real-Domain Transfer / Calibration Diagnosis V2

Date: 2026-09-28  
Status: **DESIGN FROZEN — NO TUNING ON V1.1**

## Purpose

The V1.1 independent real-development evaluation showed near-total positive admission collapse under the frozen S9 checkpoint and 0.50/0.50 thresholds.

This V2 project is a diagnosis program, not a rescue run.

It must determine which of the following explanations is most plausible before any adaptation work is considered:

1. historical-runtime mismatch;
2. frontend feature-distribution mismatch;
3. onset/state calibration shift;
4. representation/domain shift;
5. decoder admission interaction.

## Evidence separation

The existing V1.1 set is now a **sealed evaluation set**.

It may be used only for:
- reproducing the already-frozen V1.1 result under an exact historical runtime;
- non-tuning forensic measurements that do not alter thresholds, decoder, model, frontend, gain, candidate, or preprocessing;
- confirming whether exact-runtime reproduction materially changes the frozen metrics.

It must not be used for:
- choosing thresholds;
- calibration fitting;
- gain selection;
- frontend retuning;
- decoder tuning;
- fine-tuning;
- candidate selection;
- architecture selection.

Any parameter choice informed by V1.1 would contaminate it as an independent evaluation set.

## V2A — exact-runtime reproduction

First priority.

Recreate the historical execution environment as closely as practical:
- Python 3.10.x;
- torch 1.11.0+cpu;
- librosa 0.9.1;
- numpy 1.21.6;
- scipy 1.8.1;
- resampy 0.4.3;
- frozen S9 checkpoint bytes;
- frozen source pins;
- frozen 0.50/0.50 thresholds;
- frozen V2 decoder;
- exact V1.1 crops and references.

No model training.

### V2A decision rule

If exact-runtime V1.1 trusted-landmark hit rate remains below 10%, treat runtime mismatch as insufficient to explain the transfer failure.

If it improves materially, preserve both results and do not tune further until the runtime discrepancy is isolated.

## V2B — new calibration-development set

Only after V2A.

Collect a **new, separate calibration-development set** that is not part of V1.1 and is not P1/P2/P3.

Minimum:
- 12 positive clips;
- 4 negative-only clips;
- at least 60 seconds positive audio;
- at least 20 seconds negative audio;
- at least 2 capture chains or creators;
- clean and distorted guitar;
- single-note and repeated-attack material.

This set may be used for calibration diagnosis, but V1.1 remains untouched.

## V2C — calibration diagnosis on the new set

Before changing anything, export raw diagnostics:
- maximum active-state probability at reference onsets;
- silence probability at reference onsets;
- onset sigmoid at reference onsets;
- distributions for positive and negative frames;
- fraction failing state gate only;
- fraction failing onset gate only;
- fraction failing both;
- decoded event density.

Then evaluate a **prospectively declared** finite threshold grid on the new calibration-development set only.

Suggested bounded grid:
- state threshold: 0.20, 0.30, 0.40, 0.50;
- onset threshold: 0.20, 0.30, 0.40, 0.50.

This grid is not authorized by this design alone; execution requires explicit opening of V2C after V2A and the new calibration set are complete.

## V2D — holdout confirmation

If V2C identifies a plausible calibration setting, collect a second fresh holdout set before reporting improvement.

Never report tuned calibration as validated on the same clips used to choose it.

## Hard boundaries

Do not:
- retrain S9;
- fine-tune on V1.1;
- search thresholds on V1.1;
- tune gain or normalization on V1.1;
- modify decoder from V1.1 outcomes;
- open P1/P2/P3;
- open A2;
- mutate main/Production.

## Exact next action

Build and execute **V2A exact-runtime reproduction only**.

If the historical runtime cannot be recreated without altering the checkpoint/frontend/decoder semantics, freeze the limitation and stop. Do not substitute a tuning experiment.
