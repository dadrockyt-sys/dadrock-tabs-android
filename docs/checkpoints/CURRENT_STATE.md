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
User wants the eventual DadRock `/ai-tab` end-to-end result tested against the complete professional human-written PDF/reference once pre-holdout isolation is green.

## Product PDF source of truth

`app/ai-tab/page.js` is authoritative.
Preview → `/api/generate-tab-preview`; full/purchased → `/api/generate-tab-pdf`.
Authenticated Rhythm path:
`page.js → PDF API → createJimmyPaigeProfessionalPdf → createAiTabPdf → createV143RhythmPdf`.
Both preview/full carry exact structured fields including `renderEvents`; preview is locked/watermarked; `createV143RhythmPdf` is the polished DadRock renderer.

## CPU gates before GPU

Required evidence:
- canonical static: `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json` → schema 7 + `passed:true`
- consolidated self-test: `debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json` → schema 6 + `passed:true`

Old canonical static evidence is stale schema v4 from `b65cf9dd...` with `/tmp/... pdf-lib` failure and is not actionable for current code.

## Actions observability / recovery

Actions + branch writes are confirmed healthy:
- heartbeat source `f434fb682cf392c209e3f11a438b9de99e72e0ac`
- run ID `32621233674`
- proof commit `5045e95a139bd993fe87ab7cc6b44ee1a2f1e092`
- `debug/v143-contextual-prune/actions-branch-heartbeat.json` → green.

A second minimal workflow also triggered correctly:
- `.github/workflows/rhythm-static-bootstrap.yml`
- bootstrap source `f05831139981d09a5f1779dab439970103757e8e`
- run ID `32621672641`
- proof commit `ba3a4c491318ebbbd1489734c71258ee1c04f0e4`.

Therefore branch workflow creation/update and `contents:write` are working.

## Static diagnostics now bounded — CURRENT

The first upgraded bootstrap static run (`01586977...`) did not persist evidence before nearing its 15-minute job timeout. Because its `npm ci` + static runner were unbounded inside a single step, a job-level timeout could kill the step before evidence persistence.

Fixed at commit:
`b7dd58c28853b5a39735397a954bb647db1251d3` — `Bound Rhythm static diagnostic stages`.

Current `.github/workflows/rhythm-static-bootstrap.yml` now:
- exact-SHA checkout;
- CPU only;
- 15-minute job timeout;
- `npm ci --ignore-scripts --no-audit --no-fund` bounded to 300 seconds;
- authoritative `run_static_preholdout_preflight.sh` bounded to 420 seconds with `GITHUB_ACTIONS=false`;
- reserves remaining job time to always synthesize/copy a schema-v7 diagnostic and commit it;
- distinguishes `install-locked-dependencies-timeout`, `install-locked-dependencies`, `static-runner-timeout`, and `static-runner-missing-report`;
- writes `debug/v143-contextual-prune/rhythm-static-bootstrap-preflight.json` plus schema-v3 bootstrap run identity;
- never opens professional reference and does not touch Production/GPU.

Separate install-only diagnostic workflow was also added at:
`49b8aa3fcf098a3d5d524eb052b0926f2b45b1df` — `Add Rhythm dependency install diagnostic`.
Its proof path is `debug/v143-contextual-prune/rhythm-install-diagnostic.json`; at last check it had not yet persisted.

The earlier fresh V2 workflow (`3ea7a629...`) also had not persisted evidence and is no longer the primary diagnostic path; the bounded bootstrap is authoritative for the next concrete failure signal.

## After static green

Create/stabilize CPU-only schema-v6 self-test with exact SHA checkout, branch concurrency, no actor guard, internal static runner forced `GITHUB_ACTIONS=false`, and staging only the self-test proof (never canonical static evidence).

## Real-audio pre-holdout after both CPU gates green

Do not intentionally trigger GPU work until static v7 + self-test v6 are green.
Then run exactly one approved-audio pre-holdout analysis/freeze/PDF proof. Require source hash, complete runtime safety, positive frozen events, polished preview/full PDFs, exact event/hash identity, fidelity 1.0, reference sealed, Production unchanged.

Only after that proof is locked may the complete professional human-written reference be recovered/opened for isolated scoring/final wrapper.

## Immediate next steps

1. Observe bounded bootstrap proof from `b7dd58c...`.
2. If red, use only current schema-v7 `failedStage` + sanitized `failureLogTail` and fix that exact CPU issue without weakening contracts.
3. If green, establish schema-v6 self-test.
4. Save this checkpoint after every meaningful result.
5. Only after both CPU gates green, run exactly one fresh real-audio pre-holdout freeze/PDF proof.
6. Then recover/use complete professional reference strictly scorer-side.
7. If score <0.99 or critical mismatches >0, improve only general/reference-free logic, rerun fresh audio, then rescore.
8. When real gate passes, verify DadRock `/ai-tab` user end-to-end and create `Final Rhythm Pipeline`.
