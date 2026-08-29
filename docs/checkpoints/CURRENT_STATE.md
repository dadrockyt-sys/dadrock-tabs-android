# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 is CLOSED / TERMINAL. No independent professional combined-Guitar holdout asset has been admitted, so V168 remains at exactly 0 reference-facing score calls. The current public/open holdout search is now prospectively stopped at the practical frontier: GOAT is the primary access-controlled lead; G&N is a provenance-strong but rights/acquisition-blocked fallback. No currently screened openly obtainable candidate clears the frozen professional-reference + exact-source use-basis gates. The next useful work requires external asset access/provenance, not more scorer/candidate code. `main`/Production remain untouched; CPU only; fresh explicit authorization is required before GPU/CUDA/Modal.**

## Most recent continuation work — FROZEN

### Open-search stop
- `docs/checkpoints/V168_OPEN_HOLDOUT_SEARCH_STOP_20260829.md`
- creation commit `2b4d60cd022655076817b1e5bdad5bf5d0298606`
- status **OPEN SEARCH EXHAUSTED TO CURRENT PRACTICAL FRONTIER / EXTERNAL ACCESS OR NEW PROVENANCE REQUIRED / NO ASSETS ADMITTED / SCORING NOT ARMED**.
- Do not continue broad public-dataset searching by default unless genuinely new evidence appears.
- No external source/reference asset was admitted.
- No candidate-generation workflow exists.
- No generic/new-song V168 scorer adapter exists or is armed.
- V168 reference-facing score calls remain **0**.

### GOAT — PRIMARY ACQUISITION LEAD / NOT ADMITTED
- Zenodo DOI `10.5281/zenodo.15690894`; files are restricted/request-access.
- Authors' public repository explicitly directs researchers to request access on Zenodo.
- ISMIR paper says distribution is by request to better control use for **research purposes only**.
- 5.9 h of unique high-quality electric-guitar DI recordings with Guitar Pro tablatures/DadaGP, quantized MIDI, and separately fine-aligned MIDI.
- Audio/tab pairs were manually checked/aligned against tablature so every note matched; this is the strongest currently available provenance path.
- The separately fine-aligned MIDI was produced through an external alignment procedure and must **not** be silently relabeled `derivedFromModelOrCandidateOutput=false`.
- No GOAT access has been claimed or granted in this project.
- Before admission: preserve exact access grant/terms, exact version/bytes + SHA256, exact source/reference pair binding, chosen reference layer, timing conversion if any, reference isolation, and score-blind deterministic song selection.
- Public GitHub issue #1 currently reports possible duration/EOF mismatches for `item_67`, `item_96`, and `item_110`; there is no author reply at this checkpoint. Treat these as **unverified third-party integrity reports**, not confirmed defects.
- If access is later granted, integrity handling/exclusion criteria must be frozen prospectively before comparative scores; never drop adverse-result songs after scoring.

### G&N — PROVENANCE-STRONG FALLBACK / BLOCKED
- Dedicated checkpoint: `docs/checkpoints/V168_GN_DATASET_SCREENING_20260829.md`
- creation commit `b71cf2c079b695d9b6c18faacc4a85853d7c0d16`.
- TENT paper describes 42 unaccompanied monophonic electric-guitar solo tracks, 20–40 s each, 19:31 total, 1,113 note events.
- All note-event/technique timestamps were carefully annotated by an **experienced electric-guitar player** using the book's tablatures; every label was then checked by a second electric-guitar player.
- Reference provenance is unusually strong and not described as model-derived.
- Material blocker: source audio is the commercial *Rock Lead Basics: Master Class Series* companion recording. No frozen lawful research-use acquisition path for exact source audio + corresponding annotations has been established.
- Public `srviest/SoloLa` tree has code/models/outputs and `answers/*.answer`, but no source `.wav` files and no repository `LICENSE` file. No answer/note-event content was opened.
- Do not treat purchase/possession of publisher audio or the TENT article's CC BY license as a dataset/audio use grant.

## Newly terminal fast-triaged candidates

### Kaggle Guitar Transcription Dataset — EXCLUDED
- CC BY-NC-SA 4.0; creators played/annotated the data.
- Ground truth is frame-level finger press/fret/string state tied to video frames/timestamps, not a professional timing-aware note-event stream for complete guitar pieces.
- No adequate professional annotator provenance identified for frozen `professional_scorer_ready` semantics.

