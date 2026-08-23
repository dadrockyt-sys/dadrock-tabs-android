# CURRENT STATE — DadRock `/ai-tab` End-to-End Construction — V143 Preview canary

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`

# PROJECT FOCUS — `dadrocktabs.com/ai-tab` end-to-end construction

The primary project is the complete customer-facing construction and validation of `dadrocktabs.com/ai-tab`, from uploaded audio to a professional-grade tablature PDF.

The intended product flow is:

1. User uploads audio they possess and have permission to analyze.
2. User selects **Bass Guitar, Lead Guitar, or Rhythm Guitar**.
3. `app/ai-tab/page.js` drives upload, selection, analysis, state/progress, preview generation, unlock, and full-PDF delivery.
4. Audio processing/separation isolates the requested musical part as appropriate to the selected instrument.
5. Analysis extracts real musical evidence including notes/pitch, playable string/fret placement, attacks, durations, sustain, beat/measure/subdivision timing, techniques/articulations, tempo, meter, tuning, key, confidence/difficulty, and supporting metadata.
6. Analysis becomes authenticated structured musical events suitable for professional engraving. Browser/PDF code must never invent missing placement merely to make rendering succeed.
7. User receives a professional-grade TAB preview PDF.
8. After purchase/unlock, user receives the professional-grade full TAB PDF based on the same authenticated analysis.

> **User audio → instrument choice (Bass / Lead / Rhythm) → page workflow → audio separation/processing → notes + techniques + timing + metadata → authenticated musical events → professional TAB preview PDF → purchased/unlocked professional full PDF.**

Current V143 work is the proven reference-free **Rhythm** professional implementation track inside this larger product. Lead/Bass customer paths remain intact and must stay legacy/fallback until each earns its own independently validated professional analyzer identity.

---

# RESUME DIRECTIVE

Resume **only** on `v143-contextual-prune-lobo`.

Never modify `main`, merge this research branch into `main`, deploy/modify the live V143 Modal endpoint, promote/enable Production automatically, make a payment, redeem a customer token, or send customer email during automated validation.

## Mandatory continuous checkpoint maintenance

This file is the live recovery record. Update it continuously and as often as practical after meaningful actions, tests, commits, workflow results, discoveries, blockers, or changes of direction. Keep current step, latest evidence/result, status, safety boundary, immediate next step, and fallback step current. Remove stale next-step text promptly.

---

# LIVE WORKING STATE

## Current step A — bounded built-Next Rhythm HTTP gate

Authoritative workflow:

`.github/workflows/v143-ai-tab-branch-build-gate.yml`

Current bounded source:

`4c9c33b106248bf9343f4c06738344704319ab33` — `Bound and instrument V143 branch gate`

This gate performs:

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

Hard bounds:

```text
concurrency group with cancel-in-progress=true
overall job timeout: 25 minutes
analyzer verifier: 120s
Preview feature verifier: 120s
npm ci: 600s
Next build: 600s
server readiness: 60s
HTTP route smoke: 300s
post-build progress evidence commit
final compact evidence commit
```

Current heartbeat:

`debug/v143-contextual-prune/next-preview-route-smoke.json`

Latest observed at approximately 20:10 ET:

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
error: bounded-branch-gate-in-progress
vercelDeploymentAttempted: false
liveEndpointDeployedOrModified: false
productionModified: false
productionPromotionAuthorized: false
paidPurchaseAttempted: false
customerTokenRedeemed: false
customerEmailSent: false
```

Expected intermediate evidence:

`debug/v143-contextual-prune/branch-gate-progress.json`

At the latest check this file had **not yet appeared**. The bounded source was still inside its 25-minute execution ceiling, so do not yet call this a product failure.

Expected final evidence:

```text
debug/v143-contextual-prune/next-preview-route-smoke.json
debug/v143-contextual-prune/ai-tab-branch-build-gate.json
```

Required final route result:

