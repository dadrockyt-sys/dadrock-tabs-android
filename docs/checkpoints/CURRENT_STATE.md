# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — **FINAL PRE-ARM CHECKPOINT; LIVE RUN STILL UNCONSUMED.**  
Branch: `v143-contextual-prune-lobo`

## AUTHORIZATION / HARD BUDGET

User explicitly authorized making the current V143 `gomyway` Rhythm E2E work and running it. Do not ask again.

- Rhythm live/model-bearing starts: **1 available / 0 consumed**.
- Professional full-1–113 scoring passes: **1 available / 0 consumed**.
- PDF E2E: **0 performed**.
- Retry/replacement live run: **NOT authorized**.
- Lead/Bass model run: **NOT authorized**.
- No production deployment/promotion/change, no protection weakening, no optimizer/training/threshold sweep/model mutation.
- If the single live start/job fails: **STOP; no second start**.

## PRE-ARM SOURCE STATE

Staged branch head immediately before this checkpoint: `ef5718b5509b42b9afd8dbb94d634a263defd2f4`.

The execution has been isolated behind a dedicated trigger path so checkpoint/helper/workflow commits cannot start the model:

- One-shot runner: `.github/scripts/v143-one-shot-final-rhythm-e2e.sh`
- Runner blob: `5aa292b23c9dbe3190a49baf59b01d0907d59f4d`
- Trigger-only workflow: `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- Workflow triggers **only** when `.github/one-shot/v143-final-rhythm-run.txt` is pushed on this branch.
- Creating/staging the runner and workflow did **not** match that trigger path; live budget is still untouched.
- Workflow concurrency: `v143-final-rhythm-one-shot-never-retry`, `cancel-in-progress: false`.
- Workflow has `contents: read` + `id-token: write`; Vercel token comes only from existing GitHub Actions secret.
- The workflow performs a fresh **Preview-only** Vercel build/deploy. It contains no `--prod`, `promote`, rollback, env mutation, or Deployment Protection mutation.

## PINNED CURRENT-V143 SOURCE BOUNDARY

- Audio: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Audio Git blob: `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- Audio URL used by runner: `https://raw.githubusercontent.com/dadrockyt-sys/dadrock-tabs-android/main/public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Analyze route blob: `a3d02876d2c4efeb6f5258586046bc95cfc132b6`
- `/ai-tab` page blob: `c218639afcdbb7540ff7cc34583afc6d83587fa0`
- Async bridge blob: `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- Async protocol blob: `1bd55017e16a4e1d8b14c7429492f811a43a28d8`
- Modal live worker blob: `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- Deterministic scheduler/separator blob: `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- Fixed Modal worker: app `dadrock-v143-ai-tab-live`, function `rhythm_v143_request`.
- Bridge repair commit: `62deec179531b0f3e67c0e833365c2274697f02d`.

The stale existing Preview `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD` / source `0a07b393bb47123a1142fd46ea6d9a55b04f0486` was explicitly **not** used because it predates the current repaired bridge/route boundary. The staged one-shot therefore builds a new Preview from the exact armed branch checkout before the single start.

## FULL PROFESSIONAL 1–113 REFERENCE

- Preserved reference: `research/v154-professional-references/rhythm-professional-reference.json`
- Git blob: `248741bade9665a34648c59a2994bd27d73fc406`
- SHA-256: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- Coverage: measures **1–113**, 113 stored measure objects, 603 professional events/onsets, 946 notes.
- Provenance: `research/v154-professional-references/rhythm-professional-reference-provenance.json`.
- Source professional image: `public/Professionalexample.jpg`, Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`.
- The reference is **not** placed in `validation/rhythm_holdout/reference/` until after the live result is frozen and exact PDF event fidelity is verified. The temporary scorer-only copy is deleted before artifact upload.

## PROFESSIONAL SCORER / FREEZE / PDF

- `validation/rhythm_holdout/freeze_rhythm_analysis.py` blob `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`.
- `validation/rhythm_holdout/render_frozen_rhythm_pdf.mjs` blob `3c50c06e2394dfac1c80acb20aefa33583907b33`.
- `validation/rhythm_holdout/verify_pdf_event_fidelity.py` blob `5e1564216873046237fb545078a04a6b18f72b27`.
- PDF renderer: `lib/createV143RhythmPdf.js` blob `4f0e1372dd5903c05c25f0f0a302dd35e81de36b`.
- Professional scorer: `validation/rhythm_holdout/score_rhythm_holdout.py` blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`.
- Final orchestrator: `validation/rhythm_holdout/run_final_holdout_gate.py` blob `c6a84434eefa768a924395b76d1d25b4e5a51307`.
- Final threshold: 0.99; onset tolerance 0.50 step; gross timing tolerance 2.00 steps; duration tolerance 0.25 step.

One-shot runner order is fail-closed:

1. Verify all pinned blobs and professional-reference SHA without opening it in scorer infrastructure.
2. Build/deploy a fresh Vercel **Preview only** from exact `GITHUB_SHA`.
3. Model-free protected-route preflight using GitHub OIDC.
4. Send exactly **one** `operation:"start"` Rhythm request. At that instant live budget becomes consumed.
5. Poll only the same signed job token; transport errors continue same-token polling and never start a replacement.
6. Require one valid terminal structured result.
7. Freeze exact `renderEvents` with anti-leakage flags.
8. Render preview + full PDFs from that frozen event stream and verify exact PDF event fidelity = 1.0.
9. Only then copy the preserved professional 1–113 reference into scorer-only storage and call `run_final_holdout_gate.py` exactly once; it invokes the professional scorer once.
10. Capture bounded score evidence; delete temporary scorer-only reference.
11. ACK/clear the same job token. ACK does not invoke the model.
12. Scrub raw response/token/full event-bearing JSON. Preserve only bounded summary/evidence, hashes/manifests, and generated PDFs.
13. If score is below 0.99, report the score and fail the final quality gate **without rerunning the model**.

## NEXT ACTION — ARM ONCE

Create exactly one file at `.github/one-shot/v143-final-rhythm-run.txt`. That push is the deliberate one-shot trigger. Do not edit/recreate that file to retry. After the workflow begins, inspect the single resulting run only; never rerun its job/run.

After terminal workflow state:
- download/read the `v143-final-rhythm-one-shot` artifact;
- save a FINAL checkpoint with workflow run/job/deployment IDs, exact armed `GITHUB_SHA`, live start status, score metrics, PDF fidelity/artifact sizes, ACK cleanup state, and final counters;
- return to HOLD.

Current state: **READY TO ARM. Live = 0 consumed; professional score = 0 consumed; PDF E2E = 0 performed.**
