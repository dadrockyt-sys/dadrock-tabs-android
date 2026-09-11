# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-11 12:15 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the canonical current-state checkpoint for the active fresh workstream. Older verbose diagnostics, helper failures, run IDs, and superseded handoffs remain available in Git history and the linked checkpoint documents below.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference/professional scorer logic, holdout scoring, GOAT research, training/fine-tuning, or broad optimizer/ISA sweeps unless the user explicitly reopens that workstream.
- The `gomyway` filename authorizes the exact audio fixture only; it does not authorize the archived pipeline.
- GOAT research is CLOSED / REFERENCE ONLY. No restricted GOAT data was obtained or imported, and no attempt may be made to bypass the denied access.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP execution stays in `scripts/songsterr-fresh/`.
- Frozen full-mixture structure precedes note inference and cannot be rewritten downstream.
- Never silently change/drop MIDI/event identity. Raw sequential Basic Pitch indices are not cross-run identity.
- Preserve `/ai-tab`: audio upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.
- Duration research remains paused while upstream model-evidence validation is unresolved. Ignore unrelated duration/V3 workflow activity as authority for this workstream.

## AUTHORIZED FIXTURE / FROZEN STRUCTURE

Authorized audio fixture only:
- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration ~`210.674648526 s`
- authority-baseline decoded separation WAV SHA-256 `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- frozen structure identity `fnv1a32:2f493225`
- canonical structure length `19653`
- 4/4; first downbeat ~`0.65016 s`; 115 measures; 113 tempo segments

The filename/fixture does not authorize any archived V143/Gomyway scoring or implementation logic.

## FIXED MODEL PATH / DURATION STATE

Architecture remains:

frozen full-mixture structure → Demucs guitar isolation → Basic Pitch pitch/onset inference → duration-free model evidence boundary → independent model-evidence validation → dedicated release authority

Pinned model behavior remains unchanged. Demucs is `htdemucs_6s`; Basic Pitch is `0.4.0`; model asset authority remains `verify_demucs_model_asset.py`. Basic Pitch is not ground truth and candidate note-span amplitude/confidence remains diagnostic-only.

Duration remains unchanged and paused:
- V2 authoritative: `estimate_selected_pitch_releases.py`, contract `songsterr-fresh-cpu-spectral-release-evidence-v2`.
- V3 candidate-only: `estimate_selected_pitch_releases_v3.py`, contract `songsterr-fresh-spectral-activation-release-evidence-v3`.
- No Basic Pitch end as duration, generic next-onset duration, or same-pitch-reattack default.

## HOSTED REPRODUCIBILITY / POLICY B

Hosted measurements established real cross-run numerical/semantic variation in Demucs → Basic Pitch output. Exact hashes, CPU/vendor associations, historical frequency, event count, confidence, and downstream agreement remain diagnostics only.

No independently justified end-to-end numerical admission bound was found, the observed threshold-boundary variation may not be converted into a fitted tolerance, and finite repeated-run/unanimity consensus is not a proof of correctness. Policy B therefore has no justified customer-admission contract for threshold-boundary semantic inventory toggles.

## POLICY C / POLICY C-S

Persistent Policy C remains `UNENROLLED`; no persistent authority host/fingerprint exists and hosted runners are not authority fallback.

Policy C-S remains the ephemeral reproducibility mechanism: one exact Codespaces boot/source/toolchain fingerprint may be deliberately enrolled and then qualified by three exact canaries. Stop/restart/rebuild/source/fingerprint drift invalidates the epoch. A fresh epoch never inherits prior model-validation or delivery state.

Prior C-S epochs are historical only and MUST NOT be reused for V2.

Reproducibility does not imply model correctness.

## INDEPENDENT CORROBORATION V1 — CLOSED AS ADMISSION AUTHORITY

V1 is frozen as research diagnostic only.

Stable records:
- `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V1.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V1.json`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_AUTHORIZED_SONG_RESULT.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_POLICY_REVIEW.md`

Historical V1 authorized-song research result: 471 corroborated / 667 not corroborated / 2 insufficient across 1,140 events. V1 was rejected as customer-admission authority.

The historical MIDI-55 (~46.2024095 s) and MIDI-64 (~79.6261406 s) events are retrospective stress diagnostics only. They may not tune V2.

## INDEPENDENT CORROBORATION V2 — PREREGISTERED / IMPLEMENTED / CONTROLLED CI PENDING

Preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md`
- commit `64b4e7fca64b09dc124f991a170caafcb5988d0b`

Evaluator implementation:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v2.py`
- commit `a7fcf0cf0ab67673049dcc9468700280aff689a2`
- contract `songsterr-fresh-independent-pitch-corroboration-research-v2`

