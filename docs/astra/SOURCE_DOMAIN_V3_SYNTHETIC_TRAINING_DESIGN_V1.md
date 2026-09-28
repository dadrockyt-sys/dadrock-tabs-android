# Astra source-domain V3 synthetic training design V1

Date: 2026-09-28  
Status: **PROSPECTIVE SYNTHETIC-ONLY TRAINING DESIGN FROZEN**

## Question

Under the exact frozen S11 model/training/evaluation protocol, does training on the final admitted V2 source-domain training support improve robustness on the independently frozen V3 source-domain challenge while preserving ordinary clean synthetic competence?

This is the final source-domain synthetic training experiment authorized by the passed V3 model-free coverage admission.

It is synthetic-only development evidence. It cannot establish real-domain transfer.

## Frozen prerequisites

### V2 training support

Use the exact frozen V2 Stage-B intervention dataset:
- Stage-B artifact: **10999695803**
- intervention file SHA-256:
  `a17a16daeb8d698e325dc6820f18d5eda2fec75d9beebe2a9605a678124dc26b`
- 294 rows total;
- exactly 210 training rows source-domain rendered;
- validation/test features bit-identical to frozen control;
- all non-feature arrays bit-identical.

### Control

Use exact frozen S9 control:
- preparation artifact: **10993531230**
- file SHA-256:
  `16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894`

### V3 challenge

Use exact frozen V3 84-row standalone challenge:
- V3 artifact: **10999342888**
- file SHA-256:
  `368032e81722a4ca97bf2ec81b432b90ef2fc982cac20c8bd543d34f514d9bce`
- challenge manifest SHA-256:
  `2ba557e93692e18cf7a22807d36400ca3e22f87e6c9a4b12ee99534721d693ee`
- 84 rows;
- 12 rows per family;
- every row has split `test`;
- source labels/references copied from one of the frozen six test rows per family;
- no P1/P2/P3.

V3 final model-free coverage passed **35/35**:
- frozen result: `docs/astra/SOURCE_DOMAIN_V3_FINAL_RESULT_V1.json`;
- run **36487005586**;
- artifact **10999342888**.

## Arms

### Control-trained model

Train on the frozen S9 control dataset.

### Source-domain-trained model

Train on the exact V2 Stage-B intervention dataset.

For each seed, both arms use:
- identical initialization;
- identical minibatch row indices;
- identical optimizer settings;
- exactly 500 optimizer steps.

## Evaluation domains

### Ordinary clean domain

Evaluate both models on the frozen S9 control **test** split.

This preserves direct comparability with the rejected V1 source-domain training experiment.

### V3 source-domain challenge

Evaluate both models on the standalone 84-row V3 challenge.

The frozen S11 evaluator is used unchanged. Since every V3 challenge row has `split="test"`, all 84 rows are included in the same pitch-onset, pitch-onset-offset, family, admission, repeated-reference and negative-only metrics.

No V2 six-row challenge and no old V1 fixed challenge is gate-eligible.

## Model / optimizer / sampler — unchanged

Exact frozen S11 configuration:
- context5;
- 960 input features;
- encoder Linear(960,128) + ReLU;
- state head 128 -> 128 -> 126;
- onset head 128 -> 6;
- state active weight **9.0**;
- onset positive weight **8.0**;
- onset loss multiplier **4.0**;
- onset-aware sampler **32/32/32/32**;
- Adam learning rate **0.003**;
- batch size **128**;
- exactly **500 optimizer steps/model**;
- state threshold **0.50**;
- onset threshold **0.50**;
- decoder unchanged;
- threshold search/retuning **false**.

Seeds exactly:
- **20260927**
- **20260928**
- **20260929**

Exactly:
- 2 arms × 3 seeds = **6 models**
- **3,000 total optimizer steps**

## Frozen scientific gate

Retain the exact V1 source-domain training scientific gate; no criterion is weakened after prior failures.

### V3 challenge benefit

1. challenge pitch-onset F1 delta > 0 in **3/3** seeds;
2. challenge pitch-onset recall delta > 0 in **3/3** seeds;
3. mean challenge pitch-onset F1 gain >= **+0.05**;
4. mean challenge pitch-onset recall gain >= **+0.08**;
5. no seed challenge precision loss > **0.05**;
6. intervention challenge negative-only FP <= **0.10 events/sec** in every seed.

### Ordinary clean preservation

7. no seed ordinary pitch-onset F1 loss > **0.03**;
8. no seed ordinary pitch-onset precision loss > **0.03**;
9. no seed ordinary state-admission loss > **0.03**;
10. no seed ordinary joint-admission loss > **0.04**;
11. intervention ordinary negative-only FP <= **0.10 events/sec** in every seed;
12. no ordinary non-chord family loses > **0.15 F1** in more than one seed.

### Identity/runtime

13. exact frozen control/intervention/V3 challenge file hashes match;
14. control/intervention non-feature arrays are bit-identical;
15. intervention validation/test features are bit-identical to control;
16. intervention changed rows are exactly the 210 training rows;
17. V3 challenge has exactly 84 test rows / 12 per family;
18. V3 challenge source-row identities are only frozen control test rows;
19. paired initialization and minibatches match within seed;
20. all required metrics finite;
21. six models complete exactly 500 steps;
22. total optimizer steps = 3,000;
23. thresholds remain 0.50/0.50 with zero search/retuning;
24. no automatic retry / no reused launch identity;
25. historical S9 fixed-width training chord strings preserved in control/intervention.

A scientific pass requires **all** criteria.

## Hard execution ceiling

- CPU-only GitHub Actions;
- <=6 models;
- exactly <=500 steps/model;
- <=3,000 optimizer steps total;
- <=90 fit/eval CPU minutes;
- one launch attempt;
- automatic retry false;
- paid compute $0;
- P1 access false;
- P2 access false;
- P3 access false;
- Codespaces false;
- Vercel false;
- main/Production mutation false.

## Required offline package before execution

Before optimizer work:
- pin exact artifact IDs and file hashes;
- validate V2 intervention identity against control;
- validate V3 challenge schema/row/family/source identities;
- verify the unchanged S11 model source and evaluator source hashes;
- verify paired initialization/batch plans on no-optimizer fixtures;
- verify gate boundary logic;
- reject existing output path;
- require GitHub run attempt 1;
- use a unique durable launch identity;
- no hidden optimizer pilot.

## Decision after one execution

### Pass

Freeze the synthetic result. Do **not** automatically reopen P1/P2 or P3.

The next step becomes a real-domain transfer decision, which requires a fresh explicit authorization boundary before any protected media access.

### Fail

Freeze failure.

Because V3 was declared the final source-domain coverage iteration:
- no V4/V5 synthetic coverage redesign;
- no seed selection;
- no threshold/loss/sampler/architecture tuning from the result;
- no automatic model rerun.

Return to the project-level representation/data-strategy boundary.

## Current decision

**GO for offline V3 training execution-package implementation and verification only, followed by one synthetic-only run if that package passes.**
