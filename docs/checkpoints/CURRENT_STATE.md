# CURRENT STATE — DadRock `/ai-tab` V143 real-audio product canary

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Branch HEAD before this checkpoint update: `1666046a29b4e85d532dde3736a246c3a15c8a6d`

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

Active product goal:

> `dadrocktabs.com/ai-tab` uploaded user audio → Jimmy PAIge / V143 reference-free Rhythm analysis → authenticated measure/16th-step + pitch + string/fret events → branded professional tab PDF.

Keep this file updated after meaningful progress. Do not rely on chat history as the only recovery record.

Do **not** modify `main`, deploy/modify the live V143 endpoint, or enable production flags during this canary phase.

Historical compatibility research remains sealed. Do **not** launch another historical separator/GPU compatibility capture. Its conclusions remain:

```text
INTRO_CACHE_EXACT_COMPATIBLE
CURRENT_RESEARCH_FAMILY_A_COMPATIBLE
historicalProvenanceClosed: false
historicalIntroFamilyAuthenticated: false
productionPromotionAllowed: false
```

---

## Stable `/ai-tab` path already in place

`app/ai-tab/page.js` uploads permitted user audio to private Vercel Blob storage and calls `/api/analyze-audio-tab`.

`app/api/analyze-audio-tab/route.js` preserves the legacy analyzer for Lead/Bass and selects the separate V143 URL only for Rhythm when `ANALYZER_API_URL_V143` is configured. V143 identity remains fail-closed on:

```text
liveV143.referenceFree === true
```

`lib/v143RenderContract.js` accepts only events that already contain valid musical placement and playable note information:

```text
measure >= 1
step 0..15
stringIndex 0..5
fret 0..36
MIDI pitch
```

No browser/PDF code may manufacture missing measure/step placement.

Preview and final purchased PDF routes already receive the analyzer metadata/render events. PayPal/free-token verification and Resend delivery are unchanged.

Professional renderer feature gate remains default-off:

```text
JIMMY_PAIGE_PROFESSIONAL_PDF_V1 === "true"
```

No production environment variable has been enabled.

---

## Structured renderer itself is already proven

Existing synthetic structured-PDF fixture:

`debug/v143-contextual-prune/jimmy-paige-pdf-fixture/validation.json`

Validation commit:

`b40df94d76af3c6e432da0b8c20c723c298635a1`

Result:

```text
passed: true
raw/projected events: 40 / 40
measures: 28
fullPageCount: 2
previewPageCount: 2
```

It retained all 17 tested technique classes and passed PDF header, pagination, text extraction and raster checks. Therefore the remaining product blocker is real analyzer output quality, not PDF mechanics.

---

## V143 analyzer-output quality gate implemented

### Quality report

File:

`lib/v143AnalyzerQuality.js`

Initial commit:

`4542a9f15b09f0b6b9ce6980a908c7075b59a624`

Metrics include:

- reference-free identity;
- raw/considered event count;
- valid render-event count;
- render-event survival percentage;
- playable string/fret coverage;
- authenticated measure/step coverage;
- pitch validity coverage;
- measure range;
- 16th-step coverage;
- technique coverage;
- sustain coverage.

Current conservative canary eligibility thresholds:

```text
minimum valid render events: 4
minimum render-event survival: 70%
minimum playable string/fret coverage: 70%
minimum measure/step coverage: 70%
minimum pitch coverage: 70%
```

These thresholds are a canary floor, not a claim of final musical quality. Do not weaken them merely to get a pass.

Every report keeps:

```text
productionPromotionAuthorized: false
```

### Quality gate exposed and enforced at analyzer boundary

Commits:

- `5250c7629d428dcee3797ce946e81c68ffa2a4b6` — expose V143 analyzer quality metrics.
- `5655f0c6ddea6570c09dbe79e185fffdb65ab168` — gate structured engine identity on analyzer quality.
- `cf423f20f309cae810f8566141ec7ca8d64329a5` / `249316e0d5b7cecf7f5354d6acab3088a33309b2` — make modules directly testable.

A V143 Rhythm response gets the structured engine identity only when:

```text
referenceFree === true
analysisQuality.passed === true
renderEvents.length > 0
```

Passing:

```text
analysisEngine = v143-reference-free-rhythm
```

Insufficient/failing V143:

```text
analysisEngine = v143-reference-free-rhythm-fallback
```

