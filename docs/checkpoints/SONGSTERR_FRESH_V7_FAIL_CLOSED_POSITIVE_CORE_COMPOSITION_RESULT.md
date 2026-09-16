# RESULT — SONGSTERR FRESH V7 FAIL-CLOSED POSITIVE-CORE COMPOSITION V1

Status: **PASS_MECHANICAL_FAIL_CLOSED_POSITIVE_CORE / NO_REAL_CORRECTNESS**
Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## 1. SCOPE

This result freezes authoritative attempt 1 of the prospectively defined mechanical composition in:

`docs/checkpoints/SONGSTERR_FRESH_V7_FAIL_CLOSED_POSITIVE_CORE_COMPOSITION_PRE.md`.

The attempt tests only whether the already-frozen evidence/protection roles are composed exactly under the no-rescue tri-state rule.

It is **not** a correctness evaluation. The 23 frozen audio fixtures were used only for deterministic mechanical routing; their historical expected classifications were not used to compute or accept the new composition state. No class-count expectation was frozen.

No real/media/model work occurred. Archived V143/Gomyway remained untouched.

## 2. FROZEN IDENTITY

Theory review:

- `docs/checkpoints/SONGSTERR_FRESH_V7_POST_KKT_FAIL_CLOSED_COMPOSITION_REVIEW.md`
- commit `42e760e43a53ec0d17363b3905f64a8c0a5812a5`

Prospective PRE:

- PRE commit `b7cfc43b6bd7e80d9a05694b37d332f1ef540696`
- PRE blob `b7d62dce243bb8dc2e091ae6d3747691084f9b78`

Executable pair:

- module `scripts/songsterr-fresh/v7_fail_closed_positive_core_v1.py`
- module commit `5683830ebd0573b902bf205fe972a540fbaf37a9`
- module blob `6174a95c14a58ddd4dca47f021e591ebee8ee736`
- test `scripts/songsterr-fresh/test_v7_fail_closed_positive_core_v1.py`
- pair head `a96ea68eafcd6e1ff273ee2b6131af02453acdb1`
- test blob `975a2b5ad36144eee07f1e5c0035154903138544`
- PRE-to-pair compare contained exactly the two prospectively authorized added Python files.
- no composition output was observed before the pair was frozen.

Workflow:

- `.github/workflows/songsterr-v7-fail-closed-positive-core-one-shot.yml`
- workflow/head commit `60a53c25ae2c7ce46e3d5f0770a10eb278ea5614`
- workflow blob `4288b76426c4ef097956c3846720e0b91a75e92b`

Attempt 1:

- run `35121000102`
- job `104878449999`
- attempt `1`
- status `completed`
- conclusion `success`
- no rerun/rescue attempt occurred.

Artifact:

- name `songsterr-fresh-v7-fail-closed-positive-core`
- artifact ID `10457970208`
- size `64238` bytes
- digest `sha256:ed903776ca1f5bc28c6eec71499380c08ca97c04e6b58e20d8517e34282388eb`
- files:
  - `fail-closed-positive-core.json`
  - `v3-regression.txt`

Frozen guards all passed:

- Python `3.10.21`
- NumPy `1.26.4`
- SciPy `1.15.3`
- exact dependency/blob guard: PASS
- compilation/static no-network/no-model/no-media/no-subprocess guard: PASS
- explicit historical-necessity-threshold token guard: PASS
- positive-core mechanical harness: PASS
- untouched V3 iteration-3 regression: PASS
- artifact preservation: PASS.

## 3. PROSPECTIVE TRUTH-TABLE RESULT

The frozen exhaustive `2^4 = 16` truth-table was executed three times in-process.

Observed:

- truth-table row count `16`
- repetitions `3`
- deterministic `true`
- every row matched the prospectively frozen state/reason rule.

The authoritative rule therefore remained exactly:

- `S=false` -> `UNRESOLVED_SUPPORT_OR_CONTEXT` regardless of `E,O,K`;
- `S=true` and `E=true` and `O=true` and `K=true` -> `POSITIVE_CORE_CANDIDATE`;
- `S=true` with any failure among `E,O,K` -> `PROTECTION_REJECTED`, retaining all failed protection reasons in frozen order.

No rescue, vote, rank, score or weighted trade-off exists.

## 4. 23-FIXTURE MECHANICAL ROUTING RESULT

Persisted top-level facts:

- fixture count `23`
- repetitions `3`
- audio deterministic `true`
- historical expected classification used for computation: `false`
- class-count expectation frozen: `false`
- mechanical composition status `COMPLETE`
- `positiveCoreDefined:true`
- `customerDecisionDefined:false`
- `realCorrectnessDefined:false`
- `historicalNecessityThresholdApplied:false`
- `rawMagnitudeThresholdDefined:false`
- `rankCutoffDefined:false`
- `scoreDefined:false`
- `reattackFallbackDefined:false`
- `temporalDiagnosticReconstructed:false`
- real corpus evaluated `false`
- model inference invoked `false`
- Basic Pitch invoked `false`
- network invoked `false`
- customer-eligible events `0`
- may advance delivery `false`.

Observed descriptive composition counts, **not frozen acceptance targets**:

- `POSITIVE_CORE_CANDIDATE`: `12`
- `PROTECTION_REJECTED`: `2`
- `UNRESOLVED_SUPPORT_OR_CONTEXT`: `9`.

## 5. OBSERVED ROUTING INVENTORY

### `POSITIVE_CORE_CANDIDATE` — 12

