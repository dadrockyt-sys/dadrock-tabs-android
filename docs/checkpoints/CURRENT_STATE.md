# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — Bass structured integration canary active
Branch: `v143-contextual-prune-lobo`

## Safety / product contract

`dadrocktabs.com/ai-tab`: uploaded audio → Bass / Lead / Rhythm → instrument processing → authenticated musical events → professional preview TAB PDF → purchased/unlocked full professional TAB PDF.

Preview/full PDF must derive from the same authenticated analysis. Browser/PDF must never invent missing musical placement.

Resume **only** on `v143-contextual-prune-lobo`. Never modify `main`, merge this branch, alter/deploy live V143 Modal, automatically promote Production, make payment, redeem customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as professional structured output.

Save this file frequently.

## Rhythm — CLOSED GREEN

Approved fixture `public/gomywayfullaitest.m4a`. Professional analyzer and PDF are green. Rhythm proof includes 358 valid render events, 100% render survival/playability/placement/pitch validity, 112 unique measures, 25 technique events, 358 sustain coverage, tempo ~129.199 BPM, 4/4, E Standard. Local built-Next gate is green at `5b29c0c3df3c97c0f4962e058997b2134d0179b7`. Whole-product contract is green.

## Bass separation + pitch — CLOSED GREEN

Run `32611529763` passed. Direct/cascade stems are distinct, seed 143 fixed, both 211.44 s, ~99.99% 30–1000 Hz energy, ~99.7% playable-range pitch frames.

Evidence:
- `debug/v143-contextual-prune/bass-real-audio-canary-action.json`
- `debug/v143-contextual-prune/bass-real-audio-canary.json`

## Bass candidate / note / timing / playability — CLOSED GREEN

Run `32611818648` passed. 1754 authenticated events; two-view MIDI consensus; tempo 129.19921875 BPM; 4/4; 447 beats; MIDI 28..67; max grid error 0.1 s; 100% render survival/playability/timing/pitch/pitch-position consistency.

Evidence:
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

Important: separate GPU analyses can regenerate slightly different event/rare-technique counts. The structural run produced 1754 events; the technique run produced 1757. Do not require cross-run bit identity. Enrichment identity must remain 100% within each authenticated analysis.

## Bass harmonic investigation — CLOSED GREEN SAFE ABSTENTION / HARMONIC UNPROVEN

Strict harmonic detector requires minimum duration 0.22 s, max onset 0.30, min tonal purity 0.78, min upper-partial ratio 0.90, max subharmonic ratio 0.06, authenticated mapped string/fret matching a common natural-harmonic node, and two independent Bass views.

Authoritative run `32613012696` passed with:

```text
eventCount: 1757
base->subset identity: 100%
subset->final identity: 100%
quality: 100%
harmonicEventCount: 0
harmonicFamilyProven: false
safeAbstention: true
passed: true
```

Evidence:
- `debug/v143-contextual-prune/bass-real-audio-harmonic-action.json`
- `debug/v143-contextual-prune/bass-real-audio-harmonic.json`

Correct conclusion: ambiguous harmonic evidence is safely rejected. `harmonic` remains disabled/unproven. High-risk `slap`, `pop`, `tap`, `bend`, `vibrato` remain disabled/unproven.

## Existing Bass presentation contracts — GREEN SCAFFOLDS / INACTIVE

- `lib/bassProfessionalRenderContract.js`: four-string `G-D-A-E`, open MIDI `[43,38,33,28]`, frets 0..24, 16 steps/measure, exact MIDI/string/fret consistency.
- `lib/bassProfessionalQuality.js`: existing minimum-4 / 70% render/playability/timing/pitch/pitch-position thresholds.
- Existing scaffold workflows prove these contracts synthetically only.
- `lib/jimmyPaigeAnalysisPayload.js`, `lib/createAiTabPdf.js`, and `lib/createJimmyPaigeProfessionalPdf.js` still enable structured professional routing only for Rhythm. Bass remains legacy/inactive.

## LIVE STEP — real-audio Bass structured-event integration

New diagnostic integration files/commits:

- `1d80fb1fc28cad1194762d1ca32fb6b0aa75ef1f` — `lib/bassProfessionalStructuredAnalysis.js`
- `4e0ac878fbca28e629c75f76268b3ceb18512c8e` — `analyzer/verify_bass_real_audio_structured_integration.mjs`
- `b2fb4b7a2288a2751549f77b5e0f6ec9d22b345c` — `.github/workflows/bass-real-audio-structured-integration.yml`
- `30fd6ef286c9723b2c403d4431eb3d7039046d32` — explicit structured-contract safety flags
- `8a668f9a4af966b8abf14034b975a36d6ed7d587` — hardened verifier safety checks; authoritative source commit for the current run

Contract behavior:

- Projects the exact same-run final Bass events through the existing Bass render contract.
- Requires 100% render survival for this canary and exact render identity.
- Allows only the already-proven conservative labels: `slide-up`, `slide-down`, `hammer-on`, `pull-off`, `mute`, `sustain`.
- Requires every emitted technique label to retain two-view reference-free evidence.
- Requires harmonic safe abstention and no harmonic/high-risk labels.
- Reuses the unchanged existing Bass professional quality thresholds and additionally requires 100% on this canary.
- Remains diagnostic-only with professional identity, routing, PDF, live endpoint, Vercel, Production, payment, token, email, training and high-risk families disabled.

Earlier runs `32613381366` and `32613408513` were intentionally cancelled by workflow concurrency because safety-hardening commits arrived while they were running. Their failure diagnostics are not product regressions.

Current authoritative heartbeat:

```text
workflow: Bass Real Audio Structured Integration
runId: 32613450912
sourceCommit: 8a668f9a4af966b8abf14034b975a36d6ed7d587
startedAtUtc: 2026-08-23T02:41:13.180249+00:00
status: in progress
```

Expected compact evidence:
- `debug/v143-contextual-prune/bass-real-audio-structured-integration-action.json`
- `debug/v143-contextual-prune/bass-real-audio-structured-integration.json`

Passing this boundary proves structured Bass **data integration readiness only**. It does not authorize professional Bass branding, PDF routing, live Modal deployment, Vercel changes, Production, payment, token redemption, or email.

## Immediate next action

1. Poll run `32613450912` through completion.
2. Inspect action/evidence and artifact/logs if red.
3. Require 100% same-run render survival, exact render identity, evidence-backed technique labels, harmonic safe abstention, 100% established quality metrics, and all safety flags false.
4. Save this checkpoint after the result.
