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
canonicalLength 19653

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

The same Basic Pitch `predict()` call emits decoded notes and optionally captures the playable-MIDI activation slice. The sidecar cryptographically binds:
- sorted note identity `(startSeconds, midi, confidence)`
- exact float32 activation matrix bytes
- exact float64 frame-time bytes
- MIDI range and matrix shape

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

V3 design:
1. require duration-free evidence
2. preserve explicit model-upstream authorization
3. cryptographically verify the same-inference activation sidecar
4. run existing v2 spectral logic first using unchanged v2 constants/functions
5. never change a v2-resolved event
6. activation fallback is eligible only for exact v2 reason `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
7. apply the unchanged fixed activation + CQT rule
8. release is the observed valley timestamp only
9. require release < next same-pitch reattack
10. generic next onset never becomes duration
11. decoded Basic Pitch note-off never becomes duration
12. same-pitch reattack itself never becomes duration
13. activation fallback emits `durationConfidence: null`
14. exact MIDI/start/event identity is preserved within each run
15. failed fallback keeps the original v2 unresolved reason
16. provenance distinguishes v2 spectral release from activation+spectral fallback
17. activation release stage invokes no model
18. model validation remains false
19. customer eligibility remains zero

### Repeated semantic fallback stability

Two independent green attempts on commit `39f22fc49755f421aeac8d4b7caa7af2fdca0af2` produced slightly different hosted-runner model inventories (1,139 versus 1,138 notes) but the same 84 v3 fallback events.

Cross-attempt comparison found:
- 1,137 events matched by exact MIDI and start time
- max matched start delta 0.0 s
- all 84 fallback events present in both attempts
- all 84 fallback durations exactly equal; max duration delta 0.0 s
- only unmatched events were unresolved MIDI-55 detections around 46 s
- none of those unmatched events was a v3 fallback promotion

This is semantic fallback repeatability, not byte-identical cross-run model determinism.

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

The inventory cross-checks its counts against v3 release evidence and reports unresolved reason / fallback-rejection distributions and same-pitch reattack-gap statistics. It creates no release decisions.

Observed stable unresolved classes across the two v3 runner variants:
- 18 insufficient onset-to-floor contrast
- 7 no clear sustained spectral release
- 76 activation candidate but insufficient fixed CQT spectral corroboration
- 5 insufficient activation drop
- no-sustained-subthreshold-activation varies by one event: 371 versus 372

The no-sustained-activation group has short reattack gaps (median ~0.221 s, p90 ~0.442 s); the insufficient-spectral-corroboration group has a longer median gap (~0.709 s). These are descriptive measurements only, not thresholds or proposed cutoffs.

## RHYTHM FLOATING-POINT BOUNDARY DEFECT — FIXED

Root cause of the previous 32 `UNRESOLVED_RHYTHM_SPELLING` failures:
- 21 event segments + 11 rest segments
- segment lengths roughly 3.6e-15 to 2.8e-14 s
- mathematically identical beat/measure boundaries had tiny floating-point representation differences
- exact `Set` deduplication treated those values as separate cuts and created numerical-dust note/rest slices

Fix commit:
`5afab9050a96428fc61a26ffae41c66c09610e7a`

Fix:
- discard only generated event/rest segments with length <= the module's existing `EPSILON`
- do not rewrite frozen structure
- do not change pitch identity
- do not change source duration/release evidence

Regression test:
`contextual rhythm spelling discards only sub-EPSILON floating-point boundary slices`

Post-fix deterministic suite:
98/98 green.

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

## V3 CI HARDENING — GREEN

Workflow-only hardening commit:
`d332cdf2fdf930aacf9023c63989270b16c5e736`

Commit message:
`ci: harden v3 raw failure and inventory guards`

Changed only:
`.github/workflows/songsterr-fresh-model-release-v3-canary.yml`

No v2 source, v3 release logic, model logic, deterministic pipeline source, Production, or `main` changes were made.

Permanent guards added:
1. the read-only unresolved-duration inventory script is a workflow trigger dependency
2. the canary generates `v3-unresolved-duration-inventory.json`; the existing `*.json` artifact glob includes it
3. the deterministic pipeline raw failure set must contain exactly one entry:
   - code `UNRESOLVED_DURATION`
   - count exactly equal to `pipelineSummary.unresolvedDurationCount`
4. any additional raw rhythm/notation/MIDI/structure/playability failure now fails the v3 canary

### Latest hardened v3 canary — GREEN

Run:
`34423610600`

Job:
`102704074546`

Head:
`d332cdf2fdf930aacf9023c63989270b16c5e736`

Runner:
- ubuntu-24.04
- image `20260907.300.1`
- Azure `centralus`

Decoded inputs:
- analysis WAV SHA `824af60bbc3d701c8c1f085194be2acf59f0ac5d0ae4133e763eadb9793ca873`
- separation WAV SHA `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`

Runtime-scoped Demucs guitar stem SHA:
`c303f0a0d99f94e2bddedebd0679cc5034aa9505c350cc28a5200d4c419637af`

This stem SHA is diagnostic only and is a previously observed valid hosted-runner variant.

Basic Pitch latest-run evidence:
- 1,139 notes
- 97 polyphonic start clusters
- max cluster size 4
- note identity SHA `46e4ca9ff9722e0c7f787de234c1f03bbdaa188dac6e7c27929a1f2591365608`
- inference bundle SHA `e8f40c295125313835264c5781414c3ada2fd4986942c9f2a65fe526a5b0253f`
- single predict invocation
- decoded model ends diagnostic only

V2 latest-run evidence:
- attempted 1,139
- 577 resolved / 562 unresolved
- 537 `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
- 18 `INSUFFICIENT_ONSET_TO_FLOOR_CONTRAST`
- 7 `NO_CLEAR_SUSTAINED_SPECTRAL_RELEASE`
- same-pitch censor count 967

