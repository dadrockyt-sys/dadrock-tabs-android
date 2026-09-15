# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — boundary-aware V2 repair prospectively frozen and implemented; synthetic gate + one real diagnostic authorized but not yet executed
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
Hardening result: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_HARDENING_V1_RESULT.md`
Latest completed real-audio diagnostic: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_RESULT.md`
Active V2 PRE: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md`

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless explicitly reopened.
- Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP/research stays under `scripts/songsterr-fresh/`.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Synthetic/smoke diagnostics are never authoritative correctness validation.

## GLOBAL AUTHORIZATION — UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

The user's `Please try the run again` authorization was consumed by run `34938917218`, attempt 1.

The user's subsequent instruction `Lets take what was learned, repair and run again` now authorizes one boundary-repair cycle plus exactly one new non-authoritative EGFxSet V2 diagnostic, but only after the prospectively frozen synthetic gates pass. This new authorization does not change any global field and does not authorize Basic Pitch inference, threshold tuning from the real result, alternate candidates, or repeated real retries.

## HISTORICAL EGFxSET ALL-EVENTS SMOKE — STILL FROZEN FAIL

Candidate: EGFxSet v1.0 `Clean.zip#Clean/Bridge/6-0.wav`, member SHA-256 `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`, truth string 6 / fret 0 / MIDI 40.

Repaired Basic Pitch run `34936227380` emitted immutable proposals `[40,68]`; `basic-pitch.json` SHA-256 is `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`; note identity SHA-256 is `2e30685479444a8120dc3490c9c41329a89e57aa16979de42053b89a4bbb0444`.

Historical score remains `PASS_RUNTIME`, `FAIL_PITCH`, `FAIL_POSITION`, overall `FAIL_NON_AUTHORIZING_SMOKE`. Never rewrite it into a PASS.

## PIPELINE HARDENING V1 — CODE/SYNTHETIC GREEN

Combined regression run `34938422696`, job `104281318739`, passed:
- confidence-independent qualification;
- exact identity/population fail-closed behavior;
- explicit rejected-proposal preservation;
- physical-position ambiguity reporting;
- synthetic DSP note-birth tests.

Core design remains:
- Basic Pitch events are proposals only;
- only independently `corroborated` proposals promote;
- `rejected` proposals remain preserved but do not promote;
- `insufficient` remains unresolved/fail-closed;
- Basic Pitch confidence is diagnostic-only.

## LATEST COMPLETED HARDENED REAL-AUDIO DIAGNOSTIC — FROZEN FAIL AT LEFT BOUNDARY

PRE: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_PRE.md`, commit `8b741a8b25b61966c832860f4d91f42a018f898e`.

Result: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_RESULT.md`, commit `e2935b5f9c3ecb14baf770e492d03ea9d8fcfc3b`.

Execution:
- workflow `.github/workflows/songsterr-egfxset-hardened-one-shot.yml`
- workflow commit `bba6f954d55d54ce0bf660214a059b695c57481d`
- run `34938917218`
- job `104282855445`
- attempt `1`
- artifact `10384459031`
- artifact ZIP SHA-256 `a0a6a0021726c40fd4c2381c118a90e85105117b6689cfdc393e7e282a89f3a9`
- `result.json` SHA-256 `6bc52feef13bcdec57b76721eef87ebf94a157b7d4d0a8f4f08590ba95178a06`
- `qualification.json` SHA-256 `784579dd791136424142bb899455cfc6c9242fd8cc2a3efba9c8b11dfa342e85`

All infrastructure and pipeline stages completed successfully. No Basic Pitch inference occurred; the prior immutable `[40,68]` artifact was reused.

Observed V1 qualifier result:
- MIDI 40 at `0.011609977324263039 s`: `rejected`, reason `OK_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE`, left zero-padding `3072` samples, necessity fraction `0.0`;
- MIDI 68 at `0.3599092970521542 s`: `rejected`, reason `OK`, zero left-padding, necessity fraction `0.000513675778819313`.

