# SONGSTERR FRESH V3 PHYSICAL-TEMPLATE SYNTHETIC PRE

Status: **PROSPECTIVE / FROZEN ON FIRST COMMIT**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
PRE parent head: `cc924c96abf70b23e79bda60010d6c8466a1d301`

This PRE is frozen before any V3 research implementation exists and before any V3 synthetic result is observed. The first commit that creates this file freezes this iteration. If any immutable gate below fails, record the failure and create a new prospective iteration before changing the frozen criterion or fixtures.

## 1. PURPOSE AND NON-AUTHORITY

This is isolated synthetic research into the physical-template eligibility stage inherited by the frozen V6 onset-birth classifier. It is not a real-media correctness evaluation and cannot authorize delivery, model validation, V6 correctness, real calibration, holdout capture, or promotion of any Basic Pitch proposal.

Frozen historical observations, including EGFxSet, are not optimization data. In particular this iteration must not lower or tune the frozen V6 `0.20` fundamental-to-maximum-harmonic threshold, special-case MIDI 40, or choose constants by looking at any closed real-media result.

No Basic Pitch inference, V6 correctness execution, real candidate media, EGFxSet, AG-PT-set payload, rejected holdout payload, protected song, physical capture/calibration, V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, V5/FLGD, or Guitar-TECHS work is authorized by this PRE.

## 2. VERIFIED WORKFLOW BOUNDARY

The pre-implementation workflow audit is recorded in `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` at commit `cc924c96abf70b23e79bda60010d6c8466a1d301`.

The isolated V3 code paths frozen below do not match the audited automatic `songsterr-fresh-*` workflow `push.paths` filters. No new workflow file will be created for this iteration. No existing workflow YAML may be edited.

## 3. EXACT FILE BOUNDARY

After this PRE is frozen, only these files may be created or changed for V3 synthetic iteration 1:

- `scripts/songsterr-fresh/physical_template_plausibility_v3.py` — new isolated research module;
- `scripts/songsterr-fresh/test_physical_template_plausibility_v3.py` — new deterministic synthetic test/fixture harness; fixtures are defined in this file, not learned from results;
- `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT.md` — result record created only after the frozen tests run;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` — state-transition record only.

This PRE file itself is immutable after its creation commit for iteration 1. The following existing files are read-only and must not be edited by this iteration:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`;
- `scripts/songsterr-fresh/qualify_basic_pitch_note_births_v2.py`;
- all existing V6 fixture files;
- all `.github/workflows/*` files;
- all `songsterr_pipeline/**` files;
- every archived or closed research line.

Any need to modify a file outside the four allowed write paths stops this iteration and requires a new prospective checkpoint.

## 4. FROZEN LINEAGE FACTS

The frozen V6 physical-template stage currently:

- uses `SAMPLE_RATE = 44100`, `FFT_SIZE = 8192`, playable MIDI 40–88, and at most six harmonics;
- chooses a fundamental bin from the selected MIDI cell;
- samples each harmonic in a ±1 FFT-bin neighborhood;
- uses template weights `1 / harmonic`, normalized by L2 norm;
- rejects a candidate before NNLS if fundamental innovation divided by its strongest observed harmonic is below `0.20`;
- subsequently uses a separate shared-dictionary NNLS leave-one-out necessity test and requires a positive selected coefficient plus `necessityFraction >= 0.01`.

Boundary qualifier V2 leaves normal in-clip V6 classification unchanged and separately routes clip-start proposals without genuine required left context to the one-sided clip-start classifier. This V3 iteration does not alter that boundary routing.

## 5. PROSPECTIVE V3 HYPOTHESIS

A candidate pitch can be physically plausible even when its fundamental is weak if several harmonics form a coherent series around a single pitch anchor. Candidate eligibility should therefore be based on **multi-harmonic support across a prospectively bounded detuning grid**, not on one fundamental-bin amplitude ratio.

The hypothesis is accepted for synthetic iteration 1 only if the frozen criterion below:

