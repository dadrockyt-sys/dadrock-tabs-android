# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 002 remains the best frozen candidate: Guitar 41.9157%, Bass 71.8651%. Timing and admitted-event Bass pitch alternatives are now substantially exhausted. The next high-value boundary is upstream CPU-only proposal/evidence instrumentation: capture Guitar standalone harmonic pitches and Bass onset/state near-misses that the frozen algorithm never admits/proposes, while leaving the baseline output unchanged. `main`/Production remain untouched.**

## Standing V167 methodology
- Calibration only; never present V167 calibration score as holdout/generalization performance.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Reference/scorer may grade complete predeclared variants and select whole deterministic rules/parameter settings. It may not directly supply or copy candidate events or choose individual-event answers.
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
- One-shot run `33228058021`, run 1, attempt 1, job `99035528898`; SUCCESS.
- Arm commit `df77cdf143bb6808ced8478068bd00fe14b24ab8`.
- Terminal commit `b3425afd6ffd06ab367a18edd3ce4d63242f7659`, message `research: freeze V167 fixed Bass audio-evidence pitch-rule sweep [skip ci]`.
- Report `debug/v167-single-song-calibration/bass-pitch-rule-sweep.json`, blob `189466d1a4180e4fc05519b8ebdd94546d4dbf00`.
- Tested complete whole-stream rules derived only from stored `stateMidi`, `medianPyinMidi`, their voiced probabilities, fixed confidence thresholds, and fixed downward-delta thresholds; timing/cardinality unchanged.
- **Best rule is `baseline_current`; delta = 0.0 percentage points.** Current admitted Bass MIDI assignment therefore remains frozen for now.
- This materially strengthens the conclusion that low Bass recall is a **proposal/detection coverage problem upstream**, not a simple repitching problem inside already-admitted events.

## Frozen V166/V162 source audit — main upstream bottlenecks
### Guitar
- Basic Pitch frozen call uses onset threshold 0.50, frame threshold 0.30, minimum note length 90ms, MIDI range 40–88.
- Final activity/admission gates reject very little: activity rejects are 0 and total admission-score rejects across streams are only about 5 in the frozen evidence metadata. Lowering the final 0.50 Guitar admission threshold is therefore not the main opportunity.
- Active-state reattack recovery only evaluates a MIDI pitch if Basic Pitch already has that pitch active at the onset. **Standalone harmonic pitch discovery is explicitly disabled.** This is a major structural recall bottleneck for missing Guitar chord tones/polyphony.
- Final Guitar grid cap is 6 notes per grid step, so the cap is not the obvious primary limiter.

### Bass
- Stable states require voiced probability >=0.50, minimum 4 frames, median voiced >=0.55; only short gaps between identical states are bridged.
- Detected onsets without a nearby stable state never become proposals. Same-pitch reattacks have additional onset/IOI gates.
- Proposal merge within 45ms keeps only one winner.
- Final Bass admission gates also reject comparatively few events; final grid cap is one note per step, appropriate for monophonic Bass.
- Existing admitted-event `stateMidi`/pYIN substitution does not improve the score, so missing low notes must be recovered from **onsets/states/proposals not currently represented in the admitted stream**.

## Reproducible CPU source boundary
- Historical source: `public/gomywayfullaitest.m4a` from Git commit `74b0f815ff3f66f325220975c410621503de440f`.
- Exact source identity: 3,478,611 bytes; SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Historical deterministic stack: Python 3.10.21, torch 2.8.0+cpu, Demucs 4.1.0 `htdemucs_6s`, CPU, shifts=1, jobs=1. No GPU/CUDA/Modal needed.

## NEXT boundary — upstream evidence pool
1. Recover the exact historical V166 one-shot workflow/stem construction and pin every path/command needed to reproduce its CPU stems and timebase inputs.
2. Implement a V167 calibration-only, **reference-blind evidence-pool generator** that does not alter the frozen baseline candidate. Priority pools:
   - Guitar: independent onset peaks with standalone harmonic/CQT pitch candidates (including pitches not active in Basic Pitch), plus enough rank/fundamental/onset evidence for later fixed threshold sweeps.
   - Bass: detected/retained onset candidates lacking a stable-state proposal, weak/short state candidates where practical, proposal-merge losers, and alternative harmonic/pYIN candidates before final admission.
3. First evidence run must not read scorer/reference and must be CPU-only. It should reproduce/pin the source/stem/timebase identities and emit machine-readable pools only.
4. Freeze the evidence pool before any reference-facing recovery sweep.
5. After pool freeze, apply the already-frozen `-12` phase and Iteration 002 timing rules to recovery variants for apples-to-apples scoring.
6. Reference may grade only complete fixed recovery rules/threshold grids; no event-by-event reference selection.
7. Do not create Iteration 003 until a frozen recovery sweep shows a material F1 gain with a defensible precision/recall tradeoff.
