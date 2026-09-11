# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-11 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs/pro scorers, GOAT research, training/fine-tuning, broad optimizer sweeps, or duration work unless explicitly reopened.
- The protected `gomyway` fixture authorizes only that exact audio fixture, not archived implementation logic.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP work remains under `scripts/songsterr-fresh/`.
- Frozen full-mixture structure precedes note inference and cannot be rewritten downstream.
- Never silently alter/drop MIDI or event identity.
- Preserve `/ai-tab` UX flow.
- Duration research remains paused until model-evidence admission is explicitly resolved.

## FIXED MODEL / AUTHORITY BOUNDARY

Fixed model path remains:

frozen full-mixture structure → Demucs guitar isolation → Basic Pitch pitch/onset inference → duration-free model evidence → independent model-evidence validation → dedicated release authority

Pinned model behavior remains Demucs `htdemucs_6s`, Basic Pitch `0.4.0`. Basic Pitch is not ground truth.

Persistent Policy C remains `UNENROLLED`.

Historical Policy C-S V2 epoch `87926671-e6e9-4cda-87ea-8f248a6dae93` is closed/historical only and MUST NOT be reused.

Current authority remains fail-closed:
- `modelValidationComplete:false`
- customer-eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused.

## V1 / V2 / V3 — CLOSED

V1 and V2 are frozen research diagnostics rejected as admission authority.

V2 protected-song result remains historical only: 1,140 preserved events; 187 corroborated / 951 not / 2 insufficient. No historical protected-song result may tune V4.

V3 is closed after frozen GuitarSet v1.1.0 external validation failed its preregistered gates:
- 357/357 tracks
- 62,438 decoded events
- 11,252 V3-positive
- 10,019 correct positives
- precision `0.8904194809811589`
- one-sided 95% Wilson lower bound `0.8854816094599652`
- required lower bound `0.9900` → FAIL
- every player stratum and both `comp`/`solo` precision gates failed.

V3 immutable result SHA-256 `e6edd37e72f24bef069d16b4accb48423b9472fe26eb90adee15e401e5b4196d`.
V3 is **CLOSED / REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**.
GuitarSet is historical only and MUST NOT be reused as V4 pass/fail validation.

## V4 — FROZEN METHOD, EXTERNAL VALIDATION REOPENED

User explicitly authorized the V4 successor and later explicitly reopened V4 holdout/external validation.

Operative V4 preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`
- initial commit `a5cec402cf3bcd6c28ac3339d4d00de4d8cdf8b2`
- pre-implementation synthetic amendment `30b2769772d0a2a2edeaa8e92bff66ce3518fede`.

Frozen V4 implementation:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v4.py`
- commit `6e9e11e60d0d6958c30edf6bb5d686d545936a19`
- contract `songsterr-fresh-temporal-consensus-pitch-corroboration-research-v4`.

Frozen method record:
- `docs/checkpoints/SONGSTERR_FRESH_TEMPORAL_CONSENSUS_V4.md`
- commit `1f4e42a53d74d1ef6bec85a00546d7196f021135`.

Frozen V4 rule:
- mono isolated guitar, exactly 44100 Hz;
- existing `sourceStart` + integer `selectedMidi` only;
- full playable MIDI `40..88` spectral competition;
- three exact 8192-sample post-onset windows at relative offsets `1024`, `7168`, `13312`;
- spectral view: Hanning 8192, rFFT 32768, coherent harmonics 1..6, strict unique global winner;
- YIN view: `librosa==0.11.0`, frame/hop 8192, center false, fmin MIDI 39.5, fmax MIDI 88.5, trough threshold 0.1, winner by equal-tempered semitone cell;
- selected MIDI must win spectral + YIN in all three windows;
- no margin threshold, voting, fallback, confidence, duration, next onset, activation, decision surface, reference, performer/style identity, or event deletion;
- invalid/nonfinite/truncated/zero-energy/YIN-invalid required view => insufficient;
- otherwise any disagreement => not independently corroborated.

Controlled V4 CI is green:
- run `34653819306`, job `103441756944`
- final method-freeze run `34653917007`, job `103442054828`.

No protected-song V4 execution has occurred.

