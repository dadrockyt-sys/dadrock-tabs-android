# V9 fallback-free curriculum result V1

Date: 2026-09-29 UTC  
Status: **V9A PASS — SYNTHETIC SANITY FAIL — V2B BLOCKED**

The explicitly authorized frozen V9 package executed once under launch identity `v9-frozen-v1-20260929-01`.

Workflow completion was successful, but the scientific V9 gate **failed** at synthetic sanity. Under the frozen execution order, no V2B real-development inference was performed.

## Execution identity

Accepted model-free preflight:
- run **36526305988**
- job **109270011760**
- head `a0c09415abba839cf525531141dcfa7822e95f68`
- artifact **11014613083**
- digest `sha256:c764c270d0b280895fb755adcb32032b3d604e66ccef0ae627362d9b26a50b30`
- conclusion **success**

A prior preflight run **36526163229** failed before candidate generation because the test command omitted the repository root from `PYTHONPATH`. That was an infrastructure failure: 0 candidate timings, 0 renders, 0 optimizer steps, 0 inference. The import path was repaired before the consumed empirical launch.

Empirical run:
- run **36526450793**
- job **109270456836**
- head `f488e857c821fbee2846aa5ae3a511a2e30e8007`
- artifact **11015165684**
- artifact digest `sha256:e5ebb4c1450cbfac7453dc9613c33e0f64a5694044c2195ceeea36651f65af3c`
- workflow conclusion **success**
- optimizer steps **1,000 total**
- models **2**
- automatic scientific retries **0**
- threshold search **false**
- real-audio model inference **0**

## V9A timing gate — PASS

All prospective timing/identity conditions passed.

- corrected V8 L0 distance: **1.6103247396**
- V9 distance: **0.0918590535**
- relative improvement: **94.30%** (required >=60%)
- attack-group density: **1.500000/s**
- IOI p10: **0.120762 s**
- IOI p50: **0.257750 s**
- IOI p90: **0.902659 s**
- repeat250: **46.1538%**
- longGap700: **13.8462%**
- positive clips: **273**
- negative-only clips: **21**
- attack groups: **1,638**
- attacked note labels: **1,806**
- infeasible clips: **0**
- invalid labels/offsets: **0**
- fallback operations: **0**

The timing construction therefore solved the narrow common-unit distribution/generation problem under the frozen gate.

## Render

Same-runtime R3 rendering completed within ceiling:

| Arm | Examples | Logical seconds | Frames/clip | Attack groups | Attacked note labels |
|---|---:|---:|---:|---:|---:|
| 2 s comparator | 294 | 588 | 87 | 735 | 903 |
| 4 s V9 | 294 | 1,176 | 173 | 1,638 | 1,806 |

Render time was **64.49 s** and persisted datasets totaled **41.49 MiB**. No external audio assets were used.

## Training exposure

Both arms used exactly 500 updates and 64,000 sampled frames, representing 1,486.077 sampled frame-seconds and 16,000 sampled attack frames per arm.

However, attacked-note-label exposure was not equal:
- comparator: **19,702** sampled attacked note labels
- V9: **17,676**

This is an observed package difference that must be reported. It does not permit post-hoc resampling or a retry.

## Synthetic sanity — FAIL

Both models were evaluated on the same fixed comparator test population.

| Metric | Comparator | V9 intervention |
|---|---:|---:|
| Onset precision | **0.8269** | **0.3244** |
| Onset recall | 0.6667 | 0.6589 |
| Pitch-onset F1 | **0.7382** | **0.4348** |
| TP / FP / FN | 86 / 18 / 43 | 85 / **177** / 44 |
| Negative-only FP/s | 0.0 | 0.0 |
| State admission | 0.2946 | 0.3101 |
| Onset admission | 0.6202 | 0.6822 |
| Joint admission | 0.2868 | 0.2868 |

Frozen sanity checks:
- onset precision >=0.70: **FAIL**
- pitch-onset F1 decline <=0.08: **FAIL**
- onset recall decline <=0.08: PASS
- negative FP/s <=0.10: PASS
- exactly 500 updates/model: PASS
- finite metrics: PASS

The intervention retained roughly the comparator's recall but produced many more ordinary synthetic false positives. Its precision fell by about **0.5025** and pitch-onset F1 by about **0.3034**.

## Decision

**V9 does not advance to V2B.**

The contract required synthetic sanity to technically gate real-development inference, and that gate worked: V2B model inference count remains **0**.

The supported conclusion is narrow:
- fallback-free 4-second generation can closely match the chosen common-unit timing statistics;
- this complete V9 training package does **not** preserve adequate synthetic pitch-onset discrimination under the frozen comparison.

Do not conclude that long-duration timing itself is harmful. V9 jointly changed duration, attack-count allocation, gap distribution, sustain placement, and note-label exposure. In particular, equal update/frame exposure did not yield equal attacked-note-label exposure.

No threshold retuning, resampling, second V9 arm, V2B bypass, or automatic V10 is allowed from this result.

## Evidence hashes

Artifact file SHA-256:
- `timing.json`: `ae9384286a40009a328ce98fd90f15f3bbc4e31b9686f48e6f81a5275d41d913`
- render receipt: `817a474c5ffabf34a43d5fc19b2e8836982fc86a29bcdc762ada8cfb48aa7f0d`
- train result: `7f1b51592fdaf01f77d5d658abe76cc5f22de76ca70cdcf5bcfc9ac6e89dcfc7`
- comparator checkpoint: `653587a0ac02b383daca3740d26fe0685bd3fc3c88cfd86335f4a90ad3bfe8a5`
- intervention checkpoint: `98668a9e044d1de1823f6e55c982fe0729bb2361264ba9d6264b565b8ef48115`
- execution receipt: `62da92fdba5dc195eb378a45daeab1adbbea92d4677b2d72c7e2e083ae4a050d`

The GitHub artifact is retained through **2026-10-29**. The hashes are frozen in Git; the checkpoint binaries themselves remain in the workflow artifact, not the repository.

## Current stop boundary

- V9 frozen and complete
- V2B inference not performed
- V1.1/P1/P2/P3 untouched
- A2 closed
- main/Production unchanged

The next useful decision is a new project question, not a retry. A future study would need to prospectively decide whether to isolate **training exposure / attack-label weighting** from the timing package, or to pause this synthetic path. No automatic V10 is authorized.
