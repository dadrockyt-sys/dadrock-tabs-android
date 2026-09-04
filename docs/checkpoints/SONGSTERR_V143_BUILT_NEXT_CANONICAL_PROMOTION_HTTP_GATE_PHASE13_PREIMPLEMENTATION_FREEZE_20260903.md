# V143 BUILT-NEXT CANONICAL PROMOTION HTTP GATE — PHASE 13 PREIMPLEMENTATION FREEZE

Date: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`

Status: **FROZEN / BRANCH-LOCAL / REFERENCE-BLIND / PREVIEW-SIMULATION-ONLY**

## Purpose

Close the final branch-local runtime seam before the now-authorized exact-branch Vercel Preview boundary.

The gate must prove, through the compiled Next.js HTTP routes rather than direct library calls, that a safe V143 Rhythm analyzer response can travel through:

1. `/api/analyze-audio-tab`;
2. Phase 8–12 conditioning/context/candidate/promotion logic;
3. canonical promoted `renderEvents`;
4. `/api/generate-tab-preview`;
5. the structured V143 Rhythm PDF renderer.

## Frozen fixture and trust boundary

- CPU only.
- No real audio download or decode.
- No external/reference audio or reference assets.
- No GuitarSet, SplitMySong, or GOAT reads.
- No Modal, GPU, or CUDA.
- A localhost analyzer stub is authoritative only for the deterministic synthetic fixture.
- The stub returns the same seven-event known-truth fixture and full-mixture observation lineage already frozen in Phase 12.
- The request advertises an inert synthetic audio URL but the gate must never fetch it; only the localhost analyzer stub receives it as metadata.
- Vercel Preview behavior is simulated locally with `VERCEL_ENV=preview` and `VERCEL_GIT_COMMIT_REF=v143-contextual-prune-lobo`.

## Required success evidence

The built Next server must prove all of the following:

- analysis HTTP status = 200;
- `rhythmCanaryActive=true`;
- analyzer runtime safety contract remains reference-free;
- `productPlacementPromotion.promoted=true`;
- promotion reason = `PROMOTED_PLACEMENT_ONLY`;
- baseline canonical placement count = 0;
- promoted canonical placement count = 7;
- exact known-truth placement = 7/7;
- canonical musical events/generated tab remain unchanged by placement promotion;
- Product/PDF request uses the promoted canonical payload returned by the analysis HTTP route;
- preview HTTP status = 200;
- response content type = PDF;
- PDF starts with `%PDF` and is non-trivial;
- Preview feature source = `v143-branch-preview-canary`;
- renderer mode = `v143-structured-rhythm`;
- invalid/missing analysis request still fails closed with HTTP 400;
- no Production state is touched.

## Failure behavior

Any missing trust/safety field, unexpected placement count, geometry mismatch, renderer fallback, HTTP error, or exception fails Phase 13. The gate may not silently downgrade a failed canonical-promotion proof into a passing renderer-only proof.

## Authority boundary

Phase 13 itself does not deploy to Vercel. The user has separately authorized the next exact-branch Vercel Preview boundary. Only after this gate is green may that Preview deployment be created/validated.

Still forbidden without fresh explicit authorization:

- merge/commit to `main`;
- Vercel Production deployment or Preview-to-Production promotion;
- Production alias/domain/environment changes;
- restricted/reference asset reads;
- reference-facing scoring;
- Modal/GPU/CUDA use.
