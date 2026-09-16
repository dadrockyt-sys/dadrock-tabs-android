# RESULT — SONGSTERR FRESH V7 KKT RAW-NECESSITY DIAGNOSTIC V1

Status: **COMPLETE_SYNTHETIC_KKT_RAW_NECESSITY_DIAGNOSTIC_NO_FINAL_DECISION**
Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## 1. SCOPE

This result freezes authoritative attempt 1 exactly as prospectively defined by:

`docs/checkpoints/SONGSTERR_FRESH_V7_KKT_RAW_NECESSITY_DIAGNOSTIC_PRE.md`

The attempt tests whether the broad all-49 fixed-feature raw NNLS representation can assign one omitted selected MIDI a **KKT-certified strict-necessity** meaning without transporting historical `0.01`, introducing a new raw-magnitude threshold, or using rank/top-K semantics.

This remains synthetic-only and measurement-only. It does **not** define a final successor classifier, a final composition rule, a reattack fallback, model validation, customer eligibility, or any real/media/model authority.

Archived V143/Gomyway remained untouched.

## 2. FROZEN IDENTITY

Prospective PRE:

- PRE commit: `4ea9c075ea02231206a7602457e028b65c2e7a9e`
- PRE blob: `7ac28d2afb3952838825ddad77f65296817686fa`

Executable pair:

- module: `scripts/songsterr-fresh/v7_kkt_raw_necessity_diagnostics_v1.py`
- module commit: `7020dc21d1cbcc89597f24511bd40bd37b4c9f60`
- module blob: `2daa9f7f6983a3ec894fc08a86e9bced7b1f96c4`
- test: `scripts/songsterr-fresh/test_v7_kkt_raw_necessity_diagnostics_v1.py`
- pair head: `788eec22bad9f0fe13e8854fe99fa15a42a24679`
- test blob: `a52d1316bfdd54f88656c34df676ecff3e2530bf`
- PRE-to-pair compare: exactly the two prospectively authorized added Python files.
- no diagnostic output was observed before the pair was frozen.

Workflow:

- `.github/workflows/songsterr-v7-kkt-raw-necessity-diagnostic-one-shot.yml`
- workflow/head commit: `282062c7ec9508048013c16b1f91ce1f0cf209ae`
- workflow blob: `f9a082bd15fda08e5a91b20e98a5596d98e7865c`

Attempt 1:

- run: `35119500201`
- job: `104873352558`
- attempt: `1`
- status: `completed`
- conclusion: `success`
- no rerun or rescue attempt occurred.

Artifact:

- name: `songsterr-fresh-v7-kkt-raw-necessity-diagnostic`
- artifact ID: `10456247666`
- size: `63669` bytes
- digest: `sha256:0a3b8af8c62855d60665dedeee938f2c9bfb24c06452544520806e6ec9b06bae`
- persisted files:
  - `kkt-raw-necessity-diagnostic.json`
  - `v3-regression.txt`

Frozen runtime/guards all passed:

- Python `3.10.21`
- NumPy `1.26.4`
- SciPy `1.15.3`
- exact dependency/blob guard: PASS
- compilation/static no-network/no-model/no-media/no-subprocess guard: PASS
- KKT diagnostic execution: PASS
- untouched V3 iteration-3 regression: PASS
- artifact preservation: PASS.

## 3. MECHANICAL RESULT

Persisted top-level diagnostic facts:

- matrix controls: `6`
- audio fixtures: `23`
- repetitions: `3`
- matrix deterministic: `true`
- audio deterministic: `true`
- onset-available audio fixtures: `19`
- KKT-certified selected raw columns among onset-available fixtures: `17`
- `finalDecisionDefined:false`
- `rawMagnitudeThresholdDefined:false`
- `rankCutoffDefined:false`
- `historicalNecessityThresholdApplied:false`
- `reattackFallbackDefined:false`
- `temporalDiagnosticReconstructed:false`
- real corpus evaluated: `false`
- model inference invoked: `false`
- Basic Pitch invoked: `false`
- network invoked: `false`
- customer-eligible events: `0`
- may advance delivery: `false`
- mechanical diagnostic status: `COMPLETE`.

Untouched V3 iteration-3 regression persisted:

- fixture count: `34`
- repetitions: `3`
- deterministic: `true`
- mismatch count: `0`
- result: `PASS`.

No frozen V3 behavior changed.

## 4. PROSPECTIVE MATRIX-CONTROL RESULT

All six controls matched their pre-output expected certificate exactly.

| Control | Expected certified | Observed | Selected normalized lower bound | Reduced KKT defect floor | Descriptive necessity |
| --- | --- | --- | ---: | ---: | ---: |
| `unique_selected_direction` | true | true | `0.9999999999999996` | `4.440892098500627e-16` | `0.5773502691896258` |
| `selected_absent` | false | false | `0.0` | `4.440892098500627e-16` | `0.0` |
| `duplicate_selected_column` | false | false | `-4.440892098500627e-16` | `4.440892098500627e-16` | `0.0` |
| `selected_in_cone_of_others` | false | false | `-4.440892098500627e-16` | `3.1401849173675503e-16` | `0.0` |
| `weak_unique_selected_direction` | true | true | `9.999999999999995e-09` | `4.440892098500627e-16` | `7.071067811865475e-09` |
| `zero_observation` | false | false | `0.0` | `0.0` | null |

