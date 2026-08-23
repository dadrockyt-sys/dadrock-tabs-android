# CURRENT STATE — DadRock `/ai-tab` End-to-End Construction

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`

# PROJECT FOCUS

> **`dadrocktabs.com/ai-tab`: user uploaded audio → Bass / Lead / Rhythm choice → `app/ai-tab/page.js` → requested-part separation/processing → notes + playable positions + techniques + timing + metadata → authenticated musical events → professional preview TAB PDF → purchased/unlocked professional full TAB PDF.**

Preview and purchased full PDF must derive from the same authenticated analysis. Browser/PDF code must never manufacture missing musical placement.

Detailed product map:

`docs/checkpoints/AI_TAB_END_TO_END_CONSTRUCTION.md`

# FINAL PRODUCT ARCHITECTURE — SHARED CORE + SEPARATE RHYTHM / LEAD / BASS ENGINES

The intended final production structure is **one shared core plus three separate instrument-specific final-product folders/engines**. Rhythm is the proven reference architecture/template, but Lead and Bass must remain independently trainable and instrument-specific rather than becoming copies of Rhythm musical assumptions.

Target organization:

```text
analyzer/final_product/
  shared/
    audio_normalization/
    request_adapter/
    timing_grid/
    event_schema/
    metadata/
    quality_metrics/
    common_evidence/
    shared_safety/

  rhythm/
    separation/
    hz_features/
    candidate_detection/
    fretboard_mapping/
    timing/
    techniques/
    model/
    training/
    output/
    quality_gate/

  lead/
    separation/
    hz_features/
    candidate_detection/
    fretboard_mapping/
    timing/
    techniques/
    model/
    training/
    output/
    quality_gate/

  bass/
    separation/
    hz_features/
    candidate_detection/
    fretboard_mapping/
    timing/
    techniques/
    model/
    training/
    output/
    quality_gate/
