# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — LIVE PRIORITY: complete Rhythm end-to-end before Bass/Lead
Branch: `v143-contextual-prune-lobo`

## Immutable safety / product contract

Resume **only** on `v143-contextual-prune-lobo`. Never modify `main`, merge this branch, deploy/alter live V143 Modal, promote Production, make payments, redeem customer tokens, send customer emails, weaken quality thresholds, or relabel legacy Bass/Lead as professional structured output without separate authorization.

Required product path:
`user-uploaded audio → Rhythm selection → reference-free analysis → authenticated structured events → professional preview/full PDF → isolated post-freeze professional-human scoring`

Preview/full PDF must derive from the exact frozen event stream. Renderer/browser may not invent musical placement.

Professional human reference is scorer-only holdout material. Analyzer may never read/train/tune/select/infer from it. Every improvement after scoring must be general/reference-free and requires a fresh audio run from scratch before rescoring.

Save this checkpoint frequently.

## Required completion order / finalized folders

1. Rhythm: near-100 professional human agreement, zero critical mismatches, exact PDF-event fidelity 1.0 → package **`Final Rhythm Pipeline`**.
2. Bass: mold from finalized Rhythm architecture; user supplies Bass professional reference when scoring is ready → package **`Final Bass Pipeline`**.
3. Lead: mold from finalized Rhythm architecture; user supplies Lead professional reference when scoring is ready → package **`Final Lead Pipeline`**.

Bass remains paused until Rhythm is truly complete.

## Rhythm real-audio structural baseline — GREEN, musical holdout score still OPEN

Approved audio fixture: `public/gomywayfullaitest.m4a`.

Existing real-audio proof:
- engine `v143-reference-free-rhythm`, output version `v143-reference-free-rhythm-output-v2`
- reference-free; deterministic separator seed 143; professional reference not used
- 358 valid render events
- measures 1..113, 112 unique measures, all 16 grid steps represented
- 25 technique events
- sustain coverage 358/358
- tempo 129.19921875, 4/4, E Standard
- prior exact-response preview/full PDFs rendered from those 358 events

Evidence:
- `debug/v143-contextual-prune/ai-tab-real-audio-canary.json`
- `debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`
- `.github/workflows/v143-ai-tab-real-audio-canary.yml`

Structural consistency is not final musical correctness.

## Human professional Rhythm reference — CLEAN HOLDOUT NOT YET COMPLETE

Accessible clean material currently confirmed:
- Library `1000116180.jpg`: dark-theme professional human tablature, Chorus measures 33–35, labels `G6`, `A(tp2)`, `E`, `D`, exact fret stacks/rhythm/lyrics.

Explicitly **not** clean final holdout:
- DadRock/Jimmy generated/development images `1000116132.jpg`, `1000116183.jpg`, `1000116184.jpg`
- emailed DadRock generated Rhythm PDFs
- historical coarse fixtures/benchmarks
- old Chorus 33–35 development artifacts that explicitly used professional reference for scoring/development
- contextual-prune development material where `developmentReferenceUsed:true`

Formal inventory:
- `7ee4aedae7f506eb7c7e2df7eb29403fd64e42dc` — `validation/rhythm_holdout/reference/reference-inventory.json`
- `completeReferenceAvailable:false`
- `finalScoringAuthorized:false`

Some earlier uploads may no longer be loadable. If the complete clean professional source cannot be recovered, it will need to be re-uploaded when final scoring is ready. Do not block reference-free pipeline work on that yet.

## Holdout architecture — STRICT SYNTHETIC GATE GREEN

Core files:
- `validation/rhythm_holdout/canonical.py`
- `validation/rhythm_holdout/freeze_rhythm_analysis.py`
- `validation/rhythm_holdout/verify_pdf_event_fidelity.py`
- `validation/rhythm_holdout/verify_runtime_isolation.py`
- `validation/rhythm_holdout/verify_reference_completeness.py`
- `validation/rhythm_holdout/score_rhythm_holdout.py`
- `validation/rhythm_holdout/run_final_holdout_gate.py`
- `validation/rhythm_holdout/reference/reference.schema.json`
- `validation/rhythm_holdout/reference/reference-inventory.json`
- `validation/rhythm_holdout/reference/.gitignore`

