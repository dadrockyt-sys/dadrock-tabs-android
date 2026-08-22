# CURRENT STATE — DadRock `/ai-tab` V143 Preview canary

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

Active product goal:

> `dadrocktabs.com/ai-tab` uploaded user audio → Jimmy PAIge / V143 reference-free Rhythm analysis → authenticated musical events → professional structured tab PDF.

Do **not** modify `main`, deploy/modify the live V143 Modal endpoint, merge the long-lived research branch, enable/promote Production automatically, make a payment, redeem a customer token, or send customer email during automated validation.

## Mandatory continuous checkpoint maintenance

Treat this file as the live recovery record, not an end-of-session summary.

Update it **continuously and as often as practical** after meaningful actions, tests, commits, workflow results, discoveries, blockers, and changes of direction. Keep these items current:

- exact current step;
- what was just attempted/changed;
- latest commit/run/evidence and result;
- pass/fail/pending/blocker status;
- safety boundary that must remain intact;
- immediate next step;
- fallback step if blocked.

Refresh before/after risky or multi-step work and whenever interruption could make resumption ambiguous. Remove stale next-step instructions promptly.

---

# LIVE WORKING STATE

## Current step — corrected built Next.js Preview-mode HTTP gate is running

The only remaining product-validation boundary that cannot yet be exercised directly is an **actual Vercel Preview deployment**, because GitHub Actions still has no usable Vercel CLI deployment credential and native branch Preview deployment is suppressed.

Before that external blocker is resolved, the current safe goal is to prove the built Next.js application path over real HTTP under simulated Vercel Preview identity.

### Authoritative workflow

`.github/workflows/v143-ai-tab-branch-build-gate.yml`

The existing proven branch build gate was upgraded in:

`2a7ea8baac9c186a50e11e83a22a029c8e5dae94` — `Add built Preview route smoke to V143 branch gate`

It now runs:

```text
Node 22 analyzer-quality regression verifier
Node 22 Preview feature-gate regression verifier
npm ci
Node 24 full Next.js build
built Next.js server with:
  VERCEL_ENV=preview
  VERCEL_GIT_COMMIT_REF=v143-contextual-prune-lobo
GET /ai-tab
structured POST /api/generate-tab-preview
safe-fallback POST /api/generate-tab-preview
missing-tab 400 validation POST
compact evidence persistence
```

This workflow does **not** deploy to Vercel.

### HTTP smoke verifier

`analyzer/verify_v143_next_preview_route_smoke.mjs`

Initial commit:

`31f8788fa6248cfdec6e094002119dfbb5c9955a` — `Add V143 built Preview route smoke verifier`

Required structured response:

```text
HTTP 200
Content-Type: application/pdf
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: v143-structured-rhythm
PDF starts with %PDF and is non-trivial
```

Required fallback response:

```text
HTTP 200
Content-Type: application/pdf
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: polished-safe-fallback
PDF starts with %PDF and is non-trivial
```

Missing generated tab must return HTTP 400.

### Test-harness issue found and fixed

DadRock production middleware intentionally blocks scanner/tool user agents including `curl/`.

The initial smoke readiness probe used default curl, which would receive HTTP 403 and could falsely report:

```text
serverReady: false
```

even when the built application itself was healthy.

This was a **smoke-harness issue, not a product regression**. Production middleware was not weakened or changed.

Fixes:

- `41353b5c908ef656b52be7bb9ae2d784a1e4c151` — `Use allowed user agent for V143 route smoke`
  - all verifier HTTP requests now send a normal QA browser-like user agent.
- `10673a9b13b2970652c3db219eae02b38eb42a37` — `Use allowed user agent for V143 readiness probe`
  - readiness curl now sends the same allowed browser-like QA user agent.

The redundant standalone smoke workflow was removed after its smoke was folded into the authoritative branch gate:

`cd8ffd7312d78ec63ef1a32b7bf83efdb1694bad` — `Consolidate V143 route smoke into branch gate`

The verifier remains and is used by the authoritative gate.

### Current authoritative run

The corrected branch gate has started and committed its heartbeat.

Current smoke evidence path:

`debug/v143-contextual-prune/next-preview-route-smoke.json`

Latest known contents:

