# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 003 is now the frozen current best. Guitar remains exactly the Iteration 002 winner at 41.9156774457634% F1. Bass has been deterministically promoted to the frozen upstream-recovery winner at 80.45325779036827% F1, +8.588136610178598pp versus Iteration 002. The rich Iteration 003 candidate was proven musically identical to the already-scored frozen sweep winner with zero new reference-facing score calls. `main`/Production remain untouched; no GPU/CUDA/Modal work was used. The next research boundary is Guitar only: the first standalone-harmonic addition grid is terminal negative, so any further Guitar work must begin from a new preregistered hypothesis derived from frozen aggregate evidence, not per-event reference choices.**

## Standing V167 methodology
- Calibration only; never present V167 calibration score as holdout/generalization performance.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Reference/scorer may grade complete predeclared variants and select whole deterministic rules/parameter settings. It may not directly supply/copy candidate events or choose individual-event answers.
- Direct/manual reference-event copying is forbidden.
- CPU work is authorized. Fresh explicit authorization is required immediately before GPU/CUDA/Modal execution.
- Never modify/merge/promote `main` or Production without explicit user direction.

## Closed V166 anchor
- Sole generation run `33226705813`, job `99031747626`; terminal commit `7f5f5f19f6ec413fc772a9839be5497ecb2790e3`.
- Candidate `debug/v166-cpu-autonomous/generated.json`, blob `c36a4d1e14ca66235b51a866ad3908322834efff`, SHA256 `fa2411598b401f745eff49a9cbda294ed767de093c905909531c7dd4dc6eb378`.
- Counts Guitar 1050 / Bass 402; structural QC PASS. V159–V166 generations are closed forever.

## V167 progression before upstream recovery
- Baseline: Guitar **6.058125255832993%**, Bass **21.707060063224446%**.
- Frozen global phase optimum for both streams: `-12` absolute grid steps.
- Iteration 001 terminal `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`: Guitar **40.36021285304953%**, Bass **70.60063224446786%**.
- Fixed shared 8-measure phase sweep found no additional nonzero timing correction.
- Generated-only repeat completion was not promoted: Bass no gain; Guitar only +0.622pp while adding 285 notes.
- Frozen whole-stream step-rule sweep selected Guitar `max_score_x_shared` and Bass `max_score_x_mean_support`.

## V167 Iteration 002 — FROZEN PARENT
- Transform `validation/v167_single_song_calibration/apply_step_rules_v167.py`, blob `00dc94081117664890d1dc5539bf5e69fedf76fa`.
- Run `33227898407`, job `99035077043`; terminal commit `9883daaa9770123aeab2a122fa72fa2fc6c16c4c`.
- Candidate `debug/v167-single-song-calibration/iteration-002-generated.json`, blob `7eba73700116ceeca580a8851abe399aed764834`, SHA256 `96fbc329d9ba46b06d430c7c3c7b7f5b0e9077f6e133da5c3165c1fde609b5cc`.
- Guitar: **41.9156774457634%** F1 = 512 matched / 1050 generated / 1393 reference; precision 48.76190476190476%, recall 36.755204594400576%.
- Bass: **71.86512118018967%** F1 = 341 / 402 / 547; precision 84.82587064676616%, recall 62.340036563071296%.

## V167 Bass admitted-event repitch sweep — FROZEN NEGATIVE
- Code blob `2b59bb1dcb2b5724eb56457349639ec6eb6eca83`; run `33228058021`, job `99035528898`; terminal `b3425afd6ffd06ab367a18edd3ce4d63242f7659`.
- Best is `baseline_current`; delta 0.0pp. Existing admitted-event state/pYIN repitching does not improve Bass.

