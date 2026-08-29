# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V167 is now CLOSED / TERMINAL for this single-song calibration lane. V166 remains terminal/immutable. No I006 exists. Iteration 005 remains the frozen/promoted current iteration (`gss-active-only`, Guitar 42.7940586109996% F1; Bass 80.45325779036827% F1). The highest scored but unpromoted Guitar calibration candidate is terminal recurrence rule `recur-gap1-earliest` at **42.88012872083669% F1**, +0.08607010983709418pp vs I005, but it did not clear the preregistered +0.10pp promotion gate and therefore must not become I006. The final reference-blind phrase/metrical diagnosis found no sufficiently sparse, distinct phrase-consistency structure to justify another family: only 2/48 additions share a repeated exact/relative local I003 riff context, while same-MIDI/same-phase base support is broad (30/48). Active-topology and temporal-recurrence families remain closed and cannot be retuned after scores. `main`/Production remain untouched; no GPU/CUDA/Modal work was used.**

## TERMINAL V167 closure — DO NOT ARM ANOTHER V167 SWEEP
- Closure decision: **stop V167 rather than force another calibration family**.
- Rationale is methodology-first, not score-chasing:
  - recurrence family already terminal after reference grading;
  - final new analysis was reference-blind and selected no rule;
  - repeated phrase-context signal is extremely sparse (2/48 additions in one repeated exact context group; same result pitch-relative);
  - same-MIDI/same-phase support is broad (30/48; 25/48 have >=2 immutable I003 occurrences) and does not provide a clean sparse discriminator;
  - metrical-position histogram is diffuse across the 16-step measure grid and no phase rule was preregistered prospectively;
  - therefore another threshold/subset/phase sweep would risk post-hoc calibration rather than a genuinely new hypothesis.
- Do not weaken the frozen +0.10pp I006 promotion gate. Do not promote `recur-gap1-earliest` as I006.
- Future work, if any, must start as a **new phase/version with a prospectively defined objective**, preferably holdout/cross-song/generalization-oriented rather than another V167 single-song calibration sweep.

## Final post-recurrence phrase/metrical diagnosis — FROZEN
- Analyzer `validation/v167_single_song_calibration/analyze_post_recurrence_phrase_consistency_v167.py`: commit `14a2511e4f51a56dea98b8a099eacb45936e6792`, blob `5e5003e87ad7619e4ce352cbc60608db197e3690`.
- Analysis arm `61c4a2771b3b3f4b2c9006dfb631b0cfa2bd8a0e`; run `33266658642`, job `99137797299`; terminal self-removing commit `e2e6bc880abc0ce7a29e134f7922638a78e5d0db`.
- Analysis `debug/v167-single-song-calibration/post-recurrence-phrase-consistency-analysis.json`: blob `9e9123ab265f4addf7d619f7435d773f1159bd6c`, SHA256 `77e66e39c0b08680ea260aa5efadaaee0142d5ee7b30bd26ab8ec1db4f12c384`, status `POST_RECURRENCE_PHRASE_CONSISTENCY_REFERENCE_BLIND_ANALYSIS_FROZEN`.
- Receipt `debug/v167-single-song-calibration/post-recurrence-phrase-consistency-analysis-receipt.json`: blob `f5e7746d6368ec254c04cb3a439fcb389230f287`, status `POST_RECURRENCE_PHRASE_CONSISTENCY_ANALYSIS_FROZEN`.
- Policy: professional reference read=false; scorer read=false; new reference-facing score calls=0; per-event reference assignments=false; individual event correctness inferred=false; closed recurrence family retuned=false; new rule selected=false; GPU/CUDA/Modal=false; main/Production=false.

### Final structural findings
- Exact I005 additions analyzed: **48**.
- Immutable I003 same-MIDI/same-step-within-measure support:
  - >=1 occurrence: **30/48**.
  - >=2 occurrences: **25/48**.
  - This is broad support, not a sparse discriminator.
- Addition MIDI+metrical-phase multiplicity: **38** MIDI/phase pairs occur once; **5** occur twice. No large repeated MIDI/phase cluster exists.
- Exact immutable-I003 local context (+/-4 grid steps): multiplicity histogram = 46 singleton contexts + one group of 2; only **2/48** additions participate in a repeated exact context.
- Pitch-relative immutable-I003 local context (+/-4): same result = 46 singleton contexts + one group of 2; only **2/48** participate in a repeated relative context.
- Largest exact context group = **2**; largest relative context group = **2**.
- Metrical phase is diffuse: additions appear across all/virtually all 16 step positions; the most common position is step 6 with 9 additions, but selecting it now would be post-hoc and was not justified as a sparse repeated-riff family by the frozen context analysis.
- Aggregate recurrence outcome was read only as whole-rule evidence: earliest gap1 preserved 533 matches while removing 5 generated/FP events. No individual pruned/kept event was labeled correct or incorrect.

