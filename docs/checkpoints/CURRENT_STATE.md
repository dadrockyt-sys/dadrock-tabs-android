# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **ZERO-OPTIMIZER SYNTHETIC/REAL DOMAIN DIAGNOSTIC COMPLETE — MIXED FEATURE/REPRESENTATION FAILURE FROZEN; P3 SEALED**

## Standing policy

Routine GitHub work and bounded inexpensive synthetic GitHub model runs remain pre-authorized.

P1/P2/P3 real-data access remains a separate boundary.

## Canonical domain diagnostic

- run **36386315576**
- job **108812332904**
- head `72a35e694b468f8f7811934fd97ae3f215d0a576`
- workflow **SUCCESS**
- artifact **10955243031**
- artifact digest `sha256:6f1e13f86c3e6f5a0db4428a67add945ea03f21e0bade3e662afd7045f88aecc`
- optimizer steps **0**
- model weights changed **no**
- threshold search **no**
- P1 accessed **yes**
- P2 accessed **yes**
- P3 opened **no**

Frozen result:
- `docs/astra/SYNTHETIC_REAL_DOMAIN_DIAGNOSTIC_RESULT_V1.json`

Analysis:
- `docs/astra/SYNTHETIC_REAL_DOMAIN_DIAGNOSTIC_ANALYSIS_V1.md`

## Main findings

Raw feature means/std/RMS:
- synthetic **0.1823 / 0.2297 / 0.2932**
- P1 **0.1439 / 0.2111 / 0.2555**
- P2 **0.1383 / 0.1998 / 0.2430**

Centroid distance:
- synthetic -> P1: L2 **1.1617**, cosine distance **0.0740**
- synthetic -> P2: L2 **1.1906**, cosine distance **0.0833**
- P1 -> P2: L2 **0.6698**, cosine distance **0.0381**

Candidate exact reference admission:
- synthetic onset/state/joint **0.6744 / 0.3256 / 0.3101**
- P1 **0.0625 / 0.0000 / 0.0000**
- P2 **0.0000 / 0.2667 / 0.0000**

Baseline:
- P1 **0.625 / 0.625 / 0.5625**
- P2 **0.000 / 0.2667 / 0.000**

Interpretation:
- a measurable synthetic-to-real feature shift exists;
- P1 candidate failure includes severe state-identity collapse;
- P2 is immediately onset/attack-limited for both frozen models;
- global threshold rescue is contradicted because real inputs are not globally under-active; activation is misplaced relative to references.

## Do not

- threshold-rescue;
- normalize model inputs post hoc;
- seed-pick;
- tune on the eight real crops;
- reopen P3.

## Next design-only proposal

- `docs/astra/REAL_DOMAIN_FAILURE_LOCALIZATION_PROPOSAL_V1.md`

It would localize:
1. P1 pitch/string/fret error geometry;
2. P2 onset timing and attack-novelty geometry.

**Do not execute it yet. Fresh explicit P1/P2 access authorization is required.**

P3 remains sealed.
