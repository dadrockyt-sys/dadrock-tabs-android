# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-10 00:18 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the only canonical fresh-chat checkpoint for the Songsterr-inspired fresh pipeline.

> Checkpoint compaction note: prior verbose diagnostic history remains in Git at head `b0b8595a28304df64bc5804e8ce472428652e3f4`. This file stays focused on current authoritative state, hard boundaries, evidence needed for the next engineering decision, and the most relevant historical run references.

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
- basic-pitch 0.4.0 where Basic Pitch is explicitly invoked
- librosa 0.11.0 where release diagnostics require it
- soundfile 0.13.1
- tflite-runtime 2.14.0 where Basic Pitch is explicitly invoked
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

## AUTHORITATIVE SAME-RUN DEMUCS REPRODUCIBILITY — GREEN

Comparator: `scripts/songsterr-fresh/compare_demucs_stem_reproducibility.py`
Contract: `songsterr-fresh-demucs-stem-reproducibility-comparison-v1`
Workflow: `.github/workflows/songsterr-fresh-demucs-reproducibility-canary.yml`

Run:
- run `34435154554`
- job `102738562141`
- head `b0b8595a28304df64bc5804e8ce472428652e3f4`
- conclusion success
- artifact `10136054300`
- digest `sha256:a694ecb4da7ec5f34cbaf9e61833871f81b806ec87b93b18f9392a9cece97a51`

