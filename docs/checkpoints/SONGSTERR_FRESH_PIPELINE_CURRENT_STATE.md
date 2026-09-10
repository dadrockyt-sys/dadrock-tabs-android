# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-10 01:15 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the only canonical fresh-chat checkpoint for this workstream. Earlier verbose diagnostic history remains available in Git history; this file intentionally keeps the current authoritative state, hard boundaries, latest reproducibility evidence, and next actions compact.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference-based correction, professional/reference scorer logic, training/fine-tuning, or broad optimizer sweeps unless explicitly requested.
- The fixture filename containing `gomyway` authorizes that exact audio fixture only; it does not authorize the archived pipeline.
- Fresh reference-blind source-separation/model/DSP diagnostics are allowed only while preserving fail-closed contracts.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP execution stays under `scripts/songsterr-fresh/`.
- Frozen structure precedes note inference and cannot be rewritten downstream.
- Never silently change/drop detected MIDI/event identity. Cross-run identity uses stable content identity (`MIDI` + exact source start and bound inference identity where applicable), never raw sequential Basic Pitch index alone.
- Preserve `/ai-tab`: audio upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.

## AUTHORIZED FIXTURE AND FROZEN STRUCTURE

Fixture on `main`:
`public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`

- Git blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration ~210.674648526 s
- expected decoded separation WAV SHA-256 `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`

Frozen structure:
- identity `fnv1a32:2f493225`; canonical length `19653`
- 4/4, straight feel, pickup / first downbeat ~0.65016 s
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

## MODEL PATH AND FIXED DEMUCS CONTRACT UNDER STUDY

Architecture remains:
frozen full-mixture structure → Demucs guitar isolation → Basic Pitch pitch/onset inference → duration-free model evidence boundary → dedicated release authority.

Decoded Basic Pitch note-off remains diagnostic only. `MODEL_EVIDENCE_VALIDATION_PENDING` independently blocks customer delivery.

Pinned core where applicable:
- numpy 1.26.4
- torch 2.14.0
- huggingface-hub 1.30.0
- safetensors 0.8.0
- sphn 0.2.1
- demucs 4.1.0
- basic-pitch 0.4.0 where explicitly invoked
- librosa 0.11.0 where release diagnostics require it
- soundfile 0.13.1
- tflite-runtime 2.14.0 where Basic Pitch is invoked
- OMP/MKL/OpenBLAS/NumExpr threads = 1; `PYTHONHASHSEED=0`

Fixed Demucs settings:
- model `htdemucs_6s`
- device CPU
- shifts 0
- overlap 0.25
- segment 7 s

Pinned model asset authority:
- contract `songsterr-fresh-demucs-model-asset-v2`
- HF repo `adefossez/HTDemucs-6s`
- pinned revision `3c5ee475be622df764938de97e4281a7b07ffa58`
- asset upload revision `053e1404489b3dc58bf718224fac4b7316de8c93`
- `5c90dfd2.safetensors`
- SHA-256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- legacy fallback is not primary

## DURATION AUTHORITY — UNCHANGED

V2 remains authoritative:
- script `scripts/songsterr-fresh/estimate_selected_pitch_releases.py`
- contract `songsterr-fresh-cpu-spectral-release-evidence-v2`
- duration-free input required
- non-null upstream `durationSeconds` / `sourceEnd` rejected
- decoded Basic Pitch note-off never becomes duration
- generic next onset never becomes duration
- same-pitch reattack is a censor/search boundary only
- unresolved stays unresolved without observed release
- fixed V2: hop 512; sustained-low frames 5; min duration 0.07 s; max search 4.0 s; onset above floor >=12 dB; drop from onset >=18 dB; floor margin >=6 dB
- resolved method `selected-pitch-sustained-spectral-decay`

V3 remains green/repeated but candidate-only:
- `scripts/songsterr-fresh/estimate_selected_pitch_releases_v3.py`
- contract `songsterr-fresh-spectral-activation-release-evidence-v3`
- V2 runs first unchanged; V2-resolved events never change
- fallback only for exact V2 reason `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
- fixed activation + CQT rule only; no sweep/tuning
- hosted inventories historically 1,138/1,139 notes with 1,137 exact MIDI/start common matches
- all 84 fallback-resolved events stayed stable in compared historical variants
- representative results: 1,138-note environment V2 577/561 → V3 661/477; 1,139-note environment V2 577/562 → V3 661/478
- these counts are descriptive only and must never become acceptance constants

Do not mutate audited V2 while V3 remains under evaluation. Duration-rule research is paused while upstream Demucs reproducibility is being isolated.

## AUTHORITATIVE SAME-RUN DEMUCS REPRODUCIBILITY — GREEN

Run `34435154554`, job `102738562141`, head `b0b8595a28304df64bc5804e8ce472428652e3f4`, success.
Artifact `10136054300`, digest `sha256:a694ecb4da7ec5f34cbaf9e61833871f81b806ec87b93b18f9392a9cece97a51`.

- pass A/B WAV SHA both `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- pass A/B decoded float32 PCM SHA both `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2`
- exact sample equality; 0 / 18,581,504 differing values; MAE/RMSE/max all zero
- host AMD EPYC 7763, Torch AVX2, eastus, image `20260907.300.1`

