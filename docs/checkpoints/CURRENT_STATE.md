# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V158 is permanently consumed/diagnosed. V159 reference-blind CPU preregistration and numeric implementation contract remain SEALED. The V159 timebase builder, independent pre-pitch timebase QC, frozen-timebase transcriber, independent structural QC, and negative runtime guard are implemented. A song-blind static-only V159 preflight has now been added and its sole run #1 / attempt #1 is in progress. No V159 audio processing, Demucs separation, timebase artifact, candidate, generation run, structural-QC receipt, or score has been produced. Exact code identity sealing, pre-run receipt, and the one-shot CPU generation workflow remain. No professional-reference reads occurred. No GPU/Modal/CUDA has been used and main/Production remains untouched.**

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

## V159 implementation progress — SAVED
Completed/current files:
- `validation/v159_cpu_autonomous/build_timebase_v159.py` — commit `583f7fa2823a6dfd829dbfa9137182b6fd86882f`.
  - Standalone write-once reference-blind timebase builder.
  - Reads sealed prereg/contract + source audio + normalized mix + fresh drums/bass/guitar stems only.
  - Implements positive-unit fused onset beat tracker, warning capture, static four-phase evidence, prefix extrapolation, sequential ordinals/grid steps, diagnostics, and safety flags.
- `validation/v159_cpu_autonomous/timebase_qc_v159.py` — commit `96514a32cc4f82999d3c3bef50d5fa0b7508e2f6`.
  - Independent write-once hard pre-pitch QC; recomputes identities and tempo/IBI/grid/phase invariants.
  - Nonzero terminal failure; records `pitchInferenceInvoked: false`.
- `validation/v159_cpu_autonomous/transcribe_v159.py` — commit `5ffb751929d640579d24ab791945826f21420938`.
  - Self-contained sealed V158 pitch numerics applied only after `validate_runtime_boundary(args)` proves the exact frozen timebase has an independent `PASS` QC receipt.
  - Uses frozen-grid interpolation/extrapolation; cannot build/rephase the timebase.
  - Writes exactly one candidate + generation receipt; embeds the CPU environment receipt.
- `validation/v159_cpu_autonomous/structural_qc_v159.py` — introduced at `1c4cf06824c75de925320163cf6992f2da8c416e`, current amendment commit `47f7362ed7c6544a94f6a3cd4da51169ce12a474`.
  - Independently recomputes event mapping from frozen timebase, MIDI ranges, source rules, same-stream dedupe/order, counts, hash chains, code pins, and safety.
  - Single-generation proof comes from the standalone CPU environment receipt embedded exactly in the generation receipt: workflow run number `1`, attempt `1`, positive run ID.
- `debug/v159-cpu-autonomous/negative-runtime-guard.py` — commit `5cf5382e6b8b8410523f2084c1b45ddd9531df83`.
  - Static reviewer-facing guard for professional-reference/scorer/prior-version runtime path leakage.
  - Prohibits pitch imports/calls in pre-pitch timebase files and checks transcriber ordering so frozen timebase-QC PASS validation occurs before pitch inference.

## CPU/dependency and stem-layout audit — COMPLETE
Reference-blind inspection of prior CPU setup established the intended V159 host layout without reading any professional-reference/scoring artifact:
- Python `3.10`.
- `torch==2.8.0` from the CPU wheel index; expected runtime `2.8.0+cpu`, `torch.version.cuda is None`, `torch.cuda.is_available() is False`.
- `numpy==1.26.4`, `scipy==1.13.1`, `soundfile==0.12.1`, `basic-pitch==0.4.0`, `demucs==4.1.0`, `imageio-ffmpeg==0.6.0`, `librosa==0.11.0`.
- Deterministic CPU separation pattern: seed `0`, one Torch thread/inter-op thread, deterministic algorithms enabled, `htdemucs_6s`, device `cpu`, `--shifts 1`, `-j 1`.
- Exact fresh stem layout after normalizing `/tmp/v159-normalized.wav`: `/tmp/v159-demucs/htdemucs_6s/v159-normalized/guitar.wav`, `bass.wav`, and `drums.wav`.
- Historical normalization identity remains SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- This audit did not execute Demucs or open song audio.

