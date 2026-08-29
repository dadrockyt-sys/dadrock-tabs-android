# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. The 146-variant upstream-recovery sweep is now terminal/frozen. Guitar's winner is the unchanged Iteration 002 baseline at 41.9156774457634%. Bass has a material frozen whole-rule winner at 80.45325779036827% F1, +8.588136610178598pp versus Iteration 002, with +15.539305301645335pp recall and -1.622745646766166pp precision. The winner adds 110 reference-blind upstream recovery events under the predeclared low-register/no-stable-state rule. This clears the preregistered material-gain/precision-recall tradeoff gate. Next is deterministic Bass-only Iteration 003 promotion with Guitar unchanged, proving normalized musical-stream equality to the already-scored frozen winner. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or needed.**

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

## V167 Iteration 002 — FROZEN BASE FOR RECOVERY
- Transform `validation/v167_single_song_calibration/apply_step_rules_v167.py`, blob `00dc94081117664890d1dc5539bf5e69fedf76fa`.
- Run `33227898407`, job `99035077043`; terminal commit `9883daaa9770123aeab2a122fa72fa2fc6c16c4c`.
- Candidate `debug/v167-single-song-calibration/iteration-002-generated.json`, blob `7eba73700116ceeca580a8851abe399aed764834`, SHA256 `96fbc329d9ba46b06d430c7c3c7b7f5b0e9077f6e133da5c3165c1fde609b5cc`.
- Score blob `5e01636b8ebe4753ee78a5126bfa321697139932`; diagnostic blob `763b7f6450e02ea66406c5baba1372cde366cd41`; receipt blob `c80a4e2a78309e359eaee67f745111c80e70d270`.
- Guitar: **41.9156774457634%** F1 = 512 matched / 1050 generated / 1393 reference; precision 48.76190476190476%, recall 36.755204594400576%.
- Bass: **71.86512118018967%** F1 = 341 / 402 / 547; precision 84.82587064676616%, recall 62.340036563071296%.

## V167 Bass admitted-event pitch-rule sweep — FROZEN NEGATIVE
- Code `validation/v167_single_song_calibration/bass_pitch_rule_sweep_v167.py`, blob `2b59bb1dcb2b5724eb56457349639ec6eb6eca83`.
- One-shot run `33228058021`, job `99035528898`; SUCCESS; terminal commit `b3425afd6ffd06ab367a18edd3ce4d63242f7659`.
- Best rule is `baseline_current`; delta **0.0pp**. Stored `stateMidi`/pYIN substitutions do not improve admitted Bass events.

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
- Grid dedupe and monophonic cap 1/step happen before V167 timing calibration. The frozen Iteration 002 timing transform can subsequently move distinct existing events onto the same corrected step; those pre-existing timing collisions are preserved.
- Existing admitted-event `stateMidi`/pYIN repitching is frozen negative, so low-note recall must come from upstream state/onset/proposal coverage.

