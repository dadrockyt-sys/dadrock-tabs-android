# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-22 — PRIORITY PIVOT: finish Rhythm end-to-end against locked human reference before Bass/Lead
Branch: `v143-contextual-prune-lobo`

## Safety / product contract

`dadrocktabs.com/ai-tab`: uploaded audio → Bass / Lead / Rhythm → instrument processing → authenticated musical events → professional preview TAB PDF → purchased/unlocked full professional TAB PDF.

Preview/full PDF must derive from the same authenticated analysis. Browser/PDF must never invent missing musical placement.

Resume **only** on `v143-contextual-prune-lobo`. Never modify `main`, merge this branch, alter/deploy live V143 Modal, automatically promote Production, make payment, redeem customer token, send customer email, weaken quality thresholds, or relabel legacy Lead/Bass as professional structured output.

Save this file frequently.

## NEW TOP-LEVEL COMPLETION RULE — Rhythm first, then Bass, then Lead

The prior Rhythm structural/render gates being green are **not sufficient to call Rhythm complete**.

Jimmy PAIge Rhythm is complete only when the full user-facing path is proven end to end:

`user-uploaded audio → reference-free Rhythm analysis → authenticated structured events → professional preview/full PDF data path → post-hoc scoring against the professionally human-written Rhythm TAB`

The professional human TAB is **benchmark-only holdout ground truth**. Jimmy PAIge/analyzer must not read it, train from it, receive its notes/frets/timing/techniques, or use it to select/infer output during the analyzed run. The human reference may be opened only by an isolated scorer **after** the reference-free output is frozen.

Required anti-leakage architecture:

1. Analyzer job receives only uploaded audio + transcription mode/configuration; no professional reference files or reference-derived runtime labels.
2. Freeze/hash analyzer output and the exact structured events that drive the professional PDF.
3. Generate preview/full professional PDF from that same frozen analysis; renderer may not invent missing music.
4. Only after output is frozen, run an isolated benchmark scorer that reads the professional human reference.
5. Score both musical correctness and PDF fidelity. The scorer may diagnose errors but must not feed corrections back into the same scored run.
6. Any future improvement must be general/reference-free DSP/model/algorithm work, then rerun from audio from scratch before rescoring.

Near-100 completion means the generated transcription must match the human professional TAB at professional level, including at minimum: note/chord pitch content, string/fret position and voicing, measure/beat/onset placement, durations/rests/sustain/ties, section completeness, supported techniques, false-positive/false-negative control, and exact PDF fidelity to the authenticated scored event stream. Structural self-consistency alone cannot satisfy this gate.

After Rhythm passes this holdout end-to-end gate, repeat the same methodology for Bass, then Lead. Do not use the Bass/Lead professional references as runtime inputs either.

## Finalized pipeline packaging rule

When an instrument is truly complete, preserve its proven end-to-end implementation as a self-contained finalized folder before using it as the basis for the next instrument.

Required order and packaging:

1. **Rhythm first.** Once the complete upload → reference-free analysis → authenticated events → professional PDF → isolated human-reference near-100 scoring gate passes, commit the finalized implementation into its own folder named **`Final Rhythm Pipeline`**. This folder becomes the protected working blueprint for later instruments.
2. **Bass second.** Use the finalized Rhythm architecture to shape/reuse the common pipeline machinery for Bass instead of rebuilding shared pieces. Adapt only what is instrument-specific (separation, range/tuning/string mapping, techniques, scoring semantics, rendering). When the user provides the professional human Bass TAB, use it only as the isolated post-hoc scoring holdout under the same no-learning/no-runtime-reference rule. Once Bass independently reaches the same professional near-100 end-to-end standard, commit it into its own folder named **`Final Bass Pipeline`**.
3. **Lead third.** Use the finalized Rhythm architecture as the primary mold for Lead, reusing the proven shared pipeline and adapting Lead-specific analysis/techniques/register/voicing/scoring. When the user provides the professional human Lead TAB, use it only as isolated post-hoc scoring holdout. Once Lead independently reaches the professional near-100 end-to-end standard, commit it into its own folder named **`Final Lead Pipeline`**.

Do **not** ask for the Bass or Lead professional human references before those phases are ready for scoring; the user will provide each reference when needed.

The finalized folders are not permission to deploy Production or alter the live V143 endpoint. They are versioned, proven pipeline packages on `v143-contextual-prune-lobo` until separate authorization is given.

## Rhythm — STRUCTURAL/RENDER GREEN, HUMAN-REFERENCE END-TO-END SCORE STILL OPEN

Approved audio fixture `public/gomywayfullaitest.m4a`. Existing professional analyzer/render proof includes 358 valid render events, 100% render survival/playability/placement/pitch validity, 112 unique measures, 25 technique events, 358 sustain coverage, tempo ~129.199 BPM, 4/4, E Standard. Local built-Next gate is green at `5b29c0c3df3c97c0f4962e058997b2134d0179b7`. Existing whole-product structural contract is green.

