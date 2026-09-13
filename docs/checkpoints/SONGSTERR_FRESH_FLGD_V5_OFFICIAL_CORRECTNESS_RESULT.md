# IMMUTABLE RESULT — Songsterr Fresh FLGD V5 Official Correctness

Recorded: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: immutable factual result record; policy interpretation is intentionally deferred to a separate review.

## EXECUTION IDENTITY

- Workflow: `Songsterr Fresh FLGD V5 Official Correctness`
- Workflow path: `.github/workflows/songsterr-fresh-flgd-v5-official-correctness.yml`
- Workflow run ID: `34748789583`
- Job ID: `103701492462`
- Wrapper/head commit: `66e93b11ae6d087a9c02d801f159e7bc5342e1ba`
- Frozen experimental source: `6a3ea0808676ead13518e258fa912fd62a4eb33c`
- FLGD revision: `a38306c244b3ea81496ad58b4514622185e58211`
- Stage B run: `34719744595`
- Stage B artifact: `flgd-v5-stage-b-manifest-amended`, artifact ID `10305323053`
- Stage B report SHA-256: `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`

The official job completed successfully. Steps 1–12 and post-job cleanup all completed with conclusion `success`. The result-identity/fail-closed verification step printed `OFFICIAL_RESULT_GUARDS_VERIFIED` before artifact upload.

## OFFICIAL RESULT ARTIFACT

- Artifact name: `flgd-v5-official-correctness-result`
- Artifact ID: `10316047064`
- Artifact size: `19,977` bytes
- Artifact archive SHA-256: `04bf94764c38346298f78d04ee8419f1f663091cc8abe31ee827f4c54df42fb7`
- Artifact created: `2026-09-13T10:41:48Z`
- Result file: `flgd-v5-official-result.json`
- Result JSON SHA-256: `a79a09a695142ccd8c68d7d04089bb0d3ec675c11c6a39167f1e1cd0740b9c04`

The locally downloaded artifact ZIP independently reproduced the GitHub archive digest exactly, and the extracted result JSON independently reproduced the workflow-reported result SHA-256 exactly.

## FROZEN SOURCE / INPUT IDENTITIES

Result contract: `songsterr-fresh-flgd-v5-external-validation-v1`.

Source:
- branch: `songsterr-fresh-pipeline-v1`
- commit SHA: `6a3ea0808676ead13518e258fa912fd62a4eb33c`
- source worktree clean: `true`
- `independent_pitch_corroboration_v5.py` git blob: `4532d60ed43bf0cdf5878785c09df4006df37b29`
- `prepare_flgd_v5_stage_b_manifest_amended.py` git blob: `ecc6eaed2397b42b8e68a40f4bff1ce3c137fc8e`
- `transcribe_isolated_guitar_basic_pitch.py` git blob: `e9137496363f14cbe6194e32304c8b17b0b6569c`
- scoring preregistration SHA-256: `d6df9f08865e42f570700f884754aaf246d3f860b660a5f9a186ff3428fbe8eb`
- numerical amendment SHA-256: `360eb885dffa448f1404f0934d9fd65aebc50c753f4f7ef486d4ca045cc85355`

Dataset:
- origin: `https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset`
- revision: `a38306c244b3ea81496ad58b4514622185e58211`
- dataset worktree clean: `true`

Frozen input identities:
- Stage A report SHA-256: `f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3`
- Stage B report SHA-256: `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`
- included-population SHA-256: `def77a45baf1b453e3f8ec0feed82e1cd3964bd85d50fb30f4912c0564425b02`
- reference-event identity SHA-256: `e34b360515d35dc77a6f423eb8a36e860e46f9469c16a499243186aea1f6223a`
- ignored-duplicate-release identity SHA-256: `8751a5425e3348b4e7005b09121bd43425c23a9f296b8f2e58c8da1c245fcfd3`

## RUNTIME

- CPython `3.10.21`
- Linux x86_64
- Basic Pitch `0.4.0`
- NumPy `1.26.4`
- SciPy `1.15.3`
- librosa `0.11.0`
- SoundFile `0.13.1`
- CUDA disabled / CPU path

