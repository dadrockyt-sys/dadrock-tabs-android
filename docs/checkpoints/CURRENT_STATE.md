# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V168 is now the active research phase, status `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 is CLOSED / TERMINAL and must not be reopened for another Lenny Kravitz calibration sweep. The repository currently has only one professional reference set, and its frozen identity checkpoint confirms Rhythm + Lead + Bass all belong to Lenny Kravitz — Are You Gonna Go My Way. No genuinely independent second-song scorer-ready reference was found in the repository inventory. Therefore V168 has exactly 0 score calls and no scorer workflow may be armed yet. A prospective two-policy cross-song evaluation protocol is now frozen in `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`. `main`/Production remain untouched; CPU only; fresh authorization required before any GPU/CUDA/Modal.**

## V168 preregistration — FROZEN BEFORE ANY HOLDOUT EXISTS
- Preregistration file: `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`.
- Creation commit: `64d724e816808aa60d766923bb1a9ce241e89e89`.
- Git blob: `3a72db20d4ebebf8e4a25f5c37125e1a40934047`.
- Status: **HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED**.
- V168 reference-facing score-call count: **0**.
- Scientific objective: evaluate whether a fixed recovery policy learned during V167 generalizes to genuinely independent songs; do not continue optimizing the calibration song.

### Frozen V168 policies
Exactly two policies may eventually be compared. No additional variant may be added after holdout admission/reference access.

**Policy A — `v168-baseline-i005-policy`**
- General policy represented by promoted V167 I005 / `gss-active-only`.
- Frozen settings: active Basic Pitch context required; `fundamentalPresent`; rank >=0.975; activity >=0.05; onset >=0.50; candidate/max-active template-score ratio >=1.00; reject nearest different active intervals {12,19,24}; top1/site; Guitar cap6; inactive branch disabled.
- These are frozen calibration choices and may not be retuned on holdout.

**Policy B — `v168-gap1-earliest-policy`**
- Apply exact Policy A recovery stream, then group recovery additions by MIDI and collapse connected components whose consecutive grid-step gaps are <=1 to their earliest addition; singleton additions stay unchanged.
- This is the fixed terminal V167 challenger. No onset/activity/score tie-break and no holdout-driven mutation.

The Lenny I005 and recurrence JSON files are song-specific evidence, not holdout candidates. On any future admitted song, both policies must be regenerated reference-blind from that song's frontend/evidence using these frozen policy definitions.

## Holdout admission gate — HARD BLOCK
Do not arm V168 scoring until ALL are true:
1. At least **two genuinely independent songs** are frozen as holdout assets.
2. Each song is different from `Are You Gonna Go My Way`; different artists preferred when practical.
3. Each has frozen source-audio identity plus professional scorer-ready combined-Guitar reference identity.
4. Reference identities/hashes and uncertainty annotations are frozen before scoring.
5. Candidate generation cannot access professional reference note/event content.
6. Policy A and B complete outputs and hashes are frozen for every song before any professional reference is opened by scorer.
7. One global holdout manifest is frozen before the first V168 score call.
8. With fewer than two valid independent songs, status remains `HOLDOUT_ASSET_MISSING` and score calls remain **0**.

## V168 prospective evaluation rule
- Primary endpoint: combined-Guitar primary timing-aware pitch F1 under the frozen V154 scorer contract, if admitted references satisfy that contract.
- Aggregate by equal-weight macro average across admitted holdout songs.
- Policy B passes the V168 generalization gate only if ALL are true:
  - macro F1 >= Policy A + **0.10 percentage points**;
  - macro precision >= Policy A;
  - no individual holdout song loses > **0.25 percentage points F1** vs Policy A;
  - at least 2 independent songs are scored;
  - no holdout-driven retuning, song exclusion for unfavorable score, variant addition, or post-score mutation occurred.
- Tie/inconclusive -> retain Policy A / report `HOLDOUT_INSUFFICIENT`; do not add a tie-break variant after seeing scores.
- A V168 pass does not itself modify main/Production.

## Repository holdout inventory — COMPLETE ENOUGH TO BLOCK SCORING
- Existing frozen professional reference checkpoint `docs/checkpoints/V154_REFERENCE_SET_FROZEN_20260827.md` explicitly identifies the single reference set as **Lenny Kravitz — Are You Gonna Go My Way**.
- `research/v154-professional-references/scorer-ready/` contains Rhythm/Lead/Bass scorer-ready components for that same song, including `frontend-reference-payload.json`.
- Repository searches before V168 preregistration found no independent second-song asset under: holdout reference, professional reference, ground truth, golden reference, reference MIDI, benchmark reference, expected transcription, `reference.json`, or `reference-payload.json` beyond the existing Lenny lane.
- Therefore no present repository asset qualifies as cross-song holdout. Do not relabel Rhythm/Lead/Bass components or another Lenny-derived artifact as independent evaluation data.

## V167 terminal handoff — immutable
- V167 is closed; no further V167 reference-facing sweeps.
- Current promoted iteration remains I005 `gss-active-only`:
  - Guitar F1 **42.7940586109996%**, P48.54280510018215%, R38.26274228284279%; 533/1098/1393; FP565/FN860.
  - I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
  - Bass F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.
- Highest scored but unpromoted terminal calibration candidate `recur-gap1-earliest`:
  - Guitar F1 **42.88012872083669%**, P48.76486733760293%, R38.26274228284279%; 533/1093/1393; FP560/FN860.
  - Delta vs I005 +0.08607010983709418pp F1; FP -5; matched/recall unchanged.
  - SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`.
  - Did NOT clear frozen +0.10pp I006 promotion gate; no I006 exists and gate may not be weakened after result.
- V167 closure checkpoint commit `cef3d57baf346e1f01faad19bb0998d602e86386` remains the terminal single-song research handoff.

## Standing methodology / safety
- V168 is prospective evaluation, not another single-song calibration sweep.
- Professional reference content cannot be read by candidate generation/policy code.
- Freeze candidate outputs before reference scoring.
- No per-event reference choices, direct reference-event copying, post-score mutation, or retuning.
- No holdout song may be dropped because its result is unfavorable.
- Public repo may retain hashes/manifests/aggregate results; private reference bytes stay subject to existing storage boundary.
- Frozen V154 scorer blob expected for future compatible holdout: `9644e65719fbd361a9b39778ae9950c5e983e855`.
- CPU-only work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — HOLDOUT ASSET ACQUISITION ONLY
1. **Do not score anything now.**
2. Acquire/freeze at least two genuinely independent professional-reference songs and source-audio identities.
3. Do not inspect/use their note-event content to alter Policy A/B.
4. Record admitted song/reference identities in a V168 holdout manifest while preserving this preregistration unchanged.
5. Only after the minimum two-song admission gate is satisfied: implement/freeze exactly the two policy modules if needed, generate both candidates per song reference-blind, freeze all hashes/global manifest, checkpoint, then arm a separate one-shot scorer.
6. If independent assets are unavailable, remain blocked; do not substitute Lenny components or synthetic self-reference as holdout.
7. Save this checkpoint before any future V168 asset admission or code arm.