Interpretation: deterministic for repeated passes within that runner/runtime only.

## AUTHORITATIVE UNCONTROLLED CROSS-RUN DEMUCS PROVENANCE — VARIATION CONFIRMED

Run `34436134514`, aggregate job `102742547664`, artifact `10136341469`, digest `sha256:c8481becb4ebb5444e0b0b2e50bcf7ecf3273b84ed03b9d0b421d3557722c69e`.

| Sample | Region | Image | CPU | Native Torch cap | WAV SHA | PCM SHA |
| --- | --- | --- | --- | --- | --- | --- |
| a | eastus | `20260831.293.1` | AMD EPYC 7763 | AVX2 | `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81` | `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2` |
| b | northcentralus | `20260831.293.1` | AMD EPYC 9V74 | AVX512 | `0d9339dfedd13ee4d2d7f1a1262363f8a756dce4fc1168182208b0ed431cec12` | `0bd756ad4362f150fd6997835c9a91791963fe30722d4ec4d41283a41ae70219` |
| c | eastus2 | `20260907.300.1` | AMD EPYC 9V74 | AVX2 | `5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33` | `6d3ac44cd3f0156253ff7b820b72f5eda8d59eb8c60f8abd68a87c0598ec4987` |

This ruled out image version alone, CPU model alone, Torch-reported AVX capability alone, and region alone as complete explanations. No stem/environment is preferred or more correct.

## AUTHORITATIVE SAME-HOST CPU-DISPATCH DIAGNOSTIC — GREEN; DISPATCH IS CAUSAL

Comparator:
- `scripts/songsterr-fresh/compare_demucs_same_host_cpu_dispatch.py`
- commit `cd00024da042f9da64c2c2fe0e0a4c9562cc40e9`
- contract `songsterr-fresh-demucs-same-host-cpu-dispatch-comparison-v1`

Original run `34436904125` at head `d11042c8c606de51ba8976e3d3f6651ab79f7695` is **NON-AUTHORITATIVE / SUPERSEDED** because its oneDNN probe changed 16→32 channels and then reused the module. Fix commit `282a85a9645302be6d1e02d1abc2e57b4f9994d2` changed the diagnostic convolution to 16→16.

Corrected run `34438368530`, head `282a85a9645302be6d1e02d1abc2e57b4f9994d2`: **success**.

Hosts:
- a job `102748071040`: Intel Xeon Platinum 8573C, westus3, native AVX512
- b job `102748071184`: AMD EPYC 7763, westcentralus, native AVX2; provenance-only/gated
- c job `102748071203`: Intel Xeon 6973P-C, centralus, native AVX512
- aggregate `102750245161`: success; 3 probes; 2 AVX512 comparisons

Artifacts:
- a `10137259557`, digest `sha256:e9bea047f0239bbc5f27acd376f3596ab1800b9f891a5449f81071d5b905adab`
- b `10137038974`, digest `sha256:730d4123e5e267d9658c5bdda76903cd7119ecf2a100dd07c02aa826445bdaea`
- c `10137259399`, digest `sha256:5aa0fad548ac7ae76979b09bdbd0d30c5dfb7d0d1d23fd64d1f8305440f1f3ef`
- summary `10137262672`, digest `sha256:61c5d9c64e973da080c82adabd334d5ec1360ae57064415fd5c5cc9866c879a3`

Both Intel AVX512 hosts verified `ATEN_CPU_CAPABILITY=avx2` → Torch AVX2 and `ONEDNN_MAX_CPU_ISA=AVX2` → oneDNN AVX2.

Exact four-way result was byte/PCM identical across the two different Intel CPU models and regions:

