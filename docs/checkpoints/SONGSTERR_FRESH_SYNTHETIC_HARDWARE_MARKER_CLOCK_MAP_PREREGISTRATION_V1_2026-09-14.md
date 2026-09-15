# Songsterr Fresh — Synthetic Hardware-Marker Clock Map Preregistration V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE OFFICIAL HARNESS RESULT EXECUTION

## 1. Purpose

This is a zero-additional-cost, SYNTHETIC-ONLY software contract for the already-frozen purpose-built hardware timing architecture.

The prospective physical topology has:
- a fret/contact logger with its own monotonically increasing hardware tick clock;
- a deterministic sync-marker sequence emitted by that logger;
- a conditioned copy of the same marker sequence captured on the common multichannel audio-interface sample clock.

This V1 contract freezes the deterministic transform that maps logger ticks into audio-interface time using **only immutable paired hardware markers**.

It does not choose empirical real-hardware drift/jitter/dropout thresholds. Those remain reserved for future NON_HOLDOUT physical calibration if hardware ever becomes available.

## 2. Authority inherited unchanged

Parent authority:
- expanded purpose-built design commit `e37d2b4662db949157d2cf4797370f05648b6940`;
- physical-reference semantics commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- capture-QA / structural gate matrix commit `2b191b39f2f1c19564f1353381779acbc96fbeda`;
- hardware/calibration necessity + bench qualification commit `a0279b8c48c51176678229abfa92576b1d1c0c95`;
- custom/hybrid topology commit `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`.

Inherited structural timing bound remains exactly:
`0.025 s`.

This V1 does not tighten, relax, reinterpret, or empirically tune that bound.

## 3. Hard prohibitions

The implementation and harness must be local, deterministic, CPU-only, network-free, corpus-free, model-free, and synthetic-only.

It must not:
- inspect evaluated DI waveform content;
- use waveform/envelope cross-correlation;
- use spectrogram alignment;
- use audio onset detection;
- use excitation-to-DI musical-event matching;
- use DTW;
- use Basic Pitch, V6, model activations, correctness output, or any transcription model;
- access Guitar Fretboard Notes, `deb`, `ele_natural`, Guitar-TECHS, GuitarSet, IDMT, V143/Gomyway, GOAT/reference scoring, customer audio, or protected-song audio;
- discard, relabel, reorder, or selectively omit a valid hardware marker to improve the fit;
- invent a real-hardware acquisition-QA drift/jitter/dropout threshold from synthetic results;
- authorize hardware procurement, real calibration capture, holdout capture, correctness, V6, customer eligibility, or delivery.

Required downstream state remains:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## 4. Frozen numeric runtime

- Python CPU only.
- NumPy CI version: `2.1.3`.
- Float calculations: `numpy.float64`.
- Synthetic audio sample rate: exactly `48,000 Hz`.
- Synthetic logger ticks are integer nonnegative values.
- Synthetic audio marker locations are integer nonnegative sample indices.
- No random-number generator is permitted.

## 5. Frozen marker schema

Each paired hardware marker is represented conceptually by:
- `markerId`: integer;
- `loggerTick`: integer;
- `audioSampleIndex`: integer.

The fitting input is one ordered list of paired markers. There is no independent nearest-neighbor pairing stage in V1.

The marker sequence must fail closed unless all are true:
1. marker count is at least 4;
2. marker IDs are exactly `0,1,...,N-1` in the supplied order;
3. logger ticks are integers, nonnegative, and strictly increasing;
4. audio sample indices are integers, nonnegative, and strictly increasing;
5. sample rate is an integer > 0;
6. logger tick span is > 0;
7. audio sample span is > 0.

Boolean values are not accepted as integers.

No marker rejection/outlier removal is permitted. If a future real marker stream cannot satisfy the frozen schema, it must fail the applicable future acquisition/structural gate rather than be repaired by this clock-map function.

## 6. Frozen affine clock-map algorithm