Previously observed strict synthetic evidence was green: runtime isolation, complete source/reference, contiguous coverage, final wrapper, PDF event fidelity 1.0, critical mismatches 0, partial-reference hard failure, real professional reference unopened, Production unchanged.

## Exact authenticated event → PDF identity — DIRECT PROOF GREEN

Bug fixed: a second projection could previously compact/reset `eventIndex`, risking broken legato connector identities despite equal event counts.

Key commits:
- `2f7e35f26905b082ef9e7571b539794838def96f` — projection idempotent and authenticated event IDs preserved.
- `5892a8b8a6c976d50e94438fb8149a02a4e5e39a` — `createAiTabPdf` fail-closes on validated authenticated Rhythm events.
- `23909503afa0de7337d43aa419779627075fbbfe` — direct proof `debug/v143-contextual-prune/rhythm-render-contract-idempotence.json`.

Verified gapped IDs `[0,2,4]`, legato source/target identity, exact second projection equality and exact validation equality. Production unchanged.

## AI-tab polished preview / purchased PDF product contract — CONFIRMED FROM `app/ai-tab/page.js`

`app/ai-tab/page.js` is the source of truth for the preview and purchased PDF product contract.

Preview:
- `requestPreviewPdf(...)` POSTs `/api/generate-tab-preview`
- sends song, artist, transcriptionType, generatedTab, tuning, tempo, timeSignature, keySignature, analysisEngine, techniques, **renderEvents**, measureGrid, confidence, difficulty
- sends `previewSystems:4`, watermark `DADROCK TABS PREVIEW`, `locked:true`
- expects `application/pdf`

Purchased/unlocked:
- `handleDownloadPdf(...)` POSTs `/api/generate-tab-pdf`
- sends same structured musical fields including exact analyzer **renderEvents**, plus unlock/payment/token/customer-email fields
- expects `application/pdf`

For authenticated V143 Rhythm, actual PDF path is:
`page.js → API route → createJimmyPaigeProfessionalPdf → createAiTabPdf → createV143RhythmPdf`.

`createV143RhythmPdf` is the actual underlying polished Rhythm renderer, including DadRock logo/branding. Do not invent a second PDF contract.

## CRITICAL V143 runtime anti-leakage hardening — FIXED IN PRODUCT PATH, CPU PROOF ADDED

A product-path audit found a real safety gap: before this hardening, `app/api/analyze-audio-tab/route.js` and `buildJimmyPaigeAnalysisPayload(...)` effectively treated `liveV143.referenceFree === true` as sufficient identity proof. That was weaker than the immutable contract because an unsafe response could theoretically claim `referenceFree:true` while also reporting professional-reference use, reference runtime input, or required runtime labels.

Hardening commits:
- `190b6a36c349c91b97b2f3a1b66781851927f16d` — `lib/jimmyPaigeAnalysisPayload.js` now requires the complete explicit runtime safety contract before creating structured `renderEvents`:
  - `referenceFree === true`
  - `professionalReferenceUsed === false`
  - `referenceRuntimeInputUsed === false`
  - `runtimeLabelsRequired === false`
  Unsafe or missing flags hard-fail for V143 Rhythm. Payload contract bumped to v3 and records `v143RuntimeSafetyVerified`.
- `06a547c5148434553032455253a3aec0d5095b83` — new `verify_v143_runtime_safety_contract.mjs`; proves a safe synthetic V143 response is accepted and unsafe/missing flag variants are rejected. It never opens a professional reference.
- `b1273fa8eb925f46471084205e95885f98fab96a` — defense-in-depth at `app/api/analyze-audio-tab/route.js`; the API route independently requires all four flags before the response enters `buildJimmyPaigeAnalysisPayload`, returning 502 when the V143 runtime safety contract fails.
- `b486243169d5445763b00f031b28df50cd2d9e3d` — CPU preflight upgraded to schemaVersion 7 and now runs the runtime anti-leakage negative test before synthetic freeze/PDF proof.
- `3191153c0bb84c53d85c17e9bd18c026728c701d` — AI-tab product-contract verifier upgraded to schemaVersion 3 and now checks both route-layer and payload-layer anti-leakage gates in addition to the actual PDF wiring/branding.

