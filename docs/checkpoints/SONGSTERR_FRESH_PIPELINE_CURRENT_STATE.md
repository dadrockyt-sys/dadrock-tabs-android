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
- `a0fbc5fc54aa1bf91a7cc199f373d5018d158a11` — first-class musical event + rhythm notation layer;
- `9ce440755d1d70813d1043210d8bd8a28a650cd3` — six rhythm/event-schema invariant tests.

### Deterministic core

`songsterr_pipeline/index.mjs` provides:
- explicit structure/instrument conditioning;
- pickup-aware measure timing;
- stable simultaneous-onset clustering;
- joint unique-string playable chord-shape solving;
- exact MIDI reconstruction checks;
- no intentional note dropping;
- raw diagnostics for event count, pitch preservation, timing movement, and unresolved playable assignments.

### Musical event / notation layer

`songsterr_pipeline/rhythmNotation.mjs` preserves one source note = one stable event identity while notation may contain multiple tied segments.

Current behavior includes source `end`/`duration`, unresolved missing duration, structure-grid duration projection, minimum subdivision duration for collapsed snaps, beat/measure tie splitting, rest-gap diagnostics without fake MIDI notes, and straight/triplet subdivision behavior.

## VALIDATION STATUS

### Clean 13-test surface — PROVEN PASSING

On 2026-09-08, the exact branch-current `songsterr_pipeline/` implementation and both committed test files were mirrored into an isolated local Node runtime and executed with:

`node --test tests/pipeline.test.mjs tests/rhythmNotation.test.mjs`

Result:
- tests: **13**
- pass: **13**
- fail: **0**
- cancelled: **0**
- skipped: **0**

This is the first actual execution proof for the clean surface. It establishes the committed invariants for:
- exact MIDI preservation;
- zero source-event-count drift in the tested fixtures;
- stable non-chain onset clustering;
- unique-string playable chord assignment;
- tuning/capo reconstruction;
- pickup-aware grid positioning;
- beat/measure tie segmentation;
- rest diagnostics without note inflation;
- straight/triplet subdivision behavior;
- explicit unresolved duration when duration evidence is absent.

No Production/main state, model/GPU workflow, professional scorer, training path, real-audio canary, or archived V143/Gomyway pipeline was touched during this validation.

## CURRENT ENGINEERING MILESTONE

Now implement `structureMap` as the first-class fresh analyzer contract before connecting any real-audio/model work.

Required capabilities:
- tempo segments / tempo changes;
- meter segments / meter changes;
- downbeat timestamps;
- explicit measure start/end boundaries;
- pickup duration;
- beat/subdivision positions;
- straight/triplet feel;
- confidence and provenance per structural decision;
- deterministic validation of ordering/non-overlap where applicable;
- downstream note timing must consume this object rather than invent a post-hoc grid.

Backward-compatible `structurePrior` support may remain temporarily for the original 13 tests, but new structure-first work must use `structureMap` directly.

## NEXT EXECUTION ORDER

1. **Implement and test first-class `structureMap`.**
2. Add structure-first synthetic fixtures for pickup, syncopation, beat/measure crossings, straight-vs-triplet behavior, tempo-change boundary, meter-change boundary, and slightly spread chord attacks that are musically simultaneous.
3. Harden contextual rhythm spelling: beat-strength-aware ties, dotted values, explicit rest spelling, syncopation, pickup edge cases, phrase feel consistency, quantization displacement diagnostics.
4. Upgrade local chord/shape decoding: stronger fret-span/stretch constraints, role-aware open-string preference, impossible-shape rejection, deterministic tie-breaking, neighboring hand-position context. Never drop pitches merely to make fingering easier.
5. Add phrase-level fretboard path optimization with pitch correctness and physical playability ahead of movement aesthetics.
6. Define a fresh evaluator that reports raw structure, event, pitch, timing, playability, motion, notation, tie/rest, and unresolved-duration diagnostics before any composite score.
7. Only after the deterministic structure/notation/fretboard system is stable, connect real-audio evidence in this order: **full-mixture structure analysis → structureMap → role-conditioned note evidence → clean event schema → notation → fretboard decoding**.
8. Map clean analyzer output into the existing `/ai-tab` metadata/render/PDF contract.
9. Define the no-human-correction product acceptance gate across multiple real songs/roles before changing public copy.

## NON-NEGOTIABLES

- Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.
- Canonical branch: `songsterr-fresh-pipeline-v1`.
- Archived V143/Gomyway work remains archive/evidence only unless explicitly requested.
- Timing/measure structure precedes trusting note placement.
- `structureMap` must be first-class and consumed by downstream note/rhythm/tab stages.
- Preserve detected MIDI/event identity; never silently alter notes to improve notation appearance.
- Preserve existing `/ai-tab` metadata → technique/render → watermarked preview → PayPal/free-token unlock reference → full PDF → email/download flow.
- No Production or main changes.
- No accidental Modal/GPU/model/professional-scorer/training/real-audio activity.
- Keep this checkpoint updated after each meaningful architecture, implementation, or validation milestone.
