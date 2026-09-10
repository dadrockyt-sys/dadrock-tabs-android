# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-10 19:05 America/Toronto
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

Fixture on `main`: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`.

- Git blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration ~210.674648526 s
- expected decoded separation WAV SHA-256 `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- frozen structure identity `fnv1a32:2f493225`; canonical length `19653`
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
- asset upload revision `053e1404489b3dc58bf718224fac4b7316de8c93b`
- `5c90dfd2.safetensors`
- SHA-256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- legacy fallback is not primary

## DURATION AUTHORITY — UNCHANGED / PAUSED

V2 remains authoritative:
- `scripts/songsterr-fresh/estimate_selected_pitch_releases.py`
- contract `songsterr-fresh-cpu-spectral-release-evidence-v2`
- duration-free input required; non-null upstream `durationSeconds` / `sourceEnd` rejected
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
- representative historical inventories: 1,138/1,139 notes with 1,137 exact MIDI/start common matches; all 84 fallback-resolved common events stayed stable
- representative results: 1,138-note environment V2 577/561 → V3 661/477; 1,139-note environment V2 577/562 → V3 661/478
- these counts are descriptive only and must never become acceptance constants

Do not mutate audited V2 while V3 remains under evaluation. Duration-rule research stays paused until the upstream model-evidence execution policy is implemented and validated.

## DEMUCS REPRODUCIBILITY EVIDENCE — AUTHORITATIVE SUMMARY

Same-run reproducibility is green on one hosted runner:
- run `34435154554`, job `102738562141`, head `b0b8595a28304df64bc5804e8ce472428652e3f4`, success
- pass A/B WAV SHA both `4227a41f58817d32e9e122857c924c486afdc1e411a0a173bec2dfcc0c7b6b81`
- pass A/B decoded PCM SHA both `cf07e142fccf92329e69744a2c2fa886d7d7cdccce0b57763fe8d3ea8d984ba2`
- exact sample equality; MAE/RMSE/max all zero
- this proves repeated determinism within that runner/runtime only

Uncontrolled cross-run provenance confirmed variation:
- run `34436134514`, aggregate job `102742547664`, artifact `10136341469`
- three independent hosted observations produced three environment-dependent exact outcomes across AMD EPYC 7763 / AMD EPYC 9V74 and AVX2 / AVX512 observations
- image version, CPU model, Torch-reported AVX capability, and region were each ruled out as a complete explanation
- no stem/environment is preferred or more correct

Same-host CPU-dispatch diagnostic established causality:
- corrected run `34438368530`, head `282a85a9645302be6d1e02d1abc2e57b4f9994d2`, success
- `ATEN_CPU_CAPABILITY=avx2` and `ONEDNN_MAX_CPU_ISA=AVX2` each changed exact PCM on the same host
- fixed modes reproduced exactly across two sampled Intel hosts
- dispatch controls are causal numerical variables, not a correctness selector

Strict common-AVX2 cross-host canary rejected byte portability:
- implementation: `record_demucs_common_avx2_provenance.py`, `compare_demucs_common_avx2_cross_host.py`, `.github/workflows/songsterr-fresh-demucs-common-avx2-cross-host-canary.yml`
- authoritative run `34439594582`, aggregate job `102752709333`, success; five independent observations; AMD + Intel
- all hosts verified Torch AVX2 + oneDNN AVX2 before the fixed Demucs pass
- comparator status `CROSS_VENDOR_PCM_VARIATION_OBSERVED`; `allDecodedPcmIdentical: false`; three WAV/PCM hash groups
- conclusion: combined ATen + oneDNN AVX2 caps do not make generic GitHub-hosted Demucs byte/PCM-identical across Intel and AMD
- do not select a preferred vendor, CPU, WAV hash, PCM hash, or output variant; do not continue broad ISA/backend knob sweeps

## CONTROLLED-COMPUTE INVENTORY

Repository/branch inspection found no branch-tracked fresh controlled compute surface:
- strict fresh cross-host canary uses `ubuntu-latest`
- no fresh self-hosted runner label, pinned container/VM definition, dedicated CPU class, or dedicated fresh deployment worker identified
- older Docker/devcontainer and off-branch Modal artifacts belong to other workstreams and remain untouched
- GitHub connection does not expose registered Actions-runner administration inventory, so this does not prove no external self-hosted runner exists; it establishes only that no suitable controlled surface is branch-tracked or identifiable from accessible fresh infrastructure

## UPSTREAM EXECUTION POLICY — POLICY B SELECTED 2026-09-10

The execution-policy fork is now explicitly resolved in favor of **Policy B: permit bounded upstream numerical variation, and admit model evidence only through reference-blind, fail-closed downstream invariants**.

Reason for the decision:
- generic `ubuntu-latest` is not byte-reproducible for the fixed Demucs contract across observed hosted CPU classes;
- the documented common-AVX2 controls are insufficient cross-vendor;
- no branch-tracked pinned compute surface is available to implement Policy A without inventing new infrastructure;
- exact hosted WAV/PCM hashes therefore remain provenance/audit diagnostics, not admission criteria.