| Mode | WAV SHA-256 | PCM SHA-256 |
| --- | --- | --- |
| native | `c303f0a0d99f94e2bddedebd0679cc5034aa9505c350cc28a5200d4c419637af` | `0b92b9b28001a6cbc7bdb15da2324e4c2d5ea62cf76c29bd2ba5192b5d2f75fa` |
| ATen AVX2 only | `6692d15e3c97ab8ef7c501c345710a6cfb58169a07e84a004401f64e28478ab2` | `fdc3f6fa4e9b1e442b40966606243571eb3766c8768b11ef52955eec178f531a` |
| oneDNN AVX2 only | `9d95261fdda6eaed574010f6474adda2988f50dc8e363b5f91a201bf42948b52` | `2de9060889087b0e39de86f03c0547d41e125c374bf7111afe45266321509ede` |
| combined ATen + oneDNN AVX2 | `db6e52b012232aae18419de9d2efdccf3e8adf92ee6524ffe52573973d164ea0` | `62bf61909fa52529e2c1cac980a02d546910f5daed34b117769283ec3df4a49a` |

Identical per-host native deltas:
- native vs ATen cap: 18,202 / 18,581,504 differing PCM values; RMSE `9.551447402342991e-07`; max abs `3.0517578125e-05`
- native vs oneDNN cap: 45,076 differing; RMSE `1.5030807698819657e-06`; max abs `3.0517578125e-05`
- native vs combined cap: 44,322 differing; RMSE `1.4904565095481278e-06`; max abs `3.0517578125e-05`

Authoritative interpretation:
- ATen CPU dispatch and oneDNN CPU dispatch are **causal numerical variables** for this fixed Demucs execution because each documented control changes exact PCM on the same host.
- Every fixed mode reproduced exactly across the two sampled Intel hosts.
- This did not establish Intel↔AMD convergence under a common cap.
- Native Intel reproduced historical `c303f0a0...`; descriptive only, never a correctness or preference signal.

## CPU-DISPATCH CONTROL VERIFICATION

Upstream-supported diagnostic controls used:
- `ATEN_CPU_CAPABILITY=avx2`
- `ONEDNN_MAX_CPU_ISA=AVX2`

oneDNN verbose verifies the effective ISA. Intel oneMKL ISA controls are not being used as a cross-vendor portability mechanism. These controls remain diagnostic only; no production execution contract is selected.

## AUTHORITATIVE STRICT COMMON-AVX2 CROSS-HOST CANARY — CROSS-VENDOR VARIATION CONFIRMED

Purpose: test one fixed portability hypothesis only: constrain both CPU-dispatch surfaces already proven causal and ask whether exact Demucs PCM converges across independent hosted CPU classes. No downstream audio/note agreement was used to choose a result.

Dedicated implementation:
- `scripts/songsterr-fresh/record_demucs_common_avx2_provenance.py`
  - commit `c560bbbf3b254a6b4d20a1da03fa1259a2c18b7d`
  - contract `songsterr-fresh-demucs-common-avx2-provenance-v1`
- `scripts/songsterr-fresh/compare_demucs_common_avx2_cross_host.py`
  - commit `9dcb9cef95798599d2db3f243a183ff7a60b1ee5`
  - contract `songsterr-fresh-demucs-common-avx2-cross-host-comparison-v1`
- workflow `.github/workflows/songsterr-fresh-demucs-common-avx2-cross-host-canary.yml`
  - strict wiring head `0d6fc7b90d2d673d2d4536bbbb87bd7cdda968c3`

Authoritative run:
- run `34439594582`: **success**
- aggregate job `102752709333`: **success**
- aggregate artifact `10137556244`
- aggregate artifact digest `sha256:4551d7e384786bc366168b2ba3368c2f9daa63053bca7eae2c01e4f7a145b02f`
- five independent observations
- vendors observed: AMD + Intel
- CPU models observed: AMD EPYC 7763, AMD EPYC 9V45, AMD EPYC 9V74, Intel Xeon 6973P-C
- every host verified effective Torch AVX2 and oneDNN AVX2 before the fixed Demucs pass
- exact pinned fixture, decoded input SHA, model asset, dependency versions, model/settings, thread limits, and diagnostic guards were held fixed
- comparator status: `CROSS_VENDOR_PCM_VARIATION_OBSERVED`
- `allDecodedPcmIdentical: false`
- distinct WAV SHA groups: 3
- distinct decoded PCM SHA groups: 3

Exact hash groups:

| Samples | WAV SHA-256 | PCM SHA-256 |
| --- | --- | --- |
| b, e | `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81` | `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2` |
| a, c | `5b3e7c6feb153ba427303d5f2688cf3442faa74bb4e98ce298ac426824c8db33` | `6d3ac44cd3f0156253ff7b820b72f5eda8d59eb8c60f8abd68a87c0598ec4987` |
| d | `db6e52b012232aae18419de9d2efdccf3e8adf92ee6524ffe52573973d164ea0` | `62bf61909fa52529e2c1cac980a02d546910f5daed34b117769283ec3df4a49a` |

