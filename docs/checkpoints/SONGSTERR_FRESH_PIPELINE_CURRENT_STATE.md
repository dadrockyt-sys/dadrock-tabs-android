# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-10 00:45 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the only canonical fresh-chat checkpoint for this workstream. Historical verbose detail is retained in Git history; this file intentionally records current authoritative evidence, hard boundaries, active diagnostics, and next actions.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference-based correction, professional/reference scorer logic, training/fine-tuning, or broad optimizer sweeps unless explicitly requested.
- The exact fixture filename containing `gomyway` authorizes that audio fixture only; it does not authorize the archived pipeline.
- Fresh reference-blind source-separation/model/DSP diagnostics are allowed only while preserving fail-closed contracts.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP execution stays under `scripts/songsterr-fresh/`.
- Frozen structure precedes note inference and cannot be rewritten downstream.
- Never silently change/drop detected MIDI/event identity. Cross-run identity uses stable content identity (`MIDI` + exact source start and bound inference identity where applicable), never raw sequential Basic Pitch index alone.
- Preserve `/ai-tab`: audio upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.

## EXACT AUTHORIZED FIXTURE

`main:public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`

- Git blob SHA: `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration: ~210.674648526 s
- expected decoded separation WAV SHA-256: `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`

Canaries fetch the raw fixture from `main`, verify the Git blob, decode it, and fail closed if the decoded separation SHA changes.

## FROZEN STRUCTURE

- identity `fnv1a32:2f493225`; canonical length `19653`
- ~210.67465 s; 4/4; straight feel; pickup / first downbeat ~0.65016 s
- 115 measures; 113 measure-local tempo segments
- beat-grid MAE ~7.14 ms; RMSE ~10.63 ms; max ~58.05 ms; accepted true
- historical structure canary run `34192662439`, job `101953726302`, commit `2a598f0f38d755faf0cd3d46543221253f1c8997`, artifact `10042777518`, digest `sha256:5ff3ce36f559bcc02efcc985a1fa06966576da0445896326e9408ada955e9b6f`

## GUARDED CPU BASELINE

Analyzer `scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`; contract `songsterr-fresh-cpu-note-evidence-v4`.

- 492 onsets; 1,130 candidates
- 139 local unambiguous selections; 353 ambiguous; 0 no-candidate
- MIDI 40 in 97/139 selections
- role relevance unresolved; polyphony unresolved; instrument isolation none
- customer eligible 0
- latest regression run `34309259214`, job `102332311684`, head `54d9e4792d8255d56f6aec82977ac083b9c2bae4`, artifact `10087798684`, digest `sha256:a1dbe85348f66847045e616d9726ffce986a82e995de0817fb20159e6fbf9d08`, 97/97 tests, CPU duration evidence 103 resolved / 36 unresolved

## MODEL PATH AND PINS

Architecture: frozen full-mixture structure → Demucs 4.1.0 `htdemucs_6s` guitar isolation → Basic Pitch 0.4.0 polyphonic pitch/onset inference → duration-free model evidence boundary → dedicated release stage as sole active duration authority. Decoded Basic Pitch note-off is diagnostic only. `MODEL_EVIDENCE_VALIDATION_PENDING` independently blocks customer delivery.

Pinned core where applicable: numpy 1.26.4; torch 2.14.0; huggingface-hub 1.30.0; safetensors 0.8.0; sphn 0.2.1; demucs 4.1.0; basic-pitch 0.4.0; librosa 0.11.0; soundfile 0.13.1; tflite-runtime 2.14.0. OMP/MKL/OpenBLAS/NumExpr threads = 1; `PYTHONHASHSEED=0`.

Fixed Demucs settings: `htdemucs_6s`, CPU, shifts 0, overlap 0.25, segment 7.

Pinned Demucs asset authority:
- verifier contract `songsterr-fresh-demucs-model-asset-v2`
- HF repo `adefossez/HTDemucs-6s`
- pinned revision `3c5ee475be622df764938de97e4281a7b07ffa58`
- asset upload revision `053e1404489b3dc58bf718224fac4b7316de8c93`
- `5c90dfd2.safetensors`
- SHA-256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- legacy fallback is not primary

## ACTIVE V2 DURATION AUTHORITY — UNCHANGED

`script: scripts/songsterr-fresh/estimate_selected_pitch_releases.py`; contract `songsterr-fresh-cpu-spectral-release-evidence-v2`.

Hard rules: duration-free input; reject non-null upstream `durationSeconds`/`sourceEnd`; model/GPU upstream denied unless explicitly authorized with `--allow-model-upstream`; decoded Basic Pitch note-off never becomes duration; generic next onset never becomes duration; same-pitch reattack is censor/search boundary only; unresolved stays unresolved without observed release.

Fixed V2: hop 512; sustained-low frames 5; min duration 0.07 s; max search 4.0 s; onset above floor >=12 dB; drop from onset >=18 dB; floor margin >=6 dB. Resolved method `selected-pitch-sustained-spectral-decay`.

Do not mutate this audited V2 while V3 is being evaluated.

## V3 RELEASE FALLBACK — GREEN, REPEATED, NON-AUTHORITATIVE

Prototype `scripts/songsterr-fresh/estimate_selected_pitch_releases_v3.py`; contract `songsterr-fresh-spectral-activation-release-evidence-v3`.

- V2 runs first unchanged; V2-resolved events never change.
- Fallback only for exact V2 reason `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`.
- Fixed activation + CQT rule only; no sweep/tuning.
- Generic next onset, reattack timestamp, and decoded BP note-off never become duration.
- Model validation false; customer eligibility zero.
- Historical hosted inventories 1,138/1,139 model notes; 1,137 exact MIDI/start common matches; all 84 fallback-resolved events remained stable across compared historical variants.
- Representative results: 1,138 env V2 577/561, V3 661/477; 1,139 env V2 577/562, V3 661/478.

These counts are descriptive and must never become acceptance constants.

## AUTHORITATIVE SAME-RUN DEMUCS REPRODUCIBILITY — GREEN

Run `34435154554`, job `102738562141`, head `b0b8595a28304df64bc5804e8ce472428652e3f4`, success; artifact `10136054300`, digest `sha256:a694ecb4da7ec5f34cbaf9e61833871f81b806ec87b93b18f9392a9cece97a51`.

- pass A/B WAV SHA both `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- pass A/B float32 PCM SHA both `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2`
- exact sample equality; 0 / 18,581,504 differing PCM values; MAE/RMSE/max 0.0
- RMS `0.05302134928309948`; 44,100 Hz; shape 9,290,752 × 2
- AMD EPYC 7763; Torch capability AVX2; eastus; runner image `20260907.300.1`, Ubuntu 24.04.5
- platform `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`; Torch `2.14.0+cu130`; intra-op 1 / inter-op 4; CUDA unavailable

