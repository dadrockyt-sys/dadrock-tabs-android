# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-08 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`

This is the **only canonical fresh-chat checkpoint for the new Songsterr-inspired pipeline**.

Do not use the generic `docs/checkpoints/CURRENT_STATE.md` for this project. Do not resume the old V143/Gomyway investigation unless the user explicitly asks to return to that archived work.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from uploaded audio to a usable finished tab without a mandatory human correction step.

Engineering priority: musical correctness and stability before cosmetic scores. Preserve detected musical identity while making structure, timing, rhythm spelling, chord shapes, fretboard motion, techniques, and final rendering coherent enough for product use.

Do not change public accuracy promises yet. Only change `/ai-tab` wording after the clean pipeline earns a real no-human-correction acceptance standard.

## FOUNDATIONAL RULE — TIMING AND MEASURES COME FIRST

Non-negotiable real-audio order:

**full-mixture audio → timing/measure map → structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

Not:

**audio → loose notes → attempt to repair timing afterward**

`structureMap` must carry tempo/meter/feel segments, downbeats, explicit measure boundaries, pickup/anacrusis, beat/subdivision positions, confidence, and provenance. Downstream note/rhythm/tab stages consume this map directly.

## EXISTING `/ai-tab` PRODUCT SHELL — PRESERVE IT

Preserve:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock reference → full tab PDF → browser download + email delivery**

Fresh work replaces the transcription brain, not the customer/paywall/PDF journey.

## PROJECT BOUNDARY

- Old branch `v143-contextual-prune-lobo` is archive/evidence only.
- Historical Gomyway/V143 scorer contracts are not fresh acceptance criteria.
- Do not touch Production or main.
- Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or real-audio canaries without explicit user authorization.
- Old failed CI/tests do not become fresh blockers merely because they exist.

## FRESH IMPLEMENTATION

Namespace: `songsterr_pipeline/`

Important clean-line commits:
- `212be220b96de687f55cce2ca3e7698b1ac9dadb` — isolated deterministic core;
- `a0fbc5fc54aa1bf91a7cc199f373d5018d158a11` — compatibility musical event/rhythm layer;
- `e9b56a0fdceed2dafc9715f22b5c93954098877e` — first-class `structureMap` + structure-conditioned note core;
- `89c6a12d604dd203b65f4e4015d7d1d246f05a9f` — structure-map-driven event/rhythm schema;
- `b6a3a70369c1d5af269b95428a4a67e0bb2a99d5` — contextual rhythm spelling;
- `e36d734076001767306f53f7bb56c75440787dbd` — constrained playable-shape decoder;
- `9f40ed825333e33f0e3f91571d08619d3f05977c` — decoder refactor exposing multiple legal candidate shapes;
- `467fed67ef35f23a07e45aebfed340a259319b7d` — phrase-level fretboard path optimizer.

Associated test commits:
- `c682355c173f47dbb250175fb4eca718a8c91a20` — original deterministic tests;
- `9ce440755d1d70813d1043210d8bd8a28a650cd3` — compatibility rhythm tests;
- `71e553f13aa37a4c30615c094c2679b1e9504475` — structure-map tests;
- `85b175f60406fb47a81bfebfe36ba99e52ed029f` — structure-driven rhythm tests;
- `15bc52616bee054acea6a4d58c7cfd918b578c13` — contextual rhythm tests;
- `c3452d39702df616b52ecd0bac171af2bd099d12` — constrained decoder tests;
- `d684cd2a42ace038bff85637a2ef9a38b0c37371` — phrase fretboard optimizer tests.

Recent checkpoint commits:
- `3bc1c36c4d3fbeefe3a1243415de72b1a4a5a8cd` — first 13/13 proof;
- `324420a20210a3cd88284b323968366d1e86773c` — 19/19 structure-first milestone;
- `d78b01c09707f3a11e876a9e500e788a2b6c4721` — 25/25 structure-driven milestone;
- `19512a5477cea0845629e0a80723566e5ee41364` — repaired interrupted 30/30 contextual checkpoint;
- `59c1e4977d4f69a6eb83282c29670d972e84fea8` — constrained decoder checkpoint.

### First-class structure path

`structureMap.mjs` provides explicit structure before note placement, including change-boundary validation and half-open `[start, end)` segment semantics.

`structureRhythmNotation.mjs` uses that same map for onset/end projection, pickup/measure/beat segmentation, tied notation, rests, syncopation, provenance, and displacement diagnostics while preserving one source note = one event identity.

`contextualRhythmSpelling.mjs` is downstream readability only: standard/dotted/triplet values, weak-beat dotted merges, strong-beat tie preservation, explicit rest spelling, and phrase feel diagnostics. It must not change MIDI/event identity.

### Constrained playable-shape decoder

