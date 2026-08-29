# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 remains the frozen/promoted current iteration (`gss-active-only`, Guitar 42.7940586109996% F1; Bass 80.45325779036827% F1), and no I006 exists. The temporal/recurrence family is now terminal/frozen. It found a new highest *scored calibration candidate*, `recur-gap1-earliest`, at **42.88012872083669% Guitar F1** by removing 5 false positives with zero loss of matches/recall, but its **+0.08607010983709418pp** F1 gain is below the preregistered **+0.10pp** I006 promotion threshold. Therefore it is explicitly NOT promotion-eligible and must not become I006. Active-topology and recurrence families are both closed; no post-score retuning is allowed. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — RECURRENCE SWEEP TERMINAL / NO I006
- Scoring arm commit `ff1ba9f5f8d820d93b786c8adaddbd3b7160010c`.
- Workflow run `33266492124`, job `99137355639`, attempt 1; exact frozen pre-reference gate passed, exactly 3 Guitar whole-rule scores completed, then receipt/self-seal passed.
- Terminal self-removing commit `4ad6d7e24db005708a51639a4b7d50056c686f58`.
- Terminal report `debug/v167-single-song-calibration/temporal-recurrence-guitar-sweep.json`: blob `1d31573afc5d4774a6022b9438088577232e63c6`, SHA256 `800e9dbcd8565b32d2015ba6cc97a142c91dbf1c3b76f39f96818b3f4c735382`.
- Terminal receipt `debug/v167-single-song-calibration/temporal-recurrence-guitar-sweep-receipt.json`: blob `25deb1f553959cdf2e965216019480dfabf4bb10`, status `TEMPORAL_RECURRENCE_GUITAR_SWEEP_FROZEN`.
- Scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`; professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Score-call boundary held exactly: Guitar **3**, Bass **0**, reproduction control **0**.
- `newVariantsBeatingI005=1`; `newVariantsMeetingPromotionEligibility=0`.
- Policy held: all candidates frozen before reference read=true; individual event selection by reference=false; post-score mutation=false; post-score retuning=false; I006 created=false; Bass scored=false; reproduction scored=false; GPU/CUDA/Modal=false; main/Production=false; generalization claim=false.

## Terminal recurrence results — CLOSED FAMILY
### `recur-gap1-earliest` — highest scored calibration candidate, NOT promotion-eligible
- Guitar F1 **42.88012872083669%**; precision **48.76486733760293%**; recall **38.26274228284279%**.
- 533 matched / 1093 generated / 1393 reference; FP **560**; FN **860**.
- Delta vs frozen I005: F1 **+0.08607010983709418pp**; precision **+0.22206223742077813pp**; recall **0.0pp**; matched **0**; generated **-5**; FP **-5**; FN **0**.
- Candidate SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`; blob `13f2613403b82d45ce5fc5c18da26e66dd04e886`.
- Keeps 43/48 I005 additions; collapses the four preregistered same-MIDI gap<=1 bursts to their earliest event.
- This candidate **beats I005 numerically** but `eligibleForSeparateNoRescoreIteration006Promotion=false` because +0.08607pp < the frozen +0.10pp gate. Do not weaken/change the promotion gate after seeing the score.

### `recur-gap1-strongest` — negative
- Guitar F1 **42.719227674979886%**; precision **48.58188472095151%**; recall **38.11916726489591%**.
- 531 matched / 1093 generated; FP562/FN862.
- Delta vs I005: F1 **-0.07483093601970969pp**; precision **+0.03907962076935556pp**; recall **-0.14357501794687866pp**; matched -2; generated -5; FP -3; FN +2.
- Candidate SHA256 `0092a24e36ae8857a531dba254764d431811133d6d23df318615202557c13f49`.

### `recur-gap2-strongest` — negative
- Guitar F1 **42.60974627466774%**; precision **48.53211009174312%**; recall **37.97559224694903%**.
- 529 matched / 1090 generated; FP561/FN864.
- Delta vs I005: F1 **-0.1843123363318544pp**; precision **-0.01069500843903226pp**; recall **-0.2871500358937573pp**; matched -4; generated -8; FP -4; FN +4.
- Candidate SHA256 `012768977ba5f06036c04d25462e5ac47e45f4fa44e0672861f113e3fb21228b`.

