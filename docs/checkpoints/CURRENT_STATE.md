# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 is COMPLETE / FROZEN / SCORED EXACTLY ONCE / BOTH FRONT-END GATES FAILED and is permanently consumed. V154 architecture + timebase diagnostics are COMPLETE / FROZEN. V155 is PREREGISTERED BEFORE GENERATION, and its generator implementation is now STAGED / NOT RUN. There is still no V155 candidate, no V155 professional-reference read, and V155 reference-facing score calls remain 0. Next: one CPU-only reference-blind V155 generation run, structural QC, candidate freeze/checkpoint, then and only then one guarded V155 score.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- **V154 scored candidate is consumed forever:** no modification, threshold sweep, correction, variant selection, tuned replacement, or rescoring of a modified V154 candidate.
- **V155 must obey one-candidate / no-sweep / no-reference-generation policy.** Freeze candidate before reference access.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Target remains fully automatic audio -> professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Song / immutable shared identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Audio: `public/gomywayfullaitest.m4a`; SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Source m104 = 2/4 (8 sixteenth steps); others 4/4.
- Meter map: `research/v154-professional-references/source-meter-to-fixed-grid-mapping.json`; SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- Frozen scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.

## Professional references — AUTHORITATIVE / FROZEN
- **Rhythm:** `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`; 946 rows; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`; equivalence PASS.
- **Lead:** `research/v154-professional-references/scorer-ready/lead-scorer-ready.json`; 447 pitched rows; SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- Lead timing: `research/v154-professional-references/lead-source-local-attack-timing.json`; SHA256 `a1c30e9a14048fac6da6801d1ace1db203daf8807511f26c76a268e3cbf426c3`.
- **Bass:** `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`; 547 pitched rows; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- Bass timing: `research/v154-professional-references/bass-source-local-attack-timing.json`; SHA256 `7d2f4eed21413c6169ec8fcea75274b64c6dc8bb5f3c8de9cbc536b94afab244`.
- Lead rendered pages 84–105 were recovered and byte-authenticated; screenshot bytes remain uncommitted.
- Combined immutable reference: `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; Guitar 1393 / Bass 547; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; freeze run `33138868905`, job `98744968281`, commit `46e42ab`.