The existing professional PDF bridge requires the exact passing engine identity, so low-quality V143 output can still keep its generated text tab and use the polished fallback renderer but cannot silently enter structured engraving.

### Regression verifier

`analyzer/verify_v143_analyzer_quality_gate.mjs`

Commit:

`490d64e8bc842f1ff48447f86a638c9dff2bc6dd`

Workflow:

`.github/workflows/v143-analyzer-quality-gate.yml`

Commit:

`a5b3ceb4998de7e96d62fa70ed11ef8e80cd749a`

Do not claim this new CI verifier passed until a concrete run/result is surfaced. Earlier connector status inspection did not expose the push-run result.

---

## Exact V143 product chain located on this branch

The branch contains the actual V143 Rhythm product modules even though ordinary code search initially missed some of them.

### `analyzer/v143_reference_free_rhythm_pipeline.py`

`analyze_reference_free_rhythm(...)`:

- estimates timing from normalized full mix;
- detects Rhythm candidates from selected separated stems;
- preserves the paired carrier-stem contract;
- runs frozen `V143ProductionEngine` scoring/selection;
- requires `v143Score`, `v143Rank`, `v143Selected` on every runtime row.

### `analyzer/v143_modal_rhythm_router.py`

Routes only Rhythm to V143. Lead/Bass remain delegated to the legacy analyzer. Rhythm then passes through event assembly and the output adapter.

### `analyzer/v143_rhythm_event_assembly.py`

Downstream-only assembly preserves frozen V143:

```text
measure
step
timeSeconds
dominantMidi
pitchHypotheses
v143Score
v143Rank
v143Selected
```

It then adds deterministic guitar mapping and evidence-derived sustain/technique metadata.

### `analyzer/v143_rhythm_guitar_note_mapper.py`

Analyzer-side deterministic standard-tuning mapping:

```text
stringIndex 0 = high e ... 5 = low E
open MIDI = 64,59,55,50,45,40
max fret = 24
```

It selects the lowest legal fret for the already-selected MIDI pitch. This is legitimate analyzer-side note mapping; it does not infer measure/step in the renderer.

### `analyzer/v143_rhythm_output_adapter.py`

Returns the product response with:

```text
generatedTab
tuning
tempo
timeSignature
techniques
events
noteCount
candidateCount
selectedCount
engineVersion = v143-reference-free-rhythm-output-v2
```

Those events contain the exact fields needed by `v143RenderContract`.

### `analyzer/v143_modal_live_endpoint.py`

Contains the existing L4 `rhythm_v143_request(payload)` product function and packages the V143 model/dependencies. It adds the authoritative V143 identity metadata:

```text
liveV143.version = 4
liveV143.modalGpu = L4
liveV143.rhythmOnly = true
liveV143.referenceFree = true
liveV143.separatorDeterministic = true
liveV143.separatorSeed = 143
liveV143.demucsShifts = 1
liveV143.professionalReferenceUsed = false
liveV143.runtimeLabelsRequired = false
```

**Do not deploy or modify this live endpoint during the canary.**

---

## Approved real-audio canary infrastructure discovered

Approved repository audio fixture already used by V143 tooling:

`public/gomywayfullaitest.m4a`

Existing isolated Modal workflow:

`.github/workflows/v143-contextual-prune-shadow-modal-smoke.yml`

Existing diagnostic:

`debug/v143-contextual-prune/shadow-modal-smoke.json`

Verified from that diagnostic:

```text
modalCredentialsAvailableInGitHubActions: true
smokeAttempted: true
smokeExitCode: 0
smokePassed: true
```

Therefore branch GitHub Actions already has working `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`; no analyzer API token or private Blob token needs to be added for the product canary.

The historical shadow app remains separate. Do not confuse its research carrier replay with this product canary.

---

## New isolated real-audio product-canary code committed

### 1. Modal product canary

File:

`analyzer/v143_ai_tab_product_canary_modal.py`

Commit:

`fc17f8e803e6dc15c00e3c9eeef89a75622e94c2` — `Add isolated V143 AI tab product canary`

New Modal app name:

`dadrock-v143-ai-tab-product-canary`

It reuses `rhythm_image` from the existing live endpoint but does **not** deploy or modify the live endpoint.

It is locked to:

`public/gomywayfullaitest.m4a`

It executes the same product chain:

- `process_vercel_audio_request`;
- legacy inspection/validation/normalization;
- deterministic Rhythm stem provider;
- `route_normalized_audio`;
- strict bend consensus;
- strict legato evidence;
- event assembly/string-fret mapping;
- V143 output adapter.

