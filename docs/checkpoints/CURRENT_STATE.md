# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 003 is frozen current best: Guitar 41.9156774457634% F1; Bass 80.45325779036827% F1. Bass is closed for this lane. Guitar's first 48-rule additive standalone-harmonic grid is terminal negative. The terminal aggregate diagnosis now identifies the failure mechanism without new reference access: more additions strongly increase recall but destroy precision/F1, and the reference-blind pool is dominated by octave/harmonic-like inactive candidates. This supports a structurally new, sparse contextual Guitar hypothesis based on relative evidence versus active pitches plus harmonic-interval suppression. No new rule has been scored yet. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — 2026-08-29 UTC / PRE-SCORE ARM
- Resumed directly from this file on `v143-contextual-prune-lobo`; starting head was `2a7dfedd6385ef0136e1a07e6677dd3b6c47cbf0`. First resume checkpoint commit: `1c51821eb68629150f31c61d28f7094410caa92f`.
- Reconfirmed Iteration 003 is immutable for this sweep and Bass must remain scoring-stream-equivalent to I003.
- Re-read the preregistration below and implemented its exact 36-rule contextual Guitar family: onset `{0.50,0.65}`, candidate/max-active template ratio `{0.75,1.00,1.25}`, active-state `{allow_active,inactive_only}`, interval policy `{none,exclude_harmonic_octave,chord_interval}`, top-1/site, `(step,midi)` dedupe, polyphony cap 6.
- The inherited `fundamentalPresent` candidate filter is retained because the frozen aggregate structural diagnosis that preregistered the relative-ratio/interval family computed its eligible inactive pool with that same filter. This is fixed across all 36 rules, not a tuned dimension.
- New reference-blind generator: `validation/v167_single_song_calibration/build_contextual_guitar_recovery_variants_v167.py`, blob `23065c56b5b08d1d9d59fe37a01dfa95f6c6627d`, commit `40da61d541df1ad24f7d17ea097eeb6f7b4ea065`.
- New frozen-family grader: `validation/v167_single_song_calibration/score_contextual_guitar_recovery_variants_v167.py`, blob `adfd512f53e8839b295129c0768d484b5af09bc7`, commit `95adfb70254bbf3be13233d99ed844e57bb31297`.
- Predeclared top-1/site ordering is now explicit before scoring: candidate/max-active template-score ratio descending, template rank descending, template score descending, onset support descending, activity support descending, MIDI ascending.
- Grader boundary verifies manifest status/policy, all 37 candidate hashes, I003 SHA256, 512-event Bass coordinate identity in every candidate, and only then imports the frozen scorer / opens the professional reference.
- No contextual candidate has been generated or scored yet; no scorer/reference read has occurred for this family. Next substep: arm a one-shot CPU workflow that verifies these exact blobs, generates + seals all 37 complete candidates, grades them once, freezes the report/receipt, self-removes, and leaves I003 unchanged pending result review.

## Standing V167 methodology
- Calibration only; never present V167 scores as holdout/generalization performance.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Reference/scorer may grade complete predeclared variants and select whole deterministic rules/settings only. No per-event reference choices or direct reference-event copying.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## Closed V166 anchor
- Generation run `33226705813`, job `99031747626`; terminal `7f5f5f19f6ec413fc772a9839be5497ecb2790e3`.
- Candidate blob `c36a4d1e14ca66235b51a866ad3908322834efff`, SHA256 `fa2411598b401f745eff49a9cbda294ed767de093c905909531c7dd4dc6eb378`; 1050 Guitar / 402 Bass. V159–V166 closed forever.

## V167 pre-recovery progression
- Baseline Guitar 6.058125255832993%, Bass 21.707060063224446%.
- Frozen global phase `-12` steps.
- I001 terminal `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`: Guitar 40.36021285304953%, Bass 70.60063224446786%.
- Shared local phase sweep: no nonzero gain. Repeat completion: not promoted.
- Whole-stream step-rule sweep selected Guitar `max_score_x_shared`, Bass `max_score_x_mean_support`.