Interpretation: Demucs is byte/PCM deterministic for repeated passes within this one runner/runtime. This does not prove equality across independent hosted environments.

## AUTHORITATIVE CROSS-RUN DEMUCS PROVENANCE — VARIATION CONFIRMED

Implementation:
- `scripts/songsterr-fresh/record_demucs_cross_run_provenance.py`, commit `41b57e29b26d36a4d3697efd040d2930e4840b87`, contract `songsterr-fresh-demucs-cross-run-provenance-v1`
- `scripts/songsterr-fresh/compare_demucs_cross_run_provenance.py`, commit `2e714380cd0436a220d8101fa012369660bed8d5`, contract `songsterr-fresh-demucs-cross-run-comparison-v1`
- workflow `.github/workflows/songsterr-fresh-demucs-cross-run-provenance-canary.yml`, head `fffece201a31d8c56dc49a7e6637df779debc170`

Authoritative run `34436134514`: success; aggregate job `102742547664`; aggregate artifact `10136341469`, digest `sha256:c8481becb4ebb5444e0b0b2e50bcf7ecf3273b84ed03b9d0b421d3557722c69e`.

All three independent jobs matched exact source/input/model asset/top-level pins/fixed Demucs settings/Python 3.10.21/Torch `2.14.0+cu130`/kernel+glibc/thread settings/output geometry, yet produced three distinct file and PCM hashes:

| Sample | Job | Region | Image | CPU | Torch cap | WAV SHA | PCM SHA |
| --- | --- | --- | --- | --- | --- | --- | --- |
| a | `102741473454` | eastus | `20260831.293.1` | EPYC 7763 | AVX2 | `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81` | `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2` |
| b | `102741473233` | northcentralus | `20260831.293.1` | EPYC 9V74 | AVX512 | `0d9339dfedd13ee4d2d7f1a1262363f8a756dce4fc1168182208b0ed431cec12` | `0bd756ad4362f150fd6997835c9a91791963fe30722d4ec4d41283a41ae70219` |
| c | `102741473405` | eastus2 | `20260907.300.1` | EPYC 9V74 | AVX2 | `5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33` | `6d3ac44cd3f0156253ff7b820b72f5eda8d59eb8c60f8abd68a87c0598ec4987` |

Artifacts: a `10136333426` digest `sha256:1c4e4caa9b0555ca3d535120c95bf5fb01198dd2b9fbf6c7a34a75b12d227a31`; b `10136318426` digest `sha256:047c77e6cd9980c86fdf88badc032dbb7fdc789dbb84b66c7991721f6d3d2d5e`; c `10136334343` digest `sha256:34220b9a67106cd3158661b2a29547f06634be2c72f15d94d203effc94540f74`.

Evidence rules out runner image alone, CPU model alone, Torch-reported AVX capability alone, and region alone as complete explanations. Effective hosted CPU/runtime dispatch is part of the remaining boundary, but no single cause is proven. No stem or environment is preferred or more correct.

