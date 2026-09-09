# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-09 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the **only canonical fresh-chat checkpoint** for the Songsterr-inspired fresh pipeline. Do not resume archived V143/Gomyway implementation, reference tabs, scorer logic, or historical percentages unless the user explicitly asks.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that goes from uploaded audio to a usable finished tab without a mandatory human correction step. Musical identity and timing correctness take priority over cosmetic/composite scores.

Preserve the existing `/ai-tab` journey:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock → full tab PDF → browser download + email delivery**

Fresh work replaces the transcription brain, not the customer/paywall/PDF journey.

## NON-NEGOTIABLE ORDER / BOUNDARIES

**full-mixture audio → frozen timing/measure map → role-isolated structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

- Work only on `songsterr-fresh-pipeline-v1`; do not modify `main` or Production.
- Frozen structure precedes note inference and cannot be rewritten downstream.
- Never silently change/drop detected MIDI or event identity to improve notation/fingering/path/rendering.
- `songsterr_pipeline/` remains deterministic, model-free, process-free, and network-free.
- Model/audio/DSP execution lives under `scripts/songsterr-fresh/` and hands validated JSON into the deterministic namespace.
- On 2026-09-08 the user explicitly authorized the **fresh reference-blind model/source-separation path**, including GPU if technically useful.
- That authorization does **not** authorize archived V143/Gomyway code, reference tabs, reference-based correction, professional/reference scorer use, training/fine-tuning, or broad optimizer sweeps.
- Model execution authorization is separate from musical acceptance. Customer eligibility remains fail-closed until validation is deliberately completed.

## AUTHORIZED AUDIO FIXTURE

Exact authorized fixture on `main`:
- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Git blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration ~210.674648526 s

Canaries fetch only that exact blob and verify `git hash-object`.

## ACCEPTED / FROZEN STRUCTURE

Frozen structure identity: `fnv1a32:2f493225`, canonicalLength 19653.

Key facts:
- 4/4, straight feel
- pickup / first downbeat ~0.65016 s
- 115 measures
- 113 measure-local tempo segments
- beat-grid MAE ~7.14 ms
- RMSE ~10.63 ms
- max ~58.05 ms
- acceptance `true`

This structure is immutable downstream.

## GUARDED CPU BASELINE

CPU analyzer: `scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`
Contract: `songsterr-fresh-cpu-note-evidence-v4`.

Exact fixture baseline:
- 492 onsets
- 1,130 candidates
- 139 local unambiguous pitch selections
- 353 ambiguous
- 0 no-candidate
- MIDI 40 appears in 97/139 local selections
- role relevance unresolved
- polyphony unresolved
- instrument isolation `none`

Event exposure:
- pitch-resolved: 139
- role-accepted: 0
- complete-tab/customer-eligible: 0

Latest CPU regression proof: run `34309259214`, job `102332311684`, artifact `10087798684`, digest `sha256:a1dbe85348f66847045e616d9726ffce986a82e995de0817fb20159e6fbf9d08`, 97/97 tests, 103 duration-resolved / 36 unresolved.

## AUTHORIZED MODEL PATH — VALIDATION PENDING

Architecture:
1. rebuild and verify frozen full-mixture structure;
2. Demucs `4.1.0`, `htdemucs_6s`, guitar stem for reference-blind role isolation;
3. Basic Pitch `0.4.0` on isolated guitar stem for polyphonic onset/pitch identity;
4. Basic Pitch decoded note-off times are **diagnostic only**;
5. model pitch evidence is duration-free when it crosses into the duration stage;
6. dedicated release stage remains sole active duration authority;
7. model evidence adaptation requires explicit model-upstream authorization;
8. `MODEL_EVIDENCE_VALIDATION_PENDING` blocks customer eligibility.

Core model files:
- `scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py`
- `scripts/songsterr-fresh/build_isolated_polyphonic_note_evidence.mjs`
- `scripts/songsterr-fresh/run_model_note_evidence_pipeline_canary.mjs`
- `.github/workflows/songsterr-fresh-model-guitar-polyphonic-canary.yml`

`noteEvidenceEvaluator.mjs` contract version 3 keeps model evidence fail-closed until independent validation is complete.

### Historical first green model canary — stochastic Demucs shift augmentation

Run `34309319200`, job `102332488694`:
- artifact `10087877760`
- digest `sha256:c051dfe5166a0d4fb019cf50aaae7afa97c7f477225657d9cc31b311c612ca31`
- 97/97 tests
- Demucs stem SHA `d47f51ac8fe8f100c91d7f3d3d518e3f39bed25b995ed7982208445bcdc99d3c`
- Basic Pitch 1,128 notes
- role relevance resolved true
- polyphony resolved true
- pitch-resolved / role-accepted 1,128
- customer-eligible 0
- v2 durations: 591 resolved / 537 unresolved; 517 reattack-censored

