# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-10 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the only canonical fresh-chat checkpoint for the Songsterr-inspired fresh pipeline.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`.
- Do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference-based correction, professional/reference scorer logic, training/fine-tuning, or broad optimizer sweeps unless the user explicitly asks.
- The exact fixture name containing `gomyway` authorizes that audio file only.
- The fresh reference-blind source-separation/model path is authorized, including GPU if useful, while preserving fail-closed contracts.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free.
- Model/DSP execution stays under `scripts/songsterr-fresh/`.
- Frozen structure precedes note inference and cannot be rewritten downstream.
- Never silently change/drop detected MIDI/event identity.
- Preserve `/ai-tab`: audio upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.

## EXACT AUTHORIZED FIXTURE

On `main`:
`public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`

Git blob SHA:
`4dd709e3fa177b4daeed71ca97f0199757729d4b`

Duration:
~210.674648526 s

Canaries fetch the raw file from `main` and verify `git hash-object`.

## FROZEN STRUCTURE

Structure identity:
`fnv1a32:2f493225`

Canonical length:
19653

Accepted facts:
- duration ~210.67465 s
- 4/4
- straight feel
- pickup / first downbeat ~0.65016 s
- 115 measures
- 113 measure-local tempo segments
- beat-grid MAE ~7.14 ms
- RMSE ~10.63 ms
- max ~58.05 ms
- accepted true

Historical structure canary:
- run `34192662439`
- job `101953726302`
- commit `2a598f0f38d755faf0cd3d46543221253f1c8997`
- artifact `10042777518`
- digest `sha256:5ff3ce36f559bcc02efcc985a1fa06966576da0445896326e9408ada955e9b6f`

## GUARDED CPU BASELINE

Analyzer:
`scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`

Contract:
`songsterr-fresh-cpu-note-evidence-v4`

Baseline:
- 492 onsets
- 1,130 candidates
- 139 local unambiguous pitch selections
- 353 ambiguous
- 0 no-candidate
- MIDI 40 in 97/139 selections
- role relevance unresolved
- polyphony unresolved
- instrument isolation none
- customer eligible 0

Latest CPU regression:
- run `34309259214`
- job `102332311684`
- head `54d9e4792d8255d56f6aec82977ac083b9c2bae4`
- artifact `10087798684`
- digest `sha256:a1dbe85348f66847045e616d9726ffce986a82e995de0817fb20159e6fbf9d08`
- 97/97 tests
- CPU duration evidence 103 resolved / 36 unresolved

## MODEL PATH

Architecture:
1. verify frozen full-mixture structure
2. Demucs 4.1.0 `htdemucs_6s` guitar isolation
3. Basic Pitch 0.4.0 polyphonic pitch/onset inference on isolated guitar
4. decoded Basic Pitch note-off remains diagnostic only
5. model pitch evidence crosses the boundary duration-free
6. dedicated release stage is sole active duration authority
7. model adaptation requires explicit authorization
8. `MODEL_EVIDENCE_VALIDATION_PENDING` independently blocks customer delivery

Pinned environment:
- numpy 1.26.4
- torch 2.14.0
- huggingface-hub 1.30.0
- safetensors 0.8.0
- sphn 0.2.1
- demucs 4.1.0
- basic-pitch 0.4.0
- librosa 0.11.0
- soundfile 0.13.1
- tflite-runtime 2.14.0
- OMP/MKL/OpenBLAS/NumExpr threads = 1
- PYTHONHASHSEED = 0

Historical first model canary used Demucs `--shifts 1`; its exact 1,128-note output is historical only, not a reproducibility baseline.

## ACTIVE V2 DURATION AUTHORITY — UNCHANGED

Script:
`scripts/songsterr-fresh/estimate_selected_pitch_releases.py`

Contract:
`songsterr-fresh-cpu-spectral-release-evidence-v2`