Frozen V1 hardened score:
- `PASS_INPUTS`
- `FAIL_QUALIFICATION`
- `FAIL_PROMOTION`
- `FAIL_POSITION`
- overall `FAIL_HARDENED_NON_AUTHORIZING_DIAGNOSTIC`

Raw proposals `[40,68]` were preserved. Rejected evidence preserved both. No events promoted. Never reinterpret this historical V1 result.

## ACTIVE BOUNDARY QUALIFIER V2 REPAIR — FROZEN BEFORE REAL EXECUTION

PRE checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md`
commit `819d7a9a855d6f067aa40a007fdd0570d231d782`.

The concrete repair removes synthetic pre-context ownership from clip-start decisions.

### Normal in-clip path

When genuine required left context exists, use the existing frozen V6 complex-harmonic onset-birth classifier unchanged.

### Clip-start path

When onset is earlier than the inherited `3584`-sample left-context requirement:

- never zero-pad or fabricate pre-audio;
- use exactly `8192` genuine post-onset samples at 44.1 kHz;
- demean + Hann + 8192-point real FFT magnitude;
- inherit unchanged playable MIDI `40..88`, six-harmonic dictionary, RMS/feature-energy floors, physical-template fundamental ratio `0.20`, and necessity minimum `0.01`;
- use full-vs-selected-removed NNLS necessity;
- detect lower-fundamental harmonic owners for harmonics 2..6 within ±50 cents;
- a lower owner dominates only when it has positive coefficient, necessity >=0.01, and necessity >= selected-candidate necessity;
- corroborate only if the selected template is physically valid, selected coefficient >0, selected necessity >=0.01, and no dominant lower harmonic owner exists;
- missing genuine post-context or numerical/support failure remains `insufficient`.

No special-case MIDI values, EGFxSet labels, candidate confidences, or observed real-audio DSP measurements are embedded in the rule.

Implemented, CI-skipped while building the repair:

- `scripts/songsterr-fresh/clip_start_pitch_presence_v1.py`, commit `e24aea935058281c5d75b3a700759e055607e735`
- `scripts/songsterr-fresh/qualify_basic_pitch_note_births_v2.py`, commit `eeed1e8b11a53bfc4e69967de0ad49d0655867ed`
- `scripts/songsterr-fresh/build_qualified_isolated_polyphonic_note_evidence_v2.mjs`, commit `5ff87dbf962acc3dad1d474da013299019bb6f03`
- `scripts/songsterr-fresh/adapt_qualified_note_evidence_v2.mjs`, commit `ead4f6c88c4a0337621cb7cfa0072ab540031fe3`
- `scripts/songsterr-fresh/test_qualify_basic_pitch_note_births_v2.py`, commit `8842c2cb9b4702de2bbcd25145c864c82447fc7e`
- `scripts/songsterr-fresh/test_model_note_qualification_v2.mjs`, commit `f7ff6e7b2b1a242a2f513d0b4022d6069cc88eb4`

## NEXT ACTION — AUTHORIZED, NOT YET CONSUMED

Create one path-triggered successor workflow that first runs the frozen V2 synthetic gates in the exact Python/NumPy/SciPy environment. Only if those gates pass may that same workflow fetch the exact immutable EGFxSet WAV and prior Basic Pitch artifact and execute exactly one V2 real diagnostic.

Frozen real diagnostic PASS requires:
- exact inputs;
- raw proposals `[40,68]`;
- MIDI 40 `corroborated`;
- MIDI 68 `rejected`;
- zero insufficient proposals;
- promoted `[40]`;
- rejected-preserved `[68]`;
- promoted MIDI 40 maps uniquely to string 6 / fret 0 / reconstructed MIDI 40.

Any other real observation is FAIL and consumes the one real V2 authorization. No same-authorization retry.

## AUTHORITATIVE ROUTE

The completed software-lineage no-gap conclusion remains unchanged. Official correctness still requires the frozen physical calibrated route, currently budget-paused. Do not manufacture another synthetic software-lineage gate.
