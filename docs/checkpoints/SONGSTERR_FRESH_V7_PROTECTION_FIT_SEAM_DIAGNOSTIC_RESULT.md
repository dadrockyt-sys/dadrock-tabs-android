# RESULT — Songsterr Fresh V7 Protection / Raw-Fit Seam Diagnostic V1

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_PROTECTION_FIT_SEAM_DIAGNOSTIC_PRE.md`
PRE commit: `727dd82fe51f7ba64a6434c867fdec57958405d9`

## Scope

This is a frozen **synthetic measurement-only** result. It defines no successor classifier, no final PASS/FAIL, no raw-necessity threshold, no transport of historical `0.01` onto the broad raw fit, no selected-note eligibility change, no temporal/reattack repair and no real/model implication.

The prospective question was whether the already-frozen support-side protections can be observed independently beside the already-frozen broad all-gate-free fixed-feature raw fit, without using the historical support-space NNLS composite as the sole acceptance path.

## Frozen implementation / execution identity

- PRE commit: `727dd82fe51f7ba64a6434c867fdec57958405d9`
- PRE blob: `4dd284fae7e7fa2d3881b0f8dca654f0bcd2ed6d`
- module commit: `bed75bf7bb529e5e0b2fd3473c22523dbeacc147`
- module blob: `1ca6a0f8579ae73577b34fa6ed2eb0a752f9d781`
- test / pair head: `39ff57f21aad90e516d06fdd2b1854d906ac03d7`
- test blob: `f384a8c8141e4bdaf9ef9e6a42c5754d3e9ff300`
- state-only pair checkpoint commit: `a049ae4d9679fd46d3ba13b3871c14b7bfc235a6`
- workflow/head commit: `03e21ae87082c9325751755ec9a8f6843a57dcb7`
- workflow: `.github/workflows/songsterr-v7-protection-fit-seam-diagnostic-one-shot.yml`
- workflow blob: `3e3d572e6c35cebebd363e1bad5eb83b2c42f0ef`
- run: `35059307767`
- job: `104676039333`
- attempt: `1`
- workflow conclusion: `success`
- artifact: `songsterr-fresh-v7-protection-fit-seam-diagnostic`
- artifact ID: `10431851835`
- artifact digest: `sha256:5389fdc3e9d0ee81555ec64f0bc19231fb910e54f320add1e58d255cc4d855fe`
- persisted files: `protection-fit-seam-diagnostic.json`, `v3-regression.txt`

The workflow-file push was the sole first execution trigger. There was no rescue rerun, threshold search, candidate search, metric selection or post-result fixture addition.

## Mechanical result

Attempt 1 completed with:

- fixture count: `23`
- repetitions: `3`
- deterministic: `true`
- onset-available rows: `19`
- selected support-template eligible rows: `14`
- independent owner-diagnostic available rows: `14`
- independent candidate-evidence available rows: `14`
- support-eligible rows whose historical support composite failed: `3`
- all-gate-free fixed-feature raw-fit available rows: `19`
- `finalDecisionDefined:false`
- `referenceExpectedUsedForComputation:false`
- `rawNecessityThresholdDefined:false`
- `temporalDiagnosticReconstructed:false`
- real corpus evaluated: `false`
- model inference invoked: `false`
- Basic Pitch invoked: `false`
- network invoked: `false`
- customer eligible events: `0`
- may advance delivery: `false`
- mechanical diagnostic status: `COMPLETE`.

The committed test gate exactly reproduced, for every onset-available row:

- the frozen dual-view support measurements;
- selected support template and support-valid MIDI list;
- independent lower-owner diagnostics;
- independent candidate-evidence diagnostics;
- the frozen all-gate-free fixed-feature raw fit;
- the full frozen dual-view/fixed-feature reference payloads;
- the historical frozen V7 raw-to-V3 reference result.

## Untouched V3 regression

The same first workflow attempt executed the untouched V3 iteration-3 regression:

- fixture count: `34`
- repetitions: `3`
- deterministic: `true`
- mismatch count: `0`
- result: `PASS`.

No frozen V3 behavior changed.

## Finding 1 — support protections remain observable when the old support-space necessity composite fails

Exactly three rows have an eligible selected support template while the frozen support-space iteration-3 composite is not PASS:

### `octave_alias_sel72_actual60`

- support template: `ELIGIBLE`
- support-valid candidates: `3`
- candidate-evidence fraction: `0.23530600965928458`
- frozen candidate-evidence minimum: `0.10` reference/protection only
- credible lower owners: `2`
- vetoing lower owners: `1`
- historical support composite: `FAIL_NECESSITY`
- broad fixed-feature raw necessity: `0.0006851135019640799`

### `octave_alias_sel79_actual67`

- support template: `ELIGIBLE`
- support-valid candidates: `3`
- candidate-evidence fraction: `0.2387584790923918`
- credible lower owners: `2`
- vetoing lower owners: `1`
- historical support composite: `FAIL_NECESSITY`
- broad fixed-feature raw necessity: `0.0`

### `selected64_enters_over_existing60`

- support template: `ELIGIBLE`
- support-valid candidates: `6`
- candidate-evidence fraction: `0.2077502515962489`
- credible lower owners: `3`
- vetoing lower owners: `0`
- historical support composite: `FAIL_NECESSITY`
- broad fixed-feature raw necessity: `0.014558336594470958`

**Frozen interpretation:** independent support protections are mechanically observable even when the old support-space necessity composite fails. In particular, the two octave aliases expose vetoing lower owners, while the entering-MIDI64 case exposes no veto and retains support evidence above the already-frozen candidate-evidence floor. This establishes a representation/role separation only; it does not define a final acceptance rule.

## Finding 2 — the frozen support eligibility/protection view differs materially from historical raw-to-V3 wiring

For all `19` onset-available fixtures, the historical frozen V7 reference that feeds **raw V6 innovation directly into V3 iteration 3** returns:

- `passed:false`
- status `SELECTED_TEMPLATE_INELIGIBLE`.

By contrast, the leakage-cleaned support view produces an eligible selected support template on `14/19` onset-available rows.

Those 14 include all clean/detuned/noisy true-onset controls, both octave aliases, `selected64_enters_over_existing60`, both dyad selected-note rows and all three simultaneous-triad selected-note rows.

**Frozen interpretation:** historical raw-to-V3 mechanical wiring does not reproduce the support-eligibility semantics exposed by the leakage-cleaned support view. Historical V7 remains frozen historical evidence; this result does not rewrite it and does not itself define its replacement.

## Finding 3 — all 14 support-eligible rows expose the independent candidate-evidence measurement

The `14` support-eligible rows all have candidate-evidence diagnostics available. Their measured candidate-evidence fractions range from:

- minimum: `0.2077502515962489` (`selected64_enters_over_existing60`)
- maximum: `0.49289823071783523` (`clean_high_m88`).

The existing frozen support-protection minimum is `0.10`; no new evidence threshold was introduced or searched.

No support-ineligible row fabricates candidate-evidence or owner diagnostics.

## Finding 4 — octave-alias lower-owner protection remains independently visible

The only support-eligible rows containing vetoing lower-owner diagnostics are the two prospectively named octave aliases:

- `octave_alias_sel72_actual60`: one vetoing owner;
- `octave_alias_sel79_actual67`: one vetoing owner.

Their broad fixed-feature raw necessities are respectively `0.0006851135019640799` and `0.0`.

This measurement preserves the frozen lower-owner protection independently from support-space necessity. It does not authorize a new aggregation rule between owner veto and raw fit.

## Finding 5 — broad raw fit differentiates the same-audio dyad selected notes while support protections remain non-vetoing

### `simultaneous_dyad_sel60`

- support template: eligible
- support candidates: `7`
- candidate-evidence fraction: `0.34678943650665484`
- credible lower owners: `1`
- vetoing owners: `0`
- historical support composite: `PASS`
- broad fixed-feature raw necessity: `0.0041216775902363015`

### `simultaneous_dyad_sel64`

- support template: eligible
- support candidates: `7`
- candidate-evidence fraction: `0.34516681610957956`
- credible lower owners: `2`
- vetoing owners: `0`
- historical support composite: `PASS`
- broad fixed-feature raw necessity: `0.05178270149633484`

The same raw fixed-feature observation geometry therefore preserves the previously frozen broad-competition separation between the two selected notes, while the support protections themselves do not veto either row.

**No threshold is inferred from these two values.** Historical `0.01` is not transported to this raw fit by this result.

## Finding 6 — prospectively named positive/support controls

All of the following have an eligible selected support template, no vetoing owner and available broad fixed-feature raw fit:

- `clean_low_m40`: evidence `0.38443223142641103`, raw necessity `0.21180289618799777`
- `clean_mid_m64`: evidence `0.48898158023734223`, raw necessity `0.05820153811877132`
- `clean_high_m88`: evidence `0.49289823071783523`, raw necessity `0.1751822283493485`
- `detune_plus25_m64`: evidence `0.48945307367320673`, raw necessity `0.06557124232685847`
- `detune_minus25_m64`: evidence `0.4885332732424455`, raw necessity `0.009315541348354626`
- `attack_noise_true_m64`: evidence `0.4844184329612066`, raw necessity `0.05872309311957527`
- `selected64_enters_over_existing60`: evidence `0.2077502515962489`, raw necessity `0.014558336594470958`
- `simultaneous_dyad_sel64`: evidence `0.34516681610957956`, raw necessity `0.05178270149633484`
- `simultaneous_triad_sel60`: evidence `0.3339493660329132`, raw necessity `0.03996589910876862`
- `simultaneous_triad_sel64`: evidence `0.2717512737832105`, raw necessity `0.011551106328093808`
- `simultaneous_triad_sel67`: evidence `0.3189119980494523`, raw necessity `0.02679868547802654`.

These are descriptive measurements only. The spread itself demonstrates why this result cannot prospectively invent a single raw-necessity cutoff after observing the data.

## Finding 7 — support-ineligible rows remain independently distinguishable from the raw fit, but reattack remains unresolved

Five onset-available rows have no eligible selected support template:

- `already_sounding_m64`: broad raw necessity `0.0`
- `neighbor_sel60_actual61`: `0.0041471827861076635`
- `reattack_m64`: `0.05310246072441282`
- `unrelated_transient_only_sel64`: `0.0023185831926859383`
- `weak_selected64_under60`: `0.0008448320887965837`.

For `reattack_m64` specifically:

- support selected template: `NO_ELIGIBLE_DETUNING_ANCHOR`
- support-valid candidate count: `0`
- independent owner/evidence diagnostics: unavailable because support eligibility is absent
- broad fixed-feature raw fit: available
- broad raw necessity: `0.05310246072441282`
- broad raw selected coefficient: `54.99900510742498`
- broad raw feature energy: `199.2417662109049`.

The raw fit therefore remains strong while support eligibility is absent. This result does **not** identify why the reattack support representation fails and does not repair or override that support failure. The original temporal/support attempt-1 trace remains inaccessible under frozen result commit `86549fcf3f15898aa551064b522ce42ca32b1b86`.

## Insufficient/context controls

The four frozen insufficient/context rows remain unavailable without fabricated measurements:

- `silence`: `INSUFFICIENT_LOW_AUDIO_SUPPORT`
- `low_noise`: `INSUFFICIENT_LOW_AUDIO_SUPPORT`
- `truncated_pre_context`: `REQUIRED_PRE_POST_CONTEXT_OUTSIDE_AUDIO`
- `truncated_post_context`: `REQUIRED_PRE_POST_CONTEXT_OUTSIDE_AUDIO`.

## Frozen conclusion

Result label:

`COMPLETE_SYNTHETIC_PROTECTION_FIT_SEAM_DIAGNOSTIC_NO_DECISION`

Attempt 1 establishes mechanically that:

1. **Support eligibility/protection and broad raw-fit evidence can be observed side-by-side without using support-space necessity to suppress owner/evidence diagnostics.**
2. **Frozen lower-owner protection remains independently visible**, notably on the octave aliases.
3. **Frozen candidate-evidence significance remains independently visible** on all support-eligible rows.
4. **Broad fixed-feature raw competition preserves previously measured competition distinctions**, including the simultaneous-dyad selected-note separation.
5. **Historical raw-to-V3 wiring is not equivalent to the leakage-cleaned support view**: all 19 historical raw-V7 references are selected-template ineligible while 14 support-view rows are eligible.
6. **Reattack remains a separate unresolved support/temporal problem.** Strong broad raw fit does not authorize promotion of a support-ineligible event.
7. **No final successor rule is defined.** This result does not authorize a raw-necessity threshold, transported `0.01`, all-49 production rule, owner/evidence aggregation rule, selected-note eligibility change, temporal fallback, real/model evaluation or delivery advancement.

Any later executable composition requires a new prospective PRE. It must preserve the measured semantic separation and may not choose a threshold or aggregation rule retrospectively from these frozen fixture values.

## Authority / prohibited work

No EGFxSet or other real media, Basic Pitch/Demucs/model inference, real correctness run, AG-PT/rejected holdout, protected song, physical capture/calibration, `songsterr_pipeline/**`, `main`, Production, GOAT/reference, reserved GFN or archived V143/Gomyway was accessed or executed.

Global authorization remains unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`.
