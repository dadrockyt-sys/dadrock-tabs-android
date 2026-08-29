# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 002 remains the best frozen candidate: Guitar 41.9157%, Bass 71.8651%. Timing and admitted-event Bass pitch alternatives are substantially exhausted. Exact upstream discard gates and the reproducible CPU source/stem boundary are mapped. The reference-blind upstream evidence pool is frozen at terminal commit `86ab5882845b61917b8820c35b07022adef532f0`. A deterministic 146-variant upstream-recovery sweep is now explicitly preregistered in code before reference scoring: 49 Guitar variants and 97 Bass variants, including baselines. No Iteration 003 exists yet. `main`/Production remain untouched.**

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

## V167 calibration progression
- Baseline: Guitar **6.058125255832993%**, Bass **21.707060063224446%**.
- Frozen global phase sweep found the same optimum for both streams: `-12` absolute grid steps.
- Iteration 001 terminal `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`: Guitar **40.36021285304953%**, Bass **70.60063224446786%**.
- Fixed shared 8-measure phase sweep found no additional nonzero timing correction.
- Generated-only repeat completion was not promoted: Bass no gain; Guitar only +0.622pp while adding 285 notes.
- Candidate evidence probe showed every admitted event stores three audio-derived lattice alternatives.
- Frozen whole-stream step-rule sweep selected Guitar `max_score_x_shared` and Bass `max_score_x_mean_support`.

## V167 Iteration 002 — CURRENT BEST / FROZEN
- Transform `validation/v167_single_song_calibration/apply_step_rules_v167.py`, blob `00dc94081117664890d1dc5539bf5e69fedf76fa`.
- Run `33227898407`, job `99035077043`; terminal commit `9883daaa9770123aeab2a122fa72fa2fc6c16c4c`.
- Candidate `debug/v167-single-song-calibration/iteration-002-generated.json`, blob `7eba73700116ceeca580a8851abe399aed764834`, SHA256 `96fbc329d9ba46b06d430c7c3c7b7f5b0e9077f6e133da5c3165c1fde609b5cc`.
- Score blob `5e01636b8ebe4753ee78a5126bfa321697139932`; diagnostic blob `763b7f6450e02ea66406c5baba1372cde366cd41`; receipt blob `c80a4e2a78309e359eaee67f745111c80e70d270`.

### Current exact score
**Guitar**: primary F1 **41.9156774457634%** = 512 matched / 1050 generated / 1393 reference; precision 48.7619%, recall 36.7552%; gross F1 55.0962%; same-measure pitch-content F1 59.3533%. Residual primary FN 881 / FP 538; 491 FN have no generated event within ±0.5 step same measure.

**Bass**: primary F1 **71.86512118018967%** = 341 / 402 / 547; precision 84.8259%, recall 62.3400%; gross F1 74.3941%; same-measure pitch-content F1 75.0263%. Residual primary FN 206 / FP 61; 165 FN have no generated event within ±0.5 step same measure. Generated low-note counts remain sparse: MIDI 31 = 10 vs reference 73; MIDI 35 = 26 vs reference 70.

## V167 Bass admitted-event pitch-rule sweep — FROZEN NEGATIVE
- Code `validation/v167_single_song_calibration/bass_pitch_rule_sweep_v167.py`, blob `2b59bb1dcb2b5724eb56457349639ec6eb6eca83`.
- One-shot run `33228058021`, job `99035528898`; SUCCESS.
- Terminal commit `b3425afd6ffd06ab367a18edd3ce4d63242f7659`; report `debug/v167-single-song-calibration/bass-pitch-rule-sweep.json`, blob `189466d1a4180e4fc05519b8ebdd94546d4dbf00`.
- Best rule is `baseline_current`; delta **0.0 pp**. Stored `stateMidi`/pYIN substitutions do not improve admitted Bass events.
- Conclusion strengthened: low Bass recall is an upstream proposal/detection coverage problem, not a simple repitching problem inside already-admitted events.

