# RESULT — Songsterr Fresh V7 Representation Bridge Synthetic Iteration 1

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Authority: user instruction `Let's wire this better please 🙏`
PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_PRE.md`
PRE commit: `6502f00670efe9987ff5a76707d9cf32476ac4fe`

## Frozen implementation / execution identity

- bridge module commit: `3b24d9fe51a12150c8b461d59ba4ebbb223f8040`
- bridge Git blob: `a63d62371e3ad97cb2ce085ccb1c2950a5cd23a1`
- complete bridge/test pair head: `73652d19f6dc71964e788330e3a94b163a6fb4af`
- test Git blob: `a8a4bd8399763a2581209ae594349d39b38d6e7c`
- self-scoped synthetic workflow head: `59a1bdb84a00e34c42906f2425d2d556572a5f78`
- workflow: `.github/workflows/songsterr-v7-representation-bridge-synthetic-one-shot.yml`
- run: `35051843902`
- job: `104653711197`
- attempt: `1`
- workflow conclusion: `failure`

PRE-to-pair compare contained exactly the two prospectively allowed new Python files. The workflow triggered only from its own exact YAML path. Frozen dependency and new bridge/test Git blob verification passed before execution.

No same-iteration code, radius, fixture, expectation or threshold was changed after output was observed. No rerun is authorized for iteration 1.

## Frozen bridge algorithm exercised

Iteration 1 used the prospectively frozen geometry-derived line bridge:

- V6 frame size `2048`;
- V6 FFT size `8192`;
- zero-padding factor `4`;
- Hann first-null native half-width `2` bins;
- line-suppression radius `8` zero-padded bins;
- retain only the deterministic first local maximum within each ±8-bin neighborhood;
- retained amplitudes copied exactly from input;
- all non-retained bins zeroed;
- no boosting, interpolation, shifting, normalization, MIDI-specific logic or dataset-specific logic.

Structural checks all passed:

- zero vector preserved;
- isolated peak preserved exactly;
- synthetic 4x-zero-padded Hann main lobe around center bin `148` retained only bin `148` within the frozen ±8 neighborhood;
- separated peaks at bins `200` and `209` both survived;
- weaker nearby peak suppression passed;
- equal-max tie retained lower bin deterministically;
- positive scaling preserved retained-bin identities and amplitudes;
- malformed rank/length, negative, NaN and infinity inputs failed closed.

## Full V6 audio-derived fixture result — FAIL

The complete frozen 23-fixture V6 audio population was evaluated through:

`frozen V6 synthetic audio -> frozen V6 onset innovation -> iteration-1 line bridge -> frozen V3 iteration-3 composite`

Each fixture was repeated three times in-process.

Observed summary:

- fixture count: `23`
- repetitions: `3`
- deterministic: `true`
- mismatch count: `5`
- matching fixtures: `18/23`
- bridge result: `FAIL`

### Five frozen mismatches

1. `clean_low_m40`
   - expected: `onset-birth-corroborated-candidate`
   - observed: `not-onset-birth-corroborated`
   - V6 onset status: `OK`
   - analysis RMS: `0.4176328474587125`
   - raw innovation energy: `303.99794958842654`
   - raw positive bins: `4097`
   - retained positive bins: `6`
   - frozen V3 status: `REDUCED_DICTIONARY_EMPTY`

2. `selected64_enters_over_existing60`
   - expected: `onset-birth-corroborated-candidate`
   - observed: `not-onset-birth-corroborated`
   - V6 onset status: `OK`
   - analysis RMS: `0.336542505699681`
   - raw innovation energy: `217.8264003573765`
   - retained positive bins: `11`
   - frozen V3 status: `FAIL_NECESSITY`

3. `simultaneous_dyad_sel60`
   - expected: `not-onset-birth-corroborated`
   - observed: `onset-birth-corroborated-candidate`
   - V6 onset status: `OK`
   - analysis RMS: `0.3175144522240112`
   - raw innovation energy: `209.93327885773218`
   - retained positive bins: `12`
   - frozen V3 status: `PASS`
   - necessity fraction: `0.3136303864832499`
   - candidate evidence fraction: `0.5711803443474066`
   - no lower-owner veto was produced.

4. `simultaneous_triad_sel60`
   - expected: `onset-birth-corroborated-candidate`
   - observed: `not-onset-birth-corroborated`
   - V6 onset status: `OK`
   - analysis RMS: `0.2816017042655006`
   - raw innovation energy: `186.18817382479165`
   - retained positive bins: `14`
   - frozen V3 status: `FAIL_NECESSITY`

5. `reattack_m64`
   - expected: `onset-birth-corroborated-candidate`
   - observed: `not-onset-birth-corroborated`
   - V6 onset status: `OK`
   - analysis RMS: `0.43590990398881657`
   - raw innovation energy: `248.79801311654884`
   - retained positive bins: `11`
   - frozen V3 status: `SELECTED_TEMPLATE_INELIGIBLE`

## Protections that did hold

The bridge correctly matched, among others:

- clean mid MIDI 64 PASS;
- clean high MIDI 88 PASS;
- ±25-cent detuned MIDI 64 PASS;
- attack-noise true MIDI 64 PASS;
- already-sounding MIDI 64 reject;
- both octave aliases reject;
- simultaneous dyad selected MIDI 64 PASS;
- simultaneous triad selected MIDI 64 and 67 PASS;
- neighbor MIDI mismatch reject;
- unrelated transient reject;
- weak selected note under stronger note reject;
- silence and low-noise insufficient;
- truncated pre/post context insufficient.

Thus the geometry hypothesis was directionally useful: it repaired the original broad-main-lobe support failure for many audio-derived cases without weakening the frozen direct V3 suite. But a single-bin line representation is too sparse to preserve all frozen candidate-competition and necessity behavior.

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

Therefore iteration-1 failure is isolated to the **V6-audio-to-V3 representation seam**. No historical V3 result changed.

## Frozen interpretation

Iteration 1 is permanently:

`FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_SINGLE_BIN_SPARSIFICATION`

The result supports two conclusions without tuning from real data:

1. the original V6-Hann/V3-local-background mismatch was real — removing deterministic main-lobe leakage allowed most frozen V6 audio cases to reach sensible frozen V3 decisions;
2. collapsing each physical spectral lobe to exactly one bin removes too much support/context for frozen V3's candidate dictionary and NNLS necessity geometry. The clean low E2 `REDUCED_DICTIONARY_EMPTY` is the clearest structural symptom; the dyad false positive and continuing/polyphonic/reattack failures show that competition information also changed.

Do not change the radius or rescue-rerun iteration 1.

## Safe next synthetic direction

A successor iteration may preserve the geometry-derived ±8 lobe separation while retaining the frozen V3 **peak support width** around each detected local maximum rather than a single bin. The principled candidate is:

- identify deterministic local maxima with the same frozen ±8 geometry;
- retain the original, unboosted input amplitudes at each retained maximum and its immediate ±1 bins, because frozen V3 itself uses `PEAK_BIN_RADIUS = 1` when locating harmonic support;
- zero the remainder of the deterministic Hann-lobe neighborhood;
- invent no energy and change no V3/V6 threshold;
- rerun all 23 frozen V6 audio expectations plus the untouched 34-case V3 regression under a **new prospective PRE**.

This direction is synthetic-only. No real/model evaluation is authorized.

## Authority / prohibited work

No EGFxSet, prior Basic Pitch artifact, Basic Pitch inference, Demucs/model inference, real candidate media, protected song, AG-PT-set, rejected holdout, physical calibration/capture, `main`, Production, GOAT/reference, or archived V143/Gomyway was accessed or executed.

Global authorization remains unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`.