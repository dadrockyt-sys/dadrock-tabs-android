# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Priority: **complete Rhythm end-to-end before Bass/Lead**.
Latest functional commit under test: `a98151b6477f06d446bc64d7381b2045fc4854ae` — `Verify final Rhythm renderer never reprojects V143 events`.

## Absolute rules

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, redeem tokens, send customer emails, weaken thresholds, or call Bass/Lead professional structured output early.

Rhythm target:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

The browser/PDF path may never invent musical placement. Preview/full must use the same frozen/authenticated event stream.
The professional human reference is scorer-only. Runtime/analyzer may never read/train/tune/select from it. Any later musical fix must be general/reference-free and require a fresh audio run before rescoring.

**Save this checkpoint frequently.**

## Completion order

1. Rhythm: score >=0.99, zero critical mismatches, PDF-event fidelity exactly 1.0 → `Final Rhythm Pipeline`.
2. Bass from finalized Rhythm; user supplies Bass holdout when scoring is ready → `Final Bass Pipeline`.
3. Lead from finalized Rhythm; user supplies Lead holdout when ready → `Final Lead Pipeline`.

Bass remains paused.

## Existing real-audio baseline

Approved fixture: `public/gomywayfullaitest.m4a`.
Existing structural proof: V143 reference-free Rhythm, 358 valid events, measures 1..113 / 112 unique measures, all 16 grid steps, 25 technique events, sustain 358/358, 129.19921875 BPM, 4/4, E Standard, prior full+preview PDFs.
Evidence: `debug/v143-contextual-prune/ai-tab-real-audio-canary.json` and `ai-tab-real-audio-pdf-validation.json`.
This is structural proof, not final professional musical accuracy.

## Clean professional holdout

Whole-song clean professional Rhythm source is not currently complete. Confirmed clean surviving screenshot: Library `1000116180.jpg`, Chorus measures 33–35, dark professional tab, labels `G6`, `A(tp2)`, `E`, `D`.
Do not use DadRock-generated/development screenshots/PDFs, old Chorus development labels, coarse fixtures, or contextual-prune development references as final holdout.
Inventory: `validation/rhythm_holdout/reference/reference-inventory.json`, currently `completeReferenceAvailable:false`, `finalScoringAuthorized:false`.
Do not open/recover more professional material until fresh reference-free freeze/PDF proof is locked.

## `app/ai-tab/page.js` is the PDF product source of truth

Preview → `/api/generate-tab-preview`; purchased/full → `/api/generate-tab-pdf`.
Both transport the exact structured musical fields including `renderEvents`; preview is locked/watermarked and both expect PDF.
Authenticated Rhythm path:
`page.js → PDF API → createJimmyPaigeProfessionalPdf → createAiTabPdf → createV143RhythmPdf`.
`createV143RhythmPdf` is the real polished renderer with DadRock logo/branding. Do not create a second PDF path.

## Current V143 anti-leakage / identity chain

Required runtime facts:
- `referenceFree:true`
- `professionalReferenceUsed:false`
- `referenceRuntimeInputUsed:false`
- `runtimeLabelsRequired:false`
- `v143RuntimeSafetyVerified:true`

Important hardening:
- `190b6a36...`: payload builder requires complete runtime safety contract.
- `b1273fa8...`: analyze API independently fails closed.
- `7bcee069...`: freeze preparation requires raw + structured safety.
- `098622e0...`: freeze snapshot/manifest records full safety.
- `301c38bd47ebee04d6f9435554ac1fde9d0010e1`: PDF-event fidelity requires safe freeze + renderer evidence before hash/event equality.
- `6a724bae...`: reference completeness refuses reference access until safety/PDF gate is verified.
- `e0c1cd7b5ac1571e9dcd401a81064972ef1b9c48`: final wrapper binds exact professional-reference bytes before/after scoring, closing reference TOCTOU risk.

No professional reference was opened by this hardening. Production remains untouched.

## Authenticated V143 PDF chain now validates instead of re-projecting at every product boundary