```text
phase: complete-by-bounded-branch-gate
installExitCode: 0
nextBuildExitCode: 0
serverReady: true
routeSmokeExitCode: 0
passed: true
actualVercelPreviewDeployment: false
productionModified: false
productionPromotionAuthorized: false
```

Required structured Preview response:

```text
HTTP 200
Content-Type: application/pdf
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: v143-structured-rhythm
```

Required safe fallback response:

```text
HTTP 200
Content-Type: application/pdf
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: polished-safe-fallback
```

Missing generated tab must return HTTP 400.

### Scanner-UA harness issue already fixed

`middleware.js` intentionally blocks scanner/tool user agents including default `curl/`.

Production middleware was **not** weakened. The test harness was corrected:

- `41353b5c908ef656b52be7bb9ae2d784a1e4c151` — verifier requests use a browser-like QA user agent.
- `10673a9b13b2970652c3db219eae02b38eb42a37` — readiness curl uses the same QA user agent.

The redundant standalone smoke workflow was removed:

`cd8ffd7312d78ec63ef1a32b7bf83efdb1694bad` — `Consolidate V143 route smoke into branch gate`

### Immediate next action for Rhythm HTTP gate

1. Fetch `debug/v143-contextual-prune/branch-gate-progress.json`.
2. Fetch final route/build JSONs.
3. If no progress/final evidence exists after the 25-minute bound plus a small scheduling margin, treat the run as workflow-diagnostics failure/termination, **not automatically as a DadRock product failure**.
4. Use the exact compact failure field if one exists; never weaken product assertions.

Fallback interpretation:

```text
analyzer verifier nonzero → inspect analyzer regression
Preview feature verifier nonzero → inspect feature helper
installExitCode 124 → npm install exceeded hard bound
nextBuildExitCode 124 → Next build exceeded hard bound
other install/build nonzero → inspect corresponding log artifact
serverReady false after QA-UA fix → inspect built-server log
route smoke nonzero → inspect structured/fallback response evidence
```

---

## Current step B — whole-product Bass / Lead / Rhythm contract is CI-proven

Construction map:

`docs/checkpoints/AI_TAB_END_TO_END_CONSTRUCTION.md`

Commit:

`075e593ce1755330c671a07b3bb87207cc205026` — `Map AI Tab end-to-end construction state`

Verifier:

`analyzer/verify_ai_tab_end_to_end_contract.mjs`

Workflow:

`.github/workflows/ai-tab-end-to-end-contract.yml`

Key commits:

- `39b687eaf534cace2faad6e48fbcf5a5ac80f84b` — add whole-product verifier.
- `be4a65bf301d2725096a9c3de2824f2b6cabaa6e` — persist compact evidence.
- `a3f66a2632278bb944d46260e798f27c9a9a8fdf` — add branch-only CI.
- `8784cbb734928ff8284cc17d6c41f0844c7fbe22` — verify Preview and full/unlocked renderer parity.

Initial bot evidence commit:

`97ec364c257b516949e2c2be8a94c24cb0ed0d39` — `Record AI Tab end-to-end contract`

Current evidence:

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

### Construction conclusion

The **customer application wiring for all three instruments is proven**:

```text
instrument choice
→ private upload
→ analyzer request
→ fresh analyzer metadata state
→ professional Preview route decision
→ unlock/full PDF route decision
```

Preview and purchased/full routes are now statically verified to share both:

```text
getJimmyPaigeProfessionalPdfFeatureState(...)
createJimmyPaigeProfessionalPdf(...)
```

This guards against a professional Preview silently switching to a different renderer after unlock.

The remaining three-instrument parity gap is **analyzer/separation/structured-render quality**, not page wiring:

- Rhythm has deterministic requested-part separation + authenticated structured V143 events + professional structured PDF evidence.
- Lead remains legacy and has no authenticated structured professional identity.
- Bass remains legacy in the customer route and has no authenticated structured professional identity.

Do not solve this by relabeling legacy Lead/Bass output or feeding it into the Rhythm structured renderer.

---

