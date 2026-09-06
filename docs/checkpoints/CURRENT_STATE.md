# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — **PRE-CONSUMPTION GATE GREEN; ONE-SHOT LIVE RUN STILL UNCONSUMED.**  
Branch: `v143-contextual-prune-lobo`

## AUTHORIZED NEXT ACTION

User explicitly asked to make the one-shot `gomyway` Rhythm E2E work and run it. Do not ask for authorization again. Exactly one backend/model-bearing Rhythm start is authorized. If that start or job fails, STOP: no retry or replacement run.

Pre-consumption branch head verified immediately before this checkpoint: `a1fad9a019517e58f753f8f681a0c35609852566`.

## BUDGET — PRE-CONSUMPTION

- Current-V143 `gomyway` Rhythm live/model-bearing starts: **1 available / 0 consumed**.
- Professional full-1–113 scoring passes: **1 available / 0 consumed**.
- PDF E2E: **0 performed**.
- Lead/Bass model runs: **not authorized**.
- Retry/replacement live run: **not authorized**.

## PINNED INPUT / LIVE PATH

- Approved audio: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Approved audio Git blob: `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- One-shot helper: `.github/scripts/v143-existing-preview-async-breakthrough-e2e.sh`
- Helper blob: `433599afec7fff20a31ea79e4c93ef9a6da03b36`
- Analyzer route: `app/api/analyze-audio-tab/route.js`
- Route blob: `a3d02876d2c4efeb6f5258586046bc95cfc132b6`
- Async bridge: `analyzer/v143_modal_http_endpoint.py`
- Bridge blob: `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- Fixed bridge worker: Modal app `dadrock-v143-ai-tab-live`, function `rhythm_v143_request`
- Live worker source: `analyzer/v143_modal_live_endpoint.py`
- Deterministic separator source: `analyzer/v143_seeded_separator.py`
- Repaired bridge commit: `62deec179531b0f3e67c0e833365c2274697f02d`
- Bridge validation: workflow run `34000667026`, job `101398830737` — GREEN
- Model-free large Rhythm regression: workflow run `34006234785`, job `101413830044` — GREEN
- Next.js production build: workflow run `34006290464`, job `101413989631` — GREEN

### Live-run safety proof

Inspection of the pinned helper proves:
- exactly one JSON request with `operation: "start"` is constructed and sent;
- after that request, the helper only emits `operation: "status"` using the same returned signed `jobToken`, then `operation: "ack"` for that same token;
- poll transport errors only continue same-token polling and never issue another start;
- unusable start response, terminal failure, or polling deadline exits with an explicit STOP/no-second-start path;
- the helper does not train, optimize, sweep thresholds, mutate model parameters, deploy production, or promote production.

Inspection of the pinned bridge proves:
- Rhythm start spawns one `run_rhythm_async_job` orchestrator;
- that orchestrator performs one `_worker_handle().remote(...)` call;
- `_worker_handle()` is fixed to `dadrock-v143-ai-tab-live / rhythm_v143_request`;
- status uses the signed job ID plus the stored single Modal FunctionCall ID and reads the same transient result partition;
- ACK/cleanup clears the same tracked job state; it does not invoke the model.

Inspection of `analyzer/v143_modal_live_endpoint.py` confirms `rhythm_v143_request` is the deterministic reference-free Rhythm request path and reports `professionalReferenceUsed: false`, `referenceRuntimeInputUsed: false`, deterministic separator seed 143 and Demucs shifts 1.

## PINNED FULL PROFESSIONAL RHYTHM REFERENCE — 1–113

Authoritative preserved machine-readable reference:
- Path: `research/v154-professional-references/rhythm-professional-reference.json`
- Git blob: `248741bade9665a34648c59a2994bd27d73fc406`
- SHA-256: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- Schema flags: `completeReference: true`, `holdout: true`, `instrument: rhythm`
- Coverage: measures **1–113**, 113 stored measure objects
- Professional playable onset/event count: **603**
- Professional note count: **946**
- Populated professional measures: **104**
- Event fields include 16-step `step` timing and notes with `midi`, `stringIndex`, and `fret`; optional source fields handled by the scorer include duration, technique labels, ties and rests.

Pinned provenance:
- `research/v154-professional-references/rhythm-professional-reference-provenance.json`
- Source machine-readable reference: `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json`
- Source professional image: `public/Professionalexample.jpg`
- Source image Git blob: `16106197cc1269cca0b3c443908d5ef75e8b4d3e`
- Historical immutable scorer-only recovery pinned `Professionalexample.jpg` at commit `e0f91e74c815b9ecdf0a72fae6d1523414b34577`.
- Preservation provenance states the research copy is byte-identical to the source machine-readable reference and no candidate/model/production modification or reference-facing score occurred during preservation.

