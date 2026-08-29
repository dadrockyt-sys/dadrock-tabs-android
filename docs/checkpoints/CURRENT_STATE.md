# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V168 is active with status `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 is CLOSED / TERMINAL and must not be reopened for another Lenny Kravitz calibration sweep. No independent professional combined-Guitar holdout asset has been admitted, so V168 remains at exactly 0 reference-facing score calls. The frozen two-policy protocol, frozen base admission validator, and frozen/self-tested provenance companion remain unchanged. External screening now identifies GOAT as the strongest remaining acquisition candidate, but it is explicitly NOT admitted: the authoritative dataset record is restricted, requires an access request, limits use to research, and exact downloaded bytes/access terms do not yet exist in this project. GOAT's human-checked tablature content is promising; its separately fine-aligned MIDI must not be treated as automatically admissible under the frozen no-model-derived-reference gate. `main`/Production remain untouched; CPU only; fresh authorization required before GPU/CUDA/Modal.**

## V168 external holdout candidate screening — FROZEN STATUS + ADDENDUM
- Original screening checkpoint: `docs/checkpoints/V168_HOLDOUT_CANDIDATE_SCREENING_20260829.md`.
  - commit `b64bb89a5032862d67a55d73ea4d5ddb4f4730bf`; blob `b7eab377d0feb675aca59a9a0587bdccc4db5af7`.
- New addendum: `docs/checkpoints/V168_HOLDOUT_CANDIDATE_SCREENING_ADDENDUM_20260829.md`.
  - creation commit `2dcaf95ecff3ea7f7f9c422c321bf2948579eae0`.
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

### Other screened candidates — not admitted
- **GuitarSet:** rich paired guitar audio/annotations, but annotation construction is substantially automated and known annotation issues exist; not enough for current `professional_scorer_ready` contract without independent validation.
- **Guitar-TECHS:** professional performers + synchronized MIDI capture, but labels arise from instrument/MIDI-pickup capture rather than independently established professional note-event transcription.
- **IDMT-SMT-Guitar:** paired WAV/XML transcription data remains under investigation; authoritative use-basis and professional-reference provenance not yet frozen.

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

## NEXT boundary — GOAT ACCESS / CONTINUE ACCESSIBLE-CANDIDATE SCREENING
1. **Do not score.**
2. Primary path: obtain legitimate GOAT research access. Do not claim access until actually granted; preserve the grant/terms as provenance.
3. Until access exists, continue screening openly obtainable candidates for a human/professional note-event reference layer that satisfies the frozen no-model-derived-reference rule.
4. IDMT-SMT-Guitar is the next unresolved open candidate to vet for authoritative rights/use-basis and annotation provenance.
5. Do not implement GOAT reference conversion, candidate generation, or generic V168 scorer adapter before complete >=2-song assets pass BOTH frozen validators.
6. Keep EGSet12, EGDB real-world, François Leduc, and GAPS blocked/excluded unless genuinely new provenance evidence appears; do not weaken frozen semantics.
7. Save `CURRENT_STATE.md` before any admission or code arm.
8. CPU only; no GPU/CUDA/Modal; never modify main/Production.
