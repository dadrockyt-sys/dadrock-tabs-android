# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-11 America/Toronto
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

Frozen rule:
- mono isolated guitar, 44,100 Hz;
- existing onset + integer selected MIDI only;
- full MIDI 40..88 spectral competition;
- three 8192-sample post-onset windows at offsets 1024 / 7168 / 13312;
- spectral strict global winner + YIN semitone-cell winner required in all three windows;
- no margins, voting, confidence, duration, next onset, activation, decision surface, reference, performer/style identity or event deletion.

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

Immutable Stage A result:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_STAGE_A_RESULT.md`
- commit `b5516dd0b2d84014f4e28d45bb04bce1ba0617ca`.

Stage B manifest freeze:
- output SHA-256 `dfea0060296ea2289e82041545e8da0f80dd81c5dee6668e8bc7ab08293bbdeb`
- included-manifest SHA-256 `0c7946f6ac5af341bcca155a24189c4cd85b9366c0cab3282469ad43236ca344`
- 568 included pairs / 1 mechanically excluded pair
- dataset1=312 / dataset2=252 / dataset3=4
- 4,661 reference note events.

## V4 OFFICIAL SCORING CONTRACT — FROZEN BEFORE RESULTS

Primary scoring preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_PREREGISTRATION.md`
- commit `63c4a2ce74b7a9da213a176f76cfac781cec0769`.

Pre-result numerical-boundary amendment:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_NUMERICAL_AMENDMENT.md`
- commit `4ee6f2c557c51fbeeaa626bdc12f790311117f36`.

Frozen matching/gates:
- per-file one-to-one maximum-cardinality matching;
- onset difference <= 0.050 s;
- pitch difference <= 50 cents;
- offsets ignored;
- primary metric = V4-positive precision;
- one-sided 95% Wilson lower bound with `z=1.6448536269514722`;
- all 568 files complete;
- >=1000 positives;
- pooled Wilson lower bound >=0.9900;
- dataset1 and dataset2 point precision >=0.9500 when >=100 positives;
- any sample-width stratum with >=100 positives precision >=0.9500;
- dataset3 diagnostic-only because only four files.

Official harness:
- core `scripts/songsterr-fresh/external_idmt_v4_validation.py`, commit `6b48911b3694d9057b3da279fe7a8ba820395c76`
- adapter `scripts/songsterr-fresh/run_external_idmt_v4_validation.py`, commit `b4a224c399263bd8ecb906727f6d7331af4db5fe`
- controlled CI run `34657193712`, job `103452045087`: SUCCESS.

Official scoring source commit:
`ef92d873ed6cdb6b78fe06e42d0b8ffd24cce237`.

## OFFICIAL IDMT V4 RESULT — IMMUTABLE FAILURE

Immutable result record:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_RESULT.md`
- commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`
- official result artifact SHA-256 `d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`.

Runtime:
- Python `3.10.21`
- Basic Pitch `0.4.0`
- NumPy `1.26.4`
- SoundFile `0.13.1`
- librosa `0.11.0`.

Aggregate result:
- completed files: `568 / 568`
- reference events: `4661`
- decoded events: `7619`
- classifications: 1644 corroborated / 5906 not / 69 insufficient
- positive correct: `1292 / 1644`
- positive precision `0.7858880778588808`
- one-sided 95% Wilson lower bound `0.7687844934184139`
- required lower bound `0.9900` → FAIL
- positive recall `0.27719373524994634`.

Strata:
- dataset1: 309/323, precision `0.9566563467492261` → PASS
- dataset2: 958/1293, precision `0.7409126063418406` → FAIL
- dataset3: 25/28, precision `0.8928571428571429` → diagnostic only
- 16-bit: 334/351, precision `0.9515669515669516` → PASS
- 24-bit: 958/1293, precision `0.7409126063418406` → FAIL.

Frozen gates:
- `allIncludedFilesCompleted:true`
- `minimumTotalPositiveEvents:true`
- `overallWilsonLowerBound:false`
- `dataset1:true`
- `dataset2:false`
- `sampleWidthBytes2:true`
- `sampleWidthBytes3:false`
- `externalValidationPassed:false`.

## V4 POLICY REVIEW — REJECTED

Separate policy review:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_POLICY_REVIEW.md`
- commit `01a276045d32b643aa17013b959e89e41b0f305e`.

