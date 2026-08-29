# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. The preregistered state-split Guitar sweep is terminal/frozen. All four genuinely new state-split rules beat frozen I004 Guitar. The frozen whole-rule winner is `gss-active-only` at 42.7940586109996% Guitar F1, +0.17634113294692222pp versus I004, while Bass remains exactly frozen I003/I004 at 80.45325779036827% F1 and received 0 score calls. A separate deterministic NO-RESCORE I005 promoter is now staged in code but no I005 workflow is armed and no I005 artifact exists yet. The promoter regenerates `gss-active-only` from immutable I003 + frozen reference-blind evidence/timebase, requires exact score-minimal SHA equality to the already-scored winner, preserves every rich I003 Guitar dictionary, preserves Bass exactly across I003/I004/I005, and performs 0 scorer/reference reads. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — I005 PROMOTER STAGED / WORKFLOW NOT ARMED
- State-split arm commit `7e3c73c45d8b29e7ebf9a0a79b38bf5098ff5f7f`; terminal self-removing sweep commit `3bf85f51b5972faa0b9cf36cfe6f625ecab24556`.
- State-split workflow run `33258368926`, attempt 1.
- I005 promoter `validation/v167_single_song_calibration/promote_state_split_guitar_winner_v167.py`: commit `c2fee53c5f2f2fb123f534b7001daef39174ffb4`, blob `a912018b58f9bd7243229fcba3d8895e33300c44`.
- Promoter contains no professional reference/scorer input or import. It requires frozen I003/I004/pool/manifest/report identities, terminal state-split receipt identity, frozen base/state-builder blobs, exact winner id/config/summary/metrics, and exact regenerated winner SHA256 before writing I005.
- I005 logical parent is I004, but construction base is immutable I003 because the scored state-split family was defined from I003. This is explicit in the staged transform.
- No I005 workflow exists yet; no I005 candidate/proof/receipt exists; zero new reference-facing score calls have occurred after the state-split sweep.

## Frozen state-split sweep identities
- Manifest `debug/v167-single-song-calibration/state-split-guitar-sweep-manifest.json`: blob `fc5202898adc0d8aabdfce0e02c019f32443a4a1`, SHA256 `113add46d50e423708972ed18eb88df48ec1d60968e75d5e251f609f84a365e4`.
- Report `debug/v167-single-song-calibration/state-split-guitar-sweep.json`: blob `d26e4128479f760c23fe6c449cc4b3ec5ad7219b`, SHA256 `f4dfd04849eab3f15290cadb2b9ff0a2903bc6174beb428b35c71aa7c7347562`.
- Receipt `debug/v167-single-song-calibration/state-split-guitar-sweep-receipt.json`: blob `c40cd73d857c4d42d87c41c95d17d47be5f15e3c`, status `STATE_SPLIT_GUITAR_SWEEP_FROZEN`.
- Generator blob `6b480d43744a5c67c02510d55162581d896afee4`; grader blob `7e5068ce607d7f817429d39ea363840c7ba8d51e`.
- Reproduction control `gss-repro-q100-noharm`: SHA256 `63f9beaf41907bf13a734df18d7711925166b311ba5b950414ab27ca9f751bc9`; normalized Guitar exactly I004=true; normalized Bass exactly I004=true; score calls 0.
- Score-call boundary held exactly: Guitar 5 = I004 baseline + four new rules; Bass 0; reproduction control 0.
- All four new rules beat I004. No event-level reference choices, no post-score mutation/retuning, no automatic I005.

