# CURRENT STATE — DadRock `/ai-tab` V143 Preview canary

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Branch HEAD before this checkpoint update: `4f2b637ce5f2b69c4dfff07d26cac9f68fcc59d1`

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

Active product goal:

> `dadrocktabs.com/ai-tab` uploaded user audio → Jimmy PAIge / V143 reference-free Rhythm analysis → authenticated musical events → professional structured tab PDF.

Keep this file updated after meaningful progress. Do not rely on chat history as the only recovery record.

Do **not** modify `main`, modify/deploy the live V143 Modal endpoint, merge the long-lived research branch, or enable/promote Production automatically.

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

`lib/v143RenderContract.js` accepts only events containing valid:

```text
measure >= 1
step 0..15
stringIndex 0..5
fret 0..36
MIDI pitch
```

No browser/PDF layer may manufacture missing measure/step placement.

Browser metadata transport has been reviewed and verified: the browser clears stale `analysisMetadata` at the start of each new generation, stores the fresh analyzer response, and transports that same response's engine/render/grid/tuning/tempo/meter/key/technique/confidence/difficulty metadata to preview and unlocked full-PDF routes.

---

# 2. Analyzer quality gate

`lib/v143AnalyzerQuality.js` currently requires:

```text
minimum valid render events: 4
minimum render-event survival: 70%
minimum playable string/fret coverage: 70%
minimum measure/step coverage: 70%
minimum pitch coverage: 70%
```

`lib/jimmyPaigeAnalysisPayload.js` exposes:

```text
analysisEngine = v143-reference-free-rhythm
```

only when:

```text
referenceFree === true
analysisQuality.passed === true
renderEvents.length > 0
```

Otherwise the response is labeled:

```text
analysisEngine = v143-reference-free-rhythm-fallback
```

so polished/text fallback remains safe while weak V143 output cannot silently enter structured engraving.

Every quality report keeps:

```text
productionPromotionAuthorized: false
```

Important commits:

- `4542a9f15b09f0b6b9ce6980a908c7075b59a624` — analyzer-quality report.
- `5250c7629d428dcee3797ce946e81c68ffa2a4b6` — expose quality metrics.
- `5655f0c6ddea6570c09dbe79e185fffdb65ab168` — gate structured engine identity on quality.
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

# 4. Real-audio V143 product canary passed

Approved fixture:

`public/gomywayfullaitest.m4a`

Product-canary components:

- `analyzer/v143_ai_tab_product_canary_modal.py`
- `analyzer/evaluate_v143_real_audio_canary.mjs`
- `analyzer/render_v143_real_audio_canary_pdf.mjs`
- `.github/workflows/v143-ai-tab-real-audio-canary.yml`

Bot evidence commit:

`9f52bf83597e921da12887874bace0df0ffe6d47` — `Record V143 AI tab real-audio canary`

Analyzer evidence:

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

Observed techniques:

```text
bend
bend-release
hammer-on
pull-off
slide-down
slide-up
```

Exact-response PDF evidence:

`debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`

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

Workflow evidence:

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

The real-analyzer + exact-response PDF blocker is closed for this approved canary input.

---

# 5. Preview-only professional renderer gate implemented and CI-proven

Helper:

`lib/jimmyPaigeProfessionalPdfFeature.js`

The helper preserves the explicit flag:

```text
JIMMY_PAIGE_PROFESSIONAL_PDF_V1=true
```

and also auto-enables only when both are true:

```text
VERCEL_ENV === preview
VERCEL_GIT_COMMIT_REF === v143-contextual-prune-lobo
```

Used by:

- `app/api/generate-tab-preview/route.js`
- `app/api/generate-tab-pdf/route.js`

Evidence:

`debug/v143-contextual-prune/preview-pdf-feature-gate.json`

Bot evidence commit:

`f52bbb71b41f06b864b705b041ce3d2696246519` — `Record V143 Preview PDF feature gate`

```text
verifierExitCode: 0
passed: true
defaultDisabled: true
productionSameBranchDisabled: true
otherPreviewBranchDisabled: true
exactCanaryPreviewEnabled: true
explicitEnvironmentFlagPreserved: true
productionPromotionAuthorized: false
productionModified: false
```

No payment, customer-token redemption, or customer-email test has been performed.

---

# 6. Full isolated branch build gate passed

Workflow:

`.github/workflows/v143-ai-tab-branch-build-gate.yml`

Purpose: verify the two V143 safety regressions and compile the complete Next.js application without touching Vercel, the live analyzer, payments, email, or Production.

Initial workflow commit:

`22ca4ce01d2d78b1b7131bfd1aa1ceafb0e5ad5b` — `Add V143 AI tab full branch build gate`

The first run produced exit code `9` for both standalone verifier invocations while the full Next.js Node 24 build itself passed. Node exit code 9 is an invalid CLI argument condition; this was a harness/runtime compatibility issue, not a product regression.

Runtime-split fix:

`a48538b3fd121e7d525047edc8841ef436ace51c` — `Fix V143 branch build verifier runtime split`

The workflow now runs the existing ESM verifier harness under Node 22 and performs the actual application build under Node 24, matching the Vercel project runtime for the build.

Passing bot evidence commit:

`4f2b637ce5f2b69c4dfff07d26cac9f68fcc59d1` — `Record V143 AI tab branch build gate`

Evidence:

`debug/v143-contextual-prune/ai-tab-branch-build-gate.json`

