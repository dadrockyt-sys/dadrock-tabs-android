# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-09 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the only canonical fresh-chat checkpoint for the Songsterr-inspired fresh pipeline.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`.
- Do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference-based correction, professional/reference scorer logic, training/fine-tuning, or broad optimizer sweeps unless the user explicitly asks.
- The exact fixture name containing `gomyway` authorizes that audio file only.
- The user authorized the fresh reference-blind source-separation/model path, including GPU if useful, while preserving fail-closed contracts.
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
3. Basic Pitch 0.4.0 polyphonic pitch/onset inference on the isolated guitar stem
4. decoded Basic Pitch note-off remains diagnostic only
5. model pitch evidence crosses the boundary duration-free
6. the dedicated release stage is sole active duration authority
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

## DEMUCS EXECUTED ASSET — VERIFIED

Verifier:
`scripts/songsterr-fresh/verify_demucs_model_asset.py`

Contract:
`songsterr-fresh-demucs-model-asset-v2`

For `htdemucs_6s`:
- primary loader: Hugging Face
- repo: `adefossez/HTDemucs-6s`
- pinned repo snapshot: `3c5ee475be622df764938de97e4281a7b07ffa58`
- model-file upload revision: `053e1404489b3dc58bf718224fac4b7316de8c93`
- bag model signature: `5c90dfd2`
- executed asset: `5c90dfd2.safetensors`
- asset SHA256: `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- Xet hash: `4a08ca8231da4bd9433191a95ee700cc8ba8693e980ac5b444f63eff38c807e1`
- model class: `demucs.htdemucs.HTDemucs`
- legacy `.th` fallback is informational, not primary

## DEMUCS REPRODUCIBILITY — GREEN

Old `--shifts 1` cross-run drift was traced to Demucs' deliberate random shift augmentation.

Current reproducibility boundary:
- use `--shifts 0`
- verify exact fixture, runtime packages, and executed model asset
- same-job/same-runtime A/B must have identical SHA and exact byte `cmp`
- cross-environment stem SHA is diagnostic only
- cross-environment semantic note/release stability is evaluated separately

Green reproducibility run:
- run `34313902753`
- job `102345983922`
- head `88dcaf3100311b130ec4c30d2b1cbeb7dae0e24d`
- pass A/B stem SHA `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- identicalStemSha256 true
- identicalStemBytes true
- decoded separation WAV SHA `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- artifact `10089522605`
- digest `sha256:a49e36478b541907b377fb94e9a264003eb69ff1bf20dd2d2904e0fc2f37fb43`

Do not canonize a hosted-runner stem SHA or exact Basic Pitch note count across environments.

## FIXED ACTIVATION + SPECTRAL RULE

Shared helper:
`scripts/songsterr-fresh/activation_valley_release_evidence.py`

Contract:
`songsterr-fresh-activation-spectral-valley-rule-v1`

Fixed rule, no optimizer/sweep:
- Basic Pitch per-pitch activation <= 0.20
- sustained 3 Basic Pitch frames
- activation drop >= 0.15 from onset-window peak
- minimum observed span >= 0.07 s
- maximum search 4.0 s
- search stops before next same-pitch reattack
- independent selected-pitch CQT spectral drop >= 6 dB over 3 frames

The observed valley timestamp is the only possible activation-based release candidate. The reattack timestamp itself is never duration.

## SAME-INFERENCE ACTIVATION SIDECAR — GREEN

Transcription:
`scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py`

Helper:
`scripts/songsterr-fresh/basic_pitch_activation_evidence.py`

Contracts:
- `songsterr-fresh-basic-pitch-note-activation-evidence-v1`
- `songsterr-fresh-basic-pitch-note-identity-v1`
- `songsterr-fresh-basic-pitch-inference-bundle-v1`

Hard guards:
- exactly one Basic Pitch `predict()` call
- same-inference activation evidence true
- decoded model ends diagnostic only
- decoded model ends used as duration false
- sidecar writes no `sourceEnd` / `durationSeconds`
- sidecar is not active duration authority
- pitch identity changes false
- mismatched/tampered sidecar rejected

Green same-inference probe run:
- run `34315619967`
- job `102351096162`
- head `4af488ececbe756fc168bb22578117ddf14d62d4`
- artifact `10090106400`
- digest `sha256:73fb818710903358399655d0c77cde216e2bc3106d7db57b6e00ac04e46cbdf6`

Capture-only validation run:
- run `34315700274`
- job `102351339722`
- head `e68769012344ab66ccc870e2bad4fce0d91d27c5`
- artifact `10090124225`
- digest `sha256:f14447af27cc58290da07553e5bc66856813987b878a9366c7f02891d0281466`

## V3 RELEASE FALLBACK — GREEN, REPEATED, STILL NON-AUTHORITATIVE

Prototype:
`scripts/songsterr-fresh/estimate_selected_pitch_releases_v3.py`

Contract:
`songsterr-fresh-spectral-activation-release-evidence-v3`

Dedicated canary:
`.github/workflows/songsterr-fresh-model-release-v3-canary.yml`

V3 design invariants:
- v2 spectral logic runs first unchanged
- v2-resolved events are never changed
- activation fallback is eligible only for exact v2 reason `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
- fixed activation + CQT rule only; no tuning/sweep
- release is the observed valley timestamp only and must precede same-pitch reattack
- generic next onset, same-pitch reattack timestamp, and decoded Basic Pitch note-off never become duration
- exact MIDI/start/event identity is preserved within each run
- activation release stage invokes no model
- model validation remains false
- customer eligibility remains zero

