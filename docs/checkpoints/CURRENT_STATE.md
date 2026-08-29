# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 004 is now the frozen current best. It deterministically promotes the already-frozen contextual Guitar whole-rule winner `gctx-o50-q100-allow-noharm` with zero new reference-facing score calls: Guitar 42.617717478052675% F1, precision 47.97843665768194%, recall 38.334529791816224%, 534 matched / 1113 generated / 1393 reference. Bass is exactly preserved from I003 at 80.45325779036827% F1, 426 / 512 / 547, and remains closed. I004 reconstruction SHA256 exactly matched the previously scored frozen winner before promotion. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used. Next research boundary is aggregate/reference-blind Guitar diagnosis of the completed 36-rule contextual family before any new score-facing family is preregistered.**

## Current execution checkpoint — ITERATION 004 FROZEN / POST-I004 DIAGNOSIS NEXT
- Deterministic I004 promotion transform: `validation/v167_single_song_calibration/promote_contextual_guitar_winner_v167.py`, blob `cd099c6a7f1c33a4d3c5f1ce58c27d4d8d20078f`, implementation commit `4cd0dece8f8a88fc211fbecd63bb5747e6d74ae9`.
- Pre-arm checkpoint commit `1b89b9529835809cd912d2adf0ffbb87f1c4f21e`.
- Promotion arm `f66673e69a0b810eb21a1f7c9584f0357db70404`; run `33257608217`, job `99113946852`; **SUCCESS**.
- Terminal self-seal commit `edb1cbca37ffcac2cf1020e2af05120e2f3a5353`; one-shot workflow deleted itself.
- I004 candidate `debug/v167-single-song-calibration/iteration-004-generated.json`: blob `8dd85049a65f00541f7874ff99511b081a0b5ff2`, SHA256 `728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc`.
- Promotion proof `debug/v167-single-song-calibration/iteration-004-promotion-proof.json`: blob `d055f3f0a1cbf91cd4d6ac4cb26ee654b599925d`, SHA256 `b35c7bff5583786a8e23e736c56898505306e7c6c69106bf565aa11e0e0ae753`.
- Freeze receipt `debug/v167-single-song-calibration/iteration-004-freeze-receipt.json`: blob `a880a1e29dab29cc0e77f1aa569dd123e1092457`, status `ITERATION_004_FROZEN`.
- Reconstruction proof: frozen scored winner SHA256 `2527870bc4655c238d5f4fbd0e243ab518554e17c4e2c29db2794225bbbeed43` == reconstructed winner SHA256 before I004 write.
- I004 Guitar = all 1050 rich I003 Guitar event dictionaries preserved as a multiset + exactly 63 frozen contextual recovery additions; output count 1113; new coordinates unique and disjoint from parent; normalized stream exactly equals the frozen scored winner.
- I004 Bass = exact rich I003 Bass list, 512 events; normalized stream exactly equals I003.
- Promotion policy proof: professional reference read=false; scorer read=false; new reference-facing score calls=0; individual-event reference selection=false; post-sweep retuning=false; I003 modified=false; GPU/CUDA/Modal=false; `main`/Production=false; generalization claim=false.

## Frozen I004 inherited metrics
### Guitar — `gctx-o50-q100-allow-noharm`
- F1 **42.617717478052675%**.
- Precision **47.97843665768194%**.
- Recall **38.334529791816224%**.
- 534 matched / 1113 generated / 1393 reference; FP 579; FN 859.
- Delta vs I003: F1 **+0.702040032289275pp**; precision **-0.7834681042228231pp**; recall **+1.5793251974156486pp**; +22 matches; +41 FP; -22 FN.
- Frozen winner config: rank >=0.975; activity >=0.05; onset >=0.50; candidate/max-active template score >=1.00; `allow_active`; reject nearest different active intervals 12/19/24; active-pitch context required; inherited `fundamentalPresent`; top-1/site; polyphony cap 6.
- Generation summary: 63 additions from 69 eligible candidates; 63 sites with adds; 204 sites with active context.

