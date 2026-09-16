# RESULT — Songsterr Fresh V7 Representation Bridge Synthetic Iteration 2

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Authority: user instruction `Let's wire this better please 🙏`
PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_PRE_ITERATION2.md`
PRE commit: `7cc8fc88a9b3d12596dfdce553bb717bc77fb05b`

## Frozen implementation / execution identity

- peak-band bridge module commit: `56baaf07552fea521073d976c81a26658e2d5b6b`
- bridge Git blob: `402aa23f3f1821c4e5c45ccf7f170b542d76a453`
- complete bridge/test pair head: `46f4b71405946e0da68ff80e23b006f4393172c4`
- test Git blob: `167fe534cf99ac825c8127efa7828237551a5759`
- self-scoped workflow head: `b176a8665bef71ae99ff73733005ac083165c581`
- workflow: `.github/workflows/songsterr-v7-representation-bridge-synthetic-iteration2-one-shot.yml`
- run: `35052132987`
- job: `104654595776`
- attempt: `1`
- workflow conclusion: `failure`

PRE-to-pair compare contained exactly the two prospectively allowed new Python files. The workflow triggered only from its own exact YAML path. Frozen dependency and new bridge/test Git blob verification passed before execution.

No same-iteration code, support width, radius, fixture, expectation or threshold was changed after output was observed. No rerun is authorized for iteration 2.

## Frozen bridge algorithm exercised

Iteration 2 preserved the same geometry-derived center-separation rule as iteration 1:

- V6 frame size `2048`;
- V6 FFT size `8192`;
- zero-padding factor `4`;
- Hann first-null native half-width `2` bins;
- local-max separation radius `8` zero-padded bins.

Unlike iteration 1, each retained local maximum preserved the exact original input amplitudes at its frozen V3 support band `center-1`, `center`, `center+1`, because frozen V3 itself uses `PEAK_BIN_RADIUS = 1`.

No energy was invented, boosted, shifted, interpolated, renormalized or made MIDI/dataset-specific.

All structural bridge checks passed, including:

- zero input preservation;
- exact isolated three-bin peak-band preservation;
- geometry-derived Hann main-lobe center with only its exact ±1 peak band retained inside the ±8 lobe neighborhood;
- independent separated peak bands;
- suppression of weaker competing center inside a stronger center's ±8 neighborhood;
- deterministic lower-index tie ownership;
- output amplitudes never exceeding or differing from input at the same bin;
- positive scale equivariance;
- malformed rank/length, negative, NaN and infinity fail-closed behavior.

## Full V6 audio-derived fixture result — FAIL, improved to 20/23

The complete frozen 23-fixture V6 audio population was evaluated through:

`frozen V6 synthetic audio -> frozen V6 onset innovation -> iteration-2 peak-band bridge -> frozen V3 iteration-3 composite`

Each fixture was repeated three times in-process.

Observed summary:

- fixture count: `23`
- repetitions: `3`
- deterministic: `true`
- mismatch count: `3`
- matching fixtures: `20/23`
- bridge result: `FAIL`

### Three frozen mismatches

1. `selected64_enters_over_existing60`
   - expected: `onset-birth-corroborated-candidate`
   - observed: `not-onset-birth-corroborated`
   - V6 onset status: `OK`
   - analysis RMS: `0.336542505699681`
   - raw innovation energy: `217.8264003573765`
   - raw positive bins: `4097`
   - retained centers: `11`
   - retained positive bins: `33`
   - frozen V3 status: `FAIL_NECESSITY`

2. `simultaneous_dyad_sel60`
   - expected: `not-onset-birth-corroborated`
   - observed: `onset-birth-corroborated-candidate`
   - V6 onset status: `OK`
   - analysis RMS: `0.3175144522240112`
   - raw innovation energy: `209.93327885773218`
   - raw positive bins: `4097`
   - retained centers: `12`
   - retained positive bins: `36`
   - frozen V3 status: `PASS`
   - necessity fraction: `0.1840904226252075`
   - candidate evidence fraction: `0.34678943650665484`
   - lower-owner vetoes: none.

3. `reattack_m64`
   - expected: `onset-birth-corroborated-candidate`
   - observed: `not-onset-birth-corroborated`
   - V6 onset status: `OK`
   - analysis RMS: `0.43590990398881657`
   - raw innovation energy: `248.79801311654884`
   - raw positive bins: `4094`
   - retained centers: `11`
   - retained positive bins: `32`
   - frozen V3 status: `SELECTED_TEMPLATE_INELIGIBLE`.

## Concrete improvements over iteration 1

Iteration 2 repaired two of the five iteration-1 mismatches without changing any frozen threshold:

### `clean_low_m40` — repaired

- expected and observed: `onset-birth-corroborated-candidate`
- retained centers: `6`
- retained positive bins: `18`
- frozen V3 status: `PASS`
- necessity fraction: `0.12936434618438644`
- candidate evidence fraction: `0.38443223142641103`.

This directly resolves iteration 1's `REDUCED_DICTIONARY_EMPTY` failure for the low E2 synthetic control.

### `simultaneous_triad_sel60` — repaired

- expected and observed: `onset-birth-corroborated-candidate`
- frozen V3 status: `PASS`
- necessity fraction: `0.11027472693544244`
- candidate evidence fraction: `0.3339493660329132`.

The other previously matching protections remained intact, including clean mid/high notes, ±25-cent detune, attack-noise true note, already-sounding rejection, octave-alias rejection, selected dyad MIDI 64, triad MIDI 64/67, neighbor mismatch rejection, unrelated transient rejection, weak-selected-under-stronger rejection, silence/noise insufficiency and pre/post-context fail-closed behavior.

## Untouched V3 direct-spectrum regression — PASS

In the same first workflow attempt, the untouched frozen command:

`python scripts/songsterr-fresh/test_physical_template_plausibility_v3_iteration3.py`

completed with:

- fixture count `34`
- repetitions `3`
- deterministic `true`
- mismatch count `0`
- result `PASS`
- process status `0`.

Thus iteration-2 failure remains isolated to the V6-audio-to-V3 representation/composition seam. No historical V3 result changed.

## Frozen interpretation

Iteration 2 is permanently:

`FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_THREE_MISMATCHES`

The progression from iteration 1 to iteration 2 is informative:

- single-bin line collapse matched `18/23` V6 audio cases;
- preserving the frozen V3 ±1 peak band improved this to `20/23`;
- the low E2 and triad MIDI60 failures were repaired;
- three persistent failures remain, and they are qualitatively different:
  - a genuine newly entering note fails NNLS necessity;
  - one simultaneous dyad voice becomes a false PASS with no lower-owner veto;
  - a genuine reattack still fails candidate eligibility.

This pattern indicates that a single transformed spectrum is being asked to serve at least two different semantic roles:

1. **harmonic support / local-background eligibility**, which benefits from removing deterministic Hann-lobe leakage;
2. **candidate competition / NNLS necessity**, which can depend on richer spectral structure that the sparsifying bridge removes.

A third support-width tweak would therefore be post-result tuning rather than a well-justified next hypothesis.

## Safe next synthetic direction

The next research step should be prospective **dual-view diagnostic/composition research**, not another radius/width search.

A new diagnostic PRE may, without making a new final decision rule, compute for all 23 frozen V6 audio fixtures:

- raw frozen V6 innovation;
- iteration-2 peak-band support view;
- frozen V3 candidate-template eligibility and owner diagnostics on the support view;
- frozen V3/V6 competition/necessity diagnostics on the raw view where mechanically definable;
- the exact three persistent mismatch cases alongside all matching controls.

The purpose should be to determine prospectively whether support eligibility and competition/necessity can be separated into two evidence views without weakening alias, polyphony, transient or insufficiency protections.

No real/model evaluation is authorized by this result.

## Authority / prohibited work

No EGFxSet, prior Basic Pitch artifact, Basic Pitch inference, Demucs/model inference, real candidate media, protected song, AG-PT-set, rejected holdout, physical calibration/capture, `main`, Production, GOAT/reference, reserved GFN or archived V143/Gomyway was accessed or executed.

Global authorization remains unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`.