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

## HISTORICAL CLOSED WORK

V1/V2 are frozen research diagnostics rejected as admission authority.

Historical V2 protected-song result: 1,140 preserved events; 187 corroborated / 951 not / 2 insufficient. It cannot tune V4.

V3 is closed after GuitarSet v1.1.0 external validation failed preregistered gates:
- 357/357 tracks
- 62,438 decoded events
- 11,252 V3-positive
- 10,019 correct positives
- precision `0.8904194809811589`
- one-sided 95% Wilson lower bound `0.8854816094599652`
- required lower bound `0.9900` → FAIL.

GuitarSet is historical only and MUST NOT be reused as V4 pass/fail validation.

## V4 FROZEN METHOD

V4 preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`
- initial commit `a5cec402cf3bcd6c28ac3339d4d00de4d8cdf8b2`
- synthetic-only amendment `30b2769772d0a2a2edeaa8e92bff66ce3518fede`.

Frozen implementation:
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

No protected-song V4 execution has occurred.

## IDMT DATASET / STAGE A

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

Observed inventory:
- 4,292 ZIP members
- 1,173 WAV
- 667 XML
- 569 exact WAV/XML leaf-stem pairs
- dataset1=312 / dataset2=252 / dataset3=5 before mechanical filtering
- 512 unpaired WAV / 9 unpaired XML / 45 ambiguous stem groups.

Stage A performed no model inference or correctness scoring.

## IDMT STAGE B MANIFEST — FROZEN

Manifest result:
- output SHA-256 `dfea0060296ea2289e82041545e8da0f80dd81c5dee6668e8bc7ab08293bbdeb`
- included-manifest SHA-256 `0c7946f6ac5af341bcca155a24189c4cd85b9366c0cab3282469ad43236ca344`
- 568 included pairs / 1 mechanically excluded pair
- included counts dataset1=312 / dataset2=252 / dataset3=4
- 4,661 reference note events
- reference pitch range MIDI 40..92, all integer-valued
- onset range 0.19..68.0664 s
- offset range 1.4448..73.9406 s.

Stage B manifest generation performed no model inference or correctness scoring.

## FINAL V4 SCORING CONTRACT — FROZEN BEFORE RESULTS

Primary preregistration:
`docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_PREREGISTRATION.md`
commit `63c4a2ce74b7a9da213a176f76cfac781cec0769`.

Numerical-boundary amendment before any real correctness result:
`docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_NUMERICAL_AMENDMENT.md`
commit `4ee6f2c557c51fbeeaa626bdc12f790311117f36`.

Frozen matching:
- per-file one-to-one maximum-cardinality bipartite matching
- onset absolute difference <= 0.050 s
- pitch absolute difference <= 50 cents
- offsets ignored
- inclusive binary64 boundary implemented with `1e-12` absolute numerical epsilon only to preserve the preregistered inclusive boundary.

Primary metric:
- V4-positive precision
- one-sided 95% Wilson lower bound, `z=1.6448536269514722`.

Frozen gates:
1. all 568 files complete;
2. at least 1,000 V4-positive events;
3. pooled one-sided 95% Wilson lower bound >= 0.9900;
4. dataset1 >=100 positives and precision >=0.9500;
5. dataset2 >=100 positives and precision >=0.9500;
6. dataset3 pooled/diagnostic only because only four files;
7. any sample-width stratum with >=100 positives requires precision >=0.9500;
8. identity/policy guards intact.

## OFFICIAL VALIDATION HARNESS

Core harness:
`scripts/songsterr-fresh/external_idmt_v4_validation.py`
commit `6b48911b3694d9057b3da279fe7a8ba820395c76`.

Official entrypoint:
`scripts/songsterr-fresh/run_external_idmt_v4_validation.py`
commit `b4a224c399263bd8ecb906727f6d7331af4db5fe`.

Controlled official-entrypoint CI green:
- run `34657193712`
- job `103452045087`
- source `2d07d73aa3d6d5a6088eb26c53bf1905d22f7b78`.

Official scoring source commit:
`ef92d873ed6cdb6b78fe06e42d0b8ffd24cce237`.

## OFFICIAL IDMT V4 RESULT — COMPLETED / FAILED FROZEN GATES

The one official 568-file IDMT V4 holdout execution completed successfully in Codespaces on frozen source `ef92d873ed6cdb6b78fe06e42d0b8ffd24cce237`.

Observed aggregate result:
- completed files: `568 / 568`
- reference events: `4661`
- decoded events: `7619`
- classification counts:
  - `independently-corroborated-candidate`: `1644`
  - `not-independently-corroborated`: `5906`
  - `insufficient-evidence`: `69`
- V4-positive events: `1644`
- correct positives: `1292`
- positive precision: `0.7858880778588808`
- one-sided 95% Wilson lower bound: `0.7687844934184139`
- required lower bound: `0.9900` → **FAIL**
- positive recall: `0.27719373524994634`
- baseline correct count: `3752`
- baseline precision: `0.4924530778317365`.

Strata observed in the official result:
- dataset1: 323 positives / 309 correct / precision `0.9566563467492261` → mandatory dataset gate PASS
- dataset2: 1293 positives / 958 correct / precision `0.7409126063418406` → mandatory dataset gate FAIL
- dataset3: 28 positives / 25 correct / precision `0.8928571428571429` → diagnostic only
- sample width 16-bit (`2`): 351 positives / 334 correct / precision `0.9515669515669516` → gate PASS
- sample width 24-bit (`3`): 1293 positives / 958 correct / precision `0.7409126063418406` → gate FAIL.

Frozen gate outcomes:
- `allIncludedFilesCompleted:true`
- `minimumTotalPositiveEvents:true`
- `overallWilsonLowerBound:false`
- `dataset1:true`
- `dataset2:false`
- `sampleWidthBytes2:true`
- `sampleWidthBytes3:false`
- `externalValidationPassed:false`.

Runtime/provenance captured from the official artifact:
- source commit `ef92d873ed6cdb6b78fe06e42d0b8ffd24cce237`
- Python `3.10.21`
- Basic Pitch `0.4.0`
- NumPy `1.26.4`
- SoundFile `0.13.1`
- librosa `0.11.0`
- result-file SHA-256: **PENDING FINAL READ-ONLY CAPTURE FROM COMPLETED ARTIFACT**.

The result is a frozen external-validation failure. V4 MUST NOT be retuned, threshold-adjusted, post-hoc filtered, or rerun against IDMT under this preregistration.

Authority remains unchanged:
- `externalValidationPassed:false`
- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- protected song not used
- separate policy review required.

## NEXT REQUIRED STEP — CLOSE V4

1. Capture the exact SHA-256 of the completed `idmt-v4-official-result.json` artifact only; no rescoring/reexecution.
2. Write immutable V4 official result record binding that artifact hash, source/runtime/input identities and aggregate gates.
3. Write a separate V4 policy review rejecting V4 as admission authority because the frozen external-validation gates failed.
4. Update this checkpoint to CLOSED / REJECTED AS ADMISSION AUTHORITY.
5. Do not open a V5/successor without explicit user authorization.

## STILL FORBIDDEN

- any IDMT V4 rerun or tuning after this result
- protected-song V4 execution
- duration research
- GuitarSet rerun/tuning
- archived V143/Gomyway / GOAT / reference scoring
- threshold sweeps
- training/fine-tuning
- customer promotion from this failed result.
