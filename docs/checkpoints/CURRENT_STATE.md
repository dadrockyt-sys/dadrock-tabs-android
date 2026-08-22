# CURRENT STATE — DadRock `/ai-tab` V143 Preview canary

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Branch HEAD before this checkpoint update: `08b3680d5ed120eab623bb44bfa37990ddad1afb`

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

Active product goal:

> `dadrocktabs.com/ai-tab` uploaded user audio → Jimmy PAIge / V143 reference-free Rhythm analysis → authenticated musical events → professional structured tab PDF.

Do **not** modify `main`, modify/deploy the live V143 Modal endpoint, merge the long-lived research branch, or enable/promote Production automatically.

### Mandatory continuous checkpoint maintenance

Treat this file as the live recovery record for the branch, not as an end-of-session summary.

While working, update `docs/checkpoints/CURRENT_STATE.md` **continuously and as often as practical**. Prefer several small checkpoint refreshes over waiting until a large block of work is finished.

After every meaningful action, test, commit, workflow result, discovery, decision, blocker change, or change of direction, record enough current state that a brand-new chat can resume without reconstructing work from conversation history. Keep these items current:

- the exact **current step being worked on**;
- what was just attempted or changed;
- the latest relevant commit/run/evidence and its result;
- whether the step passed, failed, is pending, or is externally blocked;
- any safety boundary or assumption that must still be preserved;
- the **immediate next step** to execute;
- the next fallback step if the immediate step is blocked.

Refresh the checkpoint before and after risky or multi-step work, before changing to a different investigation path, and whenever an interruption could make the current resumption point ambiguous. If work stops unexpectedly, this file should show the most recent completed action and the exact next action to take.

Do not leave stale “next step” instructions in place after they have been completed or superseded; replace them with the new current step and next step promptly.

---

# LIVE WORKING STATE

## Current step — built Next.js Preview-mode route smoke is pending

The Vercel deployment-auth blocker remains external, so the current safe step is to close as much application-wiring uncertainty as possible **without claiming this is an actual Vercel Preview deployment**.

### Files/commits added for this step

- `analyzer/verify_v143_next_preview_route_smoke.mjs`
  - `31f8788fa6248cfdec6e094002119dfbb5c9955a` — `Add V143 built Preview route smoke verifier`
- `.github/workflows/v143-next-preview-route-smoke.yml`
  - `7dd4da52f4f3f7508c3372643803c0d63bd38fff` — initial smoke workflow
  - `08b3680d5ed120eab623bb44bfa37990ddad1afb` — `Persist every V143 Preview smoke outcome`

The workflow now records compact JSON even when npm install, Next.js build, built-server startup, or route verification fails. It also rebases its evidence commit onto the latest isolated-branch head before pushing so frequent checkpoint commits do not create a false non-fast-forward failure.

### What the smoke does

Build the complete Next.js app under Node 24, then start the built server locally with:

```text
VERCEL_ENV=preview
VERCEL_GIT_COMMIT_REF=v143-contextual-prune-lobo
```

This is deliberately only a **local simulation of Vercel Preview identity**. It does not deploy to Vercel.

It then exercises the real HTTP application path:

1. GET `/ai-tab` → require HTTP 200.
2. POST valid structured Rhythm data to `/api/generate-tab-preview` → require PDF plus:

```text
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: v143-structured-rhythm
```

3. POST fallback-labeled/invalid structured Rhythm data → require PDF plus:

```text
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: polished-safe-fallback
```

4. POST malformed data missing generated tab → require HTTP 400.

Expected evidence:

`debug/v143-contextual-prune/next-preview-route-smoke.json`

The compact evidence is required to contain pipeline exit codes plus:

```text
localNextPreviewSimulation: true
actualVercelPreviewDeployment: false
vercelDeploymentAttempted: false
liveEndpointDeployedOrModified: false
productionModified: false
productionPromotionAuthorized: false
paidPurchaseAttempted: false
customerTokenRedeemed: false
customerEmailSent: false
```

### Current status

```text
workflow hardened: true
expected evidence file present on branch: false / pending
actual Vercel Preview deployment: false
Production modified: false
```

A direct local checkout fallback was attempted from the execution container, but that container cannot resolve `github.com`; therefore it cannot independently clone/run the repository. This is an execution-environment networking limitation, not a DadRock code failure.

### Immediate next step

