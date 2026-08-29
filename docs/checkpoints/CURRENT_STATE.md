# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 004 is the frozen current best: Guitar 42.617717478052675% F1 and Bass 80.45325779036827% F1. I004 was promoted with zero new reference-facing score calls after exact reconstruction of the already-scored contextual whole-rule winner. The post-I004 aggregate/reference-blind Guitar diagnosis is now terminal/frozen. It identifies three strong structural facts: harmonic/octave suppression improves F1 in all 12 matched cells; ratio 1.00 improves F1 over 0.75 in all 12 matched cells; and `allow_active` is never worse than `inactive_only` across 18 matched cells while carrying substantially more recall/matches. The next permitted research step is a small preregistered state-split Guitar family that treats active/max-active re-attack-like proposals separately from inactive pitch proposals. No I005 exists. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — POST-I004 DIAGNOSIS FROZEN / STATE-SPLIT PREREGISTRATION NEXT
- I004 promotion terminal commit `edb1cbca37ffcac2cf1020e2af05120e2f3a5353`.
- I004 `debug/v167-single-song-calibration/iteration-004-generated.json`: blob `8dd85049a65f00541f7874ff99511b081a0b5ff2`, SHA256 `728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc`.
- I004 proof blob `d055f3f0a1cbf91cd4d6ac4cb26ee654b599925d`, SHA256 `b35c7bff5583786a8e23e736c56898505306e7c6c69106bf565aa11e0e0ae753`; freeze receipt blob `a880a1e29dab29cc0e77f1aa569dd123e1092457`, status `ITERATION_004_FROZEN`.
- I004 Guitar 1113 = all 1050 rich I003 Guitar event dictionaries preserved + 63 frozen winner additions; normalized stream exactly equals frozen scored winner. I004 Bass is exactly the rich I003 list, 512 events.
- Post-I004 analyzer `validation/v167_single_song_calibration/analyze_contextual_guitar_sweep_v167.py`: commit `8f7be4d89813fd5e9e9f078a3983de10692a99b2`, blob `9bd0e9f69f63d5886a69af9695d738bbd4c9e897`.
- Diagnosis arm `9347e304e28d19c645d18a0c9c919a1e6c2ea543`; run `33257885048`, job `99114663941`; **SUCCESS**. Terminal self-seal `623a4c3bb8f39aa580a03fd47a11a8581011ea73`; one-shot workflow deleted itself.
- Frozen analysis `debug/v167-single-song-calibration/post-i004-contextual-guitar-aggregate-analysis.json`: blob `d7f698bf9960814dea43c2f1cbd93f754c07dc43`, SHA256 `99396cd675fc107ac37142aa3afa7805d73ccc02edd875ac1059a043ee8f0f07`.
- Frozen receipt `debug/v167-single-song-calibration/post-i004-contextual-guitar-aggregate-analysis-receipt.json`: blob `c1f8640b1f728e219430789d96f6d6722572e1a7`, status `POST_I004_CONTEXTUAL_AGGREGATE_ANALYSIS_FROZEN`.
- Analysis policy: professional reference read=false; scorer read=false; new reference-facing score calls=0; per-event reference-match assignments read=false; aggregate whole-variant scores only; reference-blind evidence only for event structure; new rule selected=false; I005 created=false; GPU/CUDA/Modal=false; `main`/Production=false; generalization claim=false.

## Frozen I004 current-best metrics
### Guitar — `gctx-o50-q100-allow-noharm`
- F1 **42.617717478052675%**; precision **47.97843665768194%**; recall **38.334529791816224%**.
- 534 matched / 1113 generated / 1393 reference; FP 579; FN 859.
- Delta vs I003: F1 **+0.702040032289275pp**; precision **-0.7834681042228231pp**; recall **+1.5793251974156486pp**; +22 matches; +41 FP; -22 FN.
- Config: rank >=0.975; activity >=0.05; onset >=0.50; candidate/max-active template score >=1.00; `allow_active`; reject nearest different active intervals 12/19/24; active-pitch context required; inherited `fundamentalPresent`; top-1/site; cap 6.

### Bass — closed / exactly I003
- F1 **80.45325779036827%**; precision **83.203125%**; recall **77.87934186471663%**.
- 426 matched / 512 generated / 547 reference; FP 86; FN 121.

## Post-I004 aggregate diagnosis — FROZEN
### Harmonic suppression is the strongest precision control
- `exclude_harmonic_octave` versus `none`, matched at the same onset/ratio/active-state: **12/12 higher F1, 0 ties, 0 lower**.
- Mean delta: **+0.33091040828484897pp F1**, **+1.0527597777533495pp precision**, **-0.13161043311797302pp recall**.
- Mean event effect: **-28.583 additions**, **-26.75 FP**, only **-1.833 matches**.
- `chord_interval` versus `none` is a stronger prune: 9/12 higher F1, mean +0.1992187851689651pp F1 and +1.3185304874835773pp precision, but costs 7 matches / 0.5025125628140712pp recall on average. This supports `exclude_harmonic_octave` as the better recall/precision middle policy.

### Ratio 1.00 is a stable structural middle boundary
- Ratio `1.00` versus `0.75`, fixed onset/active-state/interval: **12/12 higher F1**.
- Mean delta: **+0.21439806530977137pp F1**, **+0.6033166465310075pp precision**, only **-0.0358937544867192pp recall** and **-0.5 matches**, while removing **15.25 additions / 14.75 FP** on average.
- Positive whole rules by ratio: `0.75` = 4, `1.00` = 6, `1.25` = 0.
- Ratio `1.25` versus `1.00` is mixed 6/12 vs 6/12 and averages **-0.12922580604163061pp F1**, **-0.5623354869586016pp recall**, **-7.833 matches**, despite +0.5849634748314879pp precision. This is under-addition on average.
- Structural interpretation: for a Basic-Pitch-active candidate, candidate/max-active template ratio cannot exceed 1.00; ratio >=1.00 therefore retains only active candidates tied for max-active template evidence, while ratio 1.25 necessarily removes the active-candidate branch. This gives a mechanistic reason to split active and inactive policies instead of tuning one shared ratio further.

