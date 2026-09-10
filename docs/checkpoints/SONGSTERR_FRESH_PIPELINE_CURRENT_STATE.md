# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-10 00:58 America/Toronto
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
- AMD EPYC 7763; Torch capability AVX2; eastus; image `20260907.300.1`

Interpretation: deterministic within this runner/runtime only, not proof of independent-run equality.

## AUTHORITATIVE CROSS-RUN DEMUCS PROVENANCE — VARIATION CONFIRMED

Implementation:
- `scripts/songsterr-fresh/record_demucs_cross_run_provenance.py`, commit `41b57e29b26d36a4d3697efd040d2930e4840b87`, contract `songsterr-fresh-demucs-cross-run-provenance-v1`
- `scripts/songsterr-fresh/compare_demucs_cross_run_provenance.py`, commit `2e714380cd0436a220d8101fa012369660bed8d5`, contract `songsterr-fresh-demucs-cross-run-comparison-v1`
- workflow `.github/workflows/songsterr-fresh-demucs-cross-run-provenance-canary.yml`, head `fffece201a31d8c56dc49a7e6637df779debc170`

Run `34436134514`: success; aggregate job `102742547664`; aggregate artifact `10136341469`, digest `sha256:c8481becb4ebb5444e0b0b2e50bcf7ecf3273b84ed03b9d0b421d3557722c69e`.

| Sample | Region | Image | CPU | Torch cap | WAV SHA | PCM SHA |
| --- | --- | --- | --- | --- | --- | --- |
| a | eastus | `20260831.293.1` | EPYC 7763 | AVX2 | `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81` | `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2` |
| b | northcentralus | `20260831.293.1` | EPYC 9V74 | AVX512 | `0d9339dfedd13ee4d2d7f1a1262363f8a756dce4fc1168182208b0ed431cec12` | `0bd756ad4362f150fd6997835c9a91791963fe30722d4ec4d41283a41ae70219` |
| c | eastus2 | `20260907.300.1` | EPYC 9V74 | AVX2 | `5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33` | `6d3ac44cd3f0156253ff7b820b72f5eda8d59eb8c60f8abd68a87c0598ec4987` |

Evidence rules out runner image alone, CPU model alone, Torch-reported AVX capability alone, and region alone as complete explanations. Effective hosted CPU/runtime dispatch is part of the boundary. No stem or environment is preferred or more correct.

Historical hosted stems include `4227a41f...` (corrected CQT), `c303f0a0...` (corrected STFT), and `5b3e7c6f...` (controlled CQT↔STFT). Historical downstream BP/release drift remains descriptive only and cannot select an environment or stem.

## CPU-DISPATCH CONTROL VERIFICATION

- PyTorch documents `ATEN_CPU_CAPABILITY=avx2` and recognizes AVX2/AVX512 dispatch.
- oneDNN documents `ONEDNN_MAX_CPU_ISA=AVX2`; oneDNN verbose exposes effective `cpu,isa`.
- Intel oneMKL ISA control is not used as a cross-vendor portability control.

These are diagnostic controls only, not production settings.

## AUTHORITATIVE SAME-HOST CPU-DISPATCH DIAGNOSTIC — GREEN

Comparator `scripts/songsterr-fresh/compare_demucs_same_host_cpu_dispatch.py`, commit `cd00024da042f9da64c2c2fe0e0a4c9562cc40e9`, contract `songsterr-fresh-demucs-same-host-cpu-dispatch-comparison-v1`.

Workflow `.github/workflows/songsterr-fresh-demucs-same-host-cpu-dispatch-canary.yml`.

### Superseded diagnostic

Original run `34436904125` at head `d11042c8c606de51ba8976e3d3f6651ab79f7695` is **NON-AUTHORITATIVE / SUPERSEDED** because its oneDNN verbose probe reused `Conv2d(16, 32, 3)` across iterations and would fail after the first channel expansion. It did not affect any production, Basic Pitch, V2/V3, or acceptance state.

Fix commit `282a85a9645302be6d1e02d1abc2e57b4f9994d2` changed both diagnostic convolutions to `Conv2d(16, 16, 3)` so repeated iterations preserve channel geometry.

### Authoritative replacement run

Run `34438368530`, head `282a85a9645302be6d1e02d1abc2e57b4f9994d2`, **success**.

Jobs:
- a `102748071040`: Intel Xeon Platinum 8573C, westus3, native Torch AVX512
- b `102748071184`: AMD EPYC 7763, westcentralus, native Torch AVX2; provenance-only as designed
- c `102748071203`: Intel Xeon 6973P-C, centralus, native Torch AVX512
- summary `102750245161`: success, `RESULT_AVAILABLE`, 3 probes, 2 eligible AVX512 hosts, 2 completed comparisons

Artifacts:
- a `10137259557`, digest `sha256:e9bea047f0239bbc5f27acd376f3596ab1800b9f891a5449f81071d5b905adab`
- b `10137038974`, digest `sha256:730d4123e5e267d9658c5bdda76903cd7119ecf2a100dd07c02aa826445bdaea`
- c `10137259399`, digest `sha256:5aa0fad548ac7ae76979b09bdbd0d30c5dfb7d0d1d23fd64d1f8305440f1f3ef`
- summary `10137262672`, digest `sha256:61c5d9c64e973da080c82adabd334d5ec1360ae57064415fd5c5cc9866c879a3`

