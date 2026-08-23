# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — PRIORITY: finish Rhythm end-to-end before Bass/Lead
Branch: `v143-contextual-prune-lobo`
Latest observed working head before this checkpoint: `e0c1cd7b5ac1571e9dcd401a81064972ef1b9c48` — `Bind immutable professional reference hash across final score`.

## Non-negotiable safety / product contract

Work **only** on `v143-contextual-prune-lobo`.
Never modify/merge `main`, deploy or alter live V143 Modal, promote Production, make payments, redeem customer tokens, send customer emails, weaken thresholds, or relabel legacy Bass/Lead as professional structured output without explicit authorization.

Required Rhythm path:
`user-uploaded audio → Rhythm selection → reference-free analysis → authenticated structured events → professional preview/full PDF → isolated post-freeze professional-human scoring`

Preview and full PDF must derive from the exact same authenticated/frozen event stream. Browser/PDF code may not invent missing musical placement.

Professional human reference is scorer-only holdout. Analyzer/runtime may never read, train, tune, select, infer, or repair from it. Any musical improvement after holdout diagnosis must be general/reference-free and followed by a fresh audio run from scratch before rescoring.

**Save this file frequently while working.**

## Completion order

1. Rhythm: professional holdout >= 0.99, zero critical mismatches, PDF-event fidelity exactly 1.0 → package `Final Rhythm Pipeline`.
2. Bass: derive from finalized Rhythm, then user supplies Bass professional holdout → package `Final Bass Pipeline`.
3. Lead: derive from finalized Rhythm, then user supplies Lead professional holdout → package `Final Lead Pipeline`.

Bass remains paused until Rhythm is truly complete.

## Real-audio structural baseline

Approved fixture: `public/gomywayfullaitest.m4a`.
Prior real-audio proof is structurally green:
- engine `v143-reference-free-rhythm`
- output `v143-reference-free-rhythm-output-v2`
- 358 valid render events
- measures 1..113, 112 unique measures
- all 16 grid steps represented
- 25 technique events
- sustain coverage 358/358
- tempo 129.19921875 BPM, 4/4, E Standard
- prior exact-response preview/full PDFs rendered

Evidence:
- `debug/v143-contextual-prune/ai-tab-real-audio-canary.json`
- `debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`

This proves structural/render behavior, **not** professional human musical accuracy.

## Professional Rhythm reference status

Clean whole-song holdout is **not yet complete**.
Confirmed clean surviving material: Library `1000116180.jpg`, dark-theme professional human tab, Chorus measures 33–35, labels `G6`, `A(tp2)`, `E`, `D`.

Do **not** use as final clean holdout:
- `1000116132.jpg`, `1000116183.jpg`, `1000116184.jpg`
- emailed DadRock-generated Rhythm PDFs
- `analyzer/fixtures/gomyway2_full_tab_reference.json`
- `analyzer/fixtures/gomyway_full_chord_sustain_reference.json`
- contextual-prune development references
- old Chorus 33–35 development artifacts that used the professional reference during development/scoring

Formal inventory: `validation/rhythm_holdout/reference/reference-inventory.json` with `completeReferenceAvailable:false`, `finalScoringAuthorized:false`.
Do not open/recover additional professional material until the fresh reference-free freeze/PDF proof is locked. If complete clean source cannot be recovered afterward, user may need to re-upload it.

## AI-tab preview / purchased PDF source of truth

User confirmed `app/ai-tab/page.js` is authoritative.

Preview:
- `/api/generate-tab-preview`
- carries song, artist, transcriptionType, generatedTab, tuning, tempo, timeSignature, keySignature, analysisEngine, techniques, **renderEvents**, measureGrid, confidence, difficulty
- `previewSystems:4`, watermark `DADROCK TABS PREVIEW`, locked preview
- expects `application/pdf`

Purchased/full:
- `/api/generate-tab-pdf`
- same structured musical fields including exact **renderEvents** plus unlock/token/payment/customer metadata
- expects `application/pdf`

Authenticated V143 Rhythm PDF path:
`app/ai-tab/page.js → PDF API route → createJimmyPaigeProfessionalPdf → createAiTabPdf → createV143RhythmPdf`

`createV143RhythmPdf` is the real polished Rhythm renderer with DadRock branding/logo. Do not create a competing PDF path.

## Exact event identity

Direct proof remains green:
- `2f7e35f...` projection idempotent and eventIndex preserved
- `5892a8b...` `createAiTabPdf` validates authenticated events
- `23909503...` direct idempotence evidence

Gapped IDs `[0,2,4]` and legato source/target relationships are preserved exactly.

## Current anti-leakage chain

V143 structured Rhythm now requires the complete runtime safety contract:
- `referenceFree === true`
- `professionalReferenceUsed === false`
- `referenceRuntimeInputUsed === false`
- `runtimeLabelsRequired === false`
- derived `v143RuntimeSafetyVerified === true`

