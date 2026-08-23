# CURRENT STATE — DadRock `/ai-tab` End-to-End Construction — V143 Preview canary

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`

# PROJECT FOCUS — `dadrocktabs.com/ai-tab` end-to-end construction

The primary project is the complete customer-facing construction and validation of `dadrocktabs.com/ai-tab`, from uploaded audio to a professional-grade tablature PDF.

> **User audio → instrument choice (Bass / Lead / Rhythm) → `app/ai-tab/page.js` workflow → requested-part separation/processing → notes + playable positions + techniques + timing + metadata → authenticated musical events → professional TAB preview PDF → purchased/unlocked professional full PDF.**

Product requirements:

1. User uploads permitted audio.
2. User selects Bass, Lead, or Rhythm.
3. The selected part is isolated/processed appropriately.
4. Analysis extracts real notes/pitch, playable string/fret positions, attacks, duration/sustain, beat/measure/subdivision timing, techniques, tempo, meter, tuning, key, confidence/difficulty, and useful metadata.
5. Missing musical placement must never be manufactured by browser/PDF code.
6. Preview and purchased full PDF must derive from the same authenticated analysis.
7. Lead/Bass legacy customer behavior remains available until professional replacements are independently proven.

Current V143 work is the proven reference-free **Rhythm** professional track. A separate inactive Bass professional separation scaffold now exists, but Bass customer routing and structured professional identity remain disabled.

---

# RESUME DIRECTIVE

Resume **only** on `v143-contextual-prune-lobo`.

Never modify `main`, merge this branch into `main`, deploy/modify the live V143 Modal endpoint, automatically promote Production, make a payment, redeem a customer token, or send customer email during automated validation.

## Mandatory continuous checkpoint maintenance

This file is the live recovery record. Update it continuously after meaningful actions, tests, commits, workflow results, discoveries, blockers, or direction changes. Keep current step, latest evidence/result, status, safety boundary, immediate next step, and fallback current. Remove stale next-step instructions promptly.

---

# LIVE WORKING STATE

## A. Authoritative Rhythm built-Next HTTP gate — staged diagnostics

The previous bounded source:

`4c9c33b106248bf9343f4c06738344704319ab33`

remained at its start heartbeat for more than 20 minutes despite the earlier successful compile-only build taking about 90 seconds. No `branch-gate-progress.json` appeared. This was treated as an opaque workflow/run problem, **not as proof of a DadRock product regression**.

It was deliberately superseded by:

`22dc06af353220006a7558c6b9ba0c262cc64cb8` — `Add staged diagnostics to V143 branch gate`

Workflow:

`.github/workflows/v143-ai-tab-branch-build-gate.yml`

Because the workflow uses:

```text
concurrency:
  group: v143-ai-tab-branch-build-gate
  cancel-in-progress: true
