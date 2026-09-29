# Post-V12 causal review V1

Date: 2026-09-29 UTC  
Status: **DOCUMENTATION/REVIEW ONLY — NO V13 OPENED**

This review obeys the current generic-continue boundary. No waveform rendering, model training, inference, workflow dispatch, V2B evaluation, or production mutation was performed.

## Main finding

After V12, the cleanest unresolved sampler-domain difference is no longer the positive-onset family mixture. It is the **family composition inside the active-non-onset stratum**.

The four-stratum sampler always draws exactly 32 frames from each stratum per update. Therefore top-level stratum weights are fixed at 25% each. What changes between the historical 2-second comparator and executed V9 is the **family distribution within each stratum**.

That distinction is important: stratum-size differences by themselves do not change the 32/32/32/32 sampler weights, but within-stratum family composition changes which kinds of examples are seen.

## Exact historical comparator stratum sizes

Using the frozen S0 target construction, 87 frames/clip, train bases 0-9, three variants/base, and the exact S1 stratum definitions:

- positive-onset: **525**
- active-non-onset: **8,220**
- negative-structure inactive: **4,635**
- other inactive: **4,890**

Executed V9, as already measured in V12:
- positive-onset: **1,170**
- active-non-onset: **10,444**
- negative-structure inactive: **10,868**
- other inactive: **13,848**

Again, those absolute sizes do not alter the fixed per-step 32-frame draw from each stratum. They alter diversity/replacement pressure and family mix within strata.

## Active-non-onset family composition

Historical comparator active-non-onset frames:

| Family | Frames | Share |
|---|---:|---:|
| isolated | 1,290 | 15.69% |
| scales | 1,320 | 16.06% |
| chords | 1,140 | 13.87% |
| repeated | 1,470 | 17.88% |
| legato | 1,560 | 18.98% |
| palmmute | 900 | 10.95% |
| mixed-positive | 540 | 6.57% |
| **total** | **8,220** | **100%** |

Executed V9 active-non-onset frames:

| Family | Frames | Share |
|---|---:|---:|
| isolated | 1,215 | 11.63% |
| scales | 2,079 | 19.91% |
| chords | 788 | 7.55% |
| repeated | 2,140 | 20.49% |
| legato | 1,163 | 11.14% |
| palmmute | 2,487 | 23.81% |
| mixed-positive | 572 | 5.48% |
| **total** | **10,444** | **100%** |

Largest share shifts from historical comparator to V9:
- palmmute: **+12.86 percentage points**
- legato: **-7.84 points**
- chords: **-6.32 points**
- isolated: **-4.06 points**
- scales: **+3.85 points**
- repeated: **+2.61 points**
- mixed-positive: **-1.09 points**

This is a larger and more structured redistribution than the other inactive family mixtures.

## Frozen historical active-non-onset target over 16,000 sampled slots

Because 32 active-non-onset frames are sampled over 500 updates, there are exactly **16,000 active-non-onset training slots** per model.

Matching historical active-non-onset family proportions with deterministic largest-remainder allocation gives:

- isolated **2,511**
- scales **2,569**
- chords **2,219**
- repeated **2,861**
- legato **3,037**
- palmmute **1,752**
- mixed-positive **1,051**
- total **16,000**

A future intervention could therefore change only which active-non-onset frames are selected while preserving:
- the exact V9 positive-onset selections;
- exact negative-structure-inactive selections;
- exact other-inactive selections;
- exact per-step shuffle;
- exact V9 dataset arrays;
- exact attacked-note-label exposure;
- exact optimizer/model/loss/threshold settings.

That is cleaner than V12 because it would **not** alter positive-onset family mix or attacked-note-label exposure.

## Negative-structure inactive composition

Historical comparator:
- legato **1,020 / 4,635 = 22.01%**
- palmmute **1,560 / 4,635 = 33.66%**
- mixed **2,055 / 4,635 = 44.34%**

Executed V9:
- legato **3,907 / 10,868 = 35.95%**
- palmmute **2,403 / 10,868 = 22.11%**
- mixed **4,558 / 10,868 = 41.94%**

Largest shifts:
- legato **+13.94 points**
- palmmute **-11.55 points**
- mixed **-2.40 points**

This is also substantial and may matter for false-positive control, but it is a less direct first target than active-non-onset because the primary V9 failure includes a large precision/state-admission mismatch and the model jointly learns active state and onset.

## Other-inactive composition

Historical comparator:
- isolated 26.38%
- scales 23.93%
- chords 28.83%
- repeated 20.86%

Executed V9:
- isolated 27.62%
- scales 20.73%
- chords 31.35%
- repeated 20.29%

These differences are comparatively modest.

## Interpretation of V12 in this context

V12 changed only the positive-onset family mixture and produced:
- common precision +0.0178
- common recall +0.0388
- common F1 +0.0244
- negative FP/s +0.1667

That modest gain does not support positive-onset family mix as the main explanation.

The fixed positive-onset intervention left the V9 active-non-onset, negative-inactive, and other-inactive family compositions untouched.

Therefore V12 does not address the strongest remaining active-state family redistribution.

## Preferred next project question, if later authorized

Do **not** open V13 automatically.

Preferred prospective question:

> With the exact executed V9 dataset and exact V9 batch plan fixed everywhere else, does matching only the historical comparator **active-non-onset family mixture** materially recover common-population precision/F1 without increasing negative-only false positives?

Clean operational design:
- no new rendering;
- no timing generation;
- no state-semantic regeneration;
- both arms use identical regenerated executed-V9 arrays;
- control reproduces exact V9 batch plan;
- intervention replaces only active-non-onset selections;
- exactly 16,000 active-non-onset slots per arm;
- frozen historical target allocation: 2,511 / 2,569 / 2,219 / 2,861 / 3,037 / 1,752 / 1,051 by family;
- positive-onset selections identical;
- negative-structure-inactive selections identical;
- other-inactive selections identical;
- per-step shuffle identical;
- attacked-note-label exposure identical by construction;
- same model, initialization, losses, thresholds, optimizer, 500 updates;
- primary eval remains common 2-second comparator test;
- secondary eval remains frozen V9 test;
- no V2B.

This would isolate a training-distribution factor that directly affects state learning while avoiding the label-exposure confound present in V10/V12.

## Secondary future question

If active-non-onset mixture fails, the next cleaner single factor would be the negative-structure-inactive family mixture:
- historical 16,000-slot target:
  - legato **3,521**
  - palmmute **5,385**
  - mixed **7,094**

That study should remain separate rather than combining both non-positive strata in one intervention.

## Current evidence ladder

Direct diagnostics now weaken simple explanations based on:
- marginal common-unit attack timing;
- attacked-note-label exposure alone;
- state-duration / legato-continuation semantics alone;
- positive-onset family mixture alone.

The remaining evidence increasingly points toward **within-stratum context/domain composition** rather than one simple attack-side statistic.

This remains a synthetic-only inference. No real-transfer claim is justified.

## Stop boundary

No V13 contract, authorization, runner, workflow, launch, or model execution was created.

Execution counts for this review:
- waveform renders **0**
- models trained **0**
- optimizer steps **0**
- model inference **0**
- V2B inference **0**
- workflow dispatches **0**

Main/Production unchanged.

At a future explicit authorization to open a new project, prospectively define/freeze the active-non-onset family-mixture study first. Empirical execution would still require fresh authorization after its contract/preflight is visible.
