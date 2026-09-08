# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-07 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## RESET DECISION

The prior `v143-contextual-prune-lobo` branch is now historical/archive evidence. Do not continue extending its old scorer, workflow, candidate, canary, correction-plan, or checkpoint maze inside this fresh pipeline.

This branch starts a clean Songsterr-inspired transcription architecture from the independently motivated clues already documented in the repository. The goal is better musical transcription quality through explicit structure + instrument conditioning, not preservation of stale experimental gates.

## SOURCE CLUES TO CARRY FORWARD

Carry forward only the architecture ideas, not the old evaluator contracts:

1. preserve full-mixture audio/context for global musical structure;
2. allow a role-specific/local note carrier for pitch/onset evidence;
3. make structure first-class: tempo, meter, pickup, straight/triplet feel;
4. make instrument configuration first-class: lead/rhythm/bass role, tuning, capo;
5. fuse global structure + local note evidence before final timing/tab decoding;
6. perform contextual onset/rhythm decoding rather than independent nearest-grid rounding;
7. decode simultaneous notes as playable shapes rather than unrelated single-note fret choices;
8. keep provenance and uncertainty visible so output remains editable.

Reference documents on the archived branch include:
- `docs/checkpoints/SONGSTERR_ARCHITECTURE_GAP_INVENTORY_20260903.md`
- `lib/aiTabConditioningV1.mjs`
- `lib/aiTabConditionedShadowProjectionV1.mjs`

Those files are clues/reference material only. Fresh code should live in an isolated namespace and should not depend on V143 implementation helpers unless a dependency is deliberately reviewed and adopted.

## ISOLATION RULES

Fresh pipeline code must not import or depend on legacy experimental scoring/gating layers such as:
- old V143 real-audio canaries;
- historical Gomyway professional/reference graders;
- rhythm-holdout gates;
- correction-plan/sidecar score machinery;
- Jimmy Page/V143 render payload helpers;
- optimizer/training/threshold-sweep scripts;
- legacy candidate replay gates.

Old metrics such as `100% pitch / 90.321% onset / 69.004% note-count` remain historical context only. They are not acceptance criteria for this new pipeline unless the exact evaluator is later recovered and intentionally adopted.

## FRESH PIPELINE LAYOUT

Build under a new isolated top-level area, proposed:

`songsterr_pipeline/`

Initial modules:
- `contracts/` — structure + instrument configuration schemas;
- `structure/` — tempo/meter/pickup/beat-grid representation;
- `events/` — normalized pitch/onset event model and onset clusters;
- `decode/` — contextual timing/rhythm decoding;
- `fretboard/` — playable simultaneous-shape and phrase-path decoding;
- `evaluate/` — transparent deterministic metrics written from scratch;
- `tests/` — synthetic/reference-free deterministic fixtures.

## PHASE ORDER

### Phase 0 — clean deterministic core
- define fresh contracts and event schema;
- add CPU-only synthetic fixtures;
- implement measure-aware onset-cluster placement;
- preserve exact MIDI pitches;
- implement joint simultaneous-note grouping/voicing legality;
- add transparent metrics with explicit formulas and raw counts.

### Phase 1 — phrase-level musical decoding
- ties/rests/syncopation/rhythm spelling;
- phrase-continuity timing decisions;
- phrase-level fretboard path optimization;
- confidence/provenance output.

### Phase 2 — audio integration
Only after the deterministic core is stable, connect existing/new audio inference behind a narrow adapter. No model/GPU run is required merely to build or test Phases 0–1.

## SAFETY / RUNTIME BOUNDARY

- Do not touch Production.
- Do not modify `main`.
- No automatic Modal/GPU/model inference.
- No professional/reference scorer.
- No optimizer/training/threshold sweep.
- No manual real-audio canary merely to continue development.
- Prefer CPU-only unit/static/synthetic validation first.

The archived V143 async safety facts remain relevant to the existing product but do not become design constraints for the fresh deterministic core unless/when integration reaches the existing API/runtime.

## IMMEDIATE NEXT TASK

Create the isolated `songsterr_pipeline/` scaffold and first deterministic contract/tests. The first implementation should prove:

- structure prior serialization;
- role/tuning/capo legality;
- exact MIDI pitch preservation;
- stable simultaneous onset grouping;
- measure-aware timing representation;
- no imports from legacy V143 scoring/gating modules.

Checkpoint this file after each meaningful fresh-pipeline milestone.
