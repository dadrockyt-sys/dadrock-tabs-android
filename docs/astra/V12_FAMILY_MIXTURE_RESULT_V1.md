# V12 positive-onset family-mixture result V1

Date: 2026-09-29 UTC  
Status: **COMPLETE — FAMILY-MIXTURE HYPOTHESIS NOT SUPPORTED**

The explicitly authorized V12 synthetic-only study executed once under launch identity `v12-family-mixture-v1-20260929-01`.

The control reproduced the frozen V9 failure exactly. The intervention then changed only positive-onset frame selection to the frozen historical comparator family mixture while keeping the same regenerated V9 arrays, all non-positive selections, per-step shuffle, model, loss, thresholds, optimizer, and step count fixed.

The prospectively frozen support gate did **not** pass.

## Execution identity

- run **36537632082**
- job **109305235382**
- head `d08dd9dc0f8318e094070cc96e30bf8713d581e7`
- workflow conclusion **success**
- artifact **11018959307**
- artifact digest `sha256:1085e801d644b52a48e007f200334ccf4a5fe3c1ed753ae90533a1b58482fa6d`
- artifact retained through **2026-10-29**
- models **2**
- optimizer steps **1,000 total**
- threshold search **false**
- automatic scientific retries **0**
- real-audio inference **0**
- V2B inference **0**

## Control reproduction — PASS

The V12 control reproduced the frozen V9 common comparator-test metrics exactly:

| Metric | Frozen V9 | V12 control |
|---|---:|---:|
| Precision | 0.324427 | 0.324427 |
| Recall | 0.658915 | 0.658915 |
| F1 | 0.434783 | 0.434783 |

Control batch-plan SHA-256:

`8995265eb96a3a9833c9d1620eea1620a6a50914280aacd00474486f0508d4d7`

## Family-mixture identity

Control positive-onset slots actually sampled:
- isolated **2,013**
- scales **3,314**
- chords **838**
- repeated **3,306**
- legato **1,661**
- palmmute **4,089**
- mixed-positive **779**

Frozen historical-mixture intervention:
- isolated **914**
- scales **3,657**
- chords **1,829**
- repeated **3,657**
- legato **914**
- palmmute **4,572**
- mixed-positive **457**

Intervention batch-plan SHA-256:

`fa9146d23f67084edb683c889d273a2fc55d2a036c7f858418c92d9329812e0c`

All non-positive selections and the per-step shuffle were identical across arms.

## Linked attacked-note-label exposure

Both arms used exactly 16,000 positive-onset frames and 64,000 total sampled frames.

Because chord onset frames have three attacked labels, the family-mixture intervention changed attacked-note-label exposure as prospectively acknowledged:

- control: **17,676**
- historical mixture: **19,658**
- increase: **1,982 labels** (**11.21%**)

This is a downstream consequence of the family-mixture intervention, not a separate controlled variable.

## Primary common comparator-test result

| Metric | V12 control | Historical family mixture | Delta |
|---|---:|---:|---:|
| Precision | 0.324427 | **0.342205** | **+0.017778** |
| Recall | 0.658915 | **0.697674** | **+0.038760** |
| F1 | 0.434783 | **0.459184** | **+0.024401** |
| State admission | 0.310078 | 0.333333 | +0.023256 |
| Onset admission | 0.682171 | 0.751938 | +0.069767 |
| Joint admission | 0.286822 | 0.333333 | +0.046512 |
| Negative FP/s | 0.0 | **0.166667** | **+0.166667** |

Frozen support requirements:
- precision gain >= +0.15: **FAIL**
- F1 gain >= +0.10: **FAIL**
- recall decline <=0.05: PASS
- negative-only FP <=0.10/s: **FAIL**

The intervention improved recall, admission, and F1 modestly, but the precision/F1 gains were far below the material-recovery thresholds and negative-only false positives exceeded the ceiling.

## Secondary frozen-V9 test population

| Metric | V12 control | Historical family mixture | Delta |
|---|---:|---:|---:|
| Precision | 0.486631 | 0.470284 | -0.016347 |
| Recall | 0.705426 | 0.705426 | 0.000000 |
| F1 | 0.575949 | 0.564341 | **-0.011608** |
| State admission | 0.286822 | 0.310078 | +0.023256 |
| Onset admission | 0.662791 | 0.678295 | +0.015504 |
| Joint admission | 0.279070 | 0.294574 | +0.015504 |

The frozen V9-test F1-decline ceiling of 0.05 passed.

## Decision

**The V12 positive-onset family-mixture hypothesis is not supported.**

Restoring the historical comparator family mixture within the positive-onset sampler did not materially recover the V9 common-population precision/F1 collapse. It produced a modest recall/F1 improvement but also introduced negative-only false positives at **0.1667/s**, above the frozen **0.10/s** ceiling.

This further weakens a simple family-mixture explanation for V9.

It does not identify the true cause. Remaining unresolved factors include:
- 4-second versus 2-second inactive/background context distribution;
- longer-range gap/sequence structure not represented by marginal timing statistics;
- interactions among duration, family mix, negative/background context and the fixed four-stratum sampler;
- possibly the 2-second versus 4-second corpus construction itself as a composite domain shift.

No post-hoc threshold tuning, sampler retuning, V12 rerun, V2B bypass, or automatic next experiment is permitted.

## Artifact hashes

- artifact ZIP: `1085e801d644b52a48e007f200334ccf4a5fe3c1ed753ae90533a1b58482fa6d`
- `result.json`: `4a5bf0f25b66ff8a842ae1fd8d434859b8769791fe109c51a049f5ff1bb76d91`
- execution receipt: `71dca6e919295947173db6af2481a06821ce49c3bef669bd87a3a51bb7e9e94c`
- control checkpoint: `da8d334c77790033b35fe6a3df3e70683b3a41b8f9e54b85f022b56f4de4f821`
- intervention checkpoint: `4b4aca670d4477fcb4c7d0f0e6fe5724d3ec802043ab04dd85c0513adb5fef3b`

## Current stop boundary

- V9 remains frozen FAIL at synthetic sanity.
- V10 remains frozen; exposure-matching did not materially rescue V9.
- V11 remains frozen; state-semantics restoration did not materially rescue V9.
- V12 is complete; historical positive-onset family-mixture restoration did not materially rescue V9.
- V2B was not run.
- main/Production unchanged.

Any next causal study must be prospectively defined and separately authorized. No automatic V13 is created by this result.
