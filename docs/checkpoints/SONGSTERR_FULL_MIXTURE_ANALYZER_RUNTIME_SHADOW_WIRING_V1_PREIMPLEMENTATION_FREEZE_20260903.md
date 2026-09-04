# FULL_MIXTURE_ANALYZER_RUNTIME_SHADOW_WIRING_V1 — PRE-IMPLEMENTATION FREEZE

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`REFERENCE-BLIND CPU SHADOW WIRING AUTHORIZED / ANALYZER AUTHORITY UNCHANGED / PRODUCT TRUST NOT AUTHORIZED / MODAL DEPLOY-INVOKE NOT AUTHORIZED`**

## Purpose

Connect the already-frozen Phase 6 adapter to the analyzer runtime as an **append-only research shadow observation** using the analyzer's already-normalized full-mixture PCM WAV.

This phase exists only to prove that the Phase 6 observation can travel through analyzer runtime without changing the canonical transcription path, analyzer selection, request success/failure semantics, Product/PDF output, or Production behavior.

## Frozen upstream dependency

Use only:

`analyzer/full_mixture_wav_adapter_v1.py`

```python
estimate_full_mixture_structure_from_wav_v1(path) -> dict
```

The Phase 6 adapter contract remains unchanged. No event-derived, carrier-derived, separated-stem-derived, reference-derived, or score-derived substitute is permitted.

## Frozen invocation seam

The shadow call must occur in analyzer runtime:

1. **after** the request audio has been normalized into the analyzer's full-mixture PCM WAV;
2. using that exact already-normalized full-mixture WAV path;
3. **before** any separation, carrier selection, carrier-specific interpretation, Basic Pitch/event interpretation, V143 contextual pruning, or other transcription-specific reasoning can provide input to the shadow estimator.

The shadow estimator may read only the normalized full-mixture WAV path. It may not read or infer from separated stems, selected carriers, generated events, professional/reference labels, GuitarSet, SplitMySong, GOAT restricted bytes, or any scorer output.

If the live runtime implementation does not expose a clean seam satisfying all three ordering constraints, implementation must stop rather than weaken this contract.

## Frozen runtime output contract

The analyzer response may add exactly one research-only field:

```text
mixtureObservation
```

Allowed values:

- a trusted Phase 3-compatible object returned by `estimate_full_mixture_structure_from_wav_v1(...)`; or
- `null` when the shadow path is unavailable or fails.

The field is append-only metadata. It is **not** canonical analyzer output and is not authorized to alter any existing field.

No existing response field may be removed, renamed, reordered for semantic reasons, gated, reranked, corrected, vetoed, replaced, or recomputed from `mixtureObservation`.

## Canonical-authority invariant — FROZEN

The pre-existing analyzer path remains authoritative for all transcription/product behavior.

`mixtureObservation` must never influence, directly or indirectly:

- analyzer selection;
- request admission/authentication;
- normalized audio selection;
- separator/carrier selection;
- Basic Pitch or event extraction;
- V143/V144/V145/V147 logic;
- generated events, render events, measure grid, tabs, fingering, tuning, capo, role, confidence, or analysis engine identity;
- success/failure status of an otherwise-valid analyzer request;
- PDF generation/rendering;
- Product/UI decisions;
- any reference-facing score or promotion decision.

The only behavioral difference allowed between shadow-disabled and shadow-successful executions is the additive research metadata value of `mixtureObservation` (plus research-only diagnostics needed to verify the shadow itself, if isolated under that field).

## Fail-open isolation — FROZEN

The shadow path must be fail-open with respect to the canonical analyzer request.

For any of the following, canonical analysis continues unchanged and `mixtureObservation` becomes `null`:

- adapter import unavailable;
- normalized full-mixture WAV path unavailable at the shadow seam;
- file missing/unreadable;
- unsupported/corrupt WAV;
- `ValueError` from Phase 6 admission;
- any unexpected adapter exception;
- malformed/non-dict adapter result;
- result missing the frozen trusted full-mixture provenance required by Phases 3–6;
- any shadow-only timeout/budget guard, if implementation introduces one;
- any other shadow-only failure.

Shadow failure must not change HTTP/analyzer status, canonical exception behavior, canonical payload fields, or canonical event/tab output.

No shadow failure may be promoted to a Product-facing error.

## Trusted-observation admission — FROZEN

Before a non-null `mixtureObservation` may be appended, the wiring must verify the minimum frozen provenance/safety assertions already established by Phases 3–6, including that the observation is full-mixture/request-audio/reference-blind and does not claim separated-carrier or transcribed-event input.

At minimum, the accepted observation must be a dictionary/object and its frozen provenance/diagnostic assertions must remain consistent with:

- full mixture only;
- request audio source;
- reference blind;
- no reference runtime input;
- no separated carrier input;
- no transcribed-event input.

