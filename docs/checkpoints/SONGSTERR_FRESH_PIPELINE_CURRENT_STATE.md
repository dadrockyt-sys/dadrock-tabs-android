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
- accepted beat-grid baseline remains unchanged

The filename/fixture does not authorize any archived V143/Gomyway scoring or implementation logic.

## FIXED MODEL PATH

Architecture remains:

frozen full-mixture structure → Demucs guitar isolation → Basic Pitch pitch/onset inference → duration-free model evidence boundary → independent model-evidence validation → dedicated release authority

Pinned model path remains unchanged:
- Demucs `htdemucs_6s`, CPU, shifts `0`, overlap `0.25`, segment `7 s`
- Basic Pitch `0.4.0`
- fixed package/thread/hash environment as already recorded in prior checkpoint history
- model asset authority remains `verify_demucs_model_asset.py`
- current Demucs model asset SHA-256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`

Basic Pitch is not ground truth. Candidate note-span amplitude/confidence remains diagnostic-only and may not define admission.

## DURATION AUTHORITY — UNCHANGED / PAUSED

V2 remains authoritative:
- `scripts/songsterr-fresh/estimate_selected_pitch_releases.py`
- contract `songsterr-fresh-cpu-spectral-release-evidence-v2`

V3 remains candidate-only:
- `scripts/songsterr-fresh/estimate_selected_pitch_releases_v3.py`
- contract `songsterr-fresh-spectral-activation-release-evidence-v3`

Hard duration rules remain unchanged:
- input must be duration-free;
- Basic Pitch decoded note-off is diagnostic only;
- generic next onset is never duration;
- same-pitch reattack is a censor/search boundary only;
- do not resume duration research until model-evidence validation is explicitly advanced by policy review.

## HOSTED MODEL-EVIDENCE REPRODUCIBILITY — MEASUREMENT ONLY

Policy B hosted measurements established real cross-run numerical/semantic variation in Demucs → Basic Pitch output.

Current conclusions remain:
- hosted exact hashes, CPU/vendor associations, historical frequency, event count, confidence, and downstream agreement are diagnostics only;
- the observed threshold-boundary MIDI toggle cannot be converted into a fitted onset tolerance;
- no independently justified end-to-end numerical admission bound was found;
- finite repeated-run/unanimity consensus is not a proof of correctness;
- therefore Policy B has no justified customer-admission contract for threshold-boundary semantic inventory toggles.

`modelValidationComplete` remains false.

## POLICY C / POLICY C-S REPRODUCIBILITY AUTHORITY

Persistent Policy C:
- architecture: `docs/checkpoints/SONGSTERR_FRESH_PINNED_COMPUTE_AUTHORITY_V1.md`
- manifest: `scripts/songsterr-fresh/pinned_compute_authority_v1.json`
- status remains `UNENROLLED`
- no persistent host/fingerprint has been enrolled
- no hosted fallback is authority-eligible

Policy C-S Codespaces session authority:
- architecture/runbook: `docs/checkpoints/SONGSTERR_FRESH_CODESPACES_SESSION_AUTHORITY.md`
- one exact Codespaces boot/source/toolchain fingerprint may be explicitly enrolled and qualified with three exact canaries
- stop/restart/rebuild/source change/fingerprint drift invalidates the epoch
- a fresh epoch never inherits prior model-validation or delivery state

A prior live C-S session successfully demonstrated same-session exact reproducibility, but that prior epoch is historical only and MUST NOT be reused for any new model-evidence method.

Reproducibility does not imply model correctness.

## INDEPENDENT CORROBORATION V1 — CLOSED AS ADMISSION AUTHORITY

V1 remains frozen as a research diagnostic only.

Key records:
- preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V1.md`
- frozen method: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1.md`
- controlled fixture manifest: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V1.json`
- authorized-song result: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_AUTHORIZED_SONG_RESULT.md`
- policy review: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_POLICY_REVIEW.md`

V1 authorized-song research result on its qualified historical C-S epoch:
- 1,140 total qualified events
- 471 `independently-corroborated-candidate`
- 667 `not-independently-corroborated`
- 2 `insufficient-evidence`

V1 was rejected as customer-admission authority. Do not patch/tune V1 from the authorized song.

The previously identified MIDI-55 (~46.2024095 s) and MIDI-64 (~79.6261406 s) song events are retrospective stress diagnostics only. They may not be used to choose V2 constants, thresholds, competitor definitions, channel logic, or fixture expectations.

## INDEPENDENT CORROBORATION V2 — PREREGISTERED / IMPLEMENTATION NOT YET COMMITTED

New preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md`
- preregistration commit `64b4e7fca64b09dc124f991a170caafcb5988d0b`

V2 is a new research contract, not a V1 patch.

Frozen V2 principles and constants before implementation:
- allowed inputs remain only the bound isolated-guitar WAV plus existing `selectedMidi` and `sourceStart`; frozen structure/stem/evidence identities are provenance only;
- exact sample rate `44100 Hz`;
- exact post-onset window `16384` samples (~`0.37151927437641723 s`);
- playable MIDI `40..88`;
- competitor offsets `{-12,-7,-2,-1,+1,+2,+7,+12}`;
- demeaned RMS `< 1e-4` => insufficient evidence;
- no substantive score-margin threshold; strict `>` determines unique best and equality fails closed;
- no duration/next-onset/reattack information may alter the fixed window.

V2 Channel A — coherent semitone-cell harmonic product:
- demean → Hann(16384) → RFFT size 32768 → normalized magnitude;
- choose the maximum-magnitude fundamental bin inside each candidate MIDI semitone cell;
- use that coherent `f_hat` for harmonics 1..4;
- sample each harmonic at nearest FFT bin ±1 neighbor;
- floor only for finite log at `1e-15`;
- score = arithmetic mean of the four natural-log magnitudes;
- selected MIDI must be strict unique best among the frozen competitors.

V2 Channel B — octave-disambiguated YIN/CMND:
- compute squared-difference function and cumulative-mean normalized difference over the required lag range;
- choose the minimum-CMND lag inside each candidate MIDI semitone cell;
- ties choose the lag nearest equal-tempered center, then smaller lag;
- linearly interpolate CMND at half that chosen lag;
- score = `CMND(tau/2) - CMND(tau)`; higher is better;
- selected MIDI must be strict unique best among the frozen competitors.

V2 classification is fail-closed unanimity:
- both channels unique-best selected => `independently-corroborated-candidate`;
- channel disagreement/non-unique selected => `not-independently-corroborated`;
- low support/invalid/truncated/non-finite required evidence => `insufficient-evidence`.

No voting, fallback channel, confidence averaging, learned calibration, reference scorer, Basic Pitch activation, authorized-song tuning, or event deletion is permitted.

## V2 CONTROLLED VALIDATION BOUNDARY

Before any authorized-song V2 run, implementation must commit deterministic exact PCM16 fixtures covering at least:
- positives: low/mid/high plucked-like tones, ±35-cent in-cell detuning cases, deterministic attack-noise robustness case;
- negatives: wrong octave both directions, deliberately dominant second harmonic, stronger neighboring semitone, stronger perfect fifth, equal close dyad, deterministic clustered/polyphonic ambiguity;
- insufficient: silence and fixed-seed very-low-level broadband noise.

Expected controlled-suite minimum: 15 fixtures (6 positive / 7 negative / 2 insufficient), plus explicit contract tests for strict ties, duration rejection, truncated-window fail-closed behavior, identity preservation, and non-promotion guards.

No public corpus is authorized by the current V2 preregistration. If public validation is later added, dataset version/license/subset/protocol/metrics/policy must be preregistered in a new version before viewing those results.

Hosted CI may exercise only controlled fixtures and contract tests. It must not evaluate the authorized song.

## V2 AUTHORIZED-SONG EXECUTION BOUNDARY

Do not evaluate the authorized song with V2 until all of the following are true:
1. V2 evaluator implementation is frozen in branch commits;
2. exact controlled-fixture manifest is committed;
3. focused controlled/contract CI is green;
4. non-promotion guards are green;
5. a NEW Policy C-S epoch is enrolled on the exact frozen source commit;
6. that new epoch passes three exact qualification canaries.

Only then may V2 run once on the authorized song while verifying the same C-S session before and after.

After that run, a separate explicit policy review remains mandatory. The result does not automatically authorize customer output.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Active blockers:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`

Current customer-eligible events: **0**.

`mayAdvanceDelivery:false`.

Duration V2 authoritative; duration V3 candidate-only; duration research paused.

No reference scorer/tab/archive logic. No GOAT. No Basic Pitch end as duration. No generic next-onset duration. No same-pitch-reattack default. No threshold sweep. No promotion from exact hashes, CPU association, historical frequency, candidate confidence, event count, downstream agreement, or aggregate corroboration count.

## ACTIVE NEXT ENGINEERING STEPS

1. Implement `scripts/songsterr-fresh/independent_pitch_corroboration_v2.py` exactly from the frozen V2 preregistration without inspecting/running the authorized song.
2. Generate the deterministic 15-fixture controlled suite and commit its exact SHA-256 manifest.
3. Add focused hosted CI for compile/self-test/fixture identity/classification and hard non-promotion guards only.
4. If any preregistered fixture expectation fails, fail closed. Do not tune from the authorized song; any method change requires a new preregistration version before authorized-song evaluation.
5. Keep this checkpoint updated after implementation and after focused CI.
6. Do not enroll/reuse a C-S epoch yet. A new epoch comes only after V2 code and controlled CI are frozen/green.

## STABLE POLICY REFERENCES

- Canonical current state: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
- GOAT closeout: `docs/checkpoints/SONGSTERR_FRESH_GOAT_RESEARCH_CLOSED_REFERENCE_ONLY.md`
- Policy B numerical-bound research: `docs/checkpoints/SONGSTERR_FRESH_POLICY_B_NUMERICAL_BOUND_RESEARCH.md`
- Persistent Policy C: `docs/checkpoints/SONGSTERR_FRESH_PINNED_COMPUTE_AUTHORITY_V1.md`
- Policy C enrollment: `docs/checkpoints/SONGSTERR_FRESH_PINNED_COMPUTE_AUTHORITY_ENROLLMENT.md`
- Policy C-S: `docs/checkpoints/SONGSTERR_FRESH_CODESPACES_SESSION_AUTHORITY.md`
- V1 preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V1.md`
- V1 method: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1.md`
- V1 authorized-song result: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_AUTHORIZED_SONG_RESULT.md`
- V1 policy review: `docs/checkpoints/SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_POLICY_REVIEW.md`
- V2 preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md`