Frozen exact controlled-fixture manifest:
- `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V2.json`
- commit `81abda5ffda85484d3e01f66737573b6b9192448`
- fixture contract `songsterr-fresh-independent-pitch-corroboration-fixtures-v2`
- 15 deterministic PCM16 fixtures: 6 expected corroborated / 7 expected not corroborated / 2 expected insufficient.

Local controlled-only verification before commit:
- Python compile passed.
- All 15 generated fixture WAV identities matched the frozen manifest used for the self-test.
- All 15 classifications matched the preregistered expected classes: 6/7/2.
- Channel-B FFT autocorrelation was compared against direct dot-product positive-lag autocorrelation on deterministic numeric data; maximum absolute difference was ~`1.99e-13` in that check.
- Exact score tie fails unique-best; an arbitrarily small strict greater-than score is a winner because V2 intentionally has no fitted margin threshold.
- duration-bearing evidence fails closed with `DURATION_MUST_REMAIN_UNRESOLVED`.
- fixed analysis window extending past available audio returns `insufficient-evidence` / `FIXED_WINDOW_OUTSIDE_AUDIO` rather than borrowing duration/next-onset information.
- evaluator source contains no authorized-song event timestamp/value tuning. No authorized-song evaluation has occurred.

Frozen V2 constants/logic remain as preregistered:
- sample rate `44100 Hz`; fixed window `16384` samples; playable MIDI `40..88`;
- competitors `{-12,-7,-2,-1,+1,+2,+7,+12}`;
- RMS `<1e-4` => insufficient;
- strict `>` unique-best with no substantive score-margin threshold;
- Channel A: coherent semitone-cell fundamental-bin selection plus four-harmonic normalized-magnitude log-mean;
- Channel B: YIN/CMND semitone-cell minimum with half-period contrast `CMND(tau/2)-CMND(tau)`;
- both channels must choose selected MIDI as strict unique best;
- no voting/fallback/confidence averaging/learned calibration/reference scorer/Basic Pitch activation/authorized-song tuning/event deletion.

No public validation corpus is authorized by V2. Hosted CI may run only the deterministic controlled fixtures and contract tests.

## V2 AUTHORIZED-SONG EXECUTION BOUNDARY

Do not evaluate the authorized song with V2 until all of the following are true:
1. evaluator + exact controlled fixture manifest are frozen;
2. focused controlled/contract CI is green;
3. hard non-promotion guards are green;
4. a NEW Policy C-S epoch is enrolled on the exact frozen source commit;
5. that epoch passes three exact qualification canaries.

Only then may frozen V2 run once on the authorized song while verifying the same C-S session before and after. A separate policy review remains mandatory afterward; the run cannot automatically authorize customer output.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Active blockers:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events: **0**.
`mayAdvanceDelivery:false`.
Duration research remains paused.

No reference scorer/tab/archive logic. No GOAT. No threshold sweep. No promotion from exact hashes, CPU association, historical frequency, candidate confidence, event count, downstream agreement, or aggregate corroboration count.

## ACTIVE NEXT ENGINEERING STEPS

1. Add focused hosted CI for V2 compile/self-test/exact fixture identities/classifications and hard non-promotion guards only.
2. Add a frozen V2 method record documenting the exact implementation contract.
3. Run/inspect focused CI. Distinguish integration/helper failures from actual controlled-method failures.
4. If a preregistered fixture expectation genuinely fails, fail closed; do not tune from the authorized song. Any method change requires a new preregistration version before song evaluation.
5. Update this checkpoint with CI commit/run/job/conclusion.
6. Do not enroll/reuse a C-S epoch yet. A new epoch comes only after V2 code and controlled CI are frozen/green.

## STABLE POLICY REFERENCES

- Canonical current state: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
- GOAT closeout: `docs/checkpoints/SONGSTERR_FRESH_GOAT_RESEARCH_CLOSED_REFERENCE_ONLY.md`
- Policy B numerical-bound research: `docs/checkpoints/SONGSTERR_FRESH_POLICY_B_NUMERICAL_BOUND_RESEARCH.md`
- Persistent Policy C: `docs/checkpoints/SONGSTERR_FRESH_PINNED_COMPUTE_AUTHORITY_V1.md`
- Policy C enrollment: `docs/checkpoints/SONGSTERR_FRESH_PINNED_COMPUTE_AUTHORITY_ENROLLMENT.md`
- Policy C-S: `docs/checkpoints/SONGSTERR_FRESH_CODESPACES_SESSION_AUTHORITY.md`
- V1 policy review: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_POLICY_REVIEW.md`
- V2 preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md`
- V2 controlled fixtures: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V2.json`
