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

## V3 — ACTIVE, FROZEN BEFORE FIRST EXTERNAL-CORPUS RESULT

User explicitly authorized the successor external-validation workstream.

### Preregistration

- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`
- commit `2dfd8c5d52093c36c0924e5f0b57eb2b2284e7d0`
- status: preregistered; **not admission authority**.

V3 does not alter or tune the frozen V2 per-event classifier. It asks: on a locked independently annotated guitar corpus, how precise are Basic Pitch events that pass unchanged V2 corroboration?

### Frozen implementation / provenance surface

Core harness:
- `scripts/songsterr-fresh/external_guitarset_validation_v3.py`
- implementation commit `a8a7b5f05950de6dfa061f7ee4995bafd778f17b`
- contract `songsterr-fresh-guitarset-external-validation-v3`.

Official execution wrapper:
- `scripts/songsterr-fresh/run_external_guitarset_validation_v3.py`
- commit `49e98254417c416f59575097ee6cdbf62636374a`
- contract `songsterr-fresh-guitarset-external-validation-execution-v3`.

Frozen method record:
- `docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3.md`
- provenance-complete method commit `1792739fa30c9304d37e94066794a38898dc98aa`.

Focused controlled CI:
- `.github/workflows/songsterr-fresh-guitarset-v3-ci.yml`
- initial workflow `27b1916ef5c9fa287b0186bdf03fa9e05fcd225a`
- self-match guard fix `96ae75bcfb7ddc4d469b4f96d4126f276f4c9d15`
- provenance verification update `e3e6f1fa1292d9ad82d55d64d1da9463829f064f`.

Controlled CI history:
- run `34642016377`, job `103403803350`: core compile/self-tests/constants green; final boundary guard self-matched its own forbidden literal. Integration guard-text failure only; no corpus execution.
- run `34642084982`, job `103404026067`, source `96ae75bc...`: **SUCCESS**.
- run `34642234908`, job `103404515324`, source `3d441088...`: **SUCCESS** after initial method-record freeze.
- run `34642484069`, job `103405310705`, source `e3e6f1fa...`: **SUCCESS** with execution-provenance wrapper checks.
- run `34642582311`, job `103405628860`, source `1792739f...`: **SUCCESS** after final provenance-complete method-record freeze.

All green runs remained controlled-only. No GuitarSet archive was downloaded/evaluated by V3 CI and the protected song was not evaluated. Current real-corpus result count remains **zero**.

### Locked external corpus

Dataset: GuitarSet v1.1.0, DOI `10.5281/zenodo.3371780`.

Authorized files only:
- `audio_mono-mic.zip`, MD5 `275966d6610ac34999b58426beb119c3`
- `annotation.zip`, MD5 `b39b78e63d3446f2e54ddb7a54df9b10`.

Exactly three publicly documented defective tracks were excluded before model results:
- `04_BN3-154-E_comp`
- `04_Jazz1-200-B_comp`
- `02_Funk2-119-G_comp`.

Locked evaluation corpus = all other **357 tracks**. GuitarSet is evaluation-only; no GuitarSet development split exists.

### Frozen inference / matching

For every locked track:
- microphone WAV must already be mono 44100 Hz; no resampling/drop
- no Demucs: GuitarSet microphone audio is already isolated guitar
- existing Basic Pitch wrapper invoked once with Basic Pitch 0.4.0, MIDI 40..88, onset .5, frame .3, minimum note length 127.7 ms, no multiple pitch bends, melodia trick enabled
- only event identity, onset seconds and integer MIDI enter validation
- Basic Pitch end/confidence remain diagnostic only
- unchanged V2 classifier runs on the exact microphone-audio window
- V3-positive = V2 `independently-corroborated-candidate`.

Ground truth = union of all six per-string GuitarSet `note_midi` annotations. Matching is one-to-one maximum-cardinality with onset difference `<=0.050 s`, pitch difference `<=50 cents`, offsets ignored, no confidence/score tie policy.

### Frozen pass gates

All must pass:
1. exact dataset/version/archive identities + exact preregistered exclusions
2. all 357 locked tracks complete; no post-hoc exclusion
3. at least 1,000 V3-positive events
4. pooled V3-positive precision one-sided 95% Wilson lower bound `>=0.9900`, `z=1.6448536269514722`
5. each player `00..05`: >=50 V3-positive and point precision >=0.9500
6. both `comp` and `solo`: >=50 V3-positive and point precision >=0.9500
7. event identity preserved + all non-promotion guards false/zero.

No gate may be relaxed after results. No GuitarSet result may tune V3 under this preregistration.

### Frozen official execution provenance

Official execution fails closed unless:
- branch exactly `songsterr-fresh-pipeline-v1`
- clean worktree
- exact source commit recorded
- Python 3.10
- Basic Pitch 0.4.0
- NumPy 1.26.4
- SoundFile 0.13.1
- work/result paths outside repo
- source and runtime unchanged before/after full execution.

Final result records full source/runtime/package provenance, SHA-256 identities for the wrapper/core/V2/Basic-Pitch wrapper/prereg/method record, complete core result + its SHA-256, exact 357-track identities, metrics/gates and unchanged false/zero policy boundary.

### FIRST REAL CORPUS EXECUTION IS NOW PERMITTED

Prerequisites are satisfied:
1. external validation preregistered before results — **YES**
2. locked corpus/version/files/exclusions frozen — **YES**
3. scorer/matching/gates frozen — **YES**
4. core harness implemented and synthetic/contract tested — **YES**
5. provenance-bound official execution wrapper frozen — **YES**
6. final controlled CI green after method/provenance freeze — **YES**
7. GuitarSet correctness result viewed so far — **NO / zero executions**.

The next permitted operation is exactly one full official 357-track GuitarSet execution using `run_external_guitarset_validation_v3.py`. Do not inspect partial correctness results and patch the method. Execution/integrity failure fails closed; do not add a track exclusion or relax a gate.

The protected song remains embargoed during V3 external validation. Historical V2 187/951/2 cannot be retrospectively promoted by any V3 result.

If external validation passes, a separate explicit policy review remains mandatory before any new protected-song execution. Any future protected-song execution requires a NEW C-S epoch after that review/authorization.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Active blockers:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`.

Customer-eligible events: **0**.
`mayAdvanceDelivery:false`.
Duration research remains paused.

No reference scorer/tab/archive logic. No GOAT. No threshold sweep. No training/fine-tuning. No promotion from exact hashes, CPU association, historical frequency, candidate confidence, event count, downstream agreement, controlled-suite pass, C-S reproducibility, aggregate corroboration count, or any external point estimate that fails the frozen V3 gates.

## ACTIVE NEXT ENGINEERING STEPS

1. Use a clean current `songsterr-fresh-pipeline-v1` source state and the pinned Python 3.10 / Basic Pitch 0.4.0 / NumPy 1.26.4 / SoundFile 0.13.1 runtime.
2. Obtain only the exact GuitarSet v1.1.0 `annotation.zip` and `audio_mono-mic.zip` archives and verify the frozen MD5s before any model work.
3. Run the official provenance wrapper once over the full locked 357-track corpus, writing work/results outside the repository.
4. Preserve the immutable result artifact and core result; do not rerun/tune based on partial results.
5. Record the completed external result and perform the mandatory separate V3 policy review.
6. Keep model validation false/customer eligibility 0/delivery false and duration paused until that review explicitly decides otherwise.
7. Do not resume protected-song execution, duration, archived V143/Gomyway, reference scoring, GOAT, threshold sweeps, or training/fine-tuning during this phase.

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
- V3 method: `SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3.md`
