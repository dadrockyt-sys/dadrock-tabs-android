# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-07 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`

This is the **only canonical fresh-chat checkpoint for the new Songsterr-inspired pipeline**.

Do not use the generic `docs/checkpoints/CURRENT_STATE.md` for this project. Do not resume the old V143/Gomyway investigation unless the user explicitly asks to return to that archived work.

## PROJECT BOUNDARY

The old branch `v143-contextual-prune-lobo` is archive/evidence only.

The new branch intentionally does **not** inherit old V143 scorer contracts, Gomyway percentages, correction plans, canary gates, professional-reference workflows, model budgets, or stale failed-test expectations as acceptance criteria.

Historical values such as `100% pitch / 90.321% onset / 69.004% note-count` may be referenced as old evidence only. They do not define success for this fresh pipeline.

**Do not touch Production.**

Do not dispatch Modal/GPU/model-bearing workflows, professional scorers, training, optimizer sweeps, or real-audio canaries unless the user explicitly authorizes them later.

## SONGSTERR-INSPIRED CLUES TO CARRY FORWARD

Carry forward architecture ideas only:

1. preserve full-mixture context for global musical structure;
2. allow a role-specific/local carrier for note evidence;
3. make structure first-class: tempo, meter, pickup, straight/triplet feel;
4. make instrument configuration first-class: lead/rhythm/bass, tuning, capo;
5. fuse structure + note evidence before final timing/tab decoding;
6. group simultaneous notes before fretboard assignment;
7. solve simultaneous notes as a playable chord/shape, not independently;
8. add phrase-aware rhythm spelling and fretboard continuity later.

Public Songsterr observations are clues only, not claims about Songsterr private implementation.

## FRESH IMPLEMENTATION ALREADY PRESENT

Branch: `songsterr-fresh-pipeline-v1`

Key commits:
- `a51f87d24af0cbcb34d9bc477cdef6bef490c16d` — fresh reset checkpoint
- `212be220b96de687f55cce2ca3e7698b1ac9dadb` — first isolated deterministic Songsterr core
- `c682355c173f47dbb250175fb4eca718a8c91a20` — focused synthetic tests
- `f0ac845c2820acb301e801060920d97dd1d4f956` — manual-only CPU test workflow
- `c39943f176fb557ed9b4a68c1ec609ce1e698aa0` — fresh pipeline README
- `32479ab6948665964fd164e12d3a629cc5aaeb60` — checkpoint fresh scaffold milestone

Fresh namespace:
- `songsterr_pipeline/`

Current deterministic core already provides:
- explicit structure/instrument conditioning;
- pickup-aware measure timing;
- stable simultaneous-onset clustering;
- joint unique-string playable chord-shape solving;
- exact MIDI reconstruction checks;
- no intentional note dropping in the deterministic core;
- raw diagnostics for event count, pitch preservation, timing movement, and unresolved playable assignments.

Validation surface:
- seven synthetic/reference-free tests;
- Node built-in test runner only;
- dedicated manual-only CPU workflow;
- no legacy V143 test suite required for fresh-pipeline progress;
- no automatic Actions run was triggered by the initial fresh scaffold commits.

The dedicated workflow has **not** been dispatched yet. Do not claim the tests passed until they are actually executed.

## NEXT STEPS — IN ORDER

### 1. Execute or locally reproduce only the fresh synthetic tests

Run only the isolated `songsterr_pipeline/` test surface when a safe execution path is available.

Required first proof:
- exact MIDI pitch preservation;
- no event-count drift;
- stable simultaneous clustering;
- legal unique-string chord assignment;
- tuning/capo correctness;
- pickup-aware measure positioning.

Do not use old V143 CI failures as blockers for this proof.

### 2. Add a first-class internal musical event schema

Separate raw inferred notes from notation/render decisions.

Target concepts:
- source onset/end;
- clustered musical onset;
- MIDI pitch;
- confidence/evidence provenance;
- measure/beat position;
- role/tuning/capo context;
- chord-cluster identity;
- decoded string/fret;
- duration spelling state;
- tie/rest state.

Keep this schema deterministic and reference-blind.

### 3. Build measure-aware rhythm spelling

Replace simple nearest-grid timing with contextual notation logic that can reason about:
- beat boundaries;
- note durations;
- ties across beats/measures;
- rests;
- syncopation;
- straight vs triplet consistency;
- pickup handling;
- phrase continuity.

Protect MIDI pitch and event identity while changing notation representation.

### 4. Upgrade chord/shape decoding

Current joint chord solving is the first clean step. Next improve it with:
- fret-span penalties;
- hand-position continuity;
- open-string preference by role/context;
- duplicate-string exclusion;
- impossible-shape rejection;
- stable ordering for deterministic output.

Do not drop pitches merely to make a shape easier unless an explicit later policy authorizes that behavior.

### 5. Add phrase-level fretboard path optimization

Move from local previous-note heuristics toward deterministic phrase-level path selection, for example beam/Viterbi-style search over playable states.

Optimize for:
- pitch correctness first;
- playability;
- compact hand movement;
- stable position choices;
- chord-shape continuity;
- role-specific behavior.

### 6. Define a new fresh-pipeline evaluator

Do not inherit the old Gomyway comparator blindly.

The fresh evaluator should report raw counts before any composite score, including:
- source notes vs rendered notes;
- exact MIDI preservation;
- onset-cluster preservation;
- timing displacement distribution;
- simultaneous-group preservation;
- playable/unplayable assignments;
- fret-span and hand-motion diagnostics;
- notation completeness by measure;
- ties/rests/duration consistency.

If a composite score is added later, its formula must live in source control beside the raw metrics.

### 7. Only then connect real model/audio output

First keep synthetic deterministic tests green.

After explicit user authorization, connect a real note-carrier/model result to the clean schema without importing the old V143 scorer/gate maze.

Keep Production untouched until a later deliberate promotion decision.

## FRESH-CHAT START INSTRUCTION

When starting a new chat, use this exact instruction:

`Please continue from docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md on branch songsterr-fresh-pipeline-v1. Keep that file updated often while you work. Do not resume the archived V143/Gomyway pipeline unless I explicitly ask.`

## NON-NEGOTIABLES

- canonical checkpoint for this project is `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`;
- branch is `songsterr-fresh-pipeline-v1`;
- old V143 branch remains archive/evidence only;
- no Production changes;
- no accidental Modal/GPU/model/professional scorer/training activity;
- no legacy scorer or failed test becomes a fresh-pipeline gate merely because it exists in the repository;
- checkpoint this file after each meaningful architecture, implementation, or validation milestone.
