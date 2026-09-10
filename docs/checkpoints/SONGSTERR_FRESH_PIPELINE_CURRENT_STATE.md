# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-09 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the only canonical fresh-chat checkpoint for the Songsterr-inspired fresh pipeline.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`.
- Do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference-based correction, professional/reference scorer logic, training/fine-tuning, or broad optimizer sweeps unless explicitly requested.
- The exact fixture name containing `gomyway` authorizes that audio file only; it does not authorize the archived V143/Gomyway pipeline.
- Fresh reference-blind source separation/model/DSP work is authorized while preserving fail-closed contracts.
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

Canaries fetch the raw fixture from `main` and verify `git hash-object` before use.

## FROZEN STRUCTURE

Identity: `fnv1a32:2f493225`
Canonical length: `19653`

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

Analyzer: `scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`
Contract: `songsterr-fresh-cpu-note-evidence-v4`

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

Script: `scripts/songsterr-fresh/estimate_selected_pitch_releases.py`
Contract: `songsterr-fresh-cpu-spectral-release-evidence-v2`

Hard rules:
- input must be duration-free
- non-null upstream `durationSeconds` / `sourceEnd` rejected
- model/GPU upstream denied unless explicitly authorized with `--allow-model-upstream`
- decoded Basic Pitch note-off never becomes duration
- generic next onset never becomes duration
- same-pitch reattack is a censor/search boundary only
- unresolved stays unresolved when no observed release is found

Fixed V2 parameters:
- HOP_LENGTH 512
- SUSTAINED_LOW_FRAMES 5
- MIN_DURATION_SECONDS 0.07
- MAX_SEARCH_SECONDS 4.0
- MIN_ONSET_ABOVE_FLOOR_DB 12
- DROP_FROM_ONSET_DB 18
- MIN_FLOOR_MARGIN_DB 6

Resolved V2 method: `selected-pitch-sustained-spectral-decay`

Do not mutate this audited V2 implementation while V3 is being evaluated.

## V3 RELEASE FALLBACK — GREEN, REPEATED, NON-AUTHORITATIVE

Prototype: `scripts/songsterr-fresh/estimate_selected_pitch_releases_v3.py`
Contract: `songsterr-fresh-spectral-activation-release-evidence-v3`

