# PRE — Songsterr Fresh V7 Representation Bridge Synthetic Iteration 1

Status: **PROSPECTIVE / FROZEN ON THIS COMMIT**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
PRE parent head: `089d6a152f9ce2bce499775b74b6e9cb4e7cdfc4`
Authority: user instruction `Let's wire this better please 🙏`

## 1. Purpose and motivation

This PRE opens a **synthetic-only representation-bridge research line** after the frozen V7 real-evaluation attempt was blocked by its prerequisite before any real/model payload access.

Frozen failure record:

- `docs/checkpoints/SONGSTERR_FRESH_V7_REAL_EVALUATION_RESULT.md`
- frozen result commit `089d6a152f9ce2bce499775b74b6e9cb4e7cdfc4`
- run `35051186125`, attempt 1
- first ordinary in-clip synthetic E2 proposal expected `corroborated` but observed `SELECTED_TEMPLATE_INELIGIBLE`
- all 17 frozen V3 detuning anchors reported `INSUFFICIENT_MULTI_HARMONIC_SUPPORT`
- prior Basic Pitch artifact fetch, EGFxSet fetch and real V7 qualification were all skipped.

The earlier V7 integration PASS proved only that already-constructed V3 synthetic spectra can traverse the V7 wrapper consistently. It did not prove that frozen V6 **audio-derived onset innovation** has the same spectral support geometry as the narrow-line spectra used by the V3 synthetic research suite.

This PRE tests and, if the frozen gates pass, establishes only that missing representation seam. It is not a correctness, calibration, model-validation, holdout or delivery gate.

## 2. Frozen representation hypothesis

Frozen V6 analysis geometry is:

- analysis frame: `2048` samples;
- analysis window: Hann;
- FFT size: `8192`;
- zero-padding factor: `8192 / 2048 = 4`;
- onset evidence: nonnegative magnitude innovation on the frozen `8192`-point real-FFT grid.

A Hann-windowed sinusoid has its first spectral null approximately two **native frame-DFT bins** from its center. Under the frozen 4x zero-padding, that deterministic main-lobe half-width occupies approximately `2 * 4 = 8` bins on the frozen 8192-point grid.

Frozen V3 synthetic spectra were constructed as narrow local peaks. Frozen V3 local-background estimation uses nearby bins within radius 6, outside only the immediate peak radius. When raw V6 Hann-windowed innovation is supplied directly, those background bins can fall inside the same deterministic Hann main lobe and therefore treat a physical harmonic's own leakage as local background.

**Iteration-1 hypothesis:** before frozen V3 evaluation, convert raw V6 onset innovation to a deterministic line-evidence representation by retaining local positive maxima and suppressing only the deterministic Hann main-lobe neighborhood around each stronger/equal retained maximum. The suppression radius is derived from frozen V6 geometry, not selected from any real observation:

`LINE_SUPPRESSION_RADIUS_BINS = 2 * (FFT_SIZE / FRAME_SAMPLES) = 8`.

No V3 threshold, V6 threshold, MIDI-specific rule, EGFxSet value or learned parameter may be changed.

## 3. Frozen bridge contract

The proposed bridge may only transform an already-constructed frozen V6 nonnegative onset-innovation vector.

Required behavior:

1. input must be a one-dimensional finite nonnegative array of exact frozen real-FFT length `FFT_SIZE / 2 + 1 = 4097`;
2. output has the same shape and frequency grid;
3. the bridge may only set bins to zero or retain their exact original amplitude; it may never boost, interpolate, shift, invent or renormalize energy;
4. use fixed suppression radius `8` bins derived above;
5. a positive bin is retained only if it is the deterministic local maximum within its clipped ±8-bin neighborhood;
6. equal-amplitude ties resolve to the lowest bin index so output is deterministic;
7. every non-retained bin is zero;
8. zero input remains zero;
9. malformed, nonfinite, negative or wrong-shaped input fails closed;
10. bridge code itself performs no file, network, subprocess, model, GPU, repository or media I/O.

This bridge is explicitly a **representation adapter**, not a pitch decision rule. It does not inspect selected MIDI, proposal confidence, dataset identity, expected class, EGFxSet metadata or reference truth.

## 4. Frozen/read-only dependencies

