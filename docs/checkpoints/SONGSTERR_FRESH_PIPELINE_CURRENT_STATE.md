# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-10 20:00 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the canonical current-state checkpoint for the fresh workstream. Use Git history for older verbose diagnostics.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference/professional scorer logic, training/fine-tuning, or broad optimizer/ISA sweeps unless explicitly requested.
- The `gomyway` filename authorizes the exact audio fixture only; it does not authorize the archived pipeline.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP execution stays in `scripts/songsterr-fresh/`.
- Frozen full-mixture structure precedes note inference and cannot be rewritten downstream.
- Never silently change/drop MIDI/event identity. Raw sequential Basic Pitch indices are not cross-run identity.
- Preserve `/ai-tab`: audio upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.

## AUTHORIZED FIXTURE / FROZEN STRUCTURE

Fixture: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a` on `main`.

- Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration ~210.674648526 s
- decoded separation WAV SHA-256 `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- structure identity `fnv1a32:2f493225`; canonical length `19653`
- 4/4, straight, first downbeat ~0.65016 s; 115 measures; 113 tempo segments
- beat-grid MAE ~7.14 ms, RMSE ~10.63 ms, max ~58.05 ms; accepted true
- historical structure canary run `34192662439`, job `101953726302`, commit `2a598f0f38d755faf0cd3d46543221253f1c8997`, artifact `10042777518`, digest `sha256:5ff3ce36f559bcc02efcc985a1fa06966576da0445896326e9408ada955e9b6f`

## GUARDED CPU BASELINE

`scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`, contract `songsterr-fresh-cpu-note-evidence-v4`:
- 492 onsets, 1,130 candidates, 139 local unambiguous, 353 ambiguous, MIDI 40 in 97/139 selections
- role relevance/polyphony unresolved, customer eligible 0
- regression run `34309259214`, job `102332311684`, head `54d9e4792d8255d56f6aec82977ac083b9c2bae4`, artifact `10087798684`, digest `sha256:a1dbe85348f66847045e616d9726ffce986a82e995de0817fb20159e6fbf9d08`, 97/97 tests

## FIXED MODEL PATH

Architecture:
frozen full-mixture structure → Demucs guitar isolation → Basic Pitch pitch/onset inference → duration-free model evidence boundary → dedicated release authority.

Pinned where applicable: numpy 1.26.4; torch 2.14.0; huggingface-hub 1.30.0; safetensors 0.8.0; sphn 0.2.1; demucs 4.1.0; basic-pitch 0.4.0; librosa 0.11.0; soundfile 0.13.1; tflite-runtime 2.14.0; OMP/MKL/OpenBLAS/NumExpr threads = 1; `PYTHONHASHSEED=0`.

Fixed Demucs: `htdemucs_6s`, CPU, shifts 0, overlap 0.25, segment 7 s.

Model asset authority `scripts/songsterr-fresh/verify_demucs_model_asset.py`:
- contract `songsterr-fresh-demucs-model-asset-v2`
- HF repo `adefossez/HTDemucs-6s`
- pinned revision `3c5ee475be622df764938de97e4281a7b07ffa58`
- authoritative asset upload revision `053e1404489b3dc58bf718224fac4b7316de8c93`
- `5c90dfd2.safetensors`, SHA-256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- legacy fallback not primary

An earlier copied asset-upload revision had an erroneous trailing `b`; commit `0f4b4cbe0a52657cf4989e07500041335a89db86` corrected the workflow/checkpoint assertion. Asset SHA never mismatched.

## DURATION AUTHORITY — UNCHANGED / PAUSED

V2 remains authoritative: `estimate_selected_pitch_releases.py`, contract `songsterr-fresh-cpu-spectral-release-evidence-v2`. Duration-free input required. Decoded Basic Pitch note-off is diagnostic only; generic next onset is never duration; same-pitch reattack is censor/search boundary only; unresolved stays unresolved without observed release. Fixed V2: hop 512, sustained-low 5 frames, minimum 0.07 s, max search 4.0 s, onset >=12 dB above floor, drop >=18 dB, floor margin >=6 dB.