## DEFERRED-REVEAL SAFETY

- execution-safety contract: `songsterr-fresh-flgd-v5-deferred-correctness-reveal-v1`
- adapter SHA-256: `3b8ef7d659e3d5759d6a50a12e3cd282f304ed620509db199a8576951ae80f3a`
- reference-blind phase 1 required for all files: `true`
- phase-1 files completed before scoring: `79`
- partial correctness progress emitted: `false`

The log recorded `FLGD_V5_PHASE1_ALL_REFERENCE_BLIND_COMPLETE 79/79` before `FLGD_V5_PHASE2_SCORING_START`.

## POPULATION / EVENT PRESERVATION

- completed files: `79 / 79`
- reference events: `76,392`
- decoded events: `84,577`
- classified events: `84,577`
- classification counts:
  - independently-corroborated-candidate: `43,349`
  - not-independently-corroborated: `41,212`
  - insufficient-evidence: `16`
- event-preservation gate: `true`
- population-completeness gate: `true`
- identity/runtime guard: `true`
- policy-boundary guard: `true`

## FROZEN PRIMARY RESULT FIELDS

- positive events: `43,349`
- positive correct: `27,850`
- positive precision: `0.642460033680131`
- one-sided 95% Wilson lower bound: `0.6386648804090969`
- positive recall: `0.3645669703633888`
- minimum-total-positive-events gate: `true`
- overall-Wilson-lower-bound gate: `false`
- `externalValidationPassed`: `false`
- `allMandatoryGatesPassed`: `false`

Frozen overall requirement in the preregistration: pooled positives >= `1000` and pooled one-sided 95% Wilson lower bound >= `0.9900`.

## SPLIT STRATA

All listed strata exceed the preregistered 100-positive threshold and therefore carry the point-precision >= `0.9500` requirement.

- train: 62 files; 34,154 positives; 22,024 correct; precision `0.6448439421444048`; robustness gate `false`
- validate: 8 files; 3,797 positives; 2,317 correct; precision `0.6102185936265473`; robustness gate `false`
- test: 9 files; 5,398 positives; 3,509 correct; precision `0.6500555761393109`; robustness gate `false`

## GUITAR-TYPE STRATA

All listed strata exceed the preregistered 100-positive threshold and therefore carry the point-precision >= `0.9500` requirement.

- nylon: 40 files; 24,521 positives; 15,220 correct; precision `0.6206924676807635`; robustness gate `false`
- electric: 35 files; 17,174 positives; 11,516 correct; precision `0.6705485035518808`; robustness gate `false`
- acoustic: 3 files; 1,152 positives; 834 correct; precision `0.7239583333333334`; robustness gate `false`
- electric-band: 1 file; 502 positives; 280 correct; precision `0.5577689243027888`; robustness gate `false`

## BASELINE FIELD RECORDED BY HARNESS

- baseline correct count: `52,979`
- baseline precision: `0.6263996121877106`

This baseline field is recorded exactly as emitted by the frozen harness and is not used here to make any policy decision.

## FAIL-CLOSED POLICY FIELDS IN RESULT

- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`
- `protectedSongUsed:false`
- `separatePolicyReviewRequired:true`
- `demucsInvoked:false`
- `basicPitchInvoked:true`
- `v5ClassifierInvoked:true`
- `correctnessMetricComputed:true`
- `estimateReferenceMatchingPerformed:true`

## IMMUTABILITY / NEXT STEP

This file is the immutable factual record of the single authorized FLGD V5 official correctness execution. It records the revealed holdout result before any policy interpretation.

No V5 threshold, Basic Pitch setting, matching tolerance, matcher, file set, split, guitar-type stratum, gate, or holdout selection may be changed or rerun under this preregistration to seek a better result.

The only next step permitted by the frozen preregistration is the separate policy review. External-validation fields in this record do not themselves authorize Production, customer eligibility, delivery advancement, duration work, protected-song execution, or reopening archived V143/Gomyway / GOAT / reference-scoring research.
