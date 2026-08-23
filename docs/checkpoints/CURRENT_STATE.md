# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — Bass technique subset closed green
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

`harmonic` remains deliberately unimplemented/unproven. High-risk `slap`, `pop`, `tap`, `bend`, `vibrato` remain disabled/unproven.

All training/routing/structured identity/PDF/live Modal/Vercel/Production/payment/token/email flags remain disabled.

## LIVE STEP — harmonic evidence boundary only

Next work must remain isolated and diagnostic. Do not enable customer output.

Goal: determine whether `harmonic` can be added conservatively using reference-free, two-view Bass spectral evidence without changing note/timing/MIDI/string/fret/duration identity. A harmonic label must require agreement from both Bass views and must remain absent when evidence is ambiguous. If a defensible harmonic boundary cannot be proven on the approved fixture, leave it unproven rather than weakening thresholds.

## Immediate next action

1. Implement a conservative two-view harmonic detector inside `analyzer/final_product/bass/techniques/bass_technique_evidence.py` only if the spectral evidence is sufficiently discriminative.
2. Extend the isolated technique verifier/workflow so harmonic is claimed only when both views agree and identity remains 100% unchanged.
3. Run a new Bass technique canary on `public/gomywayfullaitest.m4a`.
4. If red or harmonic evidence is absent/ambiguous, keep harmonic explicitly unproven and do not weaken established quality/safety.
5. Professional Bass PDF/routing/identity remain disabled. Exact-branch Vercel Preview remains an external blocker.
