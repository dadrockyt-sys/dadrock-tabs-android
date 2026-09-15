# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — hardened EGFxSet one-shot authorized and prospectively frozen; execution pending
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
Hardening result: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_HARDENING_V1_RESULT.md`
Current run PRE: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_PRE.md`

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

The user instruction `Please try the run again` authorizes exactly one non-authoritative hardened EGFxSet execution defined in `SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_PRE.md`. It does not authorize a Basic Pitch re-inference: the immutable repaired-run Basic Pitch artifact will be reused.

## HISTORICAL EGFxSET RESULT — FROZEN FAIL

Candidate: EGFxSet v1.0 `Clean.zip#Clean/Bridge/6-0.wav`, member SHA-256 `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`, truth string 6 / fret 0 / MIDI 40.

Repaired run `34936227380` / job `104274605954` used Python 3.10.21 + Basic Pitch 0.4.0 + TFLite Runtime 2.14.0 + NumPy 1.26.4 and emitted immutable MIDI proposals `{40,68}`. `basic-pitch.json` SHA-256 is `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`; note identity SHA-256 is `2e30685479444a8120dc3490c9c41329a89e57aa16979de42053b89a4bbb0444`.

Historical score remains `PASS_RUNTIME`, `FAIL_PITCH`, `FAIL_POSITION`, overall `FAIL_NON_AUTHORIZING_SMOKE`. It may not be post-filtered or rewritten into a PASS.

## PIPELINE HARDENING V1 — COMPLETE / GREEN

Final combined regression run `34938422696`, job `104281318739`, passed all hardening tests.

Key changes:

1. Basic Pitch outputs are proposals, not automatic notes.
2. Exact note-identity qualification coverage is fail-closed.
3. Independent DSP onset-birth qualification is confidence-independent.
4. Statuses are `corroborated`, `rejected`, or `insufficient`; only corroborated proposals promote.
5. Rejected proposals remain preserved in provenance and do not become unresolved notes.
6. Playable preferred fretboard layouts are separated from physical-position certainty.

Synthetic hardening evidence showed a genuine E2 birth corroborated while a MIDI-68 fifth-harmonic-like proposal during sustained E2 was rejected, invariant to Basic Pitch confidence.

## CURRENT AUTHORIZED ONE-SHOT — PENDING

Prospective authority: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_PRE.md`, commit `8b741a8b25b61966c832860f4d91f42a018f898e`.

Frozen input reuse:
- prior artifact `10383413992` from run `34936227380`;
- exact `basic-pitch.json` SHA-256 `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`;
- exact EGFxSet WAV identity above.

Frozen path:
`exact inputs -> independent DSP qualifier -> qualified evidence builder -> adapter/evaluator -> deterministic promotion/position score`.

No Basic Pitch inference is permitted in this run. No threshold/status tuning, retries, candidate switching, hand deletion, alternate media, or reference-tab scoring.

Frozen PASS requires:
- exact input identities;
- MIDI 40 `corroborated` and MIDI 68 `rejected`, zero insufficient;
- raw proposals `[40,68]` preserved;
- promoted events exactly `[40]`;
- rejected MIDI 68 preserved;
- zero unresolved onsets;
- promoted MIDI 40 uniquely maps to string 6 / fret 0 under standard tuning;
- all scripts complete successfully.

Whatever the outcome, it remains non-authoritative and cannot change global authorization/customer-delivery fields.

## AUTHORITATIVE ROUTE

The completed software-lineage no-gap conclusion remains unchanged. Official correctness still requires the frozen physical calibrated route, currently budget-paused. Do not manufacture another synthetic software-lineage gate.
