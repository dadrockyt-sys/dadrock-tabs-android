# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-10 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the only canonical fresh-chat checkpoint for the Songsterr-inspired fresh pipeline.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`.
- Do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference-based correction, professional/reference scorer logic, training/fine-tuning, or broad optimizer sweeps unless explicitly requested.
- The exact fixture name containing `gomyway` authorizes that audio file only.
- Fresh reference-blind source separation/model work is authorized, including GPU if useful, while preserving fail-closed contracts.
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

Canaries fetch raw fixture from `main` and verify `git hash-object`.

## FROZEN STRUCTURE

Identity:
`fnv1a32:2f493225`

Canonical length:
19653

Accepted facts:
- ~210.67465 s
- 4/4, straight feel
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
4. decoded Basic Pitch note-off stays diagnostic only
5. model pitch evidence crosses boundary duration-free
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
- decoded Basic Pitch note-off never becomes duration
- generic next onset never becomes duration
- same-pitch reattack is a censor/search boundary only
- unresolved stays unresolved when no observed release is found

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

## V3 RELEASE FALLBACK — GREEN, REPEATED, NON-AUTHORITATIVE

Prototype:
`scripts/songsterr-fresh/estimate_selected_pitch_releases_v3.py`

Contract:
`songsterr-fresh-spectral-activation-release-evidence-v3`

