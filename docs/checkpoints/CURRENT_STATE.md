# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — Bass harmonic safe-abstention rerun active
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

## Bass harmonic investigation — FIRST CANARY RED / HARMONIC NOT PROVEN

Run `32612695589` completed `failure` only at the fail-closed enforcement step. Modal exited 0. The first verifier exited 1 because it incorrectly required the rare `mute` family to recur in this independent rerun.

First-run evidence:

```text
eventCount: 1754
base->subset identity: 100%
subset->final identity: 100%
quality gate: 100%
harmonicEventCount: 1
harmonic consensus: 100% (2 views)
current-run subset: sustain 217, slide 74, hammer-on 11, pull-off 11, mute 0
passed: false
```

The single harmonic candidate was MIDI 40 at mapped E-string fret 12, duration ~0.244 s. Both views showed tonal purity ~0.696, upper-partial ratio ~0.52, subharmonic ratio ~0.014 and zero detected onset. A normal fretted E2 and a 12th-node natural harmonic can share the same sounding pitch and similar overtone structure, so this candidate is ambiguous. It is deliberately **not accepted as proof**.

Evidence:

- `debug/v143-contextual-prune/bass-real-audio-harmonic-action.json`
- `debug/v143-contextual-prune/bass-real-audio-harmonic.json`
- artifact `9486003926`

## Harmonic boundary hardening — IMPLEMENTED / RERUN ACTIVE

New commits:

- `db74e2e64e17000f0aeee3faa438258951687b38` — harden `bass_harmonic_evidence.py`
- `2e420d677f05442d442b61e1d8f027c42d9c74c9` — safe-abstention-aware verifier
- `1ef20763aab365042f620800f60adab9be98c830` — fail-closed workflow accepts exactly one outcome: strict proof or safe abstention

Hardening is only stricter, never looser:

```text
minimum duration: 0.22 s
maximum onset strength: 0.30
minimum tonal purity: 0.78
minimum upper-partial ratio: 0.90
maximum subharmonic ratio: 0.06
mapped string/fret must match a common natural-harmonic physical node
required independent views: 2
```

The ambiguous first-run candidate (~0.696 purity, ~0.52 upper-partial ratio) must now be rejected.

Verifier no longer conflates rare-technique recurrence across independent GPU analyses with the already-closed subset proof. It still requires current-run subset diagnostics to be sound, base→subset identity 100%, subset→final identity 100%, preservation of every current-run subset label, no unexpected labels, 100% strict two-view evidence for any harmonic actually emitted, all established quality gates green, and all production/customer flags false.

A green rerun may legitimately report `safeAbstention: true` and `harmonicFamilyProven: false`. That proves the diagnostic safely refuses ambiguous harmonic evidence; it does **not** prove harmonic technique detection.

The helper-triggered run `32612959798` was cancelled by concurrency after later verifier/workflow commits, as expected.

Current authoritative heartbeat:

```text
workflow: Bass Real Audio Harmonics
runId: 32613012696
sourceCommit: 1ef20763aab365042f620800f60adab9be98c830
startedAtUtc: 2026-08-23T02:30:40.930771+00:00
```

High-risk `slap`, `pop`, `tap`, `bend`, `vibrato` remain disabled/unproven. Professional Bass remains false. All training/routing/structured identity/PDF/live Modal/Vercel/Production/payment/token/email flags remain disabled.

## Immediate next action

1. Poll run `32613012696` through completion.
2. Inspect final action/evidence. Expected conservative result is zero harmonic labels + `safeAbstention: true` + workflow success.
3. If so, close harmonic as disabled/unproven on this fixture rather than weakening criteria.
4. If any strict harmonic survives, inspect its evidence manually before claiming proof.
5. Save this checkpoint again after the rerun.
6. Professional Bass PDF/routing/identity remain disabled. Exact-branch Vercel Preview remains an external blocker.
