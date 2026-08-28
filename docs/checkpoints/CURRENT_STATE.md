# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 and V157 are permanently consumed after one failed reference score each. V155 is protocol-invalid and never scoreable. V156 is permanently aborted before candidate. V157 post-score architecture diagnosis is now COMPLETE / FROZEN: its automatic beat clock is stable but 4/4 bar/downbeat phase is still wrong; Guitar CQT-only completion adds many false positives; Bass onset detection is reasonably dense but pYIN event formation is severely sparse and misses low-register fundamentals. V157 score count stays 1 forever. Next: confirm V158 is unused and preregister a genuinely new reference-blind CPU architecture before any generation.**

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
- Root cause: fixed audio-t=0 grid origin plus drift and major pitch/polyphony errors. Reference-derived `-13.25` / ~129.01 BPM remain diagnosis-only.

### V155 — protocol invalid / score count 0 forever
- Prereg commit `e5f51474308db460d7317cfbc4204f616ee0b069`.
- Duplicate generation runs `33140245244` and `33140267460`; never score/select its outputs.

### V156 — aborted before candidate / score count 0 forever
- Intended run `33142942558`, job `98757604810`; deterministic separation passed but environment receipt failed before candidate due wrong cache lookup + missing `os` import.
- No candidate/reference score.

