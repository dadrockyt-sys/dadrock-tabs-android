# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-12 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT, reference/pro scoring, training/fine-tuning, broad threshold/optimizer sweeps and duration work remain closed unless explicitly reopened.
- Never silently alter/drop MIDI or event identity.
- Preserve `/ai-tab` UX flow.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP execution stays under `scripts/songsterr-fresh/`.

Current authority remains fail-closed:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused
- persistent Policy C `UNENROLLED`.

## V1 / V2 / V3 — CLOSED

V1 and V2 remain frozen research diagnostics rejected as admission authority.

Historical V2 protected-song result: 1,140 preserved events; 187 corroborated / 951 not / 2 insufficient. Historical protected-song outcomes may not tune successors.

V3 is closed after frozen GuitarSet v1.1.0 validation failed preregistered gates:
- 357/357 tracks
- 62,438 decoded events
- 11,252 V3-positive
- 10,019 correct positives
- precision `0.8904194809811589`
- one-sided 95% Wilson lower bound `0.8854816094599652`
- required lower bound `0.9900` → FAIL.

GuitarSet is historical only and is not an untouched V5 holdout.

## V4 — CLOSED / REJECTED AS ADMISSION AUTHORITY

V4 preregistration:
`docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`

Frozen V4 implementation:
`scripts/songsterr-fresh/independent_pitch_corroboration_v4.py`
commit `6e9e11e60d0d6958c30edf6bb5d686d545936a19`.

Official IDMT V4 result record:
`docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_RESULT.md`
commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`.

Official result artifact SHA-256:
`d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`.

Aggregate V4 result:
- completed files `568 / 568`
- decoded events `7619`
- V4 positives `1644`
- correct positives `1292`
- positive precision `0.7858880778588808`
- one-sided 95% Wilson lower bound `0.7687844934184139`
- required lower bound `0.9900` → FAIL.

Separate policy review:
`docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_POLICY_REVIEW.md`
commit `01a276045d32b643aa17013b959e89e41b0f305e`.

Decision: **V4 CLOSED / REJECTED AS ADMISSION AUTHORITY.**
No IDMT V4 rerun, retuning, post-hoc filtering, protected-song V4 execution, or customer promotion is authorized. IDMT is historical only and is not an untouched V5 holdout.

## V5 — ACTIVE SUCCESSOR / SYNTHETIC CONTRACT GREEN

User explicitly authorized a new successor on 2026-09-12 with the instruction to fix the failures.

### V5 preregistration

`docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`
commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`.

