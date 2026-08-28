# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 and V157 are permanently consumed after one failed reference score each. V155 is protocol-invalid and never scoreable. V156 is permanently aborted before candidate. V157 post-score diagnosis is COMPLETE / FROZEN. V158 was confirmed unused and is now PREREGISTERED BEFORE GENERATION with a genuinely new reference-blind CPU architecture: sequential Viterbi bar/downbeat inference, onset-first Bass with fundamental/octave scoring, and Guitar Basic-Pitch proposals plus persistent harmonic-template tracking instead of free-standing CQT completion. No V158 generation code/candidate exists yet; V158 reference reads/score calls = 0. Next: implement canonical V158 transcriber + independent QC exactly to the sealed preregistration, then seal a pre-run identity receipt before any generation workflow.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable shared song / reference identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Source m104 = 2/4 (8 sixteenth steps), others 4/4; meter map SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Rhythm scorer-ready 946 rows SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`.
- Lead scorer-ready 447 rows SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- Bass scorer-ready 547 rows SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- Combined reference `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; Guitar 1393 / Bass 547; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.

## Closed historical versions
### V154 — consumed / score count 1 forever
- Candidate SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`; Guitar 1089 / Bass 635.
- Score run `33139017517`, job `98745430956`; Guitar F1 `0.04915390813859791`, Bass F1 `0.1116751269035533`, both FAIL vs 0.80.
- Fixed t=0 grid origin + drift + major pitch/polyphony errors; prior exact reference-derived shift/BPM values remain diagnosis-only.

### V155 — protocol invalid / score count 0 forever
- Prereg commit `e5f51474308db460d7317cfbc4204f616ee0b069`.
- Duplicate generation runs `33140245244`, `33140267460`; never score/select outputs.

### V156 — aborted before candidate / score count 0 forever
- Intended run `33142942558`, job `98757604810`; deterministic separation passed but pre-candidate model-cache receipt failed. No candidate/reference score.

## V157 frozen generation / score
- Preregistration blob `0bcca0fbb53abcc8ad8736d8e5e71e32a14004f6`.
- Sole generation run `33143471258`, run number 1, job `98759295729`; SUCCESS; freeze commit `c26e41d239d44d656bf57cf195ed39416658b680`.
- Candidate SHA256 `f5dc7094b72f8e3a988b1fdd59808cb056461d7e12a6d41508942cf499de3e71`; Git blob `3491814f4cc075aaf3eefaecf2d179f57d2d5dae`; Guitar 1779 / Bass 113.
- Independent QC blob `3528adbceb640743cc8f0e472d2cd62c49c1ebc3`; PASS.
- Sole score run `33143986627`, run number 1, job `98760898781`; score freeze commit `19317e7e44687e910088892cf9bf3e1157efc45c`.
- Score SHA256 `ffd66347990eff113814f207c303773734e79c0461fa4e4d129f1de8472594d8`; receipt blob `d1e3145cae8b12e612012533e9060d21c95ccf24`; reference-facing score calls = **1 forever**.
- Guitar F1 `0.07692307692307694` FAIL; Bass F1 `0.05757575757575757` FAIL.

## V157 post-score diagnostic — COMPLETE / FROZEN
- Script blob `64723c75dbd257719b8846d4829466cda39cb25e`; run `33144115704`, job `98761292358`; diagnostic blob `fb0460f158f97230bb5c82193f9409306bfa2960`; freeze commit `51fcd9b93a495f939ce85a7ec578f7ea3d70c5de`.
- Additional official scorer calls = 0; candidate modified = NO.
- Shared architecture evidence: Guitar and Bass global generated-only alignment diagnostics both peak at `-12.5` steps. Exact value is diagnosis-only and forbidden as a future parameter; conclusion is only that V157's bar/downbeat phase inference remains wrong.
- Guitar Basic Pitch subset is materially stronger than CQT-only completion: BP measure-pitch-content F1 `0.47770931496919167`; CQT-only `0.12956810631229235`. Do not use raw single-frame CQT peaks as free-standing future notes.
- Bass onset detector found 465 attacks vs 547 reference attacks, but only 113 events survived pYIN event formation; onset-to-event ratio `0.24301075268817204`. Bass generated MIDI effectively starts at 37 while reference contains substantial lower fundamentals. Future Bass architecture must be onset-first with soft F0 + explicit fundamental/octave evidence.
- Diagnostic caveat: quartile-shift quartile 4 accidentally includes the whole song; ignore quartile 4. Global scans, quartiles 1–3, source breakdown and Bass sparsity remain valid.