```text
schemaVersion: 2
verifierNodeVersion: 22
buildNodeVersion: 24
analyzerQualityVerifierExitCode: 0
previewFeatureVerifierExitCode: 0
nextBuildExitCode: 0
analyzerQualityVerifierPassed: true
previewFeatureVerifierPassed: true
nextBuildPassed: true
passed: true
liveEndpointDeployedOrModified: false
vercelDeploymentAttempted: false
productionModified: false
productionPromotionAuthorized: false
paidPurchaseAttempted: false
customerTokenRedeemed: false
customerEmailSent: false
```

This closes the isolated branch compile/regression boundary. The branch is buildable under Node 24 and its current V143 quality/Preview feature invariants are green.

---

# 7. Vercel Preview audit and deployment-auth blocker

Connected Vercel project:

```text
project: dadrock-tabs-android
projectId: prj_6biwsn0iHci6FHNswAUCS8UYrAqF
teamId: team_qJrw8Cuze5bCEg9M3Q67XMWt
framework: Next.js
node: 24.x
```

Connected Vercel inspection on 2026-08-22 still shows no `v143-contextual-prune-lobo` Preview deployment. The latest visible deployment is a READY Production/main deployment from 2026-08-20.

The connected Vercel deploy action does not accept a source ref/branch. Do not use it for this canary because the exact source branch cannot be guaranteed.

Native Git Preview experiments remain exhausted and cleaned up:

- Draft PR #19 was closed unmerged after it failed to produce a Preview.
- Explicit `vercel.json → git.deploymentEnabled` branch experiment also failed to produce a Preview and was removed in `19683ef4251c7b2b7143c7ab59aa754d183044fd`.
- `vercel.json` is restored to its original cron/header configuration.

Explicit Preview workflow:

`.github/workflows/v143-vercel-preview-deploy.yml`

It is branch-only and fail-closed. It checks the presence, never values, of Preview runtime keys, builds prebuilt output, deploys without `--prod`, scopes the professional-renderer flag to that deployment, and records only compact non-secret evidence.

Latest credential evidence remains:

`debug/v143-contextual-prune/vercel-preview-deploy-action.json`

```text
schemaVersion: 2
credentialAliasesChecked:
  - VERCEL_TOKEN
  - VERCEL_ACCESS_TOKEN
  - VERCEL_API_TOKEN
  - VERCEL_CLI_TOKEN
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

The Preview environment-presence booleans in that diagnostic are false only because Preview configuration could not be pulled. They do not prove the project env values themselves are absent.

## Current external blocker

No usable Vercel CLI deployment credential has yet been proven available in GitHub Actions under the four supported aliases.

Vercel OIDC does not replace the CLI authorization token required for `vercel pull/build/deploy` from GitHub Actions.

No safe automated deployment-auth path is currently available from the connected tools without either a branch-guaranteed native Preview or a Vercel deployment credential.

No unsafe fallback was used and Production remains untouched.

---

# Current boundary

The following are proven:

- real V143 analyzer output quality on approved real audio;
- 358/358 event survival through the structured render contract;
- exact-response professional full/preview PDFs;
- PDF structural/text/raster quality;
- browser transport of fresh analyzer metadata to PDF routes;
- Preview-only/Production-off professional-renderer feature logic;
- analyzer-quality regression verification;
- Preview feature-gate regression verification;
- full isolated Next.js branch build under Node 24.

The only unresolved validation boundary is the **actual deployed Vercel/Next.js Preview application wiring**.

That boundary remains blocked by deployment authentication/native Preview suppression, not by V143 analysis, event quality, browser state handling, render eligibility, PDF generation, feature-gate logic, or Next.js compilation.

---

# Next steps — resume automatically when deployment authentication is available

1. Preferred prerequisite: make a GitHub Actions repository secret available under one of the already-supported aliases, preferably:

```text
VERCEL_TOKEN
```

2. Rerun `.github/workflows/v143-vercel-preview-deploy.yml` without weakening its Preview-only safety invariants.

3. Require the diagnostic to show:

```text
vercelTokenAvailableInGitHubActions: true
previewConfigPullExitCode: 0
previewBuildExitCode: 0
previewDeployExitCode: 0
deploymentUrl: non-null
productionDeployFlagUsed: false
productionModified: false
```

4. Independently inspect the resulting deployment through the connected Vercel app and confirm target/environment is Preview before sending application requests.

5. Verify `/ai-tab` loads.

6. POST only `/api/generate-tab-preview` for renderer routing validation. Do not call `/api/generate-tab-pdf` during automated Preview testing because that route performs unlock verification and can send email.

7. Use existing approved synthetic/fixture V143 events for the first structured route test; do not rerun the GPU analyzer merely to test the Preview PDF route.

8. Require a passing structured request to return:

```text
X-Jimmy-PAIge-PDF-Feature: enabled source
X-Jimmy-PAIge-PDF-Renderer: v143-structured-rhythm
```

9. Send a legacy/invalid-structured preview request and require safe polished fallback.

10. Only if route-level testing passes and Preview has the required V143/Blob runtime keys should an actual browser upload test using `public/gomywayfullaitest.m4a` be considered.

11. Do not make a PayPal purchase, redeem a customer token, or send customer email during automated Preview testing.

12. Record compact Preview evidence under `debug/v143-contextual-prune/` and refresh this checkpoint.

13. Only after deployed Preview application wiring passes should a separate explicit Production-promotion decision be made.

14. Do **not** enable or promote Production automatically.

---

# Non-negotiable boundaries

- Work only on `v143-contextual-prune-lobo`.
- Keep this checkpoint current after meaningful progress.
- Do not modify `main`.
- Do not merge the long-lived research branch into `main`.
- Do not deploy an unspecified Vercel source merely to obtain a Preview URL.
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
