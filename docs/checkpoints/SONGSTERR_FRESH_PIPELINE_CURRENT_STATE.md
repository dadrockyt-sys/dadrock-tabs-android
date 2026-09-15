# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — pipeline hardening V1 complete and code/synthetic regression green; no new real-media/model execution
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
Latest hardening result: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_HARDENING_V1_RESULT.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP/research stays under `scripts/songsterr-fresh/`.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Synthetic/smoke evidence must never be represented as authoritative correctness validation.

## GLOBAL AUTHORIZATION — UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

The user's `Lets fix the weak points of this pipeline and make it work.` authorized the engineering hardening recorded below. It did not authorize another real EGFxSet/Basic Pitch execution and did not change any global field.

## V6 — FROZEN / UNCHANGED

Authority remains preregistration `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75` with implementation/scoring already frozen.

Essentials remain Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true. Official correctness still requires the frozen real upstream gates and >=1,000 pooled V6-positive estimates with the existing Wilson/stratum criteria. Do not tune from diagnostic observations.

## HISTORICAL EGFxSET SMOKE — STILL FAIL, NOT REWRITTEN

Candidate remains EGFxSet v1.0 `Clean.zip#Clean/Bridge/6-0.wav`, exact member SHA-256 `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`, independent label string 6 / fret 0 / MIDI 40.

Original run `34935565328` failed at runtime because NumPy 2.2.6 was incompatible with TFLite Runtime 2.14.0.

The separately authorized repaired run used the prospectively frozen environment Python 3.10.21 + Basic Pitch 0.4.0 + TFLite Runtime 2.14.0 + NumPy 1.26.4:

- run `34936227380`
- job `104274605954`
- artifact `10383413992`
- immutable Basic Pitch JSON SHA-256 `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`
- exactly one successful predict invocation
- emitted MIDI set `{40,68}`
- MIDI 40 matched expected E2/string6/fret0
- MIDI 68 was extra
- frozen score: `PASS_RUNTIME`, `FAIL_PITCH`, `FAIL_POSITION`, overall `FAIL_NON_AUTHORIZING_SMOKE`

Dedicated result checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_EGFXSET_REPAIR_RERUN_RESULT.md`.

Do not post-filter that historical result into a PASS.

## PIPELINE HARDENING V1 — COMPLETE / GREEN

Final result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_PIPELINE_HARDENING_V1_RESULT.md`
commit `1cd209f2865da079766025d0802fe3ed56ec48e8`.

### 1. Raw model events are proposals, not automatic notes

The core evidence adapter now recognizes:

- `unambiguous`: independently corroborated; promotes;
- `rejected`: explicitly rejected; preserved but never promotes;
- `ambiguous`: insufficient qualification; unresolved;
- `no-candidate`: unresolved.

Only `unambiguous` enters `promotedEvents`. Rejected candidates retain MIDI/timing/confidence/provenance and are not silently deleted.

### 2. Exact qualification identity/population is fail-closed

New builder:
`scripts/songsterr-fresh/build_qualified_isolated_polyphonic_note_evidence.mjs`

It requires exact note-identity binding and exact one-to-one qualification coverage. Missing/extra/duplicate/mismatched rows fail closed. Basic Pitch candidate confidence is explicitly diagnostic-only and cannot own the decision.

Bridge into the existing adapter/evaluator path:
`scripts/songsterr-fresh/adapt_qualified_note_evidence_v1.mjs`.

### 3. Independent DSP note-birth qualifier

Prospective DSP freeze:
`docs/checkpoints/SONGSTERR_FRESH_MODEL_NOTE_QUALIFIER_DSP_V1_PRE.md`.

Implementation:
`scripts/songsterr-fresh/qualify_basic_pitch_note_births_v1.py`.

It invokes no model and ignores Basic Pitch confidence for decisions. It reuses the pre-existing frozen V6 onset-birth/harmonic-necessity DSP constants unchanged. Left-edge pre-context is supplied deterministically with zero padding only when needed; future/right-edge audio is never fabricated.

Synthetic result: genuine E2 birth is corroborated while a MIDI-68 fifth-harmonic proposal during the sustained E2 is rejected. Reversing Basic Pitch confidences does not change the decision.

### 4. Playable fingering is no longer presented as physical certainty

Prospective freeze:
`docs/checkpoints/SONGSTERR_FRESH_PHYSICAL_POSITION_AMBIGUITY_V1_PRE.md`.

The deterministic core preserves its existing preferred playable layout but now also reports:

- `shapeCandidateCount`
- `physicalShapeResolved`
- `positionSelectionMethod`

`shapeResolved` remains backward-compatible and means a complete playable layout exists. `physicalShapeResolved:true` now requires exactly one valid full layout. Multiple layouts are explicitly marked `heuristic-preferred-layout` rather than physical truth.

Tests verify MIDI 40 is uniquely string6/fret0 under standard tuning while higher notes such as MIDI64 can have multiple playable positions.

## FINAL COMBINED REGRESSION

Workflow: `.github/workflows/songsterr-model-note-qualification-v1-tests.yml`
Workflow commit: `7027810ff9fc8f21f06ad17141319c54acd8139c`
Run: `34938422696`
Job: `104281318739`
Attempt: `1`
Conclusion: `success`

All final steps passed:

- candidate confidence diagnostic-only contract;
- model-note qualification structural/fail-closed tests;
- physical-position ambiguity tests;
- frozen Python 3.10.21 environment;
- NumPy 1.26.4 / SciPy 1.15.3 DSP test environment;
- independent DSP note-birth qualifier synthetic tests.

No EGFxSet audio, Basic Pitch inference, alternate candidate, reference tab, or real corpus was executed in this hardening run.

An old archived Gomyway workflow was automatically awakened by its pre-existing broad branch trigger during ordinary pushes. Its output was not used or treated as reopened work. Do not resume it.

## PURPOSE-BUILT AUTHORITATIVE ROUTE

The completed software-lineage no-gap conclusion remains unchanged. Authoritative correctness still requires the frozen physical calibrated route, currently budget-paused. Do not manufacture another synthetic software-lineage gate.

## NEXT HIGH-VALUE VALIDATION — NOT YET AUTHORIZED

The next useful diagnostic does **not** need another Basic Pitch inference.

If the user explicitly authorizes a real-audio validation, freeze that execution prospectively and reuse:

1. the exact already-verified EGFxSet WAV identity; and
2. the immutable repaired-run Basic Pitch JSON SHA-256 `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`.

Run only:

`independent DSP qualifier -> qualified evidence builder -> adapter/evaluator -> deterministic core/exposure`

No threshold/status changes may occur after observing that result. Such a test remains non-authoritative and cannot alter the historical all-events smoke score or global authorization flags.
