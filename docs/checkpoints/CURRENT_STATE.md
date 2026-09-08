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

## IMPLEMENTED CLEAN BASELINE

Branch creation base: archived V143 head `555e545ff5a9a55c5b440122186c455e43442a00`.

Fresh commits so far:
- `a51f87d24af0cbcb34d9bc477cdef6bef490c16d` — replace inherited V143 checkpoint with fresh-pipeline source of truth;
- `4f9f4d508689abcb907488c6e7ec05fe73a9c8a4` — isolated `songsterr_pipeline/package.json` using only Node's built-in test runner;
- `212be220b96de687f55cce2ca3e7698b1ac9dadb` — first deterministic core in `songsterr_pipeline/index.mjs`;
- `c682355c173f47dbb250175fb4eca718a8c91a20` — seven synthetic/reference-blind tests;
- `f0ac845c2820acb301e801060920d97dd1d4f956` — clean pipeline README/boundary;
- `c39943f176fb557ed9b4a68c1ec609ce1e698aa0` — manual-only CPU test workflow.

The deterministic core currently:
- normalizes structure + instrument conditioning independently of V143 helpers;
- resolves tempo/meter/pickup/straight-or-triplet grid context;
- groups near-simultaneous events before timing projection;
- anchors full-measure snapping after the pickup rather than blindly rounding from time zero;
- enumerates legal tuning/capo string/fret positions while reconstructing exact MIDI pitch;
- solves simultaneous note clusters as one unique-string playable shape;
- preserves every source event rather than dropping pitches when a cluster shape cannot be resolved;
- reports raw transform metrics: source/output count, count delta, exact MIDI matches, pitch-preservation rate, cluster count, moved onsets, playable assignments, unresolved assignments;
- declares `referenceBlind=true` and `legacyV143ScorerImported=false`.

Synthetic tests cover:
1. structure/role/tuning/capo serialization;
2. pickup-aware measure-grid snapping;
3. stable onset clustering without chain-merging unrelated attacks;
4. exact MIDI reconstruction from string/fret positions;
5. simultaneous-note unique-string shape decoding;
6. zero event-count drift + exact source MIDI preservation through the fresh core;
7. rejection of invalid tuning.

The dedicated workflow `.github/workflows/songsterr-fresh-pipeline-v1-tests.yml` is `workflow_dispatch` only, `contents: read`, CPU-only, and runs only `npm test` inside `songsterr_pipeline/`. It has **not** been dispatched yet.

GitHub Actions query for head `c39943f...` returned **zero automatic workflow runs**, confirming the initial fresh commits did not wake up the stale CI maze.

## FRESH PIPELINE LAYOUT

Current clean top-level area:

`songsterr_pipeline/`

Current files:
- `package.json`
- `index.mjs`
- `tests/pipeline.test.mjs`
- `README.md`

The single-file deterministic core is intentional for the first proof. Split it into focused modules only after its clean invariants/tests are established.

Planned module boundaries when refactoring becomes useful:
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

Status: first baseline implementation is committed. Next milestone is to execute/verify the isolated tests and fix only fresh-pipeline defects if found.

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
- No legacy V143 canary/gate should block this branch.
- Prefer CPU-only unit/static/synthetic validation first.

The archived V143 async safety facts remain relevant to the existing product but do not become design constraints for the fresh deterministic core unless/when integration reaches the existing API/runtime.

## IMMEDIATE NEXT TASK

Verify the isolated fresh-pipeline tests. If they pass, continue Phase 0 with the next genuinely musical deterministic layer:

1. separate onset placement from rhythm spelling;
2. represent beat-boundary-aware duration/tie/rest decisions;
3. add explicit raw diagnostics for every timing transformation;
4. keep event count and MIDI pitch invariant while those representations evolve.

Checkpoint this file after each meaningful fresh-pipeline milestone.
