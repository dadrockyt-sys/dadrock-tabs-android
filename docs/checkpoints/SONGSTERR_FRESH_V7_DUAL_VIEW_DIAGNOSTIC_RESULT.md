# RESULT — Songsterr Fresh V7 Dual-View Representation Diagnostic V1

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Authority: user instruction `Let's wire this better please 🙏`
PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_DUAL_VIEW_DIAGNOSTIC_PRE.md`
PRE commit: `6402e3a6f77268ccc090232b340ac3719577ba76`

## Scope

This is a frozen **measurement-only** result. No new classifier, combined PASS rule, threshold, promotion rule or real-evaluation authorization was defined or exercised.

The diagnostic compared two evidence roles across the complete frozen V6 synthetic audio population:

- support/template/owner view: frozen iteration-2 peak-band representation;
- diagnostic competition/necessity view: untouched raw V6 innovation sampled at the exact support-derived feature bins and fit against the exact support-derived template dictionary.

## Frozen implementation / execution identity

- diagnostic module commit: `344aeb3e5b80e5111c99c679dad874ae6cb7fdff`
- diagnostic module Git blob: `e9e84ed663aab732408d1d618bd9486ffb660628`
- complete diagnostic module/test pair head: `645abc37a11aeeefb1b94004467471086f47c818`
- test Git blob: `5d240e87e11d1e36f9464008cd8e2c4b7ad6a06a`
- workflow head: `5ef238b22d48d7164f84eba287dffd3a8e68aed2`
- workflow: `.github/workflows/songsterr-v7-dual-view-diagnostic-one-shot.yml`
- run: `35052606540`
- job: `104656044194`
- attempt: `1`
- workflow conclusion: `success` because the prospectively frozen diagnostic/mechanical invariants completed; this is **not** a classifier PASS.

PRE-to-pair compare contained exactly the two prospectively allowed new Python files. Blob verification passed before execution for V6, the frozen V6 fixture manifest, V3 base/iterations 2–3, untouched V3 iteration-3 test, frozen bridge V2, and the new diagnostic pair.

No code/result rescue rerun occurred.

## Mechanical result

The diagnostic test completed with:

- fixture count: `23`
- repetitions: `3`
- deterministic: `true`
- diagnostic available rows: `19`
- support-selected-template available rows: `14`
- dual-view fit available rows: `14`
- `finalDecisionDefined:false`
- frozen expected classifications were carried as reference metadata only and were not used for computation
- real corpus evaluated: `false`
- model inference invoked: `false`
- Basic Pitch invoked: `false`
- network invoked by diagnostic execution: `false`
- customer eligible events: `0`
- may advance delivery: `false`
- mechanical diagnostic status: `COMPLETE`.

The four unavailable rows were the frozen low-support/context cases: silence, low noise, truncated pre-context and truncated post-context. No context or evidence was fabricated.

## Untouched V3 direct-spectrum regression

The same first workflow attempt also executed the untouched frozen iteration-3 suite:

- fixture count `34`
- repetitions `3`
- deterministic `true`
- mismatch count `0`
- result `PASS`
- process status `0`.

The diagnostic did not alter any frozen V3 behavior.

## Key measurement — genuine note entering over existing note

Fixture: `selected64_enters_over_existing60`
Reference-only expected class: `onset-birth-corroborated-candidate`.

Support view:

- selected template valid: `true`
- selected cents: `0.0`
- supported harmonic count: `4`
- weighted harmonic coverage: `0.45578231292517013`
- valid candidate count: `6`
- frozen support-view composite: `FAIL_NECESSITY`
- support-view necessity fraction: `0.0017494445720474096`
- independent support candidate-evidence fraction: `0.20775025159624896`
- credible lower-owner MIDIs: `[45,57,61]`
- veto lower owners: `[]`.

Dual-view raw fit using the same support-derived dictionary:

- available: `true`
- feature bins: `31`
- raw feature energy: `86.56381529788506`
- selected coefficient: `54.818935799652486`
- raw-view necessity fraction: `0.22933221700538753`.

**Frozen diagnostic interpretation:** the support view is sufficient to establish a plausible candidate template, but sparsifying the observed fit evidence destroys its independent necessity. Using raw V6 innovation only for the observed NNLS fit materially restores the selected note's necessity without changing the support-derived candidate population or templates.

This supports separating support eligibility from fit evidence in a later prospectively designed composition rule.

## Key measurement — simultaneous dyad selected MIDI60 false positive

Fixture: `simultaneous_dyad_sel60`
Reference-only expected class: `not-onset-birth-corroborated`.

Support view:

- selected template valid: `true`
- selected cents: `5.0`
- supported harmonic count: `6`
- weighted harmonic coverage: `1.0`
- valid candidate count: `7`
- frozen support-view composite: `PASS`
- support-view necessity fraction: `0.18409042262520736`
- support candidate-evidence fraction: `0.34678943650665484`
- credible lower-owner MIDIs: `[52]`
- veto lower owners: `[]`.

Dual-view raw fit:

- available: `true`
- feature bins: `28`
- raw feature energy: `78.38698002009778`
- selected coefficient: `35.26484965561953`
- raw-view necessity fraction: `0.14893565820377`.

Comparison control from the same audio, selected MIDI64:

- support-view necessity `0.22317435762869003`
- support candidate-evidence fraction `0.34516681610957956`
- credible lower owners `[48,60]`, no veto
- dual-view raw necessity `0.24578762252117828`.

**Frozen diagnostic interpretation:** changing only the NNLS observed view does **not** solve the MIDI60 dyad false positive. The false selected voice remains independently necessary under both support and raw fits, and the current frozen structural lower-owner guard has no veto. A future repair for this case must therefore target a different semantic dimension; do not try to fix it by choosing another fit-view sparsity or necessity threshold from these values.

## Key measurement — genuine reattack MIDI64

Fixture: `reattack_m64`
Reference-only expected class: `onset-birth-corroborated-candidate`.

- analysis RMS: `0.43590990398881657`
- raw innovation norm/energy: `248.79801311653966`
- raw positive bins: `4094`
- support norm: `147.44113004895627`
- support positive bins: `32`
- retained centers: `11`
- selected support template valid: `false`
- selected support template status: `NO_ELIGIBLE_DETUNING_ANCHOR`
- support valid candidate count: `0`
- support candidate-evidence diagnostic unavailable
- dual-view fit unavailable because no support-derived selected template/candidate dictionary exists.

**Frozen diagnostic interpretation:** dual-view NNLS cannot repair the reattack case because the failure occurs earlier, at support eligibility itself. The reattack requires a separately justified representation/temporal-support investigation; it must not be repaired by special-casing the fixture or lowering the frozen V3 support thresholds.

## Protection controls observed

The diagnostic preserved useful separation in representative controls:

### Clean low MIDI40

- support composite PASS
- support necessity `0.12936434618438641`
- support candidate evidence `0.3844322314264112`
- dual raw necessity `0.16759268694998108`.

### Clean mid MIDI64

- support composite PASS
- support necessity `0.7990997729553808`
- support candidate evidence `0.4889815802373423`
- dual raw necessity `0.6667882823682867`.

### Clean high MIDI88

- support composite PASS
- support necessity `0.8894403782029751`
- support candidate evidence `0.4928982307178351`
- dual raw necessity `0.862405326684565`.

### Octave alias selected72 / actual60

- support selected template eligible
- support frozen composite `FAIL_NECESSITY`, necessity `0.0`
- support candidate evidence `0.23530600965928458`
- credible lower owners `[48,60]`
- veto lower owner `[60]`
- dual raw necessity `0.0015097254732536487`.

### Octave alias selected79 / actual67

- support frozen composite `FAIL_NECESSITY`, necessity `0.0`
- support candidate evidence `0.2387584790923918`
- credible lower owners `[55,67]`
- veto lower owner `[67]`
- dual raw necessity `0.0009280716012821318`.

Thus the raw-fit diagnostic does not erase the existing strong octave-alias separation in these controls.

## Frozen conclusion

Result label:

`COMPLETE_SYNTHETIC_DUAL_VIEW_DIAGNOSTIC_NO_DECISION`

The diagnostic establishes three separate engineering facts:

1. **Support/fit separation is justified for at least one real seam defect in the frozen synthetic population.** The genuine `selected64_enters_over_existing60` case changes from support-view necessity `0.00175` to raw-view necessity `0.2293` with the support-derived template population held fixed.
2. **The dyad MIDI60 false positive is not a sparsified-fit artifact.** It remains strongly necessary on raw fit and has no current lower-owner veto.
3. **The reattack failure is upstream of fitting.** Its selected support template is ineligible, so it requires a separate temporal/representation investigation.

Do not combine these observations into a new classifier under this diagnostic authorization. Any dual-view composition rule must be frozen prospectively in a new synthetic PRE. Any reattack representation change must likewise be prospectively defined and must preserve all frozen controls.

## Authority / prohibited work

No EGFxSet, prior Basic Pitch artifact, Basic Pitch/Demucs/model inference, real candidate media, protected song, AG-PT-set, rejected holdout, physical calibration/capture, `main`, Production, GOAT/reference, reserved GFN or archived V143/Gomyway was accessed or executed.

Global authorization remains unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`.