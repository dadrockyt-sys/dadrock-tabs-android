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

## CLOSED HISTORICAL LINES

V1/V2 remain rejected research diagnostics. Historical protected-song outcomes may not tune successors.

V3 is closed after GuitarSet v1.1.0 failed frozen external-validation gates. GuitarSet is historical only and is not an untouched V5 holdout.

V4 is closed/rejected after IDMT external validation. Official V4 result record:
`docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_RESULT.md`
commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`.
Official artifact SHA-256:
`d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`.
V4 result: 568/568 files, 7,619 decoded, 1,644 positive, 1,292 correct, precision `0.7858880778588808`, Wilson LB `0.7687844934184139` vs required `0.9900` → FAIL.
Policy review commit `01a276045d32b643aa17013b959e89e41b0f305e`.
IDMT is historical only and is not an untouched V5 holdout.

## V5 — ACTIVE SUCCESSOR / SYNTHETIC CONTRACT GREEN

User explicitly authorized V5 on 2026-09-12 to fix the prior failure mechanism.

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`
commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`.
Contract `songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.

V5 is not a V4 threshold retune. It uses a polyphony-aware harmonic dictionary plus selected-pitch leave-one-out NNLS necessity test.

Frozen design:
- mono isolated guitar 44,100 Hz;
- existing onset + existing MIDI 40..88 only;
- three 8192-sample windows at offsets `2048`, `8192`, `14336`;
- FFT `32768`;
- playable MIDI dictionary 40..88;
- harmonics 1..8, `1/h` weights, L2-normalized;
- deterministic NNLS, NumPy `1.26.4`, SciPy `1.15.3`;
- necessity fraction `>=0.01`;
- selected fundamental / own max harmonic ratio `>=0.05`;
- all 3 views required; no voting/fallback;
- RMS `<1e-4`, truncation/invalid evidence/solver failure => insufficient;
- no duration/end, next onset, Basic Pitch confidence/activation, truth, performer/style/dataset/bit-depth identity or event rewriting.

Implementation:
`scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`
commit `0b02fc949ba9fa0e3fac6b2edb9f19002f58fc99`.

Synthetic manifest:
`docs/checkpoints/SONGSTERR_FRESH_V5_SYNTHETIC_FIXTURES.json`
commit `efca2994efdce2c5a3b35d6e12fb9dc82096a268`.

Controlled V5 CI:
run `34718020842`, job `103618636972`, source `7f07aa34ffb45860d55bcd755372abca98019717`: **SUCCESS**.
All 20 frozen cases matched (`13 corroborated / 4 not / 3 insufficient`). V5 retained true notes in dyads, triads, six-note mixture, close dyad and dominant-harmonic cases while rejecting wrong octaves, neighboring semitone and temporal pitch change.

Method record:
`docs/checkpoints/SONGSTERR_FRESH_POLYPHONIC_HARMONIC_NECESSITY_V5.md`
commit `73e451b17f514909f204ca1a6f5fe7a5c96f6bfc`.

This is meaningful structural/synthetic progress, not admission evidence.

## V5 EXTERNAL HOLDOUT — FLGD STAGE A INVENTORY FROZEN / GREEN / NO SCORING

Candidate: François Leduc Guitar Dataset (FLGD).

Selected source:
- Hugging Face `xavriley/FrancoisLeducGuitarDataset`;
- exact verified revision `a38306c244b3ea81496ad58b4514622185e58211`;
- author-owned current release card declares MIT;
- audio + aligned MIDI for 79 solo-guitar performances;
- reported size about 282 MB.

The older restricted Zenodo artifact is not selected; its record points future research to the newer freely available HF release. V5 binds only the exact HF revision above. Dataset media must stay outside this repository and must not be redistributed/shipped.

