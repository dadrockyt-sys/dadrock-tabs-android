# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 003 remains the frozen parent: Guitar 41.9156774457634% F1; Bass 80.45325779036827% F1. The preregistered sparse contextual Guitar sweep is terminal/frozen and positive: 10/36 nonbaseline rules beat I003. Frozen winner `gctx-o50-q100-allow-noharm` scores Guitar 42.617717478052675% F1 (+0.702040032289275pp), precision 47.97843665768194% (-0.7834681042228231pp), recall 38.334529791816224% (+1.5793251974156486pp), with 63 additions and 534 matches. Bass stayed exactly I003 for every scored variant and remains closed. This clears the preregistered promotion boundary. Deterministic no-rescore I004 promotion is now implemented but not yet executed. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — I004 PROMOTION IMPLEMENTED / PRE-ARM
- Resumed from this file on `v143-contextual-prune-lobo`; turn starting head was `2a7dfedd6385ef0136e1a07e6677dd3b6c47cbf0`.
- Successful contextual sweep arm `0dec90b569de77b4410c52c354e2b764883e327f`; run `33257327955`, job `99113230085`; terminal self-seal `f93467de4ccde1d2c0b9baf02c14c194f9d644c4`.
- Frozen manifest `debug/v167-single-song-calibration/contextual-guitar-recovery-sweep-manifest.json`: blob `b9ec90a34e0d7a4a6b6ee7fb3f5a1eef7e6bba5d`, SHA256 `2f51fa0cba372acc8f797a2e700b3b0a6bb42b807ad4bad818b3c40c262df876`.
- Frozen report `debug/v167-single-song-calibration/contextual-guitar-recovery-sweep.json`: blob `b00e25f5c1fd9f8c40b440156e049317e008ec1d`, SHA256 `6b661f6dfa27d31204f4e8a9035d286d5324440b947eb3e49db99205dad9320e`.
- Frozen receipt `debug/v167-single-song-calibration/contextual-guitar-recovery-sweep-receipt.json`: blob `e4e296bb50a38935d83e2c1183160509974fd6aa`, status `CONTEXTUAL_GUITAR_RECOVERY_SWEEP_FROZEN`.
- Final contextual generator blob `fd257fe88c5dcd9b3ab135263a6457140c3f63b6`; it preserves immutable I003 parent duplicates while preventing every new `(step,midi)` collision. Successful guard established I003 Guitar pre-existing duplicate scoring-coordinate excess = 9.
- Frozen whole-rule winner candidate SHA256 `2527870bc4655c238d5f4fbd0e243ab518554e17c4e2c29db2794225bbbeed43`.
- Deterministic promotion transform added at `validation/v167_single_song_calibration/promote_contextual_guitar_winner_v167.py`; commit `4cd0dece8f8a88fc211fbecd63bb5747e6d74ae9`, blob `cd099c6a7f1c33a4d3c5f1ce58c27d4d8d20078f`.
- Promotion transform has **no reference/scorer input path**. It verifies frozen I003/pool/manifest/report SHA256s and exact base/contextual-builder Git blobs; verifies the already-selected frozen winner id/config/summary/metrics; reconstructs the complete score-minimal winner from I003 + frozen evidence/timebase; requires reconstructed SHA256 to equal `2527870bc4655c238d5f4fbd0e243ab518554e17c4e2c29db2794225bbbeed43` before writing I004.
- If reconstruction matches, I004 rich Guitar is I003 rich Guitar dictionaries plus exactly the 63 frozen winner additions; normalized Guitar must equal the frozen scored winner. I004 Bass is an exact deep copy of the rich I003 Bass list and must compare list-equal and normalized-equal to I003.
- Promotion metadata/proof explicitly records zero new reference-facing scores, no scorer read, no professional-reference read, no post-sweep retuning, no per-event reference selection, no direct reference copy, no GPU/CUDA/Modal, no `main`/Production modification.
- **No I004 candidate exists yet.** Next substep: checkpoint this pre-arm state, then arm a one-shot CPU workflow that verifies the exact promotion script/checkpoint/input blobs, performs only this deterministic reconstruction/promotion, freezes I004 candidate + proof + receipt, self-removes, and pushes only to `v143-contextual-prune-lobo`.