The `weak_unique_selected_direction` control is particularly important: an independently necessary selected component at only `1e-8` scale is still certified because its lower-bound correlation exceeds the numerical KKT floor. Therefore this attempt did not secretly recreate a scientific raw-magnitude threshold.

The duplicate-column and selected-in-cone controls remain uncertified, as required by the convex geometry: if the reduced nonnegative cone already explains the selected direction, the omitted selected column is not strictly necessary.

## 5. AUDIO-FIXTURE KKT LANDSCAPE

The table below is descriptive measurement only. `Support valid` reproduces the already-frozen independent support view. `KKT certified` refers only to broad raw strict contribution under the all-49 fixed-feature problem.

| Fixture | Support valid | KKT certified | Selected full coeff. | Descriptive raw necessity | Selected lower bound | Reduced KKT floor |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `clean_low_m40` | true | true | `81.42611719531182` | `0.21180289618799777` | `61.51601560952787` | `8.817784490611978e-13` |
| `clean_mid_m64` | true | true | `82.2886791169392` | `0.05820153811877132` | `50.21289312766301` | `1.5920570024714863e-12` |
| `clean_high_m88` | true | true | `83.34615129631635` | `0.1751822283493485` | `78.80790844549941` | `1.0690965098197853e-12` |
| `detune_plus25_m64` | true | true | `83.77111083246429` | `0.06557124232685847` | `54.21616874736452` | `1.4325194896725787e-12` |
| `detune_minus25_m64` | true | true | `47.81726140085642` | `0.009315541348354626` | `14.47532464745636` | `1.264323098913188e-12` |
| `attack_noise_true_m64` | true | true | `61.75829466696418` | `0.05872309311957527` | `37.72807175159601` | `1.2232801823052344e-12` |
| `already_sounding_m64` | false | false | `0.0` | `0.0` | `-6.177155953078174e-05` | `1.0590260003429784e-16` |
| `octave_alias_sel72_actual60` | true | true | `9.60673126119497` | `0.0006851135019640799` | `5.081976879973513` | `1.4835842299462893e-12` |
| `octave_alias_sel79_actual67` | true | false | `0.0` | `0.0` | `-0.8171773310896091` | `1.0506237925138775e-12` |
| `selected64_enters_over_existing60` | true | true | `37.96608594445441` | `0.014558336594470958` | `18.214334866568446` | `1.0963508114452132e-12` |
| `simultaneous_dyad_sel60` | true | true | `19.79690947013013` | `0.0041216775902363015` | `5.619920488522199` | `8.018934387707759e-13` |
| `simultaneous_dyad_sel64` | true | true | `42.11054768805029` | `0.05178270149633484` | `31.808066963098042` | `7.999819739733369e-13` |
| `simultaneous_triad_sel60` | true | true | `28.67770830051942` | `0.03996589910876862` | `22.18993994411353` | `5.399884403364511e-13` |
| `simultaneous_triad_sel64` | true | true | `20.669392088273124` | `0.011551106328093808` | `8.967714248451486` | `5.439584377983466e-13` |
| `simultaneous_triad_sel67` | true | true | `31.700422283759398` | `0.02679868547802654` | `12.522282274221473` | `5.698825201178812e-13` |
| `neighbor_sel60_actual61` | false | true | `29.458002182144444` | `0.0041471827861076635` | `7.840505408028372` | `1.0222973495308827e-12` |
| `reattack_m64` | false | true | `54.99900510742498` | `0.05310246072441282` | `49.9003990776755` | `1.267929865606315e-12` |
| `unrelated_transient_only_sel64` | false | true | `1.559210117795339` | `0.0023185831926859383` | `1.1516790639454904` | `8.862487166022361e-14` |
| `weak_selected64_under60` | false | true | `7.46066304216481` | `0.0008448320887965837` | `5.802452891860008` | `1.2908368974696735e-12` |

The four unavailable fixtures remain unavailable and no certificate is fabricated:

- `silence` — `INSUFFICIENT_LOW_AUDIO_SUPPORT`
- `low_noise` — `INSUFFICIENT_LOW_AUDIO_SUPPORT`
- `truncated_pre_context` — context error
- `truncated_post_context` — context error.

## 6. FROZEN INTERPRETATION

### 6.1 KKT supplies a genuine threshold-free raw-contribution semantic

The prospective matrix controls and all mechanical consistency gates passed. Under the frozen all-49 fixed-feature raw NNLS representation, the selected MIDI can therefore be assigned a mathematically grounded binary statement:

