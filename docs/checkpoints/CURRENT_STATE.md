# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V159 is now TERMINAL and permanently consumed for generation. Its single reference-blind CPU workflow ran exactly once. The new timebase architecture passed independent pre-pitch QC and one candidate was generated, but independent structural QC crashed while serializing its receipt because a NumPy `bool_` reached `json.dumps`. The workflow correctly self-sealed and froze V159 with outcome `STRUCTURAL_QC_RUNTIME_FAIL`. The V159 candidate is NOT authoritative and is NOT eligible for professional-reference scoring. Never re-arm, regenerate, repair-in-place, structurally re-QC, or score V159. Professional-reference reads remain 0; V159 reference-facing score calls remain 0; GPU/Modal/CUDA executions remain 0; main/Production remains untouched. Next work is reference-blind diagnosis of the structural-QC serialization defect and a fresh preregistered successor version (V160 or later), not a V159 retry.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- **V159 is terminal: never re-arm/regenerate/re-run structural QC or score its candidate.**
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable song/reference identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference path `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`.
- Front-end gates: combined Guitar timing-aware pitch F1 >= `0.80` AND Bass >= `0.80` before role/string/fret/technique/PDF work.

## Closed historical versions
- V154: one score forever; Guitar `0.04915390813859791`, Bass `0.1116751269035533`; failed.
- V155: invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: one score forever; Guitar `0.07692307692307694`, Bass `0.05757575757575757`; failed.
- V158: one score forever; Guitar `0.007756948933419521`, Bass `0.001976284584980237`; failed/consumed.
- **V159: one generation run forever; score count 0 forever; terminal `STRUCTURAL_QC_RUNTIME_FAIL`; candidate non-authoritative/ineligible for scoring; never re-arm.**

## V158 frozen diagnosis
- `debug/v158-cpu-autonomous/post-score-architecture-diagnosis.json`; freeze commit `8f2e03032cc5b323afd0b4668660199425bc585f`; blob `d7c5720b27f74f1f710b96a6b0da70569ae48bbc`.
- Proven failure: `2986` tracked beats over ~`216.45s` ≈ `827.72 BPM`.
- Root cause: signed robust-z beat envelope produced invalid `log1p`; bar-phase Viterbi also altered absolute beat ordinal/time scale.
- Pitch-source tuning from V158 aggregate score remains forbidden.

## V159 sealed preregistration / numeric contract
- Preregistration: `debug/v159-cpu-autonomous/preregistration.json`; commit `6264131c2c515ae2ac9b7c64627cabc70382c825`; blob `2eca55dc344908a791ba7946f42d77fbd7b8926d`; schema `dadrock.tabs.v159.reference-blind-cpu-preregistration.v1`; status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`.
- Numeric contract: `debug/v159-cpu-autonomous/implementation-contract.json`; commit `b8e8cba795c2aa0d7d3990265b2472af8d1d7e06`; blob `83dfee2d537d00dbced367bdbc467d167a96db2f`; schema `dadrock.tabs.v159.numeric-implementation-contract.v1`; status `SEALED_BEFORE_IMPLEMENTATION_CODE`.

### V159 timebase numerics — immutable historical record
- SR `22050`, hop `256`; onset arrays finite; clamp >=0; require max > `1e-12`; divide by max.
- Fused beat envelope = `0.5*unitMix + 0.5*unitDrums`.
- `librosa.beat.beat_track`: start BPM `120`, tightness `100`, sparse=true.
- Captured `RuntimeWarning` during onset/beat/rhythm construction is fatal.
- Minimum detected beats `8`; mean/median/count-duration implied BPM each `30..300`; median-IBI BPM / tracker BPM `0.5..2.0`.
- Static phase evidence weights: drums `1.0`, mix `0.5`, bass `0.5`, low-frequency flux `0.75`, harmonic-change `0.75`; low-frequency max `200Hz`, chroma `12`.
- Four static phases; tie tolerance `1e-12`, lower phase wins.
- `leadingBeatCount=(-selectedPhase)%4`; early period = median first up-to-8 positive IBIs; prepend exactly 0..3 extrapolated beats.
- Absolute beat ordinal sequential over prefix+detected; grid step = `4*ordinal`; bar phase never changes ordinal.
- Quantize `int(round(rawGridStep))`; measure `absStep//16+1`; step `absStep%16`; generation uses no professional-reference meter map.