1. accepts ordinary and weak-fundamental coherent harmonic series across the frozen timbre/detuning fixtures;
2. rejects insufficient/broadband/non-harmonic support;
3. does not remove the separate NNLS necessity protection, so lower-owner/octave alias controls remain rejected at the composite synthetic decision;
4. preserves true polyphonic births in the frozen synthetic controls;
5. produces identical decisions and diagnostics on repeat execution.

Synthetic success is evidence only that this mechanism survives these prospective synthetic gates. It is not real-world correctness evidence.

## 6. FROZEN V3 CANDIDATE-ELIGIBILITY ALGORITHM

The implementation must be a pure function over a nonnegative finite innovation spectrum and its frequency vector. It must not read audio files, model outputs, references, environment secrets, network resources, or repository datasets.

### 6.1 Constants

Freeze these constants for iteration 1:

- sample rate: `44100` Hz;
- FFT size: `8192`;
- playable MIDI: `40..88` inclusive;
- maximum harmonic count: `6`;
- harmonic peak neighborhood: nearest target bin ±`1` bin;
- detuning anchors: `-40, -35, -30, ..., +35, +40` cents inclusive, 5-cent spacing;
- local-background radius: ±`6` bins around the nearest harmonic target;
- local-background exclusion: the harmonic peak neighborhood ±`1` bin;
- local SNR multiplier: `3.0`;
- relative-to-strongest harmonic support floor: `0.10`;
- minimum supported harmonic orders: `3`;
- minimum weighted harmonic coverage: `0.35`;
- minimum total innovation L2 norm: `1e-6`;
- harmonic template weights: `1/h`, L2-normalized, unchanged in form from V6;
- composite synthetic necessity threshold: `0.01`, unchanged from frozen V6.

No constant above may be changed after seeing iteration-1 results.

### 6.2 Per-anchor harmonic observations

For candidate MIDI `m` and each frozen cents anchor `c`:

1. Set anchored fundamental `f0 = 440 * 2 ** (((m + c/100) - 69) / 12)`.
2. For harmonic orders `h = 1..6` until Nyquist, target `h * f0`.
3. Find the nearest FFT bin and select the maximum innovation value in its ±1-bin peak neighborhood. Record both selected bin and nonnegative peak value `p_h`.
4. Estimate local background `b_h` as the median innovation value in the ±6-bin target neighborhood after excluding the ±1-bin peak neighborhood. If no finite background bins exist, the anchor is invalid/fail-closed.
5. Let `P = max_h p_h`. If total innovation L2 norm is below `1e-6`, if fewer than three harmonic orders exist below Nyquist, or if `P <= 0`, the candidate is invalid/fail-closed.
6. Harmonic order `h` is supported only if
   `p_h >= max(3.0 * b_h, 0.10 * P, eps)`,
   where `eps = max(P * 1e-12, 1e-15)`.
7. Weighted harmonic coverage is
   `sum(1/h for supported h) / sum(1/h for available h)`.

An anchor is eligible only when at least three harmonic orders are supported **and** weighted harmonic coverage is at least `0.35`. There is no minimum fundamental-to-maximum-harmonic ratio in V3 eligibility; the fundamental may be below the support floor if the remaining multi-harmonic evidence passes all frozen gates.

### 6.3 Deterministic anchor selection

Evaluate every frozen cents anchor. Choose the eligible anchor with the lexicographically greatest tuple:

1. weighted harmonic coverage;
2. supported-harmonic count;
3. weighted normalized strength `sum((1/h) * (p_h/P)) / sum(1/h)`;
4. smallest absolute cents offset;
5. smallest signed cents offset.

If no anchor is eligible, the candidate is physically implausible for this V3 synthetic iteration.

For an eligible candidate, its dictionary template uses the chosen harmonic bins and the same L2-normalized `1/h` weights as frozen V6. Unsupported harmonics remain in the template; support determines eligibility, not learned template weights.

## 7. FROZEN SYNTHETIC COMPOSITE NECESSITY CHECK

Alias and lower-owner protection must not be weakened just because V3 admits weak-fundamental candidates into the dictionary.