## V158 — PREREGISTERED BEFORE GENERATION
- V158 repository search returned no prior use before naming.
- Preregistration: `debug/v158-cpu-autonomous/preregistration.json`.
- Seal commit: `cdb2eca7ec16479a5868f9a3ca18624fc0892c44`.
- Git blob: `728cf28646db225f3c266a4bb73a6112b1f60330`.
- Status: `PREREGISTERED_BEFORE_GENERATION`.
- **No V158 transcriber/candidate/generation receipt/score exists yet. V158 professional-reference reads = 0; score calls = 0.**

### Sealed V158 architecture
1. **Timebase / bar phase**
   - Dynamic beat times remain audio-derived from fused mix+drums onset envelope and piecewise-linear mapping.
   - Four-state sequential Viterbi bar-position model replaces V157's simple mean-accent phase selector.
   - State transitions: nominal cyclic next-state probability `0.985`; same-state missing-beat tolerance `0.0075`; skip-one-state extra-beat tolerance `0.0075`.
   - State-0/downbeat emissions use deterministic drums accent, mix accent, Bass accent, low-frequency spectral flux and harmonic chroma-change novelty with preregistered weights `1.0/0.5/0.5/0.75/0.75`.
   - No reference-derived shift/tempo/origin constants.
2. **Bass**
   - Onset-first: each distinct `onset_detect(backtrack=true)` attack becomes an event proposal before pitch assignment; pYIN voicing may not erase attacks.
   - Minimum inter-onset collapse only 35 ms; repeated same-pitch attacks retained.
   - Pitch uses pYIN as soft evidence plus a five-harmonic fundamental template over MIDI 28–67.
   - Explicit candidate/candidate±12 octave comparison with the same harmonic score and lower-MIDI tie break; harmonic fallback works when pYIN is unvoiced.
3. **Guitar**
   - Basic Pitch remains one fixed proposal pass: onset 0.50, frame 0.30, 90 ms, MIDI 40–88, no sweep.
   - Raw onset-local CQT-only completion is forbidden.
   - New multi-frame 36-bin/octave harmonic-template tracker uses five harmonics, minimum 3-frame persistence, max 6 simultaneous pitches, sparse residual-template pursuit, and explicit ±12 register comparison.
   - Persistent harmonic-template tracks may add proposals; single-frame CQT peaks may not.
4. **Protocol**
   - CPU-only deterministic environment; one Demucs separation, one generation workflow/run, one candidate, independent reference-blind QC, candidate freeze before reference access, then one separately sealed score call only.
   - Prior V154/V155/V157 candidates, scores, diagnostics and exact reference-derived values are prohibited generation inputs.

## Exact next steps — RESUME HERE
1. Re-fetch latest checkpoint/head before writes because concurrent continuations exist.
2. Implement canonical `validation/v158_cpu_multitrack/transcribe_v158.py` exactly to the frozen preregistration, with no professional-reference/scorer or prior generated-output imports/reads.
3. Implement independent `validation/v158_cpu_multitrack/structural_qc.py` matching the V158 schemas and preregistered invariants, including Viterbi-state-path length, Bass onset provenance, no free-standing single-frame CQT source, deterministic identities and score calls 0.
4. Pin both code blobs and seal a V158 pre-run receipt while candidate/workflow are absent.
5. Only then create the V158 generation workflow exactly once; creation itself is the sole trigger and no arm edit is allowed.
6. Generate exactly one deterministic CPU candidate, independent QC/freeze before reference read; then seal a new one-use score guard and score exactly once.
7. If a future candidate passes both 0.80 acoustic gates, only then resume Rhythm/Lead role separation, string/fret assignment, techniques and professional PDF work.
8. Fresh explicit authorization remains required immediately before Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