Hard rules:
- input must be duration-free
- non-null upstream `durationSeconds` / `sourceEnd` rejected
- model/GPU upstream denied unless explicitly authorized with `--allow-model-upstream`
- decoded Basic Pitch note-off never becomes active duration
- generic next onset never becomes duration
- same-pitch reattack is a censor/search boundary only
- unresolved remains unresolved when no observed release is found

Fixed v2 parameters:
- HOP_LENGTH 512
- SUSTAINED_LOW_FRAMES 5
- MIN_DURATION_SECONDS 0.07
- MAX_SEARCH_SECONDS 4.0
- MIN_ONSET_ABOVE_FLOOR_DB 12
- DROP_FROM_ONSET_DB 18
- MIN_FLOOR_MARGIN_DB 6

Resolved v2 method:
`selected-pitch-sustained-spectral-decay`

Do not mutate this audited v2 implementation while v3 is being evaluated.

## V3 RELEASE FALLBACK — GREEN, REPEATED, STILL NON-AUTHORITATIVE

Prototype:
`scripts/songsterr-fresh/estimate_selected_pitch_releases_v3.py`

Contract:
`songsterr-fresh-spectral-activation-release-evidence-v3`

V3 invariants:
- v2 spectral logic runs first unchanged
- v2-resolved events are never changed
- activation fallback eligible only for exact v2 reason `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
- fixed activation + CQT rule only; no tuning/sweep
- observed valley timestamp only; must precede same-pitch reattack
- generic next onset, reattack timestamp, and decoded Basic Pitch note-off never become duration
- exact MIDI/start identity preserved within each run
- activation release stage invokes no model
- model validation remains false
- customer eligibility remains zero

Fixed activation + spectral rule:
- Basic Pitch per-pitch activation <= 0.20
- sustained 3 Basic Pitch frames
- activation drop >= 0.15 from onset-window peak
- minimum observed span >= 0.07 s
- maximum search 4.0 s
- stop before next same-pitch reattack
- independent selected-pitch CQT spectral drop >= 6 dB over 3 frames

Historical stable fallback comparison:
- hosted-runner inventories 1,139 versus 1,138 notes
- 1,137 exact MIDI/start matches
- all 84 fallback events present in both attempts
- all 84 fallback durations exactly equal
- only unmatched events were unresolved MIDI-55 detections around 46 s

Post-fix 1,138-note V3 run:
- run `34319558226`
- job `102362962390`
- head `5afab9050a96428fc61a26ffae41c66c09610e7a`
- v2 577 resolved / 561 unresolved
- v3 +84 fallback = 661 resolved / 477 unresolved
- raw failures exactly `UNRESOLVED_DURATION: 477`
- rhythm spelling failures 0
- customer events 0 / delivery false
- artifact `10091514442`
- digest `sha256:fb033b19fb94128078a9d97a5832f2616cfef971aa5ba9ba2f0f90e703b6a010`

Hardened 1,139-note V3 run:
- run `34423610600`
- job `102704074546`
- head `d332cdf2fdf930aacf9023c63989270b16c5e736`
- v2 577 resolved / 562 unresolved
- v3 +84 fallback = 661 resolved / 478 unresolved
- raw failures exactly `UNRESOLVED_DURATION: 478`
- customer events 0 / delivery false
- artifact `10131961888`
- digest `sha256:660ba794985cda8b43db31e27d15f9510fc55cc5588fbd9a851a194f07747085`

The 477 versus 478 difference tracks hosted-runner model-output variation and must not become a hardcoded acceptance count.

## READ-ONLY V3 DURATION INVENTORY — V2 GREEN

Script:
`scripts/songsterr-fresh/summarize_v3_unresolved_duration_evidence.py`

Implementation commit:
`7a7180fe151f6b15ff75ba7841878c9704e52adb`

Contract:
`songsterr-fresh-v3-unresolved-duration-inventory-v2`

Hard metadata:
- `descriptiveOnly: true`
- `referenceBlind: true`
- `changesDuration: false`
- `changesPitchIdentity: false`
- `invokesModel: false`
- `readsDecodedModelNoteEnd: false`
- `usesDecodedModelNoteEndAsDuration: false`
- `usesNextOnsetAsDuration: false`
- `usesSamePitchReattackAsDuration: false`
- `proposesNewReleaseRule: false`
- `thresholdSelection: false`
- `thresholdSweep: false`

V2 adds descriptive-only context for:
- resolved/unresolved onset confidence
- next same-pitch reattack-gap distributions
- per-MIDI resolved/unresolved counts
- per-MIDI unresolved primary/fallback reason counts

Cross-run historical inventory observations:
- 1,138-note run unresolved = 477
- 1,139-note run unresolved = 478
- only per-MIDI resolution-count change is MIDI 55, matching known hosted-runner variation
- all other per-MIDI resolved/unresolved counts are unchanged

For the 478-unresolved variant:
- 453 same-pitch-reattack-censored
- 372 no sustained subthreshold activation
- 76 activation candidate but insufficient fixed CQT spectral corroboration
- 5 insufficient activation drop
- 18 insufficient onset-to-floor contrast
- 7 no clear sustained spectral release

Descriptive context only:
- 372-event group median next same-pitch reattack gap ~0.221 s
- 76-event insufficient-CQT group median ~0.709 s
- observations only; not release cutoffs or tuning targets

Green inventory-v2 canary:
- run `34427390493`
- job `102715416850`
- head `7a7180fe151f6b15ff75ba7841878c9704e52adb`
- reproduced 1,138-note environment
- V3 661 resolved / 477 unresolved
- resolved median next-same-pitch gap ~1.278 s
- unresolved median next-same-pitch gap ~0.255 s
- customer exposure 0 / delivery false
- 104/104 deterministic tests
- artifact `10133331991`
- digest `sha256:9b3cbc27f25d3c960e96a44caa492057c7f8288ba380eb960e835ed7b4573200`
- size 6,883,095 bytes
- expires 2026-09-24T02:02:39Z

## V3 INVENTORY CROSS-RUN COMPARATOR — GREEN

Comparator:
`scripts/songsterr-fresh/compare_v3_unresolved_duration_inventories.py`

Implementation commit:
`ed6d1ea2aaa5ce5302d0d9465825ea0544cf0b96`

Contract:
`songsterr-fresh-v3-unresolved-duration-inventory-comparison-v1`

Purpose:
- compare inventory-v2 outputs descriptively
- keep count/reason changes separate from continuous-statistic drift
- never infer correctness, acceptance, or a new release threshold

Input guards:
- requires exact inventory-v2 contract and version
- requires `descriptiveOnly: true` and `referenceBlind: true`
- rejects any input with duration/pitch mutation, model invocation, decoded-end use, next-onset/reattack duration use, release-rule proposal, threshold selection, or threshold sweep enabled
- rejects any changed hard no-mutation/no-model/no-threshold guard
- requires V3 release contract provenance
- verifies eligible = resolved + unresolved
- verifies unresolved primary-reason accounting
- verifies reattack-fallback accounting
- verifies per-MIDI eligible/resolved/unresolved accounting

Output is also explicitly fail-closed:
- `ownsAcceptanceDecision: false`
- `changesDuration: false`
- `changesPitchIdentity: false`
- `invokesModel: false`
- `proposesNewReleaseRule: false`
- `thresholdSelection: false`
- `thresholdSweep: false`

Built-in deterministic self-test:
- verifies expected count/reason/MIDI deltas on a synthetic pair
- rejects 12 tampered guard cases
- verifies repeated comparison output is deterministic

Dedicated lightweight CI:
- workflow `.github/workflows/songsterr-fresh-v3-inventory-comparator-tests.yml`
- workflow commit `45260e478ed31b6868cd0a1d8d039975c4dedb01`
- run `34428828187`
- job `102719726230`
- head `45260e478ed31b6868cd0a1d8d039975c4dedb01`
- Ubuntu 24.04.5 / image `20260907.300.1` / Azure `eastus2`
- Python 3.10.21
- both descriptive inventory scripts compile
- self-test output: `deterministic: true`, `selfTest: passed`, `tamperCasesRejected: 12`
- conclusion success
- no model/release execution in this workflow

Historical 1,138-vs-1,139 inventory-v2 replay through the comparator:
- fixed activation rule equal
- duration-eligible delta +1
- resolved delta 0
- unresolved delta +1
- primary-reason delta only: `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK` +1
- fallback-rejection delta only: `NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION` +1
- count/reason changes occur only under MIDI 55
- MIDI 55 eligible +1 / unresolved +1 / resolved unchanged
- MIDI 55 unresolved fraction 0.29411764705882354 → 0.3142857142857143
- common structural resolution counts otherwise stable
- continuous onset-confidence/gap statistics show small environment-dependent drift and are reported separately rather than interpreted as accuracy or acceptance evidence

Overall continuous deltas include:
- resolved onset-confidence median +0.00003635883331298828
- unresolved onset-confidence median +0.0005692392587661743
- resolved next-same-pitch-gap mean -0.00012859152099764515 s
- unresolved next-same-pitch-gap mean -0.0012349702217232528 s
- unresolved next-same-pitch-gap median unchanged at ~0.2554195011 s

This historical replay is descriptive evidence only. It does not promote V3, change a duration, or define a threshold.

## INDEPENDENT REFERENCE-BLIND PITCH SUPPORT

Probe:
`scripts/songsterr-fresh/probe_independent_pitch_support.py`

Probe remains descriptive-only:
- fixed 80 ms post-onset window
- direct semitone CQT bins
- local ±1/±2 semitone comparisons
- octave ±12 comparisons
- selected-pitch long-run 20th-percentile spectral floor
- no acceptance threshold or sweep
- no pitch rewrite/drop
- no duration/sourceEnd writes
- no reference tab/scorer/archived logic
- no Basic Pitch activation use
- no decoded Basic Pitch note-end use
- no model invocation inside probe
- no `modelValidationComplete` mutation

First two canaries reproduced exactly at payload level:
- run `34424545232`, artifact `10132278606`, digest `sha256:953af38fb6216706dab989d98b83c4fb2edba9826b7a810dda20ee15052766a6`
- run `34425140684`, artifact `10132507650`, digest `sha256:d0c01375094055377c04739ec41eef41cb450cafccac654137359f72ac543585`
- extracted 15/15 payload files byte-identical
- 1,138 exact `(onsetId, sourceStart, selectedMidi)` matches
- unmatched 0 / 0
- maximum start delta 0.0 s
- Demucs stem SHA `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- note identity SHA `e85323e5b7449ac84be7ad6076ed3ee9c2da1e9a37b3c64247637e4b82dcbe77`
- probe SHA `534015d01246965228bfc6988d92117861ff2bcd360b32060ec1f8a95b7e08db`
- local semitone histogram 914 / 112 / 96 / 13 / 3
- octave histogram 793 / 323 / 22

