# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-10 00:05 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the only canonical fresh-chat checkpoint for the Songsterr-inspired fresh pipeline.

> Checkpoint compaction note: the prior verbose diagnostic history remains in Git at parent head `b0b8595a28304df64bc5804e8ce472428652e3f4`. This file is intentionally kept focused on current authoritative state, hard boundaries, evidence needed for the next engineering decision, and the most relevant historical run references.

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
- Cross-run event identity must use stable content identity (`MIDI` + exact source start and bound inference identity where applicable), not raw sequential Basic Pitch index alone.
- Preserve `/ai-tab`: audio upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.

## EXACT AUTHORIZED FIXTURE

On `main`:
`public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`

Git blob SHA:
`4dd709e3fa177b4daeed71ca97f0199757729d4b`

Duration:
~210.674648526 s

Decoded separation WAV expected SHA-256:
`e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`

Canaries fetch the raw fixture from `main`, verify `git hash-object`, decode it, and fail closed if the decoded separation SHA changes.

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

Pinned model/runtime core:
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

Current fixed Demucs settings:
- model `htdemucs_6s`
- `--device cpu`
- `--shifts 0`
- `--overlap 0.25`
- `--segment 7`

Pinned Demucs asset authority:
- verifier contract `songsterr-fresh-demucs-model-asset-v2`
- HF repo `adefossez/HTDemucs-6s`
- pinned revision `3c5ee475be622df764938de97e4281a7b07ffa58`
- asset upload revision `053e1404489b3dc58bf718224fac4b7316de8c93`
- asset `5c90dfd2.safetensors`
- asset SHA-256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- legacy fallback is not primary

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

Resolved V2 method: `selected-pitch-sustained-spectral-decay`.
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
- all 84 fallback-resolved events remained stable in compared historical variants
- historical output variation is isolated to extra/unresolved detections and activation rejection classification drift; it must never become a hardcoded acceptance count

Representative outputs:
- 1,138-note environment: V2 577/561; V3 +84 => 661/477
- 1,139-note environment: V2 577/562; V3 +84 => 661/478
- customer events 0 / delivery false in both

## IMPORTANT REFERENCE-BLIND DIAGNOSTIC HISTORY

These diagnostics are descriptive only and cannot clear model validation or define a release threshold.

- V3 unresolved inventory: run `34427390493`, artifact `10133331991`.
- Frozen reattack/structure context: corrected run `34429657211`, job `102722261026`; spacing separated groups more than structure-slot alignment, but spacing is not a release cutoff.
- Independent pitch support: runs `34424545232`, `34425140684`, and `34426840393`; common historical events retained semitone/octave rank support across model-count variants, but self-consistency is not ground truth.
- Model-validation scaffold remains fail-closed: `songsterr_pipeline/modelValidationContractScaffold.mjs`, implementation `7f8b88c4421ad3465fd1aa532d629fa1e27772ab`.
- Spectral rejection context: green run `34430069785`, artifact `10134306664`; 84 corroborated / 76 insufficient in that environment; activation valley alone did not explain CQT rejection.
- Corrected CQT post-valley trajectory: run `34432234675`, artifact `10135045827`, digest `sha256:dc1cebfff20dd1d8856ec2df27129ee694edda40fe12ee5178309f0a87c1c83b`; 1,138 model notes; V2 577/561; V3 661/477.
- Corrected STFT cross-check: run `34433150157`, artifact `10135364820`, digest `sha256:e6401de502cc6159621274a0a5fd39dd9c321d6451f445d07a49cd85cda570c7`; 1,139 model notes; source population 84 corroborated / 76 insufficient.
- Controlled same-run CQT↔STFT comparator: run `34434013368`, artifact `10135685374`, digest `sha256:3c46d3a1d13e0f946443ea0a990eb422b91c659e5779d2a14a09effc99c946d4`; 1,139 model notes; V2 577/562; V3 661/478; same-run population 84 corroborated / 75 insufficient. Representation correlation remained low, so CQT/STFT are not substitutes and no consensus duration rule follows.

## DEMUCS HOSTED-RUNNER BYTE-REPRODUCIBILITY — CROSS-RUN ISSUE REMAINS OPEN

