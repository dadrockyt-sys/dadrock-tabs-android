# CURRENT STATE — DadRock `/ai-tab` End-to-End Construction

Updated: 2026-08-22 20:17 CDT
Branch: `v143-contextual-prune-lobo`

# PROJECT FOCUS

> `dadrocktabs.com/ai-tab`: user uploaded audio → Bass / Lead / Rhythm choice → requested-part separation/processing → notes + playable positions + techniques + timing + metadata → authenticated musical events → professional preview TAB PDF → purchased/unlocked professional full TAB PDF.

Preview and full PDF must derive from the same authenticated analysis. Browser/PDF code must never manufacture missing musical placement.

Detailed product map: `docs/checkpoints/AI_TAB_END_TO_END_CONSTRUCTION.md`

# FINAL PRODUCT ARCHITECTURE

One shared instrument-agnostic core plus three separate engines:

```text
analyzer/final_product/
  shared/
  rhythm/
  lead/
  bass/
```

Rhythm is the proven architectural template, not the universal musical model. Bass and Lead own their own Hz/pitch behavior, training/models, candidate selection, fretboard rules, techniques, quality gates, output identity, and rendering rules.

Bass uses a true Demucs `Bass` stem and four-string `G-D-A-E` mapping. Lead and Rhythm both begin from separated Guitar views and then diverge into instrument-specific analysis.

# SAFETY / RESUME

Resume **only** on `v143-contextual-prune-lobo`.

Do not modify `main`, merge this branch, alter/deploy live V143 Modal, automatically promote Production, make payment, redeem customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as structured professional output.

Save this file after every meaningful boundary or diagnostic result.

---

# RHYTHM PROFESSIONAL CORE — PASSED

Approved fixture: `public/gomywayfullaitest.m4a`

Analyzer evidence: `debug/v143-contextual-prune/ai-tab-real-audio-canary.json`

Bot evidence commit: `9f52bf83597e921da12887874bace0df0ffe6d47`

Key proof:

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

PDF evidence: `debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`

```text
passed: true
renderEventCount: 358
maximumMeasure: 113
fullPageCount: 4
previewPageCount: 4
```

---

# RHYTHM LOCAL BUILT-NEXT HTTP BOUNDARY — CLOSED GREEN

The no-cache CI gate completed and committed final evidence.

Evidence:

```text
debug/v143-contextual-prune/ai-tab-nocache-gate.json
debug/v143-contextual-prune/next-preview-route-smoke-nocache.json
```

Bot evidence commit:

`5b29c0c3df3c97c0f4962e058997b2134d0179b7` — `Record V143 no-cache route gate`

Final gate:

```text
nodeSetupCacheEnabled: false
analyzerQualityVerifierExitCode: 0
previewFeatureVerifierExitCode: 0
installExitCode: 0
nextBuildExitCode: 0
serverReady: true
routeSmokeExitCode: 0
routeVerifierPassed: true
passed: true
actualVercelPreviewDeployment: false
vercelDeploymentAttempted: false
liveEndpointDeployedOrModified: false
productionModified: false
productionPromotionAuthorized: false
```

Built-Next route proof:

```text
/ai-tab status: 200
structured status: 200
structured feature: v143-branch-preview-canary
structured renderer: v143-structured-rhythm
fallback status: 200
fallback renderer: polished-safe-fallback
missing-tab HTTP 400 validation: passed
passed: true
```

Conclusion: local Rhythm application wiring is closed green. Previous missing evidence was a CI harness/visibility problem, not dependency installation or a DadRock regression.

---

# WHOLE-PRODUCT CUSTOMER CONTRACT — PASSED

Evidence: `debug/v143-contextual-prune/ai-tab-end-to-end-contract.json`

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

Never automate the real full-PDF unlock route during validation because it can trigger payment/token/email side effects.

---

# FINAL-PRODUCT FOLDER SCAFFOLD — CREATED

The physical shared/Rhythm/Lead/Bass organization now exists under:

`analyzer/final_product/`

Bass currently includes separate `hz_features/` and `training/` areas. These folders establish ownership boundaries only; they do not activate customer routing or professional identity.

---

# BASS PROFESSIONAL TRACK — INACTIVE CONTRACTS PASSED

## Separation scaffold

Evidence: `debug/v143-contextual-prune/bass-professional-separator-scaffold.json`

Bot commit: `70c5411d2e72f06923e88075e6f48f9555a8c0e5`

