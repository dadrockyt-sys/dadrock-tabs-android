# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 remains the frozen/promoted current iteration (`gss-active-only`, Guitar 42.7940586109996% F1; Bass 80.45325779036827% F1), and no I006 exists. The temporal/recurrence family is terminal/frozen. Its highest scored calibration candidate `recur-gap1-earliest` reached **42.88012872083669% Guitar F1** (+0.08607010983709418pp vs I005) but did not meet the preregistered +0.10pp I006 promotion threshold. A new, structurally distinct post-recurrence phrase/metrical consistency analyzer is now staged and unrun. It selects no rule and reads no professional reference/scorer/per-event match assignments. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — POST-RECURRENCE PHRASE ANALYZER STAGED / NOT RUN
- Analyzer `validation/v167_single_song_calibration/analyze_post_recurrence_phrase_consistency_v167.py`: commit `14a2511e4f51a56dea98b8a099eacb45936e6792`, blob `5e5003e87ad7619e4ce352cbc60608db197e3690`.
- Analysis is deliberately distinct from the closed same-MIDI gap1/gap2 burst family. It measures only:
  - step-within-measure / MIDI-phase recurrence,
  - immutable-I003 same-MIDI/same-phase support,
  - exact local immutable-I003 riff-context repetition within +/-4 grid steps,
  - pitch-relative local immutable-I003 riff-context repetition within +/-4 grid steps.
- It reads only immutable I003/I005, terminal aggregate recurrence report, and frozen temporal structural diagnosis.
- It accepts no professional-reference or scorer input, performs 0 new score calls, reads no per-event reference assignments, infers no individual event correctness, and sets `newRuleSelectedByThisAnalysis=false`.
- The recurrence aggregate outcome may be read only as a whole-rule fact: `recur-gap1-earliest` preserved all 533 matches and removed 5 generated/FP events; no individual burst event may be labeled true/false from that result.
- No new family is preregistered yet. If phrase/metrical structure is weak or broad rather than sparse/distinct, close V167 instead of forcing another sweep.

## Terminal recurrence sweep — CLOSED / NO I006
- Scoring arm `ff1ba9f5f8d820d93b786c8adaddbd3b7160010c`; run `33266492124`, job `99137355639`; terminal self-removing commit `4ad6d7e24db005708a51639a4b7d50056c686f58`.
- Report blob `1d31573afc5d4774a6022b9438088577232e63c6`, SHA256 `800e9dbcd8565b32d2015ba6cc97a142c91dbf1c3b76f39f96818b3f4c735382`.
- Receipt blob `25deb1f553959cdf2e965216019480dfabf4bb10`, status `TEMPORAL_RECURRENCE_GUITAR_SWEEP_FROZEN`.
- Exact score boundary: Guitar 3 / Bass 0 / reproduction 0. No mutation, retuning, I006, GPU, main/Production modification, or generalization claim.
- `newVariantsBeatingI005=1`; `newVariantsMeetingPromotionEligibility=0`.

### `recur-gap1-earliest` — highest scored calibration candidate, not promoted
- F1 **42.88012872083669%**; P **48.76486733760293%**; R **38.26274228284279%**.
- 533 matched / 1093 generated / 1393 reference; FP560/FN860.
- Delta vs I005: F1 **+0.08607010983709418pp**; precision +0.22206223742077813pp; recall 0; matched 0; generated -5; FP -5; FN 0.
- Candidate SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`, blob `13f2613403b82d45ce5fc5c18da26e66dd04e886`.
- `eligibleForSeparateNoRescoreIteration006Promotion=false`; do not weaken the frozen +0.10pp promotion gate.

### Other recurrence rules
- `recur-gap1-strongest`: F1 42.719227674979886%; matched531/generated1093/FP562/FN862; delta -0.07483093601970969pp F1.
- `recur-gap2-strongest`: F1 42.60974627466774%; matched529/generated1090/FP561/FN864; delta -0.1843123363318544pp F1.
- Recurrence family is terminal. Do not score more gap thresholds, selectors, or subsets after seeing these outcomes.

## Frozen recurrence provenance
- Corrected generator blob `2f90e7a8b3e07ae59856f67cf0d299094f482d94`; grader blob `e8251df48d03e94a2d53060bc1e82b4e9d5ba4f7`.
- Generation arm `b551be770b699c4d0f3c1079796f4d9f3bcffbc2`; run `33266423759`, job `99137178880`; terminal generation commit `35548f025841ee459d00f43ea7db1133634a6be4`.
- Generation receipt blob `72dd00101541c8bd63f2271c4cea514f63cdbb3c`; manifest blob `76077bdbad3e519a09e3105633bc14b8aedb1fe9`, SHA256 `5e0eaedcf3e78e3b0c4213004a51cc04d935418315f0a281708e36d637b21ed5`.
- Frozen recurrence candidates: repro SHA `ba95511e2a92fa00a5bb335ec7913ea8f8b7559a583fc49874ee8159ea535f19`; gap1-earliest `a72ce501...c4dbe`; gap1-strongest `0092a24e...3f49`; gap2-strongest `01276897...228b`.

## Iteration 005 — FROZEN CURRENT PROMOTED ITERATION
- Guitar `gss-active-only`: F1 **42.7940586109996%**, P48.54280510018215%, R38.26274228284279%; 533/1098/1393; FP565/FN860.
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass closed: F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.
- I005 remains current promoted iteration; the unpromoted recurrence high is not I006.

## Other closed family
- Active-topology terminal report blob `4aab67d913b4b68cc518825d4495a48c3b9e76fc`, SHA256 `869825ed2a91e9f50bc6ca5ac71d922ee93dc17dd5804bf8d94d0e951e179b85`; 3 Guitar/0 Bass/0 repro; no I006 eligibility.

## Standing V167 methodology
- Calibration only; no holdout/generalization claim.
- I003/I004/I005 and terminal sweeps immutable.
- No per-event reference choices, direct reference-event copying, post-score mutation, or post-score retuning.
- Frozen promotion gates may not be weakened after results.
- Bass closed. CPU authorized; fresh explicit authorization required before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — run phrase/metrical diagnosis reference-blind
1. Arm a one-shot self-removing analysis workflow from this exact checkpoint parent.
2. Verify analyzer blob `5e5003e87ad7619e4ce352cbc60608db197e3690`, immutable I003/I005, terminal recurrence report SHA `800e9dbc...5382`, and frozen temporal diagnosis SHA `fd5c1233...1b36`.
3. Analyzer/workflow must contain no professional-reference/scorer path; perform 0 score calls.
4. Freeze analysis + receipt and self-remove workflow.
5. Read only aggregate/structural findings. Do not infer which specific burst events were reference-correct.
6. Save terminal diagnosis to checkpoint. Only preregister a new family if a genuinely distinct sparse phrase/metrical structure is naturally supported; otherwise explicitly close V167.
7. CPU only; no GPU/CUDA/Modal; never modify main/Production.
