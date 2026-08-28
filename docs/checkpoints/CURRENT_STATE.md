# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 and V157 are permanently consumed after one failed reference score each. V155 is protocol-invalid and never scoreable. V156 is permanently aborted before candidate. V157 post-score diagnosis is COMPLETE / FROZEN. V158 remains strictly pre-generation. Architecture preregistration, numeric implementation contract, and sparse-pursuit consistency resolution are sealed. The original V158 setup draft is preserved byte-for-byte as `transcribe_v158_base.py`. The two setup/provenance gaps identified in the prior checkpoint are now repaired: canonical transcriber commit `8398a6a851cc9919be46d294e653399f3fb87e30`, blob `91d65049031506fe44b44e034b1ab04022ba0b91`, consumes/enforces the pre-run receipt and computes its real entrypoint blob; independent QC commit `f93ecd163d849ac8a3d8bd661b7be39f8a767812`, blob `0bbb08225f0a21bc5bf4889189f22d89953371df`, consumes/hashes the actual environment-receipt file and verifies exact embedded equality plus transcriber/helper/pre-run pins. No musical numeric contract was changed. No candidate, generation receipt, environment receipt, pre-run receipt, generation workflow, QC freeze, professional-reference read, score call, or GPU execution exists. Next: finish syntax/static audit of these final code blobs, seal the pre-run identity receipt with their exact pins, then and only then create the one-shot CPU generation workflow.**

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
- Combined frozen reference SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; Guitar 1393 / Bass 547.

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
- Commit `cdb2eca7ec16479a5868f9a3ca18624fc0892c44`
- Git blob `728cf28646db225f3c266a4bb73a6112b1f60330`
- Status `PREREGISTERED_BEFORE_GENERATION`.

### Numeric implementation contract
- `debug/v158-cpu-autonomous/implementation-contract.json`
- Commit `90c878c50afcd70a6a2f7e58f2605ed2a7b2ba27`
- Git blob `68f01df155cd27077cea3de5a0cd048ddcb7bd76`
- Status `SEALED_BEFORE_GENERATION_CODE`.
- Canonical schemas: candidate `dadrock.tabs.v158.cpu-sequential-onset-first-generated.v1`; generation receipt `dadrock.tabs.v158.cpu-generation-receipt.v1`; environment receipt `dadrock.tabs.v158.cpu-environment-receipt.v1`; QC `dadrock.tabs.v158.reference-blind-structural-qc.v1`; pre-run receipt `dadrock.tabs.v158.pre-run-identity-receipt.v1`.
- Timebase: sr 22050 / hop 256 / start BPM 120 / tightness 100; four-state Viterbi next `.985`, same `.0075`, skip-one `.0075`; state-0 emission weights drums/mix/Bass/low-flux/chroma-change `1.0/.5/.5/.75/.75`; non-downbeat emission 0; low-frequency max 200 Hz; deterministic tie rules; piecewise beat grid; Python-round sixteenth quantization.
- Bass: onset-first; backtrack true; 35 ms collapse; 180 ms pitch window; pYIN 2048/256 soft evidence; harmonic-template MIDI 28–67; pYIN sigma `.75`; fusion `.75`; global octave/fundamental comparison; source `onset_harmonic_pyin`.
- Guitar: Basic Pitch `.5/.3/90ms`, MIDI 40–88; three-frame persistent harmonic-template tracks; max six pitches; explicit ±12 repair; no free-standing single-frame CQT; source labels only `basic_pitch`/`harmonic_track`.
- QC requires Viterbi path length = beat count, states 0–3, Bass onset provenance, forbidden CQT-only labels absent, write-once candidate/receipts, referenceRead=false, professional paths opened=0, score calls=0, exactly one generation workflow run.

### Sparse-pursuit consistency resolution — SEALED
- `debug/v158-cpu-autonomous/sparse-pursuit-contract-resolution.json`
- Commit `d07c56e51168d7f07784ad3ed67b4902245a0c4e`.
- Git blob `b4b6a5c1f8a88d359a981eb1238907805f2fc2a9`.
- Status `SEALED_BEFORE_CANONICAL_EXECUTION_CODE`.
- Candidate pool = sealed three-frame persistent top-six intersection.
- Residual = same three-frame `log1p(abs(CQT))`; template bins = radius-1 neighborhoods around harmonics 1..5.
- Iteratively choose greatest positive residual template gain, ties within `1e-12` to lower MIDI; selected templates must not overlap prior selected template bins; zero selected template bins in private residual; stop at six / no eligible candidate / non-positive gain.
- Event creation remains `harmonic_track`, same-MIDI 60 ms exclusion, 0.07 s duration; no new tuned thresholds.
- Resolution blob must be pinned in the pre-run receipt.