### Active-state branch carries the useful recall
- `allow_active` versus `inactive_only`, fixed onset/ratio/interval: **12/18 higher F1, 6 ties, 0 lower**.
- Mean delta: **+0.45000989139467595pp F1**, **+0.7418042593921987pp recall**, **+10.333 matches**; mean precision delta is nearly neutral at **-0.028885316185440275pp**, with +12.167 FP.
- All **10 positive** contextual nonbaseline rules are `allow_active`; **0/18** `inactive_only` rules beat I003.
- The frozen winner's 63 additions are structurally split **46 Basic-Pitch-active / 17 inactive** at their evidence sites. Candidate/max-active template ratio has median **1.0**, p75 **1.0069281969884114**, p90 **1.4705172253883396**.
- Interpretation boundary: this supports an active/max-active re-attack-like proposal mechanism only at aggregate/reference-blind level; no individual event is labeled a true positive or re-attack by reference.

### Onset 0.65 is not a strong next dimension
- Onset `0.65` versus `0.50`: 3/18 higher F1, 9 ties, 6 lower; mean **-0.03820393582332709pp F1** with only -1.944 additions on average. Keep onset 0.50 fixed unless a genuinely new structural reason appears.

### Addition-count mechanism
- Across all 36 rules: additions vs precision delta correlation **-0.8666120193973829**; additions vs FP delta **+0.9839527233419079**; additions vs recall delta **+0.8598359824170556**; additions vs matched delta **+0.8598359824170553**; additions vs F1 delta only **+0.17557607845070156**.
- The remaining problem is therefore not raw recall capacity. It is how to preserve the high-value active/max-active additions while applying stronger precision control to the inactive branch.

## Frozen contextual sweep anchor
- Final contextual generator blob `fd257fe88c5dcd9b3ab135263a6457140c3f63b6`.
- Sweep terminal `f93467de4ccde1d2c0b9baf02c14c194f9d644c4`.
- Manifest blob `b9ec90a34e0d7a4a6b6ee7fb3f5a1eef7e6bba5d`, SHA256 `2f51fa0cba372acc8f797a2e700b3b0a6bb42b807ad4bad818b3c40c262df876`.
- Report blob `b00e25f5c1fd9f8c40b440156e049317e008ec1d`, SHA256 `6b661f6dfa27d31204f4e8a9035d286d5324440b947eb3e49db99205dad9320e`.
- 37 variants = baseline + 36 complete contextual whole rules, all frozen before reference read; 10/36 nonbaseline positive.

## Immutable source/evidence boundary
- I003 `debug/v167-single-song-calibration/iteration-003-generated.json`: blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- Evidence pool blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- V166 frozen timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`; frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.

## Standing V167 methodology
- Calibration only; never present V167 scores as holdout/generalization performance.
- Reference/scorer may grade complete predeclared variants and select whole deterministic rules/settings only. No per-event reference choices or direct reference-event copying.
- Aggregate whole-rule score reports may be analyzed without reopening the professional reference/scorer; reference-blind evidence may be used for structural diagnosis.
- I004 remains immutable during all new candidate generation/scoring. A future I005 may exist only after a complete preregistered family is frozen, scored as whole variants, and a later deterministic promotion is separately proven.
- Bass is closed and must stay exactly I004/I003 for every future Guitar variant in this lane.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — preregister a small state-split Guitar family
1. Keep I004 immutable and include it as the frozen baseline. Generate any alternative complete Guitar streams from immutable I003 + frozen evidence/timebase, never by mutating I004 in place. Bass must remain exactly I004/I003.
2. Keep winner-proven shared structure fixed: rank >=0.975, activity >=0.05, onset >=0.50, active context required, inherited `fundamentalPresent`, top-1/site, parent-aware `(step,midi)` dedupe, cap 6, frozen `-12` timing, and harmonic interval rejection {12,19,24} on the active branch.
3. New structural hypothesis: **split active and inactive candidate policies**. Active branch = Basic-Pitch-active candidate that is tied for max active template evidence (ratio >=1.00), preserving the aggregate recall mechanism. Inactive branch is separately optional/stricter because inactive-only rules were uniformly negative.
4. Small preregistered inactive-branch family, with the active branch fixed as above:
   - `inactive_off`;
   - inactive ratio >=1.25 + `exclude_harmonic_octave`;
   - inactive ratio >=1.00 + `chord_interval`;
   - inactive ratio >=1.25 + `chord_interval`.
   Also build a no-score reproduction control `inactive ratio >=1.00 + exclude_harmonic_octave` that must normalize exactly to I004 before any reference/scorer read.
5. Freeze every complete candidate and SHA256 before any future reference/scorer read. Verify the reproduction control equals I004 and exclude it from redundant score calls. Score only baseline I004 + the four genuinely new complete state-split rules as whole variants. Winner tie-break: max Guitar F1, then precision, fewer total additions versus I003, lexicographic id. No automatic I005 promotion.
6. If none beats I004, close this state-split family. If a rule beats I004, freeze the report first and require a separate no-rescore deterministic I005 promotion boundary.
7. CPU only; fresh authorization before GPU/CUDA/Modal. Never modify/merge/promote `main` or Production.