All four frozen conditions were true (`S,E,O,K`):

- `clean_low_m40`
- `clean_mid_m64`
- `clean_high_m88`
- `detune_plus25_m64`
- `detune_minus25_m64`
- `attack_noise_true_m64`
- `selected64_enters_over_existing60`
- `simultaneous_dyad_sel60`
- `simultaneous_dyad_sel64`
- `simultaneous_triad_sel60`
- `simultaneous_triad_sel64`
- `simultaneous_triad_sel67`.

This list is descriptive only. Because the fixture labels were already exposed, it is not new correctness evidence.

### `PROTECTION_REJECTED` — 2

`octave_alias_sel72_actual60`

- support eligible `true`
- candidate evidence pass `true`
- no lower-owner veto `false`
- KKT certified `true`
- rejection reason: `LOWER_OWNER_VETO_PRESENT`.

This is the clearest mechanical demonstration that KKT raw contribution cannot rescue a frozen lower-owner veto.

`octave_alias_sel79_actual67`

- support eligible `true`
- candidate evidence pass `true`
- no lower-owner veto `false`
- KKT certified `false`
- rejection reasons:
  - `LOWER_OWNER_VETO_PRESENT`
  - `KKT_STRICT_RAW_NECESSITY_NOT_CERTIFIED`.

All applicable failed protections were retained; no single-reason overwrite occurred.

### `UNRESOLVED_SUPPORT_OR_CONTEXT` — 9

Support-ineligible with onset evidence available:

- `already_sounding_m64` — `S=false`, `K=false`
- `neighbor_sel60_actual61` — `S=false`, `K=true`
- `reattack_m64` — `S=false`, `K=true`
- `unrelated_transient_only_sel64` — `S=false`, `K=true`
- `weak_selected64_under60` — `S=false`, `K=true`.

Onset/context unavailable:

- `silence`
- `low_noise`
- `truncated_pre_context`
- `truncated_post_context`.

The key no-rescue condition is preserved: the four support-ineligible rows with `K=true`, including `reattack_m64`, remain unresolved rather than being promoted.

## 6. UNTOUCHED V3 REGRESSION

Persisted `v3-regression.txt`:

- contract `songsterr-fresh-v3-physical-template-evidence-significance-synthetic-test-v3`
- fixture count `34`
- repetitions `3`
- deterministic `true`
- mismatch count `0`
- result `PASS`.

No frozen V3 behavior changed.

## 7. FROZEN INTERPRETATION

### 7.1 The no-rescue composition is mechanically established

The attempt establishes that the ex-ante Boolean principle from the post-KKT theory review can be implemented exactly and deterministically over the frozen diagnostic packet.

The positive research state is now mechanically defined as:

`base support AND candidate-evidence significance AND no lower-owner veto AND KKT strict raw necessity`.

This definition adds no new scientific threshold and no cross-channel exchange rate.

### 7.2 The tri-state distinction is material

The attempt does not convert every non-positive proposal into the same scientific conclusion.

- Protection-rejected cases had valid support and evaluable protections that failed.
- Unresolved cases lacked selected support/context required by the positive-core contract.

That distinction prevents the unresolved temporal/support seam from being silently turned into a negative truth claim.

### 7.3 Reattack remains unresolved, not rescued

`reattack_m64` is again KKT-certified but selected-support-ineligible. The composition correctly routes it to `UNRESOLVED_SUPPORT_OR_CONTEXT`.

This is **not** a reattack solution. It is evidence that the new composition respects the existing blocker instead of bypassing it.

The original temporal/support attempt remains blocked by stored measurement access and must not be rerun or reconstructed.

### 7.4 Mechanical PASS is not correctness PASS

No fixture's historical expected classification was used to accept the new composition. The observed 12/2/9 distribution is descriptive only.

Therefore this result does not establish external precision, recall, or real-guitar reliability. It establishes software/semantic consistency of the prospectively frozen research rule.

## 8. RESULT LABEL

`PASS_MECHANICAL_FAIL_CLOSED_POSITIVE_CORE / NO_REAL_CORRECTNESS`

Attempt 1 establishes:

1. exhaustive truth-table correctness of the no-rescue rule;
2. deterministic 23-fixture mechanical routing without historical expected labels;
3. no historical `0.01` application;
4. no rank/top-K/raw cutoff/weighted score;
5. no KKT rescue of support-ineligible cases;
6. preservation of lower-owner rejection even when KKT is positive;
7. preservation of untouched V3 regression;
8. no real/model/customer authority.

## 9. NEXT RESEARCH BOUNDARY

The synthetic/mechanical composition problem is now materially closed enough to freeze a **candidate research method** for future external evaluation:

- positive-core candidate only when all four independent conditions clear;
- protection rejected when support is valid but one or more evaluable protections fail;
- unresolved when support/context is unavailable.

Further reuse of the already-exposed 23 fixtures cannot establish correctness and should not be used for method tuning.

The next substantive correctness step would require an untouched external real-data evaluation under a new prospective scoring/real-evaluation PRE and **fresh explicit user authorization**. That future PRE would need to freeze corpus/source identity, exact event population, canonical audio/model runtime, reference/alignment semantics, matching, uncertainty/statistics, treatment of unresolved cases, and pass/fail policy before any correctness output is exposed.

No such real evaluation is authorized by this result.

## 10. AUTHORITY UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

No Production/main change occurred. No closed line was reopened. Archived V143/Gomyway remained untouched.