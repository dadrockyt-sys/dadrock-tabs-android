# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 and V157 are permanently consumed after one failed reference score each. V155 is protocol-invalid and never scoreable. V156 is permanently aborted before candidate. V157 post-score diagnosis is COMPLETE / FROZEN. V158 now has exactly ONE frozen, independently reference-blind-QC-passing CPU candidate. Sole generation run `33145878069` (run number 1, attempt 1) completed SUCCESS from trigger commit `eb4c41d83d0fa77402b18da5eb6655014593c186`; the workflow self-sealed by removing `.github/workflows/v158-generate.yml` and freezing outputs at commit `1164742a49f6b760dbf3f995e91c520493f425d8`. Candidate SHA256 is `2a9e8bdfbe48f03dc5d3734780aeb937ef0c5654d55a40536069ed30ee46bcc9`; independent structural QC is PASS. V158 professional-reference reads remain 0 and reference-facing score calls remain 0. No GPU/Modal/CUDA was used and main/Production was untouched. Next: seal a separate one-use V158 score guard/workflow against this exact frozen candidate/QC identity, then open the frozen professional reference exactly once for the sole official score. Do not modify, retune, replace, or regenerate the V158 candidate.**

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
- Frozen scorer Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Combined frozen professional reference SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; Guitar 1393 / Bass 547.

## Closed historical versions
- **V154:** score count 1 forever; Guitar F1 `0.04915390813859791`, Bass F1 `0.1116751269035533`; failed.
- **V155:** protocol-invalid duplicate generation; score count 0 forever.
- **V156:** aborted before candidate; score count 0 forever.
- **V157:** sole generation run `33143471258`; candidate SHA256 `f5dc7094b72f8e3a988b1fdd59808cb056461d7e12a6d41508942cf499de3e71`; sole score run `33143986627`; Guitar F1 `0.07692307692307694`, Bass F1 `0.05757575757575757`; score count 1 forever.

## V157 frozen post-score diagnosis
- Diagnostic run `33144115704`, job `98761292358`; frozen diagnostic Git blob `fb0460f158f97230bb5c82193f9409306bfa2960`; freeze commit `51fcd9b93a495f939ce85a7ec578f7ea3d70c5de`.
- Additional official score calls 0; no candidate modification/variant.
- Architecture evidence only: stable beat clock but wrong 4/4 phase; CQT-only Guitar completion low-value/high-FP; Bass onset detection dense but pYIN event formation sparse with low-register/fundamental failure.
- Exact diagnostic alignment values are forbidden future generation constants.
- Quartile diagnostic #4 is invalid due a range predicate bug; ignore it.

## V158 sealed setup contracts
### Architecture preregistration
- `debug/v158-cpu-autonomous/preregistration.json`
- Commit `cdb2eca7ec16479a5868f9a3ca18624fc0892c44`; Git blob `728cf28646db225f3c266a4bb73a6112b1f60330`.
- Status `PREREGISTERED_BEFORE_GENERATION`.

### Numeric implementation contract
- `debug/v158-cpu-autonomous/implementation-contract.json`
- Commit `90c878c50afcd70a6a2f7e58f2605ed2a7b2ba27`; Git blob `68f01df155cd27077cea3de5a0cd048ddcb7bd76`.
- Status `SEALED_BEFORE_GENERATION_CODE`.
- Canonical schemas: candidate `dadrock.tabs.v158.cpu-sequential-onset-first-generated.v1`; generation receipt `dadrock.tabs.v158.cpu-generation-receipt.v1`; environment receipt `dadrock.tabs.v158.cpu-environment-receipt.v1`; QC `dadrock.tabs.v158.reference-blind-structural-qc.v1`; pre-run receipt `dadrock.tabs.v158.pre-run-identity-receipt.v1`.
- Timebase: sr 22050 / hop 256 / start BPM 120 / tightness 100; four-state Viterbi next `.985`, same `.0075`, skip-one `.0075`; state-0 emission weights drums/mix/Bass/low-flux/chroma-change `1.0/.5/.5/.75/.75`; non-downbeat emission 0; low-frequency max 200 Hz; deterministic tie rules; piecewise beat grid; Python-round sixteenth quantization.
- Bass: onset-first; backtrack true; 35 ms collapse; 180 ms pitch window; pYIN 2048/256 soft evidence; harmonic-template MIDI 28–67; pYIN sigma `.75`; fusion `.75`; global octave/fundamental comparison; source `onset_harmonic_pyin`.
- Guitar: Basic Pitch `.5/.3/90ms`, MIDI 40–88; three-frame persistent harmonic-template tracks; max six pitches; explicit ±12 repair; no free-standing single-frame CQT; source labels only `basic_pitch`/`harmonic_track`.

