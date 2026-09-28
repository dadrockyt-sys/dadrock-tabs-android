# Astra synthetic data diversity S9 design V1

Date: 2026-09-28
Status: **DESIGN FROZEN — NOT AUTHORIZED FOR MODEL EXECUTION**

## Question

With clip count, timbre exposure, sampler, model and optimization fixed, does increasing the number of unique **training chord voicings** from 10 to 30 improve chord generalization and state/joint admission?

This tests one variable: **training chord voicing diversity**.

## Why S9

S8 nearly tripled sampled 3-string attack frequency but chord F1 and recall fell.

Therefore repeated exposure to the existing 10 chord voicings is rejected as the next path.

## Model and training fixed

Both arms use the S6 nonlinear replacement state head:

- shared encoder: Linear(960,128) -> ReLU;
- state head: Linear(128,128) -> ReLU -> Linear(128,126);
- onset head: Linear(128,6);
- active-state weight 9.0;
- onset BCE pos_weight 8.0;
- onset loss multiplier 4.0;
- original uniform 32/32/32/32 onset-aware sampler;
- Adam lr 0.003;
- batch size 128;
- exactly 500 optimizer steps;
- thresholds 0.50 / 0.50;
- decoder V2;
- identical model initialization;
- identical flattened minibatch indices;
- zero threshold search/retuning.

## Dataset arms

Both datasets contain exactly 294 clips / 588 seconds.

Validation and test arrays are bit-identical across arms.

Every non-chord clip is bit-identical across arms.

Only the 30 **training chord clips** differ in voicing assignment.

### Control dataset

Frozen S0 chord training structure:
- 10 unique chord templates;
- each template appears under variants 0, 1 and 2;
- 30 training chord clips total.

### Intervention dataset

- 30 unique deterministic chord voicings;
- exactly 30 training chord clips total;
- timbre-condition counts remain 10 x variant 0, 10 x variant 1, 10 x variant 2.

Each intervention chord clip is paired with one control chord slot.

The paired intervention clip must use the same deterministic **timbre RNG key** as the control slot, so damping, pick-position, brightness, body-filter/noise RNG stream and timbre condition are matched. Only the chord string/fret voicing changes.

Each intervention chord template retains:
- exactly three strings;
- attacks at 0.32 s and 1.08 s;
- six note events total;
- 0.48 s note durations;
- identical attack/negative-structure semantics.

No family label is used by training.

## Unique-voicing construction

Generate 30 deterministic intervention chord signatures from the root seed.

A chord signature includes:
- the ordered three-string set;
- all six fret assignments across the two attacks.

Fail closed unless all 30 signatures are unique and none equals another intervention signature.

Record hashes of the ordered signature list.

## Required dataset identity checks

Before optimizer work, fail closed unless:

1. both datasets contain 294 clips / 588 s;
2. train/validation/test counts are 210 / 42 / 42 in both;
3. exactly 30 training chord clips exist in each;
4. control has exactly 10 unique training chord signatures;
5. intervention has exactly 30 unique training chord signatures;
6. validation/test feature/state/onset/reference arrays are bit-identical;
7. all non-chord feature/state/onset/reference arrays are bit-identical;
8. chord train frame/onset event counts are identical;
9. paired timbre RNG keys are identical slot-by-slot;
10. intervention unique-signature hash is frozen.

## Batch identity

The chord timing/active-frame structure is unchanged, so the four sampler strata must have identical flattened membership across datasets.

Precompute one 500-batch plan and use the exact same flattened indices for both models.

Fail if stratum membership differs.

## Required measurements

Report validation and test:
- overall pitch-onset TP/FP/FN, precision, recall, F1;
- onset+offset F1;
- repeated-note recall;
- family-level onset metrics;
- chord precision/recall/F1;
- negative-only FP/sec;
- exact onset/state/joint admission;
- true-state and silence probability/margins;
- optimizer steps/runtime;
- dataset hashes, unchanged-subset hashes, voicing-signature hashes and batch-plan hash.

## Frozen S9 success criteria

All must pass:

1. chord onset F1 gain >= **+0.15**;
2. chord recall gain >= **+0.15**;
3. exact state-admission gain >= **+0.05**;
4. exact joint-admission gain >= **+0.04**;
5. overall onset recall gain >= **+0.03**;
6. overall onset F1 gain >= **+0.025**;
7. absolute chord F1 >= **0.45**;
8. absolute state admission >= **0.42**;
9. absolute onset recall >= **0.65**;
10. absolute onset F1 >= **0.74**;
11. repeated recall >= **0.55**;
12. onset precision >= **0.82**;
13. onset+offset F1 decline <= **0.03**;
14. negative-only FP <= **0.10 events/s**;
15. no non-chord supported family loses > **0.15 F1**;
16. both models finish <=500 steps with finite metrics, exact model init, identical batch indices, identical validation/test and non-chord data, fixed thresholds and zero threshold search.

These are S9 development criteria only and do not revise S0-S8 gates.

## Decision branches

- **All pass:** chord voicing diversity is supported as a meaningful synthetic-data contributor. Stop and design a separate synthetic competence confirmation before any P1/P2 transfer.
- **Chord improves but global/state floors fail:** diversity helps polyphony but remains insufficient; stop.
- **No chord gain:** reject chord-voicing diversity as the next primary lever.
- **Non-chord/precision stability collapses:** reject the intervention.
- **Any dataset identity/runtime failure:** freeze and stop; zero automatic model retry.

## Hard ceiling if later authorized

- exactly two 294-clip synthetic datasets, each 588 s logical duration;
- render only the 30 replacement intervention chord training clips in addition to the frozen/control generation needed for the paired run;
- total rendering <=20 CPU minutes;
- exactly 2 models;
- 500 optimizer steps/model, 1,000 total;
- fit/eval <=60 CPU minutes;
- $0 paid compute;
- zero automatic model retries;
- no threshold tuning;
- no P1/P2/P3;
- no Codespaces;
- no Vercel;
- no deployment/main/customer delivery.

## Authorization boundary

S9 requires fresh explicit authorization before any model execution.
