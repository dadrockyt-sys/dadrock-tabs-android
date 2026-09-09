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

### Historical first green model canary (now known to use stochastic Demucs shift augmentation)

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

This run remains useful evidence, but its exact stem/note counts are **not** a reproducibility baseline because the workflow used `--shifts 1`.

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

Probe:
- `scripts/songsterr-fresh/probe_model_activation_valleys.py`
- commit `6181b44cb628e068df75b1ad7c89b18a49b83cc4`
- contract `songsterr-fresh-model-activation-valley-probe-v1`
- `descriptiveOnly: true`
- `changesDuration: false`

Fixed predeclared evidence rule; **no threshold sweep**:
- Basic Pitch per-pitch activation <= 0.20
- sustained for 3 model frames
- activation drop >= 0.15 from onset-window peak
- observed span >= 0.07 s
- search stops at next same-pitch reattack or 4.0 s
- independent selected-pitch CQT corroboration >= 6 dB spectral drop over 3 frames

Probe hard guards:
- decoded model note ends used: false
- next onset used as duration: false
- writes `sourceEnd`: false
- writes `durationSeconds`: false
- changes pitch identity: false

### First probe run

Run `34310962622`, job `102337354610`:
- exact fixture and frozen structure passed
- v2 baseline reproduced
- probe same-run identity 1,170/1,170 exact
- v2: 609 resolved / 561 unresolved; 541 reattack-censored
- corroborated activation+spectral valleys: 89/541 = 16.45%
- artifact `10088439396`, digest `sha256:5b7a6e78dfdb17e3ac451deb9c79c33b1229c7d0edc85677394420305a0817bc`
- workflow was red only because it incorrectly asserted historical cross-run counts 1,128/517

### Repaired same-run probe — green

Run `34311401076`, job `102338636114`, head `5899d45620629ac9705d1a3682b8821764bc6a02`:
- conclusion **success**
- exact fixture / frozen structure / v2 stage passed
- deterministic suite **97/97 pass**
- stochastic Demucs guitar stem SHA `dbc198ae55874d2f40325e59fc53a9ed6412eb9b0a836dc549ea88c9a453ae91`
- Basic Pitch / evidence exact same-run identity: **1,174 / 1,174**, exact MIDI true, max start delta 0, max confidence delta 0
- v2 durations: **601 resolved / 573 unresolved**
- reattack-censored unresolved: **550**
- fixed-rule corroborated valleys: **79 / 550 = 14.36%**
- candidate observed-span mean ~0.2736 s, median ~0.2438 s, p90 ~0.4180 s, max ~0.5108 s
- artifact **`10088603197`**
- artifact digest **`sha256:b13d90601f36ed150429b7d23e8d7073afac8623738498af1b3b20ed4566160c`**

Together with the first probe, this supports the existence of real activation+spectral release valleys in a minority of reattack-censored notes. It does **not** yet authorize writing those valleys as active duration.

## DEMUCS REPRODUCIBILITY — ROOT CAUSE FOUND

Three exact-fixture runs using the old `--shifts 1` workflow produced different guitar stem hashes and downstream note counts:
- `d47f51ac...` → 1,128 Basic Pitch notes
- `99ded9ff...` → 1,170 notes
- `dbc198ae...` → 1,174 notes

Root cause: Demucs `apply_model()` deliberately samples a random time offset whenever `shifts > 0`. Therefore `--shifts 1` means **one random shift-augmentation pass**, not one deterministic pass.

This explains the cross-run drift. It is not evidence by itself that model weights changed.

Demucs packaged manifest facts:
- `htdemucs_6s.yaml` maps to signature `5c90dfd2`
- remote asset: `hybrid_transformer/5c90dfd2-34c22ccb.th`
- Demucs verifies the checksum-bearing filename prefix on download.

