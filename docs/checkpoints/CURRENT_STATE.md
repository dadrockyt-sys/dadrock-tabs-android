# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V159 is TERMINAL and permanently consumed. Its sole reference-blind CPU generation run passed the new independent timebase QC and created one candidate, but structural QC crashed while serializing its receipt because `checks.frozenGrid` was a NumPy `bool_`. No valid structural-QC receipt exists. The candidate is non-authoritative and ineligible for professional-reference scoring. V159 must never be re-armed, regenerated, structurally re-QC'd, repaired in place, or scored. The exact serializer defect is now frozen in reference-blind postmortem artifacts. Next phase: preregister V160 before any successor implementation changes. Professional-reference reads/score calls remain 0 for V159 postmortem; GPU/Modal/CUDA remain 0; main/Production remains untouched.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription/postmortem/successor implementation must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- **V159 is closed forever: no re-arm, replay, regeneration, structural-QC rerun, or score.**
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable shared identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; blob `9644e65719fbd361a9b39778ae9950c5e983e855` — **do not read during successor generation/implementation**.
- Frozen professional reference `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; blob `2fbed60b543c0488934d8642c488aa06bf31bbf5` — **scoring-only**.
- Front-end gates: combined Guitar timing-aware pitch F1 >= `0.80` AND Bass >= `0.80` before role/string/fret/technique/PDF work.

## Closed versions
- V154: one score forever; Guitar `0.04915390813859791`, Bass `0.1116751269035533`; failed.
- V155: invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: one score forever; Guitar `0.07692307692307694`, Bass `0.05757575757575757`; failed.
- V158: one score forever; Guitar `0.007756948933419521`, Bass `0.001976284584980237`; failed/consumed.
- **V159: one generation run forever; score count 0 forever; terminal `STRUCTURAL_QC_RUNTIME_FAIL`; candidate non-authoritative/ineligible for scoring; never re-arm.**

## V158 frozen diagnosis
- `debug/v158-cpu-autonomous/post-score-architecture-diagnosis.json`; freeze commit `8f2e03032cc5b323afd0b4668660199425bc585f`; blob `d7c5720b27f74f1f710b96a6b0da70569ae48bbc`.
- Failure: `2986` tracked beats over ~`216.45s` ≈ `827.72 BPM`; signed robust-z beat envelope caused invalid `log1p`; bar-phase Viterbi also altered absolute ordinal/time scale.
- V158 score-derived pitch tuning remains forbidden.

## V159 sealed contracts / code identities
- Preregistration `debug/v159-cpu-autonomous/preregistration.json`; commit `6264131c2c515ae2ac9b7c64627cabc70382c825`; blob `2eca55dc344908a791ba7946f42d77fbd7b8926d`.
- Numeric contract `debug/v159-cpu-autonomous/implementation-contract.json`; commit `b8e8cba795c2aa0d7d3990265b2472af8d1d7e06`; blob `83dfee2d537d00dbced367bdbc467d167a96db2f`.
- `build_timebase_v159.py` blob `45f0e5013f13064a71c854b2c0e026482a135a8b`.
- `timebase_qc_v159.py` blob `fae5054153c90360ed5ea3f504feb432ba73eaef`.
- `transcribe_v159.py` blob `290d26099f9ac082eb19173f03d1904f7fbab45d`.
- `structural_qc_v159.py` blob `a3fbf4e8d827aca955a0995fc31930a8c631c932`.
- `negative-runtime-guard.py` blob `6a068e4699dcbcac0e236a9c54ce10efe1c96d96`.
- Static-preflight workflow blob `28cc7d465a910dfdf1f919bc58e9696392ad718f`.
- Pre-run identity receipt `debug/v159-cpu-autonomous/pre-run-identity-receipt.json`; seal commit `f9916cdb3ae0cbc2eecb3325c01fbfcac22b6bb4`; blob `9edb001227ce99570b0c4081102bf22276121499`.

## V159 frozen generation numerics — historical / do not alter retroactively
### Timebase
- SR `22050`, hop `256`; onset arrays finite; clamp >=0; normalize by positive max > `1e-12`.
- Beat envelope `0.5*unitMix + 0.5*unitDrums`; librosa beat tracker start BPM `120`, tightness `100`, sparse=true.
- Any captured `RuntimeWarning` during onset/beat/rhythm construction fatal.
- Beat count >=8; mean/median/count-duration implied BPM all `30..300`; median-IBI BPM / tracker BPM `0.5..2.0`.
- Four static phases with frozen evidence weights; `leadingBeatCount=(-selectedPhase)%4`; prepend 0..3 beats only.
- Absolute ordinal sequential; grid step `4*ordinal`; quantize `int(round(rawGridStep))`; measure `absStep//16+1`; step `absStep%16`.
### Pitch
- Same reference-blind V158 pitch numerics: harmonic template 36 bins/octave, harmonics 1..5 weights `[1,.5,.3333333333,.25,.2]`, radius1.
- Bass MIDI 28..67; onset backtrack; 35ms min IOI; 180ms window; pYIN 2048/256; sigma .75; fusion .75.
- Guitar MIDI 40..88; Basic Pitch onset .5/frame .3/min90ms/melodia=true; persistent track min3/radius1/max6; frozen register/harmonic rules; added-track duration .07s.

## V159 static preflight — PASS / CONSUMED
- Run ID `33195208763`, run #1 attempt #1, job `98930481313`, success, CPython 3.10.21.
- All Python files compiled; negative runtime guard PASS; no prior-version/reference/scorer paths; no pitch calls in pre-pitch files; transcriber requires timebase-QC PASS before pitch.
- No audio/generation artifacts created by static preflight. Never rerun it.

