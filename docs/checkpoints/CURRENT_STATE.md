# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — **REAL USER UPLOAD → V143 RHYTHM → PRIVATE PDF ARTIFACT FLOW IMPLEMENTED + BUILD GREEN; WORKER LARGE-FILE RUNTIME PROOF REMAINS.**  
Branch: `v143-contextual-prune-lobo`

> Latest user requirement is the real product path: a user uploads their chosen supported audio at `/ai-tab`, selects **Rhythm Guitar**, the current V143 async analyzer runs once, and the same completed structured result is rendered into the preview/full PDFs consumed by `app/ai-tab/page.js`. PDF generation must never start a second analyzer/model invocation.

## CURRENT VERIFIED BRANCH STATE

- Branch head immediately before this checkpoint write: `daa63261adccd3b7120df825f36f509e8b5cc64e`.
- Product implementation commit: `17397dfae18b56dcb13b9bd7291618dcf5357c6f` (`feat: scale Rhythm upload to PDF artifact flow`).
- Patch/model-free regression workflow: run `34006234785`, job `101413830044` — GREEN.
- Full model-free Next.js production build validation: run `34006290464`, job `101413989631` — GREEN, including:
  - dependency install;
  - permanent V143 large-Rhythm regression;
  - `npm run build` / Next.js production compile.
- Temporary one-shot patch script removed in commit `d454a93ada5df9ab4668f5fee741dc2a83f52607`.
- Temporary one-shot validation workflow removed in commit `daa63261adccd3b7120df825f36f509e8b5cc64e`.
- Permanent model-free regression remains: `.github/scripts/v143-large-rhythm-pipeline-regression.mjs`.
- No model/audio inference occurred during implementation or validation.

## IMPLEMENTED REAL PRODUCT FLOW

### 1. Browser upload (`app/ai-tab/page.js`)
- User chooses MP3/WAV/M4A/AAC as before.
- Upload is private Vercel Blob client upload with explicit `multipart: true`.
- Raw audio goes browser → Blob directly; it is not buffered through a Vercel Function body.

### 2. Upload authorization (`app/api/audio-upload/route.js`)
- Old application-level 50 MB maximum removed.
- Existing content-type, copyright-acknowledgement and instrument-selection validation remains.
- Vercel Blob/platform limits are now the raw-upload transport ceiling rather than an artificial 50 MB app cap.

### 3. V143 Rhythm analysis (`app/api/analyze-audio-tab/route.js`)
- Start still targets the current V143 Rhythm async analyzer for `transcriptionType === 'rhythm'`.
- Polling reuses the same async job token; no replacement job is introduced.
- Rhythm status asks for `delivery: 'pdf-artifacts'` plus song/artist metadata.
- Once that same job returns the valid structured V143 result, the route gives the already-completed structure directly to the deterministic PDF artifact renderer server-side.
- Browser receives only compact completion metadata + opaque `pdfArtifact`; large `renderEvents` do not need to cross the Vercel Function JSON response boundary.
- Browser ACKs the same analyzer token afterward, preserving existing transient-result cleanup.

### 4. Deterministic PDF artifact generation (`lib/v143RhythmPdfArtifacts.js`)
- New helper calls `createJimmyPaigeProfessionalPdf` on the already-completed V143 structured result.
- Generates both preview and full PDF **without any analyzer/model/API inference call**.
- Stores preview/full PDFs as private Vercel Blob artifacts under a random UUID path.
- Preview GET URL is signed/time-bounded (6 hours).
- Full PDF GET URL is signed/time-bounded (1 hour) and is only minted through the existing unlock route after authorization/payment/free-token verification.

### 5. Preview + unlocked PDF (`app/ai-tab/page.js`, `app/api/generate-tab-pdf/route.js`)
- Rhythm preview uses the signed private Blob preview URL directly when present.
- Full-PDF request sends the opaque artifact ID rather than resending the huge structured transcription.
- `/api/generate-tab-pdf` preserves existing PayPal/free-token unlock checks, validates the artifact ID, then signs the already-rendered private full PDF.
- Browser downloads the PDF directly from the signed Blob URL, avoiding the Vercel Function response-size boundary.
- Artifact-mode email contains the expiring private download URL rather than forcing a large PDF attachment through the function/mail response path.
- Lead/Bass and legacy non-artifact behavior remains unchanged.

## LARGE-FILE DEFENSIVE BOUNDS

