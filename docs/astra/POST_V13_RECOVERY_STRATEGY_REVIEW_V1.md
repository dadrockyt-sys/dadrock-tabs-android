# Post-V13 recovery strategy review V1

Date: 2026-09-29 UTC  
Status: **MODEL-FREE REVIEW COMPLETE — NO V14 OPENED**

This review follows the recovery-first supervisory instruction. It used committed source, contracts, and frozen result summaries only. It performed no waveform rendering, model loading, optimizer work, inference, V2B evaluation, P1/P2/P3 access, or Production mutation.

## Executive decision

Stop serial one-factor sampler-mixture studies.

The original V9 common-population failure is too large for the recent marginal interventions to count as meaningful recovery:

- successful 2-second comparator F1: **0.7381974249**
- executed V9 common-test F1: **0.4347826087**
- original deficit: **0.3034148162 F1**
- successful comparator precision: **0.8269230769**
- executed V9 precision: **0.3244274809**
- original precision deficit: **0.5024955960**

V10-V13 recovered only small fractions of that F1 gap. The next empirical project, if explicitly opened later, should therefore be a **2-second matched-context bridge** rather than another marginal family-mixture restoration.

## V9-V13 recovery table

All primary metrics below are on the same frozen 2-second common comparator test.

| Version | Changed package | Precision | Recall | F1 | F1 delta vs V9 control | Fraction of original F1 deficit recovered | State admission | Onset admission | Joint admission | Negative FP/s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| successful 2-s comparator | historical 2-s package | 0.826923 | 0.666667 | 0.738197 | +0.303415 | 100% reference | 0.294574 | 0.620155 | 0.286822 | 0 |
| V9 control/intervention baseline | 4-s V9 package | 0.324427 | 0.658915 | 0.434783 | 0 | 0% | 0.310078 | 0.682171 | 0.286822 | 0 |
| V10 | chord-enriched attacked-label exposure matching | 0.348624 | 0.589147 | 0.438040 | +0.003258 | **1.07%** | 0.271318 | 0.666667 | 0.255814 | 0 |
| V11 | historical state-duration / legato-continuation restoration package | 0.353982 | 0.620155 | 0.450704 | +0.015922 | **5.25%** | 0.263566 | 0.689922 | 0.255814 | 0 |
| V12 | historical positive-onset family mixture | 0.342205 | 0.697674 | 0.459184 | +0.024401 | **8.04%** | 0.333333 | 0.751938 | 0.333333 | **0.166667** |
| V13 | historical active-non-onset family mixture | 0.336066 | 0.635659 | 0.439678 | +0.004896 | **1.61%** | 0.263566 | 0.674419 | 0.240310 | 0 |

The percentages are each intervention's F1 improvement divided by the frozen V9-to-comparator deficit of 0.3034148162. They are not additive because the studies are separate interventions.

V12 produced the largest F1 movement, but it still recovered only about 8% of the original deficit and violated the frozen negative-only false-positive ceiling. None of V10-V13 approached material restoration.

## Confirmed construction differences: successful 2-second comparator vs executed V9

### 1. Clip duration and frame-pool geometry — confirmed

Comparator:
- **2.0 s** per clip
- 294 clips
- 588 logical seconds

V9:
- **4.0 s** per clip
- 294 clips
- 1,176 logical seconds

The model still consumes local five-frame CQT context, but training-frame eligibility pools are built over all frames. Doubling clip duration therefore changes the number and composition of active/non-onset and inactive frames even when the four sampler strata remain 32 frames each per update.

### 2. Attack-count package — confirmed

Historical comparator attack groups per positive clip:
- isolated 1
- scales 4
- chords 2
- repeated 4
- legato 1
- palmmute 5
- mixed-positive 1

Executed V9 attack groups per positive clip:
- isolated 5
- scales 8
- chords 2
- repeated 8
- legato 4
- palmmute 10
- mixed-positive 4

Thus V9 did not simply stretch the same events across twice the duration. Several families gained multiple additional attacks and corresponding state segments.

### 3. Attack-to-left-edge context — confirmed

Historical comparator first attacks occur at approximately:
- 0.22 s scales
- 0.28 s repeated/legato/palmmute
- 0.32 s isolated/chords
- 0.36 s mixed-positive

V9 first attacks are deterministically drawn from **0.050–0.120 s**.