## Frozen source audit — upstream discard bottlenecks
### Guitar
- Basic Pitch frozen call: onset threshold 0.50, frame threshold 0.30, minimum note length 90ms, MIDI 40–88.
- Same-MIDI rows can merge at segmentation when reattack evidence is unsupported.
- Segmented final gates: activity >=0.05 and admission >=0.50; these reject comparatively few candidates.
- Active-state recovery only evaluates a MIDI if Basic Pitch already has that pitch active at the onset. **Standalone harmonic pitch discovery is explicitly disabled**, making this a major missing-polyphony/chord-tone bottleneck.
- Recovery gates: onset support >=0.35, not within 0.050s existing attack, parent confidence >=0.35, pitch evidence present, template rank >=0.80, fundamental present, recovery score >=0.58, cap 3/onset.
- Grid dedupe keeps one event per `(step,midi)` by evidence/confidence; Guitar final polyphony cap = 6 notes/step.

### Bass
- Stable pYIN states require frame voiced >=0.50, minimum 4 frames, median voiced >=0.55; only <=2-frame identical-state gaps bridge.
- Detected onsets without a nearby stable state never become proposals; onset support <0.20 is rejected. Same-pitch reattacks require IOI >=0.080s and stronger local onset evidence.
- Proposals within 45ms merge to one winner; losers are normally discarded.
- Final admission rejects activity <0.04, then requires fundamental present OR median pYIN voiced >=0.60, then admission >=0.42. These final gates reject comparatively few events.
- Grid dedupe and monophonic cap 1/step follow.
- Existing admitted-event `stateMidi`/pYIN repitching is frozen negative, so low-note recall must come from upstream state/onset/proposal coverage.