### EGFxSet — EXCLUDED / WRONG EVALUATION UNIT
- Zenodo DOI `10.5281/zenodo.7044411`.
- Professional guitarist recorded all individual notes of a 22-fret Stratocaster across pickup settings, then tones were processed through effects.
- Strong real/professional performance provenance, but isolated single-tone unit rather than independent song/piece streams.

### GUITAR-FX-DIST — EXCLUDED / WRONG EVALUATION UNIT
- Uses IDMT-SMT-Audio-Effects isolated monophonic notes plus 2/3/4-note intervals/chords, then large-scale effect processing.
- Not a >=2-song professional timing-aware note-event holdout.

### EG-IPT — EXCLUDED / WRONG EVALUATION UNIT
- Large professional-performer electric-guitar technique corpus, but explicitly isolated monophonic single-note performances.
- Not a song/piece holdout.

## Previously frozen candidate screening

### IDMT-SMT-Guitar — BLOCKED
- Dedicated checkpoint `docs/checkpoints/V168_IDMT_SMT_GUITAR_SCREENING_20260829.md`, creation commit `5c197a9cef7700df717cfbb041a0673aab5429f0`.
- Fraunhofer states evaluation-purpose **CC BY-NC-ND 4.0**.
- Original 2014 benchmark had manually annotated XML ground truth.
- Current subset 3 has five short piece-like WAV/XML pairs, but later literature identifies those five pieces as later additions beyond the original two partitions and does not document their exact professional annotation/validation chain strongly enough.
- Remains **BLOCKED / NOT ADMITTED**.

### AG-PT-set — EXCLUDED
- Dedicated checkpoint `docs/checkpoints/V168_AGPT_EGSOLO_TRIAGE_20260829.md`, creation commit `e114eab039e588484d4f91fba153dd56e4a4cbaf`.
- Human/musician annotations, but monophonic individual-note/technique material rather than song/piece streams.

### EG-Solo — BLOCKED
- Same triage checkpoint above.
- Strong manual tablature-assisted annotation signal, but source performances are third-party professional YouTube demonstrations of popular rock songs; no frozen exact-source research-use grant was found.

### EGDB five-song real-world set — BLOCKED
- Paper says five real-world YouTube guitar recordings were manually annotated by the authors' musician.
- Public inspected materials do not expose the musician's exact symbolic reference events with a frozen use basis; third-party YouTube source rights/use basis unresolved.
- Do not use proposed-model rendered output WAVs as ground truth.

### EGSet12 — BLOCKED
- Authors' loader requires `jams_corrected/<track>.jams`; inference naming also says `Jams_corrected`.
- Public code/history/tree/issues/releases do not publish corrected JAMS or explain the correction derivation.
- Do not substitute public Zenodo JAMS by assumption.

### François Leduc — EXCLUDED
- Strong professional scores, but released high-resolution MIDI is created using transcription-model activations for alignment; violates current frozen `derivedFromModelOrCandidateOutput=false` gate.

### GAPS — EXCLUDED
- High-quality real classical guitar, but high-resolution reference alignment is algorithm/model-assisted before human verification/correction; excluded under current strict no-model-derived-reference rule.

### GuitarSet — NOT ADMITTED
- Rich paired guitar audio/JAMS, but note annotation construction relies substantially on automated monophonic pitch tracking from hex-string recordings and known annotation issues exist.

### Guitar-TECHS — NOT ADMITTED
- Professional performers with synchronized MIDI capture, but labels arise from instrument/MIDI-pickup capture rather than independently established professional note-event transcription.

## Frozen V168 machinery — UNCHANGED
- Base admission validator: `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`.
- Provenance companion: `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`, blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`.
- Intake requirements: `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`, blob `3064b8e9000fbab1b031ed32389cb82aab846876`.
- Preregistration: `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`, commit `64d724e816808aa60d766923bb1a9ce241e89e89`, blob `3a72db20d4ebebf8e4a25f5c37125e1a40934047`.
- Provenance self-test receipt: `debug/v168-holdout/provenance-gate-selftest-receipt.json`, blob `5540b4895e94eeb7636cbf1c0b80b1786e7bf861`.
- Frozen V154 scorer file: `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Core `score_stream()` is song-generic, but current V154 CLI/loaders hardcode **Lenny Kravitz — Are You Gonna Go My Way**; no V168 generic adapter may be built before asset admission.

