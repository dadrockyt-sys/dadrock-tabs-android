# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 remains frozen current best: Guitar `gss-active-only` **42.7940586109996% F1**, Bass **80.45325779036827% F1**. The active-topology family is terminal negative/closed and no I006 exists. The temporal/recurrence family remains preregistered and unscored. Its first generation-only freeze attempt failed safely before outputs were frozen because the generator incorrectly expected a `status` field inside the analysis JSON; the freeze status actually lives in the immutable receipt. The generator is now corrected to validate the analysis by immutable SHA + schema + policy + addition count. No recurrence rule, selector, expected count, or scorer boundary changed. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — CORRECTED RECURRENCE GENERATOR / REARM PENDING
- Original generator commit `937f3296e970ae7bf6759c9cb0efb971b0a9c3e0`, blob `9eab55638625f71949f0877369f543459bcf8fda`.
- Grader `validation/v167_single_song_calibration/score_temporal_recurrence_guitar_variants_v167.py`: commit `48e01a18c95dd76d3ed1b5dc4addd4df3bf156e6`, blob `e8251df48d03e94a2d53060bc1e82b4e9d5ba4f7`.
- First generation arm commit `702fd02e7ad259eaf273b9e124cb114f77b84c5e`; run `33266334501`, job `99136937952`, attempt 1.
- Immutable/reference-blind guard step passed. Generation then failed with `RuntimeError: temporal recurrence diagnosis is not frozen` before manifest/receipt/self-seal.
- Failure cause: the frozen analysis JSON schema is `dadrock.tabs.v167.post-topology-temporal-recurrence-analysis.v1` and has immutable SHA/policy but no top-level `status`; status `POST_TOPOLOGY_TEMPORAL_RECURRENCE_ANALYSIS_FROZEN` is in the separate immutable receipt.
- Corrected generator commit `1ceb917e5ed4611092d3a8bf6bf738850bab6859`, blob `2f90e7a8b3e07ae59856f67cf0d299094f482d94`. It validates the exact frozen analysis SHA, expected schema, `additionCount=48`, and reference/scorer/new-rule policy fields.
- No candidate files, manifest, or generation receipt were committed by the failed attempt. No reference/scorer was read; 0 score calls occurred.
- The failed generation workflow file remains because self-removal was skipped. Rearm must update that same workflow from a new exact checkpoint parent; do not rerun the failed arm unchanged.

## Recurrence implementation boundary — unchanged rules
- Generator has no scorer/reference input. It keeps all 1050 immutable I003 Guitar events and filters only the exact 48 frozen I005 additions.
- Exactly four rules exist: `recur-repro-i005`, `recur-gap1-earliest`, `recur-gap1-strongest`, `recur-gap2-strongest`. No thresholds or additional variants were added.
- Expected kept I005 additions remain hard-guarded at **48 / 43 / 43 / 40** respectively; expected Guitar counts **1098 / 1093 / 1093 / 1090**. Bass copied exactly from I005.
- `strongest_evidence` selector remains exactly max frozen onset support, then max frozen activity support, then earlier grid step; no reference outcomes.
- Grader still requires a fully frozen manifest/candidate set before reference/scorer access and remains hard-limited to Guitar **3**, Bass **0**, reproduction **0** score calls. It cannot create I006.

## Temporal/recurrence diagnosis — FROZEN / TERMINAL
- Analyzer `validation/v167_single_song_calibration/analyze_post_topology_temporal_recurrence_v167.py`: blob `156f0f2adc202b3868791514f31594426cadf0d0`.
- Analysis arm commit `b2c7ffc70ae4e2cce2bb5d124187295e3a6630a8`; run `33265800855`, job `99135533246`; terminal self-removing commit `75b08205f556212e940e410ac3e18cec2c4ef0bf`.
- Analysis `debug/v167-single-song-calibration/post-topology-temporal-recurrence-analysis.json`: blob `42a4d4bd9c016b5aee74a14eea4b78fb601a6b6e`, SHA256 `fd5c12339e594ae1207e2c4edb2eb034a9249de15ab99d3623cf5f6922061b36`, schema `dadrock.tabs.v167.post-topology-temporal-recurrence-analysis.v1`.
- Receipt `debug/v167-single-song-calibration/post-topology-temporal-recurrence-analysis-receipt.json`: blob `baefc8c8a9fdceb6a53ac3b1e3838210a19c01c4`, status `POST_TOPOLOGY_TEMPORAL_RECURRENCE_ANALYSIS_FROZEN`.
- Policy: reference read=false; scorer read=false; new reference-facing score calls=0; per-event reference match assignments=false; new rule selected=false; GPU/CUDA/Modal=false; main/Production=false.

### Frozen recurrence structure for exact 48 I005 additions
- 48 additions occupy 48 unique grid steps.
- Nearest other addition, any MIDI: median **4.5** steps; 13/48 within 1 step, 20/48 within 2, 24/48 within 4.
- Nearest other addition, same MIDI: 44 have another same-MIDI addition; median **33** steps. Only **9/48** are within 1 same-MIDI step and **14/48** within 2.
- Nearest immutable I003 base event, same MIDI: all 48 within **6** steps; median **1.5**; 24 within1, 42 within2. This broad base-proximity feature affects nearly the entire recovery set and is not a sparse discriminator.
- Same-MIDI gap<=1 bursts: MIDI64 `[1237,1238]`, MIDI64 `[1750,1751,1752]`, MIDI69 `[1405,1406]`, MIDI81 `[1341,1342]`; 9 burst events, collapse prunes 5 -> 43 additions.
- Same-MIDI gap<=2 additionally includes MIDI67 `[1410,1412]`, MIDI71 `[1435,1437]`, and extends MIDI64 to `[1750,1751,1752,1754]`; 14 burst events, collapse prunes 8 -> 40 additions.

## Preregistered recurrence family — generation pending
- `recur-repro-i005`: exact I005, 48 additions; no-score control.
- `recur-gap1-earliest`: additions **43**, Guitar **1093**.
- `recur-gap1-strongest`: additions **43**, Guitar **1093**.
- `recur-gap2-strongest`: additions **40**, Guitar **1090**.
- Planned score calls after separate candidate freeze: Guitar **3**, Bass **0**, reproduction **0**.
- Selection: max Guitar F1, then precision, fewer kept additions, lexicographic id.
- Separate I006 eligibility only if winner gains **>=+0.10pp F1 vs I005** and precision **>= I005**; scorer workflow cannot auto-create I006.

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

## NEXT boundary — rearm corrected recurrence generation freeze
1. Update the existing failed generation workflow only, from this exact checkpoint parent.
2. Verify corrected generator blob `2f90e7a8b3e07ae59856f67cf0d299094f482d94`, unchanged grader blob `e8251df48d03e94a2d53060bc1e82b4e9d5ba4f7`, and immutable I003/I005/analysis identities.
3. Generate exactly four candidates; require kept-addition counts 48/43/43/40 and Bass exact I005.
4. Commit manifest/candidate files + generation receipt and remove workflow in terminal commit.
5. Checkpoint frozen candidate identities before any scoring.
6. Only then arm separate exactly-3-call Guitar scorer workflow using frozen scorer/reference. Bass/reproduction 0 calls; no I006 auto-promotion.
7. CPU only; no GPU/CUDA/Modal; never modify main/Production.