V3 latest-run evidence:
- v2 runs first: 577 resolved
- fallback attempted 537
- fallback resolved 84
- fallback unresolved 453
- fallback rejection reasons:
  - 5 `INSUFFICIENT_ACTIVATION_DROP`
  - 76 `INSUFFICIENT_SPECTRAL_CORROBORATION`
  - 372 `NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION`
- final 661 resolved / 478 unresolved
- resolution rate ~0.580333626
- final unresolved reasons:
  - 453 `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
  - 18 `INSUFFICIENT_ONSET_TO_FLOOR_CONTRAST`
  - 7 `NO_CLEAR_SUSTAINED_SPECTRAL_RELEASE`
- fallback mean span ~0.299432 s
- fallback median span ~0.290249 s
- fallback max span ~1.069402 s
- no next-onset duration
- no reattack timestamp as duration
- no decoded model-end duration
- no invented activation confidence
- activation release stage invokes no model

Probe parity latest run:
- 537 reattack-censored events examined
- exactly 84 corroborated valleys
- exact onset-ID parity with v3 fallback
- candidate rate ~15.6425%
- rejection split exactly 5 / 76 / 372
- probe model invocation false

Read-only inventory latest run:
- duration-eligible events 1,139
- resolved 661
- unresolved 478
- fallback rejections 5 / 76 / 372
- primary final unresolved reasons 18 / 453 / 7
- hard descriptive-only guards passed

Deterministic pipeline latest run:
- source events 1,139
- pitch-resolved 1,139
- role-accepted 1,139
- exact MIDI preserved 1,139/1,139
- complete/customer eligible 0
- unresolved duration 478
- fretboard path resolved true
- raw failures exactly `[{"code":"UNRESOLVED_DURATION","count":478}]`
- `UNRESOLVED_RHYTHM_SPELLING` absent
- rawIntegrityPassed false
- upstream blockers exactly include `MODEL_EVIDENCE_VALIDATION_PENDING` and `DURATION_EVIDENCE_INCOMPLETE`
- modelValidationComplete false
- deliveryReady false
- structuredRenderEligible false

Tests:
98/98 green.

Artifact:
- name `songsterr-fresh-model-release-v3-evidence`
- ID `10131961888`
- ZIP size 6,875,747 bytes
- 20 files
- digest `sha256:660ba794985cda8b43db31e27d15f9510fc55cc5588fbd9a851a194f07747085`
- retention through 2026-09-24 UTC

### Important 477 versus 478 boundary

The post-rhythm-fix run on stem variant `4227a41f...` had 1,138 notes and 477 unresolved durations. The latest hardened run on stem variant `c303f0a0...` had 1,139 notes and 478 unresolved durations.

The v3 fallback remained exactly 84 in both observed variants. The one-event difference belongs to the already documented hosted-runner model-output variation and must **not** become a hardcoded acceptance count. The CI gate intentionally checks dynamic unresolved-count parity rather than requiring 477 or 478.

## INDEPENDENT REFERENCE-BLIND PITCH SUPPORT — FIRST CANARY GREEN

Probe:
`scripts/songsterr-fresh/probe_independent_pitch_support.py`

Probe commit:
`b8082a63...`

Dedicated canary:
`.github/workflows/songsterr-fresh-independent-pitch-support-canary.yml`

Workflow commit:
`4b806c247857458c6158e50a59d15b7130276c79`

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

Static independence guard rejects direct model/process/network imports in the probe. The probe also verifies exact duration-free note identity and hashes the actual guitar-stem bytes against declared separation provenance before reporting.

First green canary:
- run `34424545232`
- job `102706873344`
- head `4b806c247857458c6158e50a59d15b7130276c79`
- Demucs stem SHA `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- Basic Pitch 1,138 notes
- note identity SHA `e85323e5b7449ac84be7ad6076ed3ee9c2da1e9a37b3c64247637e4b82dcbe77`
- probe A/B JSON byte-identical
- probe JSON SHA `534015d01246965228bfc6988d92117861ff2bcd360b32060ec1f8a95b7e08db`
- all 1,138 `(onsetId, sourceStart, selectedMidi)` rows preserved exactly
- selected MIDI ranked #1 among ±1/±2 semitone comparison bins on 914/1,138 events (~80.3%)
- selected MIDI ranked #1 among selected + ±1-octave comparison bins on 793/1,138 events (~69.7%)
- local semitone rank histogram: 914 / 112 / 96 / 13 / 3 for ranks 1–5
- octave rank histogram: 793 / 323 / 22 for ranks 1–3
- selected-minus-best-semitone-neighbor median ~3.091 dB; mean ~1.906 dB
- selected-minus-best-compared-alternative median ~1.404 dB; mean ~-1.496 dB
- selected-pitch-above-floor median ~39.322 dB
- evaluator still blocks on `MODEL_EVIDENCE_VALIDATION_PENDING` + `DURATION_EVIDENCE_INCOMPLETE`
- complete/customer eligible 0
- delivery false
- 98/98 tests
- artifact `10132278606`
- artifact digest `sha256:953af38fb6216706dab989d98b83c4fb2edba9826b7a810dda20ee15052766a6`