## IDMT V4 EXTERNAL VALIDATION — STAGE A INVENTORY REOPENED

Metadata plan:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_METADATA_PLAN.md`
- commit `625a29d04e26fd312c0294fe91bd446a04fdde85`.

User explicitly reopened V4 holdout/external validation.

Stage A inventory preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_INVENTORY_PREREGISTRATION.md`
- commit `7ce70dd6fb9e61ec15e7fc6fb71b0e1519d67581`
- status: **inventory only; correctness scoring still blocked**.

Authorized Stage A dataset identity:
- IDMT-SMT-Guitar Dataset
- Zenodo v1.0.0
- DOI `10.5281/zenodo.7544110`
- archive `IDMT-SMT-GUITAR_V2.zip`
- expected MD5 `06796e08731bccffaed6ae59361486e4`.

Inventory tool:
- `scripts/songsterr-fresh/inventory_idmt_v4_external_validation.py`
- implementation commit `b955249d02d6dc3554ec6c69bca0883ef673951e`
- contract `songsterr-fresh-idmt-v4-inventory-v1`
- stdlib only; no Basic Pitch/V4/Demucs/NumPy/librosa/scoring imports.

Inventory CI:
- `.github/workflows/songsterr-fresh-idmt-v4-inventory-ci.yml`
- commit `9346d2c651e5a7ae0bbe8f53f66bcccdd7fbc3e7`
- run `34654695068`, job `103444417084` currently validating a synthetic ZIP only.

Stage A may only:
- verify exact archive MD5 and record SHA-256;
- list/hash every ZIP member;
- inventory directory/subset structure;
- read WAV container headers only;
- record XML tag/attribute structural signatures;
- establish exact WAV/XML pairings and integrity issues;
- write inventory results outside the repo.

Stage A MUST NOT:
- invoke Basic Pitch, V4 or Demucs;
- compute correctness, matching, precision/recall/F-score/Wilson metrics;
- use audio samples for signal scoring;
- alter V4;
- run GuitarSet or the protected song;
- resume duration or change product authority.

## STAGE B — REQUIRED BEFORE ANY CORRECTNESS RESULT

After Stage A inventory is complete, commit a separate versioned V4 IDMT execution preregistration before model inference/correctness scoring. It must freeze:
- exact included subsets/files and any exclusions/reasons;
- exact XML pitch/onset semantics and units;
- exact Basic Pitch settings/runtime;
- exact V4 implementation identity;
- exact one-to-one estimate/reference matching and tolerances;
- minimum positive count;
- uncertainty method;
- overall/stratum pass gates;
- execution provenance/fail-closed rules;
- protected-song embargo until separate policy review.

No GuitarSet result may choose these gates or tune V4.

## ACTIVE BLOCKERS / NEXT STEPS

Active blockers:
- V4 has no real-world correctness result yet;
- Stage A IDMT inventory is not yet complete;
- Stage B scoring contract is not yet frozen;
- `DURATION_EVIDENCE_INCOMPLETE`.

Next allowed work:
1. finish synthetic Stage A inventory CI;
2. if green, freeze checkpoint/source;
3. download exact IDMT archive in Codespaces outside repo and verify MD5;
4. run inventory tool once, outside repo;
5. inspect only integrity/schema output;
6. freeze Stage B external-validation preregistration;
7. only then run official Basic Pitch + V4 holdout correctness evaluation.

Still forbidden until the appropriate later gate:
- protected-song V4 execution;
- duration research;
- GuitarSet rerun/tuning;
- archived V143/Gomyway, GOAT, reference scoring, threshold sweeps, training/fine-tuning.

## STABLE REFERENCES

- V4 prereg: `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`
- V4 method: `SONGSTERR_FRESH_TEMPORAL_CONSENSUS_V4.md`
- IDMT metadata plan: `SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_METADATA_PLAN.md`
- IDMT inventory prereg: `SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_INVENTORY_PREREGISTRATION.md`
- V3 result/policy records remain frozen historical references
- Policy C-S runbook: `SONGSTERR_FRESH_CODESPACES_SESSION_AUTHORITY.md`
- GOAT closeout remains closed/reference only.