Invariants:
- v2 spectral logic runs first unchanged
- v2-resolved events never change
- activation fallback eligible only for exact v2 reason `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
- fixed activation + CQT rule only; no tuning/sweep
- observed valley timestamp only; must precede reattack
- generic next onset, reattack timestamp, decoded Basic Pitch note-off never become duration
- exact MIDI/start identity preserved within each run
- activation release stage invokes no model
- model validation false
- customer eligibility zero

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
- only unmatched historical events were unresolved MIDI-55 detections around 46 s

1,138-note V3 run:
- run `34319558226`
- job `102362962390`
- head `5afab9050a96428fc61a26ffae41c66c09610e7a`
- v2 577 resolved / 561 unresolved
- v3 +84 fallback = 661 resolved / 477 unresolved
- raw failures exactly `UNRESOLVED_DURATION: 477`
- customer events 0 / delivery false
- artifact `10091514442`
- digest `sha256:fb033b19fb94128078a9d97a5832f2616cfef971aa5ba9ba2f0f90e703b6a010`

1,139-note V3 run:
- run `34423610600`
- job `102704074546`
- head `d332cdf2fdf930aacf9023c63989270b16c5e736`
- v2 577 resolved / 562 unresolved
- v3 +84 fallback = 661 resolved / 478 unresolved
- raw failures exactly `UNRESOLVED_DURATION: 478`
- customer events 0 / delivery false
- artifact `10131961888`
- digest `sha256:660ba794985cda8b43db31e27d15f9510fc55cc5588fbd9a851a194f07747085`

The 477/478 difference tracks hosted-runner model-output variation and must not become a hardcoded acceptance count.

## READ-ONLY V3 DURATION INVENTORY — V2 GREEN

Script:
`scripts/songsterr-fresh/summarize_v3_unresolved_duration_evidence.py`

Implementation commit:
`7a7180fe151f6b15ff75ba7841878c9704e52adb`

Contract:
`songsterr-fresh-v3-unresolved-duration-inventory-v2`

Hard metadata includes:
- `descriptiveOnly: true`
- `referenceBlind: true`
- `changesDuration: false`
- `changesPitchIdentity: false`
- `invokesModel: false`
- no decoded-end/next-onset/reattack duration use
- no new release rule
- no threshold selection/sweep

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
- expires 2026-09-24T02:02:39Z

For the 478-unresolved variant:
- 453 same-pitch-reattack-censored
- 372 no sustained subthreshold activation
- 76 activation candidate but insufficient fixed CQT spectral corroboration
- 5 insufficient activation drop
- 18 insufficient onset-to-floor contrast
- 7 no clear sustained spectral release

## V3 INVENTORY CROSS-RUN COMPARATOR — GREEN

Comparator:
`scripts/songsterr-fresh/compare_v3_unresolved_duration_inventories.py`

Implementation commit:
`ed6d1ea2aaa5ce5302d0d9465825ea0544cf0b96`

Contract:
`songsterr-fresh-v3-unresolved-duration-inventory-comparison-v1`

Purpose:
- compare inventory-v2 outputs descriptively
- separate count/reason changes from continuous-statistic drift
- never infer correctness, acceptance, or a new release threshold

Input guard covers exact inventory contract/version, reference-blind/descriptive flags, no mutation/model/decoded-end/next-onset/reattack-duration/rule-selection/sweep, V3 release provenance, and all count/reason/per-MIDI accounting.

Built-in self-test:
- expected synthetic count/reason/MIDI deltas
- 12 tampered guard cases rejected
- repeated output deterministic

Initial lightweight CI:
- run `34428828187`
- job `102719726230`
- head `45260e478ed31b6868cd0a1d8d039975c4dedb01`
- success
- `deterministic: true`
- `tamperCasesRejected: 12`

Historical 1,138-vs-1,139 replay:
- fixed activation rule equal
- eligible +1
- resolved 0
- unresolved +1
- primary delta only `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK` +1
- fallback delta only `NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION` +1
- count/reason change only under MIDI 55
- MIDI 55 eligible +1 / unresolved +1 / resolved unchanged
- all continuous-statistic drift reported separately, not interpreted as accuracy

## FROZEN-STRUCTURE REATTACK CONTEXT — GREEN

Diagnostic:
`scripts/songsterr-fresh/summarize_v3_reattack_structure_context.py`

Implementation commit:
`b588a6f00d7cd2a4814ef2b0efad73265acb1c7b`

Contract:
`songsterr-fresh-v3-reattack-structure-context-v1`

Purpose:
- describe same-pitch reattack spacing relative to the already frozen tempo map
- never use reattack timestamp as duration
- never alter pitch identity or duration
- never invoke a model
- never choose a threshold or acceptance rule

Input guards require:
- exact isolated-polyphonic note-evidence v1 contract
- reference-blind, structure-conditioned, frozen evidence
- exact V3 duration-evidence source
- release stage model-invoked false
- decoded model end / generic next onset / same-pitch reattack all false as duration sources
- exact note-evidence-context v1
- accepted frozen structure identity/map
- valid ordered tempo segments
- each eligible event's `nearestStructureSlot` must actually exist in the supplied frozen structure map

The diagnostic integrates the frozen tempo segments between an event and its next detected same-pitch event to express spacing in local tempo beats. That integrated span is diagnostic context only.

Green lightweight duration-diagnostic CI:
- workflow `.github/workflows/songsterr-fresh-v3-inventory-comparator-tests.yml`
- workflow name `Songsterr Fresh V3 Duration Diagnostic Tests`
- head `327fa31ee29fc816afd408a2d46a22da1247a704`
- run `34429213420`
- job `102720916608`
- conclusion success
- Python 3.10.21
- all three descriptive tools compile
- inventory comparator self-test passes, 12 tamper cases rejected
- structure-context self-test passes
- structure-context `reattackUsedAsDuration: false`
- structure-context `tempoBeatIntegrationVerified: true`
- structure-context tamper cases rejected: 3
- no model/release execution in this workflow

Historical frozen-structure replay, 1,138-note artifact:
- resolved events with a future same-pitch reattack: 632; median gap ~1.278381406 s; median local-tempo span ~2.759494 beats
- unresolved with a future same-pitch reattack: 473; median gap ~0.255419501 s; median ~0.556962 beats
- same-pitch-reattack-censored unresolved: 452 with future reattack; median ~0.255419501 s / ~0.544231 beats
- `NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION`: 371; median ~0.220589569 s / ~0.463415 beats
- `INSUFFICIENT_SPECTRAL_CORROBORATION`: 76; median ~0.709492517 s / ~1.547103 beats
- `INSUFFICIENT_ACTIVATION_DROP`: 5; median ~0.684988662 s / ~1.439024 beats

Historical frozen-structure replay, 1,139-note artifact:
- resolved count remains 661; unresolved 478
- resolved with future same-pitch reattack: 632; median ~1.278381406 s / ~2.759494 beats
- unresolved with future same-pitch reattack: 474; median ~0.255419501 s / ~0.556962 beats
- same-pitch-reattack-censored unresolved: 453; median ~0.245093424 s / ~0.536585 beats
- `NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION`: 372; median ~0.220589569 s / ~0.463415 beats
- `INSUFFICIENT_SPECTRAL_CORROBORATION`: 76; median ~0.709492517 s / ~1.547103 beats
- `INSUFFICIENT_ACTIVATION_DROP`: 5; median ~0.684988662 s / ~1.439024 beats

Interpretation boundary:
- the no-sustained-activation class is strongly concentrated in rapid repeated-note context
- insufficient spectral corroboration occurs at materially wider reattack spacing and is therefore a distinct observed mechanism
- this is not a release cutoff, not a tuning target, not ground truth, and not acceptance evidence

## INDEPENDENT REFERENCE-BLIND PITCH SUPPORT

Probe:
`scripts/songsterr-fresh/probe_independent_pitch_support.py`

Probe remains descriptive-only:
- fixed 80 ms post-onset window
- direct semitone CQT bins
- local ±1/±2 semitone comparisons
- octave ±12 comparisons
- selected-pitch long-run 20th-percentile spectral floor
- no acceptance threshold/sweep
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
- 15/15 payload files byte-identical
- 1,138 exact `(onsetId, sourceStart, selectedMidi)` matches
- common probe SHA `534015d01246965228bfc6988d92117861ff2bcd360b32060ec1f8a95b7e08db`

Third environment sample:
- run `34426840393`
- job `102713775670`
- head `7f8b88c4421ad3465fd1aa532d629fa1e27772ab`
- Basic Pitch 1,139 notes
- one additional MIDI-64 event at `206.24416916099776 s`
- all prior 1,138 MIDI/start identities still present exactly
- common 1,138 events retain identical semitone-rank and octave-rank results
- probe A/B byte-identical within run
- artifact `10133134549`
- 104/104 tests
- blockers unchanged; customer eligible 0 / delivery false

Reproducibility/support evidence is not transcription accuracy or ground truth and cannot clear `MODEL_EVIDENCE_VALIDATION_PENDING`.

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

## RHYTHM FLOATING-POINT BOUNDARY DEFECT — FIXED

Fix commit:
`5afab9050a96428fc61a26ffae41c66c09610e7a`

Only generated event/rest slices <= existing module `EPSILON` are discarded. Frozen structure, pitch identity, and release evidence are not rewritten.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**.

V3 remains candidate-only for research/canary use. V2 remains authoritative. Do not silently replace v2 or expose v3 durations to customers without a separate explicit promotion decision.

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

1. Continue read-only repeated-note analysis using frozen structure. Add previous-same-pitch spacing and nearest-structure-slot alignment diagnostics so the rapid-repeat class can be characterized without defining a release cutoff.
2. Compare those diagnostics for V3-primary resolved, V3-fallback resolved, `NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION`, and `INSUFFICIENT_SPECTRAL_CORROBORATION` groups. Report distributions only.
3. Keep the inventory comparator and structure-context diagnostic as regression boundaries. Future changes must reject altered no-mutation/no-model/no-threshold guards.
4. Keep V2 authoritative and V3 candidate-only. Do not loosen the fixed activation/CQT rule on this fixture.
5. Model-validation scaffold design is complete for now. Do not add an accepting path until a genuinely independent validation authority/evidence source is explicitly designed and justified.
6. Any future V3 promotion must be an explicit documented branch decision with V2 preserved for regression comparison.
7. Before customer exposure, independently validate the model path and obtain complete required duration evidence; evaluator/delivery stay fail-closed until both blockers are legitimately cleared.
