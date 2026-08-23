# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — Bass harmonic canary running
Branch: `v143-contextual-prune-lobo`

## Safety / product contract

`dadrocktabs.com/ai-tab`: uploaded audio → Bass / Lead / Rhythm → instrument processing → authenticated musical events → professional preview TAB PDF → purchased/unlocked full professional TAB PDF.

Preview/full PDF must derive from the same authenticated analysis. Browser/PDF must never invent missing musical placement.

Resume **only** on `v143-contextual-prune-lobo`. Never modify `main`, merge this branch, alter/deploy live V143 Modal, automatically promote Production, make payment, redeem customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as professional structured output.

Save this file frequently.

## Rhythm — CLOSED GREEN

Approved fixture `public/gomywayfullaitest.m4a`. Professional analyzer and PDF are green. Rhythm proof includes 358 valid render events, 100% render survival/playability/placement/pitch validity, 112 unique measures, 25 technique events, 358 sustain coverage, tempo ~129.199 BPM, 4/4, E Standard. Local built-Next gate is green at `5b29c0c3df3c97c0f4962e058997b2134d0179b7`. Whole-product contract is green.

## Bass base contracts — GREEN / INACTIVE

Bass uses true Demucs `Bass` separation and standard four-string `G-D-A-E` mapping. Existing separator/render/quality scaffolds are green. Render contract requires `measure >= 1`, `step 0..15`, `stringIndex 0..3`, fret `0..24`, MIDI, and exact `openMidi[stringIndex] + fret == midi` with `[43,38,33,28]`. Existing quality thresholds remain unchanged: minimum 4 events and 70% render survival/playability/timing/pitch/pitch-position consistency.

`bass_technique_diagnostics_v7.py` is reference-guided and must not be reused.

## Bass separation + pitch — CLOSED GREEN

Run `32611529763` passed. Evidence:

- `debug/v143-contextual-prune/bass-real-audio-canary-action.json`
- `debug/v143-contextual-prune/bass-real-audio-canary.json`

Direct/cascade stems are distinct, seed 143 is fixed, both 211.44 s, ~99.99% 30–1000 Hz energy, ~99.7% playable-range pitch frames. This proves separation + reference-free pitch plausibility only.

## Bass candidate / note / timing / playability — CLOSED GREEN

Run `32611818648` passed every workflow/fail-closed step. Evidence:

- `debug/v143-contextual-prune/bass-real-audio-event-timing-action.json`
- `debug/v143-contextual-prune/bass-real-audio-event-timing.json`

Key proof:

```text
tempoBpm: 129.19921875
meter: 4/4
beatCount: 447
acceptedEvents: 1754
requiredConsensusViews: 2
Bass MIDI: 28..67
maximumGridErrorSeconds: 0.1
render survival: 100%
playable string/fret: 100%
timing coverage: 100%
pitch validity: 100%
pitch/string/fret consistency: 100%
passed: true
```

All 1754 events have exact direct+cascade MIDI consensus and authenticated grid placement. This closes the structural/audio-derived note/timing/playability boundary, not ground-truth transcription accuracy. Techniques were deliberately empty.

## Bass conservative technique subset — CLOSED GREEN

Run `32612166508` completed `success` from source commit `1b94d42a5d5ae8e3704f479c259499fa6c2c214e`. Final workflow evidence commit: `145f8a15a047016020ff20b38fb1b277b0b30603`.

Evidence:

- `debug/v143-contextual-prune/bass-real-audio-technique-action.json`
- `debug/v143-contextual-prune/bass-real-audio-technique.json`
- workflow artifact `bass-real-audio-techniques` / artifact id `9485858031`

Key proof:

```text
eventCount: 1757
identityPreservationPercent: 100
techniqueEventCount: 302
techniqueLabelCount: 332
consensusTechniquePercent: 100
sustain: 235
slide-down: 33
slide-up: 38
hammer-on: 11
pull-off: 14
mute: 1
quality gate: 100% across render/playability/timing/pitch/pitch-position
passed: true
professionalBassComplete: false
```

Proven reference-free/two-view families: `slide`, `hammer_on`, `pull_off`, `mute`, `sustain`.

Important: the isolated technique rerun regenerated 1757 base events versus 1754 in the earlier structural run. Raw candidate counts also changed slightly across the two separate GPU analyses, while timing stayed identical (129.19921875 BPM, 447 beats, same fixture/hash). This does **not** violate the technique identity gate because enrichment preserved every base event 100% within the same authenticated analysis. Do not claim cross-run bit-identical event generation from the current evidence.

All training/routing/structured identity/PDF/live Modal/Vercel/Production/payment/token/email flags remain disabled.

## LIVE STEP — isolated harmonic evidence boundary

Implementation is complete enough for the first real-audio diagnostic run, still customer-inactive.

New commits/files:

- `0d6ebd52465ccf07f9193b19eaef099d7d9f4235` — `analyzer/final_product/bass/techniques/bass_harmonic_evidence.py`
- `07e0a7a6eedade3c90f47d7baf493e4278915ba4` — `analyzer/bass_real_audio_harmonic_canary_modal.py`
- `4eb76fe1f43dddc12d97ae20ba72b0543b9f962a` — `analyzer/verify_bass_real_audio_harmonics.mjs`
- `01d71399a14f706152fdf8b3353e59b781cf3e5d` — `.github/workflows/bass-real-audio-harmonics.yml`

The helper considers only common standard-Bass open-string natural-harmonic sounding pitches and requires two-view spectral evidence: tonal purity, upper-partial support, weak subharmonic energy, controlled onset, minimum duration, and exact cross-view agreement. It does not reinterpret the mapped TAB fret as a harmonic node and must not change note/timing/MIDI/string/fret/duration identity.

The verifier is fail-closed: base→subset and subset→harmonic identity must remain 100%; the five already-proven subset families must remain proven; only `harmonic` may be newly added; every harmonic label must have two-view reference-free evidence; all quality gates must remain green; all production/customer flags remain false. At least one harmonic event is required to prove this boundary.

Current workflow heartbeat:

```text
workflow: Bass Real Audio Harmonics
runId: 32612695589
sourceCommit: 01d71399a14f706152fdf8b3353e59b781cf3e5d
startedAtUtc: 2026-08-23T02:22:40.870754+00:00
status: in_progress
currentStep: Run isolated Bass harmonic canary
```

Heartbeat: `debug/v143-contextual-prune/bass-real-audio-harmonic-start.json`.

Expected final evidence:

- `debug/v143-contextual-prune/bass-real-audio-harmonic-action.json`
- `debug/v143-contextual-prune/bass-real-audio-harmonic.json`

This detector is **not proven yet**. If the approved fixture yields absent or ambiguous harmonic evidence, keep `harmonic` unproven rather than weakening thresholds.

High-risk `slap`, `pop`, `tap`, `bend`, `vibrato` remain disabled/unproven. Professional Bass remains false.

## Immediate next action

1. Poll run `32612695589` through completion.
2. Inspect final harmonic action/evidence plus artifact/logs if red.
3. If harmonic evidence is absent/ambiguous or any identity/safety gate fails, keep harmonic explicitly unproven and do not weaken thresholds.
4. Save this checkpoint again after the run/result.
5. Professional Bass PDF/routing/identity remain disabled. Exact-branch Vercel Preview remains an external blocker.
