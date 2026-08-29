# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC  
Branch: `v143-contextual-prune-lobo`

## Active phase
**V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 is CLOSED / TERMINAL. No independent professional combined-Guitar holdout asset has been admitted. V168 reference-facing score calls remain exactly 0. GOAT is the primary access-controlled holdout lead; G&N is the strongest provenance-only fallback but remains rights/acquisition-blocked. The next useful work requires external asset access/provenance, not more scorer/candidate code. `main`/Production remain untouched. CPU only; fresh explicit authorization is required before GPU/CUDA/Modal.**

## Percentage reporting — STANDING USER INSTRUCTION
The user prefers a percentage score in future progress/test updates because it helps motivation and makes progress easier to follow.

### Project Progress Score
Use a fixed five-gate rubric, 20 percentage points each:
1. **Preregistration + frozen Policy A/B complete** — 20%.
2. **Admission/provenance validators frozen + self-tested** — 20%.
3. **External candidate screening completed to a defensible stop boundary** — 20%.
4. **>=2 admissible independent professional holdout songs acquired; rights/provenance frozen; exact source/reference SHA256-bound; both validators passed** — 20%.
5. **Reference-blind Policy A/B candidates frozen for all admitted songs + prospective holdout scoring completed under the frozen evaluation rule** — 20%.

### Current score
**Project Progress Score: 60%** — gates 1–3 complete; gates 4–5 incomplete.  
**Test Score: NOT RUN** — no legitimate V168 holdout evaluation has occurred.

### Score integrity
- Percentage display is motivational/reporting only; it never replaces frozen scientific pass/fail gates.
- Never invent/inflate a model score or round upward to imply success.
- Keep **Project Progress Score** separate from **Test Score**.
- If no legitimate evaluation ran, report `Test Score: NOT RUN`.
- Meaningful research may be reported even if the fixed Project Progress Score does not change.
- Include the percentage score in future user-facing progress/test updates and future checkpoint updates unless the user asks otherwise.

Score-reporting rule creation commit: `6145665b2705e904f657e59ed5631404f03d36d7`.

## Latest work — GOAT access request prepared
Dedicated checkpoint:
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_READY_20260829.md`
- creation commit `e6895981e3571550297efb954ec1436314042a9b`
- status **REQUEST TEXT PREPARED / ACCESS NOT YET CLAIMED OR GRANTED / NO ASSETS ADMITTED / SCORING NOT ARMED**.

### Authoritative GOAT access facts
- Dataset record: `https://zenodo.org/records/15690894`
- DOI `10.5281/zenodo.15690894`
- Version v1; Resource type Dataset; files **Restricted**.
- Public record asks interested users to include a short description of intended use.
- Public record states the dataset is **for research purposes only** and **not intended for use in any commercial product**.
- Public Rights/License field is unpopulated on the inspected record page, so any eventual owner grant/conditions must be preserved as controlling use-basis provenance.
- Public repository `JackJamesLoth/GOAT-Dataset` directs users to request access through Zenodo.
- ISMIR paper says distribution is by request to better control its use for research purposes only.

### Prepared request posture
The saved request states that V168 would use GOAT only for a controlled non-commercial research evaluation of two already-frozen policies; reference annotations remain isolated from candidate generation; restricted files are not redistributed/published/shipped; Production remains separate; and any owner conditions will be honored.

### Submission status
**NOT SUBMITTED from this session.** No Zenodo connector/plugin is currently available in this environment, so do not claim submission or approval.

When an actual request is submitted, preserve non-secret evidence of:
- request date/status;
- exact intended-use wording;
- grant date/status if approved;
- any owner conditions or restrictions.

Never commit passwords, tokens, private/secret links, or credentials.

## GOAT admission preflight if access is granted
Before any candidate code/scoring:
1. Freeze exact record/version and downloaded file identities/SHA256.
2. Freeze exact source-audio/reference pair bindings.
3. Identify the exact professional reference layer prospectively.
4. Do not silently treat separately fine-aligned MIDI as `derivedFromModelOrCandidateOutput=false`; its derivation must be reviewed under the frozen gate.
5. Freeze any timing conversion prospectively.
6. Keep professional-reference bytes inaccessible to candidate generation.
7. Freeze a deterministic score-blind song/integrity selection rule.
8. Run both frozen V168 validators on a complete >=2-song manifest before candidate generation.

### Known GOAT integrity note
Public GitHub issue #1 currently reports possible duration/EOF mismatches for `item_67`, `item_96`, and `item_110`. There was no author reply at the last inspection. These remain **unverified third-party reports**, not confirmed defects.