## V157 frozen generation
- Preregistration Git blob `0bcca0fbb53abcc8ad8736d8e5e71e32a14004f6`.
- Canonical transcriber blob `1d1725e2d79b173bd5fb0bfa7aefc25dce81dd58`; independent QC blob `5ff4df5b5c6b700272b349a1bbe709b15e17e794`; inherited reference-blind engine blob `3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8`.
- Sole generation run `33143471258`, run number 1, job `98759295729`; SUCCESS; generation workflow self-deleted.
- Candidate freeze commit `c26e41d239d44d656bf57cf195ed39416658b680`.
- Candidate `debug/v157-cpu-autonomous/generated.json`; SHA256 `f5dc7094b72f8e3a988b1fdd59808cb056461d7e12a6d41508942cf499de3e71`; Git blob `3491814f4cc075aaf3eefaecf2d179f57d2d5dae`.
- Counts: Guitar 1779 = Basic Pitch 1366 + CQT 413; Bass 113 pYIN; pre-grid excluded 0/0.
- Timebase QC: 448 beats; BPM `129.19921875`; IBI CV `0.027276358719819024`.
- Model blob SHA256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`, bytes 54,885,744.
- Stem SHA256: Guitar `b8685062c59f5c62253029f8294afdaf25f3f8adf8868ae97b47db09ab8838f9`; Bass `f109347354dd9ae4a293189834b1f6d58199a4eebe5d51dfeeedc6707c4a5316`; Drums `7ef184f2fc3b6f7fc12ea5c342bc537f6b69f1680ce36e9d4f7189be85d93e39`.
- Independent QC Git blob `3528adbceb640743cc8f0e472d2cd62c49c1ebc3`; PASS.

## V157 one-use score — permanently closed
- Guard Git blob `6396ff11f1b2960fb4c80c1633786c3089ec4883`.
- Pre-score receipt seal commit `0068a1d640a37add8a19ffc60545c468b2c0fd68`; score calls 0 at seal.
- Sole score run `33143986627`, run number 1, job `98760898781`; SUCCESS.
- Score freeze commit `19317e7e44687e910088892cf9bf3e1157efc45c`.
- Score SHA256 `ffd66347990eff113814f207c303773734e79c0461fa4e4d129f1de8472594d8`.
- Score receipt Git blob `d1e3145cae8b12e612012533e9060d21c95ccf24`; `referenceFacingScoreCalls=1`; wrapper invocation count 1.
- **V157 score count = 1 forever; never rescore/retune V157.**

### V157 frozen score — BOTH GATES FAIL
- Guitar primary ±0.5 same-MIDI: 122/1779/1393; precision `0.06857785272625071`; recall `0.08758076094759512`; **F1 `0.07692307692307694` FAIL**.
- Guitar gross ±2 F1 `0.21752837326607818`; measure-pitch-content F1 `0.4520807061790668`.
- Bass primary ±0.5 same-MIDI: 19/113/547; precision `0.168141592920354`; recall `0.03473491773308958`; **F1 `0.05757575757575757` FAIL**.
- Bass gross ±2 F1 `0.14242424242424245`; measure-pitch-content F1 `0.22424242424242424`.

## V157 post-score diagnostic — COMPLETE / FROZEN
- Diagnostic script `validation/v157_cpu_multitrack/diagnose_post_score.py`; Git blob `64723c75dbd257719b8846d4829466cda39cb25e`.
- Diagnostic run `33144115704`, run number 1, job `98761292358`; SUCCESS.
- Frozen diagnostic `debug/v157-cpu-autonomous/frontend-reference-score/post-score-diagnostic.json`; Git blob `fb0460f158f97230bb5c82193f9409306bfa2960`; freeze commit `51fcd9b93a495f939ce85a7ec578f7ea3d70c5de`.
- Safety: official scorer imported NO; official scorer called NO; additional reference-facing score calls 0; candidate modified NO; candidate variant written NO.

### Diagnostic findings
1. **Bar/downbeat phase remains wrong despite a stable beat clock.**
   - Global same-MIDI absolute-time diagnostic peaks at generated-only shift `-12.5` steps for BOTH Guitar and Bass.
   - Guitar diagnostic at that shift: matched 668 / generated 1779 / reference 1393; F1 `0.4211853720050442`.
   - Bass diagnostic at that shift: matched 96 / generated 113 / reference 547; precision `0.8495575221238938`, recall `0.17550274223034734`, F1 `0.29090909090909095`.
   - The exact `-12.5` value is **diagnostic only and may never be hardcoded into a future generator**. Architecture conclusion is only that V157's automatic 4/4 phase/origin selection is still unreliable.
2. **Guitar CQT-only completion is low-value/high-false-positive.**
   - Basic Pitch subset: 1366 events; strict F1 `0.07031533164189924`; measure-pitch-content F1 `0.47770931496919167`; shifted diagnostic F1 `0.4624864081188837`.
   - CQT-only subset: 413 events; strict F1 `0.02768549280177187`; measure-pitch-content F1 `0.12956810631229235`; shifted diagnostic F1 `0.04983388704318937`.
   - Generic architecture implication: future Guitar recognition should not use untracked onset-local CQT peaks as free-standing completion notes; use a stronger polyphonic proposal/tracking model or harmonic evidence to validate/repair model proposals instead.
3. **Bass onset detector is not the main count bottleneck; pYIN event formation is.**
   - Raw Bass onset detector found 465 onsets vs 547 reference attacks (`0.8501` ratio), but only 113 events survived event formation (`0.2430` of detected onsets; generated/reference ratio `0.2066`).
   - Generated Bass begins measure 8 and ends 102; reference spans 7–109; many reference-active measures have no generated Bass.
   - Generated Bass MIDI range effectively starts at 37; reference has substantial low-register content at MIDI 28–36, especially 31 and 35. Architecture evidence points to fundamental/octave tracking failure in addition to segmentation sparsity.
   - Generic architecture implication: future Bass should be **onset-first** (retain attack candidates) and use F0/harmonic evidence for pitch assignment, with an explicit fundamental-vs-octave model/fallback rather than requiring pYIN voiced segments to create events.

### Diagnostic caveat — MUST PRESERVE
- `quartileShiftDiagnostic` quartile 4 is invalid because the diagnostic range predicate accidentally includes all events `<=` the final bound when `q == 3`; quartile 4 therefore duplicates the whole-song scan. **Ignore all quartile-4 values.**
- Global shift scans, quartiles 1–3, source-breakdown metrics, Bass sparsity/count/pitch histograms, and scorer-independent strict/content metrics are unaffected by this caveat.

## Exact next steps — RESUME HERE
1. Re-fetch latest checkpoint/head before writes because concurrent continuations exist.
2. Confirm `V158` is unused before naming.
3. Preregister V158 **before any generation code/run**. It must be a genuine reference-blind architecture change, not a V157 threshold sweep or song-specific correction.
4. At minimum V158 should change all three failed architecture components:
   - **Timebase/bar phase:** retain dynamic beat times but replace simple four-phase mean-accent selection with a stronger reference-blind bar/downbeat model (e.g. sequential/Viterbi bar-state inference from drums, low-frequency accents, harmonic-change/novelty and structural first-onset evidence). No reference-derived shift constants.
   - **Bass:** onset-first event creation; assign pitch after preserving attacks using pYIN plus harmonic-stack/CQT fallback and explicit octave/fundamental scoring; never discard most attacks solely because pYIN voiced probability is weak.
   - **Guitar:** do not use CQT-only completion as free-standing note generation. Use one strong polyphonic proposal model plus harmonic/CQT evidence only for proposal validation, octave/register repair, and onset tracking, or adopt another genuinely polyphonic CPU model if viable.
5. Seal exact model/dependency/timebase/recognition/determinism/QC contracts and one-run/one-candidate policy before generation.
6. Generate exactly one V158 candidate reference-blind; independent QC/freeze before any reference read; then one newly sealed score call only.
7. If a future candidate passes both 0.80 acoustic gates, only then resume Rhythm/Lead role separation, string/fret assignment, techniques and professional PDF work.
8. Fresh explicit authorization remains required immediately before Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
