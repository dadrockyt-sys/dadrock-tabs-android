# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 005 is frozen current best: Guitar `gss-active-only` **42.7940586109996% F1**, Bass **80.45325779036827% F1**. The post-I005 diagnosis is frozen and the small active-topology pruning family is now fully generated, hashed, committed, and frozen **before scoring**. No topology score call has occurred yet. The manifest contains one no-score I005 reproduction control plus exactly three new Guitar whole rules; Bass is frozen exactly to I005. The next boundary is a separate scorer workflow limited to exactly 3 Guitar score calls, 0 Bass calls, and 0 reproduction-control calls. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Active-topology candidate freeze — FROZEN BEFORE SCORING
- Generator `validation/v167_single_song_calibration/build_active_topology_guitar_variants_v167.py`: blob `b7ac8a77e74df27a0b2af5bceb25bb97c81d4c7d`.
- Grader `validation/v167_single_song_calibration/score_active_topology_guitar_variants_v167.py`: blob `4458d45cfa2ea018cf40a3a24344e1b7dd9d104a`.
- Generation arm commit `51f0a261b1bcd3a33893505172aea1ad07d9bf82`; run `33265561944`, job `99134889947`; terminal self-removing commit `6d4fe21ee52e027c3a271f90cef7b70d83f662b3`.
- Generation workflow passed immutable/reference-blind guard, generation verification, and self-seal.
- Manifest `debug/v167-single-song-calibration/active-topology-guitar-manifest.json`: blob `4b3e75b7f1734807b67de827e54bd4bcc59b855b`, SHA256 `bafccfaf15f2e95959396d0f956d3224b2a4fb21290058222281cf0a77023d48`, status `FROZEN_BEFORE_REFERENCE_SCORING`.
- Generation receipt `debug/v167-single-song-calibration/active-topology-generation-receipt.json`: blob `e702f408ab63387a1c21e9a37470aa4afa6c4a66`, status `ACTIVE_TOPOLOGY_VARIANTS_FROZEN_BEFORE_SCORING`.
- Generation policy: professional reference read=false; scorer read=false; new reference-facing score calls=0; all candidate hashes frozen before scoring=true; reproduction control scored=false; Bass scored=false; GPU/CUDA/Modal=false; main/Production=false.

### Frozen topology candidates
- `topo-repro-i005`: candidate blob `a4c8a68ff10b5a168fbb19adc2e6bbdb18771061`, SHA256 `4fbd7c41093d8b3f9b382bba51d8cda29a0aeeb36071749f67b7084f5cfca652`; 1098 Guitar / 512 Bass; keeps all 48 I005 additions. **No-score reproduction control.**
- `topo-single-or-chord`: blob `f91ef9390e5dd5cb3061fec84d3c017bb0ae8bce`, SHA256 `8a924e8395d439635d577cee028d2c9b47512d5c305d0018e5cc6bbd2a6c46c4`; 1091 Guitar / 512 Bass; keeps 41 additions = 23 single +18 chord; prunes 7 near-unison/remote.
- `topo-single-only`: blob `e4f75950bd17b067546dd902fbcd4701c226b71e`, SHA256 `370ecb56e1f1e3ef4b16367f7cd6747dac8139e6d75a739e861b165eb7e88efa`; 1073 Guitar / 512 Bass; keeps 23 single additions; prunes 25.
- `topo-chord-only`: blob `559ba84378a67d04004b9eaca60264350c0cce9f`, SHA256 `2355aa168e4aed0d63f298690d092209b205191a2a64df109139624978e4950c`; 1068 Guitar / 512 Bass; keeps 18 chord additions; prunes 30.
- Source topology frozen before generation: single=23, chord=18, near-unison=5, remote=2.
- Every variant keeps all original 1050 I003 Guitar events. No event is invented or retimed. Bass normalized stream is exactly I005 for all variants.

## Frozen scoring policy for this family
- Before any reference/scorer read, scorer workflow must verify manifest SHA/blob, generation receipt, every candidate SHA/blob, I005, grader blob, scorer blob, professional-reference blob/SHA, and checkpoint identity.
- Reproduction control must be normalized-verified exactly equal I005 Guitar/Bass **without scoring**.
- All candidate Bass streams must be normalized-verified exactly equal I005 **without scoring**.
- Exactly the three new Guitar variants may receive score calls. Planned calls: Guitar **3**, Bass **0**, reproduction control **0**.
- Selection frozen: max Guitar primary F1, then max precision, fewer kept I005 additions, lexicographic id.
- Scoring workflow may never create I006 and may never mutate/retune candidates after scoring.
- Separate I006 promotion eligibility frozen in advance: winning new rule must gain at least **+0.10pp F1 vs I005** and have **precision >= I005**.

## Post-I005 aggregate diagnosis — FROZEN / TERMINAL
- Corrected analyzer blob `82ec287869102ab6af949afa174a2543768dbc55`; terminal analysis commit `dbfa511f90b2f8ccd58411211fdde540fa5ca0c9`.
- Analysis blob `043eaa2367f1efbb6309e13d2fcd52952b809e81`, SHA256 `fe7e826724a11e115a25f932d4b58ed88e3aedae67fb54142cc532cc40ab8450`.
- Exact 48 I005 additions: candidate/max-active ratio 1.0 all48; unique max candidate at all48; topology single23/chord18/near-unison5/remote2.
- Simple onset tightening rejected by frozen aggregate evidence; no onset/activity/rank/ratio dimensions are part of this family.

## Iteration 005 — FROZEN CURRENT BEST
### Guitar
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- F1 **42.7940586109996%**; precision **48.54280510018215%**; recall **38.26274228284279%**.
- 533 matched / 1098 generated / 1393 reference; FP565/FN860.

### Bass — closed
- F1 **80.45325779036827%**; precision **83.203125%**; recall **77.87934186471663%**.
- 426 matched / 512 generated / 547 reference; FP86/FN121.
- Bass must remain exactly I005/I004/I003.

## Immutable identities
- I003 blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- I005 blob `8d68f4d7fac4e094bcd617b026befddd370d9368`, SHA256 `86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.

## Standing V167 methodology
- Calibration only; never present scores as holdout/generalization performance.
- Complete deterministic whole variants are now frozen; no event-level reference choices or direct reference-event copying.
- No post-score candidate mutation/retuning.
- I003/I004/I005 and terminal reports are immutable. Bass is closed.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — arm exact 3-call active-topology Guitar scorer
1. Resolve/verify the exact frozen professional-reference path from prior V167 scorer workflow; do not guess it.
2. Create one self-removing CPU-only scoring workflow from this exact checkpoint parent.
3. Before crossing reference boundary, verify topology manifest blob `4b3e75b7f1734807b67de827e54bd4bcc59b855b` / SHA256 `bafccfaf15f2e95959396d0f956d3224b2a4fb21290058222281cf0a77023d48`, generation receipt blob `e702f408ab63387a1c21e9a37470aa4afa6c4a66`, all four frozen candidate blobs/SHA256 values, I005, grader blob `4458d45cfa2ea018cf40a3a24344e1b7dd9d104a`, scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`, professional-reference identity, and checkpoint identity.
4. Run grader once. Require exactly Guitar=3 score calls, Bass=0, reproduction=0; report all three new rules versus inherited I005 baseline.
5. Freeze report + scoring receipt; self-remove workflow. Do not create I006.
6. Read terminal result, checkpoint immediately, then only if preregistered promotion eligibility is met may a separate no-rescore I006 promoter be considered.
7. CPU only; no GPU/CUDA/Modal; never modify main/Production.
