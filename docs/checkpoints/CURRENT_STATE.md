# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — Bass harmonic first canary inspected; proof intentionally withheld
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

Run `32612166508` passed from source commit `1b94d42a5d52047e183eeee8763ef5d6c88b1d8` lineage through workflow source `1b94d42a5d5ae8e3704f479c259499fa6c2c214e`; final evidence commit `145f8a15a047016020ff20b38fb1b277b0b30603`.

Key proof: 1757 events; 100% identity preservation; 302 technique events; 332 labels; 100% two-view consensus; sustain 235; slide-down 33; slide-up 38; hammer-on 11; pull-off 14; mute 1; quality 100% across established gates.

Proven reference-free/two-view families: `slide`, `hammer_on`, `pull_off`, `mute`, `sustain`.

Evidence:

- `debug/v143-contextual-prune/bass-real-audio-technique-action.json`
- `debug/v143-contextual-prune/bass-real-audio-technique.json`
- artifact `9485858031`

Important: separate GPU analyses can regenerate slightly different event/rare-technique counts. The prior structural run produced 1754 events; the technique run produced 1757. Do not require cross-run bit identity. Enrichment identity must remain 100% within each authenticated analysis.

## Bass harmonic investigation — FIRST CANARY RED / HARMONIC NOT PROVEN

Files/commits:

- `0d6ebd52465ccf07f9193b19eaef099d7d9f4235` — `analyzer/final_product/bass/techniques/bass_harmonic_evidence.py`
- `07e0a7a6eedade3c90f47d7baf493e4278915ba4` — `analyzer/bass_real_audio_harmonic_canary_modal.py`
- `4eb76fe1f43dddc12d97ae20ba72b0543b9f962a` — `analyzer/verify_bass_real_audio_harmonics.mjs`
- `01d71399a14f706152fdf8b3353e59b781cf3e5d` — `.github/workflows/bass-real-audio-harmonics.yml`

Run `32612695589` completed `failure` only at the fail-closed enforcement step. Modal itself exited 0 and generated raw output; verifier exited 1. Evidence:

- `debug/v143-contextual-prune/bass-real-audio-harmonic-action.json`
- `debug/v143-contextual-prune/bass-real-audio-harmonic.json`
- artifact `9486003926`

Observed first-run facts:

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

The verifier failed `requiredSubsetFamiliesStillProven` because this independent rerun produced no `mute`, while the prior closed-green technique run had one mute. This is a harness conflation of independent-run repeatability with the already-closed subset proof; it is not an identity/quality regression.

More importantly, the single harmonic candidate is **not strong enough to claim harmonic**. It is MIDI 40 at mapped E-string fret 12, duration ~0.244 s. Both views showed tonal purity ~0.696, upper-partial ratio ~0.52, subharmonic ratio ~0.014 and zero detected onset. A normal fretted E2 and a 12th-node natural harmonic can share the same sounding pitch and similar overtone structure. The present spectral criteria do not defensibly distinguish them. Therefore harmonic remains unproven rather than accepting a plausible false positive.

High-risk `slap`, `pop`, `tap`, `bend`, `vibrato` remain disabled/unproven. Professional Bass remains false. All training/routing/structured identity/PDF/live Modal/Vercel/Production/payment/token/email flags remain disabled.

## LIVE STEP — convert harmonic boundary to safe-abstention diagnostic

1. Harden harmonic evidence so the ambiguous MIDI-40/fret-12 candidate is rejected unless materially stronger harmonic-specific evidence exists. Do not loosen any threshold.
2. Fix the harmonic verifier so it does not demand rare-technique recurrence from a separate GPU rerun. The already-closed subset proof remains external; within-run base→subset→harmonic identity and preservation of whatever subset labels are produced must remain 100%.
3. Allow the harmonic workflow to finish green when the detector safely abstains, while explicitly setting `harmonicFamilyProven: false`. A green workflow then means the negative/abstention boundary is sound, **not** that harmonic is proven.
4. Re-run the approved fixture. If no defensible harmonic survives, close harmonic as disabled/unproven and do not weaken criteria.
5. Save this checkpoint before/after the rerun.
6. Professional Bass PDF/routing/identity remain disabled. Exact-branch Vercel Preview remains an external blocker.
