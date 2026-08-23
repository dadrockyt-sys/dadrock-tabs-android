# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute rules

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, redeem tokens, send customer emails, weaken thresholds, or call Bass/Lead professional structured output early.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Preview/full must use the same authenticated/frozen stream. Browser/PDF may not invent placement. Professional human reference is scorer-only and may never be read/trained/tuned/selected by runtime. Any post-score musical improvement must remain general/reference-free and requires a fresh audio run before rescoring.

**Save this checkpoint frequently.**

## Completion gate

Rhythm is complete only with professional score >=0.99, zero critical mismatches, and PDF-event fidelity exactly 1.0. Then create `Final Rhythm Pipeline`. Bass remains paused until then; Lead remains after Bass.

## Existing real-audio structural baseline

Approved fixture: `public/gomywayfullaitest.m4a`.
Prior structural proof: 358 valid Rhythm events, measures 1..113 / 112 unique measures, all 16 grid steps, 25 technique events, sustain 358/358, tempo 129.19921875, 4/4, E Standard, prior full+preview PDFs.
Evidence: `debug/v143-contextual-prune/ai-tab-real-audio-canary.json` and `ai-tab-real-audio-pdf-validation.json`.
This is structural proof, not final professional musical correctness.

## Clean professional holdout

Do **not** open/recover the professional human reference yet. Fresh reference-free freeze/PDF proof must be locked first.
Previously confirmed surviving clean screenshot: Library `1000116180.jpg`, Chorus measures 33–35, labels `G6`, `A(tp2)`, `E`, `D`.
`validation/rhythm_holdout/reference/reference-inventory.json` remains `completeReferenceAvailable:false`, `finalScoringAuthorized:false`.
User now wants the eventual end-to-end DadRock result tested against the complete professional human-written PDF/reference once pre-holdout isolation is green.

## Product PDF source of truth

`app/ai-tab/page.js` is authoritative.
Preview → `/api/generate-tab-preview`; full/purchased → `/api/generate-tab-pdf`.
Authenticated Rhythm path:
`page.js → PDF API → createJimmyPaigeProfessionalPdf → createAiTabPdf → createV143RhythmPdf`.
Both preview/full carry exact structured fields including `renderEvents`; preview is locked/watermarked; `createV143RhythmPdf` is the polished DadRock renderer.

## Runtime/event safety already hardened

Required facts: `referenceFree:true`, `professionalReferenceUsed:false`, `referenceRuntimeInputUsed:false`, `runtimeLabelsRequired:false`, `v143RuntimeSafetyVerified:true`.
Downstream wrappers validate authenticated V143 events and reject invalid V143 legacy fallback. Product contract schema v7 verifies page/PDF boundaries, branding/logo, and preview lock. Production remains untouched.

## CPU gates required before GPU

Required persisted evidence:
- `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json` → schema 7, `passed:true`
- `debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json` → schema 6, `passed:true`

Old persisted static evidence is stale schema v4 from `b65cf9dd...` with `/tmp/... pdf-lib` resolution failure and must not be used to diagnose current renderer behavior.

## GitHub Actions recovery

Old static workflow was hardened with exact SHA checkout, concurrency, install diagnostics, runner failure persistence, and strict failure restoration, but still did not refresh repository evidence.

A minimal branch heartbeat proved Actions itself is healthy:
- `.github/workflows/v143-actions-branch-heartbeat.yml`
- source commit `f434fb682cf392c209e3f11a438b9de99e72e0ac`
- run ID `32621233674`
- proof commit `5045e95a139bd993fe87ab7cc6b44ee1a2f1e092`
- `debug/v143-contextual-prune/actions-branch-heartbeat.json` → `passed:true`

Therefore the stale static evidence problem is workflow-specific, not repository-wide.

## Fresh standalone static V2 — CURRENTLY IN FLIGHT

Created `.github/workflows/rhythm-preholdout-static-preflight-v2.yml` at commit:
`3ea7a6298455f5b4235d7af15fa164419f044686` — `Add fresh Rhythm static preflight workflow`.

V2 is CPU-only and:
- checks out exact triggering SHA;
- uses independent concurrency;
- installs locked dependencies;
- runs `validation/rhythm_holdout/run_static_preholdout_preflight.sh` with `GITHUB_ACTIONS=false` so only the workflow owns persistence;
- always writes canonical schema-v7 static evidence plus `debug/v143-contextual-prune/rhythm-preholdout-static-v2-run.json`;
- restores a failing job result if canonical report is not schema 7 green;
- never opens the professional reference and does not trigger the real-audio GPU workflow.

At the latest check, the V2 evidence file had not yet appeared and branch head was still `3ea7a629...`; the run may still be executing/queued. Do not infer failure until the 15-minute V2 timeout window plus queue uncertainty is exhausted.

## Self-test stabilization after static green

Current old self-test has mutable branch checkout, actor guard, no concurrency, and writes the standalone static evidence file from inside itself.
After static schema 7 green, create/stabilize a CPU-only self-test that:
- exact-SHA checks out;
- uses branch concurrency;
- has no bot actor guard;
- runs internal static preflight with `GITHUB_ACTIONS=false`;
- stages only schema-v6 self-test evidence;
- never overwrites canonical standalone static evidence.

## Real-audio pre-holdout after both CPU gates green

`.github/workflows/rhythm-professional-preholdout-real-audio.yml` exists but is not yet established green.
Do not intentionally trigger GPU work until static v7 + self-test v6 are both green.
Then permit exactly one fresh approved-audio run and require source hash, full runtime safety, positive frozen events, polished preview/full PDFs, exact event/hash identity, fidelity 1.0, reference sealed, Production unchanged.

## Immediate next steps

1. Observe V2 canonical schema-v7 result.
2. If red, use only its current `failedStage` + sanitized `failureLogTail`; fix the concrete CPU issue without weakening contracts.
3. If green, establish isolated schema-v6 self-test.
4. Save this checkpoint after every meaningful result.
5. Only after both CPU gates are green, run exactly one fresh real-audio pre-holdout freeze/PDF proof.
6. Only after that proof is locked, recover/use the complete professional human-written reference strictly in the isolated scorer/final wrapper.
7. If score <0.99 or critical mismatches >0, improve only general/reference-free logic, rerun audio from scratch, then rescore.
8. Once real gate passes, test the DadRock `/ai-tab` user end-to-end path against that professional reference and create `Final Rhythm Pipeline`.