```text
passed: true
directPath: audio -> Demucs6s Bass
cascadePath: audio -> BS-RoFormer Instrumental -> Demucs6s Bass
deterministicSeed: 143
diagnosticOnly: true
analyzerRoutingEnabled: false
professionalStructuredIdentityEnabled: false
```

## Four-string render-contract scaffold

Evidence: `debug/v143-contextual-prune/bass-professional-render-contract.json`

Bot evidence commit: `4bd524c79feb621c497d8917128b36e971d85d1b`

```text
passed: true
tuning: Standard Bass
stringLabels: G, D, A, E
openMidi: 43, 38, 33, 28
stringCount: 4
maximumFret: 24
pitchStringFretConsistencyRequired: true
pdfRendererEnabled: false
analyzerRoutingEnabled: false
professionalStructuredIdentityEnabled: false
```

## Bass quality-gate scaffold

Evidence: `debug/v143-contextual-prune/bass-professional-quality-scaffold.json`

Bot evidence commit: `4afc8e529f0098993f8a8e3fffa2c493eca747d7`

Synthetic fail-closed contract passed; legacy untimed input fails timing coverage. Thresholds remain 70% minimum for render survival, playable string/fret, timing, pitch validity, and pitch/string/fret consistency.

Historical `bass_technique_diagnostics_v7.py` is reference-guided diagnostic logic and must not be reused as the new reference-free Bass professional engine.

---

# LIVE STEP — ISOLATED BASS REAL-AUDIO CANARY

Rhythm is closed green, so the next allowed boundary has started: real-audio Bass separation + reference-free pitch evidence only.

New files:

```text
analyzer/bass_real_audio_canary_modal.py
analyzer/verify_bass_real_audio_canary.py
.github/workflows/bass-real-audio-canary.yml
```

Commits:

```text
36809663be076815f5c4e9297201120790b38850 — Add isolated Bass real-audio canary
9933233638615ec6021228a78ad0a55f435c1cc5 — Add Bass real-audio canary verifier
9b50bb6c6049f16febfc75d9b2f70c089700ce72 — Run isolated Bass real-audio canary
```

The canary is locked to `public/gomywayfullaitest.m4a` and runs only ephemeral Modal research using the frozen V143 execution image. It does **not** deploy/modify a live Modal endpoint.

It evaluates both approved Bass views:

```text
direct: audio -> Demucs6s Bass
cascade: audio -> BS-RoFormer Instrumental -> Demucs6s Bass
```

Verifier requires non-empty real stems, valid audio, Bass-band energy, active pitch frames, playable Bass-range median/pitches, deterministic seed 143, and all safety flags false.

This boundary deliberately does **not** claim note placement, timing, techniques, professional quality, structured Bass identity, PDF rendering, training, customer routing, Vercel deployment, Production modification, purchase, token redemption, or email.

Expected committed evidence:

```text
debug/v143-contextual-prune/bass-real-audio-canary-action.json
debug/v143-contextual-prune/bass-real-audio-canary.json
```

Latest check: neither evidence file has landed yet. Branch HEAD remains `9b50bb6c6049f16febfc75d9b2f70c089700ce72`, so do not infer pass/fail yet.

Immediate next action: poll branch/evidence. If evidence lands, inspect exact fields. If it passes, advance only to isolated Bass event/note/timing analysis. If it fails, diagnose only the failing metric or harness phase without weakening thresholds or safety.

---

# VERCEL PREVIEW BLOCKER

No exact-branch Vercel Preview exists yet.

`debug/v143-contextual-prune/vercel-preview-deploy-action.json` still shows GitHub Actions lacks the Vercel token required for exact-branch Preview deployment. Do not use the connected Vercel deploy action merely to obtain a URL because it cannot guarantee the exact branch source.

---

# NEXT BOUNDARIES

1. Read Bass real-audio canary action/result evidence when it lands.
2. If separation + reference-free pitch passes, build isolated Bass candidate/event/timing analysis while routing/PDF identity remain disabled.
3. Prove four-string mapping + note/timing quality against real audio through the existing Bass quality gate.
4. Only after real-audio analysis is green, add Bass-specific technique evidence and professional four-string PDF validation.
5. Keep Bass customer routing, structured identity, and PDF activation disabled until the entire Bass chain is independently proven.
6. Lead remains legacy and will later get its own separated-Guitar melodic/solo engine, Hz/pitch trajectory logic, training, techniques, quality gate, and renderer.
