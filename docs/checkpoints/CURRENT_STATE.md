# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V168 is active with status `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 is CLOSED / TERMINAL and must not be reopened for another Lenny Kravitz calibration sweep. No independent professional combined-Guitar holdout asset has been admitted, so V168 remains at exactly 0 reference-facing score calls. The frozen two-policy protocol, frozen base admission validator, and frozen/self-tested provenance companion remain unchanged. External candidate screening now identifies EGSet12 as the strongest lead, but it is explicitly NOT admitted because the authors' evaluation loader references `jams_corrected/` while the correction provenance relative to the public release is unresolved; authoritative use-basis and exact byte identities are also not yet frozen. `main`/Production remain untouched; CPU only; fresh authorization required before GPU/CUDA/Modal.**

## V168 external holdout candidate screening — FROZEN STATUS
- Screening checkpoint: `docs/checkpoints/V168_HOLDOUT_CANDIDATE_SCREENING_20260829.md`.
- Creation commit `b64bb89a5032862d67a55d73ea4d5ddb4f4730bf`; blob `b7eab377d0feb675aca59a9a0587bdccc4db5af7`.
- Classification: **CANDIDATE SCREENING ONLY / NO ASSETS ADMITTED / SCORING NOT ARMED**.
- V168 reference-facing score calls remain **0**.
- No external source-audio/reference asset has been admitted; no holdout candidate-generation workflow exists; no scorer workflow is armed.

### EGSet12 — strongest lead, still blocked
- Status **PROMISING / NOT ADMITTED / BLOCKED ON REFERENCE-CORRECTION PROVENANCE + OFFICIAL USE-BASIS/BYTE-IDENTITY VERIFICATION**.
- Official release/paper describe 12 real original solo electric-guitar performances created for guitar-tablature evaluation; pieces were composed by a professional musician/guitar player and performed by a professional guitarist.
- Release exposes track-matched `.wav`, `.jams`, and `.gp` artifacts for tracks 01–12.
- Authors' public AMT-Tools loader can extract per-string JAMS `note_midi` note events with MIDI pitch plus onset/duration intervals.
- Material blocker: authors' `AMT-Tools/amt_tools/datasets/EGSet12.py` resolves annotations from `jams_corrected/<track>.jams`, and their inference experiment name also says `Jams_corrected`.
- The inspected public code repository does not contain `jams_corrected/` files or a documented transformation/provenance explaining differences from the published release JAMS. The inspected `EGSet12.py` history does not resolve this.
- Therefore public release JAMS must NOT be relabeled `professional_scorer_ready` by assumption.
- External descriptions consistently indicate CC BY 4.0, but authoritative rights/use-basis for the exact artifacts still must be frozen before admission.
- If EGSet12 later clears both frozen gates, prospective preference is to use **all 12 tracks**, not cherry-pick two after seeing outcomes.

### Other screened candidates — not admitted
- **GuitarSet:** rich paired guitar audio/annotations, but note annotation construction is substantially automated and known annotation issues exist; professional-reference provenance is not sufficient under the current frozen gate without additional independent validation.
- **Guitar-TECHS:** professional performers with synchronized MIDI labels, but label capture is instrument/MIDI-pickup based rather than an independently established professional note-event transcription; remains insufficient under the strict professional-reference gate.
- **IDMT-SMT-Guitar:** paired WAV/XML transcription data is promising, but authoritative use-basis and professional-reference provenance remain unresolved.
- Do not promote any of these to holdout by reputation or assumption.

