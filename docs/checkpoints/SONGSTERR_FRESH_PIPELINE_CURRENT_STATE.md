# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — hardened EGFxSet one-shot executed; inputs and all processing stages passed, but genuine near-start MIDI 40 was rejected by the left-boundary DSP policy
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
Hardening result: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_HARDENING_V1_RESULT.md`
Latest real-audio diagnostic: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_RESULT.md`

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

The user's `Please try the run again` authorization was consumed by run `34938917218`, attempt 1. No retry is authorized.

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

## LATEST HARDENED REAL-AUDIO DIAGNOSTIC — FAIL AT LEFT BOUNDARY

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

Observed qualifier result:
- MIDI 40 at `0.011609977324263039 s`: `rejected`, reason `OK_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE`, left zero-padding `3072` samples, necessity fraction `0.0`;
- MIDI 68 at `0.3599092970521542 s`: `rejected`, reason `OK`, zero left-padding, necessity fraction `0.000513675778819313`;
- candidate confidence not used for either decision.

Frozen score:
- `PASS_INPUTS`
- `FAIL_QUALIFICATION`
- `FAIL_PROMOTION`
- `FAIL_POSITION`
- overall `FAIL_HARDENED_NON_AUTHORIZING_DIAGNOSTIC`

Raw proposals `[40,68]` were preserved. Rejected evidence preserved both. No events promoted.

### Key finding

The original extra-note weakness is partly solved: MIDI 68 no longer auto-promotes and is independently rejected.

The new concrete weak point is the left clip boundary. The genuine MIDI 40 proposal occurs only about 11.6 ms after clip start. The inherited V6 onset-birth classifier requires about 81.3 ms of left context at 44.1 kHz. The wrapper inserted 3072 synthetic zero samples to make the classifier evaluable, then allowed the resulting analysis to produce a hard negative. This is not safe: fabricated pre-context is not genuine physical pre-onset evidence.

Do not lower thresholds, hand-promote MIDI 40, or retroactively change this result.

## NEXT ENGINEERING DIRECTION — NO REAL RUN AUTHORIZED

Before another real-media run, prospectively design a boundary-aware qualification policy using synthetic/non-EGFxSet fixtures only.

Minimum semantic correction: when genuine required left context is absent, synthetic zero padding must not by itself be sufficient to support a hard rejection. Boundary cases should remain fail-closed unless a separately specified boundary-safe positive/negative classifier has adequate real evidence.

Any boundary classifier or policy change must be frozen and synthetically tested before another EGFxSet execution. Any subsequent real-media run requires new explicit user authorization.

## AUTHORITATIVE ROUTE

The completed software-lineage no-gap conclusion remains unchanged. Official correctness still requires the frozen physical calibrated route, currently budget-paused. Do not manufacture another synthetic software-lineage gate.
