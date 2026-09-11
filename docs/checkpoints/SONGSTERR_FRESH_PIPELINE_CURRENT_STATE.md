# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-11 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## NON-NEGOTIABLE SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Do not resume archived V143/Gomyway implementation, reference tabs, professional/reference scoring, GOAT research, holdout scoring, training/fine-tuning, or broad optimizer/ISA sweeps unless explicitly reopened.
- The `gomyway` filename authorizes the exact protected audio fixture only; it does not authorize archived pipeline logic.
- GOAT remains CLOSED / REFERENCE ONLY.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP work remains under `scripts/songsterr-fresh/`.
- Frozen full-mixture structure precedes note inference and cannot be rewritten downstream.
- Never silently alter/drop MIDI or event identity.
- Preserve `/ai-tab`: upload → AI analysis → analyzer metadata/events → preview PDF → unlock → full PDF → browser/email.
- Duration research remains paused until upstream model-evidence validation is explicitly resolved.

## PROTECTED FIXTURE / FROZEN STRUCTURE

Protected authorized-song fixture only:
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

Policy B: hosted measurements proved real cross-run numerical/semantic variation. Exact hashes, CPU association, historical frequency, confidence, event count, downstream agreement, or finite unanimity are diagnostics only and do not prove correctness. No justified end-to-end numerical admission bound exists.

Persistent Policy C remains `UNENROLLED`.

Policy C-S is ephemeral Codespaces boot/session authority. Stop/restart/rebuild/source/fingerprint drift invalidates an epoch. Reproducibility does not imply semantic correctness.

Completed V2 epoch, now historical only:
- epoch `87926671-e6e9-4cda-87ea-8f248a6dae93`
- frozen source `a76ab8cebb47a2dd1cf78243f00e436470e32df3`
- probe/enroll/verify green
- exactly three same-session canaries aggregated green
- protected-song V2 research run completed once in that same epoch
- post-run verification remained green
- later documentation commits moved source, so the epoch is historical only and MUST NOT be reused.

## V1 — CLOSED AS ADMISSION AUTHORITY

V1 remains a frozen research diagnostic, rejected as admission authority.

Historical protected-song result: 471 corroborated / 667 not corroborated / 2 insufficient across 1,140 events.

Historical MIDI-55 (~46.2024095 s) and MIDI-64 (~79.6261406 s) cases are retrospective stress diagnostics only. They may not tune V2 or V3.

Stable records:
- `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V1.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V1.json`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_AUTHORIZED_SONG_RESULT.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_POLICY_REVIEW.md`.

## V2 — CLOSED AS ADMISSION AUTHORITY

V2 completed preregistration → implementation → controlled CI → new C-S qualification → one protected-song research run → separate policy review.

Frozen implementation:
- prereg: `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md`
- evaluator: `scripts/songsterr-fresh/independent_pitch_corroboration_v2.py`
- contract `songsterr-fresh-independent-pitch-corroboration-research-v2`
- method record `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2.md`
- controlled fixtures `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V2.json`
- 15 exact controlled fixtures, expected 6 corroborated / 7 not / 2 insufficient
- canonical fixture environment Python 3.10 / NumPy 1.26.4 / SoundFile 0.13.1
- focused green CI runs `34622465693` and `34622780588`.

Frozen V2 rule:
- exactly 44100 Hz; fixed 16384-sample post-onset window
- MIDI 40..88
- competitors `{-12,-7,-2,-1,+1,+2,+7,+12}`
- demeaned RMS `<1e-4` => insufficient
- strict `>` unique-best, no substantive margin threshold
- Channel A coherent four-harmonic semitone-cell spectral score
- Channel B YIN/CMND half-period-disambiguated score
- selected MIDI must be strict unique best in both channels
- no voting/fallback/confidence fitting/reference scorer/Basic Pitch activation/authorized-song tuning/event deletion.

Protected-song V2 result:
- record `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_AUTHORIZED_SONG_RESULT.md`
- commit `0a5181d37fdf682c1203d21c80e18909e326093a`
- 1,140 preserved events: 187 corroborated / 951 not / 2 insufficient
- no admission decision; model validation false; customer eligible 0; delivery false; duration unchanged.

V2 policy review:
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_POLICY_REVIEW.md`
- commit `4189e3e2a1ae313e41409a631023e82e205347e8`
- **REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**.

Reason: controlled fixtures prove contract behavior, C-S proves reproducibility, and the protected song is not independent ground truth. The historical 187/951/2 result may not become a threshold, prior, tuning target, or retrospective promotion rule.

## V3 — EXTERNAL VALIDATION COMPLETED / FAILED FROZEN GATES

V3 was preregistered and frozen before any GuitarSet model correctness result was viewed.

### Preregistration / frozen method