The isolated synthetic harness must therefore reproduce, without importing or executing the V6 classifier, the frozen shared-dictionary necessity calculation over V3-eligible MIDI templates:

1. build V3 templates for all MIDI 40–88 against the synthetic innovation spectrum;
2. union their template bins into the observed feature vector;
3. fit nonnegative least squares on the full dictionary;
4. remove the selected candidate column and refit;
5. calculate
   `necessityFraction = (withoutSelectedResidual - fullResidual) / max(featureEnergy, 1e-15)`;
6. composite PASS requires selected coefficient `> 0` and `necessityFraction >= 0.01`.

This synthetic reproduction exists only to prove that the new eligibility stage does not bypass the frozen necessity concept. It must not call `classify_audio_event`, `_fit_onset_birth`, Basic Pitch, or any workflow.

## 8. PROSPECTIVE SYNTHETIC FIXTURE CONSTRUCTION

Fixtures are deterministic innovation spectra, not repository WAVs or real recordings. Frequencies use `np.fft.rfftfreq(8192, 1/44100)`. A harmonic-series fixture deposits each specified amplitude at the nearest bin to `h * f0` and half that amplitude at each immediately adjacent bin. Additive background, where specified, is generated from NumPy RNG seed `730915` and absolute zero-mean Gaussian samples scaled by the stated background level. No fixture may be changed after seeing results.

All named fixtures below use selected MIDI 69 unless another selected MIDI is stated.

### 8.1 Required PASS fixtures

- `strong_fundamental_inclip`: one MIDI-69 series, cents `0`, amplitudes `[1.00, 0.55, 0.36, 0.24, 0.17, 0.12]`, background `0.002`, context label `ordinary-in-clip`; selected 69 composite PASS.
- `weak_fundamental_bright_inclip`: MIDI 69, cents `0`, amplitudes `[0.03, 1.00, 0.72, 0.48, 0.30, 0.18]`, background `0.002`, ordinary-in-clip; selected 69 template eligible and composite PASS.
- `zero_fundamental_upper_support_inclip`: MIDI 69, cents `0`, amplitudes `[0.00, 1.00, 0.65, 0.45, 0.28, 0.16]`, background `0.002`, ordinary-in-clip; selected 69 template eligible and composite PASS.
- `weak_fundamental_clip_start_post_only`: same harmonic amplitudes as `weak_fundamental_bright_inclip`, context label `clip-start-post-only`, `syntheticPreContextUsed = false`; selected 69 template eligible and composite PASS. This tests only the physical-template stage with one-sided synthetic support; it does not replace or execute V2 boundary classification.
- `true_polyphony_a3_plus_e5`: simultaneous MIDI 57 amplitudes `[1.00, 0.60, 0.40, 0.30, 0.20, 0.15]` plus MIDI 76 amplitudes `[0.15, 1.00, 0.70, 0.45, 0.30, 0.20]`, both cents `0`, background `0.002`; selected MIDI 76 composite PASS.
- `true_polyphony_a4_plus_b4`: simultaneous MIDI 69 amplitudes `[1.00, 0.50, 0.32, 0.22, 0.15, 0.10]` and MIDI 71 amplitudes `[0.80, 0.55, 0.35, 0.24, 0.16, 0.11]`, background `0.002`; selected 69 composite PASS and selected 71 composite PASS.

### 8.2 Prospective timbre/detuning PASS matrix

For each profile below, test cents `-30`, `0`, and `+30`, background `0.002`, ordinary-in-clip, selected MIDI 69. All nine combinations must be template eligible and composite PASS.

- `bright`: `[0.05, 1.00, 0.80, 0.60, 0.45, 0.30]`;
- `dark`: `[1.00, 0.45, 0.22, 0.12, 0.08, 0.05]`;
- `fundamental_notch`: `[0.02, 0.85, 0.70, 0.50, 0.12, 0.11]`.

This matrix is frozen before execution and may not be expanded only after a failure in order to rescue the iteration.

### 8.3 Required FAIL fixtures