Model-asset verifier:
- `scripts/songsterr-fresh/verify_demucs_model_asset.py`
- initial commit `2b1e62a5773b2e088453e7621f8fcf674d49462d`
- contract `songsterr-fresh-demucs-model-asset-v1`
- exact identity remains fixed to model `htdemucs_6s`, signature `5c90dfd2`, filename `5c90dfd2-34c22ccb.th`, remote suffix `hybrid_transformer/5c90dfd2-34c22ccb.th`, and checksum prefix `34c22ccb`
- initial verifier incorrectly assumed the asset lived only under Torch Hub checkpoints
- Demucs 4.1 logs show the model download is Hugging Face-backed on these runners
- verifier cache-location fix commit **`f86d5a2f707ef534e343161e914c904879ef050e`** searches the exact expected filename under Torch Hub and Hugging Face cache roots while preserving every identity/checksum guard
- verifier invokes no model and changes no audio/evidence

## DETERMINISTIC `--shifts 0` EVIDENCE

Two **independent GitHub runners/jobs** already produced the exact same guitar-stem SHA with the exact fixture and Demucs `--shifts 0` settings:

**`8983d2694cbae3a519a65eadc63cc5bf691a6a542f2f6539b9a5f4461cd8727c`**

Independent proof A:
- workflow `Songsterr Fresh Demucs Reproducibility Canary`
- run `34311705244`, job `102339526614`
- deterministic pass A produced the SHA above
- the job then stopped only at the old cache-location verifier bug before pass B
- partial artifact `10088674125`, digest `sha256:133f7c67cad7ba0915533f36be89a28c979c567966a2f3221060fb35ed97773a`

Independent proof B:
- workflow `Songsterr Fresh Deterministic Activation Valley Probe`
- run `34311795363`, job `102339801600`
- rebuilt frozen structure successfully
- deterministic Demucs stem produced the **same SHA above** on a separate runner
- the job then stopped only at the same old cache-location verifier bug
- partial artifact `10088714195`, digest `sha256:0cf7a1e55c52fa923a806ecc0d15cafbaa28c60a941fad0121fadadde7aff15e`

This independent cross-runner equality is strong evidence that disabling random shift augmentation restores deterministic stem bytes for the current pinned environment. The formal same-job pass-A/pass-B proof and full model-asset SHA are still required before promotion.

## REPAIRED DETERMINISTIC CANARIES — ACTIVE

Verifier-fix head: **`f86d5a2f707ef534e343161e914c904879ef050e`**.

Reproducibility run:
- run **`34312579809`**
- job **`102342102147`**
- goal: exact fixture → `--shifts 0` pass A → full asset verification/SHA → `--shifts 0` pass B → SHA equality + byte `cmp` → artifact

Deterministic activation run:
- run **`34312579806`**
- job **`102342102323`**
- goal: exact fixture/frozen structure → `--shifts 0` separation → full asset verification → Basic Pitch duration-free evidence → unchanged v2 duration authority → unchanged descriptive activation-valley rule → 97-test suite → artifact

Do not integrate activation valleys into active duration until both repaired canaries are green and the full weight SHA / deterministic baseline are recorded.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete: true` yet.

Current model evidence blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events remain 0.

## NEXT ENGINEERING STEPS

1. Finish `34312579809`; record full Demucs asset SHA and two-pass deterministic stem proof.
2. Finish `34312579806`; record deterministic Basic Pitch count, v2 duration coverage, fixed-rule valley coverage, and 97/97 suite result.
3. If both are green, update the authoritative model canary from stochastic `--shifts 1` to deterministic `--shifts 0` and establish the new canonical model baseline.
4. Only after that integrate the **unchanged fixed** activation+spectral valley rule into the same sole duration authority, fallback-only for notes otherwise unresolved by same-pitch reattack censoring.
5. Integration must preserve negative proofs: no decoded Basic Pitch note-off as duration, no next-onset duration, no upstream duration leakage, explicit model-upstream authorization, no MIDI/event identity changes, and no scorer/reference provenance.
6. Keep `modelValidationComplete: false` and customer eligibility 0 until independent model validation is explicitly completed.

## NON-NEGOTIABLES

- Canonical branch/checkpoint above remain authoritative.
- Frozen structure cannot be rewritten downstream.
- Never silently alter/drop detected MIDI/event identity.
- Preserve the existing `/ai-tab` preview → unlock → full PDF → email/download flow.
- No `main`/Production changes.
- Real-audio work stays inside the exact authorized fixture unless the user explicitly authorizes another fixture.
- Archived V143/Gomyway implementation and scorer/reference knowledge remain untouched.
- Keep this checkpoint updated after every meaningful milestone.