Therefore V9 positive attacks generally have substantially less pre-attack clip context than the comparator.

### 4. Gap and sequence construction — confirmed

Comparator uses fixed short family motifs such as:
- scales: 0.22, 0.58, 0.94, 1.30
- repeated: 0.28, 0.68, 1.08, 1.48
- palmmute: 0.28, 0.62, 0.96, 1.30, 1.64

V9 replaces these with deterministic S/M/L gap-class sequences, including:
- S 0.080–0.250 s
- M 0.251–0.316 s
- L 0.700–1.360 s

V9's timing gate successfully matched several marginal V2B attack statistics, but this necessarily changed higher-order sequence/run structure relative to the comparator.

### 5. State-duration semantics — confirmed

Historical comparator uses family-specific durations, including long isolated/mixed states and a legato non-attacked continuation.

Executed V9 gives attacked notes a deterministic sustain from **0.12–0.48 s** and, due to the implemented template filter, omits the historical non-attacked legato continuation. V11 tested a restoration package and produced only +0.015922 F1 on the common population, so state semantics alone did not rescue the regression.

### 6. Negative-structure temporal placement — confirmed and especially important

The shared renderer places the synthetic negative-structure burst at approximately **1.70 s** for both 2-second and 4-second clips.

Consequences:
- in a 2-second comparator clip, only about **0.30 s** remains after the burst;
- in a 4-second V9 clip, about **2.30 s** remains after the burst.

Thus V9 creates roughly two additional seconds of post-structure context in the same negative-structure families. This is not repaired by merely matching the family proportions inside the negative-structure-inactive sampler stratum.

### 7. Attack-to-right-edge and post-event context — confirmed

Comparator family motifs generally finish well before 2.0 s; for example historical palmmute's last attack is at 1.64 s.

V9 permits generated schedules as late as the frozen final-margin rule, with only **0.120 s** required after the final attack.

Therefore the two domains have different distributions of both pre-attack and post-attack context relative to clip boundaries.

### 8. Renderer, frontend, model and primary evaluation — controlled in V9

Within the V9 same-runtime comparison:
- both arms use the **R3** renderer;
- timbre initialization is based on the same historical template identity;
- both use frozen RMS normalization and the same CQT frontend;
- both use five-frame context;
- both use the same S6 nonlinear model package, loss, thresholds and optimizer settings;
- both are evaluated on the same frozen 2-second comparator test for the primary synthetic sanity comparison.

Therefore the large common-test difference cannot be explained by a different V9-vs-comparator evaluation population, threshold, model architecture, or renderer arm inside that paired run.

## Joint/context descriptors: what is established versus still missing

### Established from committed source/results

- V9 attack density and marginal IOI statistics were deliberately matched toward the common-unit V2B timing reference.
- V9 and comparator have different family-specific attack counts.
- V9 has different first-attack-to-left-edge distances.
- V9 has different family-specific state durations.
- V9 omits the historical non-attacked legato continuation in executed code.
- V9 creates much more post-negative-structure inactive context because the burst remains near 1.70 s while clip duration doubles.
- V9 has materially different stratum pool sizes and family composition inside multiple strata.
- The same V9-trained control performs much better on the V9-domain test than on the comparator-domain test (previous review: +0.141167 F1), consistent with synthetic-domain shift.

### Likely linked consequences, not isolated causes

- inactive run-length distributions differ;
- state-transition counts/window differ;
- family × state-stratum joint distributions differ;
- attack density conditional on family differs;
- context immediately before and after positive onsets differs;
- boundary proximity and long-gap placement interact with family and duration.

These are direct consequences expected from the confirmed source changes, but a committed machine-readable joint-descriptor table was not found for all of them.

### Unknown / not yet measured in one frozen table

- exact distribution of attack-to-window-edge distance over every rendered training frame;
- exact inactive run-length quantiles by family and stratum;
- exact state-transition-count distribution per clip;
- exact family × stratum × boundary-context joint table;
- exact overlap/polyphony distribution after all V9 sustain draws;
- exact conditional sequence descriptors immediately around sampled training frames.

These should be measured model-free from deterministic manifests/targets if the future V14 contract preparation needs them. Do not render audio or train a model merely to obtain these descriptors.

## Why the old proposed negative-structure-mixture V14 is no longer preferred