If access is granted, check these prospectively during integrity intake. Freeze any exclusion/repair policy before comparative scores; never drop a song because its Policy A/B score is unfavorable.

## Public/open holdout search — FROZEN STOP
Dedicated checkpoint:
- `docs/checkpoints/V168_OPEN_HOLDOUT_SEARCH_STOP_20260829.md`
- creation commit `2b4d60cd022655076817b1e5bdad5bf5d0298606`
- status **OPEN SEARCH EXHAUSTED TO CURRENT PRACTICAL FRONTIER / EXTERNAL ACCESS OR NEW PROVENANCE REQUIRED**.

Do not repeatedly broad-search the same public corpora by default. Resume only if genuinely new evidence/datasets appear or access/provenance changes.

## Candidate status summary
### GOAT — PRIMARY LEAD / NOT ADMITTED
Strong original real electric-guitar audio + manually checked audio/tab pairs + explicit research-access request path. Blocked only because access/grant/bytes are not yet present and exact reference-layer derivation still must pass the frozen gate.

### G&N — PROVENANCE-STRONG FALLBACK / BLOCKED
Dedicated checkpoint `docs/checkpoints/V168_GN_DATASET_SCREENING_20260829.md`, commit `b71cf2c079b695d9b6c18faacc4a85853d7c0d16`.
- 42 unaccompanied electric-guitar solo tracks.
- Experienced electric-guitar player carefully annotated all note-event/technique timestamps using book tablatures; second electric-guitar player checked every label.
- Excellent human/professional reference provenance.
- Blocked because exact source audio comes from commercial *Rock Lead Basics* companion material and no lawful frozen research-use acquisition path for source audio + annotations has been established.

### IDMT-SMT-Guitar — BLOCKED
Dedicated checkpoint `docs/checkpoints/V168_IDMT_SMT_GUITAR_SCREENING_20260829.md`, commit `5c197a9cef7700df717cfbb041a0673aab5429f0`.
- Evaluation-purpose CC BY-NC-ND 4.0 use basis resolved.
- Original benchmark had manually annotated XML ground truth.
- Five song-like subset-3 pieces are later additions; exact professional annotation/validation chain not documented strongly enough for current `professional_scorer_ready` gate.

### AG-PT — EXCLUDED
Dedicated checkpoint `docs/checkpoints/V168_AGPT_EGSOLO_TRIAGE_20260829.md`, commit `e114eab039e588484d4f91fba153dd56e4a4cbaf`.
- Strong musician annotation evidence but isolated monophonic technique/note material, not song/piece holdout streams.

### EG-Solo — BLOCKED
- Promising manual tablature-assisted annotation.
- Source performances are third-party YouTube popular-rock demonstrations with no frozen exact-source research-use grant.

### EGDB real-world — BLOCKED
- Paper reports musician manual annotation of five real-world YouTube recordings.
- Exact public professional symbolic references/use basis not frozen; source-use rights unresolved.

### EGSet12 — BLOCKED
- Authors' loader requires `jams_corrected/<track>.jams` and inference naming references `Jams_corrected`.
- Public code/history/tree/issues/releases do not publish corrected JAMS or explain correction derivation.
- Do not substitute public release JAMS by assumption.

### François Leduc — EXCLUDED
Released high-resolution MIDI uses transcription-model activations for alignment; violates current frozen `derivedFromModelOrCandidateOutput=false` gate.

### GAPS — EXCLUDED
High-resolution alignment is algorithm/model-assisted before human verification/correction; excluded under current strict no-model-derived-reference rule.

### GuitarSet — NOT ADMITTED
Annotations rely substantially on automated monophonic pitch tracking from hex-string recordings; known annotation issues exist.

### Guitar-TECHS — NOT ADMITTED
Professional performers but synchronized MIDI/pickup labels are not independently established professional note-event transcription references.

### Other terminal fast rejects
- Kaggle Guitar Transcription Dataset — frame-level finger/fret labels, not professional timing-aware song note-event reference.
- EGFxSet — isolated single tones.
- GUITAR-FX-DIST — isolated notes/chords/effects corpus.
- EG-IPT — isolated monophonic single-note technique corpus.

