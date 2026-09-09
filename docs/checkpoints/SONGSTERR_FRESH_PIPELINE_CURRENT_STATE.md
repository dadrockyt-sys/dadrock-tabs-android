# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-09 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the **only canonical fresh-chat checkpoint** for the Songsterr-inspired fresh pipeline. Do not resume archived V143/Gomyway implementation, reference tabs, scorer logic, or historical percentages unless the user explicitly asks.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from uploaded audio to a usable finished tab without a mandatory human correction step. Musical identity and timing correctness take priority over cosmetic/composite scores.

Preserve the existing `/ai-tab` customer journey:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock → full tab PDF → browser download + email delivery**

Fresh work replaces the transcription brain, not the customer/paywall/PDF journey.

## FOUNDATIONAL ORDER

**full-mixture audio → frozen timing/measure map → role-isolated structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

`structureMap` is first-class. Once accepted for a fixture, note inference must not rewrite tempo, meter, downbeats, measures, pickup, feel, or subdivisions.

Never silently change/drop detected MIDI or event identity to improve notation, fingering, path motion, ambiguity coverage, or legacy rendering.

## PROJECT / AUTHORIZATION BOUNDARY

- Work only on `songsterr-fresh-pipeline-v1`.
- Do not modify `main` or Production.
- Old V143/Gomyway implementation is archive/evidence only.
- Historical scorer percentages are not fresh acceptance gates.
- On 2026-09-08 America/Toronto the user explicitly authorized the **fresh reference-blind model/source-separation path**, including GPU use if technically useful.
- That authorization does **not** authorize archived V143 code, reference tabs, reference-based correction, professional/reference scorer use, training/fine-tuning, or broad optimizer sweeps.
- `songsterr_pipeline/` remains deterministic, model-free, process-free, and network-free. Model/audio/DSP execution lives under `scripts/songsterr-fresh/` and passes validated JSON into the deterministic namespace.
- Model execution authorization is separate from musical acceptance. Model evidence must pass independent validation before customer eligibility can exist.

## AUTHORIZED AUDIO FIXTURE

Exact authorized fixture on `main`:
- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Git blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration ~210.674648526 s

Canaries fetch only that exact blob and verify `git hash-object`.

## ACCEPTED / FROZEN STRUCTURE

Frozen structure identity: `fnv1a32:2f493225`, canonicalLength 19653.

Key facts:
- duration ~210.67465 s
- 4/4
- straight feel
- pickup / first downbeat ~0.65016 s
- 115 measures
- 113 measure-local tempo segments
- beat-grid MAE ~7.14 ms
- RMSE ~10.63 ms
- max ~58.05 ms
- acceptance `true`

This structure is immutable downstream.

## GUARDED CPU BASELINE

CPU pitch analyzer: `scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`

Contract: `songsterr-fresh-cpu-note-evidence-v4`.

Exact fixture baseline:
- 492 onsets
- 1,130 candidates
- 139 local unambiguous selections
- 353 ambiguous
- 0 no-candidate
- MIDI 40 appears in 97/139 local selections (~69.8%)
- role relevance unresolved
- polyphony unresolved
- instrument isolation `none`

Event exposure:
- pitch-resolved: **139**
- role-accepted: **0**
- complete-tab/customer-eligible: **0**

Latest CPU regression proof remains green: run `34309259214`, job `102332311684`, artifact `10087798684`, digest `sha256:a1dbe85348f66847045e616d9726ffce986a82e995de0817fb20159e6fbf9d08`, 97/97 tests, 103 duration-resolved / 36 unresolved.

## AUTHORIZED MODEL PATH — VALIDATION PENDING

Architecture:
1. rebuild and verify frozen full-mixture structure;
2. Demucs `4.1.0`, `htdemucs_6s`, guitar stem for reference-blind role isolation;
3. Basic Pitch `0.4.0` on isolated guitar stem for polyphonic onset/pitch identity;
4. Basic Pitch decoded note-off times remain **diagnostic only**;
5. model pitch evidence is duration-free when it crosses into the dedicated duration stage;
6. dedicated release stage remains sole active duration authority;
7. note evidence is adapted only with explicit model-upstream authorization;
8. `MODEL_EVIDENCE_VALIDATION_PENDING` prevents customer eligibility until validation is deliberately completed.

