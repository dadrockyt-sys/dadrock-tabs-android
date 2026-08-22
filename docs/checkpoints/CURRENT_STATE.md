# CURRENT STATE — DadRock `/ai-tab` End-to-End Construction — V143 Preview canary

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`

# PROJECT FOCUS — `dadrocktabs.com/ai-tab` end-to-end construction

The primary project is the complete customer-facing construction and validation of `dadrocktabs.com/ai-tab`, from uploaded audio to a professional-grade tablature PDF.

The intended end-to-end product flow is:

1. **User uploads audio** they possess and have permission to analyze.
2. **User selects the transcription target:**
   - Bass Guitar
   - Lead Guitar
   - Rhythm Guitar
3. **`app/ai-tab/page.js` drives the customer workflow** — upload, selection, analysis request, progress/state handling, preview generation, and the unlock/full-PDF path.
4. **Audio processing/separation isolates the requested musical part** as needed for the selected Bass, Lead, or Rhythm transcription path.
5. **Musical analysis extracts the information required for real tablature**, including as applicable:
   - notes / pitch;
   - playable string and fret placement;
   - note attacks and durations;
   - timing, beat, measure, and subdivision placement;
   - rhythm/sustain information;
   - guitar/bass techniques such as bends, releases, slides, hammer-ons, pull-offs, vibrato, muting, harmonics, and related articulations;
   - tempo;
   - meter / time signature;
   - tuning;
   - key / tonal metadata;
   - confidence, difficulty, and other useful analysis metadata.
6. **The analysis is converted into authenticated structured musical events** suitable for professional engraving. Missing timing or musical placement must not be invented later by browser/PDF code merely to make rendering succeed.
7. **The user receives a professional-grade TAB PDF preview** generated from the analyzed musical content.
8. **After purchase/unlock, the user receives the professional-grade full TAB PDF**, preserving the same authenticated analysis while revealing the complete transcription.

The finished product must operate as one coherent pipeline:

> **User audio → instrument choice (Bass / Lead / Rhythm) → page workflow → audio separation/processing → notes + techniques + timing + metadata → authenticated musical events → professional TAB preview PDF → purchased/unlocked professional full PDF.**

Current V143 work is the reference-free **Rhythm** implementation and validation track inside this larger `/ai-tab` end-to-end product. Existing Lead/Bass behavior must remain intact while the complete product is brought to professional production quality.

## Resume directive

Resume **only** on `v143-contextual-prune-lobo`.

Product goal:

> `dadrocktabs.com/ai-tab` uploaded user audio → Bass / Lead / Rhythm selection → analysis and separation → authenticated notes, techniques, timing and metadata → professional structured preview TAB PDF → purchased/unlocked professional full TAB PDF.

Never modify `main`, merge this research branch into `main`, deploy/modify the live V143 Modal endpoint, promote/enable Production automatically, make a payment, redeem a customer token, or send customer email during automated validation.

## Mandatory continuous checkpoint maintenance

This file is the live recovery record. Update it **continuously and as often as practical** after meaningful actions, tests, commits, workflow results, discoveries, blockers, and changes of direction. Always keep current step, latest evidence/result, status, safety boundary, immediate next step, and fallback step current. Remove stale “next step” text promptly.

---

# LIVE WORKING STATE

## Current step — bounded built-Next HTTP gate is running

Actual Vercel Preview deployment remains externally blocked by deployment authentication/native Preview suppression. The current safe goal is therefore to prove the built Next.js application path over real HTTP under simulated Vercel Preview identity, **without deploying anything**.

### Why the prior run was superseded

The previous corrected gate heartbeat came from source:

`10673a9b13b2970652c3db219eae02b38eb42a37`

Its heartbeat was committed around 18:44 ET. More than the workflow’s 30-minute job timeout later it still had no final evidence. Therefore the `started-by-branch-build-gate` marker was stale: that run had terminated/timed out before the final evidence step. This was treated as a workflow-diagnostics failure, not a DadRock product failure.

### Scanner-UA harness issue already fixed

`middleware.js` intentionally blocks scanner/tool user agents including `curl/`.

The first readiness probe used default curl, which could return 403 and falsely report `serverReady:false`.

Production middleware was **not** weakened. The test harness was fixed instead:

- `41353b5c908ef656b52be7bb9ae2d784a1e4c151` — verifier requests use an allowed browser-like QA user agent.
- `10673a9b13b2970652c3db219eae02b38eb42a37` — readiness curl uses the same allowed QA user agent.

The redundant standalone smoke workflow was removed:

`cd8ffd7312d78ec63ef1a32b7bf83efdb1694bad` — `Consolidate V143 route smoke into branch gate`

The smoke verifier remains:

`analyzer/verify_v143_next_preview_route_smoke.mjs`

### Bounded/instrumented authoritative gate

Workflow:

`.github/workflows/v143-ai-tab-branch-build-gate.yml`

Current hardening commit:

`4c9c33b106248bf9343f4c06738344704319ab33` — `Bound and instrument V143 branch gate`

This version adds:

```text
one workflow concurrency group, cancel-in-progress=true
25-minute overall job timeout
120s analyzer verifier timeout
120s Preview feature verifier timeout
600s npm ci timeout
600s Next build timeout
60s built-server readiness window
300s HTTP route smoke timeout
post-build progress evidence commit
final compact evidence commit
```

This prevents another opaque indefinitely-stale “started” marker. If install/build stops, GNU `timeout` returns a concrete exit code (typically 124) and the workflow can still persist diagnostics.

### Current bounded run

Current route-smoke heartbeat:

`debug/v143-contextual-prune/next-preview-route-smoke.json`

Latest known contents:

```text
schemaVersion: 4
sourceCommit: 4c9c33b106248bf9343f4c06738344704319ab33
phase: started-bounded-branch-gate
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
error: bounded-branch-gate-in-progress
```

Expected intermediate evidence after install/build:

`debug/v143-contextual-prune/branch-gate-progress.json`

Expected final evidence:

```text
debug/v143-contextual-prune/next-preview-route-smoke.json
debug/v143-contextual-prune/ai-tab-branch-build-gate.json
```

### Required HTTP smoke behavior

Built server identity is simulated only with:

```text
VERCEL_ENV=preview
VERCEL_GIT_COMMIT_REF=v143-contextual-prune-lobo
```

The smoke must prove:

1. GET `/ai-tab` → HTTP 200.
2. Valid structured Rhythm POST `/api/generate-tab-preview` → PDF plus:

```text
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: v143-structured-rhythm
```

3. Fallback-labeled/invalid structured Rhythm POST → PDF plus:

```text
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: polished-safe-fallback
```

4. Missing generated tab → HTTP 400.

### Immediate next step

Fetch `debug/v143-contextual-prune/branch-gate-progress.json`.

- If it appears, inspect analyzer/Preview/install/build exit codes immediately.
- If install/build pass, follow the final route/build JSONs.
- Require final route phase `complete-by-bounded-branch-gate`, install/build/route exit code `0`, `serverReady:true`, and `passed:true`.

### Fallback by failure field

- analyzer verifier nonzero → inspect analyzer regression only.
- Preview feature verifier nonzero → inspect feature helper only.
- `installExitCode:124` → dependency install exceeded 10-minute hard bound; inspect npm log artifact.
- `nextBuildExitCode:124` → Next build exceeded 10-minute hard bound; inspect build log artifact.
- other install/build nonzero → inspect corresponding log/artifact.
- `serverReady:false` after UA fix → inspect built-server log.
- route smoke nonzero → inspect structured/fallback status/header/PDF evidence.

Do not weaken product assertions to obtain a pass.

---

# PROVEN PRODUCT BOUNDARIES

## Application/event contract

`app/ai-tab/page.js` uploads permitted user audio to private Vercel Blob and calls `/api/analyze-audio-tab`.

Rhythm uses V143 only when configured; Lead/Bass legacy behavior must remain unchanged.

Required runtime keys for real uploaded-audio V143 Rhythm:

```text
ANALYZER_API_URL_V143
ANALYZER_API_TOKEN
BLOB_READ_WRITE_TOKEN
```

V143 remains fail-closed on `liveV143.referenceFree === true`.

Structured events must contain valid:

```text
measure >= 1
step 0..15
stringIndex 0..5
fret 0..36
MIDI pitch
```

No browser/PDF layer may manufacture placement.

Browser metadata transport has been reviewed and verified: new generation clears stale analysis state and sends the fresh response metadata to preview/full-PDF routes.

## Analyzer quality gate

Eligibility floor:

```text
minimum valid render events: 4
minimum render-event survival: 70%
minimum playable string/fret coverage: 70%
minimum measure/step coverage: 70%
minimum pitch coverage: 70%
```

Key commits:

- `4542a9f15b09f0b6b9ce6980a908c7075b59a624` — quality report.
- `5250c7629d428dcee3797ce946e81c68ffa2a4b6` — expose metrics.
- `5655f0c6ddea6570c09dbe79e185fffdb65ab168` — gate structured identity.
- `490d64e8bc842f1ff48447f86a638c9dff2bc6dd` — verifier.
- `a5b3ceb4998de7e96d62fa70ed11ef8e80cd749a` — CI.

## Structured PDF fixture passed

`debug/v143-contextual-prune/jimmy-paige-pdf-fixture/validation.json`

Commit `b40df94d76af3c6e432da0b8c20c723c298635a1`:

```text
passed: true
raw/projected events: 40 / 40
measures: 28
fullPageCount: 2
previewPageCount: 2
```

## Real-audio V143 canary passed

Approved fixture: `public/gomywayfullaitest.m4a`

Bot evidence commit:

`9f52bf83597e921da12887874bace0df0ffe6d47`

Analyzer evidence `debug/v143-contextual-prune/ai-tab-real-audio-canary.json`:

```text
passed: true
analysisEngine: v143-reference-free-rhythm
referenceFree: true
modalGpu: L4
candidateCount: 1788
selectedCount: 358
rawEventCount: 358
validRenderEventCount: 358
renderEventSurvivalPercent: 100%
playableStringFretPercent: 100%
musicalPlacementPercent: 100%
pitchValidityPercent: 100%
unique measures: 112
technique events: 25 / 358
sustain coverage: 358 / 358
tempo: 129.19921875
meter: 4/4
tuning: E Standard
```

Exact-response PDF evidence `debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`:

```text
passed: true
renderEventCount: 358
maximumMeasure: 113
fullPageCount: 4
previewPageCount: 4
fullPdfBytes: 1,686,104
previewPdfBytes: 1,678,626
```

## Preview-only renderer feature gate passed

Auto-enable only when:

```text
VERCEL_ENV === preview
VERCEL_GIT_COMMIT_REF === v143-contextual-prune-lobo
```

Evidence `debug/v143-contextual-prune/preview-pdf-feature-gate.json`, bot commit `f52bbb71b41f06b864b705b041ce3d2696246519`:

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

## Prior full Node-24 branch build passed

Before HTTP smoke was added, schema-2 branch build evidence passed at bot commit:

`4f2b637ce5f2b69c4dfff07d26cac9f68fcc59d1`

```text
analyzerQualityVerifierExitCode: 0
previewFeatureVerifierExitCode: 0
nextBuildExitCode: 0
passed: true
productionModified: false
productionPromotionAuthorized: false
```

The bounded schema-4 gate supersedes this only after final evidence lands.

---

# VERCEL PREVIEW EXTERNAL BLOCKER

Project:

```text
project: dadrock-tabs-android
projectId: prj_6biwsn0iHci6FHNswAUCS8UYrAqF
teamId: team_qJrw8Cuze5bCEg9M3Q67XMWt
framework: Next.js
node: 24.x
```

No `v143-contextual-prune-lobo` Preview deployment has appeared.

Native Git Preview experiments were exhausted/cleaned up. The explicit fail-closed Preview workflow remains:

`.github/workflows/v143-vercel-preview-deploy.yml`

Latest credential evidence `debug/v143-contextual-prune/vercel-preview-deploy-action.json`:

```text
VERCEL_TOKEN / VERCEL_ACCESS_TOKEN / VERCEL_API_TOKEN / VERCEL_CLI_TOKEN checked
vercelTokenAvailableInGitHubActions: false
previewConfigPullExitCode: 99
previewBuildExitCode: 99
previewDeployExitCode: 99
deploymentUrl: null
productionDeployFlagUsed: false
productionModified: false
productionPromotionAuthorized: false
```

Vercel docs were rechecked: GitHub OIDC can authenticate to an **already-created** protected deployment, but does not replace the Vercel CLI authorization token needed for external CI `vercel pull/build/deploy`.

The connected Vercel deploy action does not expose an exact source branch/ref, so do not use it for this canary.

---

# NEXT BOUNDARY AFTER LOCAL HTTP PASS

If the bounded local HTTP gate passes:

1. Record final schema-4 build/route evidence here.
2. Mark local built-Next Preview-mode application wiring closed.
3. Leave only Vercel deployment/environment integration unresolved.
4. When a supported Vercel CLI token becomes available in GitHub Actions, rerun `.github/workflows/v143-vercel-preview-deploy.yml`.
5. Confirm target is Preview independently before requests.
6. Verify `/ai-tab` and POST only `/api/generate-tab-preview` first.
7. Require deployed Preview structured/fallback headers to match local evidence.
8. Only after deployed route validation and required Preview runtime-key presence consider a real browser upload using `public/gomywayfullaitest.m4a`.
9. Do not automate `/api/generate-tab-pdf` because unlock verification can send email.
10. Never promote Production automatically.

---

# NON-NEGOTIABLE BOUNDARIES

- Work only on `v143-contextual-prune-lobo`.
- Keep this checkpoint continuously current.
- Do not modify `main` or merge this branch.
- Do not deploy an unspecified Vercel source.
- Do not deploy/modify live V143 Modal during this validation.
- Do not rerun sealed historical compatibility captures.
- Do not overwrite/delete preserved compatibility evidence.
- Do not retrain/replace frozen V143 merely to make a gate pass.
- Do not manufacture measure/step data.
- Do not weaken analyzer-quality thresholds.
- Keep legacy Lead/Bass behavior unchanged.
- Keep polished PDF as safe fallback.
- Pre-Production professional-renderer activation must remain Preview-only and branch/deployment-scoped.
- Keep Production promotion disabled until a separate explicit decision.
