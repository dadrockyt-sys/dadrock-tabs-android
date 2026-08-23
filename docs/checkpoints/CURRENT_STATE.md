# CURRENT STATE — DadRock `/ai-tab` End-to-End Construction

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`

# PROJECT FOCUS — `dadrocktabs.com/ai-tab` end to end

> **User uploaded audio → Bass / Lead / Rhythm selection → `app/ai-tab/page.js` → requested-part separation/processing → notes + playable positions + techniques + timing + metadata → authenticated musical events → professional preview TAB PDF → purchased/unlocked professional full TAB PDF.**

The finished product must support all three instrument choices. Preview and purchased full PDF must derive from the same authenticated analysis. Browser/PDF code must never manufacture missing musical placement.

Detailed whole-product roadmap:

`docs/checkpoints/AI_TAB_END_TO_END_CONSTRUCTION.md`

---

# RESUME / SAFETY DIRECTIVE

Resume **only** on `v143-contextual-prune-lobo`.

Never:

- modify `main` or merge this branch into `main`;
- deploy/modify the live V143 Modal endpoint during this validation;
- automatically promote/enable Production;
- make a payment, redeem a customer token, or send customer email in automated tests;
- manufacture timing/measure/step data;
- weaken analyzer quality thresholds merely to pass a gate;
- relabel legacy Lead/Bass output as professional structured output.

Keep this file continuously current after meaningful steps/results. A new chat should be able to resume from this file alone.

---

# LIVE CURRENT STEP — staged built-Next Rhythm HTTP gate

Authoritative workflow:

`.github/workflows/v143-ai-tab-branch-build-gate.yml`

Authoritative source:

`22dc06af353220006a7558c6b9ba0c262cc64cb8` — `Add staged diagnostics to V143 branch gate`

The earlier `4c9c33b...` run was superseded because it remained opaque for >20 minutes. Do not follow its old schema-4 heartbeat.

## Current staged evidence — POST-VERIFIERS PASSED

Route heartbeat:

`debug/v143-contextual-prune/next-preview-route-smoke.json`

```text
schemaVersion: 5
sourceCommit: 22dc06af353220006a7558c6b9ba0c262cc64cb8
phase: started-staged-branch-gate
localNextPreviewSimulation: true
actualVercelPreviewDeployment: false
productionModified: false
productionPromotionAuthorized: false
```

Progress evidence:

`debug/v143-contextual-prune/branch-gate-progress.json`

Latest result:

```text
schemaVersion: 2
sourceCommit: 22dc06af353220006a7558c6b9ba0c262cc64cb8
phase: post-verifiers
analyzerQualityVerifierExitCode: 0
previewFeatureVerifierExitCode: 0
installExitCode: null
nextBuildExitCode: null
localNextPreviewSimulation: true
actualVercelPreviewDeployment: false
vercelDeploymentAttempted: false
liveEndpointDeployedOrModified: false
productionModified: false
productionPromotionAuthorized: false
```

**Interpretation:** GitHub Actions runner is healthy. Analyzer-quality and Preview feature regressions both pass. The previous long delay is now isolated to a later phase, not these product gates.

## Immediate next step

Fetch `debug/v143-contextual-prune/branch-gate-progress.json` again and follow the staged phases:

```text
post-verifiers → post-install → post-build → final HTTP evidence
```

At `post-install` require:

```text
installExitCode: 0
```

At `post-build` require:

```text
installExitCode: 0
nextBuildExitCode: 0
```

Final route evidence must become:

```text
phase: complete-by-staged-branch-gate
installExitCode: 0
nextBuildExitCode: 0
serverReady: true
routeSmokeExitCode: 0
passed: true
actualVercelPreviewDeployment: false
productionModified: false
productionPromotionAuthorized: false
```

Required structured response:

```text
HTTP 200
Content-Type: application/pdf
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: v143-structured-rhythm
```

Required fallback response:

```text
HTTP 200
Content-Type: application/pdf
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: polished-safe-fallback
```

Missing generated tab must return HTTP 400.

### Staged gate bounds

```text
overall: 35 minutes
analyzer verifier: 120s
Preview feature verifier: 120s
npm ci: 600s
Next build: 600s
server readiness: 60s
route smoke: 300s
```

If a later phase returns `124`, that command hit its hard timeout. Diagnose that phase only; do not weaken product assertions.

---

# WHOLE-PRODUCT CONTRACT — PASSED

Verifier:

`analyzer/verify_ai_tab_end_to_end_contract.mjs`

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
productionModified: false
productionPromotionAuthorized: false
```

