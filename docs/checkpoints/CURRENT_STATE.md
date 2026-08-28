# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 broad-Other CPU recognition is COMPLETE / FROZEN / SCORED EXACTLY ONCE / BOTH FRONT-END GATES FAILED. Post-score architecture and timebase diagnostics are COMPLETE / FROZEN. Root cause is now isolated to a shared upstream timebase design error (audio `t=0` was incorrectly treated as musical grid origin, with a small cumulative tempo/timebase drift) plus substantial residual pitch/polyphony recognition errors. V154 is permanently consumed and non-tunable. `V155` code search currently returns no existing use, so V155 is available for the next preregistered reference-blind CPU experiment.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- **V154 scored candidate is consumed forever.** Diagnostic inspection may read it/reference because scoring is finished, but no modification, threshold sweep, correction, variant selection, tuned replacement, or rescoring of a modified V154 candidate is allowed.
- Do not commit professional-tab screenshot bytes. Private machine-readable reference artifacts remain research-branch-only.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Frozen song / protocol
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Audio: `public/gomywayfullaitest.m4a`; SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- V154 grid tempo: `129.19921875`, 4 steps/beat, nominal 16 steps/4-4 measure.
- Source m104 = 2/4 (8 sixteenth steps); others 4/4.
- Frozen meter map: `research/v154-professional-references/source-meter-to-fixed-grid-mapping.json`; SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- V154 CPU separator: `demucs==4.1.0`, `htdemucs`, shifts 1, jobs 1; `Other` = combined Rhythm+Lead; Bass independent.
- V154 Basic Pitch `0.4.0`: onset 0.5, frame 0.3, minimum 127.7 ms, melodia enabled, no threshold sweep.
- Frozen scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.

