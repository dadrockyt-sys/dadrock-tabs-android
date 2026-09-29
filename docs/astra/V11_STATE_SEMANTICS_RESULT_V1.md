# V11 state-duration / legato-continuation result V1

Date: 2026-09-29 UTC  
Status: **COMPLETE — STATE-SEMANTICS HYPOTHESIS NOT SUPPORTED**

The explicitly authorized V11 synthetic-only study executed once under launch identity `v11-state-semantics-v1-20260929-01`.

The control reproduced the frozen V9 failure exactly. The intervention then preserved every attacked `(string, fret, onset)` tuple while restoring historical S0 family-duration targets and 84 non-attacked legato continuation events.

The prospectively frozen material-recovery gate did **not** pass.

## Execution identity

- run **36534741201**
- job **109296097761**
- head `0c3a24ab7d49a3b4525a2af372c2fbcf08fbccd6`
- workflow conclusion **success**
- artifact **11018510069**
- artifact digest `sha256:5cb15fcbb40b38bcee93e6bde1b4f4109204c9b979dcfb17910a25d2fe66bb91`
- artifact retained through **2026-10-29**
- models **2**
- optimizer steps **1,000 total**
- threshold search **false**
- automatic scientific retries **0**
- real-audio inference **0**
- V2B inference **0**

## Identity controls

Both 4-second arms preserved:
- **1,638** acoustic attack groups
- **1,806** attacked note labels
- exact attacked signature `9129b31cec8c56a8275e269b25fd9ab686b15f91e8b5da711ef6490eddfffe97`
- identical positive-onset frame identities
- **17,676** sampled attacked note labels/model
- **16,000** sampled attack frames/model
- **64,000** sampled frames/model
- **500** updates/model

The intervention added **84** non-attacked legato continuation events. Historical duration targets were truncated at **789** same-string retriggers under the prospectively frozen rule.

## Frozen V9 reproduction — PASS

The V11 control reproduced the frozen common comparator-test result exactly:

| Metric | Frozen V9 | V11 control |
|---|---:|---:|
| Precision | 0.324427 | 0.324427 |
| Recall | 0.658915 | 0.658915 |
| F1 | 0.434783 | 0.434783 |

This validates the control path.

## Primary common comparator-test population

| Metric | V11 control | State semantics restored | Delta |
|---|---:|---:|---:|
| Precision | 0.324427 | **0.353982** | **+0.029555** |
| Recall | 0.658915 | 0.620155 | **-0.038760** |
| F1 | 0.434783 | **0.450704** | **+0.015922** |
| State admission | 0.310078 | 0.263566 | -0.046512 |
| Onset admission | 0.682171 | 0.689922 | +0.007752 |
| Joint admission | 0.286822 | 0.255814 | -0.031008 |
| Negative FP/s | 0.0 | 0.0 | 0.0 |

Frozen support requirements:
- precision gain >= +0.15: **FAIL**
- F1 gain >= +0.10: **FAIL**
- recall decline <=0.05: PASS
- joint-admission decline <=0.05: PASS
- negative FP/s <=0.10: PASS

The primary precision and F1 gains were positive but small: roughly **+3.0 precision points** and **+1.6 F1 points**, far below the preregistered material-recovery thresholds.

## Secondary frozen-V9 test population

| Metric | V11 control | State semantics restored | Delta |
|---|---:|---:|---:|
| Precision | 0.486631 | 0.438144 | -0.048487 |
| Recall | 0.705426 | 0.658915 | -0.046512 |
| F1 | 0.575949 | 0.526316 | **-0.049634** |
| State admission | 0.286822 | 0.317829 | +0.031008 |
| Onset admission | 0.662791 | 0.635659 | -0.027132 |
| Joint admission | 0.279070 | 0.294574 | +0.015504 |

The frozen secondary F1-decline ceiling was 0.05; the observed decline was **0.049634**, so that check passed narrowly.

## Sampler-domain change caused by state semantics

Positive-onset stratum size stayed identical at **1,170** frames.

State-duration restoration changed non-positive frame membership, as expected:
- active-non-onset: **10,444 → 13,872**
- negative-structure inactive: **10,868 → 8,758**
- other inactive: **13,848 → 12,530**

This is not a hidden sampler change. The sampler algorithm remained fixed; the state targets changed which frames belonged to the non-positive strata.

## Decision

**The V11 state-duration / legato-continuation hypothesis is not supported.**

Restoring the historical family-duration targets plus the omitted legato continuation did not materially recover the large V9 common-population precision/F1 loss.

This weakens the idea that the V9 failure can be explained primarily by the state-duration/continuation discrepancy.

It does **not** establish the true cause. The remaining unresolved package differences include:
- 4-second versus 2-second temporal/context distribution;
- V9 attack-count allocation across families;
- gap distribution and longer-range clip structure;
- interaction between changed state occupancy and the fixed four-stratum sampler;
- other correlations introduced by moving from the historical 2-second package to the dense V9 package.

No V2B evaluation, threshold search, post-hoc retuning, V11 rerun, or automatic next experiment is permitted.

## Artifact hashes

- artifact ZIP: `5cb15fcbb40b38bcee93e6bde1b4f4109204c9b979dcfb17910a25d2fe66bb91`
- `result.json`: `993e02b43a950072f7e31b4e8075c0a635410747f186f1e963595ca481046a73`
- execution receipt: `eaeb365202f0b2b31e6b347a096763da596bff4caf51dcdc51b3c747b0087a55`
- control checkpoint: `043d272e22bcb273b3bce6c31c4b561b7e47741cfb242f6b8d419c1c7dc18bb7`
- intervention checkpoint: `3a998c7d19e8e3daecca0f624c9f3133824f9f72c30b20c6d1596d2964d91b69`

## Current stop boundary

- V9 remains frozen FAIL at synthetic sanity.
- V10 remains complete; chord-enriched exposure matching did not materially rescue V9.
- V11 is complete; state-duration/legato restoration did not materially rescue V9.
- V2B was not run.
- V1.1/P1/P2/P3 remain untouched.
- A2 remains closed.
- main/Production unchanged.

Any next study must be prospectively defined as a new project and separately authorized. No automatic V12 is created by this result.
