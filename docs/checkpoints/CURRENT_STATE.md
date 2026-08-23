# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — Bass separation/pitch canary closed green
Branch: `v143-contextual-prune-lobo`

## Product contract

`dadrocktabs.com/ai-tab`: uploaded audio → Bass / Lead / Rhythm → instrument processing → authenticated musical events → professional preview TAB PDF → purchased/unlocked full professional TAB PDF.

Preview/full PDF must derive from the same authenticated analysis. Browser/PDF code must never invent missing musical placement.

Final architecture is one shared instrument-agnostic core plus separate Rhythm / Lead / Bass engines under `analyzer/final_product/`. Rhythm is the proven architectural template only; Bass and Lead own their own musical logic, features/models/training, candidate selection, fretboard rules, techniques, quality gates, output identity, and renderers.

## Safety / resume

Resume **only** on `v143-contextual-prune-lobo`.

Never modify `main`, merge this branch, alter/deploy live V143 Modal, automatically promote Production, make payment, redeem a customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as professional structured output.

Save this file frequently after meaningful work and during long CI waits.

## Rhythm — CLOSED GREEN

Approved fixture: `public/gomywayfullaitest.m4a`.

Professional analyzer evidence: `debug/v143-contextual-prune/ai-tab-real-audio-canary.json`.

Key proof: `passed:true`, `analysisEngine:v143-reference-free-rhythm`, 358 valid render events, 100% render survival/playability/placement/pitch validity, 112 unique measures, 25 technique events, 358 sustain coverage, tempo ~129.199 BPM, 4/4, E Standard.

PDF evidence: `debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`, `passed:true`, 358 events, maximum measure 113, 4 full pages, 4 preview pages.

Local built-Next HTTP gate is closed green. Evidence:

- `debug/v143-contextual-prune/ai-tab-nocache-gate.json`
- `debug/v143-contextual-prune/next-preview-route-smoke-nocache.json`

Bot evidence commit: `5b29c0c3df3c97c0f4962e058997b2134d0179b7`.

Whole-product customer contract passed at `debug/v143-contextual-prune/ai-tab-end-to-end-contract.json`. Lead and Bass remain legacy/fail-closed; no missing placement is manufactured.

## Bass — inactive contracts green

Bass uses true Demucs `Bass` separation and standard four-string `G-D-A-E` mapping.

Existing green scaffolds/evidence:

- separator: `debug/v143-contextual-prune/bass-professional-separator-scaffold.json`
- render contract: `debug/v143-contextual-prune/bass-professional-render-contract.json`
- quality scaffold: `debug/v143-contextual-prune/bass-professional-quality-scaffold.json`

Exact reusable contracts:

- `lib/bassProfessionalRenderContract.js`
- `lib/bassProfessionalQuality.js`
- `analyzer/verify_bass_professional_quality_gate.mjs`
- `.github/workflows/bass-professional-quality-scaffold.yml`
- `analyzer/final_product/bass/hz_features/bass_frequency_profile.py`

Render contract requires `measure >= 1`, `step 0..15`, `stringIndex 0..3`, fret `0..24`, MIDI, and exact `openMidi[stringIndex] + fret == midi` with open MIDI `[43,38,33,28]` for `G,D,A,E`.

Quality thresholds remain fail-closed: minimum 4 valid render events and 70% minimum render survival, playable string/fret, timing coverage, pitch validity, and pitch/string/fret consistency.

Historical `bass_technique_diagnostics_v7.py` is reference-guided and must **not** be reused as the reference-free professional Bass engine.

## Bass real-audio separation + pitch — CLOSED GREEN

A first run failed only at the CI/Modal import harness. Diagnosis is preserved at:

- `debug/v143-contextual-prune/bass-real-audio-canary-failure-diagnostic.json`

Harness fixes:

- `885b90a741d922143bfd83e8d0c376d13a0c4582` — mount `v143_modal_live_endpoint` in the ephemeral canary image.
- `9973e30af77f0c8bbccbc9ec9960ccd858f895aa` — clean the checkout before evidence rebase/commit.

Superseding run `32611529763` passed completely. Evidence:

- `debug/v143-contextual-prune/bass-real-audio-canary-action.json`
- `debug/v143-contextual-prune/bass-real-audio-canary.json`

Action proof:

```text
modalCredentialsAvailableInGitHubActions: true
modalExitCode: 0
rawCanaryOutputPresent: true
verifierExitCode: 0
canaryEvidencePresent: true
```

Real-audio proof on `public/gomywayfullaitest.m4a`:

```text
passed: true
realAudioBassSeparationPassed: true
realAudioBassPitchEvidencePassed: true
realAudioBassCanaryPassed: true
stemsDistinct: true
deterministicSeed: 143
```

Direct Bass view:

```text
duration: 211.4409 s
sampleRate: 44100
channels: 2
bassBand30To1000HzPercent: 99.9866
activePitchFrameCount: 6942
medianFundamentalHz: 74.0637
playableRangeFramePercent: 99.7263
```

Cascade Bass view:

```text
duration: 211.4409 s
sampleRate: 44100
channels: 2
bassBand30To1000HzPercent: 99.9864
activePitchFrameCount: 6943
medianFundamentalHz: 74.0633
playableRangeFramePercent: 99.6975
```

All safety checks passed. Training, customer routing, structured Bass identity, PDF renderer, live Modal modification, Vercel deployment, Production modification/promotion, payment, token redemption, and email remain disabled/false.

This canary proves **only real Bass separation + reference-free pitch plausibility**. It explicitly does not prove note placement, timing, techniques, or full professional Bass quality.

## LIVE STEP — isolated Bass candidate / note / timing boundary

Advance exactly one boundary now: derive reference-free Bass note candidates from the two proven Bass stems, authenticate them onto the reference-free 4/4 timing grid, map them to valid four-string `G-D-A-E` positions, and evaluate those real-audio events through the existing fail-closed Bass render/quality contract.

Requirements:

- Bass-specific range only: MIDI 28..67 / ~41.203..391.995 Hz.
- Candidate evidence must come from audio, not song labels/reference TAB.
- Prefer cross-view direct+cascade consensus for authenticated note candidates.
- Timing must come from `analyzer/v143_reference_free_timing.py` or equivalent reference-free audio evidence.
- Every accepted event must contain real `measure`, `step`, MIDI, `stringIndex`, and fret with exact `openMidi[stringIndex] + fret == midi`.
- No techniques in this boundary beyond optional neutral sustain duration metadata.
- Keep training, routing, structured Bass identity, PDF rendering, live endpoint, Vercel, Production, payment/token/email disabled.
- Do not weaken the existing 70% Bass quality thresholds.

## Immediate next action

1. Implement isolated Bass-specific candidate/timing logic and a real-audio canary/verifier.
2. Run it on the same approved fixture using the proven direct/cascade Bass separation substrate.
3. Validate the generated events with the existing Bass professional render/quality contract.
4. If green, close note/timing/playability only; techniques and professional PDF remain separate future boundaries.
5. Exact-branch Vercel Preview remains an external blocker.