## Authoritative locations — RESUME HERE
### Frozen professional references
- **Rhythm:** `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`; 946 rows; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`; equivalence PASS.
- **Lead:** `research/v154-professional-references/scorer-ready/lead-scorer-ready.json`; 447 pitched rows; SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- Lead source-local timing: `research/v154-professional-references/lead-source-local-attack-timing.json`; SHA256 `a1c30e9a14048fac6da6801d1ace1db203daf8807511f26c76a268e3cbf426c3`.
- **Bass:** `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`; 547 pitched rows; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- Bass source-local timing: `research/v154-professional-references/bass-source-local-attack-timing.json`; SHA256 `7d2f4eed21413c6169ec8fcea75274b64c6dc8bb5f3c8de9cbc536b94afab244`.
- Lead rendered source pages 84–105 were recovered and byte-authenticated; screenshot bytes remain uncommitted.

### Immutable combined reference
- `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`
- SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Counts: Rhythm 946 + Lead 447 = combined Guitar 1393; Bass 547.
- Freeze run `33138868905`, job `98744968281`, commit `46e42ab`.
- Interface audit called `load_reference` only; `score_stream` was not called during payload freeze.

### Consumed generated V154 candidate
- `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json`
- SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`.
- Generation run `33096559281`, job `98602884120`, head `986e2a69a6cb877a203d2f8b04115914dc8fd2e6`.
- Counts: combined Guitar 1089; Bass 635.
- Historical artifact: `v154-broad-other-cpu-33096559281`, artifact id `9656706944`, digest `sha256:f0944432c37b369ac38cd25d058265a76f36b23e2f0bcf9808880d9e141dc518`.
- Artifact identities reconfirmed: normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`; Other stem SHA256 `c288232d1fff42f0fcf57e3e46dfd274428cb2d4e1c916f7fe663d28d42b1440`; Bass stem SHA256 `918670e9293b5aa633593fbe491ff520a045774ead7cbdba0a851301d4e86b0f`.

### Frozen one-time V154 score
- Score: `debug/v154-cpu-autonomous/v154-frontend-reference-score/score.json`; SHA256 `c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b`.
- Receipt: `debug/v154-cpu-autonomous/v154-frontend-reference-score/score-receipt.json`; validation PASS; `referenceFacingScoreCalls=1`; `scorerInvocationCountInWrapper=1`.
- Score run `33139017517`, job `98745430956`; trigger `2c1155f73b99b804267763e97fcf750f985f40c7`; freeze commit `f687153`.
- **Reference-facing score count is permanently closed at 1 for V154.**

### Frozen post-score diagnostics
- Architecture diagnostic: `debug/v154-cpu-autonomous/v154-frontend-reference-score/architecture-diagnostic.json`; SHA256 `bcc7aa275fb9c8dab3e0e9350043c5d85d48788bc13c672d97ad949d4d5595cd`; run `33139198143`, job `98746009145`, freeze commit `b6a7637`.
- Timebase diagnostic: `debug/v154-cpu-autonomous/v154-frontend-reference-score/timebase-diagnostic.json`; SHA256 `ddaddaa4cfff1de1b5e7466813d9e08cfaeb9451b5a08406e820209543fe2f3c`; script `validation/v154_cpu_multitrack/diagnose_frontend_timebase.py`; run `33139677372`, job `98747482513`, freeze commit `e87f81e`.
- Both diagnostics imported/called **no official scorer**, made **0 additional official reference-facing score calls**, wrote no corrected candidate, were CPU-only, and did not touch `main`/Production.

## V154 frozen score results — BOTH GATES FAIL
### Combined Guitar
- Primary ±0.5-step same-MIDI: matched 61 / generated 1089 / reference 1393.
- Precision `0.05601469237832874`; recall `0.04379038047379756`; **F1 `0.04915390813859791` — FAIL vs 0.80**.
- Gross ±2-step F1 `0.16760676873489122`.
- Pitch-content-by-measure diagnostic F1 `0.46333601933924257`.

### Bass
- Primary ±0.5-step same-MIDI: matched 66 / generated 635 / reference 547.
- Precision `0.10393700787401575`; recall `0.1206581352833638`; **F1 `0.1116751269035533` — FAIL vs 0.80**.
- Gross ±2-step F1 `0.2639593908629442`.
- Pitch-content-by-measure diagnostic F1 `0.5634517766497462`.

## V154 root-cause audit — COMPLETE / FROZEN
- Historical transcriber inspected at frozen blob `2f09ca1b8bc012749468f0079497ded71d318782`.
- Its `grid_location(seconds)` computed `absolute_step_float = seconds / STEP_SECONDS` and therefore hard-anchored **musical grid step 0 to audio/stem timestamp `0.000 s`**.
- V154 performed **no audio-derived beat/downbeat/phase origin estimation** and **no explicit Demucs/Basic-Pitch latency compensation** before `(measure, step)` mapping.
- Initial diagnostic found both streams independently prefer a global diagnostic shift of `-13.25` sixteenth-grid steps (~1.54 s), but this shift does not solve recognition and must never be applied as a correction to V154.
- Tighter section-wise diagnostic proves the shift is not constant:
  - Guitar early median `-11.50` → late median `-13.25` steps; delta `-1.75`.
  - Bass early median `-11.50` → late median `-13.50` steps; delta `-2.00`.
- Weighted shift-vs-time slopes independently agree:
  - Guitar slope `-0.001485`, diagnostic pure-tempo equivalent ~`129.007 BPM`.
  - Bass slope `-0.001248`, diagnostic pure-tempo equivalent ~`129.038 BPM`.
- These reference-derived BPM equivalents are **diagnostic only**; never hardcode them or use them to tune a future candidate.
- Root-cause conclusion: V154 has a **shared upstream timebase architecture failure** consisting of (a) missing automatic musical/downbeat origin alignment and (b) small cumulative tempo/timebase drift. Large residual pitch/polyphony errors are a separate recognition failure, so timing repair alone cannot satisfy the frozen gates.

## V155 naming/status
- Repository code search for `v155` returned no results on 2026-08-28; **V155 is available for the next experiment**.
- V155 does not yet have a generated candidate or score.

## Permanent rules carried forward
- Never use reference-derived `-13.25` or ~129.01 BPM as song-specific corrections/parameters in V155.
- V155 candidate generation must remain fully reference-blind.
- Do not threshold-sweep Basic Pitch and call that a new architecture; the recognition front end must change materially because residual pitch/polyphony performance is far below target.
- No GPU without fresh explicit authorization immediately beforehand.
- Do not resume role separation, string/fret assignment, techniques, or PDF polishing until a future front-end candidate passes the acoustic-recognition gates.

## Exact next steps — RESUME HERE
1. **Preregister V155 before any candidate generation.** Seal architecture, dependencies, model identities, timebase method, recognition method, structural-QC rules, frozen gates, and one-candidate/no-variant-selection policy.
2. V155 timebase must be **audio-derived and reference-blind**: estimate tempo plus beat/downbeat/phase from the audio itself; map transcription timestamps through that musical grid instead of assuming `t=0` = musical step 0. Do not feed V154 reference-derived offsets/BPM equivalents into it.
3. V155 recognition must materially change beyond V154 Basic Pitch thresholding. Prefer a polyphony-aware architecture that separately models monophonic/low-polyphony Bass and polyphonic Guitar/Other, with deterministic reference-blind post-processing only.
4. Generate **exactly one** new CPU V155 candidate. Structural-QC it reference-blind, freeze candidate + generation receipt before any reference access.
5. Build a newly sealed V155 one-time scorer receipt/protocol and score the frozen V155 candidate exactly once against the already-frozen professional references. Never select among candidates using the reference.
6. If V155 still fails the frozen acoustic gates, diagnose architecture and move to a new version; never retune a consumed candidate.
7. Fresh explicit user authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only unless separately authorized.
8. Only after a future candidate passes the front-end gates should Rhythm/Lead role separation, string/fret assignment, techniques, and professional PDF work resume.
