# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-11 15:40 America/Toronto
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

Policy C-S is an ephemeral reproducibility mechanism: one exact Codespaces boot/source/toolchain fingerprint may be deliberately enrolled and then qualified by three exact canaries. Stop/restart/rebuild/source/fingerprint drift invalidates the epoch. A fresh epoch never inherits prior model-validation or delivery state.

### Completed V2 execution epoch — historical only

The frozen V2 authorized-song research run used one new Policy C-S epoch:
- epoch: `87926671-e6e9-4cda-87ea-8f248a6dae93`
- frozen source commit: `a76ab8cebb47a2dd1cf78243f00e436470e32df3`
- branch: `songsterr-fresh-pipeline-v1`
- probe: `SESSION_PROBE_PREREQUISITES_VALID`
- enrollment: `CODESPACES_SESSION_AUTHORITY_ENROLLED`
- pre-qualification verification: `CODESPACES_SESSION_AUTHORITY_VERIFIED`
- exactly three qualification canaries completed and aggregated
- qualification: `CODESPACES_SESSION_AUTHORITY_SURFACE_QUALIFIED`
- `surfaceQualifiedForCurrentBootSession=true`
- final verification after qualification remained `CODESPACES_SESSION_AUTHORITY_VERIFIED`
- policy state remained `modelValidationComplete=false`, customer eligible events `0`, `mayAdvanceDelivery=false`, duration authority unchanged.

The authorized-song V2 run completed in that same still-running epoch before repository source moved.

Afterward, repository documentation commits changed the source binding. Epoch `87926671-…` is now historical evidence only and MUST NOT be reused for another model execution.

## INDEPENDENT CORROBORATION V1 — CLOSED AS ADMISSION AUTHORITY

V1 is frozen as research diagnostic only and was rejected as customer-admission authority.

Historical authorized-song research result: 471 corroborated / 667 not corroborated / 2 insufficient across 1,140 events.

The historical MIDI-55 (~46.2024095 s) and MIDI-64 (~79.6261406 s) events are retrospective stress diagnostics only and may not tune V2 or any successor.

Stable V1 records remain:
- `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V1.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V1.json`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_AUTHORIZED_SONG_RESULT.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_POLICY_REVIEW.md`

## INDEPENDENT CORROBORATION V2 — CLOSED AS ADMISSION AUTHORITY

V2 is frozen as research diagnostic only and has now completed its preregistered lifecycle: preregistration → implementation → controlled CI → new Policy C-S qualification → one frozen authorized-song research run → separate explicit policy review.

### Frozen V2 implementation

Preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md`
- commit `64b4e7fca64b09dc124f991a170caafcb5988d0b`