The negative-structure-inactive family redistribution is real and remains untested as an isolated variable. However, a sampler-only mixture correction would still draw frames from the executed V9 arrays, whose temporal geometry already differs substantially from the comparator.

In particular, it would not remove the extra ~2 seconds of post-burst context per 4-second negative-structure clip.

Given:
- a 0.303415 F1 primary deficit,
- four recent interventions recovering only ~1–8% individually,
- and confirmed whole-context geometry changes,

another one-factor family-mixture study has low information value relative to a matched-context bridge.

It remains an optional future diagnostic, not the default next project.

## One preferred future empirical project: V14 2-second matched-context bridge

**No V14 is opened by this review.**

If the user later explicitly authorizes a new project, prepare exactly one V14 design with this purpose:

> Test whether the successful V9 attack-timing principles can retain material benefit when returned to a 2-second comparator-like temporal/context construction.

This is a **package recovery experiment**, not a single-factor causal isolation.

### Preferred V14 design constraints

Keep fixed:
- 294 historical family/base/variant identities and train/validation/test split;
- 2.0-second clip duration;
- R3 renderer for both control and bridge;
- frozen RMS normalization and CQT frontend;
- S6 nonlinear model;
- five-frame input context;
- state/onset losses and weights;
- 0.50 / 0.50 thresholds;
- Adam learning rate 0.003;
- four 32-frame sampler strata;
- 500 updates/model;
- primary evaluation on the exact frozen common 2-second comparator test;
- no V2B or real-audio inference;
- no threshold/loss/seed search;
- no scientific retry.

Control:
- same-runtime historical 2-second comparator package.

Bridge intervention:
- 2-second clips only;
- retain the **principles** that made V9 timing successful: acoustic-attack-group accounting, deterministic first/gap construction, explicit short/medium/long gap support, no fallback repair, prospectively frozen timing identity;
- preserve comparator-like family/state semantics unless the final frozen bridge design explicitly documents a necessary difference;
- avoid the 4-second post-1.70-s inactive tail by construction;
- choose exactly one deterministic 2-second timing/count schedule prospectively, using model-free feasibility only;
- do not search several bridge schedules and select the best;
- record every remaining package difference from the control.

The exact 2-second per-family attack counts and feasible gap supports are **not** frozen by this review. They must be derived once during future V14 contract preparation from a model-free feasibility calculation and then frozen before any rendering or optimizer step. This prevents turning the recovery review itself into an undeclared parameter search.

## Prospective material-recovery gate for future V14 preparation

The original common-test F1 deficit is:

**0.7381974249 - 0.4347826087 = 0.3034148162**

A 50% recovery target corresponds to:

**F1 >= 0.5864900168**

The future V14 contract should use a recovery gate tied to the original deficit, not tiny positive movement. Recommended starting requirements to justify/freeze during contract preparation:

- common-test F1 **>= 0.5864900168**;
- common-test precision must recover a substantial preregistered fraction of the original 0.502496 precision deficit;
- recall decline versus the successful comparator constrained prospectively;
- negative-only FP/s **<= 0.10**;
- exact fixed model/update budget;
- finite metrics;
- no threshold search;
- no automatic scientific retry.

The exact precision/recall recovery thresholds must be justified and frozen before empirical execution.

## Hard stop rule after a future bridge

If an authorized V14 matched-context bridge fails to achieve material recovery:

1. do not open V15/V16 automatically;
2. stop serial synthetic micro-optimization;
3. freeze a decision brief choosing exactly one of:
   - larger synthetic-generator redesign;
   - a separately authorized independent real-development evaluation program;
   - pause this model line.

P1/P2 remain closed under the current boundary and P3 remains sealed.

## Current boundary

This review created documentation only.

Execution counts:
- waveform renders: **0**
- models trained: **0**
- optimizer steps: **0**
- model inference: **0**
- V2B inference: **0**
- P1/P2/P3 access: **none**
- workflow dispatches: **0**

Main and Production are unchanged.

**Resume instruction:** The next generic “continue” may prepare the prospective V14 matched-context bridge contract and model-free feasibility/preflight package only if that preparation is already authorized by the current handoff. Empirical rendering/training must remain behind a fresh explicit authorization after the full frozen contract/preflight is visible. Do not revert to the negative-structure-inactive mixture as the default V14.