V3 remains candidate-only: `estimate_selected_pitch_releases_v3.py`, contract `songsterr-fresh-spectral-activation-release-evidence-v3`. V2 executes unchanged first; fallback only for `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`. Representative results remain 577 resolved → 661 resolved; descriptive only, not acceptance constants.

## DEMUCS REPRODUCIBILITY FINDINGS

- same-run determinism green: run `34435154554`, exact pass A/B WAV/PCM equality, zero sample error; proves only same runner/runtime determinism
- uncontrolled hosted cross-run variation: run `34436134514`; three environment-dependent exact outcomes; no preferred output
- same-host dispatch causality: run `34438368530`; ATen/oneDNN dispatch controls alter exact PCM and are numerical variables, not correctness selectors
- common-AVX2 cross-host canary: run `34439594582`, five AMD+Intel observations, all verified AVX2, comparator `CROSS_VENDOR_PCM_VARIATION_OBSERVED`, three exact hash groups; generic hosted byte identity is not portable
- no branch-tracked fresh pinned compute surface identified; do not invent one or select a host/vendor/hash as canonical

## UPSTREAM EXECUTION POLICY — POLICY B SELECTED

Policy B permits bounded upstream numerical variation only through reference-blind, fail-closed downstream invariants.

Hard rules:
- hashes/vendor/CPU/image/region remain provenance diagnostics, never correctness selectors
- no reference tab, archived/pro scorer, or downstream agreement objective may define a variation bound
- admission must be pairwise/reference-blind or independently justified from representation semantics
- missing/invalid comparison evidence fails closed
- thresholds may only be introduced with independent justification; observed maxima are never automatically tolerances
- `modelValidationComplete` stays false until a justified admission contract is implemented, tested, and independently demonstrated

Existing model-note guards remain: valid finite MIDI/start/confidence; Basic Pitch model invocation; accepted frozen/reference-blind structure; matching structure identity; verified adapter/model provenance; no V143 boundary; decoded model end remains diagnostic; adapted model evidence forces `sourceEnd`, `durationSeconds`, `durationConfidence` null; customer delivery stays blocked.

## PAIRWISE VARIATION MEASUREMENT — GREEN / MEASUREMENT ONLY

`scripts/songsterr-fresh/compare_basic_pitch_cross_run_evidence.py`
- contract `songsterr-fresh-basic-pitch-cross-run-variation-measurement-v1`
- implementation commit `aae62eba938814a9d38dcf08f39cfdfa0456b4d9`
- CI run `34539883074`, job `103079908440`, green
- semantic key `(nearestStructureSlot, selectedMidi)` from frozen structure; deterministic duplicate pairing
- canonical A/B ordering makes reports argument-order invariant
- measures inventory/MIDI histogram/source-start/confidence/diagnostic-end variation
- malformed or incomparable evidence fails closed
- explicitly `thresholdsApplied:false`, `admissionDecisionMade:false`, `modelValidationComplete:false`, `mayAdvanceDelivery:false`, `durationAuthorityChanged:false`

## AUTHORITATIVE REAL-MODEL MEASUREMENT

Three-independent-run canary `.github/workflows/songsterr-fresh-model-evidence-cross-run-measurement-canary.yml`.

Bring-up failures were workflow guards only and are non-authoritative: run `34540126725` used wrong persisted structure field; run `34540364742` exposed the copied asset-revision typo and stopped before Basic Pitch.