Evaluator:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v2.py`
- implementation commit `a7fcf0cf0ab67673049dcc9468700280aff689a2`
- contract `songsterr-fresh-independent-pitch-corroboration-research-v2`

Frozen method record:
- `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2.md`
- latest method-record commit `886535217cabecc7a76476d1b8ea8c780834deda`

Controlled fixtures:
- `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V2.json`
- 15 deterministic PCM16 fixtures: 6 expected corroborated / 7 expected not corroborated / 2 expected insufficient
- canonical pinned-environment fixture identity commit `b1e478bfc1cb185193f3226e35e1c11841b659a2`
- environment: Python `3.10`, NumPy `1.26.4`, SoundFile `0.13.1`

Green focused CI:
- run `34622465693`, job `103339500987`: **SUCCESS**
- run `34622780588`, job `103340534639`: **SUCCESS**

Frozen V2 logic:
- `44100 Hz`; fixed `16384`-sample window; MIDI `40..88`
- competitors `{-12,-7,-2,-1,+1,+2,+7,+12}`
- RMS `<1e-4` => insufficient
- strict `>` unique-best; no substantive margin threshold
- Channel A: coherent semitone-cell fundamental-bin selection + four-harmonic normalized-magnitude log-mean
- Channel B: YIN/CMND semitone-cell minimum + `CMND(tau/2)-CMND(tau)`
- both channels must choose selected MIDI as strict unique best
- no voting/fallback/confidence averaging/learned calibration/reference scorer/Basic Pitch activation/authorized-song tuning/event deletion

No public validation corpus was authorized by V2.

### Authorized-song V2 result

Result record:
- `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_AUTHORIZED_SONG_RESULT.md`
- result-record commit `0a5181d37fdf682c1203d21c80e18909e326093a`

Execution:
- source commit `a76ab8cebb47a2dd1cf78243f00e436470e32df3`
- Policy C-S epoch `87926671-e6e9-4cda-87ea-8f248a6dae93`
- exact canary-3 bound isolated-guitar stem + duration-free evidence
- canonical evidence SHA-256 `03068378fda6e553af2e74cf8ee3e405ce0df860b6e4fd20c81b36b089f7ca2`
- all fail-closed pre-run assertions passed
- V2 executed exactly once on the authorized song
- post-run C-S verification remained green

Result across exactly 1,140 preserved events:
- independently corroborated candidate: **187**
- not independently corroborated: **951**
- insufficient evidence: **2**

Result policy boundary remained:
- `status=INDEPENDENT_CORROBORATION_V2_RESEARCH_ONLY`
- `admissionDecisionMade=false`
- `modelValidationComplete=false`
- customer eligible events `0`
- `mayAdvanceDelivery=false`
- `durationAuthorityChanged=false`

The 187/951/2 aggregate is a research observation only and must not become a threshold, prior, tuning target, or post-hoc promotion rule.

### V2 policy review decision

Policy review:
- `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_POLICY_REVIEW.md`
- policy-review commit `4189e3e2a1ae313e41409a631023e82e205347e8`
- decision: **REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**

Reason:
- synthetic controlled fixtures establish contract behavior, not real-world correctness;
- Policy C-S establishes reproducibility, not semantic truth;
- the protected authorized song cannot be used post hoc to calibrate V2;
- V2 preregistered no independent annotated validation corpus, sampling protocol, event-matching protocol, metric, or acceptance threshold;
- therefore there is no independently justified estimate that a V2-positive event is correct enough for customer admission.

This is an evidence-adequacy failure for promotion, not an implementation failure or Policy C-S failure.

The previously known MIDI-55 and MIDI-64 cases may be inspected retrospectively if useful, but their outcome cannot change this decision or tune V2 under the existing preregistration.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Active blockers:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Customer-eligible events: **0**.
`mayAdvanceDelivery:false`.
Duration research remains paused.

No reference scorer/tab/archive logic. No GOAT. No threshold sweep. No promotion from exact hashes, CPU association, historical frequency, candidate confidence, event count, downstream agreement, controlled-suite pass, C-S reproducibility alone, or aggregate corroboration count.

## ACTIVE NEXT ENGINEERING STEPS

1. Treat V1 and V2 independent corroborators as closed research diagnostics, not admission authority.
2. Do not patch/tune V2 from the 187/951/2 result or from the historical MIDI-55/MIDI-64 cases.
3. Keep `MODEL_EVIDENCE_VALIDATION_PENDING` active; upstream model evidence remains unvalidated for customer admission.
4. A successor admission method, if explicitly authorized, must start as a new preregistration/version and add genuinely independent validation evidence before any protected-song evaluation.
5. Any proposed external validation corpus must preregister exact dataset/version/right-to-use basis, subset, annotation/event-matching rules, sampling protocol, metrics, ambiguity/polyphony treatment, development/evaluation separation, and acceptance policy before results are viewed.
6. Do not resume duration research until the upstream model-evidence validation blocker is explicitly resolved.
7. Do not resume archived V143/Gomyway, reference scoring, GOAT, threshold sweeps, training/fine-tuning, or public-corpus work without explicit authorization.

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
- V2 authorized-song result: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_AUTHORIZED_SONG_RESULT.md`
- V2 policy review: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_POLICY_REVIEW.md`
