# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-13 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research and protected-song execution remain closed unless the user explicitly reopens them.
- Never silently alter/drop event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP research stays under `scripts/songsterr-fresh/`.
- Current authority remains fail-closed: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`.
- Protected song remains embargoed. No Production or customer-admission change is authorized.

## USER COMPUTE AUTHORIZATION RULE — 2026-09-13

The user explicitly authorized continued work at assistant discretion and requested that authorization be sought only before:
- any **Modal** run;
- any **Vercel heavy-GPU** run;
- any **L4 GPU** run.

Normal research, coding, GitHub work, CPU runs, checkpoints, tests and ordinary Vercel work may proceed without another authorization prompt, subject to the scientific/policy boundaries in this file.

## HISTORICAL CLOSED LINES

V1/V2 are rejected research diagnostics.

GuitarSet/V3 and IDMT/V4 are closed and revealed/contaminated for future untouched-holdout use. Do not rerun/tune them.

V4 final: 568/568 files, 7,619 decoded, 1,644 positive, 1,292 correct, precision `0.7858880778588808`, one-sided 95% Wilson LB `0.7687844934184139` vs required `0.9900` → FAIL. Result commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`; policy rejection `01a276045d32b643aa17013b959e89e41b0f305e`.

## V5 — CLOSED / EXTERNAL VALIDATION FAILED / ADMISSION REJECTED

V5 preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`, commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`.

Frozen final scoring contract: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_FINAL_SCORING_PREREGISTRATION.md`, commit `846cdedad46c10553569011a28ae01c72a9f6504`.

Single official FLGD execution:
- workflow run `34748789583`
- job `103701492462`
- frozen source `6a3ea0808676ead13518e258fa912fd62a4eb33c`
- FLGD revision `a38306c244b3ea81496ad58b4514622185e58211`
- Stage B report SHA-256 `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`
- artifact ID `10316047064`
- artifact archive SHA-256 `04bf94764c38346298f78d04ee8419f1f663091cc8abe31ee827f4c54df42fb7`
- result JSON SHA-256 `a79a09a695142ccd8c68d7d04089bb0d3ec675c11c6a39167f1e1cd0740b9c04`.

Immutable result: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_OFFICIAL_CORRECTNESS_RESULT.md`, commit `df6a306a055303a6f37b229bfc9e538803f25337`.

Valid result:
- 79/79 files
- 84,577 decoded/classified events
- 43,349 V5 positives
- 27,850 positive correct
- precision `0.642460033680131`
- one-sided 95% Wilson LB `0.6386648804090969`
- required pooled LB `0.9900`
- `externalValidationPassed:false`
- all split and guitar-type robustness gates failed; identity/runtime/event-preservation/population/policy guards passed.