Verified same-job result:
- input SHA exact
- pass A/B WAV SHA both `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- pass A/B decoded float32 PCM SHA both `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2`
- exact sample equality true
- differing PCM values 0 / 18,581,504
- MAE/RMSE/max absolute difference all 0.0
- RMS `0.05302134928309948`
- 44,100 Hz; 9,290,752 frames × 2 channels
- CPU `AMD EPYC 7763 64-Core Processor`
- Torch CPU capability AVX2
- Azure eastus
- image `20260907.300.1`, Ubuntu 24.04.5
- kernel/platform `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`
- Torch `2.14.0+cu130`; intra-op 1; inter-op 4; CUDA unavailable

Interpretation:
- Demucs is byte/PCM deterministic for two repeated passes inside this one runner/runtime.
- This does not establish byte-identical output across independent hosted runners/environments.

## AUTHORITATIVE CROSS-RUN DEMUCS PROVENANCE — GREEN DIAGNOSTIC, VARIATION CONFIRMED

Implementation:
- `scripts/songsterr-fresh/record_demucs_cross_run_provenance.py`
  - commit `41b57e29b26d36a4d3697efd040d2930e4840b87`
  - contract `songsterr-fresh-demucs-cross-run-provenance-v1`
- `scripts/songsterr-fresh/compare_demucs_cross_run_provenance.py`
  - commit `2e714380cd0436a220d8101fa012369660bed8d5`
  - contract `songsterr-fresh-demucs-cross-run-comparison-v1`
- `.github/workflows/songsterr-fresh-demucs-cross-run-provenance-canary.yml`
  - head `fffece201a31d8c56dc49a7e6637df779debc170`

Authoritative canary:
- run `34436134514`
- conclusion success
- three independent hosted Demucs jobs plus one JSON-only aggregate comparison job
- aggregate job `102742547664`
- aggregate artifact `10136341469`
- aggregate artifact digest `sha256:c8481becb4ebb5444e0b0b2e50bcf7ecf3273b84ed03b9d0b421d3557722c69e`

All three independent jobs verified the same:
- exact source Git blob
- exact decoded separation SHA `e03e1885...474a`
- Demucs 4.1.0 `htdemucs_6s`
- CPU, shifts 0, overlap 0.25, segment 7
- exact pinned HF model asset SHA `d2a1745f...d411`
- Python 3.10.21
- Torch `2.14.0+cu130`
- same kernel/platform `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`
- glibc 2.39
- Torch intra-op 1 / inter-op 4
- CUDA unavailable
- same 44,100 Hz output shape: 9,290,752 × 2

Independent results:

| Sample | Job | Azure region | Ubuntu / image | CPU | Torch CPU capability | Stem WAV SHA-256 | Decoded PCM SHA-256 | RMS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | `102741473454` | eastus | 24.04.4 / `20260831.293.1` | AMD EPYC 7763 | AVX2 | `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81` | `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2` | `0.05302134928309948` |
| b | `102741473233` | northcentralus | 24.04.4 / `20260831.293.1` | AMD EPYC 9V74 | AVX512 | `0d9339dfedd13ee4d2d7f1a1262363f8a756dce4fc1168182208b0ed431cec12` | `0bd756ad4362f150fd6997835c9a91791963fe30722d4ec4d41283a41ae70219` | `0.05302134818956235` |
| c | `102741473405` | eastus2 | 24.04.5 / `20260907.300.1` | AMD EPYC 9V74 | AVX2 | `5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33` | `6d3ac44cd3f0156253ff7b820b72f5eda8d59eb8c60f8abd68a87c0598ec4987` | `0.05302134706465266` |

Per-sample artifacts:
- a artifact `10136333426`, digest `sha256:1c4e4caa9b0555ca3d535120c95bf5fb01198dd2b9fbf6c7a34a75b12d227a31`
- b artifact `10136318426`, digest `sha256:047c77e6cd9980c86fdf88badc032dbb7fdc789dbb84b66c7991721f6d3d2d5e`
- c artifact `10136334343`, digest `sha256:34220b9a67106cd3158661b2a29547f06634be2c72f15d94d203effc94540f74`

Aggregate result:
- observation count 3
- distinct stem-file SHA count 3
- distinct decoded-PCM SHA count 3
- all file bytes identical false
- all decoded PCM identical false
- cross-run PCM variation observed true

Important exact reproductions:
- sample a exactly reproduced the historical corrected-CQT/same-run `4227a41f...` file hash and `cf07e142...` PCM hash.
- sample c exactly reproduced the historical controlled CQT↔STFT `5b3e7c6f...` file hash.
- sample b produced a newly observed fourth historical file hash `0d9339df...`.

What this evidence rules out as a complete explanation:
- **runner image version alone**: samples a and b used the same old image but produced different hashes; the `4227a41f...` hash has also occurred on both old and new image generations.
- **CPU model alone**: samples b and c were both AMD EPYC 9V74 but produced different hashes.
- **Torch-reported AVX capability alone**: samples a and c both reported AVX2 but produced different hashes.
- **region alone** is not isolated by this run and remains descriptive only; historical centralus already produced two different hashes, so region is not a complete explanation either.

What the evidence positively supports:
- cross-run Demucs output is sensitive to the effective hosted execution environment even when source bytes, decoded input, model asset, top-level package pins, thread environment, Demucs command/settings, Python version, Torch version, kernel family, and output geometry match.
- the effective CPU/runtime dispatch path is part of the remaining reproducibility boundary: b and c share the same EPYC 9V74 model but expose different Torch CPU capabilities (AVX512 vs AVX2) and produce different PCM.
- this does **not** prove that AVX512 vs AVX2 by itself caused the difference because b and c also differ in image/region/host details.
- no observed stem is more correct. No preferred stem or environment may be selected from downstream Basic Pitch/release agreement.

Hard diagnostic boundaries all passed:
- reference blind / diagnostic only
- no Basic Pitch
- no V2/V3 release invocation
- no note/pitch/duration/sourceEnd mutation
- no preferred-stem selection
- no threshold selection/sweep
- no downstream-agreement objective
- no acceptance decision/customer delivery
- no archived V143/reference scorer/reference tab logic

## RELEVANT HISTORICAL HOSTED STEMS

| Run | Stem WAV SHA-256 | Azure region | Ubuntu | Runner image | CPU captured? |
| --- | --- | --- | --- | --- | --- |
| `34432234675` corrected CQT | `4227a41f...` | eastus | 24.04.4 | `20260831.293.1` | no |
| `34433150157` corrected STFT | `c303f0a0...` | centralus | 24.04.5 | `20260907.300.1` | no |
| `34434013368` controlled CQT↔STFT | `5b3e7c6f...` | centralus | 24.04.4 | `20260831.293.1` | no |
| `34435154554` same-run repro | `4227a41f...` | eastus | 24.04.5 | `20260907.300.1` | EPYC 7763 / AVX2 |

Observed downstream drift associated with historical stem differences:
- model-note inventories varied 1,138/1,139
- one exact MIDI 64 event at source start ~113.071807709751 s shifted unresolved fallback rejection class across historical environments
- raw sequential Basic Pitch `onsetId` shifted with the inventory; therefore it is not a valid cross-run identity by itself
- V3 fallback-resolved count remained 84

These downstream facts remain descriptive only and may not be used to select a Demucs environment or stem.

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

1. Keep duration-rule research paused. The cross-run Demucs boundary is now confirmed but not yet isolated to one controllable runtime factor.
2. Next use a **narrow same-host CPU-dispatch diagnostic** if a supported runtime control can be verified from authoritative PyTorch/oneDNN behavior: on a host that natively exposes AVX512, compare one native fixed Demucs pass with one explicitly capped common CPU-ISA path in separate processes on the same runner. This must remain reference-blind and may compare only stem/PCM hashes plus runtime provenance.
3. Before implementing any CPU-ISA cap, verify the exact supported environment/runtime controls for the installed Torch/oneDNN path. Do not guess an environment variable or silently alter production execution.
4. The same-host dispatch diagnostic must not invoke Basic Pitch, V2, V3, a scorer, duration logic, or downstream agreement. It must not define a preferred stem or acceptance threshold.
5. If a same-host capability cap reproduces another known PCM hash, record that as evidence about numerical dispatch reproducibility only—not correctness. If it does not, record the negative result and continue isolating the next runtime dimension.
6. Do not resume duration-rule research until the upstream Demucs cross-run variation is characterized enough to define a reproducible execution contract or explicitly accept bounded numerical variation without using downstream agreement to choose it.
7. Keep cross-run event identity based on stable content identity (`MIDI` + exact source start and bound inference identities where applicable), never raw sequential Basic Pitch index alone.
8. Keep V2 authoritative and V3 candidate-only. Preserve `MODEL_EVIDENCE_VALIDATION_PENDING`, `DURATION_EVIDENCE_INCOMPLETE`, `modelValidationComplete: false`, and customer eligibility 0 unless genuinely independent evidence later clears them through an explicitly designed authority.
9. Do not use reference tabs/scorers, decoded Basic Pitch note end as duration, generic next onset as duration, same-pitch reattack as default duration, optimizer/threshold sweeps, or archived V143/Gomyway logic.
10. Update this checkpoint immediately after any authoritative runtime-control verification, same-host dispatch canary result, or material engineering change.

The archived V143/Gomyway pipeline remains out of scope.