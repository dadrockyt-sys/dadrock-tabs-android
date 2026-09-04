# FULL_MIXTURE_ADMITTED_SHADOW_EFFECT_VALIDATION_V1 — PHASE 9 RESULT

Date: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`  
Status: **`PHASE9_ADMITTED_SHADOW_EFFECT_PASS / EXPECTED_EFFECT_OBSERVED / DETERMINISTIC / INSTRUMENT_AUTHORITY_INVARIANT / PRODUCT-PDF_AUTHORITY_UNCHANGED / NO_MODAL-GPU / NO_REFERENCE_SCORE`**

## Frozen input contract

Pre-implementation freeze:

`docs/checkpoints/SONGSTERR_FULL_MIXTURE_ADMITTED_SHADOW_EFFECT_VALIDATION_V1_PREIMPLEMENTATION_FREEZE_20260903.md`

Freeze commit: `eb61fa0151b3491f492804a6d29d9b0788ef762d`.

Frozen status:

**`SHADOW EFFECT VALIDATION AUTHORIZED / VERIFIER-ONLY PREFERRED / PRODUCT-PDF AUTHORITY UNCHANGED / SYNTHETIC REFERENCE-BLIND ONLY / NO MODAL-GPU / NO REFERENCE SCORE / MAIN+PRODUCTION UNTOUCHED`**.

## Canonical implementation

- `b23b1dbcf66bf44372b84ae04e3611e9228ec220` — added `analyzer/verify_full_mixture_admitted_shadow_effect_validation_v1.mjs` with the frozen deterministic synthetic T1–T12 experiment matrix.
- `bd9fc1edee44cf5ee5f2e8fa01904e911df7788a` — added the isolated read-only CPU-only workflow `.github/workflows/full-mixture-admitted-shadow-effect-validation-v1.yml`.

A second verifier-only file, `analyzer/verify_full_mixture_admitted_shadow_effect_v1.mjs`, was also added concurrently at `7af40b52075a044a8d7333dfef22e38e364cba02`. It is non-authoritative for this result; the canonical frozen verifier/workflow above supplied the Phase 9 evidence. It did not change runtime, Product or PDF implementation.

## Experiment evidence

Workflow: `Full Mixture Admitted Shadow Effect Validation V1`

- run: `33828829026`;
- job: `100887194463`;
- tested head: `bd9fc1edee44cf5ee5f2e8fa01904e911df7788a`;
- conclusion: **SUCCESS**;
- T1–T12: **PASS**;
- safety-evidence gate: **PASS**.

The emitted evidence recorded:

- `referenceBlind = true`;
- `shadowOnly = true`;
- `trustedObservationEffectObserved = true`;
- `deterministicShadowEffect = true`;
- `instrumentAuthorityInvariant = true`;
- `sourceEventsMutated = false`;
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

## T1–T12 result

- T1 null-observation unresolved baseline parity — PASS.
- T2 trusted complete observation produces the expected shadow timing/measure/subdivision effect — PASS.
- T3 repeated identical inputs produce deterministic identical shadow effect — PASS.
- T4 instrument authority/string-fret decoding is invariant to the admitted global structure observation — PASS.
- T5 source events remain immutable — PASS.
- T6 explicit user structure priors retain field-by-field precedence — PASS.
- T7 forbidden provenance rolls back to the exact baseline effect — PASS.
- T8 malformed/out-of-contract musical fields roll back to the exact baseline effect — PASS.
- T9 partial trusted observations remain bounded and cannot fabricate complete measure projection — PASS.
- T10 straight/triplet/Auto feel behavior remains bounded to the intended subdivision projection — PASS.
- T11 research-only/reference-blind/non-production contracts remain intact — PASS.
- T12 canonical Product/PDF construction remains statically isolated from mixture/shadow metadata — PASS.

## What the experiment establishes

Phase 9 demonstrates, on deterministic synthetic reference-blind fixtures, that a provenance-valid Phase 8 admitted full-mixture observation has a real and predictable downstream effect on the existing research `dualContextShadowProjection`. Complete structure observations resolve the intended timing, subdivision and measure projection; rejected or incomplete inputs retain bounded fail-open behavior.

The experiment also demonstrates that this effect does **not** alter instrument authority, source events, canonical analyzer output, Product authority or PDF authority. Explicit user priors remain authoritative field by field.

This is positive evidence that the research structure signal is internally useful and safely bounded. It is **not** an accuracy benchmark against real/reference transcriptions and is **not** Product/PDF promotion evidence by itself.

## Diff / isolation proof

The tested Phase 9 head is three commits ahead of the freeze and contains only the Phase 9 checkpoint/verifier/workflow additions. The current post-test branch also contains the concurrent duplicate verifier-only addition and checkpoint maintenance. Comparison from the Phase 9 freeze to the current checkpoint head found no `app/api/` runtime/Product route change and no Product/PDF implementation expansion attributable to Phase 9.

## Safety accounting

- synthetic/reference-blind only = true;
- external/reference audio assets read = false;
- GuitarSet read/scored = false;
- SplitMySong read/scored = false;
- GOAT restricted bytes read = false;
- reference score calls = 0;
- Modal invoked/deployed = false;
- GPU/CUDA used = false;
- canonical analyzer authority changed = false;
- Product authority expanded = false;
- PDF authority expanded = false;
- `main` modified = false;
- Production modified/promoted = false.

## Next authority boundary

Phase 9 does not authorize wiring `mixtureStructureContext` or `dualContextShadowProjection` into generated tab/events/renderEvents/measureGrid, Product UI, or PDF output.

Any Product-facing use must begin with a separate frozen Phase 10 contract defining a narrow reversible authority experiment, explicit baseline/control behavior, fail-open/rollback semantics, Product/PDF isolation or scoped authority, deterministic validation, and the evidence required before any further promotion.
