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

GuitarSet is historical only.

## V4 — CLOSED / REJECTED AS ADMISSION AUTHORITY

V4 method preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`
- initial commit `a5cec402cf3bcd6c28ac3339d4d00de4d8cdf8b2`
- pre-implementation synthetic amendment `30b2769772d0a2a2edeaa8e92bff66ce3518fede`.

Frozen V4 implementation:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v4.py`
- commit `6e9e11e60d0d6958c30edf6bb5d686d545936a19`
- contract `songsterr-fresh-temporal-consensus-pitch-corroboration-research-v4`.

No protected-song V4 execution occurred.

## IDMT V4 INPUT / MANIFEST FREEZE

Dataset:
- IDMT-SMT-Guitar Dataset v1.0.0
- DOI `10.5281/zenodo.7544110`
- archive `IDMT-SMT-GUITAR_V2.zip`
- MD5 `06796e08731bccffaed6ae59361486e4`
- SHA-256 `02816258252538603c051054219cb4bba1c0ae8c9d0a3ca5418dfc951eae997a`.

Stage A inventory report SHA-256:
`fd9086891a9a699619810f4bccd6f0f2533c194afc6cc1b09cf80484626d704f`.

Stage B manifest freeze:
- output SHA-256 `dfea0060296ea2289e82041545e8da0f80dd81c5dee6668e8bc7ab08293bbdeb`
- included-manifest SHA-256 `0c7946f6ac5af341bcca155a24189c4cd85b9366c0cab3282469ad43236ca344`
- 568 included pairs / 1 mechanically excluded pair
- dataset1=312 / dataset2=252 / dataset3=4
- 4,661 reference note events.

## OFFICIAL IDMT V4 RESULT — IMMUTABLE FAILURE

Immutable result record:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_RESULT.md`
- commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`
- official result artifact SHA-256 `d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`.

Aggregate result:
- completed files `568 / 568`
- decoded events `7619`
- V4 positives `1644`
- correct positives `1292`
- positive precision `0.7858880778588808`
- one-sided 95% Wilson lower bound `0.7687844934184139`
- required lower bound `0.9900` → FAIL.

Separate policy review:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_POLICY_REVIEW.md`
- commit `01a276045d32b643aa17013b959e89e41b0f305e`.

Decision: **V4 CLOSED / REJECTED AS ADMISSION AUTHORITY.**
No IDMT V4 rerun, retuning, post-hoc filtering, protected-song V4 execution, or customer promotion is authorized.

## V5 — ACTIVE SUCCESSOR / SYNTHETIC DEVELOPMENT ONLY

User explicitly authorized a new successor on 2026-09-12 with the instruction to fix the failures.

V5 preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`
- commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`
- contract `songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.

V5 is intentionally **not** a V4 threshold retune. It replaces single-winner pitch corroboration with a polyphony-aware harmonic-necessity question: whether the selected Basic Pitch MIDI is independently necessary to explain the local harmonic spectrum when all playable guitar pitches are allowed to explain the signal simultaneously.

Frozen preregistered V5 inputs:
- mono isolated guitar, exactly 44,100 Hz;
- existing event onset as integer sample index;
- existing selected MIDI as integer, playable 40..88;
- no reference truth, duration/end, next onset, Basic Pitch confidence/activation, performer/style/dataset/bit-depth identity, downstream tablature or historical labels.

Frozen V5 signal design before implementation:
- three 8192-sample windows at post-onset offsets `2048`, `8192`, `14336`;
- FFT size `32768`, Hann after demeaning;
- full candidate MIDI dictionary 40..88;
- each candidate gets a coherent fundamental estimate inside its own semitone cell;
- nonnegative harmonic templates use harmonics 1..8 with `1/h` amplitude weighting and L2 normalization;
- simultaneous deterministic NNLS fit using SciPy `1.15.3`;
- selected-pitch necessity is measured by leave-one-selected-pitch-out residual increase;
- necessity fraction gate frozen at `>=0.01` of observed feature-vector L2 norm;
- fundamental-presence guard frozen at fundamental magnitude >= `0.05` of that candidate's strongest harmonic magnitude;
- all three temporal views must pass; no voting/fallback/majority rule;
- demeaned RMS below `1e-4`, truncation, invalid/nonfinite templates or solver failure => insufficient evidence.

V5 development contamination boundary:
- do not choose V5 constants from protected-song outcomes, GuitarSet V3 correctness, IDMT V4 correctness/strata, or post-hoc sweeps on observed holdouts;
- GuitarSet and IDMT are historical diagnostics only and are not untouched V5 admission holdouts;
- future external correctness scoring requires a different untouched holdout selected/frozen before results.

Next V5 steps, in order:
1. implement the frozen V5 corroborator under `scripts/songsterr-fresh/`;
2. freeze a deterministic synthetic fixture manifest covering monophonic range, detuning, chords/polyphony, octave traps, dominant harmonics, neighboring semitone, six-note mixture, attack noise, temporal change, silence/noise/truncation and event identity;
3. controlled synthetic/contract CI only; no real corpus access;
4. if the preregistered method is mathematically ill-posed on synthetic fixtures, document any synthetic-only amendment before using it; do not use real-corpus results to amend it;
5. only after implementation/CI is frozen green, select a genuinely untouched external holdout using metadata/inventory first;
6. freeze exact corpus manifest, annotation semantics, matching, uncertainty, minimum sample size and pass gates before any V5 correctness result;
7. one official external run, immutable result, then separate policy review.

V5 does not change authority. Current state remains:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration paused
- protected song embargoed.

## FRESH-CHAT RESUME / NEXT STEPS

A fresh chat must begin by reading this file in full and treating it as authoritative. Work only on `songsterr-fresh-pipeline-v1`.

V1–V4 are closed. V5 is the only active successor and is currently synthetic-development-only. Do not rerun/tune GuitarSet or IDMT, do not touch the protected song, and do not resume duration, archived V143/Gomyway, GOAT, reference scoring, threshold sweeps or training/fine-tuning.

Continue V5 from the ordered steps above. Keep this checkpoint updated at major preregistration, implementation, CI-freeze, external-result and policy-review boundaries.

## STILL FORBIDDEN

- IDMT V4 rerun/tuning
- GuitarSet rerun/tuning
- protected-song execution under V4 or V5 before future external validation + policy approval
- duration research
- archived V143/Gomyway / GOAT / reference scoring
- broad threshold sweeps
- training/fine-tuning
- customer promotion without passing preregistered external validation and separate policy approval.
