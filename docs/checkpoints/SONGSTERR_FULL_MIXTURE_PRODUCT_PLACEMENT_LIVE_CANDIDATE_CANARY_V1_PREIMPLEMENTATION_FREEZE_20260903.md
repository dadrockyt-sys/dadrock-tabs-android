# FULL_MIXTURE_PRODUCT_PLACEMENT_LIVE_CANDIDATE_CANARY_V1 — PREIMPLEMENTATION FREEZE

Date: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`

Status: **`PHASE11_CANARY_CONTRACT_FROZEN / IMPLEMENTATION_NOT_AUTHORIZED / NON_AUTHORITATIVE_SERVER_RESEARCH_METADATA_ONLY / LIVE_PRODUCT-PDF_AUTHORITY_UNCHANGED / NO_MODAL-GPU / NO_REFERENCE_SCORE / MAIN+PRODUCTION_UNTOUCHED`**

## Purpose

Phase 10 established, on a deterministic synthetic known-truth fixture, that the existing experiment-only full-mixture placement candidate can fill otherwise absent V143 Product placement from 0% to 100% with 7/7 exact placements while preserving canonical event identity/instrument facts and passing the existing Product render-event validator.

Phase 10 explicitly did **not** authorize live Product/PDF promotion.

The safest prospective next phase is therefore a **non-authoritative server canary**: on an already successful `/api/analyze-audio-tab` response path, compute whether the Phase 10 placement candidate would be eligible and expose only clearly labeled research/canary metadata. Canonical `structuredPayload`, `renderEvents`, `generatedTab`, `events`, measure grid, `analysisEngine`, Product UI, Preview/PDF inputs, payment/delivery behavior, and Production authority must remain unchanged.

This document freezes that prospective contract. **It does not authorize implementation.**

## Frozen current seams

Current server order in `app/api/analyze-audio-tab/route.js` is:

1. receive and validate request;
2. invoke the selected analyzer;
3. enforce V143 runtime anti-leakage safety when V143 Rhythm is selected;
4. build canonical `structuredPayload` first;
5. build server-owned Conditioning V1 contract;
6. build Phase 2 conditioning shadow;
7. build Phase 3 baseline mixture structure context with `mixtureObservation: null`;
8. independently admit analyzer `mixtureObservation` through Phase 8;
9. build Phase 4/9 `dualContextShadowProjection` as research metadata;
10. return canonical payload plus research metadata.

The Phase 10 helper is:

`analyzer/full_mixture_product_placement_candidate_v1.mjs`

`buildFullMixtureProductPlacementCandidateV1({ structuredPayload, dualContextShadowProjection })`

Its existing frozen behavior is fail-open and placement-only. It requires V143 runtime safety, empty canonical `renderEvents`, trusted full-mixture structure authority, complete straight 4/4 / pickup 0 / 16-step geometry, exact one-to-one event identity and instrument facts, and Product-validator acceptance. Existing authenticated Product placement always wins. Any mismatch returns `null`.

## Frozen Phase 11 seam

If implementation is later explicitly authorized, the only permitted live-server seam is:

`canonical structuredPayload already built`  
`+ Phase 8 mixtureStructureContext already built`  
`+ Phase 4/9 dualContextShadowProjection already built`  
`-> Phase 10 candidate helper evaluated`  
`-> append non-authoritative canary summary metadata to the JSON response`.

The helper may be evaluated **only after** canonical Product payload construction and the research shadow projection are complete. No candidate data may flow backward into canonical builders.

## Frozen canary response contract

The prospective response field is named:

`productPlacementCandidateCanary`

It must be append-only and must never replace any existing response field.

When the Phase 10 helper returns no candidate, the field must report an ineligible/fail-open state without changing the canonical response.

When the helper returns a candidate, the field may report only bounded summary/diagnostic information sufficient to observe eligibility. The frozen minimum shape is:

```js
{
  canaryContract: {
    name: 'full-mixture-product-placement-live-candidate-canary',
    version: 1,
    researchOnly: true,
    shadowOnly: true,
    placementOnlyAuthority: true,
    liveProductAuthority: false,
    pdfAuthority: false,
    productionEligible: false,
    referenceBlind: true,
    referenceScoreAuthorized: false,
  },
  eligible: boolean,
  baselineRenderEventCount: number,
  candidateRenderEventCount: number,
}
```

**Candidate `renderEvents` rows are not authorized to be emitted by Phase 11.** This canary observes eligibility/counts only. If later inspection of row-level candidate placement is desired, that requires a separately frozen data-exposure decision.

## C1–C12 frozen requirements

### C1 — Canonical-first ordering

`buildJimmyPaigeAnalysisPayload(...)` must run before any Phase 11 canary evaluation. The canary cannot influence inputs to the canonical builder.

### C2 — Existing authenticated Product placement wins

If canonical `structuredPayload.renderEvents` is non-empty/authenticated, the Phase 10 helper must remain ineligible and the canary must report no candidate. No canonical placement may be overridden, merged, compacted, reindexed, or supplemented.

### C3 — Placement-only candidate source

Phase 11 may use only the existing Phase 10 helper result produced from canonical `structuredPayload` plus Phase 4/9 `dualContextShadowProjection`. It may not independently infer string, fret, pitch, MIDI, event identity, timing, carrier structure, labels, or reference-derived information.

### C4 — Provenance and safety gates remain intact

Phase 8 full-mixture provenance admission, V143 runtime anti-leakage safety, Phase 4/9 shadow/reference-blind contracts, and Phase 10 candidate gates must remain unchanged and independently enforced.

### C5 — Fail-open canary behavior

Import failure, helper exception, missing inputs, malformed candidate result, provenance mismatch, safety mismatch, geometry mismatch, event-integrity mismatch, Product-validator rejection, or any unexpected condition must produce an ineligible/null-equivalent canary summary while preserving the exact canonical Product response behavior.

### C6 — No Product authority crossing

The canary must not mutate or replace:

- `structuredPayload`;
- `renderEvents`;
- `events`;
- `generatedTab`;
- measure grid / render contract;
- `analysisEngine`;
- Product UI inputs;
- Preview/PDF inputs;
- download/delivery/payment behavior.

### C7 — Summary-only exposure

Phase 11 may expose eligibility and bounded counts only. It must not expose candidate `renderEvents` rows or another directly consumable Product placement stream.

### C8 — Client/PDF isolation

No Product component, Preview/PDF code path, client rendering code, token/unlock path, or delivery path may read `productPlacementCandidateCanary` in Phase 11.

### C9 — Deterministic synthetic verification

A dedicated verifier must use deterministic synthetic/static fixtures and prove both eligible and fail-open cases without external audio, reference assets, Modal, GPU, Vercel Preview, or Production deployment.

### C10 — Canonical response rollback proof

Verifier must prove that removing/bypassing the canary evaluation restores the exact pre-Phase-11 canonical Product fields and that canary failures do not alter status codes or canonical payload fields on otherwise successful requests.

### C11 — No scientific-boundary crossing

Phase 11 must not read GOAT restricted bytes, SplitMySong, GuitarSet prospective players, professional references, reference labels, or any lawful/unlawful holdout. Reference-facing score calls remain 0.

### C12 — No deployment/authority promotion

Phase 11 implementation, if separately authorized, remains branch-only. No `main` merge, Production promotion, Vercel Production change, Modal deploy/invoke, GPU/CUDA use, or Product/PDF authority promotion is permitted by this contract.

## Frozen validation matrix

A later implementation must have an isolated read-only CPU workflow proving at minimum:

1. eligible synthetic Phase 10 candidate -> canary `eligible=true`, bounded counts correct;
2. existing authenticated canonical `renderEvents` -> canary ineligible, canonical placement unchanged;
3. missing/malformed dual-context projection -> fail-open ineligible;
4. untrusted mixture observation / provenance mismatch -> fail-open ineligible;
5. reference/carrier/event-input safety violation -> fail-open ineligible;
6. unresolved/Auto/triplet/non-4/4/pickup/non-16-step geometry -> fail-open ineligible;
7. event identity/string/fret/MIDI mismatch -> fail-open ineligible;
8. Product-validator rejection -> fail-open ineligible;
9. helper import/throw/malformed return -> fail-open ineligible;
10. response contains no candidate row-level render stream;
11. Product/PDF/client code contains no consumer of `productPlacementCandidateCanary`;
12. safety accounting reports no external/reference assets, Modal/GPU, `main`, Production, or Product/PDF authority change.

## Explicit non-authorizations

This freeze does **not** authorize:

- implementing Phase 11;
- using candidate placement as canonical `renderEvents`;
- Product UI or PDF consumption;
- emitting candidate row-level placement from the live route;
- changing V143 runtime authority;
- changing analyzer authority;
- changing Phase 8 admission thresholds;
- weakening any Phase 4/9/10 gate;
- reference-facing accuracy claims;
- GOAT restricted access;
- SplitMySong/GuitarSet work;
- Modal/GPU/CUDA activity;
- `main` or Production changes.

## Rollback target

The rollback target is the Phase 10-complete branch state in which `/api/analyze-audio-tab` returns canonical Product fields plus existing research metadata only, and no `productPlacementCandidateCanary` field exists.

## Decision boundary

**Implementation remains NOT AUTHORIZED until the user explicitly approves this separately frozen Phase 11 canary phase.**

If authorization is later given, implementation must stay exactly within C1–C12. Any desire to make candidate placement canonical Product/PDF authority is a later, separately frozen phase and cannot be inferred from Phase 11 authorization.