```

the new staged run supersedes the obsolete run.

### Staged gate design

```text
overall job timeout: 35 minutes
analyzer-quality verifier hard timeout: 120s
Preview feature verifier hard timeout: 120s
post-verifier evidence commit
npm ci hard timeout: 600s
post-install evidence commit
Next build hard timeout: 600s
post-build evidence commit
built-server readiness window: 60s
HTTP route smoke hard timeout: 300s
final compact evidence commit
```

Progress evidence path:

`debug/v143-contextual-prune/branch-gate-progress.json`

Expected phases:

```text
post-verifiers
post-install
post-build
```

Route evidence:

`debug/v143-contextual-prune/next-preview-route-smoke.json`

Final build evidence:

`debug/v143-contextual-prune/ai-tab-branch-build-gate.json`

At the last check immediately after commit `22dc06a...`, the new schema-5 heartbeat had not yet replaced the old schema-4 heartbeat. Therefore the exact immediate next action is to fetch the route heartbeat and progress JSON and follow only evidence whose `sourceCommit` is `22dc06af353220006a7558c6b9ba0c262cc64cb8` or a later staged-gate source.

### Required final local HTTP proof

Built server identity must be simulated only with:

```text
VERCEL_ENV=preview
VERCEL_GIT_COMMIT_REF=v143-contextual-prune-lobo
```

Required structured Preview response:

```text
HTTP 200
Content-Type: application/pdf
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: v143-structured-rhythm
valid/non-trivial PDF
```

Required safe fallback response:

```text
HTTP 200
Content-Type: application/pdf
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: polished-safe-fallback
valid/non-trivial PDF
```

Missing generated tab must return HTTP 400.

Final staged route evidence must show:

```text
phase: complete-by-staged-branch-gate
installExitCode: 0
nextBuildExitCode: 0
serverReady: true
routeSmokeExitCode: 0
passed: true
actualVercelPreviewDeployment: false
vercelDeploymentAttempted: false
productionModified: false
productionPromotionAuthorized: false
```

### Scanner-UA harness issue already fixed

Production `middleware.js` intentionally blocks scanner/tool UAs including default `curl/`.

The test harness—not production middleware—was corrected:

- `41353b5c908ef656b52be7bb9ae2d784a1e4c151` — verifier requests use an allowed browser-like QA UA.
- `10673a9b13b2970652c3db219eae02b38eb42a37` — readiness curl uses the same QA UA.

Fallback diagnosis by compact field:

```text
analyzer verifier nonzero → inspect analyzer regression
Preview feature verifier nonzero → inspect feature helper
installExitCode 124 → npm ci exceeded hard bound
nextBuildExitCode 124 → Next build exceeded hard bound
other install/build nonzero → inspect corresponding log artifact
serverReady false after QA-UA fix → inspect built-server log
route smoke nonzero → inspect structured/fallback route evidence
```

Never weaken product assertions to obtain a pass.

---

## B. Whole-product Bass / Lead / Rhythm customer contract — PASSED

Construction map:

`docs/checkpoints/AI_TAB_END_TO_END_CONSTRUCTION.md`

Latest map commit:

`d21a9fcb2be3f2abd34632f625bcf145934703fb` — `Update AI Tab construction map with Bass scaffold`

Verifier:

`analyzer/verify_ai_tab_end_to_end_contract.mjs`

Workflow:

`.github/workflows/ai-tab-end-to-end-contract.yml`

Relevant commits:

- `39b687eaf534cace2faad6e48fbcf5a5ac80f84b` — add verifier.
- `be4a65bf301d2725096a9c3de2824f2b6cabaa6e` — persist evidence.
- `a3f66a2632278bb944d46260e798f27c9a9a8fdf` — add CI.
- `8784cbb734928ff8284cc17d6c41f0844c7fbe22` — verify Preview/full professional-renderer parity.

Evidence:

`debug/v143-contextual-prune/ai-tab-end-to-end-contract.json`

Latest schema-2 result:

```text
passed: true
instrumentChoices: lead, rhythm, bass
userAudioUploadWired: true
copyrightGateWired: true
analyzerRequestWired: true
previewPdfWired: true
fullPdfUnlockWired: true
analysisMetadataTransportWired: true
previewAndFullProfessionalFeatureGateShared: true
previewAndFullProfessionalRendererShared: true
rhythmDedicatedV143RouteFailClosed: true
rhythmStructuredProfessionalRendererFailClosed: true
leadLegacyPreserved: true
bassLegacyPreserved: true
leadStructuredProfessionalIdentityPresent: false
bassStructuredProfessionalIdentityPresent: false
missingPlacementManufacturedForLegacy: false
paymentAttempted: false
tokenRedeemed: false
customerEmailSent: false
vercelDeploymentAttempted: false
productionModified: false
productionPromotionAuthorized: false
```

Conclusion:

```text
instrument choice
→ private upload
→ analyzer request
→ fresh analysis metadata
→ Preview professional-renderer decision
→ unlock/full professional-renderer decision
```

is connected for all three customer choices.

Preview and purchased/full routes are statically proven to share both:

```text
getJimmyPaigeProfessionalPdfFeatureState(...)
createJimmyPaigeProfessionalPdf(...)
```

The remaining three-instrument parity gap is analyzer/separation/structured-event quality, not page wiring.

---

## C. Inactive Bass professional separation scaffold — PASSED

Legacy Bass baseline in `analyzer/modal_analyzer.py`:

```text
Basic Pitch on normalized full mix
no requested-part stem isolation
heuristic string/fret assignment
start/end/duration available
tempo: None
meter: None
key: None
confidence/difficulty: None
technique evidence essentially bend-only
```

Therefore Bass professional parity requires a genuine analyzer track rather than a renderer switch.

Scaffold:

`analyzer/bass_professional_separator_scaffold.py`

Commit:

`4de8b0c78e18fe39c4d80adb21aab35bced37b83`

Verifier:

`analyzer/verify_bass_professional_separator_scaffold.py`

Workflow:

`.github/workflows/bass-professional-separator-scaffold.yml`

Bot evidence commit:

`70c5411d2e72f06923e88075e6f48f9555a8c0e5` — `Record Bass professional separator scaffold`

Evidence:

`debug/v143-contextual-prune/bass-professional-separator-scaffold.json`

```text
passed: true
mode: inactive-bass-professional-separator-scaffold
directPath: audio -> Demucs6s Bass
cascadePath: audio -> BS-RoFormer Instrumental -> Demucs6s Bass
demucsSingleStem: Bass
demucsShifts: 1
demucsOverlap: 0.10
demucsSegmentSize: 6
deterministicSeed: 143
referenceFree: true
diagnosticOnly: true
productionCandidate: false
analyzerRoutingEnabled: false
professionalStructuredIdentityEnabled: false
realAudioBassCanaryPassed: false
noteTimingTechniqueQualityProven: false
liveEndpointDeployedOrModified: false
vercelDeploymentAttempted: false
productionModified: false
productionPromotionAuthorized: false
paidPurchaseAttempted: false
customerTokenRedeemed: false
customerEmailSent: false
```

The scaffold creates only a deterministic two-view Bass substrate:

```text
view A: normalized audio -> Demucs6s Bass
view B: normalized audio -> BS-RoFormer Instrumental -> Demucs6s Bass
```

It is **not connected** to `/api/analyze-audio-tab` and must remain inactive until a separate approved real-audio Bass canary proves separation, notes, timing, techniques, metadata, quality, and PDF behavior.

Architecture distinction:

- Bass can be physically isolated as a Demucs `Bass` stem.
- Lead and Rhythm both live inside the separated `Guitar` stem; a future Lead professional path therefore needs lead-specific musical selection/analysis on the guitar views, not a fake “Lead stem.”

---

# PROVEN RHYTHM PRODUCT BOUNDARIES

## Application routing

```text
Lead/Bass → legacy ANALYZER_API_URL
Rhythm → ANALYZER_API_URL_V143 when configured, otherwise legacy rollback
```

V143 identity fails closed unless:

`liveV143.referenceFree === true`

Structured events require valid:

```text
measure >= 1
step 0..15
stringIndex 0..5
fret 0..36
MIDI pitch
```

No browser/PDF layer may manufacture missing placement.

## Deterministic Rhythm separation

Proven chain:

`v143_rhythm_deterministic_stem_provider.py`
→ `v143_deterministic_separator.py`
→ seeded separator
→ Rhythm router
→ bend consensus
→ legato evidence
→ structured output builder

Frozen guards:

```text
seed: 143
demucsShifts: 1
demucsOverlap: 0.10
demucsSegmentSize: 6
```

## Analyzer quality floor

```text
minimum valid render events: 4
minimum render-event survival: 70%
minimum playable string/fret coverage: 70%
minimum measure/step coverage: 70%
minimum pitch coverage: 70%
```

## Real-audio Rhythm canary — PASSED

Approved fixture:

`public/gomywayfullaitest.m4a`

Bot evidence:

`9f52bf83597e921da12887874bace0df0ffe6d47`

Evidence:

`debug/v143-contextual-prune/ai-tab-real-audio-canary.json`

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
uniqueMeasures: 112
techniqueEvents: 25/358
sustainCoverage: 358/358
tempo: 129.19921875
meter: 4/4
tuning: E Standard
techniques: bend, bend-release, hammer-on, pull-off, slide-down, slide-up
```

