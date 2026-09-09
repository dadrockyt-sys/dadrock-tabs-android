# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-09 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the **only canonical fresh-chat checkpoint** for the Songsterr-inspired fresh pipeline. Do not resume archived V143/Gomyway implementation, reference tabs, scorer logic, or historical percentages unless the user explicitly asks.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from uploaded audio to a usable finished tab without a mandatory human correction step. Musical identity and timing correctness take priority over cosmetic/composite scores.

Preserve the existing `/ai-tab` customer journey:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock → full tab PDF → browser download + email delivery**

Fresh work replaces the transcription brain, not the customer/paywall/PDF journey.

## FOUNDATIONAL ORDER

**full-mixture audio → frozen timing/measure map → role-isolated structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

`structureMap` is first-class. Once accepted for a fixture, note inference must not rewrite tempo, meter, downbeats, measures, pickup, feel, or subdivisions.

Never silently change/drop detected MIDI or event identity to improve notation, fingering, path motion, ambiguity coverage, or legacy rendering.

## PROJECT / AUTHORIZATION BOUNDARY

- Work only on `songsterr-fresh-pipeline-v1`.
- Do not modify `main` or Production.
- Old `v143-contextual-prune-lobo` / Gomyway/V143 is archive/evidence only.
- Historical scorer percentages are not fresh acceptance gates.
- On 2026-09-08 America/Toronto the user explicitly authorized the **fresh reference-blind model/source-separation path**, including GPU use if technically useful.
- That authorization does **not** authorize archived V143 code, reference tabs, reference-based correction, professional/reference scorer use, training/fine-tuning, or broad optimizer sweeps.
- `songsterr_pipeline/` remains deterministic, model-free, process-free, and network-free. Model/audio/DSP execution lives under `scripts/songsterr-fresh/` and passes validated JSON into the deterministic namespace.
- Model execution authorization is separate from musical acceptance. Model evidence must pass independent validation before customer eligibility can exist.

## AUTHORIZED AUDIO FIXTURE

Exact authorized fixture on `main`:
- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Git blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration ~210.674648526 s

Canaries fetch only that exact blob and verify `git hash-object`.

## ACCEPTED / FROZEN STRUCTURE

Frozen structure identity: `fnv1a32:2f493225`, canonicalLength 19653.

Key facts:
- duration ~210.67465 s
- 4/4
- straight feel
- pickup / first downbeat ~0.65016 s
- 115 measures
- 113 measure-local tempo segments
- beat-grid MAE ~7.14 ms
- RMSE ~10.63 ms
- max ~58.05 ms
- acceptance `true`

This structure is immutable downstream.

## DETERMINISTIC FRESH CORE

Namespace: `songsterr_pipeline/`

Important boundaries/modules:
- `structureMap.mjs`
- `structureRhythmNotation.mjs`
- `contextualRhythmSpelling.mjs`
- `playableShapeDecoder.mjs`
- `fretboardPathOptimizer.mjs`
- `structureFretboardPath.mjs`
- `freshEvaluator.mjs`
- `productShellAdapter.mjs`
- `deterministicPipeline.mjs`
- `audioStructureAdapter.mjs`
- `structureIdentity.mjs`
- `noteEvidenceAdapter.mjs`
- `noteEvidenceDiagnostics.mjs`
- `noteEvidenceEvaluator.mjs`
- `noteEventExposure.mjs`

`tests/boundaryGuard.test.mjs` protects the deterministic namespace from archived/model-bearing runtime dependencies, network calls, and process launches.

## GUARDED CPU BASELINE

CPU pitch analyzer:
`scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`

Contract: `songsterr-fresh-cpu-note-evidence-v4`.

Exact fixture:
- 492 onsets
- 1,130 candidates
- 139 local unambiguous selections
- 353 ambiguous
- 0 no-candidate
- MIDI 40 appears in 97/139 local selections (~69.8%)
- role relevance unresolved
- polyphony unresolved
- instrument isolation `none`

Event exposure:
- pitch-resolved: **139**
- role-accepted: **0**
- complete-tab/customer-eligible: **0**

The CPU baseline remains useful as a conservative regression path, not a finished transcription path.

