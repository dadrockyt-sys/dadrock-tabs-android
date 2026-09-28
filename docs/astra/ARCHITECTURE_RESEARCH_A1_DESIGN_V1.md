# Astra Architecture Research A1 — decoupled state/onset encoders

Date: 2026-09-28
Status: **NEW PROJECT VERSION — PROSPECTIVE DESIGN FROZEN BEFORE OPTIMIZER WORK**

## Authorization

The user explicitly approved opening a new architecture research version on 2026-09-28.

This is not a V3 rescue and does not rewrite any prior failed result.

## Structural hypothesis

The frozen S11 model forces two different tasks through one shared 128-unit bottleneck:

```
context5 960
    |
Linear(960,128) + ReLU
    |--------------------|
state head               onset head
128 -> 128 -> 126        128 -> 6
```

State classification and onset detection have different invariance requirements.

A shared low-capacity encoder can therefore create task interference: changes that improve onset discrimination may simultaneously damage persistent pitch/state evidence.

This is a structural hypothesis, not a claim that V3 proved gradient interference.

## A1 architecture — one deliberate change

Replace the single shared encoder with two independent encoders of identical form:

```
context5 960
   |                         |
state encoder                onset encoder
Linear(960,128)+ReLU         Linear(960,128)+ReLU
   |                         |
state head                   onset head
128 -> 128 -> 126            128 -> 6
```

No other architectural component changes.

### Unchanged

- input representation: frozen context5 over prepared 192-bin features;
- input dimension: 960;
- state head dimensions: 128 -> 128 -> 126;
- onset head dimensions: 128 -> 6;
- ReLU activations;
- state active weight: 9.0;
- onset positive weight: 8.0;
- onset loss multiplier: 4.0;
- sampler: 32/32/32/32;
- Adam learning rate: 0.003;
- batch size: 128;
- optimizer steps/model: 500;
- seeds: 20260927, 20260928, 20260929;
- state threshold: 0.50;
- onset threshold: 0.50;
- decoder/evaluator;
- V2 source-domain training support;
- ordinary clean S9 test;
- V3 84-row challenge.

No threshold, loss, sampler, preprocessing, simulator or decoder tuning is permitted in A1.

## Data

Train exactly three A1 models, one per frozen seed, on the exact V2 intervention dataset:

- file SHA-256:
  `a17a16daeb8d698e325dc6820f18d5eda2fec75d9beebe2a9605a678124dc26b`

Evaluate on:

### Ordinary clean

Exact frozen S9 control test:
- control file SHA-256:
  `16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894`

### V3 source-domain challenge

Exact frozen V3 challenge:
- file SHA-256:
  `368032e81722a4ca97bf2ec81b432b90ef2fc982cac20c8bd543d34f514d9bce`
- 84 rows / 12 per family.

P1/P2 are not used.
P3 remains sealed.

## Comparators

A1 is compared against the already-frozen **S11 intervention-trained** metrics from:

`docs/astra/SOURCE_DOMAIN_V3_SYNTHETIC_TRAINING_RESULT_V1.json`

This isolates the architecture change:
- same intervention training data;
- same seeds;
- same batch-plan construction;
- same optimizer/loss/sampler;
- same evaluation data;
- only encoder sharing changes.

No S11 model is retrained in A1.

The frozen S11 **control-trained** metrics remain a secondary absolute reference only.

## Structural admission before training

A1 implementation must pass no-optimizer tests proving:

1. exact A1 tensor shapes;
2. state and onset encoder parameter sets are disjoint;
3. state-only loss produces no gradient in the onset encoder;
4. onset-only loss produces no gradient in the state encoder;
5. same frozen sampler/batch hashes are reused per seed;
6. evaluator and thresholds are imported unchanged;
7. exact frozen data hashes match;
8. parameter count is reported, not gate-tuned.

No optimizer pilot is permitted during package verification.

## Primary A1 scientific gate

The purpose is to test whether decoupling repairs state/joint degradation **without giving back the source-domain onset robustness already obtained**.

Every criterion must pass.

### Architecture-effect criteria versus frozen S11 intervention

1. ordinary state-admission delta > 0 in **3/3** seeds;
2. mean ordinary state-admission gain >= **+0.04**;
3. ordinary joint-admission delta > 0 in **3/3** seeds;
4. mean ordinary joint-admission gain >= **+0.04**;
5. no seed V3 challenge pitch-onset F1 loss > **0.03**;
6. no seed V3 challenge pitch-onset recall loss > **0.03**;
7. no seed ordinary pitch-onset F1 loss > **0.03**;
8. no seed ordinary pitch-onset precision loss > **0.03**;
9. A1 challenge negative-only FP <= **0.10 events/sec** in every seed;
10. A1 ordinary negative-only FP <= **0.10 events/sec** in every seed.

### Absolute system guards versus frozen S11 control

These guards prevent an architecture win that still leaves the system worse than the clean baseline.

11. ordinary state-admission loss versus frozen S11 control <= **0.03** in every seed;
12. ordinary joint-admission loss versus frozen S11 control <= **0.04** in every seed;
13. V3 challenge pitch-onset F1 gain versus frozen S11 control > 0 in **3/3** seeds;
14. mean V3 challenge pitch-onset F1 gain versus frozen S11 control >= **+0.05**;
15. V3 challenge pitch-onset recall gain versus frozen S11 control > 0 in **3/3** seeds.

The previous +0.08 challenge-recall gain floor is not reused as an A1 architecture-effect gate because A1 is testing task decoupling, not re-running the final source-domain-training admission. Its recall is instead protected against regression relative to the frozen S11 intervention and required to remain positive versus the frozen control.

## Identity/runtime criteria

16. exact control/intervention/V3 challenge file hashes match;
17. exact frozen seed set;
18. exact frozen batch-plan hashes for each seed;
19. exactly three A1 models;
20. exactly 500 optimizer steps/model;
21. exactly 1,500 optimizer steps total;
22. all required metrics finite;
23. thresholds fixed 0.50/0.50;
24. zero threshold search/retuning;
25. automatic retry false;
26. no P1/P2/P3 access;
27. no main/Production mutation.

A pass requires all criteria.

## Hard execution ceiling

- CPU-only GitHub Actions;
- exactly 3 models maximum;
- exactly 500 steps/model maximum;
- 1,500 optimizer steps total maximum;
- <=45 fit/eval CPU minutes;
- one launch identity;
- run attempt 1 only;
- automatic retry false;
- paid compute $0;
- P1 access false;
- P2 access false;
- P3 access false;
- Codespaces false;
- Vercel false;
- main/Production mutation false.

## Stop rule

### If A1 passes

Freeze the result.

A pass supports the specific hypothesis that encoder decoupling materially improves the state/onset tradeoff under the frozen synthetic contract.

It does not authorize P1/P2/P3 automatically.

The next step would be a separate architecture-confirmation decision or a newly authorized independent real-development program.

### If A1 fails

Freeze failure and stop this A1 line.

Do not:
- widen/deepen the encoders;
- alter loss weights;
- retune sampler;
- lower thresholds;
- select a favorable seed;
- change context width;
- add recurrence/convolution as an automatic follow-up.

Any A2 architecture would require another explicit project decision and a new prospective rationale.

## Current decision

**GO for A1 implementation and zero-optimizer package verification.**

After the package passes its structural verification, the already-granted architecture-research approval plus the standing bounded-synthetic-run policy permits one A1 synthetic execution under this exact contract.