Fetch `debug/v143-contextual-prune/next-preview-route-smoke.json`.

- If `passed: true`: record the concrete headers/PDF byte counts and mark local built-server application wiring closed.
- If `passed: false`: use its `installExitCode`, `nextBuildExitCode`, `serverReady`, `routeSmokeExitCode`, and `error` to fix only the failing step, then rerun.

### Fallback if evidence still does not appear

The workflow definition itself is already written to guarantee a JSON result after checkout/setup-node succeeds. If no evidence commit appears, inspect GitHub Actions execution infrastructure rather than weakening the application assertions. Do not infer a product failure from absence of the evidence file alone.

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

`lib/jimmyPaigeAnalysisPayload.js` exposes `analysisEngine = v143-reference-free-rhythm` only when:

```text
referenceFree === true
analysisQuality.passed === true
renderEvents.length > 0
```

Otherwise:

```text
analysisEngine = v143-reference-free-rhythm-fallback
```

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

```text
passed: true
raw/projected events: 40 / 40
measures: 28
fullPageCount: 2
previewPageCount: 2
```

---

# 4. Real-audio V143 product canary passed

Approved fixture:

`public/gomywayfullaitest.m4a`

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

---

# 5. Preview-only professional renderer gate implemented and CI-proven

`lib/jimmyPaigeProfessionalPdfFeature.js` preserves the explicit flag and auto-enables only when:

```text
VERCEL_ENV === preview
VERCEL_GIT_COMMIT_REF === v143-contextual-prune-lobo
```

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

---

# 6. Full isolated branch build gate passed

Workflow:

`.github/workflows/v143-ai-tab-branch-build-gate.yml`

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

Read-only Vercel inspection on 2026-08-22 still shows no `v143-contextual-prune-lobo` Preview deployment. A safe re-probe from commit `49741a8db076d61696747877af2e6577bbc4a160` also produced no Vercel deployment.

Latest credential evidence:

`debug/v143-contextual-prune/vercel-preview-deploy-action.json`

```text
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
```

Fresh Vercel documentation check on 2026-08-22 reconfirmed:

- GitHub Actions OIDC can authenticate requests **to an already-created protected deployment**.
- External Vercel CLI deployment still requires Vercel authorization (`--token` / `VERCEL_TOKEN`).
- Generating a project OIDC token also requires an authenticated Vercel API/CLI context; it does not bootstrap unauthenticated CI deployment.

The connected GitHub tool does not expose repository-secret enumeration, so no further safe secret discovery is available through the current connector.

The connected Vercel deploy action does not expose an exact source branch/ref in the available schema, so do not use it for this canary.

---

# Current proven boundary

Proven:

- real V143 analyzer output quality on approved real audio;
- 358/358 event survival through the structured render contract;
- exact-response professional full/preview PDFs;
- PDF structural/text/raster quality;
- browser transport of fresh analyzer metadata to PDF routes;
- Preview-only/Production-off professional-renderer feature logic;
- analyzer-quality regression verification;
- Preview feature-gate regression verification;
- full isolated Next.js branch build under Node 24.

Pending now:

- built Next.js local Preview-mode HTTP smoke evidence.

Still unresolved regardless of that local result:

- **actual deployed Vercel/Next.js Preview environment wiring**, because no branch-guaranteed deployment path is authenticated yet.

---

# Next steps after the current smoke

If the built Next.js smoke passes:

1. Record the exact evidence here.
2. Mark local built-server application wiring closed.
3. Keep the remaining blocker strictly scoped to Vercel deployment/environment integration.
4. When a Vercel CLI token becomes available under a supported GitHub secret alias, rerun `.github/workflows/v143-vercel-preview-deploy.yml`.
5. Independently confirm target is Preview before sending application requests.
6. Verify `/ai-tab` and POST only `/api/generate-tab-preview` first.
7. Require structured and polished-fallback headers to match the local smoke.
8. Only after route-level Preview validation and required Preview runtime-key presence should an actual browser upload using `public/gomywayfullaitest.m4a` be considered.
9. Do not call `/api/generate-tab-pdf` during automated Preview validation because that route performs unlock verification and can send email.
10. Do not enable/promote Production automatically.

---

# Non-negotiable boundaries

- Work only on `v143-contextual-prune-lobo`.
- Keep this checkpoint current after meaningful progress, and continuously record the current step and immediate next step as often as practical.
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