Scorer-ready identity:
- `research/v154-professional-references/rhythm-professional-reference-scorer-ready.json`
- Scorer-ready SHA-256: `d6c9416979f25e6a81b9cd4583389b584a59421a0529fcccb4ca6f5dd47e679f`
- 946 rows, measures 1–113, steps 0–15, MIDI 40–71
- Equivalence audit: exact normalized row multiset equivalence PASS.

Partial files remain excluded from the reserved final score:
- `public/gomyway-professional-rhythm-reference-v2.json` — only measures 1–16.
- `public/gomyway-professional-rhythm-reference-17-113.json` — partial fallback.
- `public/jimmy-paige-midterm-v1/jimmy-midterm-113-measure-paper-v1.json` — blind/paper candidate, not the professional answer key.

## PINNED DETERMINISTIC PROFESSIONAL SCORER

- Scorer: `validation/rhythm_holdout/score_rhythm_holdout.py`
- Scorer Git blob: `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- Completeness verifier: `validation/rhythm_holdout/verify_reference_completeness.py`
- Completeness verifier blob: `2504581dd72b6c375fbc0b68d4d396fce58deb87`
- Canonicalizer: `validation/rhythm_holdout/canonical.py`
- Canonicalizer blob: `088d44827fb23e20d9aeeb4944a672989af5846c`
- Default final threshold: 0.99; onset tolerance 0.50 step; gross tolerance 2.00 steps; duration tolerance 0.25 step.
- The scorer validates anti-leakage, frozen event hash and exact PDF event identity before opening the professional reference; it is post-hoc only and does not write corrections into analyzer output.
- Supported scoring includes pitch/note identity, string+fret/voicing identity, onset/measure-step timing, measure coverage, false positives/extras, false negatives/misses, duration where both schemas contain comparable duration, and technique labels where encoded.
- Current V143 generated schema does not explicitly carry rest/tie flags; do not invent those results. Report them as not scoreable from current generated schema where appropriate.

## PINNED PDF PATH / NO SECOND ANALYZER PROOF

- `lib/v143RhythmPdfArtifacts.js` blob `dab369ddce19abeb3b4e27d801f8bc0a2e8ab60b`
- `lib/createJimmyPaigeProfessionalPdf.js` blob `b1e587b24c38f005294aa5ea960ce9bd9b79724c`
- `app/api/generate-tab-pdf/route.js` blob `5137831c262e79fe673249dcc8d71ac43efa95e9`

Inspection proves the Rhythm artifact builder takes an already-completed `completedPayload`, requires `analysisEngine === "v143-reference-free-rhythm"`, passes that payload's `renderEvents`/measure grid/metadata to the deterministic renderer, and creates preview/full PDFs. `createJimmyPaigeProfessionalPdf` validates the exact structured event stream and renders it; it has no analyzer/model invocation. The download route signs or renders PDF artifacts and likewise contains no analyzer call.

## EXECUTION SEQUENCE FROM HERE

1. Resolve and pin the exact existing Vercel Preview deployment/source commit/environment values required by the helper; do not deploy or promote production.
2. Run only model-free preview identity + invalid-type preflight.
3. Issue exactly one `operation:start` for the approved `gomyway` Rhythm audio. **At the instant it is issued, live budget becomes 1 consumed / 0 available.**
4. Poll only the same returned job token / same Modal FunctionCall until terminal. No second start.
5. If terminal result is valid, capture the same completed structured result before ACK.
6. Freeze/normalize that same result deterministically for the holdout scorer and PDF identity gate; no analyzer invocation.
7. Run exactly one professional scoring pass using the full 1–113 professional reference.
8. Generate/validate preview + full PDF from the exact same completed structured result; no analyzer invocation.
9. ACK/clear the same analyzer job after bounded structured evidence is captured.
10. Save FINAL state here with all IDs, score, PDF result, cleanup state and budget counters; return to HOLD.

## HARD STOPS

- No second Rhythm live start.
- No second professional score pass.
- No Lead/Bass model run.
- No optimizer/training/threshold sweep/scheduler/model/parameter mutation.
- No second analyzer invocation for PDF.
- No production Vercel deployment/promotion/change.
- No Deployment Protection weakening/bypass secret creation.
- No raw audio/stems/model bytes retained.
- Never rerun workflow runs `33999777841`, `33999522733`, or `33998283085`.

Current state: **PRE-CONSUMPTION GATE GREEN. Live = 0 consumed; professional score = 0 consumed; PDF E2E = 0 performed. Next: resolve the existing Preview target, then send the single authorized start.**