This run remains useful evidence, but exact stem/note counts are **not** a reproducibility baseline because it used Demucs `--shifts 1`.

## SINGLE DURATION AUTHORITY

Active stage: `scripts/songsterr-fresh/estimate_selected_pitch_releases.py`
Contract: `songsterr-fresh-cpu-spectral-release-evidence-v2`.

Hard rules:
- input must be duration-free;
- upstream non-null `durationSeconds` or `sourceEnd` is rejected;
- CPU path rejects model/GPU upstream by default;
- authorized model evidence requires `--allow-model-upstream`;
- Basic Pitch decoded note-off times never become active duration;
- same-pitch reattack is a censor/search boundary, not an invented duration;
- next generic onset is never used as duration.

Do not weaken these rules while improving coverage.

## ACTIVATION-VALLEY INVESTIGATION — DESCRIPTIVE ONLY

Probe: `scripts/songsterr-fresh/probe_model_activation_valleys.py`
Contract: `songsterr-fresh-model-activation-valley-probe-v1`.

Fixed predeclared rule; **no threshold sweep**:
- Basic Pitch per-pitch activation <= 0.20
- sustained for 3 model frames
- activation drop >= 0.15 from onset-window peak
- observed span >= 0.07 s
- search stops at next same-pitch reattack or 4.0 s
- independent selected-pitch CQT corroboration >= 6 dB spectral drop over 3 frames

Hard guards:
- `descriptiveOnly: true`
- `changesDuration: false`
- decoded model note ends used: false
- next onset used as duration: false
- writes `sourceEnd`: false
- writes `durationSeconds`: false
- changes pitch identity: false

First probe run `34310962622` found 89/541 corroborated valleys (16.45%) on its same-run evidence.

Repaired same-run probe `34311401076`, job `102338636114`, head `5899d45620629ac9705d1a3682b8821764bc6a02`:
- success
- 97/97 tests
- same-run Basic Pitch/evidence identity 1,174/1,174 exact
- v2 durations 601 resolved / 573 unresolved
- 550 reattack-censored
- 79/550 fixed-rule valleys = 14.36%
- artifact `10088603197`
- digest `sha256:b13d90601f36ed150429b7d23e8d7073afac8623738498af1b3b20ed4566160c`

This supports real activation+spectral release evidence for a minority of reattack-censored notes. It still does **not** authorize active duration writes.

## DEMUCS 4.1 LOADER / EXECUTED ASSET — CORRECTED

Important correction: Demucs `4.1.0` named models first load through Hugging Face, then fall back to the legacy remote repo only if HF loading fails.

For `htdemucs_6s` the **primary executed asset identity** is:
- Hugging Face namespace: `adefossez`
- repo: `adefossez/HTDemucs-6s`
- bag file: `htdemucs_6s.yaml`
- bag models: `['5c90dfd2']`
- model asset: `5c90dfd2.safetensors`
- pinned/current verified repo revision: `053e1404489b3dc58bf718224fac4b7316de8c93`
- safetensors SHA256: `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`
- Xet hash: `4a08ca8231da4bd9433191a95ee700cc8ba8693e980ac5b444f63eff38c807e1`

Legacy fallback remains informational only:
- `5c90dfd2-34c22ccb.th`
- checksum prefix `34c22ccb`

Verifier history:
- v1 initially verified the legacy fallback identity and therefore checked the wrong primary cache asset for Demucs 4.1.
- v2 commit **`f61480b24bbeb4932dad11310df7da8af020c3d1`** verifies Demucs 4.1's actual HF mapping, exact snapshot revision, exact bag membership, exact safetensors filename, and exact full SHA256.
- contract: `songsterr-fresh-demucs-model-asset-v2`
- verifier invokes no model and changes no audio/evidence.

## DEMUCS REPRODUCIBILITY — TWO DISTINCT BOUNDARIES

### 1. Intentional random-shift drift

Old `--shifts 1` runs produced different stems/counts because Demucs samples a random time offset whenever `shifts > 0`:
- `d47f51ac...` → 1,128 notes
- `99ded9ff...` → 1,170 notes
- `dbc198ae...` → 1,174 notes

`--shifts 0` removes that intentional random augmentation.

### 2. Cross-environment floating-point/runtime drift

Two earlier independent `--shifts 0` jobs on one runner generation both produced:
`8983d2694cbae3a519a65eadc63cc5bf691a6a542f2f6539b9a5f4461cd8727c`.

However a later exact-fixture `--shifts 0` run on a different GitHub Ubuntu runner image produced:
`419fcb5dd869e7d7cd2f66468c6c436fc9bb7767aaf546dd4cb61d34fde62ef1`.