- prereg: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`
- prereg commit `2dfd8c5d52093c36c0924e5f0b57eb2b2284e7d0`
- core harness `scripts/songsterr-fresh/external_guitarset_validation_v3.py`
- official wrapper `scripts/songsterr-fresh/run_external_guitarset_validation_v3.py`
- frozen method record `docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3.md`
- final pre-corpus source/checkpoint `783c3b572aff4edd9d6298e9131dffd02454a61e`.

The frozen V2 classifier, Basic Pitch settings, GuitarSet files/exclusions, matching rules, Wilson calculation and policy gates were not tuned after results.

### Locked external corpus

Dataset: GuitarSet v1.1.0, DOI `10.5281/zenodo.3371780`.

Verified archives:
- `audio_mono-mic.zip`, MD5 `275966d6610ac34999b58426beb119c3`
- `annotation.zip`, MD5 `b39b78e63d3446f2e54ddb7a54df9b10`.

Exactly three preregistered public-defect exclusions:
- `04_BN3-154-E_comp`
- `04_Jazz1-200-B_comp`
- `02_Funk2-119-G_comp`.

Locked evaluation corpus = all other **357 tracks**.

### Execution history

Attempt 1 at source `783c3b572aff4edd9d6298e9131dffd02454a61e` failed before any Basic Pitch inference result was produced. Root cause: the core harness resolved the venv interpreter symlink to system Python, which lacked NumPy. This was an execution-environment path issue, not a model/scoring/dataset result. Zero completed inference JSONs were produced.

Attempt 2 preserved the exact same frozen repository source and scoring/matching method. A non-symlink copy of the same pinned venv Python executable was used so the harness could retain the venv package context after path resolution. Runtime checks confirmed Python 3.10, NumPy 1.26.4, Basic Pitch 0.4.0 and SoundFile 0.13.1. No repository code or frozen policy threshold changed.

### Completed V3 external result

Official attempt 2 completed all **357/357** locked tracks and emitted `V3_OFFICIAL_EXTERNAL_VALIDATION_COMPLETE`.

Observed aggregate result:
- source commit: `783c3b572aff4edd9d6298e9131dffd02454a61e`
- decoded events: **62,438**
- V3-positive events: **11,252**
- V3-positive correct: **10,019**
- V3-positive precision: **0.8904194809811589** (~89.04%)
- one-sided 95% Wilson lower bound: **0.8854816094599652** (~88.55%)
- `externalValidationPassed:false`.

Frozen gate outcomes visible from the official result:
- all 357 locked tracks completed: **PASS**
- minimum 1,000 positive events: **PASS**
- pooled Wilson lower bound >=0.9900: **FAIL**
- every player `00..05` point precision >=0.9500 with >=50 positives: **FAIL for all six players**
- both `comp` and `solo` point precision >=0.9500 with >=50 positives: **FAIL for both modes**.

Policy boundary remained correctly fail-closed:
- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`
- `separatePolicyReviewRequired:true`.

### V3 policy status

Because V3 failed the preregistered external-validation gates, it **MUST NOT** become admission authority. Do not relax the 0.9900 Wilson gate, the 0.9500 stratum gates, matching tolerances, exclusions, Basic Pitch settings, or the frozen V2 classifier in response to this result.

The protected song remains embargoed; there is no justification for a protected-song V3 rerun. Historical V1/V2 protected-song results remain research diagnostics only.

A concise archival V3 result record and fail-closed policy closeout should be written next using the completed official result. If any future successor is explored, it requires a new preregistration before looking at new evaluation results and may not tune against this same GuitarSet result under the V3 contract.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Active blockers:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`.

Customer-eligible events: **0**.
`mayAdvanceDelivery:false`.
Duration research remains paused.

No reference scorer/tab/archive logic. No GOAT. No threshold sweep. No training/fine-tuning. No promotion from exact hashes, CPU association, historical frequency, candidate confidence, event count, downstream agreement, controlled-suite pass, C-S reproducibility, aggregate corroboration count, or an external result that fails the frozen V3 gates.

## ACTIVE NEXT ENGINEERING STEPS

1. Preserve the completed attempt-2 V3 official result/core result and first-attempt execution-failure evidence outside the repository until their compact identities/strata are recorded.
2. Write an immutable archival V3 external-result record with exact aggregate metrics, provenance and gate outcomes.
3. Write a V3 policy closeout: failed preregistered external validation; rejected as admission authority; retained only as research evidence.
4. Do not rerun/tune V3 against GuitarSet.
5. Do not run the protected song, resume duration, archived V143/Gomyway, reference scoring, GOAT, threshold sweeps, or training/fine-tuning.
6. Any successor validation/scorer work requires a new explicit preregistration and authorization before execution.

## STABLE POLICY REFERENCES

- canonical current state: `SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
- GOAT closeout: `SONGSTERR_FRESH_GOAT_RESEARCH_CLOSED_REFERENCE_ONLY.md`
- Policy B numerical-bound research: `SONGSTERR_FRESH_POLICY_B_NUMERICAL_BOUND_RESEARCH.md`
- persistent Policy C: `SONGSTERR_FRESH_PINNED_COMPUTE_AUTHORITY_V1.md`
- Policy C-S: `SONGSTERR_FRESH_CODESPACES_SESSION_AUTHORITY.md`
- V1 policy review: `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_POLICY_REVIEW.md`
- V2 prereg: `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V2.md`
- V2 method: `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2.md`
- V2 protected result: `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_AUTHORIZED_SONG_RESULT.md`
- V2 policy review: `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_POLICY_REVIEW.md`
- V3 prereg: `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`
- V3 frozen method: `SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3.md`
