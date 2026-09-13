# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-13 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research, broad threshold/optimizer sweeps, training/fine-tuning and protected-song execution remain closed unless explicitly reopened.
- Never silently alter/drop MIDI or event identity. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP work stays under `scripts/songsterr-fresh/`.
- Authority is fail-closed: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, persistent Policy C `UNENROLLED`.
- No customer promotion, Production change, duration work or protected-song execution is authorized by the FLGD result alone.

## HISTORICAL CLOSED LINES

V1/V2 are rejected research diagnostics. GuitarSet/V3 and IDMT/V4 are closed and contaminated for future untouched-holdout use. Do not rerun/tune them.

V4 final: 568/568 files, 7,619 decoded, 1,644 positive, 1,292 correct, precision `0.7858880778588808`, one-sided 95% Wilson LB `0.7687844934184139` vs required `0.9900` → FAIL. Artifact SHA-256 `d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`; result commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`; policy rejection `01a276045d32b643aa17013b959e89e41b0f305e`.

## V5 — FROZEN METHOD / SYNTHETIC CONTRACT GREEN

User authorized V5 on 2026-09-12.

Preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`, commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`.
Contract: `songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.
Implementation: `scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`, commit `0b02fc949ba9fa0e3fac6b2edb9f19002f58fc99`.

Frozen V5 constants: mono 44.1 kHz; MIDI 40..88; 8192-sample windows at offsets 2048/8192/14336; FFT 32768; 8 harmonics; NNLS; RMS min `1e-4`; necessity fraction min `0.01`; fundamental/max-harmonic ratio min `0.05`; all 3 views required; NumPy 1.26.4; SciPy 1.15.3. No duration/end, confidence/activation, reference truth, performer/style/dataset identity or event rewriting.

Synthetic contract: 20 cases green (`13 corroborated / 4 not / 3 insufficient`). Synthetic success was never admission evidence.

## FLGD HOLDOUT — FROZEN SOURCE

François Leduc Guitar Dataset:
- HF `xavriley/FrancoisLeducGuitarDataset`
- origin `https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset`
- exact revision `a38306c244b3ea81496ad58b4514622185e58211`
- selected release declares MIT
- media remains outside app repo / must not be redistributed.

### Stage A — COMPLETE / NO SCORING

Run `34719034991`, job `103621353045`: SUCCESS.
Immutable record: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_STAGE_A_RESULT.md`, commit `b536f5c5eb479689fdd0d4d949b2715175d712aa`.
Report SHA-256: `f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3`.
Observed 79 canonical audio + 79 canonical MIDI, 79 exact pairs, zero ambiguous/unpaired. `test_set/` model outputs are forbidden as reference truth.

### Stage B — COMPLETE / IMMUTABLE / NO SCORING

Official Stage B run `34719744595`, job `103623274603`: SUCCESS.
Immutable record: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_RESULT.md`, commit `0bc647b112745953464f24eb0980e49ff348ebb2`.

Frozen Stage B identities:
- report SHA-256 `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`
- included-population SHA-256 `def77a45baf1b453e3f8ec0feed82e1cd3964bd85d50fb30f4912c0564425b02`
- reference-event identity SHA-256 `e34b360515d35dc77a6f423eb8a36e860e46f9469c16a499243186aea1f6223a`
- ignored-duplicate-release identity SHA-256 `8751a5425e3348b4e7005b09121bd43425c23a9f296b8f2e58c8da1c245fcfd3`
- 79 rows; split train 62 / validate 8 / test 9
- guitar types nylon 40 / electric 35 / acoustic 3 / electric-band 1
- 76,392 reference note events.

### Alignment semantics — FROZEN

Audit result: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_ALIGNMENT_SEMANTICS_RESULT.md`, commit `e62de24d49aa83d3f099da9a8ce723111961c27c`.
Canonical metadata-named MIDI note times under standard SMF/PrettyMIDI tempo semantics are authoritative audio-aligned reference times. Syncpoints do not warp note onset/offset correctness scoring.

### Final scoring contract — FROZEN

Preregistration: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_FINAL_SCORING_PREREGISTRATION.md`, commit `846cdedad46c10553569011a28ae01c72a9f6504`.
Numerical amendment: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_SCORING_NUMERICAL_AMENDMENT.md`, commit `2d547c6d034defebf8369db7f48fafcf15a02cec`.

Frozen scoring requirements:
- all 79 performances; no result-based exclusions;
- Basic Pitch 0.4.0 CPU, MIDI 40..88, onset 0.5, frame 0.3, minimum note length 127.7 ms, no pitch bends, melodia trick on;
- every decoded event preserved and V5-classified exactly once;
- only `independently-corroborated-candidate` is positive;
- deterministic maximum-cardinality matching, onset <=50 ms inclusive, pitch <=50 cents inclusive; offsets/durations ignored;
- pooled positives >=1000 and one-sided 95% Wilson LB >=0.9900;
- every split/guitar-type stratum with >=100 positives requires point precision >=0.9500;
- runtime/identity/event-preservation/policy guards must pass;
- a passing execution still requires separate policy review.

Harness record: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_SCORING_HARNESS.md`, commit `2509ccfe24ded590148110d8485f1b2e0ff6173d`.
Frozen experimental source: `6a3ea0808676ead13518e258fa912fd62a4eb33c`.