Hard policy rules:
- never choose a canonical vendor, CPU model, runner image, WAV hash, PCM hash, or model output because it looks better downstream;
- no reference tab, archived scorer, professional scorer, or downstream agreement objective may define the variation bound;
- acceptance must be pairwise/reference-blind or based on independently justified representation semantics, not equality to one blessed host;
- missing/invalid comparison evidence fails closed;
- thresholds may be introduced only when justified by the model/output representation or measured reproducibility evidence, never by arbitrary tuning;
- `modelValidationComplete` stays false until this policy is implemented, tested, and demonstrated on independent runs.

### Existing fail-closed guards inherited by Policy B

Inspection of the current fresh model-note boundary confirms these already exist and must remain intact:
- `transcribe_isolated_guitar_basic_pitch.py` validates model event shape, finite starts/ends/confidences, requested MIDI range, valid temporal ordering, deterministic sorted IDs, and records a content note-inference identity; decoded note-off remains diagnostic only.
- `build_isolated_polyphonic_note_evidence.mjs` requires the frozen reference-blind context, accepted structure, Basic Pitch contract/version/role, model provenance, valid SHA-256 inference identity, event-count identity match, finite values, confidence in [0,1], playable MIDI 40–88, onsets inside frozen structure, and diagnostic end strictly after start. It forces `sourceEnd`, `durationSeconds`, and `durationConfidence` to null.
- `run_model_note_evidence_pipeline_canary.mjs` requires structure identity match, verified/reference-blind adapter provenance, model invocation, no V143 boundary violation, and validation pending at entry; it verifies pitch-resolved model events exist while `completeTabEligibleEventCount` remains 0 and delivery remains blocked.

These are necessary structural/provenance guards but are **not sufficient** to complete model validation. Policy B still needs a cross-run semantic-variation admission contract.

### Policy B measurement layer — implemented and green

The first cross-run layer is deliberately **measurement-only**; it does not define or apply an acceptance tolerance.

Implementation:
- comparator `scripts/songsterr-fresh/compare_basic_pitch_cross_run_evidence.py`
- contract `songsterr-fresh-basic-pitch-cross-run-variation-measurement-v1`
- dedicated CI `.github/workflows/songsterr-fresh-model-evidence-variation-tests.yml`
- implementation commit `aae62eba938814a9d38dcf08f39cfdfa0456b4d9`
- workflow commit `ea1283f549e137b2a3630636877479f49b4da9b2`
- green workflow run `34539883074`, job `103079908440`; compile + reference-blind/fail-closed self-test both passed

Contract behavior:
- compares adapted `songsterr-fresh-isolated-polyphonic-note-evidence-v1` artifacts, not raw sequential Basic Pitch note IDs;
- preserves `songsterr-fresh-basic-pitch-note-identity-v1` unchanged as same-inference exact integrity identity; cross-run exact SHA equality is diagnostic only;
- uses `(nearestStructureSlot, selectedMidi)` as the semantic comparison key, reusing the frozen structure's deterministic projected slot without inventing an onset tolerance;
- duplicate events within one semantic key are paired deterministically after sorting by source start/confidence/diagnostic end;
- canonicalizes validated inputs by content digest so reversing CLI A/B order yields the same report;
- measures event/key inventory drift, MIDI histogram drift, paired source-start deltas, paired confidence deltas, and diagnostic-only model-end deltas;
- malformed/incomparable inputs fail closed for contract/version/role/reference-blind/frozen-structure mismatch, structure identity mismatch, model-setting mismatch, source-audio mismatch, unsafe provenance, non-finite event values, unsupported MIDI, candidate inconsistency, exact inference-identity inconsistency, or non-null duration leakage;
- self-tests cover exact-copy zero variation, A/B swap invariance, onset/confidence perturbation, extra-event inventory drift, structure-slot drift, unsafe provenance, non-finite values, unsupported MIDI, duration leakage, and structure/source/model mismatch;
- output explicitly records `thresholdsApplied: false`, `admissionDecisionMade: false`, `modelValidationComplete: false`, `mayAdvanceDelivery: false`, and `durationAuthorityChanged: false`.

The measurement contract being green does **not** validate model evidence. It only provides a safe way to collect independent-run reproducibility evidence for a future bounded-variation admission decision.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true` yet.

Blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain **0**. V2 remains authoritative. V3 remains candidate-only. Basic Pitch output is not ground truth. No reference scorer/tab/archived logic. No decoded BP end as duration. No generic next-onset duration. No same-pitch reattack default duration. No threshold sweep. No acceptance promotion from self-consistency or downstream agreement alone.

## NEXT ENGINEERING STEPS

1. Inspect the existing fresh model-guitar / model-note canary and reuse its fixed Demucs + Basic Pitch path to produce at least two independent adapted evidence artifacts under the same source, frozen structure, model settings, and pinned asset contract. Do not rerun the completed common-AVX2 portability experiment.
2. Run `compare_basic_pitch_cross_run_evidence.py` over those independent adapted artifacts and retain the measurement report plus exact hashes/provenance as diagnostics.
3. Confirm the measurement path remains argument-order invariant and that any inventory/slot/onset/confidence differences are reported rather than normalized away.
4. Determine whether any onset/confidence tolerance can be justified from independent-run evidence and/or Basic Pitch representation semantics. If no defensible bound exists, keep admission blocked rather than inventing one.
5. Only after a bounded-variation admission contract is justified, implemented, tested, and independently demonstrated may `modelValidationComplete` be reconsidered. Duration research remains paused until then.
6. Update this checkpoint after each material implementation or validation finding.

The archived V143/Gomyway pipeline remains out of scope unless the user explicitly asks to resume it.