### Sparse-pursuit consistency resolution — SEALED
- `debug/v158-cpu-autonomous/sparse-pursuit-contract-resolution.json`
- Commit `d07c56e51168d7f07784ad3ed67b4902245a0c4e`; Git blob `b4b6a5c1f8a88d359a981eb1238907805f2fc2a9`.
- Candidate pool = sealed three-frame persistent top-six intersection; private three-frame `log1p(abs(CQT))` residual; radius-1 harmonic bins; greatest-positive residual gain; lower-MIDI tie within `1e-12`; no selected-bin overlap; max six; same-MIDI 60 ms exclusion; 0.07 s `harmonic_track`; no new tuned thresholds.

## V158 final generation code pins
- Base helper `validation/v158_cpu_multitrack/transcribe_v158_base.py`: commit `dbb9be07867a95a9592a42b0b8d8a19b1f303340`, Git blob `5617ff1a6ea301ecaeb898b123b05d2a8c915388`.
- Canonical transcriber `validation/v158_cpu_multitrack/transcribe_v158.py`: commit `8398a6a851cc9919be46d294e653399f3fb87e30`, Git blob `91d65049031506fe44b44e034b1ab04022ba0b91`.
- Independent QC `validation/v158_cpu_multitrack/structural_qc.py`: commit `f93ecd163d849ac8a3d8bd661b7be39f8a767812`, Git blob `0bbb08225f0a21bc5bf4889189f22d89953371df`.
- Setup syntax/isolation audit workflow blob `ac7b8c3de34f527e0d3f9b0b0160538b93b30e70`; sole audit run `33145622458` SUCCESS.

## V158 pre-run identity receipt — SEALED
- `debug/v158-cpu-autonomous/pre-run-receipt.json`.
- Commit `43f8339ee16bd9d822d601e39b3cedb5f41d904d`; Git blob `e7300529fee191335a6709127e07069210704162`; SHA256 used by generation/QC `daec7937b406c3bdf8bd8862b32b78f979f3b17ba2a9a829b09d06348034cff5`.
- Validation `PASS`; status `SEALED_BEFORE_GENERATION`.
- Seal boundary: candidate absent; generation/environment receipts absent; generation workflow absent; reference reads 0; reference-facing scores 0; GPU/Modal false; main/Production untouched.
- Trigger contract: one workflow-creation trigger; no second arm; one run; self-seal after QC; duplicate => abort V158 without scoring; no branch writes while active.

## V158 sole CPU generation — COMPLETE / FROZEN
- Trigger workflow `.github/workflows/v158-generate.yml` was created once at commit `eb4c41d83d0fa77402b18da5eb6655014593c186` and self-removed after success.
- Sole run ID `33145878069`; run number 1; attempt 1; conclusion SUCCESS.
- All generation steps passed: sealed identity checks, historical audio identity, exact CPU dependencies, deterministic normalization, seeded in-process CPU Demucs, pre-candidate branch stability, environment receipt, exactly one candidate generation, independent reference-blind structural QC, final freeze/self-seal.
- Freeze commit `1164742a49f6b760dbf3f995e91c520493f425d8` (`research: freeze sole V158 reference-blind CPU candidate [skip ci]`).
- Generation workflow is absent after freeze.

### Frozen candidate
- `debug/v158-cpu-autonomous/generated.json`
- Git blob `1ddb1849b3cfefc14b60f6b5ac72af9ffcdc7fa6`.
- SHA256 `2a9e8bdfbe48f03dc5d3734780aeb937ef0c5654d55a40536069ed30ee46bcc9`.
- Counts: combined Guitar 1701; Bass 465.
- Guitar sources: Basic Pitch 1331; harmonic track 370. MIDI range 40–86.
- Bass source: `onset_harmonic_pyin` 465. MIDI range 29–56.
- No pre-grid exclusions.

