# Post-V13 causal review V1

Date: 2026-09-29 UTC  
Status: **DOCUMENTATION/REVIEW ONLY — NO V14 OPENED**

This review obeys the current generic-continue boundary. No waveform rendering, model training, optimizer step, inference, workflow dispatch, V2B evaluation, or Production mutation was performed.

## Main finding

V13 cleanly tested the largest remaining active-state family redistribution and produced only a negligible common-test gain.

The strongest unresolved single sampler-domain factor is now the **family composition of the negative-structure-inactive stratum**.

This stratum is especially relevant because it contributes exactly 32 frames per update and is the only frozen stratum explicitly restricted to clips carrying negative structure while the current common-population failure is dominated by poor precision.

## Historical comparator negative-structure-inactive composition

Historical 2-second comparator training frames:

| Family | Frames | Share |
|---|---:|---:|
| legato | 1,020 | 22.01% |
| palmmute | 1,560 | 33.66% |
| mixed | 2,055 | 44.34% |
| **total** | **4,635** | **100%** |

Executed V9:

| Family | Frames | Share |
|---|---:|---:|
| legato | 3,907 | 35.95% |
| palmmute | 2,403 | 22.11% |
| mixed | 4,558 | 41.94% |
| **total** | **10,868** | **100%** |

Share shifts from historical comparator to V9:
- legato: **+13.94 percentage points**
- palmmute: **-11.55 points**
- mixed: **-2.40 points**

That is a large redistribution inside a stratum sampled at a fixed 25% of every batch.

## Frozen historical target over 16,000 negative-structure-inactive slots

Across 500 updates x 32 negative-structure-inactive slots, there are exactly **16,000** sampled slots/model.

The historical comparator proportions map to this exact largest-remainder allocation:

- legato **3,521**
- palmmute **5,385**
- mixed **7,094**
- total **16,000**

A future intervention can therefore change only the negative-structure-inactive family selection while preserving:
- the exact V9 positive-onset selections;
- exact V9 active-non-onset selections;
- exact V9 other-inactive selections;
- exact per-step permutation;
- exact attacked-note-label exposure;
- exact dataset arrays;
- exact model, initialization, loss, thresholds, optimizer, and 500-update budget.

## Why this is now the preferred next single-factor diagnostic

V10, V12, and V13 progressively isolated attack-label exposure, positive-onset family mixture, and active-non-onset family mixture.

V13 is particularly informative because all three other strata and attacked-note-label exposure were held fixed, yet common F1 improved only **+0.004896**.

The negative-structure-inactive stratum remains the one untested within-stratum family mixture with a large historical-to-V9 redistribution.

It is also mechanistically relevant to precision control:
- these are inactive frames from clips that contain negative structure;
- over-representing legato and under-representing palm-mute relative to the historical comparator may change how the model learns to suppress false activations in structurally difficult inactive regions.

This remains a hypothesis, not a conclusion.

## Preferred future project question

Do **not** open V14 automatically.

If the user explicitly authorizes a new project, prospectively freeze:

> With the exact executed V9 dataset and exact V9 batch plan fixed everywhere else, does matching only the historical comparator negative-structure-inactive family mixture materially recover common-population precision/F1 while preserving the negative-only false-positive ceiling?

Preferred operational design:
- no intervention-specific rendering;
- no timing generation;
- no state-semantic regeneration;
- same regenerated V9 dataset for both arms;
- control reproduces exact V9 batch plan;
- intervention replaces only negative-structure-inactive selections;
- exactly 16,000 negative-structure-inactive slots per arm;
- target allocation legato 3,521 / palmmute 5,385 / mixed 7,094;
- positive-onset selections identical;
- active-non-onset selections identical;
- other-inactive selections identical;
- per-step shuffle identical;
- attacked-note-label exposure identical;
- same model, losses, thresholds, optimizer, and 500 updates;
- primary evaluation = frozen 2-second comparator test;
- secondary evaluation = frozen V9 test;
- no V2B stage.

## What current evidence now weakens

Direct single-factor diagnostics now weaken simple explanations based on:
- marginal attack timing mismatch;
- attacked-note-label exposure alone;
- state-duration / legato-continuation semantics alone;
- positive-onset family mixture alone;
- active-non-onset family mixture alone.

None of those produced a material rescue under its frozen contract.

## Broader interpretation

If the negative-structure-inactive mixture also fails, the evidence would increasingly favor a **composite corpus/domain-shift explanation** rather than one isolated sampler statistic.

The likely remaining composite differences would include:
- 2-second versus 4-second temporal context;
- inactive/background diversity;
- longer-range sequence and gap structure;
- correlations across multiple strata;
- family-by-duration-by-context interactions.

At that point, continuing one-factor-at-a-time studies may become less efficient than designing a prospectively frozen **whole-package 2-second-context control** or a matched-context factorial study.

That broader design should not be opened unless the negative-inactive study is first completed or deliberately skipped under a new explicit project authorization.

## Stop boundary

No V14 contract, authorization, runner, workflow, launch, rendering, training, or inference was created.

Execution counts for this review:
- waveform renders **0**
- models trained **0**
- optimizer steps **0**
- model inference **0**
- V2B inference **0**
- workflow dispatches **0**

Main/Production unchanged.

At a future explicit authorization to open a new project, freeze the negative-structure-inactive family-mixture study first. Empirical execution must still wait for fresh authorization after that contract/preflight is visible.