```text
schemaVersion: 3
sourceCommit: 10673a9b13b2970652c3db219eae02b38eb42a37
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

The heartbeat bot commit for this corrected source is:

`03444577256f3c7bdccd855b5a9c3212d099ef1a` — `Record V143 branch gate smoke start`

### Immediate next step

Fetch both:

```text
debug/v143-contextual-prune/next-preview-route-smoke.json
debug/v143-contextual-prune/ai-tab-branch-build-gate.json
```

Follow only the final evidence whose `sourceCommit` is the corrected source (`10673a9b...`) or a later source that contains both user-agent fixes.

Require final route evidence:

```text
phase: complete-by-branch-build-gate
installExitCode: 0
nextBuildExitCode: 0
serverReady: true
routeSmokeExitCode: 0
passed: true
actualVercelPreviewDeployment: false
productionModified: false
productionPromotionAuthorized: false
```

Require the schemaVersion 3 branch gate to show analyzer, Preview feature, install, build, server, and route smoke all passing.

### Fallback if the corrected gate fails

Use only the failing compact field to select the next action:

- analyzer verifier nonzero → inspect analyzer regression only;
- Preview feature verifier nonzero → inspect feature helper only;
- install/build nonzero → inspect corresponding Actions artifact log;
- `serverReady:false` after the UA fix → inspect built server log;
- route smoke nonzero → inspect structured/fallback status/header/PDF evidence and route log.

Do **not** weaken the quality thresholds, structured event requirements, expected renderer headers, or fallback assertions merely to obtain a pass.

---

# PROVEN PRODUCT BOUNDARIES

## Stable application contract

`app/ai-tab/page.js` uploads permitted user audio to private Vercel Blob storage and calls `/api/analyze-audio-tab`.

`app/api/analyze-audio-tab/route.js` keeps legacy Lead/Bass behavior and uses the separate V143 analyzer URL for Rhythm when configured.

Required runtime keys for a real uploaded-audio V143 Rhythm request:

```text
ANALYZER_API_URL_V143
ANALYZER_API_TOKEN
BLOB_READ_WRITE_TOKEN
```

V143 identity remains fail-closed on:

```text
liveV143.referenceFree === true
```

`lib/v143RenderContract.js` accepts only events with valid:

```text
measure >= 1
step 0..15
stringIndex 0..5
fret 0..36
MIDI pitch
```

No browser/PDF layer may manufacture missing measure/step placement.

Browser metadata transport was reviewed and verified: each new generation clears stale analysis state and transports the fresh analyzer response metadata to preview/full-PDF routes.

## Analyzer quality gate

Current conservative eligibility floor:

```text
minimum valid render events: 4
minimum render-event survival: 70%
minimum playable string/fret coverage: 70%
minimum measure/step coverage: 70%
minimum pitch coverage: 70%
```

Structured engine identity is exposed only when reference-free identity is true, quality passes, and render events survive. Otherwise V143 is labeled fallback-only.

Key commits:

- `4542a9f15b09f0b6b9ce6980a908c7075b59a624` — analyzer-quality report.
- `5250c7629d428dcee3797ce946e81c68ffa2a4b6` — expose metrics.
- `5655f0c6ddea6570c09dbe79e185fffdb65ab168` — gate structured identity.
- `490d64e8bc842f1ff48447f86a638c9dff2bc6dd` — regression verifier.
- `a5b3ceb4998de7e96d62fa70ed11ef8e80cd749a` — CI workflow.

## Synthetic structured renderer fixture passed

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

## Real-audio V143 canary passed

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

## Preview-only professional renderer feature gate passed

`lib/jimmyPaigeProfessionalPdfFeature.js` preserves the explicit flag and automatically enables only when:

```text
VERCEL_ENV === preview
VERCEL_GIT_COMMIT_REF === v143-contextual-prune-lobo
```

Evidence:

`debug/v143-contextual-prune/preview-pdf-feature-gate.json`

Bot evidence commit:

`f52bbb71b41f06b864b705b041ce3d2696246519`

```text
passed: true
defaultDisabled: true
productionSameBranchDisabled: true
otherPreviewBranchDisabled: true
exactCanaryPreviewEnabled: true
explicitEnvironmentFlagPreserved: true
productionPromotionAuthorized: false
productionModified: false
```

## Full isolated branch build previously passed

Before the HTTP route smoke was added, the full branch compile/regression gate passed.

Bot evidence commit:

`4f2b637ce5f2b69c4dfff07d26cac9f68fcc59d1`

Evidence:

`debug/v143-contextual-prune/ai-tab-branch-build-gate.json`

Last proven schemaVersion 2 result:

```text
analyzerQualityVerifierExitCode: 0
previewFeatureVerifierExitCode: 0
nextBuildExitCode: 0
analyzerQualityVerifierPassed: true
previewFeatureVerifierPassed: true
nextBuildPassed: true
passed: true
productionModified: false
productionPromotionAuthorized: false
```

The running schemaVersion 3 gate supersedes this only after final evidence is committed.

---

# VERCEL PREVIEW EXTERNAL BLOCKER

Connected Vercel project:

```text
project: dadrock-tabs-android
projectId: prj_6biwsn0iHci6FHNswAUCS8UYrAqF
teamId: team_qJrw8Cuze5bCEg9M3Q67XMWt
framework: Next.js
node: 24.x
```

Read-only Vercel inspection still shows no `v143-contextual-prune-lobo` Preview deployment.

Native Git Preview experiments were exhausted and cleaned up:

- draft PR #19 produced no Preview and was closed unmerged;
- explicit `vercel.json git.deploymentEnabled` experiment produced no Preview and was removed;
- `vercel.json` is restored.

Explicit fail-closed Preview workflow:

`.github/workflows/v143-vercel-preview-deploy.yml`

Latest credential evidence:

`debug/v143-contextual-prune/vercel-preview-deploy-action.json`

```text
credentialAliasesChecked:
  VERCEL_TOKEN
  VERCEL_ACCESS_TOKEN
  VERCEL_API_TOKEN
  VERCEL_CLI_TOKEN