## V154 — CONSUMED / ONE SCORE PERMANENTLY CLOSED
### Candidate
- `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json`; SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`.
- Run `33096559281`, job `98602884120`, head `986e2a69a6cb877a203d2f8b04115914dc8fd2e6`; Guitar 1089 / Bass 635.
- Historical artifact id `9656706944`; digest `sha256:f0944432c37b369ac38cd25d058265a76f36b23e2f0bcf9808880d9e141dc518`.

### Frozen score
- `debug/v154-cpu-autonomous/v154-frontend-reference-score/score.json`; SHA256 `c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b`.
- Receipt: `debug/v154-cpu-autonomous/v154-frontend-reference-score/score-receipt.json`; validation PASS; `referenceFacingScoreCalls=1`; wrapper invocation count 1.
- Run `33139017517`, job `98745430956`; freeze commit `f687153`.
- Guitar primary timing-aware pitch F1 `0.04915390813859791` — FAIL vs 0.80.
- Bass primary timing-aware pitch F1 `0.1116751269035533` — FAIL vs 0.80.
- **V154 reference-facing score count is permanently 1.**

### Frozen diagnostics / caveats
- Architecture diagnostic: `debug/v154-cpu-autonomous/v154-frontend-reference-score/architecture-diagnostic.json`; SHA256 `bcc7aa275fb9c8dab3e0e9350043c5d85d48788bc13c672d97ad949d4d5595cd`; run `33139198143`, job `98746009145`, commit `b6a7637`.
- Caveat: its `measureIndexShiftScanPitchContent` is invalid/no-op because the same shift-bearing key was applied to generated and reference rows. Disregard that submetric. `globalAbsoluteShiftScan` remains valid because it shifts generated positions only.
- Timebase diagnostic: `debug/v154-cpu-autonomous/v154-frontend-reference-score/timebase-diagnostic.json`; SHA256 `ddaddaa4cfff1de1b5e7466813d9e08cfaeb9451b5a08406e820209543fe2f3c`; run `33139677372`, job `98747482513`, commit `e87f81e`.
- Timebase tie-break can favor proximity to prior `-13.25` on equal match counts; exact reference-derived shift/BPM values are diagnostic only and never future candidate parameters.
- Both diagnostics imported/called no official scorer, added 0 official score calls, wrote no corrected candidate, and were CPU-only.

## V154 root cause — FROZEN ARCHITECTURE DIAGNOSIS
- Historical transcriber blob `2f09ca1b8bc012749468f0079497ded71d318782` mapped `absolute_step_float = seconds / STEP_SECONDS`, hard-anchoring musical grid step 0 to audio/stem timestamp `0.000 s`.
- V154 had no audio-derived beat/downbeat/phase origin estimation and no explicit Demucs/Basic-Pitch latency compensation.
- Valid diagnostic global shift: both streams prefer about `-13.25` sixteenth steps, but this is **not** a permitted correction and does not solve recognition.
- Section trend is nonconstant: Guitar early `-11.50` -> late `-13.25`; Bass `-11.50` -> `-13.50`; shared slope indicates cumulative timebase drift as well as origin error.
- Large residual pitch/polyphony errors remain, so timing repair alone cannot pass gates.
- Never hardcode reference-derived `-13.25` or diagnostic ~129.01 BPM in a future generator.

## V155 — PREREGISTERED / GENERATOR STAGED / NOT RUN
- `V155` was confirmed unused before naming.
- Preregistration: `debug/v155-cpu-autonomous/preregistration.json`; commit `e5f51474308db460d7317cfbc4204f616ee0b069`; Git blob `9d6979b0d447d137db43017dfd18c9afdcb2a4d2`; status `PREREGISTERED_BEFORE_GENERATION`.
- Generator: `validation/v155_cpu_multitrack/generate_v155.py`; staging commit `ace14633063c8ec8ce63fd201f52514fc9cd96ae`; Git blob `d1ade9d49e4cd1d599844bc054710c146d5d1d92`.
- **Generator has not run. No V155 candidate or generation receipt exists yet. V155 reference-facing score calls = 0.**

### Sealed V155 architecture
- CPU only: Python 3.10; torch 2.8.0 CPU; numpy 1.26.4; demucs 4.1.0; Basic Pitch 0.4.0; librosa 0.11.0; imageio-ffmpeg 0.6.0.
- Separation: `htdemucs_6s`, shifts 1, jobs 1, dedicated Guitar + Bass stems, no fallback.
- Timebase: audio-derived dynamic beat times; deterministic 4-beat downbeat-phase selection; piecewise-linear beat grid; never assume `t=0` is musical grid step 0; no reference-derived timing constants.
- Bass: HPSS harmonic Bass stem + `librosa.pyin` + onset/voicing/pitch-change segmentation; Basic Pitch not used.
- Guitar: dedicated Guitar stem + one fixed Basic Pitch pass cross-checked/augmented by harmonic-CQT salience/onset evidence; no threshold sweep/reference-guided completion.
- Exactly one candidate; same-stream MIDI/grid dedup only; structural QC reference-blind.
- Frozen gates remain Guitar timing-aware pitch F1 >= 0.80 and Bass >= 0.80. If V155 fails: freeze, diagnose, new version; never retune consumed V155.

## Exact next steps — RESUME HERE
1. Stage a one-use CPU workflow that mechanically pins prereg blob `9d6979...`, generator blob `d1ade9...`, and exact audio SHA256 before running anything.
2. Workflow must reject professional-reference/scorer imports in V155 generator, install pinned CPU stack, normalize exact historical audio, run `htdemucs_6s`, assert Guitar/Bass/Drums stems, and run `generate_v155.py` exactly once.
3. Emit only `debug/v155-cpu-autonomous/generated.json` + `generation-receipt.json` (plus small identity metadata if needed); do not commit stems/audio.
4. Reference-blind structural QC must PASS; on pure setup/runtime bug before candidate creation, repair implementation without changing sealed architecture. Do not tune thresholds/architecture after seeing reference.
5. Freeze/checkpoint candidate + exact SHA/counts/timebase/model identities with **V155 score calls still 0**.
6. Only after that checkpoint construct a guarded one-use V155 scoring wrapper and score exactly once against frozen reference/scorer.
7. Stay CPU-only unless fresh explicit user authorization is obtained immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
8. Do not resume role separation/string/fret/technique/PDF work until a front-end candidate passes acoustic gates.