Invariants:
- V2 spectral logic runs first unchanged
- V2-resolved events never change
- activation fallback eligible only for exact V2 reason `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
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

Stable fallback evidence:
- hosted-runner inventories have produced 1,138 or 1,139 model notes
- 1,137 exact MIDI/start matches across historical variants
- all 84 fallback events present in both attempts
- all 84 fallback durations exactly equal
- historical output variation is isolated to extra unresolved detections and must never become a hardcoded acceptance count

Representative 1,138-note V3 environment:
- V2 577 resolved / 561 unresolved
- V3 +84 fallback = 661 resolved / 477 unresolved
- customer events 0 / delivery false

Representative 1,139-note V3 environment:
- V2 577 resolved / 562 unresolved
- V3 +84 fallback = 661 resolved / 478 unresolved
- customer events 0 / delivery false

## READ-ONLY V3 DIAGNOSTICS — GREEN

### Duration inventory

Script: `scripts/songsterr-fresh/summarize_v3_unresolved_duration_evidence.py`
Contract: `songsterr-fresh-v3-unresolved-duration-inventory-v2`
Implementation: `7a7180fe151f6b15ff75ba7841878c9704e52adb`

Green canary run `34427390493`, artifact `10133331991`.
For the 478-unresolved historical variant:
- 453 same-pitch-reattack-censored
- 372 no sustained subthreshold activation
- 76 activation candidate but insufficient fixed CQT spectral corroboration
- 5 insufficient activation drop
- 18 insufficient onset-to-floor contrast
- 7 no clear sustained spectral release

### Cross-run inventory comparator

Script: `scripts/songsterr-fresh/compare_v3_unresolved_duration_inventories.py`
Contract: `songsterr-fresh-v3-unresolved-duration-inventory-comparison-v1`
Implementation: `ed6d1ea2aaa5ce5302d0d9465825ea0544cf0b96`

Comparator remains descriptive-only and separates count/reason changes from continuous-statistic drift. Historical 1,138-vs-1,139 replay changes only one unresolved model event; no acceptance inference follows.

### Frozen-structure reattack context

Script: `scripts/songsterr-fresh/summarize_v3_reattack_structure_context.py`
Contract: `songsterr-fresh-v3-reattack-structure-context-v1`
Implementation: `b588a6f00d7cd2a4814ef2b0efad73265acb1c7b`

Observed historical context:
- V3 fallback-resolved next same-pitch spacing median ~1.20 beats
- `NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION` ~0.46 beats
- `INSUFFICIENT_SPECTRAL_CORROBORATION` ~1.55 beats

Interpretation boundary: rapid-repeat and insufficient-CQT mechanisms are observably different; spacing is not a release cutoff or acceptance rule.

### Repeated-note + structure-slot context

Script: `scripts/songsterr-fresh/summarize_v3_repeated_note_structure_context.py`
Contract: `songsterr-fresh-v3-repeated-note-structure-context-v1`
Implementation history: `5387e815d485b09363ea238cca65f914fed7dccf`, `62ed79ded9ff0010d94ed193828edb4dab098e76`, `cf98c06505456376e1032dd6545cd0c6a7f1ab24`

Corrected green CI run `34429657211`, job `102722261026`.
Key observation: next same-pitch spacing separates groups much more than frozen-slot alignment; structure alignment is not acceptance evidence.

## INDEPENDENT REFERENCE-BLIND PITCH SUPPORT

Probe: `scripts/songsterr-fresh/probe_independent_pitch_support.py`

Probe is descriptive-only:
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
- run `34424545232`, artifact `10132278606`
- run `34425140684`, artifact `10132507650`
- 15/15 payload files byte-identical
- common probe SHA `534015d01246965228bfc6988d92117861ff2bcd360b32060ec1f8a95b7e08db`

Third environment sample:
- run `34426840393`
- job `102713775670`
- Basic Pitch 1,139 notes
- all prior 1,138 MIDI/start identities remain present exactly
- common 1,138 events retain identical semitone-rank and octave-rank results
- probe A/B byte-identical within run
- artifact `10133134549`

Reproducibility/support evidence is not transcription accuracy or ground truth and cannot clear `MODEL_EVIDENCE_VALIDATION_PENDING`.

## MODEL-VALIDATION CONTRACT SCAFFOLD — FAIL-CLOSED

Module: `songsterr_pipeline/modelValidationContractScaffold.mjs`
Contract: `songsterr-fresh-model-validation-contract-scaffold` v1
Implementation: `7f8b88c4421ad3465fd1aa532d629fa1e27772ab`

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

Existing evaluator remains fail-closed and rejects model-invoked evidence unless top-level `provenance.modelValidationComplete === true`.

## RHYTHM FLOATING-POINT BOUNDARY DEFECT — FIXED

Fix commit: `5afab9050a96428fc61a26ffae41c66c09610e7a`
Only generated event/rest slices <= existing module `EPSILON` are discarded. Frozen structure, pitch identity, and release evidence are not rewritten.

## SPECTRAL REJECTION CONTEXT STUDY — GREEN

Diagnostic: `scripts/songsterr-fresh/probe_v3_activation_spectral_rejection_context.py`
Contract: `songsterr-fresh-v3-activation-spectral-rejection-context-v1`
Probe commit: `b0e255dc8f1b8dfd79189647ef9d8effefa95856`
Guard wiring: `603f8d5094ac821c8bea837fb3a254d1622a8608`
Canary workflow commit: `4207fa86c68afa3230567d37e185e8a42b76dd68`

Green full canary:
- run `34430069785`
- job `102723521376`
- head `4207fa86c68afa3230567d37e185e8a42b76dd68`
- artifact `10134306664`
- digest `sha256:9e97f53e1ab3b0fdbdc0670a7fd3cc180f617d19244e7a732694b69f4787e7cb`
- expires 2026-09-24T02:43:22Z

Observed fixed-rule population:
- 160 events passed the existing activation qualifications
- 84 were fixed-rule CQT corroborated
- 76 were `INSUFFICIENT_SPECTRAL_CORROBORATION`
- activation-drop median: corroborated ~0.4044; insufficient ~0.3499
- valley-activation median: corroborated ~0.1776; insufficient ~0.1751
- selected-pitch spectral-drop median: corroborated ~11.5105 dB; insufficient ~-0.1098 dB
- selected-pitch onset level median: corroborated ~-23.0745 dB; insufficient ~-30.6866 dB
- selected-pitch valley level median: corroborated ~-36.2008 dB; insufficient ~-29.2576 dB
- same-pitch-reattack-gap median: corroborated ~0.5521 s; insufficient ~0.7095 s
- valley-to-reattack margin median: corroborated ~0.2380 s; insufficient ~0.3715 s
- among the 76 insufficient events, 39 have negative selected-pitch spectral drop, 17 are 0–3 dB, and 20 are 3–6 dB
- activation-drop versus spectral-drop correlation inside the insufficient group is weak (~0.13)

Descriptive interpretation only:
- activation valleys are similarly low in both groups
- the insufficient class is not explained by obviously less time before reattack
- after the activation valley exists, the principal observed separation is selected-pitch audio-domain CQT behavior
- many insufficient events retain or gain selected-pitch CQT energy at the activation valley
- this does not show that the fixed 6 dB rule is wrong and is not threshold-tuning evidence

## SPECTRAL VALLEY NEIGHBORHOOD CONTEXT — GREEN

Diagnostic: `scripts/songsterr-fresh/probe_v3_spectral_valley_neighborhood_context.py`
Contract: `songsterr-fresh-v3-spectral-valley-neighborhood-context-v1`
Implementation: `1d7ca8b0bf0fb1394f7095b661c13ae901513159`
Guard wiring: `8e8441f5a36073089374f268cf766b797c04e553`
Canary wiring: `eb023119a568a6113f91eb225ffa0640ee69e0fc`

Green full frozen-fixture canary:
- run `34431148700`
- job `102726742070`
- head `eb023119a568a6113f91eb225ffa0640ee69e0fc`
- conclusion success
- 1,138 duration-free model notes
- unchanged V2: 577 resolved / 561 unresolved
- unchanged candidate V3: 661 resolved / 477 unresolved
- exact source-row/category parity passed for all 160 activation-qualified events
- artifact `10134681813`
- digest `sha256:a804f394cec3c4e1294e05ddbf340e4412dc95ef11bcfb60a0959d99cd41647d`
- expires 2026-09-24T03:00:03Z

Observed valley-neighborhood distributions:
- corroborated selected-pitch valley level median ~-35.2853 dB
- insufficient selected-pitch valley level median ~-28.5956 dB
- selected MIDI is strongest among selected + ±1/±2 semitone bins in 32/84 corroborated (~38.1%) versus 45/76 insufficient (~59.2%)
- median selected-minus-best-semitone-neighbor margin: corroborated ~-2.6623 dB; insufficient ~+1.4130 dB
- selected MIDI is strongest among selected + available octave bins in 46/84 corroborated (~54.8%) versus 46/76 insufficient (~60.5%)
- median selected-minus-best-compared-alternative margin: corroborated ~-5.7209 dB; insufficient ~-1.2773 dB
- selected MIDI is stronger than every compared semitone/octave alternative in 16/84 corroborated (~19.0%) versus 29/76 insufficient (~38.2%)
- within the 39 insufficient events with negative onset-to-valley spectral drop, 28/39 (~71.8%) still rank first among the local ±2-semitone neighborhood at the valley

Descriptive interpretation only:
- insufficient-CQT events are not primarily explained by selected-pitch energy migrating into immediately adjacent semitone bins
- many insufficient events retain a locally dominant selected-pitch spectral component after Basic Pitch activation has already fallen into the fixed valley
- corroborated events more often have the selected-pitch bin fall below other simultaneous local/octave spectral content by the valley
- this supports an activation-versus-audio temporal disagreement hypothesis, not a new release rule

## POST-VALLEY SPECTRAL TRAJECTORY CONTEXT — GREEN

Diagnostic: `scripts/songsterr-fresh/probe_v3_post_valley_spectral_trajectory_context.py`
Contract: `songsterr-fresh-v3-post-valley-spectral-trajectory-context-v1`
Initial implementation: `2f10e78fe8d06871bd920b6f86dc175c3a19a8b3`
Guard wiring: `d5928354c0fcc64be934862fe85d5d8afa0c6293`
Dedicated canary workflow: `3aca037ae70aba4748eb37705a0652f13399fcf8`
CQT-reference correction: `60bad8458ca846e03f433472c9b53111d1f8d6c7`

Purpose:
- observe selected-pitch CQT at fixed +50 ms, +100 ms, and +200 ms horizons after the already-observed activation valley
- horizons are observation points only, not release delays/cutoffs
- an observation is omitted if its 3-frame CQT window would reach the same-pitch reattack
- no alternate release timestamp is searched for or output

Hard guards:
- descriptive-only / reference-blind
- exact source-row category/MIDI identity preserved
- no duration/sourceEnd writes
- no pitch mutation
- no model invocation inside probe
- no decoded model end
- no next-onset or reattack duration
- fixed observation is not duration
- no alternate release search/output
- no delay threshold
- no release-rule proposal
- no threshold selection/sweep
- no acceptance authority

Important implementation correction:
- the first draft used a narrower CQT range based on selected MIDI values
- because `librosa.amplitude_to_db(..., ref=np.max)` depends on the transform-wide maximum, that range would make its dB scale not strictly comparable to the green source probe
- this was caught before any result was accepted
- corrected implementation uses the exact source spectral-context CQT range: MIDI 40–88, 49 bins, same harmonic preprocessing, same 512 hop, same 12 bins/octave, same global dB reference construction
- method now reports `sourceDbReferenceAligned: true`
- pre-fix full canary run `34432148553` is superseded and must not be used as evidence even if its workflow conclusion is green

Corrected lightweight guard CI:
- run `34432234645`
- job `102729956896`
- head `60bad8458ca846e03f433472c9b53111d1f8d6c7`
- conclusion success
- all earlier diagnostics remain green
- trajectory probe compiles and deterministic self-test passes

Corrected green full canary:
- run `34432234675`
- job `102729956943`
- head `60bad8458ca846e03f433472c9b53111d1f8d6c7`
- conclusion success
- exact authorized fixture hash verified
- frozen structure rebuilt and accepted
- deterministic Demucs separation/model asset verified
- duration-free Basic Pitch + activation sidecar bound
- unchanged V2 and candidate V3 release stages passed
- green spectral-rejection context rebuilt
- fixed post-valley trajectory probe passed
- exact `(onsetId, category, midi)` parity passed for all 160 rows
- fail-closed boundary assertions passed
- deterministic self-test passed
- artifact `10135045827`
- digest `sha256:dc1cebfff20dd1d8856ec2df27129ee694edda40fe12ee5178309f0a87c1c83b`
- expires 2026-09-24T03:16:25Z
- model note count 1,138
- unchanged V2: 577 resolved / 561 unresolved
- unchanged candidate V3: 661 resolved / 477 unresolved

Observed fixed-horizon coverage and within-row valley-to-observation change:

Corroborated, 84 total:
- +50 ms available 79/84; median `valleyMinusObservedDb` ~-0.6185 dB; 37/79 fell further, 42/79 rose relative to valley
- +100 ms available 68/84; median ~-1.5236 dB; 28/68 fell further, 40/68 rose
- +200 ms available 42/84; median ~-6.0886 dB; 13/42 fell further, 29/42 rose

Insufficient spectral corroboration, 76 total:
- +50 ms available 74/76; median `valleyMinusObservedDb` ~+3.6448 dB; 53/74 fell further, 21/74 rose relative to valley
- +100 ms available 69/76; median ~+3.6122 dB; 53/69 fell further, 16/69 rose
- +200 ms available 58/76; median ~+6.7710 dB; 45/58 fell further, 13/58 rose

Paired same-event subset with a full +200 ms pre-reattack observation window:
- corroborated 42 events: median valley-to-observation change ~-0.7969 dB at +50 ms, ~-1.8218 dB at +100 ms, ~-6.0886 dB at +200 ms
- insufficient 58 events: median ~+3.8207 dB at +50 ms, ~+5.1212 dB at +100 ms, ~+6.7710 dB at +200 ms

Additional insufficient-class context:
- all 39 events whose selected-pitch CQT level was higher at the activation valley than at onset still have a valid +50 ms window
- their median change from valley to +50 ms is ~+2.4045 dB; 26/39 fall further by +50 ms
- 36/39 have +100 ms coverage; median valley-to-+100 ms change ~+3.7347 dB
- 29/39 have +200 ms coverage; median valley-to-+200 ms change ~+9.8028 dB

Descriptive interpretation only:
- the insufficient-CQT class commonly continues losing selected-pitch acoustic energy after Basic Pitch activation has already entered the fixed low valley
- the corroborated class has already reached a substantially lower selected-pitch CQT state at the valley and often rebounds afterward
- the paired +200 ms subset preserves the same direction of separation, reducing concern that the headline pattern is only caused by different horizon availability
- this strengthens the activation-versus-audio temporal disagreement hypothesis on this fixture
- it does not establish a correct release timestamp, a fixed delay, a new cutoff, a changed 6 dB threshold, transcription correctness, or promotion evidence
- fixed +50/+100/+200 ms horizons must not be repurposed as release candidates

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**.
V2 remains authoritative.
V3 remains candidate-only for research/canary use.
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

1. Treat the post-valley CQT study as complete and descriptive. Do not convert +50/+100/+200 ms into a release delay or cutoff.
2. The next useful duration-side question is whether the delayed-decay pattern is specific to selected-bin CQT representation or is also visible in an independent audio-domain representation at the same already-fixed observation horizons. If studied, use a fixed representation and the same exact 160 identities; do not search for a release timestamp.
3. A suitable next read-only cross-check is fixed-band STFT/harmonic energy around the selected pitch at the already-observed valley and the same +50/+100/+200 ms horizons. It must be descriptive-only, reference-blind, and unable to write duration or choose thresholds.
4. Do not tune the 6 dB, activation, or time-delay thresholds on this fixture. No optimizer sweep.
5. Keep rapid-repeat (`NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION`) separate from insufficient-CQT mechanisms.
6. Keep all diagnostic CI guards. Future changes must reject altered no-mutation/no-model/no-threshold/no-release-search properties.
7. Keep V2 authoritative and V3 candidate-only. Any future V3 promotion must be an explicit documented branch decision with V2 preserved for regression comparison.
8. Model-validation scaffold remains fail-closed. Do not add an accepting path until a genuinely independent validation authority/evidence source is explicitly designed and justified.
9. Before customer exposure, independently validate the model path and obtain complete required duration evidence; evaluator/delivery stay fail-closed until both blockers are legitimately cleared.

The archived V143/Gomyway pipeline remains out of scope.
