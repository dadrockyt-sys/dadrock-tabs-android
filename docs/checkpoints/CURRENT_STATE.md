# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 remains frozen current best: Guitar `gss-active-only` **42.7940586109996% F1**, Bass **80.45325779036827% F1**. The active-topology family is terminal negative/closed and no I006 exists. The new reference-blind temporal/recurrence diagnosis is now terminal/frozen and identifies a sparse, genuinely new structural hypothesis: collapse only short same-MIDI bursts among the 48 frozen I005 additions. A small recurrence family is preregistered below but not yet implemented/generated/scored. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Temporal/recurrence diagnosis — FROZEN / TERMINAL
- Analyzer `validation/v167_single_song_calibration/analyze_post_topology_temporal_recurrence_v167.py`: blob `156f0f2adc202b3868791514f31594426cadf0d0`.
- Analysis arm commit `b2c7ffc70ae4e2cce2bb5d124187295e3a6630a8`; run `33265800855`, job `99135533246`; terminal self-removing commit `75b08205f556212e940e410ac3e18cec2c4ef0bf`.
- Analysis `debug/v167-single-song-calibration/post-topology-temporal-recurrence-analysis.json`: blob `42a4d4bd9c016b5aee74a14eea4b78fb601a6b6e`, SHA256 `fd5c12339e594ae1207e2c4edb2eb034a9249de15ab99d3623cf5f6922061b36`.
- Receipt `debug/v167-single-song-calibration/post-topology-temporal-recurrence-analysis-receipt.json`: blob `baefc8c8a9fdceb6a53ac3b1e3838210a19c01c4`, status `POST_TOPOLOGY_TEMPORAL_RECURRENCE_ANALYSIS_FROZEN`.
- Policy: reference read=false; scorer read=false; new reference-facing score calls=0; per-event reference match assignments=false; new rule selected=false; GPU/CUDA/Modal=false; main/Production=false.

### Frozen recurrence structure for exact 48 I005 additions
- 48 additions occupy 48 unique grid steps.
- Nearest other addition, any MIDI: median **4.5** steps; 13/48 within 1 step, 20/48 within 2, 24/48 within 4.
- Nearest other addition, same MIDI: 44 have another same-MIDI addition; median **33** steps. Only **9/48** are within 1 same-MIDI step and **14/48** within 2.
- Nearest immutable I003 base event, same MIDI: all 48 within **6** steps; median **1.5**; 24 within1, 42 within2. This broad base-proximity feature affects nearly the entire recovery set and is not a sparse discriminator, so do not build the next family around it.
- Exact same-MIDI gap<=1 connected bursts:
  - MIDI64 steps `[1237,1238]`
  - MIDI64 steps `[1750,1751,1752]`
  - MIDI69 steps `[1405,1406]`
  - MIDI81 steps `[1341,1342]`
  Total burst events=9; collapsing each burst to one event prunes exactly **5**, retaining **43/48** additions.
- Exact same-MIDI gap<=2 connected bursts additionally include MIDI67 `[1410,1412]`, MIDI71 `[1435,1437]`, and extend MIDI64 to `[1750,1751,1752,1754]`; six components contain 14 events total, so collapsing each to one prunes exactly **8**, retaining **40/48** additions.

### Reference-blind evidence within gap1 bursts
- The deterministic “strongest” selector is preregistered as max onset support, then max activity support, then earlier grid step. It is not based on reference outcomes.
- It differs from earliest selection in the observed frozen evidence:
  - MIDI64 `[1237,1238]`: onset ties at 1.0; activity favors 1238.
  - MIDI81 `[1341,1342]`: onset favors 1342 (1.0 vs 0.85884).
  - MIDI69 `[1405,1406]`: onset/activity favor 1406.
  - MIDI64 `[1750,1751,1752]`: onset ties at 1.0 for 1751/1752; activity favors 1751 over 1752; earliest would keep 1750.
- This makes “earliest” vs “strongest evidence” two genuinely distinct deterministic burst-resolution rules without any reference-facing event choice.

## Preregistered next family — same-MIDI burst collapse
All variants keep all 1050 immutable I003 Guitar events. Only the exact 48 frozen I005 additions may be filtered. Bass remains exactly I005. No onset/activity/rank threshold sweep is added.
- `recur-repro-i005`: exact I005, all48 additions; no-score reproduction control.
- `recur-gap1-earliest`: for each same-MIDI addition connected component whose consecutive grid gaps are <=1, keep only earliest; expected additions **43**, Guitar count **1093**.
- `recur-gap1-strongest`: same gap<=1 components, keep only max onset support, then max activity support, then earliest; expected additions **43**, Guitar **1093**.
- `recur-gap2-strongest`: same-MIDI components with consecutive gaps <=2, keep only strongest by same evidence ordering; expected additions **40**, Guitar **1090**.
- This family is distinct from the closed topology family and uses only frozen temporal/reference-blind evidence.
- Freeze all candidate hashes before any reference/scorer read. Planned score calls: exactly Guitar **3**, Bass **0**, reproduction **0**.
- Selection: max Guitar F1, then precision, fewer kept additions, lexicographic id.
- Scorer workflow may not create I006. Separate I006 promotion eligibility remains conservative: winner must gain **>=+0.10pp F1 vs I005** and have **precision >= I005**.

## Active-topology sweep — CLOSED
- Terminal report blob `4aab67d913b4b68cc518825d4495a48c3b9e76fc`, SHA256 `869825ed2a91e9f50bc6ca5ac71d922ee93dc17dd5804bf8d94d0e951e179b85`.
- 3 Guitar calls /0 Bass /0 reproduction; none beat I005; 0 I006-eligible. Do not retune/extend topology subsets.

## Iteration 005 — FROZEN CURRENT BEST
- Guitar: F1 **42.7940586109996%**, P **48.54280510018215%**, R **38.26274228284279%**; 533/1098/1393; FP565/FN860.
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Bass closed: F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%; 426/512/547; FP86/FN121.

## Standing V167 methodology
- Calibration only; no holdout/generalization claim.
- I003/I004/I005 and terminal sweeps immutable. Topology family closed.
- No per-event reference choices, direct reference-event copying, or post-score retuning.
- Bass closed. CPU authorized; fresh explicit authorization required before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — implement and freeze recurrence candidates reference-blind
1. Implement generator + grader exactly for the preregistered four variants above; do not add variants or thresholds.
2. Checkpoint implementation blobs before candidate generation.
3. Run a separate self-removing generation-only workflow with no scorer/reference input; require kept-addition counts 48/43/43/40 and Bass exact I005.
4. Freeze manifest/candidate hashes/receipt before any scoring.
5. Checkpoint frozen candidate identities, then arm a separate exactly-3-call Guitar scorer workflow using the existing frozen scorer/reference. Bass/reproduction receive 0 calls; no I006 auto-promotion.
6. CPU only; no GPU/CUDA/Modal; never modify main/Production.
