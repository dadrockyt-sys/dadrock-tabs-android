# Fresh front-end feasibility V1 decision

Date: 2026-10-06  
Status: **COMPLETE — FROZEN ADVANCEMENT GATE PASSED**

## Authoritative execution

- score-recovery workflow run: **37448533631**
- head SHA: `b097a45dc6c7d8fd29cc4ae13a7cbbb0d17b209f`
- frozen candidate artifact: **11403758166**
- candidate artifact digest: `sha256:128f7b954b8d10b57ca4b581eef6534d6d15f9db38563035aa73b7947620fd50`
- result artifact: **11404537641**
- result artifact digest: `sha256:a2af12b7636c2429e455f84ac43a86fb69a2fc30a97a57d55565ea0d5ebba290`
- result JSON SHA-256: `36a17b8a77c7cde03ae21f014a73a8af54e4e3e272e42c6b574be9a8a6bb567c`
- reference manifest SHA-256: `a96e23776b884bfd4a4d83cc4d21926ea868a4b00471e7c759dbe146e5829da5`

The authoritative candidate sets were frozen reference-blind in run **37441935611** and reused unchanged for score recovery.

## Frozen population

- GAPS v1.1 published test split only
- **30 tracks**
- **27 performers**
- **25,030 reference note events**

## Primary result

### Basic Pitch 0.4.0 comparator

- predictions: **33,465**
- exact pitch+onset true positives: **14,081**
- precision: **0.420768**
- recall: **0.562565**
- F1: **0.481443**
- prediction/reference ratio: **1.336996**
- classical-guitar track macro F1: **0.491678**

### François-Leduc-trained guitar front end

- predictions: **25,195**
- exact pitch+onset true positives: **21,034**
- precision: **0.834848**
- recall: **0.840352**
- F1: **0.837591**
- prediction/reference ratio: **1.006592**
- classical-guitar track macro F1: **0.842219**

### Absolute deltas vs Basic Pitch

- precision: **+0.414080**
- recall: **+0.277787**
- F1: **+0.356148**
- track macro F1: **+0.350541**

## Frozen advancement gate

Every preregistered check passed:

- aggregate F1 improvement and absolute floor: **PASS**
- aggregate precision improvement and absolute floor: **PASS**
- aggregate recall floor: **PASS**
- prediction/reference ratio 0.75–1.50: **PASS**
- every one of 27 performer floors: **PASS**
- declared content-family macro floor: **PASS**
- zero optimizer steps: **PASS**
- zero threshold search: **PASS**
- zero reference-derived prediction mutation: **PASS**

**Overall gate: PASS.**

## Interpretation

This result is strong evidence that, on fresh performer-disjoint classical-guitar material, the previously selected François-Leduc-trained guitar front end provides materially better pitch+onset evidence than Basic Pitch 0.4.0 at frozen defaults.

This supports the hypothesis that front-end / representation quality was a major unresolved bottleneck.

It does **not** establish:
- customer-ready tab accuracy;
- lead/rhythm role attribution;
- string/fret correctness in DadRock's target representation;
- robustness on mixed full-song production audio;
- correctness on Go My Way;
- permission to tune against this now-consumed GAPS test set.

The 30 GAPS test tracks / 27 performers are now consumed evaluation material and must not be reused as fresh holdout.

## Decision

Advance only to a **separately designed integration study**.

Do not automatically:
- replace Basic Pitch in Production;
- mutate the frozen Go My Way candidate;
- train or fine-tune this model;
- tune thresholds on GAPS;
- reuse the GAPS test split as validation;
- infer lead/rhythm role from this front end;
- change `main`.

The next generic continuation may prepare an integration-study design and authorization packet only. Empirical integration testing remains behind a fresh explicit authorization boundary.
