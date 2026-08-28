# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V158 is permanently consumed/diagnosed. V159 reference-blind CPU preregistration AND numeric implementation contract are now SEALED before implementation code. No V159 implementation code, timebase artifact, candidate, generation run, or score exists yet. Next allowed work is to implement the exact sealed V159 components: standalone timebase builder, independent timebase QC, candidate transcriber consuming the frozen timebase, and independent structural QC. No professional-reference reads are allowed during this work. No GPU/Modal/CUDA has been used and main/Production remains untouched.**

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
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference path `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`.
- Front-end gates: combined Guitar primary timing-aware pitch F1 >= `0.80` AND Bass >= `0.80` before role/string/fret/technique/PDF work.

## Closed historical versions
- V154: score count 1 forever; Guitar F1 `0.04915390813859791`, Bass F1 `0.1116751269035533`; failed.
- V155: invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: score count 1 forever; Guitar F1 `0.07692307692307694`, Bass F1 `0.05757575757575757`; failed.
- **V158: score count 1 forever; Guitar F1 `0.007756948933419521`, Bass F1 `0.001976284584980237`; failed/consumed; never modify/regenerate/rescore.**

## V158 frozen diagnosis
- `debug/v158-cpu-autonomous/post-score-architecture-diagnosis.json`; freeze commit `8f2e03032cc5b323afd0b4668660199425bc585f`; blob `d7c5720b27f74f1f710b96a6b0da70569ae48bbc`.
- Reference payload reads during diagnosis 0; additional score calls 0.
- Proven failure: `2986` tracked beats over ~`216.45s` => `827.7200277200278 BPM`, mean beat spacing `72.488ms`.
- Strong root-cause hypothesis: signed robust-z beat envelope fed into librosa beat tracking; generation emitted `RuntimeWarning: invalid value encountered in log1p`.
- Second defect: bar-phase Viterbi deltas changed absolute beat ordinal/time scale.
- Pitch-source tuning from V158 aggregate score remains forbidden.

## V159 preregistration — SEALED
- `debug/v159-cpu-autonomous/preregistration.json`.
- Commit `6264131c2c515ae2ac9b7c64627cabc70382c825`; blob `2eca55dc344908a791ba7946f42d77fbd7b8926d`.
- Schema `dadrock.tabs.v159.reference-blind-cpu-preregistration.v1`; status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`.
- Timebase-first architecture; V158 Guitar/Bass recognition numerics unchanged in substance; no V158 score-derived threshold tuning.
- V159 runtime cannot read prior candidates/scores/diagnostics or professional reference.
- Standalone timebase must pass independent QC before any pitch inference/candidate creation.

## V159 numeric implementation contract — SEALED
- `debug/v159-cpu-autonomous/implementation-contract.json`.
- Commit `b8e8cba795c2aa0d7d3990265b2472af8d1d7e06`; blob `83dfee2d537d00dbced367bdbc467d167a96db2f`.
- Schema `dadrock.tabs.v159.numeric-implementation-contract.v1`; status `SEALED_BEFORE_IMPLEMENTATION_CODE`.

### Exact V159 timebase numerics
- Analysis SR `22050`, hop `256`.
- Reject nonfinite onset arrays. Clamp onset strengths to >=0, require positive max > `1e-12`, divide by max. Beat envelope = `0.5*unitMix + 0.5*unitDrums`.
- `librosa.beat.beat_track`: start BPM `120`, tightness `100`, sparse=true.
- Capture warnings during onset/beat/rhythm construction; any `RuntimeWarning` is fatal before successful timebase output.
- Minimum detected beats `8`.
- Generic accepted BPM bounds `30..300` for mean-IBI, median-IBI, and beat-count/duration implied BPM.
- Tempo consistency ratio = median-IBI BPM / tracker BPM; must be `0.5..2.0` inclusive.
- Phase evidence keeps V158 weights: drums 1.0, mix 0.5, bass 0.5, low-frequency flux 0.75, harmonic-change 0.75; low-frequency max 200Hz, chroma bins 12.
- Four static phases. Phase score = mean weighted accent on phase/downbeats minus mean on non-downbeats; tie tolerance `1e-12`, lower phase wins.
- `leadingBeatCount = (-selectedPhase) % 4`; early period = median first up-to-8 positive IBIs; prepend exactly 0..3 extrapolated beats.
- Absolute beat ordinal = plain sequential index over prefix + detected beats; grid step = `4*ordinal`; bar phase never changes ordinal.
- Quantization `int(round(rawGridStep))`; measure `absStep//16+1`; step `absStep%16`; no professional-reference meter map in generation.

### Pitch numerics — deliberately unchanged from V158
- Harmonic template: 36 bins/octave; harmonics 1..5 weights `[1, .5, .3333333333, .25, .2]`; radius 1.
- Bass: MIDI 28..67; onset backtrack true; min IOI 35ms; pitch window 180ms; pYIN frame 2048/hop256; sigma .75; fusion weight .75; same exact V158 scoring/event duration rules.
- Guitar: MIDI 40..88; Basic Pitch onset `.5`, frame `.3`, min length 90ms, melodia=true; persistent track min3 frames/radius1/max6; same exact V158 register repair and harmonic-track rules; added track duration `.07s`.
- Same grid/MIDI dedupe and source precedence.

### Timebase-QC terminal rules
- Timebase QC must pass before pitch inference.
- Strictly increasing finite detected/grid beat times; positive IBIs; warning count 0; finite positive tracker tempo.
- Grid step differences exactly 4; detected beat ordinal increments exactly 1; phase and leading count consistent.
- Any timebase-QC failure is terminal for V159 before candidate creation: freeze failure and never re-arm.

## Current hard boundary
- V158 consumed; diagnosis frozen.
- **V159 preregistration + numeric contract frozen. Do not change those semantics based on later output.**
- No V159 code/timebase/candidate/run/score exists yet.
- No professional-reference read during V159 implementation/generation/QC.
- No GPU execution; main/Production untouched.

## Exact next steps — RESUME HERE
1. Re-fetch latest branch head/checkpoint before every write.
2. Implement `validation/v159_cpu_multitrack/build_timebase.py` exactly from frozen contract.
3. Implement independent `validation/v159_cpu_multitrack/timebase_qc.py`.
4. Implement V159 candidate transcriber consuming the frozen timebase while preserving V158 pitch numerics, plus independent structural QC.
5. Freeze exact code identities and create a V159 pre-run identity receipt before any workflow.
6. Arm exactly one V159 CPU generation workflow; creation is sole trigger; no branch writes while active. If timebase QC fails, freeze terminal failure/self-remove without candidate.
7. If timebase + structural QC pass, freeze exactly one candidate, then seal a one-shot score guard/workflow for exactly one professional-reference score.
8. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