## V158 final setup code identities pending pre-run seal
### Base helper — frozen
- `validation/v158_cpu_multitrack/transcribe_v158_base.py`
- Preserve commit `dbb9be07867a95a9592a42b0b8d8a19b1f303340`.
- Git blob `5617ff1a6ea301ecaeb898b123b05d2a8c915388`.
- Byte-for-byte original reference-blind setup implementation; canonical entrypoint verifies this blob before use.

### Canonical transcriber — provenance repaired
- `validation/v158_cpu_multitrack/transcribe_v158.py`
- Commit `8398a6a851cc9919be46d294e653399f3fb87e30`.
- Git blob `91d65049031506fe44b44e034b1ab04022ba0b91`.
- Musical recognition behavior remains the sealed V158 behavior: same fixed Basic Pitch, ±12 repair, independent onsets, persistent top-six pool, sparse-pursuit resolution, Bass onset-first logic from frozen base helper, and same grid mapping/dedupe.
- Required setup arguments now include `--pre-run-receipt` and `--structural-qc`.
- At runtime it computes its own Git blob and the supplied QC blob, verifies exact prereg/contract/resolution/transcriber/base-helper/QC pins from pre-run, verifies pre-run sealed-before-generation/reference-zero boundary, and verifies CPU environment receipt.
- Candidate sealed inputs and generation receipt now include actual transcriber/QC identities and pre-run receipt SHA256; the old `PIN_AT_PRE_RUN` placeholder is removed.
- Static isolation remains professional-reference/prior-output blind.

### Independent structural QC — provenance repaired
- `validation/v158_cpu_multitrack/structural_qc.py`
- Commit `f93ecd163d849ac8a3d8bd661b7be39f8a767812`.
- Git blob `0bbb08225f0a21bc5bf4889189f22d89953371df`.
- Required inputs now include actual `--environment-receipt`, `--transcriber`, and `--base-helper` paths.
- Hashes actual environment-receipt bytes and requires generation receipt linkage; parsed environment must exactly equal the receipt-embedded environment.
- Verifies pre-run exact transcriber/base-helper/QC pins, candidate sealed identities, generation-receipt implementation identities, schema/range/source/sort/dedupe/onset/timebase/Viterbi invariants, deterministic CPU dependencies, single generation workflow count, and zero reference/score counters.
- Does not import generation code and has no professional-reference/scorer input.

## Current V158 boundary
- **Final candidate-generation transcriber/helper/QC blobs exist; pre-run seal is still absent.**
- **No V158 candidate, generation receipt, environment receipt, pre-run receipt, generation workflow, QC freeze or score exists.**
- **V158 professional-reference reads = 0; reference-facing score calls = 0.**
- **No GPU execution has occurred.**

## Exact next steps — RESUME HERE
1. Re-fetch latest checkpoint/head before every write because concurrent continuations exist.
2. Finish static/syntax audit of blobs `91d6504903...`, `5617ff1a6e...`, `0bbb08225f...`; do not generate candidate.
3. Seal `debug/v158-cpu-autonomous/pre-run-receipt.json` with exact prereg/contract/resolution/transcriber/base-helper/QC pins while candidate/receipt/environment/workflow are absent and reference score calls remain 0.
4. Re-fetch and checkpoint the sealed pre-run state.
5. Only then create the V158 generation workflow exactly once; workflow creation is the sole trigger, no arm edit, and no branch writes while generation is active.
6. Generate exactly one deterministic CPU candidate; run independent structural QC/freeze before any professional-reference access; afterward seal a separate one-use score guard/workflow.
7. If a future candidate passes both 0.80 acoustic gates, only then resume Rhythm/Lead role separation, string/fret assignment, techniques and professional PDF work.
8. Fresh explicit authorization remains required immediately before Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
