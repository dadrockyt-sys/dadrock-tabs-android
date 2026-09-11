# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-11 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, professional/reference scoring, GOAT research, holdout scoring, training/fine-tuning, broad optimizer/ISA sweeps, or archived pipeline logic unless explicitly reopened.
- The `gomyway` filename authorizes only the exact protected audio fixture, not archived implementation logic.
- GOAT remains CLOSED / REFERENCE ONLY.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP work remains under `scripts/songsterr-fresh/`.
- Frozen full-mixture structure precedes note inference and cannot be rewritten downstream.
- Never silently alter/drop MIDI or event identity.
- Preserve `/ai-tab`: upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.
- Duration research remains paused until upstream model-evidence validation is explicitly resolved.

## PROTECTED FIXTURE / FIXED MODEL PATH

Protected authorized-song fixture:
- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- duration ~`210.674648526 s`
- authority-baseline decoded separation WAV SHA-256 `e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a`
- frozen structure identity `fnv1a32:2f493225`
- canonical structure length `19653`
- 4/4; first downbeat ~`0.65016 s`; 115 measures; 113 tempo segments.

Fixed production model path remains:

frozen full-mixture structure → Demucs guitar isolation → Basic Pitch pitch/onset inference → duration-free model evidence → independent model-evidence validation → dedicated release authority

Pinned model behavior remains Demucs `htdemucs_6s`, Basic Pitch `0.4.0`. Basic Pitch is not ground truth.

Duration remains unchanged and paused:
- authoritative release V2: `estimate_selected_pitch_releases.py`, contract `songsterr-fresh-cpu-spectral-release-evidence-v2`
- candidate-only release V3: `estimate_selected_pitch_releases_v3.py`, contract `songsterr-fresh-spectral-activation-release-evidence-v3`
- no Basic Pitch end as duration, generic next-onset duration, or same-pitch-reattack default.

## POLICY B / POLICY C / POLICY C-S

Policy B remains fail-closed: reproducibility, exact hashes, CPU association, historical frequency, confidence, event count, downstream agreement, finite unanimity, or synthetic-suite success do not prove semantic correctness.

Persistent Policy C remains `UNENROLLED`.

Historical Policy C-S V2 epoch:
- epoch `87926671-e6e9-4cda-87ea-8f248a6dae93`
- source `a76ab8cebb47a2dd1cf78243f00e436470e32df3`
- probe/enroll/verify green
- exactly three same-session canaries green
- one protected-song V2 research execution completed in that same epoch
- post-run verify green
- source later changed; epoch is historical only and MUST NOT be reused.

## V1 — CLOSED / REJECTED AS ADMISSION AUTHORITY

V1 is a frozen research diagnostic only.

Historical protected-song result: 471 corroborated / 667 not / 2 insufficient across 1,140 events.

Historical MIDI-55 (~46.2024095 s) and MIDI-64 (~79.6261406 s) cases remain retrospective stress diagnostics only and may not tune successors.

## V2 — CLOSED / REJECTED AS ADMISSION AUTHORITY

Frozen V2 evaluator:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v2.py`
- contract `songsterr-fresh-independent-pitch-corroboration-research-v2`
- 44.1 kHz; 16384-sample fixed post-onset window
- MIDI 40..88
- competitors `{-12,-7,-2,-1,+1,+2,+7,+12}`
- demeaned RMS `<1e-4` insufficient
- strict unique-best in both spectral and YIN/CMND channels
- no voting/fallback/confidence fitting/reference scorer/authorized-song tuning/event deletion.

Protected-song V2 result:
- 1,140 events
- 187 corroborated / 951 not / 2 insufficient
- result record `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_AUTHORIZED_SONG_RESULT.md`
- policy review `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_POLICY_REVIEW.md`
- decision: **REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**.

## V3 — CLOSED / EXTERNAL VALIDATION FAILED

V3 was preregistered before any GuitarSet correctness result:
- prereg `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`
- prereg commit `2dfd8c5d52093c36c0924e5f0b57eb2b2284e7d0`
- frozen method record `docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3.md`
- provenance-complete method commit `1792739fa30c9304d37e94066794a38898dc98aa`
- frozen official execution source `783c3b572aff4edd9d6298e9131dffd02454a61e`.

Locked V3 external result:
- GuitarSet v1.1.0, 357 locked tracks after exactly three preregistered public-data exclusions
- 62,438 decoded events
- 11,252 V3-positive
- 10,019 correct V3-positive
- precision `0.8904194809811589`
- one-sided 95% Wilson lower bound `0.8854816094599652`
- required lower bound `0.9900` → FAIL
- every player `00..05` failed point precision `>=0.9500`
- `comp` precision `0.8441590516176833` → FAIL
- `solo` precision `0.9164237123420796` → FAIL.

Artifact hashes:
- outer official result SHA-256 `e6edd37e72f24bef069d16b4accb48423b9472fe26eb90adee15e401e5b4196d`
- core result SHA-256 `9a2d103cfbe6f9c3bd8b7903c665affa41729ec2da7f303a5b1c416a2a532e4e`.

Immutable result:
- `docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3_RESULT.md`
- commit `91b021f6b3f43cee73dc58d1aebf29492a547928`.

Policy review:
- `docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3_POLICY_REVIEW.md`
- commit `3b8159be0898a71b33069f94a4ca4d1ada0a7047`
- **CLOSED / REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**.

No V3 gate may be relaxed or tuned. GuitarSet is historical after V3 and MUST NOT be reused as a V4 pass/fail corpus. No protected-song V3 execution occurred.

## V4 — ACTIVE / FROZEN SYNTHETIC-ONLY SUCCESSOR

User explicitly authorized the V4 successor after V3 closeout.

Operative preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`
- initial prereg commit `a5cec402cf3bcd6c28ac3339d4d00de4d8cdf8b2`
- pre-implementation synthetic-only amendment `30b2769772d0a2a2edeaa8e92bff66ce3518fede`.