Inventory-only preregistration:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_INVENTORY_PREREGISTRATION.md`
commit `9d039b8956a61336892d26f7763494a9440e4037`.

Untouched-holdout screening:
- GuitarSet → historical/contaminated, rejected;
- IDMT → historical/contaminated, rejected;
- Guitar-TECHS → historical checkpoint work exists, rejected;
- GAPS → strong scientifically but conflicting official/current license surfaces, not selected;
- EGFxSet → clear open real electric-guitar data but isolated single notes, secondary stress candidate only;
- isolated-guitar-chords → permissive/polyphonic but lacks exact event-level MIDI/onset truth;
- FLGD selected for Stage A because it is real solo guitar with aligned MIDI and no prior Songsterr Fresh correctness result identified.

Inventory tool:
`scripts/songsterr-fresh/inventory_flgd_v5_external_validation.py`
commit `144c18cbc9cf354053b3edfbb537348318e1a59f`.
Contract `songsterr-fresh-flgd-v5-inventory-v1`.

Tool behavior:
- requires a clean Git checkout at exact FLGD revision;
- recursively inventories every regular file except `.git/` implementation metadata;
- hashes every file SHA-256;
- records extensions/sizes;
- records WAV container headers if present;
- records MIDI SMF headers;
- records `metadata.csv` columns/row count/value domains;
- mechanically pairs exactly one `audio/<stem>.*` to exactly one `midi/<stem>.mid|midi`;
- reports ambiguous/unpaired files rather than dropping them;
- no NumPy/SciPy/librosa/Basic Pitch/Demucs/Torch/songsterr_pipeline imports;
- no sample-domain pitch analysis, V5 classification, reference matching or correctness metric.

Inventory CI:
`.github/workflows/songsterr-fresh-flgd-v5-inventory-ci.yml`
commit `153767b4a3878c1d92f479b5bfa33cd78bef88b6`.
Run `34718347519`, job `103619499809`: **SUCCESS**.
CI used only a tiny synthetic local Git repository and confirmed real FLGD was absent. Compile, revision binding, hashes, metadata parsing, WAV/MIDI headers, exact pairing and all non-scoring guards passed.

Stage A policy boundary remains:
- Basic Pitch not invoked;
- V5 not invoked;
- Demucs not invoked;
- no audio pitch analysis;
- no estimate/reference matching;
- no correctness metric;
- protected song unused;
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration unchanged/paused.

### NEXT REQUIRED STEP — REAL FLGD INVENTORY ONCE

Obtain exact FLGD HF revision outside the application repository and run the frozen inventory tool once. The resulting JSON must remain outside repo initially and its SHA-256 must be captured.

Real Stage A inventory must establish, without scoring:
- exact file count/bytes/extension counts;
- exact audio and MIDI counts;
- exact one-to-one audio/MIDI pairs;
- ambiguous/unpaired files;
- metadata.csv identity/columns/row count/domains;
- audio container/header signatures where supported;
- MIDI header signatures;
- exact per-file SHA-256 identities;
- clean false/zero policy boundary.

Only after reviewing and binding that inventory may Stage B freeze exact population, MIDI timing semantics, Basic Pitch runtime/settings, matching, uncertainty, minimum positives, overall/stratum gates and provenance before any correctness result.

Then: controlled validation-harness CI with no real FLGD correctness access → one official FLGD V5 correctness run → immutable result → separate policy review.

Until a later policy review explicitly approves V5:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration paused
- protected song embargoed.

## FRESH-CHAT RESUME / NEXT STEPS

Read this file first. Work only on `songsterr-fresh-pipeline-v1`.

V1–V4 are closed. V5 is active. V5 synthetic contract and FLGD inventory-tool CI are green. The next permitted real-data operation is **FLGD Stage A inventory only** on exact HF revision `a38306c244b3ea81496ad58b4514622185e58211`; no Basic Pitch/V5 correctness scoring is authorized yet.

Do not rerun/tune GuitarSet or IDMT, do not touch the protected song, and do not resume duration, archived V143/Gomyway, GOAT, reference scoring, broad threshold sweeps or training/fine-tuning.

Keep this checkpoint updated at real inventory, Stage B preregistration, validation-harness CI, external-result and policy-review boundaries.

## STILL FORBIDDEN

- any V5 real-corpus correctness run before Stage B scoring preregistration + green contract CI
- IDMT V4/GuitarSet rerun or tuning
- protected-song execution before future V5 external validation + policy approval
- duration research
- archived V143/Gomyway / GOAT / reference scoring
- broad threshold sweeps
- training/fine-tuning
- customer promotion without passing preregistered external validation and separate policy approval.
