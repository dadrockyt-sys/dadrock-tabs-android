# Songsterr Fresh — External GuitarSet Validation V3 Result

Status: **COMPLETE / FROZEN GATES FAILED / NOT ADMISSION AUTHORITY**

Recorded: 2026-09-11 America/Toronto

Preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`
- prereg commit `2dfd8c5d52093c36c0924e5f0b57eb2b2284e7d0`

Frozen method record:
- `docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3.md`
- provenance-complete method commit `1792739fa30c9304d37e94066794a38898dc98aa`

Official frozen source used for the external execution:
- branch `songsterr-fresh-pipeline-v1`
- commit `783c3b572aff4edd9d6298e9131dffd02454a61e`
- worktree clean during execution

## Execution note

The first official launch failed closed on the first track before any GuitarSet inference result was produced. The V3 harness resolved the supplied virtual-environment Python symlink to system Python, and the Basic Pitch child process failed immediately with `ModuleNotFoundError: No module named 'numpy'`. No completed inference JSON and no correctness result existed from that attempt.

The valid execution used a regular-file copy of the same pinned Python 3.10 executable inside the already-pinned workbench venv, so the harness could no longer dereference the interpreter path out of the venv. This changed no scorer logic, Basic Pitch setting, matching rule, dataset identity, exclusion, tolerance, or pass gate. The repository source remained the same frozen commit.

Pinned runtime observed in the valid execution:
- Python `3.10.21` / CPython
- machine `x86_64`
- Basic Pitch `0.4.0`
- NumPy `1.26.4`
- SoundFile `0.13.1`
- librosa `0.11.0`
- scipy `1.15.3`

## Locked corpus

Dataset: GuitarSet v1.1.0, DOI `10.5281/zenodo.3371780`.

Verified authorized archives:
- `annotation.zip` MD5 `b39b78e63d3446f2e54ddb7a54df9b10`
- `audio_mono-mic.zip` MD5 `275966d6610ac34999b58426beb119c3`

Preregistered exclusions only:
- `02_Funk2-119-G_comp`
- `04_BN3-154-E_comp`
- `04_Jazz1-200-B_comp`

Locked tracks completed: **357 / 357**.

## Frozen primary result

- decoded events: **62,438**
- V3-positive events: **11,252**
- correct V3-positive events: **10,019**
- V3-positive precision: **0.8904194809811589** (~89.04%)
- one-sided 95% Wilson lower bound: **0.8854816094599652** (~88.55%)

Preregistered pooled gate required Wilson lower bound `>= 0.9900`.

Result: **FAIL**.

The minimum-positive-count gate passed (`11,252 >= 1,000`) and all 357 tracks completed, but the pooled precision gate failed by a large margin.

## Frozen player strata

| Player | Correct | Positive | Precision | >= 0.9500 gate |
| --- | ---: | ---: | ---: | --- |
| 00 | 1,843 | 2,071 | 0.8899082568807339 | FAIL |
| 01 | 2,096 | 2,346 | 0.8934356351236147 | FAIL |
| 02 | 1,223 | 1,352 | 0.9045857988165681 | FAIL |
| 03 | 1,809 | 2,013 | 0.8986587183308494 | FAIL |
| 04 | 1,669 | 1,918 | 0.8701772679874870 | FAIL |
| 05 | 1,379 | 1,552 | 0.8885309278350515 | FAIL |

Every player had at least 50 positives, but every player failed the preregistered 0.9500 point-precision gate.

## Frozen mode strata

| Mode | Correct | Positive | Precision | >= 0.9500 gate |
| --- | ---: | ---: | ---: | --- |
| comp | 3,418 | 4,049 | 0.8441590516176833 | FAIL |
| solo | 6,601 | 7,203 | 0.9164237123420796 | FAIL |

Both modes had at least 50 positives, but both failed the preregistered 0.9500 point-precision gate.

## Artifact identities

Official outer result SHA-256:
- `e6edd37e72f24bef069d16b4accb48423b9472fe26eb90adee15e401e5b4196d`

Core result SHA-256:
- `9a2d103cfbe6f9c3bd8b7903c665affa41729ec2da7f303a5b1c416a2a532e4e`

Frozen implementation SHA-256 identities recorded by the official wrapper:
- `docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3.md`: `63a2283a7627f970e8f97b65ddcc2f377e55c67d7d826c3ddfe1a084fd553b6b`
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`: `bcd814d8d09abdd933ae0b6b058ac1d19d6920ecc2eb2d25448cccd1b456f22f`
- `scripts/songsterr-fresh/external_guitarset_validation_v3.py`: `f963749f729d68c28a8c2b7d41db6ae1523c4cb070059167c46bc9639b636c60`
- `scripts/songsterr-fresh/independent_pitch_corroboration_v2.py`: `102e95447ccbced240763edf370369953793aa2d02337415c99a8b68026c7daa`
- `scripts/songsterr-fresh/run_external_guitarset_validation_v3.py`: `343fc01d518018f163403df03d6857d99c1adedcbba7fde795cec6dc54683fdf`
- `scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py`: `bedaa641165e7a524b8d4e519dd82d73b92b847f13fe8055e2c60c7d12c7e93b`

## Frozen policy boundary after result

The external validation output itself retained:
- `externalValidationPassed:false`
- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`
- `separatePolicyReviewRequired:true`.

No protected-song V3 execution occurred. No V3 gate, threshold, scorer, exclusion, or matching rule may be relaxed or tuned after this result under the V3 preregistration.
