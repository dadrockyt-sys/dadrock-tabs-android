# FULL_MIXTURE_LIVE_CANDIDATE_OBSERVATION_CANARY_V1 — PHASE 11 PREIMPLEMENTATION FREEZE

Date: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`  
Pre-freeze source head: `ac8851e48e456eed8edc19c0abd920fafbfff443`  
Status: **`PHASE11 CONTRACT FROZEN / NON-AUTHORITATIVE LIVE-CANDIDATE OBSERVATION ONLY / IMPLEMENTATION NOT AUTHORIZED / PRODUCT-PDF AUTHORITY UNCHANGED / CPU SYNTHETIC REFERENCE-BLIND ONLY / NO MODAL-GPU / NO REFERENCE SCORE / MAIN+PRODUCTION UNTOUCHED`**

## Authorization boundary

The continuation request authorizes preserving project state and defining the next safe contract. The current checkpoint explicitly states that Phase 11 live-server implementation remains **NOT AUTHORIZED until separately and explicitly approved**.

This document therefore freezes the exact Phase 11 seam, metadata shape, gates, fail-open behavior, rollback proof, verification matrix, and safety boundaries **without modifying the live route or any Product/PDF authority**.

Nothing in this freeze authorizes:

- importing or invoking the Phase 10 experiment helper from the live route;
- adding live canary computation to `app/api/analyze-audio-tab/route.js`;
- changing canonical `structuredPayload`, `events`, `renderEvents`, `measureGrid`, `generatedTab`, `analysisEngine`, or analyzer selection;
- changing Preview/PDF input or Product UI behavior;
- deploying/invoking Modal or using GPU/CUDA;
- reading/scoring external reference assets, GuitarSet, SplitMySong, or restricted GOAT bytes;
- changing `main`, Vercel Preview, or Production.

## Purpose

Phase 10 proved that, on a deterministic reference-blind synthetic fixture, the admitted full-mixture structure signal can construct a Product-contract-compatible **placement-only** candidate when canonical V143-safe events have valid identity/string/fret/MIDI but no authenticated measure/step placement.

Phase 11 asks a narrower live-runtime integration question:

> Can the server compute **observation-only candidate eligibility metadata** from the already-admitted live research context while leaving every canonical Product/PDF field and request success/failure path unchanged?

This phase is a canary/observability phase only. It is **not** Product placement promotion and is **not** a real-world transcription accuracy benchmark.

## Frozen live seam

The only admissible future implementation seam is inside `app/api/analyze-audio-tab/route.js` **after** all of the following already exist successfully:

1. analyzer response and V143 runtime safety gate;
2. immutable canonical `structuredPayload = buildJimmyPaigeAnalysisPayload(...)`;
3. server-normalized `conditioningContract`;
4. baseline-first + independently admitted `mixtureStructureContext`;
5. `dualContextShadowProjection` research metadata.

A future Phase 11 canary may read only those already-built server values. It must not participate in constructing any earlier value and must not be passed into the canonical payload builder.

The current return object is the authority boundary: `...structuredPayload` remains canonical and Phase 11, if later authorized, may append only one new top-level **research metadata** field after the existing research fields.

## Frozen response metadata shape

If implementation is later explicitly authorized, the only new response field is:

```text
productPlacementCanary: {
  canaryContract: {
    name: 'full-mixture-product-placement-canary',
    version: 1,
    observationOnly: true,
    placementOnlyCandidate: true,
    productAuthorityChanged: false,
    pdfAuthorityChanged: false,
    referenceBlind: true,
    referenceScoreAuthorized: false,
    productionEligible: false
  },
  status: <ENUM>,
  reason: <ENUM>,
  evaluated: <boolean>,
  eligible: <boolean>,
  baselineRenderEventCount: <integer>,
  candidateRenderEventCount: <integer>,
  canonicalEventCount: <integer>,
  candidatePlacementCoverage: <0..1 or null>
}
```

Frozen rules:

- **No candidate `renderEvents` array may be returned.**
- No event-level measure/step rows may be exposed through this metadata field.
- No generated tab, fret/string/MIDI, timing, technique, or measure-grid payload may be duplicated into this field.
- `candidatePlacementCoverage` is an eligibility/coverage diagnostic only; it must never be named or interpreted as accuracy.
- The field must contain only bounded scalar/enum diagnostics so Product/PDF/UI code cannot accidentally consume candidate event rows.

Frozen status enum:

- `NOT_APPLICABLE` — request cannot enter the V143-safe placement canary contract;
- `BASELINE_AUTHENTICATED` — canonical Product already has authenticated `renderEvents`; candidate is not evaluated and canonical placement wins;
- `INELIGIBLE` — candidate gates fail safely;
- `ELIGIBLE_OBSERVATION_ONLY` — all candidate gates pass, but authority remains observational only;
- `CANARY_FAIL_OPEN` — canary-only computation threw/failed and the route continued unchanged.

Frozen reason enum must be finite and non-sensitive. At minimum it may distinguish:

- `NON_V143_OR_SAFETY_UNVERIFIED`;
- `AUTHENTICATED_RENDER_EVENTS_PRESENT`;
- `NO_CANONICAL_EVENTS`;
- `UNTRUSTED_OR_INCOMPLETE_STRUCTURE`;
- `UNSUPPORTED_GEOMETRY`;
- `EVENT_INTEGRITY_MISMATCH`;
- `PRODUCT_VALIDATOR_REJECTED`;
- `ELIGIBLE_PLACEMENT_ONLY`;
- `CANARY_EXCEPTION`.

No raw exception message, analyzer payload, audio URL, pathname, song/artist text, tokens, reference path, or event rows may be added to canary metadata.

## Frozen candidate gates

The Phase 11 canary must preserve the complete Phase 10 candidate gate semantics. Eligibility can be true only when all are true:

1. canonical `structuredPayload.payloadContract.v143RuntimeSafetyVerified === true`;
2. canonical `structuredPayload.renderEvents` exists and is empty;
3. canonical `structuredPayload.events` is non-empty;
4. dual-context fusion contract is version 1, `shadowOnly=true`, `referenceBlind=true`, `referenceScoreAuthorized=false`, `carrierStructureBorrowingAllowed=false`, `productionEligible=false`;
5. structure authority is `mixture-structure-context-v1`, observation status `TRUSTED_FULL_MIXTURE_OBSERVATION`, complete for measure projection, feel resolved;
6. shadow projection contract is version 1, reference-blind, shadow-only, reference-score unauthorized, production-ineligible;
7. resolved structure is exactly straight 4/4, pickup 0, supported finite tempo, `subdivisionsPerSignatureUnit=4`;
8. candidate event count equals canonical event count and maps one-to-one by canonical `eventIndex`;
9. source `stringIndex`, `fret`, and `midi` match canonical values exactly; conditioned instrument values are never promoted;
10. projected measure/subdivision geometry maps exactly to Product 16-step placement: `measure = floor(subdivisionIndex / 16) + 1`, `step = subdivisionIndex % 16`, with the derived measure matching research `measureNumber`;
11. `validateV143RenderEvents(candidate)` accepts every internally constructed candidate row unchanged;
12. any missing, malformed, provenance-invalid, geometry-invalid, integrity-invalid, or validator-rejected case yields `eligible=false` and no candidate rows escape the helper.

## Existing authenticated placement precedence — FROZEN

If canonical `structuredPayload.renderEvents.length > 0`:

- canonical placement wins absolutely;
- Phase 11 must not build a competing candidate;
- canary status is `BASELINE_AUTHENTICATED`;
- `evaluated=false`;
- `eligible=false`;
- `candidateRenderEventCount=0`;
- no Product field is changed.

This rule prevents the canary from becoming a shadow replacement path for already-authenticated Product placement.

## Canonical immutability — FROZEN

The canary may never mutate `structuredPayload` or any nested value.

A verifier must serialize/clone the canonical payload immediately before the canary call and prove exact JSON equivalence immediately after it.

The following canonical fields are specifically invariant:

- `generatedTab`;
- `events`;
- `renderEvents`;
- `renderContractVersion`;
- `measureGrid`;
- `analysisQuality`;
- `analysisEngine`;
- `payloadContract.structuredRenderEligible`;
- `payloadContract.productionPromotionAuthorized`;
- tuning/tempo/timeSignature/keySignature/difficulty/techniques/confidence/audio metadata.

## Fail-open request behavior — FROZEN

Phase 11 must be observationally fail-open:

- canary computation occurs only after the canonical route has already successfully built its normal response values;
- any canary-only exception is caught locally;
- the request must still return the same HTTP success response it would have returned without Phase 11;
- only the canary field may report `CANARY_FAIL_OPEN` / `CANARY_EXCEPTION`;
- no canary-only failure may change analyzer HTTP handling, V143 safety rejection, request validation, conditioning validation, or canonical Product payload construction.

Canonical failures remain canonical failures. Phase 11 may not catch, suppress, or reinterpret failures that occur before the canary seam.

## Product/PDF/UI isolation — FROZEN

A future Phase 11 implementation must not modify or be consumed by:

- `lib/jimmyPaigeAnalysisPayload.js`;
- `lib/v143RenderContract.js`;
- `app/api/generate-tab-preview/route.js`;
- `app/api/generate-tab-pdf/route.js`;
- `lib/createJimmyPaigeProfessionalPdf.js`;
- Product rendering components;
- PDF/preview payloads;
- analyzer selection or environment-variable routing.

No Product/PDF/UI code may read `productPlacementCanary` in Phase 11.

## Preferred future implementation shape — FROZEN

If separately authorized, use the smallest server-only change:

1. add one pure fail-open helper under `lib/` dedicated to building bounded canary metadata;
2. the helper may internally reconstruct the Phase 10 placement candidate solely to validate eligibility, but candidate rows remain local and are never returned;
3. import that helper into `app/api/analyze-audio-tab/route.js`;
4. call it only after `dualContextShadowProjection` is built;
5. append only `productPlacementCanary` to the JSON response;
6. add one deterministic verifier and one isolated CPU-only GitHub Actions workflow;
7. no unrelated refactor.

The Phase 10 file `analyzer/full_mixture_product_placement_candidate_v1.mjs` remains experiment-only. A future Phase 11 implementation should not directly wire that experiment module into the live route unless a later explicit freeze supersedes this boundary.

## Frozen C1–C14 verification matrix

- **C1 — Seam ordering:** static proof that analyzer safety, canonical payload, server conditioning/admission, and dual-context research projection are built before canary evaluation.
- **C2 — Canonical payload immutability:** canonical payload is JSON-identical before vs after canary computation.
- **C3 — Phase 10 gate equivalence:** the deterministic seven-event known-truth fixture that passed Phase 10 reports `ELIGIBLE_OBSERVATION_ONLY`, candidate count 7, coverage 1.0, while returning no candidate event rows.
- **C4 — Existing authenticated placement wins:** non-empty canonical `renderEvents` yields `BASELINE_AUTHENTICATED`, no candidate evaluation, no override.
- **C5 — Safety/provenance rollback:** V143 safety, fusion/reference/carrier, or trusted-observation violations yield non-eligible metadata only.
- **C6 — Geometry rollback:** Auto/triplet/non-4/4/non-zero-pickup/invalid subdivision geometry yields `INELIGIBLE`.
- **C7 — Event-integrity rollback:** event count/index/string/fret/MIDI/measure consistency mismatch yields `INELIGIBLE`.
- **C8 — Product validator rollback:** candidate compaction/rejection yields `INELIGIBLE` and no rows escape.
- **C9 — Fail-open exception:** forced canary-only exception returns canonical response semantics unchanged and reports only `CANARY_FAIL_OPEN` metadata.
- **C10 — Response-shape confinement:** canary object contains only the frozen bounded contract/scalar/enum fields; it contains no `renderEvents`, event arrays, raw exception text, analyzer payload, or request identifiers.
- **C11 — Product/PDF/UI isolation:** no Product/PDF/UI/preview implementation reads canary metadata and no such file is modified.
- **C12 — Canonical authority invariants:** `analysisEngine`, `structuredRenderEligible`, canonical render counts, generated tab, events, render events, and measure grid are unchanged.
- **C13 — Rollback proof:** removing the helper import/call/response field restores exact pre-Phase-11 route behavior with no other rollback.
- **C14 — Safety accounting:** external/reference assets=false; GuitarSet=false; SplitMySong=false; GOAT restricted bytes=false; reference score calls=0; Modal invoked/deployed=false; GPU=false; Vercel Preview deployment=false; `main` changed=false; Production changed=false.

## Success meaning

A future C1–C14 pass would establish only that the live server can safely **observe whether** a Phase-10-equivalent placement-only candidate would be eligible, without exposing candidate event rows or changing Product/PDF authority.

It would **not** establish real-audio transcription accuracy, would **not** make inferred placement canonical, would **not** authorize Product/PDF consumption, and would **not** authorize Production promotion.

## Rollback

Rollback must remain trivial and exact: remove the dedicated helper, its route import/call, the appended `productPlacementCanary` metadata field, verifier, and workflow. Canonical payload and Product/PDF code require no rollback because Phase 11 is forbidden from changing them.

## Implementation authorization state

**NOT AUTHORIZED.**

The next action after this freeze is to preserve it in `CURRENT_STATE.md` and wait for explicit user authorization before any Phase 11 live-server code, verifier, workflow, or route modification is created.