Exact-response PDF evidence:

`debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`

```text
passed: true
renderEventCount: 358
maximumMeasure: 113
fullPageCount: 4
previewPageCount: 4
fullPdfBytes: 1686104
previewPdfBytes: 1678626
```

Synthetic structured renderer fixture also passed at commit:

`b40df94d76af3c6e432da0b8c20c723c298635a1`

Preview feature gate evidence also passed at bot commit:

`f52bbb71b41f06b864b705b041ce3d2696246519`

Prior compile-only Node-24 branch build passed at bot commit:

`4f2b637ce5f2b69c4dfff07d26cac9f68fcc59d1`

That successful compile-only gate took approximately 90 seconds from source change to evidence, which is why the obsolete >20-minute bounded heartbeat was treated as abnormal workflow behavior.

---

# PREVIEW AND PURCHASED FULL-PDF WIRING

`app/ai-tab/page.js` stores the fresh analyzer response as `analysisMetadata` and sends the same metadata family to both PDF routes:

```text
tuning
tempo
timeSignature
keySignature
analysisEngine
techniques
renderEvents
measureGrid
confidence
difficulty
```

Preview:

`/api/generate-tab-preview`

Purchased/unlocked full PDF:

`/api/generate-tab-pdf`

Schema-2 whole-product evidence proves both routes share the same professional feature gate and `createJimmyPaigeProfessionalPdf(...)` helper.

