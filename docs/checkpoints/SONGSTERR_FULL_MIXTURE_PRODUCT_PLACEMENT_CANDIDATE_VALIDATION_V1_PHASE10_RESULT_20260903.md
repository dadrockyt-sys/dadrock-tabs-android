# FULL_MIXTURE_PRODUCT_PLACEMENT_CANDIDATE_VALIDATION_V1 — PHASE 10 RESULT

Date: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`  
Status: **`PHASE10_PRODUCT_PLACEMENT_CANDIDATE_PASS / SYNTHETIC_PLACEMENT_0_TO_100_PERCENT / 7_OF_7_EXACT / PRODUCT_VALIDATOR_ACCEPTED / LIVE_PRODUCT-PDF_AUTHORITY_UNCHANGED / NO_MODAL-GPU / NO_REFERENCE_SCORE`**

## Frozen input contract

Pre-implementation freeze:

`docs/checkpoints/SONGSTERR_FULL_MIXTURE_PRODUCT_PLACEMENT_CANDIDATE_VALIDATION_V1_PREIMPLEMENTATION_FREEZE_20260903.md`

Freeze commit: `697996069faa1a9167983357d1b94dada7c827fe`.

Frozen status:

**`PRODUCT-AUTHORITY EXPERIMENT AUTHORIZED / EXPERIMENT-ONLY PLACEMENT CANDIDATE / LIVE PRODUCT-PDF WIRING NOT AUTHORIZED / CPU SYNTHETIC REFERENCE-BLIND ONLY / NO MODAL-GPU / NO REFERENCE SCORE / MAIN+PRODUCTION UNTOUCHED`**.

## Experiment implementation

- `1cff2f5248ce7f8463928cbb3625f70d1bc97e4a` — added experiment-only `analyzer/full_mixture_product_placement_candidate_v1.mjs`.
- `569b5f02dbf91cd7d7d14f2d3640599bcb776564` — added deterministic known-truth P1–P12 verifier `analyzer/verify_full_mixture_product_placement_candidate_validation_v1.mjs`.
- `db247a0ea8343fcfd03a67ead4c987a9ff3be541` — added isolated read-only CPU-only workflow `.github/workflows/full-mixture-product-placement-candidate-validation-v1.yml`.

Checkpoint maintenance during implementation: `5c83554b040cb68f3fbce1933e456a54635ef3a7` and `73010ceb3fd8cf76c5759d99111875954af6baf3`.

No live runtime, canonical payload builder, Product UI, Preview/PDF implementation, render-contract implementation, or analyzer implementation file was modified by Phase 10.

## Workflow evidence

Workflow: `Full Mixture Product Placement Candidate Validation V1`

- run: `33829600963`;
- job: `100889565032`;
- tested head: `db247a0ea8343fcfd03a67ead4c987a9ff3be541`;
- conclusion: **SUCCESS**;
- P1–P12: **PASS**;
- safety-evidence gate: **PASS**.

The workflow used Node 22 for the verifier and GitHub Actions read-only repository permissions. No dependency install, runtime deployment, Modal invocation, GPU, external audio, or reference corpus was used.

## Synthetic known-truth result

The deterministic fixture contained **7 V143-runtime-safe canonical events** spanning multiple measure boundaries. Source events contained valid start/end/string/fret/MIDI but deliberately contained **no source `measure`/`step` placement**.

Canonical Product baseline:

- structured placement coverage = **0.0 / 0%**;
- baseline `renderEvents` = **0**;
- canonical payload remained immutable.

Experiment placement candidate:

- structured placement coverage = **1.0 / 100%**;
- exact known-truth matches = **7 / 7**;
- exact known-truth rate = **1.0 / 100%**;
- existing `validateV143RenderEvents` Product validator accepted every candidate row without compaction/drop.

This is a **synthetic placement result**, not a real-world transcription accuracy score.

## P1–P12 result

- **P1 — Canonical baseline immutability:** PASS. The canonical Product payload was built first, had zero structured render events, and was JSON-identical before/after candidate construction.
- **P2 — Known-truth placement effect:** PASS. Trusted complete straight-4/4 structure recovered the exact synthetic measure/step oracle across measure boundaries.
- **P3 — Product-contract compatibility:** PASS. The existing Product validator accepted all candidate rows unchanged.
- **P4 — Placement-only authority:** PASS. `eventIndex`, `stringIndex`, `fret`, and `midi` exactly matched canonical Product events; only `measure` and `step` were newly proposed.
- **P5 — Determinism:** PASS. Repeated identical inputs produced identical candidate output and identical metrics.
- **P6 — Existing authenticated renderEvents win:** PASS. A canonical payload with authenticated render events caused candidate construction to return no candidate; the baseline remained unchanged.
- **P7 — Provenance/safety rollback:** PASS. Non-trusted observation status and fusion/reference/carrier safety violations returned no candidate.
- **P8 — Structure-scope rollback:** PASS. Unresolved/Auto/triplet/non-4/4/non-zero-pickup/invalid-subdivision cases returned no candidate.
- **P9 — Event-integrity rollback:** PASS. Event count/index/MIDI/string/fret/measure consistency mismatches returned no candidate.
- **P10 — Explicit-prior precedence survives:** PASS. An explicit 60 BPM user prior remained authoritative over a 120 BPM observation and the synthetic placement candidate followed the already-resolved 60 BPM context exactly.
- **P11 — Live Product/PDF isolation:** PASS. No live route/Product/PDF/canonical payload/render-contract implementation consumed the experiment candidate.
- **P12 — Safety accounting:** PASS.

## Emitted safety evidence

- `referenceBlind = true`;
- `experimentOnly = true`;
- `placementOnlyAuthority = true`;
- `liveProductWiringChanged = false`;
- `pdfAuthorityChanged = false`;
- `canonicalAnalyzerOutputChanged = false`;
- `canonicalPayloadMutated = false`;
- `instrumentAuthorityInvariant = true`;
- `existingAuthenticatedRenderEventsOverridden = false`;
- `productContractValidatorAcceptedCandidate = true`;
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

## Candidate authority demonstrated

The experiment establishes a narrow Product-compatible candidate seam for one deliberately constrained case:

- analyzer response already proves the V143 runtime anti-leakage contract;
- canonical Product has valid event identity/string/fret/MIDI but no authenticated render placement;
- the admitted structure context is a trusted complete full-mixture observation;
- resolved geometry is straight 4/4 with pickup 0;
- the existing research shadow maps events one-to-one with canonical events;
- the candidate may supply only `measure` + `step`;
- existing authenticated Product placement always wins;
- any mismatch fails open to no candidate.

The candidate contract itself remains `experimentOnly=true`, `liveProductWiringAuthorized=false`, and `productionEligible=false`.

## Diff / isolation proof

Comparing freeze `697996069faa1a9167983357d1b94dada7c827fe` to tested head `db247a0ea8343fcfd03a67ead4c987a9ff3be541` shows five commits: two checkpoint updates, the experiment helper, the verifier, and the workflow. No `app/api/` file was changed in that comparison. The canonical Product/PDF/render/analyzer implementation remained untouched.

## Meaning

Phase 10 is the first positive **Product-contract compatibility** experiment for the admitted full-mixture structure signal. On the frozen deterministic known-truth fixture, the canonical structured placement baseline was 0%, while the isolated placement-only candidate produced 100% coverage and 7/7 exact known-truth placements, with no instrument-authority change and no Product-validator rejection.

This materially strengthens the case for a later narrowly gated live-candidate shadow or canary phase. It still does **not** establish real-audio transcription accuracy, does **not** authorize silently promoting inferred placement into live Product/PDF output, and does **not** authorize `main` or Production promotion.

## Next authority boundary

Any next phase should be separately frozen. The safest next step is not broad Product promotion; it is a **non-authoritative live-candidate observation/canary contract** that can compute and record candidate-vs-baseline eligibility in the server response while leaving canonical `renderEvents`, `analysisEngine`, Preview/PDF input, Product UI, and Production behavior unchanged. Real Product/PDF authority should remain a later boundary after sufficient evidence.
