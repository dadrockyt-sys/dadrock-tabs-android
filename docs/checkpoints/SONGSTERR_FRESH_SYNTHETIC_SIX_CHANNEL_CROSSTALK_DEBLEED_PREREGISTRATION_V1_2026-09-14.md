# Songsterr Fresh — Synthetic Six-Channel Crosstalk / Debleed Preregistration V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE HARNESS RESULT EXECUTION

## Purpose

This is a zero-additional-cost, deterministic, SYNTHETIC-ONLY software feasibility experiment for the prospective purpose-built six-per-string-channel reference architecture.

It asks one narrow question:

> If six already-separated source channels exist and the six-by-six crosstalk mixing matrix is known exactly, how does deterministic linear debleeding behave as bleed strength, matrix conditioning, and additive perturbation increase?

This experiment does **not** ask whether six authoritative per-string channels can be recovered from ordinary mono/stereo guitar audio. It assumes six source channels already exist before mixing.

This experiment does not establish real sensor behavior, real calibration validity, holdout validity, Songsterr Fresh correctness, production eligibility, or customer delivery readiness.

## Hard boundary / prohibitions

The harness must be fully local, deterministic, network-free, model-free, and synthetic-only.

It must not:
- access Guitar Fretboard Notes or any other external corpus;
- access `deb` or `ele_natural`;
- access customer, protected-song, Guitar-TECHS, GuitarSet, IDMT, V143/Gomyway, GOAT/reference-scoring, or any other evaluated real audio;
- use Basic Pitch or V6;
- use a neural network, learned separator, adaptive optimizer, parameter sweep, or data-dependent hyperparameter selection;
- alter the frozen V6/correctness gates;
- claim that successful inversion proves real hardware channel isolation or creates authoritative six-string truth from mono/stereo audio;
- authorize hardware procurement, real calibration capture, real holdout capture, correctness, V6, customer eligibility, or delivery.

Required downstream state remains:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## Frozen numeric runtime

- Python CPU only.
- NumPy version in CI: `2.1.3`.
- All source, noise, matrix, mixing, solve, and metric calculations use `numpy.float64`.
- Channel count: exactly 6.
- Samples per synthetic channel: exactly 8,192.
- No stochastic RNG is permitted.

## Frozen untouched synthetic source bank

Let sample index `n = 0..8191`, and `N = 8192`.

For source channel `c = 0..5`, use three integer DFT-bin sinusoids with fixed amplitude weights `(1.0, 0.6, 0.35)`.

Frozen bin table by channel:
- c0: `(37, 211, 503)`
- c1: `(53, 239, 557)`
- c2: `(71, 283, 601)`
- c3: `(89, 331, 653)`
- c4: `(109, 379, 709)`
- c5: `(131, 433, 761)`

Frozen phases for channel `c`:
- first component: `0.10 * (c + 1)` radians;
- second component: `0.30 + 0.07 * c` radians;
- third component: `0.50 + 0.11 * c` radians.

For each source channel:
1. sum the three sinusoids;
2. subtract its arithmetic mean;
3. divide by its population RMS so final RMS is exactly normalized to 1 within float64 arithmetic.

Call the resulting immutable source matrix `S`, shape `(6,8192)`.

`S` must never be modified in place. All mixed and recovered arrays are separate allocations.

The result must record SHA-256 of `S` encoded as C-order little-endian float64 bytes.

## Frozen deterministic perturbation bank

A separate six-channel deterministic perturbation bank `P`, shape `(6,8192)`, is generated analytically with no RNG.

For channel `c = 0..5`, use four cosine components with amplitude weights `(1.0, 0.7, 0.5, 0.3)` and bins:
- `1009 + 17*c`
- `1301 + 19*c`
- `1601 + 23*c`
- `1901 + 29*c`

Frozen phases are:
- `0.20 * (c + 1)` radians;
- `0.40 * (c + 1)` radians;
- `0.60 * (c + 1)` radians;
- `0.80 * (c + 1)` radians.

For each perturbation channel:
1. sum the four cosines;
2. subtract its arithmetic mean;
3. divide by its population RMS to RMS 1.

`P` is immutable and distinct from `S`.

The result must record SHA-256 of `P` encoded as C-order little-endian float64 bytes.

## Frozen crosstalk matrix family A — distance-decay bleed

Family ID: `distance_decay`.

Construct fixed off-diagonal weight matrix `W` as follows for rows/columns `i,j = 0..5`:
- `W[i,i] = 0`;
- before normalization, `W[i,j] = 1 / abs(i-j)` for `i != j`;
- normalize each row independently so its off-diagonal values sum exactly to 1 within float64 arithmetic.

For bleed level `b`, define:
`M = I + b*W`.

Frozen bleed levels:
`(0.00, 0.02, 0.05, 0.10, 0.20, 0.35, 0.50)`.

Here `b` is the total off-diagonal amplitude weight added to each observed row before perturbation.