### V159 pitch numerics — immutable historical record
- Harmonic template 36 bins/octave; harmonics 1..5 weights `[1,.5,.3333333333,.25,.2]`; radius 1.
- Bass MIDI `28..67`; onset backtrack true; min IOI `35ms`; pitch window `180ms`; pYIN frame `2048`, hop `256`; sigma `.75`; fusion `.75`; same V158 duration/scoring rules.
- Guitar MIDI `40..88`; Basic Pitch onset `.5`, frame `.3`, min length `90ms`, melodia=true; persistent track min3 frames/radius1/max6; same V158 register repair/harmonic rules; added-track duration `.07s`.
- Same grid/MIDI dedupe and source precedence.

## V159 implementation — sealed Git blobs used by the run
- `validation/v159_cpu_autonomous/build_timebase_v159.py` → `45f0e5013f13064a71c854b2c0e026482a135a8b`.
- `validation/v159_cpu_autonomous/timebase_qc_v159.py` → `fae5054153c90360ed5ea3f504feb432ba73eaef`.
- `validation/v159_cpu_autonomous/transcribe_v159.py` → `290d26099f9ac082eb19173f03d1904f7fbab45d`.
- `validation/v159_cpu_autonomous/structural_qc_v159.py` → `a3fbf4e8d827aca955a0995fc31930a8c631c932`.
- `debug/v159-cpu-autonomous/negative-runtime-guard.py` → `6a068e4699dcbcac0e236a9c54ce10efe1c96d96`.
- `.github/workflows/v159-static-preflight.yml` → `28cc7d465a910dfdf1f919bc58e9696392ad718f`.

## CPU dependency / separation layout audit — COMPLETE
- Python `3.10`; `torch==2.8.0+cpu`; NumPy `1.26.4`; SciPy `1.13.1`; SoundFile `0.12.1`; Basic Pitch `0.4.0`; Demucs `4.1.0`; imageio-ffmpeg `0.6.0`; librosa `0.11.0`.
- CPU only: `torch.version.cuda is None`, `torch.cuda.is_available() is False`.
- Determinism: seed `0`; Torch threads/inter-op `1`; deterministic algorithms enabled; math-library threads `1`.
- Fresh separation: `htdemucs_6s`, device `cpu`, shifts `1`, jobs `1`, repeat count `1`.
- Stem layout: `/tmp/v159-demucs/htdemucs_6s/v159-normalized/{guitar,bass,drums}.wav`.

## Static preflight — PASS / CONSUMED
- Workflow commit `7482e15ec60f99001c61584dd167ef142d34e7f4`; run ID `33195208763`; run number `1`; attempt `1`; job `98930481313`; conclusion `success`; CPython `3.10.21`.
- All five Python files compiled.
- Negative runtime guard schema `dadrock.tabs.v159.negative-runtime-guard.v1`: `validation=PASS`, failures `[]`.
- No prior-version runtime paths; no professional-reference/scorer runtime paths; no pitch imports/calls in pre-pitch files; transcriber requires timebase-QC PASS before pitch.
- Static workflow created no song/timebase/candidate artifacts and must not be re-run.

## Pre-run identity receipt — SEALED
- `debug/v159-cpu-autonomous/pre-run-identity-receipt.json`.
- Seal commit `f9916cdb3ae0cbc2eecb3325c01fbfcac22b6bb4`; blob `9edb001227ce99570b0c4081102bf22276121499`.
- Schema `dadrock.tabs.v159.pre-run-identity-receipt.v1`; validation `PASS`; status `SEALED_BEFORE_GENERATION`.
- At seal: all generation artifacts and generation workflow absent; professional-reference reads `0`; score calls `0`; GPU/Modal/CUDA `0`; main/Production untouched.
- Generation-workflow creation was the sole trigger; expected run count `1`; second arm forbidden; duplicate run forbidden; branch writes while active forbidden.