If admission cannot be proven, append `mixtureObservation: null`; do not repair, reinterpret, or partially trust the object.

## `/api/analyze-audio-tab` boundary — FROZEN

This phase does **not** authorize the Next.js server route to trust analyzer-supplied structure.

`app/api/analyze-audio-tab/route.js` currently builds Phase 3 with:

```text
mixtureObservation: null
```

That server-side admission point must remain unchanged during this analyzer-runtime wiring phase.

Therefore an analyzer response may carry append-only `mixtureObservation`, but `/api/analyze-audio-tab` must continue to ignore it for `mixtureStructureContext` until a separate server-side admission/wiring contract is frozen and authorized.

## Product/PDF/Production boundary — FROZEN

This phase must not modify:

- Product rendering or UI behavior;
- PDF generation or metadata inputs;
- canonical structured payload semantics;
- Vercel Production configuration;
- `main`;
- deployed Modal apps/endpoints;
- analyzer environment-variable selection;
- production promotion state.

No deployment or live invocation is authorized by this freeze.

## CPU/reference-blind boundary — FROZEN

Validation for this phase is restricted to static inspection and deterministic synthetic/local CPU fixtures.

Not authorized:

- Modal invocation or deployment;
- GPU/CUDA;
- external audio/reference corpus reads;
- GuitarSet reads/scoring;
- SplitMySong reads/scoring;
- GOAT restricted-byte reads/scoring;
- professional/reference score calls;
- accuracy claims from this phase.

## Frozen verification matrix — S1–S12

S1. **Seam ordering:** static proof that shadow input is the already-normalized full-mixture PCM WAV and the call occurs before separation/carrier/event-specific interpretation.

S2. **Success append-only:** deterministic synthetic PCM WAV produces a non-null trusted `mixtureObservation` while all canonical analyzer payload fields remain byte/structure-equivalent to the shadow-disabled baseline, excluding only explicitly isolated shadow metadata.

S3. **Adapter exception fail-open:** forced adapter exception yields `mixtureObservation: null`; canonical result/status unchanged.

S4. **Invalid WAV fail-open:** invalid/unsupported shadow WAV yields `null`; canonical result/status unchanged.

S5. **Missing WAV fail-open:** unavailable normalized shadow path yields `null`; canonical result/status unchanged.

S6. **Malformed observation fail-open:** non-dict or safety/provenance-invalid adapter result yields `null`; canonical result/status unchanged.

S7. **No carrier/event input:** static verifier proves the shadow call arguments contain only the normalized full-mixture WAV path and do not consume separated carrier/stem/event/reference inputs.

S8. **No authority crossing:** static verifier proves `mixtureObservation` is never read by canonical analyzer decision logic, event/tab generation, separator/carrier choice, or request status logic.

S9. **Server trust unchanged:** `/api/analyze-audio-tab` still supplies `mixtureObservation: null` to `buildAiTabMixtureStructureContextV1` and does not consume analyzer-supplied `mixtureObservation` for Product structure.

S10. **Product/PDF isolation:** no Product/PDF file is changed by the implementation commit and no shadow metadata enters generated/rendered tab or PDF inputs.

S11. **No Modal/GPU/reference activity:** validation evidence records Modal invoked=false, GPU used=false, external/reference corpus read=false, reference score calls=0.

S12. **Rollback proof:** removing/disabling the shadow hook restores the exact pre-wiring canonical behavior with analyzer-side `mixtureObservation` absent or null and no other required rollback.

## Implementation shape — FROZEN

Prefer the smallest possible branch-local implementation:

- one narrow helper/wrapper for fail-open shadow execution/admission if needed;
- one call at the frozen normalized-full-mixture seam;
- one append-only analyzer response field;
- deterministic/static verifier(s) for S1–S12;
- no unrelated refactor.

If wiring would require broad analyzer refactoring, changing canonical control flow, or touching Product/PDF/Production, stop and freeze a new contract instead.

## Safety accounting at freeze time

- Phase 1–6 frozen boundaries retained = true;
- reference score calls in this continuation = 0;
- external audio assets used = false;
- GuitarSet read = false;
- SplitMySong read = false;
- GOAT restricted bytes read = false;
- separated carrier used as shadow input = false;
- transcribed events used as shadow input = false;
- Modal invoked = false;
- GPU used = false;
- analyzer runtime modified by this freeze commit = false;
- `/api/analyze-audio-tab` trust modified = false;
- Product/PDF modified = false;
- Production modified = false;
- Production promotion authorized = false.

## Success meaning

An S1–S12 pass would establish only that the already-frozen Phase 6 full-mixture observation can be carried through analyzer runtime as isolated, fail-open, append-only research metadata without changing canonical behavior.

It would **not** establish real-song transcription accuracy, would **not** authorize server/Product trust of the observation, and would **not** authorize deployment or Production promotion.
