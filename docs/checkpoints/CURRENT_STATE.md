# CURRENT STATE — DadRock `/ai-tab` V143 Preview canary

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Branch HEAD before this checkpoint update: `a4555426ed3b7b16dfe68ffde50d2f7a8cfce9f9`

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

Active product goal:

> `dadrocktabs.com/ai-tab` uploaded user audio → Jimmy PAIge / V143 reference-free Rhythm analysis → authenticated musical events → professional structured tab PDF.

Keep this file updated after meaningful progress. Do not rely on chat history as the only recovery record.

Do **not** modify `main`, modify/deploy the live V143 Modal endpoint, or enable Production automatically.

Historical compatibility research remains sealed. Do not launch another historical separator/GPU compatibility capture. Historical conclusions remain:

```text
INTRO_CACHE_EXACT_COMPATIBLE
CURRENT_RESEARCH_FAMILY_A_COMPATIBLE
historicalProvenanceClosed: false
historicalIntroFamilyAuthenticated: false
productionPromotionAllowed: false
```

---

# 1. Stable application path

`app/ai-tab/page.js` uploads permitted user audio to private Vercel Blob storage and calls `/api/analyze-audio-tab`.

`app/api/analyze-audio-tab/route.js` preserves legacy Lead/Bass behavior and uses the separate V143 analyzer URL for Rhythm when configured.

V143 identity remains fail-closed on:

```text
liveV143.referenceFree === true
```

`lib/v143RenderContract.js` accepts only events that already contain valid:

```text
measure >= 1
step 0..15
stringIndex 0..5
fret 0..36
MIDI pitch
```

No browser/PDF layer may manufacture missing measure/step placement.

---

# 2. Analyzer quality gate

File:

`lib/v143AnalyzerQuality.js`

Current conservative eligibility floor:

```text
minimum valid render events: 4
minimum render-event survival: 70%
minimum playable string/fret coverage: 70%
minimum measure/step coverage: 70%
minimum pitch coverage: 70%
```

`lib/jimmyPaigeAnalysisPayload.js` exposes the report and only assigns:

```text
analysisEngine = v143-reference-free-rhythm
```

when:

```text
referenceFree === true
analysisQuality.passed === true
renderEvents.length > 0
```

Otherwise V143 is labeled:

```text
analysisEngine = v143-reference-free-rhythm-fallback
```

so it can still use the safe polished/text fallback but cannot silently enter structured engraving.

Every quality report keeps:

```text
productionPromotionAuthorized: false
```

Important commits:

- `4542a9f15b09f0b6b9ce6980a908c7075b59a624` — quality report.
- `5250c7629d428dcee3797ce946e81c68ffa2a4b6` — expose quality metrics.
- `5655f0c6ddea6570c09dbe79e185fffdb65ab168` — gate structured engine on quality.
- `490d64e8bc842f1ff48447f86a638c9dff2bc6dd` — regression verifier.
- `a5b3ceb4998de7e96d62fa70ed11ef8e80cd749a` — quality CI workflow.

---

# 3. Structured PDF renderer fixture passed

Evidence:

`debug/v143-contextual-prune/jimmy-paige-pdf-fixture/validation.json`

Commit:

`b40df94d76af3c6e432da0b8c20c723c298635a1`

Result:

```text
passed: true
raw/projected events: 40 / 40
measures: 28
fullPageCount: 2
previewPageCount: 2
```

The fixture retained all tested technique classes and passed structural/text/raster checks.

---

# 4. REAL-AUDIO V143 PRODUCT CANARY PASSED

Approved fixture:

`public/gomywayfullaitest.m4a`

Product canary components:

- `analyzer/v143_ai_tab_product_canary_modal.py`
- `analyzer/evaluate_v143_real_audio_canary.mjs`
- `analyzer/render_v143_real_audio_canary_pdf.mjs`
- `.github/workflows/v143-ai-tab-real-audio-canary.yml`

