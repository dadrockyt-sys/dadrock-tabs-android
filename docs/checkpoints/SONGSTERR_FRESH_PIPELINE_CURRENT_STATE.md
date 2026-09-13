# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-13 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research, broad threshold/optimizer sweeps, training/fine-tuning and protected-song execution remain closed unless the user explicitly reopens them.
- Never silently alter/drop MIDI or event identity. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP work stays under `scripts/songsterr-fresh/`.
- Current authority is fail-closed: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`.
- Protected song remains embargoed. No Production or customer-admission change is authorized.

## HISTORICAL CLOSED LINES

V1/V2 are rejected research diagnostics.

GuitarSet/V3 and IDMT/V4 are closed and contaminated for future untouched-holdout use. Do not rerun/tune them.

V4 final: 568/568 files, 7,619 decoded, 1,644 positive, 1,292 correct, precision `0.7858880778588808`, one-sided 95% Wilson LB `0.7687844934184139` vs required `0.9900` → FAIL. Artifact SHA-256 `d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`; result commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`; policy rejection `01a276045d32b643aa17013b959e89e41b0f305e`.

## V5 — CLOSED / EXTERNAL VALIDATION FAILED / ADMISSION REJECTED

User authorized V5 on 2026-09-12.

Preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`, commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`.
Contract: `songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.
Implementation: `scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`, commit `0b02fc949ba9fa0e3fac6b2edb9f19002f58fc99`.

Frozen V5 constants: mono 44.1 kHz; MIDI 40..88; 8192-sample windows at offsets 2048/8192/14336; FFT 32768; 8 harmonics; NNLS; RMS min `1e-4`; necessity fraction min `0.01`; fundamental/max-harmonic ratio min `0.05`; all 3 views required; NumPy 1.26.4; SciPy 1.15.3. No duration/end, confidence/activation, reference truth, performer/style/dataset identity or event rewriting.

Synthetic contract was green: 20 cases (`13 corroborated / 4 not / 3 insufficient`). Synthetic success never granted admission authority.

### FLGD frozen source

François Leduc Guitar Dataset:
- HF `xavriley/FrancoisLeducGuitarDataset`
- origin `https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset`
- exact revision `a38306c244b3ea81496ad58b4514622185e58211`
- selected release declares MIT
- media remains outside app repo / must not be redistributed.

Stage A run `34719034991`, job `103621353045`: SUCCESS.
Stage A record `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_STAGE_A_RESULT.md`, commit `b536f5c5eb479689fdd0d4d949b2715175d712aa`.
Stage A report SHA-256 `f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3`.

Stage B run `34719744595`, job `103623274603`: SUCCESS.
Stage B record `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_RESULT.md`, commit `0bc647b112745953464f24eb0980e49ff348ebb2`.
Stage B identities:
- report SHA-256 `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`
- included-population SHA-256 `def77a45baf1b453e3f8ec0feed82e1cd3964bd85d50fb30f4912c0564425b02`
- reference-event identity SHA-256 `e34b360515d35dc77a6f423eb8a36e860e46f9469c16a499243186aea1f6223a`
- ignored-duplicate-release identity SHA-256 `8751a5425e3348b4e7005b09121bd43425c23a9f296b8f2e58c8da1c245fcfd3`
- 79 performances / 76,392 reference note events
- split train 62 / validate 8 / test 9
- guitar types nylon 40 / electric 35 / acoustic 3 / electric-band 1.

Alignment result: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_ALIGNMENT_SEMANTICS_RESULT.md`, commit `e62de24d49aa83d3f099da9a8ce723111961c27c`.
Canonical metadata-named MIDI note times under standard SMF/PrettyMIDI semantics are authoritative audio-aligned reference times; syncpoints do not warp scoring times.

### Frozen final scoring contract

Preregistration: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_FINAL_SCORING_PREREGISTRATION.md`, commit `846cdedad46c10553569011a28ae01c72a9f6504`.
Numerical amendment: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_SCORING_NUMERICAL_AMENDMENT.md`, commit `2d547c6d034defebf8369db7f48fafcf15a02cec`.
Harness record: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_SCORING_HARNESS.md`, commit `2509ccfe24ded590148110d8485f1b2e0ff6173d`.
Frozen experimental source: `6a3ea0808676ead13518e258fa912fd62a4eb33c`.

Mandatory frozen bars included:
- all 79 performances, no post-result exclusions;
- event preservation;
- >=1,000 pooled V5 positives;
- pooled one-sided 95% Wilson lower bound >= `0.9900`;
- each split/guitar-type stratum with >=100 positives must have point precision >= `0.9500`;
- exact runtime/source/dataset identities and fail-closed policy guards.

### Official V5 correctness execution — COMPLETE

Wrapper: `.github/workflows/songsterr-fresh-flgd-v5-official-correctness.yml`, creation commit `66e93b11ae6d087a9c02d801f159e7bc5342e1ba`.

Single official execution:
- workflow run `34748789583`
- job `103701492462`
- wrapper/head commit `66e93b11ae6d087a9c02d801f159e7bc5342e1ba`
- frozen source `6a3ea0808676ead13518e258fa912fd62a4eb33c`
- FLGD revision `a38306c244b3ea81496ad58b4514622185e58211`
- Stage B report SHA-256 `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`.

All workflow steps completed `success`, including scoring, result-identity/fail-closed guard verification and artifact upload. All 79 reference-blind phase-1 files completed before phase-2 correctness scoring.

### Immutable official result

Record: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_OFFICIAL_CORRECTNESS_RESULT.md`.
Record commit: `df6a306a055303a6f37b229bfc9e538803f25337`.