## V167 Iteration 002 — FROZEN PARENT
- Candidate `debug/v167-single-song-calibration/iteration-002-generated.json`, blob `7eba73700116ceeca580a8851abe399aed764834`, SHA256 `96fbc329d9ba46b06d430c7c3c7b7f5b0e9077f6e133da5c3165c1fde609b5cc`.
- Guitar **41.9156774457634%** F1; P 48.76190476190476%; R 36.755204594400576%; 512/1050/1393.
- Bass **71.86512118018967%** F1; P 84.82587064676616%; R 62.340036563071296%; 341/402/547.
- Bass admitted-event repitch sweep frozen negative, delta 0.0pp.

## Frozen source/evidence boundary
- Source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; V166 timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`.
- Evidence run `33228322645`, job `99036292089`; terminal `86ab5882845b61917b8820c35b07022adef532f0`.
- Evidence pool blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Exact V166 reproduction; reference/scorer reads 0; tuning=false; candidate generation modified=false; GPU/CUDA/Modal=false; `main`/Production=false.
- Guitar pool **272 sites / 13,328 candidates**; Bass pool **913 sites / 36,520 candidates**.

## V167 upstream-recovery sweep — FROZEN / TERMINAL
- Base generator blob `24413d321f64bbfcce48812ceb85b4593dcfa80c`; corrected adapter `fbbee07493084792912c774d375ca5011672891f`; grader `32304261ff9e6bec00d22eabea08cf5070cd3d3e`.
- 146 complete variants froze before reference scoring: 49 Guitar + 97 Bass.
- Corrected successful run `33253434886`, job `99102944880`; terminal `0c74a6916e046d202cc5cf775f974bbd06fcf567`.
- Manifest blob `0ee153dbf1004d921c586516bca91e52f7bb1fde`, SHA256 `c91ee15d702746e082c059b5f99c44fcfa7a89f18e5e9f2fc81eb6513d1baa80`.
- Report blob `324f1f4e68951ac8653c51c8a436e4d35e5dc16b`, SHA256 `1bcc5eca05df31270ff7ff638cca6def3166a0e5084c4874d70d710d4696836f`.
- Guitar winner baseline; all 48 additive rules negative.
- Bass winner `b-r975-o50-a10-low_register_no_stable_state`: 110 additions, F1 **80.45325779036827%**, P83.203125%, R77.87934186471663%, +8.588136610178598pp F1.

## V167 Iteration 003 — CURRENT BEST / FROZEN
- Promotion transform blob `9c63f2a0c4732cf3c3a11faf028cf0952c27664e`.
- Run `33253690563`, job `99103631893`; terminal self-seal `17ab31bf26fa1e15a7754469b7598c071a938705`.
- Candidate `debug/v167-single-song-calibration/iteration-003-generated.json`: blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c575bf709673`.
- Proof blob `60dba77ac478ed804fd5d66993878e4921c4a72d`; receipt blob `b3979dd5b6b205a072223493248fc66b37272a5c`, status `ITERATION_003_FROZEN`.
- Guitar rich list exactly preserved 1050 ->1050. Bass 402 +110 ->512; prior rich Bass dictionaries preserved.
- Normalized streams exactly equal already-scored frozen winner; zero new reference-facing scores; no retuning.
- Frozen inherited metrics: Guitar **41.9156774457634%** F1; Bass **80.45325779036827%** F1.

