# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC  
Branch: `v143-contextual-prune-lobo`

## Active phase
**V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 is CLOSED / TERMINAL. The GOAT restricted-dataset access request has now been submitted successfully through Zenodo and is awaiting the dataset owner's decision. Submission is not approval: no GOAT bytes or owner grant/conditions are present yet, no holdout asset has been admitted, and V168 reference-facing score calls remain exactly 0. `main`/Production remain untouched. CPU only; fresh explicit authorization is required immediately before GPU/CUDA/Modal.**

## Percentage reporting — STANDING USER INSTRUCTION
The user prefers a percentage score in future progress/test updates because it helps motivation and makes progress easier to follow.

### Project Progress Score — fixed five-gate rubric
Each gate is worth 20 percentage points:
1. **Preregistration + frozen Policy A/B complete** — 20%.
2. **Admission/provenance validators frozen + self-tested** — 20%.
3. **External candidate screening completed to a defensible stop boundary** — 20%.
4. **>=2 admissible independent professional holdout songs acquired; rights/provenance frozen; exact source/reference SHA256-bound; both validators passed** — 20%.
5. **Reference-blind Policy A/B candidates frozen for all admitted songs + prospective holdout scoring completed under the frozen evaluation rule** — 20%.

### Current score
**Project Progress Score: 60%** — gates 1–3 complete; gates 4–5 incomplete.  
**Test Score: NOT RUN** — no legitimate V168 holdout evaluation has occurred.

### Score-integrity rules
- Percentage display is motivational/reporting only and never replaces frozen scientific pass/fail gates.
- Never invent/inflate a model score or round upward to imply success.
- Keep **Project Progress Score** separate from **Test Score**.
- If no legitimate evaluation ran, report `Test Score: NOT RUN`.
- Meaningful research progress may be reported even if the fixed Project Progress Score remains unchanged.
- Include percentage score in future checkpoint updates and user-facing progress/test summaries unless the user asks otherwise.

Score-reporting rule creation commit: `6145665b2705e904f657e59ed5631404f03d36d7`.

## Latest milestone — GOAT ACCESS REQUEST SUBMITTED
Dedicated submission checkpoint:
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_SUBMITTED_20260829.md`
- creation commit `2d9a2d62a712af34c2c60dfd6cf587bd9e314d96`
- status **REQUEST SUBMITTED / AWAITING OWNER DECISION / ACCESS NOT YET GRANTED / NO ASSETS ADMITTED / SCORING NOT ARMED**.

The user supplied a screenshot of an auto-generated Zenodo email whose subject/body state that the access request was submitted successfully. This is sufficient to record successful submission, but **not** approval or file access.

No private request-management link, token, password, credential, or other secret value is stored in the repository.

Prepared-request checkpoint:
- `docs/checkpoints/V168_GOAT_ACCESS_REQUEST_READY_20260829.md`
- creation commit `e6895981e3571550297efb954ec1436314042a9b`.

### GOAT authoritative access posture
- Dataset record: `https://zenodo.org/records/15690894`
- DOI `10.5281/zenodo.15690894`.
- Version v1; files restricted/request-access.
- Public record asks for a short description of intended use.
- Public record states research purposes only / not intended for commercial product use.
- Public repository `JackJamesLoth/GOAT-Dataset` directs researchers to request access through Zenodo.
- ISMIR paper says distribution is by request to control research-only use.
- No owner approval/grant has yet been claimed in this project.

### GOAT scientific/provenance notes — FROZEN
- ~5.9 h unique high-quality electric-guitar DI recordings.
- Guitar Pro tablatures / DadaGP, quantized MIDI, and separately fine-aligned MIDI are described.
- Audio/tab pairs were manually checked/aligned so every note matched.
- The separately fine-aligned MIDI was produced through an external alignment procedure and must **not** be silently relabeled `derivedFromModelOrCandidateOutput=false`.
- Before any admission, freeze exact owner grant/terms, record/version, file bytes + SHA256, source/reference pair binding, chosen reference layer, timing conversion if any, reference isolation, and deterministic score-blind song selection.

Known public GitHub issue #1 reports possible duration/EOF mismatches for `item_67`, `item_96`, and `item_110`. Treat these as **unverified third-party reports**, not confirmed defects. If access is granted, check them prospectively during integrity intake and freeze any exclusion/repair rule before comparative scoring.

Submitting the request is meaningful progress, but it does **not** satisfy gate 4; Project Progress Score therefore remains **60%**.

