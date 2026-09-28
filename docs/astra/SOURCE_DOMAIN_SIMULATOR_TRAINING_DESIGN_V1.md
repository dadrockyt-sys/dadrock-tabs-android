# Astra source-domain simulator training design V1

Date: 2026-09-28  
Status: **PROSPECTIVE SYNTHETIC-ONLY DESIGN FROZEN — TRAINING NOT YET AUTHORIZED**

## Question

With the frozen S9/S11 architecture, optimizer, sampler, labels, decoder, thresholds and seeds unchanged, does training on the prospectively frozen **waveform-level source-domain diversity package** improve performance on the fixed held-out source-domain synthetic challenge while preserving ordinary S9 synthetic competence?

This experiment is synthetic-only development evidence. It is not a P1/P2/P3 validation and cannot establish real-guitar transfer.

## Prerequisites already passed

Model-free source-domain admission and deterministic preparation are frozen in:
- `docs/astra/SOURCE_DOMAIN_SIMULATOR_DIVERSITY_PREPARATION_RESULT_V1.json`;
- preparation run **36475263654**;
- artifact **10993531230**;
- artifact digest `sha256:00bbd401e887aaabef6f5c911b2a9a767d854ad3d7254584b94927a10ec29953`.

Frozen feature identities:
- control: `b172b7cdcc0df5bc3b47b54a8dd116992f9552383babe0dc4cde5eecdac3a749`;
- intervention: `a8b5c5c590c82c152f302260430b3d6e4a3c9d5ee378d683bd8091f8f220501a`;
- challenge: `c786d846b2651872b621afa16d69a179965ffc0190a164d2e5e4ca89e0842640`.

No real media were used to fit simulator parameters.

## Arms

### Control

Frozen S9 diversified synthetic dataset and frozen S11 training path.

### Intervention

Same rows, labels, targets, split, family and historical metadata as control.

Only **training waveform-derived feature arrays** differ, produced by the frozen source-domain simulator diversity package.

Validation and ordinary test features are bit-identical to control.

### Challenge

Evaluation-only dataset:
- train/validation features bit-identical to control;
- test rows rendered with the prospectively frozen fixed source-domain challenge profile;
- all non-feature arrays bit-identical to control.

## Model and optimization — unchanged

Use the exact frozen S11 model:
- five-frame / 960-feature `context5` input;
- shared Linear(960,128) -> ReLU encoder;
- state head Linear(128,128) -> ReLU -> Linear(128,126);
- onset head Linear(128,6);
- state active weight **9.0**;
- onset positive weight **8.0**;
- onset loss multiplier **4.0**;
- onset-aware **32/32/32/32** sampler;
- Adam learning rate **0.003**;
- batch size **128**;
- exactly **500 optimizer steps/model**;
- state threshold **0.50**;
- onset threshold **0.50**;
- decoder unchanged;
- zero threshold search/retuning.

Seeds exactly:
- **20260927**
- **20260928**
- **20260929**

For every seed:
- control/intervention initialization must be byte-identical before the first update;
- minibatch row indices must be identical;
- all optimizer settings must be identical.

Exactly **6 models / 3,000 optimizer steps total**.

## Evaluation

For each seed, evaluate both trained models on:

### Ordinary domain
The frozen clean/control test set.

Report:
- pitch-plus-onset TP/FP/FN;
- precision, recall and F1;
- onset+offset F1;
- repeated-reference attack recall;
- every family pitch-plus-onset F1;
- state admission;
- joint admission;
- negative-only false positives, seconds and events/sec.

### Source-domain challenge
The fixed prospective challenge test set.

Report the same metrics and denominators.

All paired deltas are intervention minus control after absolute values are recorded.

## Frozen scientific gate

Every criterion must pass.

### Source-domain challenge benefit
1. challenge pitch-onset F1 delta > 0 in **3/3** seeds;
2. challenge pitch-onset recall delta > 0 in **3/3** seeds;
3. mean challenge pitch-onset F1 gain >= **+0.05**;
4. mean challenge pitch-onset recall gain >= **+0.08**;
5. no seed challenge precision loss > **0.05**;
6. intervention challenge negative-only FP <= **0.10 events/sec** in every seed.

### Ordinary-domain preservation
7. no seed ordinary pitch-onset F1 loss > **0.03**;
8. no seed ordinary pitch-onset precision loss > **0.03**;
9. no seed ordinary state-admission loss > **0.03**;
10. no seed ordinary joint-admission loss > **0.04**;
11. intervention ordinary negative-only FP <= **0.10 events/sec** in every seed;
12. no ordinary non-chord family loses > **0.15 F1** in more than one seed.

These intentionally retain the S13 minimum benefit/regression floors rather than weakening criteria after prior failures.

### Identity/runtime admission
13. exact frozen artifact/dataset hashes match;
14. every non-feature array is bit-identical across arms;
15. intervention validation/test features are bit-identical to control;
16. challenge train/validation features are bit-identical to control;
17. changed intervention rows are exactly the 210 training rows;
18. changed challenge rows are exactly the 42 test rows;
19. paired initialization and minibatches match within seed;
20. all required metrics are finite;
21. all six models complete exactly 500 optimizer steps;
22. total optimizer steps = 3,000;
23. thresholds remain 0.50/0.50 with zero search/retuning;
24. no automatic retry and no reused launch identity.

A scientific pass requires all criteria.

## Historical S9 string-storage caveat

The frozen S9 control contains a known fixed-width Unicode truncation on 30 training chord `template_id`/`refs_json` fields.

This experiment must:
- preserve those historical fields byte-identically in all arms;
- use state/onset arrays for training as before;
- never attempt to parse the malformed training-chord reference strings;
- evaluate only on held-out reference fields, which remain valid;
- record the caveat in the execution receipt.

This bookkeeping defect is not an intervention and must not be silently repaired in one arm.

## Hard execution ceiling

- CPU-only GitHub Actions;
- exactly at most **6 models**;
- exactly at most **500 steps/model**;
- at most **3,000 total optimizer steps**;
- <= **90 fit/eval CPU minutes**;
- one launch attempt only;
- automatic retry **false**;
- paid compute **$0**;
- no external/corpus audio acquisition;
- P1 access **false**;
- P2 access **false**;
- P3 access **false**;
- Codespaces **false**;
- Vercel **false**;
- main/Production mutation **false**.

## Execution package required before launch

Training remains disabled until a separate implementation package:
- downloads the exact frozen preparation artifact;
- checks the artifact digest and complete per-array hashes;
- pins all imported source dependencies;
- checks paired initialization/batches on tiny/no-optimizer fixtures;
- checks every gate boundary;
- rejects existing output paths;
- rejects run attempts >1;
- rejects reused launch identities through a durable ledger;
- writes failure receipts and uploads partial diagnostics;
- uses read-only repo permissions.

No optimizer pilot may be hidden in an implementation test.

## Decision after one future execution

- **Pass:** freeze as synthetic development evidence only. Do not automatically evaluate P1/P2/P3 or promote to Production.
- **Fail:** freeze and return to project-level simulator/representation review. Do not tune simulator ranges, thresholds, architecture, seeds or gates from the result.
- **Execution/identity failure:** repair only the concrete implementation defect under a new verified source identity. Do not weaken the scientific gate.

## Current decision

**GO for offline execution-package implementation/testing only.**

This document does **not** authorize model training.