### Latest CPU regression proof

Run **`34309259214`**, job **`102332311684`**, head `54d9e4792d8255d56f6aec82977ac083b9c2bae4`:
- conclusion `success`
- artifact **`10087798684`**
- artifact name `songsterr-fresh-gomyway-midterm-note-evidence`
- digest `sha256:a1dbe85348f66847045e616d9726ffce986a82e995de0817fb20159e6fbf9d08`
- deterministic tests **97/97 pass**
- CPU model-upstream default remained denied
- CPU duration result remained 103 resolved / 36 unresolved

## AUTHORIZED MODEL PATH — FIRST REAL CANARY GREEN, VALIDATION STILL PENDING

Architecture:
1. rebuild and verify frozen full-mixture structure;
2. Demucs `4.1.0`, `htdemucs_6s`, guitar stem for reference-blind role isolation;
3. Basic Pitch `0.4.0` on isolated guitar stem for polyphonic onset/pitch identity;
4. Basic Pitch decoded note-off times remain **diagnostic only**;
5. model pitch evidence is duration-free when it crosses into the dedicated duration stage;
6. dedicated release stage remains sole active duration authority;
7. note evidence is adapted only with an explicit model-upstream authorization flag;
8. independent `MODEL_EVIDENCE_VALIDATION_PENDING` blocker prevents customer eligibility until model validation is deliberately completed.

Fresh model files/contracts:
- `scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py` — `songsterr-fresh-basic-pitch-isolated-guitar-v1`
- `scripts/songsterr-fresh/build_isolated_polyphonic_note_evidence.mjs` — `songsterr-fresh-isolated-polyphonic-note-evidence-v1`
- `scripts/songsterr-fresh/run_model_note_evidence_pipeline_canary.mjs`
- `.github/workflows/songsterr-fresh-model-guitar-polyphonic-canary.yml`

`noteEvidenceEvaluator.mjs` contract is version 3 and requires explicit model-path validation before complete-tab acceptance.

### Authoritative model canary

Run **`34309319200`**, job **`102332488694`**, head **`9d4a9d823e2d7da9c9e58e0b0d8b1e0881822180`**:
- conclusion **success**
- artifact **`10087877760`**
- artifact name `songsterr-fresh-model-guitar-polyphonic-evidence`
- artifact size 470,670 bytes
- digest **`sha256:c051dfe5166a0d4fb019cf50aaae7afa97c7f477225657d9cc31b311c612ca31`**
- deterministic tests **97/97 pass**

Demucs evidence:
- model `htdemucs_6s`
- guitar stem SHA256 `d47f51ac8fe8f100c91d7f3d3d518e3f39bed25b995ed7982208445bcdc99d3c`
- CPU execution for reproducibility
- no legacy scorer/reference tab

Basic Pitch evidence:
- **1,128 notes**
- **1,020 start clusters**
- **98 polyphonic start clusters**
- max simultaneous cluster size **3**
- note density ~**5.35 notes/sec**
- decoded model note ends are diagnostic only
- MIDI 40: **40/1,128 = 3.55%**
- dominant MIDI 52: **245/1,128 = 21.72%**
- the old full-mixture E2 collapse is therefore absent on the isolated model path

Selected MIDI histogram highlights:
- 52: 245
- 64: 213
- 59: 137
- 62: 105
- 57: 78
- 67: 41
- 55: 40
- 40: 40

Frozen-structure alignment:
- mean absolute displacement ~29.90 ms
- median ~29.72 ms
- p95 ~55.42 ms
- max ~59.45 ms

Basic Pitch note-amplitude confidence is explicitly **not a calibrated probability**:
- mean ~0.5022
- median ~0.4938
- p10 ~0.3656
- p90 ~0.6495

Model decoder currently emits one selected MIDI candidate per decoded note. `unambiguous` here means decoder output is singular; it must not be overinterpreted as independently proven ground truth.

## SINGLE DURATION AUTHORITY

Active duration stage:
`scripts/songsterr-fresh/estimate_selected_pitch_releases.py`

Contract: `songsterr-fresh-cpu-spectral-release-evidence-v2`.