Artifact:
- `flgd-v5-official-correctness-result`
- artifact ID `10316047064`
- archive SHA-256 `04bf94764c38346298f78d04ee8419f1f663091cc8abe31ee827f4c54df42fb7`
- result JSON SHA-256 `a79a09a695142ccd8c68d7d04089bb0d3ec675c11c6a39167f1e1cd0740b9c04`.

Valid execution/result facts:
- completed files `79 / 79`
- reference events `76,392`
- decoded/classified events `84,577 / 84,577`
- V5 positives `43,349`
- V5-positive correct `27,850`
- V5-positive precision `0.642460033680131`
- one-sided 95% Wilson LB `0.6386648804090969`
- event preservation `true`
- population completeness `true`
- identity/runtime guard `true`
- policy-boundary guard `true`
- minimum-positive gate `true`
- overall-Wilson gate `false`
- split robustness train/validate/test: all `false`
- guitar-type robustness nylon/electric/acoustic/electric-band: all `false`
- `allMandatoryGatesPassed:false`
- `externalValidationPassed:false`.

Split precision:
- train `0.6448439421444048`
- validate `0.6102185936265473`
- test `0.6500555761393109`.

Guitar-type precision:
- nylon `0.6206924676807635`
- electric `0.6705485035518808`
- acoustic `0.7239583333333334`
- electric-band `0.5577689243027888`.

The FLGD holdout is now revealed and may not be rerun under this V5 preregistration to seek a better result.

### Separate post-result policy review — COMPLETE

Policy review: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_POST_RESULT_POLICY_REVIEW.md`.
Policy review commit: `44c99d54ed7e728e85ef4042d1f15ba09643713c`.

Decision: **V5 ADMISSION REJECTED / FAIL-CLOSED**.

Reason: the valid official result did not meet the frozen pooled Wilson-LB >= `0.9900` admission bar and also failed every required split and guitar-type robustness gate. All mandatory gates were conjunctive; diagnostics cannot override a failed gate.

This decision is final for the V5/FLGD preregistration. Do not repair it through post-hoc V5 threshold changes, Basic Pitch changes, matching changes, alternate confidence intervals, file/stratum exclusions or FLGD reruns.

## AUTHORITY AFTER V5 REVIEW

Remain exactly:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged / research paused
- protected song embargoed
- Policy C `UNENROLLED`
- no Production change
- no `/ai-tab` admission change.

V5 may remain preserved as historical research code/artifacts but has no admission authority.

## CONTAMINATION / SUCCESSOR BOUNDARY

FLGD is now a revealed correctness corpus. GuitarSet/V3 and IDMT/V4 were already revealed/closed. None may be treated as untouched admission evidence for a successor method whose design is influenced by their results.

No successor research line is authorized by the V5 policy review itself.

If the user explicitly authorizes a successor method, it must be a new research/preregistration line, not a V5 result-seeking retune. Any future admission claim requires a new frozen protocol and a genuinely untouched external holdout selected before correctness is observed.

Do not use protected-song outcomes to develop or validate a successor admission method.

## STILL FORBIDDEN

- V5 FLGD rerun or post-result tuning
- V5 threshold/settings/matcher/tolerance/gate changes intended to rescue this result
- post-hoc FLGD row/file/split/guitar-type selection
- `test_set/` model outputs as truth
- GuitarSet/IDMT rerun/tuning
- archived V143/Gomyway / GOAT/reference scoring
- duration research
- protected-song execution
- broad threshold sweeps / training / fine-tuning
- Production/customer promotion without a new valid policy authorization.

## NEXT ALLOWED ACTION

No further research execution is authorized by the current scope.

Wait for explicit user authorization of a new successor research scope or explicit reopening of another closed scope. Do not infer authorization to begin V6 or to resume V143/Gomyway.

## FRESH-CHAT HANDOFF

Continue from this file on `songsterr-fresh-pipeline-v1`.

V5 official FLGD result is immutable at commit `df6a306a055303a6f37b229bfc9e538803f25337`; separate policy review is commit `44c99d54ed7e728e85ef4042d1f15ba09643713c`; V5 admission is rejected and all model/customer authority remains false/zero.

Do not rerun FLGD V5, do not start a successor without explicit user authorization, and do not resume archived V143/Gomyway unless the user explicitly asks.
