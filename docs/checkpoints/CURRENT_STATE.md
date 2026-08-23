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
- latest observed bot evidence `debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json` reached schemaVersion 3 and passed:
  - runtime isolation true
  - reference completeness true
  - complete source true
  - contiguous coverage true
  - reference opened only after freeze validation true
  - final wrapper passed true
  - PDF event fidelity 1.0
  - critical mismatches 0
  - partial-reference wrapper hard-failure true
  - real professional reference opened false
  - Production unchanged

A later consolidated self-test workflow was committed at `1d99690759a4d572d389bd3e7599cebd76d84b1b`; its consolidated static-PDF portion is still under diagnosis below.

## Exact authenticated event → PDF identity — DIRECT PROOF GREEN

Bug fixed: a second projection could previously compact/reset `eventIndex`, risking broken legato connector identities despite equal event counts.

Key commits:
- `2f7e35f26905b082ef9e7571b539794838def96f` — projection idempotent and authenticated event IDs preserved.
- `5892a8b8a6c976d50e94438fb8149a02a4e5e39a` — `createAiTabPdf` fail-closes on validated authenticated Rhythm events.
- `23909503afa0de7337d43aa419779627075fbbfe` — direct proof `debug/v143-contextual-prune/rhythm-render-contract-idempotence.json`.

Verified gapped IDs `[0,2,4]`, legato source/target identity, exact second projection equality and exact validation equality. Production unchanged.

## AI-tab polished preview / purchased PDF product contract — CONFIRMED FROM `app/ai-tab/page.js`

User pointed out that the authoritative preview/full-PDF payload and route information is already in `app/ai-tab/page.js`. This is now the source of truth for the PDF validation path.

Preview flow in `page.js`:
- `requestPreviewPdf(...)` POSTs to `/api/generate-tab-preview`
- sends `song`, `artist`, `transcriptionType`, `generatedTab`, `tuning`, `tempo`, `timeSignature`, `keySignature`, `analysisEngine`, `techniques`, **`renderEvents`**, `measureGrid`, `confidence`, `difficulty`
- sends `previewSystems: 4`, watermark `DADROCK TABS PREVIEW`, and `locked:true`
- expects `application/pdf`

Purchased/unlocked flow in `page.js`:
- `handleDownloadPdf(...)` POSTs to `/api/generate-tab-pdf`
- sends the same structured musical fields, including the exact analyzer **`renderEvents`**, plus unlock/payment/token and customer-email fields
- expects `application/pdf`

Route verification:
- `app/api/generate-tab-preview/route.js` and `app/api/generate-tab-pdf/route.js` both use `createJimmyPaigeProfessionalPdf(...)` when the professional PDF feature is enabled
- for authenticated V143 Rhythm (`analysisEngine === 'v143-reference-free-rhythm'` with render events), `createJimmyPaigeProfessionalPdf` routes through `createAiTabPdf` → `createV143RhythmPdf`
- therefore the structured Rhythm renderer currently under test **is** the final underlying polished renderer for the actual `/ai-tab` preview and purchased PDF path, including the DadRock logo/branding

Do not invent a second PDF product contract. Tests should mirror the fields/routes from `app/ai-tab/page.js` and the two API routes above.

New static contract proof:
- `a45f71296bf0ffb2284f5adeea462f2ab94114ac` — `validation/rhythm_holdout/verify_ai_tab_pdf_product_contract.mjs` reads the real `page.js`, both PDF API routes, `createJimmyPaigeProfessionalPdf.js`, and `createAiTabPdf.js`; it fails if the endpoints, shared structured musical fields, `renderEvents`, preview lock/watermark settings, or V143 professional-renderer routing disappear.
- `fa67cf7b39a026684a956698cf42ec5422b232dd` — static preflight workflow now runs this product-contract verifier before the PDF renderer test.

## Fresh real-audio pre-holdout freeze/PDF gate — CODED, authoritative result still pending

Committed machinery:
- `32b538fc2b7b1a23a3f47aa66bbaa6c528d0faa8` — raw product response → structured freeze input only after explicit no-reference safety checks.
- `a185760b134e38b548711d928b24e559530f9b40` — render preview/full professional PDFs from frozen events only.
- `16bc56a5885802c194a77864553681b7634b7112` — freeze records source-audio SHA-256/bytes.
- `8066dd24494ba7c550c3c0481d4932cf6e45470c` — `.github/workflows/rhythm-professional-preholdout-real-audio.yml`.