Important commits:
- `190b6a36...` payload builder requires all runtime safety flags; payload contract v3.
- `06a547c5...` negative runtime-safety tester rejects unsafe/missing flags.
- `b1273fa8...` analyze API route independently fails closed with 502.
- `7bcee069...` freeze-input preparation requires raw + structured safety contract.
- `098622e0...` freeze snapshot/manifest schema v2 records full safety state.
- `301c38bd47ebee04d6f9435554ac1fde9d0010e1` PDF-event fidelity schema v2 requires safe freeze + renderer evidence before exact event/hash proof.
- `6a724bae...` reference completeness refuses reference access without the verified safety state and PDF fidelity.
- `e0c1cd7b5ac1571e9dcd401a81064972ef1b9c48` final wrapper hashes the exact professional-reference bytes after completeness authorization and verifies the same bytes are still present before/after scoring, closing a reference TOCTOU gap.

No holdout reference was opened by these changes. No live/Production action was taken.

## V143 PDF fail-closed hardening just added

Commit `d36839458fa129491d107c2203423fbeb2c240c6`:
`lib/createJimmyPaigeProfessionalPdf.js` now refuses to silently fall back to a legacy polished renderer when the request explicitly identifies itself as authenticated `v143-reference-free-rhythm` but has no valid structured render events. It throws instead.

Commit `75be9283dff79ad1ce587574f9575eda32e7352a`:
`verify_ai_tab_pdf_product_contract.mjs` schema v4 now proves the above guard exists and reports `authenticatedV143RhythmRejectsLegacyPdfFallback`.

This protects product identity: a broken V143 event stream cannot be displayed as a successful legacy-looking V143 PDF.

## Holdout harness

Core scorer-only tools:
- `validation/rhythm_holdout/canonical.py`
- `freeze_rhythm_analysis.py`
- `verify_pdf_event_fidelity.py`
- `verify_runtime_isolation.py`
- `verify_reference_completeness.py`
- `score_rhythm_holdout.py`
- `run_final_holdout_gate.py`
- `reference/reference.schema.json`

Default professional threshold remains `0.99`; critical mismatch count must be 0; PDF-event fidelity must equal 1.0.

## CPU polished-PDF preflight — refreshed proof still pending

Current authoritative targets:
- `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json` → schemaVersion **7**, `passed:true`
- `debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json` → schemaVersion **6**, `passed:true`

The currently persisted static schemaVersion 4 failure is stale. It was caused by standalone modules living in `/tmp` and therefore failing Node resolution of installed `pdf-lib`; it is **not** evidence that the logo/polished product renderer is broken.

Current runner is repository-local `.preholdout-static` and checks:
- runtime isolation
- `app/ai-tab/page.js` preview/full contract
- V143 anti-leakage negative cases
- real-audio workflow contract
- 400 synthetic events / 100 measures
- polished full + preview PDF render
- exact renderer projection
- PDF headers/page output
- exact frozen/PDF hash equality
- PDF-event fidelity 1.0

After `301c38...`, the synthetic self-test PDF fixture had to carry the new renderer safety metadata. Commit `126a2e5256742a9970bdc62a4db47122dc40e5d3` fixed the positive fixture and ensures the wrong-PDF negative fixture fails for event mismatch rather than missing metadata.

A staged local Next gate bot commit has appeared during these changes, but its evidence says no actual Vercel deployment and no Production modification. It is not the consolidated CPU proof.

## Fresh real-audio pre-holdout gate — do not duplicate GPU work

Workflow: `.github/workflows/rhythm-professional-preholdout-real-audio.yml`.
It is coded to run approved real audio through the product canary, freeze exact events before reference access, render full/preview PDFs, and prove exact event identity.

`debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` is not yet established green.

**Do not intentionally trigger another expensive GPU run until CPU schema v7 + self-test schema v6 are green.**

Once CPU proof is green, strengthen the real-audio compact proof to explicitly include runtime-label absence, freeze/PDF runtime safety, renderer reference-sealed state, live-endpoint-unmodified state, and promotion unauthorized state. Editing that workflow will intentionally trigger exactly one fresh GPU run; use that single run as the authoritative fresh pre-holdout proof.

## Immediate next actions

1. Poll branch/debug evidence for refreshed CPU results.
2. Require static schema v7 `passed:true` and consolidated self-test schema v6 `passed:true`.
3. If red, use only current `failedStage` + sanitized `failureLogTail`; fix the concrete issue without weakening product or scoring contracts.
4. Save this checkpoint again after each meaningful result.
5. Once CPU is green, make the one intentional real-audio workflow hardening edit and allow exactly one fresh GPU run.
6. Require fresh approved-audio source hash, complete runtime safety, positive frozen event count, polished preview/full PDFs, exact event/hash identity, PDF fidelity 1.0, reference sealed, Production unchanged.
7. Then recover/re-supply the clean complete professional Rhythm source if necessary.
8. Run: reference completeness → isolated professional scorer → mandatory final wrapper.
9. If score <0.99 or critical mismatches >0, change only general/reference-free algorithms and rerun audio from scratch.
10. Only after the real gate passes create `Final Rhythm Pipeline`.

## Bass — paused

Existing diagnostics remain green but are not final ground truth. No Bass capability work before Rhythm completion.