The amendment replaced the initially proposed plain real-cepstrum view after a generated E2 fixture exposed octave/harmonic aliasing. This occurred before implementation and before any external/protected correctness result. The operative second view is standard YIN.

Frozen implementation:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v4.py`
- commit `6e9e11e60d0d6958c30edf6bb5d686d545936a19`
- contract `songsterr-fresh-temporal-consensus-pitch-corroboration-research-v4`.

Focused CI:
- `.github/workflows/songsterr-fresh-temporal-consensus-v4-ci.yml`
- workflow commit `736872e8fdf922c3975eda833ebd9616692bbd65`.

Frozen method record:
- `docs/checkpoints/SONGSTERR_FRESH_TEMPORAL_CONSENSUS_V4.md`
- method commit `1f4e42a53d74d1ef6bec85a00546d7196f021135`.

V4 fixed method:
- isolated mono guitar audio only; exactly 44100 Hz;
- existing `sourceStart` + integer `selectedMidi` only;
- full playable MIDI `40..88` spectral competition;
- three exact 8192-sample windows at onset-relative offsets `1024`, `7168`, `13312`;
- spectral view: Hanning 8192, rFFT 32768, semitone-cell fundamental, coherent harmonics 1..6, log-mean score, strict unique global winner;
- YIN view: `librosa==0.11.0`, frame/hop 8192, center false, fmin MIDI 39.5, fmax MIDI 88.5, trough threshold 0.1, winner by equal-tempered semitone cell;
- selected MIDI must win both decisions in all three windows;
- no voting, fallback, margin threshold, confidence, duration, next onset, activation, decision surface, reference, performer/style identity, or event deletion;
- invalid/nonfinite/truncated/zero-energy/YIN-invalid required view => insufficient;
- otherwise any disagreement => not independently corroborated.

Controlled synthetic CI:
- run `34653819306`, job `103441756944`, source `736872e8fdf922c3975eda833ebd9616692bbd65`: **SUCCESS**;
- final documentation-complete freeze run `34653917007`, job `103442054828`, exact source `1f4e42a53d74d1ef6bec85a00546d7196f021135`: **SUCCESS**.

Green contract coverage includes stable low/mid/high pitches, +25-cent detune, attack noise, wrong octave, stronger adjacent/fifth/polyphonic competitors, temporal pitch change, zero audio, truncation, strict tie rejection, full MIDI competition, evidence identity preservation, duration rejection, and all policy guards false/zero.

No GuitarSet, IDMT, or protected-song V4 correctness result has been produced. Controlled CI explicitly remained synthetic-only.

Untouched candidate external corpus metadata only:
- IDMT-SMT-Guitar Dataset, Zenodo v1.0.0, DOI `10.5281/zenodo.7544110`;
- archive `IDMT-SMT-GUITAR_V2.zip`, MD5 `06796e08731bccffaed6ae59361486e4`;
- public documentation describes mono 44100-Hz guitar audio and XML note-event annotations.

**Holdout scoring remains closed.** V4 is frozen at the pre-external-validation boundary. Do not download/infer/score IDMT until the user explicitly reopens holdout/external validation and a separate versioned validation preregistration freezes exact subsets/files, manifest, XML interpretation, matching, sample-size/uncertainty gates and execution provenance before any correctness result.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Current authority state:
- `modelValidationComplete:false`
- customer-eligible events: **0**
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused
- persistent Policy C `UNENROLLED`.

Active blockers:
- model-evidence admission remains unresolved after V3 external-validation failure
- V4 has synthetic contract evidence only and no real-world validation authority
- external/holdout validation is not reopened
- `DURATION_EVIDENCE_INCOMPLETE`.

No reference scorer/tab/archive logic. No GOAT. No threshold sweep. No training/fine-tuning. No promotion from hashes, reproducibility, confidence, event counts, synthetic-suite success, C-S agreement, historical protected-song results, or failed external results.

## NEXT ALLOWED WORK

V4 implementation/method/controlled CI are frozen and green. Under the current scope, the next external correctness step is intentionally blocked.

Allowed without reopening holdout:
- documentation-only maintenance;
- inspect public IDMT documentation/metadata without downloading/scoring audio;
- design a future versioned external-validation preregistration, but do not execute it.

Requires explicit user reopening of holdout/external validation:
- download/inventory the IDMT archive;
- run Basic Pitch/V4 on IDMT;
- compute any real correctness metric or pass/fail result.

Still forbidden:
- rerun GuitarSet V3 for tuning;
- run the protected song;
- resume duration;
- reopen archived V143/Gomyway, GOAT, reference scoring, threshold sweeps, or training/fine-tuning.

## STABLE REFERENCES

- canonical current state: `SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
- V4 prereg: `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`
- V4 method: `SONGSTERR_FRESH_TEMPORAL_CONSENSUS_V4.md`
- V3 prereg/method/result/policy review remain frozen historical references
- V2 prereg/method/result/policy review remain frozen historical references
- Policy C-S runbook: `SONGSTERR_FRESH_CODESPACES_SESSION_AUTHORITY.md`
- GOAT closeout: `SONGSTERR_FRESH_GOAT_RESEARCH_CLOSED_REFERENCE_ONLY.md`.
