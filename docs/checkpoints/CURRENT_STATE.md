# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-06 — **TWO PRE-START FAILURES ONLY; PROVEN PROTECTED-PREVIEW TRANSPORT STAGED; LIVE RUN STILL UNCONSUMED.**  
Branch: `v143-contextual-prune-lobo`

## AUTHORIZATION / HARD BUDGET

User explicitly authorized making the current V143 `gomyway` Rhythm E2E work and running it. Do not ask again.

- Rhythm live/model-bearing starts: **1 available / 0 consumed**.
- Professional full-1–113 scoring passes: **1 available / 0 consumed**.
- PDF E2E: **0 performed**.
- Any retry/replacement **after `operation:"start"` is sent**: **NOT authorized**.
- Lead/Bass model run: **NOT authorized**.
- No production deployment/promotion/change, no Deployment Protection weakening, no bypass secret/share-link creation, no optimizer/training/threshold sweep/model mutation.

## PRE-START ATTEMPT HISTORY — BOTH ZERO CONSUMPTION

### Attempt 1 — packaging failure before route preflight

- Arm commit: `610ac358cdff8b60970c408b366666425c2d660a`
- Workflow run: `34012505486`
- Job: `101430616920`
- Preview deployment: `dpl_7fe8G9PswNHpvVr7ovMkiVByMpqU`
- Failure: `NOW_SANDBOX_WORKER_MAX_UNCOMPRESSED_FUNCTION_SIZE`; `/api/analyze-audio-tab` was 425.26 MB > 250 MB.
- Artifact ID: `9982913980`
- Artifact digest: `sha256:0dab392435d412c34fe2a1946dfa235c3ab658f99cc03878f98cbbce0070cb1e`
- Preserved summary proves `modelBearingStartRequestCount=0`, `professionalScoreCalls=0`, `pdfE2EPerformed=false`.
- Never rerun workflow `34012505486` / job `101430616920`.

Packaging repair:
- Commit `cd32eccdb2f3b587e6bbae5b4e3e19406d120e3e`
- `next.config.js` blob `d057c0731bc7f8b261c3598a45a7aea6dc5c9583`
- Added `/api/analyze-audio-tab` to existing public-trace exclusion while explicitly retaining `public/DadRock-Tabs-Logo.png`.
- Model/analyzer/bridge/scheduler/reference/production logic unchanged.

### Attempt 2 — protected-route transport failure before model start

- Arm commit: `6212f6c64a2bcebaebfae7f4f7bc22d2a0483894`
- Workflow run: `34012747879`
- Job: `101431245172`
- Exact Preview deployment: `dpl_3LdGRdXb7ZkmNUojrXun72my84M4`
- Preview URL: `https://dadrock-tabs-android-iwhmrcol7-stephen-mcnally-s-projects.vercel.app`
- Preview source commit: `6212f6c64a2bcebaebfae7f4f7bc22d2a0483894`
- Preview target: `preview`
- Preview state: **READY**
- Build/package fix validated on the exact armed Preview; no 425 MB failure.
- Failure: model-free protected-route preflight returned `protectedPreviewRouteReached=false` using the new runner's raw GitHub OIDC curl path.
- Vercel runtime logs contained no function invocation for that preflight, confirming failure occurred before application route execution.
- Artifact ID: `9982986412`
- Artifact zip digest from workflow: `ceb5393458c5bec5d007ec56919c122b6fe911a61509e1e104060918354acc31`
- Preserved summary proves `modelBearingStartRequestCount=0`, `professionalScoreCalls=0`, `pdfE2EPerformed=false`, `previewReady=true`.
- Never rerun workflow `34012747879` / job `101431245172`.

Therefore **both attempts were pre-start infrastructure attempts, not model retries. Live budget remains 0 consumed.**

## ROOT CAUSE / PROVEN TRANSPORT FIX

Historical repo helper commit `e24eb3b3ef05f25faa2ddefd1bee66327549b98e` repaired the protected Preview preflight by using the Vercel CLI's authenticated transport:

`vercel curl /api/analyze-audio-tab --deployment <preview> -- ...`

The current repo helper `.github/scripts/v143-existing-preview-async-breakthrough-e2e.sh` uses that same `vercel curl` transport for **preflight, start, same-token status polling, and ACK**. This is the already-established protected-Preview path; it does not disable protection, create a bypass secret, or create a share link.