## Frozen state-split winner — `gss-active-only`
- Candidate SHA256 `aa042135c542f2025522bb0d8ab9491c8457bf95025db5953b714d452afc0d5e`.
- Guitar F1 **42.7940586109996%**; precision **48.54280510018215%**; recall **38.26274228284279%**.
- 533 matched / 1098 generated / 1393 reference; FP 565; FN 860.
- Delta vs I004: F1 **+0.17634113294692222pp**; precision **+0.5643684425002127pp**; recall **-0.07178750897343655pp**; matched -1; generated -15; FP -14; FN +1.
- Additions vs I003: **48**, all Basic-Pitch-active/max-active branch; inactive additions **0**.
- Structural config fixed: rank >=0.975; activity >=0.05; onset >=0.50; Basic-Pitch active context required; inherited `fundamentalPresent`; top-1/site; cap 6; active candidate ratio >=1.00; reject nearest different active intervals {12,19,24}; inactive branch disabled.
- Interpretation at whole-rule level only: the previously retained inactive branch contributed more false positives than useful recall. This is a rule-level calibration conclusion, not an event-level truth label or generalization claim.

## Other frozen state-split results
- `gss-inactive-q125-noharm`: Guitar F1 42.72%; +0.10228252194732224pp vs I004; 534 matched / 1107 generated; 57 additions = 47 active +10 inactive.
- `gss-inactive-q100-chord`: Guitar F1 42.64000000000001%; +0.022282521947331047pp vs I004; 533 matched / 1107 generated; 57 additions = 47 active +10 inactive.
- `gss-inactive-q125-chord`: also beat I004; terminal report/receipt remains source of truth for its exact metrics.
- Winner ranking preregistered: max Guitar F1, then max precision, fewer additions vs I003, lexicographic rule id.

## Frozen I004 prior best
### Guitar — `gctx-o50-q100-allow-noharm`
- F1 **42.617717478052675%**; precision **47.97843665768194%**; recall **38.334529791816224%**.
- 534 matched / 1113 generated / 1393 reference; FP 579; FN 859.
- I004 Guitar 1113 = all 1050 rich I003 Guitar events +63 contextual additions.

### Bass — closed / exactly I003
- F1 **80.45325779036827%**; precision **83.203125%**; recall **77.87934186471663%**.
- 426 matched / 512 generated / 547 reference; FP 86; FN 121.

## Immutable source/evidence boundary
- I003 `debug/v167-single-song-calibration/iteration-003-generated.json`: blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- I004 `debug/v167-single-song-calibration/iteration-004-generated.json`: blob `8dd85049a65f00541f7874ff99511b081a0b5ff2`, SHA256 `728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc`.
- Evidence pool blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Frozen V166 timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`.
- Base recovery builder blob `24413d321f64bbfcce48812ceb85b4593dcfa80c`.
- State-split builder blob `6b480d43744a5c67c02510d55162581d896afee4`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.

## Standing V167 methodology
- Calibration only; never present V167 scores as holdout/generalization performance.
- Reference/scorer may grade complete predeclared whole variants only. No per-event reference choices or direct reference-event copying.
- I003 and I004 are immutable.
- Bass is closed and must remain exactly I004/I003 for every Guitar promotion.
- The frozen state-split report/receipt is terminal; do not rescore this family.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — arm deterministic NO-RESCORE I005 promotion
1. Re-read exact branch head/checkpoint and staged promoter blob `a912018b58f9bd7243229fcba3d8895e33300c44`.
2. Create one self-removing CPU-only workflow from the exact checkpoint parent. It must verify only frozen Git/tree identities and must not read/import scorer/reference.
3. Run the promoter with I003 + I004 + frozen evidence/timebase + frozen state-split manifest/report/receipt. Require regenerated score-minimal winner SHA256 `aa042135c542f2025522bb0d8ab9491c8457bf95025db5953b714d452afc0d5e`.
4. Require rich I005 Guitar = all original I003 dictionaries + exactly 48 winner additions; normalized I005 Guitar = frozen scored winner; rich/normalized Bass = exact I003/I004.
5. Freeze `iteration-005-generated.json`, `iteration-005-promotion-proof.json`, and `iteration-005-freeze-receipt.json`; self-remove workflow. New scorer/reference calls = 0.
6. After I005 is frozen, checkpoint again and only then diagnose/choose the next Guitar hypothesis from aggregate/reference-blind evidence if warranted.
7. CPU only; no GPU/CUDA/Modal. Never modify `main` or Production.
