# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 remains frozen current best: Guitar `gss-active-only` **42.7940586109996% F1**, Bass **80.45325779036827% F1**. The preregistered active-topology pruning sweep is now terminal/frozen. Exactly three new Guitar whole rules were scored; Bass and the I005 reproduction control received 0 score calls. None of the three topology prunes beat I005, and 0 met the preregistered I006 promotion boundary, so **no I006 is authorized or created**. The next work must be aggregate/reference-blind diagnosis of a genuinely new structural dimension; do not retune or extend the just-scored topology subset family. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Active-topology Guitar sweep — FROZEN / TERMINAL NEGATIVE
- Frozen generation manifest blob `4b3e75b7f1734807b67de827e54bd4bcc59b855b`, SHA256 `bafccfaf15f2e95959396d0f956d3224b2a4fb21290058222281cf0a77023d48`.
- Generation receipt blob `e702f408ab63387a1c21e9a37470aa4afa6c4a66`, status `ACTIVE_TOPOLOGY_VARIANTS_FROZEN_BEFORE_SCORING`.
- Scoring arm commit `8ed642489561cf407f78bbe4350e5aeabac02010`; run `33265672682`, job `99135186427`; terminal self-removing commit `840c800feeaffc21b2ef77cb98a6ac61676e2c92`.
- Report `debug/v167-single-song-calibration/active-topology-guitar-sweep.json`: blob `4aab67d913b4b68cc518825d4495a48c3b9e76fc`, SHA256 `869825ed2a91e9f50bc6ca5ac71d922ee93dc17dd5804bf8d94d0e951e179b85`.
- Receipt `debug/v167-single-song-calibration/active-topology-guitar-sweep-receipt.json`: blob `344bd76334367e5cb3d02f361703386842a2d3dd`, status `ACTIVE_TOPOLOGY_GUITAR_SWEEP_FROZEN`.
- Score boundary held exactly: Guitar **3**, Bass **0**, reproduction control **0**.
- All candidates were committed/frozen before professional-reference access; no event-level reference selection; no post-score mutation/retuning; no I006; GPU/CUDA/Modal=false; main/Production=false.
- `newVariantsBeatingI005=0`; `newVariantsMeetingPromotionEligibility=0`; winner including baseline is `i005-baseline`.

### Frozen topology results vs I005
- I005 baseline: F1 **42.7940586109996%**; P **48.54280510018215%**; R **38.26274228284279%**; 533 matched / 1098 generated; FP565/FN860.
- `topo-single-or-chord` (keeps 41; prunes 7 near-unison/remote): F1 **42.7536231884058%**; P **48.67094408799267%**; R **38.11916726489591%**; 531/1091; FP560/FN862. Delta: **-0.04043542259379862pp F1**, +0.12813898781051658pp P, -0.14357501794687866pp R; matched -2, generated -7, FP -5.
- `topo-single-only` (keeps 23; prunes 25): F1 **42.497972424979724%**; P **48.835041938490215%**; R **37.616654702081836%**; 524/1073; FP549/FN869. Delta: **-0.2960861860198727pp F1**, +0.29223683830806313pp P, -0.6460875807609512pp R; matched -9, FP -16.
- `topo-chord-only` (keeps 18; prunes 30): F1 **42.17797643234458%**; P **48.59550561797753%**; R **37.25771715721464%**; 519/1068; FP549/FN874. Delta: **-0.6160821786550197pp F1**, +0.052700517795378765pp P, -1.005025125628145pp R; matched -14, FP -16.

### Aggregate mechanism — whole-rule only
- Relative to the 1050-event I003 Guitar base, the 23 `single` additions contribute aggregate +12 matched / +11 FP.
- The 18 `chord` additions contribute aggregate +7 matched / +11 FP.
- The combined 7 `near_unison + remote` additions contribute aggregate +2 matched / +5 FP.
- These are algebraic differences between complete frozen whole-rule scores, **not per-event reference labels**. They justify only aggregate diagnosis, not choosing individual events.
- Removing all 7 near-unison/remote events improved precision but slightly reduced F1. Therefore the existing topology categories are not a clean pruning separator at the whole-rule level.
- Do not extend the same topology subset search after seeing these scores; the active-topology family is terminal to avoid post-score retuning.