## Public/open holdout search — FROZEN STOP
Dedicated checkpoint:
- `docs/checkpoints/V168_OPEN_HOLDOUT_SEARCH_STOP_20260829.md`
- creation commit `2b4d60cd022655076817b1e5bdad5bf5d0298606`
- status **OPEN SEARCH EXHAUSTED TO CURRENT PRACTICAL FRONTIER / EXTERNAL ACCESS OR NEW PROVENANCE REQUIRED**.

Do not continue broad public-dataset searching by default. Resume only if genuinely new evidence/corpora appear, GOAT access status changes, G&N rights/provenance changes, or the user supplies another exact licensed professional holdout source/reference pair.

## Candidate status summary
### GOAT — PRIMARY LEAD / REQUEST PENDING / NOT ADMITTED
Strongest current path. Await owner decision. No files/reference events may be assumed available before grant.

### G&N — PROVENANCE-STRONG FALLBACK / BLOCKED
Dedicated checkpoint: `docs/checkpoints/V168_GN_DATASET_SCREENING_20260829.md`, commit `b71cf2c079b695d9b6c18faacc4a85853d7c0d16`.
- 42 unaccompanied monophonic electric-guitar solo tracks, 20–40 s each.
- Experienced electric-guitar player manually annotated note/timing/technique labels from book tablature; second electric-guitar player checked every label.
- Strong professional/human reference provenance.
- Blocked because exact source audio is commercial *Rock Lead Basics* companion material and no frozen lawful research-use acquisition path for exact source audio + annotations exists.

### IDMT-SMT-Guitar — BLOCKED
Dedicated checkpoint: `docs/checkpoints/V168_IDMT_SMT_GUITAR_SCREENING_20260829.md`, commit `5c197a9cef7700df717cfbb041a0673aab5429f0`.
Evaluation-purpose CC BY-NC-ND 4.0 basis exists, but exact professional annotation/validation provenance for the later five song-like subset-3 pieces is not strong enough for the current gate.

### AG-PT — EXCLUDED
`docs/checkpoints/V168_AGPT_EGSOLO_TRIAGE_20260829.md`, commit `e114eab039e588484d4f91fba153dd56e4a4cbaf`. Human/musician annotations, but isolated monophonic technique-note units rather than song/piece holdout streams.

### EG-Solo — BLOCKED
Promising manual tablature-assisted annotation, but source performances are third-party professional YouTube demonstrations and no frozen exact-source research-use grant was found.

### EGDB real-world — BLOCKED
Musician manual annotation reported for five YouTube guitar recordings; exact professional symbolic references/use basis and source rights remain unresolved.

### EGSet12 — BLOCKED
Authors' loader requires `jams_corrected/<track>.jams`; corrected JAMS are not publicly published/explained sufficiently. Do not substitute public Zenodo JAMS by assumption.

### Terminal exclusions / not admitted
- François Leduc — high-resolution MIDI uses transcription-model activations for alignment; violates strict no-model-derived-reference gate.
- GAPS — high-resolution reference alignment algorithm/model-assisted before human verification/correction.
- GuitarSet — annotation construction relies substantially on automated monophonic pitch tracking; known annotation issues.
- Guitar-TECHS — synchronized MIDI/pickup capture, not independently established professional note-event transcription reference.
- Kaggle Guitar Transcription Dataset — frame-level finger/fret labels, not professional timing-aware song reference.
- EGFxSet — isolated tones.
- GUITAR-FX-DIST — isolated notes/chords/effects material.
- EG-IPT — isolated monophonic single-note technique material.