## Frozen V168 machinery — UNCHANGED
- Base admission validator: `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`.
- Provenance companion: `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`, blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`.
- Intake requirements: `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`, blob `3064b8e9000fbab1b031ed32389cb82aab846876`.
- Preregistration: `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`, commit `64d724e816808aa60d766923bb1a9ce241e89e89`, blob `3a72db20d4ebebf8e4a25f5c37125e1a40934047`.
- Provenance self-test receipt: `debug/v168-holdout/provenance-gate-selftest-receipt.json`, blob `5540b4895e94eeb7636cbf1c0b80b1786e7bf861`.
- Frozen V154 scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Core `score_stream()` is song-generic, but current V154 CLI/loaders hardcode **Lenny Kravitz — Are You Gonna Go My Way**; do not implement a generic V168 adapter before asset admission.

## Frozen V168 policies — UNCHANGED
**Policy A — `v168-baseline-i005-policy`**  
V167 I005 / `gss-active-only` with frozen calibration settings.

**Policy B — `v168-gap1-earliest-policy`**  
Exact Policy A stream, then same-MIDI connected components with consecutive grid gaps <=1 collapse to earliest event; singletons unchanged.

No holdout-driven selector/threshold mutation.

## Holdout admission gate — HARD BLOCK
No V168 scorer workflow may be armed until:
1. >=2 genuinely independent songs pass BOTH frozen validators;
2. each is different from `Are You Gonna Go My Way`;
3. each has frozen exact source audio + professional scorer-ready combined-Guitar reference identity + source/reference pair binding;
4. `professionalReference.derivedFromModelOrCandidateOutput=false` is defensible;
5. candidate generation cannot access professional-reference content/bytes;
6. Policy A/B candidates are generated reference-blind and fully hash-frozen for every admitted song;
7. a global candidate-freeze manifest is committed before first score call.

If fewer than 2 valid songs exist, remain `HOLDOUT_ASSET_MISSING`; score calls remain **0**.

## V168 prospective evaluation rule — UNCHANGED
Primary: combined-Guitar timing-aware pitch F1 under frozen V154 `score_stream()` semantics, equal-weight macro average across admitted songs.

Policy B passes only if ALL:
- macro F1 >= Policy A + **0.10pp**;
- macro precision >= Policy A;
- no individual song loses > **0.25pp F1** vs Policy A;
- >=2 independent songs scored;
- no holdout-driven retuning, adverse-result song exclusion, variant addition, or post-score mutation.

Tie/inconclusive -> retain Policy A / `HOLDOUT_INSUFFICIENT`.

## V167 terminal handoff — IMMUTABLE
- Promoted I005 `gss-active-only`: Guitar F1 **42.7940586109996%**, P48.54280510018215%, R38.26274228284279%; 533/1098/1393; FP565/FN860; SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass: F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.
- Highest scored but unpromoted `recur-gap1-earliest`: Guitar F1 **42.88012872083669%**, +0.08607010983709418pp vs I005; SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`.
- It did NOT clear frozen +0.10pp promotion threshold. No I006 exists.
- V167 closure commit `cef3d57baf346e1f01faad19bb0998d602e86386`.

## Standing safety/methodology
- V168 is prospective holdout evaluation, not calibration continuation.
- Reference content cannot be read by candidate generation/policy code.
- Freeze all candidate outputs before reference scoring.
- No per-event reference choices, direct reference-event copying, post-score mutation, retuning, adverse-result song exclusion, or gate weakening.
- Third-party/private permission obtained by another project does **not** transfer to DadRock.
- Public availability, a YouTube URL, commercial purchase, article license, or unlicensed GitHub repository is not by itself an adequate exact-source `rightsOrUseBasis`.
- CPU only; fresh explicit authorization immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — GOAT REQUEST MUST BE SUBMITTED / EXTERNAL ACCESS REQUIRED
1. **Project Progress Score: 60%. Test Score: NOT RUN.**
2. **Do not score.**
3. **Do not implement candidate generation or a generic/new-song scorer adapter.**
4. Submit the prepared GOAT request through the official Zenodo record. This session currently has no Zenodo connector/plugin, so do not claim it was submitted here.
5. Preserve any grant/conditions as provenance without committing secrets.
6. Once access is actually granted, resume immediately with score-blind GOAT metadata/integrity intake: exact version/bytes/SHA256, source/reference pair binding, reference-layer derivation, license/use terms, and reported duration/EOF anomalies.
7. Freeze deterministic integrity/song-selection rules before comparative scoring.
8. No asset admission until a complete >=2-song manifest passes BOTH frozen validators.
9. Secondary path only if needed: obtain explicit lawful research-use rights/source/reference distribution for G&N or a genuinely new professional dataset.
10. Save `CURRENT_STATE.md` before any future admission, candidate code arm, or scorer arm.
11. Include Project Progress Score/Test Score in future user-facing updates.
12. CPU only; no GPU/CUDA/Modal; never modify main/Production.
