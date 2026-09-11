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

## CURRENT AUTHORITY

Fixed model path remains:

frozen full-mixture structure → Demucs guitar isolation → Basic Pitch pitch/onset inference → duration-free model evidence → independent model-evidence validation → dedicated release authority

Pinned model behavior remains Demucs `htdemucs_6s`, Basic Pitch `0.4.0`. Basic Pitch is not ground truth.

Persistent Policy C remains `UNENROLLED`.

Authority remains fail-closed:
- `modelValidationComplete:false`
- customer-eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused.

## V1 / V2 / V3 — CLOSED

V1 and V2 are frozen research diagnostics rejected as admission authority.

Historical V2 protected-song result: 1,140 preserved events; 187 corroborated / 951 not / 2 insufficient. No protected-song historical result may tune V4.

V3 is closed after frozen GuitarSet v1.1.0 validation failed its preregistered gates:
- 357/357 tracks
- 62,438 decoded events
- 11,252 V3-positive
- 10,019 correct positives
- precision `0.8904194809811589`
- one-sided 95% Wilson lower bound `0.8854816094599652`
- required lower bound `0.9900` → FAIL
- every player stratum and both `comp`/`solo` gates failed.

V3 is **CLOSED / REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**. GuitarSet is historical only and MUST NOT be reused as V4 pass/fail validation.

## V4 — FROZEN METHOD, EXTERNAL VALIDATION REOPENED

User explicitly authorized V4 and later explicitly reopened V4 holdout/external validation.

Operative V4 preregistration:
- `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`
- initial commit `a5cec402cf3bcd6c28ac3339d4d00de4d8cdf8b2`
- pre-implementation synthetic amendment `30b2769772d0a2a2edeaa8e92bff66ce3518fede`.

Frozen V4 implementation:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v4.py`
- commit `6e9e11e60d0d6958c30edf6bb5d686d545936a19`
- contract `songsterr-fresh-temporal-consensus-pitch-corroboration-research-v4`.

Frozen method:
- mono isolated guitar, 44100 Hz;
- `sourceStart` + integer `selectedMidi` only;
- full MIDI `40..88` spectral competition;
- three 8192-sample windows at relative offsets `1024`, `7168`, `13312`;
- spectral strict global winner + YIN semitone-cell winner required in all three windows;
- no margins, voting, fallback, confidence, duration, next onset, activation, decision surface, reference, performer/style identity, or event deletion.

Controlled V4 CI green:
- run `34653819306`, job `103441756944`
- documentation-complete freeze run `34653917007`, job `103442054828`.

No protected-song V4 execution has occurred.

## IDMT V4 — STAGE A INVENTORY COMPLETE

Dataset:
- IDMT-SMT-Guitar Dataset
- Zenodo v1.0.0
- DOI `10.5281/zenodo.7544110`
- archive `IDMT-SMT-GUITAR_V2.zip`
- MD5 `06796e08731bccffaed6ae59361486e4`
- SHA-256 `02816258252538603c051054219cb4bba1c0ae8c9d0a3ca5418dfc951eae997a`.

Stage A inventory preregistration:
- `SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_INVENTORY_PREREGISTRATION.md`
- commit `7ce70dd6fb9e61ec15e7fc6fb71b0e1519d67581`.

Inventory tool:
- `scripts/songsterr-fresh/inventory_idmt_v4_external_validation.py`
- commit `b955249d02d6dc3554ec6c69bca0883ef673951e`
- contract `songsterr-fresh-idmt-v4-inventory-v1`.

Inventory CI:
- run `34654695068`, job `103444417084`: **SUCCESS**.

Real Stage A inventory completed once in Codespaces outside the repository.

Bound inventory report SHA-256:
- `fd9086891a9a699619810f4bccd6f0f2533c194afc6cc1b09cf80484626d704f`.

Immutable Stage A result:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_STAGE_A_RESULT.md`
- commit `b5516dd0b2d84014f4e28d45bb04bce1ba0617ca`.

Observed Stage A inventory facts:
- ZIP members: `4292`
- `.wav`: `1173`
- `.xml`: `667`
- exact one-to-one WAV/XML leaf-stem pairs: `569`
- pair counts: `dataset1=312`, `dataset2=252`, `dataset3=5`
- unpaired WAV: `512`
- unpaired XML: `9`
- ambiguous stem groups: `45`
- WAV formats: mono 16-bit `911`, mono 24-bit `261`, stereo 16-bit `1`; all observed sample rate `44100 Hz`
- note-event XML path exposes `onsetSec`, `offsetSec`, `pitch`, string/fret and expression metadata.