### Environment receipt
- `debug/v158-cpu-autonomous/environment-receipt.json`
- Git blob `9749b5c58952ca56a80df4834ea2ae116471f532`.
- SHA256 `1bb07ed96cdbcf1dfe5a29aea85da68e43aa63bf2835008ca98a4bae46557d9a`.
- CPU-only: torch `2.8.0+cpu`; CUDA unavailable; Demucs `htdemucs_6s`, shifts 1, jobs 1; single run/separation; deterministic seeds/thread counts sealed.
- Stem SHA256: Guitar `1a39ba7a89a798a9372a4db934119d7e3b0300512b6b3d57ee2cfa0eb1f4310f`; Bass `ad3f30f678f3f1d53f36b44fdd2c4b5438df9ea2154d755222543783a0eabb18`; drums `450fa2deada5b4222039473eb2bec4f012b9e09b754c7d70d75a0f12430f8ec2`.

### Generation receipt
- `debug/v158-cpu-autonomous/generation-receipt.json`
- Git blob `3afb6c011065568890e1e48e437882e7848f1aaa`.
- SHA256 `e05716636d4bf63fd86ab0f3bc97cb2e274fcd600d47a839d32dfff5543ef12f`.
- Candidate SHA linkage, actual transcriber/helper/QC/resolution identities, pre-run SHA, environment SHA, audio/stem identities, and all safety counters are frozen.
- Receipt state `PENDING_INDEPENDENT_STRUCTURAL_QC` is the generation-time state; the separate independent QC below subsequently passed.

### Independent structural QC — PASS
- `debug/v158-cpu-autonomous/structural-qc.json`
- Git blob `4cb52d4f17359fa4386945800b09fcf0171a8e30`.
- Schema `dadrock.tabs.v158.reference-blind-structural-qc.v1`; validation `PASS`.
- Candidate SHA matches frozen candidate.
- Environment/generation/pre-run/transcriber/helper/QC pins all verified.
- Timebase: beat count 2986; state-path length 2986; state counts 0=924, 1=821, 2=828, 3=413.
- Safety: referenceRead false; professional reference paths opened 0; reference-facing score calls 0; professional-quality metric used false; human correction false; threshold sweep false; variant selection false; GPU false; main/Production untouched.

## Current V158 boundary
- **Exactly one V158 candidate exists and is frozen. It must never be modified or replaced.**
- **Independent reference-blind structural QC = PASS.**
- **V158 professional-reference reads = 0; reference-facing official score calls = 0.**
- **No GPU execution has occurred.**
- **The generation workflow has self-removed and cannot produce a second candidate without violating the protocol.**

## Exact next steps — RESUME HERE
1. Re-fetch latest checkpoint/head before each write because concurrent continuations exist.
2. Inspect/reuse the frozen V157 one-use score-guard mechanics only as protocol scaffolding; do not reuse V157 candidate scores/diagnostic constants as V158 generation/scoring inputs.
3. Seal a V158 score guard against candidate SHA256 `2a9e8bdf...`, candidate blob `1ddb1849...`, generation receipt blob `3afb6c01...`, environment receipt blob `9749b5c5...`, structural-QC blob `4cb52d4f...`, frozen scorer blob `9644e657...`, and frozen reference SHA256 `b39a203a...` while V158 score calls remain 0.
4. Create the V158 score workflow exactly once; creation is the sole trigger. It may open the professional reference only for scoring the already-frozen candidate, must call the frozen scorer exactly once, freeze the score result, and self-remove.
5. After the sole score, V158 is permanently consumed regardless of pass/fail. Never retune, regenerate, or score a replacement.
6. Gate: require both combined Guitar F1 >= 0.80 and Bass F1 >= 0.80 before resuming Rhythm/Lead role separation, string/fret assignment, techniques and professional PDF work.
7. Fresh explicit authorization remains required immediately before Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