## Current step C — inactive Bass professional separation scaffold is CI-proven

Legacy Bass baseline was inspected in `analyzer/modal_analyzer.py`:

```text
Basic Pitch runs on normalized full mix
no requested-part stem isolation
heuristic string/fret assignment
start/end/duration available
tempo: None
meter: None
key: None
confidence/difficulty: None
technique evidence essentially bend-only
```

Therefore Bass professional parity requires a real analyzer track, not a renderer toggle.

Inactive scaffold:

`analyzer/bass_professional_separator_scaffold.py`

Commit:

`4de8b0c78e18fe39c4d80adb21aab35bced37b83` — `Scaffold deterministic Bass stem separation`

Verifier:

`analyzer/verify_bass_professional_separator_scaffold.py`

Commit:

`2c6c909a0a726ed7892bed75d2fde1bb38afb13a`

Workflow:

`.github/workflows/bass-professional-separator-scaffold.yml`

Commit:

`c61fa19a4d9f609b014fa6fafdbeb22dd479c895` — `Add Bass separator scaffold CI`

Bot evidence commit:

`70c5411d2e72f06923e88075e6f48f9555a8c0e5` — `Record Bass professional separator scaffold`

Evidence:

`debug/v143-contextual-prune/bass-professional-separator-scaffold.json`

Result:

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

### Bass boundary

This scaffold is **not activated** anywhere in the customer application. It establishes only a deterministic, reference-free two-view Bass separation substrate:

```text
view A: normalized audio -> Demucs6s Bass
view B: normalized audio -> BS-RoFormer Instrumental -> Demucs6s Bass
```

Do not route `/api/analyze-audio-tab` to it and do not create a Bass professional engine identity until a separate real-audio Bass canary proves note, timing, technique, metadata, quality, and PDF behavior.

The next Bass step should occur only after the current Rhythm HTTP gate is resolved unless there is a separate explicit reason to parallelize GPU work.

---

# PROVEN RHYTHM PRODUCT BOUNDARIES

## Application/event contract

`app/ai-tab/page.js` uploads permitted user audio to private Vercel Blob and calls `/api/analyze-audio-tab`.

`app/api/analyze-audio-tab/route.js` currently routes:

```text
Lead/Bass → legacy ANALYZER_API_URL
Rhythm → ANALYZER_API_URL_V143 when configured, otherwise legacy rollback
```

V143 identity fails closed unless:

`liveV143.referenceFree === true`

Structured render events require valid:

```text
measure >= 1
step 0..15
stringIndex 0..5
fret 0..36
MIDI pitch
```

No browser/PDF layer may manufacture missing placement.

## Deterministic Rhythm separation

The proven V143 product canary uses:

`v143_rhythm_deterministic_stem_provider.py`
→ `v143_deterministic_separator.py`
→ seeded separator
→ Rhythm router
→ bend consensus
→ legato evidence
→ structured output builder.

Frozen deterministic separator guards:

```text
seed: 143
demucsShifts: 1
demucsOverlap: 0.10
demucsSegmentSize: 6
```

Do not alter these merely to make a gate pass.

## Analyzer quality floor

```text
minimum valid render events: 4
minimum render-event survival: 70%
minimum playable string/fret coverage: 70%
minimum measure/step coverage: 70%
minimum pitch coverage: 70%
```

## Real-audio V143 canary passed

Approved fixture:

`public/gomywayfullaitest.m4a`

Bot evidence commit:

`9f52bf83597e921da12887874bace0df0ffe6d47`

Analyzer evidence:

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
unique measures: 112
technique events: 25 / 358
sustain coverage: 358 / 358
tempo: 129.19921875
meter: 4/4
tuning: E Standard
observed techniques: bend, bend-release, hammer-on, pull-off, slide-down, slide-up
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

## Synthetic professional renderer fixture passed

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

## Preview feature gate passed

Professional renderer auto-enables only when:

```text
VERCEL_ENV === preview
VERCEL_GIT_COMMIT_REF === v143-contextual-prune-lobo
```