Stage A policy boundary remained clean:
- no Basic Pitch
- no V4 classifier
- no Demucs
- no estimate/reference matching
- no correctness metric
- no protected song
- no duration change
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`.

## IDMT V4 — STAGE B MANIFEST PREPARATION FROZEN / GREEN

Stage B manifest-preparation preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_MANIFEST_PREREGISTRATION.md`
- commit `c1fc43acea14b4d1a5656c1a41ba4ba2b7ab5c1d`.

Manifest generator:
- `scripts/songsterr-fresh/prepare_idmt_v4_stage_b_manifest.py`
- implementation commit `aae1c2a382a98589c679706e8267543a483b2100`
- contract `songsterr-fresh-idmt-v4-stage-b-manifest-v1`.

Frozen mechanical inclusion rule:
- Stage A exact one-to-one pair only;
- dataset directory exactly `dataset1`, `dataset2` or `dataset3`;
- archive/member identities must match Stage A;
- WAV must be mono, 44100 Hz, `NONE` compression, 16- or 24-bit;
- XML root `instrumentRecording`;
- at least one transcription `event`;
- every event must contain finite `onsetSec`, `offsetSec`, `pitch`;
- onset >= 0; offset >= onset;
- no model/performance/style/confidence/correctness-based exclusion.

Stage B manifest CI workflow:
- `.github/workflows/songsterr-fresh-idmt-v4-stage-b-manifest-ci.yml`
- initial run `34656460903`, job `103449848908`: synthetic behavior/identities green; boundary guard false-positive on required `demucsInvoked` policy key only.
- guard fixed with AST import inspection at commit `3a9b47fc67f9d0b9a7643a46d6cd460b974360d9`; no manifest logic changed.
- green run `34656525179`, job `103450044793`: **SUCCESS**.

No real IDMT correctness result exists yet. The Stage B manifest preparation is still non-scoring.

## NEXT REQUIRED STEP — GENERATE REAL STAGE B MANIFEST

Use the existing Stage A archive/report in Codespaces. Update the repository to the current canonical branch head, verify a clean worktree, then run `prepare_idmt_v4_stage_b_manifest.py` once with output outside the repository.

The real Stage B manifest output must freeze:
- exact included pair count and dataset counts;
- exact exclusion count/reasons;
- exact included-manifest SHA-256;
- output SHA-256;
- total annotation event count;
- annotation `pitch` numeric range and integer/non-integer counts;
- onset/offset ranges;
- policy boundary false/zero.

After that output is reviewed, commit the final **Stage B scoring preregistration** before any Basic Pitch/V4 run. That preregistration must freeze:
- exact manifest hash/population;
- annotation semantics/units;
- Basic Pitch settings/runtime;
- V4/source identities;
- one-to-one matching tolerances/tie rules;
- minimum positive count;
- uncertainty method;
- overall/stratum gates;
- execution provenance/fail-closed rules;
- protected-song embargo until separate policy review.

Only then may one official IDMT correctness evaluation run.

## STILL FORBIDDEN

Until the later gates explicitly authorize them:
- protected-song V4 execution;
- duration research;
- GuitarSet rerun/tuning;
- archived V143/Gomyway, GOAT, reference scoring;
- threshold sweeps;
- training/fine-tuning;
- customer promotion from synthetic success, hashes, reproducibility, or unreviewed external results.

## STABLE REFERENCES

- V4 prereg: `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`
- V4 method: `SONGSTERR_FRESH_TEMPORAL_CONSENSUS_V4.md`
- IDMT metadata plan: `SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_METADATA_PLAN.md`
- IDMT inventory prereg: `SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_INVENTORY_PREREGISTRATION.md`
- IDMT Stage A result: `SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_STAGE_A_RESULT.md`
- IDMT Stage B manifest prereg: `SONGSTERR_FRESH_IDMT_V4_STAGE_B_MANIFEST_PREREGISTRATION.md`
- V3 records remain frozen historical references
- Policy C-S runbook remains historical for V2 only
- GOAT remains closed/reference only.