Third independent environment sample:
- run `34426840393`
- job `102713775670`
- head `7f8b88c4421ad3465fd1aa532d629fa1e27772ab`
- runner ubuntu-24.04 image `20260907.300.1`, Azure `eastus2`
- Demucs guitar stem SHA `5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33`
- Basic Pitch 1,139 notes
- note identity SHA `1e41a51a3463aa87b3d4c76f8e4cccadcb708dd3d1f51ae6895b950269a61024`
- one additional MIDI-64 event at `206.24416916099776 s`
- all prior 1,138 MIDI/start identities remain present exactly
- common 1,138 events retain identical semitone-rank and octave-rank results
- probe A/B byte-identical within run, SHA `b4841d0121dd80b3561acbc5c6bbdaadc1b81a56b1fcf6eb8c8b116e3a2eb63c`
- local semitone histogram 915 / 112 / 96 / 13 / 3
- octave histogram 794 / 323 / 22
- only small continuous spectral/confidence drift on common events
- artifact `10133134549`
- digest `sha256:2e7244fc0d2cfb6d72c005c29b448492f06338588d35c509485923ee9b738b72`
- 104/104 tests
- evaluator blockers unchanged; customer eligible 0 / delivery false

Interpretation boundary:
- reproducibility/support evidence is not transcription accuracy or ground truth
- hosted-runner stem/model variation stays distinct from probe determinism
- do not derive accuracy score or fixture-tuned acceptance threshold
- do not use self-consistency to clear `MODEL_EVIDENCE_VALIDATION_PENDING`

