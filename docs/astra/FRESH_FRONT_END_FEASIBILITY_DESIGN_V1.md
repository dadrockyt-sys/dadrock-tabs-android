# Fresh independent front-end feasibility design V1

Date: 2026-10-06  
Branch: `astra-work`  
Status: **DESIGN FROZEN — EXECUTION NOT AUTHORIZED**

## Purpose

Test whether a frozen alternative note/onset representation can materially improve guitar evidence on genuinely fresh performer-disjoint rights-cleared material, without fitting, threshold search, or reference-derived post-processing.

This is a feasibility diagnostic only. It does not authorize production changes, Go My Way mutation, threshold tuning, model training, or a recovery algorithm.

## Stage 0 — candidate/source selection without reference scores

Before any empirical execution, select exactly one alternative frozen front end and one fresh evaluation source using only non-performance criteria.

### Alternative front-end eligibility

The candidate must:
- be pretrained and usable with frozen weights;
- expose note pitch plus onset timing directly or through a deterministic documented conversion;
- have a license compatible with internal evaluation;
- run within the bounded evaluation budget;
- require zero optimizer steps;
- require no calibration on evaluation labels;
- have a fixed published/default inference configuration that can be frozen before scoring.

Selection must not use accuracy numbers computed on the future evaluation material.

Basic Pitch 0.4.0 remains the frozen comparator at its historical default configuration; no threshold changes are allowed.

### Evaluation-source eligibility

The source must:
- be rights-cleared for this evaluation;
- contain guitar note/onset reference annotations;
- be performer-disjoint from consumed real-development material;
- exclude Go My Way;
- exclude GuitarSet players 00/01/03;
- not reuse a reference population previously inspected to choose candidate parameters;
- provide enough performer/content diversity to report performer-level and content-family macro metrics.

The exact source identity, version, hashes, performer identities, and split must be frozen before any reference-facing inference score.

## Stage 1 — frozen candidate generation

For each front end:
- run the exact frozen configuration on audio only;
- candidate generation must not read reference annotations;
- freeze all per-track prediction files and a manifest before reference parsing;
- record model/package identity and hashes where technically available;
- record event counts and source-audio hashes;
- no prediction mutation after freezing.

## Stage 2 — single reference-facing score

Use one scorer with a prospectively frozen contract:
- onset tolerance: **50 ms**;
- primary pairing: maximum-cardinality onset-only, then minimum total absolute onset error;
- pitch never selects primary pairs;
- report exact pitch among matched events;
- report unmatched references and unmatched predictions;
- report ambiguity-aware pitch statistics for chord-like components;
- report performer-level aggregates;
- report content-family macro aggregates;
- report prediction/reference event-count ratio.

The score is executed once per frozen front end. No threshold sweep, no retry with altered inference settings, and no score-driven post-processing.

## Primary comparison

Comparator: **Basic Pitch 0.4.0 frozen historical defaults**.

Intervention: **one alternative frozen front end selected in Stage 0**.

The purpose is to determine whether the alternative representation materially improves precision/F1 without sacrificing useful recall.

## Prospective advancement gate

The exact numerical gate must be frozen in a launch authorization after the Stage-0 candidate/source identities are known and before any reference-facing score.

The gate must include all of:
- aggregate pitch+onset F1 improvement over Basic Pitch by a prospectively justified minimum;
- aggregate precision improvement over Basic Pitch by a prospectively justified minimum;
- aggregate recall floor;
- performer-level floor for every included performer;
- content-family macro floor for every declared content family;
- bounded prediction/reference count ratio;
- zero optimizer steps;
- zero threshold search;
- zero reference-derived prediction mutation.

No single aggregate metric may override a failed performer/content safety floor.

## Stop rules

If the frozen gate fails:
- stop;
- do not tune either front end;
- do not add a second alternative model;
- do not alter thresholds;
- do not derive Go My Way corrections;
- do not reuse the scored evaluation set as fresh holdout.

If the gate passes:
- record only that the alternative representation merits a separately designed downstream integration study;
- do not integrate automatically.

## Isolation and provenance

Candidate-generation jobs may read audio but not references.  
Scoring jobs may read references but must not run candidate inference.  
Reference files/audio must not be committed to the repository.  
Only hashes, manifests, aggregate receipts, and bounded diagnostic outputs may be retained.

## Explicit non-authorization

This design does **not** authorize:
- candidate-model download for empirical evaluation;
- evaluation-dataset download or reference inspection;
- inference;
- scoring;
- training;
- threshold tuning;
- production changes;
- Go My Way mutation.

Those require a separate explicit execution authorization after the Stage-0 identities and final numerical gate are visible.
