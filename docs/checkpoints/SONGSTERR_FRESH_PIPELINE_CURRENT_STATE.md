# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-11 12:32 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the canonical current-state checkpoint for the active fresh workstream. Older verbose diagnostics, helper failures, run IDs, and superseded handoffs remain available in Git history and the linked checkpoint documents below.

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, reference/professional scorer logic, holdout scoring, GOAT research, training/fine-tuning, or broad optimizer/ISA sweeps unless the user explicitly reopens that workstream.
- The `gomyway` filename authorizes the exact audio fixture only; it does not authorize the archived pipeline.
- GOAT research is CLOSED / REFERENCE ONLY.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP execution stays in `scripts/songsterr-fresh/`.
- Frozen full-mixture structure precedes note inference and cannot be rewritten downstream.
- Never silently change/drop MIDI/event identity.
- Preserve `/ai-tab`: audio upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.
- Duration research remains paused while upstream model-evidence validation is unresolved.

## AUTHORIZED FIXTURE / FROZEN STRUCTURE

Authorized audio fixture only:
- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration ~`210.674648526 s`
- authority-baseline decoded separation WAV SHA-256 `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- frozen structure identity `fnv1a32:2f493225`
- canonical structure length `19653`
- 4/4; first downbeat ~`0.65016 s`; 115 measures; 113 tempo segments

The filename/fixture does not authorize archived V143/Gomyway scoring or implementation logic.

## FIXED MODEL PATH / DURATION STATE

Architecture remains:

frozen full-mixture structure → Demucs guitar isolation → Basic Pitch pitch/onset inference → duration-free model evidence boundary → independent model-evidence validation → dedicated release authority

Pinned model behavior remains unchanged. Demucs is `htdemucs_6s`; Basic Pitch is `0.4.0`; Basic Pitch is not ground truth.

Duration remains unchanged and paused:
- V2 authoritative: `estimate_selected_pitch_releases.py`, contract `songsterr-fresh-cpu-spectral-release-evidence-v2`.
- V3 candidate-only: `estimate_selected_pitch_releases_v3.py`, contract `songsterr-fresh-spectral-activation-release-evidence-v3`.
- No Basic Pitch end as duration, generic next-onset duration, or same-pitch-reattack default.

## HOSTED REPRODUCIBILITY / POLICY B

Hosted measurements established real cross-run numerical/semantic variation in Demucs → Basic Pitch output. Exact hashes, CPU/vendor associations, historical frequency, event count, confidence, downstream agreement, or finite unanimity remain diagnostics only and do not establish correctness.

No independently justified end-to-end numerical admission bound was found. Policy B therefore has no justified customer-admission contract for threshold-boundary semantic inventory toggles.

## POLICY C / POLICY C-S

Persistent Policy C remains `UNENROLLED`; no persistent authority host/fingerprint exists and hosted runners are not authority fallback.

Policy C-S remains the ephemeral reproducibility mechanism: one exact Codespaces boot/source/toolchain fingerprint may be deliberately enrolled and then qualified by three exact canaries. Stop/restart/rebuild/source/fingerprint drift invalidates the epoch. A fresh epoch never inherits prior model-validation or delivery state.

Prior C-S epochs are historical only and MUST NOT be reused for V2.

Reproducibility does not imply model correctness.

## INDEPENDENT CORROBORATION V1 — CLOSED AS ADMISSION AUTHORITY

V1 is frozen as research diagnostic only and was rejected as customer-admission authority.

Historical authorized-song research result: 471 corroborated / 667 not corroborated / 2 insufficient across 1,140 events.

The historical MIDI-55 (~46.2024095 s) and MIDI-64 (~79.6261406 s) events are retrospective stress diagnostics only and may not tune V2.

Stable V1 records remain:
- `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V1.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V1.json`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_AUTHORIZED_SONG_RESULT.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_POLICY_REVIEW.md`

## INDEPENDENT CORROBORATION V2 — PREREGISTERED / IMPLEMENTED / CONTROLLED CI GREEN

Preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md`
- commit `64b4e7fca64b09dc124f991a170caafcb5988d0b`

Evaluator:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v2.py`
- implementation commit `a7fcf0cf0ab67673049dcc9468700280aff689a2`
- contract `songsterr-fresh-independent-pitch-corroboration-research-v2`

Frozen method record:
- `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2.md`
- created at commit `6dda1a45b536ad211fe6cd094d38401a082e3831`
- integration note update at commit `189cded24f16ea84ede3be74fe8d668a588725b7`

Controlled-fixture manifest:
- `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V2.json`
- fixture contract `songsterr-fresh-independent-pitch-corroboration-fixtures-v2`
- 15 deterministic PCM16 fixtures: 6 expected corroborated / 7 expected not corroborated / 2 expected insufficient.
- initial local-runtime hash freeze commit `81abda5ffda85484d3e01f66737573b6b9192448` was superseded before any authorized-song run because Python/NumPy runtime differences changed exact generated PCM hashes.
- canonical pinned-environment fixture identity commit: `b1e478bfc1cb185193f3226e35e1c11841b659a2`.
- canonical controlled-fixture generation environment: Python `3.10`, NumPy `1.26.4`, SoundFile `0.13.1` on the focused hosted workflow.
- scoring method, signal definitions, expected class labels, and preregistered constants were not changed during identity correction.