## MODEL-VALIDATION CONTRACT SCAFFOLD — FAIL-CLOSED

Implementation commit:
`7f8b88c4421ad3465fd1aa532d629fa1e27772ab`

Module:
`songsterr_pipeline/modelValidationContractScaffold.mjs`

Contract:
`songsterr-fresh-model-validation-contract-scaffold` v1

Hard properties:
- `ownsAcceptanceDecision: false`
- `externalValidationAuthorityDefined: false`
- `diagnosticEvidenceCanClearValidation: false`
- `mutatesModelValidationComplete: false`
- `validation.validated: false`
- `validation.acceptanceAuthority: null`
- blocker fixed to `MODEL_EVIDENCE_VALIDATION_PENDING`
- no threshold definition/sweep
- no pitch rewrite
- no model/process/network access
- no reference tab
- no archived V143 import

Existing evaluator remains unchanged and rejects model-invoked evidence unless top-level `provenance.modelValidationComplete === true`.

Six regression tests prove reproducibility/support-only evidence cannot clear validation. Deterministic suite is 104/104 green.

Scaffold-head regressions all green:
- core tests run `34426840359`, job `102713775748`, 104/104
- deterministic activation-valley run `34426840327`, artifact `10133119495`, digest `sha256:fbef60dc3d624595b164c46afb7d9f2bb24222dd23a97d33f60ea5e0d4d2cac6`
- V3 canary run `34426840323`, artifact `10133130774`, digest `sha256:a082ac08eea339cc329e5189a9938af4a95a2f9f6a6ad29439a9d7f145c4a16e`
- independent pitch-support run `34426840393`, artifact `10133134549`, digest above

