# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 20:56 local
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

## LIVE STEP — isolated Bass real-audio canary harness fixed; rerun active

Run `32610329984` completed failure, but the failure was a harness/import failure and **did not evaluate Bass musical quality**.

Saved evidence:

- `debug/v143-contextual-prune/bass-real-audio-canary-action.json`
- `debug/v143-contextual-prune/bass-real-audio-canary-failure-diagnostic.json`

Exact diagnosis from the workflow artifact/log:

- Modal credentials were available.
- The remote function repeatedly failed during module hydration with `ModuleNotFoundError: No module named 'v143_modal_live_endpoint'` while importing `bass_real_audio_canary_modal.py`.
- The local Modal command then hit the explicit 1500-second timeout (`modalExitCode:124`), so no raw canary output existed and the verifier was correctly skipped (`verifierExitCode:99`).
- The compact evidence commit also failed because generated evidence left the checkout dirty before `git rebase` (`cannot rebase: You have unstaged changes`).
- No quality thresholds were changed and all training/routing/identity/PDF/live/Production/payment/token/email safety flags remained false.

Harness fixes committed:

- `885b90a741d922143bfd83e8d0c376d13a0c4582` — mounts `v143_modal_live_endpoint` in the ephemeral Bass canary image so the remote function module can hydrate.
- `9973e30af77f0c8bbccbc9ec9960ccd858f895aa` — preserves generated evidence in `/tmp`, restores a clean Git checkout before rebase, then restores/commits evidence after rebase.

Current superseding canary run:

- run ID: `32611529763`
- source commit: `9973e30af77f0c8bbccbc9ec9960ccd858f895aa`
- heartbeat started UTC: `2026-08-23T01:55:48.802605+00:00`
- heartbeat evidence: `debug/v143-contextual-prune/bass-real-audio-canary-start.json`

The canary remains locked to `public/gomywayfullaitest.m4a` and evaluates only:

- direct: audio → Demucs6s `Bass`
- cascade: audio → BS-RoFormer `Instrumental` → Demucs6s `Bass`

It uses ephemeral Modal research substrate only; it does not deploy/modify live Modal.

It proves separation + reference-free Bass pitch evidence only if green. It deliberately does **not** claim note placement, timing, techniques, professional quality, structured Bass identity, PDF rendering, training, routing, Vercel deployment, Production modification, purchase, token redemption, or email.

Expected final evidence:

- `debug/v143-contextual-prune/bass-real-audio-canary-action.json`
- `debug/v143-contextual-prune/bass-real-audio-canary.json`

A next-stage Bass candidate/timing design has been inspected but **no candidate-detection file has been committed yet**. Reusable reference-free timing logic exists in `analyzer/v143_reference_free_timing.py`; Guitar-specific `v143_candidate_timing_adapter.py` may be reused only structurally, not with Guitar pitch/range assumptions. The Bass candidate boundary must use MIDI 28..67 / ~41.203..391.995 Hz, preserve authenticated measure/step placement, and remain isolated from training/routing/identity/PDF activation.

## Immediate next action

1. Poll run `32611529763` through completion.
2. Fetch committed action/result evidence immediately when available.
3. If green, close only Bass separation + pitch and advance one boundary to isolated Bass candidate/note/timing analysis.
4. If it fails, inspect the exact new artifact/log and fix only that harness/metric; do not weaken thresholds or safety.
5. Exact-branch Vercel Preview remains an external blocker.
