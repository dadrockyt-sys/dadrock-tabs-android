# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V168 is active with status `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 is CLOSED / TERMINAL and must not be reopened for another Lenny Kravitz calibration sweep. No independent professional combined-Guitar holdout asset has been admitted, so V168 remains at exactly 0 reference-facing score calls. The frozen two-policy protocol, frozen base admission validator, and frozen/self-tested provenance companion remain unchanged. GOAT remains the strongest acquisition lead but is explicitly NOT admitted because legitimate restricted research access and exact access terms/bytes are not yet present. IDMT-SMT-Guitar has now been screened to a terminal `BLOCKED / NOT ADMITTED` state under the current frozen gate: its public use basis is resolved and the original partitions have manual-ground-truth evidence, but the five song-like subset-3 pieces were later additions whose exact annotation preparation/professional validation provenance is not documented strongly enough to claim `professional_scorer_ready`. `main`/Production remain untouched; CPU only; fresh authorization required before GPU/CUDA/Modal.**

## V168 external holdout candidate screening — FROZEN STATUS + ADDENDA
- Original screening checkpoint: `docs/checkpoints/V168_HOLDOUT_CANDIDATE_SCREENING_20260829.md`.
  - commit `b64bb89a5032862d67a55d73ea4d5ddb4f4730bf`; blob `b7eab377d0feb675aca59a9a0587bdccc4db5af7`.
- Candidate addendum: `docs/checkpoints/V168_HOLDOUT_CANDIDATE_SCREENING_ADDENDUM_20260829.md`.
  - creation commit `2dcaf95ecff3ea7f7f9c422c321bf2948579eae0`.
- IDMT screening: `docs/checkpoints/V168_IDMT_SMT_GUITAR_SCREENING_20260829.md`.
  - creation commit `5c197a9cef7700df717cfbb041a0673aab5429f0`.
- Classification remains **SCREENING ONLY / NO ASSETS ADMITTED / SCORING NOT ARMED**.
- V168 reference-facing score calls remain **0**.
- No external source-audio/reference asset has been admitted; no holdout candidate-generation workflow exists; no scorer workflow is armed.

### GOAT — PRIMARY ACQUISITION LEAD / NOT ADMITTED
- Authoritative dataset record: Zenodo DOI `10.5281/zenodo.15690894`, resource type Dataset, status **Restricted**.
- Record states files are available by request for **research purposes only** and are not intended for use in a commercial product.
- The record exposes no dataset license value in the inspected rights field; the eventual access grant/terms must therefore be preserved as the frozen use-basis provenance.
- Paper describes 5.9 hours of unique real electric-guitar DI recordings with Guitar Pro tablatures, DadaGP text, quantized MIDI, and separately fine-aligned MIDI.
- Data came from main authors plus two third-party content creators. Each collected audio/tab pair was **manually checked and aligned against the tablature to ensure every note was correct between audio and tablature**.
- Additional audio was recorded by playing community-created tablatures exactly.
- The Guitar Pro/tab content is the only currently defensible professional-reference starting layer.
- A separate fine-aligned MIDI layer was produced using an external alignment procedure. Do NOT silently label that derived alignment `derivedFromModelOrCandidateOutput=false`.
- Public GOAT GitHub repository exposes two illustrative audio/tab/MIDI examples but no repository `LICENSE` file was observed in the inspected tree; examples are not a rights shortcut around the restricted dataset record.
- Before GOAT admission, must freeze: actual access grant/terms, exact dataset version + SHA256 bytes, source/reference pair binding, exact reference layer, any timing-conversion algorithm/parameters, reference isolation, and a score-blind deterministic song-selection rule.
- No GOAT access has been claimed or granted in this project at this checkpoint.

### EGDB five-song real-world evaluation set — BLOCKED
- Paper states five real-world YouTube guitar recordings were **manually annotated by the authors' musician**: strong annotation provenance.
- Public demo repo exposes five `RealData/clipN.wav` source clips and five `RealDataTranscription/clipN.wav` files used as the proposed model's rendered outputs.
- Inspected public tree does not expose the musician's manual symbolic reference note events for those five clips.
- Source recordings are third-party YouTube material; no frozen rights/use grant for the exact clips is provided in the demo/repo.
- Do not use the proposed-model output WAVs as ground truth.
- Therefore blocked on both exact professional-reference identity and source-recording use-basis.

### François Leduc Dataset — EXCLUDED UNDER CURRENT FROZEN GATE
- Strong professional source-score provenance and dozens of solo-guitar audio/MIDI pairs.
- But released high-resolution MIDI is created by aligning professional scores to **transcription-model activations**.
- Frozen V168 companion requires `professionalReference.derivedFromModelOrCandidateOutput=false`.
- Do not weaken/reinterpret the gate after discovering this dataset. The released aligned MIDI is excluded for V168.
- Raw commercial scores are a different artifact and would require separate rights, exact audio pairing, and prospective timing conversion; none is admitted.

