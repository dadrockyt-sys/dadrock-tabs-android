# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 is now frozen current best. Guitar inherits the already-scored terminal state-split winner `gss-active-only` at 42.7940586109996% F1; Bass remains exactly I003/I004 at 80.45325779036827% F1. I005 was promoted deterministically with zero new scorer/reference reads: the score-minimal winner was regenerated from immutable I003 + frozen reference-blind evidence/timebase and matched the already-scored winner SHA256 exactly before the rich I005 candidate was written. All original I003 Guitar dictionaries are preserved, exactly 48 frozen winner additions are present, and Bass is rich-list identical across I003/I004/I005. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used. The next research boundary is aggregate/reference-blind diagnosis of the terminal state-split family and I005 structure before preregistering any new Guitar family.**

## Current execution checkpoint — I005 FROZEN / NEXT FAMILY NOT YET PREREGISTERED
- I005 arm commit `6f54d0b672e4d7e2b0ced4da5cb8566b7e324712`; terminal self-removing commit `489a23ce75c1c39c3287a2ffd5aae5b3f10cac08`.
- I005 promotion workflow run `33264957530`, job `99133281983`, attempt 1; all critical guard/reconstruction/self-seal steps passed.
- Promoter `validation/v167_single_song_calibration/promote_state_split_guitar_winner_v167.py`: blob `a912018b58f9bd7243229fcba3d8895e33300c44`.
- I005 candidate `debug/v167-single-song-calibration/iteration-005-generated.json`: blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Promotion proof `debug/v167-single-song-calibration/iteration-005-promotion-proof.json`: blob `668128054f5ad644055913833cd07ef197bce538`, SHA256 `a286b96819dacba1d4e1cf7aa84589a29279df0b02b4104ced5d5a7c77e2ca15`.
- Freeze receipt `debug/v167-single-song-calibration/iteration-005-freeze-receipt.json`: blob `85a3280910e8f5cc257ea30e3047d3ea51f85a20`, status `ITERATION_005_FROZEN`.
- Regenerated score-minimal winner SHA256 `aa042135c542f2025522bb0d8ab9491c8457bf95025db5953b714d452afc0d5e` exactly equals the already-scored frozen state-split winner.
- New reference-facing score calls during I005 promotion: **0**. Professional reference read by promotion=false; scorer read by promotion=false.

## Iteration 005 — FROZEN CURRENT BEST
### Guitar — `gss-active-only`
- F1 **42.7940586109996%**; precision **48.54280510018215%**; recall **38.26274228284279%**.
- 533 matched / 1098 generated / 1393 reference; FP 565; FN 860.
- Delta vs I004: F1 **+0.17634113294692222pp**; precision **+0.5643684425002127pp**; recall **-0.07178750897343655pp**; matched -1; generated -15; FP -14; FN +1.
- I005 Guitar = all **1050** original rich I003 Guitar dictionaries + exactly **48** frozen state-split additions = **1098** events.
- Construction-base rich dictionary multiset preserved exactly=true; new coordinates disjoint from I003=true; new coordinates unique=true; normalized Guitar exactly equals the frozen scored winner=true.
- Structural rule: rank >=0.975; activity >=0.05; onset >=0.50; Basic-Pitch active context required; `fundamentalPresent`; top-1/site; cap 6; active candidate/max-active ratio >=1.00; nearest different active intervals {12,19,24} rejected; inactive branch disabled.

### Bass — closed / identical I003-I005
- F1 **80.45325779036827%**; precision **83.203125%**; recall **77.87934186471663%**.
- 426 matched / 512 generated / 547 reference; FP 86; FN 121.
- Rich list exactly preserved across I003/I004/I005=true; normalized equal I004=true; no Bass score call occurred during state-split sweep promotion.

## Frozen state-split sweep — terminal source of I005 winner
- Manifest blob `fc5202898adc0d8aabdfce0e02c019f32443a4a1`, SHA256 `113add46d50e423708972ed18eb88df48ec1d60968e75d5e251f609f84a365e4`.
- Report blob `d26e4128479f760c23fe6c449cc4b3ec5ad7219b`, SHA256 `f4dfd04849eab3f15290cadb2b9ff0a2903bc6174beb428b35c71aa7c7347562`.
- Receipt blob `c40cd73d857c4d42d87c41c95d17d47be5f15e3c`, status `STATE_SPLIT_GUITAR_SWEEP_FROZEN`.
- Reproduction control `gss-repro-q100-noharm` normalized exactly to I004 Guitar/Bass and received 0 score calls.
- Scoring boundary held: exactly 5 Guitar calls = I004 baseline + four new whole rules; 0 Bass calls; 0 reproduction-control calls.
- All four new rules beat I004. Winner `gss-active-only`.
- `gss-active-only`: 48 active / 0 inactive additions, F1 42.7940586109996%.
- `gss-inactive-q125-noharm`: 47 active +10 inactive additions, F1 42.72%.
- `gss-inactive-q100-chord`: 47 active +10 inactive additions, F1 42.64000000000001%.
- `gss-inactive-q125-chord`: also beat I004; terminal report/receipt remains source of truth for exact metrics.
- Whole-rule interpretation: disabling the inactive branch improved the precision/FP tradeoff most strongly; no individual candidate is labeled by reference as true/false by this conclusion.

## Frozen I004 prior best
- Guitar F1 **42.617717478052675%**; precision 47.97843665768194%; recall 38.334529791816224%; 534/1113/1393; FP579/FN859.
- I004 contained 63 contextual additions = 46 Basic-Pitch-active +17 inactive.
- I005 has net -15 Guitar events versus I004 while gaining +0.17634113294692222pp F1 and +0.5643684425002127pp precision.

## Immutable source/evidence boundary
- I003 blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- I004 blob `8dd85049a65f00541f7874ff99511b081a0b5ff2`, SHA256 `728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc`.
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Evidence pool blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Frozen V166 timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`, SHA256 `899746d3048d239bc0032375d412a109ea04b055df19df1b7b08dc3e73aa5ca0`.
- Base recovery builder blob `24413d321f64bbfcce48812ceb85b4593dcfa80c`.
- State-split builder blob `6b480d43744a5c67c02510d55162581d896afee4`.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.

## Standing V167 methodology
- Calibration only; never present V167 scores as holdout/generalization performance.
- Reference/scorer may grade complete predeclared whole variants only. No per-event reference choices or direct reference-event copying.
- I003, I004, and I005 are immutable.
- Bass is closed and must remain exactly I005/I004/I003 in future Guitar-only work.
- Frozen state-split sweep is terminal; do not rescore or retune that same family.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — aggregate/reference-blind post-I005 diagnosis
1. Re-read exact branch head/checkpoint, frozen state-split report/receipt, I004/I005 identities, and frozen evidence pool.
2. Do **not** read professional reference/scorer and do not perform any new score call.
3. Analyze only aggregate whole-rule state-split results plus reference-blind structural evidence to explain why active-only wins and identify whether another genuinely new sparse Guitar hypothesis is defensible.
4. Useful structural questions: where the 48 active additions sit relative to active-pitch multiplicity, candidate/max-active score ties, nearest-active intervals, onset/activity support, and whether a stricter reference-blind subfamily could reduce FP without collapsing recall.
5. Any next family must be small, structurally distinct, preregistered before scoring, and must keep Bass exactly I005. Do not use per-event reference assignments to choose events or thresholds.
6. Save the aggregate diagnosis and checkpoint before arming any new reference-facing sweep.
7. CPU only; no GPU/CUDA/Modal. Never modify `main` or Production.