- `lib/jimmyPaigeAnalysisPayload.js`: structured event cap raised 20,000 → 100,000.
- `lib/v143RenderContract.js`: render event cap raised 5,000 → 100,000.
- Audio metadata validation bound raised 1 GiB → 5 TiB so valid Blob metadata is not rejected solely by the old app bound.
- These are defensive application/render bounds, not a statement that the analyzer itself can process 5 TiB audio.

## WHAT “ANY SIZE” MEANS HERE

Do **not** claim literal infinity/unbounded audio.

Verified product transport behavior:
- old 50 MB DadRock application ceiling is gone;
- raw uploads use multipart private Blob transport;
- current Vercel Blob platform documentation allows multipart Blob objects up to the platform maximum (currently documented as 5 TB);
- large analyzer structures are rendered server-side instead of returned wholesale to the browser;
- large PDF bytes are served directly by signed private Blob URL instead of through a Vercel Function response.

Remaining finite constraints may include:
- browser/network/upload reliability and Vercel Blob account/platform quota;
- exact deployed Modal V143 worker source-download strategy and worker disk/RAM/GPU/runtime;
- ffmpeg decode behavior/duration;
- model segmentation/windowing/merging behavior;
- 100,000-event defensive structured/render limit;
- Vercel Function execution duration/memory while rendering a very large PDF;
- PDF renderer memory/page-count/resource behavior.

## REMAINING RUNTIME PROOF GAP

The exact source/deployment implementation of Modal app/function:
- app: `dadrock-v143-rhythm`
- function: `rhythm_v143_request`

has **not yet been located/pinned** in the repository during this continuation. `analyzer/v143_modal_http_endpoint.py` is the bridge to that function, not the full underlying worker implementation.

Therefore it is already proven that the **DadRock web transport + structured-result + PDF path no longer imposes the old small-file boundaries**, but it is not yet proven that the deployed analyzer worker can decode/process every large Blob that the storage layer can accept. Locate the worker implementation/deployment evidence before claiming analyzer-side arbitrary-duration support.

## SECURITY / RETENTION BOUNDARIES

- User source audio remains private Blob input.
- Full structured analyzer result remains in existing transient analyzer state until ACK/TTL; no persistent structured-result JSON cache was added.
- Persisted new artifacts are output PDFs only and are private.
- Signed artifact URLs are GET-only and time-bounded.
- Full PDF access remains behind existing unlock verification.
- No production Vercel deployment/promotion performed.
- No Deployment Protection weakening/disablement or bypass secret creation.
- No restricted GOAT assets accessed.
- No optimizer/training/model/scheduler/parameter mutation.
- No whole-branch merge to `main`.

## LIVE-RUN / BUDGET ACCOUNTING

- New V143 Rhythm real-audio/model starts used during this implementation: **0**.
- Previously authorized single `gomyway` V143 Rhythm start: **1 available / 0 consumed** unless a later explicit authorization supersedes it.
- Professional Rhythm-reference score passes used: **0**.
- New PDF artifact model invocation: **0** (PDF renderer is deterministic/non-model).
- Production promotion/change: **0**.
- Restricted GOAT access: **0**.

## IMMEDIATE NEXT STEPS FOR A FRESH CHAT

1. Re-read this checkpoint and verify current branch head.
2. Locate/pin authoritative deployed source or deployment evidence for `dadrock-v143-rhythm / rhythm_v143_request`.
3. Inspect its private Blob download path, whether it buffers the complete compressed/decompressed audio in RAM/disk, ffmpeg invocation, maximum duration/bytes, function timeout, ephemeral disk/RAM/GPU limits, model windowing/segmentation and merge behavior.
4. If worker contains avoidable whole-file/small-duration limits, make the narrowest worker-side change required to process large practical user recordings; do not mutate model/scheduler/parameters.
5. Add model-free/static regression checks around those worker limits where possible.
6. Save `CURRENT_STATE.md` before any live model-bearing validation.
7. Only after worker-side proof is complete, decide whether the existing explicitly authorized single `gomyway` Rhythm E2E run is useful as the one live validation. No retry/replacement run without new authorization.
8. No production promotion until explicitly authorized.

Current state: **WEB/UPLOAD/ASYNC-HANDOFF/PDF PATH IMPLEMENTED AND NEXT.JS BUILD GREEN. LIVE INFERENCE = 0. REMAINING WORK = PROVE/PATCH THE ACTUAL V143 RHYTHM WORKER'S LARGE-FILE DECODE/RUNTIME PATH.**