Both AVX512 hosts verified:
- `ATEN_CPU_CAPABILITY=avx2` makes Torch report AVX2 in a fresh process.
- oneDNN native verbose reported the host-native Intel AVX10.1/AMX path; `ONEDNN_MAX_CPU_ISA=AVX2` reported Intel AVX2.
- exact fixture/input/model asset/dependency pins/Demucs settings were unchanged.

### Exact four-way result — identical across both different Intel AVX512 hosts

| Mode | WAV SHA-256 | PCM SHA-256 |
| --- | --- | --- |
| native | `c303f0a0d99f94e2bddedebd0679cc5034aa9505c350cc28a5200d4c419637af` | `0b92b9b28001a6cbc7bdb15da2324e4c2d5ea62cf76c29bd2ba5192b5d2f75fa` |
| ATen AVX2 cap | `6692d15e3c97ab8ef7c501c345710a6cfb58169a07e84a004401f64e28478ab2` | `fdc3f6fa4e9b1e442b40966606243571eb3766c8768b11ef52955eec178f531a` |
| oneDNN AVX2 cap | `9d95261fdda6eaed574010f6474adda2988f50dc8e363b5f91a201bf42948b52` | `2de9060889087b0e39de86f03c0547d41e125c374bf7111afe45266321509ede` |
| combined ATen + oneDNN AVX2 caps | `db6e52b012232aae18419de9d2efdccf3e8adf92ee6524ffe52573973d164ea0` | `62bf61909fa52529e2c1cac980a02d546910f5daed34b117769283ec3df4a49a` |

On **each** of the two Intel hosts, native vs cap numerical deltas were also identical:
- native vs ATen cap: 18,202 / 18,581,504 PCM values differ; RMSE `9.551447402342991e-07`; max abs `3.0517578125e-05`
- native vs oneDNN cap: 45,076 differ; RMSE `1.5030807698819657e-06`; max abs `3.0517578125e-05`
- native vs combined cap: 44,322 differ; RMSE `1.4904565095481278e-06`; max abs `3.0517578125e-05`

### Authoritative interpretation

What is now positively demonstrated:
- CPU library dispatch **causally changes exact Demucs numerical output on the same physical hosted runner**, because changing only the documented dispatch control changes exact PCM/file hashes.
- ATen-only and oneDNN-only controls each independently alter the result; the combined control yields another distinct deterministic result.
- For this run, every fixed dispatch mode reproduced **byte/PCM exactly across two different Intel AVX512 CPU models in two different Azure regions**.
- The native Intel result exactly reproduces the historical `c303f0a0...` hosted stem, but that is descriptive only and does not make it preferred or correct.

What is **not** yet established:
- no evidence yet shows that the combined AVX2 cap makes AMD and Intel hosts converge to the same PCM.
- no production execution contract has been selected.
- no cap has been shown more accurate than another; downstream Basic Pitch/release agreement may not be used to choose one.
- these tiny numerical deltas are reproducibility evidence only, not musical-quality evidence.

Hard boundaries passed: reference blind; diagnostic only; no Basic Pitch; no V2/V3; no note/pitch/duration/sourceEnd mutation; no scorer/reference tab; no threshold selection/sweep; no downstream-agreement objective; no acceptance/customer delivery; no archived V143 logic.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Current blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**. V2 remains authoritative. V3 remains candidate-only. Basic Pitch output is not ground truth. No reference scorer/tab/archived logic. No decoded BP end as duration. No generic next-onset duration. No same-pitch reattack default duration. No threshold sweep. No acceptance promotion from self-consistency alone.

## NEXT ENGINEERING STEPS

1. Keep duration-rule research paused.
2. Run one narrow **cross-host common-dispatch** diagnostic using only the fixed combined controls `ATEN_CPU_CAPABILITY=avx2` + `ONEDNN_MAX_CPU_ISA=AVX2` on several independent hosted jobs. Each job must verify the exact fixture/input/model asset/settings and record CPU vendor/model, region, image, native capability, capped capability/oneDNN ISA, file SHA and PCM SHA.
3. This is a single fixed portability hypothesis, not a sweep. Do not run Basic Pitch, V2/V3, a scorer, duration logic, or downstream-agreement analysis.
4. The specific question is whether the same combined AVX2 execution contract yields exact PCM across both Intel and AMD hosted CPUs. If all sampled vendors converge, record it as a reproducibility-contract candidate only and require an independent confirmation before any production change.
5. If AMD and Intel remain different under the combined cap, record that the documented dispatch caps are insufficient to normalize the remaining vendor/microarchitecture/runtime boundary; do not choose a vendor by downstream behavior.
6. No production runtime cap may be adopted until explicitly supported by repeated independent cross-vendor evidence and a separate deployment/contract decision.
7. Keep cross-run event identity based on stable content identity, never raw sequential BP index alone.
8. Preserve V2 authority, V3 candidate-only state, both blockers, `modelValidationComplete: false`, and customer eligibility 0.
9. Do not use reference tabs/scorers, decoded BP note end as duration, generic next onset as duration, same-pitch reattack as default duration, optimizer/threshold sweeps, or archived V143/Gomyway logic.
10. Update this checkpoint immediately after the cross-host common-dispatch canary is implemented/launched and after any authoritative result.

The archived V143/Gomyway pipeline remains out of scope.