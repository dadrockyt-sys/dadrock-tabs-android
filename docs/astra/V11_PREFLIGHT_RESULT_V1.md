# V11 state-duration / legato-continuation preflight result V1

Date: 2026-09-29 UTC  
Status: **MODEL-FREE PREFLIGHT PASS — EMPIRICAL EXECUTION NOT AUTHORIZED**

The new V11 project has been prospectively frozen and its model-free preflight passed.

Frozen question:

> With successful V9 attack timing/counts fixed, does restoring historical family-specific state/audio durations and the omitted legato continuation materially recover common-population precision/F1?

## Preflight identity

- run **36534288763**
- job **109294696440**
- head `d736257bf2181b1c1a936ac74b825000c15b4588`
- artifact **11017093440**
- digest `sha256:974b0c3a9e86448b0c4b70ec37dada523dfe5a0eb208ac297ce6a0e8e0d56e81`
- conclusion **success**
- artifact retained through **2026-10-29**

All pure contract and static source tests passed.

## Attack identity preserved

The model-free audit verified both 4-second arms contain exactly:

- **1,638 acoustic attack groups**
- **1,806 attacked note labels**
- **273 positive clips**
- **21 negative-only clips**

The attacked `(string, fret, onset)` signature is identical across control and intervention:

`9129b31cec8c56a8275e269b25fd9ab686b15f91e8b5da711ef6490eddfffe97`

So V11 does not move attack times or change attacked note identity.

## Restored state semantics

The intervention restores historical family duration targets and applies the frozen same-string retrigger truncation rule.

Static audit found:

- restored non-attacked legato continuation events: **84**
- attacked states truncated at a later same-string retrigger: **789**

Per family:

| Family | Positive clips | Restored continuations | Retrigger-truncated attacked states |
|---|---:|---:|---:|
| isolated | 42 | 0 | 168 |
| scales | 42 | 0 | 37 |
| chords | 42 | 0 | 126 |
| repeated | 42 | 0 | 243 |
| legato | 42 | **84** | 84 |
| palmmute | 42 | 0 | 82 |
| mixed-positive | 21 | 0 | 49 |

These truncations are expected consequences of preserving the successful denser V9 attack timing while restoring historical target state durations. They are part of the prospectively frozen intervention, not fallback corrections.

## Empirical gate already frozen

A future empirical V11 execution would require exact V9 control reproduction first.

The state-semantics hypothesis would then require all frozen material-recovery conditions, including:

- common precision gain >= **+0.15**
- common F1 gain >= **+0.10**
- common recall decline <= **0.05**
- common joint-admission decline <= **0.05**
- common negative FP <= **0.10/s**
- frozen-V9 test F1 decline <= **0.05**
- exactly 500 updates/model
- exactly 2 models
- no threshold search or scientific retry

There is no V2B stage.

## Current execution counts

- waveform renders: **0**
- models trained: **0**
- optimizer steps: **0**
- model inference: **0**
- V2B inference: **0**

The authorization that opened V11 was used for prospective definition and model-free preflight only. A fresh explicit authorization after this frozen contract/preflight is required before empirical rendering or training.
