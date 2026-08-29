# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 003 remains the frozen parent: Guitar 41.9156774457634% F1; Bass 80.45325779036827% F1. The preregistered sparse contextual Guitar sweep is now terminal/frozen and positive: 10/36 nonbaseline rules beat I003, with winner `gctx-o50-q100-allow-noharm` at Guitar 42.617717478052675% F1 (+0.702040032289275pp), precision 47.97843665768194% (-0.7834681042228231pp), recall 38.334529791816224% (+1.5793251974156486pp), 63 additions, 534 matches. Bass stayed exactly I003 for every scored variant and remains closed. This clears the checkpoint promotion condition with a defensible recall/precision tradeoff. Next is deterministic no-rescore I004 promotion of the already-frozen whole-rule winner. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — 2026-08-29 UTC / CONTEXTUAL SWEEP FROZEN, I004 PROMOTION NEXT
- Resumed from this file on `v143-contextual-prune-lobo`; starting head was `2a7dfedd6385ef0136e1a07e6677dd3b6c47cbf0`.
- The exact preregistered 36-rule Guitar family stayed fixed in substance throughout execution: rank `0.975`, activity `0.05`, onset `{0.50,0.65}`, candidate/max-active template ratio `{0.75,1.00,1.25}`, active-state `{allow_active,inactive_only}`, interval policy `{none,exclude_harmonic_octave,chord_interval}`, inherited `fundamentalPresent`, active-pitch context required, top-1/site, parent-aware new-event `(step,midi)` dedupe, polyphony cap 6.
- First arm `82c1e0e375d8be6d1c0a974d311723381bfdf91c`; run `33256979705`, job `99112324623`: stopped in preregistration verification on stale checkpoint SHA256 metadata. No candidates generated; zero scorer/reference reads.
- The immutable I003 Git blob `758f8762632e916306aed9b036a6483af9431dc0` independently hashes to corrected SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`; prior `...c575bf709673` checkpoint text was metadata error only. I003 bytes were never changed.
- Second arm `d32acd8a0d6a202bd2d5e27cfe4a381210a7d768`; run `33257192660`, job `99112883194`: full preregistration verification passed, then generation stopped on an overly strict assertion because immutable I003 Guitar already contains duplicate scoring coordinates. Grading/reference read skipped.
- Third arm `0dec90b569de77b4410c52c354e2b764883e327f`; run `33257327955`, job `99113230085`: **SUCCESS**. Pre-score guard established immutable I003 Guitar duplicate-coordinate excess = **9**. All 37 complete candidates froze before reference/scorer read; additions ranged 0..117; Bass count 512 in every variant.
- Contextual generator final blob `fd257fe88c5dcd9b3ab135263a6457140c3f63b6` (commit `4ae7b91ce196b97df9e033fab7ff1880c32e1069`). It preserves I003 parent duplicates while rejecting every new event that collides with a parent or earlier new `(step,midi)` coordinate. Candidate thresholds/ranking were not changed by this invariant correction.
- Base grader blob `adfd512f53e8839b295129c0768d484b5af09bc7`; safe identity adapter blob `8555101a684f59f7dcd910d7c6f7694e968a68b1`. The adapter only corrects the stale I003 SHA guard; scoring/winner logic remains the preregistered grader.
- Successful sweep self-sealed at terminal commit `f93467de4ccde1d2c0b9baf02c14c194f9d644c4`; the one-shot workflow was deleted.
- Frozen manifest `debug/v167-single-song-calibration/contextual-guitar-recovery-sweep-manifest.json`: blob `b9ec90a34e0d7a4a6b6ee7fb3f5a1eef7e6bba5d`, SHA256 `2f51fa0cba372acc8f797a2e700b3b0a6bb42b807ad4bad818b3c40c262df876`.
- Frozen report `debug/v167-single-song-calibration/contextual-guitar-recovery-sweep.json`: blob `b00e25f5c1fd9f8c40b440156e049317e008ec1d`, SHA256 `6b661f6dfa27d31204f4e8a9035d286d5324440b947eb3e49db99205dad9320e`.
- Frozen receipt `debug/v167-single-song-calibration/contextual-guitar-recovery-sweep-receipt.json`: blob `e4e296bb50a38935d83e2c1183160509974fd6aa`, status `CONTEXTUAL_GUITAR_RECOVERY_SWEEP_FROZEN`.
- Sweep policy proof: 37 variants = 1 baseline + 36 contextual; all frozen before reference read; whole-rule selection only; individual-event reference selection false; post-score candidate mutation false; Bass coordinate identity verified before reference read; I004 not created by scoring workflow; generalization claim false; GPU/CUDA/Modal false; `main`/Production false.

## Frozen contextual Guitar winner
- Rule `gctx-o50-q100-allow-noharm`.
- Config: template rank >=0.975; activity >=0.05; onset >=0.50; candidate/max-active template-score ratio >=1.00; `allow_active`; nearest different active interval 12/19/24 rejected; active context required; inherited `fundamentalPresent`; top-1/site; cap 6.
- Frozen candidate SHA256 `2527870bc4655c238d5f4fbd0e243ab518554e17c4e2c29db2794225bbbeed43`.
- Generation: 63 additions from 69 eligible candidates, 63 sites with adds, 204 sites with active context.
- Guitar: F1 **42.617717478052675%**; precision **47.97843665768194%**; recall **38.334529791816224%**; matched 534; generated 1113; reference 1393; FP 579; FN 859.
- Delta vs I003: F1 **+0.702040032289275pp**; precision **-0.7834681042228231pp**; recall **+1.5793251974156486pp**; +22 matches; +41 FP; -22 FN.
- **10 / 36** nonbaseline contextual rules beat I003 Guitar F1. The selected whole rule wins by the preregistered ordering: max F1, then precision, fewer additions, lexicographic id.
- Bass inherited baseline remains F1 **80.45325779036827%**, precision 83.203125%, recall 77.87934186471663%, matched 426 / generated 512 / reference 547.

## Standing V167 methodology
- Calibration only; never present V167 scores as holdout/generalization performance.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Reference/scorer may grade complete predeclared variants and select whole deterministic rules/settings only. No per-event reference choices or direct reference-event copying.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## Closed V166 anchor
- Generation run `33226705813`, job `99031747626`; terminal `7f5f5f19f6ec413fc772a9839be5497ecb2790e3`.
- Candidate blob `c36a4d1e14ca66235b51a866ad3908322834efff`, SHA256 `fa2411598b401f745eff49a9cbda294ed767de093c905909531c7dd4dc6eb378`; 1050 Guitar / 402 Bass. V159–V166 closed forever.

## V167 pre-recovery progression
- Baseline Guitar 6.058125255832993%, Bass 21.707060063224446%.
- Frozen global phase `-12` steps.
- I001 terminal `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`: Guitar 40.36021285304953%, Bass 70.60063224446786%.
- Shared local phase sweep: no nonzero gain. Repeat completion: not promoted.
- Whole-stream step-rule sweep selected Guitar `max_score_x_shared`, Bass `max_score_x_mean_support`.

## V167 Iteration 002 — FROZEN PARENT
- Candidate `debug/v167-single-song-calibration/iteration-002-generated.json`, blob `7eba73700116ceeca580a8851abe399aed764834`, SHA256 `96fbc329d9ba46b06d430c7c3c7b7f5b0e9077f6e133da5c3165c1fde609b5cc`.
- Guitar **41.9156774457634%** F1; P 48.76190476190476%; R 36.755204594400576%; 512/1050/1393.
- Bass **71.86512118018967%** F1; P 84.82587064676616%; R 62.340036563071296%; 341/402/547.

## V167 Iteration 003 — FROZEN PARENT FOR I004
- Promotion transform blob `9c63f2a0c4732cf3c3a11faf028cf0952c27664e`.
- Run `33253690563`, job `99103631893`; terminal self-seal `17ab31bf26fa1e15a7754469b7598c071a938705`.
- Candidate `debug/v167-single-song-calibration/iteration-003-generated.json`: blob `758f8762632e916306aed9b036a6483af9431dc0`, corrected SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- Proof blob `60dba77ac478ed804fd5d66993878e4921c4a72d`; receipt blob `b3979dd5b6b205a072223493248fc66b37272a5c`, status `ITERATION_003_FROZEN`.
- Guitar 1050; Bass 512. Frozen inherited metrics: Guitar **41.9156774457634%** F1; Bass **80.45325779036827%** F1.

## NEXT boundary — promote frozen contextual winner to I004 without rescoring
1. I003 stays immutable. Reconstruct only frozen winner `gctx-o50-q100-allow-noharm` from I003 + frozen evidence/timebase + final contextual builder.
2. Reconstructed score-minimal candidate must SHA256-match frozen scored winner `2527870bc4655c238d5f4fbd0e243ab518554e17c4e2c29db2794225bbbeed43` before writing I004.
3. I004 Guitar = all rich I003 Guitar events preserved exactly as event dictionaries + exactly the 63 frozen winner additions. Normalized Guitar scoring stream must equal the frozen scored winner.
4. I004 Bass list must remain exactly equal to rich I003 Bass; normalized Bass stream must also remain exactly the already-scored I003 Bass baseline.
5. Promotion reads frozen manifest/report only to verify the already-selected whole rule; it must not open professional reference/scorer files, must not rescore, retune, or make per-event reference choices.
6. Freeze I004 candidate + promotion proof + receipt in a self-removing CPU-only workflow. No GPU/CUDA/Modal. Never modify/merge/promote `main` or Production without explicit user direction.
