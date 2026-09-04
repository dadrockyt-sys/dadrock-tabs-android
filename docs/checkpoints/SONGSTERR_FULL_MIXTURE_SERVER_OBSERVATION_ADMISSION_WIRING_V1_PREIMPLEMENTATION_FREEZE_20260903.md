# FULL_MIXTURE_SERVER_OBSERVATION_ADMISSION_WIRING_V1 — PRE-IMPLEMENTATION FREEZE

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`SERVER RESEARCH-CONTEXT TRUST AUTHORIZED / PRODUCT-PDF AUTHORITY UNCHANGED / FAIL-OPEN REQUIRED / NO MODAL-GPU / NO REFERENCE SCORE`**

## Authorization

The user explicitly authorized proceeding with the next required work on 2026-09-03. This freeze authorizes only the narrow server-side admission/wiring described below. It does not authorize `main` merge, Production promotion, Product/PDF authority expansion, GPU/CUDA, Modal deployment/invocation, external/reference corpus access, or reference-facing scoring.

## Purpose

Admit the already-Phase-7 analyzer-supplied `mixtureObservation` into the existing server-owned `buildAiTabMixtureStructureContextV1(...)` research context, while preserving canonical analyzer/Product/PDF behavior and request success/failure semantics.

The server may trust a Phase-7 observation only after independent server-side provenance/admission checks. A bad or unavailable analyzer observation must behave exactly like no observation.

## Frozen authority boundary

Authorized:

- server may read `analyzerData?.mixtureObservation`;
- server may independently admit/reject it;
- an admitted observation may be supplied only to `buildAiTabMixtureStructureContextV1(...)`;
- the resulting `mixtureStructureContext` and existing `dualContextShadowProjection` remain research metadata.

Not authorized:

- changing `structuredPayload` fields;
- changing generated tab, events, render events, measure grid, tuning, capo, difficulty, confidence, techniques, analysis engine, or analyzer selection;
- changing PDF/preview inputs or rendering;
- changing request admission/authentication or analyzer HTTP status behavior;
- making `mixtureStructureContext` Product-authoritative;
- `main`/Production promotion;
- Modal/GPU/reference work.

## Baseline-first fail-open rule — FROZEN

The route must first build the exact canonical baseline mixture context using:

```text
mixtureObservation: null
```

with the existing server-normalized `structurePrior` and server-owned `mixtureSource`.

Only after that baseline succeeds may the route attempt analyzer-observation admission.

If any observation-only admission or candidate-context construction step fails for any reason, the route must retain the already-built baseline context and continue normally. The analyzer observation must not change an otherwise-valid request into an error.

This preserves existing validation authority for `structurePrior` and `mixtureSource`: failures in those server-owned inputs remain canonical failures exactly as before.

## Server-side observation admission — FROZEN

An analyzer observation may be considered only if it is a plain object and proves all of the following:

- `version === 1`;
- `provenance.sourceKind === 'full-mixture'`;
- `provenance.sourceIdentity === 'request-audio'`;
- `provenance.referenceBlind === true`;
- `provenance.referenceRuntimeInputUsed === false`;
- diagnostics are present and consistent with Phase 7/6 provenance;
- `diagnostics.referenceBlind === true`;
- `diagnostics.carrierInputUsed === false`;
- `diagnostics.transcribedEventInputUsed === false`;
- `diagnostics.wavAdapter.fullMixtureOnly === true`;
- `diagnostics.wavAdapter.separatedCarrierUsed === false`;
- `diagnostics.wavAdapter.transcribedEventInputUsed === false`.

The server may not repair, infer, substitute, or partially trust missing provenance.

After provenance admission, the existing `buildAiTabMixtureStructureContextV1(...)` remains authoritative for field-level musical validation, confidence/method validation, user-prior precedence, and observation version/value rules. If that candidate build throws, the route falls back to the baseline null-observation context.

## User-prior precedence — FROZEN

Existing Phase 3 semantics remain unchanged:

- explicit user structure priors always win field-by-field;
- admitted full-mixture observations may fill only Auto/unresolved fields;
- absent/low-information observation fields remain unresolved;
- no observation may overwrite an explicit user tempo, meter, pickup, or feel.

## Product/PDF isolation — FROZEN

`mixtureStructureContext` and `dualContextShadowProjection` remain response research metadata only.

This phase must not change:

- `app/api/generate-tab-preview/route.js`;
- `app/api/generate-tab-pdf/route.js`;
- `lib/createJimmyPaigeProfessionalPdf.js`;
- any generated/rendered tab or PDF input;
- any UI/Product decision path.

## Frozen verification matrix — T1–T12

T1. **Baseline-first ordering:** static proof that the null-observation baseline context is built before reading/admitting analyzer observation.

T2. **Trusted observation connected:** a synthetic trusted Phase-7-shaped observation is admitted and fills unresolved Auto structure fields in `mixtureStructureContext`.

T3. **User prior precedence:** explicit user priors remain authoritative over disagreeing admitted observation fields.

T4. **Missing observation fail-open:** absent/null analyzer observation retains baseline context and request semantics.

T5. **Malformed observation fail-open:** non-object/malformed observation retains baseline context.

T6. **Bad provenance fail-open:** carrier/reference/event/separated-stem provenance violations retain baseline context.

T7. **Field validation fail-open:** provenance-valid but musically invalid version/value/confidence/method retains baseline context rather than failing the route.

T8. **Canonical payload isolation:** `structuredPayload` is built before mixture observation trust and never reads `mixtureStructureContext`/observation.

T9. **Analyzer/status isolation:** analyzer selection, request validation, analyzer fetch/status handling, and V143 safety gate do not depend on mixture observation.

T10. **Product/PDF isolation:** no Product/PDF file is changed or consumes the admitted observation/context.

T11. **No Modal/GPU/reference activity:** validation records Modal invoked=false, GPU used=false, external/reference reads=false, reference score calls=0.

T12. **Rollback proof:** changing the candidate observation path back to null restores the exact pre-Phase-8 server research-context behavior with no other rollback.

## Implementation shape — FROZEN

Prefer the smallest branch-local implementation:

- one server-side admission helper in `lib/`;
- baseline `buildAiTabMixtureStructureContextV1(... mixtureObservation: null ...)` remains explicit;
- one fail-open candidate build from admitted analyzer observation;
- deterministic/static verifier and isolated CPU-only workflow;
- no unrelated refactor.

## Safety accounting at freeze time

- Phase 1–7 boundaries retained = true;
- analyzer runtime already carries research `mixtureObservation` = true;
- server currently trusts analyzer observation = false;
- Product/PDF currently trusts mixture context = false;
- reference score calls in this phase = 0;
- external/reference audio read = false;
- GuitarSet read = false;
- SplitMySong read = false;
- GOAT restricted bytes read = false;
- Modal invoked/deployed = false;
- GPU/CUDA used = false;
- `main` modified = false;
- Production modified/promoted = false.

## Success meaning

A T1–T12 pass establishes only that a provenance-valid Phase-7 analyzer observation can safely populate the server-owned research `mixtureStructureContext` while malformed/untrusted observations fail open to the pre-existing null-observation baseline.

It does **not** establish transcription accuracy, Product/PDF correctness, Production eligibility, or reference-facing improvement, and it does not authorize Product/PDF authority or Production promotion.