Focused workflow:
- `.github/workflows/songsterr-fresh-independent-corroboration-v2-ci.yml`
- initial workflow commit `610245dd7bba66a358f90490a7b5746f9f87c8be`
- pinned-identity diagnostic update `90f0a4dd3717091f8f6aeee959212240bd35e56d`.

CI history:
- run `34622138929`, job `103338450038`: failed at exact fixture identity because the initial manifest had been produced in a newer local NumPy/Python runtime; compile had passed. This was an integration identity-freeze failure, not a scoring/classification failure.
- run `34622342886`, job `103339112223`: emitted all exact pinned-environment fixture identities and intentionally still failed against the not-yet-corrected manifest.
- run `34622465693`, job `103339500987`, source commit `b1e478bfc1cb185193f3226e35e1c11841b659a2`: **SUCCESS**.

Green run `34622465693` proved:
- checkout/setup/dependency install/compile all passed;
- all 15 regenerated PCM identities exactly matched the corrected frozen manifest;
- all 15 observed classifications matched expected labels: **6 corroborated / 7 not corroborated / 2 insufficient**;
- strict score equality fails unique-best and strict `>` wins, with no fitted score-margin threshold;
- FFT linear autocorrelation agrees with direct positive-lag dot products within the fixed CI tolerance;
- duration-bearing evidence is rejected before research scoring;
- fixed-window overrun returns `insufficient-evidence` / `FIXED_WINDOW_OUTSIDE_AUDIO`;
- event onset/MIDI identity is preserved;
- every non-promotion guard remained false/zero;
- `AUTHORIZED_SONG_NOT_EVALUATED_BY_V2_CI` passed.

Frozen V2 constants/logic remain exactly as preregistered:
- `44100 Hz`; fixed `16384`-sample window; MIDI `40..88`;
- competitors `{-12,-7,-2,-1,+1,+2,+7,+12}`;
- RMS `<1e-4` => insufficient;
- strict `>` unique-best, no substantive score-margin threshold;
- Channel A: coherent semitone-cell fundamental-bin selection + four-harmonic normalized-magnitude log-mean;
- Channel B: YIN/CMND semitone-cell minimum + `CMND(tau/2)-CMND(tau)`;
- both channels must choose the selected MIDI as strict unique best;
- no voting/fallback/confidence averaging/learned calibration/reference scorer/Basic Pitch activation/authorized-song tuning/event deletion.

No public validation corpus is authorized by V2.

## V2 AUTHORIZED-SONG EXECUTION BOUNDARY

The first three prerequisites are now satisfied:
1. evaluator + exact controlled fixture manifest are frozen — **YES**;
2. focused controlled/contract CI is green — **YES**;
3. hard non-promotion guards are green — **YES**.

Still required before any V2 authorized-song evaluation:
4. enroll a **NEW** Policy C-S epoch on the exact frozen V2 source state;
5. pass three exact qualification canaries in that same epoch.

Only after 4–5 may frozen V2 run once on the authorized song while verifying the same C-S session before and after.

A separate explicit policy review remains mandatory afterward; a successful research run does not automatically authorize customer output.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Active blockers:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events: **0**.
`mayAdvanceDelivery:false`.
Duration research remains paused.

No reference scorer/tab/archive logic. No GOAT. No threshold sweep. No promotion from exact hashes, CPU association, historical frequency, candidate confidence, event count, downstream agreement, controlled-suite pass, or aggregate corroboration count.

## ACTIVE NEXT ENGINEERING STEPS

1. Read the Policy C-S enrollment/runbook again and identify the exact frozen V2 source state that must be enrolled after this checkpoint update.
2. Create/enroll a **new** C-S epoch only if the available Codespaces tooling can preserve and verify the exact required boot/source/toolchain fingerprint; never reuse a historical epoch.
3. Run exactly three qualification canaries in the same new epoch and require exact equality under the existing C-S contract.
4. Update this checkpoint after enrollment and after each qualification outcome.
5. Do **not** evaluate the authorized song until the new epoch is fully qualified.
6. Do not resume duration research, archived V143/Gomyway, reference scoring, or GOAT work.

## STABLE POLICY REFERENCES

- Canonical current state: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
- GOAT closeout: `docs/checkpoints/SONGSTERR_FRESH_GOAT_RESEARCH_CLOSED_REFERENCE_ONLY.md`
- Policy B numerical-bound research: `docs/checkpoints/SONGSTERR_FRESH_POLICY_B_NUMERICAL_BOUND_RESEARCH.md`
- Persistent Policy C: `docs/checkpoints/SONGSTERR_FRESH_PINNED_COMPUTE_AUTHORITY_V1.md`
- Policy C enrollment: `docs/checkpoints/SONGSTERR_FRESH_PINNED_COMPUTE_AUTHORITY_ENROLLMENT.md`
- Policy C-S: `docs/checkpoints/SONGSTERR_FRESH_CODESPACES_SESSION_AUTHORITY.md`
- V1 policy review: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_POLICY_REVIEW.md`
- V2 preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md`
- V2 method: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2.md`
- V2 controlled fixtures: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V2.json`