## Static preflight — IN PROGRESS
- Added `.github/workflows/v159-static-preflight.yml` at commit `7482e15ec60f99001c61584dd167ef142d34e7f4`.
- Workflow is path-self-triggered only and read-only (`contents: read`).
- Sole run ID `33195208763`; workflow run number `1`; attempt `1`; event `push`; head commit `7482e15ec60f99001c61584dd167ef142d34e7f4`.
- It performs only: sealed prereg/contract blob checks, generated-artifact absence checks, `python -m py_compile`, the V159 negative-runtime guard, and a final proof that no runtime artifact was created.
- It installs no project/audio dependencies and invokes no V159 runtime module, song audio, Demucs, pitch recognition, scorer, or professional reference.
- At this checkpoint write the audit job is still `in_progress`; no PASS is claimed yet.

## Validation status
- **No V159 song audio processing has run yet.**
- No fresh Demucs separation, timebase construction, timebase QC, pitch inference, candidate, structural-QC receipt, or score has run.
- A local sandbox checkout/compile retry still could not resolve `github.com`; therefore local syntax execution is not counted as evidence.
- GitHub-hosted static reviewer/preflight run #1 is in progress and is the authoritative pending syntax/AST check.
- Professional-reference reads during this V159 implementation/resume phase: `0`.
- V159 reference-facing score calls: `0`.
- GPU/Modal/CUDA executions: `0`.
- `main`/Production modifications: `0`.

## Current hard boundary
- V158 consumed; diagnosis frozen.
- **V159 preregistration + numeric contract frozen. Do not change those semantics based on later output.**
- V159 implementation code exists but has not been executed on the song.
- No pitch inference is allowed until a fresh V159 timebase-QC receipt freezes `PASS` inside the single CPU generation workflow.
- No professional-reference read during implementation/generation/QC.
- No branch writes while the eventual one-shot generation workflow is active.
- No GPU execution without fresh explicit authorization.

## Resume verification — 2026-08-28
- Re-fetched `docs/checkpoints/CURRENT_STATE.md` and branch metadata before resuming.
- Initial verified resume head was `fbebd6afe3138f8d1e8d2b7b4f60f0ba7e20ee6d`; a checkpoint-only resume verification commit advanced it to `fa999290ac3448e1159da2fe9b05f4cfb71f6846` before the static preflight was created.
- Static preflight creation then advanced branch head to `7482e15ec60f99001c61584dd167ef142d34e7f4`.
- No candidate/generation progress existed before creating the static preflight.

## Exact next steps — RESUME HERE
1. Re-fetch latest branch head/checkpoint before every write.
2. Wait only by active polling in this same work session for V159 static preflight run `33195208763` to finish; inspect its jobs/logs. Do not claim PASS until all static steps succeed.
3. If static preflight fails, resolve implementation-only/static defects without changing sealed V159 numerics, then use a new explicitly audited static workflow version rather than re-running the consumed attempt.
4. If static preflight passes, freeze exact final runtime code/blob identities and create `dadrock.tabs.v159.pre-run-identity-receipt.v1` proving no timebase/candidate/generation/environment/structural-QC receipt existed at seal and reference reads/score calls were zero.
5. Only after reviewer/pre-run sealing, arm exactly one V159 CPU generation workflow; creation is the sole trigger. The workflow must create a CPU environment receipt with `workflowRunNumber=1`, `workflowRunAttempt=1`, and positive `workflowRunId`.
6. Workflow order: verify audio/normalization identity → fresh CPU `htdemucs_6s` → build write-once timebase → independent timebase QC. If QC FAILS, freeze terminal V159 failure and create no candidate. If PASS, run transcriber → independent structural QC.
7. If timebase + structural QC pass, freeze exactly one candidate, then separately seal a one-shot scoring guard/workflow for exactly one professional-reference score.
8. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
