# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-08 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`

This is the **only canonical fresh-chat checkpoint for the new Songsterr-inspired pipeline**.

Do not use the generic `docs/checkpoints/CURRENT_STATE.md` for this project. Do not resume the old V143/Gomyway investigation unless the user explicitly asks to return to that archived work.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from uploaded audio to a usable finished tab without a mandatory human correction step.

The immediate engineering priority is musical correctness and stability, not a cosmetic score. Preserve detected musical identity while progressively making structure, timing, rhythm spelling, chord shapes, fretboard motion, techniques, and final rendering coherent enough for product use.

Do not change public accuracy promises yet. The current `/ai-tab` page copy still allows for occasional corrections; only change that wording after the clean pipeline earns a real no-human-correction acceptance standard.

## FOUNDATIONAL RULE — TIMING AND MEASURES COME FIRST

This is non-negotiable for the fresh pipeline.

Intended real-audio order:

**full-mixture audio → timing/measure map → structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

Not:

**audio → loose notes → attempt to repair timing afterward**

The structure layer must resolve or explicitly carry uncertainty for tempo/tempo changes, downbeats, meter/meter changes, measure boundaries, pickup/anacrusis, straight/triplet feel, beat/subdivision positions, confidence, and provenance. Downstream note/rhythm/tab stages must consume that resolved structure directly.

## EXISTING `/ai-tab` PRODUCT SHELL — PRESERVE IT

Replace the transcription brain; preserve the proven customer journey:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock reference → full tab PDF → browser download + email delivery**

Existing page-facing fields include `generatedTab`, `tuning`, `tempo`, `timeSignature`, `keySignature`, `analysisEngine`, `techniques`, `renderEvents`, `measureGrid`, `confidence`, `difficulty`, and PDF artifact metadata where available.

The fresh core must not bypass or discard the preview/paywall/full-PDF flow.

## PROJECT BOUNDARY

- Old branch `v143-contextual-prune-lobo` is archive/evidence only.
- Historical Gomyway/V143 values and scorer contracts are not fresh-pipeline acceptance criteria.
- Do not touch Production or main.
- Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or real-audio canaries unless the user explicitly authorizes them.
- Old failed CI/tests do not become fresh blockers merely because they exist.

## FRESH IMPLEMENTATION PRESENT

Fresh namespace: `songsterr_pipeline/`

Recorded clean-line commits:
- `a51f87d24af0cbcb34d9bc477cdef6bef490c16d` — fresh reset checkpoint;
- `212be220b96de687f55cce2ca3e7698b1ac9dadb` — first isolated deterministic Songsterr core;
- `c682355c173f47dbb250175fb4eca718a8c91a20` — first seven synthetic tests;
- `f0ac845c2820acb301e801060920d97dd1d4f956` — fresh pipeline README;
- `c39943f176fb557ed9b4a68c1ec609ce1e698aa0` — manual-only CPU test workflow;
- `a0fbc5fc54aa1bf91a7cc199f373d5018d158a11` — compatibility musical-event + rhythm notation layer;
- `9ce440755d1d70813d1043210d8bd8a28a650cd3` — six compatibility rhythm/event-schema invariant tests;
- `3bc1c36c4d3fbeefe3a1243415de72b1a4a5a8cd` — checkpoint recording first proven 13/13 local clean-suite pass;
- `e9b56a0fdceed2dafc9715f22b5c93954098877e` — first-class `structureMap` implementation and structure-conditioned note core;
- `71e553f13aa37a4c30615c094c2679b1e9504475` — six `structureMap`/structure-conditioned core tests;
- `324420a20210a3cd88284b323968366d1e86773c` — checkpoint recording the 19/19 structure-first milestone;
- `89c6a12d604dd203b65f4e4015d7d1d246f05a9f` — structure-map-driven musical event/rhythm notation schema;
- `85b175f60406fb47a81bfebfe36ba99e52ed029f` — six structure-map-driven rhythm/notation tests.

### Compatibility deterministic core

`songsterr_pipeline/index.mjs` provides the original clean deterministic baseline with explicit conditioning, pickup-aware timing, stable onset clustering, unique-string shape solving, exact MIDI reconstruction, no intentional note dropping, and raw count/pitch/timing/playability diagnostics.

Its `structurePrior` path remains temporarily for backward compatibility and the original tests. New work should use `structureMap` directly.

### Compatibility rhythm layer

`songsterr_pipeline/rhythmNotation.mjs` preserves one source note = one stable event identity while notation may contain multiple tied segments. It remains as compatibility evidence; the first-class structure path is now `structureRhythmNotation.mjs`.

### First-class `structureMap`

`songsterr_pipeline/structureMap.mjs` now establishes structure before note placement.

It provides:
- tempo segments with confidence/provenance;
- meter segments with confidence/provenance;
- straight/triplet feel segments with confidence/provenance;
- explicit pickup duration;
- materialized pickup/full measures;
- explicit measure start/end boundaries;
- materialized downbeats;
- beat boundaries and subdivision timestamps;
- map-level confidence/provenance;
- continuity/non-overlap validation;
- rejection of tempo/meter/feel changes that do not align to a measure boundary;
- half-open segment semantics `[start, end)` so changes take effect exactly at the boundary;
- `locateInStructureMap(...)`;
- `snapTimestampToStructureMap(...)`;
- `runStructureMappedCore(...)`, whose note timing consumes the map directly before fretboard assignment.

