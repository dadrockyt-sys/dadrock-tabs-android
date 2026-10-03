# Transcription Trust / Flag Holdout Study Protocol V1

Date: 2026-10-02  
Branch: `astra-work`  
Status: **MODEL-FREE ADMISSION DESIGN — NO THRESHOLD DEFINED**

## Purpose

Define the minimum new evidence required before an automatic transcription trust/flagging threshold may even be considered.

This protocol exists because S0 has already been used for:
- separator diagnostics;
- duplicate-class analysis;
- transcription-failure attribution;
- reliability observability;
- cross-stem overlap exploration.

Therefore S0 may not also be used to choose or validate a future automatic trust threshold.

## Two-stage study required

A future study must contain two fully source-disjoint phases.

### Phase A — new calibration cohort

Minimum **48 cases**, none sharing source assets with S0 or prior development:

- 12 `complementary_both_present`
- 6 `target_absent_guitar`
- 6 `target_absent_bass`
- 6 `duplicate_role_guitar`
- 6 `duplicate_role_bass`
- 12 `hard_complementary_confuser`

Purpose:
- inspect new feature distributions;
- determine whether a candidate trust/flagging rule is even plausible;
- if justified, freeze exactly one candidate rule after calibration.

No holdout outcomes may be inspected while that rule is being chosen.

### Phase B — sealed holdout cohort

A second, independently sourced cohort with the same minimum 48-case stratum balance.

Required:
- no source hash shared with Phase A;
- no source hash shared with S0 or prior development;
- unique case IDs across the whole study;
- ground-truth role condition defined independently of diagnostic outputs.

The candidate rule, implementation hash, feature definitions, and success criteria must be committed **before** opening holdout outcomes.

## Why these strata are required

`complementary_both_present` measures false review flags on normal guitar+bass mixtures.

`target_absent_guitar` and `target_absent_bass` test false-role outputs, including the class of problem previously seen in S0.

`duplicate_role_guitar` and `duplicate_role_bass` test the hard condition where one musical role is represented across both labeled outputs.

`hard_complementary_confuser` prevents a future rule from simply treating synchronous rhythms, octaves, similar event counts, or strong cross-stem musical relation as proof of duplication.

## Admission requirements implemented in code

`astra_backend/trustFlagHoldoutProtocol.mjs` checks:

- schema identity;
- threshold is still undefined;
- automatic correction remains unauthorized;
- production delivery remains unauthorized;
- minimum stratum counts in both phases;
- valid source SHA-256 identities;
- no duplicate case IDs;
- no calibration/holdout source leakage;
- no overlap with supplied prior-development/S0 source hashes.

The protocol validator operates on manifests only. It does not load audio, run a separator, run Basic Pitch, or inspect model outcomes.

## What may happen after calibration

Only if Phase A provides a coherent, pre-specified rationale may one candidate flagging rule be written down.

That future candidate record must freeze, before holdout evaluation:
- exact input features;
- exact mathematical rule;
- exact thresholds;
- missing-data behavior;
- pair-state behavior;
- reason-code mapping;
- implementation commit/blob identity;
- evaluation metrics;
- pass/fail criteria.

No threshold may be changed after holdout outcomes are visible.

## What this protocol does NOT authorize

It does not authorize:
- choosing a threshold now;
- fitting on S0;
- automatic note deletion;
- automatic stem mutation;
- automatic role reassignment;
- production delivery;
- commercial-recording evaluation;
- changes to `main`.

## Current decision

Before automatic trust/flagging can be considered, the project needs **at least 96 new admitted cases**:
- 48 new calibration cases;
- 48 new sealed holdout cases.

Both phases must satisfy the stratum balance and source-disjointness rules above.

Until those new cohorts exist and pass model-free admission, the existing uncertainty presentation remains the correct behavior: preserve evidence, expose reason codes, and fail closed for complete-tab eligibility when uncertainty is unresolved.