## Reproducible CPU source boundary
- Historical source: `public/gomywayfullaitest.m4a` from Git commit `74b0f815ff3f66f325220975c410621503de440f`.
- Exact source: 3,478,611 bytes; SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Frozen V166 timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef` stores exact normalized-mix/stem identities.
- Historical deterministic stack: Python 3.10.21, torch 2.8.0+cpu, Demucs 4.1.0 `htdemucs_6s`, CPU, shifts=1, jobs=1.

## V167 upstream evidence instrumentation — FROZEN / TERMINAL
- Observer `validation/v167_single_song_calibration/instrument_v166_nearmiss_v167.py`, blob `1224932a841e27bfdfe8d61fd631e5c1f728d485`.
- Runner `validation/v167_single_song_calibration/run_instrument_v166_nearmiss_v167.py`, blob `af216b9727ca851a32c43c318ee18849c4043752`.
- Augmentation `validation/v167_single_song_calibration/augment_upstream_pitch_pool_v167.py`, blob `daf4ace1b6eff1da81bb537b38caa4dcb0976b29`.
- Successful CPU run `33228322645`, job `99036292089`; terminal self-seal commit `86ab5882845b61917b8820c35b07022adef532f0`.
- Evidence pool `debug/v167-single-song-calibration/nearmiss-evidence-pool.json`, blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Receipt blob `8268eb6eeb0bbb00b98bcf3dcf2812c8a55932a3`, status `EVIDENCE_POOL_FROZEN`.
- Exact V166 musical reproduction: **1050 Guitar / 402 Bass**; reference/scorer reads 0; threshold tuning false; GPU/CUDA/Modal false.
- Guitar pool: **272 sites / 13,328 candidates**. Bass pool: **913 sites / 36,520 candidates**.

## V167 upstream-recovery sweep preregistration
- Base generator `validation/v167_single_song_calibration/build_upstream_recovery_variants_v167.py`, blob `24413d321f64bbfcce48812ceb85b4593dcfa80c`, commit `6935311a96cc8ba391ad461ef1368ae7bed789b1`.
- Corrected guard-only adapter `validation/v167_single_song_calibration/build_upstream_recovery_variants_v167_rearm.py`, blob `fbbee07493084792912c774d375ca5011672891f`, commit `ffa7694b48e4e64b7e6a354a1704546909a45533`.
- Grader `validation/v167_single_song_calibration/score_upstream_recovery_variants_v167.py`, blob `32304261ff9e6bec00d22eabea08cf5070cd3d3e`, commit `589a046a08c7e508bae910774e8f74bb5c4b96ac`.
- **146 complete variants frozen before reference scoring**: 49 Guitar (baseline + 48) and 97 Bass (baseline + 96).
- Guitar grid: template rank 0.80/0.90/0.95/0.975 × onset 0.35/0.50/0.65 × max 1/2 additions/site × Basic-Pitch-inactive-only true/false; fundamental required; activity >=0.05; existing I002 events preferred; cap 6.
- Bass grid: template rank 0.80/0.90/0.95/0.975 × onset 0.20/0.35/0.50 × activity 0.04/0.10 × scope all/no-stable-state/low-register/low-register+no-stable-state; fundamental required; low register MIDI <=40; new additions only on steps empty in I002; inherited I002 timing collisions preserved.
- New recovery timing fixed reference-blind: nearest frozen V166 subdivision then frozen `-12` global phase. Existing I002 timing retained.
- Winner selection frozen: max primary F1, then max precision, then fewer additions, then lexicographic id. Material-gain reporting threshold = 1.0pp. No automatic I003 promotion.

### First arm — SAFE PRE-SCORE FAILURE
- Arm commit `8880dabdc9ac93d52e126328abd0965d23f45392`; run `33253264878`, job `99102488179`, run 1 / attempt 1.
- Identity/preregistration guard **SUCCESS**; reference-blind generation **FAILURE** at an overstrict inherited Bass global-monophony assertion; grading **SKIPPED**; freeze **SKIPPED**.
- Therefore zero reference-facing scores were consumed by the failed arm. No candidate/threshold/rule/reference/main/Production mutation occurred.
- Initial adapter draft blob `bcc369871f6170687bbc753be62d3d7b3266ed98` was never run; config-iterator self-binding was caught in code review before re-arm.

## V167 upstream-recovery sweep — FROZEN / TERMINAL
- Corrected arm commit `168113eed4e053a97220ab8ad9daefb189d5fd93`.
- Successful workflow run `33253434886`, job `99102944880`, run number 2 / attempt 1. Every workflow step **SUCCESS**.
- Terminal self-seal commit `0c74a6916e046d202cc5cf775f974bbd06fcf567`; one-shot workflow deleted.
- Manifest `debug/v167-single-song-calibration/upstream-recovery-rule-sweep-manifest.json`: blob `0ee153dbf1004d921c586516bca91e52f7bb1fde`, SHA256 `c91ee15d702746e082c059b5f99c44fcfa7a89f18e5e9f2fc81eb6513d1baa80`.
- Report `debug/v167-single-song-calibration/upstream-recovery-rule-sweep.json`: blob `324f1f4e68951ac8653c51c8a436e4d35e5dc16b`, SHA256 `1bcc5eca05df31270ff7ff638cca6def3166a0e5084c4874d70d710d4696836f`.
- Receipt `debug/v167-single-song-calibration/upstream-recovery-rule-sweep-receipt.json`: blob `a502e6fbc04d6423177c45c9dad418cede22c2d9`, status `UPSTREAM_RECOVERY_SWEEP_FROZEN`.
- Receipt proves: variants frozen before reference read=true; individual event selection by reference=false; post-score candidate mutation=false; GPU/CUDA/Modal=false; `main`/Production modified=false; generalization claim=false; Iteration 003 created=false.

### Frozen Guitar result
- Winner: `g-baseline` — unchanged Iteration 002.
- F1 **41.9156774457634%**, precision **48.76190476190476%**, recall **36.755204594400576%**; matched 512 / generated 1050 / reference 1393.
- Delta vs I002: **0.0pp**. All 48 standalone-harmonic recovery whole rules failed to beat the baseline under this predeclared grid.

### Frozen Bass winner — MATERIAL
- Rule id: `b-r975-o50-a10-low_register_no_stable_state`.
- Whole-rule gates: template rank >=**0.975**; onset support >=**0.50**; activity support >=**0.10**; fundamental required; MIDI <=**40**; only candidates at sites with **no nearby stable state**; existing I002 events always preserved; new recovery only on previously empty corrected steps.
- Frozen swept candidate SHA256 `2e04edd9cb61795ea9679ce899c7ded9549bb0f5d9f8e04a5d53fdf07ec9fa13`.
- Added **110** events from 149 eligible candidates across 110 sites; **4** pre-existing I002 collision steps preserved.
- Primary F1 **80.45325779036827%** = **426 matched / 512 generated / 547 reference**.
- Precision **83.203125%**; recall **77.87934186471663%**; false positives 86; false negatives 121.
- Gross F1 **83.09726156751652%**; same-measure pitch-content F1 **84.04154863078376%**.
- Delta vs I002: **+8.588136610178598pp F1**, **-1.622745646766166pp precision**, **+15.539305301645335pp recall**, +85 matched, +110 generated, +25 FP, -85 FN.
- `materialGainAtLeast1pp=true`. This also exceeds the frozen scorer's 80% Bass primary-F1 target.

## NEXT boundary — deterministic Iteration 003 Bass-only promotion
1. Promote exactly the frozen Bass winner rule above; keep Guitar musically identical to Iteration 002. Do not tune or rescore alternative rules.
2. Reconstruct the frozen score-minimal winner reference-blind from I002 + immutable evidence pool/timebase and verify SHA256 exactly `2e04edd9...` before promotion.
3. Build an Iteration 003 candidate that preserves all existing I002 rich event metadata, appending only the 110 frozen winner recovery events to Bass. Do not modify/re-pitch/re-time any existing I002 event.
4. Prove normalized `(measure, step, midi)` Guitar/Bass streams exactly equal the already-scored frozen winning variant. Because the frozen scorer ignores extra metadata, inherit the frozen sweep metrics from exact normalized-stream equality rather than performing another tuning loop.
5. Freeze Iteration 003 candidate + structural/equality receipt. If a verification score is produced, it must be a one-time exact-reproduction check only, not a new selection/tuning round.
6. Keep the sweep terminal. Guitar standalone harmonic recovery is a frozen negative in this grid; do not reopen it without a new preregistered hypothesis.
7. Keep CPU-only. Fresh explicit authorization is required before any GPU/CUDA/Modal work.
8. Never modify/merge/promote `main` or Production without explicit user direction.