Key commits:

- `97ec364c257b516949e2c2be8a94c24cb0ed0d39` — initial bot evidence.
- `8784cbb734928ff8284cc17d6c41f0844c7fbe22` — Preview/full renderer parity guard.

**Conclusion:** customer application wiring is proven for Bass, Lead, and Rhythm. The remaining parity gap is professional analyzer/separation/event quality, not page wiring.

---

# RHYTHM PROFESSIONAL TRACK — PROVEN ANALYZER/PDF CORE

Approved fixture:

`public/gomywayfullaitest.m4a`

Real-audio evidence:

`debug/v143-contextual-prune/ai-tab-real-audio-canary.json`

Bot evidence commit:

`9f52bf83597e921da12887874bace0df0ffe6d47`

Key result:

```text
passed: true
analysisEngine: v143-reference-free-rhythm
referenceFree: true
modalGpu: L4
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
```

Structured identity remains fail-closed on `liveV143.referenceFree === true` plus analyzer quality and surviving structured events.

---

# BASS PROFESSIONAL TRACK — INACTIVE SEPARATION SCAFFOLD PASSED

Files:

```text
analyzer/bass_professional_separator_scaffold.py
analyzer/verify_bass_professional_separator_scaffold.py
.github/workflows/bass-professional-separator-scaffold.yml
```

Evidence:

`debug/v143-contextual-prune/bass-professional-separator-scaffold.json`

Bot evidence:

`70c5411d2e72f06923e88075e6f48f9555a8c0e5`

```text
passed: true
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
productionModified: false
productionPromotionAuthorized: false
```

Do **not** route customer Bass traffic to this scaffold yet. Next Bass milestone is an isolated approved real-audio separation/analysis canary only after the current Rhythm integration gate is resolved.

Important architecture distinction:

- Bass has a true Demucs `Bass` stem.
- Lead and Rhythm both exist inside the separated `Guitar` stem. A future Lead path needs Lead-specific musical analysis/selection on guitar views, not a fictitious Lead stem.

---

# VERCEL PREVIEW BLOCKER

No exact-branch Vercel Preview is available yet.

Project:

```text
project: dadrock-tabs-android
projectId: prj_6biwsn0iHci6FHNswAUCS8UYrAqF
teamId: team_qJrw8Cuze5bCEg9M3Q67XMWt
node: 24.x
```

Fail-closed workflow:

`.github/workflows/v143-vercel-preview-deploy.yml`

Latest evidence:

`debug/v143-contextual-prune/vercel-preview-deploy-action.json`

```text
vercelTokenAvailableInGitHubActions: false
previewConfigPullExitCode: 99
previewBuildExitCode: 99
previewDeployExitCode: 99
deploymentUrl: null
productionDeployFlagUsed: false
productionModified: false
productionPromotionAuthorized: false
```

Do not use the connected Vercel deploy action merely to obtain a URL because it does not expose an exact source branch/ref.

---

# NEXT AFTER STAGED LOCAL HTTP PASS

1. Mark local built-Next Rhythm application wiring closed.
2. Leave real Vercel Preview deployment/environment integration as the remaining Rhythm application blocker.
3. When a supported Vercel CLI token exists, rerun the fail-closed Preview deployment workflow.
4. Confirm target is Preview before requests.
5. Validate `/ai-tab` and `/api/generate-tab-preview` first.
6. Only after deployed route + runtime-key proof, consider actual browser upload using `public/gomywayfullaitest.m4a`.
7. Do not automate `/api/generate-tab-pdf` because unlock verification can cause payment/token/email side effects.
8. After Rhythm application integration is closed, advance Bass real-audio professional canary and then a separate Lead professional track.