> the selected raw column is, or is not, KKT-certified as a strict positive descent direction from the selected-omitted NNLS optimum beyond the reduced solver's own numerical stationarity/error floor.

This is materially different from choosing a raw-necessity fraction cutoff after observing fixtures. Its scientific boundary is the NNLS KKT boundary at zero; its finite-precision floor is self-derived from the same reduced solve and explicit float64 arithmetic bounds.

This result does not claim that KKT strict necessity is sufficient for a correct guitar birth.

### 6.2 Historical `0.01` is directly shown to be non-portable

`detune_minus25_m64` has descriptive broad-raw necessity

`0.009315541348354626`,

which lies below historical `0.01`, yet its selected normalized KKT lower bound is

`14.47532464745636`

against a reduced KKT defect floor of only

`1.264323098913188e-12`,

and it is cleanly KKT-certified.

This supplies concrete synthetic evidence consistent with the prior theory review: historical `0.01` is not the mathematical boundary of the new representation and must not be transported to it.

### 6.3 KKT raw necessity cannot replace lower-owner protection

`octave_alias_sel72_actual60` is KKT-certified with descriptive raw necessity only `0.0006851135019640799`, but its already-frozen lower-owner diagnostics identify MIDI60 as a credible vetoing owner with three owner-exclusive supported bins and zero selected-exclusive supported bins.

Therefore raw strict contribution and lower-owner explanation are distinct semantics. KKT certification does not make this octave alias independently acceptable.

The second octave alias, `octave_alias_sel79_actual67`, is both owner-vetoed by MIDI67 and not KKT-certified. The two alias controls therefore also show that raw KKT can sometimes reject an alias by itself, but owner protection remains independently necessary because it catches cases raw strict contribution can still certify.

### 6.4 KKT raw necessity cannot bypass support/local-background protection

Four support-ineligible selected cases are nevertheless KKT-certified:

- `neighbor_sel60_actual61`
- `reattack_m64`
- `unrelated_transient_only_sel64`
- `weak_selected64_under60`.

This is not a contradiction. The raw fit asks whether the selected raw template supplies a unique descent direction in the broad raw observation. The support view asks a different physical question about leakage-cleaned multi-harmonic local support.

The result therefore reinforces the frozen semantic separation rather than collapsing it.

In particular, `reattack_m64` remains support-ineligible and KKT-certified. **This does not authorize a reattack fallback or raw-evidence bypass.** The inaccessible first temporal/support attempt remains authoritative and unresolved.

### 6.5 KKT also changes the interpretation of very small descriptive necessity

Several KKT-certified rows have descriptive raw necessity well below historical `0.01`, including:

- `simultaneous_dyad_sel60`: `0.0041216775902363015`
- `neighbor_sel60_actual61`: `0.0041471827861076635`
- `unrelated_transient_only_sel64`: `0.0023185831926859383`
- `weak_selected64_under60`: `0.0008448320887965837`
- `octave_alias_sel72_actual60`: `0.0006851135019640799`.

KKT certification says only that removing the selected raw column leaves a reduced optimum with a robust positive descent direction along that column. It does not say that the contribution is large, reliable as a birth, or sufficient for admission.

Therefore this attempt resolves the *raw contribution semantics* problem but not the *final composition/sufficiency* problem.

## 7. RESULT LABEL

`COMPLETE_SYNTHETIC_KKT_RAW_NECESSITY_DIAGNOSTIC_NO_FINAL_DECISION`

Attempt 1 establishes that:

1. the all-49 fixed-feature raw NNLS problem admits a prospectively justified, cutoff-free KKT strict-necessity certificate;
2. the certificate is deterministic and passes all six prospective matrix controls, including a `1e-8` unique-direction positive control;
3. the certificate is mechanically consistent with full/reduced residual improvement whenever it certifies;
4. historical descriptive raw necessity remains reproducible but no historical `0.01` is applied;
5. KKT raw necessity is an independent raw-contribution dimension, not a replacement for support eligibility, lower-owner veto, candidate-evidence significance, or temporal/support semantics;
6. no rank/top-K/maximum-only rule, candidate subset, learned score, per-MIDI exception or reattack fallback is defined;
7. no final successor classifier is defined.

## 8. NEXT RESEARCH BOUNDARY

The raw-necessity **boundary** problem is now materially narrower: broad raw contribution can be expressed without a tuned numeric threshold.

The remaining composition problem is still unresolved. A later final-composition PRE would need a genuinely prospective justification for how support eligibility, frozen candidate-evidence significance, frozen owner protection and KKT strict raw contribution combine as a decision rule. It must not infer such aggregation from this attempt's fixture outcomes.

The reattack temporal/support dimension remains an independent blocker and cannot be bypassed merely because `reattack_m64` is KKT-certified.

Any future executable composition requires a new prospective PRE before code/output. Any real/media/model route requires a new real-evaluation PRE plus fresh explicit user authorization.

## 9. AUTHORITY UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

No frozen V6/V3/V7 result was rewritten. No Production/main change occurred. Archived V143/Gomyway remained untouched.