Run `34312579809`, job `102342102147`:
- runner image Ubuntu 24.04.4 / image `20260831.293.1`
- Demucs 4.1.0, Torch 2.14.0, CPU, shifts 0, overlap 0.25, segment 7
- pass A succeeded with `419fcb5d...`
- job then failed only because the still-old verifier searched for the legacy `.th` asset, so pass B was skipped
- partial artifact `10088968246`, digest `sha256:7833ce06f2417f0c7b539465c38fb6b63c5c4e64b45da88fb296963a6e179133`

Therefore **cross-runner byte-exact stem equality is not an acceptance requirement**. The valid reproducibility contract is now:
1. exact source fixture and decoded input hashes recorded;
2. pinned model/runtime identities recorded;
3. `--shifts 0`;
4. same-job / same-runtime pass A and B must be byte-identical;
5. cross-environment stem hashes are diagnostic;
6. semantic note/evidence stability across environments must be evaluated separately.

Do not call any single stem SHA universally canonical across arbitrary runner hardware/images.

## PINNED REPRODUCIBILITY WORKFLOW — ACTIVE

Workflow: `.github/workflows/songsterr-fresh-demucs-reproducibility-canary.yml`
Hardened commit: **`ac30d9339847456be07821fd74d70f538a1402fc`**.

New controls:
- explicit `numpy==1.26.4`
- `torch==2.14.0`
- `huggingface-hub==1.30.0`
- `safetensors==0.8.0`
- `sphn==0.2.1`
- `demucs==4.1.0`
- `soundfile==0.13.1`
- CPU thread env pinned to 1 for OMP/MKL/OpenBLAS/NumExpr
- `PYTHONHASHSEED=0`
- decoded separation WAV SHA recorded
- runner image / CPU / FFmpeg / package runtime manifest recorded
- executed HF asset v2 verification
- same-job pass A == pass B SHA and byte `cmp`
- determinism contract explicitly says cross-environment byte equality is not required.

Active run:
- **`34313107961`**
- job **`102343661824`**

## PINNED DETERMINISTIC ACTIVATION CANARY — ACTIVE

Workflow: `.github/workflows/songsterr-fresh-model-activation-valley-deterministic.yml`
Hardened commit: **`5baecdc46fcf94f51b4fa4ed968b3231cde28eba`**.

It now uses the same pinned model/runtime/threading controls, records analysis + separation WAV hashes and runtime provenance, verifies the executed HF safetensors asset, rebuilds frozen structure, runs duration-free Basic Pitch evidence, applies unchanged v2 sole release authority, runs the unchanged descriptive activation-valley rule, and requires 97/97 deterministic tests.

It intentionally has **no fixed stem-hash or historical Basic Pitch count gate**; same-run MIDI/event identity remains the gate while cross-environment semantic stability is characterized.

Active run:
- **`34313160939`**
- job **`102343811787`**

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true` yet.

Current model evidence blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain 0.

## NEXT ENGINEERING STEPS

1. Finish pinned reproducibility run `34313107961`; require executed HF asset v2 proof and same-job pass-A/pass-B byte identity.
2. Finish pinned activation run `34313160939`; record exact same-run Basic Pitch count, v2 duration coverage, fixed-rule valley coverage, and 97/97 result.
3. If both are green, update the authoritative model canary from `--shifts 1` to `--shifts 0`, use the same pinned runtime/HF asset proof, and establish the new **runtime-scoped** model baseline.
4. Before active duration integration, compare at least the available `--shifts 0` environments semantically: note count/distribution/onset identity characteristics and duration/valley coverage. Do not require stem-byte equality across environments.
5. Then capture Basic Pitch raw `note` activations from the existing transcription inference rather than rerunning Basic Pitch solely for duration evidence.
6. Integrate the **unchanged fixed** activation+spectral valley rule into the same sole duration authority, fallback-only for events otherwise unresolved by same-pitch reattack censoring.
7. Integration negative proofs must preserve: no decoded Basic Pitch note-off as duration, no next-onset duration, no upstream duration leakage, explicit model-upstream authorization, no MIDI/event identity changes, and no scorer/reference provenance.
8. Keep `modelValidationComplete: false` and customer eligibility 0 until independent model validation is explicitly completed.

## NON-NEGOTIABLES

- Canonical branch/checkpoint above remain authoritative.
- Frozen structure cannot be rewritten downstream.
- Never silently alter/drop detected MIDI/event identity.
- Preserve the existing `/ai-tab` preview → unlock → full PDF → email/download flow.
- No `main`/Production changes.
- Real-audio work stays inside the exact authorized fixture unless the user explicitly authorizes another fixture.
- Archived V143/Gomyway implementation and scorer/reference knowledge remain untouched.
- Keep this checkpoint updated after every meaningful milestone.