The canary uses the same V143 Rhythm product image/pipeline but bypasses private Blob networking by feeding the approved repository fixture bytes directly into the request adapter. It does not use a private Blob token and does not deploy/modify the live endpoint.

Bot evidence commit:

`9f52bf83597e921da12887874bace0df0ffe6d47` — `Record V143 AI tab real-audio canary`

## Analyzer evidence

`debug/v143-contextual-prune/ai-tab-real-audio-canary.json`

```text
passed: true
analysisEngine: v143-reference-free-rhythm
engineVersion: v143-reference-free-rhythm-output-v2
referenceFree: true
modalGpu: L4
professionalReferenceUsed: false
runtimeLabelsRequired: false
candidateCount: 1788
selectedCount: 358
rawEventCount: 358
validRenderEventCount: 358
renderEventSurvivalPercent: 100%
playableStringFretPercent: 100%
musicalPlacementPercent: 100%
pitchValidityPercent: 100%
first measure: 1
last measure: 113
unique measures: 112
16th-step coverage: all 0..15
technique events: 25 / 358
sustain coverage: 358 / 358
tempo: 129.19921875
meter: 4/4
tuning: E Standard
```

Techniques observed:

```text
bend
bend-release
hammer-on
pull-off
slide-down
slide-up
```

All analyzer-quality failures are empty.

## Exact-response PDF evidence

`debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`

The exact same 358 returned render events were passed to `createV143RhythmPdf`.

```text
attempted: true
passed: true
renderEventCount: 358
maximumMeasure: 113
fullPageCount: 4
previewPageCount: 4
fullPdfBytes: 1,686,104
previewPdfBytes: 1,678,626
```

All PDF structural checks, text extraction checks and page-one raster checks passed.

## Workflow evidence

`debug/v143-contextual-prune/ai-tab-real-audio-canary-action.json`

```text
modalCredentialsAvailableInGitHubActions: true
modalExitCode: 0
qualityEvaluatorExitCode: 0
pdfRendererExitCode: 0
pdfInspectionExitCode: 0
privateBlobTokenUsed: false
liveEndpointDeployedOrModified: false
productionModified: false
productionPromotionAuthorized: false
```

The previous real-analyzer/PDF blocker is therefore closed for this approved canary input.

---

# 5. Vercel audit completed

Connected Vercel project:

```text
project: dadrock-tabs-android
framework: Next.js
node: 24.x
```

Read-only deployment inspection on 2026-08-22 found the recent deployment history to be Production/main deployments only. The latest surfaced deployment was READY and targeted Production from `main`.

No existing deployment for `v143-contextual-prune-lobo` was present in the recent Vercel deployment list.

There was also no existing GitHub PR for `v143-contextual-prune-lobo`.

The connected Vercel tool surface available in this chat does not expose environment-variable mutation, so no Vercel environment setting was changed.

**Production remains untouched.**

---

# 6. Preview-only professional renderer activation implemented

Rather than mutate any Production/Preview environment variable, this branch now contains a self-limiting feature-state helper:

`lib/jimmyPaigeProfessionalPdfFeature.js`

Commit:

`ef91510f92e34292e86200edc7f319f5c10dc838` — `Add Preview-only Jimmy PAIge renderer gate`

The helper preserves the existing explicit flag:

```text
JIMMY_PAIGE_PROFESSIONAL_PDF_V1=true
```

but also enables the professional renderer automatically only when **both** are true:

```text
VERCEL_ENV === preview
VERCEL_GIT_COMMIT_REF === v143-contextual-prune-lobo
```

Therefore:

- Production on this branch does not auto-enable it;
- other Preview branches do not auto-enable it;
- this exact branch Preview does enable it;
- the existing explicit environment flag behavior remains intact;
- `productionPromotionAuthorized` remains false.

The helper is now used by both:

- `app/api/generate-tab-preview/route.js`
- `app/api/generate-tab-pdf/route.js`

