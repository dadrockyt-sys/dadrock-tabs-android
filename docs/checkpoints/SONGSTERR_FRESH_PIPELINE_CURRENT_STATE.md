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

### Locked V3 corpus / gates

Dataset: GuitarSet v1.1.0, DOI `10.5281/zenodo.3371780`.

Verified archives:
- `annotation.zip` MD5 `b39b78e63d3446f2e54ddb7a54df9b10`
- `audio_mono-mic.zip` MD5 `275966d6610ac34999b58426beb119c3`.

Preregistered exclusions only:
- `02_Funk2-119-G_comp`
- `04_BN3-154-E_comp`
- `04_Jazz1-200-B_comp`.

Locked evaluation = all other 357 tracks.

Frozen V3-positive definition = unchanged V2 `independently-corroborated-candidate` on Basic Pitch events from the isolated GuitarSet microphone audio.

Matching = one-to-one maximum-cardinality against union of six GuitarSet `note_midi` annotations with onset difference `<=0.050 s`, pitch difference `<=50 cents`, offsets ignored.

Frozen gates required all of:
1. exact dataset/archive/exclusion contract
2. 357/357 tracks complete
3. >=1,000 positives
4. pooled positive precision one-sided 95% Wilson lower bound `>=0.9900`
5. each player `00..05` >=50 positives and precision `>=0.9500`
6. both `comp` and `solo` >=50 positives and precision `>=0.9500`
7. event identity preserved and all non-promotion guards false/zero.

### V3 execution

First launch failed before any inference/correctness result: the harness dereferenced the venv Python symlink to system Python and the first Basic Pitch child failed with `ModuleNotFoundError: No module named 'numpy'`. Zero completed inference JSONs existed from that launch.

The valid run used a regular-file copy of the same pinned Python executable inside the same pinned venv; repository source and every substantive V3 method/gate remained unchanged.

Valid execution provenance:
- branch `songsterr-fresh-pipeline-v1`
- source `783c3b572aff4edd9d6298e9131dffd02454a61e`
- worktree clean
- Python `3.10.21`
- Basic Pitch `0.4.0`
- NumPy `1.26.4`
- SoundFile `0.13.1`
- 357/357 tracks completed.

Frozen result:
- decoded events: **62,438**
- V3-positive: **11,252**
- correct V3-positive: **10,019**
- precision: **0.8904194809811589**
- one-sided 95% Wilson lower bound: **0.8854816094599652**
- required lower bound: **0.9900** → FAIL
- every player `00..05` failed point precision `>=0.9500`
- `comp` precision `0.8441590516176833` → FAIL
- `solo` precision `0.9164237123420796` → FAIL.

Artifact hashes:
- outer official result SHA-256 `e6edd37e72f24bef069d16b4accb48423b9472fe26eb90adee15e401e5b4196d`
- core result SHA-256 `9a2d103cfbe6f9c3bd8b7903c665affa41729ec2da7f303a5b1c416a2a532e4e`.

Immutable result record:
- `docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3_RESULT.md`
- commit `91b021f6b3f43cee73dc58d1aebf29492a547928`.

Separate policy review:
- `docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3_POLICY_REVIEW.md`
- commit `3b8159be0898a71b33069f94a4ca4d1ada0a7047`
- decision: **CLOSED / REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**.

No V3 gate may be relaxed or tuned after this result. Do not add exclusions, lower thresholds, reinterpret the 89% precision as sufficient, or use historical protected-song behavior to override the external result.

No protected-song V3 execution occurred and none is authorized from this failed V3 result.

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
- `DURATION_EVIDENCE_INCOMPLETE`.

No reference scorer/tab/archive logic. No GOAT. No threshold sweep. No training/fine-tuning. No promotion from hashes, reproducibility, confidence, event counts, synthetic-suite success, C-S agreement, historical protected-song results, or an external result that failed the frozen gates.

## NEXT ALLOWED WORK

V1, V2, and V3 are closed as admission-authority candidates.

No V4/successor workstream is opened by this checkpoint. A future successor requires explicit user authorization and a **new preregistration before any successor result is viewed**. It may use V3 only as historical research evidence; it may not patch or retune V3 in place.

Until such authorization:
- do not rerun GuitarSet V3
- do not run the protected song
- do not resume duration
- do not reopen archived V143/Gomyway, GOAT, reference scoring, threshold sweeps, or training/fine-tuning.

## STABLE REFERENCES

- canonical current state: `SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
- V3 prereg: `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`
- V3 method: `SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3.md`
- V3 immutable result: `SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3_RESULT.md`
- V3 policy review: `SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3_POLICY_REVIEW.md`
- V2 prereg/method/result/policy review remain frozen historical references
- Policy C-S runbook: `SONGSTERR_FRESH_CODESPACES_SESSION_AUTHORITY.md`
- GOAT closeout: `SONGSTERR_FRESH_GOAT_RESEARCH_CLOSED_REFERENCE_ONLY.md`.