The following are byte-for-byte read-only throughout this iteration:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`;
- `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3.py`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration2.py`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration3.py`;
- `scripts/songsterr-fresh/test_physical_template_plausibility_v3_iteration2.py`;
- `scripts/songsterr-fresh/test_physical_template_plausibility_v3_iteration3.py`;
- `scripts/songsterr-fresh/onset_birth_corroboration_v7.py`;
- all V2/clip-start implementation files;
- all prior V3/V7 PRE/result checkpoints;
- `songsterr_pipeline/**`;
- `main`, Production, every closed line, and archived V143/Gomyway.

Historical thresholds remain frozen, including V3 `necessityFraction >= 0.01` and `candidateEvidenceFraction >= 0.10`. The historical V6 `0.20` fundamental ratio is not edited or reused as a bridge parameter.

## 5. Prospective write boundary

After this PRE is frozen, iteration 1 may create/change only:

- `scripts/songsterr-fresh/v6_innovation_line_bridge_v1.py` — new pure in-memory representation bridge;
- `scripts/songsterr-fresh/test_v6_innovation_line_bridge_v1.py` — new synthetic seam/regression test;
- `.github/workflows/songsterr-v7-representation-bridge-synthetic-one-shot.yml` — new self-scoped synthetic-only one-shot runner, only if required for execution;
- `docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_RESULT.md` — first-result record;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` — state-only updates.

No other executable or workflow file may change under this PRE. Any additional path requires a new prospective PRE before creation.

## 6. Frozen synthetic gates

The first committed bridge/test pair must evaluate the complete frozen V6 audio-derived fixture population from `v6_onset_birth_synthetic_fixtures.json`, using the frozen V6 audio synthesis and onset-innovation construction, then the new bridge, then frozen V3 iteration-3 composite evaluation.

### 6.1 Full 23-fixture V6 audio population

All 23 existing expected classifications are frozen as bridge expectations before execution:

- `clean_low_m40` -> `onset-birth-corroborated-candidate`
- `clean_mid_m64` -> `onset-birth-corroborated-candidate`
- `clean_high_m88` -> `onset-birth-corroborated-candidate`
- `detune_plus25_m64` -> `onset-birth-corroborated-candidate`
- `detune_minus25_m64` -> `onset-birth-corroborated-candidate`
- `attack_noise_true_m64` -> `onset-birth-corroborated-candidate`
- `already_sounding_m64` -> `not-onset-birth-corroborated`
- `octave_alias_sel72_actual60` -> `not-onset-birth-corroborated`
- `octave_alias_sel79_actual67` -> `not-onset-birth-corroborated`
- `selected64_enters_over_existing60` -> `onset-birth-corroborated-candidate`
- `simultaneous_dyad_sel60` -> `not-onset-birth-corroborated`
- `simultaneous_dyad_sel64` -> `onset-birth-corroborated-candidate`
- `simultaneous_triad_sel60` -> `onset-birth-corroborated-candidate`
- `simultaneous_triad_sel64` -> `onset-birth-corroborated-candidate`
- `simultaneous_triad_sel67` -> `onset-birth-corroborated-candidate`
- `neighbor_sel60_actual61` -> `not-onset-birth-corroborated`
- `reattack_m64` -> `onset-birth-corroborated-candidate`
- `unrelated_transient_only_sel64` -> `not-onset-birth-corroborated`
- `weak_selected64_under60` -> `not-onset-birth-corroborated`
- `silence` -> `insufficient-evidence`
- `low_noise` -> `insufficient-evidence`
- `truncated_pre_context` -> `insufficient-evidence`
- `truncated_post_context` -> `insufficient-evidence`.

For fixtures with insufficient pre/post context or insufficient V6 audio/innovation support, the bridge path must fail closed without fabricating context or spectral energy.

For fully analyzable fixtures, mapping is frozen:

- frozen V3 iteration-3 PASS -> `onset-birth-corroborated-candidate`;
- frozen V3 iteration-3 FAIL -> `not-onset-birth-corroborated`.

Every bridge-path PASS must preserve finite frozen V3 diagnostics `necessityFraction >= 0.01` and `candidateEvidenceFraction >= 0.10`.

### 6.2 Frozen V3 direct-spectrum regression

The untouched frozen iteration-3 test must still pass all 34 direct-spectrum fixtures exactly as previously recorded. The bridge must not be inserted into or used to reinterpret those frozen direct-spectrum tests.

### 6.3 Bridge structural invariants

Prospective structural cases must verify:

- zero vector -> zero vector;
- one isolated positive peak is retained at identical amplitude;
- a synthetic 4x-zero-padded Hann main-lobe cluster retains only its deterministic center/maximum;
- two peaks separated by more than 8 bins both survive;
- lower-amplitude bins within 8 bins of a stronger local maximum are suppressed;
- equal maxima within one neighborhood deterministically retain the lower bin index;
- output nonzero values are a subset of exact input nonzero values and amplitudes are unchanged;
- scaling a finite nonnegative input by a positive scalar preserves retained-bin indices and scales retained amplitudes by the same scalar;
- malformed rank, length, negative or nonfinite input fails closed.

### 6.4 Determinism

Run the complete bridge test population three times in-process. Outcomes, retained-bin identities and V3 diagnostic decisions must be deterministic.

## 7. Workflow isolation / execution boundary

The prior automatic-trigger audit established no catch-all `scripts/songsterr-fresh/**` push path. Since that audit, the only newly added automatic real-evaluation workflow is `.github/workflows/songsterr-egfxset-v7-real-evaluation-one-shot.yml`, which is self-scoped to its own YAML path and therefore cannot be triggered by the two proposed bridge Python files or this PRE/result documentation.

Before executable bridge files are committed, re-check current workflow changes since the prior audit. If any current automatic path can match the proposed bridge files, stop and harden the boundary prospectively without executing that workflow.

If repository execution requires a workflow, only the new prospectively allowed `songsterr-v7-representation-bridge-synthetic-one-shot.yml` may be created. It must:

- trigger only on a push changing **its own exact YAML path**;
- run only frozen blob checks plus the two synthetic test commands defined below;
- contain no `curl`, `wget`, artifact download, dataset URL, model invocation, Basic Pitch, Demucs, real-media path, protected-song path, dispatch, repository mutation or GPU/heavy-compute step;
- never call the prior EGFxSet one-shot workflow.

## 8. First-run policy

Before any bridge execution:

1. commit the first bridge module and test pair;
2. verify PRE-to-pair diff contains exactly those two new Python files;
3. record exact Git blobs;
4. perform a static forbidden-import/I/O scan;
5. if a synthetic workflow is needed, commit its frozen self-scoped YAML only after the pair is fixed;
6. execute exactly once:
   - `python scripts/songsterr-fresh/test_v6_innovation_line_bridge_v1.py`
   - and, in the same first attempt, the untouched regression `python scripts/songsterr-fresh/test_physical_template_plausibility_v3_iteration3.py`.

Freeze the first result exactly as observed. No same-iteration rescue rerun, fixture edit, expected-result edit, radius edit, threshold edit or code repair is allowed after first output is observed. Any failed iteration requires a new prospective iteration PRE.

## 9. Explicit prohibitions

This PRE does **not** authorize:

- EGFxSet access or retry;
- prior Basic Pitch artifact download;
- Basic Pitch or Demucs/model inference;
- real candidate/media access of any kind;
- V6/V7 real correctness execution;
- changing V6, V2, V3 or V7 frozen source;
- changing `FRAME_SAMPLES`, `FFT_SIZE`, V3 support/background radii, V3 thresholds, necessity/evidence thresholds or historical V6 thresholds;
- MIDI-specific or dataset-specific branches;
- learned/tuned bridge parameters;
- AG-PT-set or rejected-holdout reopening;
- protected-song work;
- physical calibration/capture;
- `songsterr_pipeline/**`, `main`, Production or reserved GFN changes;
- GOAT/reference work;
- archived V143/Gomyway.

## 10. Authority after this PRE

A PASS would establish only that a deterministic geometry-derived representation bridge reconciles the frozen V6 synthetic audio innovation with the frozen V3 evidence model while preserving the prospectively frozen synthetic protections. It would not authorize integration into Production or any real/model run.

Any subsequent successor integration requires its own prospective integration PRE. Any future EGFxSet or other real-media evaluation requires a new separately frozen real-evaluation PRE and **fresh explicit user authorization** after this synthetic line is complete.