Interpretation boundary:
- this is independent audio-domain support evidence, not ground truth
- semitone-local support is substantially stronger than octave discrimination
- do not collapse these metrics into a single accuracy score
- do not derive an acceptance threshold from this fixture
- do not use this first-run self-consistency to clear `MODEL_EVIDENCE_VALIDATION_PENDING`

## PITCH-SUPPORT STRUCTURE TRIGGER — GREEN

Trigger-hardening commit:
`cf2afeb357b247d6cccaf648eef32dd3a52373fb`

Dispatcher:
`.github/workflows/songsterr-fresh-independent-pitch-support-structure-trigger.yml`

Purpose:
- watch the full-mixture structure-analysis dependencies used by the pitch-support canary
- dispatch the existing independent pitch-support canary at the current branch HEAD
- avoid duplicating or weakening the established proof workflow

Dispatcher run:
- run `34425135282`
- job `102708656431`
- head `cf2afeb357b247d6cccaf648eef32dd3a52373fb`
- conclusion success

The dispatcher successfully launched second full pitch-support canary run `34425140684` at the same head.

At checkpoint-save time, second run `34425140684` is still in progress. Do not assume its result; fetch its final run/job status and artifact before performing cross-run semantic comparison.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Raw deterministic failures are now duration-only. The previous 32 numerical-dust rhythm failures are resolved and guarded against regression.

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

1. Start by fetching canonical branch `songsterr-fresh-pipeline-v1` and re-reading this checkpoint. Do not work on `main` or Production.
2. Check second independent pitch-support canary run `34425140684` to completion. It was launched by the green structure-trigger dispatcher at head `cf2afeb357b247d6cccaf648eef32dd3a52373fb` and was still running when this checkpoint was saved.
3. If run `34425140684` is green:
   - fetch its job logs and artifact metadata
   - record exact run/job/head/artifact/digest
   - record its Demucs stem SHA, Basic Pitch note count, note-identity SHA, probe A/B SHA, rank histograms, and continuous dB summaries
   - confirm 98/98 deterministic tests, evaluator blockers unchanged, customer eligible 0, and delivery false
4. Download/inspect both pitch-support artifacts and perform a **descriptive cross-run semantic comparison** only:
   - compare exact note identities where they overlap
   - reuse the already established 10 ms simultaneous/start-cluster tolerance only if needed for hosted-runner event matching; do not invent a new tolerance
   - report matched event count, unmatched event identities, start-time deltas, and stability of semitone/octave rank/support metrics
   - distinguish hosted-runner model-output variation from probe determinism
   - do not convert the comparison into an accuracy score or acceptance threshold
5. If run `34425140684` fails, fix only the isolated pitch-support probe/workflow/dispatcher boundary implicated by the failure. Do not modify v2 release authority, v3 fixed fallback thresholds, frozen structure, or customer delivery gates unless independently justified by a separate defect.
6. Update this checkpoint immediately after the second-run/cross-run milestone with exact evidence. Keep the first green canary (`34424545232`, artifact `10132278606`, digest `sha256:953af38f...`) as the baseline comparison point.
7. After the cross-run comparison, decide only whether the independent probe is stable enough to support designing a **future explicit model-validation contract**. Do not set `modelValidationComplete: true` from this fixture or from Basic Pitch/CQT self-consistency alone.
8. Continue descriptive study of the remaining 477/478 duration ambiguity separately. Keep audited v2 authoritative and v3 candidate-only; preserve the fixed activation + spectral rule exactly and do not tune it on this fixture.
9. Any future v3 promotion from candidate to authoritative release authority must be an explicit documented branch decision with v2 preserved for regression comparison.
10. Before any customer exposure, independently validate the model path and obtain complete required duration evidence; evaluator and delivery must remain fail-closed until both blockers are legitimately cleared.
