# CURRENT STATE — DadRock `/ai-tab` V143 Preview canary

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Branch HEAD before this checkpoint update: `8c6a30ff1005ea16f4a9c4d701d241b606f98901`

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

Active product goal:

> `dadrocktabs.com/ai-tab` uploaded user audio → Jimmy PAIge / V143 reference-free Rhythm analysis → authenticated musical events → professional structured tab PDF.

Keep this file updated after meaningful progress. Do not rely on chat history as the only recovery record.

Do **not** modify `main`, modify/deploy the live V143 Modal endpoint, merge the research branch, or enable/promote Production automatically.

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

Required runtime keys for a real uploaded-audio V143 Rhythm request are:

```text
ANALYZER_API_URL_V143
ANALYZER_API_TOKEN
BLOB_READ_WRITE_TOKEN
```

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

`lib/v143AnalyzerQuality.js` defines the current conservative eligibility floor:

```text
minimum valid render events: 4
minimum render-event survival: 70%
minimum playable string/fret coverage: 70%
minimum measure/step coverage: 70%
minimum pitch coverage: 70%
```

`lib/jimmyPaigeAnalysisPayload.js` exposes the report and assigns:

```text
analysisEngine = v143-reference-free-rhythm
```

only when:

```text
referenceFree === true
analysisQuality.passed === true
renderEvents.length > 0
```

Otherwise V143 is labeled:

```text
analysisEngine = v143-reference-free-rhythm-fallback
```

so safe polished/text fallback remains available while weak V143 output cannot silently enter structured engraving.

Every quality report keeps:

```text
productionPromotionAuthorized: false
```

Important commits:

- `4542a9f15b09f0b6b9ce6980a908c7075b59a624` — quality report.
- `5250c7629d428dcee3797ce946e81c68ffa2a4b6` — expose quality metrics.
- `5655f0c6ddea6570c09dbe79e185fffdb65ab168` — gate structured engine on quality.
- `490d64e8bc842f1ff48447f86a638c9dff2bc6dd` — analyzer-quality regression verifier.
- `a5b3ceb4998de7e96d62fa70ed11ef8e80cd749a` — analyzer-quality CI workflow.

---

# 3. Structured renderer fixture passed

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

The synthetic fixture retained all tested technique classes and passed structural/text/raster checks.

---

# 4. REAL-AUDIO V143 PRODUCT CANARY PASSED

Approved fixture:

`public/gomywayfullaitest.m4a`

Product canary components:

- `analyzer/v143_ai_tab_product_canary_modal.py`
- `analyzer/evaluate_v143_real_audio_canary.mjs`
- `analyzer/render_v143_real_audio_canary_pdf.mjs`
- `.github/workflows/v143-ai-tab-real-audio-canary.yml`

The canary uses the same V143 Rhythm product image/pipeline but bypasses private Blob networking by feeding approved fixture bytes directly into the request adapter. It uses no private Blob token and does not deploy/modify the live endpoint.

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

The previous real-analyzer/PDF blocker is closed for this approved canary input.

---

# 5. Preview-only professional renderer gate implemented

Helper:

`lib/jimmyPaigeProfessionalPdfFeature.js`

Commit:

`ef91510f92e34292e86200edc7f319f5c10dc838`

The helper preserves the existing explicit flag:

```text
JIMMY_PAIGE_PROFESSIONAL_PDF_V1=true
```

and also auto-enables only when both are true:

```text
VERCEL_ENV === preview
VERCEL_GIT_COMMIT_REF === v143-contextual-prune-lobo
```

Therefore:

- Production on this branch does not auto-enable it;
- other Preview branches do not auto-enable it;
- this exact branch Preview does enable it;
- explicit env-flag behavior remains intact;
- `productionPromotionAuthorized` remains false.

Used by:

- `app/api/generate-tab-preview/route.js`
- `app/api/generate-tab-pdf/route.js`

Route commits:

- `54fc2da9d7181ad55752d81dffc4a690778f6e7f` — preview route uses feature helper and returns `X-Jimmy-PAIge-PDF-Feature`.
- `a51dba8d773f4939bec1d50b9b41dd229913f43a` — final PDF route uses same helper.

Preview gate verifier:

`analyzer/verify_jimmy_paige_preview_feature_gate.mjs`

Commit:

`4651a0f5cd7c5ffc0b909d0480de2308713d7773`

Workflow:

`.github/workflows/v143-preview-pdf-feature-gate.yml`

Commit:

`a4555426ed3b7b16dfe68ffde50d2f7a8cfce9f9`

Do not claim that workflow passed until concrete execution evidence is surfaced.

No payment, customer-token redemption, or customer-email test has been performed.

---

# 6. Vercel Preview audit and deployment attempts

Connected Vercel project:

```text
project: dadrock-tabs-android
projectId: prj_6biwsn0iHci6FHNswAUCS8UYrAqF
teamId: team_qJrw8Cuze5bCEg9M3Q67XMWt
framework: Next.js
node: 24.x
```

Read-only deployment inspection on 2026-08-22 showed recent deployments were Production/main only. No `v143-contextual-prune-lobo` Preview deployment appeared after ordinary branch pushes.

The connected Vercel tool can list/inspect deployments and logs, but its direct deploy action does not accept a source ref/branch. **Do not use that action for this canary because the exact source branch cannot be guaranteed.**

The connected Vercel tool surface exposed here also does not expose environment-variable writes or an env-list action, so project envs were not changed.

Production remains untouched.

---

# 7. Draft PR Preview experiment was safely closed

Draft PR #19 was created only to test whether native Git→Vercel Preview integration would react:

`V143 /ai-tab professional PDF Preview canary`

It was explicitly marked DO NOT MERGE.