## Reproducible CPU source boundary
- Historical source: `public/gomywayfullaitest.m4a` from Git commit `74b0f815ff3f66f325220975c410621503de440f`.
- Exact source: 3,478,611 bytes; SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Frozen V166 timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef` stores exact normalized-mix/stem SHA256+byte identities.
- Historical deterministic stack: Python 3.10.21, torch 2.8.0+cpu, Demucs 4.1.0 `htdemucs_6s`, CPU, shifts=1, jobs=1. No GPU/CUDA/Modal needed.

## V167 upstream evidence instrumentation — FROZEN / TERMINAL
- Output-neutral observer `validation/v167_single_song_calibration/instrument_v166_nearmiss_v167.py`, blob `1224932a841e27bfdfe8d61fd631e5c1f728d485`.
- Pinned event-logic runner `validation/v167_single_song_calibration/run_instrument_v166_nearmiss_v167.py`, blob `af216b9727ca851a32c43c318ee18849c4043752`.
- Upstream pitch augmentation `validation/v167_single_song_calibration/augment_upstream_pitch_pool_v167.py`, frozen blob `daf4ace1b6eff1da81bb537b38caa4dcb0976b29`.
- Corrected re-arm commit `7e8d15fcb57ddc34550ce7215f10c00603008852` fixed the first arm's self-matching guard without weakening the boundary: only observer/runner/augmentation source is scanned for forbidden reference/scorer paths.
- Successful one-shot CPU run `33228322645`, job `99036292089`, run 2/attempt 1; every step completed SUCCESS.
- Terminal self-seal commit `86ab5882845b61917b8820c35b07022adef532f0` deleted `.github/workflows/v167-nearmiss-instrumentation.yml` and froze exactly the evidence pool + receipt.
- Evidence pool `debug/v167-single-song-calibration/nearmiss-evidence-pool.json`, blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Receipt `debug/v167-single-song-calibration/nearmiss-evidence-receipt.json`, blob `8268eb6eeb0bbb00b98bcf3dcf2812c8a55932a3`, status `EVIDENCE_POOL_FROZEN`.
- Exact reproduction proof: frozen V166 musical streams reproduced bit-for-policy exactly at **1050 Guitar / 402 Bass**; source/mix/Guitar/Bass/drums hashes matched the frozen V166 boundary.
- Policy proof: reference read=false, scorer read=false, reference-facing score calls=0, threshold tuning=false, candidate generation behavior modified=false, GPU/CUDA/Modal=false, `main`/Production modified=false.

### Frozen observer counts
- Guitar: 272 independent onsets; 1,404 raw; 1,010 segmented; 1,005 segmented admitted; 5 admission-score rejects; 48 recovered. Grid input 1,053 -> 1,050 final; 18 evidence step corrections; cap 6.
- Bass: 465 raw onsets; 464 retained; 394 stable states; 449 merged proposals; 449 admitted; **0** activity/additional/admission-score rejects. Grid input 449 -> 405 unique step/MIDI -> 402 final under monophonic cap; 6 evidence step corrections.
- Standalone Guitar harmonic pool: **272 sites / 13,328 candidates**.
- Bass pre-admission pool: **913 sites / 36,520 candidates**.
- The pool is evidence only: augmentation changed zero generated events.

## V167 predeclared upstream-recovery sweep — STAGED BEFORE REFERENCE READ
- Reference-blind generator `validation/v167_single_song_calibration/build_upstream_recovery_variants_v167.py`, blob `24413d321f64bbfcce48812ceb85b4593dcfa80c`, implementation commit `6935311a96cc8ba391ad461ef1368ae7bed789b1`.
- Frozen-manifest grader `validation/v167_single_song_calibration/score_upstream_recovery_variants_v167.py`, blob `32304261ff9e6bec00d22eabea08cf5070cd3d3e`, implementation commit `589a046a08c7e508bae910774e8f74bb5c4b96ac`.
- The generator accepts no reference/scorer input and predeclares **146 complete variants before scoring**: **49 Guitar** (baseline + 48 whole rules) and **97 Bass** (baseline + 96 whole rules).
- Guitar grid: template-rank thresholds 0.80/0.90/0.95/0.975 × onset support 0.35/0.50/0.65 × max 1/2 additions per site × Basic-Pitch-inactive-only true/false; fundamental required; activity >=0.05; existing Iteration 002 events always win; `(step,midi)` dedupe and polyphony cap 6 remain.
- Bass grid: template-rank thresholds 0.80/0.90/0.95/0.975 × onset support 0.20/0.35/0.50 × activity 0.04/0.10 × scope all/no-stable-state/low-register/low-register+no-stable-state; fundamental required; low-register scope is MIDI <=40; existing Iteration 002 events always win; only empty monophonic steps are filled.
- New recovery-event timing is fixed without reference: nearest frozen V166 subdivision, then the already-frozen `-12` global phase. Existing Iteration 002 events retain their already-frozen whole-stream step-rule timing.
- Score-minimal candidate files are SHA256-sealed in a manifest before any scorer/reference read. The grader verifies every candidate hash before importing the scorer or opening the professional reference.
- Winner selection is frozen in advance: max primary F1, then max precision, then fewer added events, then lexicographically smaller rule id. A >=1.0pp F1 gain is reported as material, but promotion is never automatic.
- No Iteration 003 has been created. No reference-facing score has been run against this variant set yet.

## NEXT boundary — one-shot CPU recovery sweep
1. Arm a one-shot workflow on `v143-contextual-prune-lobo` only, pinned to the current preregistration state and exact blobs above.
2. Generate all 146 score-minimal variants plus the frozen manifest **before** crossing the reference-facing boundary; verify exact pool/base/timebase identities and manifest/candidate hashes.
3. Only after the complete manifest is sealed, run the frozen scorer/reference over all complete variants. Do not alter any candidate after scoring begins.
4. Require the baseline variants to reproduce Iteration 002 exactly: Guitar 41.9156774457634%, Bass 71.86512118018967%.
5. Freeze the manifest, complete score report, and receipt; self-delete the one-shot workflow and record run/job/terminal commit, blobs/hashes, winners, deltas, candidate additions, precision/recall/F1.
6. Do not create Iteration 003 unless the frozen sweep shows a material F1 gain with a defensible precision/recall tradeoff.
7. Keep CPU-only. Fresh explicit authorization is required before any GPU/CUDA/Modal work.
8. Never modify/merge/promote `main` or Production without explicit user direction.
