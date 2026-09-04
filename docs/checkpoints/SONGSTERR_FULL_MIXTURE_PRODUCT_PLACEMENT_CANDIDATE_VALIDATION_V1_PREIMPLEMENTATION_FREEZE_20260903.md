# FULL_MIXTURE_PRODUCT_PLACEMENT_CANDIDATE_VALIDATION_V1 — PHASE 10 PREIMPLEMENTATION FREEZE

Date: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`  
Pre-freeze source head: `5dfe60d157e5274b711770b10c5b3c9260731de8`  
Status: **`PRODUCT-AUTHORITY EXPERIMENT AUTHORIZED / EXPERIMENT-ONLY PLACEMENT CANDIDATE / LIVE PRODUCT-PDF WIRING NOT AUTHORIZED / CPU SYNTHETIC REFERENCE-BLIND ONLY / NO MODAL-GPU / NO REFERENCE SCORE / MAIN+PRODUCTION UNTOUCHED`**

## Authorization and purpose

The user explicitly authorized running the next Product-authority experiment in this continuation. This phase may construct and validate an **experiment-only** Product placement candidate. It does **not** authorize wiring that candidate into `app/api/analyze-audio-tab`, Preview/PDF routes, Product UI, `main`, Vercel Preview, or Production.

Phase 9 established that an admitted full-mixture observation has a deterministic bounded effect on the research timing/measure shadow projection. Phase 10 asks the next narrow question:

> If the existing canonical V143-safe event stream has playable event identity/string/fret/MIDI but no authenticated measure/step placement, can the admitted research structure produce a deterministic Product-contract-compatible **placement-only candidate** on synthetic known-truth fixtures without changing any non-placement authority?

This is a synthetic contract experiment, not a real-audio/reference accuracy benchmark.

## Frozen Product seam

The current Product contract accepts V143 structured rendering only through `renderEvents` validated by `validateV143RenderEvents`. Each row requires at least:

- `eventIndex`;
- `measure >= 1`;
- `step` in `0..15`;
- `stringIndex` in `0..5`;
- `fret` in `0..36`;
- integer MIDI.

The research `dualContextShadowProjection` can provide bounded timing/measure placement but remains `shadowOnly=true` and `productionEligible=false`.

Phase 10 must **not** relabel the research contract as production-eligible. It may only build a separate experiment candidate and compare that candidate with the immutable canonical baseline.

## Frozen narrow candidate scope

The experiment candidate may add **only `measure` and `step` placement authority**. It must preserve canonical Product event identity and instrument facts exactly:

- `eventIndex` unchanged;
- `stringIndex` unchanged;
- `fret` unchanged;
- `midi` unchanged.

It may use `durationSteps = 1` as a neutral Product-contract minimum and `techniques = []`; Phase 10 does not grant sustain, technique, string/fret, pitch, generated-tab, analyzer-selection, or measure-grid authority.

The candidate is admitted only when every frozen gate below passes:

1. canonical payload proves `v143RuntimeSafetyVerified=true`;
2. canonical baseline `renderEvents` is empty — existing authenticated Product `renderEvents` must never be replaced or rewritten;
3. dual-context fusion contract is version 1, reference-blind, reference-score unauthorized, carrier borrowing forbidden, `shadowOnly=true`, `productionEligible=false`;
4. structure authority reports `TRUSTED_FULL_MIXTURE_OBSERVATION`, complete measure projection, and resolved feel;
5. resolved structure is exactly straight **4/4**, pickup **0**, with a finite supported tempo and `subdivisionsPerSignatureUnit=4`;
6. candidate and canonical event counts match and every projection row maps one-to-one by event index;
7. projected `measureNumber` is integer >=1 and `subdivisionIndex` is integer >=0;
8. for straight 4/4, `measure = floor(subdivisionIndex / 16) + 1` and `step = subdivisionIndex % 16`, and the derived measure must equal the research `measureNumber`;
9. canonical event string/fret/MIDI must be valid and must match the shadow row's source string/fret/MIDI exactly; conditioned string/fret values are never promoted;
10. `validateV143RenderEvents(candidate)` must return the same row count and exact identity/instrument/placement values;
11. any missing/malformed/mismatched/out-of-scope input returns **no candidate** and leaves the canonical baseline object untouched;
12. the experiment helper/verifier/workflow must remain isolated from live Product/PDF/runtime wiring.

Why straight 4/4 / pickup 0 only: the existing V143 Product contract has a fixed 16-step-per-measure placement field. Phase 10 must not invent an unreviewed mapping for triplet feel, alternate meters, or pickup measure 0.

## Frozen synthetic experiment fixture

Use deterministic V143-runtime-safe synthetic events with valid start/end/string/fret/MIDI and **no source measure/step fields**. Use a provenance-valid admitted full-mixture observation resolving straight 4/4, pickup 0, at a fixed synthetic tempo.

The fixture must include events spanning at least two measures and boundary steps, including measure 1 step 0, a non-zero within-measure step, measure 1 step 15, and measure 2 step 0.

A known synthetic oracle records the expected `(eventIndex, measure, step, stringIndex, fret, midi)` rows. The canonical baseline must have zero structured `renderEvents`; the experiment candidate must be compared directly against this oracle.

This may report synthetic placement coverage/exact-match improvement. It must not be described as real-world transcription accuracy.

## Frozen P1–P12 matrix

- **P1 — Canonical baseline immutability:** canonical Product payload is created first, has no structured render events for the no-measure/no-step fixture, and is byte/JSON-equivalent before vs after candidate construction.
- **P2 — Known-truth placement effect:** complete trusted straight-4/4 structure produces the exact synthetic oracle measure/step rows across measure boundaries.
- **P3 — Product-contract compatibility:** `validateV143RenderEvents` accepts every candidate row without compaction/drop.
- **P4 — Placement-only authority:** candidate `eventIndex/stringIndex/fret/midi` are exactly canonical; only measure/step are newly authoritative.
- **P5 — Determinism:** repeated identical inputs produce identical candidate output and identical synthetic metrics.
- **P6 — Existing authenticated renderEvents win:** if canonical Product already has non-empty authenticated `renderEvents`, candidate construction returns no candidate and never overrides them.
- **P7 — Provenance/safety rollback:** non-trusted observation status, non-reference-blind fusion, carrier/reference authorization mismatch, or invalid safety contract returns no candidate.
- **P8 — Structure-scope rollback:** incomplete structure, Auto feel, triplet feel, non-4/4 meter, non-zero pickup, or invalid subdivision geometry returns no candidate.
- **P9 — Event-integrity rollback:** count/index/MIDI/string/fret mismatch between canonical events and shadow source rows returns no candidate.
- **P10 — Explicit-prior precedence survives:** a separately constructed fully resolved straight-4/4 context with an explicit supported tempo prior continues to drive shadow placement according to the already-resolved context; Phase 10 never bypasses Phase 8/3 precedence.
- **P11 — Live Product/PDF isolation:** no runtime route, Product UI, Preview/PDF implementation, canonical payload builder, render contract, or analyzer implementation is modified or reads the experiment candidate.
- **P12 — Safety accounting:** no external/reference asset, GuitarSet, SplitMySong, GOAT restricted bytes, reference scorer, Modal invocation/deploy, GPU/CUDA, `main`, Vercel Preview deployment, or Production mutation.

## Success criteria

Phase 10 passes only if all P1–P12 pass and the emitted safety evidence states:

- `referenceBlind=true`;
- `experimentOnly=true`;
- `liveProductWiringChanged=false`;
- `pdfAuthorityChanged=false`;
- `canonicalAnalyzerOutputChanged=false`;
- `canonicalPayloadMutated=false`;
- `placementOnlyAuthority=true`;
- `instrumentAuthorityInvariant=true`;
- `existingAuthenticatedRenderEventsOverridden=false`;
- `externalAudioAssetsUsed=false`;
- `guitarSetRead=false`;
- `splitMySongRead=false`;
- `goatRestrictedBytesRead=false`;
- `referenceScoreCalls=0`;
- `modalInvoked=false`;
- `gpuUsed=false`;
- `mainModified=false`;
- `productionModified=false`;
- every P1–P12 = `PASS`.

## Implementation boundary

Preferred implementation is verifier-only / experiment-helper-only under `analyzer/` plus an isolated read-only GitHub Actions workflow. Do not modify live runtime or Product/PDF implementation files unless this freeze is explicitly superseded by a later contract.

## Rollback

Rollback is trivial: delete/ignore the experiment-only helper/verifier/workflow. The canonical Product baseline is never mutated and no live route consumes the candidate.

## Not authorized by this phase

- wiring candidate render events into `structuredPayload`;
- setting `structuredRenderEligible=true` from the research signal in live code;
- changing `analysisEngine`;
- changing generated tab/events/string/fret/MIDI/techniques/sustain;
- changing Preview/PDF Product authority;
- deploying/invoking Modal;
- GPU/CUDA;
- reading/scoring reference assets;
- merging `main`;
- Vercel Preview or Production promotion.
