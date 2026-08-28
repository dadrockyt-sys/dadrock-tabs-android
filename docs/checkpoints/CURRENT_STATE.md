# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V158 is permanently consumed and diagnosed. V159 is now PREREGISTERED, reference-blind, CPU-only, and timebase-first. No V159 implementation code, timebase artifact, candidate, generation run, or score exists yet. The next allowed action is to seal the V159 numeric implementation contract before writing V159 implementation code. No GPU/Modal/CUDA has been used and main/Production remains untouched.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable shared identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference path `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; Git blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`.
- Front-end gates remain combined Guitar primary timing-aware pitch F1 >= `0.80` AND Bass primary timing-aware pitch F1 >= `0.80` before role/string/fret/technique/PDF work.

## Closed historical versions
- V154: score count 1 forever; Guitar F1 `0.04915390813859791`, Bass F1 `0.1116751269035533`; failed.
- V155: protocol-invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: score count 1 forever; Guitar F1 `0.07692307692307694`, Bass F1 `0.05757575757575757`; failed.
- **V158: score count 1 forever; Guitar F1 `0.007756948933419521`, Bass F1 `0.001976284584980237`; failed and consumed. Never modify/regenerate/rescore.**

## V158 frozen score protocol/results
- Candidate freeze commit `1164742a49f6b760dbf3f995e91c520493f425d8`.
- Candidate `debug/v158-cpu-autonomous/generated.json`: blob `1ddb1849b3cfefc14b60f6b5ac72af9ffcdc7fa6`; SHA256 `2a9e8bdfbe48f03dc5d3734780aeb937ef0c5654d55a40536069ed30ee46bcc9`; Guitar 1701; Bass 465.
- Sole generation run `33145878069`; run number 1; attempt 1; SUCCESS; workflow self-removed.
- Sole score run `33147577735`; run number 1; attempt 1; SUCCESS as protocol; scorer invoked exactly once; workflow self-removed.
- Score freeze commit `8681e0d80b3f5c9f0e7a3dd0c0b71dbfc0d77b19`.
- Score `debug/v158-cpu-autonomous/frontend-reference-score/score.json`: blob `1a4d113d7d3c3f1fdf4106bc0cada9b2914ce2cd`; SHA256 `e0043db204849842c1425adeac89696c250cf8e6daf748b39473c77220c9bdf4`.
- Consumption receipt blob `a311305775bc9b26d2ff82f5a55c4cc0e5e8b378`; status `COMPLETE_CONSUMED`; retry false; candidate SHA/blob unchanged before/after.

## V158 post-score architecture diagnosis — FROZEN
- Artifact `debug/v158-cpu-autonomous/post-score-architecture-diagnosis.json`.
- Freeze commit `8f2e03032cc5b323afd0b4668660199425bc585f`; Git blob `d7c5720b27f74f1f710b96a6b0da70569ae48bbc`.
- Diagnosis reference payload reads = 0; additional scorer calls = 0; candidate untouched; threshold sweep false; GPU false.
- **Proven critical failure:** structural QC had `2986` tracked beats across ~`216.45 s`, equivalent to `827.7200277200278 BPM` and `72.488 ms` mean beat spacing. The musical coordinate system was unusable.
- **Strongest root-cause hypothesis:** V158 passed a signed robust-z fused onset envelope directly to `librosa.beat.beat_track`; V158 contract explicitly allowed negative values and the sole generation run emitted `RuntimeWarning: invalid value encountered in log1p` from librosa rhythm processing.
- **Second architecture defect:** V158 bar-phase Viterbi state deltas changed absolute beat ordinal, allowing a phase model to stretch/compress time.
- Guitar overgeneration and Bass undercount are secondary unresolved recognition risks; do not tune them from V158 score because the broken timebase dominates and the aggregate score is not source-conditional.