Evidence:

`debug/v143-contextual-prune/preview-pdf-feature-gate.json`

Bot commit:

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

## Prior full Node-24 build passed

Before the HTTP route smoke was added, isolated branch build evidence passed:

`4f2b637ce5f2b69c4dfff07d26cac9f68fcc59d1`

```text
analyzerQualityVerifierExitCode: 0
previewFeatureVerifierExitCode: 0
nextBuildExitCode: 0
passed: true
productionModified: false
productionPromotionAuthorized: false
```

The bounded schema-4 HTTP gate supersedes this only after final evidence lands.

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

Preview route:

`/api/generate-tab-preview`

Purchased/unlocked route:

`/api/generate-tab-pdf`

Both routes use the same professional feature helper and `createJimmyPaigeProfessionalPdf(...)` when enabled. Schema-2 end-to-end evidence verifies this parity.

The full route remains protected by PayPal/free-token verification and can send customer email. Do **not** automate the real full route in branch validation because payment/token/email side effects are prohibited.

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

Fail-closed Preview deployment workflow:

`.github/workflows/v143-vercel-preview-deploy.yml`

Latest credential evidence:

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

Vercel docs were rechecked: GitHub OIDC can authenticate requests to an already-created protected deployment, but does not replace the Vercel CLI authorization token needed by external CI to `vercel pull/build/deploy`.

The connected Vercel deployment action does not expose an exact source branch/ref. Do not use it for this canary merely to obtain a URL.

---

# NEXT BOUNDARIES

## Immediate

1. Finish/read the bounded built-Next Rhythm HTTP gate.
2. If it passes, mark local built-Next Preview-mode application wiring closed.
3. If it fails or terminates before progress evidence, diagnose the workflow boundary without weakening product assertions.

## After local Rhythm HTTP pass

1. Leave only real Vercel Preview deployment/environment integration unresolved for the Rhythm application path.
2. When a supported Vercel CLI token becomes available in GitHub Actions, rerun `.github/workflows/v143-vercel-preview-deploy.yml`.
3. Independently confirm target is Preview before requests.
4. Verify `/ai-tab` and POST only `/api/generate-tab-preview` first.
5. Require deployed structured/fallback headers to match local evidence.
6. Only after deployed route validation and required Preview runtime-key presence, consider real browser upload using `public/gomywayfullaitest.m4a`.
7. Do not automate `/api/generate-tab-pdf` because unlock verification can trigger payment/token/email side effects.

## Three-instrument professional parity

Use Rhythm as the reference architecture for separate Lead and Bass professional tracks.

Bass has now reached only this safe milestone:

```text
deterministic two-view Bass separation scaffold: contract-proven
real-audio Bass separation: not yet proven
Bass note/timing/technique quality: not yet proven
Bass structured professional identity: disabled
Bass analyzer routing: disabled
```

Lead remains legacy and has not yet started a professional separation scaffold.

Do not promote Lead/Bass to structured status until each has its own real-audio separation, analysis, quality, and professional PDF evidence.

---

# NON-NEGOTIABLE BOUNDARIES

- Work only on `v143-contextual-prune-lobo`.
- Keep this checkpoint continuously current.
- Do not modify `main` or merge this branch.
- Do not deploy an unspecified Vercel source.
- Do not deploy/modify the live V143 Modal endpoint during this validation.
- Do not rerun sealed historical compatibility captures.
- Do not overwrite/delete preserved compatibility evidence.
- Do not retrain/replace frozen V143 merely to make a gate pass.
- Do not manufacture measure/step timing or musical placement.
- Do not weaken analyzer-quality thresholds.
- Keep Lead/Bass legacy behavior unchanged until replacements are independently proven.
- Keep polished PDF as safe fallback.
- Preview and full PDF must derive from the same authenticated analysis result.
- Pre-Production professional-renderer activation must remain Preview-only and branch/deployment-scoped.
- Keep Production promotion disabled until a separate explicit decision.