## Frozen contextual Guitar winner
- Rule `gctx-o50-q100-allow-noharm`.
- Config: template rank >=0.975; activity >=0.05; onset >=0.50; candidate/max-active template-score ratio >=1.00; `allow_active`; nearest different active interval 12/19/24 rejected; active context required; inherited `fundamentalPresent`; top-1/site; cap 6.
- Generation: 63 additions from 69 eligible candidates, 63 sites with adds, 204 sites with active context.
- Guitar: F1 **42.617717478052675%**; precision **47.97843665768194%**; recall **38.334529791816224%**; matched 534; generated 1113; reference 1393; FP 579; FN 859.
- Delta vs I003: F1 **+0.702040032289275pp**; precision **-0.7834681042228231pp**; recall **+1.5793251974156486pp**; +22 matches; +41 FP; -22 FN.
- **10 / 36** nonbaseline contextual rules beat I003 Guitar F1. Winner selection was preregistered: max Guitar F1, then precision, fewer additions, lexicographic id.
- Bass inherited baseline: F1 **80.45325779036827%**, precision 83.203125%, recall 77.87934186471663%, matched 426 / generated 512 / reference 547.

## Immutable promotion inputs
- I003 `debug/v167-single-song-calibration/iteration-003-generated.json`: Git blob `758f8762632e916306aed9b036a6483af9431dc0`, corrected independently-established SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`; Guitar 1050 / Bass 512.
- Evidence pool `debug/v167-single-song-calibration/nearmiss-evidence-pool.json`: blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Timebase `debug/v166-cpu-autonomous/timebase.json`: blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`.
- Base recovery builder `validation/v167_single_song_calibration/build_upstream_recovery_variants_v167.py`: blob `24413d321f64bbfcce48812ceb85b4593dcfa80c`.
- Contextual builder `validation/v167_single_song_calibration/build_contextual_guitar_recovery_variants_v167.py`: blob `fd257fe88c5dcd9b3ab135263a6457140c3f63b6`.
- Frozen contextual manifest/report identities are listed above.

## Execution history / safe-stop audit
- First contextual arm `82c1e0e375d8be6d1c0a974d311723381bfdf91c`; run `33256979705`, job `99112324623`: pre-score guard stopped on stale historical I003 SHA metadata. Zero candidates generated; zero reference/scorer reads.
- Immutable I003 blob `758f876...` independently hashes to `f15c6f40...ae37115`; prior checkpoint `...bf709673` was metadata error only; I003 bytes were never modified.
- Second arm `d32acd8a0d6a202bd2d5e27cfe4a381210a7d768`; run `33257192660`, job `99112883194`: preregistration guard passed, generation then safely stopped because a postcondition incorrectly assumed parent global coordinate uniqueness. Grading/reference skipped.
- Parent-aware invariant correction only: preserve I003's 9 duplicate-coordinate excess; forbid all new collisions. Rule thresholds/ranking unchanged.
- Third arm/run succeeded and self-sealed as listed above. All 37 complete candidates froze before any reference read; additions ranged 0..117; Bass coordinate identity was verified before scoring.

## Standing V167 methodology
- Calibration only; never present V167 scores as holdout/generalization performance.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- **I004 promotion must not read either scorer or professional reference.** Reference/scorer were used only by the already-frozen complete-rule sweep.
- No per-event reference choices or direct reference-event copying.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## V167 Iteration 003 — FROZEN PARENT FOR I004
- Run `33253690563`, job `99103631893`; terminal self-seal `17ab31bf26fa1e15a7754469b7598c071a938705`.
- Candidate blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- Guitar 1050; Bass 512. Frozen inherited metrics: Guitar **41.9156774457634%** F1; Bass **80.45325779036827%** F1.

## NEXT boundary — execute and freeze I004 without rescoring
1. Keep I003 immutable.
2. Arm a one-shot CPU workflow only after verifying exact current branch parent, promotion script blob, checkpoint blob, I003/pool/timebase/manifest/report/base-builder/contextual-builder blobs and frozen SHA256s.
3. Workflow must not name/read the professional reference or scorer.
4. Reconstructed score-minimal candidate must SHA256-match frozen winner `2527870bc4655c238d5f4fbd0e243ab518554e17c4e2c29db2794225bbbeed43` before I004 is written.
5. Freeze `iteration-004-generated.json`, promotion proof, and freeze receipt; self-remove the workflow. Bass rich list must remain exactly I003; Guitar normalized stream must equal frozen contextual winner.
6. No new reference-facing score is needed or permitted for promotion; inherit already-frozen metrics by exact stream equality.
7. Never modify/merge/promote `main` or Production. CPU only; fresh authorization before GPU/CUDA/Modal.