## OFFICIAL V5 CORRECTNESS EXECUTION — COMPLETE

Authorized wrapper: `.github/workflows/songsterr-fresh-flgd-v5-official-correctness.yml`, creation commit `66e93b11ae6d087a9c02d801f159e7bc5342e1ba`.

Single official run:
- workflow run `34748789583`
- job `103701492462`
- wrapper/head `66e93b11ae6d087a9c02d801f159e7bc5342e1ba`
- frozen source `6a3ea0808676ead13518e258fa912fd62a4eb33c`
- FLGD revision `a38306c244b3ea81496ad58b4514622185e58211`
- Stage B report SHA-256 `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`

All execution steps, including official scoring, result-identity verification, fail-closed policy verification and artifact upload, completed `success`.

Deferred-reveal safety remained valid: all 79 reference-blind phase-1 files completed before phase-2 scoring; no partial correctness progress was emitted.

## IMMUTABLE OFFICIAL RESULT — RECORDED / POLICY REVIEW PENDING

Immutable factual result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_OFFICIAL_CORRECTNESS_RESULT.md`

Result checkpoint commit:
`df6a306a055303a6f37b229bfc9e538803f25337`

Official artifact:
- name `flgd-v5-official-correctness-result`
- artifact ID `10316047064`
- archive SHA-256 `04bf94764c38346298f78d04ee8419f1f663091cc8abe31ee827f4c54df42fb7`
- result JSON SHA-256 `a79a09a695142ccd8c68d7d04089bb0d3ec675c11c6a39167f1e1cd0740b9c04`

Recorded result fields, without policy interpretation in this checkpoint update:
- completed files `79 / 79`
- decoded/classified events `84,577 / 84,577`
- positive events `43,349`
- positive correct `27,850`
- positive precision `0.642460033680131`
- one-sided 95% Wilson LB `0.6386648804090969`
- event preservation `true`
- population completeness `true`
- identity/runtime guards `true`
- policy-boundary guard `true`
- minimum-positive gate `true`
- overall-Wilson gate `false`
- split robustness: train `false`, validate `false`, test `false`
- guitar-type robustness: nylon `false`, electric `false`, acoustic `false`, electric-band `false`
- `allMandatoryGatesPassed:false`
- `externalValidationPassed:false`

Result policy fields remain fail-closed:
- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- protected song unused/embargoed
- separate policy review required.

The FLGD holdout is now revealed. Do not rerun this holdout under the V5 preregistration and do not tune V5, Basic Pitch settings, thresholds, tolerances, matcher, files, strata, gates or holdout selection against this result.

## NEXT ALLOWED ACTION

Conduct the separate V5 policy review from the immutable result checkpoint. The policy review must not change the revealed experimental result and must preserve the no-rerun/no-post-hoc-tuning boundary.

Until that review is committed, keep `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority paused, protected song embargoed and Policy C `UNENROLLED`.

## STILL FORBIDDEN

- any V5 result-seeking rerun or post-result tuning under this preregistration
- post-hoc FLGD row/stratum selection
- use of `test_set/` model outputs as truth
- GuitarSet/IDMT rerun/tuning
- protected-song execution
- duration research
- archived V143/Gomyway / GOAT / reference scoring
- broad threshold sweeps / training / fine-tuning
- Production/customer promotion without a valid later policy authorization

## FRESH-CHAT HANDOFF

Continue from this file on `songsterr-fresh-pipeline-v1`. The official FLGD V5 result has been immutably recorded at commit `df6a306a055303a6f37b229bfc9e538803f25337`; the next action is the separate V5 policy review. Do not rerun FLGD V5 and do not resume archived V143/Gomyway unless the user explicitly reopens that scope.