`playableShapeDecoder.mjs` now:
- enumerates exact-MIDI playable positions under tuning/capo;
- enforces unique-string simultaneous assignment;
- rejects excessive fretted span, string span, and adjacent-string fret delta;
- has role-aware lead/rhythm/bass policies and open-string preferences;
- exposes neighboring hand-position context hooks;
- exposes **multiple valid candidate shapes** via `enumeratePlayableShapes(...)`;
- uses deterministic scoring/tie-breaking;
- returns explicit unresolved reasons instead of dropping pitches;
- reports raw shape diagnostics and candidate/rejection counts.

### Phrase-level fretboard path optimizer

`fretboardPathOptimizer.mjs` performs deterministic dynamic-programming search over valid candidate shapes from each onset/chord.

Hard constraints happen before path scoring:
1. every source MIDI must remain present;
2. every chosen assignment must reconstruct exact MIDI;
3. simultaneous notes use unique strings;
4. physically rejected local shapes never enter the phrase search.

Path costs then consider:
- center-fret movement;
- string-set changes;
- a small local-shape quality cost.

Current outputs include chosen assignments per onset plus raw diagnostics:
- candidate count per onset;
- total/max center-fret movement;
- string-set change count;
- open-string usage;
- total path cost;
- unresolved onset count.

If any onset has no legal state, the phrase returns `UNRESOLVED_ONSET_SHAPE` with original MIDI groups intact. It does **not** drop notes to continue.

## VALIDATION STATUS

Proven earlier branch surfaces:
- original clean surface: **13/13 pass**;
- structure-first surface: **19/19 pass** after fixing exact-boundary segment semantics;
- structure-driven event/rhythm surface: **25/25 pass**;
- contextual rhythm spelling complete namespace run before interruption: **30/30 pass**.

### Constrained decoder isolated proof

Exact new decoder test surface: **5/5 pass**.

### Candidate enumeration + phrase path isolated proof — CURRENT NEW PROOF

The refactored decoder plus phrase optimizer were executed together in an isolated local Node runtime against the same playable-position contract used by `index.mjs`.

Result:
- tests: **10**
- pass: **10**
- fail: **0**

Proven behavior includes:
- multiple legal exact-MIDI candidate states are exposed;
- phrase search reduces total hand movement versus independent local decoding on a synthetic `[64] → [76] → [64]` phrase;
- every selected chord state preserves exact MIDI and unique strings;
- deliberately unresolved onset aborts explicitly with original MIDI groups intact;
- repeated path selection is deterministic and movement diagnostics are stable;
- the original five constrained-decoder tests still pass after the candidate-state refactor.

The full branch-wide suite has not been re-executed after the decoder/path additions because this container cannot resolve GitHub directly. Do not claim a new branch-wide 40-test result yet.

No Production/main, model/GPU, professional scorer, training, real-audio canary, or archived V143/Gomyway path was touched.

## CURRENT ENGINEERING MILESTONE

Wire phrase-selected constrained fingering onto the **structure-first event schema** without allowing fretboard optimization to mutate timing, notation, event IDs, cluster identity, or MIDI.

Required proof:
- structure-map projected starts/ends unchanged;
- measure/beat/pickup positions unchanged;
- notation segments/ties/rests unchanged;
- event IDs/source indexes/MIDI unchanged;
- cluster-to-path assignment mapping deterministic;
- optimized path movement no worse than the pre-existing independent local choices on a targeted fixture;
- unresolved path remains explicit rather than silently falling back by deleting notes.

## NEXT EXECUTION ORDER

1. Add structure-event → phrase-path integration with invariance tests.
2. Define a fresh evaluator reporting raw structure, event, pitch, timing, playability, motion, notation, tie/rest, and unresolved-duration diagnostics before any composite score.
3. Only after the deterministic structure/notation/fretboard system is stable, connect real-audio evidence in this order: **full-mixture structure analysis → structureMap → role-conditioned note evidence → clean event schema → notation → fretboard decoding**.
4. Map clean analyzer output into the existing `/ai-tab` metadata/render/PDF contract.
5. Define the no-human-correction product acceptance gate across multiple real songs/roles before changing public copy.

## NON-NEGOTIABLES

- Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.
- Canonical branch: `songsterr-fresh-pipeline-v1`.
- Archived V143/Gomyway work remains archive/evidence only unless explicitly requested.
- Timing/measure structure precedes trusting note placement.
- `structureMap` is first-class and consumed downstream.
- Preserve detected MIDI/event identity; never silently alter notes to improve notation or fingering.
- Never drop pitches merely to satisfy a shape/path optimizer.
- Preserve existing `/ai-tab` preview → unlock → full PDF → email/download customer flow.
- No Production or main changes.
- No accidental Modal/GPU/model/professional-scorer/training/real-audio activity.
- Keep this checkpoint updated after each meaningful milestone.