## Frozen source/evidence boundary
- Historical source `public/gomywayfullaitest.m4a` from commit `74b0f815ff3f66f325220975c410621503de440f`; SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Frozen V166 timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`.
- CPU stack: Python 3.10.21, torch 2.8.0+cpu, Demucs 4.1.0 `htdemucs_6s`, CPU, shifts=1, jobs=1.
- Upstream evidence run `33228322645`, job `99036292089`; terminal self-seal `86ab5882845b61917b8820c35b07022adef532f0`.
- Evidence pool `debug/v167-single-song-calibration/nearmiss-evidence-pool.json`, blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Receipt blob `8268eb6eeb0bbb00b98bcf3dcf2812c8a55932a3`, status `EVIDENCE_POOL_FROZEN`.
- Exact V166 musical reproduction: 1050 Guitar / 402 Bass. Reference/scorer reads 0; threshold tuning=false; candidate generation behavior modified=false; GPU/CUDA/Modal=false; `main`/Production=false.
- Guitar standalone harmonic pool: **272 sites / 13,328 candidates**.
- Bass pre-admission pool: **913 sites / 36,520 candidates**.
- Bass final admission gates rejected essentially nothing; missing Bass recall was upstream proposal/state coverage.
- Guitar active-state recovery historically did not perform standalone harmonic pitch discovery; missing chord-tone/polyphony coverage remains an upstream hypothesis area.

## V167 upstream-recovery sweep preregistration
- Base generator `validation/v167_single_song_calibration/build_upstream_recovery_variants_v167.py`, blob `24413d321f64bbfcce48812ceb85b4593dcfa80c`, commit `6935311a96cc8ba391ad461ef1368ae7bed789b1`.
- Corrected guard-only adapter `validation/v167_single_song_calibration/build_upstream_recovery_variants_v167_rearm.py`, blob `fbbee07493084792912c774d375ca5011672891f`, commit `ffa7694b48e4e64b7e6a354a1704546909a45533`.
- Grader `validation/v167_single_song_calibration/score_upstream_recovery_variants_v167.py`, blob `32304261ff9e6bec00d22eabea08cf5070cd3d3e`, commit `589a046a08c7e508bae910774e8f74bb5c4b96ac`.
- 146 complete variants frozen before reference scoring: 49 Guitar (baseline + 48) and 97 Bass (baseline + 96).
- Guitar grid: template rank 0.80/0.90/0.95/0.975 × onset 0.35/0.50/0.65 × max 1/2 additions/site × Basic-Pitch-inactive-only true/false; fundamental required; activity >=0.05; existing I002 events preferred; cap 6.
- Bass grid: template rank 0.80/0.90/0.95/0.975 × onset 0.20/0.35/0.50 × activity 0.04/0.10 × scope all/no-stable-state/low-register/low-register+no-stable-state; fundamental required; low register MIDI <=40; new additions only on I002-empty corrected steps; inherited I002 timing collisions preserved.
- New recovery timing fixed reference-blind: nearest frozen V166 subdivision then frozen `-12` global phase. Existing I002 timing retained.
- Winner selection frozen in advance: max primary F1, max precision, fewer additions, lexicographic id. Material threshold 1.0pp. No automatic I003 promotion.

### First sweep arm — SAFE PRE-SCORE FAILURE
- Arm `8880dabdc9ac93d52e126328abd0965d23f45392`; run `33253264878`, job `99102488179`.
- Identity guard SUCCESS; reference-blind generation failed on an overstrict inherited Bass monophony assertion; grading SKIPPED; freeze SKIPPED. Zero reference-facing scores consumed.
- Corrected adapter preserves the 4 inherited I002 post-calibration Bass collision steps while still adding at most one new event to a previously empty corrected step.

## V167 upstream-recovery sweep — FROZEN / TERMINAL
- Corrected arm `168113eed4e053a97220ab8ad9daefb189d5fd93`; successful run `33253434886`, job `99102944880`; all steps SUCCESS.
- Terminal self-seal `0c74a6916e046d202cc5cf775f974bbd06fcf567`; one-shot workflow deleted.
- Manifest `debug/v167-single-song-calibration/upstream-recovery-rule-sweep-manifest.json`: blob `0ee153dbf1004d921c586516bca91e52f7bb1fde`, SHA256 `c91ee15d702746e082c059b5f99c44fcfa7a89f18e5e9f2fc81eb6513d1baa80`.
- Report `debug/v167-single-song-calibration/upstream-recovery-rule-sweep.json`: blob `324f1f4e68951ac8653c51c8a436e4d35e5dc16b`, SHA256 `1bcc5eca05df31270ff7ff638cca6def3166a0e5084c4874d70d710d4696836f`.
- Receipt `debug/v167-single-song-calibration/upstream-recovery-rule-sweep-receipt.json`: blob `a502e6fbc04d6423177c45c9dad418cede22c2d9`, status `UPSTREAM_RECOVERY_SWEEP_FROZEN`.
- Policy: variants frozen before reference read=true; individual-event reference selection=false; post-score mutation=false; GPU/CUDA/Modal=false; `main`/Production=false; generalization claim=false.

### Frozen Guitar sweep result
- Winner `g-baseline`; unchanged I002.
- F1 **41.9156774457634%**; precision 48.76190476190476%; recall 36.755204594400576%; 512/1050/1393.
- Delta 0.0pp. All 48 standalone-harmonic addition whole rules are terminal negative in this first grid.

### Frozen Bass sweep winner — MATERIAL
- Rule `b-r975-o50-a10-low_register_no_stable_state`.
- Gates: template rank >=0.975; onset >=0.50; activity >=0.10; fundamental required; MIDI <=40; no nearby stable state; existing I002 events preserved; recovery only on previously empty corrected steps.
- Frozen score-minimal candidate SHA256 `2e04edd9cb61795ea9679ce899c7ded9549bb0f5d9f8e04a5d53fdf07ec9fa13`.
- Added 110 events from 149 eligible candidates / 110 sites; preserved 4 inherited I002 collision steps.
- Primary F1 **80.45325779036827%** = 426 matched / 512 generated / 547 reference.
- Precision **83.203125%**; recall **77.87934186471663%**; FP 86; FN 121.
- Gross F1 83.09726156751652%; same-measure pitch-content F1 84.04154863078376%.
- Delta vs I002: **+8.588136610178598pp F1**, -1.622745646766166pp precision, +15.539305301645335pp recall, +85 matched, +110 generated, +25 FP, -85 FN.
- `materialGainAtLeast1pp=true`; exceeds frozen Bass primary-F1 target 80%.

## V167 Iteration 003 — CURRENT BEST / FROZEN
- Promotion transform `validation/v167_single_song_calibration/promote_upstream_recovery_winner_v167.py`, blob `9c63f2a0c4732cf3c3a11faf028cf0952c27664e`, implementation commit `8f2c4628a8c1448cf1b33bd521c2e133fb600e98`.
- Pre-arm checkpoint commit `5e436ff4fd0178f0fd5cf959ee2b2923e27d7f2f`.
- One-shot arm commit `157bf0ed3514d106a9888d6877183e9a54e462d3`.
- Workflow run `33253690563`, job `99103631893`, run 1 / attempt 1; **all steps SUCCESS**.
- Terminal self-seal commit `17ab31bf26fa1e15a7754469b7598c071a938705`; one-shot workflow deleted.
- Candidate `debug/v167-single-song-calibration/iteration-003-generated.json`: git blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- Promotion proof `debug/v167-single-song-calibration/iteration-003-promotion-proof.json`: git blob `60dba77ac478ed804fd5d66993878e4921c4a72d`, SHA256 `35cb7c95252e4000cc522cd474616b5a0265731ab2454ea123d7756b7872059d`.
- Receipt `debug/v167-single-song-calibration/iteration-003-promotion-receipt.json`: git blob `b3979dd5b6b205a072223493248fc66b37272a5c`, status `ITERATION_003_FROZEN`.
- Promotion reconstructed the frozen score-minimal winner at exact SHA256 `2e04edd9cb61795ea9679ce899c7ded9549bb0f5d9f8e04a5d53fdf07ec9fa13` before writing I003.
- Guitar proof: parent count 1050 -> I003 count 1050; rich parent list exactly preserved=true; normalized stream equal frozen scored winner=true.
- Bass proof: parent count 402 + exactly 110 recovery additions -> I003 count 512; pre-existing rich event dictionary multiset exactly preserved=true; normalized stream equal frozen scored winner=true.
- Policy proof: professional reference read by promotion=false; scorer read by promotion=false; new reference-facing score calls=0; individual-event reference selection=false; direct reference event copy=false; post-sweep retuning=false; GPU/CUDA/Modal=false; `main`/Production modified=false; generalization claim=false.

### Frozen Iteration 003 inherited metrics
- **Guitar:** F1 **41.9156774457634%**, precision **48.76190476190476%**, recall **36.755204594400576%**, 512 matched / 1050 generated / 1393 reference.
- **Bass:** F1 **80.45325779036827%**, precision **83.203125%**, recall **77.87934186471663%**, 426 matched / 512 generated / 547 reference; FP 86 / FN 121; gross F1 83.09726156751652%; same-measure pitch-content F1 84.04154863078376%.
- These are inherited from exact normalized musical-stream equality to the already-scored frozen sweep winner; I003 itself performed no new reference-facing score.

## NEXT boundary — new preregistered Guitar hypothesis only
1. Keep Iteration 003 immutable as the current best. Bass recovery is frozen/promoted; do not retune it in this lane.
2. Analyze only **aggregate whole-variant results** from the terminal 48-rule Guitar sweep plus reference-blind candidate/evidence distributions. Do not use per-event reference matches to choose notes.
3. Determine why additive standalone-harmonic recovery loses to baseline: quantify additions versus F1/precision/recall at each predeclared threshold family and identify whether the issue is over-addition, weak ranking discrimination, timing occupancy, or missing contextual gating.
4. Any next Guitar candidate family must be explicitly preregistered as a new deterministic whole-rule hypothesis before reference scoring. Prefer a structurally different gate (for example contextual/relative evidence) rather than simply expanding the already-negative absolute-threshold grid.
5. Do not create Iteration 004 unless a new frozen whole-rule Guitar sweep materially beats I003 Guitar with a defensible precision/recall tradeoff while Bass remains exactly I003.
6. Keep CPU-only. Fresh explicit authorization is required before any GPU/CUDA/Modal work.
7. Never modify/merge/promote `main` or Production without explicit user direction.