Core model files/contracts:
- `scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py` — `songsterr-fresh-basic-pitch-isolated-guitar-v1`
- `scripts/songsterr-fresh/build_isolated_polyphonic_note_evidence.mjs` — `songsterr-fresh-isolated-polyphonic-note-evidence-v1`
- `scripts/songsterr-fresh/run_model_note_evidence_pipeline_canary.mjs`
- `.github/workflows/songsterr-fresh-model-guitar-polyphonic-canary.yml`

`noteEvidenceEvaluator.mjs` contract version 3 keeps model evidence fail-closed until independent validation is complete.

### First green model canary

Run `34309319200`, job `102332488694`, head `9d4a9d823e2d7da9c9e58e0b0d8b1e0881822180`:
- conclusion success
- artifact `10087877760`
- digest `sha256:c051dfe5166a0d4fb019cf50aaae7afa97c7f477225657d9cc31b311c612ca31`
- 97/97 deterministic tests
- Demucs guitar stem SHA256 `d47f51ac8fe8f100c91d7f3d3d518e3f39bed25b995ed7982208445bcdc99d3c`
- Basic Pitch: 1,128 notes, 1,020 start clusters, 98 polyphonic start clusters, max cluster size 3
- MIDI 40 only 40/1,128 (3.55%), so the old full-mixture E2 collapse is absent
- role relevance resolved true
- polyphony resolved true
- pitch-resolved 1,128
- role-accepted 1,128
- complete-tab/customer-eligible 0
- exact MIDI 1,128/1,128 preserved
- fretboard path resolved true