### GAPS — EXCLUDED UNDER CURRENT FROZEN GATE
- High-quality real classical-guitar dataset, but high-resolution alignment is model/algorithm-assisted before human verification/correction.
- Frozen no-model-derived-reference rule remains controlling. Excluded for current V168.

### EGSet12 — still blocked
- Authors' loader resolves annotations from `jams_corrected/<track>.jams` and inference naming also references `Jams_corrected`.
- Public repository/issues/PRs/releases/project site/inspected history did not recover the corrected annotation bytes or correction derivation.
- Do not substitute public release JAMS by assumption.

### IDMT-SMT-Guitar — BLOCKED / NOT ADMITTED
- Frozen screening checkpoint: `docs/checkpoints/V168_IDMT_SMT_GUITAR_SCREENING_20260829.md`, creation commit `5c197a9cef7700df717cfbb041a0673aab5429f0`.
- Authoritative Fraunhofer IDMT page states the dataset is provided **for evaluation purpose under CC BY-NC-ND 4.0**.
- Zenodo DOI `10.5281/zenodo.7544110`, version `1.0.0`, exposes `IDMT-SMT-GUITAR_V2.zip` (1.3 GB), published MD5 `06796e08731bccffaed6ae59361486e4`.
- Original DAFx-2014 benchmark paper states its dataset was **recorded and manually annotated with all note parameters**, stored in XML, and used as ground truth.
- Current public subset 3 contains five short monophonic/polyphonic guitar pieces, each with XML; 2024 SynthTab independently describes these as string-level note annotated.
- Material blocker: a 2024 annotation-quality paper identifies the five short pieces and 64 longer pieces as **later additions beyond the two original partitions** and says IDMT's manual annotation procedure is not documented beyond annotation format details.
- Therefore the original paper's manual-annotation statement cannot be projected prospectively onto subset 3 as proof of a complete professional annotation/validation chain.
- A later independent random-sample onset audit reports good timing accuracy (about 8.5 ms mean absolute error on its IDMT sample), but that is not full professional validation of the five subset-3 XML references.
- Do not promote subset 3 to `professional_scorer_ready` without genuinely new primary-source provenance tying those exact five references to an adequate professional annotation/validation process.
- No IDMT source/reference bytes were acquired or inspected; no asset was admitted; score calls remain **0**.

### Other screened candidates — not admitted
- **GuitarSet:** rich paired guitar audio/annotations, but annotation construction is substantially automated and known annotation issues exist; not enough for current `professional_scorer_ready` contract without independent validation.
- **Guitar-TECHS:** professional performers + synchronized MIDI capture, but labels arise from instrument/MIDI-pickup capture rather than independently established professional note-event transcription.

## Frozen V154 scorer compatibility finding
- Frozen scorer file `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Core `score_stream()` matching algorithm is song-generic and remains the frozen matching semantics to preserve.
- But `load_generated()`, `load_reference()`, and `main()` hardcode **Lenny Kravitz — Are You Gonna Go My Way** identity.
- Future V168 must not claim the frozen V154 CLI directly accepts arbitrary holdout songs unchanged.
- If and only if a valid >=2-song external holdout is admitted first, a prospective V168 adapter may later be staged that reuses unchanged `score_stream()` semantics with a new-song normalization/input layer.
- Adapter must be frozen before any V168 reference-facing score call and may not alter matching semantics/tolerances. No adapter exists or is armed now.

## V168 provenance intake gate — FROZEN / SELF-TESTED
- Frozen base admission validator: `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`.
- Prospective provenance companion: `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`, creation commit `3102d78a99d506f31f728d1496a47fbe4e872223`, blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`.
- Intake requirements: `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`, blob `3064b8e9000fbab1b031ed32389cb82aab846876`.
- Companion validates the SAME frozen manifest schema and adds prospective provenance/source-reference binding requirements.
- Companion cannot score and opens no source-audio bytes, professional-reference bytes/note events, generated candidates, or scorer code.
- One-shot self-test run `33267391386`, job `99139780307`; terminal self-removing commit `e406ddac3eb7b1601fe6923df9afc62d99825a1a`.
- Receipt `debug/v168-holdout/provenance-gate-selftest-receipt.json`, blob `5540b4895e94eeb7636cbf1c0b80b1786e7bf861`, status `V168_HOLDOUT_PROVENANCE_GATE_SELF_TEST_FROZEN`.
- Five negative cases all rejected: source/reference binding mismatch; model-derived reference; candidate-generation reference access; unfrozen provenance; scorer incompatibility.
- Self-test confirms score calls=0, assets admitted=0, GPU/CUDA/Modal=false, main/Production=false.

## V168 preregistration — FROZEN
- `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`
- Commit `64d724e816808aa60d766923bb1a9ce241e89e89`; blob `3a72db20d4ebebf8e4a25f5c37125e1a40934047`.
- Objective: cross-song generalization comparison only; do not continue tuning the V167 calibration song.