## Terminal temporal/recurrence sweep — CLOSED / NO I006
- Scoring arm `ff1ba9f5f8d820d93b786c8adaddbd3b7160010c`; run `33266492124`, job `99137355639`; terminal self-removing commit `4ad6d7e24db005708a51639a4b7d50056c686f58`.
- Report blob `1d31573afc5d4774a6022b9438088577232e63c6`, SHA256 `800e9dbcd8565b32d2015ba6cc97a142c91dbf1c3b76f39f96818b3f4c735382`.
- Receipt blob `25deb1f553959cdf2e965216019480dfabf4bb10`, status `TEMPORAL_RECURRENCE_GUITAR_SWEEP_FROZEN`.
- Score calls exactly Guitar 3 / Bass 0 / reproduction 0. `newVariantsBeatingI005=1`; `newVariantsMeetingPromotionEligibility=0`.

### Highest scored calibration candidate — `recur-gap1-earliest`, unpromoted
- Guitar F1 **42.88012872083669%**; precision **48.76486733760293%**; recall **38.26274228284279%**.
- 533 matched / 1093 generated / 1393 reference; FP560/FN860.
- Delta vs I005: F1 **+0.08607010983709418pp**; precision +0.22206223742077813pp; recall 0; matched 0; generated -5; FP -5; FN 0.
- Candidate SHA256 `a72ce501c6d4cdbcbbdc67370ef2b35b88ad2358921d1de90f86d7f5af4c4dbe`, blob `13f2613403b82d45ce5fc5c18da26e66dd04e886`.
- `eligibleForSeparateNoRescoreIteration006Promotion=false`.

### Other terminal recurrence rules
- `recur-gap1-strongest`: F1 42.719227674979886%; matched531/generated1093/FP562/FN862; delta -0.07483093601970969pp F1.
- `recur-gap2-strongest`: F1 42.60974627466774%; matched529/generated1090/FP561/FN864; delta -0.1843123363318544pp F1.
- Do not extend gap thresholds, selectors, or subsets.

## Recurrence generation provenance
- Corrected generator blob `2f90e7a8b3e07ae59856f67cf0d299094f482d94`; grader blob `e8251df48d03e94a2d53060bc1e82b4e9d5ba4f7`.
- Generation arm `b551be770b699c4d0f3c1079796f4d9f3bcffbc2`; run `33266423759`, job `99137178880`; terminal generation commit `35548f025841ee459d00f43ea7db1133634a6be4`.
- Generation receipt blob `72dd00101541c8bd63f2271c4cea514f63cdbb3c`; manifest blob `76077bdbad3e519a09e3105633bc14b8aedb1fe9`, SHA256 `5e0eaedcf3e78e3b0c4213004a51cc04d935418315f0a281708e36d637b21ed5`.

## Iteration 005 — FROZEN CURRENT PROMOTED ITERATION
- Guitar `gss-active-only`: F1 **42.7940586109996%**, P48.54280510018215%, R38.26274228284279%; 533/1098/1393; FP565/FN860.
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass closed: F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.
- I005 remains the current promoted iteration. There is no I006.

## Other closed family
- Active-topology terminal report blob `4aab67d913b4b68cc518825d4495a48c3b9e76fc`, SHA256 `869825ed2a91e9f50bc6ca5ac71d922ee93dc17dd5804bf8d94d0e951e179b85`; 3 Guitar/0 Bass/0 repro; no I006 eligibility.

## Standing methodology / handoff rules
- V167 is terminal. Do not arm another V167 reference-facing sweep from this checkpoint.
- Calibration scores are not holdout/generalization evidence.
- I003/I004/I005 and all terminal V167 reports/receipts are immutable.
- No per-event reference choices, direct reference-event copying, post-score mutation, or post-score retuning.
- Frozen promotion gates may not be weakened after results.
- Bass closed. CPU-only work was used; fresh explicit authorization required before any GPU/CUDA/Modal work.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — new phase only, if continued
1. Do **not** continue V167 single-song reference-guided calibration.
2. If research continues, create a new explicit phase/version with a prospectively written objective and immutable starting point.
3. Prefer cross-song/holdout validation or generalization-focused work so gains are no longer selected solely on this one calibration song.
4. Preserve I005 as current promoted iteration and `recur-gap1-earliest` as an unpromoted terminal calibration finding.
5. Save a new checkpoint before any new phase is armed.
6. CPU only unless fresh GPU/CUDA/Modal authorization is explicitly provided; never modify main/Production.
