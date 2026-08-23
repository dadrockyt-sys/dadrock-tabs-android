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

## Static diagnostic path — CURRENT

The original full-repository `npm ci` diagnostic path did not persist timely evidence even after bounded install/preflight stages. This is CI dependency-environment overhead, not a renderer or musical defect.

New authoritative bootstrap change:
`f84e4b1504fb648799341fbf68255664fb95dc0b` — `Use minimal PDF dependency for Rhythm static gate`.

The static preflight only requires `pdf-lib` as an external runtime package; all other checks are repository Python/Node scripts and local modules. The bootstrap now creates an isolated parent package containing exactly `pdf-lib@1.17.1`. Its ESM workspace is nested below that directory, so normal Node parent-directory module resolution sees the package without installing the complete Next.js application graph.

Current bootstrap behavior:
- exact triggering SHA checkout;
- CPU only; professional reference remains sealed;
- installs only `pdf-lib@1.17.1`, bounded to 180 seconds;
- runs authoritative `validation/rhythm_holdout/run_static_preholdout_preflight.sh` with `GITHUB_ACTIONS=false`, bounded to 360 seconds;
- preserves the same schema-v7 contracts and thresholds; no checks were removed or weakened;
- persists `debug/v143-contextual-prune/rhythm-static-bootstrap-preflight.json` and schema-v4 run identity;
- distinguishes minimal dependency install failure/timeout from static-runner failure/timeout;
- Production, Modal and GPU remain untouched.

The earlier fresh V2 workflow and full-`npm ci` bootstrap attempts are no longer primary. The minimal-dependency bootstrap is the next actionable proof source.

## After static green

Create/stabilize CPU-only schema-v6 self-test with exact SHA checkout, branch concurrency, no actor guard, internal static runner forced `GITHUB_ACTIONS=false`, and staging only the self-test proof (never canonical static evidence). The same isolated `pdf-lib@1.17.1` dependency approach may be used because the self-test's PDF/static contract uses the same renderer dependency.

## Real-audio pre-holdout after both CPU gates green

Do not intentionally trigger GPU work until static v7 + self-test v6 are green.
Then run exactly one approved-audio pre-holdout analysis/freeze/PDF proof. Require source hash, complete runtime safety, positive frozen events, polished preview/full PDFs, exact event/hash identity, fidelity 1.0, reference sealed, Production unchanged.

Only after that proof is locked may the complete professional human-written reference be recovered/opened for isolated scoring/final wrapper.

## Immediate next steps

1. Observe minimal-dependency bootstrap proof from `f84e4b15...`.
2. If red, use only current schema-v7 `failedStage` + sanitized `failureLogTail` and fix that exact CPU issue without weakening contracts.
3. If green, establish schema-v6 self-test immediately.
4. Save this checkpoint after every meaningful result.
5. Only after both CPU gates green, run exactly one fresh real-audio pre-holdout freeze/PDF proof.
6. Then recover/use complete professional reference strictly scorer-side.
7. If score <0.99 or critical mismatches >0, improve only general/reference-free logic, rerun fresh audio, then rescore.
8. When real gate passes, verify DadRock `/ai-tab` user end-to-end and create `Final Rhythm Pipeline`.