### Frozen policies
**Policy A — `v168-baseline-i005-policy`**
- V167 I005 / `gss-active-only` policy with fixed calibration settings: active Basic Pitch context, `fundamentalPresent`, rank>=0.975, activity>=0.05, onset>=0.50, candidate/max-active score ratio>=1.00, reject nearest different active intervals {12,19,24}, top1/site, Guitar cap6, inactive branch off.

**Policy B — `v168-gap1-earliest-policy`**
- Exact Policy A stream, then same-MIDI connected components with consecutive grid gaps<=1 collapse to earliest event; singletons unchanged.
- No holdout-driven selector/threshold mutation.

Song-specific Lenny candidate JSONs are not holdout candidates. For future admitted songs, both policies must be regenerated from reference-blind frontend/evidence using the fixed definitions.

## Holdout admission gate — HARD BLOCK
No V168 scorer workflow may be armed until:
1. >=2 genuinely independent songs pass BOTH the frozen base admission validator and frozen provenance companion.
2. Each is different from `Are You Gonna Go My Way`; different artists preferred where practical.
3. Each has frozen source audio + professional scorer-ready combined-Guitar reference identity and frozen source/reference pair binding.
4. Candidate generation cannot access professional-reference event content or reference bytes.
5. Policy A/B outputs for every admitted song are generated reference-blind and fully hash-frozen before scorer/reference access.
6. A global candidate-freeze manifest is committed before first V168 score call.
7. If fewer than 2 valid songs exist, remain `HOLDOUT_ASSET_MISSING` and score calls remain **0**.

## V168 prospective evaluation rule
- Primary: combined-Guitar primary timing-aware pitch F1 under frozen V154 `score_stream()` matching contract, through a future prospectively frozen new-song adapter if required.
- Equal-weight macro average across admitted holdout songs.
- Policy B passes only if ALL:
  - macro F1 >= Policy A + **0.10pp**;
  - macro precision >= Policy A;
  - no individual holdout song loses > **0.25pp F1** vs Policy A;
  - >=2 independent songs scored;
  - no holdout-driven retuning, adverse-result song exclusion, variant addition, or post-score mutation.
- Tie/inconclusive -> retain Policy A / `HOLDOUT_INSUFFICIENT`; do not add variants after seeing scores.
- Any V168 pass is research evidence only; it does not modify main/Production.

## Repository holdout inventory result
- Only repository professional reference set remains **Lenny Kravitz — Are You Gonna Go My Way** (Rhythm + Lead + Bass components).
- No independent second-song professional scorer-ready reference exists in the project repository.
- Prior DadRock lesson/transcription assets are not professional holdout ground truth by assumption.

## V167 terminal handoff — immutable
- Current promoted I005 `gss-active-only`: Guitar F1 **42.7940586109996%**, P48.54280510018215%, R38.26274228284279%; 533/1098/1393; FP565/FN860. I005 SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass closed: F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.
- Highest scored but unpromoted `recur-gap1-earliest`: Guitar F1 **42.88012872083669%**, P48.76486733760293%, R38.26274228284279%; 533/1093/1393; FP560/FN860; +0.08607010983709418pp vs I005; SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`.
- It did NOT clear frozen +0.10pp I006 promotion threshold. No I006 exists; do not weaken gate.
- V167 closure commit `cef3d57baf346e1f01faad19bb0998d602e86386`.

## Standing methodology / safety
- V168 is prospective holdout evaluation, not calibration continuation.
- Reference content cannot be read by candidate generation/policy code.
- Freeze all candidates before reference scoring.
- No per-event reference choices, direct reference-event copying, post-score mutation, retuning, adverse-result song exclusion, or gate weakening.
- Public repo may retain non-secret hashes/manifests/provenance labels/aggregate results; private/restricted reference bytes remain under applicable storage terms.
- CPU only; fresh explicit authorization immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — GOAT ACCESS / REMAINING OPEN-CANDIDATE TRIAGE
1. **Do not score.**
2. Primary path remains legitimate GOAT research access. Do not claim access until actually granted; preserve grant/terms as provenance.
3. Continue only score-blind metadata/provenance screening of remaining openly obtainable candidates that could plausibly supply >=2 independent real guitar pieces with human/professional note-event references.
4. Fast-triage AG-PT-set and EG-Solo next: AG-PT is likely non-song/monophonic and EG-Solo likely has third-party YouTube source-rights problems, but freeze those conclusions from authoritative sources rather than assumption.
5. Do not reopen IDMT subset 3 unless genuinely new primary-source annotation/validation provenance appears.
6. Do not implement reference conversion, candidate generation, or a generic V168 scorer adapter before a complete >=2-song manifest passes BOTH frozen validators.
7. Keep EGSet12, EGDB real-world, François Leduc, GAPS, IDMT, GuitarSet, and Guitar-TECHS blocked/excluded under their current reasons; do not weaken frozen semantics.
8. Save `CURRENT_STATE.md` again before any admission or code arm.
9. CPU only; no GPU/CUDA/Modal; never modify main/Production.