Commits:

- `54fc2da9d7181ad55752d81dffc4a690778f6e7f` — Preview PDF route uses branch Preview gate and returns `X-Jimmy-PAIge-PDF-Feature` header.
- `a51dba8d773f4939bec1d50b9b41dd229913f43a` — final PDF route uses the same gate.

No payment/email test has been performed and none should be performed automatically.

---

# 7. Preview gate regression verification added

Verifier:

`analyzer/verify_jimmy_paige_preview_feature_gate.mjs`

Commit:

`4651a0f5cd7c5ffc0b909d0480de2308713d7773`

It asserts:

- default disabled;
- Production + canary branch remains disabled;
- Preview + wrong branch remains disabled;
- Preview + exact canary branch enables professional renderer;
- existing explicit flag still works;
- production promotion remains unauthorized.

Workflow:

`.github/workflows/v143-preview-pdf-feature-gate.yml`

Commit:

`a4555426ed3b7b16dfe68ffde50d2f7a8cfce9f9`

Do not claim this verifier passed until a concrete workflow result/evidence is surfaced.

These changes do not match the real-audio GPU workflow path filter, so they should not retrigger the expensive real-audio transcription canary.

---

# Current boundary

The next task is to create a Vercel Preview deployment for this branch without touching Production.

The normal Git integration has not created a branch Preview from branch pushes alone. There is currently no PR for this branch.

The preferred next move is a **draft PR** from:

```text
v143-contextual-prune-lobo -> main
```

for Preview generation/testing only. Do not merge it automatically.

---

# Next steps — execute automatically in this order

1. Inspect the Preview gate CI result if it surfaces; fix only genuine gate/build issues.

2. Open a **draft PR** from `v143-contextual-prune-lobo` to `main` with explicit wording that it is a Preview canary and must not be merged during validation.

3. Inspect Vercel deployments until a deployment appears with:

```text
githubCommitRef = v143-contextual-prune-lobo
target = preview
```

4. Verify Preview build health/logs. If Vercel does not create a PR Preview automatically, investigate Git integration/build-ignore settings before using any manual deployment mechanism.

5. Verify the Preview page `/ai-tab` loads.

6. Verify server-safe Preview PDF behavior without purchase/email:
   - POST the preview endpoint only;
   - confirm `X-Jimmy-PAIge-PDF-Feature = v143-branch-preview-canary`;
   - confirm valid V143 events select `v143-structured-rhythm`;
   - confirm legacy/failed structured data falls back safely.

7. Prefer using already-preserved fixture/analyzer evidence for route-level renderer testing; do not rerun the GPU analyzer unless actual uploaded-audio browser routing must be verified and no cheaper exact-contract path is sufficient.

8. Do not make a PayPal purchase, redeem a customer token, or send customer email during automated Preview testing.

9. Record compact Preview evidence under `debug/v143-contextual-prune/` and refresh this checkpoint.

10. Only after Preview application wiring passes should a separate explicit Production-promotion decision be made.

11. Do **not** enable or promote Production automatically.

---

# Non-negotiable boundaries

- Work only on `v143-contextual-prune-lobo`.
- Keep this checkpoint current after meaningful progress.
- Do not modify `main`.
- Do not merge the Preview-canary PR automatically.
- Do not deploy/modify the live V143 Modal endpoint during Preview validation unless a separate explicit need is proven.
- Do not rerun historical compatibility captures.
- Do not overwrite/delete preserved compatibility evidence.
- Do not retrain/replace frozen V143 merely to make a gate pass.
- Do not manufacture measure/step data in browser/PDF code.
- Do not weaken analyzer-quality thresholds merely to produce a pass.
- Keep legacy Lead/Bass behavior unchanged.
- Keep polished PDF rendering as the safe fallback.
- Any automatic professional renderer activation before Production approval must remain Preview-only and branch-scoped.
- Keep Production promotion disabled until a separate explicit decision.