## Frozen V168 machinery — UNCHANGED
- Base admission validator: `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`.
- Provenance companion: `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`, blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`.
- Intake requirements: `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`, blob `3064b8e9000fbab1b031ed32389cb82aab846876`.
- Preregistration: `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`, commit `64d724e816808aa60d766923bb1a9ce241e89e89`, blob `3a72db20d4ebebf8e4a25f5c37125e1a40934047`.
- Provenance self-test receipt: `debug/v168-holdout/provenance-gate-selftest-receipt.json`, blob `5540b4895e94eeb7636cbf1c0b80b1786e7bf861`.
- Frozen V154 scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Core `score_stream()` is song-generic, but current V154 CLI/loaders hardcode **Lenny Kravitz — Are You Gonna Go My Way**. Do not build/arm a generic V168 adapter before asset admission.

## Frozen V168 policies — UNCHANGED
**Policy A — `v168-baseline-i005-policy`**  
V167 I005 / `gss-active-only` with frozen calibration settings: active Basic Pitch context, `fundamentalPresent`, rank>=0.975, activity>=0.05, onset>=0.50, candidate/max-active score ratio>=1.00, reject nearest different active intervals {12,19,24}, top1/site, Guitar cap6, inactive branch off.

**Policy B — `v168-gap1-earliest-policy`**  
Exact Policy A stream, then same-MIDI connected components with consecutive grid gaps <=1 collapse to earliest event; singletons unchanged.

No holdout-driven selector/threshold mutation.

## Holdout admission gate — HARD BLOCK
No V168 scorer workflow may be armed until:
1. >=2 genuinely independent songs pass BOTH frozen validators;
2. each is different from `Are You Gonna Go My Way`; different artists preferred where practical;
3. each has frozen exact source audio + professional scorer-ready combined-Guitar reference identity + source/reference pair binding;
4. `professionalReference.derivedFromModelOrCandidateOutput=false` is defensible;
5. candidate generation cannot access professional-reference content/bytes;
6. Policy A/B candidates are generated reference-blind and fully hash-frozen for every admitted song;
7. a global candidate-freeze manifest is committed before first reference-facing score call.

If fewer than 2 valid songs exist, remain `HOLDOUT_ASSET_MISSING`; score calls remain **0**.

## V168 prospective evaluation rule — UNCHANGED
Primary metric: combined-Guitar timing-aware pitch F1 under frozen V154 `score_stream()` semantics, equal-weight macro average across admitted holdout songs.

Policy B passes only if ALL:
- macro F1 >= Policy A + **0.10pp**;
- macro precision >= Policy A;
- no individual song loses > **0.25pp F1** vs Policy A;
- >=2 independent songs scored;
- no holdout-driven retuning, adverse-result song exclusion, variant addition, or post-score mutation.

Tie/inconclusive -> retain Policy A / `HOLDOUT_INSUFFICIENT`.

## V167 terminal handoff — IMMUTABLE
- Promoted I005 `gss-active-only`: Guitar F1 **42.7940586109996%**, P48.54280510018215%, R38.26274228284279%; 533/1098/1393; FP565/FN860; SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.
- Highest scored but unpromoted `recur-gap1-earliest`: Guitar F1 **42.88012872083669%**, +0.08607010983709418pp vs I005; SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`.
- It did NOT clear frozen +0.10pp promotion threshold. No I006 exists.
- V167 closure commit `cef3d57baf346e1f01faad19bb0998d602e86386`.

## Standing safety / methodology
- V168 is prospective holdout evaluation, not calibration continuation.
- Professional-reference content cannot be read to choose favorable tracks or by candidate-generation/policy code.
- Freeze all candidates before any professional-reference scoring.
- No per-event reference choices, direct reference-event copying, post-score mutation, retuning, adverse-result song exclusion, or gate weakening.
- Third-party/private permission obtained by another project does not transfer to DadRock.
- Public availability, YouTube URL, commercial purchase, article license, or unlicensed GitHub repository is not by itself an adequate exact-source rights/use basis.
- CPU only; fresh explicit authorization immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — GOAT OWNER DECISION / EXTERNAL ACCESS REQUIRED
1. **Project Progress Score: 60%. Test Score: NOT RUN.**
2. **Do not score.**
3. **Do not implement candidate generation or a generic/new-song scorer adapter.**
4. GOAT request is submitted; await explicit owner/Zenodo decision. Do not claim approval until grant evidence exists.
5. Preserve non-secret grant wording/date/conditions/restrictions if approval arrives; never commit secret links/tokens/credentials.
6. Once access is actually granted, perform score-blind GOAT metadata/integrity intake first: exact record/version, file bytes/SHA256, source/reference binding, reference-layer derivation, use terms, and the reported duration/EOF anomalies.
7. Freeze deterministic integrity/song-selection rules before reading professional note-event content for scoring or generating comparative results.
8. No asset admission until a complete >=2-song manifest passes BOTH frozen validators.
9. Only after admission may reference-blind Policy A/B candidate generation be armed; freeze all candidates globally before first score call.
10. Save `CURRENT_STATE.md` before any future admission, candidate-code arm, scorer arm, or reference-facing score call.
11. Keep Project Progress Score/Test Score in future user-facing updates.
12. CPU only; no GPU/CUDA/Modal; never modify main/Production.