First model-path duration result:
- 591 / 1,128 resolved (52.39%)
- 537 unresolved
- 517 `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
- 16 `INSUFFICIENT_ONSET_TO_FLOOR_CONTRAST`
- 4 `NO_CLEAR_SUSTAINED_SPECTRAL_RELEASE`

Current evaluation blockers remain:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

## SINGLE DURATION AUTHORITY

Active stage: `scripts/songsterr-fresh/estimate_selected_pitch_releases.py`

Contract: `songsterr-fresh-cpu-spectral-release-evidence-v2`.

Hard rules:
- input must be duration-free;
- any upstream non-null `durationSeconds` or `sourceEnd` is rejected;
- CPU path rejects model/GPU upstream by default;
- authorized model evidence requires explicit `--allow-model-upstream`;
- Basic Pitch decoded note-off times never become active duration;
- same-pitch reattack is a censor/search boundary, not an invented duration;
- next generic onset is never used as duration.

Do not weaken these rules while improving coverage.

## ACTIVATION-VALLEY DURATION INVESTIGATION — DESCRIPTIVE ONLY

New probe:
- `scripts/songsterr-fresh/probe_model_activation_valleys.py`
- commit `6181b44cb628e068df75b1ad7c89b18a49b83cc4`
- contract `songsterr-fresh-model-activation-valley-probe-v1`
- `descriptiveOnly: true`
- `changesDuration: false`

New canary:
- `.github/workflows/songsterr-fresh-model-activation-valley-probe.yml`
- initial workflow commit `87961c543fb8984b8d04cece4112f77b8dfc3a21`
- repaired same-run identity assertions commit `5899d45620629ac9705d1a3682b8821764bc6a02`

The probe has fixed predeclared rules; **no threshold sweep**:
- Basic Pitch per-pitch activation <= 0.20
- sustained for 3 model frames
- activation drop >= 0.15 from the onset-window peak
- observed span >= 0.07 s
- search ends at the next same-pitch reattack or 4.0 s
- independent selected-pitch CQT corroboration requires >= 6 dB spectral drop over 3 frames

Hard guards in probe output:
- decoded model note ends used: false
- next onset used as duration: false
- writes `sourceEnd`: false
- writes `durationSeconds`: false
- changes pitch identity: false

### First exact-fixture activation probe — informative but CI-red for stale historical count assumption

Run `34310962622`, job `102337354610`, head `87961c543fb8984b8d04cece4112f77b8dfc3a21`:
- exact authorized fixture passed
- frozen structure identity passed
- current v2 duration baseline reproduced successfully for that run
- artifact upload succeeded: `10088439396`
- artifact digest `sha256:5b7a6e78dfdb17e3ac451deb9c79c33b1229c7d0edc85677394420305a0817bc`
- probe itself proved exact same-run Basic Pitch identity: 1,170 model events = 1,170 evidence events, exact MIDI identity true, max start delta 0, max confidence delta 0
- the workflow step failed only because it incorrectly asserted historical cross-run counts 1,128 / 517
- deterministic suite was therefore skipped in that first probe run

Same-run model evidence on that probe:
- Basic Pitch notes: **1,170**
- start clusters: 1,052
- polyphonic start clusters: 101
- max cluster size: 4
- v2 durations: **609 resolved / 561 unresolved** (~52.05%)
- reattack-censored unresolved: **541**
- Demucs guitar stem SHA256: `99ded9ff55f0f0bcab7b79abf5126e873474d69064e6703724e6ae199b63921d`

Fixed-rule activation-valley probe result:
- examined reattack-censored cases: **541**
- corroborated activation + spectral valley candidates: **89**
- candidate rate: **16.45%**
- rejection reasons:
  - 371 `NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION`
  - 73 `INSUFFICIENT_SPECTRAL_CORROBORATION`
  - 8 `INSUFFICIENT_ACTIVATION_DROP`
- candidate observed-span mean ~0.2877 s
- median ~0.2786 s
- p10 ~0.1741 s
- p90 ~0.4435 s
- max ~0.5470 s

This is promising evidence that a minority of reattack-censored notes contain a real observed release valley. It is **not yet integrated into active duration** and must not be used as a duration gate until the probe is green and reproducibility is hardened.

## NEW REPRODUCIBILITY FINDING — DEMUCS OUTPUT DRIFT

The two exact-fixture model runs used the same declared package/model/device/settings but produced different guitar-stem hashes:
- earlier: `d47f51ac8fe8f100c91d7f3d3d518e3f39bed25b995ed7982208445bcdc99d3c`
- later: `99ded9ff55f0f0bcab7b79abf5126e873474d69064e6703724e6ae199b63921d`

That changed downstream Basic Pitch counts from 1,128 to 1,170. Therefore **historical exact note count is not a valid cross-run identity gate until Demucs reproducibility is pinned**.

Upstream Demucs manifest facts:
- `htdemucs_6s.yaml` maps to model signature `5c90dfd2`
- Demucs remote manifest names asset `hybrid_transformer/5c90dfd2-34c22ccb.th`

Next reproducibility hardening must record/verify the actual downloaded model-weight cryptographic hash and determine whether stem drift comes from changing asset bytes or CPU inference/runtime nondeterminism.

Do not mark model validation complete until this is resolved or explicitly bounded.

## ACTIVE CANARY

Repaired activation-valley canary dispatched from commit `5899d45620629ac9705d1a3682b8821764bc6a02`:
- run `34311401076`
- job `102338636114`
- assertions now compare model/evidence identity **within the same run** and compare examined reattack count to that same run's v2 unresolved-reason count
- no historical 1,128/517 count is used as a cross-run gate

Update this section when the run completes.

## NEXT ENGINEERING STEPS

1. Finish the repaired exact-fixture activation probe and require the 97-test deterministic suite to remain green.
2. Record the downloaded Demucs `5c90dfd2-34c22ccb.th` weight SHA256 in CI and compare across exact-fixture runs.
3. If weights are identical, investigate CPU/runtime determinism before treating Demucs stem bytes or exact Basic Pitch counts as reproducible identities.
4. Keep activation-valley evidence descriptive until reproducibility is understood.
5. Only then consider integrating the fixed activation+spectral valley rule into the **same sole duration authority** as a fallback for reattack-censored notes.
6. Integration must preserve negative proofs: no Basic Pitch decoded note-off may populate active duration/end, no next-onset duration, no MIDI identity changes.
7. Do **not** set `modelValidationComplete: true` or expose customer-eligible events yet.

## NON-NEGOTIABLES

- Canonical branch/checkpoint above remain authoritative.
- Frozen structure precedes note placement and cannot be rewritten downstream.
- Never silently alter detected MIDI/event identity.
- Never drop pitches merely to satisfy fingering/path/legacy rendering.
- Preserve the existing `/ai-tab` preview → unlock → full PDF → email/download flow.
- No `main`/Production changes.
- Real-audio work stays inside the exact authorized fixture unless the user explicitly authorizes another fixture.
- Archived V143/Gomyway implementation and scorer/reference knowledge remain untouched.
- Model execution is authorized for the fresh path, but model evidence remains non-deliverable until explicit validation succeeds.
- Keep this checkpoint updated after every meaningful milestone.