## Guitar aggregate diagnosis — FROZEN / TERMINAL
- Analyzer `validation/v167_single_song_calibration/analyze_guitar_recovery_sweep_v167.py`, blob `c6fedb0f5b8404ff472495362e7b37ecdf734f15`, implementation `9f62891686f5bfeef303c11012e7d427916da4aa`.
- Arm `216a5e5014a7f5620e5af5750326788a73d2869c`; run `33253840653`, job `99104039755`; terminal self-seal `90e333a54e4eeca8a62fb78efe607d2277314e2a`.
- Analysis `debug/v167-single-song-calibration/guitar-recovery-sweep-aggregate-analysis.json`: blob `df7df6a2504ea8295f9c7ac6a150825d9edfb4cd`, SHA256 `9b395b0977d979a09eb5b65dbaee85694f09861bbd16c7fcb0ec45e8db2d05de`.
- Receipt blob `c9fc8563f5d8cd995f4fc353df56f72912a3678c`, status `GUITAR_RECOVERY_AGGREGATE_ANALYSIS_FROZEN`.
- Policy: no professional reference/scorer read by analysis; no new reference-facing scores; no per-event match assignments; aggregate whole-variant scores only; candidate evidence reference-blind; no new rule selected by analysis.

### Aggregate failure mechanism
- **0 / 48** nonbaseline Guitar rules beat I003/I002 Guitar baseline.
- Best nonbaseline: `g-r975-o50-n1-i0`; **227 additions**; 544 matches (+32), but 733 FP (+195). F1 **40.74906367041199%**, delta **-1.1666137753514105pp**; precision -6.162061378976025pp; recall +2.2972002871500363pp.
- Across all 48 whole rules: additions vs F1 delta correlation **-0.7416972534834104**; additions vs precision delta **-0.9573408067181765**; additions vs recall delta **+0.7364716686311232**.
- The old grid therefore fails primarily by **over-addition / poor precision**, not inability to add true positives.

### Reference-blind structural evidence
- 272 sites / 13,328 candidates; 270 sites have at least one inactive candidate at the old grid floor; 68 sites have no Basic Pitch active MIDI and therefore no useful active-pitch context.
- At the 204 sites with active-pitch context, top-inactive template-score / max-active template-score ratio: median **0.6892**, p75 **1.0089**, p90 **1.4639**, mean 0.8424.
- Top-vs-second inactive template-rank gap is weakly discriminative: median **0.020408**, p90 **0.040816**.
- Nearest-active semitone distance for top inactive candidate is dominated by **12 semitones: 100 sites**. Other harmonic-like distances include 19 semitones: 6 sites; 24 semitones: 2 sites. Distance 7 occurs 16 sites; smaller non-octave intervals are much less common.
- Mechanistic interpretation: the standalone harmonic pool often promotes octave/harmonic energy around an already-active pitch. Absolute template/onset thresholds alone cannot distinguish these from missing chord tones/re-attacks.

## NEXT boundary — preregister sparse contextual Guitar recovery family
1. Keep I003 immutable; keep Bass exactly I003.
2. Define a small new whole-rule Guitar grid before scoring using **relative evidence to active pitches**, not another broad absolute-threshold expansion.
3. Proposed preregistration basis from frozen evidence only:
   - fixed strong template rank floor `0.975` and activity floor `0.05`;
   - onset floor `{0.50, 0.65}`;
   - top **1** addition/site only;
   - require at least one Basic Pitch active pitch at the site;
   - candidate/max-active template-score ratio `{0.75, 1.00, 1.25}` (chosen around median/p75/p90 structural distribution, not per-event reference outcomes);
   - candidate active-state mode `{allow_active, inactive_only}`;
   - interval-context policy as a structural dimension: `none`, `exclude_harmonic_octave` (nearest different active interval 12/19/24 rejected), and `chord_interval` (nearest different active interval in {3,4,5,7,8,9,10}).
   - Existing I003 Guitar events always win; `(step,midi)` dedupe and polyphony cap 6 remain; new event timing remains nearest frozen V166 subdivision then frozen `-12` phase.
4. This gives baseline + 36 contextual whole rules. Freeze all candidates and hashes before any reference/scorer read. Winner selection should remain max Guitar F1, then precision, fewer additions, lexicographic id. Bass normalized stream must remain exactly I003 for every variant.
5. Do not create I004 unless this new frozen Guitar sweep materially beats I003 Guitar with a defensible precision/recall tradeoff.
6. CPU only; fresh authorization before GPU/CUDA/Modal. Never modify/merge/promote `main` or Production without explicit user direction.
