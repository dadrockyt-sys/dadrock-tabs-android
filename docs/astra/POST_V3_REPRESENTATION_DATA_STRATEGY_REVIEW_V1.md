# Astra post-V3 project-level representation/data strategy review V1

Date: 2026-09-28  
Status: **FINAL SOURCE-DOMAIN SYNTHETIC TRAINING FAILED — SYNTHETIC TUNING LINE CLOSED**

## Scope

This review follows the final admitted V3 source-domain challenge and the one preregistered V3 synthetic training experiment.

No model is loaded or trained here.
No waveform is rendered.
No thresholds, loss weights, sampler, architecture or decoder are changed.
P1/P2 remain closed.
P3 remains sealed.

## Frozen evidence considered

1. corrected P1/P2 model-free real-domain integrity audit V2;
2. real-domain failure localization V1;
3. S12 failed feature-space intervention;
4. S13 failed feature-space intervention;
5. source-domain simulator V1 training failure;
6. V2 joint-coverage model-free preparation and 34/35 failure;
7. V3 final model-free coverage pass, 35/35;
8. final V3 synthetic training result:
   - `docs/astra/SOURCE_DOMAIN_V3_SYNTHETIC_TRAINING_RESULT_V1.json`.

## What V3 established

The V3 model-free package removed the earlier known coverage objection:
- exact V2 training support retained;
- independently constructed 84-row V3 challenge;
- 12 challenge rows/family;
- 35/35 model-free family/descriptor support checks passed.

Therefore the final training failure cannot be dismissed as the same known V1/V2 challenge-support defect.

The final paired training result nevertheless failed the preregistered gate.

### Positive synthetic evidence

Across all three seeds, source-domain training improved V3 challenge pitch-onset F1:
- mean **+0.06114**;
- minimum **+0.05671**;
- positive **3/3**.

It also improved challenge onset recall in all three seeds:
- mean **+0.01809**;
- positive **3/3**.

Challenge precision improved substantially:
- mean **+0.11438**;
- positive **3/3**.

Ordinary clean onset F1 and recall also increased:
- F1 mean **+0.02066**;
- recall mean **+0.03101**.

This is evidence that the source-domain training distribution changes the model in a direction that can improve the onset event metric under independently admitted source variation.

### Failing evidence

The improvement was not sufficient or stable under the full task contract.

Failed frozen gates:
1. mean V3 challenge onset-recall gain >= +0.08:
   - observed **+0.01809**;
2. intervention V3 challenge negative-only FP <= 0.10 events/sec in every seed:
   - seed 20260928 observed **0.16667**;
3. no ordinary state-admission loss > 0.03:
   - mean loss **0.07752**;
   - every seed lost at least 0.0620;
4. no ordinary joint-admission loss > 0.04:
   - mean loss **0.06718**;
   - every seed lost at least 0.0620.

Challenge state/joint admission also moved downward:
- state admission mean delta **-0.03618**;
- joint admission mean delta **-0.04522**.

Thus the source-domain package did not produce a generally stronger transcription system. It improved one part of the event tradeoff while reducing state/joint admission and failing one negative-only guard.

## Interpretation

The evidence is now inconsistent with a simple claim that the main remaining problem is merely insufficient attack-envelope/source-domain coverage.

Source-domain diversity clearly affects onset robustness, but adequate model-free source coverage did not convert that into the required recall/state/joint robustness.

The frozen S11 model has two shallow heads sharing one 128-unit flattened five-frame encoder:
- state head;
- onset head.

The observed pattern is compatible with a task/representation tradeoff in the frozen model or objective, but **does not prove** architecture or loss coupling is the cause.

Other unresolved possibilities include:
- source simulator semantics still differ from real note-state evidence in ways not captured by the five admitted descriptors;
- frozen CQT/RMS representation may discard or normalize information needed jointly by state and onset heads;
- shallow context5 representation may not support both source-invariant onset cues and stable pitch/state admission;
- the synthetic labels/tasks may interact with source randomization differently from real guitar data.

The experiment cannot distinguish these.

## Why another synthetic tuning run is not justified

Do not use this result to:
- lower state/onset thresholds;
- rebalance the state/onset loss;
- change active-state weights;
- alter the 32/32/32/32 sampler;
- widen decoder windows;
- choose the best seed;
- weaken the recall/state/joint gates;
- create V4/V5 source-domain ranges/challenges;
- directly substitute a larger/deeper architecture and retry.

Those would be post-hoc optimizations against the final synthetic result.

The earlier project strategy allowed an architecture experiment only after the source-domain package passed the synthetic robustness gate. That condition was not met.

## Current scientific boundary

The repo-owned synthetic line has now answered what it can answer under the frozen S11 task/model:

- feature-space onset corruption was not a robust solution;
- physically broader source-domain variation can improve onset F1;
- model-free train/challenge source coverage can be made adequate;
- even with that coverage, the frozen model does not satisfy the joint onset/state/negative-control contract.

The remaining ambiguity cannot be resolved reliably by another synthetic tuning iteration using the same evidence.

## Next informative evidence

The next empirical program should be based on **new independent development evidence**, not another transformation of the current synthetic corpus.

Acceptable future paths are:

### A. Broader real development set

Acquire/use a prospectively defined real-guitar development set that is:
- independent of P3;
- broader than the already-exposed P1/P2 captures;
- balanced across note families, articulation, dynamics and source/acquisition variation;
- large enough to compare state and onset failure modes without fitting to eight bounded examples.

Before use, freeze:
- source/capture list;
- annotation contract;
- train/dev role;
- preprocessing/version;
- exact model-free diagnostics;
- whether any model evaluation/training is permitted.

This requires explicit authorization for the new real data.

### B. New architecture research track

A new architecture track may be designed only as a **new project version**, not a V3 rescue.

Before any optimizer work it must:
- define architectural hypotheses independently of V3 score tuning;
- keep the final V3 data result frozen;
- avoid tuning thresholds/loss/sampler simultaneously;
- establish model-free/structural reasons for the change;
- use a newly preregistered evaluation contract;
- remain synthetic-only until its own gate passes.

This review does not authorize such a model run automatically.

## P1/P2/P3 decision

Do not reopen P1/P2 to evaluate the failed V3 candidate.
That would consume real-domain evidence on a candidate that did not pass its prospective synthetic gate.

P3 remains sealed.

## Final decision

**NO-GO for additional source-domain synthetic tuning/model execution from the current evidence.**

The next empirical action requires one of:
- explicit authorization for a new broader real development set; or
- a separately approved new architecture research version with its own prospective contract.

Until then:
- freeze V3 failure;
- keep P1/P2 closed;
- keep P3 sealed;
- do not run another model automatically.
