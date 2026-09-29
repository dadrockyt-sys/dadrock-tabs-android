# V10 attack-label exposure isolation result V1

Date: 2026-09-29 UTC  
Status: **COMPLETE — EXPOSURE HYPOTHESIS NOT SUPPORTED**

The explicitly authorized V10 synthetic-only diagnostic executed once under launch identity `v10-exposure-v1-20260929-01`.

The study reproduced the frozen V9 failure exactly, then increased sampled attacked-note-label exposure from **17,676** to **19,702** while keeping the V9 dataset, model, loss, thresholds, optimizer, step count, non-positive stratum selections and per-step shuffle fixed.

The prospectively frozen material-recovery gate did **not** pass.

## Execution identity

- run **36528001337**
- job **109275178270**
- head `b5c661b6f383571bf31383e2a1d884089c71311d`
- workflow conclusion **success**
- artifact **11015118480**
- artifact digest `sha256:34bed0c4f07458915196d5fb91cf3ca521ccb5ae8d01233ca0b2de6303e50fee`
- artifact retained through **2026-10-29**
- models **2**
- optimizer steps **1,000 total**
- automatic scientific retries **0**
- threshold search **false**
- real-audio inference **0**
- V2B inference **0**

## Identity and exposure

Both arms used:
- 16,000 positive-onset frame slots
- 500 updates
- the same regenerated frozen V9 training arrays
- identical non-positive stratum selections
- identical per-step shuffle

Control:
- attacked-note-label exposure **17,676**
- batch-plan SHA-256 `8995265eb96a3a9833c9d1620eea1620a6a50914280aacd00474486f0508d4d7`

Exposure-balanced intervention:
- attacked-note-label exposure **19,702**
- 1,851 three-label positive frames
- 14,149 one-label positive frames
- batch-plan SHA-256 `d439414e7b1dd92a4b505d14752da9bdeee203ee1dc09ff3a3e5c923e22cc837`

## Frozen V9 reproduction — PASS

The V10 control reproduced the frozen V9 common comparator-test result exactly:

| Metric | Frozen V9 | V10 control |
|---|---:|---:|
| Precision | 0.324427 | 0.324427 |
| Recall | 0.658915 | 0.658915 |
| F1 | 0.434783 | 0.434783 |

This validates the control path before interpreting the exposure intervention.

## Primary common comparator-test population

| Metric | V10 control | Exposure-balanced | Delta |
|---|---:|---:|---:|
| Precision | 0.324427 | **0.348624** | **+0.024196** |
| Recall | 0.658915 | 0.589147 | **-0.069767** |
| F1 | 0.434783 | **0.438040** | **+0.003258** |
| Negative FP/s | 0.0 | 0.0 | 0.0 |
| State admission | 0.310078 | 0.271318 | -0.038760 |
| Onset admission | 0.682171 | 0.666667 | -0.015504 |
| Joint admission | 0.286822 | 0.255814 | -0.031008 |

Frozen support requirements:
- precision gain >= +0.20: **FAIL**
- F1 gain >= +0.15: **FAIL**
- recall decline <=0.08: PASS
- negative FP/s <=0.10: PASS

The intervention recovered only about **2.4 precision points** and **0.3 F1 points** on the primary population, far below the prospectively required material recovery.

## Secondary V9 test population

| Metric | V10 control | Exposure-balanced | Delta |
|---|---:|---:|---:|
| Precision | 0.486631 | **0.537994** | **+0.051363** |
| Recall | 0.705426 | 0.686047 | -0.019380 |
| F1 | 0.575949 | **0.603066** | **+0.027117** |
| Negative FP/s | 0.0 | 0.0 | 0.0 |

The secondary population improved modestly, but this does not rescue the primary preregistered gate.

## Decision

**The V10 attacked-note-label exposure hypothesis is not supported.**

Exact exposure matching did not materially restore the synthetic precision/F1 collapse seen in V9.

This narrows the explanation: the approximately 11% attacked-label exposure deficit measured in V9 was not, by itself, a sufficient explanation for the large common-population precision/F1 loss.

The result does **not** identify the true cause. Remaining package differences include, among others:
- longer temporal/context distribution;
- active/sustain-frame composition;
- attack-count allocation across families;
- onset/state coupling under the longer clips;
- gap/sustain placement interactions.

No post-hoc sampler retuning, threshold search, V2B bypass, or automatic next experiment is permitted.

## Artifact hashes

- `result.json`: `7d94334506a55799b5d24ca36a490aa96c71047eef0d984e4b4ff8a283aee689`
- execution receipt: `acffa9b2491e87ec2f550b6f3433c542ee11ba8c97b8e088a967fbb57253c63f`
- control checkpoint: `d1b57eeeb7fbf980fade36e1f2dcd06a5099f32bb63af5acb0d356ee9a6d52d3`
- exposure-balanced checkpoint: `f57b034f013ec0a245d83e38654afe2f8aa0d761fbf2fcd711cf5c4ff07b31b6`

## Current stop boundary

- V9 remains frozen FAIL at synthetic sanity.
- V10 is complete and its exposure hypothesis is not supported.
- V2B was not run.
- V1.1/P1/P2/P3 remain untouched.
- A2 remains closed.
- main/Production unchanged.

The next project, if any, must be prospectively defined and separately authorized. No automatic V11 is created by this result.
