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
- clean branch `songsterr-fresh-pipeline-v1`
- probe/enroll/verify green
- exactly three same-session canaries aggregated green
- `surfaceQualifiedForCurrentBootSession=true`
- protected-song V2 research run completed once in that same epoch
- post-run session verification remained green
- documentation commits later moved repository source, so this epoch is historical only and MUST NOT be reused.

## V1 — CLOSED AS ADMISSION AUTHORITY

V1 remains a frozen research diagnostic, rejected as admission authority.

Historical protected-song result: 471 corroborated / 667 not corroborated / 2 insufficient across 1,140 events.

Historical MIDI-55 (~46.2024095 s) and MIDI-64 (~79.6261406 s) cases are retrospective stress diagnostics only. They may not tune V2 or V3.

Stable records:
- `SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V1.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_CONTROLLED_FIXTURES_V1.json`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_AUTHORIZED_SONG_RESULT.md`
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V1_POLICY_REVIEW.md`

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
- exactly 44100 Hz
- fixed 16384-sample post-onset window
- MIDI 40..88
- competitors `{-12,-7,-2,-1,+1,+2,+7,+12}`
- demeaned RMS `<1e-4` => insufficient
- strict `>` unique-best, no substantive margin threshold
- Channel A coherent four-harmonic semitone-cell spectral score
- Channel B YIN/CMND half-period-disambiguated score
- selected MIDI must be strict unique best in both channels
- no voting/fallback/confidence fitting/reference scorer/Basic Pitch activation/authorized-song tuning/event deletion.

Protected-song V2 result:
- result record `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_AUTHORIZED_SONG_RESULT.md`
- commit `0a5181d37fdf682c1203d21c80e18909e326093a`
- 1,140 preserved events
- 187 independently corroborated candidate
- 951 not independently corroborated
- 2 insufficient
- no admission decision; model validation false; customer eligible 0; delivery false; duration unchanged.

V2 policy review:
- `SONGSTERR_FRESH_INDEPENDENT_CORROBORATION_V2_POLICY_REVIEW.md`
- commit `4189e3e2a1ae313e41409a631023e82e205347e8`
- decision: **REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**.

Reason: controlled fixtures prove contract behavior, C-S proves reproducibility, and the protected song is not independent ground truth. V2 preregistered no external annotated-corpus accuracy protocol. The 187/951/2 result may not become a threshold, prior, tuning target, or retrospective promotion rule.

## V3 — ACTIVE, PREREGISTERED EXTERNAL VALIDATION SUCCESSOR

User explicitly authorized continuing into the successor external-validation workstream.

Preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`
- prereg commit `2dfd8c5d52093c36c0924e5f0b57eb2b2284e7d0`
- status: preregistered; **not admission authority**.

V3 does not alter or tune the frozen V2 per-event classifier. It asks a new independent question: on a locked annotated guitar corpus, how precise are Basic Pitch events that pass the unchanged V2 corroborator?

### Locked external corpus

Dataset: GuitarSet v1.1.0, DOI `10.5281/zenodo.3371780`.

Authorized files only:
- `audio_mono-mic.zip`, MD5 `275966d6610ac34999b58426beb119c3`
- `annotation.zip`, MD5 `b39b78e63d3446f2e54ddb7a54df9b10`.

The microphone audio is already isolated guitar, so V3 external validation does not invoke Demucs. It validates the isolated-guitar pitch/onset evidence boundary directly.

Exactly three publicly documented defective tracks are preregistered out before results:
- `04_BN3-154-E_comp`
- `04_Jazz1-200-B_comp`
- `02_Funk2-119-G_comp`.

Locked evaluation corpus: all other 357 tracks. No GuitarSet development split exists; GuitarSet is evaluation-only. Development may use synthetic/unit fixtures only.

### Frozen V3 inference / matching

For every locked track:
- require 44100-Hz microphone WAV; no silent resampling/drop
- invoke existing `transcribe_isolated_guitar_basic_pitch.py` once with frozen defaults: Basic Pitch 0.4.0, MIDI 40..88, onset 0.5, frame 0.3, minimum note length 127.7 ms, no multiple pitch bends, melodia trick enabled
- use only event identity, `startSeconds`, integer MIDI for evaluation
- Basic Pitch end/confidence remain diagnostic only
- apply unchanged V2 classifier to the exact microphone audio window
- V3-positive = frozen V2 `independently-corroborated-candidate`.

Ground truth is the union of all six per-string GuitarSet `midi_note` annotations. Match V3-positive estimates to references by one-to-one maximum-cardinality matching with:
- onset difference `<= 0.050 s`
- pitch difference `<= 50 cents`
- offsets ignored
- no confidence/score tie policy.

### Frozen V3 pass gates

All must pass:
1. exact dataset/version/archive identities and preregistered exclusions
2. all 357 tracks complete; no new post-hoc exclusion
3. at least 1,000 V3-positive events
4. pooled V3-positive precision one-sided 95% Wilson lower bound `>= 0.9900` using `z=1.6448536269514722`
5. every player `00..05`: at least 50 V3-positive events and point precision `>=0.9500`
6. each mode `comp` and `solo`: at least 50 V3-positive events and point precision `>=0.9500`
7. event identity preserved and all non-promotion guards false/zero.

No gate may be relaxed after results. No GuitarSet result may tune V3 under this preregistration.

### V3 execution embargo / boundary

Before prereg commit, only dataset documentation/metadata/known-error information was reviewed. No GuitarSet Basic Pitch inference or V2/V3 classification result was run or viewed.

Next allowed work:
- implement the V3 validation harness
- add synthetic/contract tests
- freeze implementation + focused controlled CI
- only then execute GuitarSet evaluation for the first time.

The protected authorized song must not be inspected/rerun during V3 external validation. Historical V2 187/951/2 cannot be retrospectively promoted by a V3 pass.

If V3 external validation passes, a separate explicit policy review is mandatory. Only after that review and explicit authorization may a new C-S epoch run a fresh protected-song V3 execution.

## CURRENT ACCEPTANCE STATE

Do **not** set `modelValidationComplete:true`.

Active blockers:
- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`.

Customer-eligible events: **0**.
`mayAdvanceDelivery:false`.
Duration research remains paused.

No reference scorer/tab/archive logic. No GOAT. No threshold sweep. No training/fine-tuning. No promotion from exact hashes, CPU association, historical frequency, candidate confidence, event count, downstream agreement, controlled-suite pass, C-S reproducibility, aggregate corroboration count, or external point estimate that fails the frozen V3 policy gates.

## ACTIVE NEXT ENGINEERING STEPS

1. Implement a deterministic V3 GuitarSet validation harness that imports/reuses the frozen V2 classifier rather than copying or changing it.
2. Hard-code/verify the v1.1.0 archive MD5 identities and exact three known-error exclusions.
3. Implement locked six-string reference parsing, one-to-one 50-ms/50-cent matching, Wilson lower bound, player/mode strata, and fail-closed policy report.
4. Add self-tests/synthetic contract tests proving matching, ties, polyphony, exclusions, Wilson math, event preservation, no duration/reference leakage into scoring, and non-promotion guards.
5. Add focused CI that runs only synthetic/contract tests. It MUST NOT download or evaluate GuitarSet.
6. Freeze the harness and CI green before any GuitarSet inference/result is viewed.
7. Then run the full locked 357-track evaluation once and write an immutable result record.
8. Do not resume duration, protected-song execution, archived V143/Gomyway, reference scoring, GOAT, threshold sweeps, or training/fine-tuning during V3 external validation.

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