The only deliberate substitution is the Blob download callback: approved fixture bytes are written directly into the request adapter's temporary file. No private Blob URL/token is required.

The raw analyzer response is written only to ephemeral:

`.canary/v143-product-output.json`

and must **not** be committed.

### 2. Sanitized real-audio quality evaluator

File:

`analyzer/evaluate_v143_real_audio_canary.mjs`

Commit:

`0aa205a10fb1e9c9229f9b27fd2cf3fbdcdcced6` — `Add real-audio V143 quality evaluator`

It runs the raw product result through the exact web payload contract:

`buildJimmyPaigeAnalysisPayload(... usingV143RhythmAnalyzer: true)`

and writes only sanitized evidence to:

`debug/v143-contextual-prune/ai-tab-real-audio-canary.json`

The report contains quality metrics/counts/identity/routing/source SHA but not the raw generated tab, raw events, tokens or private URLs.

### 3. Exact-response professional PDF validator

File:

`analyzer/render_v143_real_audio_canary_pdf.mjs`

Commit:

`1666046a29b4e85d532dde3736a246c3a15c8a6d` — `Add exact-response V143 canary PDF validator`

If and only if the real analyzer quality gate passes, it sends the **same returned `renderEvents`** into `createV143RhythmPdf` for full and preview PDFs.

It writes PDF files only to ephemeral `.canary/` artifact storage and writes compact validation to:

`debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`

If analyzer quality fails, it records:

```text
attempted: false
passed: false
reason: analyzer-quality-gate-failed
```

rather than fabricating a structured PDF success.

The validator checks exact event count, maximum measure agreement, PDF headers, useful size, page count and full/preview distinction. Workflow-level text extraction/raster checks are still to be wired.

---

## Current state / blocker

The instrumentation and isolated canary programs are now present, but the new product canary has **not yet been run**.

No claim of a real-audio V143 pass should be made yet.

No live endpoint has been deployed/modified and no production flag has been changed.

---

## Next steps — execute automatically in this order

1. **Add branch-only GitHub Actions workflow** `.github/workflows/v143-ai-tab-real-audio-canary.yml`.
   - `workflow_dispatch` plus a one-time push trigger scoped to the new canary files/workflow;
   - explicit checkout of `v143-contextual-prune-lobo`;
   - use existing `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET`;
   - run the isolated product canary once on the approved audio fixture;
   - evaluate sanitized analyzer quality;
   - conditionally render exact-response full/preview PDFs without another GPU transcription run;
   - run generic PDF text extraction/raster checks;
   - upload raw analyzer/PDF/PNG evidence only as a short-retention Actions artifact;
   - commit only compact sanitized JSON validations.

2. **Inspect the concrete workflow run/jobs/logs** and distinguish infrastructure failure from musical-quality failure.

3. **If the analyzer gate passes**, require exact-response PDF structural/text/raster validation to pass before considering any preview renderer promotion.

4. **If the analyzer gate fails**, diagnose the actual missing field/coverage from `analysisQuality.failures`; do not weaken thresholds merely to make it green.

5. **After the bot commits compact evidence**, refresh this checkpoint with the exact run result and new branch HEAD.

6. Only after real-audio analyzer + exact-response PDF validation both pass should a separate decision be made about enabling `JIMMY_PAIGE_PROFESSIONAL_PDF_V1` in a Vercel **preview/canary** environment.

7. Do **not** enable production automatically.

---

## Non-negotiable boundaries

- Work only on `v143-contextual-prune-lobo`.
- Keep this checkpoint current after meaningful progress.
- Do not modify `main`.
- Do not deploy/modify `v143_modal_live_endpoint.py` during this canary.
- Do not run another historical fresh compatibility separator capture.
- Do not overwrite/delete preserved historical compatibility evidence.
- Do not retrain/replace frozen V143 merely to make the PDF gate pass.
- Do not manufacture measure/step data in browser/PDF code.
- Do not weaken analyzer-quality thresholds merely to produce a pass.
- Keep legacy Lead/Bass behavior unchanged.
- Keep polished PDF renderer as safe fallback.
- Keep `JIMMY_PAIGE_PROFESSIONAL_PDF_V1` default-off until explicitly promoted after canary validation.
- Keep production promotion disabled until a separate explicit decision.