Authoritative completed run `34540837228`, head `0f4b4cbe0a52657cf4989e07500041335a89db86`, success:
- jobs A `103082902022`, B `103082902438`, C `103082902292`; aggregate `103084400834`
- aggregate artifact `10177361715`, digest `sha256:74c4c1acb4830ec00b63ad19e1c26925aec0bc0b871ed073913cd10d5aea262c`
- A/B exact: 1,139 events; stem SHA `5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33`; note SHA `1e41a51a3463aa87b3d4c76f8e4cccadcb708dd3d1f51ae6895b950269a61024`; activation bundle `4d2c1c7af035e26ff86919fb169354676bc35b56658d306c7410a94f573f1151`
- C: 1,138 events; stem SHA `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`; note SHA `e85323e5b7449ac84be7ad6076ed3ee9c2da1e9a37b3c64247637e4b82dcbe77`; activation bundle `5e1aa1f76bfb2b3dae77f6aeb6bf6dd1fc5f84e102292dd12a5432683b330159`
- A↔C and B↔C: 1,138 common semantic events, zero source-start delta; one MIDI-64 event at slot `206.22657596371883` present in A/B and absent in C
- common-event confidence delta max `0.0124053955078125`, mean `0.00008660461917283875`, RMS `0.0004107038163407931`
- diagnostic-only model-end delta max `0.6398326530612053` s, mean `0.0005622431046232033` s, RMS `0.01896685259331218` s; never duration evidence
- A/B CPU AMD EPYC 9V74; C AMD EPYC 7763; same image/pins/thread env/source/structure. CPU association is descriptive only and is not a selector.
- three observations do not justify a tolerance.

## FORMAL MEASUREMENT-SET CONTRACT — IMPLEMENTED / FOCUSED CI GREEN

New `scripts/songsterr-fresh/aggregate_basic_pitch_cross_run_measurements.py`:
- contract `songsterr-fresh-basic-pitch-cross-run-variation-measurement-set-v1`
- implementation commit `d3b99a1c1fffd6fde8c13c0a0b9af89673749391`
- test wiring commit `ccb1d04496ed245641da7863b452230c2b3bed1c`
- focused CI run `34544408404`, job `103093808844`, success
- validates exact source/decoded-input/frozen-structure/model/package/thread snapshot and safe runtime guards
- recomputes each pair report from the supplied evidence and rejects altered reports
- requires the complete unordered pair set with no missing/extra pair
- binds runtime canonical-evidence SHA, note identity, activation identity, and structure identity back to validated evidence
- groups exact stem/evidence/note/activation/frame-time outcomes descriptively; no preferred group
- summarizes observed maxima as `descriptiveOnly:true`, `mayDefineTolerance:false`
- hard boundary includes `preferredOutputSelected:false`, `exactHashesAreAdmissionCriteria:false`, `runtimeProvenanceIsAdmissionCriterion:false`, `observedMaximaAreAdmissionCriteria:false`
- self-tests cover complete pair set, argument-order invariance, exact grouping, unsafe runtime guard, digest binding, missing pair, thresholded pair, pair recomputation, package drift, and no preferred output/admission

Canary wiring commit `1a005b3cfba084374667e1132574ca804c98d6fc` replaces the prior inline aggregate summary with the formal aggregate script and adds an independent non-promotional boundary assertion. No numerical model controls changed.

Active validation: run `34544587948` at head `1a005b3cfba084374667e1132574ca804c98d6fc`; three independent model observations are in progress. Treat no result from this run as authoritative until all observation jobs and the formal aggregate job succeed.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**. V2 authoritative; V3 candidate-only. Basic Pitch is not ground truth. No reference scorer/tab/archive logic. No BP end as duration. No generic next-onset duration. No same-pitch-reattack default. No threshold sweep. No promotion from self-consistency, exact hashes, CPU association, or downstream agreement.

## NEXT ENGINEERING STEPS

1. Complete/inspect run `34544587948` on the fixed snapshot.
2. If the formal aggregate fails, classify contract/workflow bugs separately from model variation; do not alter model numerical controls to make it pass.
3. If it succeeds, record artifact digest, exact outcome groups, descriptive envelope, and whether it reproduces or expands the previous one-event variation. Observed maxima remain non-admission evidence.
4. Build a broader independent measurement base only if needed to reason about representation-semantic bounds; do not rerun the completed common-AVX2 portability experiment.
5. Do not create an admission threshold unless independently justified. If no defensible bound exists, keep validation blocked.
6. Duration research remains paused until upstream model-evidence validation is resolved.
7. Keep this checkpoint updated after material findings.

The archived V143/Gomyway pipeline remains out of scope unless the user explicitly asks to resume it.