Observed with the same decoded separation-input SHA and fixed Demucs model/settings:
- corrected CQT canary `34432234675`: guitar WAV SHA `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- corrected STFT canary `34433150157`: guitar WAV SHA `c303f0a0d99f94e2bddedebd0679cc5034aa9505c350cc28a5200d4c419637af`
- controlled same-run representation canary `34434013368`: guitar WAV SHA `5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33`

Observed downstream drift associated with those hosted-run differences:
- model-note inventories varied 1,138/1,139
- one exact MIDI 64 event at source start ~113.071807709751 s shifted unresolved fallback rejection class across historical environments
- raw sequential Basic Pitch `onsetId` shifted with the inventory; therefore it is not a valid cross-run identity by itself
- the V3 fallback-resolved count remained 84

Interpretation boundary:
- this is a reproducibility engineering issue, not evidence that any hosted-run stem is more correct
- do not select a preferred stem by downstream agreement
- do not tune Demucs, Basic Pitch, CQT/STFT, or release thresholds to reproduce a historical inventory
- cross-run continuous DSP comparison remains non-authoritative until the environment boundary is characterized

## DEMUCS SAME-RUN REPRODUCIBILITY DIAGNOSTIC — GREEN

Comparator: `scripts/songsterr-fresh/compare_demucs_stem_reproducibility.py`
Contract: `songsterr-fresh-demucs-stem-reproducibility-comparison-v1`
Comparator implementation: `1cdd62040e4c196748f8eeecf2f97c43ec5f9e32`
Diagnostic guard wiring: `11560137c512128cd1eb108aad77ceb24c531f8a`
Pinned lightweight dependency repair: `e4d6a732a1b8419408a52599ac32458e053a488b`
Full reproducibility workflow wiring: `b0b8595a28304df64bc5804e8ce472428652e3f4`
Workflow: `.github/workflows/songsterr-fresh-demucs-reproducibility-canary.yml`

Authoritative full canary:
- run `34435154554`
- job `102738562141`
- head `b0b8595a28304df64bc5804e8ce472428652e3f4`
- conclusion: **success**
- completed `2026-09-10T04:03:06Z`
- artifact `10136054300`
- artifact digest `sha256:a694ecb4da7ec5f34cbaf9e61833871f81b806ec87b93b18f9392a9cece97a51`
- artifact expires `2026-09-24T04:03:03Z`

Verified same-job result:
- decoded separation input SHA: `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- pass A WAV SHA: `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- pass B WAV SHA: `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- pass A PCM SHA: `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2`
- pass B PCM SHA: `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2`
- file bytes identical: true
- decoded PCM bytes identical: true
- exact sample equality: true
- differing PCM values: 0 / 18,581,504 = 0.0
- MAE: 0.0
- RMSE: 0.0
- max absolute difference: 0.0
- SNR relative to A: null because error RMS is exactly zero
- reference stem RMS: `0.05302134928309948`
- sample rate: 44,100 Hz
- shape: 9,290,752 frames × 2 channels

Runtime provenance for this green same-job canary:
- CPU: `AMD EPYC 7763 64-Core Processor`
- GitHub runner image: `ubuntu-24.04`, image version `20260907.300.1`
- hosted compute provisioner version `20260828.587`, Azure region `eastus`
- OS reported by job: Ubuntu 24.04.5 LTS
- kernel/platform: `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`
- Python 3.10.21
- FFmpeg 6.1.1-3ubuntu5
- Torch runtime `2.14.0+cu130`
- Torch CPU capability AVX2; MKL/MKLDNN/OpenMP available
- Torch intra-op threads 1; inter-op threads 4
- CUDA unavailable
- fixed OMP/MKL/OpenBLAS/NumExpr thread environment = 1; PYTHONHASHSEED=0
- pinned Demucs asset verification passed exactly

Comparator boundaries remain intact:
- reference-blind and diagnostic-only
- cannot select a preferred stem
- cannot mutate notes, pitch identity, duration, sourceEnd, release evidence, or acceptance state
- no Basic Pitch invocation and no V2/V3 release invocation in this workflow
- no threshold selection/sweep or downstream-agreement optimization

Authoritative interpretation:
- **Demucs is byte/PCM deterministic for two repeated passes inside this one runner/runtime.**
- This does **not** establish byte-identical output across independent hosted runners/environments.
- The current pass A/B SHA equals the historical corrected-CQT stem SHA `4227a41f...`, while other historical hosted runs produced `c303f0a0...` and `5b3e7c6f...`.
- Therefore the next problem is specifically the independent-run runner/CPU/runtime boundary, not within-process/pass nondeterminism.
- No duration-rule research should resume until that boundary is characterized enough to know what upstream variation is being consumed.

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

## NEXT ENGINEERING STEPS

1. Treat run `34435154554` as the authoritative same-run reproducibility result: two Demucs passes are byte/PCM identical on one AMD EPYC 7763 hosted runner.
2. Characterize the **cross-run** hosted-environment boundary next. Start with the known differing-stem runs `34432234675`, `34433150157`, and `34434013368`: compare runner image version/provisioner/OS/kernel where logs expose them. Do not infer CPU model when an older workflow did not record it.
3. If historical logs are insufficient to isolate the boundary, create one narrow reference-blind Demucs provenance canary that runs the exact verified input + pinned asset + fixed Demucs settings on multiple independent hosted jobs/runners and records CPU model, `lscpu`, runner image, kernel, Torch build/runtime, package versions, file SHA, and decoded PCM SHA. It must not invoke Basic Pitch, V2, V3, or any scorer.
4. Cross-run provenance diagnostics must define no preferred stem, acceptance threshold, duration rule, threshold sweep, or downstream-agreement objective.
5. Do not resume duration-rule research until the upstream Demucs cross-run variation is characterized. Do not create another release delay/cutoff, representation-consensus rule, or threshold experiment while this issue remains open.
6. Keep cross-run event identity based on stable content identity (`MIDI` + exact source start and bound inference identities where applicable), never raw sequential Basic Pitch index alone.
7. Keep V2 authoritative and V3 candidate-only. Preserve `MODEL_EVIDENCE_VALIDATION_PENDING`, `DURATION_EVIDENCE_INCOMPLETE`, `modelValidationComplete: false`, and customer eligibility 0 unless genuinely independent evidence later clears them through an explicitly designed authority.
8. Do not use reference tabs/scorers, decoded Basic Pitch note end as duration, generic next onset as duration, same-pitch reattack as default duration, optimizer/threshold sweeps, or archived V143/Gomyway logic.
9. Update this checkpoint immediately after each authoritative cross-run provenance result or material engineering change.

The archived V143/Gomyway pipeline remains out of scope.