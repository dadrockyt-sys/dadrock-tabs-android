# SONGSTERR — FULL MIXTURE ADMITTED SHADOW EFFECT VALIDATION V1 — PREIMPLEMENTATION FREEZE

Date: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`  
Phase: 9  
Experiment: `FULL_MIXTURE_ADMITTED_SHADOW_EFFECT_VALIDATION_V1`

## Decision

**AUTHORIZED ONLY AS A BRANCH-LOCAL, CPU-ONLY, SYNTHETIC/REFERENCE-BLIND SHADOW-EFFECT VALIDATION.**

This phase may verify whether a Phase 8-admitted full-mixture observation produces deterministic, appropriately bounded changes in the existing `dualContextShadowProjection`. It may not promote that projection or any mixture structure estimate into canonical analyzer events, generated tablature, Product/UI rendering, Preview/PDF rendering, purchase/token paths, `main`, or Production.

## Frozen purpose

Phase 8 proved that server-side analyzer observations can be independently admitted into the research-only `mixtureStructureContext` while Product/PDF authority remains unchanged. Phase 9 must answer the next narrower question:

> Given fixed synthetic analyzer events and Conditioning V1 instrument authority, does a trusted full-mixture observation change only the expected shadow timing/measure projection, deterministically, while rejected observations and explicit user priors preserve baseline behavior?

This is an effect-validation experiment, not an authority-promotion experiment.

## Frozen inputs

Only deterministic synthetic/reference-blind fixtures may be used.

Allowed inputs:

- synthetic event arrays with timestamps/MIDI and optional source string/fret fields;
- server-normalized Conditioning V1 objects;
- synthetic Phase-7-shaped full-mixture observations satisfying the complete Phase 8 provenance/diagnostic admission contract;
- malformed or forbidden synthetic observations used solely to test rollback/fail-open behavior.

Forbidden inputs:

- GOAT restricted bytes or labels;
- GuitarSet prospective/held-out assets or labels;
- SplitMySong assets or labels;
- Songsterr/professional/reference tablature, MIDI, timing, structure, or labels;
- separated carrier/stem structure as global structure authority;
- transcribed-event-derived structure observations;
- external audio downloads;
- reference-facing score calls;
- Modal invocation/deployment or GPU/CUDA work.

## Frozen topology

The experiment must exercise the existing path without changing its authority:

`synthetic events + Conditioning V1`

and

`synthetic full-mixture observation -> Phase 8 admission -> mixtureStructureContext`

then

`buildAiTabDualContextShadowFusionV1(...) -> dualContextShadowProjection`

The null-observation Phase 3 context remains the rollback/baseline.

## Required validation matrix

The verifier must cover at least the following invariants:

1. **Baseline unresolved parity** — null observation produces the existing unresolved shadow structure when Auto structure is unresolved.
2. **Trusted complete observation effect** — a fully admitted observation can resolve tempo/time-signature/pickup/feel and deterministically produce projected starts, subdivision indices, and musical positions.
3. **Determinism** — identical inputs produce byte/deep-equal shadow results across repeated calls.
4. **Instrument-authority invariance** — observation changes global shadow structure only; role/tuning/capo and conditioned string/fret decoding remain identical for the same events/conditioning.
5. **Source-event immutability** — input events are not mutated.
6. **Explicit user-prior precedence** — explicit user structure fields override conflicting admitted observation fields exactly as Phase 3 specifies.
7. **Rejected observation rollback** — forbidden source/reference/carrier/event provenance returns the exact baseline `mixtureStructureContext` and a shadow projection deep-equal to the baseline projection.
8. **Malformed/invalid field rollback** — malformed or out-of-contract observation fields likewise preserve baseline effect.
9. **Partial-observation boundedness** — partial trusted observations may fill only unresolved fields and must not fabricate completeness; unresolved measure projection remains unresolved unless the resulting context is actually complete.
10. **Feel boundedness** — straight/triplet may change only the expected shadow subdivision grid; `auto` remains unresolved and is never fabricated by an observation.
11. **Research-only contract preservation** — `mixtureStructureContext.contextContract.productionEligible` and `dualContextShadowProjection.fusionContract.productionEligible` remain false; both remain reference-blind and reference-score unauthorized.
12. **Product/PDF static isolation** — canonical payload construction, generated tab/events/renderEvents/measureGrid, Preview/PDF routes, and Product authority remain independent of mixture observation/shadow projection.

The implementation may add a verifier, compact evidence artifact, and isolated GitHub Actions workflow. Production code should not need modification for this phase. If the experiment exposes a defect in existing research-only helper behavior, any code fix must be separately justified against this frozen boundary and must not broaden authority.

## Pass criteria

Phase 9 passes only if all frozen validation items pass and evidence records all of the following:

- `referenceBlind = true`;
- `shadowOnly = true`;
- `productAuthorityChanged = false`;
- `pdfAuthorityChanged = false`;
- `canonicalAnalyzerOutputChanged = false`;
- `externalAudioAssetsUsed = false`;
- `guitarSetRead = false`;
- `splitMySongRead = false`;
- `goatRestrictedBytesRead = false`;
- `referenceScoreCalls = 0`;
- `modalInvoked = false`;
- `gpuUsed = false`;
- `mainModified = false`;
- `productionModified = false`;
- `productionPromotionAuthorized = false`.

Any missing safety evidence is a failure.

## Failure / rollback rule

A failed verifier or ambiguous effect does **not** authorize threshold weakening, authority promotion, use of reference assets, or Product/PDF wiring. The rollback is the Phase 8-complete branch state and its null-observation baseline behavior.

## Frozen non-goals

Phase 9 does not:

- improve or score transcription accuracy;
- change analyzer selection;
- change V143 runtime safety checks;
- change canonical events or generated tab text;
- change Product UI, Preview, PDF, purchase, token, or email behavior;
- deploy a Vercel Preview;
- deploy/invoke Modal;
- merge `main`;
- promote Production.

## Frozen status

**`SHADOW EFFECT VALIDATION AUTHORIZED / VERIFIER-ONLY PREFERRED / PRODUCT-PDF AUTHORITY UNCHANGED / SYNTHETIC REFERENCE-BLIND ONLY / NO MODAL-GPU / NO REFERENCE SCORE / MAIN+PRODUCTION UNTOUCHED`**
