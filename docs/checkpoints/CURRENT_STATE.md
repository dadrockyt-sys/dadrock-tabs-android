# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 002 remains the best frozen candidate: Guitar 41.9157%, Bass 71.8651%. Timing and admitted-event Bass pitch alternatives are substantially exhausted. Exact upstream discard gates and the reproducible CPU source/stem boundary are mapped. A reference-blind, output-neutral evidence observer plus standalone Guitar/Bass pitch-pool augmentation is now staged. Its first arm failed safely in the pre-compute guard because the workflow scanned its own forbidden-string literals; no dependency/audio/pitch work ran. Re-arm is next. `main`/Production remain untouched.**

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

## V167 upstream evidence instrumentation — STAGED
- Output-neutral observer `validation/v167_single_song_calibration/instrument_v166_nearmiss_v167.py`, blob `1224932a841e27bfdfe8d61fd631e5c1f728d485`, implementation commit `d6b26d5305c4b57e4e8056cdd98078a9b205401b`.
- Pinned event-logic runner `validation/v167_single_song_calibration/run_instrument_v166_nearmiss_v167.py`, current blob `af216b9727ca851a32c43c318ee18849c4043752`.
- Upstream pitch augmentation `validation/v167_single_song_calibration/augment_upstream_pitch_pool_v167.py` staged at commit `8110e8d341e7165b0e0d305d293e9703fcd4014c`.
- Observer calls the exact pinned V166 front-end functions and must reproduce the frozen V166 musical streams **exactly** at 1050 Guitar / 402 Bass before evidence is accepted.
- Observer records Guitar raw/segmentation/admission/recovery/grid reject reasons and Bass state/onset/proposal-merge/admission/grid reject reasons without altering decisions.
- Augmentation adds:
  - Guitar all MIDI 40–88 six-frame harmonic candidates at every independent onset peak, including pitches not active in Basic Pitch.
  - Bass all MIDI 28–67 harmonic+pYIN candidates at retained-onset and merged-proposal sites, including sites without a nearby stable state.
- No professional reference/scorer is an input to observer or augmentation.

### First arm — SAFE PRE-COMPUTE FAILURE
- Workflow `.github/workflows/v167-nearmiss-instrumentation.yml` armed at commit `efe1db25f2914a033eb9f67e6177d2fece95c5a5`.
- Run `33228188560`, job `99035902132`, run 1/attempt 1, FAILED at `Verify immutable identities and reference-blind boundary`.
- Dependency install, source materialization, Demucs, observer, augmentation, and freeze steps were all skipped. No audio/pitch computation or evidence output occurred.
- Cause identified: the guard concatenated the workflow text into its scan while the workflow itself contained the forbidden reference/scorer filenames as literal strings in the `forbidden` tuple. The guard therefore self-matched by construction.
- Fix: scan only observer/runner/augmentation code for forbidden reference/scorer paths; re-arm as workflow run 2 with current branch parent pinned.

## NEXT boundary — freeze reference-blind upstream evidence pool
1. Re-arm the corrected one-shot CPU instrumentation workflow. Keep exact source, dependency, V166 code, candidate, and timebase identity assertions.
2. Reproduce deterministic CPU stems and verify normalized-mix/stem hashes against frozen V166 timebase.
3. Run the output-neutral observer and require exact frozen V166 musical-stream equality (1050/402) before accepting any evidence.
4. Add standalone Guitar harmonic and Bass pre-admission pitch pools; reference/scorer remain unread.
5. Freeze evidence pool + receipt and self-seal workflow. Update this checkpoint with run/job/terminal commit, blobs/hashes, pool counts, and exact reproduction proof.
6. Only after the pool is frozen, build reference-facing fixed recovery-rule/threshold sweeps. Prioritize Guitar missing chord tones/polyphony and Bass MIDI 31/35 low-register recall.
7. Apply the already-frozen `-12` phase and Iteration 002 timing rules to recovery variants for apples-to-apples scoring.
8. Do not create Iteration 003 until a frozen recovery sweep shows a material F1 gain with a defensible precision/recall tradeoff.