Required proof from this gate:
1. fresh approved user-upload-equivalent audio analysis
2. `referenceFree:true`
3. `professionalReferenceUsed:false`
4. `referenceRuntimeInputUsed:false`
5. exact frozen event hash
6. professional preview/full PDF generated from frozen events
7. PDF event hash exactly equals frozen hash; fidelity 1.0
8. human reference remains sealed/unopened

Expected compact evidence `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` is still absent. Do not call this gate green yet and do not launch duplicate expensive GPU work until CPU glue is green.

## CPU static pre-holdout glue — FAILURE LOCALIZED; ENVIRONMENT FIX + DIAGNOSTICS COMMITTED

Purpose: exercise exact raw product-response → structured payload → freeze → actual polished V143 Rhythm renderer → PDF-event-fidelity glue without GPU or professional reference.

Files/commits:
- `57a9955a6f4a2e799d3df92216409a81055712eb` — reusable `validation/rhythm_holdout/run_static_preholdout_preflight.sh`.
- `a1dac791e7266c04f09fe3efa267e6a978d1e667` — simplified CPU workflow using reusable runner.
- `88b8260791dc86c292e02a0fa93bb8447897b0aa` — failure diagnostics persist to branch.
- `eea01a28d674fe130db38a086eff054e0e007fd0` — aligned static workflow with the `/ai-tab` PDF product files and moved standalone ESM work from `/tmp` into `$GITHUB_WORKSPACE/.preholdout-static` so Node can resolve the repository's installed `pdf-lib` dependency exactly as the product renderer does.
- `eb57a53f9a54294f69fc5174a89ef549da4b6039` — static runner now persists a sanitized last-24-lines diagnostic tail from the failing stage into `rhythm-preholdout-static-preflight.json`; no secrets are expected in this CPU test, and token/secret-like assignments are redacted defensively.
- product-contract verifier commits `a45f712...` / `fa67cf7...` ensure the CPU proof is explicitly tied to the real `/ai-tab` preview and purchased-PDF wiring before rendering.

Latest persisted diagnostic before those fixes:
`debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json`

Observed:
```text
schemaVersion: 2
passed: false
failedStage: professional-pdf-render
exitStatus: 1
usesSyntheticAudioResponseOnly: true
realProfessionalReferenceOpened: false
productionModified: false
```

Important diagnosis: the previous CPU test copied `createV143RhythmPdf.mjs` under `/tmp/.../esm`. Node package resolution starts from the importing module's location, so `pdf-lib` installed in the repository `node_modules` could be unreachable before the renderer itself ran. The updated workflow now keeps those standalone modules under the repository workspace. This is a test-environment correction only; no production renderer behavior, branding, or thresholds were changed.

Await the new static workflow evidence. If it becomes green, this confirms the earlier PDF-stage failure was test glue rather than a polished-renderer defect. If it still fails, the next committed schemaVersion 3 diagnostic should contain the exact sanitized renderer-log tail needed to fix the concrete exception.

## Immediate next actions

1. Observe the post-`fa67cf7...` static preflight result: first require the `app/ai-tab/page.js` product-contract gate, then professional preview/full PDFs and exact PDF-event fidelity 1.0.
2. If still red, read `failureLogTail` from the schemaVersion 3 diagnostic and fix only the concrete failing condition.
3. Save this checkpoint after each meaningful change.
4. Only after CPU glue is green, diagnose/retrigger exactly one fresh real-audio pre-holdout GPU run if needed.
5. Recover/re-supply a **clean complete** professional Rhythm source only after the fresh reference-free freeze/PDF evidence is safely locked.
6. Run: freeze/PDF proof → reference completeness verifier → isolated professional scorer → `run_final_holdout_gate.py`.
7. If score <0.99 or any critical mismatch, change only general/reference-free algorithms; rerun audio from scratch and rescore.
8. Only after the real gate passes create **`Final Rhythm Pipeline`**.

## Bass — GREEN DIAGNOSTICS, PAUSED

No new Bass capability work before Rhythm completion.
- separation/pitch `32611529763` passed
- note/timing/playability `32611818648` passed
- conservative techniques `32612166508` passed
- harmonic `32613012696` passed safe abstention; harmonic remains unproven
- structured integration `32613450912` at `8a668f9a4af966b8abf14034b975a36d6ed7d587` completed success