### Bass — closed / exactly I003
- F1 **80.45325779036827%**; precision **83.203125%**; recall **77.87934186471663%**.
- 426 matched / 512 generated / 547 reference; FP 86; FN 121.

## Frozen contextual sweep anchor
- Final contextual generator blob `fd257fe88c5dcd9b3ab135263a6457140c3f63b6`.
- Sweep terminal self-seal `f93467de4ccde1d2c0b9baf02c14c194f9d644c4`.
- Manifest `debug/v167-single-song-calibration/contextual-guitar-recovery-sweep-manifest.json`: blob `b9ec90a34e0d7a4a6b6ee7fb3f5a1eef7e6bba5d`, SHA256 `2f51fa0cba372acc8f797a2e700b3b0a6bb42b807ad4bad818b3c40c262df876`.
- Report `debug/v167-single-song-calibration/contextual-guitar-recovery-sweep.json`: blob `b00e25f5c1fd9f8c40b440156e049317e008ec1d`, SHA256 `6b661f6dfa27d31204f4e8a9035d286d5324440b947eb3e49db99205dad9320e`.
- Receipt blob `e4e296bb50a38935d83e2c1183160509974fd6aa`, status `CONTEXTUAL_GUITAR_RECOVERY_SWEEP_FROZEN`.
- 37 variants = baseline + 36 contextual whole rules; all complete candidates frozen before reference read.
- **10 / 36** nonbaseline contextual rules beat I003 Guitar F1.
- Winner selection was preregistered: max Guitar F1, then precision, fewer additions, lexicographic rule id.
- I003 immutable parent contained 9 pre-existing duplicate scoring-coordinate excess; final generator preserved parent duplicates while forbidding every new `(step,midi)` collision.

## Immutable source/evidence boundary
- I003 parent `debug/v167-single-song-calibration/iteration-003-generated.json`: blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- Evidence pool `debug/v167-single-song-calibration/nearmiss-evidence-pool.json`: blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Frozen V166 timebase `debug/v166-cpu-autonomous/timebase.json`: blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`.
- Base recovery builder blob `24413d321f64bbfcce48812ceb85b4593dcfa80c`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.

## Standing V167 methodology
- Calibration only; never present V167 scores as holdout/generalization performance.
- Reference/scorer may grade complete predeclared variants and select whole deterministic rules/settings only. No per-event reference choices or direct reference-event copying.
- Aggregate whole-rule score reports may be analyzed without opening the professional reference/scorer again; reference-blind evidence may be used for structural diagnosis.
- I004 is immutable unless a later already-frozen whole-rule winner is deterministically promoted after its own complete preregistered sweep.
- Bass is closed for this lane unless a genuinely new upstream hypothesis is separately preregistered.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — post-I004 aggregate/reference-blind Guitar diagnosis
1. Keep I004 immutable; keep Bass exactly I004/I003 and do not score Bass.
2. Analyze only the frozen 37-rule contextual sweep report plus frozen reference-blind Guitar evidence (and, if useful, the frozen I004 addition set). Do **not** open the professional reference or scorer; do not read per-event reference match assignments.
3. Quantify whole-rule factor effects for onset `{0.50,0.65}`, ratio `{0.75,1.00,1.25}`, active-state `{allow_active,inactive_only}`, and interval policy `{none,exclude_harmonic_octave,chord_interval}`; relate additions to F1/precision/recall deltas and identify which structural dimensions drive the 10 positive rules.
4. Specifically test at aggregate-rule level whether harmonic suppression recovers precision, whether `allow_active` is carrying re-attack recall, and whether ratio `1.00` is a stable middle regime versus `0.75` over-addition and `1.25` under-addition.
5. Freeze the analysis + receipt in a self-removing CPU-only workflow. No new reference-facing score calls.
6. Only after that frozen diagnosis may a genuinely new small Guitar family be preregistered. Freeze every candidate/rule before any future scorer/reference read; do not create I005 automatically.
7. Never modify/merge/promote `main` or Production; fresh explicit authorization required before GPU/CUDA/Modal.
