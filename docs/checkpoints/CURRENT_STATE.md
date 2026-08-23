# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — Bass note/timing/playability closed green
Branch: `v143-contextual-prune-lobo`

## Product contract / safety

`dadrocktabs.com/ai-tab`: uploaded audio → Bass / Lead / Rhythm → instrument processing → authenticated musical events → professional preview TAB PDF → purchased/unlocked full professional TAB PDF.

Preview/full PDF must derive from the same authenticated analysis. Browser/PDF code must never invent missing musical placement.

Resume **only** on `v143-contextual-prune-lobo`.

Never modify `main`, merge this branch, alter/deploy live V143 Modal, automatically promote Production, make payment, redeem a customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as professional structured output.

Save this file frequently after meaningful work and during long CI waits.

## Rhythm — CLOSED GREEN

Approved fixture: `public/gomywayfullaitest.m4a`.

Professional analyzer: `debug/v143-contextual-prune/ai-tab-real-audio-canary.json` — `passed:true`, 358 valid render events, 100% render survival/playability/placement/pitch validity, 112 unique measures, 25 technique events, 358 sustain coverage, tempo ~129.199 BPM, 4/4, E Standard.

PDF: `debug/v143-contextual-prune/ai-tab-real-audio-pdf-validation.json` — `passed:true`, 358 events, max measure 113, 4 full pages, 4 preview pages.

Local built-Next HTTP gate is green at `5b29c0c3df3c97c0f4962e058997b2134d0179b7`. Whole-product contract passed at `debug/v143-contextual-prune/ai-tab-end-to-end-contract.json`.

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

Evidence:

- `debug/v143-contextual-prune/bass-real-audio-canary-action.json`
- `debug/v143-contextual-prune/bass-real-audio-canary.json`

Run `32611529763`: Modal exit 0, verifier exit 0, `passed:true`, real separation true, pitch evidence true, distinct direct/cascade stems, deterministic seed 143. Both 211.44-second Bass views have ~99.99% 30–1000 Hz energy and ~99.7% playable-range pitch frames.

This proved only real Bass separation + reference-free pitch plausibility.

## Bass candidate / note / timing / playability — CLOSED GREEN

Implemented files:

- `analyzer/final_product/shared/timing_grid.py`
- `analyzer/final_product/bass/candidate_detection/bass_candidate_timing.py`
- `analyzer/bass_real_audio_event_timing_canary_modal.py`
- `analyzer/verify_bass_real_audio_event_timing.mjs`
- `.github/workflows/bass-real-audio-event-timing.yml`

Run `32611818648` completed **success**, including fail-closed enforcement.

Evidence:

- `debug/v143-contextual-prune/bass-real-audio-event-timing-action.json`
- `debug/v143-contextual-prune/bass-real-audio-event-timing.json`

Action proof:

```text
modalCredentialsAvailableInGitHubActions: true
modalExitCode: 0
rawCanaryOutputPresent: true
verifierExitCode: 0
canaryEvidencePresent: true
```

Reference-free timing proof:

```text
tempoBpm: 129.19921875
meter: 4/4
beatCount: 447
firstBeatInMeasure: 3
downbeatIndexMod4: 1
beatConfidence: 0.7233
barConfidence: 0.0880
```

Candidate proof:

```text
direct raw Basic Pitch events: 21354
cascade raw Basic Pitch events: 20589
direct grid-aligned: 21079
cascade grid-aligned: 20309
slot/pitch hypotheses: 22648
rejected without two-view consensus: 9132
consensus slots / accepted events: 1754
requiredConsensusViews: 2
Bass MIDI range: 28..67
maximumGridErrorSeconds: 0.1
```

All 1754 accepted events are supported by exact direct+cascade MIDI consensus, fall in the Bass range, are authenticated to the reference-free timing grid, map to valid four-string G-D-A-E positions, and contain no technique claim.

Existing Bass professional quality gate on these real-audio events:

```text
rawEventCount: 1754
validRenderEventCount: 1754
renderEventSurvivalPercent: 100
playableStringFretPercent: 100
timingCoveragePercent: 100
pitchValidityPercent: 100
pitchStringFretConsistencyPercent: 100
passed: true
```

Boundary result:

```text
passed: true
realAudioBassCandidateTimingPassed: true
noteTimingPlayabilityBoundaryPassed: true
techniqueQualityProven: false
professionalBassComplete: false
```

All safety checks remained green/disabled: no training, customer routing, structured Bass identity, PDF renderer, live Modal change, Vercel deployment, Production modification/promotion, payment, token redemption, or email.

Important interpretation: this closes the audio-derived candidate/note/timing/playability **contract boundary**. It does not claim ground-truth note transcription accuracy against a reference TAB, and it does not prove Bass techniques or complete professional Bass output.

## LIVE STEP — isolated Bass technique evidence

Advance exactly one boundary next: add conservative, reference-free Bass-specific technique evidence to the already authenticated 1754-event substrate.

Requirements:

- no reference TAB, song identity, artist identity, or fixture-specific labels;
- technique evidence must derive from the separated Bass audio and authenticated event trajectories;
- do not reuse `bass_technique_diagnostics_v7.py`;
- preserve note/timing/string/fret fields unchanged;
- fail closed: uncertain events remain technique-free rather than guessed;
- technique families must be independently evidenced and conservative;
- no training authorization in this boundary;
- keep routing, structured identity, PDF, live Modal, Vercel, Production, payment/token/email disabled;
- existing Bass note/timing/playability thresholds remain unchanged.

Candidate technique families from the inactive training contract are `slide`, `hammer_on`, `pull_off`, `mute`, `harmonic`, and `sustain`; higher-risk `slap`, `pop`, `tap`, `bend`, and `vibrato` remain future evidence boundaries unless separately proven.

## Immediate next action

1. Inspect proven reference-free Rhythm technique modules only for reusable structural patterns, not Guitar musical assumptions.
2. Implement isolated Bass-specific conservative technique extraction over the accepted real-audio Bass events and direct/cascade stems.
3. Verify that techniques never alter authenticated note/timing/playability and that uncertain techniques remain absent.
4. Run an isolated real-audio technique canary on the approved fixture.
5. Professional Bass PDF/routing/identity remain disabled after this boundary; exact-branch Vercel Preview remains an external blocker.
