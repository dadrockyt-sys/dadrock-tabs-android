# Songsterr Fresh V6 — EGFxSet One-Shot Smoke Result

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: `FAIL_NON_AUTHORIZING_SMOKE_RUNTIME`
Media delta: frozen candidate accessed exactly for the authorized one-shot; no alternate candidate inspected or processed

## Scope

This checkpoint records the completed optional $0 one-file external audio smoke test authorized by the user after the candidate, runtime settings, and scoring rule were frozen. It is not V6 correctness validation, does not authorize Basic Pitch/V6/correctness globally, and does not replace the budget-paused physical holdout.

Archived V143/Gomyway, Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD, and reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched and closed.

## Candidate — FROZEN BEFORE MEDIA ACCESS

Dataset: **EGFxSet — Electric Guitar Effects dataset**
Canonical dataset record: Zenodo DOI `10.5281/zenodo.7044411`, version 1.0.
Independent project description: `https://egfxset.github.io/`.

Published metadata establishes that EGFxSet contains all notes of a standard-tuned 22-fret Stratocaster and that each clean tone has independent string/fret annotation. The official project documentation defines the string-fret tuple as string number `1..6` and fret `0..22`, with `0` denoting an open string.

Frozen source identity:

- archive: `Clean.zip`
- published archive MD5: `cdb1b401960f56becc8640387910e78a`
- member: `Clean/Bridge/6-0.wav`
- published physical label: string `6`, fret `0`
- tuning: standard guitar EADGBE
- expected MIDI: `40` (E2)

The authorized run downloaded `Clean.zip`, verified the archive against the frozen MD5, and extracted only the frozen member for processing.

Observed frozen member identity:

- bytes: `722976`
- SHA-256: `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`

No alternate EGFxSet audio member was decoded, auditioned, waveform-inspected, or processed.

## Plausibly untouched check

Before any media access, the candidate was selected from independent metadata. The active branch had been reviewed from HEAD `cf222e7f7017ae814290abdddca7b3f0ddf9cbfd`; the latest 100 commit metadata entries searched in that review contained no `EGFx` / `EGFxSet` reference. This was supporting evidence only, not proof that no historical local access ever occurred.

## Frozen pipeline entry and physical-position mapping

Current isolated-guitar transcription entry point:
`scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py`

The frozen test required Spotify Basic Pitch `0.4.0`, CPU, minimum MIDI 40, maximum MIDI 88, onset threshold 0.5, frame threshold 0.3, minimum note length 127.7 ms, bends false, and melodia true.

The deterministic fresh core maps MIDI to playable string/fret positions using standard guitar tuning MIDI `[40,45,50,55,59,64]`. MIDI `40` maps uniquely to string `6`, fret `0`.

## Frozen scoring rule

The scoring rule was fully frozen before output observation:

1. Run `transcribe_isolated_guitar_basic_pitch.py` exactly once under the frozen settings on CPU.
2. No listening, waveform inspection, trimming, onset hand-labeling, denoising, EQ, gain tuning, threshold changes, retries, or alternate-candidate substitution.
3. `PASS_PITCH` requires a non-empty decoded-note artifact whose complete emitted MIDI set is exactly `{40}`; repeated MIDI-40 segments are allowed.
4. `PASS_POSITION` requires every emitted event to map through the unchanged deterministic standard-guitar mapper to exactly string `6`, fret `0`, reconstructed MIDI `40`.
5. `PASS_RUNTIME` requires the one Basic Pitch invocation and deterministic mapping to complete and produce the expected parseable artifacts without retry.
6. Overall PASS requires runtime + pitch + position PASS. No independent onset truth exists, so official V6 onset scoring is not used.
7. Neither PASS nor FAIL authorizes V6/correctness/model validation/customer eligibility/delivery.

## Scoped one-run authorization — CONSUMED

On 2026-09-15 America/Toronto, immediately after being presented with the exact required permission for the frozen EGFxSet candidate, the user replied: `I authorize one set 💪💚`.

That was recorded as authorization for **exactly one non-authorizing Basic Pitch smoke run** on the frozen `Clean/Bridge/6-0.wav` candidate under the already frozen defaults, deterministic mapping, and scoring rule.

The authorization has now been consumed. **No retry is authorized.**

Global current-state fields remain unchanged:

- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## Official one-shot execution result

Workflow commit: `9ee39e3daf462e4b15f9e72564a4a937a3424088`
Workflow: `.github/workflows/songsterr-egfxset-one-shot.yml`
Run: `34935565328`
Job: `104272581611`
Run attempt: `1`
Workflow conclusion: `success` because diagnostic scoring/artifact upload were deliberately allowed to complete after inference failure.
Artifact: `10383088803`, `songsterr-egfxset-one-shot`
Artifact ZIP digest: `sha256:d4626ab210f492828367451cad06992aa06db56052093586defc33e696a5d2e9`

Execution stages:

- Python 3.10.21 setup: PASS
- `basic-pitch==0.4.0` installation/version check: PASS
- frozen `Clean.zip` download: PASS
- archive MD5 verification: PASS
- exact frozen member extraction: PASS
- **single Basic Pitch invocation: FAIL**
- frozen scorer execution: PASS
- immutable diagnostic artifact upload: PASS

### Exact runtime failure class

`basic-pitch==0.4.0` installed `numpy==2.2.6` and `tflite-runtime==2.14.0` on the Linux Python 3.10 runner. At the one permitted `predict()` invocation, TFLite initialization failed before model inference because the TFLite extension was compiled against NumPy 1.x and could not run with NumPy 2.2.6.

Primary error:

`AttributeError: _ARRAY_API not found`

Basic Pitch then reported that its bundled `nmp.tflite` model could not be loaded with the installed TensorFlowLite runtime and exited with code 1.

This failure occurred during model initialization. No primary `basic-pitch.json` decoded-note artifact was produced.

## Frozen score

Diagnostic result contract: `songsterr-fresh-egfxset-one-shot-smoke-v1`

- dependency outcome: `success`
- media outcome: `success`
- inference outcome: `failure`
- primary output present: `false`
- decoded note count: `0`
- unique MIDI values: `[]`
- MIDI histogram: `{}`
- runtime: `FAIL_RUNTIME`
- pitch: `FAIL_PITCH`
- position: `FAIL_POSITION`
- overall: `FAIL_NON_AUTHORIZING_SMOKE`

The pitch and position failures are mechanical consequences of the absent decoded-note artifact. **They are not evidence that Basic Pitch predicted a wrong pitch or wrong physical position.** The model never reached a successful inference result.

## Interpretation / authority

The only supported conclusion is:

**The authorized EGFxSet one-file smoke attempt failed at runtime before decoded-note output because of a NumPy 2.x / TFLite binary incompatibility. It produced no evidence for or against MIDI-40 / string-6-fret-0 recognition.**

Do not reinterpret this as an audio-model correctness failure. Do not tune from it. Do not retry, pin NumPy `<2`, swap inference backends, or otherwise repair-and-rerun under the consumed authorization.

Any later repaired smoke execution would require a new explicit prospective authorization and a separately frozen environment correction before media/model execution. That would still be non-authoritative and would not replace the physical calibrated holdout.

The authoritative next validation route remains the physical calibrated holdout and remains budget-paused.