## RHYTHM FLOATING-POINT BOUNDARY DEFECT — FIXED

Fix commit:
`5afab9050a96428fc61a26ffae41c66c09610e7a`

Only generated event/rest slices <= existing module `EPSILON` are discarded. Frozen structure, pitch identity, and release evidence are not rewritten. Regression remains green in 104-test suite.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**.

V3 remains a validated candidate release authority for research/canary use only. V2 remains authoritative. Do not silently replace v2 and do not expose v3 durations to customers without a separate explicit promotion decision.

Basic Pitch output is not ground truth.
No reference scorer.
No archived logic.
No reference tab.
No decoded Basic Pitch end as duration.
No generic next-onset duration.
No same-pitch reattack default duration.
No threshold sweep.
No acceptance promotion from self-consistency alone.

## NEXT ENGINEERING STEPS — FRESH CHAT HANDOFF

1. Continue descriptive study of the same-pitch-reattack-censored unresolved class without modifying V2/V3. Focus on context that may explain why fixed evidence is absent, not on selecting a cutoff.
2. Quantify tempo/structure-relative reattack spacing and repeated-note context for resolved versus unresolved events using frozen structure only. Keep this as read-only diagnostic evidence.
3. Keep the comparator as a regression boundary for future inventory changes. Any comparison with changed activation rule must be called out explicitly and never treated as an accuracy comparison.
4. Keep V2 authoritative and V3 candidate-only. Treat rapid repeated-note and insufficient-CQT-corroboration classes as distinct observed mechanisms; do not loosen the fixed activation/CQT rule on this fixture.
5. Model-validation scaffold design is complete for now. Do not add an accepting path until a genuinely independent validation authority/evidence source is explicitly designed and justified.
6. Any future v3 promotion must be an explicit documented branch decision with v2 preserved for regression comparison.
7. Before customer exposure, independently validate model path and obtain complete required duration evidence; evaluator/delivery remain fail-closed until both blockers are legitimately cleared.
