# Post-V11 causal review V1

Date: 2026-09-29 UTC  
Status: **DOCUMENTATION/REVIEW ONLY — NO V12 OPENED**

This review obeys the current generic-continue boundary. No waveform rendering, optimizer step, model inference, workflow dispatch, real-audio access, or V2B evaluation was performed.

## Main finding

After V10 and V11, the cleanest unresolved difference is now the **family composition of the positive-onset training stratum**.

The S1/V9/V10/V11 training policy samples exactly 32 positive-onset frames per update. Within that stratum, frame selection is uniform. Therefore the number of attack frames contributed by each family directly determines how often that family appears in the positive-onset gradient stream.

V9 changed that composition substantially when it changed attack counts per clip.

## Historical 2-second comparator positive-onset composition

For the 10 training bases per ordinary family and 5 positive mixed bases, the historical 2-second comparator contains:

| Family | Train positive-onset frames | Share |
|---|---:|---:|
| isolated | 30 | 5.714% |
| scales | 120 | 22.857% |
| chords | 60 | 11.429% |
| repeated | 120 | 22.857% |
| legato | 30 | 5.714% |
| palmmute | 150 | 28.571% |
| mixed-positive | 15 | 2.857% |
| **total** | **525** | **100%** |

These proportions are the same as the whole retained comparator attack-group proportions because the train split preserves the base-family construction.

## Executed V9 positive-onset composition

The executed V9 4-second training set contains exactly 1,170 positive-onset frames, matching the V11 empirical stratum report:

| Family | Train positive-onset frames | Share |
|---|---:|---:|
| isolated | 150 | 12.821% |
| scales | 240 | 20.513% |
| chords | 60 | 5.128% |
| repeated | 240 | 20.513% |
| legato | 120 | 10.256% |
| palmmute | 300 | 25.641% |
| mixed-positive | 60 | 5.128% |
| **total** | **1,170** | **100%** |

Largest shifts versus the historical comparator:
- isolated: **+7.106 percentage points**
- chords: **-6.300 points**
- legato: **+4.542 points**
- mixed-positive: **+2.271 points**
- palmmute: **-2.930 points**
- scales/repeated: each **-2.344 points**

This is not merely a dataset-count observation. Because the sampler takes a fixed 32 positive-onset frames every update, these proportions directly alter expected positive-onset training exposure.

## Expected 16,000 positive-onset slots under current V9 sampling

Across 500 updates x 32 positive-onset slots, uniform V9 sampling implies approximately:

| Family | Expected slots |
|---|---:|
| isolated | 2,051.3 |
| scales | 3,282.1 |
| chords | 820.5 |
| repeated | 3,282.1 |
| legato | 1,641.0 |
| palmmute | 4,102.6 |
| mixed-positive | 820.5 |

By contrast, matching the historical comparator family proportions over exactly 16,000 slots would use a deterministic largest-remainder allocation:

| Family | Frozen historical-proportion slots |
|---|---:|
| isolated | 914 |
| scales | 3,657 |
| chords | 1,829 |
| repeated | 3,657 |
| legato | 914 |
| palmmute | 4,572 |
| mixed-positive | 457 |
| **total** | **16,000** |

This would approximately halve isolated exposure, more than double chord-frame exposure, reduce legato/mixed exposure, and increase scales/repeated/palmmute toward the historical comparator mixture.

## Why this is a stronger next question than another duration/timing change

V9 established that the new attack timing can satisfy the common-unit timing target.

V10's chord-enriched attacked-label-count intervention gave only a tiny primary F1 gain, but it did not restore the full historical family mixture.

V11 restored state-duration/legato semantics and also gave only a small primary gain.

The remaining family-mixture shift is directly coupled to the frozen onset-aware sampler and is large enough to affect thousands of positive-onset samples over 500 updates.

The same V9 model also continues to perform much better on its own V9-domain test than on the old common 2-second test, which remains consistent with a training-distribution mismatch rather than a simple failure to learn onsets at all.

## Preferred next project question, if later authorized

Do **not** open V12 automatically.

The preferred prospective question is:

> With the exact executed V9 dataset, attack timing, state semantics, model, loss, thresholds, optimizer, total positive-onset slots, and all non-positive batch selections fixed, does matching the historical comparator **positive-onset family mixture** materially recover common-population precision/F1?

The cleanest operational intervention would:
- train both arms on the exact same executed V9 dataset arrays;
- control arm reproduces the exact V9 batch plan;
- intervention replaces only the 32 positive-onset selections per update;
- total positive-onset slots remain exactly 16,000;
- intervention uses the frozen historical-proportion totals listed above;
- all active-non-onset, negative-structure-inactive, and other-inactive selections remain exactly identical;
- same per-step 128-frame shuffle;
- same initialization, model, losses, thresholds, optimizer, and 500 updates;
- no rendering and no timing/state regeneration;
- primary evaluation remains the common 2-second comparator test;
- secondary evaluation remains the frozen V9 test;
- no V2B stage.

### Important qualification

This would be a **family-mixture intervention**, not a pure attacked-note-label-count intervention.

Chord onset frames contain three attacked note labels, so restoring historical chord-frame share will also raise attacked-note-label exposure as a downstream consequence. That linked change must be reported, not hidden.

A stronger implementation could prospectively report both:
- positive-onset frame exposure by family;
- attacked-note-label exposure by family and total.

The causal claim would remain limited to the historical positive-onset family-mixture package.

## Alternative smaller diagnostic

If a future study wants to avoid changing which positive-onset examples are selected, a separate design could keep the exact V9 batch indices and apply a preregistered family-specific gradient weight to positive-onset samples.

That would isolate family weighting more directly, but it changes the loss function and is less directly comparable to the existing sampler. It should be a separate project choice, not mixed into the preferred resampling study.

## What is now weakened

The evidence now weakens these simple explanations for V9's primary precision/F1 collapse:
- raw common-unit timing mismatch;
- attacked-note-label exposure deficit alone;
- historical state-duration/legato-continuation omission alone.

None is ruled out as part of interactions, but none produced a material rescue in its executed diagnostic.

## What remains unresolved

Most important unresolved factors:
1. positive-onset family composition under the fixed four-stratum sampler;
2. 4-second versus 2-second inactive/background context diversity;
3. family-specific gap/sequence structure beyond marginal timing statistics;
4. interactions among family composition, state occupancy, and onset/state losses.

The positive-onset family composition is the most directly testable next factor because it can be changed without any new audio rendering or timing generation.

## Stop boundary

No V12 contract, runner, workflow, or authorization file was created.

Execution counts for this review:
- waveform renders: **0**
- models trained: **0**
- optimizer steps: **0**
- model inference: **0**
- V2B inference: **0**
- workflow dispatches: **0**

V1.1/P1/P2/P3/A2 untouched. Main/Production unchanged.

At a future explicit authorization to open a new project, prospectively define and freeze the family-mixture study before any empirical execution.
