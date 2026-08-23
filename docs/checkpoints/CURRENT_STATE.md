# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **complete Rhythm end-to-end before Bass/Lead**.
Latest functional commit under test: `400edb3febfa32626f7830d641f641c9325a93bf` — `Verify AI PDF router rejects invalid V143 fallback`.
Latest CPU-workflow orchestration commit: `b7b91f9c47001e2e931cd3e9d69163f7d0317e23` — `Allow authoritative Rhythm static gate on all branch pushes`.

## Absolute rules

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, redeem tokens, send customer emails, weaken thresholds, or call Bass/Lead professional structured output early.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Preview/full must use the same authenticated/frozen stream. Browser/PDF may not invent placement. Professional human reference is scorer-only and may never be read/trained/tuned/selected by runtime. Any post-score musical improvement must remain general/reference-free and requires a fresh audio run before rescoring.

**Save this checkpoint frequently.**

## Completion order

1. Rhythm: professional score >=0.99, zero critical mismatches, PDF-event fidelity exactly 1.0 → `Final Rhythm Pipeline`.
2. Bass only after Rhythm; user provides Bass holdout when scoring is ready → `Final Bass Pipeline`.
3. Lead only after that → `Final Lead Pipeline`.

Bass remains paused.

## Existing real-audio Rhythm baseline

Approved fixture: `public/gomywayfullaitest.m4a`.
Existing structural proof: V143 reference-free Rhythm, 358 valid events, measures 1..113 / 112 unique measures, all 16 grid steps, 25 technique events, sustain 358/358, tempo 129.19921875, 4/4, E Standard, prior full+preview PDFs.
Evidence: `debug/v143-contextual-prune/ai-tab-real-audio-canary.json` and `ai-tab-real-audio-pdf-validation.json`.
This is structural proof, not final professional musical correctness.

## Clean professional holdout

Complete clean whole-song professional Rhythm source is still not available. Confirmed clean surviving screenshot: Library `1000116180.jpg`, Chorus measures 33–35, dark professional TAB, labels `G6`, `A(tp2)`, `E`, `D`.
Do not use DadRock/generated/development screenshots, old Chorus development references, coarse fixtures, or contextual-prune development references as final ground truth.
`validation/rhythm_holdout/reference/reference-inventory.json` remains `completeReferenceAvailable:false`, `finalScoringAuthorized:false`.
Do not unblock reference access until fresh reference-free freeze/PDF proof is locked.

## `app/ai-tab/page.js` is the PDF product source of truth

Preview → `/api/generate-tab-preview`; purchased/full → `/api/generate-tab-pdf`.
Both carry exact structured musical fields including `renderEvents`; preview is locked/watermarked and both expect PDF.
Authenticated Rhythm path:
`page.js → PDF API → createJimmyPaigeProfessionalPdf → createAiTabPdf → createV143RhythmPdf`.
`createV143RhythmPdf` is the real polished renderer with DadRock logo/branding. Do not invent a second PDF path.

## V143 runtime safety / event identity chain

Required runtime facts:
- `referenceFree:true`
- `professionalReferenceUsed:false`
- `referenceRuntimeInputUsed:false`
- `runtimeLabelsRequired:false`
- `v143RuntimeSafetyVerified:true`

Important hardening already in branch:
- payload + analyzer API fail closed on incomplete runtime safety;
- freeze/PDF fidelity/reference completeness/final wrapper bind that safety;
- `e0c1cd7b...` binds immutable professional-reference bytes before/after scoring;
- `a7a76e5b...`, `e7128a7f...`, `0f902f49...` make professional wrapper, AI PDF router and final Rhythm renderer validate authenticated events rather than re-project them and prohibit legacy fallback for invalid V143 streams;
- `400edb3f...` product-contract schema v7 verifies all three downstream exact-validation boundaries plus `app/ai-tab/page.js`, DadRock branding/logo and preview lock.

No professional reference was opened by this hardening. Production remains untouched.

## CPU proof target — authoritative refresh still required

Required evidence:
- `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json` → schema **7**, `passed:true`
- `debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json` → schema **6**, `passed:true`

The currently persisted static file is still stale schema v4 from `b65cf9dd...` with `/tmp/... pdf-lib` module-resolution failure. That old failure is test-environment-only and must not be treated as a current polished renderer/logo defect. The current runner uses repository-local `.preholdout-static`.

### CPU workflow orchestration repairs

`741a8bf7512a4b2e4c49f461301b0fce1cc98dcd`:
- static workflow checks out exact `${{ github.sha }}` instead of mutable branch head;
- branch-scoped concurrency cancels overlapping older static runs.

`8f00a6be802f2d0ff9ce3de69ba85b3ab7b617ac`:
- dependency install is logged;
- a sanitized schema-v7 `install-locked-dependencies` diagnostic is committed if `npm ci` fails before the main runner.

`b7b91f9c47001e2e931cd3e9d69163f7d0317e23`:
- removed the standalone static job's `github.actor != github-actions[bot]` guard;
- this is safe from evidence loops because `debug/**` is not in that workflow's push path filter;
- exact-SHA checkout, concurrency and install-failure diagnostics remain intact.

These changes affect CI orchestration/evidence only. They do not modify renderer behavior, musical thresholds, Modal/Production, payment paths, or professional-reference access.

Next authoritative event is the fresh schema-v7 static result from `b7b91f9c...` (or descendant containing it). Ignore stale schema-v4 evidence while waiting.

## Fresh real-audio pre-holdout workflow

`.github/workflows/rhythm-professional-preholdout-real-audio.yml` is coded, but `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` is not established green.

**Do not intentionally trigger duplicate GPU work until CPU static v7 + self-test v6 are both green.**
After CPU green, strengthen that workflow's compact proof and intentionally allow exactly one fresh approved-audio GPU run. Require source hash, complete runtime safety, positive frozen events, polished preview/full PDFs, exact event/hash identity, fidelity 1.0, reference sealed, Production unchanged.

## Immediate next steps

1. Observe new standalone static evidence from `b7b91f9c...`; require schema v7.
2. If red, use only the current `failedStage` + sanitized `failureLogTail` and fix the concrete issue without weakening contracts.
3. If green, stabilize the consolidated self-test (exact triggering SHA/concurrency and avoid cross-workflow static evidence races) and require schema v6 green.
4. Save this checkpoint after every meaningful result.
5. Only after both CPU gates green, proceed to exactly one fresh real-audio pre-holdout run.
6. Only after fresh freeze/PDF proof is locked, recover/re-supply the complete clean professional Rhythm source if needed and run completeness → isolated scorer → final wrapper.
7. If score <0.99 or critical mismatches >0, improve only general/reference-free logic, rerun audio from scratch, then rescore.
8. Only after the real gate passes create `Final Rhythm Pipeline`.

## Bass

Paused until Rhythm is complete. Existing Bass diagnostics remain available but are not final professional ground truth.
