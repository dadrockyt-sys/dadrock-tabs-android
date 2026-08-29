# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 remains frozen current best: Guitar `gss-active-only` **42.7940586109996% F1**, Bass **80.45325779036827% F1**. The active-topology family is terminal negative/closed and no I006 exists. The temporal/recurrence family is now fully generated and frozen before scoring. All four candidate hashes, the manifest, and the generation receipt are committed; the generation workflow self-removed. No recurrence candidate has been scored yet. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — RECURRENCE CANDIDATES FROZEN / SCORING NOT YET ARMED
- Corrected generator `validation/v167_single_song_calibration/build_temporal_recurrence_guitar_variants_v167.py`: commit `1ceb917e5ed4611092d3a8bf6bf738850bab6859`, blob `2f90e7a8b3e07ae59856f67cf0d299094f482d94`.
- Grader `validation/v167_single_song_calibration/score_temporal_recurrence_guitar_variants_v167.py`: blob `e8251df48d03e94a2d53060bc1e82b4e9d5ba4f7`.
- Successful corrected generation arm `b551be770b699c4d0f3c1079796f4d9f3bcffbc2`; run `33266423759`, job `99137178880`; terminal self-removing commit `35548f025841ee459d00f43ea7db1133634a6be4`.
- Generation receipt `debug/v167-single-song-calibration/temporal-recurrence-generation-receipt.json`: blob `72dd00101541c8bd63f2271c4cea514f63cdbb3c`, status `TEMPORAL_RECURRENCE_VARIANTS_FROZEN_BEFORE_SCORING`.
- Manifest blob `76077bdbad3e519a09e3105633bc14b8aedb1fe9`, SHA256 `5e0eaedcf3e78e3b0c4213004a51cc04d935418315f0a281708e36d637b21ed5`.
- Generation policy: professional reference read=false; scorer read=false; new reference-facing calls=0; Bass scored=false; reproduction scored=false; all candidate hashes frozen before scoring=true.

### Frozen recurrence candidates
- `recur-repro-i005`: 48 additions / 1098 Guitar; blob `73e5ef69a58d42ac511fe16b3c9da8c1060c8002`; SHA256 `ba95511e2a92fa00a5bb335ec7913ea8f8b7559a583fc49874ee8159ea535f19`; exact no-score I005 reproduction control.
- `recur-gap1-earliest`: 43 additions / 1093 Guitar; blob `13f2613403b82d45ce5fc5c18da26e66dd04e886`; SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`; collapses 4 gap1 burst components / 9 burst events / 5 pruned.
- `recur-gap1-strongest`: 43 additions / 1093 Guitar; blob `7299ef6d1d31e8157a7a0d7e9d9169aa279fb86b`; SHA256 `0092a24e36ae8857a531dba254764d431811133d6d23df318615202557c13f49`; same four gap1 components, strongest frozen evidence selector.
- `recur-gap2-strongest`: 40 additions / 1090 Guitar; blob `10322fcadf4081a833795a03a2deadee33f3cfa6`; SHA256 `012768977ba5f06036c04d25462e5ac47e45f4fa44e0672861f113e3fb21228b`; collapses 6 gap2 components / 14 burst events / 8 pruned.
- Bass count is 512 for every candidate and is fixed exactly to I005.

## Safe failed generation attempt — historical only
- First generation arm `702fd02e7ad259eaf273b9e124cb114f77b84c5e`; run `33266334501`, job `99136937952`.
- Reference-blind guard passed; generation failed before outputs because the analysis JSON has no top-level `status`. Freeze status lives in its receipt.
- No candidate/manifest/receipt was committed by that failed attempt; 0 scorer/reference calls. Corrected generator validates immutable SHA + schema + policy + `additionCount=48` instead. No rule changed.

## Temporal/recurrence diagnosis — FROZEN / TERMINAL
- Analysis blob `42a4d4bd9c016b5aee74a14eea4b78fb601a6b6e`, SHA256 `fd5c12339e594ae1207e2c4edb2eb034a9249de15ab99d3623cf5f6922061b36`, schema `dadrock.tabs.v167.post-topology-temporal-recurrence-analysis.v1`.
- Receipt blob `baefc8c8a9fdceb6a53ac3b1e3838210a19c01c4`, status `POST_TOPOLOGY_TEMPORAL_RECURRENCE_ANALYSIS_FROZEN`.
- Frozen structure: gap1 same-MIDI bursts prune exactly 5 of 48; gap2 prune exactly 8. `strongest_evidence` = max onset, then activity, then earlier step; no reference outcome input.

## Recurrence scoring boundary — preregistered
- Score exactly the three new Guitar whole rules: `recur-gap1-earliest`, `recur-gap1-strongest`, `recur-gap2-strongest`.
- Score calls: Guitar **3**, Bass **0**, reproduction **0**.
- Pre-reference gate must verify manifest SHA/blob, generation receipt, every committed candidate SHA, exact I005 reproduction equality, and Bass equality before scorer import/reference open.
- Selection: max Guitar F1, then precision, fewer kept additions, lexicographic id.
- Scorer workflow cannot create I006 or mutate candidates after scoring.
- Separate I006 eligibility only if best new rule gains **>=+0.10pp F1 vs I005** and precision **>= I005**.

## Active-topology sweep — CLOSED
- Terminal report blob `4aab67d913b4b68cc518825d4495a48c3b9e76fc`, SHA256 `869825ed2a91e9f50bc6ca5ac71d922ee93dc17dd5804bf8d94d0e951e179b85`.
- 3 Guitar calls / 0 Bass / 0 reproduction; none beat I005; 0 I006-eligible. Do not retune/extend topology subsets.

## Iteration 005 — FROZEN CURRENT BEST
- Guitar: F1 **42.7940586109996%**, P **48.54280510018215%**, R **38.26274228284279%**; 533/1098/1393; FP565/FN860.
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass closed: F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.

## Standing V167 methodology
- Calibration only; no holdout/generalization claim.
- I003/I004/I005 and terminal sweeps immutable.
- No per-event reference choices, direct reference-event copying, or post-score retuning.
- Bass closed. CPU authorized; fresh explicit authorization required before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — score frozen recurrence candidates
1. Arm a new self-removing scorer workflow from this exact checkpoint parent only.
2. Use frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855` and frozen reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5` / SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
3. Before reference read, verify manifest blob/SHA, receipt blob, grader blob, all four candidate blobs/SHAs, exact reproduction equality, and Bass equality.
4. Run exactly 3 Guitar score calls; 0 Bass; 0 reproduction. No candidate mutation, retuning, or I006 creation.
5. Freeze report + scoring receipt and remove scorer workflow.
6. Checkpoint terminal recurrence result. Only if a new winner passes separate eligibility should a no-rescore I006 promotion be considered.
7. CPU only; no GPU/CUDA/Modal; never modify main/Production.
