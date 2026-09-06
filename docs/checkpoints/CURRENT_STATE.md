# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — **REAL USER-FLOW TARGET: ARBITRARY AUDIO UPLOAD → RHYTHM → PDF.**  
Branch: `v143-contextual-prune-lobo`

> Latest user direction supersedes the narrow goal of proving only the pinned `gomyway` fixture as the product target. The product target is now the real `/ai-tab` user flow: a user uploads their own supported audio file, selects **Rhythm Guitar**, the V143 pipeline processes that uploaded audio end-to-end, and `app/ai-tab/page.js` receives/returns the generated PDF through the existing product UI. Preserve older forensic checkpoints for history and safety boundaries.

## CURRENT BRANCH / VERIFIED BASELINE

- Branch head observed before this checkpoint write: `4fc47b9c3d34323ae19a5f1e2d748b623b7b426e`.
- Current `app/ai-tab/page.js` already uploads user audio through `@vercel/blob/client` to `/api/audio-upload`, submits `/api/analyze-audio-tab`, polls async Rhythm jobs, ACKs transient completed results, and sends analyzer output to `/api/generate-tab-preview`.
- Current page supports MP3, WAV, M4A and AAC selection.
- Existing repaired V143 async bridge commit remains `62deec179531b0f3e67c0e833365c2274697f02d`; regression commit remains `056508efdebc5973fde25cd4d83eb40108189231`.
- Authoritative model-free GREEN validation remains workflow run `34000667026`, job `101398830737`.
- Previously consumed diagnostic runs `33999777841`, `33999522733`, and `33998283085` must never be rerun.

## LATEST USER REQUIREMENT

Implement/verify the product pipeline so that:

1. A real user can upload their chosen supported audio on `dadrocktabs.com/ai-tab`.
2. The file is handled by the upload architecture without an artificial small-file assumption in the browser/server handoff; large practical user files must use direct Blob upload rather than being buffered through a Vercel Function body.
3. User selects **Rhythm Guitar**.
4. `/api/analyze-audio-tab` starts the current V143 Rhythm analyzer against that uploaded Blob source.
5. `app/ai-tab/page.js` polls the same async job until terminal without spawning replacement jobs.
6. The returned structured Rhythm result is handed directly to the deterministic PDF renderer.
7. The page exposes the resulting PDF to the user through the existing preview/unlock/download product flow.
8. The PDF stage must never restart audio/model inference.

Interpret “any size audio file” as **remove avoidable application-level small-file limits and support large practical uploads using streaming/direct Blob architecture**. Do not claim literally unbounded bytes where Vercel Blob, browser, network, analyzer runtime, ffmpeg, memory, or platform quotas impose finite limits. Surface deterministic errors for genuine platform limits.

## IMPORTANT SAFETY / EXECUTION ACCOUNTING

- No new model-bearing/audio inference has been consumed while retargeting this checkpoint.
- The earlier one-shot `gomyway` authorization has **not** been spent.
- Do not turn implementation work into repeated paid/model-bearing tests.
- No production Vercel promotion/change unless explicitly authorized.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No restricted GOAT access.
- No optimizer/training/overnight search or scheduler/model/parameter mutation.
- No whole-branch merge to `main`.
- Async result storage remains transient; no raw audio/stems/model bytes retained as evidence.

## NEXT STEPS FOR CONTINUATION

1. Inspect `app/api/audio-upload/route.js` for upload-size/content-type constraints and confirm browser-to-Blob direct upload, not Vercel Function body buffering.
2. Inspect `app/api/analyze-audio-tab/route.js` for source validation, Blob access, max-size/download assumptions, Rhythm async start/status/ACK behavior, timeouts, and payload size limits.
3. Inspect `analyzer/v143_modal_http_endpoint.py` and the current V143 worker path for audio download/read limits, ffmpeg input handling, duration/segment assumptions, request-body limits, and whole-file in-memory buffering that would break large uploads.
4. Inspect `app/api/generate-tab-preview/route.js` and `app/api/generate-tab-pdf/route.js` plus the page download handler to prove the structured analyzer result is converted to PDF without a second inference call.
5. Make the narrowest code changes needed for large practical user uploads and end-to-end Rhythm → PDF handoff.
6. Add/adjust model-free regression coverage for upload validation, async status/ACK, structured result → PDF handoff, and prevention of a second analyzer start.
7. Save `CURRENT_STATE.md` after meaningful changes and before any live/model-bearing test.
8. Validate with model-free/static tests first. Do not consume a live Rhythm model run merely to test routing if deterministic tests suffice.
9. If a real model-bearing E2E is eventually used, preserve the previous explicit single-run budget unless the user grants broader live-run authorization.
10. End with a checkpoint describing exact changed files, test evidence, remaining platform limits, and whether the real `/ai-tab` upload → Rhythm → PDF path is ready.

Current state: **IMPLEMENTATION/VERIFICATION IN PROGRESS. No new live inference consumed.**
