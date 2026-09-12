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
Historical protected-song outcomes may not tune successors.

V3 is closed after GuitarSet v1.1.0 external validation failed preregistered gates. GuitarSet is historical only and is not an untouched V5 holdout.

## V4 — CLOSED / REJECTED AS ADMISSION AUTHORITY

V4 implementation:
`scripts/songsterr-fresh/independent_pitch_corroboration_v4.py`
commit `6e9e11e60d0d6958c30edf6bb5d686d545936a19`.

Official V4 result record:
`docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_RESULT.md`
commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`.

Official V4 result artifact SHA-256:
`d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`.

V4 aggregate:
- 568/568 files
- 7,619 decoded
- 1,644 positive
- 1,292 correct
- precision `0.7858880778588808`
- one-sided 95% Wilson lower bound `0.7687844934184139`
- required `0.9900` → FAIL.

Policy review:
`docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_POLICY_REVIEW.md`
commit `01a276045d32b643aa17013b959e89e41b0f305e`.

Decision: **V4 CLOSED / REJECTED AS ADMISSION AUTHORITY.** IDMT is historical only and is not an untouched V5 holdout.

## V5 — ACTIVE SUCCESSOR / SYNTHETIC CONTRACT GREEN

User explicitly authorized V5 on 2026-09-12 to fix the prior failure mechanism.

### V5 preregistration

`docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`
commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`.

Contract:
`songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.

V5 is not a V4 threshold retune. It uses a polyphony-aware harmonic dictionary and selected-pitch leave-one-out NNLS necessity test.

Frozen design:
- mono isolated guitar, 44,100 Hz;
- existing onset + existing MIDI 40..88 only;
- windows: 8192 samples at offsets `2048`, `8192`, `14336`;
- FFT `32768`;
- MIDI dictionary 40..88;
- harmonics 1..8, `1/h` weights, L2 normalization;
- deterministic NNLS, SciPy `1.15.3`, NumPy `1.26.4`;
- necessity fraction `>=0.01`;
- fundamental/max-own-harmonic ratio `>=0.05`;
- all 3 views required;
- RMS `<1e-4`, truncation or invalid evidence => insufficient;
- no duration, next onset, Basic Pitch confidence/activation, reference truth, style/dataset/bit-depth identity or event rewriting.

### Implementation / synthetic freeze

Implementation:
`scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`
commit `0b02fc949ba9fa0e3fac6b2edb9f19002f58fc99`.

Synthetic manifest:
`docs/checkpoints/SONGSTERR_FRESH_V5_SYNTHETIC_FIXTURES.json`
commit `efca2994efdce2c5a3b35d6e12fb9dc82096a268`.

Controlled CI:
`.github/workflows/songsterr-fresh-v5-polyphonic-necessity-ci.yml`
run `34718020842`, job `103618636972`, source `7f07aa34ffb45860d55bcd755372abca98019717`: **SUCCESS**.

All 20 frozen synthetic fixtures matched exactly (`13 corroborated / 4 not / 3 insufficient`). V5 retained true selected notes in dyads, triads, a six-note mixture, a close dyad and a dominant-harmonic case while rejecting wrong octaves, a neighboring semitone and temporal pitch change.

Method record:
`docs/checkpoints/SONGSTERR_FRESH_POLYPHONIC_HARMONIC_NECESSITY_V5.md`
commit `73e451b17f514909f204ca1a6f5fe7a5c96f6bfc`.

This is meaningful synthetic progress but not admission evidence.

## V5 EXTERNAL HOLDOUT — FLGD STAGE A INVENTORY SELECTED / NO SCORING

Candidate: François Leduc Guitar Dataset (FLGD).

Selected canonical source:
- Hugging Face repository `xavriley/FrancoisLeducGuitarDataset` owned by dataset co-author Xavier Riley;
- exact verified revision `a38306c244b3ea81496ad58b4514622185e58211`;
- current provider card declares MIT;
- provider describes audio + aligned MIDI for 79 solo-guitar performances;
- reported repository size about 282 MB.

The older Zenodo v1.0.0 artifact is not selected. Its record explicitly redirects future research to the newer freely available Hugging Face version. V5 binds only the exact HF revision above.

Inventory-only preregistration:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_INVENTORY_PREREGISTRATION.md`
commit `9d039b8956a61336892d26f7763494a9440e4037`.

Untouched-holdout screening:
- GuitarSet: contaminated/historical → rejected;
- IDMT: contaminated/historical → rejected;
- Guitar-TECHS: historical checkpoint work exists → rejected;
- GAPS: scientifically attractive but upstream/current license terms conflict across official surfaces → not selected;
- EGFxSet: clearly open real electric-guitar data but isolated single tones, not sufficient primary polyphonic event holdout;
- isolated-guitar-chords: permissive and polyphonic but lacks exact event-level MIDI/onset truth needed for this admission metric;
- FLGD selected for Stage A because it is real solo guitar with aligned MIDI and no prior Songsterr Fresh correctness result identified.

Stage A is inventory-only. It may enumerate/hash files, inspect metadata/container/MIDI structure and mechanical audio/MIDI pairing. It MUST NOT run Basic Pitch, V5, Demucs, audio pitch analysis, estimate/reference matching or any correctness metric.

### Next V5 steps

1. implement deterministic FLGD inventory tool with no model/scoring imports;
2. controlled synthetic/local-directory CI for the inventory tool, with no FLGD data;
3. obtain exact HF revision outside the repo and run inventory once;
4. bind inventory report SHA-256 and exact audio/MIDI population;
5. freeze Stage B population, MIDI time semantics, Basic Pitch runtime/settings, matching, uncertainty, minimum positives, overall/stratum gates and provenance **before correctness**;
6. controlled validation-harness CI with no real FLGD correctness access;
7. one official FLGD V5 correctness run;
8. immutable result + separate policy review.

Until a later policy review explicitly approves V5:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration paused
- protected song embargoed.

## FRESH-CHAT RESUME / NEXT STEPS

Read this file first. Work only on `songsterr-fresh-pipeline-v1`.

V1–V4 are closed. V5 is active. Its implementation and synthetic contract are green. FLGD exact HF revision `a38306c244b3ea81496ad58b4514622185e58211` is selected for inventory-only Stage A. The immediate permitted work is to implement/CI the inventory tool and inventory the exact revision without any model correctness scoring.

Do not rerun/tune GuitarSet or IDMT, do not touch the protected song, and do not resume duration, archived V143/Gomyway, GOAT, reference scoring, broad threshold sweeps or training/fine-tuning.

Keep this checkpoint updated at inventory, Stage B preregistration, validation-harness CI, external-result and policy-review boundaries.

## STILL FORBIDDEN

- any V5 real-corpus correctness run before Stage B scoring preregistration + green contract CI
- IDMT V4/GuitarSet rerun or tuning
- protected-song execution before future V5 external validation + policy approval
- duration research
- archived V143/Gomyway / GOAT / reference scoring
- broad threshold sweeps
- training/fine-tuning
- customer promotion without passing preregistered external validation and separate policy approval.