## Frozen V154 scorer compatibility finding
- Frozen scorer file `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Core `score_stream()` matching algorithm is song-generic and remains the frozen matching semantics to preserve.
- But `load_generated()`, `load_reference()`, and `main()` hardcode **Lenny Kravitz — Are You Gonna Go My Way** identity.
- Therefore future V168 must not claim the frozen V154 CLI directly accepts arbitrary holdout songs unchanged.
- If and only if a valid >=2-song external holdout is admitted first, a prospective V168 adapter may later be staged that reuses the unchanged frozen `score_stream()` algorithm with a new-song normalization/input layer.
- Such an adapter must be frozen before any V168 reference-facing score call and may not alter matching semantics/tolerances. No adapter is implemented or armed now.

## V168 provenance intake gate — FROZEN / SELF-TESTED
- Frozen base admission validator remains immutable: `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`, blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`.
- Prospective provenance companion: `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`.
- Creation commit `3102d78a99d506f31f728d1496a47fbe4e872223`; blob `9edb8a65cc809d7fe42a288d6a00cfc602f37dcc`.
- Intake requirements: `docs/checkpoints/V168_HOLDOUT_ASSET_INTAKE_REQUIREMENTS_20260829.md`, blob `3064b8e9000fbab1b031ed32389cb82aab846876`.
- Companion validates the SAME frozen manifest schema `dadrock.tabs.v168.holdout-asset-manifest.v1`; it first calls the frozen base validator and then adds prospective provenance/source-reference binding requirements.
- Companion opens no source-audio bytes, professional-reference bytes/note events, generated candidates, or scorer code; it cannot score.
- One-shot self-test arm commit `830f06e4294ce4c519da97507b3d58b2ad841fef`; run `33267391386`, job `99139780307`; terminal self-removing commit `e406ddac3eb7b1601fe6923df9afc62d99825a1a`.
- Self-test receipt `debug/v168-holdout/provenance-gate-selftest-receipt.json`: blob `5540b4895e94eeb7636cbf1c0b80b1786e7bf861`; status `V168_HOLDOUT_PROVENANCE_GATE_SELF_TEST_FROZEN`.
- Five negative cases all rejected: source/reference binding mismatch; model-derived reference; candidate-generation reference access; unfrozen provenance; scorer incompatibility.
- Self-test confirms source/reference bytes read=false, scorer read=false, holdout assets admitted=0, score calls=0, GPU/CUDA/Modal=false, main/Production=false.

## V168 preregistration — FROZEN
- `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`
- Commit `64d724e816808aa60d766923bb1a9ce241e89e89`; blob `3a72db20d4ebebf8e4a25f5c37125e1a40934047`.
- Status **HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED**.
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
- Primary: combined-Guitar primary timing-aware pitch F1 under the frozen V154 `score_stream()` matching contract, through a future prospectively frozen new-song adapter if required.
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
- `docs/checkpoints/V154_REFERENCE_SET_FROZEN_20260827.md` confirms the one repository professional reference set is **Lenny Kravitz — Are You Gonna Go My Way** with Rhythm + Lead + Bass components.
- `research/v154-professional-references/scorer-ready/` is the same song/reference lane.
- Repository inventory/searches found no independent second-song professional scorer-ready reference.
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
- No per-event reference choices, direct reference-event copying, post-score mutation, retuning, or adverse-result song exclusion.
- Public repo may retain non-secret hashes/manifests/provenance labels/aggregate results; private/restricted reference bytes remain under their applicable storage boundary.
- CPU only; fresh explicit authorization immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — RESOLVE EGSET12 PROVENANCE OR KEEP HOLDOUT BLOCKED
1. **Do not score.**
2. Search EGSet12 authors' public repository history/issues/releases and authoritative release metadata for the provenance of `jams_corrected`, including any alignment/correction procedure and whether corrected annotation bytes are publicly obtainable/frozen.
3. Resolve authoritative rights/use-basis for the exact source-audio and reference artifacts; do not rely solely on secondary license summaries.
4. Do not admit the public Zenodo JAMS as professional ground truth unless the correction/provenance issue is resolved prospectively.
5. If EGSet12 cannot clear the frozen gates, keep it blocked and continue candidate acquisition; do not weaken `professional_scorer_ready` semantics.
6. Do not implement candidate generation or a generic V168 scorer adapter until a complete >=2-song manifest has passed BOTH frozen validators.
7. Save `CURRENT_STATE.md` before any future asset admission or code arm.
8. CPU only; no GPU/CUDA/Modal; never modify main/Production.
