# FULL_MIXTURE_PRODUCT_PLACEMENT_CANONICAL_PROMOTION_V1 — PREIMPLEMENTATION FREEZE

Date: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`  
Pre-freeze head: `71097e3bb4929806ab8d454655668eabbe560ccc`  
Status: **`PHASE12_CANONICAL_PRODUCT-PDF_PLACEMENT_PROMOTION_AUTHORIZED / BRANCH_ONLY / EXISTING_AUTHENTICATED_PLACEMENT_WINS / STRICT_CANDIDATE+QUALITY_GATES / NO_MAIN-PRODUCTION-DEPLOY / NO_MODAL-GPU / NO_REFERENCE_SCORE`**

## User authorization

The user explicitly authorized the Product/PDF placement promotion after Phase 11 closed green.

This authorization crosses the next authority boundary only: a Phase-10/11-validated, reference-blind, placement-only candidate may become canonical `renderEvents` in the branch response when every frozen Phase 12 gate passes.

It does **not** authorize:

- merge to `main`;
- Vercel Preview or Production deployment/promotion;
- changing payment, token, email-delivery, or pricing logic;
- weakening V143 runtime safety, Phase 8 provenance admission, Phase 10 candidate integrity, or PDF validation;
- external/reference corpus reads or reference-facing scoring;
- GOAT restricted bytes, SplitMySong, GuitarSet prospective players;
- Modal deployment/invocation, GPU or CUDA.

## Purpose

Phase 10 proved exact deterministic placement recovery for the frozen seven-event synthetic fixture. Phase 11 proved the same candidate can be evaluated safely in the live server path without changing canonical output.

Phase 12 authorizes the smallest controlled Product/PDF promotion:

`canonical structured payload with no authenticated placement`
`+ trusted admitted full-mixture structure context`
`+ Phase 10 placement-only candidate`
`+ post-promotion V143 quality gate`
`-> canonical structured V143 Rhythm renderEvents`

Existing authenticated analyzer placement always wins and is never replaced.

## Frozen implementation seam

Inside `app/api/analyze-audio-tab/route.js`:

1. analyzer request/status and V143 runtime anti-leakage gate remain unchanged;
2. `buildJimmyPaigeAnalysisPayload(...)` still builds the canonical analyzer baseline first;
3. Conditioning V1, Phase 8 mixture admission, and dual-context shadow projection remain unchanged;
4. Phase 11 canary is evaluated against the pre-promotion baseline for continuity/observability;
5. only then may Phase 12 build a promoted payload copy;
6. the response spreads the promoted payload copy instead of the baseline only when promotion succeeds.

No candidate data may flow backward into analyzer selection, request validation, analyzer HTTP handling, conditioning, or Phase 8 admission.

## Existing authenticated placement precedence — FROZEN

If baseline `structuredPayload.renderEvents.length > 0`:

- no Phase 12 candidate is built for authority;
- existing analyzer-authenticated Product placement remains canonical exactly as before;
- `analysisEngine`, `analysisQuality`, render counts and structured eligibility remain the baseline values;
- Phase 12 reports `promoted=false`, reason `AUTHENTICATED_RENDER_EVENTS_PRESENT`;
- no merge/supplement/reindex/replacement is allowed.

## Promotion eligibility — FROZEN

Promotion may occur only if all are true:

1. `structuredPayload.payloadContract.v143RuntimeSafetyVerified === true`;
2. `structuredPayload.payloadContract.transcriptionType === 'rhythm'`;
3. baseline `analysisEngine === 'v143-reference-free-rhythm-fallback'`;
4. baseline `renderEvents` exists and is empty;
5. baseline canonical `events` exists and is non-empty;
6. existing Phase 10 `buildFullMixtureProductPlacementCandidateV1(...)` returns a non-null candidate without any gate weakening;
7. candidate contract remains version 1, experiment-only lineage, placement-only, reference-blind, reference-score unauthorized, production-ineligible, and not previously live-authorized;
8. candidate baseline render count equals zero;
9. candidate row count exactly equals canonical event count;
10. `validateV143RenderEvents(candidate.renderEvents)` accepts every row with no drop/compaction/reindex difference;
11. candidate rows preserve canonical `eventIndex`, `stringIndex`, `fret`, and `midi` exactly;
12. only `measure`/`step` placement authority is newly admitted; `durationSteps` remains the Phase 10 bounded value and techniques remain empty unless a later separately frozen phase authorizes technique promotion;
13. a post-promotion V143 quality report passes after canonical event identity/instrument facts are combined with the admitted candidate measure/step placement;
14. the promotion helper can construct a canonical copy without mutating the baseline payload.

Any failed gate means **no promotion** and exact baseline Product behavior remains.

## Post-promotion quality gate — FROZEN

Phase 12 must not merely flip `analysisEngine` because a candidate exists.

The helper must build an internal effective quality input by combining each canonical event with only the candidate `measure` and `step`, preserving every canonical event identity/instrument field. It then runs the existing `buildV143AnalyzerQualityReport(...)` against:

- `referenceFree: true`;
- those effective quality events;
- the validated promoted `renderEvents`.

Promotion requires `analysisQuality.passed === true`.

This keeps the existing V143 minimum-event/survival/playability/placement/pitch/measure quality thresholds active after placement promotion.

## Canonical promoted payload — FROZEN

On successful promotion, return a new payload copy with:

- `renderEvents = validated candidate renderEvents`;
- `renderContractVersion = 1`;
- `analysisEngine = 'v143-reference-free-rhythm'` so the already-existing Preview/PDF professional renderer consumes the structured stream;
- `analysisQuality = post-promotion quality report`;
- `payloadContract.renderEventCount = promoted row count`;
- `payloadContract.renderContractVersion = 1`;
- `payloadContract.analyzerQualityGatePassed = true`;
- `payloadContract.structuredRenderEligible = true`;
- a bounded `payloadContract.placementPromotion` marker naming Phase 12 and recording placement-only/reference-blind authority;
- `payloadContract.productionPromotionAuthorized` remains **false** because `main`/Production deployment is not authorized by this phase.

The following remain unchanged exactly:

- `generatedTab`;
- canonical `events` including start/end/string/fret/MIDI/technique fields;
- `measureGrid`;
- tuning/tempo/timeSignature/keySignature/difficulty/techniques/confidence/note count/audio metadata;
- analyzer selection and V143 runtime safety facts.

## Product/PDF consumption — FROZEN

No rewrite of Preview/PDF/payment routes is required or authorized unless verification proves otherwise.

Existing behavior already forwards `analysisMetadata.renderEvents` and `analysisMetadata.analysisEngine` from `/ai-tab` to:

- `/api/generate-tab-preview`;
- `/api/generate-tab-pdf`.

Existing `createJimmyPaigeProfessionalPdf(...)` / `createAiTabPdf(...)` already require:

- Rhythm transcription;
- `analysisEngine === 'v143-reference-free-rhythm'`;
- non-empty `validateV143RenderEvents(...)`-accepted rows;

and fail closed rather than silently downgrading an identified structured V143 request.

Phase 12 therefore promotes by changing only the analysis response authority when gates pass. Payment/token/email logic remains untouched.

## Promotion metadata — FROZEN

Append one bounded top-level field:

```text
productPlacementPromotion: {
  promotionContract: {
    name: 'full-mixture-product-placement-canonical-promotion',
    version: 1,
    placementOnlyAuthority: true,
    referenceBlind: true,
    referenceScoreAuthorized: false,
    productAuthority: true,
    pdfAuthority: true,
    productionDeploymentAuthorized: false
  },
  promoted: boolean,
  reason: <finite enum>,
  baselineRenderEventCount: integer,
  canonicalRenderEventCount: integer
}
```

Finite reasons must include at minimum:

- `PROMOTED_PLACEMENT_ONLY`;
- `AUTHENTICATED_RENDER_EVENTS_PRESENT`;
- `NON_V143_RHYTHM_BASELINE`;
- `CANDIDATE_INELIGIBLE`;
- `QUALITY_GATE_REJECTED`;
- `PROMOTION_FAIL_OPEN`.

No raw exception text, request identifiers, tokens, URLs, or duplicate event stream may appear in this metadata.

## Failure semantics — FROZEN

Promotion-specific failures are fail-safe to the pre-Phase-12 baseline:

- malformed/ineligible candidate -> baseline response;
- post-promotion quality failure -> baseline response;
- promotion helper exception -> baseline response;
- no promotion-specific failure may turn an otherwise valid analysis request into an HTTP error.

Canonical failures that occur before the promotion seam remain canonical failures and must not be suppressed.

## P12 verification matrix — R1–R16

R1. **Baseline-first ordering:** canonical analyzer payload and Phase 8/11 research data exist before promotion.

R2. **Synthetic promotion succeeds:** frozen seven-event Phase 10 fixture promotes 0 -> 7 canonical render events.

R3. **Exact placement:** promoted rows match the frozen known-truth seven-event oracle exactly.

R4. **Instrument authority invariant:** canonical eventIndex/string/fret/MIDI remain exact; generatedTab/events are unchanged.

R5. **Existing authenticated placement wins:** non-empty baseline renderEvents are returned unchanged and never merged/replaced.

R6. **Non-V143/Rhythm rollback:** lead/bass/non-V143/fallback mismatch cannot promote.

R7. **Provenance/safety rollback:** all Phase 10 reference/carrier/trust gates still block promotion.

R8. **Geometry rollback:** unresolved/triplet/non-4/4/pickup/non-16-step geometry cannot promote.

R9. **Event-integrity rollback:** candidate/canonical count/index/string/fret/MIDI mismatch cannot promote.

R10. **Product validator rollback:** validator-rejected candidate cannot promote.

R11. **Quality gate rollback:** fewer than existing minimum valid events or another post-promotion quality failure cannot promote.

R12. **Canonical contract update:** successful promotion sets render counts/version, structured eligibility, quality pass, exact structured analysis engine, and bounded placement marker while keeping production deployment unauthorized.

R13. **PDF structured renderer proof:** a promoted synthetic payload passed to the existing professional PDF wrapper selects `v143-structured-rhythm`, accepts all promoted rows, and produces non-empty PDF bytes without external/reference assets.

R14. **Client/route forwarding proof:** `/ai-tab` still forwards response `renderEvents` + `analysisEngine` to Preview/PDF; payment/token/email verification logic is unchanged.

R15. **Promotion exception rollback:** injected promotion-only exception returns exact baseline Product payload plus `promoted=false`; no request-authority mutation.

R16. **Safety/build gate:** deterministic CPU verifier + full branch build pass; external/reference reads=false; reference score calls=0; Modal/GPU/CUDA=false; Vercel Preview/Production deployment=false; `main`/Production modified=false.

## Preferred implementation shape — FROZEN

- one pure server helper in `lib/` for promotion;
- reuse the existing Phase 10 candidate builder unchanged;
- reuse existing `validateV143RenderEvents` and `buildV143AnalyzerQualityReport` unchanged;
- minimal route change after Phase 11 canary;
- no Preview/PDF/payment/client rewrite unless required by failed integration proof;
- one deterministic CPU verifier and one isolated GitHub Actions workflow using repository-standard `npm ci` + `npm run build`;
- frequent `CURRENT_STATE.md` checkpoints.

## Rollback

Exact rollback is:

1. remove Phase 12 promotion helper;
2. remove its route import/call and switch response spread back to baseline `structuredPayload`;
3. remove `productPlacementPromotion` metadata;
4. remove Phase 12 verifier/workflow.

Phase 11 canary and all earlier phases remain intact.

## Success meaning

A green Phase 12 establishes branch-local Product/PDF **placement authority** for the narrowly admitted reference-blind full-mixture candidate under the frozen gates.

It does not establish real-audio transcription accuracy, does not authorize `main`/Production deployment, does not authorize external/reference scoring, and does not broaden authority beyond placement (`measure`/`step`).