Contract:
`songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.

V5 is **not** a V4 threshold retune. It replaces single-winner pitch corroboration with a polyphony-aware harmonic-necessity test: the existing selected MIDI must remain necessary to explain the local spectrum when all playable guitar pitches are allowed to explain the signal simultaneously.

Frozen V5 inputs:
- mono isolated guitar exactly 44,100 Hz;
- existing onset as integer sample index;
- existing selected MIDI integer 40..88;
- no reference truth, duration/end, next onset, Basic Pitch confidence/activation, performer/style/dataset/bit-depth identity, downstream tablature or historical labels.

Frozen V5 signal design:
- three 8192-sample windows at post-onset offsets `2048`, `8192`, `14336`;
- FFT size `32768`;
- full candidate MIDI dictionary 40..88;
- coherent fundamental estimate inside each candidate semitone cell;
- harmonics 1..8, template amplitude weights `1/h`, L2-normalized;
- simultaneous deterministic NNLS using SciPy `1.15.3`;
- selected-pitch leave-one-out residual necessity fraction `>=0.01`;
- fundamental/own-max-harmonic magnitude ratio `>=0.05`;
- all three temporal views required; no voting/fallback;
- demeaned RMS `<1e-4`, truncation, invalid/nonfinite template or solver failure => insufficient evidence.

Development contamination boundary:
- do not choose V5 constants from protected-song outcomes, GuitarSet V3 correctness, IDMT V4 correctness/strata, or post-hoc sweeps on observed holdouts;
- previously observed corpora remain historical diagnostics only;
- future admission validation requires a genuinely untouched corpus/partition frozen before correctness results.

### V5 implementation

`scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`
implementation commit `0b02fc949ba9fa0e3fac6b2edb9f19002f58fc99`.

The implementation has no standalone real-corpus mode and invokes no Basic Pitch, Demucs, Torch or `songsterr_pipeline` code.

### V5 synthetic fixture manifest

`docs/checkpoints/SONGSTERR_FRESH_V5_SYNTHETIC_FIXTURES.json`
manifest commit `efca2994efdce2c5a3b35d6e12fb9dc82096a268`.

Frozen fixture count `20` with expected class counts:
- corroborated `13`
- not corroborated `4`
- insufficient `3`.

Coverage includes:
- monophonic low/mid/high guitar range;
- ±25-cent detuning;
- attack noise;
- dominant second harmonic;
- perfect-fifth dyad;
- major/minor triads with different selected chord tones;
- dense six-note mixture;
- equal close dyad;
- wrong-octave traps;
- neighboring-semitone trap;
- temporal pitch change;
- silence, low-level noise and truncation;
- selected-MIDI identity preservation.

### V5 controlled CI — GREEN

Workflow:
`.github/workflows/songsterr-fresh-v5-polyphonic-necessity-ci.yml`
workflow commit `7f07aa34ffb45860d55bcd755372abca98019717`.

Run `34718020842`, job `103618636972`: **SUCCESS**.

Exact CI source: `7f07aa34ffb45860d55bcd755372abca98019717`.

Runtime:
- CPython `3.10.21`
- NumPy `1.26.4`
- SciPy `1.15.3`.

All 20 frozen fixture classifications matched exactly (`13 / 4 / 3`). In particular V5 retained true selected notes in dyads, triads, a dense six-note mixture, a close dyad and a dominant-harmonic case while rejecting wrong octaves, a stronger neighboring semitone and a temporal pitch change.

The CI also verified exact constants, synthetic-only execution, non-promotion guards, no protected-song fixture and no real GuitarSet/IDMT holdout access.

Method record:
`docs/checkpoints/SONGSTERR_FRESH_POLYPHONIC_HARMONIC_NECESSITY_V5.md`
commit `73e451b17f514909f204ca1a6f5fe7a5c96f6bfc`.

### Current interpretation

V5 has demonstrated that its polyphonic formulation is mathematically viable on the frozen synthetic contract and directly improves the structural weakness that motivated the successor: simultaneous true chord tones can coexist in the explanation rather than competing for one global pitch winner.

This is meaningful engineering progress but **not** real-guitar admission evidence.

### Next V5 gate

1. inventory candidate external corpora against repository history and reject anything already materially analyzed;
2. choose a genuinely untouched corpus or untouched preregistered partition using metadata/inventory only;
3. freeze exact dataset/version/files, mechanical exclusions, annotation semantics, Basic Pitch runtime/settings, matching protocol, uncertainty method, minimum positive count, overall/stratum pass gates, source/runtime/provenance and fail-closed policy boundary **before** any correctness result;
4. controlled validation-harness CI with no real holdout access;
5. one official external V5 correctness run;
6. immutable result record;
7. separate policy review.

Until step 7 explicitly approves V5:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration paused
- protected song embargoed.

## FRESH-CHAT RESUME / NEXT STEPS

A fresh chat must begin by reading this file in full and treating it as authoritative. Work only on `songsterr-fresh-pipeline-v1`.

V1–V4 are closed. V5 is the only active successor. Its implementation and 20-case synthetic contract are green. The next permitted work is untouched-holdout metadata/inventory and preregistration only; do not score a real corpus until the exact external-validation contract is frozen.

Do not rerun/tune GuitarSet or IDMT, do not touch the protected song, and do not resume duration, archived V143/Gomyway, GOAT, reference scoring, broad threshold sweeps or training/fine-tuning.

Keep this checkpoint updated at major holdout selection, preregistration, validation-harness CI, external-result and policy-review boundaries.

## STILL FORBIDDEN

- IDMT V4 rerun/tuning
- GuitarSet rerun/tuning
- protected-song execution under V4 or V5 before future external validation + policy approval
- duration research
- archived V143/Gomyway / GOAT / reference scoring
- broad threshold sweeps
- training/fine-tuning
- customer promotion without passing preregistered external validation and separate policy approval.