Repeated semantic fallback stability on commit `39f22fc49755f421aeac8d4b7caa7af2fdca0af2`:
- hosted-runner model inventories differed 1,139 versus 1,138 notes
- 1,137 events matched by exact MIDI and start time
- max matched start delta 0.0 s
- all 84 fallback events present in both attempts
- all 84 fallback durations exactly equal; max duration delta 0.0 s
- only unmatched events were unresolved MIDI-55 detections around 46 s
- none was a v3 fallback promotion

Post-fix full v3 canary:
- run `34319558226`
- job `102362962390`
- head `5afab9050a96428fc61a26ffae41c66c09610e7a`
- Basic Pitch 1,138 notes
- v2 577 resolved / 561 unresolved
- v3 +84 fallback = 661 resolved / 477 unresolved
- exact MIDI 1,138/1,138
- raw failures exactly `UNRESOLVED_DURATION: 477`
- `UNRESOLVED_RHYTHM_SPELLING` = 0
- customer events 0
- delivery false
- 98/98 tests
- artifact `10091514442`
- digest `sha256:fb033b19fb94128078a9d97a5832f2616cfef971aa5ba9ba2f0f90e703b6a010`

Latest hardened v3 canary before the current scaffold commit:
- run `34423610600`
- job `102704074546`
- head `d332cdf2fdf930aacf9023c63989270b16c5e736`
- Basic Pitch 1,139 notes
- v2 577 resolved / 562 unresolved
- v3 +84 fallback = 661 resolved / 478 unresolved
- exact MIDI 1,139/1,139
- raw failures exactly `UNRESOLVED_DURATION: 478`
- evaluator blockers unchanged
- customer eligible 0
- delivery false
- 98/98 tests
- artifact `10131961888`
- digest `sha256:660ba794985cda8b43db31e27d15f9510fc55cc5588fbd9a851a194f07747085`

The 477 versus 478 difference tracks known 1,138 versus 1,139 hosted-runner model-output variation and must not become a hardcoded acceptance count. V3 fallback remained exactly 84 in both variants.

## READ-ONLY UNRESOLVED V3 DURATION INVENTORY

Script:
`scripts/songsterr-fresh/summarize_v3_unresolved_duration_evidence.py`

Commit:
`628d556e193c70dd60bf2bb4292223ee05a19d4d`

Contract:
`songsterr-fresh-v3-unresolved-duration-inventory-v1`

Hard metadata:
- `descriptiveOnly: true`
- `changesDuration: false`
- `changesPitchIdentity: false`
- `invokesModel: false`
- `usesDecodedModelNoteEnd: false`
- `thresholdSelection: false`

Observed stable unresolved classes across two v3 runner variants:
- 18 insufficient onset-to-floor contrast
- 7 no clear sustained spectral release
- 76 activation candidate but insufficient fixed CQT spectral corroboration
- 5 insufficient activation drop
- no-sustained-subthreshold-activation varies by one event: 371 versus 372

These are descriptive measurements only, not thresholds or proposed cutoffs.

## RHYTHM FLOATING-POINT BOUNDARY DEFECT — FIXED

Fix commit:
`5afab9050a96428fc61a26ffae41c66c09610e7a`

Root cause:
- 21 event segments + 11 rest segments were numerical dust
- lengths roughly 3.6e-15 to 2.8e-14 s
- exact `Set` deduplication split mathematically identical beat/measure boundaries

Fix:
- discard only generated event/rest segments with length <= existing module `EPSILON`
- do not rewrite frozen structure, pitch identity, or release evidence

Regression:
`contextual rhythm spelling discards only sub-EPSILON floating-point boundary slices`

## INDEPENDENT REFERENCE-BLIND PITCH SUPPORT — TWO-RUN EXACT REPRODUCTION

Probe:
`scripts/songsterr-fresh/probe_independent_pitch_support.py`