New final helper staged:
- `.github/scripts/v143-one-shot-final-rhythm-existing-preview.sh`
- Blob: `e2847e4d05ae1fea781ef07e891fece1bfbecbf0`
- Commit creating helper: `2db1642d8fe54d1b6076131d6a5e91ad1c5852ba`
- Reuses immutable READY Preview `dpl_3LdGRdXb7ZkmNUojrXun72my84M4`; performs **no deployment**.
- Uses `vercel inspect` to require exact deployment ID + target preview + READY.
- Uses proven `vercel curl --deployment` for model-free preflight, the single authorized start, same-token polls, and ACK.
- Includes EXIT-trap same-job ACK cleanup if validation fails after a live token exists; no replacement model start.
- Freezes terminal `renderEvents`, renders preview/full PDFs from that same freeze, verifies PDF-event fidelity, then opens the professional reference and scores once.
- Scrubs raw response/token/reference/full-event transient files before artifact upload.

Workflow staged:
- `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- Workflow blob: `947690980cf11ef9a53b837a2c70e718b8f7a5d9`
- Commit: `3c068925cd8fdec272fad456b1f7d0052d43f545`
- Trigger path: `.github/one-shot/v143-final-rhythm-run-3.txt`
- `contents: read` only; no OIDC permission needed.
- Pins exact READY Preview URL/ID/source commit and all current route/model-support blobs.
- Concurrency remains `v143-final-rhythm-one-shot-never-retry`, `cancel-in-progress:false`.

## PINNED CURRENT-V143 SOURCE BOUNDARY

- Audio: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Audio Git blob: `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- Analyze route blob: `a3d02876d2c4efeb6f5258586046bc95cfc132b6`
- `/ai-tab` page blob: `c218639afcdbb7540ff7cc34583afc6d83587fa0`
- `next.config.js` blob: `d057c0731bc7f8b261c3598a45a7aea6dc5c9583`
- Async bridge blob: `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- Async protocol blob: `1bd55017e16a4e1d8b14c7429492f811a43a28d8`
- Modal live worker blob: `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- Deterministic separator/scheduler blob: `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- Fixed Modal worker: app `dadrock-v143-ai-tab-live`, function `rhythm_v143_request`.

## FULL PROFESSIONAL RHYTHM REFERENCE — 1–113

- `research/v154-professional-references/rhythm-professional-reference.json`
- Git blob: `248741bade9665a34648c59a2994bd27d73fc406`
- SHA-256: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- Coverage: measures 1–113, 113 stored measures, 603 professional events/onsets, 946 notes.
- Reference remains outside scorer-only temp storage until exact live freeze + PDF fidelity are complete.

## FINAL FREEZE / PDF / SCORE PINS

- Freeze: `validation/rhythm_holdout/freeze_rhythm_analysis.py` blob `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- PDF render harness: `validation/rhythm_holdout/render_frozen_rhythm_pdf.mjs` blob `3c50c06e2394dfac1c80acb20aefa33583907b33`
- PDF fidelity verifier: `validation/rhythm_holdout/verify_pdf_event_fidelity.py` blob `5e1564216873046237fb545078a04a6b18f72b27`
- Renderer: `lib/createV143RhythmPdf.js` blob `4f0e1372dd5903c05c25f0f0a302dd35e81de36b`
- Scorer: `validation/rhythm_holdout/score_rhythm_holdout.py` blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- Final gate: `validation/rhythm_holdout/run_final_holdout_gate.py` blob `c6a84434eefa768a924395b76d1d25b4e5a51307`
- Threshold: 0.99.

## EXACT NEXT ACTION

Create `.github/one-shot/v143-final-rhythm-run-3.txt` exactly once.

This third arm still precedes any model start because attempts 1 and 2 have immutable artifacts proving zero start requests. The run must:
1. verify the exact existing READY Preview and all pinned blobs;
2. run model-free preflight through proven `vercel curl` transport;
3. only if preflight passes, send exactly **one** `operation:"start"` — at that instant live budget becomes consumed;
4. poll only the same signed job token;
5. never send a replacement start under any failure;
6. on completion, freeze exact result → render preview/full PDFs → prove PDF fidelity 1.0 → open professional reference → score exactly once → ACK same job → scrub transient material;
7. save FINAL checkpoint and return to HOLD.

Current state: **READY FOR THIRD PRE-START ARM. Live = 0 consumed; professional score = 0 consumed; PDF E2E = 0 performed.**