Given logger ticks `x_i` and audio times `y_i = audioSampleIndex_i / sampleRate`, fit:

`audioSeconds = interceptSeconds + secondsPerLoggerTick * loggerTick`.

The fit is ordinary unweighted least squares using **all** validated markers.

Frozen computation:
1. convert `x` and `y` to float64 arrays;
2. `xMean = mean(x)`;
3. `yMean = mean(y)`;
4. `xCentered = x - xMean`;
5. denominator `D = sum(xCentered * xCentered)`; fail if non-finite or `D <= 0`;
6. `secondsPerLoggerTick = sum(xCentered * (y - yMean)) / D`;
7. fail if slope is non-finite or `<= 0`;
8. `interceptSeconds = yMean - secondsPerLoggerTick * xMean`;
9. fail if intercept is non-finite;
10. marker predictions are `interceptSeconds + secondsPerLoggerTick*x`;
11. marker residuals are `predicted - observedAudioSeconds`.

No weighting, robust regression, RANSAC, piecewise fitting, spline fitting, marker trimming, or adaptive model selection is permitted in V1.

## 7. Frozen clock-map diagnostics

For every fitted marker sequence report:
- marker count;
- sample rate;
- `interceptSeconds`;
- `secondsPerLoggerTick`;
- derived `loggerTicksPerSecond = 1 / secondsPerLoggerTick`;
- first/last logger tick;
- first/last audio sample index;
- per-marker residual seconds;
- maximum absolute marker residual seconds;
- RMS marker residual seconds;
- marker-input SHA-256 under canonical JSON serialization;
- transform-contract ID.

All values must be finite.

The fitting function itself does not apply a real-hardware pass/fail drift or jitter threshold.

## 8. Frozen mapping rule

For any validated integer/nonnegative reference tick `t`, mapped audio time is exactly:

`interceptSeconds + secondsPerLoggerTick * t`.

A vector of query ticks must be finite after conversion, nonnegative, and nondecreasing. No query-time clipping to the marker range is performed.

For future real use, whether extrapolation outside the marker span is permitted must be frozen in the real calibration/capture plan. This synthetic V1 reports extrapolation behavior but does not authorize it for real capture.

## 9. Frozen synthetic marker schedule

Synthetic logger marker ticks are fixed at:

`0, 500000, 1000000, ..., 10000000`

inclusive, giving exactly 21 paired markers.

Synthetic evaluation/reference ticks are fixed at:

`0, 250000, 500000, ..., 10000000`

inclusive, giving exactly 41 evaluation ticks.

Audio sample index generation always uses deterministic half-away-from-zero behavior for nonnegative values implemented as:

`floor(value + 0.5)`.

Python's banker-rounding must not be used for synthetic marker generation.

## 10. Frozen synthetic cases

Every case has known synthetic truth `truthSeconds(tick)` used only by the synthetic harness to quantify mapping error. Real operation will not possess this synthetic truth function.

### Case A — `exact_affine`

- intercept: `0.250000 s`;
- true seconds/tick: `1.000000e-6`;
- no extra marker perturbation;
- no nonlinear warp.

### Case B — `positive_100ppm`

- intercept: `0.125000 s`;
- true seconds/tick: `1.000100e-6`;
- no extra marker perturbation;
- no nonlinear warp.

### Case C — `negative_100ppm`

- intercept: `0.375000 s`;
- true seconds/tick: `0.999900e-6`;
- no extra marker perturbation;
- no nonlinear warp.

### Case D — `deterministic_marker_jitter_1ms`

- intercept: `0.200000 s`;
- true seconds/tick: `1.000000e-6`;
- no nonlinear warp;
- add these fixed integer audio-sample offsets to the 21 generated marker sample indices, in order:

`(0, 48, -48, 24, -24, 36, -36, 12, -12, 48, -48, 24, -24, 36, -36, 12, -12, 48, -48, 24, 0)`.

At 48 kHz, the maximum injected marker perturbation magnitude is exactly 1 ms.

