# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-06 — **PACKAGING REPAIRED; SECOND PRE-START ARM READY; LIVE RUN STILL UNCONSUMED.**  
Branch: `v143-contextual-prune-lobo`

## AUTHORIZATION / HARD BUDGET

User explicitly authorized making the current V143 `gomyway` Rhythm E2E work and running it. Do not ask again.

- Rhythm live/model-bearing starts: **1 available / 0 consumed**.
- Professional full-1–113 scoring passes: **1 available / 0 consumed**.
- PDF E2E: **0 performed**.
- Retry/replacement **after a live start is sent**: **NOT authorized**.
- Lead/Bass model run: **NOT authorized**.
- No production deployment/promotion/change, no Deployment Protection weakening, no optimizer/training/threshold sweep/scheduler/model/parameter mutation.
- If the single live start/job fails after `operation:"start"` is sent: **STOP; no second model start**.

Verified branch head immediately before this checkpoint: `1bfd02a2d4b1d440afa1d00157a981f4205d6a5f`.

## FIRST ARM — PRE-START FAILURE ONLY; BUDGET NOT SPENT

The first dedicated arm was commit `610ac358cdff8b60970c408b366666425c2d660a`, workflow run `34012505486`, job `101430616920`.

Its fresh Preview deployment was:
- Deployment ID: `dpl_7fe8G9PswNHpvVr7ovMkiVByMpqU`
- URL: `dadrock-tabs-android-fxgu52jbs-stephen-mcnally-s-projects.vercel.app`
- Source commit: `610ac358cdff8b60970c408b366666425c2d660a`
- Target: Preview / non-production
- Result: `ERROR` during Vercel `direct:build`
- Error code: `NOW_SANDBOX_WORKER_MAX_UNCOMPRESSED_FUNCTION_SIZE`
- Error detail: `api/analyze-audio-tab` was **425.26 MB uncompressed**, exceeding Vercel's 250 MB function limit.

Crucially, the deployment failed before protected-route preflight and before the runner reached the single `operation:"start"` boundary.

Preserved first-arm artifact:
- Artifact: `v143-final-rhythm-one-shot`
- Artifact ID: `9982913980`
- Artifact digest: `sha256:0dab392435d412c34fe2a1946dfa235c3ab658f99cc03878f98cbbce0070cb1e`
- Its bounded summary explicitly records:
  - `modelBearingStartRequestCount: 0`
  - `professionalScoreCalls: 0`
  - `pdfE2EPerformed: false`
  - `completed: false`
  - `acknowledged: false`
  - `transientResultCleared: false`
  - `productionEnvironmentChanged: false`
  - `productionPromotionPerformed: false`
  - `deploymentProtectionDisabled: false`
  - `referenceOpenedBeforeFreeze: false`
  - no raw audio/stems/model bytes retained.

Therefore this was **not a model retry** and did not consume the user's one authorized model-bearing run or score.

Never rerun workflow run `34012505486` or job `101430616920`.

## MODEL-FREE PACKAGING REPAIR

Root cause: `app/api/analyze-audio-tab/route.js` imports the V143 Rhythm PDF artifact path, so its Next.js server trace was pulling the large `public/` research/static tree. Existing proven trace isolation covered the PDF routes but not `/api/analyze-audio-tab`.

Applied the same existing model-free trace isolation pattern to the analyzer route:
- Commit: `cd32eccdb2f3b587e6bbae5b4e3e19406d120e3e`
- File: `next.config.js`
- New blob: `d057c0731bc7f8b261c3598a45a7aea6dc5c9583`
- `/api/analyze-audio-tab` now excludes `./public/**/*` from its serverless trace and explicitly includes only `./public/DadRock-Tabs-Logo.png`, matching the Product/PDF trace policy.
- No analyzer route logic, model, scheduler, bridge, thresholds, reference, or production configuration changed.

## SECOND PRE-START ARM ISOLATION