Probe method is descriptive only and was fixed before inspecting fixture results:
- 80 ms post-onset measurement window
- direct semitone CQT bins
- local comparisons at ±1 and ±2 semitones
- octave comparisons at ±12 semitones
- selected-pitch long-run 20th-percentile spectral floor
- no acceptance threshold
- no threshold sweep
- no pitch rewrite/drop
- no duration/sourceEnd writes
- no reference tab
- no professional/reference scorer
- no archived V143 logic
- no Basic Pitch activation use
- no decoded Basic Pitch note-end use
- no model invocation inside the probe
- no `modelValidationComplete` mutation

Static independence guard rejects direct model/process/network imports in the probe. The probe verifies exact duration-free note identity and hashes the actual guitar-stem bytes against declared separation provenance before reporting.

First canary:
- run `34424545232`
- job `102706873344`
- head `4b806c247857458c6158e50a59d15b7130276c79`
- artifact `10132278606`
- ZIP size 757,426 bytes / 15 files
- digest `sha256:953af38fb6216706dab989d98b83c4fb2edba9826b7a810dda20ee15052766a6`

Structure-trigger dispatcher:
- commit `cf2afeb357b247d6cccaf648eef32dd3a52373fb`
- run `34425135282`
- job `102708656431`
- conclusion success
- dispatched second canary at the same head

Second canary:
- run `34425140684`
- job `102708677916`
- head `cf2afeb357b247d6cccaf648eef32dd3a52373fb`
- artifact `10132507650`
- ZIP size 757,426 bytes / 15 files
- digest `sha256:d0c01375094055377c04739ec41eef41cb450cafccac654137359f72ac543585`
- 98/98 tests
- customer eligible 0 / delivery false

