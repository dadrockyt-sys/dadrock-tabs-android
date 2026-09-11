# Songsterr Fresh — IDMT V4 External Validation Result

Status: **IMMUTABLE OFFICIAL RESULT / FAILED FROZEN GATES / NOT ADMISSION AUTHORITY**

Recorded: 2026-09-11 America/Toronto

Branch: `songsterr-fresh-pipeline-v1`

## Result artifact identity

Official external-validation result artifact:
- local result path at execution time: `/workspaces/.songsterr-fresh-idmt-v4-official-ef92d873/idmt-v4-official-result.json`
- SHA-256: `d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`

Execution source:
- Git commit: `ef92d873ed6cdb6b78fe06e42d0b8ffd24cce237`
- worktree clean at execution start/end per harness

Dataset/input identities were frozen before scoring:
- IDMT-SMT-Guitar Dataset v1.0.0
- DOI `10.5281/zenodo.7544110`
- archive MD5 `06796e08731bccffaed6ae59361486e4`
- archive SHA-256 `02816258252538603c051054219cb4bba1c0ae8c9d0a3ca5418dfc951eae997a`
- Stage A report SHA-256 `fd9086891a9a699619810f4bccd6f0f2533c194afc6cc1b09cf80484626d704f`
- Stage B manifest result SHA-256 `dfea0060296ea2289e82041545e8da0f80dd81c5dee6668e8bc7ab08293bbdeb`
- included-manifest SHA-256 `0c7946f6ac5af341bcca155a24189c4cd85b9366c0cab3282469ad43236ca344`
- included files: `568`
- reference events: `4661`

## Runtime provenance

- Python `3.10.21`
- `basic-pitch==0.4.0`
- `numpy==1.26.4`
- `soundfile==0.13.1`
- `librosa==0.11.0`

Implementation hashes captured by the official result:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_NUMERICAL_AMENDMENT.md` → `d75b7f55157ce8db1f3489d319d93086259ce9719ad91ac524fa365b65fabe7d`
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_PREREGISTRATION.md` → `67afbe43543237819aa415e2c7b9fd91bca8933db6d9612edca6fbab21857b9a`
- `scripts/songsterr-fresh/external_idmt_v4_validation.py` → `9c2b6e359e2cefb65ee49f5b89cc1d2ab60ce0f73447fcacd02f0a7edd3e4cae`
- `scripts/songsterr-fresh/independent_pitch_corroboration_v4.py` → `734ea1e7eff59c1a215cfe3fd8688f01d45aa0e763b09da661dd1aa0582807e7`
- `scripts/songsterr-fresh/run_external_idmt_v4_validation.py` → `f2674e0850b7fbff511da14d35456a4839ab3c4b2df5cd9da442dd103f452b0d`
- `scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py` → `bedaa641165e7a524b8d4e519dd82d73b92b847f13fe8055e2c60c7d12c7e93b`

## Frozen scoring contract

The scoring contract was committed before any IDMT correctness result:
- per-file one-to-one maximum-cardinality bipartite matching;
- onset absolute difference `<= 0.050 s`;
- pitch absolute difference `<= 50 cents`;
- note offsets ignored;
- inclusive floating-point boundary preserved with a preregistered `1e-12` absolute numerical epsilon only;
- primary metric: precision among V4-positive events;
- uncertainty: one-sided 95% Wilson lower bound with `z=1.6448536269514722`.

Mandatory gates were frozen before scoring:
- all 568 files complete;
- at least 1000 V4-positive events;
- pooled one-sided 95% Wilson lower bound `>= 0.9900`;
- dataset1 and dataset2 each require at least 100 positives and point precision `>= 0.9500`;
- dataset3 pooled/diagnostic only because only four files were preregistered;
- each sample-width stratum with at least 100 positives requires precision `>= 0.9500`;
- identity and policy guards remain intact.

## Official aggregate result

- completed files: `568 / 568`
- reference events: `4661`
- decoded events: `7619`
- classification counts:
  - `independently-corroborated-candidate`: `1644`
  - `not-independently-corroborated`: `5906`
  - `insufficient-evidence`: `69`
- V4-positive events: `1644`
- V4-positive correct events: `1292`
- V4-positive precision: `0.7858880778588808`
- one-sided 95% Wilson lower bound: `0.7687844934184139`
- required lower bound: `0.9900`
- positive recall: `0.27719373524994634`

Diagnostic baseline only:
- baseline correct count: `3752`
- baseline precision: `0.4924530778317365`

## Strata

Dataset strata:
- dataset1: 312 files; 323 positives; 309 correct; precision `0.9566563467492261` → PASS
- dataset2: 252 files; 1293 positives; 958 correct; precision `0.7409126063418406` → FAIL
- dataset3: 4 files; 28 positives; 25 correct; precision `0.8928571428571429` → diagnostic only

Sample-width strata:
- 16-bit / sample width `2`: 316 files; 351 positives; 334 correct; precision `0.9515669515669516` → PASS
- 24-bit / sample width `3`: 252 files; 1293 positives; 958 correct; precision `0.7409126063418406` → FAIL

Frozen gate outcomes:
- `allIncludedFilesCompleted:true`
- `minimumTotalPositiveEvents:true`
- `overallWilsonLowerBound:false`
- `dataset1:true`
- `dataset2:false`
- `sampleWidthBytes2:true`
- `sampleWidthBytes3:false`
- `externalValidationPassed:false`

## Policy boundary preserved

The official artifact reports:
- `externalValidationPassed:false`
- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`
- `protectedSongUsed:false`
- `demucsInvoked:false`
- `separatePolicyReviewRequired:true`

## Interpretation

V4 failed the preregistered external-validation contract. The pooled precision/Wilson requirement failed by a wide margin, and mandatory dataset2 and 24-bit sample-width gates also failed.

This result MUST NOT be used to justify post-hoc threshold changes, exclusions, retuning, IDMT reruns, protected-song execution, or customer promotion under V4. The result is retained as an immutable research diagnostic only.