Hard rules:
- input must be duration-free;
- any upstream non-null `durationSeconds` or `sourceEnd` is rejected;
- CPU path rejects model/GPU upstream by default;
- authorized model evidence requires explicit `--allow-model-upstream`;
- model note-off times never become active duration;
- same-pitch reattack remains a censor/search boundary, not an invented duration;
- next generic onset is never used as duration.

Authoritative model-path duration result:
- attempted **1,128**
- resolved **591**
- unresolved **537**
- resolution rate **52.39%**
- unresolved reasons:
  - **517** `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
  - **16** `INSUFFICIENT_ONSET_TO_FLOOR_CONTRAST`
  - **4** `NO_CLEAR_SUSTAINED_SPECTRAL_RELEASE`
- same-pitch reattack censor count **956**
- mean resolved duration ~0.4800 s
- median ~0.3484 s
- max ~3.9268 s
- mean heuristic duration confidence ~0.9199

Duration completeness is the main current musical blocker.

## AUTHORIZATION / FAIL-CLOSED PROOF

The authoritative model workflow proves both sides of the execution boundary:
- adapting model evidence **without** `--allow-model-upstream` fails with `CPU_NOTE_EVIDENCE_CANARY_MODEL_NOT_ALLOWED` and creates no output;
- the same evidence **with** the explicit flag adapts successfully;
- legacy scorer provenance remains forbidden.

Model evidence evaluation currently returns exactly:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

The earlier blockers are cleared on this model path:
- no `ROLE_RELEVANCE_UNRESOLVED`
- no `POLYPHONY_UNRESOLVED`
- no `PITCH_EVIDENCE_UNRESOLVED`

Event exposure:
- pitch-resolved: **1,128**
- role-accepted: **1,128**
- complete-tab/customer-eligible: **0**

Deterministic exercise:
- source/final events: **1,128**
- exact MIDI preserved: **1,128/1,128**
- fretboard path resolves: **true**
- unresolved durations: **537**
- unresolved rhythm spellings: **31**
- rawIntegrityPassed: **false**
- rawResultReady: **false**
- deliveryReady: **false**
- structuredRenderEligible: **false**

This is the desired state: the major role/polyphony capability jump is visible and mechanically testable, while customer delivery remains fail-closed.

## NEXT ENGINEERING STEP

Do **not** set `modelValidationComplete: true` yet.

The next justified milestone is to improve the **same single duration authority**, especially the 517 reattack-censored notes, without copying Basic Pitch decoded note-offs and without setting duration equal to the next onset.

Basic Pitch `predict()` exposes raw model activation matrices (`note`, `onset`, `contour`) in addition to decoded note events. Use the raw per-pitch `note` activation as additional release evidence inside the dedicated duration stage.

Planned approach:
1. retain a compact, auditable Basic Pitch per-pitch activation representation tied to the exact model run;
2. for same-pitch rearticulations, search between onset and next same-pitch reattack for a **real sustained activation/spectral valley**;
3. if a sufficiently strong valley is independently supported, use that observed valley time as release evidence;
4. otherwise remain unresolved;
5. never use `diagnosticModelEndSeconds` as active duration;
6. add negative CI proof that activation evidence cannot populate upstream duration/end fields and that decoded model note-off leakage is still rejected;
7. inspect resulting coverage/distribution before changing model validation status.

Avoid threshold sweeps or hidden composite scores. Start with fixed, auditable evidence rules and preserve per-event provenance.

## NON-NEGOTIABLES

- Canonical branch/checkpoint above remain authoritative.
- Frozen structure precedes note placement and cannot be rewritten downstream.
- Never silently alter detected MIDI/event identity.
- Never drop pitches merely to satisfy fingering/path/legacy rendering.
- Preserve the existing `/ai-tab` preview → unlock → full PDF → email/download flow.
- No `main`/Production changes.
- Real-audio work stays inside the exact authorized fixture unless the user explicitly authorizes another fixture.
- Archived V143/Gomyway implementation and scorer/reference knowledge remain untouched.
- Model execution is authorized for the fresh path, but model evidence remains non-deliverable until explicit validation succeeds.
- Keep this checkpoint updated after every meaningful milestone.