## Frozen V168 policies — UNCHANGED
**Policy A — `v168-baseline-i005-policy`**
- V167 I005 / `gss-active-only` with fixed calibration settings.

**Policy B — `v168-gap1-earliest-policy`**
- Exact Policy A stream, then same-MIDI connected components with consecutive grid gaps <=1 collapse to earliest event; singletons unchanged.

No holdout-driven selector/threshold mutation is permitted.

## Holdout admission gate — HARD BLOCK
No V168 scorer workflow may be armed until:
1. >=2 genuinely independent songs pass BOTH frozen validators;
2. each is different from `Are You Gonna Go My Way`;
3. each has frozen exact source audio + professional scorer-ready combined-Guitar reference identity + source/reference pair binding;
4. `professionalReference.derivedFromModelOrCandidateOutput=false` is defensible;
5. candidate generation cannot access professional-reference content/bytes;
6. Policy A/B candidates are generated reference-blind and fully hash-frozen for every admitted song;
7. a global candidate-freeze manifest is committed before first score call.

If fewer than 2 valid songs exist, remain `HOLDOUT_ASSET_MISSING` and score calls remain **0**.

## V168 prospective evaluation rule — UNCHANGED
- Primary metric: combined-Guitar primary timing-aware pitch F1 under frozen V154 `score_stream()` semantics, through a future prospectively frozen adapter if required.
- Equal-weight macro average across admitted songs.
- Policy B passes only if ALL:
  - macro F1 >= Policy A + **0.10pp**;
  - macro precision >= Policy A;
  - no individual song loses > **0.25pp F1** vs Policy A;
  - >=2 independent songs scored;
  - no holdout-driven retuning, adverse-result song exclusion, variant addition, or post-score mutation.
- Tie/inconclusive -> retain Policy A / `HOLDOUT_INSUFFICIENT`.

## V167 terminal handoff — IMMUTABLE
- Promoted I005 `gss-active-only`: Guitar F1 **42.7940586109996%**, P48.54280510018215%, R38.26274228284279%; 533/1098/1393; FP565/FN860; SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass: F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.
- Highest scored but unpromoted `recur-gap1-earliest`: Guitar F1 **42.88012872083669%**, +0.08607010983709418pp vs I005; SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`.
- It did NOT clear frozen +0.10pp promotion threshold. No I006 exists.
- V167 closure commit `cef3d57baf346e1f01faad19bb0998d602e86386`.

## Standing methodology / safety
- V168 is prospective holdout evaluation, not calibration continuation.
- Reference content cannot be read by candidate generation/policy code.
- Freeze all candidate outputs before reference scoring.
- No per-event reference choices, direct reference-event copying, post-score mutation, retuning, adverse-result song exclusion, or gate weakening.
- Third-party/private permission obtained by another project does **not** transfer to DadRock.
- Public availability, a YouTube URL, commercial purchase, article license, or unlicensed GitHub repository is not by itself an adequate exact-source `rightsOrUseBasis`.
- CPU only; fresh explicit authorization immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — EXTERNAL ACCESS / PROVENANCE REQUIRED
1. **Do not score.**
2. **Do not implement candidate generation or a generic/new-song scorer adapter.**
3. Primary next step is legitimate GOAT research access. Do not claim access until actually granted; preserve exact grant/terms as provenance.
4. Once GOAT access exists, perform a score-blind metadata/integrity intake first: exact version/bytes/SHA256, source/reference pairing, reference-layer derivation, license/use terms, and verification of any reported duration/EOF anomalies. Freeze deterministic integrity/song-selection rules before comparative scoring.
5. Secondary path: obtain explicit lawful research-use rights and exact source/reference distribution for G&N or another professional set.
6. Resume broad candidate search only if genuinely new evidence/corpora appear; do not repeatedly re-screen the same blocked/excluded datasets.
7. No asset admission until a complete >=2-song manifest passes BOTH frozen validators.
8. Save this checkpoint again before any future admission, candidate code arm, or scorer arm.
9. CPU only; no GPU/CUDA/Modal; never modify main/Production.