vercelTokenAvailableInGitHubActions: false
previewConfigPullExitCode: 99
previewBuildExitCode: 99
previewDeployExitCode: 99
deploymentUrl: null
deploymentRequestedAsPreview: true
productionDeployFlagUsed: false
projectEnvironmentMutated: false
productionModified: false
productionPromotionAuthorized: false
```

Fresh Vercel documentation review confirmed GitHub OIDC can authenticate requests to an **already-created** protected deployment, but it does not replace the Vercel CLI authorization token needed for external CI `vercel pull/build/deploy`.

The connected GitHub tool cannot enumerate repository secret names/values, and the connected Vercel deployment action does not expose an exact source branch/ref. Therefore do not use an unspecified-source deploy action to obtain a Preview URL.

---

# NEXT BOUNDARY AFTER LOCAL HTTP GATE

If the corrected built-server HTTP gate passes:

1. Record final schemaVersion 3 route/build evidence here.
2. Mark **local built Next.js Preview-mode application wiring** closed.
3. Keep the remaining blocker strictly scoped to Vercel deployment/environment integration.
4. When a Vercel CLI token becomes available under a supported GitHub secret alias, rerun `.github/workflows/v143-vercel-preview-deploy.yml`.
5. Independently verify the resulting deployment target/environment is Preview before sending requests.
6. Verify `/ai-tab` and POST only `/api/generate-tab-preview` first.
7. Require the deployed Preview structured/fallback headers to match the local HTTP gate.
8. Only after route-level deployed Preview validation and required Preview runtime-key presence should a real browser upload using `public/gomywayfullaitest.m4a` be considered.
9. Do not call `/api/generate-tab-pdf` during automated Preview validation because that route performs unlock verification and can send email.
10. Do not promote Production automatically.

---

# NON-NEGOTIABLE BOUNDARIES

- Work only on `v143-contextual-prune-lobo`.
- Continuously keep this checkpoint current.
- Do not modify `main`.
- Do not merge the long-lived research branch into `main`.
- Do not deploy an unspecified Vercel source merely to obtain a Preview URL.
- Do not deploy/modify the live V143 Modal endpoint during this validation.
- Do not rerun sealed historical compatibility captures.
- Do not overwrite/delete preserved compatibility evidence.
- Do not retrain/replace frozen V143 merely to make a gate pass.
- Do not manufacture measure/step data in browser/PDF code.
- Do not weaken analyzer-quality thresholds merely to produce a pass.
- Keep legacy Lead/Bass behavior unchanged.
- Keep polished PDF rendering as the safe fallback.
- Any pre-Production professional renderer activation must remain Preview-only and branch/deployment-scoped.
- Keep Production promotion disabled until a separate explicit decision.