## Frozen topology candidates
- `topo-repro-i005`: blob `a4c8a68ff10b5a168fbb19adc2e6bbdb18771061`, SHA256 `4fbd7c41093d8b3f9b382bba51d8cda29a0aeeb36071749f67b7084f5cfca652`; 1098 Guitar /512 Bass; no-score control.
- `topo-single-or-chord`: blob `f91ef9390e5dd5cb3061fec84d3c017bb0ae8bce`, SHA256 `8a924e8395d439635d577cee028d2c9b47512d5c305d0018e5cc6bbd2a6c46c4`.
- `topo-single-only`: blob `e4f75950bd17b067546dd902fbcd4701c226b71e`, SHA256 `370ecb56e1f1e3ef4b16367f7cd6747dac8139e6d75a739e861b165eb7e88efa`.
- `topo-chord-only`: blob `559ba84378a67d04004b9eaca60264350c0cce9f`, SHA256 `2355aa168e4aed0d63f298690d092209b205191a2a64df109139624978e4950c`.

## Post-I005 diagnosis already frozen
- Analysis blob `043eaa2367f1efbb6309e13d2fcd52952b809e81`, SHA256 `fe7e826724a11e115a25f932d4b58ed88e3aedae67fb54142cc532cc40ab8450`.
- Exact I005 additions: 48/48 unique sites; ratio=1.0 all; max-active tie count=1 all; topology single23/chord18/near-unison5/remote2.
- Simple onset tightening is terminal unsupported by aggregate evidence.

## Iteration 005 — FROZEN CURRENT BEST
### Guitar
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- F1 **42.7940586109996%**; precision **48.54280510018215%**; recall **38.26274228284279%**.
- 533 matched / 1098 generated / 1393 reference; FP565/FN860.

### Bass — closed
- F1 **80.45325779036827%**; precision **83.203125%**; recall **77.87934186471663%**.
- 426 matched /512 generated /547 reference; FP86/FN121.
- Bass must remain exactly I005/I004/I003.

## Immutable identities
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`, scorer SHA256 from terminal report `95f4e22f3367ec930bd1d07141266f60712240f0f83bd07d2e1cc4eae815dda2`.
- Professional reference path `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`, blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.

## Standing V167 methodology
- Calibration only; never present scores as holdout/generalization performance.
- I003/I004/I005 and all terminal sweep reports are immutable.
- Active-topology sweep is terminal; do not add post-hoc topology subsets to the same family.
- No per-event reference choices, direct reference-event copying, or post-score candidate mutation/retuning.
- Bass closed. CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — reference-blind temporal/recurrence diagnosis
1. Keep I005 immutable; do not score anything yet.
2. Analyze the exact 48 I005 additions using only their frozen coordinates/evidence and aggregate terminal sweep reports. No professional reference/scorer read and no per-event match assignments.
3. Examine a genuinely new dimension not used in prior grids: temporal recurrence/clustering of active-state reattacks — distance to prior/next I005 addition, same-MIDI recurrence spacing, consecutive-grid clusters, repeated MIDI runs, and relation to the 1050 immutable base Guitar event coordinates.
4. Quantify whether additions concentrate in short same-MIDI/grid-step bursts or collide closely with existing same-MIDI/base events in ways that could support a deterministic refractory/recurrence rule.
5. Do not select thresholds/rules from reference outcomes. Any proposed family must be justified from reference-blind structural distributions and must be small/preregistered before scoring.
6. Freeze diagnosis + receipt and checkpoint before implementing any new family.
7. CPU only; no GPU/CUDA/Modal; never modify main/Production.