### First-class structure-driven event / notation layer

`songsterr_pipeline/structureRhythmNotation.mjs` now consumes `structureMap` directly for note starts, note ends, duration projection, beat/measure segmentation, pickup crossings, ties, rest gaps, feel, and timing diagnostics.

Current schema behavior:
- one source note = one stable `eventId` / event identity;
- exact MIDI stays attached to the source event;
- onset projection comes from explicit structure-map subdivision slots;
- end/duration projection uses the same structure-map slot set;
- collapsed projected duration advances to the next valid structure slot rather than inventing arbitrary time;
- beat/measure/pickup crossings split into tied notation segments without duplicating source events;
- syncopated starts are diagnosed from beat-relative structure positions;
- rest gaps are diagnostics only, never fake MIDI notes;
- missing duration remains explicitly unresolved;
- per-event onset/end displacement is preserved;
- aggregate mean/max absolute onset/end displacement is reported;
- provenance records the structure-map version/source;
- legacy V143 scorer import remains explicitly false.

## VALIDATION STATUS

### Original clean surface

On 2026-09-08, the original clean surface was executed in an isolated local Node runtime:

`node --test tests/pipeline.test.mjs tests/rhythmNotation.test.mjs`

Result: **13/13 pass, 0 fail**.

### First-class structure-map surface

After implementing `structureMap`, the expanded suite was executed:

`node --test tests/pipeline.test.mjs tests/rhythmNotation.test.mjs tests/structureMap.test.mjs`

Final result: **19/19 pass, 0 fail**.

The first expanded run caught a genuine exact-boundary bug: lookup selected a segment that ended at the change timestamp. Interval semantics were corrected to `[start, end)`, then all 19 tests passed.

### Structure-driven rhythm/notation surface — CURRENT PROVEN BASELINE

After adding `structureRhythmNotation.mjs`, the complete namespace test suite was executed with:

`node --test tests/*.test.mjs`

Result:
- tests: **25**
- pass: **25**
- fail: **0**
- cancelled: **0**
- skipped: **0**

New proven behavior includes:
- pickup note tied across explicit pickup → measure 1 boundary;
- syncopated attack snapped to a structure-map subdivision with quantization displacement reported;
- same raw attack resolves differently under straight vs triplet structure maps;
- measure-crossing duration becomes tied segments without event duplication;
- silence becomes rest diagnostics without fake MIDI events;
- missing duration remains unresolved;
- exact MIDI/event-count preservation remains intact across the structure-driven path.

No Production/main state, model/GPU workflow, professional scorer, training path, real-audio canary, or archived V143/Gomyway pipeline was touched during validation.

## CURRENT ENGINEERING MILESTONE

Harden contextual rhythm spelling on top of the now-proven structure-first event schema.

Next clean goals:
- beat-strength-aware tie decisions rather than splitting every beat crossing mechanically;
- dotted values where clearer than ties;
- explicit rest spelling by beat/measure rather than only raw gap diagnostics;
- stronger syncopation-aware notation;
- more pickup edge cases;
- phrase-level straight/triplet consistency diagnostics;
- preserve raw quantization displacement and source MIDI/event identity throughout.

After rhythm spelling is stable, upgrade local chord/shape decoding with stronger physical constraints and then add phrase-level fretboard path optimization.

## NEXT EXECUTION ORDER

1. Harden contextual rhythm spelling on `structureRhythmNotation.mjs`.
2. Upgrade local chord/shape decoding: stronger fret-span/stretch constraints, role-aware open-string preference, impossible-shape rejection, deterministic tie-breaking, neighboring hand-position context. Never drop pitches merely to make fingering easier.
3. Add phrase-level fretboard path optimization with pitch correctness and physical playability ahead of movement aesthetics.
4. Define a fresh evaluator that reports raw structure, event, pitch, timing, playability, motion, notation, tie/rest, and unresolved-duration diagnostics before any composite score.
5. Only after the deterministic structure/notation/fretboard system is stable, connect real-audio evidence in this order: **full-mixture structure analysis → structureMap → role-conditioned note evidence → clean event schema → notation → fretboard decoding**.
6. Map clean analyzer output into the existing `/ai-tab` metadata/render/PDF contract.
7. Define the no-human-correction product acceptance gate across multiple real songs/roles before changing public copy.

## NON-NEGOTIABLES

- Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.
- Canonical branch: `songsterr-fresh-pipeline-v1`.
- Archived V143/Gomyway work remains archive/evidence only unless explicitly requested.
- Timing/measure structure precedes trusting note placement.
- `structureMap` is first-class and must be consumed by downstream note/rhythm/tab stages.
- Preserve detected MIDI/event identity; never silently alter notes to improve notation appearance.
- Preserve existing `/ai-tab` metadata → technique/render → watermarked preview → PayPal/free-token unlock reference → full PDF → email/download flow.
- No Production or main changes.
- No accidental Modal/GPU/model/professional-scorer/training/real-audio activity.
- Keep this checkpoint updated after each meaningful architecture, implementation, or validation milestone.