Per-host artifacts:
- a `10137543653`, digest `sha256:86e477e3664db81cb17158876611b4068d2b1f38c17839cdd9c47dd4e3c5fe1f`
- b `10137543684`, digest `sha256:7916fe1254f93eeb765f9a1de644c0277acb0ae71e15c07aa9e6eabe5e8730ed`
- c `10137537337`, digest `sha256:27357b933fe8ae387099498a8677af7b86e27fa2cbb34b7844fe3c3530d86eeb`
- d `10137540776`, digest `sha256:20e4301ae1513bc193f0825932d31dfb0f512e64200fe1293eaf5acaece5ea96`
- e `10137547512`, digest `sha256:851d7424dfecc435b6cd504ca1f1e712263b03d8223da8071f6eb5f2a2815b4c`

Additional bounded evidence:
- samples b and e were independent AMD EPYC 7763 hosts and reproduced the same `4227a41f...` WAV / `cf07e142...` PCM result despite different hosted runner-image observations in the broader test history.
- the earlier preliminary run `34439336421` sampled only AMD EPYC 7763 hosts and was therefore cross-vendor-inconclusive; it is supporting repeatability evidence only, not the portability answer.

Authoritative interpretation:
- **Reject the hypothesis that combined `ATEN_CPU_CAPABILITY=avx2` + `ONEDNN_MAX_CPU_ISA=AVX2` makes generic GitHub-hosted CPU execution byte/PCM-identical across Intel and AMD.**
- The documented dispatch controls are real causal variables, but they are insufficient to normalize the remaining CPU/microarchitecture/runtime numerical boundary.
- Do not select a preferred vendor, CPU, WAV hash, or PCM hash from downstream agreement or perceived audio quality.
- Do not promote either AVX2 cap to Production from these diagnostics.
- Do not continue with broad ISA/backend knob sweeps.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true`.

Blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**. V2 remains authoritative. V3 remains candidate-only. Basic Pitch output is not ground truth. No reference scorer/tab/archived logic. No decoded BP end as duration. No generic next-onset duration. No same-pitch reattack default duration. No threshold sweep. No acceptance promotion from self-consistency or downstream agreement alone.

## FRESH-CHAT NEXT ENGINEERING STEPS

Start here in the next chat. Do not repeat the completed common-AVX2 portability experiment unless a specific new reason emerges.

1. **Inspect the repository and available CI/infrastructure for an already-existing controlled compute path** suitable for Demucs: self-hosted runner labels, pinned container/VM definitions, dedicated CPU class, deployment worker, or other execution surface where the CPU/runtime boundary can actually be fixed. This is inspection only first; do not change Production.
2. If a controlled execution surface already exists, design one **reference-blind reproducibility canary** for that exact compute contract: exact authorized fixture/input/model/dependencies/Demucs settings, at least two independent job/process lifecycles, exact WAV + decoded PCM hashes, environment provenance, and all current hard guards. No Basic Pitch, duration logic, scorer, reference tab, downstream-agreement objective, or customer acceptance in this canary.
3. If no controllable CPU/runtime surface exists, document that generic `ubuntu-latest` is not a byte-reproducible Demucs execution contract for this model. Then narrow the engineering decision to either (a) introducing a genuinely pinned compute class for model execution or (b) explicitly accepting bounded upstream numerical variation and validating downstream invariants without ever selecting a vendor/hash by agreement. Do not silently choose between these policies.
4. Do **not** spend the next step on more `ATEN_CPU_CAPABILITY` / oneDNN ISA combinations, oneMKL controls, backend toggles, thread-count sweeps, or optimizer sweeps. The current evidence already shows that the two documented CPU-dispatch caps are insufficient cross-vendor.
5. Keep duration-rule research paused until the upstream Demucs execution boundary is either reproducibly pinned or an explicit bounded-variation policy is defined. V2 remains the authoritative duration source during this pause; V3 remains candidate-only.
6. Once the upstream execution policy is resolved, continue **model-evidence validation first**, still reference-blind and preserving stable event identity. Only after that should V3 duration evidence be reconsidered for promotion against independently justified evidence; never use decoded Basic Pitch note-off, generic next onset, or same-pitch reattack as default duration.
7. Preserve throughout: frozen structure, `/ai-tab` flow, stable cross-run event identity, both blockers, `modelValidationComplete: false`, customer eligibility 0, V2 authority, V3 candidate-only status, and all fail-closed guards.
8. Keep this checkpoint updated after each material finding or branch-only implementation change.

The archived V143/Gomyway pipeline remains out of scope unless the user explicitly asks to resume it.