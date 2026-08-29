# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 003 is frozen current best: Guitar 41.9156774457634% F1 unchanged from I002; Bass 80.45325779036827% F1 after deterministic promotion of the terminal upstream-recovery winner. The I003 rich candidate is proven musically identical to the already-scored frozen winner with zero new reference-facing score calls. Bass is closed for this lane. Guitar's first 48-rule standalone-harmonic addition grid is terminal negative. An aggregate-only/reference-blind Guitar analysis is now staged to explain that failure and expose structural contextual evidence for a genuinely new preregistered hypothesis. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

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

## V167 pre-recovery progression
- Baseline: Guitar **6.058125255832993%**, Bass **21.707060063224446%**.
- Frozen global phase optimum for both streams: `-12` absolute grid steps.
- Iteration 001 terminal `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`: Guitar **40.36021285304953%**, Bass **70.60063224446786%**.
- Fixed shared 8-measure phase sweep found no additional nonzero correction.
- Generated-only repeat completion not promoted: Bass no gain; Guitar +0.622pp while adding 285 notes.
- Frozen whole-stream step-rule sweep selected Guitar `max_score_x_shared`, Bass `max_score_x_mean_support`.

## V167 Iteration 002 — FROZEN PARENT
- Transform blob `00dc94081117664890d1dc5539bf5e69fedf76fa`; run `33227898407`, job `99035077043`; terminal `9883daaa9770123aeab2a122fa72fa2fc6c16c4c`.
- Candidate `debug/v167-single-song-calibration/iteration-002-generated.json`, blob `7eba73700116ceeca580a8851abe399aed764834`, SHA256 `96fbc329d9ba46b06d430c7c3c7b7f5b0e9077f6e133da5c3165c1fde609b5cc`.
- Guitar: **41.9156774457634%** F1; precision 48.76190476190476%; recall 36.755204594400576%; 512/1050/1393.
- Bass: **71.86512118018967%** F1; precision 84.82587064676616%; recall 62.340036563071296%; 341/402/547.

## V167 Bass admitted-event repitch sweep — FROZEN NEGATIVE
- Code blob `2b59bb1dcb2b5724eb56457349639ec6eb6eca83`; run `33228058021`, job `99035528898`; terminal `b3425afd6ffd06ab367a18edd3ce4d63242f7659`.
- Best `baseline_current`; delta 0.0pp. Existing admitted-event state/pYIN repitching does not improve Bass.

