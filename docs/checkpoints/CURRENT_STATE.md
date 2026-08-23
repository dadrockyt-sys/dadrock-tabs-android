# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — Bass event/timing canary active
Branch: `v143-contextual-prune-lobo`

## Product contract / safety

`dadrocktabs.com/ai-tab`: uploaded audio → Bass / Lead / Rhythm → instrument processing → authenticated musical events → professional preview TAB PDF → purchased/unlocked full professional TAB PDF.

Preview/full PDF must derive from the same authenticated analysis. Browser/PDF code must never invent missing musical placement.

Resume **only** on `v143-contextual-prune-lobo`.

Never modify `main`, merge this branch, alter/deploy live V143 Modal, automatically promote Production, make payment, redeem a customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as professional structured output.

Save this file frequently after meaningful work and during long CI waits.

## Rhythm — CLOSED GREEN

Approved fixture: `public/gomywayfullaitest.m4a`.

Professional analyzer evidence: `debug/v143-contextual-prune/ai-tab-real-audio-canary.json`.

Key proof: `passed:true`, `analysisEngine:v143-reference-free-rhythm`, 358 valid render events, 100% render survival/playability/placement/pitch validity, 112 unique measures, 25 technique events, 358 sustain coverage, tempo ~129.199 BPM, 4/4, E Standard.

PDF evidence: `debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json`, `passed:true`, 358 events, maximum measure 113, 4 full pages, 4 preview pages.

Local built-Next HTTP gate is closed green at bot evidence commit `5b29c0c3df3c97c0f4962e058997b2134d0179b7`. Whole-product customer contract passed at `debug/v143-contextual-prune/ai-tab-end-to-end-contract.json`.

## Bass base contracts — GREEN / INACTIVE

Bass uses true Demucs `Bass` separation and standard four-string `G-D-A-E` mapping.

Green prerequisites:

- `debug/v143-contextual-prune/bass-professional-separator-scaffold.json`
- `debug/v143-contextual-prune/bass-professional-render-contract.json`
- `debug/v143-contextual-prune/bass-professional-quality-scaffold.json`
- `lib/bassProfessionalRenderContract.js`
- `lib/bassProfessionalQuality.js`
- `analyzer/final_product/bass/hz_features/bass_frequency_profile.py`

Render contract requires authenticated `measure >= 1`, `step 0..15`, `stringIndex 0..3`, fret `0..24`, MIDI, and exact `openMidi[stringIndex] + fret == midi` with open MIDI `[43,38,33,28]` for `G,D,A,E`.

Quality thresholds remain unchanged/fail-closed: minimum 4 valid render events and 70% minimum render survival, playable string/fret, timing coverage, pitch validity, and pitch/string/fret consistency.

Historical `bass_technique_diagnostics_v7.py` is reference-guided and must **not** be reused as the reference-free professional Bass engine.

## Bass real-audio separation + pitch — CLOSED GREEN

Failure-harness diagnosis is preserved at `debug/v143-contextual-prune/bass-real-audio-canary-failure-diagnostic.json`. Harness fixes were commits `885b90a741d922143bfd83e8d0c376d13a0c4582` and `9973e30af77f0c8bbccbc9ec9960ccd858f895aa`.

Superseding run `32611529763` passed completely. Evidence:

- `debug/v143-contextual-prune/bass-real-audio-canary-action.json`
- `debug/v143-contextual-prune/bass-real-audio-canary.json`

Proof:

```text
modalExitCode: 0
verifierExitCode: 0
passed: true
realAudioBassSeparationPassed: true
realAudioBassPitchEvidencePassed: true
realAudioBassCanaryPassed: true
stemsDistinct: true
deterministicSeed: 143
```

Direct view: 211.4409 s, 44.1 kHz stereo, 99.9866% energy 30–1000 Hz, 6942 active pitch frames, median 74.0637 Hz, 99.7263% playable-range frames.

Cascade view: 211.4409 s, 44.1 kHz stereo, 99.9864% energy 30–1000 Hz, 6943 active pitch frames, median 74.0633 Hz, 99.6975% playable-range frames.

This proves only real Bass separation + reference-free pitch plausibility. Note/timing/techniques/full professional quality were not claimed.

## LIVE STEP — Bass candidate / note / timing / playability canary ACTIVE

Exactly one next boundary has been implemented. New files/commits:

- `929bbee6293a13a42ee7c7c43f0975a89d739fd9` — `analyzer/final_product/shared/timing_grid.py`; shared instrument-agnostic 4/4 subdivision grid and nearest-slot authentication.
- `812265864e30e2ac3cd56270f615f7d5fa540c27` — `analyzer/final_product/bass/candidate_detection/bass_candidate_timing.py`; Bass-only Basic Pitch range MIDI 28..67 / ~41.203..391.995 Hz, exact direct+cascade consensus, authenticated timing slots, deterministic four-string position selection.
- `daa695a66bf36d985467a30654bc7e06b5b54bc2` — `analyzer/bass_real_audio_event_timing_canary_modal.py`; isolated Modal real-audio orchestration using full-mix reference-free timing plus the two proven Bass stems.
- `26492e0fff05c50743e20fad8c5129742e38edf6` — `analyzer/verify_bass_real_audio_event_timing.mjs`; validates generated real-audio events through the existing Bass render contract and unchanged fail-closed quality gate.
- `370cdca101f983a5c11a3bbd53bb68724de9dc2f` — `.github/workflows/bass-real-audio-event-timing.yml`; isolated run + heartbeat + artifact + compact evidence commit + fail-closed enforcement.

Boundary rules:

- audio-derived candidates only; no song/reference TAB labels;
- exact direct+cascade MIDI consensus required;
- reference-free timing comes from `analyzer/v143_reference_free_timing.py`;
- every accepted event must carry real `measure`, `step`, MIDI, `stringIndex`, fret, and exact pitch-position consistency;
- no technique claim: every event carries an empty technique list in this boundary;
- existing 70% quality thresholds are reused unchanged;
- training/routing/structured identity/PDF/live/Vercel/Production/payment/token/email remain disabled.

Current GitHub Actions heartbeat:

```text
workflow: Bass Real Audio Event Timing
runId: 32611818648
sourceCommit: 370cdca101f983a5c11a3bbd53bb68724de9dc2f
startedAtUtc: 2026-08-23T02:02:29.507123+00:00
```

Heartbeat evidence: `debug/v143-contextual-prune/bass-real-audio-event-timing-start.json`.

Expected final evidence:

- `debug/v143-contextual-prune/bass-real-audio-event-timing-action.json`
- `debug/v143-contextual-prune/bass-real-audio-event-timing.json`

## Immediate next action

1. Poll run `32611818648` through completion.
2. Fetch action/result evidence and exact logs/artifact if any phase fails.
3. If green, close only candidate/note/timing/playability. Techniques remain the next separate boundary; professional Bass PDF/routing remain disabled.
4. If red, fix only the exact harness/metric without weakening thresholds or safety.
5. Exact-branch Vercel Preview remains an external blocker.