- `octave_alias_lower_a3_selected_a4`: only MIDI 57 with amplitudes `[1.00, 0.60, 0.40, 0.30, 0.20, 0.15]`, selected MIDI 69; composite FAIL even if MIDI 69 becomes V3-template-eligible.
- `third_harmonic_owner_a3_selected_e5`: only MIDI 57 with the same amplitudes, selected MIDI 76; composite FAIL.
- `two_harmonics_only`: selected MIDI 69 support amplitudes `[0.00, 1.00, 0.80, 0.00, 0.00, 0.00]`, background `0.002`; template ineligible and composite FAIL.
- `single_peak_only`: selected MIDI 69 support amplitudes `[0.00, 1.00, 0.00, 0.00, 0.00, 0.00]`, background `0.002`; template ineligible and composite FAIL.
- `broadband_noise`: no harmonic series, deterministic absolute Gaussian background scale `0.02`; template ineligible and composite FAIL.
- `near_silence`: all-zero spectrum except deterministic absolute Gaussian background scale `1e-10`; fail closed for insufficient innovation and composite FAIL.
- `nonharmonic_impulses`: deterministic peaks of amplitude `1.0, 0.8, 0.6, 0.4` at frequencies `311, 503, 911, 1427` Hz plus background `0.002`, selected MIDI 69; template ineligible and composite FAIL.
- `clip_start_insufficient_support`: context label `clip-start-post-only`, `syntheticPreContextUsed = false`, amplitudes `[0.00, 0.20, 0.00, 0.00, 0.00, 0.00]`, background `0.002`; template ineligible and composite FAIL.

## 9. IMMUTABLE ACCEPTANCE GATES

Iteration 1 is PASS only if **all** of the following are true on the first committed implementation/test pair:

1. every required PASS fixture and every one of the nine timbre/detuning matrix cases gives the exact frozen expected decision;
2. every required FAIL fixture gives the exact frozen expected decision;
3. octave/lower-owner failures are evaluated at the composite V3-template + unchanged-necessity stage; they may not be declared safe merely because another heuristic rejects them;
4. both selected notes in `true_polyphony_a4_plus_b4` independently pass the composite test, and selected MIDI 76 passes in `true_polyphony_a3_plus_e5`;
5. weak/zero-fundamental PASS fixtures are not rescued by changing `0.20`; the V3 criterion contains no fundamental/max eligibility threshold;
6. the module does not import or execute Basic Pitch, V6 `classify_audio_event`, V6 `_fit_onset_birth`, subprocesses, network clients, workflow APIs, or real-media loaders;
7. no test opens any repository dataset/audio/model artifact; fixture data are generated in memory only;
8. the test harness runs the full fixture set three times in the same process and canonical serialized decision/diagnostic records are byte-identical across all three repetitions;
9. nonfinite spectrum values, shape mismatch, negative innovation, missing frequency bins, or fewer than three available harmonic orders fail closed with deterministic error/status output;
10. existing frozen V2/V6 files, workflow files, `songsterr_pipeline/**`, V143/Gomyway, and all closed lines remain byte-untouched by this iteration.

There are no partial-pass, xfail, tolerance-by-inspection, or post-result exception rules. Any gate failure freezes iteration 1 as FAIL.

## 10. IMPLEMENTATION/EXECUTION ORDER

After this PRE commit exists:

1. create only `physical_template_plausibility_v3.py` and its dedicated test file;
2. review the diff against this PRE before execution;
3. run only the dedicated local synthetic test file;
4. do not run broad repository tests if they could invoke unrelated workflows/models/media paths;
5. record the first committed implementation result without tuning;
6. create `SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT.md` and update the current-state checkpoint;
7. if any immutable gate fails, stop iteration 1. Any algorithm/constant/fixture revision requires a new prospective PRE iteration before rerun.

## 11. AUTHORIZATION AFTER SYNTHETIC RESULT

Even a complete iteration-1 synthetic PASS does **not** authorize editing frozen V6 in place or running any real-media/model correctness evaluation. Integration into a successor classifier and any real evaluation require a separately frozen next-stage PRE and explicit authorization consistent with the current-state checkpoint.