## Frozen source/evidence boundary
- Source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; frozen V166 timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`.
- Historical CPU stack: Python 3.10.21, torch 2.8.0+cpu, Demucs 4.1.0 `htdemucs_6s`, CPU, shifts=1, jobs=1.
- Evidence run `33228322645`, job `99036292089`; terminal `86ab5882845b61917b8820c35b07022adef532f0`.
- Evidence pool `debug/v167-single-song-calibration/nearmiss-evidence-pool.json`, blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Evidence receipt blob `8268eb6eeb0bbb00b98bcf3dcf2812c8a55932a3`, status `EVIDENCE_POOL_FROZEN`.
- Exact V166 musical reproduction 1050 Guitar / 402 Bass; reference/scorer reads 0; tuning=false; candidate generation modified=false; GPU/CUDA/Modal=false; `main`/Production=false.
- Guitar standalone harmonic pool: **272 sites / 13,328 candidates**. Bass pre-admission pool: **913 sites / 36,520 candidates**.

## V167 upstream-recovery sweep — FROZEN / TERMINAL
- Base generator blob `24413d321f64bbfcce48812ceb85b4593dcfa80c`; corrected adapter blob `fbbee07493084792912c774d375ca5011672891f`; grader blob `32304261ff9e6bec00d22eabea08cf5070cd3d3e`.
- 146 complete variants froze before reference scoring: 49 Guitar and 97 Bass.
- First arm `8880dab...`, run `33253264878`, job `99102488179`: safe pre-score generation failure; grading skipped; zero reference-facing scores. Corrected inherited Bass collision guard before re-arm.
- Corrected arm `168113eed4e053a97220ab8ad9daefb189d5fd93`; successful run `33253434886`, job `99102944880`; terminal `0c74a6916e046d202cc5cf775f974bbd06fcf567`.
- Manifest blob `0ee153dbf1004d921c586516bca91e52f7bb1fde`, SHA256 `c91ee15d702746e082c059b5f99c44fcfa7a89f18e5e9f2fc81eb6513d1baa80`.
- Report blob `324f1f4e68951ac8653c51c8a436e4d35e5dc16b`, SHA256 `1bcc5eca05df31270ff7ff638cca6def3166a0e5084c4874d70d710d4696836f`.
- Receipt blob `a502e6fbc04d6423177c45c9dad418cede22c2d9`, status `UPSTREAM_RECOVERY_SWEEP_FROZEN`.
- Policy: variants frozen before reference read=true; per-event reference selection=false; post-score mutation=false; GPU/CUDA/Modal=false; `main`/Production=false.

### Frozen Guitar sweep result
- Winner `g-baseline`; I002 unchanged.
- F1 **41.9156774457634%**; precision 48.76190476190476%; recall 36.755204594400576%; 512/1050/1393.
- Delta 0.0pp. All 48 additive standalone-harmonic rules are terminal negative in the first absolute-threshold grid.

### Frozen Bass sweep winner
- Rule `b-r975-o50-a10-low_register_no_stable_state`: template rank >=0.975, onset >=0.50, activity >=0.10, fundamental required, MIDI <=40, no nearby stable state, I002 events preserved, additions only on previously empty corrected steps.
- Frozen minimal candidate SHA256 `2e04edd9cb61795ea9679ce899c7ded9549bb0f5d9f8e04a5d53fdf07ec9fa13`.
- Added 110 events; primary F1 **80.45325779036827%** = 426/512/547; precision 83.203125%; recall 77.87934186471663%; FP86/FN121.
- Delta vs I002: **+8.588136610178598pp F1**, -1.622745646766166pp precision, +15.539305301645335pp recall.

## V167 Iteration 003 — CURRENT BEST / FROZEN
- Promotion transform `validation/v167_single_song_calibration/promote_upstream_recovery_winner_v167.py`, blob `9c63f2a0c4732cf3c3a11faf028cf0952c27664e`, commit `8f2c4628a8c1448cf1b33bd521c2e133fb600e98`.
- Arm `157bf0ed3514d106a9888d6877183e9a54e462d3`; workflow run `33253690563`, job `99103631893`; all steps SUCCESS.
- Terminal self-seal `17ab31bf26fa1e15a7754469b7598c071a938705`; workflow deleted.
- Candidate `debug/v167-single-song-calibration/iteration-003-generated.json`: blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- Proof blob `60dba77ac478ed804fd5d66993878e4921c4a72d`, SHA256 `35cb7c95252e4000cc522cd474616b5a0265731ab2454ea123d7756b7872059d`.
- Receipt blob `b3979dd5b6b205a072223493248fc66b37272a5c`, status `ITERATION_003_FROZEN`.
- Reconstructed already-scored winner SHA exactly `2e04edd9...` before promotion.
- Guitar: 1050 ->1050, rich list exactly preserved, normalized equal scored winner=true.
- Bass: 402 +110 ->512, all prior rich event dictionaries preserved, normalized equal scored winner=true.
- Zero new reference-facing scores; reference/scorer read by promotion=false; post-sweep retuning=false; GPU/CUDA/Modal=false; `main`/Production=false.

### Frozen I003 inherited metrics
- **Guitar:** F1 **41.9156774457634%**, precision **48.76190476190476%**, recall **36.755204594400576%**, 512/1050/1393.
- **Bass:** F1 **80.45325779036827%**, precision **83.203125%**, recall **77.87934186471663%**, 426/512/547; FP86/FN121; gross F1 83.09726156751652%; same-measure pitch-content F1 84.04154863078376%.

## Guitar aggregate diagnosis — STAGED / NO NEW REFERENCE ACCESS
- Analyzer `validation/v167_single_song_calibration/analyze_guitar_recovery_sweep_v167.py`, blob `c6fedb0f5b8404ff472495362e7b37ecdf734f15`, commit `9f62891686f5bfeef303c11012e7d427916da4aa`.
- Inputs only: terminal sweep report SHA256 `1bcc...` and immutable reference-blind evidence pool SHA256 `1c983...`.
- It reads no professional reference, no scorer, and no per-event match assignments; new reference-facing score calls=0.
- It will summarize all 48 nonbaseline Guitar whole rules: top variants, additions, F1/precision/recall deltas, factor-level behavior, addition-count buckets, and correlations between added events and aggregate score deltas.
- Separately, it will analyze reference-blind site structure across all 272/13,328 Guitar evidence rows: active-pitch count, eligible inactive candidates, top-inactive/template-score strength relative to existing active pitches, top-vs-second evidence gaps, and nearest active semitone-distance distribution.
- This analysis itself selects no new rule. Its only allowed use is to preregister a structurally new deterministic whole-rule family without per-event reference choices.

## NEXT boundary — one-shot aggregate Guitar diagnosis
1. Run/freeze the aggregate analyzer on `v143-contextual-prune-lobo`, pinned to blob `c6fedb0...`, sweep report `324f1...`, and evidence pool `aa7da3...`.
2. Record exact best nonbaseline whole rule, addition/F1/precision/recall trends, factor summaries, and reference-blind structural distributions.
3. Use those aggregate/reference-blind findings to define a new contextual Guitar hypothesis only if there is a clear mechanistic basis. Do not simply broaden the terminal negative absolute-threshold grid.
4. Any new Guitar sweep must be fully preregistered before reference scoring and must keep I003 Bass exactly frozen.
5. Do not create I004 unless a new frozen whole-rule Guitar sweep materially beats I003 Guitar with a defensible precision/recall tradeoff.
6. CPU only; fresh explicit authorization before GPU/CUDA/Modal. Never modify/merge/promote `main` or Production without explicit user direction.