The full route verifies PayPal/free-token unlock and can send customer email. Do **not** automate the real full route during branch validation.

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

No branch Preview deployment has appeared.

Fail-closed workflow:

`.github/workflows/v143-vercel-preview-deploy.yml`

Evidence:

`debug/v143-contextual-prune/vercel-preview-deploy-action.json`

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

GitHub OIDC can authenticate requests to an existing protected Vercel deployment, but does not replace the Vercel CLI authorization token needed for external CI deploy. The connected Vercel deploy action does not expose an exact source branch/ref, so do not use it merely to obtain a URL.

---

# NEXT BOUNDARIES

## Immediate

1. Follow staged gate source `22dc06af353220006a7558c6b9ba0c262cc64cb8`.
2. Fetch route heartbeat and `branch-gate-progress.json`.
3. Record each staged phase as it lands.
4. Require final local HTTP structured/fallback proof.
5. If a phase fails, diagnose exactly that phase without weakening assertions.

## After local Rhythm HTTP pass

1. Mark local built-Next Preview-mode Rhythm application wiring closed.
2. Leave real Vercel Preview deployment/environment integration as the remaining Rhythm application blocker.
3. When a supported Vercel CLI token becomes available, rerun the fail-closed Preview deploy workflow.
4. Independently confirm Preview target before requests.
5. Test `/ai-tab` and `/api/generate-tab-preview` first.
6. Only after deployed route + required runtime keys pass, consider real browser upload with `public/gomywayfullaitest.m4a`.
7. Do not automate `/api/generate-tab-pdf` because of payment/token/email side effects.

## Three-instrument professional parity

- Rhythm: real-audio professional analyzer + PDF proof exists.
- Bass: inactive deterministic separation scaffold proof exists; real-audio professional analysis not yet proven.
- Lead: remains legacy; future professional path should use separated guitar views plus Lead-specific analysis/selection, not a fictitious Lead stem.

Do not activate Lead/Bass structured identities until each earns independent real-audio analyzer, quality, and PDF evidence.

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
- Do not manufacture timing/musical placement.
- Do not weaken analyzer-quality thresholds.
- Keep Lead/Bass legacy customer behavior intact until replacements are independently proven.
- Keep the Bass scaffold inactive until real-audio evidence exists.
- Keep polished PDF as safe fallback.
- Preview and full PDF must derive from the same authenticated analysis.
- Pre-Production professional-renderer activation remains Preview-only and branch/deployment-scoped.
- Keep Production promotion disabled until a separate explicit decision.