```

Professional rendering should follow the same separation of concerns:

```text
pdf/shared/
pdf/rhythm/
pdf/lead/
pdf/bass/
```

Architecture rules:

1. **Rhythm is the implementation template, not the universal musical model.** Reuse its proven pipeline shape to reduce workload: separation/views → Hz/pitch evidence → candidates → timing → playable position → technique evidence → authenticated events → quality gate → professional PDF.
2. **Shared code should contain only genuinely instrument-agnostic behavior** such as audio normalization, request handling, timing/grid utilities, common event schema, metadata transport, evidence/safety helpers, and reusable PDF layout primitives.
3. **Each instrument owns its own Hz/frequency behavior, training data, model/checkpoints, candidate selection, fretboard mapping, techniques, quality thresholds, output identity, and instrument-specific rendering rules.** This intentionally permits independent Bass and Lead training without changing the frozen/proven Rhythm engine.
4. **Bass has a real separate Bass stem.** The professional Bass path should use deterministic Demucs `Bass` separation (including the already scaffolded paired direct/cascade views), four-string `G-D-A-E` mapping, Bass-specific Hz ranges/features, Bass training, Bass techniques, Bass quality gate, and a true four-string professional TAB renderer.
5. **Lead and Rhythm both begin from separated Guitar views, not imaginary Lead/Rhythm stems.** Lead and Rhythm may reuse the same deterministic Guitar separation substrate, but they must diverge after separation: Rhythm keeps its chord/riff-oriented V143 analysis while Lead gets Lead-specific melodic/solo selection, Hz/pitch trajectory logic, fretboard movement, bends/releases/vibrato/slides/legato emphasis, Lead training, and its own quality gate.
6. **Separate model/training evolution is allowed and expected.** Future Bass or Lead Hz features, datasets, learned weights/checkpoints, technique models, and tuning-specific behavior must be able to evolve independently without retraining or modifying the proven Rhythm engine.
7. **No instrument earns structured professional identity merely by matching the folder shape.** Lead and Bass remain fail-closed until each independently passes real-audio separation/analysis quality, authenticated timing/playability, technique evidence, preview/full PDF evidence, and its own conservative quality gate.
8. **Do not duplicate shared infrastructure unnecessarily.** The goal of the folder split is to reduce workload and prevent cross-instrument regressions while preserving independent musical intelligence where it matters.

Concise final architecture:

> **Shared DadRock core + Rhythm engine + Lead engine + Bass engine. Rhythm supplies the proven architectural pattern; Bass and Lead get their own Hz analysis, training/models, techniques, fretboard rules, quality gates, identities, and final renderers.**

# SAFETY / RESUME

Resume **only** on `v143-contextual-prune-lobo`.

Do not modify `main`, merge this branch, alter/deploy live V143 Modal, automatically promote Production, make payment, redeem customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as structured professional output.

Keep this file continuously current after meaningful results.

---

# LIVE STEP — STAGED RHYTHM BUILT-NEXT HTTP GATE

Workflow:

`.github/workflows/v143-ai-tab-branch-build-gate.yml`

Authoritative source:

`22dc06af353220006a7558c6b9ba0c262cc64cb8` — `Add staged diagnostics to V143 branch gate`

The obsolete `4c9c33b...` >20-minute opaque run was superseded. Follow only source `22dc06a...` or a later staged source.

Current heartbeat:

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

Current staged progress:

`debug/v143-contextual-prune/branch-gate-progress.json`

```text
schemaVersion: 2
sourceCommit: 22dc06af353220006a7558c6b9ba0c262cc64cb8
phase: post-verifiers
analyzerQualityVerifierExitCode: 0
previewFeatureVerifierExitCode: 0
installExitCode: null
nextBuildExitCode: null
productionModified: false
productionPromotionAuthorized: false
```

**Meaning:** runner is healthy; analyzer-quality and Preview feature regressions pass. The workflow is currently in the Node-24 setup/install portion.

Staged phases:

```text
post-verifiers → post-install → post-build → final HTTP evidence
```

Immediate next action: fetch `branch-gate-progress.json` and require `post-install` with `installExitCode:0`, then `post-build` with `nextBuildExitCode:0`.

Final route proof must show:

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

Required structured Preview headers:

```text
X-Jimmy-PAIge-PDF-Feature: v143-branch-preview-canary
X-Jimmy-PAIge-PDF-Renderer: v143-structured-rhythm
```

Required fallback renderer:

`polished-safe-fallback`

Missing generated tab must return HTTP 400.

Hard bounds:

```text
overall 35m
verifiers 120s each
npm ci 600s
Next build 600s
server readiness 60s
route smoke 300s
```

Exit `124` means that phase hit its hard timeout. Diagnose only the failing phase; do not weaken assertions.

---

# WHOLE-PRODUCT CUSTOMER CONTRACT — PASSED

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

Preview and purchased/full routes are contract-proven to share `getJimmyPaigeProfessionalPdfFeatureState(...)` and `createJimmyPaigeProfessionalPdf(...)`.

---

# RHYTHM PROFESSIONAL CORE — PASSED

Approved fixture:

`public/gomywayfullaitest.m4a`

Analyzer evidence:

`debug/v143-contextual-prune/ai-tab-real-audio-canary.json`

Bot evidence:

`9f52bf83597e921da12887874bace0df0ffe6d47`

Key results:

```text
passed: true
analysisEngine: v143-reference-free-rhythm
referenceFree: true
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
```

PDF evidence:

`debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`

```text
passed: true
renderEventCount: 358
maximumMeasure: 113
fullPageCount: 4
previewPageCount: 4
```

---

# BASS PROFESSIONAL TRACK — INACTIVE SCAFFOLDS PASSED

## Separation scaffold

Evidence:

`debug/v143-contextual-prune/bass-professional-separator-scaffold.json`

Bot commit:

`70c5411d2e72f06923e88075e6f48f9555a8c0e5`

```text
passed: true
directPath: audio -> Demucs6s Bass
cascadePath: audio -> BS-RoFormer Instrumental -> Demucs6s Bass
deterministicSeed: 143
diagnosticOnly: true
analyzerRoutingEnabled: false
professionalStructuredIdentityEnabled: false
realAudioBassCanaryPassed: false
```

## Four-string render-contract scaffold

Files:

```text
lib/bassProfessionalRenderContract.js
analyzer/verify_bass_professional_render_contract.mjs
.github/workflows/bass-professional-render-contract.yml
```

Bot evidence commit:

`4bd524c79feb621c497d8917128b36e971d85d1b` — `Record Bass professional render scaffold`

Evidence:

`debug/v143-contextual-prune/bass-professional-render-contract.json`

```text
passed: true
tuning: Standard Bass
stringLabels: G, D, A, E
openMidi: 43, 38, 33, 28
stringCount: 4
maximumFret: 24
stepsPerMeasure: 16
validFixtureEvents: 4
projectedFixtureEvents: 4
invalidFixtureEventsRejected: 5
pitchStringFretConsistencyRequired: true
diagnosticOnly: true
productionCandidate: false
pdfRendererEnabled: false
analyzerRoutingEnabled: false
professionalStructuredIdentityEnabled: false
realAudioBassCanaryPassed: false
productionModified: false
productionPromotionAuthorized: false
```

**Important:** this prevents future Bass output from being incorrectly engraved on the six-string Rhythm/Guitar staff. No Bass PDF renderer is enabled yet.

Historical `bass_technique_diagnostics_v7.py` was reviewed and explicitly identifies itself as `reference-guided-bass-technique-diagnostic-only`; do not reuse that label-guided logic in the new reference-free Bass professional path.

Architecture distinction:

- Bass has a true Demucs `Bass` stem.
- Lead and Rhythm both live in the separated `Guitar` stem; future Lead needs Lead-specific analysis/selection, not a fake Lead stem.

---

# VERCEL PREVIEW BLOCKER

No exact-branch Vercel Preview exists yet.

`debug/v143-contextual-prune/vercel-preview-deploy-action.json` still shows:

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

Do not use the connected Vercel deploy action merely to obtain a URL because it cannot guarantee the exact branch source.

---

# NEXT BOUNDARIES

1. Finish the staged Rhythm built-Next HTTP gate.
2. If it passes, mark local Rhythm application wiring closed; real Vercel Preview integration remains external blocker.
3. Only after the Rhythm integration boundary is closed, advance Bass from inactive contracts to an isolated approved real-audio separation/analysis canary.
4. Keep Bass routing, Bass structured identity, and Bass PDF renderer disabled until real-audio quality is proven.
5. Lead remains legacy; future professional Lead should use separated guitar views plus Lead-specific analysis/selection.
6. Never automate the real full-PDF unlock route during validation because it can trigger payment/token/email side effects.
