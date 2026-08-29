# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 remains frozen current best: Guitar `gss-active-only` **42.7940586109996% F1**, Bass **80.45325779036827% F1**. The active-topology sweep is terminal negative and closed: none of its 3 new Guitar rules beat I005, so no I006 exists or is eligible. A genuinely new reference-blind temporal/recurrence analyzer is now staged but has not run. It will inspect only the exact 48 frozen I005 additions, immutable I003/I005 coordinates, and terminal aggregate reports; it has no scorer/reference input and selects no rule. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Temporal/recurrence diagnosis — STAGED / NOT RUN
- Analyzer `validation/v167_single_song_calibration/analyze_post_topology_temporal_recurrence_v167.py`: commit `fb123eacb7084815231d7d42d7b23d553e81d9c9`, blob `156f0f2adc202b3868791514f31594426cadf0d0`.
- Inputs fixed: I003 SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`; I005 SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`; terminal topology report SHA256 `869825ed2a91e9f50bc6ca5ac71d922ee93dc17dd5804bf8d94d0e951e179b85`; prior post-I005 diagnosis SHA256 `fe7e826724a11e115a25f932d4b58ed88e3aedae67fb54142cc532cc40ab8450`.
- Analyzer measures a new structural dimension only: nearest prior/next I005 addition, same-MIDI addition recurrence, nearest prior/next immutable-base event, same-MIDI base-event spacing, short grid-step clusters, and repeated-MIDI runs.
- Thresholds `{1,2,3,4,6,8,12,16,24,32}` are diagnostic reporting bins only; the analyzer does **not** select a threshold/rule.
- Policy hard-coded in output: professional reference read=false; scorer read=false; new reference-facing score calls=0; per-event reference match assignments=false; new rule selected=false; GPU/CUDA/Modal=false; main/Production=false.
- Planned output `debug/v167-single-song-calibration/post-topology-temporal-recurrence-analysis.json`; no output/receipt exists yet.

## Active-topology sweep — FROZEN / TERMINAL NEGATIVE
- Scoring run `33265672682`, job `99135186427`; terminal commit `840c800feeaffc21b2ef77cb98a6ac61676e2c92`.
- Report blob `4aab67d913b4b68cc518825d4495a48c3b9e76fc`, SHA256 `869825ed2a91e9f50bc6ca5ac71d922ee93dc17dd5804bf8d94d0e951e179b85`.
- Receipt blob `344bd76334367e5cb3d02f361703386842a2d3dd`, status `ACTIVE_TOPOLOGY_GUITAR_SWEEP_FROZEN`.
- Score calls exactly Guitar=3, Bass=0, reproduction=0. New variants beating I005=0; meeting I006 eligibility=0. No I006 created.
- `topo-single-or-chord`: -0.04043542259379862pp F1 vs I005, +0.12813898781051658pp precision; removed 7 events, lost 2 matches, removed 5 FP.
- `topo-single-only`: -0.2960861860198727pp F1; removed 25, lost 9 matches, removed 16 FP.
- `topo-chord-only`: -0.6160821786550197pp F1; removed 30, lost 14 matches, removed 16 FP.
- Do not retune/extend the same topology subset family post-score.

## Iteration 005 — FROZEN CURRENT BEST
- Guitar: F1 **42.7940586109996%**, P **48.54280510018215%**, R **38.26274228284279%**; 533/1098/1393; FP565/FN860.
- I005 candidate blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass closed: F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.

## Standing V167 methodology
- Calibration only; no holdout/generalization claim.
- I003/I004/I005 and terminal sweeps immutable. Active-topology family closed.
- No per-event reference choices, direct reference-event copying, or post-score retuning.
- Bass closed. CPU authorized; fresh explicit authorization required before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — run/freeze temporal recurrence diagnosis
1. Create one self-removing CPU-only workflow from this exact checkpoint parent.
2. Verify I003/I005/topology-report/prior-diagnosis identities, analyzer blob `156f0f2adc202b3868791514f31594426cadf0d0`, and checkpoint identity.
3. Assert analyzer has no scorer/reference CLI/path; compile and run once.
4. Require output status `POST_TOPOLOGY_TEMPORAL_RECURRENCE_REFERENCE_BLIND_ANALYSIS_FROZEN`, addition count=48, policy reference/scorer/per-event matches=false, new score calls=0, rule selected=false.
5. Freeze analysis + receipt and self-remove workflow; checkpoint findings before proposing any new family.
6. CPU only; no GPU/CUDA/Modal; never modify main/Production.