## V159 one-shot CPU generation — CONSUMED / TERMINAL
- Arm commit: `0e33dc356cef573a146bfe74fae718a523aa8fec` (`research: arm sole V159 reference-blind CPU generation`).
- Workflow: `.github/workflows/v159-generate.yml`; created as the sole trigger and self-deleted in terminal freeze.
- Run ID `33195994387`; run number `1`; attempt `1`; job `98933144549`.
- Pre-run sealed-identity + negative-runtime guard: **PASS**.
- Exact CPU dependency assertions: **PASS**.
- Historical source audio identity: **PASS**.
- Deterministic normalized WAV identity: **PASS**.
- Fresh one-pass CPU `htdemucs_6s` separation: **PASS**.
- Environment receipt created; SHA256 `f1348bd53547b9b168793d694b9f777cde9b8b6e1fc3d03f069b5db216445154`.
- Timebase created; SHA256 `036b60261bdd07def93352ec18d03d13727e3f25cd3550d308fb0b9e94c73b53`.
- Timebase result: `448` detected beats; selected phase `1`.
- Independent timebase QC: **PASS**, failed checks `[]`; receipt SHA256 `d8b5337d884258aaa9d9f3a3ed48493396e226077f480db0b56bca9e60ba2a01`.
- Pitch inference then ran because the pre-pitch boundary had passed.
- Candidate created: SHA256 `a2057b0f160f8f689ea7593acb277e8a6c56325ef3183cfef58e7196907fb36c`; counts: combined Guitar `2276`, Bass `460`.
- Generation receipt created; SHA256 `a7551158b77be424f661e7eed9090e2656f6b3088c9c5df156e1ccc850b5476e`.
- Generation reported `referenceRead=false`, score calls `0`, timebase QC `PASS`.

## V159 terminal structural-QC runtime defect
- `validation/v159_cpu_autonomous/structural_qc_v159.py` reached receipt serialization after recomputing its checks.
- It crashed at `json.dumps(receipt, indent=2, sort_keys=True)` with:
  - `TypeError: Object of type bool_ is not JSON serializable`.
  - Stack ended at structural-QC source line 303 while writing the receipt.
- Therefore **no structural-QC receipt exists**.
- This is an implementation/runtime serialization defect, not a professional-reference score result.
- Do not infer structural PASS or FAIL from the crash; no valid independent structural-QC receipt exists.
- Do not repair and rerun V159. Any serialization fix belongs only in a newly preregistered successor version.

## V159 terminal freeze — AUTHORITATIVE
- Freeze commit: `e0ab58ef5766f6c1515453c05b80e86429140acb` (`research: freeze terminal V159 generation failure [skip ci]`).
- `debug/v159-cpu-autonomous/terminal-freeze.json`; Git blob `e3cb31788a87921ed7ebc44db1f523e6e081e9b8`.
- Schema `dadrock.tabs.v159.terminal-freeze.v1`; status `TERMINAL`.
- Outcome `STRUCTURAL_QC_RUNTIME_FAIL`.
- Last completed stage `CANDIDATE_CREATED`.
- `candidateAuthoritative=false`.
- `eligibleForProfessionalReferenceScoring=false`.
- `neverRearmV159=true`.
- Structural-QC artifact absent.
- Safety: professional-reference reads `0`; professional-reference paths opened `0`; reference-facing score calls `0`; CUDA/GPU false; Modal false; main/Production unchanged.
- Workflow self-deleted and pushed the terminal freeze commit exactly once.

## Current hard boundary
- **V159 is closed forever. Never re-arm it, rerun its structural QC, regenerate its candidate, or score it.**
- The V159 timebase-QC PASS is useful architectural evidence, but it does not make the terminal V159 candidate authoritative.
- No professional-reference access is permitted during postmortem or successor implementation.
- Any successor must be freshly preregistered before implementation/execution and must not be tuned from a professional-reference score of V159 (none exists and none is allowed).
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Perform a **reference-blind implementation-only postmortem** of `structural_qc_v159.py` to identify every NumPy scalar/array value that can leak into the receipt and prove the exact `numpy.bool_` source. Do not read professional reference/scorer/candidate quality against reference.
3. Freeze a short V159 postmortem receipt documenting only the serialization/runtime defect and preserving score/reference-read counts at zero.
4. Preregister a new successor version (expected V160) before implementation. Explicitly state V159 is terminal and cannot be repaired/replayed.
5. Successor design may carry forward the already sealed/reference-blind V159 timebase/pitch numerics only if preregistered before execution; add a JSON-native scalar normalization contract for independent QC receipts and static tests covering NumPy scalar serialization.
6. Run a song-blind static preflight for the successor, including a synthetic structural-QC receipt serialization test, before any audio execution.
7. Seal final successor code identities and a new pre-run receipt; then arm exactly one fresh CPU workflow for the successor under the same one-shot safeguards.
8. Only a successor candidate that independently passes timebase QC **and** structural QC may become authoritative and later be scored once against the professional reference.
9. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
