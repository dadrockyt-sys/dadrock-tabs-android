# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V168 is active with status `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 is CLOSED / TERMINAL and must not be reopened for another Lenny Kravitz calibration sweep. The repository still has only one professional scorer-ready reference set, all for Lenny Kravitz — Are You Gonna Go My Way; prior project history contains many other song lessons/transcriptions but no separate frozen professional scorer-ready ground-truth set was identified. Therefore V168 remains at exactly 0 score calls. The prospective two-policy protocol and a hard holdout-asset admission validator are now frozen before any future holdout is admitted. `main`/Production remain untouched; CPU only; fresh authorization required before GPU/CUDA/Modal.**

## V168 preregistration — FROZEN
- `docs/checkpoints/V168_HOLDOUT_PREREGISTRATION_20260829.md`
- Commit `64d724e816808aa60d766923bb1a9ce241e89e89`; blob `3a72db20d4ebebf8e4a25f5c37125e1a40934047`.
- Status **HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED**.
- V168 reference-facing score calls: **0**.
- Objective: cross-song generalization comparison only; do not continue tuning the V167 calibration song.

### Frozen policies
**Policy A — `v168-baseline-i005-policy`**
- V167 I005 / `gss-active-only` policy with fixed calibration settings: active Basic Pitch context, `fundamentalPresent`, rank>=0.975, activity>=0.05, onset>=0.50, candidate/max-active score ratio>=1.00, reject nearest different active intervals {12,19,24}, top1/site, Guitar cap6, inactive branch off.

**Policy B — `v168-gap1-earliest-policy`**
- Exact Policy A stream, then same-MIDI connected components with consecutive grid gaps<=1 collapse to earliest event; singletons unchanged.
- No holdout-driven selector/threshold mutation.

Song-specific Lenny candidate JSONs are not holdout candidates. For future admitted songs, both policies must be regenerated from reference-blind frontend/evidence using the fixed definitions.

## V168 holdout asset admission validator — FROZEN
- Validator `validation/v168_holdout/validate_holdout_asset_manifest_v168.py`.
- Creation commit `283f055ddc399deb8d4b8ec8d0cd34f65b68c9f7`.
- Git blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`.
- This validator has no audio/reference-event/scorer access and cannot score anything.
- Frozen manifest schema: `dadrock.tabs.v168.holdout-asset-manifest.v1`.
- Hard minimum: **2** independent songs.
- Hard calibration exclusion: song id/title cannot be Lenny Kravitz — Are You Gonna Go My Way.
- Hard policy list: exactly `v168-baseline-i005-policy`, `v168-gap1-earliest-policy`.
- Each admitted song must have:
  - unique song id;
  - frozen unique source-audio SHA256 identity;
  - frozen unique professional-reference SHA256 identity;
  - `professionalReference.kind=professional_scorer_ready`;
  - combined Guitar coverage=true;
  - uncertainty annotations frozen=true;
  - candidate generation may read reference note events=false;
  - reference frozen before candidate scoring=true;
  - independence from V167 calibration song=true;
  - admission decision made without comparative scores=true.
- Global boundary requires reference-facing scoring unarmed, comparative scores unread before admission freeze, V168 score calls before asset freeze=0, main/Production=false, GPU/CUDA/Modal=false.
- Duplicate song/source/reference identities are rejected.

## Holdout admission gate — HARD BLOCK
No V168 scorer workflow may be armed until:
1. >=2 genuinely independent songs validate through the frozen admission contract.
2. Each is different from `Are You Gonna Go My Way`; different artists preferred where practical.
3. Each has frozen source audio + professional scorer-ready combined-Guitar reference identity.
4. Candidate generation cannot access professional-reference event content.
5. Policy A/B outputs for every admitted song are generated reference-blind and fully hash-frozen before scorer/reference access.
6. A global candidate-freeze manifest is committed before first V168 score call.
7. If fewer than 2 valid songs exist, remain `HOLDOUT_ASSET_MISSING` and score calls remain **0**.

## V168 prospective evaluation rule
- Primary: combined-Guitar primary timing-aware pitch F1 under frozen V154 scorer contract if compatible.
- Equal-weight macro average across admitted holdout songs.
- Policy B passes only if ALL:
  - macro F1 >= Policy A + **0.10pp**;
  - macro precision >= Policy A;
  - no individual holdout song loses > **0.25pp F1** vs Policy A;
  - >=2 independent songs scored;
  - no holdout-driven retuning, adverse-result song exclusion, variant addition, or post-score mutation.
- Tie/inconclusive -> retain Policy A / `HOLDOUT_INSUFFICIENT`; do not add variants after seeing scores.
- Any V168 pass is research evidence only; it does not modify main/Production.

## Holdout inventory result
- `docs/checkpoints/V154_REFERENCE_SET_FROZEN_20260827.md` confirms the one professional reference set is **Lenny Kravitz — Are You Gonna Go My Way** with Rhythm + Lead + Bass components.
- `research/v154-professional-references/scorer-ready/` is the same song/reference lane.
- Repo searches found no independent second-song professional scorer-ready reference under holdout/professional-reference/ground-truth/golden/reference-MIDI/benchmark/expected/reference-filename searches.
- Prior project context contains numerous non-Lenny DadRock lesson/transcription songs, but no separate frozen professional scorer-ready ground-truth reference was found. Do not promote ordinary lesson/tab assets to holdout ground truth by assumption.

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
- No per-event reference choices, direct reference-event copying, post-score mutation, or retuning.
- No holdout song may be dropped for unfavorable outcome.
- Public repo may retain hashes/manifests/aggregate results; private reference bytes remain under existing storage boundary.
- Expected frozen scorer for compatible future references: blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- CPU only; fresh explicit authorization immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — EXTERNAL HOLDOUT ASSET ACQUISITION / ADMISSION
1. **Do not score now.**
2. Acquire/freeze at least two genuinely independent professional combined-Guitar reference songs and matching source-audio identities.
3. Build the holdout asset manifest using schema `dadrock.tabs.v168.holdout-asset-manifest.v1` and validate it with frozen validator blob `c9e0b00f...d579`.
4. Do not use professional note/event content to modify Policy A/B.
5. Once >=2 assets validate, checkpoint their identities before implementing/arming any candidate generation or scoring workflow.
6. If assets are unavailable, remain blocked; do not substitute Lenny components, ordinary DadRock lesson tabs, or synthetic self-reference as holdout.
7. Save `CURRENT_STATE.md` before any future asset admission or code arm.