Historical comparison: corrected CQT run `34432234675` gave `4227a41f...`; corrected STFT `34433150157` gave `c303f0a0...`; controlled CQT↔STFT `34434013368` gave `5b3e7c6f...`. Historical downstream BP/release drift remains descriptive only and cannot select an environment or stem.

## CPU-DISPATCH CONTROL VERIFICATION

Authoritative upstream runtime controls were checked before changing diagnostic execution:
- PyTorch documents `ATEN_CPU_CAPABILITY=avx2` to cap ATen CPU dispatch and recognizes AVX2/AVX512.
- oneDNN documents `ONEDNN_MAX_CPU_ISA=AVX2` as a CPU dispatcher upper bound; oneDNN verbose can expose effective `cpu,isa`.
- Intel oneMKL `MKL_ENABLE_INSTRUCTIONS` is not applicable as a portability control on these AMD EPYC hosts and is not used.

These controls are diagnostic only and are not production settings.

## SAME-HOST CPU-DISPATCH DIAGNOSTIC — REPLACEMENT RUN ACTIVE

Comparator:
- `scripts/songsterr-fresh/compare_demucs_same_host_cpu_dispatch.py`
- commit `cd00024da042f9da64c2c2fe0e0a4c9562cc40e9`
- contract `songsterr-fresh-demucs-same-host-cpu-dispatch-comparison-v1`

Workflow: `.github/workflows/songsterr-fresh-demucs-same-host-cpu-dispatch-canary.yml`.

### Superseded run

- original workflow head `d11042c8c606de51ba8976e3d3f6651ab79f7695`
- run `34436904125`
- **NON-AUTHORITATIVE / SUPERSEDED**
- reason: the oneDNN verbose probe constructed `Conv2d(16, 32, 3)` and then reused it for three loop iterations; after the first iteration the tensor had 32 channels while the module still expected 16, so an eligible host would fail on the second iteration.
- no result from this run may be used as evidence, even if other probe metadata/artifacts exist.
- this diagnostic bug did not affect the authoritative same-run or cross-run canaries, production execution, Basic Pitch, V2/V3, or acceptance state.

### Fix and replacement

- fix commit `282a85a9645302be6d1e02d1abc2e57b4f9994d2`
- both oneDNN probe convolutions now use `Conv2d(16, 16, 3)`, preserving channel count across all three loop iterations while the pad restores spatial geometry.
- replacement workflow run `34438368530`
- replacement head `282a85a9645302be6d1e02d1abc2e57b4f9994d2`
- event push; launched `2026-09-10T04:44:49Z`
- status at this checkpoint: queued; no host capability or comparison result is authoritative yet.

Replacement design remains unchanged:
- three independently assigned hosted probe jobs verify exact fixture/input/dependencies and record native CPU model/Torch capability.
- only a native AVX512 host runs four fixed Demucs passes on the same host in separate processes: native; ATen AVX2 cap; oneDNN AVX2 cap; combined caps.
- ATen cap must verify as AVX2 before Demucs; oneDNN native/capped verbose headers are diagnostic evidence.
- compare file/PCM hashes and numerical deltas only; upload diagnostics, not stem audio.
- no Basic Pitch, V2/V3, note/pitch/duration/sourceEnd mutation, scorer/reference tab, threshold selection/sweep, downstream-agreement objective, acceptance/customer delivery, or archived V143 logic.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**. V2 remains authoritative. V3 remains candidate-only. Basic Pitch output is not ground truth. No reference scorer/tab/archived logic. No decoded BP end as duration. No generic next-onset duration. No same-pitch reattack default duration. No threshold sweep. No acceptance promotion from self-consistency alone.

## NEXT ENGINEERING STEPS

1. Finish replacement same-host CPU-dispatch run `34438368530`; inspect all three probe records and any native-AVX512 four-way comparison.
2. If no AVX512 host is assigned, record only the bounded inconclusive result; do not infer dispatch causality from AVX2-only probes.
3. If an AVX512 host is assigned, use same-host file/PCM hashes and numerical deltas only to determine whether ATen dispatch, oneDNN dispatch, or their combination changes the fixed Demucs result on that host. This addresses numerical causality only, never correctness.
4. Do not promote any CPU cap to production from a single diagnostic. A reproducible execution contract requires explicitly designed repeated independent evidence.
5. Keep duration-rule research paused until upstream Demucs variation is characterized enough to define a reproducible execution contract or explicitly accept bounded numerical variation without downstream-agreement selection.
6. Keep stable cross-run event identity; never use sequential BP index as identity.
7. Preserve both blockers, V2 authority, V3 candidate status, `modelValidationComplete: false`, and customer eligibility 0.
8. Do not use reference tabs/scorers, decoded BP note end as duration, generic next onset as duration, same-pitch reattack as default duration, optimizer/threshold sweeps, or archived V143/Gomyway logic.
9. Update this checkpoint immediately after host capability is known, any same-host comparison result, or material engineering change.

The archived V143/Gomyway pipeline remains out of scope.