Decision:
- **V4 is CLOSED / REJECTED AS ADMISSION AUTHORITY.**
- Dataset1/16-bit success cannot override pooled, dataset2, and 24-bit failures.
- no post-hoc subset selection, threshold adjustment, retuning, filtering, or IDMT rerun is authorized under V4;
- no protected-song V4 execution is authorized;
- result retained as research diagnostic only.

Authority remains unchanged:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused
- protected song not used.

## NEXT ALLOWED ACTION

There is no active successor.

Do **not** open V5 or any new model-evidence successor unless the user explicitly authorizes one. A successor must use a fresh preregistration before implementation/external scoring and must not tune against protected-song historical outcomes or reuse a previously observed admission holdout as though it were untouched.

The Codespace used for V4 may now be stopped; no active boot/session authority is needed.

## FRESH-CHAT RESUME / NEXT STEPS

A fresh chat must begin by reading this file in full and treating it as authoritative. Then:

1. Confirm work is still on branch `songsterr-fresh-pipeline-v1`; do not touch `main` or Production.
2. Preserve the current fail-closed authority state: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration paused.
3. Treat V1, V2, V3 and V4 as closed research diagnostics. Do not rerun/tune their holdouts and do not execute the protected song under V4.
4. Do not interpret a generic “continue” as permission to silently reopen archived V143/Gomyway, GOAT, reference scoring, duration, threshold sweeps, or training/fine-tuning.
5. Do not create or activate V5/a successor unless the user explicitly authorizes a new successor/model-evidence line.
6. If the user explicitly authorizes a successor, start with a **new preregistration before implementation**. The design must be derived from independent signal/model-validation principles and must not optimize specifically for V4’s observed dataset2/24-bit failure, protected-song history, GuitarSet results, or IDMT results.
7. Successor development should be synthetic/contract-only first. Freeze constants, input contract, event-identity guarantees, failure semantics, runtime/provenance, and non-promotion guards before external scoring.
8. Choose any future admission holdout before viewing correctness results, using metadata/inventory only at first. Previously observed GuitarSet and IDMT correctness results are not untouched holdouts and must not be reused as if they were.
9. Before any real external correctness run, freeze the exact corpus manifest, exclusions, annotation semantics, matching protocol, uncertainty method, minimum sample size, overall/stratum pass gates, source/runtime hashes, and fail-closed policy boundary.
10. Run controlled CI with synthetic fixtures and no real holdout access. Only after that source is frozen green may one official holdout execution occur.
11. After any future official holdout result, do not tune/rerun against that holdout. Write an immutable result record and a separate policy review. Only a passing preregistered external-validation result plus separate policy approval may change `modelValidationComplete` or customer eligibility.
12. Duration/release research remains paused until model-evidence admission is genuinely resolved by a future approved successor.
13. Keep this checkpoint updated at major preregistration, implementation, CI-freeze, external-result, and policy-review boundaries. Do not commit checkpoint changes during any boot/source-bound authority epoch if doing so would invalidate that epoch.

Recommended first fresh-chat user prompt if they want to continue the research line:

`Please continue from docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md on branch songsterr-fresh-pipeline-v1. I explicitly authorize opening a new successor after V4.`

If the user does not explicitly authorize a successor, stop at closed-state review/planning only.

## STILL FORBIDDEN

- IDMT V4 rerun/tuning
- protected-song V4 execution
- duration research
- GuitarSet rerun/tuning
- archived V143/Gomyway / GOAT / reference scoring
- threshold sweeps
- training/fine-tuning
- customer promotion from V4.