Shared reproduced evidence across both runs:
- Demucs stem SHA `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- Basic Pitch 1,138 notes
- note identity SHA `e85323e5b7449ac84be7ad6076ed3ee9c2da1e9a37b3c64247637e4b82dcbe77`
- probe JSON SHA `534015d01246965228bfc6988d92117861ff2bcd360b32060ec1f8a95b7e08db`
- local semitone rank histogram 914 / 112 / 96 / 13 / 3
- octave rank histogram 793 / 323 / 22
- selected-minus-best-semitone-neighbor mean 1.9064934408727556 dB; median 3.0905303955078125 dB
- selected-minus-best-compared-alternative mean -1.4956962291301867 dB; median 1.403792381286621 dB
- selected-pitch-above-floor mean 38.670555924531236 dB; median 39.32196750640869 dB
- selected-minus-octave-above mean 8.893831113939335 dB; median 8.784372806549072 dB
- selected-minus-octave-below mean 27.434707292563466 dB; median 27.877296447753906 dB

Direct artifact-to-artifact comparison:
- both archives contain 15 files
- archive digests differ, but all 15 extracted payload files are byte-identical
- run A events 1,138 / run B events 1,138
- exact `(onsetId, sourceStart, selectedMidi)` intersection 1,138
- unmatched identities 0 / 0
- nonzero matched start-time deltas 0
- maximum matched start-time delta 0.0 s
- complete probe event arrays identical
- all recorded support-statistic cross-run deltas 0.0
- existing 10 ms simultaneous/start-cluster tolerance was not needed

Key extracted payload SHAs:
- `basic-pitch-guitar-notes.json` `494c48921c279277f5eba5a6678f70f081d95781136fef1e43e2304fec27faa2`
- `raw-model-note-evidence-duration-free.json` `ab9a5bfcd5ff12f368dcbe1bfe1e10a53ba7785cdeac3446ae120b3a16a2a090`
- `adapted-model-note-evidence-duration-free.json` `4b2940c910cf63c23ebb6a1c834a86eeb3283328c7e2190dabfd3ac19a75757b`
- `independent-pitch-support-a.json` `534015d01246965228bfc6988d92117861ff2bcd360b32060ec1f8a95b7e08db`
- `independent-pitch-support-b.json` `534015d01246965228bfc6988d92117861ff2bcd360b32060ec1f8a95b7e08db`
- `model-pipeline-duration-free-result.json` `4d899521d166157b38789c936b452e994eb51c317636583944c225e7899ebd5e`
- `adapted-structure-map.json` `8cc62bd649aa921643e39ecbdd4ab39837a6621f3f66d5c4407579f169f84770`

Interpretation boundary:
- for this runner pair there was no hosted-runner model-output variation
- this proves probe determinism/reproducibility for these two hosted runs, not transcription accuracy or ground truth
- independent audio-domain support is not an accuracy score
- do not derive an acceptance threshold from this fixture
- do not use self-consistency to clear `MODEL_EVIDENCE_VALIDATION_PENDING`

Checkpoint commits for this milestone:
- `1e27f13a0b987ceb37c12dd1a14f6b4ecae05da0` — second canary evidence
- `3997890c77a4ef73b8bd3fe8d6a73cc1fff181ab` — cross-run artifact proof

## MODEL-VALIDATION CONTRACT SCAFFOLD — IMPLEMENTED, FAIL-CLOSED

Implementation commit:
`7f8b88c4421ad3465fd1aa532d629fa1e27772ab`

New deterministic module:
`songsterr_pipeline/modelValidationContractScaffold.mjs`

Contract:
`songsterr-fresh-model-validation-contract-scaffold` v1

Purpose:
- provide a typed/structured home for model-validation design evidence
- bind diagnostics to a note-inference identity
- record reproducibility and independent pitch-support diagnostics
- explicitly enumerate independent evidence still required
- remain incapable of accepting the model path by itself

Hard scaffold properties:
- `ownsAcceptanceDecision: false`
- `externalValidationAuthorityDefined: false`
- `diagnosticEvidenceCanClearValidation: false`
- `mutatesModelValidationComplete: false`
- `validation.validated: false`
- `validation.acceptanceAuthority: null`
- blocker fixed to `MODEL_EVIDENCE_VALIDATION_PENDING`
- no threshold definition
- no threshold sweep
- no pitch rewrite
- no model invocation
- no process/network access
- no reference tab
- no archived V143 import

Required future independent evidence categories recorded by the scaffold:
- externally defined validation authority
- independent evidence not derived from Basic Pitch self-consistency
- identity-bound validation result

The existing evaluator was intentionally left unchanged. Its live fail-closed rule remains:
model-invoked evidence is rejected unless top-level `provenance.modelValidationComplete === true`.

New regression test file:
`songsterr_pipeline/tests/modelValidationContractScaffold.test.mjs`

Six new tests prove:
1. scaffold is fail-closed by construction
2. full reproducibility + independent pitch-support diagnostics cannot clear validation
3. diagnostic input cannot smuggle `validated`, `modelValidationComplete`, or an acceptance authority into the scaffold
4. scaffold defines no acceptance threshold and cannot rewrite pitch identity
5. scaffold output is deterministic
6. even the strongest support-only scaffold still leaves the real evaluator blocked by `MODEL_EVIDENCE_VALIDATION_PENDING`

Deterministic CI:
- run `34426840359`
- job `102713775748`
- head `7f8b88c4421ad3465fd1aa532d629fa1e27772ab`
- Ubuntu 24.04.5 / runner image `20260907.300.1`
- Node 22.23.2
- **104/104 tests pass**
- 0 failures
- existing fresh namespace isolation guard also passes

This implementation does not wire any new validation authority into Production or the evaluator. It only makes the pending-validation boundary explicit and regression-guarded.

## CURRENT PUSH-TRIGGERED REGRESSIONS

Head under test:
`7f8b88c4421ad3465fd1aa532d629fa1e27772ab`

Completed:
- `34426840359` — Songsterr Fresh Pipeline V1 Tests — success, 104/104

Still running at this checkpoint update:
- `34426840327` — Songsterr Fresh Deterministic Activation Valley Probe — in progress
- `34426840323` — Songsterr Fresh Model Release V3 Canary — in progress
- `34426840393` — Songsterr Fresh Independent Pitch Support Canary — in progress

Record their final evidence here when completed. Do not treat an in-progress run as passed.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**.

V3 is a validated candidate release authority for research/canary use only. V2 remains authoritative. Do not silently replace v2 in the authoritative model workflow and do not expose v3 durations to customers until a separate promotion decision is explicitly documented.

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

1. Record final results for the three current push-triggered regressions (`34426840327`, `34426840323`, `34426840393`) without changing acceptance state.
2. Treat model-validation scaffold design steps as complete for now. Do not add an accepting path until a genuinely independent validation authority/evidence source is explicitly designed and justified.
3. Continue descriptive study of the remaining 477/478 duration ambiguity separately. Keep audited v2 authoritative and v3 candidate-only; preserve the fixed activation + spectral rule exactly and do not tune it on this fixture.
4. Any new duration study must be descriptive/identity-preserving by default: no duration mutation, no pitch mutation, no decoded Basic Pitch note-off, no generic next onset, no reattack-as-duration, and no fixture-derived threshold selection.
5. Any future v3 promotion from candidate to authoritative release authority must be an explicit documented branch decision with v2 preserved for regression comparison.
6. Before any customer exposure, independently validate the model path and obtain complete required duration evidence; evaluator and delivery must remain fail-closed until both blockers are legitimately cleared.