No threshold, musical inference, renderer, payment, email, live Modal, or Production behavior was loosened or promoted. These changes are fail-closed safety hardening on the isolated branch.

A bot commit `33ace6ee89b377be2a98d05b7d6c34e10b1b9a6e` was observed after the payload hardening; it only refreshed `debug/v143-contextual-prune/next-preview-route-smoke.json` to record a staged local branch-gate start for source commit `190b6a...`. It explicitly reported local simulation / no actual Vercel preview deployment in that evidence file change.

## Fresh real-audio pre-holdout freeze/PDF gate — CODED, authoritative result still pending

Committed machinery:
- `32b538fc2b7b1a23a3f47aa66bbaa6c528d0faa8` — raw product response → structured freeze input after explicit no-reference checks.
- `a185760b134e38b548711d928b24e559530f9b40` — preview/full professional PDFs from frozen events only.
- `16bc56a5885802c194a77864553681b7634b7112` — freeze records source-audio SHA-256/bytes.
- `8066dd24494ba7c550c3c0481d4932cf6e45470c` — real-audio pre-holdout workflow.
- `b63f6d33d7b8a8a73d752e4f97e47aeda256260d` — static verifier for future real-audio workflow contract.
- `ad740dd51d8bbb9793988fa19b52921997b054c4` — CPU preflight requires that GPU-workflow contract before GPU use.

Required proof: fresh audio, all anti-leakage flags safe, frozen source/event hashes, full+preview PDF, exact PDF/frozen event hash equality, fidelity 1.0, human reference unopened.

`debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` is still not established green. Do not launch duplicate expensive GPU work until CPU glue is green.

## CPU polished-PDF preflight — OLD FAILURE EXPLAINED; POST-FIX SCHEMA 7 EVIDENCE PENDING

Old persisted failure was test-environment-only:
```text
Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'pdf-lib'
imported from /tmp/rhythm-preholdout-static/esm/render-frozen.mjs
```

The repository has locked `pdf-lib`; the old standalone test lived under `/tmp`, outside repository Node package resolution. This is not evidence of a logo or polished-renderer defect.

Fixes:
- reusable runner is repository-local under `.preholdout-static`
- consolidated self-test also uses `$GITHUB_WORKSPACE/.preholdout-static`
- CPU preflight now gates the real `app/ai-tab/page.js` PDF contract, polished branding/logo path, future real-audio workflow safety, and V143 runtime anti-leakage behavior before accepting PDF/hash proof

Current authoritative post-hardening CPU target is schemaVersion 7. The old schemaVersion 4 `/tmp` failure JSON is stale and must not be treated as current evidence.

## Immediate next actions

1. Observe refreshed `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json`; require schemaVersion 7 `passed:true`, runtime anti-leakage contract true, page.js polished PDF contract true, future real-audio workflow contract true, 400 events/100 measures, full+preview PDFs, hash equality, fidelity 1.0.
2. Observe refreshed consolidated holdout self-test; require all synthetic final-wrapper/static/product safety gates green.
3. If CPU remains red, use persisted `failedStage` + `failureLogTail`; do not alter product renderer unless evidence proves a real renderer defect.
4. Save checkpoint after each meaningful result.
5. Only after CPU glue is green, execute/diagnose exactly one fresh real-audio pre-holdout GPU run if necessary.
6. Once fresh reference-free freeze/PDF evidence is locked, recover/re-supply a **clean complete** professional Rhythm source if necessary.
7. Run final sequence: freeze/PDF proof → reference completeness verifier → isolated professional scorer → `run_final_holdout_gate.py`.
8. If score <0.99 or any critical mismatch, change only general/reference-free algorithms; rerun audio from scratch and rescore.
9. Only after real gate passes create **`Final Rhythm Pipeline`**.

## Bass — GREEN DIAGNOSTICS, PAUSED

No new Bass capability work before Rhythm completion.
- separation/pitch `32611529763` passed
- note/timing/playability `32611818648` passed
- conservative techniques `32612166508` passed
- harmonic `32613012696` passed safe abstention; harmonic remains unproven
- structured integration `32613450912` at `8a668f9a4af966b8abf14034b975a36d6ed7d587` completed success
