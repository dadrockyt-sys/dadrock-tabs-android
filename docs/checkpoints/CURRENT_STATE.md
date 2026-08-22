# CURRENT STATE — DadRock `/ai-tab` V143 Preview canary

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Branch HEAD before this checkpoint update: `e28bdfdc6659cd905063455cb6a6f79dcf00101c`

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

## Current step — authoritative branch build + HTTP Preview-route gate is running

The actual Vercel Preview deployment remains blocked by missing deployment authentication, so the current safe objective is to prove the **built Next.js application wiring over real HTTP** without deploying anything.

### Smoke verifier

`analyzer/verify_v143_next_preview_route_smoke.mjs`

Commit:

`31f8788fa6248cfdec6e094002119dfbb5c9955a` — `Add V143 built Preview route smoke verifier`

The verifier requires:

1. GET `/ai-tab` → HTTP 200.
2. Structured Rhythm POST to `/api/generate-tab-preview` → PDF with:

```text
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: v143-structured-rhythm
```

3. Fallback-labeled/invalid structured Rhythm POST → PDF with:

```text
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: polished-safe-fallback
```

4. Missing generated tab → HTTP 400.

### First dedicated smoke workflow

`.github/workflows/v143-next-preview-route-smoke.yml`

Relevant commits:

- `7dd4da52f4f3f7508c3372643803c0d63bd38fff` — initial smoke workflow.
- `08b3680d5ed120eab623bb44bfa37990ddad1afb` — persist all pipeline failures.
- `0b299b544590131f75126e93ba977032f08396d5` — add immediate smoke-start heartbeat.

GitHub Actions proved this workflow actually started by committing:

`6feca47e9cca7908ca0475ba4cecdf760bc353dd` — `Record V143 Preview smoke start`

That heartbeat recorded:

```text
sourceCommit: 0b299b544590131f75126e93ba977032f08396d5
phase: started
localNextPreviewSimulation: true
actualVercelPreviewDeployment: false
productionModified: false
productionPromotionAuthorized: false
error: smoke-run-in-progress
```

### Authoritative smoke folded into the already-proven branch build gate

To avoid relying on a newly-created workflow identity, the same real HTTP smoke has now also been folded into the existing proven workflow:

`.github/workflows/v143-ai-tab-branch-build-gate.yml`

Commit:

`2a7ea8baac9c186a50e11e83a22a029c8e5dae94` — `Add built Preview route smoke to V143 branch gate`

This upgraded gate now performs:

```text
Node 22 analyzer-quality verifier
Node 22 Preview feature verifier
npm ci
Node 24 full Next.js build
built Next.js server startup with:
  VERCEL_ENV=preview
  VERCEL_GIT_COMMIT_REF=v143-contextual-prune-lobo
GET /ai-tab
structured /api/generate-tab-preview POST
safe-fallback /api/generate-tab-preview POST
400 validation POST
compact evidence persistence
```

It explicitly does **not** deploy to Vercel and does not touch the live analyzer, payment, customer token, customer email, or Production.

GitHub Actions proved this authoritative gate started by committing:

`e28bdfdc6659cd905063455cb6a6f79dcf00101c` — `Record V143 branch gate smoke start`

Current evidence:

`debug/v143-contextual-prune/next-preview-route-smoke.json`

```text
schemaVersion: 3
sourceCommit: 2a7ea8baac9c186a50e11e83a22a029c8e5dae94
phase: started-by-branch-build-gate
localNextPreviewSimulation: true
actualVercelPreviewDeployment: false
installExitCode: null
nextBuildExitCode: null
serverReady: false
routeSmokeExitCode: null
passed: false
vercelDeploymentAttempted: false
liveEndpointDeployedOrModified: false
productionModified: false
productionPromotionAuthorized: false
paidPurchaseAttempted: false
customerTokenRedeemed: false
customerEmailSent: false
error: branch-build-gate-in-progress
```

### Immediate next step

Fetch both:

- `debug/v143-contextual-prune/next-preview-route-smoke.json`
- `debug/v143-contextual-prune/ai-tab-branch-build-gate.json`

Require the final route smoke to change to a completed phase and report:

```text
installExitCode: 0
nextBuildExitCode: 0
serverReady: true
routeSmokeExitCode: 0
passed: true
```

Also require the branch build gate to report all analyzer/feature/build/route checks passing.

### Fallback if the gate fails

Use only the compact failing field to select the next action:

- analyzer verifier failure → inspect analyzer regression only;
- Preview feature verifier failure → inspect feature helper only;
- npm/build failure → inspect build logs/artifact;
- `serverReady: false` → inspect built server log;
- nonzero route smoke → inspect the HTTP verifier result and route log.

Do not weaken the structured/fallback assertions merely to get a green result.

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

# 6. Full isolated branch build gate previously passed

Before the route smoke was added, the branch build gate passed with:

Bot evidence commit:

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

The currently-running schemaVersion 3 gate supersedes this only after its final evidence lands.

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

Read-only Vercel inspection on 2026-08-22 still shows no `v143-contextual-prune-lobo` Preview deployment. A safe credential re-probe also produced no Vercel deployment.

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

Already proven:

- real V143 analyzer output quality on approved real audio;
- 358/358 event survival through the structured render contract;
- exact-response professional full/preview PDFs;
- PDF structural/text/raster quality;
- browser transport of fresh analyzer metadata to PDF routes;
- Preview-only/Production-off professional-renderer feature logic;
- analyzer-quality regression verification;
- Preview feature-gate regression verification;
- full isolated Next.js branch build under Node 24.

Currently executing:

- built Next.js local Preview-mode HTTP route smoke inside the authoritative branch build gate.

Still unresolved regardless of that local result:

- **actual deployed Vercel/Next.js Preview environment wiring**, because no branch-guaranteed deployment path is authenticated yet.

---

# Next steps after the current gate

If the branch build + route gate passes:

1. Record final schemaVersion 3 evidence here.
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
