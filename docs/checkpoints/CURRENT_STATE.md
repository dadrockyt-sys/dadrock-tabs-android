# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — Bass harmonic safe-abstention CLOSED GREEN; harmonic remains unproven
Branch: `v143-contextual-prune-lobo`

## Safety / product contract

`dadrocktabs.com/ai-tab`: uploaded audio → Bass / Lead / Rhythm → instrument processing → authenticated musical events → professional preview TAB PDF → purchased/unlocked full professional TAB PDF.

Preview/full PDF must derive from the same authenticated analysis. Browser/PDF must never invent missing musical placement.

Resume **only** on `v143-contextual-prune-lobo`. Never modify `main`, merge this branch, alter/deploy live V143 Modal, automatically promote Production, make payment, redeem customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as professional structured output.

Save this file frequently.

## Rhythm — CLOSED GREEN

Approved fixture `public/gomywayfullaitest.m4a`. Professional analyzer and PDF are green. Rhythm proof includes 358 valid render events, 100% render survival/playability/placement/pitch validity, 112 unique measures, 25 technique events, 358 sustain coverage, tempo ~129.199 BPM, 4/4, E Standard. Local built-Next gate is green at `5b29c0c3df3c97c0f4962e058997b2134d0179b7`. Whole-product contract is green.

## Bass separation + pitch — CLOSED GREEN

Run `32611529763` passed. Direct/cascade stems are distinct, seed 143 fixed, both 211.44 s, ~99.99% 30–1000 Hz energy, ~99.7% playable-range pitch frames. Evidence:

- `debug/v143-contextual-prune/bass-real-audio-canary-action.json`
- `debug/v143-contextual-prune/bass-real-audio-canary.json`

## Bass candidate / note / timing / playability — CLOSED GREEN

Run `32611818648` passed. 1754 authenticated events; two-view MIDI consensus; tempo 129.19921875 BPM; 4/4; 447 beats; MIDI 28..67; max grid error 0.1 s; 100% render survival/playability/timing/pitch/pitch-position consistency. Evidence:

- `debug/v143-contextual-prune/bass-real-audio-event-timing-action.json`
- `debug/v143-contextual-prune/bass-real-audio-event-timing.json`

This closes structural/audio-derived note/timing/playability, not ground-truth transcription accuracy.

## Bass conservative technique subset — CLOSED GREEN

Run `32612166508` passed. Final evidence commit `145f8a15a047016020ff20b38fb1b277b0b30603`.

Key proof: 1757 events; 100% identity preservation; 302 technique events; 332 labels; 100% two-view consensus; sustain 235; slide-down 33; slide-up 38; hammer-on 11; pull-off 14; mute 1; quality 100% across established gates.

Proven reference-free/two-view families: `slide`, `hammer_on`, `pull_off`, `mute`, `sustain`.

Evidence:

- `debug/v143-contextual-prune/bass-real-audio-technique-action.json`
- `debug/v143-contextual-prune/bass-real-audio-technique.json`
- artifact `9485858031`

Important: separate GPU analyses can regenerate slightly different event/rare-technique counts. The prior structural run produced 1754 events; the technique run produced 1757. Do not require cross-run bit identity. Enrichment identity must remain 100% within each authenticated analysis.

## Bass harmonic investigation — CLOSED GREEN SAFE ABSTENTION / HARMONIC UNPROVEN

First run `32612695589` exposed one ambiguous MIDI-40/fret-12 candidate and a verifier mistake that required rare `mute` recurrence across independent GPU reruns. The candidate was deliberately not accepted as harmonic proof because a normal fretted E2 and a 12th-node natural harmonic can share the same sounding pitch and similar overtone structure.

Hardening commits:

- `db74e2e64e17000f0aeee3faa438258951687b38` — stricter harmonic evidence
- `2e420d677f05442d442b61e1d8f027c42d9c74c9` — safe-abstention-aware verifier
- `1ef20763aab365042f620800f60adab9be98c830` — fail-closed workflow accepts exactly one outcome: strict proof or safe abstention

Strict detector requirements:

```text
minimum duration: 0.22 s
maximum onset strength: 0.30
minimum tonal purity: 0.78
minimum upper-partial ratio: 0.90
maximum subharmonic ratio: 0.06
mapped string/fret must match a common natural-harmonic physical node
required independent views: 2
```

Authoritative rerun `32613012696` from source commit `1ef20763aab365042f620800f60adab9be98c830` completed `success` and every workflow step passed.

Final harmonic diagnostic proof:

```text
eventCount: 1757
base->subset identity: 100%
subset->final identity: 100%
quality gate: 100% across all established metrics
harmonicEventCount: 0
harmonicLabelCount: 0
harmonicConsensusPercent: 100 (vacuous: no emitted harmonic labels)
harmonicEvidenceObserved: false
harmonicFamilyProven: false
safeAbstention: true
bassHarmonicDiagnosticBoundaryPassed: true
passed: true
```

Current-run conservative subset also reproduced the prior green counts: sustain 235, slide-down 33, slide-up 38, hammer-on 11, pull-off 14, mute 1.

Evidence:

- `debug/v143-contextual-prune/bass-real-audio-harmonic-action.json`
- `debug/v143-contextual-prune/bass-real-audio-harmonic.json`

The correct product conclusion is: the reference-free harmonic diagnostic safely rejects ambiguous evidence on the approved fixture. `harmonic` remains disabled/unproven. Do not weaken criteria or relabel this abstention as harmonic proof.

High-risk `slap`, `pop`, `tap`, `bend`, `vibrato` remain disabled/unproven. Professional Bass remains false. All training/routing/structured identity/PDF/live Modal/Vercel/Production/payment/token/email flags remain disabled.

## LIVE STEP — determine the next isolated Bass completion boundary

Do not enable professional Bass routing/PDF/customer output merely because the safe subset is green. Harmonic is still unproven and high-risk families remain disabled.

## Immediate next action

1. Inspect existing Bass final-product/scaffold/checkpoint code to identify the next missing professional completion contract after separation, timing/playability, conservative techniques, and harmonic safe-abstention.
2. Prefer an integration/quality contract that can explicitly preserve unsupported techniques as absent rather than attempting high-risk technique families without defensible evidence.
3. Keep all routing, structured professional identity, PDF renderer, live Modal, Vercel, Production, payment, token, and email flags disabled while proving the next isolated boundary.
4. Save this checkpoint before any new canary/workflow and again after its result.