Synthetic truth for evaluation ticks excludes this marker perturbation; it represents marker-observation error.

### Case E — `quadratic_warp_10ms`

- intercept: `0.300000 s`;
- base seconds/tick: `1.000000e-6`;
- nonlinear warp: `0.010 * (tick / 10000000)^2` seconds;
- no extra discrete marker perturbation.

Synthetic truth includes the quadratic warp.

### Case F — `quadratic_warp_180ms_stress`

- intercept: `0.300000 s`;
- base seconds/tick: `1.000000e-6`;
- nonlinear warp: `0.180 * (tick / 10000000)^2` seconds;
- no extra discrete marker perturbation.

This is deliberately a software stress case, not a claim about plausible real hardware.

Synthetic truth includes the quadratic warp.

## 11. Frozen synthetic truth metrics

For each case, after fitting the frozen affine map, evaluate all 41 frozen evaluation ticks and report:
- per-evaluation-tick mapping error = `mappedSeconds - truthSeconds`;
- maximum absolute truth mapping error seconds;
- RMS truth mapping error seconds;
- inherited structural-bound diagnostic:
  `syntheticTruthWithinFrozen025SecondStructuralBound = maxAbsoluteTruthMappingErrorSeconds <= 0.025`.

This boolean is a **synthetic diagnostic only**. It is not a substitute for future hardware timing proof and does not create an acquisition-QA threshold.

Also report the true synthetic intercept/base seconds-per-tick/warp amplitude for provenance.

## 12. Frozen aggregate result

Canonical result JSON must contain:
- contract ID `songsterr-fresh-synthetic-hardware-marker-clock-map-v1`;
- study stage `SYNTHETIC_SOFTWARE_FEASIBILITY_ONLY`;
- NumPy version;
- algorithm contract ID `hardware-marker-affine-ols-v1`;
- sample rate;
- frozen marker/evaluation schedules;
- frozen structural bound `0.025`;
- all six case results in the fixed order A-F;
- finite-value checks;
- case count exactly 6;
- unchanged downstream authorization fields.

Canonical JSON serialization uses sorted keys, compact separators `(',', ':')`, UTF-8, and must be byte-identical for identical implementation/runtime bytes.

## 13. Frozen contract tests before official result

Before the official harness-result step, synthetic tests must pass and enforce at minimum:
- no RNG/network/corpus/model dependency;
- exact marker and evaluation tick schedules;
- exact six frozen case definitions;
- exact half-away-from-zero sample-index generation for nonnegative values;
- schema rejects fewer than 4 markers;
- schema rejects duplicate/skipped/out-of-order marker IDs;
- schema rejects non-integer/bool ticks/sample indices;
- schema rejects nonmonotonic logger ticks or audio sample indices;
- affine coefficients match an independently calculated exact affine fixture;
- no marker rejection occurs;
- mapping equation is exact;
- residual formulas are exact;
- exact-affine synthetic case maps to near float64/sample-quantization precision;
- canonical JSON byte determinism;
- all authorization fields remain false/zero.

The workflow must run compile + contract tests before the official synthetic harness step.

## 14. Interpretation boundary

This experiment may establish only software behavior of the frozen affine marker transform under deterministic synthetic inputs.

It may show:
- exact affine clock relationships are recovered correctly;
- finite marker quantization/jitter creates finite residual/mapping error;
- an affine transform cannot perfectly model sufficiently nonlinear clock behavior;
- the inherited 25 ms structural bound can be exercised against synthetic truth without changing it.

It cannot show:
- actual hardware drift/jitter;
- actual marker-detection accuracy;
- actual logger oscillator stability;
- actual audio-interface clock behavior;
- real sync-loss/dropout thresholds;
- that future hardware will pass the 25 ms bound;
- that a future holdout is structurally suitable;
- that correctness, V6, or customer delivery may proceed.

Any future empirical drift/jitter/dropout thresholds remain blocked until real NON_HOLDOUT hardware calibration exists and must be frozen before the first holdout attempt.