## Frozen recurrence generation provenance
- Corrected generator blob `2f90e7a8b3e07ae59856f67cf0d299094f482d94`; grader blob `e8251df48d03e94a2d53060bc1e82b4e9d5ba4f7`.
- Successful generation arm `b551be770b699c4d0f3c1079796f4d9f3bcffbc2`; run `33266423759`, job `99137178880`; terminal generation commit `35548f025841ee459d00f43ea7db1133634a6be4`.
- Generation receipt blob `72dd00101541c8bd63f2271c4cea514f63cdbb3c`, status `TEMPORAL_RECURRENCE_VARIANTS_FROZEN_BEFORE_SCORING`.
- Manifest blob `76077bdbad3e519a09e3105633bc14b8aedb1fe9`, SHA256 `5e0eaedcf3e78e3b0c4213004a51cc04d935418315f0a281708e36d637b21ed5`.
- Reproduction control `recur-repro-i005`: SHA256 `ba95511e2a92fa00a5bb335ec7913ea8f8b7559a583fc49874ee8159ea535f19`; exact I005; 0 score calls.

## Safe failed recurrence-generation attempt — historical only
- First generation arm `702fd02e7ad259eaf273b9e124cb114f77b84c5e`; run `33266334501`, job `99136937952`.
- Reference-blind guard passed; generation failed before frozen output because analysis JSON has no top-level status; freeze status lives in receipt.
- Corrected generator commit `1ceb917e5ed4611092d3a8bf6bf738850bab6859`; no rule/selector/count changed; failed attempt made 0 reference/scorer calls and committed no candidates.

## Iteration 005 — FROZEN CURRENT PROMOTED ITERATION
- Guitar `gss-active-only`: F1 **42.7940586109996%**, P **48.54280510018215%**, R **38.26274228284279%**; 533/1098/1393; FP565/FN860.
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass closed: F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.
- I005 remains the current frozen/promoted iteration because the new recurrence high did not clear its preregistered promotion gate. Do not call the unpromoted recurrence candidate I006.

## Closed families
- Active-topology sweep: terminal negative; report blob `4aab67d913b4b68cc518825d4495a48c3b9e76fc`, SHA256 `869825ed2a91e9f50bc6ca5ac71d922ee93dc17dd5804bf8d94d0e951e179b85`; 3 Guitar /0 Bass /0 repro; no I006 eligibility.
- Temporal/recurrence sweep: terminal; one numeric improvement (`recur-gap1-earliest`) but below promotion gate. **Do not retune/extend the same gap1/gap2 burst-collapse family after seeing scores.**

## Standing V167 methodology
- Calibration only; no holdout/generalization claim.
- I003/I004/I005 and terminal sweeps immutable.
- No per-event reference choices, direct reference-event copying, post-score mutation, or post-score retuning.
- Promotion gates are frozen prospectively and may not be weakened after results.
- Bass closed. CPU authorized; fresh explicit authorization required before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — reference-blind post-recurrence diagnosis only
1. Treat the temporal/recurrence family as terminal. Do not score another gap threshold, burst selector, or subset of the same four burst components.
2. Perform a new **reference-blind / aggregate-only** diagnosis using immutable generated candidates, the frozen recurrence aggregate report, prior frozen structural analyses, and I003/I005 structure. Do not read per-event reference match assignments and do not run scorer/reference calls.
3. Explain structurally why the family outcome is informative without labeling any individual pruned/kept event true/false. The key aggregate observation is that earliest gap1 preserved all 533 matches while removing 5 generated events/FPs, whereas strongest gap1 lost 2 matches despite the same generated count.
4. Search only for a **genuinely distinct structural dimension** if one is naturally supported (for example phrase-position/repetition consistency or another reference-blind musical-context feature); do not derive a new selector from which specific earliest/strongest events scored correctly.
5. Save the diagnosis and checkpoint before preregistering any new family. If no distinct defensible family emerges, explicitly close V167 rather than forcing another sweep.
6. CPU only; no GPU/CUDA/Modal; never modify main/Production.