Vercel did not surface a Preview deployment from the PR.

The PR was also an unsuitable merge vehicle because the long-lived research branch is enormous relative to current `main` (thousands of changed files and thousands of commits).

PR #19 was therefore closed unmerged on 2026-08-22 after it failed to trigger a Preview.

Current PR state:

```text
state: closed
draft: true
merged: false
```

Do not reopen it merely to obtain a Preview unless the Git integration behavior changes and a specific need is proven.

---

# 8. Explicit GitHub Actions Vercel Preview workflow is ready, but blocked by missing VERCEL_TOKEN

Workflow:

`.github/workflows/v143-vercel-preview-deploy.yml`

Commit:

`7a5c5f0b4aac01d0bf28f326fdf7313473fac84f` — `Add isolated V143 Vercel Preview deploy workflow`

The workflow is branch-only and fail-closed. It is designed to:

1. check whether `VERCEL_TOKEN` exists without printing it;
2. target the known project/team IDs;
3. run `vercel pull --environment=preview`;
4. check only the presence (never values) of:
   - `ANALYZER_API_URL_V143`
   - `ANALYZER_API_TOKEN`
   - `BLOB_READ_WRITE_TOKEN`;
5. run `vercel build`;
6. deploy the prebuilt output with **no `--prod`**;
7. set `JIMMY_PAIGE_PROFESSIONAL_PDF_V1=true` only via deployment-scoped `--env`;
8. commit only compact non-secret evidence;
9. never perform payment/token/email actions.

Bot diagnostic commit:

`8c6a30ff1005ea16f4a9c4d701d241b606f98901` — `Record V143 Vercel Preview deployment`

Evidence:

`debug/v143-contextual-prune/vercel-preview-deploy-action.json`

Actual result:

```text
vercelTokenAvailableInGitHubActions: false
previewConfigPullExitCode: 99
previewBuildExitCode: 99
previewDeployExitCode: 99
deploymentUrl: null
deploymentRequestedAsPreview: true
productionDeployFlagUsed: false
professionalRendererDeploymentScoped: true
projectEnvironmentMutated: false
productionModified: false
productionPromotionAuthorized: false
paidPurchaseAttempted: false
customerTokenRedeemed: false
customerEmailSent: false
```

The Preview environment-presence booleans are false only because Preview configuration could not be pulled without `VERCEL_TOKEN`; they do **not** prove those Vercel project env vars are actually absent.

## Precise current external blocker

GitHub Actions does not currently have a repository secret named:

```text
VERCEL_TOKEN
```

Without that token, the branch can neither pull the Vercel Preview configuration nor create a CLI Preview deployment from CI.

No unsafe fallback was used. No Production change occurred.

---

# Current boundary

The core V143 product path is already proven with real audio and exact-response professional PDFs.

The only unresolved validation boundary is the real Vercel/Next.js Preview application wiring.

That boundary is currently blocked by deployment authentication, **not** by the analyzer, render contract, PDF renderer, or V143 event quality.

---

# Next steps — execute automatically when the deployment credential boundary is available

1. If a `VERCEL_TOKEN` repository secret becomes available, rerun `.github/workflows/v143-vercel-preview-deploy.yml` without changing its Preview-only safety invariants.

2. Require the deployment diagnostic to show:

```text
vercelTokenAvailableInGitHubActions: true
previewConfigPullExitCode: 0
previewBuildExitCode: 0
previewDeployExitCode: 0
deploymentUrl: non-null
productionDeployFlagUsed: false
productionModified: false
```

3. Inspect the resulting deployment through the connected Vercel app and independently confirm target/environment is Preview before sending application requests.

4. Verify `/ai-tab` loads on that Preview.

5. POST only `/api/generate-tab-preview` for renderer routing validation; do not use `/api/generate-tab-pdf` because that path performs payment/free-token verification and can send email.

6. For a passing structured route test, use already-approved synthetic/fixture V143 render events. Do not rerun the GPU analyzer merely to test the Preview PDF route.

7. Confirm Preview response headers:

```text
X-Jimmy-PAIge-PDF-Feature: enabled source
X-Jimmy-PAIge-PDF-Renderer: v143-structured-rhythm
```

8. Send a legacy/invalid-structured preview request and require safe polished fallback.

9. Only if route-level testing passes and the Preview has the required V143/Blob runtime keys should an actual browser upload test using `public/gomywayfullaitest.m4a` be considered.

10. Do not make a PayPal purchase, redeem a customer token, or send customer email during automated Preview testing.

11. Record compact Preview evidence under `debug/v143-contextual-prune/` and refresh this checkpoint.

12. Only after Preview application wiring passes should a separate explicit Production-promotion decision be made.

13. Do **not** enable or promote Production automatically.

---

# Non-negotiable boundaries

- Work only on `v143-contextual-prune-lobo`.
- Keep this checkpoint current after meaningful progress.
- Do not modify `main`.
- Do not merge the long-lived research branch into `main`.
- Do not deploy an unspecified Vercel source just to obtain a Preview URL.
- Do not deploy/modify the live V143 Modal endpoint during Preview validation unless a separate explicit need is proven.
- Do not rerun historical compatibility captures.
- Do not overwrite/delete preserved compatibility evidence.
- Do not retrain/replace frozen V143 merely to make a gate pass.
- Do not manufacture measure/step data in browser/PDF code.
- Do not weaken analyzer-quality thresholds merely to produce a pass.
- Keep legacy Lead/Bass behavior unchanged.
- Keep polished PDF rendering as the safe fallback.
- Any automatic professional renderer activation before Production approval must remain Preview-only and branch/deployment-scoped.
- Keep Production promotion disabled until a separate explicit decision.