Updated trigger-only workflow in commit `1bfd02a2d4b1d440afa1d00157a981f4205d6a5f`:
- Workflow: `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- Workflow blob: `87d662bf25822c89c0d9e5c5b0a8fac3bd347bb5`
- New trigger path: `.github/one-shot/v143-final-rhythm-run-2.txt`
- The workflow now also pins `next.config.js` blob `d057c0731bc7f8b261c3598a45a7aea6dc5c9583` before execution.
- Updating the workflow itself did not match the trigger path and therefore did not issue a live/model request.
- Concurrency remains `v143-final-rhythm-one-shot-never-retry`, `cancel-in-progress: false`.
- Permissions remain `contents: read`, `id-token: write`; Vercel authentication comes from the existing Actions secret.
- The runner builds/deploys **Preview only** and contains no `--prod`, `promote`, rollback, env mutation, or Deployment Protection mutation.

One-shot runner:
- `.github/scripts/v143-one-shot-final-rhythm-e2e.sh`
- Blob: `5aa292b23c9dbe3190a49baf59b01d0907d59f4d`

## PINNED CURRENT-V143 SOURCE BOUNDARY

- Audio: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Audio Git blob: `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- Analyze route blob: `a3d02876d2c4efeb6f5258586046bc95cfc132b6`
- `/ai-tab` page blob: `c218639afcdbb7540ff7cc34583afc6d83587fa0`
- `next.config.js` packaging blob: `d057c0731bc7f8b261c3598a45a7aea6dc5c9583`
- Async bridge blob: `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- Async protocol blob: `1bd55017e16a4e1d8b14c7429492f811a43a28d8`
- Modal live worker blob: `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- Deterministic separator/scheduler blob: `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- Fixed Modal worker: app `dadrock-v143-ai-tab-live`, function `rhythm_v143_request`.
- Bridge repair commit: `62deec179531b0f3e67c0e833365c2274697f02d`.

## FULL PROFESSIONAL RHYTHM REFERENCE — 1–113

- Reference: `research/v154-professional-references/rhythm-professional-reference.json`
- Git blob: `248741bade9665a34648c59a2994bd27d73fc406`
- SHA-256: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- Coverage: measures **1–113**, 113 stored measure objects, 603 professional events/onsets, 946 notes.
- Provenance: `research/v154-professional-references/rhythm-professional-reference-provenance.json`.
- Professional image source: `public/Professionalexample.jpg`, Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`.
- Scorer-only temporary reference access is forbidden until the live result is frozen and exact PDF event fidelity has passed.

Excluded from the reserved score:
- `public/gomyway-professional-rhythm-reference-v2.json` — measures 1–16 only.
- `public/gomyway-professional-rhythm-reference-17-113.json` — partial fallback.
- `public/jimmy-paige-midterm-v1/jimmy-midterm-113-measure-paper-v1.json` — blind/paper candidate, not answer key.

## PROFESSIONAL SCORER / FREEZE / PDF PINS

- `validation/rhythm_holdout/freeze_rhythm_analysis.py` blob `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- `validation/rhythm_holdout/render_frozen_rhythm_pdf.mjs` blob `3c50c06e2394dfac1c80acb20aefa33583907b33`
- `validation/rhythm_holdout/verify_pdf_event_fidelity.py` blob `5e1564216873046237fb545078a04a6b18f72b27`
- `lib/createV143RhythmPdf.js` blob `4f0e1372dd5903c05c25f0f0a302dd35e81de36b`
- Professional scorer `validation/rhythm_holdout/score_rhythm_holdout.py` blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- Completeness verifier blob `2504581dd72b6c375fbc0b68d4d396fce58deb87`
- Canonicalizer blob `088d44827fb23e20d9aeeb4944a672989af5846c`
- Final orchestrator `validation/rhythm_holdout/run_final_holdout_gate.py` blob `c6a84434eefa768a924395b76d1d25b4e5a51307`
- Professional threshold 0.99; onset tolerance 0.50 step; gross timing tolerance 2.00 steps; duration tolerance 0.25 step.

## EXACT NEXT ACTION

Create `.github/one-shot/v143-final-rhythm-run-2.txt` exactly once. That push is a **second pre-start infrastructure attempt**, not a second model attempt, because the first workflow's immutable artifact proves `modelBearingStartRequestCount = 0`.

Then inspect only the resulting `V143 Final Rhythm One Shot` workflow run:
1. source and packaging pins must pass;
2. fresh Preview must build READY;
3. model-free protected-route preflight must pass;
4. exactly one `operation:"start"` may then be sent — **at that instant live budget becomes 1 consumed / 0 available**;
5. poll only the same signed job token / same Modal FunctionCall;
6. no replacement start under any terminal failure;
7. if completed, freeze the exact structured result, render preview/full PDFs from it, prove PDF event fidelity = 1.0, then open the professional reference and score exactly once;
8. ACK/clear the same job and scrub raw/token/reference/event-bearing transient files;
9. save FINAL checkpoint and return to HOLD.

Current state: **READY FOR SECOND PRE-START ARM. Live = 0 consumed; professional score = 0 consumed; PDF E2E = 0 performed.**
