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

Important commits:
- `10ae14101cff959a7b90822b33c44df229ad0b61` — complete-source reference schema requirements.
- `4169e44522815539cdc4a299730a9ca8e32d53da` — strict reference completeness verifier; validates freeze/PDF safety before opening reference.
- `669f4445d6b98391754de25276cd6cb1ed54b7cf` — real holdout/event transcription ignored from git.
- `4f9c0d83686f56853a5b6ba2edb1035ed323a542` — mandatory `run_final_holdout_gate.py` binds completeness + scorer + frozen/PDF hashes.
- `10bc229a424dda3ad56a680fc7000d7286687a2f` — self-test exercises mandatory final wrapper.
- latest previously observed strict synthetic evidence was green: runtime isolation, complete source/reference, contiguous coverage, final wrapper, PDF event fidelity 1.0, critical mismatches 0, partial-reference hard failure, real professional reference unopened, Production unchanged.

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

Routes:
- `app/api/generate-tab-preview/route.js`
- `app/api/generate-tab-pdf/route.js`
Both use `createJimmyPaigeProfessionalPdf(...)` when professional PDF feature is enabled.

For authenticated V143 Rhythm (`analysisEngine === 'v143-reference-free-rhythm'` + render events), actual path is:
`page.js → API route → createJimmyPaigeProfessionalPdf → createAiTabPdf → createV143RhythmPdf`.

Therefore `createV143RhythmPdf` is the underlying polished Rhythm renderer used by the actual `/ai-tab` preview/purchased PDF product, including DadRock logo/branding. Do not invent a second PDF contract.

Static product-path protection:
- `a45f71296bf0ffb2284f5adeea462f2ab94114ac` — original `verify_ai_tab_pdf_product_contract.mjs` gate.
- `280c86fcf40e57a9d365b77321e1a1e3d37609c7` — strengthened contract verifier now also proves both UI flows expect PDFs, both API routes use the professional feature gate, authenticated V143 Rhythm routes to the structured renderer, and `createV143RhythmPdf` still carries the actual DadRock logo path, product branding, preview watermark/lock, and branded footer.
- `3cd507e4898e44840d1a32a550f6bc947dc2761f` — reusable static preflight upgraded to schemaVersion 5 and explicitly gates on those polished product-contract facts before accepting PDF render/hash proof.

These are validation-only changes; production renderer behavior and branding were not altered.

## Fresh real-audio pre-holdout freeze/PDF gate — CODED, authoritative result still pending

Committed machinery:
- `32b538fc2b7b1a23a3f47aa66bbaa6c528d0faa8` — raw product response → structured freeze input after explicit no-reference checks.
- `a185760b134e38b548711d928b24e559530f9b40` — preview/full professional PDFs from frozen events only.
- `16bc56a5885802c194a77864553681b7634b7112` — freeze records source-audio SHA-256/bytes.
- `8066dd24494ba7c550c3c0481d4932cf6e45470c` — real-audio pre-holdout workflow.

Required proof: fresh audio, referenceFree true, professionalReferenceUsed false, referenceRuntimeInputUsed false, frozen source/event hashes, full+preview PDF, exact PDF/frozen event hash equality, fidelity 1.0, human reference unopened.

`debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` is still not established green. Do not launch duplicate expensive GPU work until CPU glue is green.

## CPU polished-PDF preflight — EXACT ROOT CAUSE FOUND AND TEST GLUE FIXED; REFRESH RUNS IN FLIGHT

The previous failure was **not evidence of a logo or polished renderer defect**.

Latest persisted old failure diagnostic from source commit `b65cf9dd016edb3fce54d2cd36dd73d9a593f637` explicitly showed:
```text
failedStage: professional-pdf-render
Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'pdf-lib'
imported from /tmp/rhythm-preholdout-static/esm/render-frozen.mjs
```

This proves Node was executing a standalone ESM copy under `/tmp`, outside the repository package-resolution tree. The repository has `pdf-lib` as a locked dependency, and the actual product renderer runs inside the repository/Next.js environment.

Fixes now in branch:
- reusable runner default is repository-local: `$ROOT/.preholdout-static`
- `1906bd89b35abdc2ea121f7d6605acc2f24eee04` — consolidated self-test no longer overrides the runner with `/tmp`; it uses `$GITHUB_WORKSPACE/.preholdout-static`
- `e5bade98915c6b9b4af75ba55f8c214ee1109b4e` — consolidated path uses the same authoritative AI-tab PDF preflight runner
- `280c86fcf40e57a9d365b77321e1a1e3d37609c7` / `3cd507e4898e44840d1a32a550f6bc947dc2761f` — polished product contract strengthened and CPU workflows retriggered without touching the GPU real-audio workflow

Current branch head before this checkpoint: `3cd507e4898e44840d1a32a550f6bc947dc2761f`.

Await refreshed bot evidence. Do not treat the old `/tmp` failure JSON as current post-fix evidence. If a refreshed run fails, use its persisted `failedStage` and sanitized `failureLogTail` rather than guessing.

No live Modal, Production, payments, token redemption, email, or customer flow was invoked.

## Immediate next actions

1. Observe refreshed `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json`; require schemaVersion 5 `passed:true`, page.js product contract true, polished branding/logo contract true, 400 events/100 measures, full+preview PDFs, hash equality, fidelity 1.0.
2. Observe refreshed `debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json`; require consolidated `passed:true` with product-path/static/final-wrapper gates green.
3. If any CPU gate remains red, use the new persisted `failureLogTail`; do not alter product rendering unless evidence proves a real product defect.
4. Save this checkpoint after each meaningful result.
5. Only after CPU glue is green, diagnose/retrigger exactly one fresh real-audio pre-holdout GPU run if needed.
6. After fresh reference-free freeze/PDF evidence is safely locked, recover/re-supply a **clean complete** professional Rhythm source if necessary.
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