However, current older human-reference benchmark infrastructure is too coarse to establish professional near-100 transcription equivalence. `analyzer/modal_gomyway2_full_reference_benchmark.py` scores fret inventory, allowed-fret precision, string overlap, technique presence, motif subsequences, and register. `analyzer/fixtures/gomyway2_full_tab_reference.json` contains summarized motifs/inventories rather than a complete event-by-event professional TAB representation. That benchmark can remain diagnostic history but cannot be the final completion authority.

Rhythm is therefore reopened for the final end-to-end professional holdout benchmark.

### Rhythm professional-reference inventory — IN PROGRESS, DO NOT SCORE YET

The already-supplied material has begun to be inventoried without exposing it to analyzer runtime.

Confirmed distinctions:

- The emailed DadRock V143 Rhythm PDF `ds-music-are-you-gonna-go-my-way-remastered-2025-lenny-kravitz-rhythm-tab.pdf` is a **generated DadRock output**, not the professional human holdout reference. Never use it as ground truth.
- A Library image named `1000116180.jpg` is a clearly different dark-theme professional tablature source for **Are You Gonna Go My Way**, showing Chorus measures 33–35 with chord/voicing labels including `G6`, `A(tp2)`, `E`, `D`, exact string/fret stacks, rhythmic notation, and aligned lyrics. Treat this as holdout/reference material only.
- Other Library images such as `1000116132.jpg` and `1000116183.jpg` are DadRock/Jimmy PAIge generated proof PDFs and are not the human reference.
- The complete human reference has **not yet been reconstructed/inventoried event-by-event**, so no final professional score is authorized yet.

Historical contextual-prune development grading also contains a 431-event reference count for measures 17–96 (`contextual-prune-freeze-manifest.json`), but that older development reference was used during historical model development and therefore cannot automatically be promoted to the new clean holdout completion authority. It may help locate provenance/source material, not serve as a leak-free final score unless isolation is proven.

Next inventory work: locate the complete professional source/pages and any existing event-level extraction/provenance in the repository or supplied Library before manually reconstructing anything.

## Bass separation + pitch — CLOSED GREEN / PAUSED

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

## Bass structured integration canary — CLOSED GREEN, BASS NOW PAUSED

Diagnostic integration files/commits:

- `1d80fb1fc28cad1194762d1ca32fb6b0aa75ef1f` — `lib/bassProfessionalStructuredAnalysis.js`
- `4e0ac878fbca28e629c75f76268b3ceb18512c8e` — `analyzer/verify_bass_real_audio_structured_integration.mjs`
- `b2fb4b7a2288a2751549f77b5e0f6ec9d22b345c` — `.github/workflows/bass-real-audio-structured-integration.yml`
- `30fd6ef286c9723b2c403d4431eb3d7039046d32` — explicit structured-contract safety flags
- `8a668f9a4af966b8abf14034b975a36d6ed7d587` — hardened verifier safety checks; authoritative source commit

Authoritative result:

```text
workflow: Bass Real Audio Structured Integration
runId: 32613450912
sourceCommit: 8a668f9a4af966b8abf14034b975a36d6ed7d587
runStartedAtUtc: 2026-08-23T02:40:35Z
completedAtUtc: 2026-08-23T02:44:56Z
status: completed
conclusion: success
```

This closes the already-started isolated Bass diagnostic only. Start **no additional Bass capability expansion** until Rhythm passes the professional human-reference end-to-end gate.

## LIVE PRIORITY — build the final Rhythm holdout benchmark

Immediate next action:

1. Finish inventorying the exact professionally human-written Rhythm TAB source already supplied and convert it into a complete scorer-only event/measure ground truth without exposing it to analyzer runtime.
2. Locate any existing event-level professional-reference extraction/provenance before manually reconstructing the human source. Do not substitute generated DadRock proof PDFs for the human reference.
3. Build a scorer that aligns frozen Jimmy PAIge Rhythm events to that reference measure-by-measure and reports precision/recall/F1 plus exact/near-exact correctness for pitch/chords, string/fret/voicing, timing, durations/rests/sustain/ties, and supported techniques.
4. Add hard anti-leakage assertions: `referenceFree:true`, `professionalReferenceUsed:false`, no scorer/reference import in analyzer code path, and hash/freeze analysis before scorer access.
5. Verify professional PDF derives 100% from the exact scored frozen events; PDF fidelity must be 100% even if transcription accuracy is still below target.
6. Run user-upload-equivalent audio → analyzer → structured events → professional PDF → isolated holdout scorer.
7. Do not declare Rhythm complete until the post-hoc human-reference score is near 100% with no critical musical mismatches. Improve only through reference-free/general algorithms, rerunning from audio from scratch after every change.
8. Once Rhythm passes, package it as `Final Rhythm Pipeline`; then build Bass from that blueprint and wait for the user's Bass professional reference when Bass reaches scoring. After Bass passes, package `Final Bass Pipeline`; then build Lead from the Rhythm blueprint and wait for the user's Lead professional reference when Lead reaches scoring. After Lead passes, package `Final Lead Pipeline`.
