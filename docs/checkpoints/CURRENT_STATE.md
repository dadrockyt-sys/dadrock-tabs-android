# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 21:38 EDT
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

## Bass — inactive contracts already green

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

## LIVE STEP — isolated Bass real-audio canary ACTIVE

Canary files:

- `analyzer/bass_real_audio_canary_modal.py`
- `analyzer/verify_bass_real_audio_canary.py`
- `.github/workflows/bass-real-audio-canary.yml`

Initial trigger commit `9b50bb6c6049f16febfc75d9b2f70c089700ce72` produced no visible branch evidence after the bounded workflow window, so the workflow was safely retriggered with an early heartbeat in commit:

- `751a30f0bb4b5310921d202a8026fcd9114aa652` — `Retrigger Bass canary with early run heartbeat`

Heartbeat evidence is committed:

- `debug/v143-contextual-prune/bass-real-audio-canary-start.json`
- GitHub Actions run ID: `32610329984`
- job ID: `97122230041`
- run attempt: `1`
- source commit: `751a30f0bb4b5310921d202a8026fcd9114aa652`
- started UTC: `2026-08-23T01:26:27.264028+00:00`

Latest direct job inspection at about 21:38 EDT: run `32610329984` remains `in_progress`. Checkout, heartbeat, Python setup, and Modal CLI install all passed. The active step is still `Run isolated real-audio Bass separator canary`; verifier/evidence/fail-closed enforcement remain pending. This is roughly 13 minutes into the run and still inside the remote/job timeout bounds. Do **not** infer pass/fail yet.

The canary is locked to `public/gomywayfullaitest.m4a` and evaluates only:

- direct: audio → Demucs6s `Bass`
- cascade: audio → BS-RoFormer `Instrumental` → Demucs6s `Bass`

It uses ephemeral Modal research substrate only; it does not deploy/modify live Modal.

It proves separation + reference-free Bass pitch evidence only if green. It deliberately does **not** claim note placement, timing, techniques, professional quality, structured Bass identity, PDF rendering, training, routing, Vercel deployment, Production modification, purchase, token redemption, or email.

Expected final evidence:

- `debug/v143-contextual-prune/bass-real-audio-canary-action.json`
- `debug/v143-contextual-prune/bass-real-audio-canary.json`

A next-stage Bass candidate/timing design was inspected but **no candidate-detection file has been committed yet**. Reusable reference-free timing logic exists in `analyzer/v143_reference_free_timing.py`; Guitar-specific `v143_candidate_timing_adapter.py` may be reused only structurally, not with Guitar pitch/range assumptions.

## Immediate next action

1. Poll GitHub Actions run `32610329984` / job `97122230041` until the current Modal separator step finishes.
2. Fetch `bass-real-audio-canary-action.json` and `bass-real-audio-canary.json` immediately when committed.
3. If green, close only the Bass separation + pitch boundary.
4. Then implement one isolated reference-free Bass candidate/note/timing boundary using Bass-specific playable range and the existing four-string contract. Keep training/routing/identity/PDF disabled.
5. If canary fails, diagnose only the exact failing harness/metric without weakening thresholds or safety.
6. Exact-branch Vercel Preview remains an external blocker.