## V159 one-shot CPU generation — CONSUMED
- Arm commit `0e33dc356cef573a146bfe74fae718a523aa8fec`; sole workflow `.github/workflows/v159-generate.yml` self-deleted at terminal freeze.
- Run ID `33195994387`; run #1 attempt #1; job `98933144549`.
- CPU dependency pins PASS: Python 3.10, `torch==2.8.0+cpu`, NumPy 1.26.4, SciPy 1.13.1, SoundFile 0.12.1, Basic Pitch 0.4.0, Demucs 4.1.0, imageio-ffmpeg 0.6.0, librosa 0.11.0.
- CPU assertions/determinism PASS; CUDA unavailable; seed0; threads1; deterministic algorithms true.
- Historical source identity PASS; normalized WAV identity PASS.
- Fresh one-pass CPU `htdemucs_6s` PASS; stems `/tmp/v159-demucs/htdemucs_6s/v159-normalized/{guitar,bass,drums}.wav`.
- Environment receipt SHA256 `f1348bd53547b9b168793d694b9f777cde9b8b6e1fc3d03f069b5db216445154`.
- Timebase SHA256 `036b60261bdd07def93352ec18d03d13727e3f25cd3550d308fb0b9e94c73b53`; `448` detected beats; selected phase `1`.
- Independent timebase QC **PASS**, failed checks `[]`; receipt SHA256 `d8b5337d884258aaa9d9f3a3ed48493396e226077f480db0b56bca9e60ba2a01`.
- Candidate created once after QC PASS; SHA256 `a2057b0f160f8f689ea7593acb277e8a6c56325ef3183cfef58e7196907fb36c`; counts combined Guitar `2276`, Bass `460`.
- Generation receipt SHA256 `a7551158b77be424f661e7eed9090e2656f6b3088c9c5df156e1ccc850b5476e`.
- Generation referenceRead=false; score calls 0.

## V159 terminal freeze — AUTHORITATIVE
- Commit `e0ab58ef5766f6c1515453c05b80e86429140acb`.
- `debug/v159-cpu-autonomous/terminal-freeze.json`; blob `e3cb31788a87921ed7ebc44db1f523e6e081e9b8`.
- Schema `dadrock.tabs.v159.terminal-freeze.v1`; status TERMINAL; outcome `STRUCTURAL_QC_RUNTIME_FAIL`; last completed stage `CANDIDATE_CREATED`.
- `candidateAuthoritative=false`; `eligibleForProfessionalReferenceScoring=false`; `neverRearmV159=true`; structural-QC receipt absent.
- Safety: reference reads 0; professional paths opened 0; reference-facing score calls 0; GPU/CUDA false; Modal false; main/Production untouched.

## V159 frozen serializer postmortem — COMPLETE
Two compatible reference-blind diagnosis receipts now document the same proven root cause:
- `debug/v159-cpu-autonomous/post-terminal-structural-runtime-diagnosis.json`; commit `1cb558d2865f96739ab5c9ef513d15c4d09f5ba4`; blob `95d89bec0c7571e84d945d812f968909ad475c39`.
- `debug/v159-cpu-autonomous/post-run-implementation-diagnosis.json`; commit `4094f636ee6ab13f6eca8d43b19823f845b143b0`; blob `6d01cd2b6f8f3f9df52277904b0f892df9ba8fc0`.
- Proven leaking field: `checks.frozenGrid`.
- Source pattern ends in `np.all(np.diff(steps) == 4.0)`.
- Python `and` returns the last evaluated operand; `np.all` returns `numpy.bool_`; therefore truthy frozen-grid evaluation stores a NumPy scalar directly in `checks`.
- `passed = all(bool(value) for value in checks.values())` normalizes only the aggregate control-flow result, not the stored `checks` values.
- Receipt embeds raw `checks`; `json.dumps` therefore raises `TypeError: Object of type bool_ is not JSON serializable` before structural-QC receipt write.
- Reviewed direct assignments found no other NumPy scalar/array leak in V159 `checks`.
- Successor-only repair requirement: generic deterministic recursive JSON normalization (`numpy.generic -> .item()`, ndarray -> `.tolist()` recursively), explicit native bool for `frozenGrid`, and static synthetic coverage for numpy bool/int/float/array serialization plus assertion that all structural check values are native bool.
- No professional reference/scorer/prior score/candidate-quality comparison was used for this diagnosis; score/reference-read counts remain zero.

## Current hard boundary
- **V159 closed forever.** No patch/replay/regeneration/structural-QC rerun/score.
- V159 timebase-QC PASS is architecture evidence only; it does not make V159 candidate authoritative.
- No professional-reference access during V160 preregistration/implementation/generation/QC.
- Any successor must be freshly preregistered before implementation/execution.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Create and freeze **V160 preregistration before any V160 implementation code**.
3. V160 prereg must explicitly: preserve V159 terminality; carry forward V159 reference-blind timebase/pitch numerics unchanged in substance; prohibit V159 candidate/score/reference reads; add only successor structural-QC serialization hardening and static-test contract.
4. Seal a V160 numeric/implementation contract before implementation if separated from preregistration.
5. Implement V160 as fresh files/paths only; do not modify V159 artifacts/code.
6. Add deterministic recursive JSON-native normalization for QC receipts, explicit bool normalization of structural checks, and a song-blind synthetic serializer test for `numpy.bool_`, NumPy integer/float scalars, and ndarray.
7. Run a song-blind CPU static preflight before any V160 audio processing. It must compile all V160 files, run negative runtime guard, run synthetic serializer test, and prove no V160 generation artifacts exist.
8. Seal final V160 code identities and pre-run receipt; only then arm exactly one fresh CPU generation workflow.
9. Only if V160 timebase QC + structural QC both PASS may its single candidate become authoritative and later be scored exactly once.
10. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