`d36839458fa129491d107c2203423fbeb2c240c6`:
Authenticated V143 Rhythm cannot silently fall back to legacy polished output when structured events are absent/invalid.

`a7a76e5b4d270f5b2e25f4869da4e19c5d86c660`:
`createJimmyPaigeProfessionalPdf` uses `validateV143RenderEvents(...)`, not a second projection. It cannot compact/drop malformed events and render surviving rows as successful V143.

`e7128a7f39a55366dde339a1a1a1c762eabdf5e4`:
The final polished renderer `createV143RhythmPdf` now also uses `validateV143RenderEvents(...)` rather than `projectV143RenderEvents(...)`. Thus the last PDF layer itself cannot silently compact/drop/coerce authenticated events. Invalid/empty streams fail closed.

`a98151b6477f06d446bc64d7381b2045fc4854ae`:
`verify_ai_tab_pdf_product_contract.mjs` schema v6 now requires exact validation and forbids re-projection both in `createJimmyPaigeProfessionalPdf` and in final `createV143RhythmPdf`, while still verifying page.js wiring, runtime safety, no legacy fallback, DadRock logo/branding, preview lock and structured renderer path.

This closes the last obvious PDF event-integrity re-projection edge. Stop adding speculative PDF hardening now; wait for CPU evidence unless a concrete failing diagnostic identifies another issue.

## CPU proof target — WAIT FOR REFRESH, DO NOT USE STALE FILE

Authoritative targets:
- `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json` → schema **7**, `passed:true`
- `debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json` → schema **6**, `passed:true`

The persisted static schema v4 `/tmp ... pdf-lib` error is stale. It was a test-environment package-resolution failure, not a polished renderer/logo defect. Current preflight runs repository-local `.preholdout-static`.

Current CPU gate checks runtime isolation, page.js preview/full contract, runtime negative cases, real-audio workflow contract, 400 synthetic events / 100 measures, polished preview/full PDFs, exact event/hash identity, PDF fidelity 1.0, holdout completeness/final wrapper, and exact V143 validation through the entire PDF chain.

Recent synthetic fixture repair: `126a2e5256742a9970bdc62a4db47122dc40e5d3` added renderer safety metadata required by the strengthened PDF-fidelity verifier. Wrong-PDF fixture carries valid safety metadata so it fails for event mismatch, not metadata absence.

## Fresh real-audio pre-holdout workflow

`.github/workflows/rhythm-professional-preholdout-real-audio.yml` is coded but `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` is not yet established green.

**Do not intentionally trigger duplicate GPU work before CPU schema v7 + self-test v6 are green.**
After CPU turns green, strengthen that workflow's compact report with explicit runtime-label absence, freeze/PDF runtime safety, renderer reference-sealed state, live-endpoint-unmodified state, and promotion unauthorized state. Editing the workflow should intentionally cause exactly one fresh authoritative GPU run.

## Immediate next steps

1. Poll refreshed CPU evidence; ignore stale schema v4/v3 evidence.
2. Require static v7 green + consolidated self-test v6 green for `a98151b...` or a descendant containing it.
3. If red, use current `failedStage` + sanitized `failureLogTail`; fix only the concrete issue and do not weaken product/scoring contracts.
4. Save this file after the result.
5. Once CPU green, make the one intentional real-audio workflow hardening edit and allow exactly one GPU run.
6. Require fresh approved-audio hash, full runtime safety, positive frozen event count, polished preview/full PDF, exact event/hash equality, fidelity 1.0, reference sealed, Production unchanged.
7. Only then recover/re-supply the clean complete Rhythm professional source if needed.
8. Run completeness → isolated scorer → final wrapper. If <0.99 or critical mismatches >0, improve only general/reference-free logic and rerun audio from scratch.
9. Only after pass create `Final Rhythm Pipeline`.

## Bass

Paused until Rhythm is complete. Existing Bass diagnostics remain available but are not final professional ground truth.