Separate policy review: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_POST_RESULT_POLICY_REVIEW.md`, commit `44c99d54ed7e728e85ef4042d1f15ba09643713c`.

Decision: **V5 ADMISSION REJECTED / FAIL-CLOSED**.

FLGD is now revealed. Do not rerun FLGD V5 or tune V5 against its result.

## V6 — ACTIVE SUCCESSOR RESEARCH / SYNTHETIC + METADATA ONLY

User continued the project on 2026-09-13 under the standing compute rule above.

Research charter: `docs/checkpoints/SONGSTERR_FRESH_SUCCESSOR_RESEARCH_CHARTER_V6.md`.
Charter commit: `2b96fba0e3df955e62386691023cb31eeb2d11f6`.

V6 is a genuinely new successor line, not a V5 rescue or threshold retune.

### Scientific gap

V1/V2/V4/V5 primarily use post-onset steady-state pitch/periodicity/spectral evidence. V6 investigates whether the selected MIDI shows an **onset-synchronous acoustic birth signature**: candidate-specific complex/harmonic innovation that appears at the decoded onset relative to the immediately preceding audio state.

Candidate family A: onset-synchronous complex-harmonic birth corroboration, CPU/reference-blind, preserving the Basic Pitch event and MIDI exactly.

Candidate family B: optional independent guitar-model agreement as a second corroborating channel. Candidate model: MIT-licensed `xavriley/midi-transcription-models` GAPS guitar checkpoint, to be pinned by exact revision/SHA before any engineering use. If used, GAPS cannot be an untouched V6 holdout.

No exact V6 method/constants are final yet. Synthetic-only development may select/amend them before any new real-corpus correctness exposure. Once a final V6 method preregistration is frozen, its holdout may not be used for tuning.

### Closed correctness inputs for V6 design

Do not use event-level correctness from:
- FLGD V5;
- IDMT V4;
- GuitarSet V3;
- protected-song outcomes.

These may be referenced only to identify previously failed method families and prevent accidental repetition.

### Synthetic contract requirements

Synthetic development must include at least:
- clean low/mid/high guitar notes;
- detuning;
- attack noise;
- silence/low noise;
- truncated pre/post context;
- selected pitch already sounding before event;
- octave/harmonic alias trap;
- true selected note entering over an already-sounding lower note;
- simultaneous dyads/triads;
- neighboring semitone competition;
- selected-note reattack;
- unrelated transient at selected onset;
- exact identity/MIDI preservation.

Synthetic success is not admission evidence.

## EXTERNAL HOLDOUT SEARCH — METADATA ONLY

No V6 real correctness holdout is frozen yet.

### Guitar-TECHS — leading candidate, not yet admitted

Public project/Zenodo materials describe:
- real electric-guitar performances;
- three professional performers and varied gear/rooms;
- DI, amp-mic, egocentric and exocentric audio;
- per-string MIDI captured with a Fishman Triple Play Connect;
- CC BY 4.0 licensing.

However, the Zenodo description warns that some signal paths may exhibit up to 100 ms temporal misalignment. Therefore Guitar-TECHS cannot be scored yet. A separate metadata/reference-blind alignment-semantics audit must first freeze an authoritative audio path and any deterministic alignment correction before correctness is seen.

### GuitarDuets — not preferred for external-real admission

The dataset contains real and synthesized classical-guitar duets, but published note-level MIDI annotation is specifically described for the synthesized subset. It is therefore not currently preferred as the real-audio V6 admission holdout.

### GAPS — not adopted as V6 holdout

GAPS is not currently adopted because public licensing statements are inconsistent across distribution surfaces. It is also unsuitable as an untouched holdout if the GAPS-trained independent guitar model is used.

## NEXT ALLOWED ACTIONS

Proceed without another user prompt on CPU/synthetic/metadata work:
1. build deterministic V6 onset-birth synthetic fixtures;
2. implement candidate-family-A onset-synchronous complex/harmonic corroboration under `scripts/songsterr-fresh/`;
3. run controlled CPU-only synthetic tests and checkpoint results;
4. optionally inspect/pin the independent GAPS guitar model and CPU inference path without using real admission correctness;
5. select/freeze one final V6 method before new real-corpus correctness;
6. perform a Guitar-TECHS metadata/alignment audit before any scoring;
7. only after method + holdout semantics + scoring gates are frozen may one official untouched external correctness run occur.

Ask the user before any Modal, Vercel heavy-GPU or L4 run.

## STILL FORBIDDEN

- V5 FLGD rerun or post-result tuning
- using FLGD/IDMT/GuitarSet correctness to select V6 constants
- post-hoc holdout file/stratum selection
- protected-song execution
- duration research
- archived V143/Gomyway / GOAT/reference scoring
- real-corpus threshold/optimizer sweeps
- training/fine-tuning on a proposed admission holdout
- Production/customer promotion without new untouched external validation and separate policy approval
- Modal, Vercel heavy-GPU or L4 execution without explicit user authorization.

## FRESH-CHAT HANDOFF

Continue from this file on `songsterr-fresh-pipeline-v1`.

V5 is closed and rejected. V6 successor research is active only for synthetic/metadata development under charter `2b96fba0e3df955e62386691023cb31eeb2d11f6`.

Next: build/test the onset-synchronous birth-signature candidate on deterministic synthetic fixtures; keep FLGD/IDMT/GuitarSet correctness closed; do not resume V143/Gomyway; ask only before Modal/Vercel-heavy-GPU/L4 runs.
