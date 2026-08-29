# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 is frozen current best. Guitar inherits the already-scored terminal state-split winner `gss-active-only` at 42.7940586109996% F1; Bass remains exactly I003/I004 at 80.45325779036827% F1. I005 is immutable. The first post-I005 reference-blind analyzer run failed safely before writing output because it incorrectly equated pre-grid structural eligibility with the frozen builder's post timing/dedupe/polyphony `eligible` count. The reference-blind boundary itself passed. A corrected rearm analyzer is now staged: it studies the exact 48 frozen I005 additions and their frozen reference-blind evidence directly and does not make the invalid eligibility-count equivalence. No analysis output is frozen yet. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — CORRECTED POST-I005 ANALYZER STAGED / REARM NOT YET RUN
- First analyzer `validation/v167_single_song_calibration/analyze_post_i005_active_only_v167.py`: commit `fdbb26b4ca50f235dbaf459941004194bcf3a7c1`, blob `86a32010f441fb518146f3717ae8d9ab3b94b8ea`.
- First analysis arm commit `e7c40c589017dc5027bbf4aaaee574cfe4bbd425`; run `33265180179`, job `99133883024`, attempt 1.
- Immutable/reference-blind guard step passed. Analyzer step failed with `RuntimeError: active-only current-rule eligible site count no longer equals 48` before receipt/self-seal; therefore no frozen analysis artifact or receipt was created.
- Failure mechanism is methodological/tooling only: the analyzer's local structural test omitted frozen timing correction, `(step,midi)` dedupe, and polyphony-cap guards used by the state-split builder, so a pre-grid count was incorrectly asserted equal to the builder's post-grid `eligible=48` summary.
- Corrected analyzer `validation/v167_single_song_calibration/analyze_post_i005_active_only_v167_rearm.py`: commit `70ace4cd7d7594ee89c8ab341bdbdde9059eec3d`, blob `82ec287869102ab6af949afa174a2543768dbc55`.
- Corrected boundary: the exact 48 frozen I005 additions are the authoritative post-grid selected set. The evidence pool is used only to characterize those selected sites (active-pitch multiplicity, max-active ties, candidate competition, intervals, onset/activity/rank distributions). It does not infer a new post-grid eligible count from incomplete structural predicates.
- Corrected analyzer still has no professional-reference/scorer input, reads no per-event reference matches, performs 0 new reference-facing score calls, and sets `newRuleSelectedByThisAnalysis=false`.
- The failed workflow file remains on branch only because its self-removal step was skipped after failure; it must be rearmed by updating that same workflow from an exact checkpoint parent, not rerun as-is.

## Iteration 005 — FROZEN CURRENT BEST
### Guitar — `gss-active-only`
- Candidate `debug/v167-single-song-calibration/iteration-005-generated.json`: blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Promotion proof blob `668128054f5ad644055913833cd07ef197bce538`, SHA256 `a286b96819dacba1d4e1cf7aa84589a29279df0b02b4104ced5d5a7c77e2ca15`.
- Freeze receipt blob `85a3280910e8f5cc257ea30e3047d3ea51f85a20`, status `ITERATION_005_FROZEN`.
- F1 **42.7940586109996%**; precision **48.54280510018215%**; recall **38.26274228284279%**.
- 533 matched / 1098 generated / 1393 reference; FP 565; FN 860.
- Delta vs I004: F1 **+0.17634113294692222pp**; precision **+0.5643684425002127pp**; recall **-0.07178750897343655pp**; matched -1; generated -15; FP -14; FN +1.
- I005 Guitar = all **1050** original rich I003 Guitar dictionaries + exactly **48** frozen state-split additions = **1098** events.
- Normalized Guitar exactly equals frozen scored winner SHA256 `aa042135c542f2025522bb0d8ab9491c8457bf95025db5953b714d452afc0d5e`.
- Structural rule: rank >=0.975; activity >=0.05; onset >=0.50; Basic-Pitch active context required; `fundamentalPresent`; top-1/site; cap 6; active candidate/max-active ratio >=1.00; nearest different active intervals {12,19,24} rejected; inactive branch disabled.

### Bass — closed / identical I003-I005
- F1 **80.45325779036827%**; precision **83.203125%**; recall **77.87934186471663%**.
- 426 matched / 512 generated / 547 reference; FP 86; FN 121.
- Rich list exactly preserved across I003/I004/I005=true; normalized equal I004=true.

## Frozen state-split sweep — terminal source of I005 winner
- Manifest blob `fc5202898adc0d8aabdfce0e02c019f32443a4a1`, SHA256 `113add46d50e423708972ed18eb88df48ec1d60968e75d5e251f609f84a365e4`.
- Report blob `d26e4128479f760c23fe6c449cc4b3ec5ad7219b`, SHA256 `f4dfd04849eab3f15290cadb2b9ff0a2903bc6174beb428b35c71aa7c7347562`.
- Receipt blob `c40cd73d857c4d42d87c41c95d17d47be5f15e3c`, status `STATE_SPLIT_GUITAR_SWEEP_FROZEN`.
- Scoring boundary held: exactly 5 Guitar calls = I004 baseline + four new whole rules; 0 Bass calls; 0 reproduction-control calls.
- All four new rules beat I004. Winner `gss-active-only`.
- `gss-active-only`: 48 active / 0 inactive additions, F1 42.7940586109996%.
- `gss-inactive-q125-noharm`: 47 active +10 inactive additions, F1 42.72%.
- `gss-inactive-q100-chord`: 47 active +10 inactive additions, F1 42.64000000000001%.
- `gss-inactive-q125-chord`: also beat I004; terminal report remains source of truth for exact metrics.
- Whole-rule interpretation: disabling the inactive branch improved the precision/FP tradeoff most strongly; no individual candidate is labeled by reference as true/false by this conclusion.

## Frozen contextual sweep aggregate source
- Report `debug/v167-single-song-calibration/contextual-guitar-recovery-sweep.json`: blob `b00e25f5c1fd9f8c40b440156e049317e008ec1d`, SHA256 `6b661f6dfa27d31204f4e8a9035d286d5324440b947eb3e49db99205dad9320e`.
- Used only at whole-rule aggregate level to compare pre-existing onset 0.50 vs 0.65 variants with otherwise matching configs. No per-event scorer assignments are used.

## Immutable source/evidence boundary
- I003 blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- I004 blob `8dd85049a65f00541f7874ff99511b081a0b5ff2`, SHA256 `728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc`.
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Evidence pool blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Frozen V166 timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`, SHA256 `899746d3048d239bc0032375d412a109ea04b055df19df1b7b08dc3e73aa5ca0`.
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

## NEXT boundary — rearm corrected aggregate/reference-blind diagnosis
1. Update the existing failed self-removing workflow from this exact checkpoint parent; do not rerun the failed workflow unchanged.
2. Point it to corrected analyzer blob `82ec287869102ab6af949afa174a2543768dbc55`; verify frozen contextual report, state-split report, evidence pool, I003, I005, and checkpoint identities.
3. Compile corrected analyzer and assert it contains no professional-reference/scorer path or CLI input.
4. Run once; require status `POST_I005_AGGREGATE_REFERENCE_BLIND_ANALYSIS_FROZEN`, exactly 48 I005 additions / 48 unique selected sites, and policy showing 0 reference/scorer/per-event match access.
5. Freeze `post-i005-active-only-aggregate-analysis.json` and receipt; self-remove workflow.
6. Read frozen diagnosis and checkpoint before deciding or preregistering any new Guitar family.
7. CPU only; no GPU/CUDA/Modal. Never modify `main` or Production.