## Frozen crosstalk matrix family B — paired conditioning stress

Family ID: `paired_conditioning`.

Start with the 6x6 identity matrix. Couple only string-channel pairs `(0,1)`, `(2,3)`, `(4,5)` symmetrically:
- `M[0,1] = M[1,0] = b`;
- `M[2,3] = M[3,2] = b`;
- `M[4,5] = M[5,4] = b`;
- all other off-diagonal entries are 0;
- all diagonal entries remain 1.

Frozen bleed/conditioning levels:
`(0.10, 0.30, 0.50, 0.70, 0.85, 0.95)`.

This family is deliberately a numerical-conditioning stress family; high levels are not claims about expected real hardware bleed.

## Frozen perturbation levels

For every matrix case, evaluate perturbation RMS scale `sigma` in:
`(0.0, 0.0001, 0.001, 0.01)`.

For each case, observed mixed channels are:
`Y = M @ S + sigma * P`.

No clipping, quantization, gain renormalization, or additional noise is permitted.

## Frozen recovery methods

Three estimates are compared.

### 1. Untreated mixed baseline

`S_hat_raw = Y`

This baseline intentionally applies no debleeding.

### 2. Direct known-matrix solve

Method ID: `direct_solve`.

Recover:
`S_hat_direct = numpy.linalg.solve(M, Y)`.

No pseudoinverse thresholding or alternate solver is permitted.

### 3. Fixed ridge/Tikhonov solve

Method ID: `ridge_1e-4`.

Frozen regularization constant:
`lambda = 1e-4`.

Recover:
`S_hat_ridge = solve(M.T @ M + lambda*I, M.T @ Y)`.

The same fixed lambda is used for every family, bleed level, conditioning level, and perturbation level. It must not be tuned from results.

## Frozen condition metric

For each matrix `M`, report the ordinary 2-norm condition number:
`numpy.linalg.cond(M, 2)`.

Also record:
- family ID;
- bleed level `b`;
- perturbation level `sigma`;
- matrix SHA-256 from C-order little-endian float64 bytes.

## Frozen reconstruction metrics

For estimate `E` versus untouched source `S`:

Per-channel NRMSE:
`||E[c]-S[c]||_2 / ||S[c]||_2`.

Report for each method:
- all six per-channel NRMSE values;
- pooled NRMSE = `||E-S||_F / ||S||_F`;
- maximum per-channel NRMSE.

For direct and ridge recovery, also report improvement over untreated mixed baseline in dB:
`20 * log10(max(raw_pooled_nrmse, 1e-15) / max(recovered_pooled_nrmse, 1e-15))`.

No other primary metric or threshold may be selected after results are observed.

## Frozen result structure

Canonical JSON must include:
- contract ID `songsterr-fresh-synthetic-six-channel-debleed-v1`;
- study stage `SYNTHETIC_SOFTWARE_FEASIBILITY_ONLY`;
- NumPy version;
- source/noise generation contract identifiers;
- source and perturbation SHA-256 values;
- each family/matrix/bleed/condition case;
- each perturbation level;
- raw, direct, and ridge metrics;
- total case count;
- finite-value checks;
- unchanged downstream authorization fields.

Canonical JSON serialization uses sorted keys, compact separators `(',', ':')`, UTF-8, and must be byte-identical for identical implementation/runtime bytes.

## Frozen synthetic contract tests before result execution

Before the official harness result step, tests must pass and enforce at minimum:
- exactly six source channels and 8,192 samples;
- no RNG and no network/external-corpus dependency in harness behavior;
- deterministic source and perturbation bytes/hashes;
- source and perturbation RMS normalization;
- source arrays are not mutated by mixing/recovery;
- exact family-A levels and row-normalized distance weights;
- exact family-B pair topology and levels;
- exact perturbation levels;
- direct solve equation;
- ridge equation with lambda exactly `1e-4`;
- condition number reporting;
- NRMSE formulas;
- zero-bleed/zero-perturbation direct recovery is numerically near machine precision;
- canonical JSON byte determinism;
- all authorization fields remain false/zero.

The workflow must run compile + synthetic contract tests before the official harness result step.

## Frozen interpretation boundary

There is **no production PASS threshold**.

Expected descriptive patterns such as larger error under stronger bleed, larger condition number, or stronger perturbation are not authorization gates and may not be used to retroactively change this method.

A successful result can show only that, under known synthetic mixing and already-separated six-channel inputs, deterministic linear algebra can remove some or all synthetic crosstalk depending on matrix conditioning and perturbation.

It cannot show:
- that real per-string sensors have the same crosstalk matrix;
- that the matrix is known or stable in real hardware;
- that mono/stereo audio can be decomposed into authoritative six-string channels;
- that independent physical truth exists;
- that any real holdout or customer audio is correct.

Any later real calibration/capture remains separately gated and budget-paused.
