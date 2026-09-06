# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — **LARGE PRACTICAL USER UPLOAD → V143 RHYTHM → PRIVATE PDF ARTIFACT FLOW IMPLEMENTED; COMPILE VALIDATION NEXT.**  
Branch: `v143-contextual-prune-lobo`

> Latest user requirement is the real product path, not a fixture-only test: a user uploads their chosen supported audio at `/ai-tab`, selects **Rhythm Guitar**, the current V143 async analyzer runs exactly once, and the same completed structured result is rendered into the preview/full PDFs used by `app/ai-tab/page.js`. No second analyzer invocation is permitted for PDF generation.

## CURRENT IMPLEMENTATION STATE

- Product implementation commit: `17397dfae18b56dcb13b9bd7291618dcf5357c6f` (`feat: scale Rhythm upload to PDF artifact flow`).
- Model-free patch/regression workflow run: `34006234785`, job `101413830044` — GREEN for checkout, exact patch, regression assertions, diff check and commit.
- No live/model-bearing audio inference was performed by that workflow.
- Current product changes:
  - `app/ai-tab/page.js`
    - user audio upload now explicitly uses Vercel Blob `multipart: true`;
    - Rhythm status polling requests compact `delivery: 'pdf-artifacts'` and carries song/artist metadata;
    - preview consumes a signed private Blob preview URL when supplied;
    - full PDF request carries only the artifact ID plus the existing unlock metadata/compact tab metadata;
    - when the unlock route returns a signed Blob URL, the browser downloads the PDF directly from Blob instead of forcing PDF bytes through a Vercel Function response.
  - `app/api/audio-upload/route.js`
    - removed the old application-level 50 MB maximum;
    - content-type/copyright/instrument validation remains;
    - raw audio continues browser → private Vercel Blob rather than through a Vercel Function request body.
  - `app/api/analyze-audio-tab/route.js`
    - after the same V143 async token reaches `completed`, the full structured result is passed server-side to the deterministic PDF artifact renderer when `delivery === 'pdf-artifacts'`;
    - only compact metadata + `pdfArtifact` is returned to the browser;
    - page still ACKs the same analyzer token afterward so transient analyzer state is cleared/TTL-bounded;
    - no second model/analyzer start was added.
  - `lib/v143RhythmPdfArtifacts.js` (new)
    - deterministically renders preview + full PDF from the already-completed V143 structured result using `createJimmyPaigeProfessionalPdf`;
    - stores both PDFs as **private** Vercel Blob artifacts under a random UUID capability path;
    - mints GET-only time-bounded signed URLs;
    - preview signed URL lifetime = 6 hours; full download signed URL lifetime = 1 hour;
    - helper contains no analyzer/API model invocation.
  - `app/api/generate-tab-pdf/route.js`
    - preserves existing PayPal/free-token unlock verification;
    - for Rhythm PDF artifacts, validates the UUID artifact reference only after unlock verification, signs the existing private full PDF, emails a private expiring download link, and returns compact JSON containing the signed URL;
    - legacy Lead/Bass/non-artifact behavior remains unchanged.
  - `lib/jimmyPaigeAnalysisPayload.js`
    - structured event defensive cap raised from 20,000 to 100,000;
    - audio metadata file-size bound raised from 1 GiB to 5 TiB.
  - `lib/v143RenderContract.js`
    - structured Rhythm render-event defensive cap raised from 5,000 to 100,000.
  - `.github/scripts/v143-large-rhythm-pipeline-regression.mjs` (new)
    - model-free assertions prove multipart upload, removal of 50 MB cap, compact artifact status path, signed preview/full downloads, private GET-only artifact handling, deterministic renderer use, no analyzer call in PDF helper, and raised structured-event caps.

## PLATFORM BOUNDARIES / DEFINITION OF “ANY SIZE”

- Do **not** claim literally unlimited bytes.
- The application-level 50 MB ceiling has been removed.
- Vercel Blob multipart upload is the raw-audio transport, so the large audio bytes do not cross the Vercel Function 4.5 MB request/response body boundary.
- Vercel Blob currently supports multipart objects up to its platform limit (official Vercel documentation currently states up to 5 TB).
- The large structured V143 result is kept server-side for PDF rendering; it no longer needs to cross the browser/Vercel Function JSON response boundary.
- The large finished PDF is downloaded browser ← signed private Blob; it no longer needs to cross the Vercel Function PDF response boundary.
- Remaining finite limits can still come from browser/network conditions, Blob quotas, Modal worker download/decode/runtime/memory, ffmpeg, the 100,000-event defensive product/render caps, Vercel Function execution duration/memory during artifact rendering, and PDF renderer resource use.
- The exact deployed `dadrock-v143-rhythm / rhythm_v143_request` worker source has not yet been located in this repository, so its own full-file duration/memory/decode ceiling is **not yet proven**. Do not state that arbitrary 5 TB audio can actually be analyzed by the model merely because Blob can store it.

## SECURITY / RETENTION BOUNDARIES

- User source audio remains private Blob input.
- Full structured analyzer result remains in existing transient analyzer state until ACK/TTL; no persistent structured-result JSON cache was added.
- Persisted artifacts are output PDFs only, stored private; direct access requires short-lived signed GET URLs.
- Full PDF URL is minted only after the existing unlock check.
- No production deployment/promotion has been performed.
- No Deployment Protection weakening/disablement or bypass secret was created.
- No restricted GOAT assets accessed.
- No optimizer/training/model/scheduler/parameter mutation.
- No whole-branch merge to `main`.

## LIVE-RUN / BUDGET ACCOUNTING

- New V143 Rhythm real-audio/model starts used during this implementation: **0**.
- Previously authorized `gomyway` single Rhythm start remains **1 available / 0 consumed** unless superseded by a later explicit user authorization.
- Professional reference scoring passes used: **0**.
- Production promotion/change: **0**.
- Restricted GOAT access: **0**.

## IMMEDIATE NEXT STEPS

1. Run a model-free Next.js compile/build validation against commit `17397dfae18b56dcb13b9bd7291618dcf5357c6f` (or its checkpoint descendant) to catch JSX/import/API-contract compile errors. Do **not** start the analyzer/model.
2. If compile validation fails, inspect the exact error and make the smallest code-only correction; rerun only model-free validation.
3. Verify the exact current `@vercel/blob` signed URL API usage (`issueSignedToken` + `presignUrl`) against installed `@vercel/blob` 2.6.1 / official docs; current implementation follows the 2026 signed-URL contract.
4. Inspect/locate authoritative source or deployment evidence for the Modal worker `dadrock-v143-rhythm` function `rhythm_v143_request`, specifically its private Blob download/decode approach, whole-file buffering, ffmpeg behavior, duration assumptions, GPU/model segmentation, and runtime/memory limits. This is the remaining evidence needed before claiming the analyzer itself handles arbitrarily long files.
5. Remove temporary one-shot patch machinery (`.github/workflows/v143-large-rhythm-pdf-pipeline.yml` and `.github/scripts/apply-v143-large-rhythm-pipeline.py`) after validation; retain the permanent regression script.
6. Save `CURRENT_STATE.md` again with compile result, exact final head and any remaining runtime limitation.
7. Do not consume a real/model-bearing Rhythm run until model-free verification is complete and the checkpoint is saved immediately beforehand.

Current state: **IMPLEMENTED / MODEL-FREE REGRESSION GREEN / COMPILE VALIDATION PENDING. Live inference consumed = 0.**