## V159 preregistration — SEALED BEFORE IMPLEMENTATION
- Artifact `debug/v159-cpu-autonomous/preregistration.json`.
- Commit `6264131c2c515ae2ac9b7c64627cabc70382c825`; Git blob `2eca55dc344908a791ba7946f42d77fbd7b8926d`.
- Schema `dadrock.tabs.v159.reference-blind-cpu-preregistration.v1`; status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`.
- Purpose: isolate the timebase repair while keeping V158 Guitar/Bass recognition numerics unchanged in substance; **no V158 score-derived threshold tuning**.
- V159 runtime is forbidden from reading any prior generated candidate, score, diagnostic, or professional reference.
- CPU-only deterministic execution/dependency identities remain the same as V158.

### V159 preregistered timebase architecture
1. Materialize a standalone V159 timebase artifact and independently QC it **before any Guitar/Bass pitch inference**.
2. Direct beat envelope = equal fusion of mix/drum onset strengths after finite clamp to >=0 and deterministic unit-max scaling. Signed robust-z is forbidden as direct beat-tracker input.
3. `librosa.beat.beat_track` remains fixed at start BPM 120, tightness 100, sparse mode; RuntimeWarning/NaN/Inf in rhythm construction is fatal before candidate emission.
4. Every accepted detected beat advances absolute beat ordinal by exactly one; sixteenth step = `4 * absoluteBeatOrdinal`.
5. Bar phase is one static 4-beat phase chosen from audio accent evidence. It labels downbeats only and **cannot alter beat times or ordinal**. Dynamic Viterbi state transitions are removed.
6. Musical origin = phase-consistent downbeat at/immediately before first accepted tracked beat, using only early detected beat period for at most 0..3 prefix beats. No professional-reference shift.
7. Generated front-end measure mapping remains fixed 16 sixteenth steps per measure; generation consumes no professional-reference meter map.

### V159 preregistered pre-candidate timebase QC
Must pass before pitch inference/candidate creation:
- fused envelope provenance finite/nonnegative and nonzero;
- zero rhythm RuntimeWarnings;
- tracker tempo finite/positive;
- >=8 strictly increasing finite beat times and positive IBIs;
- mean/median IBI implied BPM and beat-count/duration implied BPM each within generic `30..300` BPM;
- median-IBI BPM / tracker tempo within `0.5..2.0` to tolerate ordinary half/double tempo but reject pathological divergence;
- selected phase in 0..3;
- beat ordinal increments exactly one;
- raw grid strictly increasing;
- reference read false.
Required diagnostics include duration, beat count, tracker tempo, mean/median IBI, implied BPMs, tempo ratio, all four phase scores, leading beat count, early period, grid extent, and warnings.
- Any failure aborts V159 before authoritative candidate creation, freezes failure, and forbids re-arm of V159.

## Current hard boundary
- **V158 consumed forever; V158 diagnosis frozen.**
- **V159 preregistration frozen; do not change architecture semantics after seeing generation output.**
- **No V159 candidate/timebase/run/score exists yet.**
- **No professional-reference read is allowed during V159 implementation/generation/QC.**
- **No GPU execution has occurred. main/Production untouched.**

## Exact next steps — RESUME HERE
1. Re-fetch latest branch head/checkpoint before every write because concurrent continuations may exist.
2. Create and freeze `debug/v159-cpu-autonomous/implementation-contract.json` before V159 implementation code. It must pin exact numerics for the preregistered timebase/QC and copy V158 Guitar/Bass numerics unchanged.
3. Only after contract freeze, implement separate V159 timebase builder + independent timebase QC + candidate transcriber consuming the frozen timebase + independent structural QC.
4. Seal exact code identities and a pre-run receipt before arming any workflow.
5. Create the V159 generation workflow exactly once; creation is the sole trigger. No branch writes while active. If timebase QC fails, freeze failure and self-remove without a candidate; never re-arm V159.
6. If timebase QC + structural QC pass, freeze exactly one V159 candidate. Only then may a one-shot professional-reference scoring guard/workflow be sealed and invoked exactly once.
7. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
